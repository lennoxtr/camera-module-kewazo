import os
import shutil

class DashboardHandler:
    MESSAGE_TIMEOUT = 10.0
    PING_DASHBOARD_COMMAND = 'ping -c 1 -W 2 {dashboard_host_ip}'
    SEND_TO_DASHBOARD_COMMAND = "sshpass -f {ssh_pass_file_name} scp -P {connection_port} -o StrictHostKeyChecking=no -pr {images_folder_directory} {dashboard_host_name}@{dashboard_host_ip}:{dashboard_storage_directory}"
    CREATE_NEW_FOLDER_ON_DASHBOARD_COMMAND = ""

    def __init__(self, ssh_pass_file_name, connection_port, dashboard_host_name, dashboard_host_ip,
                 dashboard_storage_directory, images_top_level_directory):
        self.ssh_pass_file_name = ssh_pass_file_name
        self.connection_port = connection_port
        self.dashboard_host_name = dashboard_host_name
        self.dashboard_host_ip = dashboard_host_ip
        self.dashboard_storage_directory = dashboard_storage_directory
        self.images_top_level_directory = images_top_level_directory
        self.is_connected_to_dashboard = self.connect_to_dashboard()
        self.unsend_image_folder = self.get_unsend_image_folders()

    def connect_to_dashboard(self):
        response_code = os.system(self.PING_DASHBOARD_COMMAND.format(dashboard_host_ip=self.dashboard_host_ip))
        if response_code == 0:
            print("CONNECTED TO DASHBOARD")
            return True
        else:
            print("COULD NOT REACH DASHBOARD")
            return False
    
    def check_dashboard_connection(self):
        return self.is_connected_to_dashboard
    
    def get_unsend_image_folders(self):
        scandir_object = os.scandir(self.images_top_level_directory)
        images_folder_list = []
        for entry in scandir_object:
            if (entry.is_dir()):
                images_folder_list.append(entry.name)
        return images_folder_list

    def contain_unsend_image_folder(self):
        return len(self.unsend_image_folder) > 0

    def send_image_to_dashboard(self, latest_image_folder):
        # TODO: Implement checking whether a part of the folder already existed on dashboard
        while self.contain_unsend_image_folder():
            print("UPLOADING OLD FOLDER")
            images_folder_name = self.unsend_image_folder.pop(0)
            images_folder_directory = os.path.join(self.images_top_level_directory, images_folder_name)
            try:
                os.system(self.SEND_TO_DASHBOARD_COMMAND.format(
                    ssh_pass_file_name=self.ssh_pass_file_name,
                    connection_port=self.connection_port,
                    images_folder_directory=images_folder_directory,
                    dashboard_host_name=self.dashboard_host_name,
                    dashboard_host_ip=self.dashboard_host_ip,
                    dashboard_storage_directory=self.dashboard_storage_directory))
                shutil.rmtree(images_folder_directory)
            except:
                self.is_connected_to_dashboard = False
                print("COULD NOT REACH DASHBOARD")

        try:
            os.system()
        except:
            self.is_connected_to_dashboard = False
            print("COULD NOT REACH DASHBOARD")
