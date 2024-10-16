#!/usr/bin/env python

"""
For custom msg types, need to build pkg in workspace and then add here
"""

def import_msg_type(msg_type):

    # Adding a new msg type is as easy as including an import and updating the variable 
    if msg_type == "std_msgs/String":
        from std_msgs.msg import String
        subscriber_msg = String
    if msg_type == "std_msgs/Bool":
        from std_msgs.msg import Bool
        subscriber_msg = Bool
    if msg_type == "std_msgs/Empty":
        from std_msgs.msg import Empty
        subscriber_msg = Bool
    elif msg_type == "geometry_msgs/Twist":
        from geometry_msgs.msg import Twist
        subscriber_msg = Twist
    elif msg_type == "geometry_msgs/Pose":
        from geometry_msgs.msg import Pose
        subscriber_msg = Pose
    elif msg_type == "geometry_msgs/PoseArray":
        from geometry_msgs.msg import PoseArray
        subscriber_msg = PoseArray
    elif msg_type == "geometry_msgs/PoseStamped":
        from geometry_msgs.msg import PoseStamped
        subscriber_msg = PoseStamped
    elif msg_type == "geometry_msgs/PoseWithCovariance":
        from geometry_msgs.msg import PoseWithCovariance
        subscriber_msg = PoseWithCovariance
    elif msg_type == "geometry_msgs/PoseWithCovarianceStamped":
        from geometry_msgs.msg import PoseWithCovarianceStamped
        subscriber_msg = PoseWithCovarianceStamped
    elif msg_type == "geometry_msgs/Vector3":
        from geometry_msgs.msg import Vector3
        subscriber_msg = Vector3
    elif msg_type == "sensors_msgs/Image":
        from sensor_msgs.msg import Image
        subscriber_msg = Image
    elif msg_type == "sensor_msgs/LaserScan":
        from sensor_msgs.msg import LaserScan
        subscriber_msg = LaserScan
    elif msg_type == "sensor_msgs/BatteryState":
        from sensor_msgs.msg import BatteryState
        subscriber_msg = BatteryState
    elif msg_type == "sensor_msgs/Imu":
        from sensor_msgs.msg import Imu
        subscriber_msg = Imu
    elif msg_type == "sensor_msgs/PointCloud2":
        from sensor_msgs.msg import PointCloud2
        subscriber_msg = PointCloud2
    elif msg_type == "sensor_msgs/JointState":
        from sensor_msgs.msg import JointState
        subscriber_msg = JointState
    elif msg_type == "sensor_msgs/NavSatFix":
        from sensor_msgs.msg import NavSatFix
        subscriber_msg = NavSatFix
    elif msg_type == "nav_msgs/Odometry":
        from nav_msgs.msg import Odometry
        subscriber_msg = Odometry
    elif msg_type == "nav_msgs/OccupancyGrid":
        from nav_msgs.msg import OccupancyGrid
        subscriber_msg = OccupancyGrid
    elif msg_type == "actionlib_msgs/GoalStatus":
        from actionlib_msgs.msg import GoalStatus
        subscriber_msg = GoalStatus
    else:
        raise ValueError("MSG NOT SUPPORTED: Only String/Twist/Image are currently supported. \
                          Please add imports to utils.py for specific msg type.")
    
    return subscriber_msg
