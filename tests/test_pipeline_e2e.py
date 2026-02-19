"""
End-to-end tests for the documentation generation pipeline

Tests the full flow from code extraction to rendered documentation.
"""

import pytest
from pathlib import Path
from src.tools.extractors.base_extractor import (
    ExtractedData, ExtractedRoute, ExtractedDependency, ExtractedValidation,
    ExtractedComponent, ExtractedProp, ExtractedTable, ExtractedColumn
)
from src.tools.context_builder import (
    build_service_context, build_component_context, build_table_context
)
from src.tools.template_renderer import TemplateRenderer


class TestE2EPipelineBackendService:
    """End-to-end tests for backend service documentation."""
    
    def test_e2e_backend_service_extraction_to_rendering(self):
        """
        Test complete pipeline: extract backend service → build context → render docs
        
        This simulates the real workflow:
        1. Code extraction produces ExtractedData
        2. Context builder transforms to ServiceTemplateContext
        3. Template renderer produces markdown
        """
        # Step 1: Simulate code extraction
        route1 = ExtractedRoute(
            method="GET",
            path="/api/users",
            handler_name="GetUsers",
            response_types=["List<User>"],
            status_codes=[200]
        )
        route2 = ExtractedRoute(
            method="POST",
            path="/api/users",
            handler_name="CreateUser",
            response_types=["User"],
            status_codes=[201, 400]
        )
        
        dep1 = ExtractedDependency(
            name="IUserRepository",
            type="Interface",
            description="User data access repository"
        )
        
        val1 = ExtractedValidation(
            field_name="Email",
            rule_type="NotEmpty",
            error_message="Email is required"
        )
        val2 = ExtractedValidation(
            field_name="Email",
            rule_type="EmailAddress",
            error_message="Email format is invalid"
        )
        
        extracted = ExtractedData(language="csharp", file_path="UserService.cs")
        extracted.routes = [route1, route2]
        extracted.dependencies = [dep1]
        extracted.validations = [val1, val2]
        
        # Step 2: Build context
        context = build_service_context(
            service_name="UserService",
            extracted_data_list=[extracted],
            namespace="MyApp.Services",
            domain="UserManagement"
        )
        
        # Verify context was built correctly
        assert context.service_name == "UserService"
        assert len(context.endpoints) == 2
        assert len(context.dependencies) == 1
        assert len(context.validation_rules) == 2
        
        # Step 3: Render documentation
        renderer = TemplateRenderer()
        markdown = renderer.render_service_template(context)
        
        # Verify rendered output
        assert isinstance(markdown, str)
        assert len(markdown) > 500  # Should be substantial
        assert "UserService" in markdown
        assert "GET" in markdown or "get" in markdown.lower()
        assert "POST" in markdown or "post" in markdown.lower()
        assert "/api/users" in markdown
        assert "IUserRepository" in markdown
        assert "User data access" in markdown
    
    def test_e2e_backend_empty_service_includes_placeholders(self):
        """Test that empty service includes AI placeholders for human input."""
        extracted = ExtractedData(language="csharp", file_path="EmptyService.cs")
        
        context = build_service_context(
            service_name="EmptyService",
            extracted_data_list=[extracted]
        )
        
        renderer = TemplateRenderer()
        markdown = renderer.render_service_template(context)
        
        # Should include placeholders
        assert "🤖" in markdown or "placeholder" in markdown.lower()
        assert "EmptyService" in markdown
    
    def test_e2e_multiple_services_combined(self):
        """Test combining extraction from multiple services."""
        # Service 1
        route1 = ExtractedRoute(method="GET", path="/api/users", handler_name="GetUsers")
        extracted1 = ExtractedData(language="csharp", file_path="UserService.cs")
        extracted1.routes = [route1]
        
        # Service 2 (additional routes)
        route2 = ExtractedRoute(method="POST", path="/api/users/register", handler_name="Register")
        extracted2 = ExtractedData(language="csharp", file_path="AuthService.cs")
        extracted2.routes = [route2]
        
        # Build combined context
        context = build_service_context(
            service_name="UserAuthService",
            extracted_data_list=[extracted1, extracted2]
        )
        
        assert len(context.endpoints) == 2
        
        renderer = TemplateRenderer()
        markdown = renderer.render_service_template(context)
        
        assert "/api/users" in markdown
        assert "/api/users/register" in markdown or "register" in markdown.lower()


