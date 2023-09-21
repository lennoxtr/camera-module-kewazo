from can_bus_handler import CanBusHandler
from camera_handler import CameraHandler
from dashboard_handler import DashboardHandler
    
class CentralHandler:
    MESSAGE_TIMEOUT = 10.0

    def __init__(self, ssh_pass_file_name, connection_port, dashboard_host_name, dashboard_host_ip,
                  dashboard_storage_directory, rm_speed_threshold, camera_address_list, can_id_to_listen):
        
        self.can_handler = CanBusHandler.setup_can(can_id_to_listen)
        self.dashboard_handler = DashboardHandler(ssh_pass_file_name, connection_port, dashboard_host_name,
                                                   dashboard_host_ip, dashboard_storage_directory)
        self.camera_handler = CameraHandler(rm_speed_threshold, camera_address_list)

    def send_image_to_dashboard(self):
        images_local_storage_directory = self.camera_handler.get_saving_directory().name

        if self.dashboard_handler.check_dashboard_connection() == True:
            self.dashboard_handler.send_image_to_dashboard(images_local_storage_directory)
        else:
            print("SAVING PICTURES LOCALLY")  
    
    def handle_can_message(self):
        while True:
            try:
                msg = self.can_handler.recv(self.MESSAGE_TIMEOUT)
                if msg is None:
                    print("Timeout occured. No message")
                else:
                    print(msg)
                    rm_speed = int.from_bytes(msg.data, byteorder='little')
                    self.camera_handler.do_something(rm_speed)
                    self.send_image_to_dashboard()

            except KeyboardInterrupt:
                self.camera_handler.close_camera()
                CanBusHandler.can_down()
                break

if __name__ == "__main__":
    ssh_pass_file_name = "ssh_pass"
    connection_port = "18538"
    dashboard_host_name = "hakan"
    dashboard_host_ip = "7.tcp.eu.ngrok.io"
    dashboard_storage_directory = "/home/hakan/images"
    camera_address_list = ['/dev/video0', '/dev/video2']
    rm_speed_threshold = 10
    can_id_to_listen = 0x3A0

    dashboard_handler = DashboardHandler(ssh_pass_file_name=ssh_pass_file_name,
                                        connection_port=connection_port,
                                        dashboard_host_name=dashboard_host_name,
                                        dashboard_host_ip=dashboard_host_ip,
                                        dashboard_storage_directory=dashboard_storage_directory,
                                        rm_speed_threshold=rm_speed_threshold,
                                        camera_address_list=camera_address_list,
                                        can_id_to_listen=can_id_to_listen)
    dashboard_handler.handle_can_message()
