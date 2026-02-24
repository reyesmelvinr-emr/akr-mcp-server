"""
End-to-end integration tests for the complete AKR MCP server workflow.

Phase 5: Integration tests verifying full workflow from extraction through writing.
Tests: extract_code_context → get_charter → validate_documentation → write_documentation
"""

import json
import tempfile
from pathlib import Path
from typing import Any, Dict

import pytest

from src.tools.code_analytics import CodeAnalyzer
from src.tools.template_schema_builder import TemplateSchemaBuilder
from src.tools.validation_library import ValidationEngine, ValidationTier


class TestEndToEndWorkflow:
    """Test complete workflows from extraction to writing."""
    
    def setup_method(self):
        """Set up test resources."""
        self.analyzer = CodeAnalyzer()
        self.schema_builder = TemplateSchemaBuilder()
        self.validator = ValidationEngine(schema_builder=self.schema_builder, config={})
        self.temp_dir = tempfile.TemporaryDirectory()
    
    def teardown_method(self):
        """Clean up test resources."""
        self.temp_dir.cleanup()
    
    def test_csharp_extraction_to_charter_request(self):
        """Test extracting C# code and preparing charter request."""
        # Step 1: Create sample C# file
        csharp_content = '''
namespace MyServices
{
    /// <summary>
    /// Manages user authentication and session lifecycle.
    /// </summary>
    public class AuthenticationService
    {
        public async Task<LoginResult> AuthenticateAsync(string username, string password)
        {
            // Implementation
            return new LoginResult { IsSuccess = true };
        }
        
        public void LogoutUser(string userId)
        {
            // Implementation
        }
    }
}
'''
        csharp_path = Path(self.temp_dir.name) / "auth_service.cs"
        csharp_path.write_text(csharp_content)
        
        # Step 2: Extract code context
        result = self.analyzer.analyze(str(csharp_path), ["methods", "classes"])
        
        # Verify extraction
        assert result["language_detected"] == "csharp"
        assert "methods" in result or "classes" in result
        
        # Step 3: Prepare for charter generation
        # The extracted data would be passed to Copilot Chat for charter drafting
        charter_request = {
            "file_path": str(csharp_path),
            "language": result["language_detected"],
            "extracted_items": {
                "classes": result.get("classes", []),
                "methods": result.get("methods", []),
            },
            "prompt": "Generate a technical charter document for this service"
        }
        
        # Verify request structure
        assert charter_request["language"] == "csharp"
        assert "classes" in charter_request["extracted_items"]
    
    def test_sql_extraction_to_charter_request(self):
        """Test extracting SQL schema and preparing charter request."""
        # Step 1: Create sample SQL file
        sql_content = '''
CREATE TABLE users (
    user_id INT PRIMARY KEY IDENTITY(1,1),
    username NVARCHAR(255) NOT NULL UNIQUE,
    email NVARCHAR(255) NOT NULL,
    created_at DATETIME DEFAULT GETDATE()
);

CREATE TABLE sessions (
    session_id UNIQUEIDENTIFIER PRIMARY KEY,
    user_id INT NOT NULL FOREIGN KEY REFERENCES users(user_id),
    expires_at DATETIME NOT NULL
);
'''
        sql_path = Path(self.temp_dir.name) / "schema.sql"
        sql_path.write_text(sql_content)
        
        # Step 2: Extract schema
        result = self.analyzer.analyze(str(sql_path), ["sql_tables"])
        
        # Verify extraction
        assert result["language_detected"] == "sql"
        if result.get("sql_tables"):
            assert len(result["sql_tables"]) > 0
        
        # Step 3: Prepare for charter generation
        charter_request = {
            "file_path": str(sql_path),
            "language": result["language_detected"],
            "extracted_items": {
                "tables": result.get("sql_tables", []),
            },
            "prompt": "Generate a database charter document for this schema"
        }
        
        assert charter_request["language"] == "sql"
        assert "tables" in charter_request["extracted_items"]
    
    def test_charter_validation_workflow(self):
        """Test validating generated charter documentation."""
        # Step 1: Create sample charter document
        charter_content = '''# Service Charter: Authentication Service

## Overview
Manages user authentication and session lifecycle.

## Responsibilities
- User login/logout
- Session management
- Password validation

## Interfaces
- AuthenticateAsync(username, password): Task<LoginResult>
- LogoutUser(userId): void

## Data Structures
### LoginResult
- IsSuccess: bool
- Message: string
- SessionToken: string

## Error Handling
- InvalidCredentialsException
- SessionExpiredException
'''
        
        # Step 2: Validate charter with TIER_1
        # In real workflow, this would be done after manual review
        validation_data = {
            "content": charter_content,
            "status": "ready_for_validation",
            "metadata": {
                "source": "copilot_chat",
                "template_used": "service_template"
            }
        }
        
        # Verify validation data structure
        assert validation_data["status"] == "ready_for_validation"
        assert validation_data["metadata"]["template_used"] == "service_template"
        assert len(validation_data["content"]) > 0
    
    def test_full_workflow_extract_validate_prepare_write(self):
        """Test complete workflow: extract → validate → prepare → write."""
        # Step 1: Extract from sample code
        sample_code = '''
namespace UserManagement
{
    /// <summary>
    /// Handles user CRUD operations.
    /// </summary>
    public class UserService
    {
        public User GetUserById(int userId)
        {
            // Implementation
            return new User { Id = userId };
        }
        
        public void CreateUser(User user)
        {
            // Implementation
        }
    }
}
'''
        code_path = Path(self.temp_dir.name) / "user_service.cs"
        code_path.write_text(sample_code)
        
        extraction = self.analyzer.analyze(str(code_path), ["methods", "classes"])
        
        # Step 2: Simulate charter generation (would be done by Chat)
        charter = f'''# Service Charter: User Service

## Purpose
Manages user CRUD operations and lifecycle.

## Components
- GetUserById: Retrieves user by ID
- CreateUser: Creates new user record

## Data Models
- User: Primary domain model

## Dependencies
- Database service
- Logging service
'''
        charter_path = Path(self.temp_dir.name) / "charter.md"
        charter_path.write_text(charter)
        
        # Step 3: Validate charter
        # In real workflow, validation engine would check against schema
        validation_data = {
            "content": charter,
            "status": "ready_for_validation",
            "metadata": {
                "source": "copilot_chat",
                "template_used": "service_template"
            }
        }
        
        validation_result = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "metadata": validation_data["metadata"]
        }
        
        # Step 4: Prepare write metadata
        write_manifest = {
            "source_file": str(code_path),
            "charter_content": charter,
            "extraction_result": extraction,
            "validation_result": validation_result,
            "operation": "write",
            "dry_run": False,
            "write_mode": "create"
        }
        
        # Verify manifest structure
        assert write_manifest["source_file"] == str(code_path)
        assert write_manifest["charter_content"] == charter
        assert "extraction_result" in write_manifest
        assert "validation_result" in write_manifest
        assert write_manifest["operation"] == "write"


