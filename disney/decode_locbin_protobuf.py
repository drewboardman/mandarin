import sys

def read_varint(data, pos):
    result = 0
    shift = 0
    while True:
        if pos >= len(data):
            print("EOF while reading varint")
            return None, pos
        b = data[pos]
        pos += 1
        result |= ((b & 0x7F) << shift)
        if not (b & 0x80):
            break
        shift += 7
    return result, pos

def parse_locbin(filename):
    with open(filename, 'rb') as f:
        data = f.read()
    pos = 0
    results = []
    while pos < len(data):
        key = value = None
        start = pos
        if data[pos] == 0x0A:  # key field
            pos += 1
            key_len, pos = read_varint(data, pos)
            if key_len is None:
                break
            key = data[pos:pos+key_len].decode('utf-8', errors='replace')
            pos += key_len
            if pos < len(data) and data[pos] == 0x12:  # value field
                pos += 1
                val_len, pos = read_varint(data, pos)
                if val_len is None:
                    break
                value = data[pos:pos+val_len].decode('utf-8', errors='replace')
                pos += val_len
                print(f'Found: "{key}", "{value}"')
                results.append((key, value))
            else:
                print(f'Key without value at offset {start}: "{key}"')
        else:
            # Print what byte was skipped
            print(f'Skipping byte at {pos}: {data[pos]:02X}')
            pos += 1
    return results

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python debug_decode_locbin.py <file.locbin>")
        sys.exit(1)
    filename = sys.argv[1]
    entries = parse_locbin(filename)
    for k, v in entries:
        print(f'"{k}", "{v}"')