"""
Unit tests for Phase 9: Business Rules & Use Cases

Tests the BusinessRuleExtractor module and integration with the extraction pipeline.
"""

import pytest
from pathlib import Path
from tools.extractors.business_rule_extractor import (
    BusinessRuleExtractor, BusinessRule, UseCase, FAQItem, RuleType
)
from tools.extractors.csharp_extractor import CSharpExtractor
from tools.context_builder import build_service_context


class TestBusinessRuleExtractor:
    """Test BusinessRuleExtractor functionality."""
    
    def test_extract_from_exceptions(self):
        """Test extraction of business rules from exception throws."""
        source_code = '''
        public class CourseService
        {
            public async Task CreateAsync(CreateCourseRequest request)
            {
                var existing = await _repo.GetByTitleAsync(request.Title);
                if (existing != null)
                {
                    throw new DuplicateCourseException("Course with this title already exists");
                }
                
                if (request == null)
                {
                    throw new ArgumentNullException(nameof(request));
                }
            }
        }
        '''
        
        extractor = BusinessRuleExtractor()
        rules = extractor.extract_business_rules(source_code, "CourseService.cs")
        
        assert len(rules) > 0, "Should extract at least one rule"
        
        # Check for uniqueness constraint
        duplicate_rules = [r for r in rules if 'duplicate' in r.description.lower() or 'unique' in r.description.lower()]
        assert len(duplicate_rules) > 0, "Should detect uniqueness constraint"
        
        duplicate_rule = duplicate_rules[0]
        assert duplicate_rule.rule_type == RuleType.CONSTRAINT
        assert "409 Conflict" in duplicate_rule.violation_consequence
        
        # Check for validation rule
        validation_rules = [r for r in rules if r.rule_type == RuleType.VALIDATION]
        assert len(validation_rules) > 0, "Should detect validation rule"
    
    def test_extract_from_data_annotations(self):
        """Test extraction of business rules from DataAnnotations."""
        source_code = '''
        public class CreateCourseRequest
        {
            [Required(ErrorMessage = "Title is required")]
            [StringLength(100, MinimumLength = 3)]
            public string Title { get; set; }
            
            [Range(1, 36, ErrorMessage = "ValidityMonths must be between 1 and 36")]
            public int ValidityMonths { get; set; }
        }
        '''
        
        extractor = BusinessRuleExtractor()
        rules = extractor.extract_business_rules(source_code, "CreateCourseRequest.cs")
        
        assert len(rules) >= 3, "Should extract multiple rules from DataAnnotations"
        
        # Check for Required rule
        required_rules = [r for r in rules if 'required' in r.description.lower()]
        assert len(required_rules) > 0, "Should detect Required attribute"
        
        # Check for StringLength rule
        length_rules = [r for r in rules if 'between 3 and 100' in r.description.lower()]
        assert len(length_rules) > 0, "Should detect StringLength with min/max"
        
        # Check for Range rule
        range_rules = [r for r in rules if 'between 1 and 36' in r.description.lower()]
        assert len(range_rules) > 0, "Should detect Range attribute"
    
    def test_extract_from_validations(self):
        """Test extraction of business rules from validation patterns."""
        source_code = '''
        public async Task UpdateAsync(UpdateRequest request)
        {
            if (request == null)
                throw new ArgumentNullException(nameof(request));
            
            if (string.IsNullOrWhiteSpace(request.Title))
                throw new ArgumentException("Title cannot be empty");
        }
        '''
        
        extractor = BusinessRuleExtractor()
        rules = extractor.extract_business_rules(source_code, "Service.cs")
        
        assert len(rules) >= 2, "Should extract validation rules"
        
        # Check for null check
        null_rules = [r for r in rules if 'null' in r.description.lower()]
        assert len(null_rules) > 0, "Should detect null validation"
        
        # Check for string validation
        string_rules = [r for r in rules if 'empty' in r.description.lower() or 'whitespace' in r.description.lower()]
        assert len(string_rules) > 0, "Should detect string validation"
    
    def test_extract_use_cases(self):
        """Test extraction of use cases from service methods."""
        source_code = '''
        public class CourseService
        {
            public async Task<CourseDto> CreateAsync(CreateRequest request)
            {
                // Create implementation
                return new CourseDto();
            }
            
            public async Task<CourseDto> UpdateAsync(Guid id, UpdateRequest request)
            {
                // Update implementation
                return new CourseDto();
            }
            
            public async Task DeleteAsync(Guid id)
            {
                // Delete implementation
            }
            
            public async Task<CourseDto> GetAsync(Guid id)
            {
                // Get implementation
                return new CourseDto();
            }
        }
        '''
        
        extractor = BusinessRuleExtractor()
        use_cases = extractor.extract_use_cases(source_code, "CourseService.cs")
        
        assert len(use_cases) == 4, "Should extract 4 use cases (CRUD operations)"
        
        # Verify use case structure
        create_use_case = next((uc for uc in use_cases if 'create' in uc.title.lower()), None)
        assert create_use_case is not None, "Should have Create use case"
        assert len(create_use_case.steps) > 0, "Use case should have steps"
        assert len(create_use_case.preconditions) > 0, "Use case should have preconditions"
        
        update_use_case = next((uc for uc in use_cases if 'update' in uc.title.lower()), None)
        assert update_use_case is not None, "Should have Update use case"
        
        delete_use_case = next((uc for uc in use_cases if 'delete' in uc.title.lower()), None)
        assert delete_use_case is not None, "Should have Delete use case"
        
        get_use_case = next((uc for uc in use_cases if 'retrieve' in uc.title.lower()), None)
        assert get_use_case is not None, "Should have Get/Retrieve use case"
    
    def test_extract_faq_items(self):
        """Test extraction of FAQ items from exceptions and validations."""
        source_code = '''
        public async Task CreateAsync(CreateRequest request)
        {
            if (!ModelState.IsValid)
            {
                return BadRequest(ModelState);
            }
            
            var existing = await _repo.FindByTitleAsync(request.Title);
            if (existing != null)
            {
                throw new DuplicateCourseException("Course with this title already exists");
            }
            
            var found = await _repo.GetAsync(id);
            if (found == null)
            {
                throw new NotFoundException("Course not found");
            }
        }
        '''
        
        extractor = BusinessRuleExtractor()
        faq_items = extractor.extract_faq_items(source_code, "Service.cs")
        
        assert len(faq_items) > 0, "Should extract FAQ items"
        
        # Check for validation FAQ
        validation_faq = next((faq for faq in faq_items if 'validation' in faq.question.lower()), None)
        assert validation_faq is not None, "Should have validation FAQ"
        assert validation_faq.category == "Validation"
        
        # Check for duplicate/conflict FAQ
        conflict_faq = next((faq for faq in faq_items if 'already exists' in faq.answer.lower()), None)
        assert conflict_faq is not None, "Should have conflict FAQ"
        
        # Check for not found FAQ
        notfound_faq = next((faq for faq in faq_items if 'not found' in faq.answer.lower()), None)
        assert notfound_faq is not None, "Should have not found FAQ"
    
    def test_rule_types_classification(self):
        """Test that rules are correctly classified by type."""
        source_code = '''
        public class Service
        {
            public async Task Process()
            {
                // Validation
                if (request == null)
                    throw new ArgumentNullException();
                
                // Constraint
                if (existing != null)
                    throw new DuplicateCourseException("Already exists");
                
                // Invariant
                if (course.IsPublished)
                    throw new InvalidOperationException("Cannot modify published course");
            }
        }
        '''
        
        extractor = BusinessRuleExtractor()
        rules = extractor.extract_business_rules(source_code, "Service.cs")
        
        # Should have different rule types
        rule_types = {r.rule_type for r in rules}
        assert RuleType.VALIDATION in rule_types, "Should have validation rules"
        assert RuleType.CONSTRAINT in rule_types, "Should have constraint rules"
        assert RuleType.INVARIANT in rule_types, "Should have invariant rules"


