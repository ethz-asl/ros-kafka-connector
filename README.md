# ROS Package: ros_kafka_connector 

This is a ROS package for subscribing or publishing to topics using Kafka. 

Takes a yaml file with {`msg_type`, `ros_topic`, `kafka_topic`}. Can publish the messages between ros and kafka. Put the yaml file in the `config/` folder. 

Example yaml file in: [`topics.yaml`](../blob/heron/config/topics.yaml)

```yaml
robot_name:
    - msg_type: "std_msgs/String"
      ros_topic: "/string"
      kafka_topic: "string"
    - msg_type: "geometry_msgs/Pose"
      ros_topic: "/pose"
      kafka_topic: "pose"
```

Will find dictionary:
```python
topic_dict: {
    'std_msgs/String': {'/string', 'string'},
    'geometry_msgs/Pose' : {'/pose', 'pose'}
}
```
Message types that are added are in the `utils.py` file.  To add new message types to the converter, add cases to `import_msg_type` function. If you have custom messages from ROS, you need to make them callable in your ros workspace. 

| Parameter       |  Info           | Default  |
| ------------- |:-------------:| -----:|
| bootstrap_server      | IP of kafka server | "localhost:9092" |
| topics_filename      | file name of yaml      |  "topics.yaml" |
| update_rate | update publisher rate      |    "10.0" |
| robot_name | first line of yaml |   "UGV" |


#### installation & running
additional libraries required:
```
pip install kafka-python pyyaml
sudo apt install ros-noetic-rospy-message-converter
```

To start publishing kafka topics to ROS:
```console
roslaunch ros_kafka_connector ros_publisher.launch
```

To start publishing ROS topics to kafka:
```
$ roslaunch ros_kafka_connector kafka_publisher.launch
```
