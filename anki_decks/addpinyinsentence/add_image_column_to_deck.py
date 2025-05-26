import argparse
import csv
import os
import requests
import hashlib
from time import sleep
from dotenv import load_dotenv

def fetch_pexels_image(query, api_key):
    url = "https://api.pexels.com/v1/search"
    headers = {
        "Authorization": api_key
    }
    params = {
        "query": query,
        "per_page": 1,
        "size": "small"
    }
    try:
        resp = requests.get(url, headers=headers, params=params, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            photos = data.get("photos", [])
            if photos:
                # Get the small image URL (from src["small"])
                return photos[0].get("src", {}).get("small")
        else:
            print(f"Pexels error for '{query}':", resp.status_code, resp.text)
    except Exception as e:
        print(f"Pexels exception for '{query}': {e}")
    return None

def fetch_unsplash_image(query, api_key):
    url = "https://api.unsplash.com/search/photos"
    params = {
        "query": query,
        "per_page": 1,
        "order_by": "relevant",
        "client_id": api_key,
        "content_filter": "high",
        "orientation": "squarish"
    }
    try:
        resp = requests.get(url, params=params, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            results = data.get("results", [])
            if results:
                # Get the user's small profile image from the first result
                return results[0].get("user", {}).get("profile_image", {}).get("small")
        else:
            print(f"Unsplash error for '{query}':", resp.status_code, resp.text)
    except Exception as e:
        print(f"Unsplash exception for '{query}': {e}")
    return None

def sanitize_filename(text):
    # Remove problematic characters and keep it short
    return ''.join(c for c in text if c.isalnum() or c in ('-_')).rstrip()

def main():
    parser = argparse.ArgumentParser(description="Add image column to Mandarin deck using Pexels/Unsplash API.")
    parser.add_argument('--input-file', '-i', required=True, help='Input TSV file with pinyin column')
    parser.add_argument('--output-file', '-o', default='deck_with_images.txt', help='Output TSV file')
    parser.add_argument('--image-dir', default='card_images', help='Directory to save images')
    args = parser.parse_args()

    # Load .env file from the current working directory (repo root)
    load_dotenv(dotenv_path="secrets.env")
    unsplash_api_key = os.environ.get('UNSPLASH_API_KEY')
    pexels_api_key = os.environ.get('PEXELS_API_KEY')

    if not unsplash_api_key or not pexels_api_key:
        raise ValueError('Both Unsplash and Pexels API keys must be provided in secrets.env as UNSPLASH_API_KEY and PEXELS_API_KEY')

    os.makedirs(args.image_dir, exist_ok=True)

    with open(args.input_file, 'r', encoding='utf-8') as fin, open(args.output_file, 'w', encoding='utf-8', newline='') as fout:
        reader = csv.reader(fin, delimiter='\t')
        writer = csv.writer(fout, delimiter='\t')
        for idx, row in enumerate(reader):
            if len(row) < 2:
                writer.writerow(row + [''])
                continue
            query = row[1].strip()  # English translation as your search query
            print(f"searching for image: {query}")
            hash_part = hashlib.md5(query.encode('utf-8')).hexdigest()[:8]
            safe_query = sanitize_filename(query)
            img_filename = f"{safe_query}_{hash_part}.jpg"
            img_path = os.path.join(args.image_dir, img_filename)

            img_url = None
            if not os.path.exists(img_path):
                # Try Pexels first, then Unsplash as backup
                img_url = fetch_pexels_image(query, pexels_api_key)
                if not img_url:
                    img_url = fetch_unsplash_image(query, unsplash_api_key)
                if img_url:
                    try:
                        img_data = requests.get(img_url, timeout=15).content
                        with open(img_path, 'wb') as img_file:
                            img_file.write(img_data)
                        sleep(0.5)  # Throttle to 2 requests per second
                    except Exception as e:
                        print(f"Failed to download image for '{query}': {e}")
                        img_path = ''
                else:
                    img_path = ''
            rel_img_path = os.path.abspath(img_path) if os.path.exists(img_path) else ''
            writer.writerow(row + [rel_img_path])
    print(f"Done! Output saved to {args.output_file}")

if __name__ == '__main__':
    main()