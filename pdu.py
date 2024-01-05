import time
from pathlib import Path

import serial
from serial import Serial


class PDU:

    def __init__(self, serialPort: str):
        self.relayState = 0
        self.serialPort = None
        self.serialPortStr = serialPort

        self._setupSerial()
        self._loadRelayState()
        self._gradualPowerUp()

    def _setupSerial(self):
        self.serialPort = Serial()
        self.serialPort.port = self.serialPortStr
        self.serialPort.baudrate = 115200
        self.serialPort.bytesize = serial.EIGHTBITS
        self.serialPort.parity = serial.PARITY_NONE
        self.serialPort.stopbits = serial.STOPBITS_ONE
        self.serialPort.open()
        time.sleep(2)

    def disconnect(self):
        self.relayState = 0
        self.updateRelays()
        self.serialPort.close()

    def _sendCommandToMCU(self, command) -> str:
        if self.serialPort is None:
            return "err"

        self.serialPort.write(f"{command}\n".encode())

    def _saveRelayState(self):
        with open("relayState", "w+") as file:
            file.write(str(self.relayState))

    def _loadRelayState(self):
        if Path("relayState").exists():
            with open("relayState", "r") as file:
                self.relayState = int(file.read())

    def modifyRelayState(self, index: int, value: int, save=True):
        if value:
            self.relayState |= (1 << index - 1)
        else:
            self.relayState &= ~(1 << index - 1)

        if save:
            self._saveRelayState()

    def updateRelays(self):
        self._sendCommandToMCU(self.relayState)

    def getRelayState(self):
        state = list(str(bin(self.relayState))[2:].zfill(16))
        state.reverse()
        return state

    def getCurrentUsage(self):
        self._sendCommandToMCU("current")
        return 1234

    def _gradualPowerUp(self):
        tempRelayState = self.getRelayState()
        self.relayState = 0

        for bit, i in zip(tempRelayState, range(1, 17)):
            if int(bit):
                self.modifyRelayState(i, int(bit), False)
                self.updateRelays()
                time.sleep(3)
