import logging
from PySide6.QtCore import QObject, Signal, Slot
from .device import Lamp

class Worker(QObject):
    done = Signal(str, object, str)

    def __init__(self):
        super().__init__()
        self.lamp = Lamp()

    @Slot(str, object)
    def run(self, action, payload):
        try:
            if action == 'connect':
                result = self.lamp.connect(*payload)
            elif action == 'disconnect':
                self.lamp.close()
                result = None
            else:
                result = self.lamp.execute(action, payload)
            self.done.emit(action, result, '')
        except Exception as exc:
            logging.exception('Error en %s', action)
            self.lamp.close()
            self.done.emit(action, None, f'{type(exc).__name__}: {exc}')
