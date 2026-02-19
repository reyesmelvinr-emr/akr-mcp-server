"""
Unit tests for template_context.py

Tests the data models and context classes used for Jinja2 template rendering.
"""

import pytest
from datetime import datetime
from src.tools.template_context import (
    ServiceTemplateContext, ComponentTemplateContext, TableTemplateContext,
    EndpointContext, DependencyContext, ValidationRuleContext,
    PropContext, EventContext, StateContext,
    ColumnContext, ConstraintContext, ForeignKeyContext
)


class TestServiceTemplateContext:
    """Test service documentation context."""
    
    def test_create_minimal_service_context(self):
        """Test creating a service context with minimal data."""
        context = ServiceTemplateContext(
            service_name="UserService",
            namespace="MyApp.Services"
        )
        
        assert context.service_name == "UserService"
        assert context.namespace == "MyApp.Services"
        assert context.status == "Active"
        assert len(context.endpoints) == 0
        assert len(context.dependencies) == 0
    
    def test_service_context_with_endpoints(self):
        """Test service context with API endpoints."""
        endpoint1 = EndpointContext(
            method="GET",
            path="/api/users/{id}",
            handler="GetUserById",
            summary="Retrieve user by ID",
            status_codes=[200, 404]
        )
        endpoint2 = EndpointContext(
            method="POST",
            path="/api/users",
            handler="CreateUser",
            summary="Create new user",
            status_codes=[201, 400]
        )
        
        context = ServiceTemplateContext(
            service_name="UserService",
            endpoints=[endpoint1, endpoint2]
        )
        
        assert len(context.endpoints) == 2
        assert context.endpoints[0].method == "GET"
        assert context.endpoints[1].method == "POST"
    
    def test_service_context_with_dependencies(self):
        """Test service context with dependencies."""
        dep1 = DependencyContext(
            name="IUserRepository",
            type="Interface",
            purpose="Data access for users",
            code_location="UserService.cs:12"
        )
        dep2 = DependencyContext(
            name="ILogger",
            type="Interface",
            purpose="Logging",
            code_location="UserService.cs:13",
            is_critical=False
        )
        
        context = ServiceTemplateContext(
            service_name="UserService",
            dependencies=[dep1, dep2]
        )
        
        assert len(context.dependencies) == 2
        assert context.dependencies[0].is_critical == False
        assert context.dependencies[1].name == "ILogger"
    
    def test_service_context_with_validation_rules(self):
        """Test service context with validation rules."""
        rule1 = ValidationRuleContext(
            property="Email",
            rule_type="NotEmpty",
            error_message="Email is required",
            code_location="UserValidator.cs:45"
        )
        rule2 = ValidationRuleContext(
            property="Email",
            rule_type="EmailAddress",
            error_message="Invalid email format",
            code_location="UserValidator.cs:46"
        )
        
        context = ServiceTemplateContext(
            service_name="UserService",
            validation_rules=[rule1, rule2]
        )
        
        assert len(context.validation_rules) == 2
        assert context.validation_rules[0].rule_type == "NotEmpty"
        assert context.validation_rules[1].rule_type == "EmailAddress"


class TestComponentTemplateContext:
    """Test component documentation context."""
    
    def test_create_minimal_component_context(self):
        """Test creating a component context with minimal data."""
        context = ComponentTemplateContext(
            component_name="UserCard"
        )
        
        assert context.component_name == "UserCard"
        assert context.component_type == "Functional"
        assert context.complexity == "Medium"
        assert len(context.props) == 0
    
    def test_component_context_with_props(self):
        """Test component context with props."""
        prop1 = PropContext(
            name="userId",
            type="string",
            required=True,
            description="User ID"
        )
        prop2 = PropContext(
            name="showDetails",
            type="boolean",
            required=False,
            default="false",
            description="Whether to show details"
        )
        
        context = ComponentTemplateContext(
            component_name="UserCard",
            props=[prop1, prop2]
        )
        
        assert len(context.props) == 2
        assert context.props[0].required == True
        assert context.props[1].required == False
    
    def test_component_context_with_events(self):
        """Test component context with events."""
        event1 = EventContext(
            name="onUserClick",
            handler_type="click",
            triggered_when="User clicks on card"
        )
        event2 = EventContext(
            name="onUserEdit",
            handler_type="custom",
            triggered_when="Edit button clicked"
        )
        
        context = ComponentTemplateContext(
            component_name="UserCard",
            events=[event1, event2]
        )
        
        assert len(context.events) == 2
        assert context.events[0].name == "onUserClick"
    
    def test_component_context_with_state(self):
        """Test component context with state variables."""
        state1 = StateContext(
            name="isExpanded",
            type="boolean",
            initial_value="false",
            purpose="Track expanded state"
        )
        state2 = StateContext(
            name="selectedTab",
            type="string",
            initial_value="'overview'",
            purpose="Current tab"
        )
        
        context = ComponentTemplateContext(
            component_name="UserCard",
            state_vars=[state1, state2]
        )
        
        assert len(context.state_vars) == 2
        assert context.state_vars[0].initial_value == "false"


