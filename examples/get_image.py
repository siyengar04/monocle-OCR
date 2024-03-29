import asyncio
import io
import PIL.Image as Image
import time
from brilliant import Monocle
import binascii

remote_script = '''
import bluetooth, camera, time, led
camera.capture()
time.sleep_ms(100)
while data := camera.read(bluetooth.max_length()):
    led.on(led.GREEN)
    while True:
        try:
            bluetooth.send(data)
        except OSError:
            continue
        break
    led.off(led.GREEN)
'''

async def get_image():
    async with Monocle() as m:
        await m.send_command(remote_script)
        return await m.get_all_data()

data = asyncio.run(get_image())
print(data)
img = Image.open(io.BytesIO(data))
img.show()