"""
Integration tests for CodeAnalyzer with template population
"""

import pytest
from pathlib import Path
from src.tools.code_analyzer import CodeAnalyzer


def test_code_analyzer_initialization():
    """Test CodeAnalyzer initialization with config"""
    config = {
        'enabled': True,
        'depth': 'full',
        'languages': ['csharp', 'typescript', 'sql']
    }
    
    analyzer = CodeAnalyzer(config)
    
    assert analyzer.enabled == True
    assert analyzer.depth == 'full'
    assert len(analyzer.extractors) == 3


def test_code_analyzer_analyze_csharp():
    """Test analyzing a simple C# file"""
    code = """
public class TestService
{
    public string GetData()
    {
        return "data";
    }
}
"""
    
    test_file = Path("test_service.cs")
    try:
        test_file.write_text(code, encoding='utf-8')
        
        analyzer = CodeAnalyzer()
        results = analyzer.analyze_files([str(test_file)], 'backend')
        
        assert len(results) == 1
        assert results[0].language == 'csharp'
        assert len(results[0].classes) == 1
    finally:
        if test_file.exists():
            test_file.unlink()


def test_code_analyzer_populate_template():
    """Test template population with extracted data"""
    template = """
# Test Service Documentation

## Methods

🤖 Describe the methods exposed by this service

## Dependencies

🤖 List the dependencies
"""
    
    code = """
public class TestService
{
    public string GetData(int id)
    {
        return "data";
    }
}
"""
    
    test_file = Path("test_populate.cs")
    try:
        test_file.write_text(code, encoding='utf-8')
        
        analyzer = CodeAnalyzer()
        results = analyzer.analyze_files([str(test_file)], 'backend')
        populated = analyzer.populate_template(template, results)
        
        # Check that methods section was populated
        assert 'GetData' in populated
        assert '🤖 Describe the methods' not in populated
        assert '<!-- AI-extracted: Methods -->' in populated
    finally:
        if test_file.exists():
            test_file.unlink()


def test_code_analyzer_fallback_on_error():
    """Test that analyzer handles errors gracefully"""
    # Non-existent file
    analyzer = CodeAnalyzer()
    results = analyzer.analyze_files(['nonexistent.cs'], 'backend')
    
    # Should return empty list, not crash
    assert isinstance(results, list)


def test_code_analyzer_disabled():
    """Test that analyzer respects enabled=false config"""
    config = {'enabled': False}
    
    code = """
public class TestService
{
    public string GetData() { return "data"; }
}
"""
    
    test_file = Path("test_disabled.cs")
    try:
        test_file.write_text(code, encoding='utf-8')
        
        analyzer = CodeAnalyzer(config)
        results = analyzer.analyze_files([str(test_file)], 'backend')
        
        # Should return empty list when disabled
        assert len(results) == 0
    finally:
        if test_file.exists():
            test_file.unlink()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
