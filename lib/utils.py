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


def save_ranked_combs(combinations, filename):
    num_rating = 2
    all_energy = np.zeros((num_rating + 1, len(combinations)))
    header = []
    for index, comb in enumerate(combinations):
        motor, gear, stiffness = comb["motor"], comb["gear"], "S" + str(comb["stiffness"])
        all_energy[0, index] = comb["energy"]
        all_energy[1, index] = comb["T_rating"]
        all_energy[2, index] = comb["V_rating"]
        header.append("_".join([motor, gear, stiffness]))

    df = pd.DataFrame(all_energy, columns=header)
    df.to_csv(filename)

