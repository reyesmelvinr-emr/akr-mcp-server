"""
Test script for Role-Based Interview functionality

This script tests the role-based filtering of interview questions
to ensure each role only sees relevant questions based on their
expertise areas.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from tools.human_input_interview import (
    InterviewRole,
    RoleProfile,
    RoleProfileManager,
    InputCategory,
    QuestionPriority,
    HumanInputDetector,
    InterviewManager,
    start_documentation_interview,
    get_next_interview_question,
    end_documentation_interview,
    DEFAULT_ROLE_PROFILES,
    get_role_profile_manager,
    reset_role_profile_manager
)


# Sample template content with various sections requiring human input
SAMPLE_TEMPLATE = """# UserService Documentation

## Overview
🤖 This service handles user management functionality.

## Business Context
❓ [HUMAN: Explain the business purpose and value this service provides]

## Historical Background
❓ _Why was this service created and what did it replace?_

## Design Decisions
❓ **What architectural decisions were made and why?**

## Security & Compliance
❓ [HUMAN: Describe any security requirements or compliance considerations]

## Performance Requirements
❓ [HUMAN: What are the SLA and performance requirements?]

## Configuration
❓ [HUMAN: Document environment-specific configuration needs]

## Error Handling
❓ [HUMAN: Describe error handling strategies and patterns]

## Testing Strategy
❓ [HUMAN: What testing approaches are used?]

## Known Issues
❓ [HUMAN: List any known issues or limitations]

## Future Plans
❓ [HUMAN: Describe planned enhancements]

