#!/usr/bin/env python

import base64
import json
import argparse

import cv2
from kafka import KafkaConsumer
import numpy as np

def consume_images(kafka_topic: str, kafka_server: str):

    consumer = KafkaConsumer(
        kafka_topic,
        bootstrap_servers=kafka_server,
        value_deserializer=lambda m: json.loads(m.decode("ascii")),
    )

    print(f"subscribed to Kafka topic: {kafka_topic}")

    for message in consumer:
        print(f"type of message {type(message)}")
        try:
            image_data = message.value["image_data"]
            image_bytes = base64.b64decode(image_data)
            nparr = np.frombuffer(image_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

            if img_rgb is not None:
                cv2.imshow("Kafka Image", img_rgb)
                cv2.waitKey(1)
        except Exception as err:
            print(f"Error decoding image: {err}")

if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument("-t", "--topic", default="test.image.stream", help="Kafka topic name") 
    parser.add_argument("-s", "--server", default="10.2.0.8:9092", help="Kafka bootstrap server")

    args = parser.parse_args()
    
    consume_images(args.topic, args.server)
