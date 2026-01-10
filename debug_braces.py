
with open('map_creator.py', 'r') as f:
    lines = f.readlines()

start_line = 185
end_line = 526

print(f"Checking lines {start_line} to {end_line}")

for i, line in enumerate(lines[start_line:end_line], start=start_line):
    # Remove {{ and }} to see if any { or } remain
    clean_line = line.replace('{{', '').replace('}}', '')
    if '{' in clean_line or '}' in clean_line:
        print(f"Line {i+1}: {line.strip()}")
        print(f"   -> Suspicious char found in: {clean_line.strip()}")
