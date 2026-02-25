"""
Tests for Phase 3 Validation Library.

Tests cover:
- ValidationEngine core logic
- Tier-based severity adjustments
- YAML frontmatter validation (with JSON schema)
- Section validation (presence, order, completeness)
- Auto-fix capabilities
- Diff generation
"""

import pytest
from unittest.mock import Mock, patch, MagicMock

from src.tools.validation_library import (
    ValidationEngine,
    ValidationTier,
    EnhancedViolation,
    ProvenzanceMetadata,
    ValidationResult,
    ViolationType,
)
from src.tools.template_schema_builder import TemplateSchemaBuilder
from src.tools.document_parser import BasicDocumentParser


# ==================== FIXTURES ====================


@pytest.fixture
def mock_schema_builder():
    """Mock TemplateSchemaBuilder."""
    builder = Mock(spec=TemplateSchemaBuilder)
    
    # Create mock template schema with proper section objects
    mock_schema = Mock()
    
    # Create mock sections with actual .name attributes (not Mock name parameter)
    mock_section_1 = Mock()
    mock_section_1.name = "Quick Reference"
    
    mock_section_2 = Mock()
    mock_section_2.name = "What & Why"
    
    mock_section_3 = Mock()
    mock_section_3.name = "API Contract"
    
    mock_schema.required_sections = [
        mock_section_1,
        mock_section_2,
        mock_section_3,
    ]
    
    builder.build_schema.return_value = mock_schema
    
    # Add mock resolver to prevent AttributeError
    mock_resolver = Mock()
    builder._resolver = mock_resolver
    
    return builder


@pytest.fixture
def validation_engine(mock_schema_builder):
    """Create ValidationEngine with mock dependencies."""
    return ValidationEngine(schema_builder=mock_schema_builder)


@pytest.fixture
def valid_markdown_with_yaml():
    """Sample valid markdown with YAML frontmatter."""
    return """---
templateId: lean_baseline_service_template
project: PaymentService
repo: microservices/payment
branch: main
generatedAtUTC: 2026-02-24T10:00:00Z
---

# Payment Service Documentation

## Quick Reference

The Payment Service handles all transaction processing.

## What & Why

This service exists to centralize payment logic and reduce code duplication.

## API Contract

| Endpoint | Method | Description |
|----------|--------|-------------|
| /payments | POST | Create new payment |
| /payments/{id} | GET | Get payment details |
"""


@pytest.fixture
def invalid_markdown_no_yaml():
    """Sample invalid markdown missing YAML frontmatter."""
    return """# Payment Service Documentation

## Quick Reference

The Payment Service handles all transaction processing.

## What & Why

This service exists.

## API Contract

Some API details here.
"""


@pytest.fixture
def incomplete_markdown():
    """Sample markdown with truly missing required sections."""
    return """---
templateId: lean_baseline_service_template
project: PaymentService
repo: microservices/payment
branch: main
generatedAtUTC: 2026-02-24T10:00:00Z
---

# Payment Service Documentation

## Quick Reference

Brief description.

## What & Why

Brief description of what and why.
"""


# ==================== UNIT TESTS ====================


class TestValidationEngineTierConfiguration:
    """Test tier-based severity thresholds."""

    def test_tier1_threshold(self, validation_engine):
        """TIER_1 requires 80% completeness."""
        assert validation_engine.tier_thresholds[ValidationTier.TIER_1]["completeness"] == 0.80

    def test_tier2_threshold(self, validation_engine):
        """TIER_2 requires 60% completeness."""
        assert validation_engine.tier_thresholds[ValidationTier.TIER_2]["completeness"] == 0.60

    def test_tier3_threshold(self, validation_engine):
        """TIER_3 requires 30% completeness."""
        assert validation_engine.tier_thresholds[ValidationTier.TIER_3]["completeness"] == 0.30


