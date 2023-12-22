"""
This module helps controlling multiple Camera objects at the same time with parallel processing, 
initializing Camera objects with specified Liftbot information, setting pipelines for
taking and receiving images from DepthAI cameras, and saving the received image to the host device.

It wraps DepthAI's Device object in the Kewazo Camera object so that each camera object includes
information specific to Liftbot, such as the Liftbot ID, or camera placement on the Transportation
Platform (TP).
It allows the user to set up either a common operation pipeline for all cameras, or different
pipeline for each camera if need. 
It allows all Camera objects to be controlled from a single class, the CameraHandler. The
CameraHandler class facilitates multiprocess operation of all Camera objects via Thread.
Camerahandler also sets a common saving directory for all cameras. After receiving the RM's
speed information from the CAN layer, it determines whether the Camera objects should remain idle,
or take pictures.

The structure of folders to save images is as follows:
.
|
|_ Top directory to save image on host device (Example: /images)
        |
        |_ Date specific saving folder (Example: /230717, denoting 17 July 2023)
                |
                |_ Timestamp saving folder (Example: /130450, denoting 1:04:50 PM)
                        |
                        |_ Image 1
                        |
                        |_ Image 2
                        |
                        |_ ...

Typical usage example:

    kewazo_camera_object = Camera(liftbot_id, camera_name, oak_device_info, oak_device_pipeline)
    kewazo_camera_object.process_image(context_manager, timestamp_saving_directory, date, timestamp)

    camera_handler = CameraHandler(liftbot_id, local_images_saving_directory,
                rm_speed_threshold, camera_position_mapping)
    camera_handler.execute(rm_speed)

DepthAI's API documentation and tutorial can be found at:
https://docs.luxonis.com/projects/api/en/latest/ 

"""

import os
import threading
import contextlib
import datetime
import time
import cv2
import numpy as np
from numpy.linalg import norm
import logging
import depthai as dai
import shutil

