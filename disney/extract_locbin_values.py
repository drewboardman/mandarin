import sys
import re

def extract_values(filename):
    with open(filename, 'rb') as f:
        data = f.read()
    results = []
    i = 0
    while i < len(data):
        sep = data.find(b'\x12', i)
        if sep == -1:
            break
        # After \x12: 1 length byte, then the value
        if sep + 2 > len(data):
            break
        length = data[sep+1]
        value_bytes = data[sep+2:sep+2+length]
        try:
            value = value_bytes.decode('utf-8')
        except UnicodeDecodeError:
            i = sep + 2 + length
            continue
        # Only keep if contains any Chinese character
        if re.search(r'[\u4e00-\u9fff]', value):
            results.append(value)
        i = sep + 2 + length
    return results

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python extract_locbin_values.py <file.locbin>")
        sys.exit(1)
    values = extract_values(sys.argv[1])
    # Print as comma-separated, quoted
    print(','.join(f'"{v}"' for v in values))