class TestTableTemplateContext:
    """Test table documentation context."""
    
    def test_create_minimal_table_context(self):
        """Test creating a table context with minimal data."""
        context = TableTemplateContext(
            table_name="Users",
            schema_name="dbo"
        )
        
        assert context.table_name == "Users"
        assert context.schema_name == "dbo"
        assert context.status == "Active"
        assert len(context.columns) == 0
    
    def test_table_context_with_columns(self):
        """Test table context with column definitions."""
        col1 = ColumnContext(
            name="UserId",
            type="INT",
            nullable=False,
            is_primary_key=True,
            description="Primary key"
        )
        col2 = ColumnContext(
            name="Email",
            type="VARCHAR(255)",
            nullable=False,
            description="User email address"
        )
        col3 = ColumnContext(
            name="IsActive",
            type="BIT",
            nullable=False,
            default="1",
            description="Active flag"
        )
        
        context = TableTemplateContext(
            table_name="Users",
            columns=[col1, col2, col3]
        )
        
        assert len(context.columns) == 3
        assert context.columns[0].is_primary_key == True
        assert context.columns[0].nullable == False
        assert context.columns[2].default == "1"
    
    def test_table_context_with_foreign_keys(self):
        """Test table context with foreign key relationships."""
        fk1 = ForeignKeyContext(
            column="DepartmentId",
            referenced_table="Departments",
            referenced_column="DepartmentId",
            relationship="N:1"
        )
        fk2 = ForeignKeyContext(
            column="ManagerId",
            referenced_table="Users",
            referenced_column="UserId",
            relationship="N:1"
        )
        
        context = TableTemplateContext(
            table_name="Users",
            foreign_keys=[fk1, fk2]
        )
        
        assert len(context.foreign_keys) == 2
        assert context.foreign_keys[0].referenced_table == "Departments"
        assert context.foreign_keys[1].relationship == "N:1"
    
    def test_table_context_with_constraints(self):
        """Test table context with check constraints."""
        const1 = ConstraintContext(
            name="CK_Users_Age",
            constraint_type="CHECK",
            description="Age must be positive",
            sql_expression="Age > 0"
        )
        
        context = TableTemplateContext(
            table_name="Users",
            check_constraints=[const1]
        )
        
        assert len(context.check_constraints) == 1
        assert context.check_constraints[0].constraint_type == "CHECK"


class TestContextDataIntegrity:
    """Test data integrity and consistency."""
    
    def test_service_context_preserves_all_data(self):
        """Test that service context preserves all provided data."""
        context = ServiceTemplateContext(
            service_name="TestService",
            namespace="TestNamespace",
            domain="TestDomain",
            version="2.0",
            service_summary="Test summary",
            capabilities=["Cap1", "Cap2"]
        )
        
        assert context.service_name == "TestService"
        assert context.namespace == "TestNamespace"
        assert context.domain == "TestDomain"
        assert context.version == "2.0"
        assert context.service_summary == "Test summary"
        assert context.capabilities == ["Cap1", "Cap2"]
    
    def test_component_context_has_valid_complexity_levels(self):
        """Test component complexity levels."""
        for complexity in ["Simple", "Medium", "Complex"]:
            context = ComponentTemplateContext(
                component_name="Test",
                complexity=complexity
            )
            assert context.complexity == complexity
    
    def test_foreign_key_relationship_types(self):
        """Test valid foreign key relationship types."""
        for relationship in ["1:1", "1:N", "N:1", "N:N"]:
            fk = ForeignKeyContext(
                column="TestCol",
                referenced_table="TestTable",
                referenced_column="Id",
                relationship=relationship
            )
            assert fk.relationship == relationship


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