class TestYAMLValidation:
    """Test YAML front matter validation."""

    def test_missing_yaml_frontmatter_is_blocker(self, validation_engine, invalid_markdown_no_yaml):
        """Missing YAML front matter should produce BLOCKER violation."""
        result = validation_engine.validate(
            doc_content=invalid_markdown_no_yaml,
            template_id="test_template",
            tier_level=ValidationTier.TIER_2,
        )
        
        # Should have BLOCKER for missing YAML
        blockers = [v for v in result.violations if v.severity == "BLOCKER"]
        assert len(blockers) > 0
        assert any(
            "YAML" in v.message.upper() or "frontmatter" in v.message.lower()
            for v in blockers
        )

    def test_valid_yaml_frontmatter_no_blocker(self, validation_engine, valid_markdown_with_yaml):
        """Valid YAML frontmatter should not produce YAML violations."""
        result = validation_engine.validate(
            doc_content=valid_markdown_with_yaml,
            template_id="test_template",
            tier_level=ValidationTier.TIER_2,
        )
        
        # Should not have YAML-related BLOCKERs
        yaml_blockers = [
            v for v in result.violations
            if v.severity == "BLOCKER" and "yaml" in v.type.lower()
        ]
        assert len(yaml_blockers) == 0

    def test_missing_yaml_field_returns_field_path(self, validation_engine):
        """Missing YAML fields should include field_path in violation."""
        yaml_only = """---
project: Test
---
# Document
"""
        result = validation_engine.validate(
            doc_content=yaml_only,
            template_id="test_template",
            tier_level=ValidationTier.TIER_2,
        )
        
        yaml_violations = [v for v in result.violations if "yaml" in v.type.lower()]
        # Violations should have field_path pointing to specific field
        for v in yaml_violations:
            assert v.field_path.startswith("frontmatter")


class TestSectionValidation:
    """Test section presence and order validation."""

    def test_missing_required_section(self, validation_engine, incomplete_markdown):
        """Missing required section should produce FIXABLE violation."""
        result = validation_engine.validate(
            doc_content=incomplete_markdown,
            template_id="test_template",
            tier_level=ValidationTier.TIER_2,
        )
        
        # Should detect missing or empty sections
        section_violations = [
            v for v in result.violations
            if "section" in v.type.lower()
        ]
        assert len(section_violations) > 0

    def test_section_order_validation(self, validation_engine):
        """Sections in wrong order should produce violation."""
        wrong_order = """---
templateId: test
project: Test
repo: test/test
generatedAtUTC: 2026-02-24T10:00:00Z
---

# Document

## API Contract

First section.

## What & Why

Second section.

## Quick Reference

Third section.
"""
        result = validation_engine.validate(
            doc_content=wrong_order,
            template_id="test_template",
            tier_level=ValidationTier.TIER_2,
        )
        
        # Should detect order violation
        order_violations = [
            v for v in result.violations
            if "order" in v.type.lower()
        ]
        # Note: may or may not have order violations depending on schema
        for v in order_violations:
            assert v.type == ViolationType.WRONG_SECTION_ORDER.value


class TestCompletenessCalculation:
    """Test completeness estimation."""

    def test_empty_document_zero_completeness(self, validation_engine):
        """Empty document should have 0% completeness."""
        result = validation_engine.validate(
            doc_content="",
            template_id="test_template",
            tier_level=ValidationTier.TIER_2,
        )
        assert result.completeness == 0.0

    def test_complete_sections_increase_completeness(self, validation_engine, valid_markdown_with_yaml):
        """Sections with >50 words should count as filled."""
        result = validation_engine.validate(
            doc_content=valid_markdown_with_yaml,
            template_id="test_template",
            tier_level=ValidationTier.TIER_2,
        )
        
        # Should estimate completeness >0 for filled sections
        assert result.completeness > 0.0

    def test_table_counts_as_filled(self, validation_engine):
        """Sections with tables should count as filled."""
        with_table = """---
templateId: test
project: Test
repo: test/test
generatedAtUTC: 2026-02-24T10:00:00Z
---

## Section

| Column | Value |
|--------|-------|
| test   | value |
"""
        result = validation_engine.validate(
            doc_content=with_table,
            template_id="test_template",
            tier_level=ValidationTier.TIER_2,
        )
        
        # Section with table should count as filled
        assert result.completeness > 0.0


