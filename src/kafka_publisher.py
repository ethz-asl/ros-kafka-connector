#!/usr/bin/env python

import json
from kafka import KafkaProducer
from kafka import KafkaConsumer
import rospy
import rospkg
from rospy_message_converter import json_message_converter
import utils


class KafkaPublisher:
    # TODO need to make kafka topics!!
    """
    takes a yaml file with:
    - ros msg types
    - ros topic names
    - kafka topic names

    subscribes to the ros topic, and converts to json format
    publishes json msg to the kafka topic

    """

    def __init__(self):

        rospy.init_node("kafka_publisher")
        rospy.on_shutdown(self.shutdown)

        self.load_parameters()
        pkg = rospkg.RosPack()
        yaml_file = (
            pkg.get_path("ros_kafka_connector") + "/config/" + self._filename
        )

        topics_dict = utils.load_yaml_to_dict(yaml_file, robot_name="UGV")

        # start kafka producer
        # self.producer = KafkaProducer(
        #     bootstrap_servers=self._bootstrap_server,
        #     value_serializer=lambda m: json.dumps(m).encode('ascii')
        # )

        for msg_type, topics in topics_dict.items():
            ros_topic = topics["ros_topic"]
            kafka_topic = topics["kafka_topic"]
            msg_class = utils.import_msg_type(msg_type)
            rospy.Subscriber(
                ros_topic,
                msg_class,
                lambda msg: self.callback(msg, kafka_topic),
            )
            rospy.loginfo(
                f"Using {msg_type} from ROS: {ros_topic} -> KAFKA: {kafka_topic}"
            )

    def load_parameters(self) -> None:
        self._filename = rospy.get_param("~topics_filename", "topics.yaml")
        self._bootstrap_server = rospy.get_param(
            "~bootstrap_server", "localhost:9092"
        )
        self._update_rate = float(rospy.get_param("~update_rate", "10.0"))

    def callback(self, msg, kafka_topic: str) -> None:
        """
        takes msg from ros, converts to json, publishes to kafka
        
        :param msg: ros msg from subscriber 
        :param kafka_topic (str): kafka topic name

        """
        json_str = json_message_converter.convert_ros_message_to_json(msg)
        # self.producer.send(kafka_topic, json_str)

    def run(self):
        rate = rospy.Rate(self._update_rate)
        while not rospy.is_shutdown():
            rate.sleep()

    def shutdown(self):
        rospy.loginfo("Shutting down")


if __name__ == "__main__":

    try:
        node = KafkaPublisher()
        node.run()
    except rospy.ROSInterruptException:
        pass

    rospy.loginfo("Exiting")
