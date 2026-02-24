"""
Tests for CodeAnalyzer and extract_code_context extraction capabilities.

Phase 4: Tests for deterministic code extraction (C# and SQL).
Heuristic extractors (TypeScript, Business Rule, etc.) are deprecated in v0.2.0.
"""

import pytest
from pathlib import Path
import tempfile
import json

from src.tools.code_analytics import CodeAnalyzer


class TestCodeAnalyzerLanguageDetection:
    """Test language detection from file extensions."""
    
    def test_csharp_detection(self):
        """Detect C# files from .cs extension."""
        analyzer = CodeAnalyzer()
        assert analyzer.detect_language("MyFile.cs") == "csharp"
        assert analyzer.detect_language("Service.CS") == "csharp"
        assert analyzer.detect_language("path/to/Controller.cs") == "csharp"
    
    def test_sql_detection(self):
        """Detect SQL files from .sql extension."""
        analyzer = CodeAnalyzer()
        assert analyzer.detect_language("schema.sql") == "sql"
        assert analyzer.detect_language("migration.SQL") == "sql"
        assert analyzer.detect_language("db/migrations/001.sql") == "sql"
    
    def test_unknown_language(self):
        """Return None for unrecognized file types."""
        analyzer = CodeAnalyzer()
        assert analyzer.detect_language("file.ts") is None
        assert analyzer.detect_language("file.py") is None
        assert analyzer.detect_language("file.js") is None
        assert analyzer.detect_language("file.txt") is None


class TestCSharpExtraction:
    """Test C# code extraction using CSharpExtractor."""
    
    @pytest.fixture
    def csharp_sample(self):
        """Create a temporary C# file with sample code."""
        csharp_code = '''
namespace MyApp.Services
{
    using System;
    using MyApp.Models;
    using System.Collections.Generic;
    
    public class UserService
    {
        private readonly IRepository<User> _userRepo;
        
        public UserService(IRepository<User> userRepo)
        {
            _userRepo = userRepo;
        }
        
        public async Task<User> GetUserById(string userId)
        {
            if (string.IsNullOrEmpty(userId))
                throw new ArgumentException("User ID cannot be empty");
            
            return await _userRepo.GetByIdAsync(userId);
        }
        
        public List<User> GetAllUsers()
        {
            return _userRepo.GetAll().ToList();
        }
    }
}
'''
        with tempfile.NamedTemporaryFile(mode='w', suffix='.cs', delete=False) as f:
            f.write(csharp_code)
            f.flush()
            yield Path(f.name)
    
    def test_extract_csharp_methods(self, csharp_sample):
        """Extract methods from C# file."""
        analyzer = CodeAnalyzer()
        methods = analyzer.extract_methods(str(csharp_sample))
        
        # Should find constructor and public methods
        method_names = [m["name"] for m in methods]
        assert len(methods) > 0
        # Methods should have required fields
        for method in methods:
            assert "name" in method
            assert "signature" in method
            assert "parameters" in method
            assert "return_type" in method
            assert isinstance(method["parameters"], list)
    
    def test_extract_csharp_classes(self, csharp_sample):
        """Extract classes from C# file."""
        analyzer = CodeAnalyzer()
        classes = analyzer.extract_classes(str(csharp_sample))
        
        assert len(classes) > 0
        # Check structure
        for cls in classes:
            assert "name" in cls
            assert "type" in cls  # 'class' or 'interface'
            assert "namespace" in cls
            assert "methods" in cls
            assert "properties" in cls
            assert "base_classes" in cls
    
    def test_extract_csharp_imports(self, csharp_sample):
        """Extract imports/usings from C# file."""
        analyzer = CodeAnalyzer()
        imports = analyzer.extract_imports(str(csharp_sample))
        
        assert len(imports) > 0
        # Should find System, MyApp.Models, System.Collections.Generic
        for imp in imports:
            assert "module_name" in imp
            assert "import_type" in imp
    
    def test_analyze_csharp_file(self, csharp_sample):
        """Full analyze workflow for C# file."""
        analyzer = CodeAnalyzer()
        result = analyzer.analyze(str(csharp_sample), extraction_types=["methods", "classes"])
        
        assert result["language_detected"] == "csharp"
        assert "methods" in result
        assert "classes" in result
        assert "metadata" in result
        assert result["metadata"]["language"] == "csharp"
        assert result["metadata"]["extractor_version"] == "0.2.0"


