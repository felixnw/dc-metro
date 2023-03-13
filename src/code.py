# DC Metro Board
from time import sleep
from config import config
from train_board import TrainBoard
from metro_api import MetroApi, MetroApiOnFireException
import busio
import board
from digitalio import DigitalInOut
import neopixel
from adafruit_esp32spi import adafruit_esp32spi
from adafruit_esp32spi import adafruit_esp32spi_wifimanager
from supervisor import reload

# Get wifi details and more from a secrets.py file
try:
    from secrets import secrets
except ImportError:
    print("WiFi secrets missing!")
    raise

# Set up the network connection
esp32_cs = DigitalInOut(board.ESP_CS)
esp32_ready = DigitalInOut(board.ESP_BUSY)
esp32_reset = DigitalInOut(board.ESP_RESET)
spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
esp = adafruit_esp32spi.ESP_SPIcontrol(spi, esp32_cs, esp32_ready, esp32_reset)
status_light = neopixel.NeoPixel(board.NEOPIXEL, 1, brightness=0.2)
wifi = adafruit_esp32spi_wifimanager.ESPSPI_WiFiManager(esp, secrets, status_light)

if esp.status == adafruit_esp32spi.WL_IDLE_STATUS:
    print("ESP32 found and in idle mode")
print("Firmware vers.", esp.firmware_version)

print("Connecting to AP...")
while not esp.is_connected:
    try:
        esp.connect_AP(secrets['ssid'], secrets['password'])
    except OSError as e:
        print("Could not connect to AP, retrying: ", e)
        continue
print("Connected to", str(esp.ssid, 'utf-8'), "\tRSSI: ", esp.rssi)
print("Pinging google.com to establish proof of connectivity: %d ms" % esp.ping("google.com"))

station_code = config['metro_station_code']
refresh_interval = config['refresh_interval']
api = MetroApi()

# Refresh train information and deal with errors
def refresh_trains() -> [dict]:
    try:
        trains = api.fetch_train_predictions(wifi, station_code)
    except MetroApiOnFireException:
        print('WMATA API is currently on fire. Perhaps reloading will help...')
        reload()  # equivalent to using CTRL-D in a serial console
        return None
    return trains

train_board = TrainBoard(refresh_trains)

# MAIN LOOP: Call the the API every [refresh_interval] seconds
while True:
    print("Starting main loop...")
    train_board.refresh()
    sleep(refresh_interval)
