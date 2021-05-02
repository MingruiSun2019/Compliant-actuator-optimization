"""
This file saves the default (recommended) parameters
"""

# Stiffness (Nm/rad)
STIFFNESS_UPPER = 600
STIFFNESS_LOWER = 100
STIFFNESS_INTERVAL = 100

# Gear
GEAR_EFFICIENCY_CONSTANT = 0.8
GEAR_RATIO_UPPER = 150
GEAR_RATIO_LOWER = 30
GEAR_RATIO_INTERVAL = 20

# Motor
MOTOR_EFFICIENCY_CONSTANT = 0.75
MOTOR_INERTIA_UPPER = 4000
MOTOR_INERTIA_LOWER = 50
MOTOR_INERTIA_INTERVAL = 300
# TODO: non-linear interval

# Motor driver
DRIVER_VOLTAGE_LIMIT = 50
DRIVER_CURRENT_LIMIT = 10
