#!/usr/bin/env python

import yaml

def load_yaml_to_dict(yaml_file: str, robot_name: str = 'UGV') -> dict:
    with open(yaml_file, 'r') as file:
        yaml_data = yaml.safe_load(file)

    topic_dict = {topic['topic']: topic['msg_type'] for topic in yaml_data[robot_name]}

    return topic_dict

yaml_file = "../config/topics.yaml"
topic_dict = load_yaml_to_dict(yaml_file)

for topic, msg_type in topic_dict.items():
    print(f"topic: {topic}, type: {msg_type}")