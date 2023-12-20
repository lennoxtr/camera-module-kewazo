"""
This module allows the Camera Module to receive CAN messages from specified CAN ID

It handles setting up CAN communication to connect a CAN controller such as MCP2515
to the CAN network.
It creates a CAN bus object with specified filters which the Camera Module can
use to receive CAN messages from different CAN IDs to determine whether it should capture images.
It also disconnects the CAN controller from CAN network when the Camera Module is turned off.

Typical usage example:

    can0 = CanBushandler.setup_can(can_id_list_to_listen)
    CanBushandler.can_down()

"""

import os
import can
import logging

class CanBusHandler:
    """
    A class that handles setting up CAN communication and disconnecting from CAN network.
    """

    @staticmethod
    def setup_can(can_id_list_to_listen):
        """
        Connect CAN controller (MCP2515) to the CAN network to receive messages
        from specified CAN ID.
        Return a CAN object with specified CAN ID filters and masks.

        Args:
            can_id_list_to_listen (list) : list of CAN ID to filter CAN messages.

        Returns:
            can.interface.Bus : a CAN object.

        """
        logging.basicConfig(filename='debug.log', encoding='utf-8', filemode='a', level=logging.WARNING)

        # Check whether the bitrate here matches RM's
        try:
            os.system('sudo ip link set can0 type can bitrate 1000000')
            os.system('sudo ifconfig can0 up')
        except:
            logging.critical("CAN SETUP ERROR")


        can_channel = 'can0'
        can_bustype = 'socketcan'
        can_filters = []
        for can_id in can_id_list_to_listen:
            can_filters.append({"can_id": can_id, "can_mask": 0x7FF, "extended": False})

        can0 = can.interface.Bus(channel=can_channel, bustype=can_bustype, can_filters=can_filters)
        logging.info("CAN SETUP OK")

        return can0

    @staticmethod
    def can_down():
        """
        Disconnect CAN controller from the CAN network
        """
        os.system('sudo ifconfig can0 down')
        logging.critical("CAN network down")
