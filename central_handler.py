from multiprocessing import Process
from can_bus_handler import CanBusHandler
from camera_handler import CameraHandler
from dashboard_handler import DashboardHandler

class CentralHandler:
    LOCAL_IMAGES_SAVING_DIRECTORY = "./images"

    def __init__(self,liftbot_id, ssh_pass_file_name, connection_port, dashboard_host_name,
                 dashboard_host_ip, dashboard_images_saving_directory, rm_speed_threshold,
                 camera_address_list, camera_position_mapping, can_id_list_to_listen):
        self.liftbot_id = liftbot_id
        self.can_handler = CanBusHandler.setup_can(can_id_list_to_listen=can_id_list_to_listen)
        self.dashboard_handler = DashboardHandler(ssh_pass_file_name=ssh_pass_file_name,
                                                  connection_port=connection_port,
                                                  dashboard_host_name=dashboard_host_name,
                                                  dashboard_host_ip=dashboard_host_ip,
                                                  dashboard_images_saving_directory=dashboard_images_saving_directory,
                                                  local_images_saving_directory=self.LOCAL_IMAGES_SAVING_DIRECTORY)
        self.camera_handler = CameraHandler(liftbot_id=liftbot_id,
                                            local_images_saving_directory=self.LOCAL_IMAGES_SAVING_DIRECTORY,
                                            rm_speed_threshold=rm_speed_threshold,
                                            camera_address_list=camera_address_list,
                                            camera_position_mapping=camera_position_mapping)

    def send_image_to_dashboard(self):
        while True:
            if self.dashboard_handler.is_connected_to_dashboard:
                self.dashboard_handler.execute()

    def handle_can_message(self):
        while True:
            msg = self.can_handler.recv()
            rm_speed_as_bytes = msg.data[-4:]
            rm_speed = int.from_bytes(rm_speed_as_bytes, byteorder='little', signed=True)
            self.camera_handler.execute(rm_speed)

    def start(self):
        try:
            process_uploading_images = Process(target=self.send_image_to_dashboard)
            process_handling_can_messages = Process(target=self.handle_can_message)

            process_uploading_images.start()
            process_handling_can_messages.start()

        except KeyboardInterrupt:
            CanBusHandler.can_down()

if __name__ == "__main__":
    LIFTBOT_ID = "LB1"
    SSH_PASS_FILE = "ssh_pass"
    CONNECTION_PORT = "18538"
    DASHBOARD_HOST_NAME = "khang"
    DASHBOARD_HOST_IP = "7.tcp.eu.ngrok.io"
    DASHBOARD_IMAGES_SAVING_DIRECTORY= "/mnt/HC_Volume_11785377/images/"
    CAMERA_ADDRESS_LIST = ['/dev/video0', '/dev/video2'] # maximum is 4
    CAMERA_POSITION_MAPPING = {0: "left", 1: "right"} # 0: left, 1: right, 2: top, 3: bottom
    RM_SPEED_THRESHOLD = 1000 # Speed threshold is +- 100000
    CAN_ID_LIST_TO_LISTEN = [0x3A0]

    central_handler = CentralHandler(liftbot_id=LIFTBOT_ID,
                                     ssh_pass_file_name=SSH_PASS_FILE,
                                     connection_port=CONNECTION_PORT,
                                     dashboard_host_name=DASHBOARD_HOST_NAME,
                                     dashboard_host_ip=DASHBOARD_HOST_IP,
                                     dashboard_images_saving_directory=DASHBOARD_IMAGES_SAVING_DIRECTORY,
                                     rm_speed_threshold=RM_SPEED_THRESHOLD,
                                     camera_address_list=CAMERA_ADDRESS_LIST,
                                     camera_position_mapping=CAMERA_POSITION_MAPPING,
                                     can_id_list_to_listen=CAN_ID_LIST_TO_LISTEN)
    central_handler.start()
