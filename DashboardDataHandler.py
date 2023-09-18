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
    def __init__(self, RM_speed_threshold):
        self.canHandler = CanHandler.setup_can()
        self.cameraHandler = CameraHandler(RM_speed_threshold)

    def handleMessage(self):
        while True:
            try:
                msg = self.canHandler.recv(10.0)
                if msg is None:
                    print("Timeout occured. No message")
                else:
                    print(msg)
                    RM_speed = int.from_bytes(msg.data, byteorder='little')
                    self.cameraHandler.doSomething(RM_speed)
                    self.sendImageToDashboard()

            except KeyboardInterrupt:
                CanHandler.can_down()
                break

    def sendImageToDashboard(self):
        #os.system('sshpass -f ssh_pass -P 18538 -o StrictHostKeyChecking=np <file_name> hakan@7.tcp.eu.ngrok.io:/home/hakan/images')
        return


if __name__ == "__main__":
    camera_address_list = ['/dev/video0', '/dev/video2']
    dashboardDataHandler = DashboardDataHandler(RM_speed_threshold= 10)
    dashboardDataHandler.handleMessage()
