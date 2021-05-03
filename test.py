import pandas as pd
import numpy as np

#catalog = pd.read_csv("./catalog/Gear_catalog_user_defined.csv")
#for index, row in catalog.iterrows():
#    print(row['Name'], row['ratio'], row['eff'])

time_series = np.linspace(0, 0.0114*100, 100)
print(time_series)
print(len(time_series))
df = pd.DataFrame(time_series, columns=["Time"])
df.to_csv("./test.csv")
# TODO: torque do per kg, add body weight
