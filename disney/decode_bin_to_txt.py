import sys
import re

def clean_key(raw_key):
    # Remove any leading non-word characters (anything that isn't a letter, digit, or _)
    key = raw_key.lstrip().lstrip('"/\n\t ')
    # Sometimes keys are prefixed with weird control bytes, so extract the actual key
    match = re.search(r'([A-Za-z0-9_!]+.*_DisplayName|[A-Za-z0-9_!]+)', key)
    return match.group(0) if match else key

def parse_bin_file(filename):
    with open(filename, 'rb') as f:
        data = f.read()
    
    i = 0
    results = []
    while i < len(data):
        sep = data.find(b'\x12', i)
        if sep == -1:
            break
        raw_key = data[i:sep].decode('utf-8', errors='ignore')
        length = data[sep+1]
        value = data[sep+2:sep+2+length].decode('utf-8', errors='ignore')
        key = clean_key(raw_key)
        # Only append if key looks valid (contains at least one letter)
        if re.search(r'[A-Za-z]', key):
            results.append((key, value))
        i = sep + 2 + length
    return results

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python decode_bin_to_txt.py <file.bin>")
        sys.exit(1)
    filename = sys.argv[1]
    entries = parse_bin_file(filename)
    for k, v in entries:
        print(f'"{k}", "{v}"')