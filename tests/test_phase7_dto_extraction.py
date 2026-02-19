"""
Phase 7 Unit Tests: DTO and Request-Response Extraction

Tests for:
- DTOExtractor: Extract properties, types, DataAnnotations from C# DTOs
- Context Builder: Transform DTOs to template context
- Template Rendering: DTO examples in Jinja2 output
"""

import pytest
from pathlib import Path
from src.tools.extractors.dto_extractor import DTOExtractor, DTOProperty, ValidationRule, ExtractedDTO
from src.tools.extractors.csharp_extractor import CSharpExtractor


class TestDTOExtraction:
    """Test DTO property and validation extraction."""
    
    def test_extract_dto_properties(self):
        """Test extraction of DTO properties."""
        sample_code = '''
        public class CreateCourseRequest
        {
            public string Title { get; set; }
            public bool IsRequired { get; set; }
            public int? ValidityMonths { get; set; }
            public string? Category { get; set; }
        }
        '''
        
        extractor = DTOExtractor()
        dtos = extractor.extract_dtos(sample_code, "test.cs")
        
        assert len(dtos) == 1
        dto = dtos[0]
        assert dto.name == "CreateCourseRequest"
        assert len(dto.properties) == 4
        
        # Check properties
        property_names = [p.name for p in dto.properties]
        assert "Title" in property_names
        assert "IsRequired" in property_names
        assert "ValidityMonths" in property_names
        assert "Category" in property_names
        
        # Check nullability
        title_prop = next(p for p in dto.properties if p.name == "Title")
        assert not title_prop.nullable
        
        validity_prop = next(p for p in dto.properties if p.name == "ValidityMonths")
        assert validity_prop.nullable
        
    def test_extract_data_annotations(self):
        """Test extraction of DataAnnotations attributes."""
        sample_code = '''
        public class UpdateCourseRequest
        {
            [Required]
            public string Title { get; set; }
            
            [StringLength(255)]
            public string? Description { get; set; }
            
            [Range(1, 60)]
            public int? ValidityMonths { get; set; }
        }
        '''
        
        extractor = DTOExtractor()
        dtos = extractor.extract_dtos(sample_code, "test.cs")
        
        assert len(dtos) == 1
        dto = dtos[0]
        
        # Check Required attribute
        title_prop = next(p for p in dto.properties if p.name == "Title")
        assert title_prop.required
        
        # Check StringLength attribute
        description_prop = next(p for p in dto.properties if p.name == "Description")
        assert "StringLength" in description_prop.attributes
        
    def test_generate_sample_json(self):
        """Test sample JSON generation for DTOs."""
        sample_code = '''
        public class CourseDetailDto
        {
            public Guid Id { get; set; }
            public string Title { get; set; }
            public bool IsRequired { get; set; }
            public DateTime CreatedUtc { get; set; }
        }
        '''
        
        extractor = DTOExtractor()
        dtos = extractor.extract_dtos(sample_code, "test.cs")
        dto = dtos[0]
        
        sample = extractor.generate_sample_json(dto)
        
        assert "Id" in sample
        assert "Title" in sample
        assert "IsRequired" in sample
        assert "CreatedUtc" in sample
        
        # Check that values are properly typed
        assert isinstance(sample["IsRequired"], bool)
        assert sample["IsRequired"] == True
        
    def test_determine_dto_type(self):
        """Test DTO type inference from class name."""
        extractor = DTOExtractor()
        
        assert extractor._determine_dto_type("CreateCourseRequest") == "CreateRequest"
        assert extractor._determine_dto_type("UpdateCourseRequest") == "UpdateRequest"
        assert extractor._determine_dto_type("CourseDetailDto") == "DetailResponse"
        assert extractor._determine_dto_type("CourseListResponse") == "ListResponse"
        assert extractor._determine_dto_type("CoursesContract") == "Contract"
        
    def test_generate_validation_matrix(self):
        """Test validation matrix generation for templates."""
        sample_code = '''
        public class CourseRequest
        {
            [Required]
            [StringLength(255)]
            public string Title { get; set; }
            
            public bool IsRequired { get; set; }
        }
        '''
        
        extractor = DTOExtractor()
        dtos = extractor.extract_dtos(sample_code, "test.cs")
        dto = dtos[0]
        
        matrix = extractor.generate_validation_matrix(dto)
        
        # Should have validation rules for Title
        title_validations = [m for m in matrix if m['property'] == 'Title']
        assert len(title_validations) > 0
        
        # Check matrix structure
        for rule in matrix:
            assert 'property' in rule
            assert 'rule' in rule
            assert 'error_message' in rule
            
    def test_csharp_extractor_includes_dtos(self):
        """Test that CSharpExtractor includes DTOs in extraction."""
        test_file = Path("test_dtos.cs")
        
        sample_code = '''
        namespace TestApp
        {
            public class CourseRequest
            {
                public string Title { get; set; }
                public bool IsRequired { get; set; }
            }
            
            public class CourseResponse
            {
                public Guid Id { get; set; }
                public string Title { get; set; }
            }
        }
        '''
        
        # Write temporary test file
        test_file.write_text(sample_code)
        
        try:
            extractor = CSharpExtractor()
            extracted = extractor.extract(test_file)
            
            # Should extract DTOs
            assert len(extracted.dtos) >= 2
            
            dto_names = [dto.name for dto in extracted.dtos]
            assert "CourseRequest" in dto_names
            assert "CourseResponse" in dto_names
            
        finally:
            test_file.unlink(missing_ok=True)


class TestDTOContextTransformation:
    """Test transformation of DTOs to template context."""
    
    def test_dto_fields_in_context(self):
        """Test that DTOs populate request_response_examples and request_response_schemas."""
        from src.tools.context_builder import build_service_context
        from src.tools.extractors.base_extractor import ExtractedData
        
        # Create mock extracted data with DTOs
        extracted = ExtractedData(language='csharp', file_path='test.cs')
        
        # Extract from real code
        sample_code = '''
        public class CreateCourseRequest
        {
            [Required]
            public string Title { get; set; }
            public bool IsRequired { get; set; }
        }
        '''
        
        dto_extractor = DTOExtractor()
        extracted.dtos = dto_extractor.extract_dtos(sample_code, 'test.cs')
        
        # Build context
        context = build_service_context(
            service_name="CourseService",
            extracted_data_list=[extracted],
            domain="Backend"
        )
        
        # Check that DTO data is in context
        assert len(context.request_response_examples) > 0 or len(context.request_response_schemas) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
