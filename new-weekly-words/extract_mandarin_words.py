input_file = "raw_notes.txt"
output_file = "known_words.txt"

with open(input_file, encoding="utf-8") as inp, open(output_file, "w", encoding="utf-8") as outp:
    for line in inp:
        line = line.strip()
        if not line or line.startswith("#"):
            continue  # Skip empty lines and metadata
        parts = line.split('\t')
        # Handle single-word lines (no tab)
        if len(parts) == 1:
            word = parts[0].strip()
            if word:
                outp.write(word + "\n")
        else:
            # Multi-field line: if first part is numeric, skip it
            if parts[0].isdigit():
                parts = parts[1:]
            if parts and parts[0]:
                word = parts[0].strip()
                if word:
                    outp.write(word + "\n")