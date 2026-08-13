"""Main script to generate eCommerce blog posts automatically from trending topics or keywords"""
import os
import sys
import time
import datetime

# Ensure scripts dir is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import all modules
from config import *
from keywords_handler import get_keyword_row, parse_keyword_row, remove_keyword_from_file, get_keywords_count
from google_news_fetcher import GoogleNewsFetcher
from article_generator import generate_article, generate_image_prompt
from image_generator import generate_image_freepik
from google_indexing import submit_to_google_indexing, check_indexing_status
from google_sheets_logger import log_to_google_sheets
from webpushr_notifier import send_blog_post_notification
from insert_ads import insert_ads_into_content


def main():
    print("=" * 60)
    print("🚀 Starting EcommerceMart AI Blog Generator")
    print("=" * 60)

    # Verify environment variables
    if not GEMINI_API_KEY:
        print("❌ GEMINI_API_KEY not found in environment")
        return
    print("✅ GEMINI_API_KEY found")

    if not FREEPIK_API_KEY:
        print("❌ FREEPIK_API_KEY not found in environment")
        return
    print("✅ FREEPIK_API_KEY found")

    # Check available manual keywords
    manual_keywords_count = get_keywords_count()
    print(f"\n📊 Posts to generate this run: {POSTS_PER_RUN}")
    print(f"📋 Manual keywords in keywords.txt: {manual_keywords_count}")

    # Initialize Google News trending fetcher & existing posts analyzer
    news_fetcher = GoogleNewsFetcher()

    posts_generated = 0

    for post_num in range(1, POSTS_PER_RUN + 1):
        print(f"\n{'=' * 60}")
        print(f"📝 Processing Post {post_num}/{POSTS_PER_RUN}")
        print("=" * 60)

        keyword_data = None
        source_is_manual_file = False

        # Priority 1: Check if manual keywords exist in keywords.txt
        if manual_keywords_count > 0:
            row = get_keyword_row()
            if row:
                parsed = parse_keyword_row(row)
                if parsed:
                    keyword_data = parsed
                    source_is_manual_file = True
                    print(f"📋 Using keyword from keywords.txt: {keyword_data['title'][:60]}...")
                else:
                    print("⚠️ Invalid keyword format in keywords.txt, removing...")
                    remove_keyword_from_file()
                    manual_keywords_count -= 1

        # Priority 2: Fetch trending topic from Google News
        if not keyword_data:
            print("🔥 Discovering trending eCommerce topic from Google News...")
            keyword_data = news_fetcher.get_trending_topic_for_blog()

        if not keyword_data:
            print("❌ Failed to obtain topic for generation.")
            break

        title = keyword_data['title']
        focus_kw = keyword_data['focus_kw']
        permalink = keyword_data['permalink']
        semantic_kw = keyword_data.get('semantic_kw', '')
        affiliate_links = keyword_data.get('affiliate_links', '')
        hook_kw = keyword_data.get('hook_kw', '')
        search_kw = keyword_data.get('search_kw', '')
        tags = keyword_data.get('tags', '')
        source_link = keyword_data.get('source_link', '')

        print(f"\n🎯 Selected Topic: {title}")
        print(f"   Focus Keyword: {focus_kw}")
        print(f"   Permalink: {permalink}")
        if source_link:
            print(f"   Source: {source_link}")

        # Setup file paths
        today = datetime.date.today().isoformat()
        post_path = f"{POSTS_DIR}/{today}-{permalink}.md"
        image_file = f"{IMAGES_DIR}/featured_{permalink}.webp"

        # Check if post already exists on disk
        if os.path.exists(post_path):
            print(f"\n⚠️ Post already exists at {post_path}, skipping...")
            if source_is_manual_file:
                remove_keyword_from_file()
                manual_keywords_count -= 1
            continue

        try:
            # Step 1: Generate article
            print(f"\n{'=' * 60}")
            print("Step 1: Generating SEO Article with Gemini AI")
            print("=" * 60)
            article = generate_article(
                title=title,
                focus_kw=focus_kw,
                permalink=permalink,
                semantic_kw=semantic_kw,
                affiliate_links=affiliate_links,
                hook_kw=hook_kw,
                search_kw=search_kw,
                tags=tags
            )
            print(f"✅ Article generated successfully ({len(article)} chars)")

            # Step 2: Generate Freepik image prompt
            print(f"\n{'=' * 60}")
            print("Step 2: Creating Photorealistic Featured Image Prompt")
            print("=" * 60)
            image_prompt = generate_image_prompt(title, focus_kw)
            print(f"📝 Prompt: {image_prompt[:120]}...")

            # Step 3: Generate and compress featured image via Freepik
            print(f"\n{'=' * 60}")
            print("Step 3: Generating Image with Freepik AI & Compressing to WebP")
            print("=" * 60)
            generate_image_freepik(image_prompt, image_file)
            print(f"✅ Featured image created: {image_file}")

            # Step 4: Insert AdSense in-article ads and save post
            print(f"\n{'=' * 60}")
            print("Step 4: Inserting Ads & Saving Markdown Post")
            print("=" * 60)
            final_article = insert_ads_into_content(article)

            with open(post_path, "w", encoding="utf-8") as f:
                f.write(final_article)
            print(f"✅ Post saved: {post_path}")

            post_url = f"{SITE_DOMAIN}/{permalink}"

            print(f"\n{'=' * 60}")
            print(f"🎉 SUCCESS: Post {post_num} Created!")
            print("=" * 60)
            print(f"📰 Title: {title}")
            print(f"🌐 URL: {post_url}")

            posts_generated += 1

            # Remove manual keyword from file if source was keywords.txt
            if source_is_manual_file:
                remove_keyword_from_file()
                manual_keywords_count -= 1

            # Step 5: Post-publish integrations (Indexing, Push, Sheets)
            if post_num == POSTS_PER_RUN or post_num == posts_generated:
                # Webpushr Notification
                try:
                    send_blog_post_notification(title, permalink, focus_kw)
                except Exception as e:
                    print(f"ℹ️ Webpushr notification skipped/failed: {e}")

                # Google Indexing Submission
                indexing_status = "Not Attempted"
                try:
                    if GOOGLE_SERVICE_ACCOUNT_JSON:
                        success = submit_to_google_indexing(post_url)
                        indexing_status = "Success" if success else "Failed"
                except Exception as e:
                    indexing_status = f"Failed - {str(e)[:50]}"
                    print(f"ℹ️ Google Indexing API skipped/failed: {e}")

                # Google Sheets Logger
                try:
                    if GOOGLE_SERVICE_ACCOUNT_JSON and GOOGLE_SPREADSHEET_ID:
                        log_to_google_sheets(
                            title, focus_kw, permalink,
                            image_file, final_article, indexing_status
                        )
                except Exception as e:
                    print(f"ℹ️ Sheets logger skipped/failed: {e}")

        except Exception as e:
            print(f"\n{'=' * 60}")
            print(f"❌ Error during post generation: {e}")
            print("=" * 60)
            import traceback
            traceback.print_exc()
            continue

    print(f"\n{'=' * 60}")
    print("🏁 WORKFLOW COMPLETE")
    print("=" * 60)
    print(f"✅ Total Posts Generated: {posts_generated}")


if __name__ == "__main__":
    main()