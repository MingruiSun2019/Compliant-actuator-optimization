import pandas as pd

catalog = pd.read_csv("./catalog/Gear_catalog_user_defined.csv")
for index, row in catalog.iterrows():
    print(row['Name'], row['ratio'], row['eff'])
