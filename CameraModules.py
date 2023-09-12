import cv2

class CameraModule:
    CAMERA_FRAME_WIDTH = 2560
    CAMERA_FRAME_HEIGHT = 1440


    camera_address_list = []
    camera_object_list = []

    def addCamera(self, camera_address):
        self.camera_address_list.append(camera_address)

    def initializeAllCameras(self):
        for camera_address in self.camera_address_list:
            cap = cv2.VideoCapture(camera_address)
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.CAMERA_FRAME_WIDTH)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.CAMERA_FRAME_HEIGHT)
            self.camera_object_list.append(cap)  

    def captureImage(self):
        camera_id = 0
        for camera_object in self.camera_object_list:
            if (camera_object.isOpened()):
                ret, frame = camera_object.read()
                if not ret:
                    print("Cannot open camera!")
                else:
                    cv2.imwrite('Camera ' + camera_id, frame)
            camera_id += 1

    def captureVideo(self, videtime_between_image_frame):
        return

    def closeCamera(self):
        for camera_object in self.camera_object_list:
            camera_object.release()

