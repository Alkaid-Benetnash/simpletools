#
#
# Desired use case: inside gdb and run `source xxx.py`
#
#


# break point event handler
class EventHandler(object):
    stopRequested = False
    def __init__(self, name: str):
        gdb.events.stop.connect(self.handler)
        self.name = name
    def destroy(self):
        gdb.events.stop.disconnect(self.handler)
    def handler(self, event):
        if isinstance(event, gdb.SignalEvent):
            print(f'{self.name}: stop event received, {event.stop_signal}')
        if isinstance(event, gdb.BreakpointEvent):
            print(f'{self.name}: breakpoint event received for br {event.breakpoint.number}')
        self.stopRequested = True
    def resetStop(self):
        self.stopRequested = False
    def queryStop(self):
        return self.stopRequested

class InferiorContinueCMD(gdb.Command):
    """
    Assumption:
        1. breakpoints have been set properly
        2. detach-on-fork=off and follow-fork-mode=child
    Argument:
        @param mainInferiorNum int the inferior number of the main process
    This command will continue the execution of the current inferior or its children inferiors until hitting any breakpoints
    In the case of child inferiors exited normally, this command will automatically switch to the main inferior and continue
    """
    DEFAULT_MAIN_INFERIOR_NUM = 1
    def __init__(self, eventHandler):
        super().__init__("infcontinue", gdb.COMMAND_USER)
        self.eventHandler = eventHandler
    def invoke(self, argument, from_tty):
        try:
            infNum = int(argument)
        except ValueError:
            infNum = self.DEFAULT_MAIN_INFERIOR_NUM
        self.eventHandler.resetStop()
        gdb.execute('continue')
        while not self.eventHandler.queryStop():
            gdb.execute(f'inferior {infNum}')
            gdb.execute('continue')

class DisassembleNearRIPCMD(gdb.Command):
    """
    Argument:
        @param windowSize int the number of bytes around the $rip to disassemble
    This command disassemble a given window of instructions around the $rip
    """
    DEFAULT_RIP_WINDOW_SIZE = 100
    def __init__(self):
        super().__init__("disrip", gdb.COMMAND_USER)
    def invoke(self, argument, from_tty):
        try:
            windowSize = int(argument)
        except ValueError:
            windowSize = DEFAULT_RIP_WINDOW_SIZE
        gdb.execute(f"disassemble $rip-{windowSize/2}, +{windowSize/2}")

class RegisterUserScriptCMD(gdb.Command):
    def __init__(self):
        super().__init__('regScript', gdb.COMMAND_USER)
        self.eventHandler = None
        self.executed = False
    def invoke(self, argument, from_tty):
        if self.executed:
            print('User script already registered, skip reg')
        else:
            print('[Script]: set detach-on-fork=off and follow-fork-mode=child')
            gdb.execute('set detach-on-fork off')
            gdb.execute('set follow-fork-mode child')
            self.eventHandler = EventHandler("inferior_event_handler")
            InferiorContinueCMD(self.eventHandler)
            self.executed = True
class UnregisterUserScriptCMD(gdb.Command):
    def __init__(self, regCMD):
        super().__init__('deregScript', gdb.COMMAND_USER)
        self.regCMD = regCMD
    def invoke(self, argument, from_tty):
        if self.regCMD.executed:
            self.regCMD.eventHandler.destroy()
            self.regCMD.executed = False
        else:
            print('User script has not been registered, skip dereg')
gdb.execute('set disassembly-flavor intel')
regCMD = RegisterUserScriptCMD()
regCMD.invoke("", False)
unregCMD = UnregisterUserScriptCMD(regCMD)
