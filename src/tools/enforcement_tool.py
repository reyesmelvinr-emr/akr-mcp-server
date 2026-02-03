"""
EnforcementTool: Main orchestrator for template enforcement workflow.

Coordinates all components:
1. Template schema building
2. Document parsing
3. YAML generation
4. Validation
5. File writing with logging

Provides unified validate_and_write() API for integration with server.py.
"""

import os
from dataclasses import dataclass
from typing import List, Dict, Optional, Any

from .enforcement_tool_types import (
    FileMetadata,
    ValidationResult,
    ViolationSeverity,
)
from .template_schema_builder import TemplateSchemaBuilder
from .document_parser import BasicDocumentParser
from .yaml_frontmatter_generator import YAMLFrontmatterGenerator
from .validation_engine import ValidationEngine
from .file_writer import FileWriter, WriteResult
from .enforcement_logger import EnforcementLogger


@dataclass
class EnforceResult:
    """Result of full enforcement workflow (validate + write)."""
    valid: bool
    file_path: Optional[str] = None
    confidence: float = 0.0
    validation_errors: List[str] = None
    write_errors: List[str] = None
    write_warnings: List[str] = None
    dry_run: bool = False
    summary: str = ""
    
    def __post_init__(self):
        """Initialize mutable defaults."""
        if self.validation_errors is None:
            self.validation_errors = []
        if self.write_errors is None:
            self.write_errors = []
        if self.write_warnings is None:
            self.write_warnings = []


