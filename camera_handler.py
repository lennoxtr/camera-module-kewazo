import os
from multiprocessing import Process
import datetime
import cv2
import depthai as dai
import threading
import contextlib
import time

class Camera:
    def __init__(self, liftbot_id, camera_name, depthai_device):
        self.liftbot_id = liftbot_id
        self.camera_name = camera_name
        self.depthai_device = depthai_device

    def capture_image(self, stack, image_frame_queue):
        self.depthai_device = stack.enter_context(self.depthai_device)
        self.depthai_device.startPipeline()
        output_queue = self.depthai_device.getOutputQueue(name="mjpeg", maxSize=1, blocking=False)
        image_frame = output_queue.get()
        frame = cv2.imdecode(image_frame.getData(), cv2.IMREAD_COLOR)
        image_frame_queue.put(frame)

class CameraHandler:
    CAMERA_FRAME_WIDTH = 300
    CAMERA_FRAME_HEIGHT = 300
    IMAGE_NAMING = "{liftbot_id}_{camera_name}_{date}_{timestamp}.jpg"
    
    camera_object_list = []

    def __init__(self, liftbot_id, local_images_saving_directory,
                rm_speed_threshold, camera_position_mapping):
        self.liftbot_id = liftbot_id
        self.local_images_saving_directory = local_images_saving_directory
        self.rm_speed_threshold = rm_speed_threshold
        self.last_speed_registered = 0
        self.rm_status = 0

        camera_id = 0
        depthai_device_pipeline = self.set_depthai_device_pipeline()
        all_camera_devices = dai.Device.getAllAvailableDevices()

        if len(all_camera_devices) != 0:
            for device in all_camera_devices:
                MxID = device.getMxId()
                device_info = dai.DeviceInfo(MxID)
                camera_object = Camera(liftbot_id=liftbot_id,
                                   camera_name=camera_position_mapping[camera_id],
                                   depthai_camera = dai.Device(depthai_device_pipeline, device_info))
                self.camera_object_list.append(camera_object)
                camera_id += 1

    
    def set_depthai_device_pipeline(self):
        #defining a pipeline for all connected OAK cameras
        pipeline = dai.Pipeline()
        cam_rgb = pipeline.create(dai.node.ColorCamera)
        cam_rgb.setPreviewSize(Camera.CAMERA_FRAME_WIDTH, Camera.CAMERA_FRAME_HEIGHT)
        cam_rgb.setBoardSocket(dai.CameraBoardSocket.RGB)
        cam_rgb.setResolution(dai.ColorCameraProperties.SensorResolution.THE_1080_P)

        xout_rgb = pipeline.create(dai.node.XLinkOut)
        xout_rgb.setStreamName("rgb")

        return pipeline

    def set_saving_directory(self, parent_directory, new_folder_name):
        saving_directory = os.path.join(parent_directory, new_folder_name)
        if not os.path.exists(saving_directory):
            os.makedirs(saving_directory)
        return saving_directory

    def execute(self, rm_speed):

        #print("RM speed is ", rm_speed)
        speed_diff = abs(rm_speed - self.last_speed_registered)

        if (speed_diff > self.rm_speed_threshold and abs(rm_speed) < 400000 and self.rm_status == 0):
            #print("RM SPEED DIFFERENCE GREATER THAN THRESHOLD. TAKING IMAGE")
            self.capture_images()
            self.rm_status = 1

        if abs(rm_speed) < 400000 and abs(rm_speed) > 400:
            self.last_speed_registered = rm_speed
        else:
            self.rm_status = 0
            self.last_speed_registered = 0

    def capture_images(self):
        with contextlib.ExitStack() as stack:
            pass



        date = datetime.date.today().strftime("%y%m%d")
        timestamp = datetime.datetime.now().strftime("%H%M%S")
        date_specific_saving_directory = self.set_saving_directory(self.local_images_saving_directory, date)
        timestamp_saving_directory = self.set_saving_directory(date_specific_saving_directory, timestamp)

        process_list = []
        for camera_object in self.camera_object_list:
            process_capturing_image = Process(target=camera_object.capture_image, args=(timestamp_saving_directory, date, timestamp))
            process_capturing_image.start()
            process_list.append(process_capturing_image)
        
        for process in process_list:
            process.join()
