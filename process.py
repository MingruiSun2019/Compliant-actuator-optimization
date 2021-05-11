"""
Collects all steps for this software
"""
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


def process():
    # Select if using default parameters or user defined
    print("Select if using default parameters or user defined")
    question_txt = "Do you want to use default parameters(y) or user defined(n)?"
    ans = ask_answer(question_txt)
    params = Params(Q1_dict[ans])

    # Load human data
    print("Load human data")
    human_data = HumanData(params)
    human_data.assign_weights()

    # Fit motor efficiency based on default motor database
    popt = fit_motor_efficiency(Default_motor_catalog)

    # Initialize actuator and polyfitor
    print("Initialize actuator and polyfitor")
    polyfitor = Polyfitor()
    actuator = SeaType1(params=params, polyfitor=polyfitor,  motor_eff_model=popt)

    # Initialize optimizer 4QCI
    print("Initialize optimizer 4QCI")
    energy_model_4qci = Optimize4QCI(human_data, actuator, params)

    # Do optimization using 4QCI model
    print("Do optimization using 4QCI model")
    ranked_comb_info = energy_model_4qci.optimize_routine()
    min_ave_power = min([x["ave_power"] for x in ranked_comb_info])
    print("ranked_4qci_comb:", ranked_comb_info)

    # Generate recommended variable range from n opt points
    print("Generate recommended variable range from n opt points")
    stiffness_range, ratio_range, m_inertia_range = energy_model_4qci.get_recommendation(ranked_comb_info, n_points=params.subopt_n)
    print("Stiffness range: ", stiffness_range)
    print("Ratio range: ", ratio_range)
    print("Motor inertia range: ", m_inertia_range)

    # Get peak load torque
    peak_load_torque = energy_model_4qci.get_peak_torque()
    print("Peak torque: ", peak_load_torque)
    print("Min_ave_power: ", min_ave_power)

    # Select if use recommended narrow down catalog, or user defined
    # TODO: auto-select
    question_txt = "Do you want to use default database (y), or user defined database (n)?"
    ans = ask_answer(question_txt)
    if ans == "y":
        # TODO: if cannot find, redo range
        gear_catalog_hd = narrow_down_gear_catalog(ratio_range, peak_load_torque, filename=Default_gear_catalog_hd)
        gear_catalog_pg = narrow_down_gear_catalog(ratio_range, peak_load_torque, filename=Default_gear_catalog_pg)
        gear_catalog_sg = narrow_down_gear_catalog(ratio_range, peak_load_torque, filename=Default_gear_catalog_sg)
        gear_catalog = pd.concat([gear_catalog_hd, gear_catalog_pg, gear_catalog_sg])
        refined_inertia_range = refine_inertia_range(m_inertia_range, gear_catalog, params)
        print("refined_inertia_range: ", refined_inertia_range)
        motor_catalog = narrow_down_motor_catalog(refined_inertia_range, min_ave_power, filename=Default_motor_catalog)
        print("Found ", len(motor_catalog), "motors!")
        print("Found ", len(gear_catalog), "gears! ",
              "{} Spur Gear, {} Planetary Gear, {} armonic drive".format(len(gear_catalog_sg), len(gear_catalog_pg), len(gear_catalog_hd)))
    elif ans == "n":
        motor_catalog = load_catalog(Ud_motor_catalog)
        gear_catalog = load_catalog(Ud_gear_catalog)

    # Initialize optimizer FMM
    print("Initialize optimizer FMM")
    energy_model_fmm = OptimizeFMM(human_data, actuator, stiffness_range, motor_catalog, gear_catalog)

    # Do optimization with FMM model
    # return all the combinations with their energy consumption,
    # performance rating
    print("Do optimization with FMM model")
    ranked_comb_info, max_ratings = energy_model_fmm.optimize_routine()
    filtered_comb_init = [x for x in ranked_comb_info if x["T_rating"] <= max_ratings["T_rating"] and x["V_rating"] <= max_ratings["V_rating"]
                          and x["U_rating"] <= max_ratings["U_rating"] and x["I_rating"] <= max_ratings["I_rating"]
                          and x["motor_dia"] <= 100 and x["motor_length"] <= 80 and x["gear_type"] == 2]   # default value
    filtered_comb_init = pd.DataFrame(filtered_comb_init)
    print(filtered_comb_init)

    # Select if want visualization
    dash_app, output_list, input_list, table_output, table_input, stat_output = generate_app_layout(human_data,
                                                                                                    filtered_comb_init,
                                                                                                    max_ratings)

    # Callback functions
    @dash_app.callback(output_list, input_list)
    def update_graph(comb, usr_t, usr_v, usr_u, usr_i, usr_motor_len, usr_motor_dia, usr_gear_type):
        # Gear type: 0: spur gear, 1:planetary gear, 2:harmonic drive
        filtered_comb = [x for x in ranked_comb_info if
                         x["T_rating"] <= float(usr_t)+0.001 and x["V_rating"] <= float(usr_v)
                         and x["U_rating"] <= float(usr_u) and x["I_rating"] <= float(usr_i)
                         and x["motor_dia"] <= float(usr_motor_len) and x["motor_length"] <= float(usr_motor_dia)
                         and x["gear_type"] == int(usr_gear_type)]

        comb_i = int(comb[1:]) - 1
        motor = motor_catalog.loc[motor_catalog['Name'] == filtered_comb[comb_i]["motor_name"]].squeeze()  # df to series
        gear = gear_catalog.loc[gear_catalog['Name'] == filtered_comb[comb_i]["gear_name"]].squeeze()  # df to series
        stiffness = filtered_comb[comb_i]["stiffness"]

        all_figs = []
        for i in range(len(human_data.weights)):
            actuator.initialize()
            actuator.gather_info(stiffness, gear, motor,
                                 human_data.torque_data[i]["Data"], human_data.angle_data[i]["Data"],
                                 human_data.angle_data[i]["Time"])
            output_figs = get_dash_plots(actuator, motor, My_settings)
            all_figs += list(output_figs)

        return all_figs

    @dash_app.callback(table_output, table_input)
    def update_graph(user_torque_rating, user_speed_rating, usr_u, usr_i, usr_motor_len, usr_motor_dia, usr_gear_type):
        filtered_comb = [x for x in ranked_comb_info if
                         x["T_rating"] <= float(user_torque_rating)+0.001 and x["V_rating"] <= float(user_speed_rating)
                         and x["U_rating"] <= float(usr_u) and x["I_rating"] <= float(usr_i)
                         and x["motor_dia"] <= float(usr_motor_len) and x["motor_length"] <= float(usr_motor_dia)
                         and x["gear_type"] == int(usr_gear_type)]
        table_data = pd.DataFrame(filtered_comb[:100])  # Only take the top 100
        table_data = table_data.round(2)
        return [table_data.to_dict('records')]

    @dash_app.callback(stat_output, table_input)
    def update_graph(stat_1, stat_2, stat_3, stat_4, stat_5, stat_6, stat_7):
        gear_type_name = ["spur gear", "planetary gear", "harmonic drive"]
        stat_2dec = [num_2dec(stat_1), num_2dec(stat_2), num_2dec(stat_3),
                     num_2dec(stat_4), num_2dec(stat_5), num_2dec(stat_6), gear_type_name[int(stat_7)]]
        return stat_2dec

    dash_app.run_server(debug=False)


if __name__ == "__main__":
    process()
