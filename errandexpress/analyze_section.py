import re

def analyze_nesting():
    """Analyze the nesting structure around lines 445-535"""
    file_path = r"c:\Users\Admin\Desktop\errandexpress - bottle neck\errandexpress\core\templates\task_detail_modern.html"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Focus on lines 445-535
    start = 444  # 0-indexed
    end = 535
    
    balance = 0
    print("=" * 80)
    print("ANALYZING LINES 445-535")
    print("=" * 80)
    
    for i in range(start, min(end, len(lines))):
        line = lines[i]
        line_num = i + 1
        
        # Check for if/elif/else/endif
        if re.search(r'{%\s*if\s+', line):
            print(f"Line {line_num}: [OPEN IF] Balance: {balance} -> {balance+1}")
            print(f"  {line.strip()[:80]}")
            balance += 1
        elif re.search(r'{%\s*elif\s+', line):
            print(f"Line {line_num}: [ELIF] Balance: {balance}")
            print(f"  {line.strip()[:80]}")
        elif re.search(r'{%\s*else\s*%}', line):
            print(f"Line {line_num}: [ELSE] Balance: {balance}")
            print(f"  {line.strip()[:80]}")
        elif re.search(r'{%\s*endif\s*%}', line):
            balance -= 1
            print(f"Line {line_num}: [CLOSE ENDIF] Balance: {balance+1} -> {balance}")
            print(f"  {line.strip()[:80]}")
            if balance < 0:
                print(f"  ❌ ERROR: Balance went negative!")
                return
    
    print("\n" + "=" * 80)
    print(f"FINAL BALANCE: {balance}")
    if balance == 0:
        print("✅ Balanced within this section")
    else:
        print(f"⚠️  Imbalanced: {balance} unclosed blocks")

if __name__ == "__main__":
    analyze_nesting()
