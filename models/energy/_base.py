class EnergyModelBase():
    def __init__(self, huaman_data, actuator):
        self.huaman_data = huaman_data
        self.actuator = actuator

    def load_human_data(self, activity_i):
        des_torque = self.huaman_data.torque_data[activity_i]["Data"]
        des_angle = self.huaman_data.angle_data[activity_i]["Data"]
        time_series = self.huaman_data.angle_data[activity_i]["Time"]
        time_step = time_series[1] - time_series[0]
        return des_torque, des_angle, time_series, time_step
