import math

def calculate_robot_speed(motor_rpm: float, gear_ratio: float, wheel_diameter_inches: float) -> float:
    """
    Calculates the linear speed of a robot in feet per second.

    Args:
        motor_rpm (float): The RPM of the motor.
        gear_ratio (float): The total gear ratio (motor to wheel).
        wheel_diameter_inches (float): The diameter of the wheel in inches.

    Returns:
        float: The linear speed of the robot in feet per second.
    """
    if gear_ratio == 0:
        return 0.0 # Avoid division by zero
    output_rpm = motor_rpm / gear_ratio
    wheel_circumference_inches = wheel_diameter_inches * math.pi
    speed_inches_per_minute = output_rpm * wheel_circumference_inches
    speed_feet_per_second = (speed_inches_per_minute / 12) / 60
    return speed_feet_per_second

def calculate_motor_free_speed(motor_type: str) -> float:
    """
    Returns the free speed RPM for common FRC motors.
    This is a simplified lookup for demonstration.

    Args:
        motor_type (str): The type of FRC motor (e.g., 'NEO', 'Falcon 500', 'CIM').

    Returns:
        float: The free speed RPM of the motor, or 0 if not recognized.
    """
    motor_speeds = {
        'NEO': 5676, # REV Robotics NEO Brushless Motor
        'Falcon 500': 6380, # VEXpro Falcon 500
        'CIM': 5330, # AndyMark CIM Motor
        'MiniCIM': 6200, # AndyMark Mini CIM Motor
        '775pro': 18730 # VEXpro 775pro
    }
    return motor_speeds.get(motor_type, 0.0)