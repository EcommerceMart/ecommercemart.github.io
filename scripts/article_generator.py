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


def generate_stock_photo_keywords(title, focus_kw=""):
    """Generate clean, highly relevant stock photo search queries for Pexels and Unsplash"""
    prompt = f"""
Given this eCommerce article title: "{title}" and focus keyword: "{focus_kw}"
Generate 3 distinct, clean search queries (1-3 words each) suitable for finding authentic, relevant commercial stock photos on Pexels or Unsplash.

Examples of good queries:
- For "Amazon Review Variation Split": "product packaging, retail display, shopping cart"
- For "eCommerce CRO Strategies": "customer shopping, retail store, mobile checkout"
- For "Order Management Software": "warehouse logistics, delivery boxes, automated shipping"
- For "DTC Brand Marketing": "product unboxing, boutique retail, beauty cosmetics"

Return ONLY a comma-separated list of 3 queries. No quotes, no markdown, no explanations.
"""
    try:
        print("🔍 Generating stock photo search queries...")
        ai_client = get_genai_client()
        response = ai_client.models.generate_content(
            model=TEXT_MODEL,
            contents=prompt
        )
        queries = [q.strip().strip('"').strip("'") for q in response.text.strip().split(',') if q.strip()]
        return queries if queries else [focus_kw, "ecommerce shopping", "retail"]
    except Exception as e:
        print(f"⚠️ Stock query generation fallback: {e}")
        return [focus_kw, "ecommerce", "online retail"]


def generate_image_prompt(title, focus_kw=""):
    """Generate a highly relevant, visually distinct, strictly physical image prompt tailored to the article"""
    prompt = f"""
You are an expert art director creating an ultra-realistic, custom featured image prompt for an eCommerce publication.

Article Title: "{title}"
Focus Keyword: "{focus_kw}"

CRITICAL RULES:
1. MUST BE A CONCRETE PHYSICAL REAL-WORLD SCENE:
   - Depict tangible, physical objects: actual products, boutique shelves, cardboard delivery packages, smartphone in hand with a clean shop app, organized warehouse aisles, modern unboxing setups, studio product photography pedestals.
   - STRICTLY FORBIDDEN: NO abstract metaphors, NO glowing energy hands, NO floating magical symbols, NO fantasy vortexes, NO sci-fi holograms.
   - AVOID CLICHÉS: Do NOT generate a standard laptop showing wavy abstract blue graphs on an empty desk.
2. HIGH RELEVANCE: The scene must directly match what the article is about (e.g. products on a counter, retail store, package shipping, unboxing experience, customer shopping).
3. ABSOLUTE ZERO TEXT: NO text, NO letters, NO words, NO numbers, NO watermarks, NO brand logos anywhere.
4. STYLE: Commercial editorial photography, 8K resolution, realistic natural & studio lighting, shallow depth of field, 16:9 widescreen composition.

Output ONLY the final image generation prompt (1-2 vivid sentences describing the tangible objects, setting, lighting, and camera perspective).
"""

    print("🎨 Generating contextual AI image prompt...")
    ai_client = get_genai_client()
    response = ai_client.models.generate_content(
        model=TEXT_MODEL,
        contents=prompt
    )
    return response.text.strip()
