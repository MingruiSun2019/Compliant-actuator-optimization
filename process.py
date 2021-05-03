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


Q1_dict = {"y": "default", "n": "user_defined"}


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
    question_txt = "Torque rating (0-1)?"
    user_torque_rating = ask_answer(question_txt)
    question_txt = "Speed rating (0-1)?"
    user_speed_rating = ask_answer(question_txt)

    # Output filtered combinations with energy consumption and
    # performance rating
    filtered_comb = [x for x in ranked_comb_info if x["T_rating"] >= float(user_torque_rating) and x["V_rating"] >= float(user_speed_rating)]
    print("Selected combination:")
    print(filtered_comb)

    # Select if want visualization


    # Visualization

    pass


if __name__ == "__main__":
    process()
