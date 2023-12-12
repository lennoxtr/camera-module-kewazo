"""
This module handles sending captured images from the host device to the server

Upon initialization, it pings the server to determine whether the server
is reachable. If the check shows that the server is reachable, the module 
will create new saving directories on the server where the captured images will
be send to. The images stored locally on host device will then be deleted. If
the check shows that server is not reachable, the captured images will remain
stored locally on host device.

If during the process of sending captured images to the server, the server
becomes unreachable, all subsequent images will remain stored locally on
host device.

Upon losing connection with the server, there will be no attempt to reconnect.

The structure of folders to save images on the server is as follows:
.
|
|_ Top directory to save image on server (Example: /images)
        |
        |_ Date specific saving folder (Example: /230717, denoting 17 July 2023)
                |
                |_ Timestamp saving folder (Example: /130450, denoting 1:04:50 PM)
                        |
                        |_ Image 1
                        |
                        |_ Image 2
                        |
                        |_ ...


Typical usage example:
    dashboard_handler = DashboardHandler(ssh_pass_file_name, connection_port,
                                        dashboard_host_name, dashboard_host_ip,
                                        dashboard_images_saving_directory,
                                        local_images_saving_directory)
    dashboard_handler.execute()

"""

import os
import shutil
from multiprocessing import Process, Pool

