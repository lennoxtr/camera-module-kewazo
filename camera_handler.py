import cv2
from datetime import datetime, date
from multiprocessing import Process
import os

class Camera:
    CAMERA_FRAME_WIDTH = 2560
    CAMERA_FRAME_HEIGHT = 1440

    def __init__(self, camera_id, camera_address, main_saving_directory):
        self.camera_id = camera_id
        self.camera_name = "CAMERA_" + str(camera_id)
        self.camera_address = camera_address
        self.main_saving_directory = main_saving_directory
        self.camera_object = cv2.VideoCapture(camera_address, cv2.CAP_V4L)
        print("CAMERA " + self.camera_address + " ADDED OK")
        self.camera_object.set(cv2.CAP_PROP_FRAME_WIDTH, self.CAMERA_FRAME_WIDTH)
        self.camera_object.set(cv2.CAP_PROP_FRAME_HEIGHT, self.CAMERA_FRAME_HEIGHT)
        print("CAMERA " + self.camera_address + " INITIALIZED OK")

    
    def capture_image(self):
        timestamp_folder_name = datetime.datetime.now().strftime("%H%M%S")
        timestamp_folder_directory = os.path.join(self.main_saving_directory, timestamp_folder_name)
        os.mkdir(timestamp_folder_directory)

        if (self.camera_object.isOpened()):
            ret, frame = self.camera_object.read()
            if not ret:
                print("CANNOT OPEN " + self.camera_name)
            else:
                image_file_directory = os.path.join(timestamp_folder_directory, self.camera_name)
                try:
                    cv2.imwrite(image_file_directory, frame)
                    print(self.camera_name + ' CAPTURED')
                except:
                    print("COULD NOT SAVE IMAGE")

    def capture_video(self, time_between_image_frame):
        return

    def close_camera(self):
        self.camera_object.release()
        print(self.camera_name + " TURNED OFF")

class CameraHandler:
    camera_object_list = []

    def __init__(self, images_top_level_directory, rm_speed_threshold, camera_address_list):
        self.images_top_level_directory = images_top_level_directory
        self.rm_speed_threshold = rm_speed_threshold
        self.main_saving_directory = self.set_saving_directory()
        camera_id = 0
        for camera_address in camera_address_list:
            camera_object = Camera(camera_id=camera_id, 
                                   camera_address=camera_address,
                                   main_saving_directory=self.main_saving_directory)
            self.camera_object_list.append(camera_object)
            camera_id += 1
    
    def set_saving_directory(self):
        timestamp_saving_folder = datetime.date.today().strftime("%y-%m-%d")
        main_saving_directory = os.path.join(self.images_top_level_directory, timestamp_saving_folder)
        os.mkdir(main_saving_directory)
        return main_saving_directory
    
    def get_saving_directory(self):
        return self.main_saving_directory

    def do_something(self, rm_speed):
        print("Current RM speed received is: " + str(rm_speed))
        if (rm_speed < self.rm_speed_threshold):
            print("RM NOT MOVING. NO ACTION")
        else:
            print("RM SPEED GREATER THAN THRESHOLD. TAKING IMAGE")
            self.capture_image()

    def capture_image(self):
        process_list = []
        for camera_object in self.camera_object_list:
            process_capture_image = Process(target=camera_object.capture_image())
            process_capture_image.start()
            process_list.append(process_capture_image)

        for process_capture_image in process_list:
            process_capture_image.join()

    def capture_video(self, time_between_image_frame):
        process_list = []
        for camera_object in self.camera_object_list:
            process_capture_video = Process(target=camera_object.capture_video(time_between_image_frame))
            process_capture_video.start()
            process_list.append(process_capture_video)

        for process_capture_video in process_list:
            process_capture_video.join()

    def close_camera(self):
        for camera_object in self.camera_object_list:
            camera_object.close_camera()