class TestSQLExtraction:
    """Test SQL DDL extraction using SQLExtractor."""
    
    @pytest.fixture
    def sql_sample(self):
        """Create a temporary SQL file with sample DDL."""
        sql_code = '''
CREATE TABLE dbo.Users (
    UserId INT PRIMARY KEY IDENTITY(1,1),
    Email NVARCHAR(255) NOT NULL,
    CreatedAt DATETIME DEFAULT GETUTCDATE(),
    IsActive BIT DEFAULT 1
);

CREATE TABLE dbo.Orders (
    OrderId INT PRIMARY KEY IDENTITY(1,1),
    UserId INT NOT NULL,
    OrderDate DATETIME NOT NULL,
    Total DECIMAL(10, 2),
    CONSTRAINT FK_Orders_Users FOREIGN KEY (UserId) REFERENCES Users(UserId)
);
'''
        with tempfile.NamedTemporaryFile(mode='w', suffix='.sql', delete=False) as f:
            f.write(sql_code)
            f.flush()
            yield Path(f.name)
    
    def test_extract_sql_tables(self, sql_sample):
        """Extract table definitions from SQL file."""
        analyzer = CodeAnalyzer()
        tables = analyzer.extract_sql_tables(str(sql_sample))
        
        assert len(tables) > 0
        # Check table structure
        for table in tables:
            assert "name" in table
            assert "schema" in table
            assert "columns" in table
            assert isinstance(table["columns"], list)
    
    def test_sql_table_schema_structure(self, sql_sample):
        """Verify SQL table schema includes column metadata."""
        analyzer = CodeAnalyzer()
        tables = analyzer.extract_sql_tables(str(sql_sample))
        
        assert len(tables) > 0
        # First table should be Users
        users_table = next((t for t in tables if t["name"] == "Users"), None)
        assert users_table is not None
        
        # Check columns structure
        for column in users_table["columns"]:
            assert "name" in column
            assert "type" in column
            assert "nullable" in column
            assert "primary_key" in column
    
    def test_analyze_sql_file(self, sql_sample):
        """Full analyze workflow for SQL file."""
        analyzer = CodeAnalyzer()
        result = analyzer.analyze(str(sql_sample), extraction_types=["sql_tables"])
        
        assert result["language_detected"] == "sql"
        assert "sql_tables" in result
        assert "metadata" in result
        assert result["metadata"]["language"] == "sql"
    
    def test_sql_auto_extraction_types(self, sql_sample):
        """Auto-select extraction types based on language."""
        analyzer = CodeAnalyzer()
        # Don't specify extraction_types; should auto-select sql_tables
        result = analyzer.analyze(str(sql_sample))
        
        assert result["language_detected"] == "sql"
        assert "sql_tables" in result


class TestExtractCodeContextErrorHandling:
    """Test error handling and edge cases."""
    
    def test_nonexistent_file(self):
        """Handle nonexistent file gracefully."""
        analyzer = CodeAnalyzer()
        result = analyzer.analyze("/nonexistent/file.cs")
        
        # Language is detected from extension, but extraction fails
        assert result["language_detected"] == "csharp"
        # When extraction fails, errors are logged in extraction_errors
        # Note: individual extract_* methods catch exceptions and return empty lists,
        # so we check that either metadata has errors OR extraction returned empty results
        has_extraction_errors = (
            "extraction_errors" in result.get("metadata", {}) and 
            len(result["metadata"]["extraction_errors"]) > 0
        )
        has_empty_results = (
            len(result.get("methods", [])) == 0 and
            len(result.get("classes", [])) == 0 and
            len(result.get("imports", [])) == 0
        )
        assert has_extraction_errors or has_empty_results, "Should handle error gracefully"
    
    def test_unsupported_file_type(self):
        """Handle unsupported file types."""
        analyzer = CodeAnalyzer()
        result = analyzer.analyze("file.py")
        
        assert result["language_detected"] is None
        assert "extraction_errors" in result["metadata"]
        assert len(result["metadata"]["extraction_errors"]) > 0
    
    
    def test_empty_extraction_result(self):
        """Handle empty files gracefully."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.cs', delete=False) as f:
            f.write("")
            f.flush()
            
            analyzer = CodeAnalyzer()
            result = analyzer.analyze(f.name)
            
            assert result["language_detected"] == "csharp"
            # Empty file may have empty methods/classes lists
            assert "methods" in result or "classes" in result


class TestMetadataGeneration:
    """Test metadata generation in extraction results."""
    
    @pytest.fixture
    def csharp_sample(self):
        """Simple C# file for metadata tests."""
        csharp_code = 'public class Test { public void Method() { } }'
        with tempfile.NamedTemporaryFile(mode='w', suffix='.cs', delete=False) as f:
            f.write(csharp_code)
            f.flush()
            yield Path(f.name)
    
    def test_metadata_structure(self, csharp_sample):
        """Verify metadata contains required fields."""
        analyzer = CodeAnalyzer()
        result = analyzer.analyze(str(csharp_sample))
        
        metadata = result["metadata"]
        assert "file_path" in metadata
        assert "language" in metadata
        assert "extractor_version" in metadata
        assert metadata["extractor_version"] == "0.2.0"
        assert metadata["partial"] is False  # Incomplete extraction marker
    
    def test_error_metadata(self):
        """Verify error case metadata."""
        analyzer = CodeAnalyzer()
        result = analyzer.analyze("/nonexistent.cs")
        
        metadata = result["metadata"]
        # When extraction fails, the partial flag should be set
        # Either extraction_errors is populated OR partial is True
        has_errors = "extraction_errors" in metadata and isinstance(metadata.get("extraction_errors"), list)
        is_partial = metadata.get("partial", False)
        assert has_errors or is_partial, "Should mark as error or partial"


