from PySide6.QtCore import QThread, QTimer, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QSpinBox, QSlider, QComboBox, QCheckBox,
    QColorDialog, QGroupBox)
from PySide6.QtCore import Qt
from . import settings
from .worker import Worker

PRESETS = [('Ámbar cálido', [255, 150, 60]), ('Lectura RGB', [255, 210, 160]),
           ('Azul', [35, 85, 255]), ('Rosa', [255, 45, 130])]

class Window(QMainWindow):
    request = Signal(str, object)

    def __init__(self):
        super().__init__()
        self.values = settings.load()
        self.busy = self.connected = self.closing = False
        self.want_connection = False
        self.failures = 0
        self.setWindowTitle('LightControl 0.1 · LEDENET')
        self.resize(540, 570)
        root = QWidget(); layout = QVBoxLayout(root); self.setCentralWidget(root)
        title = QLabel('LightControl'); title.setStyleSheet('font-size:28px;font-weight:600')
        layout.addWidget(title)
        layout.addWidget(QLabel('AK001-ZJ210 · Control local por Wi-Fi'))
        row = QHBoxLayout(); layout.addLayout(row)
        self.host = QLineEdit(self.values['host']); self.host.setPlaceholderText('IP del foco')
        self.port = QSpinBox(); self.port.setRange(1, 65535); self.port.setValue(self.values['port'])
        row.addWidget(self.host); row.addWidget(self.port)
        row = QHBoxLayout(); layout.addLayout(row)
        self.connect_button = QPushButton('Conectar / Reconectar')
        self.disconnect_button = QPushButton('Desconectar')
        row.addWidget(self.connect_button); row.addWidget(self.disconnect_button)
        self.auto = QCheckBox('Reconectar automáticamente'); self.auto.setChecked(self.values['auto'])
        layout.addWidget(self.auto)
        self.status = QLabel('Desconectado'); self.status.setWordWrap(True); layout.addWidget(self.status)
        self.observed = QLabel('Estado del foco: —'); self.observed.setWordWrap(True); layout.addWidget(self.observed)
        self.controls = QGroupBox('Controles'); box = QVBoxLayout(self.controls); layout.addWidget(self.controls)
        row = QHBoxLayout(); box.addLayout(row)
        for label, value in [('Encender', True), ('Apagar', False)]:
            button = QPushButton(label); row.addWidget(button)
            button.clicked.connect(lambda checked=False, v=value: self.send('power', v))
        self.mode = QComboBox(); self.mode.addItems(['RGB', 'Blanco cálido']); self.mode.setCurrentText(self.values['mode']); box.addWidget(self.mode)
        self.color = QPushButton(); self.update_color(); box.addWidget(self.color)
        self.rgb = []
        row = QHBoxLayout(); box.addLayout(row)
        for index, name in enumerate(('R', 'G', 'B')):
            row.addWidget(QLabel(name)); spin = QSpinBox(); spin.setRange(0, 255); spin.setValue(self.values['rgb'][index]); row.addWidget(spin); self.rgb.append(spin)
            spin.valueChanged.connect(self.rgb_changed)
        self.brightness = self.slider(box, 'Brillo', self.values['brightness'])
        self.white = self.slider(box, 'Nivel blanco cálido', self.values['white'])
        self.preset = QComboBox(); self.preset.addItems([p[0] for p in PRESETS]); self.preset.setCurrentIndex(self.values['preset']); box.addWidget(self.preset)
        preset_button = QPushButton('Cargar preset'); box.addWidget(preset_button)
        apply_button = QPushButton('Aplicar color / brillo'); box.addWidget(apply_button)
        refresh = QPushButton('Consultar estado'); box.addWidget(refresh)
        note = QLabel('Los controles muestran tu selección; “Estado del foco” muestra la lectura real.\nAplicar color puede encender el foco. Los presets son colores locales.'); note.setWordWrap(True); layout.addWidget(note)
        layout.addStretch()
        self.thread = QThread(self); self.worker = Worker(); self.worker.moveToThread(self.thread)
        self.request.connect(self.worker.run); self.worker.done.connect(self.finished)
        self.thread.finished.connect(self.worker.deleteLater); self.thread.start()
        self.timer = QTimer(self); self.timer.setInterval(5000); self.timer.timeout.connect(self.tick); self.timer.start()
        self.connect_button.clicked.connect(self.connect_lamp)
        self.disconnect_button.clicked.connect(self.disconnect_lamp)
        self.color.clicked.connect(self.choose_color)
        preset_button.clicked.connect(self.load_preset)
        apply_button.clicked.connect(lambda: self.send('apply', self.collect()))
        refresh.clicked.connect(lambda: self.send('refresh', None))
        self.update_enabled()

    def slider(self, box, name, value):
        label = QLabel(f'{name}: {value}%'); box.addWidget(label)
        slider = QSlider(Qt.Orientation.Horizontal); slider.setRange(0, 100); slider.setValue(value); box.addWidget(slider)
        slider.valueChanged.connect(lambda v: label.setText(f'{name}: {v}%'))
        return slider

    def update_color(self):
        rgb = self.values['rgb']; self.color.setText('Elegir color · #' + ''.join(f'{v:02X}' for v in rgb))

    def rgb_changed(self):
        self.values['rgb'] = [s.value() for s in self.rgb]; self.update_color()

    def choose_color(self):
        color = QColorDialog.getColor(QColor(*self.values['rgb']), self)
        if color.isValid():
            for spin, value in zip(self.rgb, color.getRgb()[:3]): spin.setValue(value)

    def load_preset(self):
        self.mode.setCurrentText('RGB')
        for spin, value in zip(self.rgb, PRESETS[self.preset.currentIndex()][1]): spin.setValue(value)

    def collect(self):
        self.values.update(host=self.host.text().strip(), port=self.port.value(),
            brightness=self.brightness.value(), white=self.white.value(), mode=self.mode.currentText(),
            auto=self.auto.isChecked(), preset=self.preset.currentIndex())
        return dict(self.values)

    def persist(self):
        try: settings.save(self.collect())
        except OSError as exc: self.status.setText(f'No se pudieron guardar ajustes: {exc}')

    def update_enabled(self):
        self.controls.setEnabled(self.connected and not self.busy and not self.closing)
        self.connect_button.setEnabled(not self.busy and not self.closing)
        self.disconnect_button.setEnabled(not self.busy and not self.closing)
        self.host.setEnabled(not self.busy); self.port.setEnabled(not self.busy)

    def send(self, action, payload):
        if self.busy: return
        self.busy = True; self.update_enabled(); self.request.emit(action, payload)

    def connect_lamp(self):
        if not self.host.text().strip():
            self.status.setText('Escribe una IP o nombre de host.'); return
        self.want_connection = True; self.status.setText('Conectando…'); self.persist()
        self.send('connect', (self.host.text().strip(), self.port.value()))

    def disconnect_lamp(self):
        self.want_connection = False; self.send('disconnect', None)

    def finished(self, action, state, error):
        self.busy = False
        if self.closing:
            if action != 'disconnect': self.send('disconnect', None); return
            self.thread.quit(); self.thread.wait(); self.close(); return
        if error:
            self.connected = False; self.failures += 1
            self.status.setText(f'Sin conexión · {error}\nComprueba el Wi-Fi del foco y la IP. No se reenvió el comando.')
        elif action == 'disconnect':
            self.connected = False; self.status.setText('Desconectado'); self.observed.setText('Estado del foco: —')
        else:
            self.connected = True; self.failures = 0
            self.status.setText(f'Conectado · modelo {state["model"]} · {state["protocol"]}')
            self.observed.setText(f'Estado del foco: {"encendido" if state["power"] else "apagado"} · RGB {tuple(state["rgb"])} · canal blanco {"disponible" if state["white"] else "no anunciado"}')
            self.mode.model().item(1).setEnabled(state['white'])
            if not state['white']: self.mode.setCurrentText('RGB')
        self.timer.setInterval(min(30000, 5000 * 2 ** min(self.failures, 3)))
        self.update_enabled()

    def tick(self):
        if self.busy or self.closing: return
        if self.connected: self.send('refresh', None)
        elif self.want_connection and self.auto.isChecked(): self.connect_lamp()

    def closeEvent(self, event):
        if not self.thread.isRunning(): event.accept(); return
        event.ignore()
        if self.closing: return
        self.closing = True; self.want_connection = False; self.timer.stop(); self.persist()
        self.status.setText('Cerrando conexión…'); self.update_enabled()
        if not self.busy: self.send('disconnect', None)
