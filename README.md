# Camera System

A camera system that utilizes DepthAI's API to capture all cargo and payload loaded the platform to understand what type of payload (including different scaffolding parts) KEWAZO customers use during projects. 

It is controllable by the RM via CAN Bus. It sends images to KEWAZO's server in close to real time.

Currently, the system supports [OAK-1 Lite](https://shop.luxonis.com/products/oak-1-lite?variant=42583148069087) camera from Luxonis, and webcam cameras.

## Prerequisites
### Hardware
- 2 x cameras with USB A interface
- Raspberry Pi 4 as host device for cameras
- 2nd device for simulation (Raspberry Pi 3/ 4/ 5, Raspberry Pi Zero/ Zero W/ Zero 2)
- [RS485 CAN hat](https://www.waveshare.com/rs485-can-hat.htm) for host device and simulation device 
- Powered USB Hub
- 35V-5V DC-DC converter, outputting 5A

### Software
- Ubuntu 20.04 LTS on host device
- Python 3.10

## Installation and Setup
1. Choose the camera configuration and checkout the corresponding branch.
* For Luxonis cameras, checkout OAK_support
* For normal webcam cameras, checkout main
2. Clone the repository
```
git clone https://github.com/lennoxtr/camera-module-kewazo.git/tree/{branch}
```
2. Install dependencies on host device
```
pip -r install requirements.txt
``` 
3. Connect hardware components. Refer to [Electrical Architecture](#electrical-architecture) for more details
4. Run the script on the host device
```
sudo python3 central_handler.py
```
$~~~~~~~~~$ If running simulation, run the script on the simulating device
```
sudo python3 rm_speed_simulation.py
```

## Electrical Architecture
### Running on actual TP
* The block diagram below is for using OAK-1 Lite cameras
![Electrical Architecture for running on TP](https://github.com/lennoxtr/camera-module-kewazo/blob/main/Electrical/Running%20on%20TP.png)
### Running simulation
* The block diagram below is for using OAK-1 Lite cameras, and Raspberry Pi Zero 2 as simulating device
![Electrical Architecture for running simulation](https://github.com/lennoxtr/camera-module-kewazo/blob/main/Electrical/Running%20RM%20Speed%20Simulation.png)


## External Documentation

For Luxonis's OAK-1 Lite documentation: https://docs.luxonis.com/projects/hardware/en/latest/pages/NG9096/

For DepthAI API documentation: https://docs.luxonis.com/projects/api/en/latest/

For RS485 CAN hat documentation: https://www.waveshare.com/wiki/RS485_CAN_HAT
