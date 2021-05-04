import numpy as np


class Polyfitor():
    """
    This class contains all functions regarding polyfit
    """

    def __init__(self, poly_order=12, target_res=200, ext_lvl=0.02, acc_limit=1000):
        self._poly_order = poly_order
        self._target_res = target_res
        self._ext_lvl = ext_lvl
        self._acc_limit = acc_limit

    def _fit_dots(self, arr_x, arr_y, poly_order):
        poly_coef, residue, _, _, _ = np.polyfit(arr_x, arr_y, poly_order, full=True)
        return poly_coef, residue

    def multi_fit(self, arr_x, arr_y, arr_x_real, result_x, result_y, is_left=None):
        # TODO: limit output
        poly_coef, residue = self._fit_dots(arr_x, arr_y, self._poly_order)
        if residue <= self._target_res:
            result_x.append(arr_x_real)
            result_y.append(poly_coef)
            return result_x, result_y
        else:
            arr_len = len(arr_x_real)
            arr_len_full = len(arr_x)
            real_half_len = int(np.ceil(arr_len / 2))
            full_half_len = int(np.ceil(arr_len_full / 2))
            ext_len = int(arr_len * self._ext_lvl)
            if is_left == 1:
                arr_x_left = arr_x[:real_half_len + ext_len]
                arr_x_left_real = arr_x_real[:real_half_len]
                arr_y_left = arr_y[:real_half_len + ext_len]
                arr_x_right = arr_x[real_half_len - ext_len:]
                arr_x_right_real = arr_x_real[real_half_len:]
                arr_y_right = arr_y[real_half_len - ext_len:]
            elif is_left == 0:
                arr_x_left = arr_x[:- real_half_len + ext_len]
                arr_x_left_real = arr_x_real[:real_half_len]
                arr_y_left = arr_y[:- real_half_len + ext_len]
                arr_x_right = arr_x[- real_half_len - ext_len:]
                arr_x_right_real = arr_x_real[real_half_len:]
                arr_y_right = arr_y[- real_half_len - ext_len:]
            else:
                arr_x_left = arr_x[:full_half_len + ext_len]
                arr_x_left_real = arr_x_real[:real_half_len]
                arr_y_left = arr_y[:full_half_len + ext_len]
                arr_x_right = arr_x[full_half_len - ext_len:]
                arr_x_right_real = arr_x_real[real_half_len:]
                arr_y_right = arr_y[full_half_len - ext_len:]

            result_x, result_y = self.multi_fit(arr_x_left, arr_y_left, arr_x_left_real, result_x, result_y, is_left=1)
            result_x, result_y = self.multi_fit(arr_x_right, arr_y_right, arr_x_right_real, result_x, result_y, is_left=0)

            return result_x, result_y

    def get_acc(self, result_x, result_y):
        x_data = []
        motor_acc = []
        for i in range(len(result_x)):
            x_data += list(result_x[i])
            poly_model = np.poly1d(result_y[i])
            my_acc = np.polyder(poly_model, 2)
            motor_acc += list(my_acc(result_x[i]))
        motor_acc = np.array(motor_acc)
        motor_acc = np.clip(motor_acc, a_min=-self._acc_limit, a_max=self._acc_limit)

        return np.array(x_data), motor_acc
