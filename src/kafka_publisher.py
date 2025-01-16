#!/usr/bin/env python

import rospy
import rospkg
import json

from typing import Dict, Any
from kafka import KafkaProducer
from confluent_kafka.admin import AdminClient, NewTopic
from rospy_message_converter import json_message_converter
from sensor_msgs.msg import Image

import utils


class KafkaPublisher:
    """
    takes a yaml file with:
    - ros msg types
    - ros topic names
    - kafka topic names

    subscribes to the ros topic, and converts to json format
    publishes json msg to the kafka topic

    """

    def __init__(self) -> None:

        rospy.init_node("kafka_publisher")
        rospy.on_shutdown(self.shutdown)

        self.load_parameters()
        pkg = rospkg.RosPack()
        yaml_file = (
            pkg.get_path("ros_kafka_connector") + "/config/" + self._filename
        )

        self.topics_dict = utils.load_yaml_to_dict(yaml_file, self._robot_name)

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

        self.create_kafka_topics(self.topics_dict)

        # start kafka producer
        self.producer = KafkaProducer(
            bootstrap_servers=self._bootstrap_server,
            security_protocol=self._security_protocol,
            value_serializer=lambda m: json.dumps(m).encode("ascii"),
        )

        # create topic storage for the latest messages
        self.latest_msgs = {
            details["ros_topic"]: None for details in self.topics_dict.values()
        }

        # subscribers for all topics
        for msg_type, details in self.topics_dict.items():
            ros_topic = details["ros_topic"]
            msg_class = utils.import_msg_type(msg_type)
            rospy.Subscriber(
                ros_topic,
                msg_class,
                self.message_callback,
                callback_args=ros_topic,
            )
            rospy.loginfo(f"Subscribed to ROS topic: {ros_topic}")

        self.run()

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

    def create_kafka_topics(self, topics_dict: Dict[str, Dict[str, str]]) -> None:
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

    def message_callback(self, msg: Any, ros_topic: str) -> None:
        """
        stores latest ros msg
        """
        self.latest_msgs[ros_topic] = msg

    def publish_to_kafka(self) -> None:
        """
        publish the latest messages to their respective Kafka topics.
        """
        for msg_type, details in self.topics_dict.items():
            ros_topic = details["ros_topic"]
            kafka_topic = details["kafka_topic"]
            msg = self.latest_msgs[ros_topic]

            if msg is None:
                continue  # skip if no message has been received yet

            try:
                # convert messages to JSON
                json_message = (
                    json_message_converter.convert_ros_message_to_json(msg)
                )

                self.producer.send(kafka_topic, json_message)
                rospy.loginfo(f"Published to Kafka topic: {kafka_topic}")
            except Exception as e:
                rospy.logerr(
                    f"Failed to publish message from {ros_topic} to {kafka_topic}: {e}"
                )

    def run(self) -> None:
        rate = rospy.Rate(self._update_rate)
        while not rospy.is_shutdown():
            self.publish_to_kafka()
            rate.sleep()

    def shutdown(self) -> None:
        rospy.loginfo("Shutting down")


if __name__ == "__main__":

    try:
        node = KafkaPublisher()
        node.run()
    except rospy.ROSInterruptException:
        pass

    rospy.loginfo("Exiting")
