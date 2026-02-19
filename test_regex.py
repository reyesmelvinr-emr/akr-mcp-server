"""
Quick test to verify template population regex works
"""

import re

# Sample template section
template = """
### Endpoints

🤖 [AI: Extract from ApiRoutes.cs and controller [Http*] attributes]

| Method | Route | Purpose | Auth |
|--------|-------|---------|------|
| 🤖 `GET` | 🤖 `/v1/[resource]` | 🤖 Get all | 🤖 Yes |
| 🤖 `GET` | 🤖 `/v1/[resource]/{id}` | 🤖 Get by ID | 🤖 Yes |
"""

# Test replacement content
replacement_content = """| Method | Path | Handler | Response Types |
|--------|------|---------|----------------|
| **GET** | `/api/courses` | `GetAllAsync()` | `IEnumerable<CourseDto>` |
| **GET** | `/api/courses/{id}` | `GetByIdAsync()` | `CourseDto` |"""

# Pattern from code_analyzer.py
section_name = "Endpoints"
section_header_pattern = rf'(###+\s+{re.escape(section_name)}[^\n]*\n+)(🤖[^\n]+\n+)(\|[^\n]+\|[^\n]+\n\|[-:\s|]+\n(?:\|[^\n]+\n)*)'

print("Testing regex pattern...")
print(f"Pattern: {section_header_pattern}\n")

match = re.search(section_header_pattern, template, re.IGNORECASE)

if match:
    print("✅ Pattern MATCHED!")
    print(f"\nCapture groups:")
    print(f"Group 1 (header): {repr(match.group(1))}")
    print(f"Group 2 (instruction): {repr(match.group(2))}")
    print(f"Group 3 (table): {repr(match.group(3))}")
    
    # Test replacement
    replacement = rf'\1<!-- AI-extracted: {section_name} -->\n{replacement_content}\n\n'
    result = re.sub(section_header_pattern, replacement, template, flags=re.IGNORECASE, count=1)
    
    print(f"\n✅ After replacement:")
    print(result)
else:
    print("❌ Pattern DID NOT match")
    print("\nTrying to debug...")
    
    # Test individual components
    header_pattern = rf'###+\s+{re.escape(section_name)}[^\n]*\n+'
    if re.search(header_pattern, template):
        print("  ✅ Header pattern matches")
    else:
        print("  ❌ Header pattern doesn't match")
    
    instruction_pattern = r'🤖[^\n]+\n+'
    if re.search(instruction_pattern, template):
        print("  ✅ Instruction pattern matches")
    else:
        print("  ❌ Instruction pattern doesn't match")
    
    table_pattern = r'\|[^\n]+\|[^\n]+\n\|[-:\s|]+\n(?:\|[^\n]+\n)*'
    if re.search(table_pattern, template):
        print("  ✅ Table pattern matches")
    else:
        print("  ❌ Table pattern doesn't match")
