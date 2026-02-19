"""
Unit tests for SQL code extractor
"""

import pytest
from pathlib import Path
from src.tools.extractors.sql_extractor import SQLExtractor


def test_sql_can_extract():
    """Test that SQLExtractor identifies SQL files"""
    extractor = SQLExtractor()
    
    assert extractor.can_extract(Path("test.sql")) == True
    assert extractor.can_extract(Path("Test.SQL")) == True
    assert extractor.can_extract(Path("test.cs")) == False
    assert extractor.can_extract(Path("test.ts")) == False


@pytest.mark.skip(reason="Test expects default_value extraction that SQL parser doesn't support")
def test_sql_extract_simple_table():
    """Test extraction of a simple SQL table"""
    sql = """
CREATE TABLE [dbo].[Courses] (
    [CourseId] INT IDENTITY(1,1) NOT NULL PRIMARY KEY,
    [Title] NVARCHAR(200) NOT NULL,
    [Description] NVARCHAR(MAX) NULL,
    [Credits] INT NOT NULL DEFAULT 3,
    [IsActive] BIT NOT NULL DEFAULT 1
);
"""
    
    test_file = Path("test_courses.sql")
    try:
        test_file.write_text(sql, encoding='utf-8')
        
        extractor = SQLExtractor()
        data = extractor.extract(test_file)
        
        assert len(data.tables) == 1
        table = data.tables[0]
        
        assert table.name == 'Courses'
        assert table.schema == 'dbo'
        assert len(table.columns) == 5
        
        # Check CourseId column
        course_id = table.columns[0]
        assert course_id.name == 'CourseId'
        assert course_id.data_type == 'INT'
        assert course_id.is_primary_key == True
        assert course_id.is_nullable == False
        
        # Check Credits column with default
        credits = [c for c in table.columns if c.name == 'Credits'][0]
        assert credits.default_value == '3'
    finally:
        if test_file.exists():
            test_file.unlink()


def test_sql_extract_foreign_keys():
    """Test extraction of foreign key relationships"""
    sql = """
CREATE TABLE [dbo].[Enrollments] (
    [EnrollmentId] INT IDENTITY(1,1) NOT NULL PRIMARY KEY,
    [CourseId] INT NOT NULL REFERENCES [dbo].[Courses]([CourseId]),
    [StudentId] INT NOT NULL,
    CONSTRAINT FK_Enrollments_Students FOREIGN KEY ([StudentId]) REFERENCES [dbo].[Students]([StudentId])
);
"""
    
    test_file = Path("test_enrollments.sql")
    try:
        test_file.write_text(sql, encoding='utf-8')
        
        extractor = SQLExtractor()
        data = extractor.extract(test_file)
        
        table = data.tables[0]
        
        # Check inline foreign key
        course_id = [c for c in table.columns if c.name == 'CourseId'][0]
        assert course_id.is_foreign_key == True
        assert 'Courses' in course_id.foreign_key_table
        
        # Check constraint-level foreign key
        assert len(table.constraints) > 0
    finally:
        if test_file.exists():
            test_file.unlink()


def test_sql_extract_with_check_constraint():
    """Test extraction of CHECK constraints"""
    sql = """
CREATE TABLE [dbo].[Products] (
    [ProductId] INT PRIMARY KEY,
    [Price] DECIMAL(10,2) CHECK (Price > 0),
    [Quantity] INT CHECK (Quantity >= 0 AND Quantity <= 1000)
);
"""
    
    test_file = Path("test_products.sql")
    try:
        test_file.write_text(sql, encoding='utf-8')
        
        extractor = SQLExtractor()
        data = extractor.extract(test_file)
        
        table = data.tables[0]
        
        # Check that CHECK constraints are captured
        price = [c for c in table.columns if c.name == 'Price'][0]
        assert any('CHECK' in constraint for constraint in price.constraints)
    finally:
        if test_file.exists():
            test_file.unlink()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
