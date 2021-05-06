"""
This file includes all other minor functions
"""
import pandas as pd
import numpy as np


def ask_answer(question):
    """
    Get user inputs
    """
    print(question)
    ans = input()
    return ans


def load_catalog(filename):
    """
    Load Gear or Motor catalog
    """
    catalog = pd.read_csv(filename)
    return catalog


def fit_motor_efficiency():
    motor_catalog = load_catalog("./catalog/Motor_catalog_user_defined.csv")
    speed_torque_ratio_data = []
    efficiency_data = []
    motor_count = 0
    for index, row in motor_catalog.iterrows():
        if motor_count > 10:
            break
        speed_array = np.linspace(100, row["Vn"] * row["kn"] * 1.5, 10)
        torque_array = np.linspace(0.05, row["In"] * row["km"] * 10, 10)
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

    poly_coef = np.polyfit(speed_torque_ratio_data, efficiency_data, 3)
    model = np.poly1d(poly_coef)

    return model


def num_2dec(num):
    return "{:.2f}".format(num)


def narrow_down_catalog(key_range, key, filename, is_motor=True):
    def_cat = load_catalog(filename)
    count = 0
    for sub_range in key_range:
        if is_motor:
            sub_cat = def_cat[(def_cat[key] >= sub_range[0]-200) & (def_cat[key] <= sub_range[1])]   # to include gear inertia
        else:
            sub_cat = def_cat[(def_cat[key] >= sub_range[0]) & (def_cat[key] <= sub_range[1])]
        if count == 0:
            filtered_cat = sub_cat
        else:
            pd.concat([filtered_cat, sub_cat])
        count += 1

    return filtered_cat


