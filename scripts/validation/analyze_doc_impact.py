#!/usr/bin/env python3
"""
Analyze documentation impact for pull requests.
Identifies which testing documentation is affected by feature documentation changes.
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Set
import yaml
import re


class DocumentationImpactAnalyzer:
    """Analyzes impact of documentation changes on related files."""
    
    def __init__(self, docs_dir: str = "docs"):
        self.docs_dir = Path(docs_dir)
        self.features_dir = self.docs_dir / "features"
        self.testing_dir = self.docs_dir / "testing"
        
    def analyze_changed_files(self, changed_files: List[str]) -> Dict:
        """Analyze impact of changed files on documentation ecosystem."""
        
        # Filter for documentation files only
        doc_changes = [f for f in changed_files if f.startswith('docs/') and f.endswith('.md')]
        
        if not doc_changes:
            return {
                "changed_files": [],
                "impact": {
                    "affected_features": [],
                    "affected_testing": [],
                    "broken_links": [],
                    "recommendations": []
                },
                "summary": "No documentation changes detected"
            }
        
        # Separate feature and testing changes
        feature_changes = [f for f in doc_changes if 'features/' in f]
        testing_changes = [f for f in doc_changes if 'testing/' in f]
        
        # Analyze impact
        impact = {
            "affected_features": [],
            "affected_testing": [],
            "broken_links": [],
            "recommendations": []
        }
        
        # For each changed feature doc, find related testing docs
        for feature_file in feature_changes:
            related_testing = self._find_related_testing(feature_file)
            if related_testing:
                impact["affected_testing"].extend(related_testing)
                impact["recommendations"].append(
                    f"Review and update testing documentation for {Path(feature_file).stem}"
                )
        
        # For each changed testing doc, find related feature docs
        for testing_file in testing_changes:
            related_feature = self._find_related_feature(testing_file)
            if related_feature:
                impact["affected_features"].append(related_feature)
                impact["recommendations"].append(
                    f"Verify feature documentation alignment with {Path(testing_file).stem}"
                )
        
        # Check for broken links
        for doc_file in doc_changes:
            broken = self._check_broken_links(doc_file)
            if broken:
                impact["broken_links"].extend(broken)
        
        # Generate summary
        summary_parts = []
        if feature_changes:
            summary_parts.append(f"{len(feature_changes)} feature doc(s) changed")
        if testing_changes:
            summary_parts.append(f"{len(testing_changes)} testing doc(s) changed")
        if impact["affected_testing"]:
            summary_parts.append(f"{len(impact['affected_testing'])} testing doc(s) affected")
        if impact["broken_links"]:
            summary_parts.append(f"{len(impact['broken_links'])} broken link(s) detected")
        
        summary = ", ".join(summary_parts) if summary_parts else "No significant impact"
        
        return {
            "changed_files": doc_changes,
            "feature_changes": feature_changes,
            "testing_changes": testing_changes,
            "impact": impact,
            "summary": summary
        }
    
    def _find_related_testing(self, feature_file: str) -> List[str]:
        """Find testing documentation related to a feature file."""
        related = []
        
        try:
            # Read feature file front matter
            with open(feature_file, 'r', encoding='utf-8') as f:
                content = f.read()
                front_matter = self._extract_front_matter(content)
                
                if front_matter and 'relatedTesting' in front_matter:
                    testing_refs = front_matter['relatedTesting']
                    if isinstance(testing_refs, list):
                        related.extend(testing_refs)
                    elif isinstance(testing_refs, str):
                        related.append(testing_refs)
        except Exception as e:
            print(f"Warning: Could not read {feature_file}: {e}", file=sys.stderr)
        
        return related
    
    def _find_related_feature(self, testing_file: str) -> str:
        """Find feature documentation related to a testing file."""
        try:
            # Read testing file front matter
            with open(testing_file, 'r', encoding='utf-8') as f:
                content = f.read()
                front_matter = self._extract_front_matter(content)
                
                if front_matter and 'relatedFeature' in front_matter:
                    return front_matter['relatedFeature']
        except Exception as e:
            print(f"Warning: Could not read {testing_file}: {e}", file=sys.stderr)
        
        return None
    
    def _extract_front_matter(self, content: str) -> Dict:
        """Extract YAML front matter from markdown file."""
        # Match YAML front matter
        match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
        if match:
            try:
                return yaml.safe_load(match.group(1))
            except yaml.YAMLError:
                return None
        return None
    
    def _check_broken_links(self, doc_file: str) -> List[str]:
        """Check for broken internal links in a documentation file."""
        broken = []
        
        try:
            with open(doc_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Find all markdown links
                links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)
                
                for link_text, link_path in links:
                    # Skip external links
                    if link_path.startswith(('http://', 'https://', '#')):
                        continue
                    
                    # Resolve relative path
                    doc_dir = Path(doc_file).parent
                    target = (doc_dir / link_path).resolve()
                    
                    if not target.exists():
                        broken.append({
                            "file": doc_file,
                            "link_text": link_text,
                            "target": link_path,
                            "message": f"Link target does not exist: {link_path}"
                        })
        except Exception as e:
            print(f"Warning: Could not check links in {doc_file}: {e}", file=sys.stderr)
        
        return broken
    
    def generate_pr_comment(self, analysis: Dict) -> str:
        """Generate formatted PR comment from analysis results."""
        
        if not analysis["changed_files"]:
            return "No documentation changes in this PR."
        
        comment = "## 📊 Documentation Impact Analysis\n\n"
        
        # Summary section
        comment += f"**Summary:** {analysis['summary']}\n\n"
        
        # Changed files section
        if analysis["changed_files"]:
            comment += "### 📝 Changed Documentation\n\n"
            comment += "| File | Type |\n"
            comment += "|------|------|\n"
            for file in analysis["changed_files"]:
                doc_type = "Feature" if "features/" in file else "Testing" if "testing/" in file else "Other"
                comment += f"| `{file}` | {doc_type} |\n"
            comment += "\n"
        
        # Impact section
        impact = analysis["impact"]
        
        if impact["affected_testing"]:
            comment += "### 🔗 Affected Testing Documentation\n\n"
            comment += "The following testing documentation may need updates:\n\n"
            for testing_doc in impact["affected_testing"]:
                comment += f"- `{testing_doc}`\n"
            comment += "\n"
        
        if impact["affected_features"]:
            comment += "### 🔗 Affected Feature Documentation\n\n"
            comment += "The following feature documentation may need review:\n\n"
            for feature_doc in impact["affected_features"]:
                comment += f"- `{feature_doc}`\n"
            comment += "\n"
        
        if impact["broken_links"]:
            comment += "### ⚠️ Broken Links Detected\n\n"
            comment += "| File | Link | Issue |\n"
            comment += "|------|------|-------|\n"
            for broken in impact["broken_links"]:
                comment += f"| `{broken['file']}` | `{broken['target']}` | {broken['message']} |\n"
            comment += "\n"
        
        if impact["recommendations"]:
            comment += "### 📋 Recommendations\n\n"
            for rec in impact["recommendations"]:
                comment += f"- {rec}\n"
            comment += "\n"
        
        # Footer
        comment += "---\n"
        comment += "*💡 Tip: Run `/docs.validate-testing-traceability` locally to verify all links.*\n"
        comment += "<sub>Powered by AKR MCP Documentation Server</sub>\n"
        
        return comment


def main():
    parser = argparse.ArgumentParser(description="Analyze documentation impact for pull requests")
    parser.add_argument("--changed-files", nargs='+', help="List of changed files")
    parser.add_argument("--changed-files-file", help="File containing list of changed files (one per line)")
    parser.add_argument("--docs-dir", default="docs", help="Documentation directory (default: docs)")
    parser.add_argument("--output", choices=["json", "markdown"], default="markdown", 
                       help="Output format (default: markdown)")
    
    args = parser.parse_args()
    
    # Get changed files
    changed_files = []
    if args.changed_files:
        changed_files = args.changed_files
    elif args.changed_files_file:
        with open(args.changed_files_file, 'r') as f:
            changed_files = [line.strip() for line in f if line.strip()]
    else:
        print("Error: Either --changed-files or --changed-files-file is required", file=sys.stderr)
        sys.exit(1)
    
    # Analyze impact
    analyzer = DocumentationImpactAnalyzer(docs_dir=args.docs_dir)
    analysis = analyzer.analyze_changed_files(changed_files)
    
    # Output results
    if args.output == "json":
        print(json.dumps(analysis, indent=2))
    else:
        print(analyzer.generate_pr_comment(analysis))
    
    # Exit code based on findings
    if analysis["impact"]["broken_links"]:
        sys.exit(2)  # Warnings
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