class Camera:
    """
    A class that initialize DepthAI's Device object with a specified pipeline. It 
    wraps DepthAI's Device object in the Kewazo Camera object so that each
    camera object includes information specific to Liftbot, such as the Liftbot ID, or camera
    placement on the Transportation Platform (TP).
    
    """
    IMAGE_NAMING = "{liftbot_id}_{camera_name}_{date}_{timestamp}.jpg"
    BRIGHTNESS_LOW = 70 # Threshold to determine whether image is too dark
    BRIGHTNESS_HIGH = 90 # Threshold to determine whether image is too bright
    GAMMA_ADJUSTMENT_STEP = 0.01 # Exposure step to adjust camera exposure

    def __init__(self, liftbot_id, camera_name, oak_device_info, oak_device_pipeline):
        """
        Initialize the camera object with information specific to Liftbot, such as
        Liftbot ID and camera placement on TP.

        Args:
            liftbot_id (string) : an ID to differentiate between multiple Liftbots 
                                to know which Liftbot the camera belongs to
            camera_name (string) : a name that suggests the placement of the camera on TP.
                                Limited to 'left' or 'right'.
            oak_device_info (dai.DeviceInfo) : a DepthAI's DeviceInfo object to initialize
                                                DepthAI's Device object
            oak_device_pipeline (dai.Pipeline) : a DepthAI's Pipeline object to control
                                                how DepthAI camera take pictures, the resolution
                                                of pictures, image detection, ... and how 
                                                it sends pictures to host device

        """
        self.liftbot_id = liftbot_id
        self.camera_name = camera_name
        self.oak_device_info = oak_device_info
        self.oak_device_pipeline = oak_device_pipeline
        self.gamma = 1.0 # Default of DepthAI camera
        self.brightness_control = 0 # Default of DepthAI camera

    def process_image(self, context_manager, timestamp_saving_directory, date, timestamp):
        """
        Initialize DepthAI's Device object from DeviceInfo object, generate input queue to receive
        image capture command and output queue to send image to host device. Save image to
        host device in a specified folder. 

        Args:
            context_manager (contextlib.ExitStack) : a context manager object to enter the
                                                context of the initialized Device object and
                                                close it cleanly after use. 
            timestamp_saving_directory (string) : the directory to save images
            date (string) : the date the image was captured, in the format YYMMDD
            timestamp (string) : the time the image was captured, in the format HHMMSS

        """

        # Initialize Device object with a specified pipeline
        try:
            oak_device : dai.Device = context_manager.enter_context(dai.Device(self.oak_device_info))
            logging.info("Camera initialized")
        except Exception:
            logging.exception("Error when initialization camera ", self.camera_name)
        try:
            oak_device.startPipeline(self.oak_device_pipeline)
            logging.info("Start pipeline on camera ", self.camera_name)
        except Exception:
            logging.exception("Cannot start pipeline on camera ", self.camera_name)

        # Define an input queue to send capture image event to Depthai device
        # maxSize=1 and blocking=False means that only the latest capture event is in the queue
        # This is to prevent the camera from receving too many capture events within a short period
        # Which may happen when the RM moves a lot in short period
        input_control_queue = oak_device.getInputQueue(name="control", maxSize=1, blocking=False)

        # Define an image output queue with non-blocking behavior for the Depthai device
        # maxSize=1 and blocking=False means that only the latest captured is in the output queue
        image_output_queue = oak_device.getOutputQueue(name="still", maxSize=1, blocking=False)

        # Define capture event for depthai_device
        ctrl = dai.CameraControl()
        ctrl.setBrightness(self.brightness_control)
        ctrl.setCaptureStill(True)

        # Send capture event to depthai device to capture 1 image
        input_control_queue.send(ctrl)
        logging.info("Send capture command to camera ", self.camera_name)

        # Time delay to make sure that the capture event is received
        time.sleep(0.5)

        # Set specific directory to save image
        image_file_name = self.IMAGE_NAMING.format(liftbot_id=self.liftbot_id,
                                              camera_name=self.camera_name,
                                              date=date,
                                              timestamp=timestamp)

        image_file_directory = os.path.join(timestamp_saving_directory, image_file_name)

        if image_output_queue.has():
            frame = image_output_queue.get().getCvFrame()

            # Analyze brightness of image to adjust camera exposure for
            # different lighting environments.
            #
            # Brightness is calculated using geometric mean of R, G, B
            # channels of a picture
            
            brightness = np.average(norm(frame, axis=2)) / np.sqrt(3)


            # If brightness is too great or too low, gamma correction
            # would return weird images.
            #
            # The idea here is that if brightness is too great or too
            # low, the images won't be sent. Instead, the brightness of
            # the next image taken will be increased or decreased

            if brightness > 130 or brightness < 40:
                if brightness > 130:
                    self.brightness_control -= 1
                    try:
                        shutil.rmtree(timestamp_saving_directory)
                    except Exception:
                        return
                    return
                elif brightness < 40:
                    self.brightness_control += 1
                    try:
                        shutil.rmtree(timestamp_saving_directory)
                    except Exception:
                        return
                    return
                
            counter = 0 # Counter to prevent infinite loop
            while (counter < 10) and (brightness > self.BRIGHTNESS_HIGH or brightness < self.BRIGHTNESS_LOW):
                # Adjusting gamma values
                if brightness > self.BRIGHTNESS_HIGH:
                    logging.warning(self.camera_name,
                                " BRIGHTNESS TOO HIGH. INCREASING GAMMA")
                    self.gamma += self.GAMMA_ADJUSTMENT_STEP
                    frame = self.gamma_correction(frame, self.gamma)
                elif brightness < self.BRIGHTNESS_LOW:
                    logging.warning(self.camera_name,
                                " BRIGHTNESS TOO LOW. DECREASING GAMMA")
                    self.gamma -= self.GAMMA_ADJUSTMENT_STEP
                    frame = self.gamma_correction(frame, self.gamma)
                brightness = np.average(norm(frame, axis=2)) / np.sqrt(3)
                counter += 1
            
            logging.info(self.camera_name,
                                " BRIGHTNESS WITHIN THRESHOLD")
            
            if cv2.imwrite(image_file_directory, frame):
                logging.info(self.camera_name, " SAVED")
            else:
                logging.critical(self.camera_name, " NOT SAVED")
        else:
            return
    
    def gamma_correction(self, frame, gamma):
        '''
        Perform gamma correction so the image doesn't look too bright
        or dark in different environment
        '''
        gamma_table = [np.power(x / 255.0, gamma) * 255.0 for x in range(256)]
        gamma_table = np.round(np.array(gamma_table)).astype(np.uint8)
        return cv2.LUT(frame, gamma_table)

