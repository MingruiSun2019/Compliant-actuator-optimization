import pandas as pd
import numpy as np
from lib.utils import *
import matplotlib.pyplot as plt

#catalog = pd.read_csv("./catalog/Gear_catalog_user_defined.csv")
#for index, row in catalog.iterrows():
#    print(row['Name'], row['ratio'], row['eff'])ear

motor_catalog = load_catalog("./catalog/Motor_catalog_default.csv")
speed_torque_ratio_data = []
efficiency_data = []
motor_count = 0
for index, row in motor_catalog.iterrows():
    if motor_count > 10:
        break
    speed_array = np.linspace(100, row["Vn"] * row["kn"] * 1.5, 50)
    torque_array = np.linspace(0.05, row["In"] * row["km"] * 2, 50)
    t_s_ratio_array = np.zeros(len(speed_array) * len(torque_array))
    current_array = np.zeros(len(t_s_ratio_array))
    joule_array = np.zeros(len(t_s_ratio_array))
    pm_array = np.zeros(len(t_s_ratio_array))
    eff_list = np.zeros(len(t_s_ratio_array))
    count = 0
    for speed in speed_array:
        for torque in torque_array:
            t_s_ratio_array[count] = speed / torque
            current_array[count] = torque / row["km"]
            joule_array[count] = current_array[count] ** 2 * row["Rw"]
            pm_array[count] = speed * torque
            eff_list[count] = pm_array[count] / (pm_array[count] + joule_array[count])
            count += 1

    speed_torque_ratio_data += list(np.log(t_s_ratio_array))
    efficiency_data += list(eff_list)
    motor_count += 1

plt.scatter(speed_torque_ratio_data, efficiency_data, c='blue', alpha=0.1)

poly_coef = np.polyfit(speed_torque_ratio_data, efficiency_data, 3)
print(poly_coef)
model = np.poly1d(poly_coef)
x = np.linspace(6, 12, 100)
fitted_y = model(x)

plt.plot(x, fitted_y, c='red', alpha=0.5)
plt.xlabel("log(speed/torque) (rpm/Nm)")
plt.ylabel("Motor efficiency")
plt.savefig("fit.png")
