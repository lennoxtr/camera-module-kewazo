import os
import can

def setup_can_object():
    os.system('sudo ip link set can0 type can bitrate 100000')
    os.system('sudo ifconfig can0 up')

    can0 = can.interface.Bus(channel = 'can0', bustype = 'socketcan')# socketcan_native

    return can0

if __name__ == "__main__":
    can0 = setup_can_object()

    while True:
        RM_speed =  int(input("RM simulated speed as integer: "))
        msg = can.Message(arbitration_id=0x3A0, data=[RM_speed], is_extended_id=False)

        can0.send(msg)
    

 