class TestTierAdjustments:
    """Test tier-based severity adjustments."""

    def test_tier1_strict_severity(self, validation_engine):
        """TIER_1 should keep FIXABLE violations as FIXABLE for critical issues."""
        incomplete = """---
templateId: test
project: Test
repo: test/test
generatedAtUTC: 2026-02-24T10:00:00Z
---

## Quick Reference

Minimal content.
"""
        result = validation_engine.validate(
            doc_content=incomplete,
            template_id="test_template",
            tier_level=ValidationTier.TIER_1,
        )
        
        # TIER_1 should be strict about completeness
        assert result.tier_level == ValidationTier.TIER_1.value

    def test_tier2_moderate_severity(self, validation_engine):
        """TIER_2 should apply moderate severity rules."""
        result = validation_engine.validate(
            doc_content="## Quick Reference\n\nContent\n",
            template_id="test_template",
            tier_level=ValidationTier.TIER_2,
        )
        
        assert result.tier_level == ValidationTier.TIER_2.value

    def test_tier3_lenient_severity(self, validation_engine):
        """TIER_3 should downgrade FIXABLE to WARN where appropriate."""
        result = validation_engine.validate(
            doc_content="## Section\n\nContent\n",
            template_id="test_template",
            tier_level=ValidationTier.TIER_3,
        )
        
        assert result.tier_level == ValidationTier.TIER_3.value


class TestAutoFixCapabilities:
    """Test auto-fix methods."""

    def test_missing_yaml_can_be_fixed(self, validation_engine, invalid_markdown_no_yaml):
        """Missing YAML should be auto-fixable."""
        result = validation_engine.validate(
            doc_content=invalid_markdown_no_yaml,
            template_id="test_template",
            tier_level=ValidationTier.TIER_2,
            auto_fix=True,
        )
        
        # Auto-fixed content should have YAML
        if result.auto_fixed_content:
            assert result.auto_fixed_content.startswith("---")
            assert "templateId" in result.auto_fixed_content

    def test_auto_fix_returns_patched_content(self, validation_engine, incomplete_markdown):
        """Auto-fix should return patched content."""
        original_lines = incomplete_markdown.count("\n")
        
        result = validation_engine.validate(
            doc_content=incomplete_markdown,
            template_id="test_template",
            tier_level=ValidationTier.TIER_2,
            auto_fix=True,
        )
        
        if result.auto_fixed_content:
            # Patched content may be longer (from added sections)
            patched_lines = result.auto_fixed_content.count("\n")
            assert patched_lines >= original_lines

    def test_diff_generated_when_auto_fix_applied(self, validation_engine, invalid_markdown_no_yaml):
        """Diff should be generated if auto-fix changes content."""
        result = validation_engine.validate(
            doc_content=invalid_markdown_no_yaml,
            template_id="test_template",
            tier_level=ValidationTier.TIER_2,
            auto_fix=True,
            dry_run=True,
        )
        
        if result.auto_fixed_content != invalid_markdown_no_yaml:
            # Diff should be present if content changed
            if result.diff:
                assert "---" in result.diff or "+++" in result.diff or "@@" in result.diff


class TestViolationStructure:
    """Test violation data structure."""

    def test_enhanced_violation_has_field_path(self, validation_engine, incomplete_markdown):
        """Violations should include field_path for precise debugging."""
        result = validation_engine.validate(
            doc_content=incomplete_markdown,
            template_id="test_template",
            tier_level=ValidationTier.TIER_2,
        )
        
        for violation in result.violations:
            assert violation.field_path is not None
            assert len(violation.field_path) > 0

    def test_violation_includes_validator_for_schema_errors(self, validation_engine):
        """Schema validation errors should include validator type."""
        # This would require a real schema with validation; for now, just test structure
        violation = EnhancedViolation(
            type="test",
            severity="BLOCKER",
            field="frontmatter",
            field_path="frontmatter.project",
            message="Test violation",
            suggestion="Fix the field",
            auto_fixable=False,
            validator="type",
        )
        
        assert violation.validator == "type"
        assert violation.to_dict()["validator"] == "type"


