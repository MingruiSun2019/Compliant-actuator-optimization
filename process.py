"""
Collects all steps for this software
"""
from .lib.utils import *
from .lib.parameter_loader import Params

Q1_dict = {"y": "default", "n": "user_defined"}


def process():
    # Select if using default parameters or user defined
    question_txt = "Do you want to use default parameters(y) or user defined(n)?"
    ans = ask_answer(question_txt)
    params = Params(Q1_dict[ans])

    # Do optimization using 4QCI model
    # return n opt points

    # Generate recommended variable range

    # Select if use recommended narrow down catalog, or user defined

    # Do optimization with FMM model
    # return all the combinations with their energy consumption,
    # performance rating

    # User input performance tolerance

    # Output filtered combinations with energy consumption and
    # performance rating

    # Select if want visualization

    # Visualization

    pass


if __name__ == "__main__":
    process()