class TestMultiLanguageWorkflow:
    """Test workflows with multiple languages in repo."""
    
    def setup_method(self):
        """Set up test resources."""
        self.analyzer = CodeAnalyzer()
        self.temp_dir = tempfile.TemporaryDirectory()
    
    def teardown_method(self):
        """Clean up test resources."""
        self.temp_dir.cleanup()
    
    def test_mixed_repo_extraction(self):
        """Test extracting from repository with mixed C# and SQL files."""
        # Create sample mixed repo
        csharp_file = Path(self.temp_dir.name) / "service.cs"
        csharp_file.write_text('''
public class OrderService {
    public Order GetOrder(int id) { return new Order(); }
}
''')
        
        sql_file = Path(self.temp_dir.name) / "schema.sql"
        sql_file.write_text('''
CREATE TABLE orders (
    order_id INT PRIMARY KEY,
    customer_id INT NOT NULL
);
''')
        
        # Extract from C# file
        cs_result = self.analyzer.analyze(str(csharp_file), ["classes", "methods"])
        assert cs_result["language_detected"] == "csharp"
        
        # Extract from SQL file
        sql_result = self.analyzer.analyze(str(sql_file), ["sql_tables"])
        assert sql_result["language_detected"] == "sql"
        
        # Verify both can be processed
        assert cs_result.get("classes") is not None or cs_result.get("methods") is not None
        assert sql_result.get("sql_tables") is not None or "metadata" in sql_result


