import csv

FILENAME = "SUBTLEX-CH-WF.txt"

with open(FILENAME, encoding='gbk') as f:
    # Skip the info lines
    next(f)
    next(f)
    # Now set up the CSV reader from the header line
    reader = csv.DictReader(f, delimiter='\t')
    print("CSV Headers:", reader.fieldnames)
    for i, row in enumerate(reader):
        print(f"{row['Word']} | count: {row['WCount']} | per million: {row['W/million']}")
        if i >= 9:
            break