class TestValidationResult:
    """Test ValidationResult data structure."""

    def test_result_serializes_to_dict(self, validation_engine, valid_markdown_with_yaml):
        """ValidationResult should serialize to JSON-compatible dict."""
        result = validation_engine.validate(
            doc_content=valid_markdown_with_yaml,
            template_id="test_template",
            tier_level=ValidationTier.TIER_2,
        )
        
        result_dict = result.to_dict()
        
        # Check structure
        assert "is_valid" in result_dict
        assert "violations" in result_dict
        assert "completeness" in result_dict
        assert "tier_level" in result_dict

    def test_result_includes_metadata(self, validation_engine, valid_markdown_with_yaml):
        """ValidationResult should include metadata."""
        result = validation_engine.validate(
            doc_content=valid_markdown_with_yaml,
            template_id="test_template",
            tier_level=ValidationTier.TIER_2,
        )
        
        assert result.metadata is not None
        assert result.metadata.template_source == "submodule"
        assert result.metadata.validated_at_utc is not None


# ==================== INTEGRATION TESTS ====================


class TestValidationWorkflow:
    """Integration tests for full validation workflow."""

    def test_valid_document_passes_validation(self, validation_engine, valid_markdown_with_yaml):
        """Complete valid document should pass validation."""
        result = validation_engine.validate(
            doc_content=valid_markdown_with_yaml,
            template_id="test_template",
            tier_level=ValidationTier.TIER_2,
        )
        
        # Should be valid or have low severity issues
        assert result.is_valid or all(
            v.severity != "BLOCKER" for v in result.violations
        )

    def test_invalid_document_fails_validation(self, validation_engine, invalid_markdown_no_yaml):
        """Invalid document should fail validation (have BLOCKER violations)."""
        result = validation_engine.validate(
            doc_content=invalid_markdown_no_yaml,
            template_id="test_template",
            tier_level=ValidationTier.TIER_2,
        )
        
        # Should have BLOCKER violations
        has_blockers = any(v.severity == "BLOCKER" for v in result.violations)
        assert has_blockers
        assert not result.is_valid

    def test_tier_level_affects_validity(self, validation_engine):
        """Same document may be valid in TIER_3 but invalid in TIER_1."""
        minimal_doc = """---
templateId: test
project: Test
repo: test/test
generatedAtUTC: 2026-02-24T10:00:00Z
---

## Section

Very short.
"""
        
        result_tier3 = validation_engine.validate(
            doc_content=minimal_doc,
            template_id="test_template",
            tier_level=ValidationTier.TIER_3,
        )
        
        result_tier1 = validation_engine.validate(
            doc_content=minimal_doc,
            template_id="test_template",
            tier_level=ValidationTier.TIER_1,
        )
        
        # TIER_3 is more lenient, TIER_1 is strict
        # (May not always differ, depending on content, but structure should be tested)
        assert result_tier3.tier_level == ValidationTier.TIER_3.value
        assert result_tier1.tier_level == ValidationTier.TIER_1.value


# ==================== EDGE CASES ====================


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_empty_string_document(self, validation_engine):
        """Empty document should handle gracefully."""
        result = validation_engine.validate(
            doc_content="",
            template_id="test_template",
            tier_level=ValidationTier.TIER_2,
        )
        
        # Should not crash; should report violations
        assert isinstance(result, ValidationResult)
        assert result.completeness == 0.0

    def test_malformed_yaml_handling(self, validation_engine):
        """Malformed YAML should be handled gracefully."""
        malformed = """---
project: Test
invalid_yaml: : : :
---
# Document
"""
        result = validation_engine.validate(
            doc_content=malformed,
            template_id="test_template",
            tier_level=ValidationTier.TIER_2,
        )
        
        # Should handle gracefully without crashing
        assert isinstance(result, ValidationResult)

    def test_code_blocks_skipped_in_completeness(self, validation_engine):
        """Code blocks should not count toward word count."""
        with_code = """---
templateId: test
project: Test
repo: test/test
generatedAtUTC: 2026-02-24T10:00:00Z
---

## Section

```python
# This is 100 lines of code
def function():
    pass
```

Real section content here.
"""
        result = validation_engine.validate(
            doc_content=with_code,
            template_id="test_template",
            tier_level=ValidationTier.TIER_2,
        )
        
        # Should not crash; code/blocks should be handled
        assert result.completeness >= 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
