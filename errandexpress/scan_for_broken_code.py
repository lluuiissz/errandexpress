import os
import re

def scan_directory(root_dir, max_line_length=500):
    print(f"Scanning {root_dir} for potential broken code...")
    problems_found = False

    for dirpath, dirnames, filenames in os.walk(root_dir):
        if 'node_modules' in dirpath or 'venv' in dirpath or '.git' in dirpath or '__pycache__' in dirpath:
            continue
            
        for filename in filenames:
            if not filename.endswith(('.html', '.js', '.py', '.css')):
                continue
                
            filepath = os.path.join(dirpath, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    
                for i, line in enumerate(lines):
                    line = line.strip()
                    
                    # Check 1: Excessively long lines (possible collapse)
                    if len(line) > max_line_length:
                        # Skip minified files
                        if '.min.' in filename:
                            continue
                        
                        # Check for suspicious collapsed JS keyword patterns in long lines
                        if re.search(r';\s*(function|const|let|var|if|for|while)\s', line):
                            print(f"[POSSIBLE COLLAPSE] {filepath}:{i+1} - Length: {len(line)}")
                            print(f"   Snippet: {line[:100]}...")
                            problems_found = True
                            
                    # Check 2: Broken Django/Jinja tags
                    # Opening tag without closing on same line (basic heuristic, doesn't cover all multi-line cases)
                    if ('{{' in line and '}}' not in line) or ('{%' in line and '%}' not in line):
                        # valid multi-line tags exist, but let's flag for review if it looks weird
                        # e.g. starts with script code
                        if re.search(r'const|let|var|function', line):
                             print(f"[SUSPICIOUS TAG] {filepath}:{i+1}")
                             print(f"   Snippet: {line[:100]}...")
                             problems_found = True

                    # Check 3: Suspicious brace patterns from recent issues
                    if re.search(r'\}\s*else\s*\{\s*sendTypingStatus', line):
                         print(f"[KNOWN ERROR PATTERN] {filepath}:{i+1}")
                         problems_found = True

            except UnicodeDecodeError:
                continue
            except Exception as e:
                print(f"Error reading {filepath}: {str(e)}")

    if not problems_found:
        print("No obvious broken code patterns found.")
    else:
        print("\nScan complete. Please review flagged files.")

if __name__ == "__main__":
    scan_directory(os.getcwd())
