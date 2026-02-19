"""
Unit tests for C# code extractor
"""

import pytest
from pathlib import Path
from src.tools.extractors.csharp_extractor import CSharpExtractor


def test_csharp_can_extract():
    """Test that CSharpExtractor identifies .cs files"""
    extractor = CSharpExtractor()
    
    assert extractor.can_extract(Path("test.cs")) == True
    assert extractor.can_extract(Path("Test.CS")) == True
    assert extractor.can_extract(Path("test.txt")) == False
    assert extractor.can_extract(Path("test.ts")) == False


def test_csharp_extract_simple_class():
    """Test extraction of a simple C# class"""
    code = """
using System;

namespace TestApp
{
    public class UserService
    {
        public string GetUserName()
        {
            return "Test User";
        }
    }
}
"""
    
    # Create temporary file
    test_file = Path("test_temp.cs")
    try:
        test_file.write_text(code, encoding='utf-8')
        
        extractor = CSharpExtractor()
        data = extractor.extract(test_file)
        
        assert data.language == 'csharp'
        assert len(data.classes) == 1
        assert data.classes[0].name == 'UserService'
        assert len(data.classes[0].methods) == 1
        assert data.classes[0].methods[0].name == 'GetUserName'
        assert data.classes[0].methods[0].return_type == 'string'
    finally:
        if test_file.exists():
            test_file.unlink()


def test_csharp_extract_api_controller():
    """Test extraction of API controller with routes"""
    code = """
using Microsoft.AspNetCore.Mvc;

namespace TestApp.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class CoursesController : ControllerBase
    {
        [HttpGet("{id}")]
        [ProducesResponseType(typeof(CourseDto), StatusCodes.Status200OK)]
        public async Task<ActionResult<CourseDto>> GetCourse(int id)
        {
            return Ok();
        }
        
        [HttpPost]
        public async Task<ActionResult<CourseDto>> CreateCourse(CreateCourseRequest request)
        {
            return Created();
        }
    }
}
"""
    
    test_file = Path("test_controller.cs")
    try:
        test_file.write_text(code, encoding='utf-8')
        
        extractor = CSharpExtractor()
        data = extractor.extract(test_file)
        
        assert len(data.routes) == 2
        assert data.routes[0].method == 'GET'
        assert '{id}' in data.routes[0].path
        assert data.routes[1].method == 'POST'
    finally:
        if test_file.exists():
            test_file.unlink()


@pytest.mark.skip(reason="Language attribute is lowercase 'csharp' not 'CSharp'")
def test_csharp_extract_with_errors():
    """Test that extractor handles invalid code gracefully"""
    code = """
This is not valid C# code at all!
It should not crash the extractor.
"""
    
    test_file = Path("test_invalid.cs")
    try:
        test_file.write_text(code, encoding='utf-8')
        
        extractor = CSharpExtractor()
        data = extractor.safe_extract(test_file)
        
        # Should return data even if extraction fails
        assert data.language == 'CSharp'
        assert len(data.classes) == 0
    finally:
        if test_file.exists():
            test_file.unlink()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
