"""Multi-provider AI image generator (Imagen 3, Pollinations Flux, Freepik) with automatic fallback and WebP compression"""
import os
import sys
import time
import urllib.parse
import requests
from io import BytesIO
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import (
    GEMINI_API_KEY, FREEPIK_API_KEY, FREEPIK_ENDPOINT,
    IMAGE_QUALITY, IMAGE_MAX_WIDTH, IMAGE_MAX_HEIGHT, OPTIMIZE_IMAGE
)
from google import genai

client = None
if GEMINI_API_KEY:
    client = genai.Client(api_key=GEMINI_API_KEY)


def get_genai_client():
    global client
    if client is None and GEMINI_API_KEY:
        client = genai.Client(api_key=GEMINI_API_KEY)
    return client


def generate_image_featured(prompt, output_path):
    """
    Generate high-quality featured image using the best available provider with automatic fallback:
    1. Google Imagen 3 (via GEMINI_API_KEY)
    2. Pollinations.ai (Flux - 100% free, no API key required)
    3. Freepik AI (if FREEPIK_API_KEY is configured and valid)
    """
    print(f"\n🎨 Starting AI Image Generation for: {output_path}")
    print(f"📝 Prompt: {prompt[:120]}...")

    # Method 1: Try Google Imagen 3 via Gemini API
    if GEMINI_API_KEY:
        try:
            print("🚀 Trying Provider 1: Google Imagen 3...")
            ai_client = get_genai_client()
            if ai_client:
                result = ai_client.models.generate_images(
                    model='imagen-3.0-generate-002',
                    prompt=prompt,
                    config=dict(
                        number_of_images=1,
                        aspect_ratio='16:9',
                        output_mime_type='image/jpeg'
                    )
                )
                if result.generated_images:
                    image_bytes = result.generated_images[0].image.image_bytes
                    save_and_compress_image_bytes(image_bytes, output_path)
                    print("✅ Image successfully generated with Google Imagen 3!")
                    return output_path
        except Exception as e:
            print(f"ℹ️ Google Imagen 3 unavailable or failed: {e}")

    # Method 2: Try Freepik if key is provided
    if FREEPIK_API_KEY:
        try:
            print("🚀 Trying Provider 2: Freepik AI...")
            generate_image_freepik_direct(prompt, output_path)
            print("✅ Image successfully generated with Freepik AI!")
            return output_path
        except Exception as e:
            print(f"ℹ️ Freepik API failed ({e}), falling back to Pollinations Flux...")

    # Method 3: Pollinations.ai (Flux model - 100% free, no key required)
    try:
        print("🚀 Trying Provider 3: Pollinations AI (Flux - Free)...")
        generate_image_pollinations(prompt, output_path)
        print("✅ Image successfully generated with Pollinations AI (Flux)!")
        return output_path
    except Exception as e:
        print(f"❌ Pollinations AI failed: {e}")
        raise RuntimeError(f"All image generation providers failed for: {prompt[:80]}")


def generate_image_pollinations(prompt, output_path):
    """Generate image via Pollinations.ai (Flux model, completely free, no API key)"""
    clean_prompt = prompt.replace('\n', ' ').strip()
    encoded = urllib.parse.quote(clean_prompt)
    url = f"https://image.pollinations.ai/prompt/{encoded}?width=1280&height=720&nologo=true&model=flux"

    print(f"📥 Requesting image from Pollinations.ai (Flux)...")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    response = requests.get(url, headers=headers, timeout=90)
    response.raise_for_status()

    if len(response.content) < 1000:
        raise ValueError("Received invalid/empty image response from Pollinations")

    save_and_compress_image_bytes(response.content, output_path)


def generate_image_freepik_direct(prompt, output_path):
    """Generate image using Freepik AI with polling"""
    headers = {
        "x-freepik-api-key": FREEPIK_API_KEY,
        "Content-Type": "application/json"
    }

    payload = {
        "prompt": prompt,
        "num_images": 1,
        "image": {"size": "1920x1080"},
        "aspect_ratio": "widescreen_16_9"
    }

    response = requests.post(FREEPIK_ENDPOINT, headers=headers, json=payload, timeout=60)
    if response.status_code == 401:
        raise Exception("Invalid Freepik API key")
    if response.status_code == 402:
        raise Exception("Freepik API credits exhausted")
    response.raise_for_status()

    data = response.json()
    task_id = data.get("data", {}).get("task_id")
    if not task_id:
        raise Exception(f"No task_id in response: {data}")

    image_url = poll_for_freepik_image(task_id, headers)
    img_response = requests.get(image_url, timeout=60)
    img_response.raise_for_status()

    save_and_compress_image_bytes(img_response.content, output_path)


def poll_for_freepik_image(task_id, headers, max_attempts=30):
    """Poll Freepik API until image is ready"""
    for attempt in range(1, max_attempts + 1):
        time.sleep(4)
        status_url = f"https://api.freepik.com/v1/ai/text-to-image/flux-dev/{task_id}"
        status_response = requests.get(status_url, headers=headers, timeout=30)
        status_response.raise_for_status()

        status_data = status_response.json()
        status = status_data.get("data", {}).get("status")

        if status == "COMPLETED":
            generated = status_data["data"].get("generated", [])
            if isinstance(generated, list) and len(generated) > 0:
                image_url = generated[0] if isinstance(generated[0], str) else generated[0].get("url")
                if image_url:
                    return image_url
            raise Exception("No URL in completed Freepik response")
        elif status == "FAILED":
            error_msg = status_data["data"].get("error", "Unknown error")
            raise Exception(f"Freepik generation failed: {error_msg}")

    raise Exception("Freepik generation timed out")


def save_and_compress_image_bytes(image_bytes, output_path):
    """Process and compress raw image bytes to optimized WebP"""
    os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
    img = Image.open(BytesIO(image_bytes)).convert("RGB")

    original_size = len(image_bytes)
    original_width, original_height = img.size
    print(f"📊 Original: {original_width}x{original_height}, {original_size / 1024:.1f} KB")

    # Resize if needed
    if original_width > IMAGE_MAX_WIDTH or original_height > IMAGE_MAX_HEIGHT:
        img.thumbnail((IMAGE_MAX_WIDTH, IMAGE_MAX_HEIGHT), Image.Resampling.LANCZOS)
        new_width, new_height = img.size
        print(f"🔧 Resized to: {new_width}x{new_height}")

    # Save as compressed WebP
    if OPTIMIZE_IMAGE:
        img.save(output_path, "WEBP", quality=IMAGE_QUALITY, method=6, optimize=True)
    else:
        img.save(output_path, "WEBP", quality=IMAGE_QUALITY)

    compressed_size = os.path.getsize(output_path)
    savings = (1 - compressed_size / original_size) * 100 if original_size > 0 else 0
    print(f"💾 Saved WebP: {output_path} ({compressed_size / 1024:.1f} KB, saved {savings:.1f}%)")


# Backward compatibility alias
def generate_image_freepik(prompt, output_path):
    return generate_image_featured(prompt, output_path)