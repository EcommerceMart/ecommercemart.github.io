import os
import re

posts_dir = '_posts'
all_posts = []
for file in os.listdir(posts_dir):
    if file.endswith('.md'):
        path = os.path.join(posts_dir, file)
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        all_posts.append((file, content))

posts_with_related = [p for p in all_posts if '## Related Posts' in p[1]]
posts_without = [p for p in all_posts if '## Related Posts' not in p[1]]

def extract_title(content):
    lines = content.split('\n')
    in_front = False
    for line in lines:
        if line.strip() == '---':
            if in_front:
                break
            in_front = True
            continue
        if in_front and line.startswith('title:'):
            title = line.split(':', 1)[1].strip().strip('"').strip("'")
            return title
    return None

all_titles = {}
for file, content in all_posts:
    title = extract_title(content)
    if title:
        all_titles[file] = title

stop_words = set(['is', 'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'as', 'how', 'what', 'why', 'when', 'where', 'who', 'guide', 'tips', '2025', 'review', 'legit'])

def tokenize(title):
    words = re.findall(r'\b\w+\b', title.lower())
    return [w for w in words if w not in stop_words and not w.isdigit()]

tokens_dict = {file: tokenize(title) for file, title in all_titles.items()}

updated_posts = []

for post in posts_without:
    file = post[0]
    if file not in all_titles:
        continue
    my_tokens = tokens_dict[file]
    matches = []
    for other_file, other_tokens in tokens_dict.items():
        if other_file == file:
            continue
        common = set(my_tokens) & set(other_tokens)
        if len(common) >= 2:
            matches.append(other_file)
    if not matches:
        # find popular
        matches = [f for f, t in tokens_dict.items() if 'shopify' in ' '.join(t).lower() or 'ecommerce' in ' '.join(t).lower()]
    # pick up to 5
    selected = matches[:5]
    # now, for each selected, get title and url
    links = []
    for sel_file in selected:
        sel_title = all_titles[sel_file]
        # slug from file: year-month-day-slug.md
        parts = sel_file.split('-', 3)
        year = parts[0]
        month = parts[1]
        day = parts[2]
        slug = parts[3].rsplit('.', 1)[0]
        url = f"{{{{ site.baseurl }}}}/ {year}/{month}/{day}/{slug}/"
        links.append(f"[{sel_title}]({url})")
    # now, add to the file
    content = post[1]
    # add at end
    new_content = content + '\n\n## Related Posts\n\n' + '\n'.join(links) + '\n'
    # write back
    with open(os.path.join(posts_dir, file), 'w', encoding='utf-8') as f:
        f.write(new_content)
    updated_posts.append(file)

print("Posts updated:")
for p in updated_posts:
    print(p)