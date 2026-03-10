import json
try:
    with open('notebook.ipynb', 'r', encoding='utf-8') as f:
        nb = json.load(f)
    with open('notebook_code.md', 'w', encoding='utf-8') as out:
        for i, cell in enumerate(nb['cells']):
            if cell['cell_type'] == 'code':
                out.write(f"### Cell {i}\n```python\n")
                out.write("".join(cell.get('source', [])))
                out.write("\n```\n\n")
    print("Successfully extracted notebook code.")
except Exception as e:
    print(f"Error: {e}")
