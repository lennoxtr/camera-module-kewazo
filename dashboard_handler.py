import os
import can
from camera_handler import Camera, CameraHandler

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
    
class DashboardHandler:
    def __init__(self, ssh_pass_file, dashboard_server_address, RM_speed_threshold, camera_address_list):
        self.ssh_pass_file = ssh_pass_file
        self.dashboard_server_address = dashboard_server_address
        self.canHandler = CanHandler.setup_can()
        self.cameraHandler = CameraHandler(RM_speed_threshold, camera_address_list)

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
    ssh_pass_file = "ssh_pass"
    dashboard_server_address = "hakan@7.tcp.eu.ngrok.io"
    camera_address_list = ['/dev/video0', '/dev/video2']
    RM_speed_threshold = 10

    dashboardHandler = DashboardHandler(ssh_pass_file= ssh_pass_file,
                                                dashboard_server_address= dashboard_server_address,
                                                RM_speed_threshold= RM_speed_threshold,
                                                camera_address_list= camera_address_list)
    dashboardHandler.handleMessage()
