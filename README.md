# ROS Package: `ros_kafka_connector` 

This is a ROS package for subscribing or publishing to topics using Kafka. 

Takes a yaml file with {`msg_type`, `ros_topic`, `kafka_topic`}. Can publish the messages between ros and kafka. Put the yaml file in the `config/` folder. 

Example yaml file in: [`topics.yaml`](https://github.com/ethz-asl/ros-kafka-connector/blob/heron/config/topics.yaml)

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
Message types that are added are in the [`utils.py`](https://github.com/ethz-asl/ros-kafka-connector/blob/master/src/utils.py) file.  To add new message types to the converter, add cases to `import_msg_type` function. If you have custom messages from ROS, you need to make them callable in your ros workspace. 

This package does depend on both [`robotnik_msgs`](https://github.com/RobotnikAutomation/robotnik_msgs/tree/ros-devel) and [`heron_msgs`](https://github.com/RobotnikAutomation/heron_msgs). Make sure to add these packages to your catkin ws. 

| Parameter       |  Info           | Default  |
| ------------- |:-------------:| -----:|
| bootstrap_server      | IP of kafka server | "localhost:9092" |
| topics_filename      | file name of yaml      |  "topics.yaml" |
| update_rate | update publisher rate  (ms)  |    "10.0" |
| robot_name | first line of yaml |   "UGV" |


## Installation & running on Ubuntu 20.04
additional libraries can be found in the `requirements.txt` file.

### VPN setup

Download VPN Wireguard:
```bash
sudo apt install wireguard
```

Download the config files for the VpN (sent in email), and copy the folder to `/etc` 
```bash
sudo cp /path/to/configs /etc/wireguard/
```

Set the permissions for the files:
```bash
sudo chmod 600 /etc/wireguard/<folder_name>/*
```

**To start the VPN:**
```bahs
sudo wg-quick up /etc/wireguard/heron/wg_heron_2.conf
```
Change the `wg_heron_2.conf` file to any *but* `wg_heron_8.conf`.

Confirm the VPN is up using:
```bash
ping 10.2.0.8
```

**To stop the VPN:**
```bash
sudo wg-quick down /etc/wireguard/heron/wg_heron_2.conf
```

(optional) I added these to my `~/.bashrc`:
```bash
# heron aliases
alias heron_vpn_up='sudo wg-quick up /etc/wireguard/heron/wg_heron_2.conf'
alias heron_vpn_down='sudo wg-quick down /etc/wireguard/heron/wg_heron_2.conf'
```

### Kafka client setup

1. Connect to the VPN
2. Start publishing data to ROS (ROSBag, simulation)

To start publishing kafka topics to ROS:
```bash
roslaunch ros_kafka_connector ros_publisher.launch
```

To start publishing ROS topics to kafka:
```bash
roslaunch ros_kafka_connector kafka_publisher.launch
```
Images will get compressed using opencv to Base64 format. Use the file `scripts/image_consumer.py` to view the images from the kafka messages. This script doesn't require ROS.

### Kafka GUI setup

Install the kakfa UI through docker.

```bash
docker run -d --name=kafka-ui -p 8080:8080 \
  -e KAFKA_CLUSTERS_0_NAME=local \
  -e KAFKA_CLUSTERS_0_BOOTSTRAPSERVERS=10.2.0.8:9092 \
  -e KAFKA_CLUSTERS_0_PROPERTIES_SECURITY_PROTOCOL=PLAINTEXT \
  provectuslabs/kafka-ui:latest
```

Access the UI at http://localhost:8080


