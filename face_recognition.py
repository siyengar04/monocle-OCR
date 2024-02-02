import asyncio
import io
import PIL.Image as Image
import time
from brilliant import *
import binascii
import cv2
import webbrowser
from urllib.parse import urlparse
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

remote_script = '''
import bluetooth, camera, time, led, touch, display
text = display.Text('Waiting...', 100, 0, display.WHITE, justify=display.TOP_LEFT)
display.show(text)
def trigger_capture(button):
    len = bluetooth.max_length()
    text = display.Text('Capturing...', 100, 0, display.WHITE, justify=display.TOP_LEFT)
    display.show(text)
    camera.capture()
    time.sleep_ms(100)
    while data := camera.read(bluetooth.max_length() - 4):
        led.on(led.GREEN)
        while True:
            try:
                bluetooth.send((b"img:" + data)[:len])
            except OSError:
                continue
            break
    led.off(led.GREEN)
    bluetooth.send(b'end:')
    done = display.Text('Done', 100, 0, display.WHITE, justify=display.TOP_LEFT)
    display.show(done)
touch.callback(touch.EITHER, trigger_capture)
'''



async def get_image():
    async with Monocle() as m:
        await m.send_command(remote_script)
        await ev.wait()
        data = await m.get_all_data()
        return data
            
        

async def detect():
    image = cv2.imread('output.jpg')
    # Convert the image to gray scale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # Performing OCR
    text = pytesseract.image_to_string(gray, config='--psm 3')
    
    if text:
        print("Detected text:")
        print(text)
        return text
    else:
        print("No text found in the image.")
        return "no data found"
async def display(data):
    async with Monocle() as m:
        await m.send_command(f"import display \ntext = display.Text('{data}', 100, 0, display.WHITE, justify=display.TOP_LEFT) \ndisplay.show(text)")
        
async def check(data):
    try:
        result = urlparse(data)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False

async def display_text_on_monocle(detected_text):
    command_to_display_text = f'''
import display
text = display.Text('{detected_text}', 100, 0, display.WHITE, justify=display.TOP_LEFT)
display.show(text)
'''
    async with Monocle() as m:
        await m.send_command(command_to_display_text)

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

async def detect_faces(image_path):
    image = cv2.imread(image_path)
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray_image, scaleFactor=1.1, minNeighbors=5)
    
    # For simplicity, we'll just return the number of faces detected
    num_faces_detected = len(faces)
    return num_faces_detected


async def main():
    while True:
        data = await get_image()
        img = Image.open(io.BytesIO(data))
        jpgImg = img.convert('RGB')
        jpgImg.save('output.jpg')
        detected_text = await detect()
        num_faces = await detect_faces('output.jpg')
        
        # You can now display the detected text and number of faces on the Monocle
        await display_text_on_monocle(f"Text: {detected_text}, Faces: {num_faces}")
        ev.clear()

asyncio.run(main())