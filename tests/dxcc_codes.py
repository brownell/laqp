import csv
from pprint import pprint

data = [None] * 750

foo = []

with open('tests/DXCC_entities.csv', 'r') as f:
    reader = csv.reader(f)
    for row in reader:
        # print(f"{row[0]}: {row[1].split('  ')[0]}\n")
        data[int(row[0])] = row[1].split('  ')[0]
#         number = int(row[0])    # cast first column to int
#         label  = row[1].strip() # second column is already a string
#         foo.append((number, label))

for i in range(0,100):
    pprint(f"{i}: {data[i]}")
# pprint(f"FOO: {foo}")