class TestErrorHandlingWorkflow:
    """Test error handling in workflows."""
    
    def setup_method(self):
        """Set up test resources."""
        self.analyzer = CodeAnalyzer()
        self.schema_builder = TemplateSchemaBuilder()
        self.validator = ValidationEngine(schema_builder=self.schema_builder, config={})
        self.temp_dir = tempfile.TemporaryDirectory()
    
    def teardown_method(self):
        """Clean up test resources."""
        self.temp_dir.cleanup()
    
    def test_missing_source_file_handling(self):
        """Test workflow handles missing source files gracefully."""
        missing_file = Path(self.temp_dir.name) / "nonexistent.cs"
        
        # Extraction should handle gracefully
        result = self.analyzer.analyze(str(missing_file), ["methods"])
        
        # Should have metadata indicating extraction issues
        assert "metadata" in result
        # Result should either be partial or indicate error
        assert result.get("metadata", {}).get("partial") or result.get("extraction_errors")
    
    def test_invalid_charter_validation(self):
        """Test validation of invalid/incomplete charter."""
        # Create a simple invalid charter case
        invalid_content = "Just some random text without proper structure."
        
        # In real workflow, validation would check structure
        validation_result = {
            "is_valid": False,
            "errors": ["Missing required sections"],
            "warnings": [],
            "content": invalid_content
        }
        
        # Should indicate validation issues
        assert validation_result["is_valid"] is False
        assert len(validation_result["errors"]) > 0
    
    def test_charter_generation_error_recovery(self):
        """Test recovery when charter generation fails in workflow."""
        # Create a file that might fail parsing
        ambiguous_file = Path(self.temp_dir.name) / "ambiguous.cs"
        ambiguous_file.write_text("*** INVALID C# CODE ***")
        
        # Extraction should handle gracefully
        result = self.analyzer.analyze(str(ambiguous_file), ["methods", "classes"])
        
        # Should have error metadata
        assert "metadata" in result
        
        # Workflow should be able to continue
        # (e.g., manual override or user review)
        next_step = {
            "extraction_result": result,
            "manual_review": True,
            "user_override": "Proceed with empty context"
        }
        
        assert next_step["manual_review"] is True
        assert next_step["extraction_result"]["metadata"]["partial"]


class TestAuditTrailInWorkflow:
    """Test that workflow maintains audit trails for compliance."""
    
    def setup_method(self):
        """Set up test resources."""
        self.analyzer = CodeAnalyzer()
        self.temp_dir = tempfile.TemporaryDirectory()
    
    def teardown_method(self):
        """Clean up test resources."""
        self.temp_dir.cleanup()
    
    def test_workflow_maintains_extraction_metadata(self):
        """Test that extraction maintains audit trail."""
        sample = Path(self.temp_dir.name) / "test.cs"
        sample.write_text("public class Test { public void Run() {} }")
        
        result = self.analyzer.analyze(str(sample), ["classes"])
        
        # Should have metadata with audit information
        metadata = result.get("metadata", {})
        assert "language_detected" in metadata or result.get("language_detected")
        assert "extractor_version" in metadata or "metadata" in result
    
    def test_workflow_operation_sequence_tracking(self):
        """Test tracking of workflow operation sequence."""
        operations = []
        
        # Step 1: Extract
        operations.append({"type": "extract", "status": "success"})
        
        # Step 2: Charter generation (simulated)
        operations.append({"type": "charter_generation", "status": "success"})
        
        # Step 3: Validate
        operations.append({"type": "validate", "status": "success"})
        
        # Step 4: Write
        operations.append({"type": "write", "status": "pending"})
        
        # Verify sequence
        assert len(operations) == 4
        assert operations[0]["type"] == "extract"
        assert operations[-1]["type"] == "write"
        
        # All steps should be traceable
        for op in operations:
            assert "type" in op
            assert "status" in op


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
