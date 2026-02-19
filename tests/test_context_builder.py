"""
Unit tests for context_builder.py

Tests the transformation functions that convert ExtractedData to template contexts.
"""

import pytest
from src.tools.extractors.base_extractor import (
    ExtractedData, ExtractedRoute, ExtractedDependency, ExtractedValidation,
    ExtractedMethod, ExtractedParameter, ExtractedComponent, ExtractedProp,
    ExtractedTable, ExtractedColumn
)
from src.tools.context_builder import (
    build_service_context, build_component_context, build_table_context,
    report_extraction_gaps
)


class TestBuildServiceContext:
    """Test service context building from extracted data."""
    
    def test_build_service_context_with_empty_data(self):
        """Test building service context with empty extracted data."""
        extracted = ExtractedData(language="csharp", file_path="Test.cs")
        
        context = build_service_context(
            service_name="TestService",
            extracted_data_list=[extracted]
        )
        
        assert context.service_name == "TestService"
        assert len(context.endpoints) == 0
        assert len(context.dependencies) == 0
        assert len(context.validation_rules) == 0
    
    def test_build_service_context_with_routes(self):
        """Test building service context with API routes."""
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
        
        extracted = ExtractedData(language="csharp", file_path="UserController.cs")
        extracted.routes = [route1, route2]
        
        context = build_service_context(
            service_name="UserService",
            extracted_data_list=[extracted]
        )
        
        assert len(context.endpoints) == 2
        assert context.endpoints[0].method == "GET"
        assert context.endpoints[1].method == "POST"
        assert context.endpoints[0].path == "/api/users"
    
    def test_build_service_context_with_dependencies(self):
        """Test building service context with dependencies."""
        dep1 = ExtractedDependency(
            name="IUserRepository",
            type="Interface",
            description="User data access"
        )
        dep2 = ExtractedDependency(
            name="IValidator",
            type="Interface"
        )
        
        extracted = ExtractedData(language="csharp", file_path="UserService.cs")
        extracted.dependencies = [dep1, dep2]
        
        context = build_service_context(
            service_name="UserService",
            extracted_data_list=[extracted]
        )
        
        assert len(context.dependencies) == 2
        assert context.dependencies[0].name == "IUserRepository"
        assert context.dependencies[0].purpose == "User data access"
        assert context.dependencies[1].purpose == "Injected dependency"
    
    def test_build_service_context_with_validations(self):
        """Test building service context with validation rules."""
        val1 = ExtractedValidation(
            field_name="Email",
            rule_type="NotEmpty",
            error_message="Email is required"
        )
        val2 = ExtractedValidation(
            field_name="Email",
            rule_type="EmailAddress",
            error_message="Invalid email"
        )
        
        extracted = ExtractedData(language="csharp", file_path="UserValidator.cs")
        extracted.validations = [val1, val2]
        
        context = build_service_context(
            service_name="UserService",
            extracted_data_list=[extracted]
        )
        
        assert len(context.validation_rules) == 2
        assert context.validation_rules[0].property == "Email"
        assert context.validation_rules[0].rule_type == "NotEmpty"
    
    def test_build_service_context_preserves_namespace_and_domain(self):
        """Test that namespace and domain are preserved."""
        extracted = ExtractedData(language="csharp", file_path="UserService.cs")
        
        context = build_service_context(
            service_name="UserService",
            extracted_data_list=[extracted],
            namespace="MyApp.Services",
            domain="UserManagement"
        )
        
        assert context.namespace == "MyApp.Services"
        assert context.domain == "UserManagement"


class TestBuildComponentContext:
    """Test component context building from extracted data."""
    
    def test_build_component_context_with_empty_data(self):
        """Test building component context with empty extracted data."""
        extracted = ExtractedData(language="typescript", file_path="UserCard.tsx")
        
        context = build_component_context(
            component_name="UserCard",
            extracted_data_list=[extracted]
        )
        
        assert context.component_name == "UserCard"
        assert len(context.props) == 0
        assert len(context.state_vars) == 0
        assert len(context.events) == 0
    
    def test_build_component_context_with_props(self):
        """Test building component context with props."""
        prop1 = ExtractedProp(
            name="userId",
            type="string",
            is_required=True,
            description="User ID"
        )
        prop2 = ExtractedProp(
            name="onSelect",
            type="(userId: string) => void",
            is_required=False,
            default="undefined"
        )
        
        component = ExtractedComponent(
            name="UserCard",
            props=[prop1, prop2]
        )
        
        extracted = ExtractedData(language="typescript", file_path="UserCard.tsx")
        extracted.components = [component]
        
        context = build_component_context(
            component_name="UserCard",
            extracted_data_list=[extracted]
        )
        
        assert len(context.props) == 2
        assert context.props[0].name == "userId"
        assert context.props[0].required == True
        assert context.props[1].default == "undefined"
    
    def test_build_component_context_with_state(self):
        """Test building component context with state variables."""
        component = ExtractedComponent(
            name="UserCard",
            state_variables=[
                {"name": "isExpanded", "type": "boolean", "initial_value": "false"},
                {"name": "selectedTab", "type": "string", "initial_value": "'overview'"}
            ]
        )
        
        extracted = ExtractedData(language="typescript", file_path="UserCard.tsx")
        extracted.components = [component]
        
        context = build_component_context(
            component_name="UserCard",
            extracted_data_list=[extracted]
        )
        
        assert len(context.state_vars) == 2
        assert context.state_vars[0].name == "isExpanded"
        assert context.state_vars[0].type == "boolean"


