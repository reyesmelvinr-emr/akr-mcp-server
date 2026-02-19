"""
Code analyzer for extracting documentation content from source files.
"""

import json
import logging
from pathlib import Path
from typing import List, Dict, Optional, Any
from datetime import datetime

from .extractors.base_extractor import BaseExtractor, ExtractedData
from .extractors.csharp_extractor import CSharpExtractor
from .extractors.typescript_extractor import TypeScriptExtractor
from .extractors.sql_extractor import SQLExtractor
from .context_builder import (
    build_service_context, build_component_context, build_table_context,
    report_extraction_gaps
)
from .template_renderer import TemplateRenderer


logger = logging.getLogger(__name__)


class CodeAnalyzer:
    """Analyzes source code files and extracts documentation content."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the code analyzer.
        
        Args:
            config: Configuration dictionary with analysis settings
        """
        self.config = config or {}
        self.enabled = self.config.get('enabled', True)
        self.depth = self.config.get('depth', 'full')
        self.languages = self.config.get('languages', ['csharp', 'typescript', 'sql'])
        self.timeout = self.config.get('timeout_seconds', 30)
        self.fallback = self.config.get('fallback_on_error', 'partial')
        
        # Initialize extractors
        self.extractors: List[BaseExtractor] = []
        if 'csharp' in self.languages:
            self.extractors.append(CSharpExtractor(self.config))
        if 'typescript' in self.languages:
            self.extractors.append(TypeScriptExtractor(self.config))
        if 'sql' in self.languages:
            self.extractors.append(SQLExtractor(self.config))
    
    def analyze_files(self, file_paths: List[str], project_type: str) -> List[ExtractedData]:
        """
        Analyze multiple source files and extract documentation content.
        
        Args:
            file_paths: List of file paths to analyze
            project_type: Project type (backend, ui, database)
            
        Returns:
            List of ExtractedData objects, one per file
        """
        if not self.enabled:
            logger.info("Code analysis is disabled in configuration")
            return []
        
        results = []
        for file_path_str in file_paths:
            file_path = Path(file_path_str)
            
            if not file_path.exists():
                logger.warning(f"File not found: {file_path}")
                continue
            
            # Find appropriate extractor
            extractor = self._find_extractor(file_path)
            if not extractor:
                logger.warning(f"No extractor found for file: {file_path}")
                continue
            
            # Extract data
            logger.info(f"Extracting from {file_path} using {extractor.__class__.__name__}")
            extracted = extractor.safe_extract(file_path)
            results.append(extracted)
            
            # Log extraction results
            self._log_extraction_results(extracted)
        
        return results
    
    def _find_extractor(self, file_path: Path) -> Optional[BaseExtractor]:
        """Find the appropriate extractor for the given file."""
        for extractor in self.extractors:
            if extractor.can_extract(file_path):
                return extractor
        return None
    
    def _log_extraction_results(self, extracted: ExtractedData):
        """Log extraction results and metrics."""
        metrics = {
            'timestamp': datetime.now().isoformat(),
            'event_type': 'code_analysis_result',
            'file_path': extracted.file_path,
            'language': extracted.language,
            'classes_extracted': len(extracted.classes),
            'methods_extracted': len(extracted.methods),
            'routes_extracted': len(extracted.routes),
            'validations_extracted': len(extracted.validations),
            'dependencies_extracted': len(extracted.dependencies),
            'tables_extracted': len(extracted.tables),
            'components_extracted': len(extracted.components),
            'errors': extracted.extraction_errors,
            'warnings': extracted.extraction_warnings
        }
        
        # Log to console
        if extracted.extraction_errors:
            for error in extracted.extraction_errors:
                logger.error(f"⚠️ {error}")
        if extracted.extraction_warnings:
            for warning in extracted.extraction_warnings:
                logger.warning(f"⚠️ {warning}")
        
        # Log metrics to enforcement log
        log_path = Path(__file__).parent.parent.parent / 'logs' / 'enforcement.jsonl'
        try:
            log_path.parent.mkdir(parents=True, exist_ok=True)
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps(metrics) + '\n')
        except Exception as e:
            logger.warning(f"Could not write to enforcement log: {e}")
    
    def populate_template(
        self,
        template_content: str,
        extracted_data_list: List[ExtractedData],
        project_type: str = "backend",
        service_name: str = "Service"
    ) -> str:
        """
        Populate template with extracted data using Jinja2 rendering.
        
        Uses context builders to transform ExtractedData into template contexts,
        then renders Jinja2 templates with the context data.
        
        Args:
            template_content: Original template content (kept for compatibility)
            extracted_data_list: List of extracted data from source files
            project_type: 'backend', 'ui', or 'database'
            service_name: Name of the service/component/table being documented
            
        Returns:
            Fully rendered markdown documentation
        """
        if not extracted_data_list:
            logger.info("No extracted data to populate template")
            return template_content
        
        logger.info(
            f"Rendering Jinja2 template for {project_type} project: {service_name}"
        )
        
        try:
            # Initialize renderer
            renderer = TemplateRenderer()
            
            # Determine what to render based on project type and extracted data
            if project_type == "backend" or (extracted_data_list[0].routes or extracted_data_list[0].classes):
                logger.info("Rendering service documentation")
                context = build_service_context(
                    service_name=service_name,
                    extracted_data_list=extracted_data_list
                )
                
                # Log extraction gaps for diagnostics
                gaps = report_extraction_gaps(extracted_data_list, "backend")
                if gaps['gaps']:
                    for gap in gaps['gaps']:
                        logger.warning(f"Extraction gap: {gap}")
                
                rendered = renderer.render_service_template(context)
            
            elif project_type == "ui" or extracted_data_list[0].components:
                logger.info("Rendering component documentation")
                context = build_component_context(
                    component_name=service_name,
                    extracted_data_list=extracted_data_list
                )
                
                gaps = report_extraction_gaps(extracted_data_list, "ui")
                if gaps['gaps']:
                    for gap in gaps['gaps']:
                        logger.warning(f"Extraction gap: {gap}")
                
                rendered = renderer.render_component_template(context)
            
            elif project_type == "database" or extracted_data_list[0].tables:
                logger.info("Rendering table documentation")
                context = build_table_context(
                    table_name=service_name,
                    extracted_data_list=extracted_data_list
                )
                
                gaps = report_extraction_gaps(extracted_data_list, "database")
                if gaps['gaps']:
                    for gap in gaps['gaps']:
                        logger.warning(f"Extraction gap: {gap}")
                
                rendered = renderer.render_table_template(context)
            
            else:
                # Fallback if type can't be determined
                logger.warning("Could not determine project type, defaulting to service")
                context = build_service_context(
                    service_name=service_name,
                    extracted_data_list=extracted_data_list
                )
                rendered = renderer.render_service_template(context)
            
            logger.info(f"Successfully rendered documentation: {len(rendered)} characters")
            return rendered
            
        except Exception as e:
            logger.error(f"Error rendering template: {e}", exc_info=True)
            # Fallback: return original template_content or empty string
            if self.fallback == "full":
                return template_content
            else:
                # Return empty string with error message
                return f"<!-- ERROR: Failed to render template: {str(e)} -->\n"
    

    
    # Formatting helper methods
    
    def _format_dependencies_table(self, dependencies: List) -> str:
        """Format dependencies as markdown table."""
        lines = ["| Dependency | Type | Purpose |", "|------------|------|---------|"]
        for dep in dependencies:
            desc = dep.description or "Injected dependency"
            lines.append(f"| `{dep.name}` | `{dep.type}` | {desc} |")
        return '\n'.join(lines)
    
    def _format_methods_table(self, methods: List) -> str:
        """Format methods as markdown table."""
        lines = ["| Method | Parameters | Returns | Description |", "|--------|------------|---------|-------------|"]
        for method in methods:
            params = ', '.join([f"{p.name}: {p.type or 'unknown'}" for p in method.parameters]) or "None"
            returns = method.return_type or "void"
            desc = method.description or ""
            lines.append(f"| `{method.name}()` | {params} | `{returns}` | {desc} |")
        return '\n'.join(lines)
    
    def _format_routes_table(self, routes: List) -> str:
        """Format API routes as markdown table."""
        lines = ["| Method | Path | Handler | Response Types |", "|--------|------|---------|----------------|"]
        for route in routes:
            responses = ', '.join([f"`{r}`" for r in route.response_types]) or "N/A"
            lines.append(f"| **{route.method}** | `{route.path}` | `{route.handler_name}()` | {responses} |")
        return '\n'.join(lines)
    
    def _format_validations_list(self, validations: List) -> str:
        """Format validations as bullet list."""
        lines = []
        for val in validations:
            rule_desc = f"**{val.field_name}**: {val.rule_type}"
            if val.rule_value:
                rule_desc += f" ({val.rule_value})"
            if val.error_message:
                rule_desc += f" - _{val.error_message}_"
            lines.append(f"- {rule_desc}")
        return '\n'.join(lines)
    
    def _format_props_table(self, props: List) -> str:
        """Format React props as markdown table."""
        lines = ["| Prop | Type | Required | Default | Description |", "|------|------|----------|---------|-------------|"]
        for prop in props:
            required = "Yes" if prop.is_required else "No"
            default = prop.default_value or "—"
            desc = prop.description or ""
            lines.append(f"| `{prop.name}` | `{prop.type}` | {required} | `{default}` | {desc} |")
        return '\n'.join(lines)
    
    def _format_events_list(self, events: List[str]) -> str:
        """Format event handlers as bullet list."""
        return '\n'.join([f"- `{event}()`" for event in events])
    
    def _format_state_list(self, state_vars: List[Dict[str, Any]]) -> str:
        """Format state variables as bullet list."""
        lines = []
        for var in state_vars:
            name = var.get('name', 'unknown')
            type_info = var.get('type', 'unknown')
            lines.append(f"- `{name}`: {type_info}")
        return '\n'.join(lines)
    
    def _format_columns_table(self, columns: List) -> str:
        """Format database columns as markdown table."""
        lines = ["| Column | Type | Nullable | Default | Constraints |", "|--------|------|----------|---------|-------------|"]
        for col in columns:
            nullable = "Yes" if col.is_nullable else "No"
            default = col.default_value or "—"
            constraints = ', '.join(col.constraints) or "—"
            if col.is_primary_key:
                constraints = "PRIMARY KEY" + (f", {constraints}" if constraints != "—" else "")
            if col.is_foreign_key:
                fk = f"FK → {col.foreign_key_table}.{col.foreign_key_column}"
                constraints = fk + (f", {constraints}" if constraints != "—" else "")
            lines.append(f"| `{col.name}` | `{col.data_type}` | {nullable} | `{default}` | {constraints} |")
        return '\n'.join(lines)
    
    def _format_constraints_list(self, constraints: List[str]) -> str:
        """Format constraints as bullet list."""
        return '\n'.join([f"- {constraint}" for constraint in constraints])
    
    def _format_indexes_list(self, indexes: List[Dict[str, Any]]) -> str:
        """Format indexes as bullet list."""
        lines = []
        for idx in indexes:
            name = idx.get('name', 'unknown')
            columns = ', '.join(idx.get('columns', []))
            unique = " (UNIQUE)" if idx.get('is_unique', False) else ""
            lines.append(f"- **{name}**: {columns}{unique}")
        return '\n'.join(lines)
