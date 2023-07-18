import io
import os
import time
from picamera import PiCamera
import numpy as np
from kafka import KafkaProducer

widthH = 2592  # too slow for motion check, only use for the save sequence
heightH = 1944
width = 1440  # use lower resolution for motion check
height = 1080

# how much must the color value (0-255) change to be considered a change
threshold = 30
# % change  # how many pixels must change to begin a save sequence
minPixelsChanged = width * height * 2 / 100
print("minPixelsChanged=", minPixelsChanged)  # debug

print('Creating in-memory stream')
stream = io.BytesIO()
step = 1  # use this to toggle where the image gets saved
numImages = 1  # count number of images processed
captureCount = 0  # flag used to begin a sequence capture

chunkSize = 1000000

def filenames():
    frame = 0
    fileName = time.strftime("NAS/%Y%m%d/%Y%m%d-%H%M%S-", time.localtime())
    while frame < 20:
        yield '%s%02d.h264' % (fileName, frame)
        frame += 1

def read_in_chunks(file_object, chunkSize):
    chunks = []
    index = 0
    while True:
        data = file_object.read(chunkSize)
        if not data:
            break
        yield {
            "index": index,
            "data": data
        }
        index+=1

def publish_video(video_file):
    print(video_file)
    kafka_topic = "motion_video"
    kafka_bootstrap_servers = ['localhost:29092']
    time.sleep(0.5)
    # Start up producer
    producer = KafkaProducer(bootstrap_servers=kafka_bootstrap_servers, api_version=(2, 2, 0))
    print('Kafka --- ok producer')

    print('Kafka --- publishing video...')
    file = open(video_file, 'rb')
    for v in read_in_chunks(file, chunkSize):
        key = v["index"]
        value = v["data"]
        producer.send(kafka_topic, key=str(key).encode(), value=value)
        print('Kafka --- sended')
    producer.send(kafka_topic, key=b'end', value=str(os.path.basename(video_file)).encode())
    producer.flush()
    print('Kafka --- sended end')
    print('publish complete')

# begin monitoring
with PiCamera() as camera:
    time.sleep(1)  # let camera warm up
    try:
        while threshold > 0:
            # use a smaller resolution for higher speed compare
            camera.resolution = (1440, 1080)

            print('Capture ', numImages)
            if step == 1:
                stream.seek(0)
                # use video port for high speed
                camera.capture(stream, 'rgba', True)
                data1 = np.fromstring(stream.getvalue(), dtype=np.uint8)
                step = 2
            else:
                stream.seek(0)
                camera.capture(stream, 'rgba', True)
                data2 = np.fromstring(stream.getvalue(), dtype=np.uint8)
                step = 1
            numImages = numImages + 1

            if numImages > 4:  # ignore first few images because if the camera is not quite ready it will register as motion right away
                # look for motion unless we are in save mode
                if captureCount <= 0:
                    print("Compare")
                    # not capturing, test for motion (very simplistic, but works good enough for my purposes)
                    # get difference between 2 successive images
                    data3 = np.abs(data1 - data2)
                    # there are 4 times the number of pixels due to rgba
                    numTriggers = np.count_nonzero(
                        data3 > threshold) / 4 / threshold

                    print("Trigger cnt=", numTriggers)

                    if numTriggers > minPixelsChanged:
                        captureCount = 1  # capture ? sequences in a row
                        # make sure directory exists for today
                        # unfortunately this saves as UTC time instead of local, will fix it later sorry
                        d = time.strftime("NAS/%Y%m%d")
                        if not os.path.exists(d):
                            os.makedirs(d)

                if captureCount > 0:
                    # in capture mode, save an image in hi res
                    camera.resolution = (width, height)
                    # once again, UTC time instead of local time
                    dtFileStr = time.strftime("NAS/%Y%m%d/%Y%m%d-%H%M%S-00.h264", time.localtime())
                    print("Saving sequence ", dtFileStr)
                    # record video to NAS directory
                    camera.start_preview()
                    camera.start_recording(dtFileStr)
                    time.sleep(5)
                    camera.stop_recording()
                    camera.stop_preview()
                    # publish video to kafka broker
                    publish_video(dtFileStr)
                    # remove video after publish
                    os.remove(dtFileStr)
                    captureCount = captureCount-1

    finally:
        camera.close()
        print('Program Terminated')
