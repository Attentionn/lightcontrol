import logging
import sys
from logging.handlers import RotatingFileHandler
from PySide6.QtWidgets import QApplication
from lightcontrol.settings import data_dir
from lightcontrol.ui import Window

def main():
    directory = data_dir(); directory.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(level=logging.INFO, handlers=[RotatingFileHandler(
        directory / 'lightcontrol.log', maxBytes=500_000, backupCount=2, encoding='utf-8')])
    app = QApplication(sys.argv); app.setApplicationName('LightControl')
    window = Window(); window.show()
    return app.exec()

if __name__ == '__main__':
    sys.exit(main())
