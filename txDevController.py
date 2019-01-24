#!/usr/bin/python
"""
Telex Serial Communication over CH340-Chip
"""
__author__      = "Jochen Krapf"
__email__       = "jk@nerd2nerd.org"
__copyright__   = "Copyright 2018, JK"
__license__     = "GPL3"
__version__     = "0.0.1"

from threading import Thread
import time

import txBase

#######

class TelexController(txBase.TelexBase):
    _fontstr = {'A': 'VSSV', 'B': '[YYR', 'C': 'CZZZ', 'D': '[ZZC', 'E': '[YYZ', 'F': '[SSE', 'G': 'CZYX', 'H': '[  [', 'I': 'Z[Z', 'J': '<TZK', 'K': '[ RZ', 'L': '[TTT', 'M': '[|M|[', 'N': '[| [', 'O': 'CZZZC', 'P': '[SS|', 'Q': 'CZBV', 'R': '[SFL', 'S': 'LYYD', 'T': 'EE[EE', 'U': 'KTTK', 'V': 'U<T<U', 'W': '[<I<[', 'X': 'ZR RZ', 'Y': 'E|M|E', 'Z': 'ZBYWZ', '0': 'CZZC', '1': 'L[T', '2': 'BYYL', '3': 'ZYYR', '4': 'U V ', '5': 'UYYD', '6': 'NPYD', '7': 'EBSA', '8': 'RYYR', '9': 'LYFI', '.': 'OO', ',': 'ON', ';': 'GR', '+': '  [  ', '-': '    ', '*': 'YC CY', '/': 'T< |E', '=': 'RRRR', '(': 'CZ', ')': 'ZC', '?': 'EYY|', "'": 'AA', ' ': '~~', '': '~', '\r': '  RZZ', '<': '  RZZ', '\n': 'YYYYY', '|': 'YYYYY'}
    _fontsep = '~'


    def __init__(self, device_id:str):
        self.device_id = device_id

        self.id = '§'
        self.params = {}
        self._rx_buffer = []
        self._mx_buffer = []

        self._font_mode = False

        self._run = True
        self._tx_thread = Thread(target=self.thread_memory)
        self._tx_thread.start()


    def __del__(self):
        self._run = False
        pass
    

    def read(self) -> str:
        ret = ''

        if self._rx_buffer:
            ret = self._rx_buffer.pop(0)

        return ret


    def write(self, a:str, source:str):
        if self.device_id and a == '#':   # found 'Wer da?' / 'WRU'
            self._rx_buffer.extend(list('\r\n' + self.device_id))   # send back device id
            return True


        if a == '\x1bAT':   # AT
            self._rx_buffer.append('\x1bD')   # send text
            return True

        if a == '\x1bST':   # ST
            self._rx_buffer.append('\x1bZ')   # send text
            return True

        if a == '\x1bLT':   # LT
            self._rx_buffer.append('\x1bA')   # send text
            return True


        if a == '\x1bFONT':   # set to font mode
            self._font_mode = not self._font_mode
            return True

        if self._font_mode:   # 
            f = self._fontstr.get(a, None)
            if f:
                f += self._fontsep
                self._rx_buffer.extend(list(f))   # send back font pattern
            return True


        if a == '\x1bLOREM':   # print LOREM IPSUM
            self._rx_buffer.extend(list('LOREM IPSUM DOLOR SIT AMET, CONSETETUR SADIPSCING ELITR, SED DIAM'))   # send text
            return True


        if a == '\x1bRY':   # print RY pattern
            self._rx_buffer.extend(list('RYRYRYRYRYRYRYRYRYRYRYRYRYRYRYRYRYRYRYRYRYRYRYRYRYRYRYRYRYRYRYRYRY'))   # send text
            return True


        if a == '\x1bABC':   # print ABC pattern
            self._rx_buffer.extend(list('ABCDEFGHIJKLMNOPQRSTUVWXYZ 1234567890 .,-+=/()?\'%'))   # send text
            return True

        if a[:3] == '\x1bM=':   # set memory text
            self._mx_buffer.extend(list(a[3:]))   # send text
            return True

        if a == '\x1bMC':   # clear memory text
            self._mx_buffer = []
            return True


        if a == '\x1bT':   # actual time
            text = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + '\r\n'
            self._mx_buffer.extend(list(text))   # send text
            return True


    def thread_memory(self):
        while self._run:
            #LOG('.')
            if self._mx_buffer:
                a = self._mx_buffer.pop(0)
                self._rx_buffer.append(a)
            time.sleep(0.15)


#######
