import os
import can
import CameraHandler 

class CanHandler:
    @staticmethod
    def setup_can():
        os.system('sudo ip link set can0 type can bitrate 100000')
        os.system('sudo ifconfig can0 up')
        can0 = can.interface.Bus(channel = 'can0', bustype = 'socketcan')# socketcan_native
        print('CAN SETUP OK')
        return can0
    
    @staticmethod
    def can_down():
        os.system('sudo ifconfig can0 down')
    
class DashboardDataHandler:
    def __init__(self):
        self.canHandler = CanHandler.setup_can()
        self.cameraHandler

    def messageHandler(self, action):
        while True:
            try:
                msg = self.can_handler.recv(10.0)
                if msg is None:
                    print("Timeout occured. No message")
                else:
                    print(msg)
                    RM_speed = int.from_bytes(msg.data, byteorder='little')


            except KeyboardInterrupt:
                CanHandler.can_down()
                break

    def sendDataToDashboard(self):
        return

def do_something(RM_speed, cameraModule):
    print("Current RM speed received is: " + str(RM_speed))
    if (RM_speed > 10):
        print("RM SPEED GREATER THAN THRESHOLD. TAKING PICTURES")
        cameraModule.captureImage()
    else:
        print("RM NOT MOVING. NO PICTURE TAKEN")


if __name__ == "__main__":
    camera_address_list = ['/dev/video0', '/dev/video2']
    dashboardDataHandler = DashboardDataHandler()
    cameraHandler = CameraHandler()

    cameraHandler.initializeAllCameras(camera_address_list=camera_address_list)

    while True:
        try:
            msg = can0.recv(10.0)
            if msg is None:
                print("Timeout occured. No message")
            else:
                print(msg)
                RM_speed = int.from_bytes(msg.data, byteorder='little')
                do_something(RM_speed=RM_speed, cameraModule=cameraModule)

