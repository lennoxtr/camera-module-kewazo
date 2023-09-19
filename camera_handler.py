import cv2
from datetime import datetime
from multiprocessing import Process
import os

class Camera:
    CAMERA_FRAME_WIDTH = 2560
    CAMERA_FRAME_HEIGHT = 1440

    def __init__(self, camera_id, camera_address):
        self.camera_id = camera_id
        self.camera_name = "CAMERA_" + str(camera_id)
        self.camera_address = camera_address
        self.camera_object = cv2.VideoCapture(camera_address)
        print("CAMERA " + self.camera_address + " ADDED OK")
        self.camera_object.set(cv2.CAP_PROP_FRAME_WIDTH, self.CAMERA_FRAME_WIDTH)
        self.camera_object.set(cv2.CAP_PROP_FRAME_HEIGHT, self.CAMERA_FRAME_HEIGHT)
        print("CAMERA " + self.camera_address + " INITIALIZED OK")

    
    def captureImage(self):
        if (self.camera_object.isOpened()):
            ret, frame = self.camera_object.read()
            if not ret:
                print("CANNOT OPEN " + self.camera_name)
            else:
                image_timestamp = datetime.now().strftime('%Y-%m-%d_%H.%M.%S')
                file_name = self.camera_name + "_" + image_timestamp + ".jpg"
                cv2.imwrite(file_name, frame)
                try:
                    os.system('sshpass -f ssh_pass scp -P 18538 -o StrictHostKeyChecking=no ' + file_name + ' hakan@7.tcp.eu.ngrok.io:/home/hakan/images')
                    print(self.camera_name + ' CAPTURED')
                    print(file_name + " UPLOADED")

                except:
                    print("COULD NOT UPLOAD")
    
    def captureVideo(self, time_between_image_frame):
        return

    def closeCamera(self):
        self.camera_object.release()
        print(self.camera_name + " TURNED OFF")

class CameraHandler:
    camera_object_list = []

    def __init__(self, RM_speed_threshold, camera_address_list):
        self.RM_speed_threshold = RM_speed_threshold

        camera_id = 0
        for camera_address in camera_address_list:
            camera_object = Camera(camera_id=camera_id, camera_address=camera_address)
            self.camera_object_list.append(camera_object)
            camera_id += 1
    
    def doSomething(self, RM_speed):
        print("Current RM speed received is: " + str(RM_speed))
        if (RM_speed < self.RM_speed_threshold):
            print("RM NOT MOVING. NO ACTION")
        else:
            print("RM SPEED GREATER THAN THRESHOLD. TAKING PICTURES")
            self.captureImage()

    def captureImage(self):
        process_list = []
        for camera_object in self.camera_object_list:
            process_capture_image = Process(target=camera_object.captureImage())
            process_capture_image.start()
            process_list.append(process_capture_image)

        for process_capture_image in process_list:
            process_capture_image.join()

    def captureVideo(self, time_between_image_frame):
        process_list = []
        for camera_object in self.camera_object_list:
            process_capture_video = Process(target=camera_object.captureVideo(time_between_image_frame))
            process_capture_video.start()
            process_list.append(process_capture_video)

        for process_capture_video in process_list:
            process_capture_video.join()

    def closeCamera(self):
        for camera_object in self.camera_object_list:
            camera_object.closeCamera()