class EnforcementTool:
    """Main enforcement tool that orchestrates validation and writing."""
    
    def __init__(self, logger: Optional[EnforcementLogger] = None):
        """
        Initialize EnforcementTool.
        
        Args:
            logger: Optional EnforcementLogger for audit trail. If not provided, creates internal one.
        """
        self.schema_builder = TemplateSchemaBuilder()
        self.document_parser = BasicDocumentParser()
        self.yaml_generator = YAMLFrontmatterGenerator()
        self.validation_engine = ValidationEngine()
        self.file_writer = FileWriter()
        self.logger = logger or EnforcementLogger()
    
    def validate_and_write(
        self,
        generated_markdown: str,
        template_name: str,
        output_path: str,
        file_metadata: FileMetadata,
        config: Dict[str, Any],
        update_mode: str = "replace",
        overwrite: bool = False,
        dry_run: bool = False,
        template_content: Optional[str] = None,
    ) -> EnforceResult:
        """
        Complete enforcement workflow: validate + (conditionally write).
        
        This is the main API entry point for server.py integration.
        
        Args:
            generated_markdown: Markdown content from LLM
            template_name: Name of template to validate against (e.g., "lean_baseline_service_template")
            output_path: Target file path (relative to workspace root)
            file_metadata: FileMetadata with component info (name, path, domain, etc.)
            config: AKR config dict with workspace_root, pathMappings, etc.
            update_mode: How to handle existing file (replace, merge_sections, append)
            overwrite: Whether to overwrite existing files (if False, fail if file exists)
            dry_run: If True, validate but don't write (return preview)
            template_content: Optional pre-loaded template content (if not provided, loads from resources)
        
        Returns:
            EnforceResult with validation status, confidence, file path, errors
        """
        errors = []
        
        # Step 1: Load or use provided template content
        try:
            if template_content is None:
                # Would load from AKRResourceManager in production
                # For now, assume it's provided or we create a minimal one
                template_content = ""
            
            # Step 2: Build schema from template
            schema = self.schema_builder.build_schema(template_name, template_content)
            self.logger.log_schema_built(
                template_name=template_name,
                section_count=len(schema.required_sections),
                checksum=schema.checksum
            )
        
        except Exception as e:
            errors.append(f"Failed to build schema: {str(e)}")
            return EnforceResult(valid=False, validation_errors=errors)
        
        # Step 3: Parse generated markdown
        try:
            parsed_doc = self.document_parser.parse_document(generated_markdown)
        except Exception as e:
            errors.append(f"Failed to parse document: {str(e)}")
            return EnforceResult(valid=False, validation_errors=errors)
        
        # Step 4: Generate YAML front matter if missing
        yaml_data = parsed_doc.yaml_data.copy() if parsed_doc.yaml_data else {}
        if not yaml_data or len(yaml_data) == 0:
            try:
                yaml_block = self.yaml_generator.generate(file_metadata, template_name)
                # Parse generated YAML back into dict (basic parsing)
                for line in yaml_block.strip().split('\n'):
                    if line.startswith('---'):
                        continue
                    if ':' in line:
                        key, value = line.split(':', 1)
                        yaml_data[key.strip()] = value.strip()
            except Exception as e:
                errors.append(f"Failed to generate YAML front matter: {str(e)}")
                return EnforceResult(valid=False, validation_errors=errors)
        
        # Step 5: Reconstruct markdown with YAML front matter
        if yaml_data and not generated_markdown.startswith('---'):
            yaml_lines = ['---']
            for key, value in yaml_data.items():
                yaml_lines.append(f"{key}: {value}")
            yaml_lines.append('---')
            generated_markdown = '\n'.join(yaml_lines) + '\n' + generated_markdown
            parsed_doc = self.document_parser.parse_document(generated_markdown)
        
        # Step 6: Validate document
        validation_result: ValidationResult = self.validation_engine.validate_phase1(
            parsed_doc, schema
        )
        
        effective_mode = "per_file"  # Phase 1 supports per_file; per_module comes in Phase 2
        self.logger.log_validation_run(
            template_name=template_name,
            file_path=output_path,
            valid=validation_result.valid,
            confidence=validation_result.confidence,
            blocker_count=validation_result.severity_summary.get("blockers", 0),
            fixable_count=validation_result.severity_summary.get("fixable", 0),
            warn_count=validation_result.severity_summary.get("warnings", 0),
            effective_mode=effective_mode
        )
        
        if not validation_result.valid:
            # Validation failed
            violation_messages = [
                f"{v.type} (line {v.line}): {v.message}" if v.line else f"{v.type}: {v.message}"
                for v in validation_result.violations
            ]
            return EnforceResult(
                valid=False,
                confidence=validation_result.confidence,
                validation_errors=violation_messages,
                summary=f"Validation failed: {len(validation_result.violations)} violations found"
            )
        
        # Step 7: If dry_run, return preview without writing
        if dry_run:
            return EnforceResult(
                valid=True,
                file_path=output_path,
                confidence=validation_result.confidence,
                dry_run=True,
                summary=f"Dry-run validation passed. Would write to {output_path}"
            )
        
        # Step 8: Write file with security checks
        self.logger.log_write_attempt(
            file_path=output_path,
            template_name=template_name,
            update_mode=update_mode,
            effective_mode=effective_mode,
            overwrite=overwrite,
            dry_run=False
        )
        
        write_result: WriteResult = self.file_writer.write(
            generated_markdown,
            output_path,
            config
        )
        
        if write_result.success:
            self.logger.log_write_success(
                file_path=write_result.file_path,
                file_size_bytes=len(generated_markdown.encode('utf-8')),
                dry_run=False
            )
            return EnforceResult(
                valid=True,
                file_path=write_result.file_path,
                confidence=validation_result.confidence,
                write_warnings=write_result.warnings,
                summary=f"Documentation validated and written successfully to {write_result.file_path}"
            )
        
        else:
            self.logger.log_write_failure(
                file_path=output_path,
                error_type="WRITE_ERROR",
                error_message="; ".join(write_result.errors)
            )
            return EnforceResult(
                valid=False,
                confidence=validation_result.confidence,
                write_errors=write_result.errors,
                summary="Documentation validated but write failed"
            )
    
    def get_logger(self) -> EnforcementLogger:
        """
        Get the logger instance.
        
        Returns:
            EnforcementLogger for accessing logs/events
        """
        return self.logger
