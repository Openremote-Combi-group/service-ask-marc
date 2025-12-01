# Fix test imports script
import re
from pathlib import Path

def fix_test_file(file_path):
    """Fix imports in a test file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    
    # Fix all src.services.mcp_server patterns
    content = re.sub(r"from src\.services\.mcp_server\.app", "from app", content)
    content = re.sub(r"import src\.services\.mcp_server\.app", "import app", content)
    content = re.sub(r"'src\.services\.mcp_server\.app", "'app", content)
    content = re.sub(r'"src\.services\.mcp_server\.app', '"app', content)
    
    # Fix all src.services.mcp_client_api patterns  
    content = re.sub(r"from src\.services\.mcp_client_api\.app", "from app", content)
    content = re.sub(r"import src\.services\.mcp_client_api\.app", "import app", content)
    content = re.sub(r"'src\.services\.mcp_client_api\.app", "'app", content)
    content = re.sub(r'"src\.services\.mcp_client_api\.app', '"app', content)
    
    if content != original:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Fixed: {file_path}")
        return True
    return False

# Find all test files
test_root = Path('tests')
fixed_count = 0

for test_file in test_root.rglob('test_*.py'):
    if fix_test_file(test_file):
        fixed_count += 1

print(f"\nFixed {fixed_count} test files")
