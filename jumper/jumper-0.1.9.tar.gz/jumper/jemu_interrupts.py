"""
:copyright: (c) 2017 by Jumper Labs Ltd.
:license: Apache 2.0, see LICENSE.txt for more details.
"""


class Interrupts(object):
    RESET = 'Reset'
    NMI = "NMI"
    HARD_FAULT = "Hard Fault"
    MEMORY_MANAGE_FAULT = "Memory Management Fault"
    BUS_FAULT = "Bus Fault"
    USAGE_FAULT = "Usage Fault"
    SVCALL = "Svcall"
    DEBUG_NON = "Debug Non"
    PENDSV = "Pendsv"
    SYSTICK = "Systick"

    POWER = "Power"
    RADIO = "Radio"
    UARTE0_UART_0 = "Uarte0 Uart0"
    SPIM0_SPIS0_TWIM0_TWIS0_SPI0_TWI0 = "Spim0 / Spis0 / Twim0 / Twis0 / Spi0 / Twi0"
    SPIM0_SPIS1_TWIM1_TWIS1_SPI1_TWI1 = "Spim1 / Spis1 / Twim1 / Twis1 / Spi1 / Twi1"
    GPIOTE = "GPIOTE"
    SAADC = "SAADC"
    TIMER0 = "Timer0"
    TIMER1 = "Timer1"
    RTC0 = "RTC0"
    TEMP = "Temp"
    RNG = "RNG"
    WDT = "WDT"
    RTC1 = "RTC1"
    COMP_LPCOMP = "Comp / Lpcomp"
    SWI0_EGU0 = "SWI0EGU0"
    SWI0_EGU1 = "SWI0EGU1"
    SWI0_EGU2 = "SWI0EGU2"
    SWI0_EGU3 = "SWI0EGU3"
    SWI0_EGU4 = "SWI0EGU4"
    SWI0_EGU5 = "SWI0EGU5"
    PWM = "PWM"
    MWU = "Mwu"
    SPIM2_SPIS2_SPI2 = "Spim2 / Spis2 / Spi2"
    RTC2 = "RTC2"
    FPU = "FPU"


class JemuInterrupts(object):
    _TYPE_STRING = "type"
    _INT = "interrupt"

    def __init__(self):
        self._interrupt_callbacks = []
        self._jemu_connection = None


    def set_jemu_connection(self, jemu_connection):
        self._jemu_connection = jemu_connection
        self._jemu_connection.register(self.receive_packet)

    def on_interrupt(self, callback):
        self._interrupt_callbacks += callback

    def receive_packet(self, jemu_packet):
        if jemu_packet[self._TYPE_STRING] == self._INT:
            for callback in self._interrupt_callbacks:
                callback(jemu_packet['interrupt_type'])

