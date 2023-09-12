import os
import can
from CameraModules import CameraModule

#msg = can.Message(arbitration_id=0x123, data=[0, 1, 2, 3, 4, 5, 6, 7], is_extended_id=False)


def setup_can_object():
    os.system('sudo ip link set can0 type can bitrate 100000')
    os.system('sudo ifconfig can0 up')
    can0 = can.interface.Bus(channel = 'can0', bustype = 'socketcan')# socketcan_native
    return can0

def do_something(RM_speed, cameraModule):
    if (RM_speed > 10):
        cameraModule.captureImage()
        

if __name__ == "__main__":
    can0 = setup_can_object()
    cameraModule = CameraModule()
    cameraModule.addCamera()
    cameraModule.initializeAllCameras()

    while True:
        msg = can0.recv()
        if msg is None:
            print("Timeout occured. No message")
        else:
            print(msg)
            do_something(msg.data, cameraModule=cameraModule)
        

    os.system('sudo ifconfig can0 down')