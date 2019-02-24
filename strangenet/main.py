# main.py - StrangeNet
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import os, sys, logging
import backend_pytun
# import backend_wintap

backend = None

logging.basicConfig(level=logging.DEBUG)

if os.name == 'posix':
    logging.debug('OS is posix, using python-pytun to network.')
    backend = backend_pytun.backend()
else:
    sys.exit('Unsupported os: ' + os.name)

from xbee import strangenet_xbee

xbee = strangenet_xbee()

# event loop
while True:
    pack = backend.poll(10)
    if pack is not None:
        xbee.tx(pack['IP'], pack['payload'])
