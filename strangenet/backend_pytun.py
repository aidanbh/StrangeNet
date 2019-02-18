# backend_pytun.py - StrangeNet
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import os, sys, logging, select

import pytun
from pytun import TunTapDevice

import pypacker.pypacker as pypacker
from pypacker.pypacker import Packet
from pypacker.layer3 import ip, icmp

class backend:
    def __init__(self):
        self.tun = TunTapDevice(name='strangenet',flags=pytun.IFF_TUN|pytun.IFF_NO_PI)
        logging.debug('Created Linux tun device ' + self.tun.name)
        self.tun.addr = os.getenv('STRANGENET_IP', '10.0.0.1')
        logging.info('Assigned Linux tun device IP: ' + self.tun.addr)
        self.tun.netmask = os.getenv('STRANGENET_NETMASK', '255.255.255.0')
        logging.info('Configured Linux tun device netmask: ' + self.tun.netmask)
        self.tun.persist(True) # TODO figure out what this does and if we need it
        self.tun.mtu=256
        self.tun.up()
        logging.info('Linux tun device is up!')

        # setup polling

        self.poller = select.poll()
        self.poller.register(self.tun, select.POLLIN)

        # HERE BE DEBUG

    def set_mtu(self, mtu):
        self.tun.mtu = mtu

    # called by main code when data is recieved from XBee
    def tx(self, payload):
       self.tun.write(payload)

    def poll(self):
        logging.debug('working on latest packets from tun')
        
        data = self.tun.read(self.tun.mtu)
        if data is not None:
                    logging.debug('data incoming on TUN')
                    sys.stdout.buffer.write(data)
                    pack = ip.IP(data)
                    return {"IP": pack.dst, "payload": data}
        
    def phy_noroute(self, invalidip, datastart):
       pass
