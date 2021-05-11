import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from scipy.optimize import curve_fit
from lib.utils import *
from lib.parameter_loader import Params
from lib.polyfit import Polyfitor
from lib.human_data_processing import HumanData
from models.actuator.sea_type1 import SeaType1
from models.energy.model_4qci import Optimize4QCI
from models.energy.model_fmm import OptimizeFMM
from dashboard.dash_lib import generate_app_layout, get_dash_plots, My_settings


Q1_dict = {"y": "default", "n": "user_defined"}
Default_motor_catalog = "catalog/Motor_catalog_default.csv"
Default_gear_catalog_hd = "catalog/Gear_catalog_default_hd.csv"
Default_gear_catalog_pg = "catalog/Gear_catalog_default_pg.csv"
Default_gear_catalog_sg = "catalog/Gear_catalog_default_sg.csv"
Ud_motor_catalog = "catalog/Motor_catalog_user_defined.csv"
Ud_gear_catalog = "catalog/Gear_catalog_user_defined.csv"

#catalog = pd.read_csv("./catalog/Gear_catalog_user_defined.csv")
#for index, row in catalog.iterrows():
#    print(row['Name'], row['ratio'], row['eff'])ear


def sigmoid(x, L, x0, k, b):
    y = L / (1 + np.exp(-k * (x - x0))) + b
    return (y)

def sigmoid2(x, k):
    y = 1 / (1 + k * np.exp(-x))
    return (y)


def motor_eff_fit_demo():
    motor_catalog = load_catalog(Ud_motor_catalog)
    speed_torque_ratio_data = []
    efficiency_data = []
    motor_count = 0
    for index, row in motor_catalog.iterrows():
        if motor_count > 10:
            break
        #speed_array = np.linspace(1, row["Vn"] * row["kn"] * 1, 100)
        #torque_array = np.linspace(0.01, row["In"] * row["km"] * 6, 100)
        speed_array = np.random.uniform(low=1, high=row["Vn"] * row["kn"] * 1, size=(100,))
        torque_array = np.random.uniform(low=0.01, high=row["In"] * row["km"] * 6, size=(100,))
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

    plt.scatter(speed_torque_ratio_data, efficiency_data, c='blue', alpha=0.1, s=4, label="motor data")

    poly_coef = np.polyfit(speed_torque_ratio_data, efficiency_data, 3)
    print(poly_coef)
    model = np.poly1d(poly_coef)
    x = np.linspace(1, 13, 100)
    fitted_y = model(x)

    p0 = [max(efficiency_data), np.median(speed_torque_ratio_data), 1, min(efficiency_data)]  # this is an mandatory initial guess
    p02 = [max(efficiency_data)]

    popt, pcov = curve_fit(sigmoid2, speed_torque_ratio_data, efficiency_data, p02, method='dogbox')

    #plt.plot(x, fitted_y, c='green', alpha=1, linewidth=3, label='polynomial')
    x = np.linspace(1, 13, 100)
    plt.plot(x, sigmoid2(np.array(x), *popt), c='red', alpha=1, linewidth=3, label='sigmoid')
    #plt.plot(x, np.ones(len(x)) * 0.95, c='g', alpha=0.6, linewidth=2, label='const 0.8')
    #plt.plot(x, np.ones(len(x)) * 0.9, c='y', alpha=0.6, linewidth=2, label='const 0.7')
    #plt.plot(x, np.ones(len(x)) * 0.8, c='c', alpha=0.6, linewidth=2, label='const 0.6')
    #plt.plot(x, np.ones(len(x)) * 0.7, c='m', alpha=0.6, linewidth=2, label='const 0.6')

    plt.legend()
    plt.xlabel("log(speed/torque) (rpm/Nm)")
    plt.ylabel("Motor efficiency")
    #plt.savefig("fit.png")
    plt.show()

    true_y = np.array(efficiency_data)
    eval_x = np.array(speed_torque_ratio_data)
    eval_sig_y = sigmoid2(eval_x, *popt)
    sig_rmse = np.sqrt(np.mean((eval_sig_y - true_y) ** 2))

    cosnt_eff1 = 0.95
    eval_const_y1 = np.ones(len(eval_x)) * cosnt_eff1
    const_rmse1 = np.sqrt(np.mean((eval_const_y1 - true_y) ** 2))
    cosnt_eff2 = 0.9
    eval_const_y2 = np.ones(len(eval_x)) * cosnt_eff2
    const_rmse2 = np.sqrt(np.mean((eval_const_y2 - true_y) ** 2))
    cosnt_eff3 = 0.8
    eval_const_y3 = np.ones(len(eval_x)) * cosnt_eff3
    const_rmse3 = np.sqrt(np.mean((eval_const_y3 - true_y) ** 2))
    cosnt_eff4 = 0.7
    eval_const_y4 = np.ones(len(eval_x)) * cosnt_eff4
    const_rmse4 = np.sqrt(np.mean((eval_const_y4 - true_y) ** 2))

    print("sigmoid RMSE: ", sig_rmse)
    print("const RMSE1: ", const_rmse1)
    print("const RMSE2: ", const_rmse2)
    print("const RMSE3: ", const_rmse3)
    print("const RMSE4: ", const_rmse4)



