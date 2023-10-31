import os

import pandas as pd

df_csv_append = pd.DataFrame()

# append the CSV files
for file in os.listdir():
    if file.endswith('csv'):
        df = pd.read_csv(file)
        df_csv_append = pd.concat([df_csv_append, df], ignore_index=True)


df_csv_append.to_csv('supplier_products.csv', sep='\t', encoding='utf-8')