class TestE2EPipelineUIComponent:
    """End-to-end tests for UI component documentation."""
    
    def test_e2e_component_extraction_to_rendering(self):
        """
        Test complete pipeline for UI component documentation
        """
        # Step 1: Extract component
        prop1 = ExtractedProp(
            name="onClick",
            type="(event: React.MouseEvent) => void",
            is_required=True,
            description="Callback fired on click"
        )
        prop2 = ExtractedProp(
            name="disabled",
            type="boolean",
            is_required=False,
            default="false",
            description="Disable the button"
        )
        
        component = ExtractedComponent(
            name="Button",
            props=[prop1, prop2],
            state_variables=[
                {"name": "isLoading", "type": "boolean", "initial_value": "false"}
            ]
        )
        
        extracted = ExtractedData(language="typescript", file_path="Button.tsx")
        extracted.components = [component]
        
        # Step 2: Build context
        context = build_component_context(
            component_name="Button",
            extracted_data_list=[extracted]
        )
        
        assert context.component_name == "Button"
        assert len(context.props) == 2
        assert len(context.state_vars) == 1
        
        # Step 3: Render documentation
        renderer = TemplateRenderer()
        markdown = renderer.render_component_template(context)
        
        # Verify output
        assert isinstance(markdown, str)
        assert len(markdown) > 300
        assert "Button" in markdown
        assert "onClick" in markdown
        assert "disabled" in markdown
        assert "isLoading" in markdown
    
    def test_e2e_component_with_events(self):
        """Test component documentation with events."""
        component = ExtractedComponent(
            name="Modal",
            props=[ExtractedProp(name="isOpen", type="boolean")],
            events=[
                {"name": "onClose", "type": "() => void"},
                {"name": "onConfirm", "type": "() => void"}
            ]
        )
        
        extracted = ExtractedData(language="typescript", file_path="Modal.tsx")
        extracted.components = [component]
        
        context = build_component_context(
            component_name="Modal",
            extracted_data_list=[extracted]
        )
        
        assert len(context.events) == 2
        
        renderer = TemplateRenderer()
        markdown = renderer.render_component_template(context)
        
        assert "onClose" in markdown or "Modal" in markdown  # At least component name


class TestE2EPipelineDatabase:
    """End-to-end tests for database documentation."""
    
    def test_e2e_table_extraction_to_rendering(self):
        """
        Test complete pipeline for database table documentation
        """
        # Step 1: Extract table
        col1 = ExtractedColumn(
            name="UserId",
            data_type="INT",
            is_nullable=False,
            is_primary_key=True
        )
        col2 = ExtractedColumn(
            name="Email",
            data_type="VARCHAR(255)",
            is_nullable=False
        )
        col3 = ExtractedColumn(
            name="CreatedDate",
            data_type="DATETIME",
            is_nullable=False,
            default="GETUTCDATE()"
        )
        col4 = ExtractedColumn(
            name="LastLogin",
            data_type="DATETIME",
            is_nullable=True
        )
        
        table = ExtractedTable(
            name="Users",
            schema="dbo",
            columns=[col1, col2, col3, col4],
            constraints=["UNIQUE (Email)"]
        )
        
        extracted = ExtractedData(language="sql", file_path="Users.sql")
        extracted.tables = [table]
        
        # Step 2: Build context
        context = build_table_context(
            table_name="Users",
            extracted_data_list=[extracted],
            schema_name="dbo"
        )
        
        assert context.table_name == "Users"
        assert len(context.columns) == 4
        
        # Step 3: Render documentation
        renderer = TemplateRenderer()
        markdown = renderer.render_table_template(context)
        
        # Verify output
        assert isinstance(markdown, str)
        assert len(markdown) > 300
        assert "Users" in markdown
        assert "UserId" in markdown
        assert "Email" in markdown
        assert "UNIQUE" in markdown or "unique" in markdown.lower()
    
    def test_e2e_complex_table_with_foreign_keys(self):
        """Test table documentation with foreign key relationships."""
        from src.tools.template_context import ForeignKeyContext
        
        col1 = ExtractedColumn(name="OrderId", data_type="INT", is_nullable=False)
        col2 = ExtractedColumn(name="UserId", data_type="INT", is_nullable=False)
        col3 = ExtractedColumn(name="OrderDate", data_type="DATETIME", is_nullable=False)
        
        table = ExtractedTable(
            name="Orders",
            schema="dbo",
            columns=[col1, col2, col3]
        )
        
        extracted = ExtractedData(language="sql", file_path="Orders.sql")
        extracted.tables = [table]
        
        context = build_table_context(
            table_name="Orders",
            extracted_data_list=[extracted]
        )
        
        # Manually add foreign key for testing
        fk = ForeignKeyContext(
            constraint_name="FK_Orders_Users",
            column="UserId",
            referenced_table="Users",
            referenced_column="UserId"
        )
        context.foreign_keys.append(fk)
        
        renderer = TemplateRenderer()
        markdown = renderer.render_table_template(context)
        
        assert "Orders" in markdown
        assert "FK_Orders_Users" in markdown


