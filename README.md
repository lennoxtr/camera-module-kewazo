# Camera System

A camera system that utilizes DepthAI's API to capture all cargo and payload loaded on the platform to understand what type of payload (including different scaffolding parts) KEWAZO customers use during projects. 

It is controllable by the RM via CAN Bus. After capturing images, it performs gamma correction to adjust the images' brightness so that they don't appear too bright or too dark in different environments. It then sends these images to KEWAZO's server in close to real time.

Currently, the system supports [OAK-1 Lite](https://shop.luxonis.com/products/oak-1-lite?variant=42583148069087) camera from Luxonis, and webcam cameras.

## Prerequisites
### Hardware
- 2 x cameras with USB A interface
- Raspberry Pi 4 as host device for cameras
- 2nd device for simulation (Raspberry Pi 3/ 4/ 5, Raspberry Pi Zero/ Zero W/ Zero 2)
- [RS485 CAN hat](https://www.waveshare.com/rs485-can-hat.htm) for host device and simulation device 
- Powered USB Hub
- 35V-5V DC-DC converter, outputting 5A
- 2 x 1.5 meter long USC A-USB C 3.0 cables
- Camera mounts, 3D printed with TPU

### Software
- Ubuntu 20.04 LTS on host device
- Python 3.10

## Installation and Setup
1. Choose the camera configuration and checkout the corresponding branch.
* For Luxonis cameras, checkout OAK_support
* For normal webcam cameras, checkout main
2. Clone the repository on the host device
```
git clone https://github.com/lennoxtr/camera-module-kewazo.git/tree/{branch}
```
3. Navigate into the cloned folder on the host device, create a folder for images and error log
```
mkdir images
cd ..
mkdir log
```
4. Install dependencies on host device
```
pip -r install requirements.txt
``` 
5. Connect hardware components. Refer to [Electrical Architecture](#electrical-architecture) for more details
6. Run the script on the host device
```
sudo python3 central_handler.py
```
$~~~~~~~~~$ If running simulation, run the script on the simulating device
```
sudo python3 rm_speed_simulation.py
```

## Start script automatically when powered on
1. Create a service that starts after network connection is establish
```
sudo nano /etc/systemd/system/upload-tp-image.service
```
2. Enter the following into the file, which will run the bash script that runs the Python script.
Change {host_device_name} to actual host device name. Save the file
```
[Unit]
After=network-online.target

[Service]
Type=simple
User=root
ExecStart=/home/{host_device_name}/upload-tp-image.bash

[Install]
WantedBy=multi-user.target

```
3. Create a bash file to run the script
```
sudo nano ~/home/{host_device_name}/upload-tp-image.bash
```
4. Enter the following into the file. Replace {path_to_folder_containing_script} with the correct path. Save the file afterward
```
#!/bin/bash

cd {path_to_folder_containing_script}

sudo python3 {path_to_folder_containing_script}/central_handler.py
```
5. Change permissions of the files
```
sudo chmod 744 ~/home/{host_device_name}/upload-tp-image.bash

sudo chmod 664 /etc/systemd/system/upload-tp-image.service
```
6. Verify that the bash file can run correctly
```
. ~/home/{host_device_name}/upload-tp-image.bash
```
7. Reload daemon
```
sudo systemctl daemon-reload
```
8. Enable service
```
sudo systemctl enable /etc/systemd/system/upload-tp-image.service
```
9. Reboot device
```
sudo reboot
```

## Debugging
### Settinng up dynamic update of host device's IP address to facilitate debugging
1. Create a service that starts after network connection is establish
network connection is establish
```
sudo nano /etc/systemd/system/ip2server.service
```

2. Enter the following into the file, which will run the bash script that update the IP address.
Change {host_device_name} to actual host device name. Save the file

```
[Unit]
After=network-online.target

[Service]
Type=simple
User=root
ExecStart=/home/{host_device_name}/ipserver.bash

[Install]
WantedBy=multi-user.target

```

3. Create a bash file to run the script
```
sudo nano ~/home/{host_device_name}/ip2server.bash
```
4. Enter the following into the file
```
#!/bin/bash

sudo python3 {path_to_folder_containing_script}/central_handler.py
```
5. Change permissions of the files
```
sudo chmod 744 ~/home/{host_device_name}/ip2server.bash

sudo chmod 664 /etc/systemd/system/ip2server.service 

```
6. Verify that the bash file can run correctly
```
. ~/home/{host_device_name}/ip2server.bash
```
$~~~~~~~~~$ Log on to server, navigate to cam_ip to check if IP address is sent successfully
```
ssh khang@7.tcp.eu.ngrok.io -p 18538

cat cam_ip/rpi1.txt
```

7. Reload daemon
```
sudo systemctl daemon-reload
```
8. Enable service
```
sudo systemctl enable /etc/systemd/system/ip2server.service
```
9. Reboot device
```
sudo reboot
```
### Debugging during running
1. On host device, check log file for warning and error logs:
```
cat log/debug.log
```

## Electrical Architecture
### Running on actual TP
* The block diagram below is for using OAK-1 Lite cameras
![Electrical Architecture for running on TP](https://github.com/lennoxtr/camera-module-kewazo/blob/OAK_support/Electrical/Running%20on%20TP.png)
### Running simulation
* The block diagram below is for using OAK-1 Lite cameras, and Raspberry Pi Zero 2 as simulating device
![Electrical Architecture for running simulation](https://github.com/lennoxtr/camera-module-kewazo/blob/OAK_support/Electrical/Running%20RM%20Speed%20Simulation.png)


## External Documentation

For Luxonis's OAK-1 Lite documentation: https://docs.luxonis.com/projects/hardware/en/latest/pages/NG9096/

For DepthAI API documentation: https://docs.luxonis.com/projects/api/en/latest/

For RS485 CAN hat documentation: https://www.waveshare.com/wiki/RS485_CAN_HAT
