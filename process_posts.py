import os
import yaml

posts_dir = '_posts'
posts = []

for file in os.listdir(posts_dir):
    if file.endswith('.md') or file.endswith('.markdown'):
        path = os.path.join(posts_dir, file)
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        lines = content.split('\n')
        fm = {}
        fm_end = -1
        if lines and lines[0] == '---':
            for i in range(1, len(lines)):
                if lines[i] == '---':
                    fm_end = i
                    fm_str = '\n'.join(lines[1:i])
                    try:
                        fm = yaml.safe_load(fm_str) or {}
                    except yaml.YAMLError:
                        fm = {}
                    break
        title = fm.get('title', '')
        categories = fm.get('categories', [])
        tags = fm.get('tags', [])
        if isinstance(categories, str):
            categories = [categories]
        if isinstance(tags, str):
            tags = [tags]
        categories_lower = [c.lower() for c in categories if c]
        tags_lower = [t.lower() for t in tags if t]
        
        # parse date and slug
        parts = file.split('-', 3)
        if len(parts) >= 4 and parts[3].endswith(('.md', '.markdown')):
            year = parts[0]
            month = parts[1]
            day = parts[2]
            slug = parts[3].rsplit('.', 1)[0]
        else:
            # fallback
            year = '2024'
            month = '01'
            day = '01'
            slug = file.rsplit('.', 1)[0]
        
        if not title:
            title = slug.replace('-', ' ').title()
        
        posts.append({
            'file': file,
            'path': path,
            'title': title,
            'categories': categories_lower,
            'tags': tags_lower,
            'year': year,
            'month': month,
            'day': day,
            'slug': slug,
            'content': content,
            'fm_end': fm_end
        })

# find related
for post in posts:
    related = []
    my_cats = set(post['categories'])
    my_tags = set(post['tags'])
    for other in posts:
        if other['file'] == post['file']:
            continue
        other_cats = set(other['categories'])
        other_tags = set(other['tags'])
        if my_cats & other_cats or my_tags & other_tags:
            related.append(other)
    if len(related) > 5:
        related = related[:5]
    if related and '## Related Posts' not in post['content']:
        lines = post['content'].split('\n')
        content_start = post['fm_end'] + 1 if post['fm_end'] > 0 else 0
        related_section = '\n## Related Posts\n'
        for rel in related:
            link = f'[{rel["title"]}]({{{{ site.baseurl }}}}/{{{rel["year"]}}}/{{{rel["month"]}}}/{{{rel["day"]}}}/{{{rel["slug"]}}}/)\n'
            related_section += link
        new_content = '\n'.join(lines[:content_start]) + '\n' + '\n'.join(lines[content_start:]) + related_section
        with open(post['path'], 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Added related posts to {post['file']}")