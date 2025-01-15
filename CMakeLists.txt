cmake_minimum_required(VERSION 2.8.3)
project(ros_kafka_connector)

find_package(catkin REQUIRED)
catkin_python_setup()
catkin_package(
    CATKIN_DEPENDS
    rospy
    std_msgs
    geometry_msgs
    sensor_msgs
    tf2_msgs
    heron_msgs
    robotnik_msgs
)
