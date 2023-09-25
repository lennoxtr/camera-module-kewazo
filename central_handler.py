from can_bus_handler import CanBusHandler
from camera_handler import CameraHandler
from dashboard_handler import DashboardHandler
from multiprocessing import Process
    
class CentralHandler:
    MESSAGE_TIMEOUT = 10.0
    IMAGES_TOP_LEVEL_DIRECTORY = "./images"

    def __init__(self,liftbot_id, ssh_pass_file_name, connection_port, dashboard_host_name, dashboard_host_ip,
                  dashboard_storage_directory, rm_speed_threshold, camera_address_list, camera_position_mapping, can_id_list_to_listen):
        
        self.liftbot_id = liftbot_id
        self.can_handler = CanBusHandler.setup_can(can_id_list_to_listen=can_id_list_to_listen)
        self.dashboard_handler = DashboardHandler(ssh_pass_file_name=ssh_pass_file_name,
                                                  connection_port=connection_port,
                                                  dashboard_host_name=dashboard_host_name,
                                                  dashboard_host_ip=dashboard_host_ip,
                                                  dashboard_storage_directory=dashboard_storage_directory, 
                                                  images_top_level_directory=self.IMAGES_TOP_LEVEL_DIRECTORY)
        self.camera_handler = CameraHandler(liftbot_id=liftbot_id,
                                            images_top_level_directory=self.IMAGES_TOP_LEVEL_DIRECTORY,
                                            rm_speed_threshold=rm_speed_threshold,
                                            camera_address_list=camera_address_list,
                                            camera_position_mapping=camera_position_mapping)

    def send_image_to_dashboard(self):
        while self.dashboard_handler.check_dashboard_connection() == True:
            self.dashboard_handler.send_image_to_dashboard()
        else:
            print("SAVING IMAGES LOCALLY ONLY")  
    
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
            except KeyboardInterrupt:
                self.camera_handler.close_camera()
                CanBusHandler.can_down()
                break
    
    def start(self):
        process_uploading_images = Process(target=self.send_image_to_dashboard())
        process_handling_can_messages = Process(target=self.handle_can_message())

        process_uploading_images.start()
        process_handling_can_messages.start()

        process_uploading_images.join()
        process_handling_can_messages.join()

if __name__ == "__main__":
    liftbot_id = "LB1"
    ssh_pass_file_name = "ssh_pass"
    connection_port = "18538"
    dashboard_host_name = "hakan"
    dashboard_host_ip = "7.tcp.eu.ngrok.io"
    dashboard_storage_directory = "/home/hakan/images"
    camera_address_list = ['/dev/video0', '/dev/video2'] # maximum is 4
    camera_position_mapping = {0: "left", 1: "right"} # 0: left, 1: right, 2: top, 3: bottom
    rm_speed_threshold = 10
    can_id_list_to_listen = [0x3A0]

    central_handler = CentralHandler(liftbot_id=liftbot_id,
                                     ssh_pass_file_name=ssh_pass_file_name,
                                     connection_port=connection_port,
                                     dashboard_host_name=dashboard_host_name,
                                     dashboard_host_ip=dashboard_host_ip,
                                     dashboard_storage_directory=dashboard_storage_directory,
                                     rm_speed_threshold=rm_speed_threshold,
                                     camera_address_list=camera_address_list,
                                     camera_position_mapping=camera_position_mapping,
                                     can_id_list_to_listen=can_id_list_to_listen)
    central_handler.start()