class CameraHandler:
    """
    A class that helps intialize and control mutiple camera objects at the same time.
    It also determines what the cameras should do from the current RM's speed.

    """
    kewazo_camera_object_list = []

    def __init__(self, liftbot_id, local_images_saving_directory,
                rm_speed_threshold, camera_position_mapping):
        """
        Initialize multiple Camera objects with the appropriate DeviceInfo, Pipeline,
        and information about Liftbot. 

        NOTE: Only the Camera object gets initialized, not the DepthAI Device object.
        The Device object will only get initialized when the cameras need to capture 
        images. This is because initializing the Device object too soon may cause 
        "Device already in use" error.

        Args:
            liftbot_id (string) : the ID to differentiate between multiple Liftbots 
                                to know which Liftbot the camera belongs to 
            local_images_saving_directory (string) : the top directory on host device that
                                                contain all folders of captured images
            rm_speed_threshold (int) : the speed threshold to determine whether the RM is
                                    actually moving. This is implemented as the RM_speed
                                    retrieved from CAN sometimes show very high value
                                    like 400000 when the RM is not moving. It is an
                                    absolute value
            camera_position_mapping (dictionary) : the dictionary to map camera's id to its
                                                position on the TP. Only holds 2 values to
                                                map to 'left' or 'right'

        """

        self.liftbot_id = liftbot_id
        self.local_images_saving_directory = local_images_saving_directory
        self.rm_speed_threshold = rm_speed_threshold
        self.last_speed_registered = 0 # Last recored RM speed, initialized to 0
        self.rm_status = 0 # Current state of RM. 1 is moving, 0 is stationary

        camera_id = 0
        # Generate a common Pipeline for all Depth AI camera.
        oak_device_pipeline = self.set_depthai_common_pipeline()

        # Get all available OAK devices. Note that available means that
        # the device is connect and not in use.
        all_camera_devices = dai.Device.getAllAvailableDevices()

        # Intialize Camera object with the common pipeline. If a camera does not use
        # the common pipeline, it must be initialized separately.

        if len(all_camera_devices) != 0:
            for oak_device_info in all_camera_devices:
                kewazo_camera_object = Camera(liftbot_id=liftbot_id,
                                   camera_name=camera_position_mapping[camera_id],
                                   oak_device_info=oak_device_info,
                                   oak_device_pipeline=oak_device_pipeline)
                self.kewazo_camera_object_list.append(kewazo_camera_object)
                camera_id += 1

    def set_depthai_common_pipeline(self):
        """
        Generate a common Pipeline for all DepthAI Device.

        Returns:
            dai.Pipeline : a Pipeline object that contains information about
                        how the camera should capture image, when it
                        captures image, and how it can send the captured
                        image to host device.

        """

        # Define an empty pipeline for all available OAK cameras
        pipeline = dai.Pipeline()

        # Define a Color Camera Node for getting image frames from camera
        cam_rgb = pipeline.create(dai.node.ColorCamera)
        cam_rgb.setFps(10) # Lower FPS to increase exposure range

        # Define xLinkIn node for receiving capture image event from host device
        xin_still = pipeline.create(dai.node.XLinkIn)
        xin_still.setStreamName("control")
        xin_still.out.link(cam_rgb.inputControl)

        # Define XLinkOut node for sending image frame to host device
        xout_still = pipeline.create(dai.node.XLinkOut)
        xout_still.setStreamName("still")
        cam_rgb.still.link(xout_still.input)

        return pipeline

    def set_saving_directory(self, parent_directory, new_folder_name):
        """
        Generate a new saving directory based on the parent directory and
        the new folder's name. Do nothing if directory already exists

        """
        saving_directory = os.path.join(parent_directory, new_folder_name)
        try:
            if not os.path.exists(saving_directory):
                os.makedirs(saving_directory)
        except Exception:
            logging.critical("No permission to create folder")
        return saving_directory

    def execute(self, rm_speed):
        """
        Determine what the cameras should do based on the speed threshold, the current RM status,
        and the difference between the current RM speed and the last recorded RM speed.
 
        """
        speed_diff = abs(rm_speed - self.last_speed_registered)

        # There are 3 conditions that must be satisfied in order for the cameras to capture images:
        #
        # 1. The RM must not be moving (rm_status=0).
        # 2. The current RM Speed is normal (abs(rm_speed) < 400000). This is implemented due to
        # the fact that even when the RM is stationary, the recorded speed sent via CAN Bus can
        #  sometimes be > 400000 or < -400000.
        # 3. The absolute difference between the current RM speed and the last recorded RM speed
        # is greater than the speed threshold. This is implemented as the camera should only
        # capture images when the RM start moving (when the speed difference is large). When
        # the RM is moving, although there will still be difference between the speed recorded,
        # such difference is not very large.
        #
        # Upon satisfying all 3 conditions, a command will be send to all cameras to capture images.
        # The RM status will also be updated to 1 (moving).

        if (speed_diff > self.rm_speed_threshold and abs(rm_speed) < 210
            and self.rm_status == 0 and speed_diff < 100):
            self.process_images()
            logging.info("Taking photos")
            self.rm_status = 1

        # If the RM speed is normal (abs(rm_speed) < 400000 and abs(rm_speed) < 400000 > 40), the
        # current RM speed will be recorded as the last RM speed to faciliate comparison
        # with the next recorded RM speed.

        if abs(rm_speed) < 210 and abs(rm_speed) > 150: #correct value here is 400
            self.last_speed_registered = rm_speed

        # If the RM speed is not normal, the RM will be determined to be stationary.
        # Its status will be updated to 0 (stationary).
        # The last_speed_registered will also be 0.

        else:
            self.rm_status = 0
            self.last_speed_registered = 0

    def process_images(self):
        """
        Generate appropriate saving directory for images based on the current date and time.
        Use thread-based parallelism to command all Camera objects to capture images. 

        """

        # Dtermine the current date and time
        # Date is in the format YYMMDD
        # Time is in the format HHMMSS
        date = datetime.date.today().strftime("%y%m%d")
        timestamp = datetime.datetime.now().strftime("%H%M%S")

        # Generate date and timestamp saving directories
        date_specific_saving_directory = self.set_saving_directory(
            self.local_images_saving_directory, date)
        timestamp_saving_directory = self.set_saving_directory(
            date_specific_saving_directory, timestamp)

        with contextlib.ExitStack() as context_manager:
            process_list = []
            for camera_object in self.kewazo_camera_object_list:
                # NOTE: Process-based parallelism does not work. Only Thread was
                # found to work properly
                process_capturing_image = threading.Thread(target=camera_object.process_image,
                                                           args=(context_manager,
                                                                timestamp_saving_directory,
                                                                date,
                                                                timestamp))
                process_capturing_image.start()
                process_list.append(process_capturing_image)
            for process in process_list:
                process.join()
