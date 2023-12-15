"""
This module handles setting up the camera system to receive CAN message,
capture images, and send images to server.

All operations (receving message, capture images, and send images) are
done synchronously with thread-based parallelism.

Typical usage example:

    central_handler = CentralHandler(liftbot_id, ssh_pass_file_name,
                                    connection_port, dashboard_host_name,
                                    dashboard_host_ip, dashboard_images_saving_directory,
                                    rm_speed_threshold, camera_position_mapping,
                                    can_id_list_to_listen)
    central_handler.start()

"""
import time
import threading
from multiprocessing import Process
from can_bus_handler import CanBusHandler
from camera_handler import CameraHandler
from dashboard_handler import DashboardHandler


class CentralHandler:
    """
    This module handles setting up the camera system to receive CAN message,
    capture images, and send images to server.

    All operations (receving message, capture images, and send images) are
    done synchronously with thread-based parallelism.

    """

    LOCAL_IMAGES_SAVING_DIRECTORY = "./images"

    def __init__(self, liftbot_id, ssh_pass_file_name, connection_port, dashboard_host_name,
                 dashboard_host_ip, dashboard_images_saving_directory, rm_speed_threshold,
                 camera_position_mapping, can_id_list_to_listen):

        """
        Initialize the CentralHandler with the appropriate information so it can set up
        CAN communication and initialize Dashboardhandler and CameraHandler

        Args:
            liftbot_id (string) : an ID to differentiate between multiple Liftbots 
                            to know which Liftbot the camera belongs to
            ssh_pass_file_name (.txt) : a file that contains the ssh password to
                                    connect to the server
            connection_port (int) : a number to indicate which port on the server to
                                        connect to
            dashboard_host_name (string) : the server's host name 
            dashboard_host_ip (string) : the server's host ip
            dashboard_images_saving_directory (string) : the top folder that contains
                                                    all the images on the server
            local_images_saving_directory (string) : the top folder that contains all
                                                the images on the host device
            rm_speed_threshold (int) : the speed threshold to determine whether the RM is
                                    actually moving. This is implemented as the RM_speed
                                    retrieved from CAN sometimes show very high value
                                    like 400000 when the RM is not moving. It is an
                                    absolute value
            camera_position_mapping (dictionary) : the dictionary to map camera's id to
                                            its position on the TP. Only holds 2 values
                                            to map to 'left' or 'right'
            can_id_list_to_listen (list) : list of CAN ID to filter CAN messages

        """
        self.liftbot_id = liftbot_id

        self.can_handler = CanBusHandler.setup_can(can_id_list_to_listen=can_id_list_to_listen)
        self.dashboard_handler = DashboardHandler(ssh_pass_file_name=ssh_pass_file_name,
                                                  connection_port=connection_port,
                                                  dashboard_host_name=dashboard_host_name,
                                                  dashboard_host_ip=dashboard_host_ip,
                                                  dashboard_images_saving_directory=
                                                  dashboard_images_saving_directory,
                                                  local_images_saving_directory=
                                                  self.LOCAL_IMAGES_SAVING_DIRECTORY)
        self.camera_handler = CameraHandler(liftbot_id=liftbot_id,
                                            local_images_saving_directory=
                                            self.LOCAL_IMAGES_SAVING_DIRECTORY,
                                            rm_speed_threshold=rm_speed_threshold,
                                            camera_position_mapping=camera_position_mapping)
        print("Central Handler setup OK")

    def send_image_to_dashboard(self):
        """
        Execute Dashboard Handler to send images to server.

        """
        while True:
            self.dashboard_handler.execute()

    def handle_can_message(self):
        """
        Receiving CAN message from the RM. The function then convert
        this message to the actual RM speed, and tell Camera Handler to
        execute its operation based on this speed. 

        """
        while True:
            msg = self.can_handler.recv()
            # RM speed is the last 4 bytes of the CAN message
            rm_speed_as_bytes = msg.data[-4:]

            # Converting the speed from the CAN message to the actual RM speed.
            #
            # NOTE: CAN message follows little endian system.
            rm_speed = int.from_bytes(rm_speed_as_bytes, byteorder='little', signed=True)
            self.camera_handler.execute(rm_speed)
            time.sleep(1)

    def start(self):
        """
        Start camera system execution.
        """
        try:
            process_handling_can_messages = threading.Thread(target=self.handle_can_message)
            process_uploading_images = Process(target=self.send_image_to_dashboard)

            process_uploading_images.start()
            process_handling_can_messages.start()

            process_uploading_images.join()
            process_handling_can_messages.join()

        except KeyboardInterrupt:
            CanBusHandler.can_down()

if __name__ == "__main__":
    LIFTBOT_ID = "LB1"
    SSH_PASS_FILE = "ssh_pass"
    CONNECTION_PORT = "18538"
    DASHBOARD_HOST_NAME = "khang"
    DASHBOARD_HOST_IP = "7.tcp.eu.ngrok.io"
    DASHBOARD_IMAGES_SAVING_DIRECTORY= "./images"
    CAMERA_POSITION_MAPPING = {0: "left", 1: "right"}
    RM_SPEED_THRESHOLD = 50 # Speed threshold is absolute value +- 10000
    CAN_ID_LIST_TO_LISTEN = [0x3A0]

    central_handler = CentralHandler(liftbot_id=LIFTBOT_ID,
                                     ssh_pass_file_name=SSH_PASS_FILE,
                                     connection_port=CONNECTION_PORT,
                                     dashboard_host_name=DASHBOARD_HOST_NAME,
                                     dashboard_host_ip=DASHBOARD_HOST_IP,
                                     dashboard_images_saving_directory=
                                     DASHBOARD_IMAGES_SAVING_DIRECTORY,
                                     rm_speed_threshold=RM_SPEED_THRESHOLD,
                                     camera_position_mapping=CAMERA_POSITION_MAPPING,
                                     can_id_list_to_listen=CAN_ID_LIST_TO_LISTEN)
    central_handler.start()
