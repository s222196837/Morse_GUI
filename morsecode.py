#!/usr/bin/env python

import sys
import RPi.GPIO as GPIO
from PyQt5.QtWidgets import QMainWindow, QApplication, QAction
from PyQt5.QtWidgets import QWidget, QPushButton, QLineEdit
from PyQt5.QtCore import QCoreApplication, QTimer


class LED:
    def __init__(self):
        """ class dealing with LED (and console) interaction """
        self.pin = 8
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BOARD) # use physical pin numbering
        GPIO.setup(self.pin, GPIO.OUT, initial = GPIO.LOW)

    def on(self, time):
        GPIO.output(self.pin, GPIO.HIGH) # on
        print("LED on", self.pin, time)

    def off(self, time=None):
        GPIO.output(self.pin, GPIO.LOW) # off
        if time:
            print("LED off", self.pin, time)
        else:
            print("LED off", self.pin)


class MorseLED(QTimer):
    def __init__(self):
        """ class dealing with implementing morse code output """
        """ Asynchronous, using QTimer as its base class such """
        """ that Qt main loop (user experience) never blocks. """
        super().__init__()
        self.timeout.connect(self.progress) # timer callback
        self.led = LED()

        self.limit = 12 # requirement: transmit max 12 characters
        self.basic = 250 # smallest transmission time (millisecs)
        self.series = []  # actively sending this Morse sequence
        self.blank = False  # actively sending a sequence gap
        self.code = self.morse()

    def morse(self):
        """ create a dict mapping ascii alphabet to morse code """
        # morse alphabet
        di = dit = 1 # dots
        dah = 3      # dash

        # ascii alphabet
        morse = {}
        morse['A'] = [di, dah]
        morse['B'] = [dah, di, di, dit]
        morse['C'] = [dah, di, dah, dit]
        morse['D'] = [dah, di, dit]
        morse['E'] = [dit]
        morse['F'] = [di, di, dah, dit]
        morse['G'] = [dah, dah, dit]
        morse['H'] = [di,di, di, dit]
        morse['I'] = [di, dit]
        morse['J'] = [di, dah, dah, dah]
        morse['K'] = [dah, di, dah]
        morse['L'] = [di, dah, di, dit]
        morse['M'] = [dah, dah]
        morse['N'] = [dah, dit]
        morse['O'] = [dah, dah, dah]
        morse['P'] = [di, dah, dah, dit]
        morse['Q'] = [dah, dah, di, dah]
        morse['R'] = [di, dah, dit]
        morse['S'] = [di, di, dit]
        morse['T'] = [dah]
        morse['U'] = [di, di, dah]
        morse['V'] = [di, di, di, dah]
        morse['W'] = [di, dah, dah]
        morse['X'] = [dah, di, di, dah]
        morse['Y'] = [dah, di, dah, dah]
        morse['Z'] = [dah, dah, di, dit]

        return morse

    def reset(self):
        """ ensure we are not actively transmitting """
        self.stop()
        self.series = []
        self.blank = False

    def transmit_word(self, word):
        """ convert to uppercase and prepare for transmission """
        self.reset()
        if len(word) > 0:
            self.word = word.upper()
            self.word = self.word[0 : self.limit]
            print("XMIT word:", self.word)
            self.transmit_character()

    def transmit_character(self):
        """ initiate first character and remove it from word """
        if len(self.word) == 0:
            self.reset()  # completed this word
            return

        while len(self.word) > 0:
            character = self.word[0]
            self.word = self.word[1:]  # drop this character
            try:
                self.series = self.code[character]
            except KeyError:
                continue
            print("XMIT char:", character, "SEQ", self.series)
            self.start(self.basic)  # go to progress() now
            return

    def progress(self):
        """ transmit a morse code series - chop it as we go """
        self.stop()
        self.led.off()
        if len(self.series) > 0:
            if self.blank:  # send a gap (LED off) between a di/dah
                self.blank = False
                self.start(self.basic)
            else:
                xmit = self.series[0]
                self.series = self.series[1:]  # drop from series
                self.led.on(xmit * self.basic)
                self.blank = True
                self.start(xmit * self.basic)
        elif len(self.word) > 0:
            self.transmit_character()
        else:
            self.reset()


class App(QMainWindow):
    def __init__(self, title):
        """ user interface elements driving the Morse code engine """
        super().__init__()
        self.initUI(title)
        self.led = MorseLED()

    def initUI(self, title):
        self.setWindowTitle(title)
        self.setGeometry(100, 100, 400, 130)
        self.setFixedSize(400, 130)

        # Create textbox
        self.textbox = QLineEdit(self)
        self.textbox.move(20, 20)
        self.textbox.resize(360,40)

        # Create transmit and quit buttons
        self.button = QPushButton('Transmit', self)
        self.button.move(20, 80)
        self.button.clicked.connect(self.click)
        self.finish = QPushButton('Quit', self)
        self.finish.move(280, 80)
        self.finish.clicked.connect(QCoreApplication.instance().quit)

        # Present the completed interface
        self.show()

    def click(self):
        """ handle state change on any radio button """
        value = self.textbox.text().strip()
        self.led.transmit_word(value)


# main
app = QApplication(sys.argv)
me = App('Morse Code LED')
sys.exit(app.exec_())
