import os

class DashboardHandler:
    MESSAGE_TIMEOUT = 10.0

    def __init__(self, ssh_pass_file_name, connection_port, dashboard_host_name, dashboard_host_ip, dashboard_storage_directory):
        self.ssh_pass_file_name = ssh_pass_file_name
        self.connection_port = connection_port
        self.dashboard_host_name = dashboard_host_name
        self.dashboard_host_ip = dashboard_host_ip
        self.dashboard_storage_directory = dashboard_storage_directory
        self.is_connected_to_dashboard = self.connect_to_dashboard()
    
    def connect_to_dashboard(self):
        response_code = os.system("ping -c 1 " + self.dashboard_host_ip)
        if response_code == 0:
            print("CONNECTED TO DASHBOARD")
            return True
        else:
            print("COULD NOT REACH DASHBOARD")
            return False
    
    def check_dashboard_connection(self):
        return self.is_connected_to_dashboard

    def send_image_to_dashboard(self, images_local_storage_directory):
        saved_images_list = os.listdir(images_local_storage_directory)
        while len(saved_images_list) > 0:
            saved_image = saved_images_list.pop(0)
            saving_path = os.path.join(images_local_storage_directory, saved_image)
            try:
                os.system('sshpass -f ' + self.ssh_pass_file_name + ' scp -P ' + self.connection_port
                       + ' -o StrictHostKeyChecking=no ' + saving_path + ' ' + self.dashboard_storage_directory)
                os.remove(saving_path)
                print("UPLOADED OK")
            except:
                self.is_connected = False
                print("DASHBOARD CONNECTION LOST")
