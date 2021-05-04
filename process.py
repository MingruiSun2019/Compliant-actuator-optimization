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
from dashboard.dash_main import generate_app_layout, get_dash_plots


Q1_dict = {"y": "default", "n": "user_defined"}

My_settings = {
        "Deactive_color": "#19aae1",
        "Active_color": '#ffa500',
        "Plot_color": '#1f2c56',
        "Paper_color": '#1f2c56',
        "Font_color": '#ee9b06',
        "text_color": 'white',
        "grid_color": '#476293',
        "margin_left": "1.6vw"
    }


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

    # Initialize actuator and polyfitor
    print("Initialize actuator and polyfitor")
    polyfitor = Polyfitor()
    actuator = SeaType1(params=params, polyfitor=polyfitor)

    # Initialize optimizer 4QCI
    print("Initialize optimizer 4QCI")
    energy_model_4qci = Optimize4QCI(human_data, actuator, params)

    # Do optimization using 4QCI model
    print("Do optimization using 4QCI model")
    ranked_comb_info = energy_model_4qci.optimize_routine()
    print("ranked_4qci_comb:", ranked_comb_info)

    # Generate recommended variable range from n opt points
    print("Generate recommended variable range from n opt points")
    stiffness_range, ratio_range, m_inertia_range = energy_model_4qci.get_recommendation(ranked_comb_info, n_points=30)
    print("Stiffness range: ", stiffness_range)
    print("Ratio range: ", ratio_range)
    print("Motor inertia range: ", m_inertia_range)

    # Select if use recommended narrow down catalog, or user defined
    print("Select if use recommended narrow down catalog, or user defined")
    motor_catalog = load_catalog("./catalog/Motor_catalog_user_defined.csv")
    gear_catalog = load_catalog("./catalog/Gear_catalog_user_defined.csv")

    # Initialize optimizer FMM
    print("Initialize optimizer FMM")
    energy_model_fmm = OptimizeFMM(human_data, actuator, stiffness_range, motor_catalog, gear_catalog)

    # Do optimization with FMM model
    # return all the combinations with their energy consumption,
    # performance rating
    print("Do optimization with FMM model")
    ranked_comb_info = energy_model_fmm.optimize_routine()
    print(ranked_comb_info)

    # User input performance tolerance
    # question_txt = "Torque rating (0-1)?"
    # user_torque_rating = ask_answer(question_txt)
    # question_txt = "Speed rating (0-1)?"
    # user_speed_rating = ask_answer(question_txt)

    # Output filtered combinations with energy consumption and
    # performance rating
    # filtered_comb = [x for x in ranked_comb_info if x["T_rating"] >= float(user_torque_rating) and x["V_rating"] >= float(user_speed_rating)]
    # print("Selected combination:")
    # print(filtered_comb)

    # Select if want visualization
    dash_app, output_list, input_list = generate_app_layout(ranked_comb_info, human_data, motor_catalog, gear_catalog, actuator)
    num_activity = len(human_data.weights)

    @dash_app.callback(output_list, input_list)
    def update_graph(comb, user_torque_rating, user_speed_rating):
        filtered_comb = [x for x in ranked_comb_info if
                         x["T_rating"] >= float(user_torque_rating) and x["V_rating"] >= float(user_speed_rating)]
        comb_i = int(comb[1:])
        motor = motor_catalog.loc[motor_catalog['ID'] == filtered_comb[comb_i]["motor_id"]].squeeze()  # df to series
        gear = gear_catalog.loc[gear_catalog['ID'] == filtered_comb[comb_i]["gear_id"]].squeeze()  # df to series
        stiffness = filtered_comb[comb_i]["stiffness"]

        all_figs = []
        for i in range(num_activity):
            actuator.initialize()
            actuator.gather_info(stiffness, gear, motor,
                                 human_data.torque_data[i]["Data"], human_data.angle_data[i]["Data"],
                                 human_data.angle_data[i]["Time"])
            output_figs = get_dash_plots(actuator, motor, My_settings)
            all_figs += list(output_figs)

        return all_figs

    dash_app.run_server(debug=False)

    # Visualization

    pass


if __name__ == "__main__":
    process()
