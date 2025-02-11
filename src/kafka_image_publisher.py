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
from std_srvs.srv import Empty

from heron_msgs.srv import (
    SendImageToKafka,
    SendImageToKafkaRequest,
    SendImageToKafkaResponse,
)

class KafkaImagePublisher:
    """
    sends ROS images to kafka with ROS srv call
    images in kafka are in the Base64 type.

    services will send an image before and after image processing
    e.g. pothole detection

    hardcoded ros topics & kafka topics
    kafka topics should already be created
    """
    def __init__(self):

        rospy.init_node("kafka_image_publisher")

        self.load_parameters()
        self.bridge = CvBridge()

        # start kafka producer
        self.producer = KafkaProducer(
            bootstrap_servers=self.bootstrap_server_,
            security_protocol=self.security_protocol_,
            value_serializer=lambda m: json.dumps(m).encode("ascii"),
        )

        self.bridge = CvBridge() # start bridge to convert images

        # services for before/after image processing
        self.img_srv = rospy.Service(
            "/kafka/publish_image",
            SendImageToKafka,
            self.send_to_kafka,
        )
    
        rospy.spin()

    def load_parameters(self) -> None:
        self.bootstrap_server_ = rospy.get_param(
            "~bootstrap_server", "10.2.0.8:9092"
        )
        self.security_protocol_ = rospy.get_param(
            "~security_protocol", "PLAINTEXT"
        )
        self.kafka_topic_ = "ugv.image"

    def send_to_kafka(self, req: SendImageToKafkaRequest) -> SendImageToKafkaResponse:
        try:
            cv_image = self.bridge.imgmsg_to_cv2(
                req.image, desired_encoding="passthrough"
            )
            _, buffer = cv2.imencode(
                ".jpg", cv_image, [cv2.IMWRITE_JPEG_QUALITY, 50]
            )
            base64_image = base64.b64encode(buffer).decode("utf-8")

            # Create a json message
            json_message = {"message": str(req.message), "image_data": base64_image}
            rospy.loginfo(f"Encoded image to Base64 for topic {self.kafka_topic_}")
            self.producer.send(self.kafka_topic_, json_message)
            return SendImageToKafkaResponse(success=True)
        except Exception as err:
            rospy.logerr(
                f"Failed to process image message for topic {self.kafka_topic_}: {err}"
            )
            return SendImageToKafkaResponse(success=False)


if __name__ == "__main__":

    try:
        node = KafkaImagePublisher()
    except rospy.ROSInterruptException:
        pass

    rospy.loginfo("Exiting")
