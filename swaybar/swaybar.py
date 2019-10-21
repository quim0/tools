import os
import re
import subprocess
from datetime import datetime

BATTERY_PATH_ROOT = '/sys/class/power_supply/'
BATTERY_PATH = None

def get_battery_path(): 
    global BATTERY_PATH
    if BATTERY_PATH is not None:
        return BATTERY_PATH

    for f in os.listdir(BATTERY_PATH_ROOT):
        f = os.path.join(BATTERY_PATH_ROOT, f)
        if os.path.isdir(f):
            BATTERY_PATH = os.path.join(BATTERY_PATH_ROOT, f)
            return BATTERY_PATH

BATTERY_STATUS_FILE = os.path.join(
    get_battery_path(),
    'status'
    )

def get_battery_status():
    with open(BATTERY_STATUS_FILE, 'r') as f:
        res = f.read().strip('\n')
        if res in ['Charging', 'Full']:
            return '🔌'
        if res == 'Discharging':
            return '🔋'
        return '?'

BATTERY_PERCENTAGE_FILE = os.path.join(
    get_battery_path(),
    'capacity'
    )

def get_battery_percentage():
    with open(BATTERY_PERCENTAGE_FILE, 'r') as f:
        return int(f.read())

BATTERY_ALARM_FILE = os.path.join(
    get_battery_path(),
    'alarm'
    )

def get_battery_alarm():
    with open(BATTERY_ALARM_FILE, 'r') as f:
        return int(f.read()) != 0

# ---------------- WIFI ----------------

INTERFACE = 'wlp2s0'
GET_SSID_CMD = f'iw dev {INTERFACE} info'

def get_wifi_ssid():
    # TODO: Get a better implementation
    output = subprocess.check_output(GET_SSID_CMD.split())
    results = re.findall(b'ssid (.+)', output)
    if len(results) == 0:
        return b''

    return results[0]

# ---------------- DATE ----------------

def get_date():
    now = datetime.now()
    return now.strftime('%d-%m-%Y %H:%M:%S')

def gen_swaybar_string():
    sb_elems = []
    # WIFI
    ssid = get_wifi_ssid().decode('utf-8')
    if len(ssid) > 0:
        sb_elems.append(f'WIFI [{ssid}]')
        sb_elems.append('--')
    # BATTERY
    if get_battery_alarm():
        sb_elems.append('[!]')
    sb_elems.append(str(get_battery_percentage()) + '%')
    sb_elems.append('(' + get_battery_status() + ')')
    sb_elems.append('--')
    # DATE
    sb_elems.append(get_date())

    return ' '.join(sb_elems)

if __name__ == '__main__':
    print(gen_swaybar_string())
