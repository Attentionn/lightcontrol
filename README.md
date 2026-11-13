# LightControl

Un experimento para controlar un foco Magic Home desde una app nativa de Windows.

Tenía un LEDENET AK001-ZJ210 y ganas de ver si podía controlarlo sin depender de la app del celular. El foco respondió por la red local, así que quedó esta interfaz pequeña con PySide6 y `flux_led`.

**Estado: archivado.** Lo dejo aquí como referencia de lo que salió. No hay planes de mantenimiento ni de agregar más dispositivos.

## Qué hace

- Encender y apagar el foco.
- Elegir RGB, blanco cálido y brillo.
- Cargar algunos colores predefinidos.
- Consultar el estado y reconectar si se pierde la conexión.
- Guardar la selección y los datos de conexión entre sesiones.

El modelo usa RGB y blanco cálido en modos separados. Los presets son colores locales, no animaciones del firmware. Aplicar un color puede encender el foco.

## Ejecutar

Windows, Python 3.13 x64 y acceso a la red del foco.

Desde la carpeta del proyecto, ejecuta en PowerShell, en este orden:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-lock.txt
.\.venv\Scripts\python.exe main.py
```

No hace falta activar el entorno. `requirements-lock.txt` fija las versiones del entorno de desarrollo; `requirements.txt` contiene los rangos de las dependencias principales.

## Conectar el foco

En modo AP, conecta la PC al Wi-Fi del foco y usa:

```text
IP:     10.10.123.3
Puerto: 5577 TCP
```

Pulsa **Conectar / Reconectar**. Si el foco ya está conectado al router, usa la IP que le haya asignado y conecta la PC a esa misma red. La app no configura el Wi-Fi del foco.

Seleccionar un color no lo envía: hay que pulsar **Aplicar color / brillo**. La lectura real aparece por separado de los controles. Al reconectar no se vuelve a enviar el último comando.

Los ajustes y registros se guardan en `%LOCALAPPDATA%\LightControl`.

## Build de Windows

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-build.txt
.\.venv\Scripts\python.exe -m PyInstaller --clean --noconfirm LightControl.spec
```

El resultado queda en `dist/LightControl/`. Hay que conservar la carpeta completa, incluido `_internal`.

El build no está firmado. Windows 11 Smart App Control puede bloquear el ejecutable o sus dependencias. Para distribuirlo hace falta resolver la firma de código con un proveedor confiable y revisar también las DLL y extensiones. Un certificado autofirmado no sustituye esa confianza. Ejecutar desde Python es la opción de desarrollo, aunque sus componentes también están sujetos a la protección de Windows.

No es necesario ni se recomienda desactivar Smart App Control. Más información: [firma de código para Smart App Control](https://learn.microsoft.com/en-us/windows/apps/develop/smart-app-control/code-signing-for-smart-app-control).

## Código

```text
main.py                  Inicio y registro de errores
lightcontrol/ui.py       Ventana y reconexión
lightcontrol/worker.py   Operaciones de red en segundo plano
lightcontrol/device.py   Adaptador de flux_led
lightcontrol/settings.py Preferencias locales
LightControl.spec        Configuración de PyInstaller
```

Proyecto limitado a este experimento con el AK001-ZJ210. Puede necesitar ajustes para otros firmwares. No modifica la potencia del foco ni permite superar su brillo máximo.

## Dependencias

- [PySide6 / Qt for Python](https://www.qt.io/qt-for-python)
- [flux_led](https://github.com/beville/flux_led)
- [PyInstaller](https://pyinstaller.org/)

El código de este proyecto se publica bajo MIT. Las dependencias conservan sus propias licencias; consulta sus condiciones antes de redistribuir binarios.
