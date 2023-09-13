import os
import can
from CameraModules import CameraModule

def setup_can_object():
    os.system('sudo ip link set can0 type can bitrate 100000')
    os.system('sudo ifconfig can0 up')
    can0 = can.interface.Bus(channel = 'can0', bustype = 'socketcan')# socketcan_native
    print('CAN SETUP OK')
    return can0

def do_something(RM_speed, cameraModule):
    print("Current RM speed received is: " + str(RM_speed))
    if (RM_speed > 10):
        print("RM SPEED GREATER THAN THRESHOLD. TAKING PICTURES")
        cameraModule.captureImage()
    else:
        print("RM NOT MOVING. NO PICTURE TAKEN")


if __name__ == "__main__":
    camera_address_list = ['/dev/video0', '/dev/video2']
    can0 = setup_can_object()
    cameraModule = CameraModule()
    cameraModule.initializeCameras(camera_address_list=camera_address_list)

    while True:
        try:
            msg = can0.recv(10.0)
            if msg is None:
                print("Timeout occured. No message")
            else:
                print(msg)
                RM_speed = int.from_bytes(msg.data, byteorder='little')
                do_something(RM_speed=RM_speed, cameraModule=cameraModule)
        except KeyboardInterrupt:
            cameraModule.closeCamera()
            os.system('sudo ifconfig can0 down')
            break
