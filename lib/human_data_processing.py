from os import listdir
from os.path import isfile, join
import pandas as pd
from polyfit import Polyfitor


class HumanData():
    """
    Load human data and pre-process
    User needs to make sure the filenames in /angle and /torque match exactly
    also make sure they are of the same length
    """
    def __init__(self):
        self.angle_data = []
        self._torque_raw = []
        self.torque_data = []
        self.weights = []
        self._scan_filenames()
        self._load_data()

    def _scan_filenames(self):
        angle_path = "../human_data/angle/"
        torque_path = "../human_data/torque/"
        self.angle_files = sorted([f for f in listdir(angle_path) if isfile(join(angle_path, f))])
        self.torque_files = sorted([f for f in listdir(torque_path) if isfile(join(torque_path, f))])

    def assign_weights(self):
        for file in self.angle_files:
            print("Please enter weight for: ", file)
            weight_temp = input()
            self.weights.append(weight_temp)
        print("Assign weight finished")

    def _load_data(self):
        for file in self.angle_files:
            file_data = pd.read_csv(file)
            self.angle_data.append(file_data)
        print("Read angle data done")
        for file in self.torque_files:
            file_data = pd.read_csv(file)
            self._torque_raw.append(file_data)
        print("Read torque data done")

