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

        self.bridge = CvBridge()

        self.body_img_srv = rospy.Service(
            "/kafka/publish_body_image",
            SendImageToKafka,
            self.send_body_image_cb,
        )
        self.arm_img_srv = rospy.Service(
            "/kafka/publish_arm_image", SendImageToKafka, self.send_arm_image_cb
        )

        rospy.spin()

    def load_parameters(self) -> None:
        self.filename_ = rospy.get_param("~topics_filename", "topics.yaml")
        self.bootstrap_server_ = rospy.get_param(
            "~bootstrap_server", "10.2.0.8:9092"
        )
        self.security_protocol_ = rospy.get_param(
            "~security_protocol", "PLAINTEXT"
        )
        self.update_rate_ = float(rospy.get_param("~update_rate", "10.0"))
        self.rate_ = rospy.Rate(self.update_rate_)
        self.robot_name_ = rospy.get_param("~robot_name", "UGV")
        self.body_ros_topic_ = "/front_rgbd_camera/rgb/image_raw"
        self.arm_ros_topic_ = "/wrist_rgbd_camera/rgb/image_raw"
        self.body_kafka_topic_ = "ugv.image.body"
        self.arm_kafka_topic_ = "ugv.image.arm"

    def send_body_image_cb(
        self, req: SendImageToKafkaRequest
    ) -> SendImageToKafkaResponse:

        return self.send_to_kafka(
            self.body_kafka_topic_, req.message, req.image
        )

    def send_arm_image_cb(
        self, req: SendImageToKafkaRequest
    ) -> SendImageToKafkaResponse:

        return self.send_to_kafka(self.arm_kafka_topic_, req.message, req.image)

    def send_to_kafka(self, kafka_topic, msg, img) -> SendImageToKafkaResponse:
        try:
            cv_image = self.bridge.imgmsg_to_cv2(
                img, desired_encoding="passthrough"
            )
            _, buffer = cv2.imencode(
                ".jpg", cv_image, [cv2.IMWRITE_JPEG_QUALITY, 50]
            )
            base64_image = base64.b64encode(buffer).decode("utf-8")

            # Create a json message
            json_message = {"message": msg, "image_data": base64_image}
            rospy.loginfo(f"Encoded image to Base64 for topic {kafka_topic}")
            self.producer.send(kafka_topic, json_message)
            return SendImageToKafkaResponse(success=True)
        except Exception as err:
            rospy.logerr(
                f"Failed to process image message for topic {kafka_topic}: {err}"
            )
            return SendImageToKafkaResponse(success=False)


if __name__ == "__main__":

    try:
        node = KafkaImagePublisher()
    except rospy.ROSInterruptException:
        pass

    rospy.loginfo("Exiting")
