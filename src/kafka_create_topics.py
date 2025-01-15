#!/usr/bin/env python

import json
import base64
import cv2
from cv_bridge import CvBridge
from kafka import KafkaProducer, KafkaConsumer
from confluent_kafka.admin import AdminClient, NewTopic
import rospy
import rospkg
from rospy_message_converter import json_message_converter
from sensor_msgs.msg import Image
import utils


class KafkaCreateTopics:
    """
    takes a yaml file with:
    - ros msg types
    - ros topic names
    - kafka topic names

    subscribes to the ros topic, and converts to json format
    publishes json msg to the kafka topic

    """

    def __init__(self):

        rospy.init_node("kafka_topic_creator")

        self.load_parameters()
        pkg = rospkg.RosPack()
        yaml_file = (
            pkg.get_path("ros_kafka_connector") + "/config/" + self._filename
        )
        self.bridge = CvBridge()

        topics_dict = utils.load_yaml_to_dict(yaml_file, self._robot_name)

        # initialise admin client to create topics
        self.admin_client = AdminClient(
            {"bootstrap.servers": self._bootstrap_server}
        )

        try:
            self.admin_client.list_topics(timeout=5)
            rospy.loginfo("Kafka connection successful.")
        except Exception as err:
            rospy.logerr(f"Failed to connect to Kafka: {err}")
            rospy.signal_shutdown("Kafka connection failed.")

        self.create_kafka_topics(topics_dict)

    def load_parameters(self) -> None:
        self._filename = rospy.get_param("~topics_filename", "topics.yaml")
        self._bootstrap_server = rospy.get_param(
            "~bootstrap_server", "10.2.0.8:9092"
        )
        self._security_protocol = rospy.get_param(
            "~security_protocol", "PLAINTEXT"
        )
        self._update_rate = float(rospy.get_param("~update_rate", "10.0"))
        self._robot_name = rospy.get_param("~robot_name", "UGV")

    def create_kafka_topics(self, topics_dict: dict) -> None:
        """
        creates kafka topics based on config

        :param topics_dict (dict): dictionary of kafka & ros topics
        """
        kafka_topics = [
            topics["kafka_topic"] for topics in topics_dict.values()
        ]

        # check topic doesn't already exist
        existing_topics = self.admin_client.list_topics().topics.keys()
        new_topics = [
            NewTopic(topic, num_partitions=1, replication_factor=1)
            for topic in kafka_topics
            if topic not in existing_topics
        ]

        if new_topics:
            rospy.loginfo(
                f"Creating kafka topic {[t.topic for t in new_topics]}"
            )
            futures = self.admin_client.create_topics(new_topics)

            for topic, future in futures.items():
                try:
                    future.result()  # wait for op to finish
                    rospy.loginfo(f"Kafka topic '{topic}' created sucessfully!")
                except Exception as err:
                    rospy.logerr(f"Failed to create topic '{topic}' : {err}")

        else:
            rospy.logerr("All kafka topics already exist.")

if __name__ == "__main__":

    try:
        node = KafkaCreateTopics()
    except rospy.ROSInterruptException:
        pass

    rospy.loginfo("Exiting")
