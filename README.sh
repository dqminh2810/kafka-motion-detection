# Motion detection 
Project allowing to detect motion via pi camera then notify and send video recording by using kafka

### Requirements
#### Software
- Python v3.8
- Node v20.4
- Docker v24.0.4
- docker-compose v1.29.2
- Raspbian 32 bit support picamera module
#### Hardware
- Raspberry Pi 4B 
- Integrated Pi camera 

### Setup development environment
#### Test pi camera available
`vcgencmd get_camera`

`raspistill -t 0`

#### Kafka broker
`docker-compose up -d`

`docker exec kafka kafka-topics.sh --create --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1 --topic motion_video `

#### Kafka producer
- Open new terminal 
`cd producer`

`pip install -r requirement.txt`

`python main.py`

#### Kafka consumer
- Open new terminal
`cd consumer`

`npm i`

`npm run`
