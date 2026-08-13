import os
import sys
import re

# Ensure scripts dir is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from google import genai
from config import TEXT_MODEL, GEMINI_API_KEY

client = None
if GEMINI_API_KEY:
    client = genai.Client(api_key=GEMINI_API_KEY)


def get_genai_client():
    global client
    if client is None:
        if not GEMINI_API_KEY:
            raise ValueError("❌ GEMINI_API_KEY environment variable is not set")
        client = genai.Client(api_key=GEMINI_API_KEY)
    return client


def generate_article(title, focus_kw, permalink, semantic_kw, affiliate_links="", hook_kw="", search_kw="", tags=""):
    """Generate SEO-optimized blog article"""
    prompt = f"""
Write an in-depth, authoritative, SEO-optimised blog post on the title "{title}".
Focus Keyword: {focus_kw}
LSI / Semantic Keywords: {semantic_kw}
Search Intent Queries: {search_kw}

Rules & Guidelines:
- Clear, engaging English that is easily readable and actionable for online sellers and store owners.
- Don't write more than 3 sentences per paragraph; change paragraph after 3 sentences.
- Hook: {hook_kw or "Discover essential strategies and actionable steps to grow your online store."}
- If the article is related to ecommerce metrics, calculations, ROI, or pricing, create an interactive HTML/CSS/JS calculator widget embedded directly in the content.
- Use "you" to address the reader directly.
- Include links/references to reputable platforms or resources (e.g., Shopify, Amazon, Google Analytics) where relevant.
- Do NOT use H1 in the markdown body. Use H2, H3, H4 headings with a clean logical structure.
- Use bullet points, comparison tables, step-by-step frameworks, best practices, and data callouts.
- Write a comprehensive article of more than 2,000 words.
- Include a dedicated "Frequently Asked Questions (FAQs)" section at the end.
- Format cleanly in Jekyll Markdown.
- Naturally weave in the focus keyword and semantic keywords.
- Do NOT output any front matter, YAML, or metadata blocks in your response.
"""

    print("🤖 Generating comprehensive article with Gemini...")
    ai_client = get_genai_client()
    response = ai_client.models.generate_content(
        model=TEXT_MODEL,
        contents=prompt
    )

    # Remove any front matter that AI might have added
    content = remove_front_matter(response.text)

    # Add custom front matter
    article = create_custom_front_matter(title, focus_kw, permalink, tags=tags) + "\n\n" + content

    return article


def remove_front_matter(content):
    """Remove any existing front matter from AI-generated content"""
    # Remove front matter between --- delimiters
    content = re.sub(r'^---\s*\n.*?\n---\s*\n', '', content, flags=re.DOTALL)

    lines = content.split('\n')
    clean_lines = []
    skip_yaml = True

    for line in lines:
        if line.strip().startswith('#') or (line.strip() and ':' not in line):
            skip_yaml = False

        if not skip_yaml:
            clean_lines.append(line)
        elif skip_yaml and line.strip() and ':' not in line:
            skip_yaml = False
            clean_lines.append(line)

    return '\n'.join(clean_lines).strip()


def create_custom_front_matter(title, focus_kw, permalink, tags=""):
    """Create properly formatted Jekyll front matter"""
    escaped_title = title.replace('"', '\\"')

    # Generate meta description
    description = generate_description(title, focus_kw)

    # Format tags
    if tags:
        if isinstance(tags, str):
            tag_list = [t.strip().strip('"').strip("'") for t in tags.split(',') if t.strip()]
        else:
            tag_list = [str(t).strip() for t in tags if str(t).strip()]
    else:
        tag_list = [focus_kw.title(), "Ecommerce", "Online Business", "Retail Strategy"]

    # Ensure uniqueness while preserving order
    seen = set()
    unique_tags = []
    for t in tag_list:
        if t.lower() not in seen:
            seen.add(t.lower())
            unique_tags.append(t)

    formatted_tags = ", ".join(f'"{t}"' for t in unique_tags[:6])

    front_matter = f"""---
title: "{escaped_title}"
description: "{description}"
author_profile: true
read_time: true
comments: true
share: true
related: true
toc: true 
toc_sticky: true 
toc_icon: "list-ul"
tags: [{formatted_tags}]
featured: false
image: '/assets/images/featured_{permalink}.webp'
---"""

    return front_matter


def generate_description(title, focus_kw):
    """Generate SEO-optimized meta description (150-160 characters)"""
    prompt = f"""
Generate a compelling meta description for this blog post.

Title: {title}
Focus Keyword: {focus_kw}

Requirements:
- EXACTLY 150-160 characters (this is critical)
- Include the focus keyword naturally
- Action-oriented and engaging for ecommerce sellers
- No quotes or special characters
- Complete sentence

Return ONLY the description text, nothing else.
"""

    print("📝 Generating meta description...")
    ai_client = get_genai_client()
    response = ai_client.models.generate_content(
        model=TEXT_MODEL,
        contents=prompt
    )

    description = response.text.strip().replace('"', '').replace("'", "")

    if len(description) > 160:
        description = description[:157].rsplit(' ', 1)[0] + "..."

    print(f"✅ Description generated: {description} ({len(description)} chars)")
    return description


def generate_image_prompt(title, focus_kw=""):
    """Generate image prompt for Freepik AI"""
    prompt = f"""
Create a detailed, photorealistic featured image prompt for an eCommerce business article:
Title: {title}
Focus Keyword: {focus_kw}

Requirements:
- Photorealistic, professional commercial photography, 4K quality
- Modern eCommerce / digital retail theme (e.g. sleek laptop with store dashboard, modern fulfillment center, stylish product packaging, retail store strategy, clean aesthetic)
- Absolutely NO text, words, labels, letters, or logos in the image
- 16:9 widescreen composition suitable as a blog header
- Vibrant, modern studio lighting and balanced colors

Return ONLY the image prompt text, nothing else.
"""

    print("🎨 Generating Freepik image prompt...")
    ai_client = get_genai_client()
    response = ai_client.models.generate_content(
        model=TEXT_MODEL,
        contents=prompt
    )
    return response.text.strip()
