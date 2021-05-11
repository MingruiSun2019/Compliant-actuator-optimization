"""
This file allows users to input parameters according to
their specific requirements
"""

# Body weight
BODY_WEIGHT = 90

# Stiffness (Nm/rad)
STIFFNESS_UPPER = 600
STIFFNESS_LOWER = 100
STIFFNESS_INTERVAL = 50

# Gear
GEAR_EFFICIENCY_CONSTANT = 0.75
GEAR_RATIO_UPPER = 200
GEAR_RATIO_LOWER = 1
GEAR_RATIO_INTERVAL = 20

# Motor
MOTOR_EFFICIENCY_CONSTANT = 0.5
MOTOR_INERTIA_UPPER = 1000
MOTOR_INERTIA_LOWER = 10
MOTOR_INERTIA_INTERVAL = 50
# TODO: non-linear interval

# Motor driver
DRIVER_VOLTAGE_LIMIT = 50
DRIVER_CURRENT_LIMIT = 15

# Link inertia
LINK_INERTIA = 1800000  # (gcm^2)

# Sub optimal points percent
SUB_OPT_RATE = 0.2