import cv2
from multiprocessing import Process

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
                cv2.imwrite(self.camera_name + '.jpg', frame)
                print(self.camera_name + ' CAPTURED')
    
    def captureVideo(self, time_between_image_frame):
        return

    def closeCamera(self):
        self.camera_object.release()
        print(self.camera_name + " TURNED OFF")


class CameraModule:
    camera_object_list = []

    def initializeCameras(self, camera_address_list):
        camera_id = 0
        for camera_address in camera_address_list:
            camera_object = Camera(camera_id=camera_id, camera_address=camera_address)
            self.camera_object_list.append(camera_object)
            camera_id += 1

    def captureImage(self):
        process_list = []
        for camera_object in self.camera_object_list:
            process_capture_image = Process(target=camera_object.captureImage())
            process_capture_image.start()
            process_list.append(process_capture_image)

        for process_capture_image in process_list:
            process_capture_image.join()

        '''
        camera_id = 0
        for camera_object in self.camera_object_list:
            if (camera_object.isOpened()):
                camera_name = 'CAMERA_' + str(camera_id)
                ret, frame = camera_object.read()
                if not ret:
                    print("CANNOT OPEN " + camera_name)
                else:
                    cv2.imwrite(camera_name + '.jpg', frame)
                    print(camera_name + ' CAPTURED')
            camera_id += 1
        '''

    def captureVideo(self, time_between_image_frame):
        return

    def closeCamera(self):
        for camera_object in self.camera_object_list:
            camera_object.closeCamera()



