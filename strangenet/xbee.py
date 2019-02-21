# xbee.py - StrangeNet
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import os, sys, logging

from digi.xbee.devices import XBeeDevice, DigiMeshDevice
from digi.xbee.util import utils as xbu

class strangenet_xbee:
    def __init__(self):
        logging.debug("Initializing local XBee...")
        
        port = os.getenv("STRANGENET_XBEE_PORT", "/dev/ttyUSB0")
        baud = os.getenv("STRANGENET_XBEE_BAUD", 230400)
        logging.debug("Using port: " + port + " and baud: " + str(baud))
        self.device = XBeeDevice(port,  baud)
        self.device.open() # automatically does read_device_info() for local device
        
        # the XBee waits NT * 0.1 sec on a ND, DN or FN (default 0x82
        # self.device.set_parameter('NT', xbu.hex_string_to_bytes('10'))

        print('Printing NP value')
        print(self.device.get_parameter("NP")) # NP: max packet size in hex
        self.mtu = self.device.get_parameter("NP")

        ipv4 = os.getenv('STRANGENET_IP', '10.0.0.1')
        logging.debug('Writing IP address ' + ipv4 + ' to XBee device...')
        self.device.set_parameter("NI", bytearray(('STR_' + ipv4), 'utf-8'))

        self.device.write_changes() # in case of accidental reset

        # create a XBeeNetwork object to store discovered devices
        self.xnet = self.device.get_network()

    def tx(self, dst_ip, payload):

        # we have an IP, encode to NI
        # dst is a bytearray representing the destination IPv4
        # there is probably a cleaner way to do this
        dst = dst_ip.hex() # in hex this should be a fixed size
        dstNI = 'STR_' + (str(int(dst[:2], 16)) + '.' + str(int(dst[2:4], 16)) + '.' + str(int(dst[4:6], 16)) + '.' + str(int(dst[6:8], 16)))
        print('\nSending to NI:', dstNI)
        
        # special procedures for broadcast
        if dstNI[3:] is "10.0.0.0": # FIXME do the things to support other subnets
            return self.broadcast_tx(payload)
        
        # see if we have the MAC cached, note that caching last duration of runtime
        # so we do not have an easy way for devices to change IP
        destdev = self.xnet.get_device_by_node_id(dstNI)
        
        if destdev is None: # not in xnet
            # we will have to resolve, this will block for NT * 0.1 sec
            # unpredictable behavior will result from duplicate NI's, the following picks the first
            destdev = self.xnet.discover_device(dstNI)
            if destdev is None:
                return "NOROUTE"

        # proceed to send the data now that we have destdev
        # TODO do this asynchronously
        
        try:
            self.device.send_data(destdev, payload) # no exec == success (ACK recd)
        except digi.xbee.TimeoutException:
            logging.warning("Timeout on XBee link")
            return "TIMEOUT"
        except XBeeException: # wrong op mode, corrupt response, serial error
            return "ERROR"

    def broadcast_tx(self, payload):
        pass

    def poll(self, timeout):
        logging.debug("Polling XBee device for incoming packets...")
        data = self.device.read_data()
        if data is not None:
            logging.debug("Packet recd from XBee, forwarding to TUN...")
            # we have an XBeeMessage object
            return {'payload': bytes(data.data)}
        else:
            logging.debug("Nothing from XBee this time.")
            return None # None = no data w/in timeout (set to zero for instant)
