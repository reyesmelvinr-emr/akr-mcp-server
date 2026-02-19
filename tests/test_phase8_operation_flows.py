"""
Unit tests for Phase 8: Operation Flow Extraction

Tests the MethodFlowAnalyzer module and integration with the extraction pipeline.
"""

import pytest
from pathlib import Path
from tools.extractors.method_flow_analyzer import (
    MethodFlowAnalyzer, OperationFlow, FlowStep, FlowStepType
)
from tools.extractors.csharp_extractor import CSharpExtractor
from tools.context_builder import build_service_context


class TestMethodFlowAnalyzer:
    """Test MethodFlowAnalyzer functionality."""
    
    def test_extract_create_flow(self):
        """Test extraction of Create operation flow."""
        source_code = '''
        public class CourseService
        {
            public async Task<CourseDetailDto> CreateCourseAsync(CreateCourseRequest request)
            {
                // Validate input
                if (request == null)
                    throw new ArgumentNullException(nameof(request));
                
                // Check if exists
                var existing = await _repo.GetByIdAsync(request.Id);
                if (existing != null)
                    throw new ConflictException("Course already exists");
                
                // Create entity
                var course = new Course
                {
                    Title = request.Title,
                    IsRequired = request.IsRequired
                };
                
                // Save to database
                await _repo.AddAsync(course);
                await _repo.SaveChangesAsync();
                
                // Map to DTO
                return _mapper.Map<CourseDetailDto>(course);
            }
        }
        '''
        
        analyzer = MethodFlowAnalyzer()
        flows = analyzer.extract_flows(source_code, "CourseService.cs")
        
        assert len(flows) > 0, "Should extract at least one flow"
        
        flow = flows[0]
        assert flow.method_name == "CreateCourseAsync"
        assert flow.operation_type == "Create"
        assert len(flow.steps) > 0, "Should have at least one step"
        
        # Check for validation step
        has_validation = any(s.step_type == FlowStepType.VALIDATION for s in flow.steps)
        assert has_validation, "Should detect validation step"
        
        # Check for query step
        has_query = any(s.step_type == FlowStepType.QUERY for s in flow.steps)
        assert has_query, "Should detect query step"
        
        # Check for persistence step
        has_persistence = any(s.step_type == FlowStepType.PERSISTENCE for s in flow.steps)
        assert has_persistence, "Should detect persistence step"
    
    def test_generate_ascii_diagram(self):
        """Test ASCII diagram generation."""
        flow = OperationFlow(
            method_name="CreateAsync",
            operation_type="Create"
        )
        
        flow.steps.append(FlowStep(
            step_number=1,
            step_type=FlowStepType.VALIDATION,
            description="Validate Inputs",
            what="Check parameters",
            why="Ensure valid data",
            error_path="400 BadRequest"
        ))
        
        flow.steps.append(FlowStep(
            step_number=2,
            step_type=FlowStepType.PERSISTENCE,
            description="Save Data",
            what="Persist to database",
            why="Make changes durable",
            error_path="500 InternalServerError"
        ))
        
        diagram = flow.generate_ascii_diagram()
        
        assert "Step 1: Validate Inputs" in diagram
        assert "Step 2: Save Data" in diagram
        assert "┌─" in diagram  # Box characters
        assert "↓" in diagram  # Arrow
        assert "SUCCESS" in diagram
    
    def test_operation_type_detection(self):
        """Test operation type is correctly determined from method name."""
        analyzer = MethodFlowAnalyzer()
        
        assert analyzer._determine_operation_type("CreateAsync") == "Create"
        assert analyzer._determine_operation_type("UpdateCourseAsync") == "Update"
        assert analyzer._determine_operation_type("DeleteAsync") == "Delete"
        assert analyzer._determine_operation_type("GetByIdAsync") == "Query"
        assert analyzer._determine_operation_type("AddCourse") == "Create"
    
    def test_pattern_detection(self):
        """Test pattern detection for different step types."""
        analyzer = MethodFlowAnalyzer()
        
        # Validation patterns
        validation_code = "if (course == null) throw new ArgumentNullException();"
        assert analyzer._contains_pattern(validation_code, analyzer.validation_patterns)
        
        # Query patterns
        query_code = "var course = await _repo.FirstOrDefaultAsync(x => x.Id == id);"
        assert analyzer._contains_pattern(query_code, analyzer.query_patterns)
        
        # Persistence patterns
        persistence_code = "await _context.SaveChangesAsync();"
        assert analyzer._contains_pattern(persistence_code, analyzer.persistence_patterns)
        
        # Mapping patterns
        mapping_code = "return _mapper.Map<CourseDto>(course);"
        assert analyzer._contains_pattern(mapping_code, analyzer.mapping_patterns)
    
    def test_multiple_flows_extraction(self):
        """Test extraction of multiple operation flows from one file."""
        source_code = '''
        public class CourseService
        {
            public async Task<Course> CreateAsync(CreateRequest req)
            {
                if (req == null) throw new ArgumentNullException();
                await _repo.AddAsync(req);
                return req;
            }
            
            public async Task<Course> UpdateAsync(UpdateRequest req)
            {
                var existing = await _repo.GetByIdAsync(req.Id);
                existing.Update(req);
                await _repo.SaveChangesAsync();
                return existing;
            }
            
            public async Task DeleteAsync(Guid id)
            {
                var course = await _repo.FindAsync(id);
                await _repo.Remove(course);
            }
        }
        '''
        
        analyzer = MethodFlowAnalyzer()
        flows = analyzer.extract_flows(source_code, "CourseService.cs")
        
        assert len(flows) == 3, "Should extract all three CRUD operations"
        
        method_names = [f.method_name for f in flows]
        assert "CreateAsync" in method_names
        assert "UpdateAsync" in method_names
        assert "DeleteAsync" in method_names