class TestBuildTableContext:
    """Test table context building from extracted data."""
    
    def test_build_table_context_with_columns(self):
        """Test building table context with columns."""
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
        
        table = ExtractedTable(
            name="Users",
            schema="dbo",
            columns=[col1, col2, col3]
        )
        
        extracted = ExtractedData(language="sql", file_path="Users.sql")
        extracted.tables = [table]
        
        context = build_table_context(
            table_name="Users",
            extracted_data_list=[extracted],
            schema_name="dbo"
        )
        
        assert context.table_name == "Users"
        assert context.schema_name == "dbo"
        assert len(context.columns) == 3
        assert context.columns[0].is_primary_key == True
        assert context.columns[2].default == "GETUTCDATE()"
    
    def test_build_table_context_with_constraints(self):
        """Test building table context with constraints."""
        table = ExtractedTable(
            name="Users",
            schema="dbo",
            columns=[],
            constraints=[
                "CHECK (Age > 0)",
                "UNIQUE (Email)"
            ]
        )
        
        extracted = ExtractedData(language="sql", file_path="Users.sql")
        extracted.tables = [table]
        
        context = build_table_context(
            table_name="Users",
            extracted_data_list=[extracted]
        )
        
        assert len(context.check_constraints) == 1
        assert context.check_constraints[0].constraint_type == "CHECK"


class TestExtractionGapReporting:
    """Test extraction gap reporting for diagnostics."""
    
    def test_report_extraction_gaps_backend_no_routes(self):
        """Test detection of missing routes in backend extraction."""
        extracted = ExtractedData(language="csharp", file_path="Service.cs")
        
        report = report_extraction_gaps([extracted], "backend")
        
        assert len(report['gaps']) > 0
        assert any("routes" in gap.lower() for gap in report['gaps'])
    
    def test_report_extraction_gaps_backend_no_dependencies(self):
        """Test detection of missing dependencies in backend extraction."""
        extracted = ExtractedData(language="csharp", file_path="Service.cs")
        
        report = report_extraction_gaps([extracted], "backend")
        
        assert len(report['gaps']) > 0
    
    def test_report_extraction_gaps_ui_no_components(self):
        """Test detection of missing components in UI extraction."""
        extracted = ExtractedData(language="typescript", file_path="Component.tsx")
        
        report = report_extraction_gaps([extracted], "ui")
        
        assert len(report['gaps']) > 0
        assert any("component" in gap.lower() for gap in report['gaps'])
    
    def test_report_extraction_gaps_database_no_tables(self):
        """Test detection of missing tables in database extraction."""
        extracted = ExtractedData(language="sql", file_path="Schema.sql")
        
        report = report_extraction_gaps([extracted], "database")
        
        assert len(report['gaps']) > 0
        assert any("table" in gap.lower() for gap in report['gaps'])
    
    def test_report_extraction_success(self):
        """Test report shows no gaps when data is present."""
        # Create extracted data with routes (backend)
        route = ExtractedRoute(method="GET", path="/test", handler_name="Test")
        extracted = ExtractedData(language="csharp", file_path="Service.cs")
        extracted.routes = [route]
        
        report = report_extraction_gaps([extracted], "backend")
        
        # Should still have some gaps (dependencies, validations)
        # but routes should not be mentioned as missing
        assert not any("route" in gap.lower() for gap in report['gaps'])


class TestContextBuilderRobustness:
    """Test robustness of context builders."""
    
    def test_build_context_with_multiple_extracted_files(self):
        """Test building context from multiple extracted files."""
        route = ExtractedRoute(method="GET", path="/api/test", handler_name="GetTest")
        extracted1 = ExtractedData(language="csharp", file_path="Controller.cs")
        extracted1.routes = [route]
        
        dep = ExtractedDependency(name="IRepository", type="Interface")
        extracted2 = ExtractedData(language="csharp", file_path="Service.cs")
        extracted2.dependencies = [dep]
        
        context = build_service_context(
            service_name="TestService",
            extracted_data_list=[extracted1, extracted2]
        )
        
        assert len(context.endpoints) == 1
        assert len(context.dependencies) == 1
    
    def test_build_context_with_partial_data(self):
        """Test building context with incomplete data fields."""
        route = ExtractedRoute(
            method="GET",
            path="/api/test",
            handler_name="GetTest"
            # Missing response_types and status_codes
        )
        extracted = ExtractedData(language="csharp", file_path="Controller.cs")
        extracted.routes = [route]
        
        context = build_service_context(
            service_name="TestService",
            extracted_data_list=[extracted]
        )
        
        assert len(context.endpoints) == 1
        assert context.endpoints[0].response_types == []
        assert context.endpoints[0].status_codes == []


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
