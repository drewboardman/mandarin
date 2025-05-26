import argparse
import csv
import os
import requests
import hashlib
from time import sleep
from dotenv import load_dotenv

def fetch_unsplash_image(query, api_key, size="small"):
    url = "https://api.unsplash.com/photos/random"
    params = {
        "query": query,
        "client_id": api_key,
        "orientation": "squarish"
    }
    resp = requests.get(url, params=params)
    if resp.status_code == 200:
        data = resp.json()
        img_url = data['urls'].get(size)
        return img_url
    else:
        print(f"Error fetching image for '{query}':", resp.status_code, resp.text)
        return None

def sanitize_filename(text):
    # Remove problematic characters and keep it short
    return ''.join(c for c in text if c.isalnum() or c in ('-_')).rstrip()

def main():
    parser = argparse.ArgumentParser(description="Add image column to Mandarin deck using Unsplash API.")
    parser.add_argument('--input-file', '-i', required=True, help='Input TSV file with pinyin column')
    parser.add_argument('--output-file', '-o', default='deck_with_images.txt', help='Output TSV file')
    parser.add_argument('--api-key', required=False, help='Unsplash API key (or set in secrets.env)')
    parser.add_argument('--image-dir', default='card_images', help='Directory to save images')
    parser.add_argument('--image-size', default='thumb', help='Unsplash image size (thumb, small, regular)')
    args = parser.parse_args()

    # Load .env file if present
    load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'secrets.env'))
    api_key = args.api_key or os.environ.get('UNSPLASH_API_KEY')
    if not api_key:
        raise ValueError('Unsplash API key must be provided via --api-key or in secrets.env as UNSPLASH_API_KEY')

    os.makedirs(args.image_dir, exist_ok=True)

    with open(args.input_file, 'r', encoding='utf-8') as fin, open(args.output_file, 'w', encoding='utf-8', newline='') as fout:
        reader = csv.reader(fin, delimiter='\t')
        writer = csv.writer(fout, delimiter='\t')
        for idx, row in enumerate(reader):
            if len(row) < 5:
                writer.writerow(row + [''])
                continue
            word = row[0]
            # Use a hash to avoid filename conflicts
            hash_part = hashlib.md5(word.encode('utf-8')).hexdigest()[:8]
            safe_word = sanitize_filename(word)
            img_filename = f"{safe_word}_{hash_part}.jpg"
            img_path = os.path.join(args.image_dir, img_filename)
            if not os.path.exists(img_path):
                img_url = fetch_unsplash_image(word, api_key, size=args.image_size)
                if img_url:
                    try:
                        img_data = requests.get(img_url).content
                        with open(img_path, 'wb') as img_file:
                            img_file.write(img_data)
                        sleep(0.5)  # Be nice to the API
                    except Exception as e:
                        print(f"Failed to download image for '{word}': {e}")
                        img_path = ''
                else:
                    img_path = ''
            rel_img_path = os.path.relpath(img_path, os.path.dirname(args.output_file)) if os.path.exists(img_path) else ''
            writer.writerow(row + [rel_img_path])
    print(f"Done! Output saved to {args.output_file}")

if __name__ == '__main__':
    main()
