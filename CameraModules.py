import cv2

class CameraModule:
    CAMERA_FRAME_WIDTH = 2560
    CAMERA_FRAME_HEIGHT = 1440


    camera_address_list = []
    camera_object_list = []

    def addCamera(self, camera_address):
        self.camera_address_list.append(camera_address)        
        print('ADD CAMERA ' + camera_address + ' OK')


    def initializeAllCameras(self):
        for camera_address in self.camera_address_list:
            print('FOUND CAMERA AT ' + camera_address)
            cap = cv2.VideoCapture(camera_address)
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.CAMERA_FRAME_WIDTH)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.CAMERA_FRAME_HEIGHT)
            self.camera_object_list.append(cap)

        print('INITIALIZE CAMERAS OK')
    
    def initializeAllCameras(self, camera_address_list):
        self.camera_address_list = camera_address_list
        print('INITIALIZE CAMERAS OK')


    def captureImage(self):
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

    def captureVideo(self, videtime_between_image_frame):
        return

    def closeCamera(self):
        for camera_object in self.camera_object_list:
            camera_object.release()
        print('CAMERAS TURNED OFF')