class DashboardHandler:
    """
    A class that handles sending image folders to dashboard using
    process-based parallelism. It also pings the server to check for connection.

    If the image folders are sent successfully to the server, DashboardHandler will
    erase the copy of the corresponding folder on the host device. That is, after
    it send /230717 on the host device to the server, it will erase the /230717 
    folder on the host device.

    If during the process of sending captured images to the server, the server
    becomes unreachable, the DashboardHandler will not send any subsequent image
    folder to the server.

    Upon losing connection with the server, DashboardHandler will not attempt
    to reconnect. 

    """
    PING_DASHBOARD_COMMAND = 'ping -c 1 -W 2 {dashboard_host_ip}'
    SEND_TO_DASHBOARD_COMMAND = "sshpass -f {ssh_pass_file_name} scp -P {connection_port} -o StrictHostKeyChecking=no -pr {local_image_folder_directory} {dashboard_host_name}@{dashboard_host_ip}:{dashboard_images_saving_directory}/{date_specific_folder}"
    CREATE_NEW_FOLDER_ON_DASHBOARD_COMMAND = "sshpass -f {ssh_pass_file_name} ssh {dashboard_host_name}@{dashboard_host_ip} -p {connection_port} mkdir {dashboard_images_saving_directory}/{date_specific_folder}"

    def __init__(self, ssh_pass_file_name, connection_port, dashboard_host_name, dashboard_host_ip,
                 dashboard_images_saving_directory, local_images_saving_directory):
        """
        Initialize the DashboardHandler with the appropriate information to connect to the server.

        Args:
            ssh_pass_file_name (.txt) : a file that contains the ssh password to connect to
                                        the server
            connection_port (int) : a number to indicate which port on the server to
                                        connect to
            dashboard_host_name (string) : the server's host name 
            dashboard_host_ip (string) : the server's host ip
            dashboard_images_saving_directory (string) : the top folder that contains all the
                                                        images on the server
            local_images_saving_directory : the top folder that contains all the
                                            images on the host device

        """

        self.ssh_pass_file_name = ssh_pass_file_name
        self.connection_port = connection_port
        self.dashboard_host_name = dashboard_host_name
        self.dashboard_host_ip = dashboard_host_ip
        self.dashboard_images_saving_directory = dashboard_images_saving_directory
        self.local_images_saving_directory = local_images_saving_directory

        # Perform a ping to check server connection
        self.is_connected_to_dashboard = self.connect_to_dashboard()

    def connect_to_dashboard(self):
        """
        Ping the server to check for server connection. The function will send 1 packet
        for wait for 2 seconds for a reply. If it does not receive any, it will
        assume that the server is non reachable.

        """

        response_code = os.system(self.PING_DASHBOARD_COMMAND.format(dashboard_host_ip=self.dashboard_host_ip))
        if response_code == 0:
            return True
        return False

    def get_all_subfolders(self, local_folder_directory):
        """
        Get all subfolders immediately below a directory (non-recursive).

        Args:
            local_folder_directory (string) : the directory to search for subfolders
        
        Returns:
            list : a list that contains the name of all subfolders immediately below
                    a directory

        """
        scandir_object = os.scandir(local_folder_directory)
        subfolders_list = []
        for entry in scandir_object:
            if entry.is_dir():
                subfolders_list.append(entry.name)
        return subfolders_list

    def send_single_folder_to_dashboard(self, date_specific_folder):
        """
        Send a single folder to the server. It also updates whether the server
        is reachable. 

        If the image folders are sent successfully to the server, DashboardHandler will
        erase the copy of the corresponding folder on the host device. That is, after
        it send /230717 on the host device to the server, it will erase the /230717 
        folder on the host device.

        Args:
            date_specific_folder (string) : the name of the folder to send. The folder
                                        must be immediately below the top level folder
                                        for saving images (Ex: /images) on the host device
        """

        date_specific_folder_local_directory = os.path.join(self.local_images_saving_directory, date_specific_folder)
        timestamp_folders_to_send = self.get_all_subfolders(date_specific_folder_local_directory)

        # Erase the date folder if it is empty.
        #
        # This usually happens if all timestamp folders were sent successfully
        # to the server on the previous Liftbot run (as all timestamp
        # folders would then be deleted, leaving an empty date folder)  

        if len(timestamp_folders_to_send) == 0:
            shutil.rmtree(date_specific_folder_local_directory)
        
        # Do nothing if server is non-reachable
        elif self.is_connected_to_dashboard is False:
            pass

        else:
            try:
                # Create a new folder on the server with the same name as the date folder if it
                # doesn't exist
                os.system(self.CREATE_NEW_FOLDER_ON_DASHBOARD_COMMAND.format(
                    ssh_pass_file_name=self.ssh_pass_file_name,
                    dashboard_host_name=self.dashboard_host_name,
                    dashboard_host_ip=self.dashboard_host_ip,
                    connection_port=self.connection_port,
                    dashboard_images_saving_directory=self.dashboard_images_saving_directory,
                    date_specific_folder=date_specific_folder))
            except:
                print("Date specific folder already exist on dashboard")
            
            # Send all timestamp folders under the date folder to the server
            for timestamp_folder in timestamp_folders_to_send:
                subfolder_local_directory = os.path.join(date_specific_folder_local_directory, timestamp_folder)
                try:
                    os.system(self.SEND_TO_DASHBOARD_COMMAND.format(
                        ssh_pass_file_name=self.ssh_pass_file_name,
                        connection_port=self.connection_port,
                        local_image_folder_directory=subfolder_local_directory,
                        dashboard_host_name=self.dashboard_host_name,
                        dashboard_host_ip=self.dashboard_host_ip,
                        dashboard_images_saving_directory=self.dashboard_images_saving_directory,
                        date_specific_folder=date_specific_folder))
                    
                    # Remove the timestamp folder on the host device if it was successfully
                    # sent to the server
                    shutil.rmtree(subfolder_local_directory)
                except:
                    # If the server is not reachable during the process of sending images,
                    # the server is assumed to be non-reachable indefinitely until the 
                    # RM restarts. All subsequent images captured by the camers will be
                    # stored locally on host device. There will be no attempt to reconnect
                    # to the server. 

                    self.is_connected_to_dashboard = False
                    continue

    def send_multiple_folders_to_dashboard(self, local_image_folder_list):
        """
        Use process-based parallelism to send image folders to the server.

        Args:
            local_image_folder_directories_list (list) : a list that contains the 
                                                    directory of all image folders to send.
                                                    All of the folders must be immediately
                                                    below the top level folder for saving images
                                                    (Ex: /images) on the host device

        """

        with Pool() as p:
            p.map(self.send_single_folder_to_dashboard, local_image_folder_list)

    def execute(self):
        """
        Perform checks to check whether the host device contains any image folders not
        sent to the server in the previous Liftbot run (perhaps due to bad server connection)

        If there are folders that were not send to the server, the function will send these
        folders, along with the new image folders that the cameras have just captured in 
        the curent run, to the server. This is done via process-based parallelism

        """

        date_specific_directories_list = self.get_all_subfolders(self.local_images_saving_directory)

        # Check there exists a date folder on host device 
        if len(date_specific_directories_list) > 0:

            # The new image folders that the cameras have just captured in 
            # the curent run will be at the end of the list
            latest_date_specific_folder = date_specific_directories_list[-1]

            # Get folders that were not send to the server in the previous run, if any
            unsend_image_folders_list = date_specific_directories_list[:-1]

            # Send newest image folder to server
            process_send_live_images = Process(target=self.send_single_folder_to_dashboard(latest_date_specific_folder))
            process_send_live_images.start()

            # Check whether there are folders that were not send to the server in the previous run
            #
            # NOTE: As the check is performed on the date folder, there are 2 scenarios:
            #
            # 1. Date folder from the previous run exists, and it contain images that
            # were not sent to the server. In this case, these folders will be send to the server
            # 2. Date folder from the previous run exists, but it is empty. This usually happens if
            # all timestamp folders were sent successfully to the server on the previous Liftbot
            # run (as all timestamp folders would then be deleted, leaving an empty date folder). In
            # this case, the folder will be deleted  
            if len(unsend_image_folders_list) > 0:
                process_send_old_images = Process(target=self.send_multiple_folders_to_dashboard(unsend_image_folders_list))
                process_send_old_images.start()

            process_send_live_images.join()
            if len(unsend_image_folders_list) > 0:
                process_send_old_images.join()

        # Do nothing if there is no date folder on host device
        else:
            pass
