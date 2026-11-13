"""Only this module knows flux_led. All calls belong to one worker thread."""
from flux_led import WifiLedBulb
from flux_led.const import COLOR_MODE_DIM
import time

class Lamp:
    def __init__(self, factory=WifiLedBulb):
        self.factory = factory
        self.bulb = None

    def close(self):
        if self.bulb is not None:
            self.bulb.close()
            self.bulb = None

    def connect(self, host, port):
        self.close()
        self.bulb = self.factory(host, port=port, timeout=2)
        return self.state(refresh=False)

    def state(self, refresh=True):
        if self.bulb is None:
            raise ConnectionError('Conecta primero el foco.')
        if refresh:
            self.bulb.update_state(retry=0)
        if not self.bulb.available:
            raise ConnectionError('El foco no respondió con un estado válido.')
        return dict(power=bool(self.bulb.is_on), rgb=list(self.bulb.rgb),
                    model=self.bulb.model_num, protocol=str(self.bulb.protocol),
                    white=self.supports_white())

    def supports_white(self):
        return bool(self.bulb.rgbwcapable or COLOR_MODE_DIM in self.bulb.color_modes)

    def execute(self, action, values):
        if self.bulb is None:
            raise ConnectionError('Sin conexión.')
        if action == 'power':
            (self.bulb.turnOn if values else self.bulb.turnOff)(retry=0)
        elif action == 'apply':
            level = values['brightness'] / 100
            if values['mode'] == 'RGB':
                rgb = [round(v * level) for v in values['rgb']]
                self.bulb.setRgb(*rgb, persist=False, retry=0)
            else:
                if not self.supports_white():
                    raise ValueError('Este firmware no anuncia canal blanco cálido dedicado. Usa RGB cálido.')
                self.bulb.setWarmWhite255(round(255 * values['white'] / 100 * level), persist=False, retry=0)
        elif action != 'refresh':
            raise ValueError('Acción desconocida.')
        if action != 'refresh':
            time.sleep(0.2)
        return self.state()
