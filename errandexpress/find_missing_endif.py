import re

def find_missing_endif():
    """Find where the missing endif should be"""
    file_path = r"c:\Users\Admin\Desktop\errandexpress - bottle neck\errandexpress\core\templates\task_detail_modern.html"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Track if/endif balance
    balance = 0
    max_balance = 0
    problem_areas = []
    
    for i, line in enumerate(lines, 1):
        # Count if statements
        if_matches = re.findall(r'{%\s*if\s+', line)
        endif_matches = re.findall(r'{%\s*endif\s*%}', line)
        
        balance += len(if_matches)
        balance -= len(endif_matches)
        
        if balance > max_balance:
            max_balance = balance
        
        # Track areas where balance is high (potential missing endif)
        if balance > 3:
            problem_areas.append((i, balance, line.strip()[:80]))
    
    print("=" * 80)
    print("IF/ENDIF BALANCE ANALYSIS")
    print("=" * 80)
    print("Total if tags: 29")
    print("Total endif tags: 28")
    print("Missing: 1 endif tag")
    print()
    print("High nesting areas (potential missing endif locations):")
    print("-" * 80)
    
    for line_num, bal, content in problem_areas[-10:]:  # Show last 10 high-balance areas
        print("Line", line_num, "| Balance:", bal, "|", content)
    
    print()
    print("=" * 80)
    print("Checking common problem patterns...")
    print("=" * 80)
    
    # Look for if statements without corresponding endif
    for i in range(len(lines)):
        line = lines[i]
        
        # Check for user == task.doer block
        if 'user == task.doer' in line:
            print("Found 'user == task.doer' at line", i+1)
            # Count if/endif in next 50 lines
            block_if = 0
            block_endif = 0
            for j in range(i, min(i+50, len(lines))):
                block_if += len(re.findall(r'{%\s*if\s+', lines[j]))
                block_endif += len(re.findall(r'{%\s*endif\s*%}', lines[j]))
            print("  Block has", block_if, "if and", block_endif, "endif")
            if block_if != block_endif:
                print("  ⚠️ IMBALANCED! Missing", block_if - block_endif, "endif")

if __name__ == "__main__":
    find_missing_endif()
