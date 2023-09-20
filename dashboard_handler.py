import os
import can
from camera_handler import Camera, CameraHandler

class CanHandler:
    @staticmethod
    def setup_can():
        os.system('sudo ip link set can0 type can bitrate 100000')
        os.system('sudo ifconfig can0 up')

        can_channel = 'can0'
        can_bustype = 'socketcan'
        can_filters = [{"can_id": 0x3A0, "can_mask": 0xFFF, "extended": False}]

        can0 = can.interface.Bus(channel=can_channel, bustype=can_bustype, can_filters=can_filters)
        print('CAN SETUP OK')
        return can0
    
    @staticmethod
    def can_down():
        os.system('sudo ifconfig can0 down')
    
class DashboardHandler:
    MESSAGE_TIMEOUT = 10.0

    def __init__(self, ssh_pass_file_name, connection_port, dashboard_server_address, RM_speed_threshold, camera_address_list):
        self.ssh_pass_file_name = ssh_pass_file_name
        self.connection_port = connection_port
        self.dashboard_server_address = dashboard_server_address
        self.canHandler = CanHandler.setup_can()
        self.cameraHandler = CameraHandler(RM_speed_threshold, camera_address_list)

    def handleMessage(self):
        while True:
            try:
                msg = self.canHandler.recv(self.MESSAGE_TIMEOUT)
                if msg is None:
                    print("Timeout occured. No message")
                else:
                    print(msg)
                    RM_speed = int.from_bytes(msg.data, byteorder='little')
                    self.cameraHandler.doSomething(RM_speed)
                    self.sendImageToDashboard()

            except KeyboardInterrupt:
                self.cameraHandler.closeCamera()
                CanHandler.can_down()
                break

    def sendImageToDashboard(self):
        directory_to_upload = self.cameraHandler.getSavingDirectory().name
        saved_images_list = os.listdir(directory_to_upload)
        while len(saved_images_list) > 0:
            saved_image = saved_images_list.pop(0)
            saving_path = os.path.join(directory_to_upload, saved_image)
            os.system('sshpass -f ' + self.ssh_pass_file_name + ' scp -P ' + self.connection_port
                       + ' -o StrictHostKeyChecking=no ' + saving_path + ' ' + self.dashboard_server_address)
            os.remove(saving_path)
        print("UPLOADED OK")

if __name__ == "__main__":
    ssh_pass_file_name = "ssh_pass"
    connection_port = "18538"
    dashboard_server_address = "hakan@7.tcp.eu.ngrok.io:/home/hakan/images"
    camera_address_list = ['/dev/video0', '/dev/video2']
    RM_speed_threshold = 10

    dashboardHandler = DashboardHandler(ssh_pass_file_name=ssh_pass_file_name,
                                        connection_port=connection_port,
                                        dashboard_server_address=dashboard_server_address,
                                        RM_speed_threshold=RM_speed_threshold,
                                        camera_address_list=camera_address_list)
    dashboardHandler.handleMessage()
