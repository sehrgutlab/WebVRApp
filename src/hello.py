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
import json

class AppSession(ApplicationSession):

    log = Logger()
    events = ( uinput.KEY_E, uinput.KEY_H,  uinput.KEY_L, uinput.KEY_V, uinput.KEY_END,uinput.KEY_HOME, uinput.KEY_UP, uinput.KEY_DOWN )

    lastzValue = 0.0
    @inlineCallbacks
    def onJoin(self, details):

        # SUBSCRIBE to a topic and receive events
        #
        self.zstoreFlag = 1
        self.lastzValue = 0.0
	self.zCounter = 0
        self.ystoreFlag = 1
        self.lastyValue = 0.0

        def y_direction(IMUTable):
            if self.ystoreFlag == 1:
                self.lastyValue  = abs( IMUTable['y'])
                self.ystoreFlag = 0
                return
            curryValue = abs(IMUTable['y'])
            ydiff = self.lastyValue  - curryValue
            gammaValue = IMUTable['gamma']
            if abs(gammaValue) > 66:
                print "Z Stable" 
                if ( curryValue > 1.5)  and (abs(ydiff) > 0.4):
                    print "Right"
                    self.keyb.emit_click(uinput.KEY_V)
                if ( curryValue < 1.5) and  (abs(ydiff) > 0.4):
                    print "Left"
                    self.keyb.emit_click(uinput.KEY_END)
            self.lastyValue  =  curryValue
	    print "The diff is ",ydiff, abs(ydiff)

 
        def z_direction(IMUTable):
            if self.zstoreFlag == 1:
                self.lastzValue  = IMUTable['z']
                self.zstoreFlag = 0
                return
            currzValue = IMUTable['z']
            zdiff = self.lastzValue  - currzValue
            gammaValue = IMUTable['gamma']
            if abs(gammaValue) > 66:
                print "Z Stable" 
                if ( currzValue > 1.5)  and (abs(zdiff) > 0.4):
                    print "Forward"
                    self.keyb.emit_click(uinput.KEY_UP)
                if ( currzValue < 1.5) and  (abs(zdiff) > 0.4):
                    print "Backward"
                    self.keyb.emit_click(uinput.KEY_DOWN)
            self.lastzValue  =  currzValue
	    print "The diff is ",zdiff, abs(zdiff)

        def on_event(i):
            print("Got event: {}".format(i))
            IMUTab = json.loads(i);
            print IMUTab['z']
            z_direction(IMUTab)
            y_direction(IMUTab)
            #if self.storeFlag == 1:
            #   self.lastzValue  = IMUTab['z']
            #   self.storeFlag = 0
            #   return
            #currzValue = IMUTab['z']
            #zdiff = self.lastzValue  - currzValue
            

	yield self.subscribe(on_event, 'com.myapp.topic1')
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
#	self.disp = SmartDisplay(visible=1, size=(640, 480) ).start()
#	self.command = EasyProcess('celestia -s -f').start()	
#	self.command = EasyProcess('lightdm --test-mode').start()	
	self.p = Popen(['celestia'], stdout=PIPE, stdin=PIPE, stderr=PIPE)
#	self.p = Popen(['xterm'], stdout=PIPE, stdin=PIPE, stderr=PIPE)
	

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
            # CALL a remote procedure
            #
            #try:
            #    res = yield self.call('com.example.mul2', counter, 3)
            #    self.log.info("mul2() called with result: {result}",
            #                  result=res)
            #except ApplicationError as e:
            #    # ignore errors due to the frontend not yet having
            #    # registered the procedure we would like to call
            #    if e.error != 'wamp.error.no_such_procedure':
            #        raise e
            #return #yield sleep(0)
#           self.keyb.emit_click(uinput.KEY_HOME)
            yield sleep(0)
            #stdout_data = self.p.communicate(input='o\n'.encode())
