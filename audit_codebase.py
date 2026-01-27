import os
import re
import ast

def check_python_file(file_path):
    """Check a Python file for syntax errors."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        ast.parse(content)
        return None
    except SyntaxError as e:
        return f"SyntaxError: {e.msg} at line {e.lineno}"
    except Exception as e:
        return f"Error reading file: {e}"

def check_template_file(file_path):
    """Check a Django template for split tags and raw code artifacts."""
    errors = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Check for split tags {% ... \n ... %}
        match = re.search(r'{%[^%\}]*\n[^%]*%}', content)
        if match:
            errors.append(f"Split Django tag detected: {repr(match.group(0))}")
            
        # Check for raw var tags {{ ... \n ... }}
        if re.search(r'{{[^}\n]*\n[^}]*}}', content):
            errors.append("Split Django variable tag detected (multi-line {{ }})")
            
    except Exception as e:
        errors.append(f"Error reading file: {e}")
        
    return errors

def scan_codebase(root_dir):
    print(f"Scanning codebase at: {root_dir}")
    issues_found = 0
    
    for root, dirs, files in os.walk(root_dir):
        # Skip virtual envs and git
        if 'venv' in root or '.git' in root or '__pycache__' in root:
            continue
            
        for file in files:
            file_path = os.path.join(root, file)
            
            if file.endswith('.py'):
                error = check_python_file(file_path)
                if error:
                    print(f"[PYTHON] {file_path}")
                    print(f"   - {error}")
                    issues_found += 1
                    
                errors = check_template_file(file_path)
                if errors:
                    print(f"[TEMPLATE] {file_path}")
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                    for err in errors:
                        print(f"   - {err}")
                        # visual aid
                        if "Split Django variable" in err:
                            import re
                            match = re.search(r'{{[^}\n]*\n[^}]*}}', content)
                            if match:
                                print(f"     MATCH: {repr(match.group(0))}")
                    issues_found += 1

    if issues_found == 0:
        print("\nCodebase verification complete. No issues found.")
    else:
        print(f"\nVerification complete. Found issues in {issues_found} files.")

if __name__ == "__main__":
    scan_codebase(os.getcwd())
