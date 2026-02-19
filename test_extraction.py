"""
Test code analysis on CoursesController
"""

import sys
from pathlib import Path

# Don't add src to sys.path - it causes import issues
# Import modules directly by their file paths
import importlib.util

spec = importlib.util.spec_from_file_location(
    "code_analyzer",
    Path(__file__).parent / "src" / "tools" / "code_analyzer.py"
)
code_analyzer_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(code_analyzer_module)

spec2 = importlib.util.spec_from_file_location(
    "csharp_extractor",
    Path(__file__).parent / "src" / "tools" / "extractors" / "csharp_extractor.py"
)
csharp_module = importlib.util.module_from_spec(spec2)
spec2.loader.exec_module(csharp_module)

CodeAnalyzer = code_analyzer_module.CodeAnalyzer

# Test file
test_file = r"C:\Users\E1481541\OneDrive - Emerson\Documents\CDS - Team Hawkeye\Training Test Workspace\training-tracker-backend\TrainingTracker.Api\Controllers\CoursesController.cs"

if not Path(test_file).exists():
    print(f"❌ Test file not found: {test_file}")
    sys.exit(1)

print(f"📄 Analyzing: {test_file}\n")

# Create analyzer with default config
config = {
    'enabled': True,
    'depth': 'full',
    'languages': ['csharp', 'typescript', 'sql']
}

analyzer = CodeAnalyzer(config=config)

# Analyze the file
results = analyzer.analyze_files([test_file], 'backend')

if results:
    data = results[0]
    print(f"✅ Extraction successful!\n")
    print(f"Language: {data.language}")
    print(f"Classes: {len(data.classes)}")
    print(f"Methods: {len(data.methods)}")
    print(f"Routes: {len(data.routes)}")
    print(f"Validations: {len(data.validations)}")
    print(f"Dependencies: {len(data.dependencies)}")
    print(f"Errors: {len(data.extraction_errors)}")
    print(f"Warnings: {len(data.extraction_warnings)}\n")
    
    if data.classes:
        print(f"📦 Classes:")
        for cls in data.classes:
            print(f"  - {cls.name} (base: {cls.base_classes})")
            print(f"    Methods: {len(cls.methods)}")
    
    if data.routes:
        print(f"\n🌐 Routes:")
        for route in data.routes:
            print(f"  - {route.method} {route.path} -> {route.handler_name}")
    
    if data.dependencies:
        print(f"\n🔗 Dependencies:")
        for dep in data.dependencies:
            print(f"  - {dep.name}: {dep.type}")
    
    if data.extraction_errors:
        print(f"\n❌ Errors:")
        for err in data.extraction_errors:
            print(f"  - {err}")
    
    if data.extraction_warnings:
        print(f"\n⚠️  Warnings:")
        for warn in data.extraction_warnings:
            print(f"  - {warn}")
    
    # Test template population
    print(f"\n📝 Testing template population...")
    template_sample = """
### Endpoints

🤖 [AI: Extract from ApiRoutes.cs and controller [Http*] attributes]

| Method | Route | Purpose | Auth |
|--------|-------|---------|------|
| 🤖 `GET` | 🤖 `/v1/[resource]` | 🤖 Get all | 🤖 Yes |
"""
    
    populated = analyzer.populate_template(template_sample, results)
    
    if "AI-extracted" in populated:
        print(f"✅ Template population WORKED!")
        print(f"\n{populated}")
    else:
        print(f"❌ Template population FAILED - no replacement occurred")
        print(f"Template after populate_template call:")
        print(populated)
else:
    print(f"❌ No results returned from analyzer")
