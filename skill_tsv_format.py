with open('resources/skill.tsv', 'r', encoding='utf-8') as file:
    lines = file.readlines()

formatted_lines = []
for line in lines:
    if "\t" not in line:
        formatted_lines[-1] = formatted_lines[-1].strip() + "\\n" + line
    else:
        formatted_lines.append(line)

with open('resources/skill.tsv', 'w', encoding='utf-8') as file:
    file.writelines(formatted_lines)
