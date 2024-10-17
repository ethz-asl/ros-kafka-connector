#!/usr/bin/env python

import rospy
import yaml

"""
For custom msg types, need to build pkg in workspace and then add here
"""


def load_yaml_to_dict(yaml_file: str, robot_name: str = "UGV") -> dict:
    """
    takes yaml file and converts to dict which includes topic names & msg types

    :param yaml_file (str): path to yaml file
    :param robot_name(str, optional): first line of yaml file, default -> 'UGV' 
    :return topic_dict (dict): dictionary mapping topics & msg types

    example: topic_list.yaml

    robot_name:
        - msg_type: "std_msgs/String"
          ros_topic: "/string"
          kafka_topic: "string"
        - msg_type: "geometry_msgs/Pose"
          ros_topic: "/pose"
          kafka_topic: "pose"

    topic_dict: {
        'std_msgs/String': {'/string', 'string'},
        'geometry_msgs/Pose' : {'/pose', 'pose'}
    }
    """
    with open(yaml_file, "r") as file:
        yaml_data = yaml.safe_load(file)

    topics_dict = {}
    for topic in yaml_data[robot_name]:
        msg_type = topic["msg_type"]
        ros_topic = topic["ros_topic"]
        kafka_topic = topic["kafka_topic"]

        topics_dict[msg_type] = {
            "ros_topic": ros_topic,
            "kafka_topic": kafka_topic,
        }

    return topics_dict


def import_msg_type(msg_type: str):
    """
    takes a ros msg_type and dynamically imports the msg type and returns it
    
    :params msg_type (str): the string identifier for the ROS msg type
    :return subscriber_type (class): the corresponding ROS msg class
    :raises ValueError: if msg_type is not found
    """
    if msg_type == "std_msgs/String":
        from std_msgs.msg import String

        subscriber_msg = String
    elif msg_type == "std_msgs/Bool":
        from std_msgs.msg import Bool

        subscriber_msg = Bool
    elif msg_type == "std_msgs/Empty":
        from std_msgs.msg import Empty

        subscriber_msg = Empty
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
    elif msg_type == "sensor_msgs/Image":
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
    elif msg_type == "tf2_msgs/TFMessage":
        from tf2_msgs.msg import TFMessage

        subscriber_msg = TFMessage
    else:
        raise ValueError(
            f'MSG "{msg_type}" IS NOT SUPPORTED \nPlease add imports to utils.py for specific msg type.'
        )

    return subscriber_msg
