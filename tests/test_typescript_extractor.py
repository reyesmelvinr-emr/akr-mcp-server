"""
Unit tests for TypeScript/React code extractor
"""

import pytest
from pathlib import Path
from src.tools.extractors.typescript_extractor import TypeScriptExtractor


def test_typescript_can_extract():
    """Test that TypeScriptExtractor identifies TypeScript files"""
    extractor = TypeScriptExtractor()
    
    assert extractor.can_extract(Path("test.ts")) == True
    assert extractor.can_extract(Path("test.tsx")) == True
    assert extractor.can_extract(Path("Test.TSX")) == True
    assert extractor.can_extract(Path("test.js")) == True
    assert extractor.can_extract(Path("test.cs")) == False


def test_typescript_extract_function_component():
    """Test extraction of React function component"""
    code = """
import React from 'react';

interface ButtonProps {
    label: string;
    onClick: () => void;
    disabled?: boolean;
}

export function Button({ label, onClick, disabled = false }: ButtonProps) {
    const [isPressed, setIsPressed] = React.useState(false);
    
    const handleClick = () => {
        setIsPressed(true);
        onClick();
    };
    
    return (
        <button onClick={handleClick} disabled={disabled} className="btn-primary">
            {label}
        </button>
    );
}
"""
    
    test_file = Path("test_button.tsx")
    try:
        test_file.write_text(code, encoding='utf-8')
        
        extractor = TypeScriptExtractor()
        data = extractor.extract(test_file)
        
        assert len(data.components) == 1
        component = data.components[0]
        
        assert component.name == 'Button'
        assert len(component.props) == 3
        assert component.props[0].name == 'label'
        assert component.props[0].type == 'string'
        assert component.props[0].is_required == True
        
        assert len(component.state_variables) == 1
        assert component.state_variables[0]['name'] == 'isPressed'
        
        assert 'handleClick' in component.event_handlers
    finally:
        if test_file.exists():
            test_file.unlink()


def test_typescript_extract_with_hooks():
    """Test extraction of hooks usage"""
    code = """
import React, { useState, useEffect, useCallback } from 'react';

export function DataLoader() {
    const [data, setData] = useState<any>(null);
    
    useEffect(() => {
        fetchData();
    }, []);
    
    const fetchData = useCallback(() => {
        // fetch logic
    }, []);
    
    return <div>{data}</div>;
}
"""
    
    test_file = Path("test_hooks.tsx")
    try:
        test_file.write_text(code, encoding='utf-8')
        
        extractor = TypeScriptExtractor()
        data = extractor.extract(test_file)
        
        component = data.components[0]
        assert 'useState' in component.hooks
        assert 'useEffect' in component.hooks
        assert 'useCallback' in component.hooks
    finally:
        if test_file.exists():
            test_file.unlink()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
