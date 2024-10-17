#!/usr/bin/env python

import json
from kafka import KafkaProducer
from kafka import KafkaConsumer
import rospy
import rospkg
from rospy_message_converter import json_message_converter
import utils


class ROSPublisher:
    def __init__(self):

        rospy.init_node("ros_publisher")
        rospy.on_shutdown(self.shutdown)

        self.load_parameters()
        pkg = rospkg.RosPack()
        yaml_file = (
            pkg.get_path("ros_kafka_connector") + "/config/" + self._filename
        )

        topics_dict = utils.load_yaml_to_dict(yaml_file, self._robot_name)

        self.consumers = []
        self.publishers = []
        for msg_type, topics in topics_dict.items():
            ros_topic = topics["ros_topic"]
            kafka_topic = topics["kafka_topic"]

            consumer = KafkaConsumer(
                kafka_topic,
                bootstrap_servers=self._bootstrap_server,
                value_deserializer=lambda m: json.loads(m.decode("ascii")),
                auto_offset_reset="latest",
                consumer_timeout_ms=5000,
            )
            msg_class = utils.import_msg_type(msg_type)
            publisher = rospy.Publisher(ros_topic, msg_class, queue_size=10)
            rospy.loginfo(
                f"Using {msg_type} from ROS: {ros_topic} -> KAFKA: {kafka_topic}"
            )

            self.consumers.append(consumer)
            self.publishers.append(publisher)

    def load_parameters(self) -> None:
        self._filename = rospy.get_param("~topics_filename", "topics.yaml")
        self._bootstrap_server = rospy.get_param(
            "~bootstrap_server", "localhost:9092"
        )
        self._robot_name = rospy.get_param("~robot_name", "UGV")
        

    def run(self):

        while not rospy.is_shutdown():
            for consumer, publisher in zip(self.consumers, self.publishers):
                for msg in consumer:
                    json_str = json.dump(msg.value)
                    ros_msg = json_message_converter.convert_json_to_ros_message(
                        publisher.type, json_str
                    )
                    publisher.publish(ros_msg)

        rospy.spin()

    def shutdown(self):
        rospy.loginfo("Shutting down")


if __name__ == "__main__":

    try:
        node = ROSPublisher()
        node.run()
    except rospy.ROSInterruptException:
        pass

    rospy.loginfo("Exiting")
