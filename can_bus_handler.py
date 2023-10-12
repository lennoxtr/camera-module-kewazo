import os
import can

class CanBusHandler:
    @staticmethod
    def setup_can(can_id_list_to_listen):
        os.system('sudo ip link set can0 type can bitrate 1000000')
        os.system('sudo ifconfig can0 up')

        can_channel = 'can0'
        can_bustype = 'socketcan'
        can_filters = []
        for can_id in can_id_list_to_listen:
            can_filters.append({"can_id": can_id, "can_mask": 0x7FF, "extended": False})

        can0 = can.interface.Bus(channel=can_channel, bustype=can_bustype, can_filters=can_filters)
        print('CAN SETUP OK')
        return can0

    @staticmethod
    def can_down():
        os.system('sudo ifconfig can0 down')