def gai_csv():
    gear_pg = pd.read_csv("catalog/Gear_catalog_default_pg.csv")
    gear_pg["Name"] = gear_pg["Name"] + "-" + gear_pg["ratio"].astype(str)
    gear_pg["Name"] = gear_pg["Name"].apply(lambda x:x if x[-2:] != ".0" else x[:-2])
    gear_pg["eff"] = gear_pg["eff"].apply(lambda x: x/100)
    gear_pg.to_csv("Gear_catalog_default_pg_new.csv")

    gear_sg = pd.read_csv("catalog/Gear_catalog_default_sg.csv")
    gear_sg["Name"] = gear_sg["Name"] + "-" + gear_sg["ratio"].astype(str)
    gear_sg["Name"] = gear_sg["Name"].apply(lambda x: x if x[-2:] != ".0" else x[:-2])
    gear_sg["eff"] = gear_sg["eff"].apply(lambda x: x / 100)
    gear_sg.to_csv("Gear_catalog_default_sg_new.csv")


def fit_test():
    x = np.linspace(1,100000, 1000)
    k = 100
    y = x / (x + k)
    plt.plot(x, y)
    plt.show()


def result2():
    params = Params("user_defined")
    human_data = HumanData(params)
    human_data.assign_weights()
    des_torque = human_data.torque_data[0]["Data"]
    des_angle = human_data.angle_data[0]["Data"]
    time_series = human_data.angle_data[0]["Time"]
    time_step = time_series[1] - time_series[0]

    # Fit motor efficiency based on default motor database
    popt = fit_motor_efficiency(Default_motor_catalog)

    # Initialize actuator and polyfitor
    print("Initialize actuator and polyfitor")
    polyfitor = Polyfitor()
    actuator = SeaType1(params=params, polyfitor=polyfitor, motor_eff_model=popt)

    motor_data_set = load_catalog(Ud_motor_catalog)
    gear_data_set = load_catalog(Ud_gear_catalog)
    stiffness_set = [100, 200, 300, 400]

    for sitf_i, stiffness in enumerate(stiffness_set):
        ratio_list = np.zeros(len(gear_data_set))
        inertia_list = np.zeros(len(motor_data_set))
        energy_array_fmm = np.zeros((len(gear_data_set) * len(motor_data_set), 3))
        energy_array_4qcei_new = np.zeros((len(gear_data_set) * len(motor_data_set), 3))
        energy_array_4qcei_old = np.zeros((len(gear_data_set) * len(motor_data_set), 3))
        count = 0
        for gear_i, gear in gear_data_set.sort_values(by=['ratio']).iterrows():
            for motor_i, motor in motor_data_set.sort_values(by=['Jr']).iterrows():
                ratio = gear["ratio"]
                inertia = motor["Jr"] + gear["inertia"]
                # fmm
                """
                torque_constant = motor['km']
                windingR = motor['Rw']
                motor_angle, motor_speed, motor_torque = actuator.backward_calculation_fmm(stiffness, gear, motor, des_torque, des_angle, time_series)

                input_current = motor_torque / torque_constant
                electrical_power = np.array(len(motor_speed))
                for i in range(len(motor_speed)):
                    if motor_speed[i] * des_torque[i] >= 0:
                        electrical_power = motor_speed / 60 * 2 * np.pi * motor_torque + windingR * input_current ** 2
                    else:
                        electrical_power = motor_speed / 60 * 2 * np.pi * motor_torque - windingR * input_current ** 2

                electrical_power = np.clip(electrical_power, a_min=0, a_max=None)  # no-rechargable bettery
                electrical_energy = np.sum(electrical_power) * time_step
                energy_array_fmm[count, :] = np.array([ratio, inertia, electrical_energy])
                """

                # fmm2
                torque_constant = motor['km']
                speed_constant = motor['kn']
                windingR = motor['Rw']
                temp_k = 30000 / np.pi * windingR / ((torque_constant * 1000) ** 2)  # motor gradient
                motor_angle, motor_speed, motor_torque = actuator.backward_calculation_fmm(stiffness, gear, motor, des_torque, des_angle, time_series)
                input_voltage, input_current = actuator.get_motor_inputs(motor_torque, motor_speed, motor)
                input_current = motor_torque / torque_constant
                input_voltage = (motor_speed + temp_k * motor_torque * 1000) / speed_constant
                electrical_power = input_voltage * input_current  # speed (rpm) to (rad/s)
                # electrical_power = motor_speed / 60 * 2 * np.pi * motor_torque + windingR * input_current ** 2
                electrical_power = np.clip(electrical_power, a_min=0, a_max=None)  # no-rechargable bettery
                electrical_energy = np.sum(electrical_power) * time_step
                energy_array_fmm[count, :] = np.array([ratio, inertia, electrical_energy])

                # 4qcei-original
                motor_angle, motor_speed, motor_torque, actual_motor_eff = actuator.backward_calculation_4qci(stiffness,
                                                                                                              ratio,
                                                                                                              inertia,
                                                                                                              des_torque,
                                                                                                              des_angle,
                                                                                                              time_series)
                mechanical_power = motor_speed / 60 * 2 * np.pi * motor_torque  # speed (rpm) to (rad/s)
                const_eff = 0.9
                new_mot_eff = np.zeros(len(actual_motor_eff))
                for i in range(len(actual_motor_eff)):
                    if actual_motor_eff[i] > 1:
                        new_mot_eff[i] = const_eff
                    else:
                        new_mot_eff[i] = 1 / const_eff
                electrical_power = mechanical_power / new_mot_eff
                electrical_power = np.clip(electrical_power, a_min=0, a_max=None)  # no-rechargable bettery
                electrical_energy = np.sum(electrical_power) * time_step  # depend on direction of power flow
                # energy_array_4qcei[gear_i, motor_i] = electrical_energy
                energy_array_4qcei_old[count, :] = np.array([ratio, inertia, electrical_energy])


                # 4qcei-improved
                motor_angle, motor_speed, motor_torque, actual_motor_eff = actuator.backward_calculation_4qci(stiffness, ratio, inertia, des_torque, des_angle, time_series)
                mechanical_power = motor_speed / 60 * 2 * np.pi * motor_torque  # speed (rpm) to (rad/s)

                electrical_power = mechanical_power / actual_motor_eff
                electrical_power = np.clip(electrical_power, a_min=0, a_max=None)  # no-rechargable bettery
                electrical_energy = np.sum(electrical_power) * time_step  # depend on direction of power flow
                # energy_array_4qcei[gear_i, motor_i] = electrical_energy
                energy_array_4qcei_new[count, :] = np.array([ratio, inertia, electrical_energy])
                count += 1

        temp = energy_array_fmm[:, 2].argsort()
        ranks_fmm = np.empty_like(temp)
        ranks_fmm[temp] = np.arange(len(energy_array_fmm))
        # print(ranks_fmm)
        print("fmm best", energy_array_fmm[energy_array_fmm[:, 2].argsort()][0, :])

        temp = energy_array_4qcei_new[:, 2].argsort()
        ranks_4qcei_new = np.empty_like(temp)
        ranks_4qcei_new[temp] = np.arange(len(energy_array_4qcei_new))
        # print(ranks_4qcei)
        print("4qcei-new best", energy_array_4qcei_new[energy_array_4qcei_new[:, 2].argsort()][0, :])

        temp = energy_array_4qcei_old[:, 2].argsort()
        ranks_4qcei_old = np.empty_like(temp)
        ranks_4qcei_old[temp] = np.arange(len(energy_array_4qcei_old))
        # print(ranks_4qcei)
        print("4qcei-new best", energy_array_4qcei_old[energy_array_4qcei_old[:, 2].argsort()][0, :])

        rmse_new = np.sqrt(np.mean((ranks_fmm - ranks_4qcei_new) ** 2))
        manhattan_new = np.sum(np.abs(ranks_fmm - ranks_4qcei_new))
        print("manhattan_new", manhattan_new)
        rmse_old = np.sqrt(np.mean((ranks_fmm - ranks_4qcei_old) ** 2))
        manhattan_old = np.sum(np.abs(ranks_fmm - ranks_4qcei_old))
        print("manhattan_old", manhattan_old)

        fig = plt.figure()
        ax = fig.add_subplot(projection='3d')

        ax.scatter(energy_array_fmm[:, 0], energy_array_fmm[:, 1], energy_array_fmm[:, 2], label="fmm")
        ax.scatter(energy_array_4qcei_new[:, 0], energy_array_4qcei_new[:, 1], energy_array_4qcei_new[:, 2], label="4qcei-improved")
        ax.scatter(energy_array_4qcei_old[:, 0], energy_array_4qcei_old[:, 1], energy_array_4qcei_old[:, 2], label="4qcei-original")
        ax.set_ylabel("drive train inertia (gcm^2)")
        ax.set_xlabel("transmission ratio")
        ax.set_zlabel("Energy consumption (J)")
        ax.legend()
        plt.tight_layout()
        plt.savefig("surface_{}.png".format(stiffness))
        plt.show()


def cross_entropy(predictions, targets, epsilon=1e-12):
    """
    Computes cross entropy between targets (encoded as one-hot vectors)
    and predictions.
    Input: predictions (N, k) ndarray
           targets (N, k) ndarray
    Returns: scalar
    """
    predictions = np.clip(predictions, epsilon, 1. - epsilon)
    N = predictions.shape[0]
    ce = -np.sum(targets*np.log(predictions+1e-9))/N
    return ce


if __name__ == "__main__":
    result2()
