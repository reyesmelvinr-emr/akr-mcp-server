"""
SQL code extractor for analyzing database schema files.

Extracts table definitions, columns, constraints, indexes, and foreign keys
from SQL DDL (CREATE TABLE) statements.
"""

import re
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any

from .base_extractor import (
    BaseExtractor, ExtractedData, ExtractedTable, ExtractedColumn
)


logger = logging.getLogger(__name__)


class SQLExtractor(BaseExtractor):
    """Extractor for SQL DDL source files."""
    
    def can_extract(self, file_path: Path) -> bool:
        """Check if file is a SQL source file."""
        return file_path.suffix.lower() in ['.sql']
    
    def extract(self, file_path: Path) -> ExtractedData:
        """Extract information from SQL source file."""
        logger.info(f"Extracting SQL data from {file_path}")
        
        # Read file content
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            raise Exception(f"Failed to read file: {e}")
        
        # Initialize extracted data
        data = ExtractedData(language='sql', file_path=str(file_path))
        
        try:
            # Extract table definitions
            tables = self._extract_tables(content)
            data.tables = tables
            
        except Exception as e:
            data.extraction_errors.append(f"Extraction error: {str(e)}")
            logger.error(f"Error extracting from {file_path}: {e}", exc_info=True)
        
        return data
    
    def _extract_tables(self, content: str) -> List[ExtractedTable]:
        """Extract CREATE TABLE statements."""
        tables = []
        
        # Pattern: CREATE TABLE [schema].[tablename] (...)
        # This handles single-line and multi-line CREATE TABLE statements
        table_pattern = r'CREATE\s+TABLE\s+(?:\[?(\w+)\]?\.)?\[?(\w+)\]?\s*\((.*?)\)(?:\s+(?:WITH|ON).*?)?;'
        
        for match in re.finditer(table_pattern, content, re.IGNORECASE | re.DOTALL):
            schema = match.group(1)
            table_name = match.group(2)
            table_body = match.group(3)
            
            # Extract columns
            columns = self._extract_columns(table_body)
            
            # Extract constraints
            constraints = self._extract_table_constraints(table_body)
            
            table = ExtractedTable(
                name=table_name,
                schema=schema,
                columns=columns,
                constraints=constraints
            )
            tables.append(table)
            
            logger.debug(f"Extracted table: {schema}.{table_name} with {len(columns)} columns")
        
        # Extract indexes separately (CREATE INDEX statements)
        for table in tables:
            indexes = self._extract_indexes(content, table.name)
            table.indexes = indexes
        
        return tables
    
    def _extract_columns(self, table_body: str) -> List[ExtractedColumn]:
        """Extract column definitions from table body."""
        columns = []
        
        # Split by comma, but respect nested parentheses (for CHECK constraints, etc.)
        column_definitions = self._split_column_definitions(table_body)
        
        for col_def in column_definitions:
            col_def = col_def.strip()
            
            # Skip constraint definitions (they start with CONSTRAINT or key keywords)
            if re.match(r'^\s*(?:CONSTRAINT|PRIMARY|FOREIGN|UNIQUE|CHECK|INDEX|KEY)\s+', col_def, re.IGNORECASE):
                continue
            
            # Parse column definition
            column = self._parse_column_definition(col_def)
            if column:
                columns.append(column)
                logger.debug(f"Extracted column: {column.name} ({column.data_type})")
        
        return columns
    
    def _parse_column_definition(self, col_def: str) -> Optional[ExtractedColumn]:
        """Parse a single column definition."""
        
        # Pattern: [ColumnName] DataType [(size)] [NULL|NOT NULL] [DEFAULT value] [other constraints]
        # Remove brackets around column name
        col_def = re.sub(r'^\[([^\]]+)\]', r'\1', col_def)
        
        # Extract column name (first word)
        parts = col_def.split(None, 1)
        if len(parts) < 2:
            return None
        
        column_name = parts[0].strip('[]')
        rest = parts[1]
        
        # Extract data type (next word, may include size)
        data_type_match = re.match(r'(\w+)(?:\(([^)]+)\))?', rest)
        if not data_type_match:
            return None
        
        data_type = data_type_match.group(1)
        data_size = data_type_match.group(2)
        if data_size:
            data_type += f"({data_size})"
        
        # Check for NOT NULL
        is_nullable = 'NOT NULL' not in col_def.upper()
        
        # Extract default value
        default_value = None
        default_match = re.search(r'DEFAULT\s+([^,\s]+(?:\s+[^,\s]+)*?)(?:\s+(?:NULL|NOT|PRIMARY|FOREIGN|UNIQUE|CHECK|REFERENCES|,|$))', 
                                 col_def, re.IGNORECASE)
        if default_match:
            default_value = default_match.group(1).strip()
        
        # Check for PRIMARY KEY
        is_primary_key = bool(re.search(r'\bPRIMARY\s+KEY\b', col_def, re.IGNORECASE))
        
        # Check for FOREIGN KEY / REFERENCES
        is_foreign_key = False
        foreign_key_table = None
        foreign_key_column = None
        
        fk_match = re.search(r'REFERENCES\s+\[?(\w+)\]?(?:\.\[?(\w+)\]?)?\s*\(\[?(\w+)\]?\)', col_def, re.IGNORECASE)
        if fk_match:
            is_foreign_key = True
            # Handle schema.table or just table
            if fk_match.group(2):
                foreign_key_table = f"{fk_match.group(1)}.{fk_match.group(2)}"
                foreign_key_column = fk_match.group(3) if len(fk_match.groups()) > 2 else None
            else:
                foreign_key_table = fk_match.group(1)
                foreign_key_column = fk_match.group(2) if fk_match.group(2) else None
        
        # Extract other constraints
        constraints = []
        if 'UNIQUE' in col_def.upper():
            constraints.append('UNIQUE')
        if 'IDENTITY' in col_def.upper():
            constraints.append('IDENTITY')
        if 'AUTO_INCREMENT' in col_def.upper():
            constraints.append('AUTO_INCREMENT')
        
        # Extract CHECK constraints
        check_match = re.search(r'CHECK\s*\(([^)]+)\)', col_def, re.IGNORECASE)
        if check_match:
            constraints.append(f"CHECK ({check_match.group(1)})")
        
        column = ExtractedColumn(
            name=column_name,
            data_type=data_type,
            is_nullable=is_nullable,
            default_value=default_value,
            is_primary_key=is_primary_key,
            is_foreign_key=is_foreign_key,
            foreign_key_table=foreign_key_table,
            foreign_key_column=foreign_key_column,
            constraints=constraints
        )
        
        return column
    
    def _extract_table_constraints(self, table_body: str) -> List[str]:
        """Extract table-level constraints (PRIMARY KEY, FOREIGN KEY, etc.)."""
        constraints = []
        
        # Split by comma, respect parentheses
        definitions = self._split_column_definitions(table_body)
        
        for definition in definitions:
            definition = definition.strip()
            
            # Check if it's a constraint definition
            if re.match(r'^\s*(?:CONSTRAINT|PRIMARY|FOREIGN|UNIQUE|CHECK)\s+', definition, re.IGNORECASE):
                # Clean up the constraint
                constraint = re.sub(r'\s+', ' ', definition).strip()
                constraints.append(constraint)
                logger.debug(f"Extracted constraint: {constraint[:50]}...")
        
        return constraints
    
    def _extract_indexes(self, content: str, table_name: str) -> List[Dict[str, Any]]:
        """Extract CREATE INDEX statements for a specific table."""
        indexes = []
        
        # Pattern: CREATE [UNIQUE] INDEX IndexName ON TableName (columns)
        index_pattern = rf'CREATE\s+(UNIQUE\s+)?(?:(?:CLUSTERED|NONCLUSTERED)\s+)?INDEX\s+\[?(\w+)\]?\s+ON\s+(?:\[?\w+\]?\.)?\[?{table_name}\]?\s*\(([^)]+)\)'
        
        for match in re.finditer(index_pattern, content, re.IGNORECASE):
            is_unique = bool(match.group(1))
            index_name = match.group(2)
            columns_str = match.group(3)
            
            # Parse column names
            columns = [col.strip().strip('[]') for col in columns_str.split(',')]
            
            index = {
                'name': index_name,
                'columns': columns,
                'is_unique': is_unique
            }
            indexes.append(index)
            
            logger.debug(f"Extracted index: {index_name} on {', '.join(columns)}")
        
        return indexes
    
    def _split_column_definitions(self, table_body: str) -> List[str]:
        """Split table body by commas, respecting nested parentheses."""
        definitions = []
        current = []
        paren_depth = 0
        
        for char in table_body:
            if char == '(':
                paren_depth += 1
            elif char == ')':
                paren_depth -= 1
            
            if char == ',' and paren_depth == 0:
                definitions.append(''.join(current))
                current = []
            else:
                current.append(char)
        
        if current:
            definitions.append(''.join(current))
        
        return definitions