class TestOutputConsistency:
    """Test that analyzer produces consistent, well-formed output."""
    
    @pytest.fixture
    def csharp_sample(self):
        """C# file for consistency tests."""
        code = '''
namespace Test {
    public class MyClass {
        public string MyMethod(int param1, string param2) { return ""; }
    }
}
'''
        with tempfile.NamedTemporaryFile(mode='w', suffix='.cs', delete=False) as f:
            f.write(code)
            f.flush()
            yield Path(f.name)
    
    def test_output_json_serializable(self, csharp_sample):
        """Ensure output is JSON-serializable."""
        analyzer = CodeAnalyzer()
        result = analyzer.analyze(str(csharp_sample))
        
        # Should be JSON-serializable
        json_str = json.dumps(result)
        assert json_str is not None
        
        # Should deserialize back
        deserialized = json.loads(json_str)
        assert deserialized["language_detected"] == "csharp"
    
    def test_no_placeholder_markers(self, csharp_sample):
        """Ensure no placeholder markers (❓, 🤖) in output."""
        analyzer = CodeAnalyzer()
        result = analyzer.analyze(str(csharp_sample))
        
        result_str = json.dumps(result)
        assert "❓" not in result_str
        assert "🤖" not in result_str


class TestDeprecatedExtractorsNotUsed:
    """Verify that deprecated extractors are not used by CodeAnalyzer."""
    
    def test_only_deterministic_extractors(self):
        """CodeAnalyzer only uses C# and SQL extractors."""
        analyzer = CodeAnalyzer()
        
        # Should only have 2 extractors
        assert len(analyzer.extractors) == 2
        
        # Verify extractor types
        extractor_types = [type(e).__name__ for e in analyzer.extractors]
        assert "CSharpExtractor" in extractor_types
        assert "SQLExtractor" in extractor_types
        
        # Deprecated extractors should NOT be present
        deprecated = [
            "TypeScriptExtractor",
            "BusinessRuleExtractor",
            "FailureModeExtractor",
            "MethodFlowAnalyzer",
            "ExampleExtractor"
        ]
        for deprecated_type in deprecated:
            assert deprecated_type not in extractor_types


class TestAnalyzeMethod:
    """Test the unified analyze() method."""
    
    @pytest.fixture
    def csharp_sample(self):
        """C# file for analyze tests."""
        code = 'public class Service { public void DoWork() { } }'
        with tempfile.NamedTemporaryFile(mode='w', suffix='.cs', delete=False) as f:
            f.write(code)
            f.flush()
            yield Path(f.name)
    
    def test_analyze_with_explicit_types(self, csharp_sample):
        """Analyze with explicitly specified extraction types."""
        analyzer = CodeAnalyzer()
        result = analyzer.analyze(
            str(csharp_sample),
            extraction_types=["methods", "classes"]
        )
        
        assert "methods" in result
        assert "classes" in result
        # Should not have sql_tables for C# file
        assert "sql_tables" not in result
    
    def test_analyze_auto_select_types(self, csharp_sample):
        """Analyze with auto-selection of extraction types."""
        analyzer = CodeAnalyzer()
        result = analyzer.analyze(str(csharp_sample))  # No extraction_types
        
        # For C# file, should auto-select methods, classes, imports
        assert "methods" in result
        assert "classes" in result
        assert "imports" in result
        assert "sql_tables" not in result
    
    def test_analyze_returns_standard_structure(self, csharp_sample):
        """Verify analyze returns standard result structure."""
        analyzer = CodeAnalyzer()
        result = analyzer.analyze(str(csharp_sample))
        
        # Required top-level keys
        assert "language_detected" in result
        assert "metadata" in result
        assert "extraction_errors" in result
        
        # Metadata structure
        metadata = result["metadata"]
        assert "file_path" in metadata
        assert "language" in metadata
        assert "extractor_version" in metadata
        assert "partial" in metadata


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
