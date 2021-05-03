from os import listdir
from os.path import isfile, join
import pandas as pd


class HumanData():
    """
    Load human data and pre-process
    User needs to make sure the filenames in /angle and /torque match exactly
    also make sure they are of the same length
    """
    def __init__(self, params):
        self.params = params
        self.angle_path = "human_data/angle/"
        self.torque_path = "human_data/torque/"
        self.angle_files = None
        self.torque_files = None
        self.angle_data = []
        self.torque_data = []
        self.weights = []
        self._scan_filenames()
        self._load_data()

    def _scan_filenames(self):
        self.angle_files = sorted([f for f in listdir(self.angle_path) if isfile(join(self.angle_path, f))])
        self.torque_files = sorted([f for f in listdir(self.torque_path) if isfile(join(self.torque_path, f))])

    def assign_weights(self):
        for file in self.angle_files:
            print("Please enter weight for: ", file)
            weight_temp = input()
            self.weights.append(float(weight_temp))
        print("Assign weight finished")

    def _load_data(self):
        for file in self.angle_files:
            angle_data = pd.read_csv(self.angle_path + file)
            self.angle_data.append(angle_data)
        print("Read angle data done")
        for file in self.torque_files:
            torque_data_per_kg = pd.read_csv(self.torque_path + file)
            torque_data = torque_data_per_kg.apply(self._apply_body_weight)
            self.torque_data.append(torque_data)
        print("Read torque data done")

    def _apply_body_weight(self, x):
        return x * self.params.body_weight