class TestPhase9Integration:
    """Test Phase 9 integration with the extraction pipeline."""
    
    def test_csharp_extractor_includes_phase9(self):
        """Test that CSharpExtractor extracts business rules, use cases, and FAQ."""
        source_code = '''
        public class CourseService
        {
            public async Task<CourseDto> CreateAsync(CreateCourseRequest request)
            {
                if (request == null)
                    throw new ArgumentNullException(nameof(request));
                
                var existing = await _repo.GetByTitleAsync(request.Title);
                if (existing != null)
                    throw new DuplicateCourseException("Course already exists");
                
                var course = new Course { Title = request.Title };
                await _repo.AddAsync(course);
                return _mapper.Map<CourseDto>(course);
            }
        }
        '''
        
        # Write to temp file
        temp_file = Path("test_service.cs")
        temp_file.write_text(source_code)
        
        try:
            extractor = CSharpExtractor()
            extracted = extractor.extract(temp_file)
            
            assert hasattr(extracted, 'enhanced_business_rules'), "Should have enhanced_business_rules field"
            assert hasattr(extracted, 'use_cases'), "Should have use_cases field"
            assert hasattr(extracted, 'faq_items'), "Should have faq_items field"
            
            assert len(extracted.enhanced_business_rules) > 0, "Should extract business rules"
            assert len(extracted.use_cases) > 0, "Should extract use cases"
            assert len(extracted.faq_items) > 0, "Should extract FAQ items"
        finally:
            if temp_file.exists():
                temp_file.unlink()
    
    def test_context_builder_transforms_phase9(self):
        """Test that context builder transforms Phase 9 data into template context."""
        source_code = '''
        public class CourseService
        {
            public async Task<Course> UpdateAsync(Guid id, UpdateRequest req)
            {
                if (req == null)
                    throw new ArgumentNullException(nameof(req));
                
                var course = await _repo.GetAsync(id);
                if (course == null)
                    throw new NotFoundException("Course not found");
                
                course.Update(req);
                await _repo.SaveAsync();
                return course;
            }
        }
        '''
        
        # Write to temp file
        temp_file = Path("test_service.cs")
        temp_file.write_text(source_code)
        
        try:
            extractor = CSharpExtractor()
            extracted = extractor.extract(temp_file)
            
            # Build service context
            context = build_service_context("TestService", [extracted])
            
            assert hasattr(context, 'enhanced_business_rules'), "Context should have enhanced_business_rules"
            assert hasattr(context, 'use_cases'), "Context should have use_cases"
            assert hasattr(context, 'faq_items'), "Context should have faq_items"
            
            assert len(context.enhanced_business_rules) > 0, "Should have transformed business rules"
            assert len(context.use_cases) > 0, "Should have transformed use cases"
            assert len(context.faq_items) > 0, "Should have transformed FAQ items"
            
            # Verify structure
            rule = context.enhanced_business_rules[0]
            assert 'description' in rule
            assert 'rule_type' in rule
            
            use_case = context.use_cases[0]
            assert 'title' in use_case
            assert 'steps' in use_case
            
            faq = context.faq_items[0]
            assert 'question' in faq
            assert 'answer' in faq
        finally:
            if temp_file.exists():
                temp_file.unlink()


