###############################################################################
#
# Copyright (C) 2014, Tavendo GmbH and/or collaborators. All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
# this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#
###############################################################################

from twisted.internet.defer import inlineCallbacks
from twisted.logger import Logger

from autobahn.twisted.util import sleep
from autobahn.twisted.wamp import ApplicationSession
from autobahn.wamp.exception import ApplicationError

from easyprocess import EasyProcess
from subprocess import Popen, PIPE, STDOUT
from pyvirtualdisplay import Display
from pyvirtualdisplay.smartdisplay import SmartDisplay

import base64
from base64 import encodestring
import cStringIO

import uinput

class AppSession(ApplicationSession):

    log = Logger()
    events = ( uinput.KEY_E, uinput.KEY_H,  uinput.KEY_L, uinput.KEY_V )

    @inlineCallbacks
    def onJoin(self, details):

        # SUBSCRIBE to a topic and receive events
        #
        def onhello(msg):
            self.log.info("event for 'onhello' received: {msg}", msg=msg)

        yield self.subscribe(onhello, 'com.example.onhello')
        self.log.info("subscribed to topic 'onhello'")

        # REGISTER a procedure for remote calling
        #
        def add2(x, y):
            self.log.info("add2() called with {x} and {y}", x=x, y=y)
            return x + y

        yield self.register(add2, 'com.example.add2')
        self.log.info("procedure add2() registered")
	self.keyb = uinput.Device(self.events) 
	self.disp = SmartDisplay(visible=1, size=(800,600)).start()
#	self.command = EasyProcess('celestia -s -f').start()	
#	self.command = EasyProcess('lightdm --test-mode').start()	
	self.p = Popen(['celestia'], stdout=PIPE, stdin=PIPE, stderr=PIPE)
	#self.p = Popen(['xterm'], stdout=PIPE, stdin=PIPE, stderr=STDOUT)
	

        # PUBLISH and CALL every second .. forever
        #
        counter = 0
        sleep(10)
        while True:
        #    stdout_data = p.communicate(input="\x1B[C")[0]
        #    print stdout_data
            self.buffer = cStringIO.StringIO()
            #self.img = self.disp.wait()
            self.img = self.disp.waitgrab(timeout=0.1, autocrop=False)
            self.img.save(self.buffer, "JPEG")
            self.imgStr =  base64.b64encode(self.buffer.getvalue())
            yield self.publish('com.example.image', self.imgStr)
            # PUBLISH an event
            #
            #yield self.publish('com.example.oncounter', counter)
            self.log.info("published to 'oncounter' with counter {counter}",
                          counter=counter)
            #counter += 1

            # CALL a remote procedure
            #
            try:
                res = yield self.call('com.example.mul2', counter, 3)
                self.log.info("mul2() called with result: {result}",
                              result=res)
            except ApplicationError as e:
                # ignore errors due to the frontend not yet having
                # registered the procedure we would like to call
                if e.error != 'wamp.error.no_such_procedure':
                    raise e
            #return #yield sleep(0)
            #self.keyb.emit_click(uinput.KEY_V)
            yield sleep(0)
            #stdout_data = self.p.communicate(input='o\n'.encode())