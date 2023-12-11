import os
import threading
import contextlib
import cv2
import datetime
import depthai as dai
import time

class Camera:
    CAMERA_FRAME_WIDTH = 300
    CAMERA_FRAME_HEIGHT = 300
    IMAGE_NAMING = "{liftbot_id}_{camera_name}_{date}_{timestamp}.jpg"

    def __init__(self, liftbot_id, camera_name, OAK_device_info, OAK_device_pipeline):
        self.liftbot_id = liftbot_id
        self.camera_name = camera_name
        self.OAK_device_info = OAK_device_info
        self.OAK_device_pipeline = OAK_device_pipeline
        
    def process_image(self, context_manager, timestamp_saving_directory, date, timestamp):
        print(dai.Device.getAllAvailableDevices())
        print("I'm here")
        OAK_device = dai.Device(self.OAK_device_info)
        print("init")
        OAK_device.startPipeline(self.OAK_device_pipeline)

        #define an input queue to send capture image event to depthai device
        input_control_queue = OAK_device.getInputQueue(name="control", maxSize=1, blocking=False)
        #define an image output queue with non-blocking behavior for the depthai device
        image_output_queue = OAK_device.getOutputQueue(name="still", maxSize=1, blocking=False)

        #define capture event for depthai_device 
        ctrl = dai.CameraControl()
        ctrl.setCaptureStill(True)
        dai.Device.getOutputQueue

        #send capture event to depthai device to capture 1 image
        input_control_queue.send(ctrl)
        time.sleep(0.5)

        #set specific directory to save image
        image_file_name = self.IMAGE_NAMING.format(liftbot_id=self.liftbot_id,
                                              camera_name=self.camera_name,
                                              date=date,
                                              timestamp=timestamp)
        
        image_file_directory = os.path.join(timestamp_saving_directory, image_file_name)

        if image_output_queue.has():
            frame = image_output_queue.get().getCvFrame()
            cv2.imwrite(image_file_directory, frame)
            print("taken")
        else:
            print("No message")

class CameraHandler:
    
    kewazo_camera_object_list = []

    def __init__(self, liftbot_id, local_images_saving_directory,
                rm_speed_threshold, camera_position_mapping):
        self.liftbot_id = liftbot_id
        self.local_images_saving_directory = local_images_saving_directory
        self.rm_speed_threshold = rm_speed_threshold
        self.last_speed_registered = 0
        self.rm_status = 0

        camera_id = 0
        OAK_device_pipeline = self.set_depthai_common_pipeline()
        all_camera_devices = dai.Device.getAllAvailableDevices()
        print(all_camera_devices)
        print("Check 1")

        if len(all_camera_devices) != 0:
            for OAK_device_info in all_camera_devices:
                kewazo_camera_object = Camera(liftbot_id=liftbot_id,
                                   camera_name=camera_position_mapping[camera_id],
                                   OAK_device_info=OAK_device_info,
                                   OAK_device_pipeline=OAK_device_pipeline)
                self.kewazo_camera_object_list.append(kewazo_camera_object)
                camera_id += 1

    
    def set_depthai_common_pipeline(self):
        #define a pipeline for all connected OAK cameras
        pipeline = dai.Pipeline()

        #define Color Camera Node for getting image frames
        cam_rgb = pipeline.create(dai.node.ColorCamera)
       
        #define xLinkIn node for receiving capture image event from host
        xin_still = pipeline.create(dai.node.XLinkIn)
        xin_still.setStreamName("control")
        xin_still.out.link(cam_rgb.inputControl)

        #define XLinkOut node for sending image frame to host
        xout_still = pipeline.create(dai.node.XLinkOut)
        xout_still.setStreamName("still")
        cam_rgb.still.link(xout_still.input)

        return pipeline

    def set_saving_directory(self, parent_directory, new_folder_name):
        saving_directory = os.path.join(parent_directory, new_folder_name)
        if not os.path.exists(saving_directory):
            os.makedirs(saving_directory)
        return saving_directory

    def execute(self, rm_speed):
        speed_diff = abs(rm_speed - self.last_speed_registered)

        if (speed_diff > self.rm_speed_threshold and abs(rm_speed) < 400000 and self.rm_status == 0):
            self.process_images()
            self.rm_status = 1

        if abs(rm_speed) < 400000 and abs(rm_speed) > 40: #correct value here is 400
            self.last_speed_registered = rm_speed
        else:
            self.rm_status = 0
            self.last_speed_registered = 0

    def process_images(self):
        date = datetime.date.today().strftime("%y%m%d")
        timestamp = datetime.datetime.now().strftime("%H%M%S")
        date_specific_saving_directory = self.set_saving_directory(self.local_images_saving_directory, date)
        timestamp_saving_directory = self.set_saving_directory(date_specific_saving_directory, timestamp)

        with contextlib.ExitStack() as context_manager:
            process_list = []
            for camera_object in self.kewazo_camera_object_list:
                process_capturing_image = threading.Thread(target=camera_object.process_image, args=(context_manager, timestamp_saving_directory, date, timestamp))
                process_capturing_image.start()
                process_list.append(process_capturing_image)
        
            for process in process_list:
                process.join()
