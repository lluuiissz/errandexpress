import re

def find_all_if_endif():
    """Find all if and endif tags with their line numbers"""
    file_path = r"c:\Users\Admin\Desktop\errandexpress - bottle neck\errandexpress\core\templates\task_detail_modern.html"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    if_tags = []
    endif_tags = []
    
    for i, line in enumerate(lines, 1):
        # Find all if tags (but not elif)
        if_matches = re.findall(r'{%\s*if\s+', line)
        for match in if_matches:
            if_tags.append((i, line.strip()[:60]))
        
        # Find all endif tags
        endif_matches = re.findall(r'{%\s*endif\s*%}', line)
        for match in endif_matches:
            endif_tags.append((i, line.strip()[:60]))
    
    print("=" * 80)
    print("ALL IF/ENDIF TAGS")
    print("=" * 80)
    print("Total IF tags:", len(if_tags))
    print("Total ENDIF tags:", len(endif_tags))
    print()
    
    # Show last 10 if tags and last 10 endif tags
    print("Last 10 IF tags:")
    print("-" * 80)
    for line_num, content in if_tags[-10:]:
        print("Line", line_num, ":", content)
    
    print()
    print("Last 10 ENDIF tags:")
    print("-" * 80)
    for line_num, content in endif_tags[-10:]:
        print("Line", line_num, ":", content)
    
    # Try to match if/endif pairs
    print()
    print("=" * 80)
    print("CHECKING FOR UNCLOSED IF BLOCKS")
    print("=" * 80)
    
    # Simple heuristic: check if there's an if without a corresponding endif nearby
    for i in range(len(if_tags) - 1):
        if_line = if_tags[i][0]
        next_if_line = if_tags[i+1][0]
        
        # Count endif between this if and next if
        endif_between = sum(1 for line_num, _ in endif_tags if if_line < line_num < next_if_line)
        
        if endif_between == 0 and (next_if_line - if_line) > 10:
            print("Suspicious: IF at line", if_line, "has no ENDIF before next IF at line", next_if_line)
            print("  Content:", if_tags[i][1])

if __name__ == "__main__":
    find_all_if_endif()
