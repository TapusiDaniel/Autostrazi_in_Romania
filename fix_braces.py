
import re

file_path = 'map_creator.py'

with open(file_path, 'r') as f:
    lines = f.readlines()

# 1. Change f""" to """ at line 185 (index 184)
# We search for the line containing `ux_enhancements_html = f"""`
found_start = False
start_idx = -1
for i, line in enumerate(lines):
    if 'ux_enhancements_html = f"""' in line:
        lines[i] = line.replace('ux_enhancements_html = f"""', 'ux_enhancements_html = """')
        start_idx = i
        found_start = True
        break

if not found_start:
    print("Could not find start of string")
    exit(1)

# 2. Find end of string
# We look for `"""` and `m.get_root().html.add_child` which follows it
end_idx = -1
for i in range(start_idx + 1, len(lines)):
    if '"""' in lines[i] and 'm.get_root().html.add_child' not in lines[i]: # The closing """ is usually on its own line or with indentation
         # But wait, looking at file content, line 526 is just `    """`
         if lines[i].strip() == '"""':
             end_idx = i
             break

if end_idx == -1:
    print("Could not find end of string")
    # Fallback to hardcoded line if search fails, but let's try to be smart
    # Based on previous views, it ends around line 526
    # Let's just scan for the first """ after start_idx
    for i in range(start_idx + 1, len(lines)):
         if '"""' in lines[i]:
             end_idx = i
             break

print(f"Converting braces from line {start_idx+1} to {end_idx+1}")

# 3. Replace braces in the range
for i in range(start_idx + 1, end_idx): # Exclusive of start and end lines (the quotes)
    # We want to replace {{ -> { and }} -> }
    # But ONLY if they are double. If they are already single (which caused the error), we leave them?
    # No, if we are switching to normal string, ALL braces should be single.
    # So whether they are {{ or {, result should be {.
    
    # Logic:
    # Replace {{ with {
    # Replace }} with }
    # But wait, what if I have {{{ ? -> {{ ?
    
    # Safe approach: 
    # 1. format string style brace escaping means {{ escapes to {.
    # So we simply replace '{{' with '{' and '}}' with '}'.
    # If there was a SINGLE {, it stays {.
    # This is exactly what we want for normal string.
    
    lines[i] = lines[i].replace('{{', '{').replace('}}', '}')

with open(file_path, 'w') as f:
    f.writelines(lines)

print("Conversion complete.")
