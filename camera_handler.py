import cv2
import datetime
from multiprocessing import Process, Pool
import os
import time

class Camera:
    CAMERA_FRAME_WIDTH = 2560
    CAMERA_FRAME_HEIGHT = 1440
    IMAGE_NAMING = "{liftbot_id}_{camera_name}.jpg"

    def __init__(self, liftbot_id, camera_name, camera_address, main_saving_directory):
        self.liftbot_id = liftbot_id
        self.camera_name = camera_name
        self.camera_address = camera_address
        self.main_saving_directory = main_saving_directory
        self.camera_object = cv2.VideoCapture(camera_address, cv2.CAP_V4L)
        print("CAMERA " + self.camera_address + " ADDED OK")
        self.camera_object.set(cv2.CAP_PROP_FRAME_WIDTH, self.CAMERA_FRAME_WIDTH)
        self.camera_object.set(cv2.CAP_PROP_FRAME_HEIGHT, self.CAMERA_FRAME_HEIGHT)
        print("CAMERA " + self.camera_address + " INITIALIZED OK")


    def capture_image(self, timestamp_folder_directory):
        if (self.camera_object.isOpened()):
            ret, frame = self.camera_object.read()
            if not ret:
                print("CANNOT GET CAMERA FRAME")
            print(timestamp_folder_directory)
            image_file_directory = os.path.join(timestamp_folder_directory, self.IMAGE_NAMING.format(liftbot_id=self.liftbot_id, camera_name=self.camera_name))
            print(image_file_directory)
            try:
                cv2.imwrite(image_file_directory, frame)
                print(self.camera_name + ' CAPTURED')
            except:
                print("COULD NOT SAVE IMAGE")

    @staticmethod
    def capture_image_helper(self, image_capturing_params):
        camera_object = image_capturing_params[0]
        latest_image_folder = image_capturing_params[1]
        camera_object.capture_image(latest_image_folder)

    def close_camera(self):
        self.camera_object.release()
        print(self.camera_name + " TURNED OFF")

class CameraHandler:
    camera_object_list = []

    def __init__(self, liftbot_id, images_top_level_directory, rm_speed_threshold, camera_address_list, camera_position_mapping):
        self.liftbot_id = liftbot_id
        self.images_top_level_directory = images_top_level_directory
        self.rm_speed_threshold = rm_speed_threshold
        self.main_saving_directory = self.set_saving_directory()
        self.last_speed_registered = 0
        self.latest_image_folder = []

        camera_id = 0
        for camera_address in camera_address_list:
            camera_object = Camera(liftbot_id=liftbot_id,
                                   camera_name= camera_position_mapping[camera_id], 
                                   camera_address=camera_address,
                                   main_saving_directory=self.main_saving_directory)
            self.camera_object_list.append(camera_object)
            camera_id += 1
    
    def set_saving_directory(self):
        timestamp_saving_folder = datetime.date.today().strftime("%y-%m-%d")
        main_saving_directory = os.path.join(self.images_top_level_directory, timestamp_saving_folder)
        if not os.path.exists(main_saving_directory):
            os.makedirs(main_saving_directory)
        return main_saving_directory
    
    def get_saving_directory(self):
        return self.main_saving_directory

    def do_something(self, rm_speed):
        speed_diff = abs(rm_speed - self.last_speed_registered)

        if (speed_diff > self.rm_speed_threshold and rm_speed < 300000):
            print("RM SPEED DIFFERENCE GREATER THAN THRESHOLD. TAKING IMAGE")
            self.capture_image()

        self.last_speed_registered = rm_speed

    def capture_image(self):
        timestamp_folder_name = datetime.datetime.now().strftime("%H%M%S")
        timestamp_folder_directory = os.path.join(self.main_saving_directory, timestamp_folder_name)
        os.mkdir(timestamp_folder_directory)
        self.latest_image_folder = timestamp_folder_directory
        time.sleep(2)

        with Pool() as p:
            results = p.map(Camera.capture_image_helper, [(camera_object, timestamp_folder_directory) for camera_object in self.camera_object_list])
        
    def get_latest_image_folder(self):
        return self.latest_image_folder

    def close_camera(self):
        for camera_object in self.camera_object_list:
            camera_object.close_camera()



