with open('see_think_act_agent.py', 'r') as f:
    lines = f.readlines()

# Fix indentation for _finish_report method (lines 919-926, 0-indexed: 918-925)
# These should be indented by 4 spaces
for i in range(918, 926):
    if lines[i].strip():  # Only indent non-empty lines
        lines[i] = '    ' + lines[i]

with open('see_think_act_agent.py', 'w') as f:
    f.writelines(lines)
print('Fixed _finish_report indentation')