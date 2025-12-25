import os
import re

posts_dir = '_posts'
updated_count = 0
example_change = None

for filename in os.listdir(posts_dir):
    if not filename.endswith('.md'):
        continue
    filepath = os.path.join(posts_dir, filename)
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    # Find the Related Posts section
    match = re.search(r'(## Related Posts\n.*?)(?=##|\Z)', content, re.DOTALL)
    if match:
        section = match.group(1)
        # Pattern to match {{ site.baseurl }}/{year}/{month}/{day}/{slug}/
        pattern = r'\{\{ site\.baseurl \}\}/\{[^}]+\}/\{[^}]+\}/\{[^}]+\}/(\{[^}]+\}/)'
        new_section = re.sub(pattern, r'{{ site.baseurl }}/\1', section)
        if new_section != section:
            if example_change is None:
                # Find the first change
                old_lines = section.split('\n')
                new_lines = new_section.split('\n')
                for old_line, new_line in zip(old_lines, new_lines):
                    if old_line != new_line and '{{ site.baseurl }}' in old_line:
                        example_change = f"Old: {old_line}\nNew: {new_line}"
                        break
            # Replace in content
            new_content = content.replace(section, new_section)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            updated_count += 1
            print(f'Updated {filename}')

print(f'Total posts updated: {updated_count}')
if example_change:
    print(f'Example change:\n{example_change}')