class TestRealWorldExtraction:
    """Test with realistic CourseService code."""
    
    def test_course_service_business_rules(self):
        """Test extraction from realistic CourseService with multiple business rules."""
        source_code = '''
        public class CourseService : ICourseService
        {
            public async Task<CourseDto> CreateAsync(CreateCourseRequest request)
            {
                // Validate request
                if (request == null)
                    throw new ArgumentNullException(nameof(request));
                
                if (string.IsNullOrWhiteSpace(request.Title))
                    throw new ArgumentException("Title is required", nameof(request.Title));
                
                // BR: Course titles must be unique within the system
                var existing = await _repo.GetByTitleAsync(request.Title);
                if (existing != null)
                {
                    throw new DuplicateCourseException($"Course '{request.Title}' already exists");
                }
                
                // BR: Validity period must be reasonable (1-36 months)
                if (request.ValidityMonths < 1 || request.ValidityMonths > 36)
                {
                    throw new ArgumentException("Validity months must be between 1 and 36");
                }
                
                var course = new Course
                {
                    Id = Guid.NewGuid(),
                    Title = request.Title,
                    ValidityMonths = request.ValidityMonths,
                    CreatedUtc = DateTime.UtcNow
                };
                
                await _repo.AddAsync(course);
                return _mapper.Map<CourseDto>(course);
            }
        }
        '''
        
        extractor = BusinessRuleExtractor()
        
        # Extract business rules
        rules = extractor.extract_business_rules(source_code, "CourseService.cs")
        assert len(rules) >= 4, "Should extract multiple business rules"
        
        # Verify specific rules
        unique_title_rule = next((r for r in rules if 'unique' in r.description.lower()), None)
        assert unique_title_rule is not None, "Should detect unique title rule"
        
        validity_rule = next((r for r in rules if 'validity' in r.description.lower() or '1 and 36' in r.description), None)
        assert validity_rule is not None, "Should detect validity period rule"
        
        # Extract use cases
        use_cases = extractor.extract_use_cases(source_code, "CourseService.cs")
        assert len(use_cases) > 0, "Should extract use case"
        
        create_use_case = use_cases[0]
        assert 'create' in create_use_case.title.lower()
        assert len(create_use_case.steps) >= 3, "Should have multiple steps"
        
        # Extract FAQ
        faq_items = extractor.extract_faq_items(source_code, "CourseService.cs")
        assert len(faq_items) > 0, "Should extract FAQ items"
        
        # Verify FAQ categories
        categories = {faq.category for faq in faq_items}
        assert "Error Handling" in categories or "Validation" in categories


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
