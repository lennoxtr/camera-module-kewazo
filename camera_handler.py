import cv2
import datetime
from multiprocessing import Process
import os

class Camera:
    CAMERA_FRAME_WIDTH = 2560
    CAMERA_FRAME_HEIGHT = 1440
    IMAGE_NAMING = "{liftbot_id}_{camera_name}_{date}_{timestamp}.jpg"

    def __init__(self, liftbot_id, camera_name, camera_address):
        self.liftbot_id = liftbot_id
        self.camera_name = camera_name
        self.camera_address = camera_address

    def capture_image(self, timestamp_saving_directory, date, timestamp):
        capturing_object = cv2.VideoCapture(self.camera_address, cv2.CAP_V4L)
        capturing_object.set(cv2.CAP_PROP_FRAME_WIDTH, self.CAMERA_FRAME_WIDTH)
        capturing_object.set(cv2.CAP_PROP_FRAME_HEIGHT, self.CAMERA_FRAME_HEIGHT)
        if (capturing_object.isOpened()):
            ret, frame = capturing_object.read()
            if not ret:
                print("CANNOT GET CAMERA FRAME")
            image_directory = os.path.join(timestamp_saving_directory, self.IMAGE_NAMING.format(
                liftbot_id=self.liftbot_id, camera_name=self.camera_name, date=date, timestamp=timestamp))

            try:
                cv2.imwrite(image_directory, frame)
                print(self.camera_name + ' CAPTURED')
            except:
                print("COULD NOT SAVE IMAGE")
            capturing_object.release()

class CameraHandler:
    camera_object_list = []

    def __init__(self, liftbot_id, local_images_saving_directory, rm_speed_threshold, camera_address_list, camera_position_mapping):
        self.liftbot_id = liftbot_id
        self.local_images_saving_directory = local_images_saving_directory
        self.rm_speed_threshold = rm_speed_threshold
        self.last_speed_registered = 0
        self.rm_status = 0

        camera_id = 0
        for camera_address in camera_address_list:
            camera_object = Camera(liftbot_id=liftbot_id,
                                   camera_name=camera_position_mapping[camera_id], 
                                   camera_address=camera_address)
            self.camera_object_list.append(camera_object)
            camera_id += 1
    
    def set_date_specific_saving_directory(self, date):
        date_specific_saving_directory = os.path.join(self.local_images_saving_directory, date)
        if not os.path.exists(date_specific_saving_directory):
            os.makedirs(date_specific_saving_directory)
        return date_specific_saving_directory
    
    def set_timestamp_saving_directory(self, date_specific_saving_directory, timestamp):
        timestamp_saving_directory = os.path.join(date_specific_saving_directory, timestamp)
        if not os.path.exists(timestamp_saving_directory):
            os.makedirs(timestamp_saving_directory)
        return timestamp_saving_directory

    def execute(self, rm_speed):
        
        print("RM speed is ", rm_speed) 
        speed_diff = abs(rm_speed - self.last_speed_registered)

        if (speed_diff > self.rm_speed_threshold and abs(rm_speed) < 400000 and self.rm_status == 0):
            print("RM SPEED DIFFERENCE GREATER THAN THRESHOLD. TAKING IMAGE")
            self.capture_image()
            self.rm_status = 1
        
        if abs(rm_speed) < 400000 and abs(rm_speed) > 400:
            self.last_speed_registered = rm_speed
        else:
            self.rm_status = 0
            self.last_speed_registered = 0

    def capture_image(self):
        date = datetime.date.today().strftime("%y%m%d")
        timestamp = datetime.datetime.now().strftime("%H%M%S")
        date_specific_saving_directory = self.set_date_specific_saving_directory(date=date)
        timestamp_saving_directory = self.set_timestamp_saving_directory(date_specific_saving_directory=date_specific_saving_directory, timestamp=timestamp)

        process_list = []
        for camera_object in self.camera_object_list:
            process_capturing_image = Process(target=camera_object.capture_image, args=(timestamp_saving_directory, date, timestamp))
            process_capturing_image.start()
            process_list.append(process_capturing_image)
        
        for process in process_list:
            process.join()