class TestPhase8Integration:
    """Test Phase 8 integration with the extraction pipeline."""
    
    def test_csharp_extractor_includes_flows(self):
        """Test that CSharpExtractor extracts operation flows."""
        source_code = '''
        public class CourseService
        {
            public async Task<CourseDetailDto> CreateCourseAsync(CreateCourseRequest request)
            {
                if (request == null) throw new ArgumentNullException();
                var course = new Course { Title = request.Title };
                await _repo.AddAsync(course);
                await _repo.SaveChangesAsync();
                return _mapper.Map<CourseDetailDto>(course);
            }
        }
        '''
        
        # Write to temp file
        temp_file = Path("test_service.cs")
        temp_file.write_text(source_code)
        
        try:
            extractor = CSharpExtractor()
            extracted = extractor.extract(temp_file)
            
            assert hasattr(extracted, 'operation_flows'), "Should have operation_flows field"
            assert len(extracted.operation_flows) > 0, "Should extract at least one flow"
            
            flow = extracted.operation_flows[0]
            assert flow.method_name == "CreateCourseAsync"
            assert flow.operation_type == "Create"
        finally:
            if temp_file.exists():
                temp_file.unlink()
    
    def test_context_builder_transforms_flows(self):
        """Test that context builder transforms flows into template context."""
        source_code = '''
        public class CourseService
        {
            public async Task<Course> UpdateAsync(UpdateRequest req)
            {
                if (req == null) throw new ArgumentNullException();
                var existing = await _repo.GetByIdAsync(req.Id);
                if (existing == null) throw new NotFoundException();
                existing.Title = req.Title;
                await _repo.SaveChangesAsync();
                return existing;
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
            
            assert hasattr(context, 'operation_flows'), "Context should have operation_flows"
            assert len(context.operation_flows) > 0, "Should have transformed flows"
            
            flow_dict = context.operation_flows[0]
            assert 'method_name' in flow_dict
            assert 'operation_type' in flow_dict
            assert 'ascii_diagram' in flow_dict
            assert 'steps' in flow_dict
            
            # Verify ASCII diagram was generated
            assert len(flow_dict['ascii_diagram']) > 0
            assert '┌─' in flow_dict['ascii_diagram']  # Box characters
        finally:
            if temp_file.exists():
                temp_file.unlink()


class TestRealWorldFlow:
    """Test with realistic CourseService method."""
    
    def test_course_service_create_flow(self):
        """Test extraction from realistic CourseService.CreateAsync method."""
        source_code = '''
        public class CourseService : ICourseService
        {
            private readonly ICourseRepository _repo;
            private readonly IMapper _mapper;
            private readonly ILogger<CourseService> _logger;
            
            public async Task<CourseDetailDto> CreateAsync(CreateCourseRequest request)
            {
                _logger.LogInformation("Creating course: {Title}", request.Title);
                
                // Validate request
                if (request == null)
                    throw new ArgumentNullException(nameof(request));
                
                if (string.IsNullOrWhiteSpace(request.Title))
                    throw new ArgumentException("Title is required", nameof(request.Title));
                
                // Check for duplicates
                var existing = await _repo.GetByTitleAsync(request.Title);
                if (existing != null)
                {
                    _logger.LogWarning("Course with title {Title} already exists", request.Title);
                    throw new DuplicateCourseException($"Course '{request.Title}' already exists");
                }
                
                // Create entity
                var course = new Course
                {
                    Id = Guid.NewGuid(),
                    Title = request.Title,
                    Description = request.Description,
                    IsRequired = request.IsRequired,
                    ValidityMonths = request.ValidityMonths,
                    CreatedUtc = DateTime.UtcNow
                };
                
                // Persist
                await _repo.AddAsync(course);
                await _repo.SaveChangesAsync();
                
                _logger.LogInformation("Successfully created course {Id}", course.Id);
                
                // Return DTO
                return _mapper.Map<CourseDetailDto>(course);
            }
        }
        '''
        
        analyzer = MethodFlowAnalyzer()
        flows = analyzer.extract_flows(source_code, "CourseService.cs")
        
        assert len(flows) > 0
        
        flow = flows[0]
        assert flow.method_name == "CreateAsync"
        assert flow.operation_type == "Create"
        
        # Should have multiple steps
        assert len(flow.steps) >= 3, "Should have validation, query, and persistence steps"
        
        # Generate diagram and check format
        diagram = flow.generate_ascii_diagram()
        assert "Step 1:" in diagram
        assert "What  →" in diagram
        assert "Why   →" in diagram
        assert len(diagram.split('\n')) > 10, "Diagram should have multiple lines"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
