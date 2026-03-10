import json
with open('notebook.ipynb', 'r', encoding='utf-8') as f:
    nb = json.load(f)
for i, cell in enumerate(nb['cells']):
    if cell['cell_type'] == 'code':
        print(f"--- Cell {i} ---")
        for line in cell.get('source', []):
            print(line.rstrip('\n'))
import pandas as pd
df = pd.read_csv('customer_churn_data.csv')
print("\n--- CSV Info ---")
print(df.info())
print("\n--- CSV Head ---")
print(df.head())