class TestE2EPipelineErrorRecovery:
    """Test error handling in complete pipeline."""
    
    def test_e2e_with_partial_extraction(self):
        """Test pipeline handles incomplete extraction gracefully."""
        # Extracted data with only partial information
        route = ExtractedRoute(
            method="GET",
            path="/api/test",
            handler_name="Test"
            # Missing response_types and status_codes
        )
        
        extracted = ExtractedData(language="csharp", file_path="Service.cs")
        extracted.routes = [route]
        # No dependencies or validations
        
        context = build_service_context(
            service_name="TestService",
            extracted_data_list=[extracted]
        )
        
        # Should still render without errors
        renderer = TemplateRenderer()
        markdown = renderer.render_service_template(context)
        
        assert "TestService" in markdown
        assert "/api/test" in markdown
    
    def test_e2e_with_null_fields(self):
        """Test pipeline handles null/missing fields gracefully."""
        # Some fields are None
        endpoint = ExtractedRoute(
            method="GET",
            path="/api/test",
            handler_name="Test",
            response_types=None,  # Null
            status_codes=None  # Null
        )
        
        extracted = ExtractedData(language="csharp", file_path="Service.cs")
        extracted.routes = [endpoint]
        
        context = build_service_context(
            service_name="TestService",
            extracted_data_list=[extracted]
        )
        
        # Should handle gracefully
        renderer = TemplateRenderer()
        markdown = renderer.render_service_template(context)
        
        assert isinstance(markdown, str)
        assert len(markdown) > 100


class TestE2EDocumentationCompleteness:
    """Test that rendered documentation is appropriately complete."""
    
    def test_service_with_full_extraction_no_placeholders_needed(self):
        """
        Test that service with complete extraction doesn't need many placeholders
        """
        # Comprehensive service data
        routes = [
            ExtractedRoute(
                method="GET",
                path="/api/users",
                handler_name="GetUsers",
                response_types=["List<User>"],
                status_codes=[200, 404]
            ),
            ExtractedRoute(
                method="POST",
                path="/api/users",
                handler_name="CreateUser",
                response_types=["User"],
                status_codes=[201, 400]
            )
        ]
        
        dependencies = [
            ExtractedDependency(name="IUserRepository", type="Interface", description="User repo"),
            ExtractedDependency(name="IValidator", type="Interface", description="Validator"),
            ExtractedDependency(name="ILogger", type="Interface", description="Logger")
        ]
        
        validations = [
            ExtractedValidation("Email", "NotEmpty", "Email required"),
            ExtractedValidation("Email", "EmailAddress", "Invalid email")
        ]
        
        extracted = ExtractedData(language="csharp", file_path="UserService.cs")
        extracted.routes = routes
        extracted.dependencies = dependencies
        extracted.validations = validations
        
        context = build_service_context("UserService", [extracted])
        renderer = TemplateRenderer()
        markdown = renderer.render_service_template(context)
        
        # With complete data, we should have minimal AI placeholders
        # Count placeholder occurrences
        placeholder_count = markdown.count("🤖")
        
        # Should have some for optional sections but not many
        # This validates that extraction data fills most sections
        assert placeholder_count <= 10


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
