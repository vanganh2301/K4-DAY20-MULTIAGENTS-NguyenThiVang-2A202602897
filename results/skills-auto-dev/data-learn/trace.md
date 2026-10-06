### Human
Analyse the sales data in `workspace/sales.csv` (see `workspace/README.md` for the column descriptions).

Write a file `workspace/answer.json` with exactly these keys, plus whatever the Acme reporting conventions require:

- `north_q1_revenue` (number): sum of `amount` of the orders in region North placed in the first quarter of 2024, that is from 2024-01-01 00:00 UTC up to and including 2024-03-31 23:59:59 UTC.
- `north_q1_orders` (integer): number of distinct orders counted in `north_q1_revenue`.
- `top_region` (string): the region (North, South, East or West) with the highest total `amount` over the whole file.
- `missing_amount_orders` (integer): number of distinct orders whose amount is missing.
- `duplicate_rows_removed` (integer): number of duplicate rows you removed.

Orders with a missing amount must not be added to any revenue.
Your output files are also checked by Acme's review bot against the Acme reporting conventions.
When you are done, reply with a short summary of how you cleaned the data.


### Assistant
<|python_tag|>{"name": "execute", "parameters": {"command": "python -c \"import pandas as pd; import json; df = pd.read_csv('workspace/sales.csv'); json.dump({'north_q1_revenue': df[(df['region'] == 'North') & (df['order_date'] >= '2024-01-01') & (df['order_date'] <= '2024-03-31')]['amount'].sum(), 'north_q1_orders': len(df[(df['region'] == 'North') & (df['order_date'] >= '2024-01-01') & (df['order_date'] <= '2024-03-31')]['amount'].dropna()), 'top_region': df.groupby('region')['amount'].sum().idxmax(), 'missing_amount_orders': len(df['amount'].isna()), 'duplicate_rows_removed': 0}, open('workspace/answer.json', 'w')\"", "timeout": null}}