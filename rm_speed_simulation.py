"""
A script to simulate how RM sends CAN message to the camera system's host
device. It is used to test the camera system without the need to connect
to the actual RM and TP.

Usually, this is done by connecting the host device's CAN bus to the
test device's CAN bus. This script will be run on the test device.

"""

import os
import can

def setup_can_object():
    """
    Connect CAN controller (MCP2515) of the test device to the CAN network
    to simulate sending CAN messages to the camera system.

    Returns:
        can.interface.Bus : a CAN object.

    """
    # Check whether the bitrate here matches RM's and camera system's
    os.system('sudo ip link set can0 type can bitrate 100000')
    os.system('sudo ifconfig can0 up')

    can0 = can.interface.Bus(channel = 'can0', bustype = 'socketcan') # socketcan_native

    return can0

if __name__ == "__main__":
    can_object = setup_can_object()

    # Simulate sending RM speed to the camera system's host device via
    # CAN bus
    # Check whether the arbitration_id matches the actual RM's CAN ID
    # that send the RM speed
    while True:
        RM_speed =  int(input("RM simulated speed as integer: "))
        msg = can.Message(arbitration_id=0x3A0, data=[RM_speed], is_extended_id=False)
        can_object.send(msg)
