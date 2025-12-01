"""Fix FunctionTool calls in test files by adding .fn attribute and sys.path fixes."""
import re
from pathlib import Path

def fix_file(file_path: Path, service_name: str):
    """Fix a single test file."""
    content = file_path.read_text(encoding='utf-8')
    original = content
    
    # Pattern to find "await function_name(" calls
    # We need to add .fn before the opening parenthesis
    pattern = r'(result\s*=\s*await\s+)(\w+)\('
    
    def replacer(match):
        prefix = match.group(1)
        func_name = match.group(2)
        # Only fix if it's a known MCP tool function (starts with lowercase, not a mock)
        if func_name[0].islower() and not func_name.startswith('mock'):
            return f'{prefix}{func_name}.fn('
        return match.group(0)
    
    content = re.sub(pattern, replacer, content)
    
    # Add sys.path manipulation after imports from app.services
    # Find: from app.services.X import Y
    # Replace with: 
    #   import sys
    #   sys.path.insert(0, 'src/services/mcp-server')
    #   from app.services.X import Y
    #   sys.path.pop(0)
    
    import_pattern = r'(\s+)(from app\.services\.\w+ import [^\n]+)'
    
    def import_replacer(match):
        indent = match.group(1)
        import_line = match.group(2)
        return f'''{indent}import sys
{indent}sys.path.insert(0, 'src/services/{service_name}')
{indent}{import_line}
{indent}sys.path.pop(0)'''
    
    content = re.sub(import_pattern, import_replacer, content)
    
    if content != original:
        file_path.write_text(content, encoding='utf-8')
        print(f"Fixed {file_path}")
        return True
    return False

# Fix all service test files
test_dir = Path('tests/mcp-server')
files_to_fix = [
    ('test_services_asset.py', 'mcp-server'),
    ('test_services_asset_model.py', 'mcp-server'),
    ('test_services_realm.py', 'mcp-server'),
    ('test_services_rule.py', 'mcp-server'),
]

fixed_count = 0
for filename, service in files_to_fix:
    file_path = test_dir / filename
    if file_path.exists():
        if fix_file(file_path, service):
            fixed_count += 1

print(f"\nFixed {fixed_count} files")
