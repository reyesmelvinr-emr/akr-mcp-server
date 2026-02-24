"""
Code Analytics - Unified code extraction interface.

Provides deterministic code analysis using language-specific extractors.
Composes CSharpExtractor (for C#/.NET) and SQLExtractor (for SQL DDL).

As of v0.2.0, this module uses only deterministic extractors.
Heuristic extractors (TypeScript, Business Rule, Failure Mode, etc.) are deprecated.
For semantic analysis, use Copilot Chat with extracted code context and AKR charters.
"""

import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

from .extractors.csharp_extractor import CSharpExtractor
from .extractors.sql_extractor import SQLExtractor
from .extractors.base_extractor import ExtractedData


logger = logging.getLogger(__name__)


class CodeAnalyzer:
    """Unified code analyzer using deterministic extractors."""
    
    def __init__(self):
        """Initialize code analyzer with deterministic extractors."""
        self.csharp_extractor = CSharpExtractor()
        self.sql_extractor = SQLExtractor()
        self.extractors = [self.csharp_extractor, self.sql_extractor]
    
    def detect_language(self, file_path: str) -> Optional[str]:
        """Detect primary language from file extension.
        
        Args:
            file_path: Path to source file
            
        Returns:
            Language identifier ('csharp', 'sql', or None if unknown)
        """
        path = Path(file_path)
        suffix = path.suffix.lower()
        
        language_map = {
            '.cs': 'csharp',
            '.sql': 'sql',
        }
        
        return language_map.get(suffix)
    
    def extract_methods(self, file_path: str) -> List[Dict[str, Any]]:
        """Extract methods/functions from source file.
        
        Args:
            file_path: Path to source file
            
        Returns:
            List of method metadata dicts with keys:
            - name: Method/function name
            - signature: Full method signature
            - parameters: List of parameter dicts
            - return_type: Return type (if available)
            - access_level: public/private/protected (if applicable)
            - line_number: Line where method is defined
        """
        path = Path(file_path)
        
        # Find appropriate extractor
        for extractor in self.extractors:
            if extractor.can_extract(path):
                try:
                    extracted = extractor.extract(path)
                    return self._format_methods(extracted.methods)
                except Exception as e:
                    logger.error(f"Error extracting methods from {file_path}: {e}")
                    return []
        
        return []
    
    def extract_classes(self, file_path: str) -> List[Dict[str, Any]]:
        """Extract class/interface definitions from source file.
        
        Args:
            file_path: Path to source file
            
        Returns:
            List of class metadata dicts with keys:
            - name: Class/interface name
            - type: 'class' or 'interface'
            - namespace: Namespace (if applicable)
            - methods: List of method names in class
            - properties: List of property names
            - base_classes: List of inherited classes
        """
        path = Path(file_path)
        
        # Find appropriate extractor
        for extractor in self.extractors:
            if extractor.can_extract(path):
                try:
                    extracted = extractor.extract(path)
                    return self._format_classes(extracted.classes, extracted.raw_data)
                except Exception as e:
                    logger.error(f"Error extracting classes from {file_path}: {e}")
                    return []
        
        return []
    
    def extract_imports(self, file_path: str) -> List[Dict[str, Any]]:
        """Extract external dependencies/imports from source file.
        
        Args:
            file_path: Path to source file
            
        Returns:
            List of import metadata dicts with keys:
            - module_name: Name of module/namespace
            - import_type: 'using' (C#), 'require', 'import' (JS)
            - alias: Alias if present
        """
        path = Path(file_path)
        
        # Find appropriate extractor
        for extractor in self.extractors:
            if extractor.can_extract(path):
                try:
                    extracted = extractor.extract(path)
                    return self._format_imports(extracted.dependencies)
                except Exception as e:
                    logger.error(f"Error extracting imports from {file_path}: {e}")
                    return []
        
        return []
    
    def extract_sql_tables(self, file_path: str) -> List[Dict[str, Any]]:
        """Extract SQL table definitions from DDL file.
        
        Args:
            file_path: Path to SQL file
            
        Returns:
            List of table metadata dicts with keys:
            - name: Table name
            - schema: Schema name (if present)
            - columns: List of column metadata dicts
            - constraints: List of constraint definitions
            - primary_key: Primary key column(s)
            - indexes: List of index definitions
        """
        path = Path(file_path)
        
        # Find SQL extractor
        if self.sql_extractor.can_extract(path):
            try:
                extracted = self.sql_extractor.extract(path)
                return self._format_tables(extracted.tables)
            except Exception as e:
                logger.error(f"Error extracting tables from {file_path}: {e}")
                return []
        
        return []
    
    def analyze(
        self,
        file_path: str,
        extraction_types: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Analyze source file and extract specified components.
        
        Args:
            file_path: Path to source file
            extraction_types: List of extraction types to perform
                            (e.g., ['methods', 'classes', 'imports'])
                            If None, performs all applicable extractions
        
        Returns:
            Dict with keys:
            - language_detected: Detected language identifier
            - methods: Extracted methods (if applicable)
            - classes: Extracted classes (if applicable)
            - imports: Extracted imports (if applicable)
            - sql_tables: Extracted SQL tables (if applicable)
            - metadata: Extraction metadata (timestamp, extractor version, etc.)
            - extraction_errors: List of errors encountered
        """
        path = Path(file_path)
        language = self.detect_language(file_path)
        
        extraction_errors = []
        
        if not language:
            return {
                "language_detected": None,
                "metadata": {
                    "file_path": file_path,
                    "extraction_errors": [f"Unsupported file type: {path.suffix}"],
                    "extractor_version": "0.2.0",
                    "partial": True
                },
                "extraction_errors": [f"Cannot extract from {path.suffix} files"]
            }
        
        if extraction_types is None:
            # Perform all applicable extractions
            if language == 'sql':
                extraction_types = ['sql_tables']
            else:
                extraction_types = ['methods', 'classes', 'imports']
        
        result = {
            "language_detected": language,
            "metadata": {
                "file_path": file_path,
                "language": language,
                "extractor_version": "0.2.0",
                "partial": False
            },
            "extraction_errors": []
        }
        
        # Track if any extraction succeeded
        had_successful_extraction = False
        
        # Perform requested extractions
        if 'methods' in extraction_types:
            try:
                methods = self.extract_methods(file_path)
                result['methods'] = methods
                if methods:
                    had_successful_extraction = True
            except Exception as e:
                extraction_errors.append(f"Method extraction failed: {str(e)}")
        
        if 'classes' in extraction_types:
            try:
                classes = self.extract_classes(file_path)
                result['classes'] = classes
                if classes:
                    had_successful_extraction = True
            except Exception as e:
                extraction_errors.append(f"Class extraction failed: {str(e)}")
        
        if 'imports' in extraction_types:
            try:
                imports = self.extract_imports(file_path)
                result['imports'] = imports
                if imports:
                    had_successful_extraction = True
            except Exception as e:
                extraction_errors.append(f"Import extraction failed: {str(e)}")
        
        if 'sql_tables' in extraction_types:
            try:
                tables = self.extract_sql_tables(file_path)
                result['sql_tables'] = tables
                if tables:
                    had_successful_extraction = True
            except Exception as e:
                extraction_errors.append(f"SQL table extraction failed: {str(e)}")
        
        # Collect errors and mark as partial if no extractions succeeded
        if extraction_errors:
            result["metadata"]["extraction_errors"] = extraction_errors
            result["extraction_errors"] = extraction_errors
            result["metadata"]["partial"] = True
        elif not had_successful_extraction and extraction_types:
            # No errors but also no successful extractions (e.g., file not found)
            result["metadata"]["partial"] = True
        
        return result
    
    # Private formatting methods
    
    @staticmethod
    def _format_methods(methods) -> List[Dict[str, Any]]:
        """Format extracted methods for output."""
        formatted = []
        for method in methods:
            # Build signature from method name and parameters
            param_strs = [f"{p.name}: {p.type or 'Any'}" for p in method.parameters] if method.parameters else []
            signature = f"{method.name}({', '.join(param_strs)})"
            
            formatted.append({
                "name": method.name,
                "signature": signature,
                "parameters": [
                    {
                        "name": p.name,
                        "type": p.type,
                        "default": p.default_value
                    }
                    for p in method.parameters
                ] if method.parameters else [],
                "return_type": method.return_type,
                "access_level": "public" if method.is_public else "private",
                "line_number": method.line_number
            })
        return formatted
    
    @staticmethod
    def _format_classes(classes, raw_data: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """Format extracted classes for output."""
        formatted = []
        namespace = (raw_data or {}).get('namespace', '') if raw_data else ''
        
        for cls in classes:
            # Determine if it's a class or interface (for now, assume class unless metadata says otherwise)
            cls_type = "interface" if hasattr(cls, 'is_interface') and cls.is_interface else "class"
            
            formatted.append({
                "name": cls.name,
                "type": cls_type,
                "namespace": namespace or getattr(cls, 'namespace', '') or "",
                "methods": [m.name for m in cls.methods] if cls.methods else [],
                "properties": [p.get("name") if isinstance(p, dict) else str(p) for p in cls.properties] if cls.properties else [],
                "base_classes": cls.base_classes if cls.base_classes else []
            })
        return formatted
    
    @staticmethod
    def _format_imports(dependencies) -> List[Dict[str, Any]]:
        """Format extracted dependencies for output."""
        formatted = []
        for dep in dependencies:
            formatted.append({
                "module_name": dep.name,
                "import_type": dep.type,
                "alias": dep.alias if hasattr(dep, 'alias') else None
            })
        return formatted
    
    @staticmethod
    def _format_tables(tables) -> List[Dict[str, Any]]:
        """Format extracted SQL tables for output."""
        formatted = []
        for table in tables:
            formatted.append({
                "name": table.name,
                "schema": table.schema or "dbo",
                "columns": [
                    {
                        "name": col.name,
                        "type": col.data_type,  # Corrected: data_type, not type
                        "nullable": col.is_nullable,
                        "default": col.default_value,
                        "primary_key": col.is_primary_key
                    }
                    for col in table.columns
                ] if table.columns else [],
                "constraints": table.constraints if table.constraints else [],
                "primary_key": [col.name for col in table.columns if col.is_primary_key]
                               if table.columns else []
            })
        return formatted
