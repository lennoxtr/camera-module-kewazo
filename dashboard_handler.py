import os
import shutil
from multiprocessing import Process, Pool

class DashboardHandler:
    PING_DASHBOARD_COMMAND = 'ping -c 1 -W 2 {dashboard_host_ip}'
    SEND_TO_DASHBOARD_COMMAND = "sshpass -f {ssh_pass_file_name} scp -P {connection_port} -o StrictHostKeyChecking=no -pr {local_image_folder_directory} {dashboard_host_name}@{dashboard_host_ip}:{dashboard_images_saving_directory}/{date_specific_folder}"
    CREATE_NEW_FOLDER_ON_DASHBOARD_COMMAND = "sshpass -f {ssh_pass_file_name} ssh {dashboard_host_name}@{dashboard_host_ip} -p {connection_port} mkdir {dashboard_images_saving_directory}/{date_specific_folder}"

    def __init__(self, ssh_pass_file_name, connection_port, dashboard_host_name, dashboard_host_ip,
                 dashboard_images_saving_directory, local_images_saving_directory):
        self.ssh_pass_file_name = ssh_pass_file_name
        self.connection_port = connection_port
        self.dashboard_host_name = dashboard_host_name
        self.dashboard_host_ip = dashboard_host_ip
        self.dashboard_images_saving_directory = dashboard_images_saving_directory
        self.local_images_saving_directory = local_images_saving_directory
        self.is_connected_to_dashboard = self.connect_to_dashboard()

    def connect_to_dashboard(self):
        response_code = os.system(self.PING_DASHBOARD_COMMAND.format(dashboard_host_ip=self.dashboard_host_ip))
        if response_code == 0:
            print("CONNECTED TO DASHBOARD")
            return True
        else:
            print("COULD NOT REACH DASHBOARD")
            return False
    
    def get_all_subfolders(self, local_folder_directory):
        scandir_object = os.scandir(local_folder_directory)
        subfolders_list = []
        for entry in scandir_object:
            if (entry.is_dir()):
                subfolders_list.append(entry.name)
        return subfolders_list

    def send_single_folder_to_dashboard(self, date_specific_folder):
        date_specific_folder_local_directory = os.path.join(self.local_images_saving_directory, date_specific_folder)
        timestamp_folders_to_send = self.get_all_subfolders(local_folder_directory=date_specific_folder_local_directory)
        if len(timestamp_folders_to_send) == 0:
            shutil.rmtree(date_specific_folder_local_directory)
        elif self.is_connected_to_dashboard == False:
            pass
        else:    
            try:
                os.system(self.CREATE_NEW_FOLDER_ON_DASHBOARD_COMMAND.format(
                    ssh_pass_file_name=self.ssh_pass_file_name,
                    dashboard_host_name=self.dashboard_host_name,
                    dashboard_host_ip=self.dashboard_host_ip,
                    connection_port=self.connection_port,
                    dashboard_images_saving_directory=self.dashboard_images_saving_directory,
                    date_specific_folder=date_specific_folder))
            except:
                print("Date specific folder already exist on dashboard")
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
                    shutil.rmtree(subfolder_local_directory)
                except:
                    self.is_connected_to_dashboard = False
                    print("COULD NOT REACH DASHBOARD")
                    continue

    def send_multiple_folders_to_dashboard(self, local_image_folder_directories_list):
        with Pool() as p:
            p.map(self.send_single_folder_to_dashboard, local_image_folder_directories_list)

    def execute(self):
        date_specific_directories_list = self.get_all_subfolders(self.local_images_saving_directory)
        if len(date_specific_directories_list) > 0:
            latest_date_specific_folder = date_specific_directories_list[-1]
            unsend_image_folders_list = date_specific_directories_list[:-1]

            process_send_live_images = Process(target=self.send_single_folder_to_dashboard(latest_date_specific_folder))
            process_send_live_images.start()

            if len(unsend_image_folders_list) > 0:
                process_send_old_images = Process(target=self.send_multiple_folders_to_dashboard(unsend_image_folders_list))
                process_send_old_images.start()
            
            process_send_live_images.join()
            if len(unsend_image_folders_list) > 0:
                process_send_old_images.join()

        else:
            pass
