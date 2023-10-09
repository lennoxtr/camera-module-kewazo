import os
import shutil
from multiprocessing import Pool

class DashboardHandler:
    PING_DASHBOARD_COMMAND = 'ping -c 1 -W 2 {dashboard_host_ip}'
    SEND_TO_DASHBOARD_COMMAND = "sshpass -f {ssh_pass_file_name} scp -P {connection_port} -o StrictHostKeyChecking=no -pr {local_image_folder_directory} {dashboard_host_name}@{dashboard_host_ip}:{dashboard_images_saving_directory}"
    CREATE_NEW_FOLDER_ON_DASHBOARD_COMMAND = ""

    def __init__(self, ssh_pass_file_name, connection_port, dashboard_host_name, dashboard_host_ip,
                 dashboard_images_saving_directory, local_images_saving_directory):
        self.ssh_pass_file_name = ssh_pass_file_name
        self.connection_port = connection_port
        self.dashboard_host_name = dashboard_host_name
        self.dashboard_host_ip = dashboard_host_ip
        self.dashboard_images_saving_directory = dashboard_images_saving_directory
        self.local_images_saving_directory = local_images_saving_directory
        self.is_connected_to_dashboard = self.connect_to_dashboard()
        self.unsend_image_folders = self.get_unsend_image_folders()

    def connect_to_dashboard(self):
        response_code = os.system(self.PING_DASHBOARD_COMMAND.format(dashboard_host_ip=self.dashboard_host_ip))
        if response_code == 0:
            print("CONNECTED TO DASHBOARD")
            return True
        else:
            print("COULD NOT REACH DASHBOARD")
            return False
    
    def get_unsend_image_folders(self):
        scandir_object = os.scandir(self.local_images_saving_directory)
        unsend_images_folder_list = []
        for entry in scandir_object:
            if (entry.is_dir()):
                unsend_images_folder_list.append(entry.name)
        return unsend_images_folder_list

    def send_single_folder_to_dashboard(self, local_image_folder_directory):
        try:
            os.system(self.SEND_TO_DASHBOARD_COMMAND.format(
                ssh_pass_file_name=self.ssh_pass_file_name,
                connection_port=self.connection_port,
                local_image_folder_directory=local_image_folder_directory,
                dashboard_host_name=self.dashboard_host_name,
                dashboard_host_ip=self.dashboard_host_ip,
                dashboard_images_saving_directory=self.dashboard_images_saving_directory))
            shutil.rmtree(local_image_folder_directory)
        except:
            self.connect_to_dashboard = False
            print("COULD NOT REACH DASHBOARD")

    def send_multiple_folders_to_dashboard(self, local_image_folder_directories_list):
        with Pool() as p:
            p.map(self.send_single_folder_to_dashboard, local_image_folder_directories_list)

    def send_image_to_dashboard(self):
        # TODO: Implement checking whether a part of the folder already existed on dashboard
        while self.contain_unsend_image_folders():
            print("UPLOADING OLD FOLDER")
            images_folder_name = self.unsend_image_folders.pop(0)
            images_folder_directory = os.path.join(self.local_images_saving_directory, images_folder_name)
            try:
                os.system(self.SEND_TO_DASHBOARD_COMMAND.format(
                    ssh_pass_file_name=self.ssh_pass_file_name,
                    connection_port=self.connection_port,
                    images_folder_directory=images_folder_directory,
                    dashboard_host_name=self.dashboard_host_name,
                    dashboard_host_ip=self.dashboard_host_ip,
                    dashboard_images_saving_directory=self.dashboard_images_saving_directory))
                shutil.rmtree(images_folder_directory)
            except:
                self.is_connected_to_dashboard = False
                print("COULD NOT REACH DASHBOARD")

        try:
            os.system()
        except:
            self.is_connected_to_dashboard = False
            print("COULD NOT REACH DASHBOARD")