## Team Ownership
❓ [HUMAN: Who owns this service and how to contact them?]
"""


def test_default_role_profiles():
    """Test that all default role profiles are properly configured."""
    print("\n" + "="*60)
    print("Testing Default Role Profiles")
    print("="*60)
    
    # Reset to ensure we're using defaults
    reset_role_profile_manager()
    manager = get_role_profile_manager()
    
    # Check all built-in roles exist
    expected_roles = [
        InterviewRole.TECHNICAL_LEAD,
        InterviewRole.DEVELOPER,
        InterviewRole.PRODUCT_OWNER,
        InterviewRole.QA_TESTER,
        InterviewRole.SCRUM_MASTER,
        InterviewRole.GENERAL
    ]
    
    print("\nChecking all built-in roles:")
    for role in expected_roles:
        profile = manager.get_profile(role)
        if profile:
            print(f"  ✓ {role.value}: {profile.display_name}")
            print(f"    - Primary categories: {len(profile.primary_categories)}")
            print(f"    - Secondary categories: {len(profile.secondary_categories)}")
            print(f"    - Excluded categories: {len(profile.excluded_categories)}")
        else:
            print(f"  ✗ {role.value}: NOT FOUND")
    
    return True


def test_role_profile_filtering():
    """Test that role profiles correctly filter questions."""
    print("\n" + "="*60)
    print("Testing Role Profile Filtering Logic")
    print("="*60)
    
    profiles = DEFAULT_ROLE_PROFILES
    
    # Test Technical Lead profile
    tl_profile = profiles[InterviewRole.TECHNICAL_LEAD]
    print(f"\nTechnical Lead - {tl_profile.display_name}:")
    
    # TL should answer design rationale questions
    assert tl_profile.should_ask(InputCategory.DESIGN_RATIONALE), "TL should answer design rationale"
    assert tl_profile.is_primary(InputCategory.DESIGN_RATIONALE), "Design rationale is primary for TL"
    print(f"  ✓ Should answer DESIGN_RATIONALE: {tl_profile.should_ask(InputCategory.DESIGN_RATIONALE)}")
    
    # TL should NOT answer business context questions
    assert not tl_profile.should_ask(InputCategory.BUSINESS_CONTEXT), "TL should NOT answer business context"
    print(f"  ✓ Should NOT answer BUSINESS_CONTEXT: {not tl_profile.should_ask(InputCategory.BUSINESS_CONTEXT)}")
    
    # Test Product Owner profile
    po_profile = profiles[InterviewRole.PRODUCT_OWNER]
    print(f"\nProduct Owner - {po_profile.display_name}:")
    
    # PO should answer business context
    assert po_profile.should_ask(InputCategory.BUSINESS_CONTEXT), "PO should answer business context"
    assert po_profile.is_primary(InputCategory.BUSINESS_CONTEXT), "Business context is primary for PO"
    print(f"  ✓ Should answer BUSINESS_CONTEXT: {po_profile.should_ask(InputCategory.BUSINESS_CONTEXT)}")
    
    # PO should NOT answer configuration
    assert not po_profile.should_ask(InputCategory.CONFIGURATION), "PO should NOT answer configuration"
    print(f"  ✓ Should NOT answer CONFIGURATION: {not po_profile.should_ask(InputCategory.CONFIGURATION)}")
    
    # Test QA Tester profile
    qa_profile = profiles[InterviewRole.QA_TESTER]
    print(f"\nQA Tester - {qa_profile.display_name}:")
    
    # QA should answer testing questions
    assert qa_profile.should_ask(InputCategory.TESTING), "QA should answer testing"
    print(f"  ✓ Should answer TESTING: {qa_profile.should_ask(InputCategory.TESTING)}")
    
    # Test General profile - should answer everything
    general_profile = profiles[InterviewRole.GENERAL]
    print(f"\nGeneral - {general_profile.display_name}:")
    
    for category in InputCategory:
        assert general_profile.should_ask(category), f"General should answer {category.value}"
    print(f"  ✓ Should answer ALL categories (no filtering)")
    
    return True


def test_delegation_suggestions():
    """Test that delegation targets are correctly suggested."""
    print("\n" + "="*60)
    print("Testing Delegation Suggestions")
    print("="*60)
    
    tl_profile = DEFAULT_ROLE_PROFILES[InterviewRole.TECHNICAL_LEAD]
    
    # Business context should be delegated to Product Owner
    target = tl_profile.get_delegation_target(InputCategory.BUSINESS_CONTEXT)
    print(f"\n  BUSINESS_CONTEXT -> {target}")
    assert target == "Product Owner", f"Expected 'Product Owner', got '{target}'"
    print(f"  ✓ Correctly suggests Product Owner for business context")
    
    po_profile = DEFAULT_ROLE_PROFILES[InterviewRole.PRODUCT_OWNER]
    
    # Configuration should be delegated to Developer
    target = po_profile.get_delegation_target(InputCategory.CONFIGURATION)
    print(f"  CONFIGURATION -> {target}")
    assert target == "Developer", f"Expected 'Developer', got '{target}'"
    print(f"  ✓ Correctly suggests Developer for configuration")
    
    # Design rationale should be delegated to Technical Lead
    target = po_profile.get_delegation_target(InputCategory.DESIGN_RATIONALE)
    print(f"  DESIGN_RATIONALE -> {target}")
    assert target == "Technical Lead", f"Expected 'Technical Lead', got '{target}'"
    print(f"  ✓ Correctly suggests Technical Lead for design rationale")
    
    return True


def test_interview_session_with_role():
    """Test starting an interview session with a specific role."""
    print("\n" + "="*60)
    print("Testing Interview Session with Role")
    print("="*60)
    
    # Reset role manager to use defaults
    reset_role_profile_manager()
    
    # Test with Technical Lead role
    print("\n  Starting session as TECHNICAL_LEAD...")
    result = start_documentation_interview(
        source_file="src/services/UserService.cs",
        template_content=SAMPLE_TEMPLATE,
        template_name="standard_service_template",
        component_type="services",
        role="technical_lead"
    )
    
    assert result.get("success"), f"Session should start successfully: {result.get('error')}"
    print(f"  ✓ Session started: {result['session_id']}")
    print(f"  ✓ Role: {result.get('role_display_name')} ({result.get('role')})")
    print(f"  ✓ Questions for this role: {result['total_questions']}")
    print(f"  ✓ Questions delegated to others: {result.get('questions_delegated_to_others', 0)}")
    
    # Technical lead should have fewer questions than general
    tl_questions = result['total_questions']
    tl_delegated = result.get('questions_delegated_to_others', 0)
    
    # End session and check delegated questions
    end_result = end_documentation_interview(result['session_id'])
    
    print(f"\n  Session ended.")
    delegated = end_result.get('questions_for_other_roles', [])
    print(f"  ✓ Questions for other roles: {len(delegated)}")
    
    if delegated:
        print("\n  Delegated questions:")
        for q in delegated[:3]:  # Show first 3
            print(f"    - {q['section_title']} -> {q['suggested_role']}")
    
    return True


def test_all_roles_interview_counts():
    """Test interview question counts for all roles."""
    print("\n" + "="*60)
    print("Testing Question Counts for All Roles")
    print("="*60)
    
    # Reset role manager
    reset_role_profile_manager()
    
    roles = ["general", "technical_lead", "developer", "product_owner", "qa_tester", "scrum_master"]
    results = {}
    
    for role in roles:
        result = start_documentation_interview(
            source_file=f"test_{role}.cs",
            template_content=SAMPLE_TEMPLATE,
            template_name="test_template",
            component_type="services",
            role=role
        )
        
        if result.get("success"):
            results[role] = {
                "questions": result['total_questions'],
                "delegated": result.get('questions_delegated_to_others', 0)
            }
            # Clean up session
            end_documentation_interview(result['session_id'])
    
    print("\n  Role               | Questions | Delegated")
    print("  " + "-"*45)
    
    for role, counts in results.items():
        print(f"  {role:<18} | {counts['questions']:>9} | {counts['delegated']:>9}")
    
    # Verify General has the most questions (no filtering)
    general_q = results.get("general", {}).get("questions", 0)
    print(f"\n  ✓ General role has {general_q} questions (should be highest)")
    
    # Verify all roles have fewer or equal questions compared to general
    for role, counts in results.items():
        if role != "general":
            assert counts["questions"] <= general_q, f"{role} should have <= questions than general"
    print(f"  ✓ All other roles have filtered question counts")
    
    # Verify sum of questions + delegated equals general for each role
    for role, counts in results.items():
        if role != "general":
            total = counts["questions"] + counts["delegated"]
            if total == general_q:
                print(f"  ✓ {role}: {counts['questions']} + {counts['delegated']} = {general_q} (matches general)")
    
    return True


def test_custom_role_profiles():
    """Test custom role profiles from configuration."""
    print("\n" + "="*60)
    print("Testing Custom Role Profiles")
    print("="*60)
    
    # Define custom profiles (e.g., a Security Engineer role)
    custom_profiles = {
        "security_engineer": {
            "displayName": "Security Engineer",
            "description": "Security-focused questions only",
            "primaryCategories": ["security_compliance", "performance"],
            "secondaryCategories": ["known_issues"],
            "excludedCategories": [
                "business_context", "business_rules", "future_plans",
                "team_ownership", "historical_context"
            ]
        },
        # Override developer to be more focused
        "developer": {
            "displayName": "Developer (Custom)",
            "description": "Focused developer questions",
            "primaryCategories": ["configuration", "error_handling"],
            "secondaryCategories": [],
            "excludedCategories": [
                "business_context", "business_rules", "future_plans",
                "team_ownership", "historical_context", "security_compliance",
                "performance", "testing"
            ]
        }
    }
    
    # Reset and create manager with custom profiles
    reset_role_profile_manager()
    manager = get_role_profile_manager(custom_profiles)
    
    # Check custom role exists
    se_profile = manager.get_profile("security_engineer")
    print(f"\n  Custom role 'security_engineer':")
    print(f"    Display Name: {se_profile.display_name}")
    print(f"    Description: {se_profile.description}")
    print(f"    Primary categories: {len(se_profile.primary_categories)}")
    
    # Check developer was overridden
    dev_profile = manager.get_profile("developer")
    print(f"\n  Overridden 'developer' role:")
    print(f"    Display Name: {dev_profile.display_name}")
    print(f"    Excluded categories: {len(dev_profile.excluded_categories)}")
    
    # Verify security engineer answers security questions
    assert se_profile.should_ask(InputCategory.SECURITY_COMPLIANCE), "SE should answer security"
    print(f"  ✓ Security Engineer answers SECURITY_COMPLIANCE")
    
    # Verify security engineer doesn't answer business context
    assert not se_profile.should_ask(InputCategory.BUSINESS_CONTEXT), "SE should NOT answer business"
    print(f"  ✓ Security Engineer skips BUSINESS_CONTEXT")
    
    # Reset back to defaults for other tests
    reset_role_profile_manager()
    
    return True


def test_role_profile_manager_list_roles():
    """Test listing all available roles."""
    print("\n" + "="*60)
    print("Testing Role Profile Manager list_roles()")
    print("="*60)
    
    reset_role_profile_manager()
    manager = get_role_profile_manager()
    
    roles = manager.list_roles()
    print(f"\n  Found {len(roles)} roles:")
    
    for role_info in roles:
        print(f"\n    {role_info['display_name']}:")
        print(f"      - Key: {role_info['role']}")
        print(f"      - Built-in: {role_info['is_builtin']}")
        print(f"      - Primary categories: {role_info['primary_category_count']}")
        print(f"      - Excluded categories: {role_info['excluded_category_count']}")
    
    # Verify all expected roles are present
    role_keys = [r['role'] for r in roles]
    expected = ['technical_lead', 'developer', 'product_owner', 'qa_tester', 'scrum_master', 'general']
    
    for exp in expected:
        assert exp in role_keys, f"Expected role '{exp}' not found"
    print(f"\n  ✓ All {len(expected)} expected roles found")
    
    return True


async def main():
    """Run all role-based interview tests."""
    print("\n" + "#"*60)
    print("# Role-Based Interview - Test Suite")
    print("#"*60)
    
    tests = [
        ("Default Role Profiles", test_default_role_profiles),
        ("Role Profile Filtering", test_role_profile_filtering),
        ("Delegation Suggestions", test_delegation_suggestions),
        ("Interview Session with Role", test_interview_session_with_role),
        ("All Roles Question Counts", test_all_roles_interview_counts),
        ("Custom Role Profiles", test_custom_role_profiles),
        ("List Roles", test_role_profile_manager_list_roles),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            result = test_func()
            if result:
                passed += 1
                print(f"\n  ✓ {name}: PASSED")
            else:
                failed += 1
                print(f"\n  ✗ {name}: FAILED")
        except Exception as e:
            failed += 1
            print(f"\n  ✗ {name}: ERROR - {str(e)}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "#"*60)
    print(f"# Test Results: {passed} passed, {failed} failed")
    print("#"*60)
    
    return failed == 0


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
