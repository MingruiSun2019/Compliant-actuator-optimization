"""
This file includes all other minor functions
"""
import pandas as pd


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

