import os, sys
import re
import subprocess
from datetime import datetime, timedelta

SWAYBAR_PATH = os.path.join(os.getenv('HOME'), '.swaybar')

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

# ---------------- COUNTDOWN ----------------

'''
COUNTDOWN file format:
start_time_epoch;duration_in_seconds
'''
COUNTDOWN_FILE_PATH = os.path.join(SWAYBAR_PATH, 'cron')
def get_countdown():
    if os.path.isfile(COUNTDOWN_FILE_PATH):
        with open(COUNTDOWN_FILE_PATH, 'r') as f:
            ts, duration = f.read().split(';')
            start = datetime.fromtimestamp(float(ts))
            duration = timedelta(seconds=int(duration))
        now = datetime.now()
        if (start + duration) < now:
            # Countdown already finished
            return None
        else:
            delta = (now - start)
            r = duration - delta
            hours = int(r.seconds / 3600)
            minutes = int((r.seconds - (hours * 3600)) / 60)
            seconds = r.seconds % 60
            return f'{hours}:{minutes}:{seconds}'
    return None

def set_countdown(cd):
    with open(COUNTDOWN_FILE_PATH, 'w') as f:
        now = datetime.now().timestamp()
        f.write(f'{now};{cd}')


def gen_swaybar_string():
    sb_elems = []
    # COUNTDOWN
    cd = get_countdown()
    if cd is not None:
        sb_elems.append(f'⏳ {cd}')
        sb_elems.append(f'--')
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
    if len(sys.argv) == 3:
        if sys.argv[1] == 'set_countdown':
            try:
                cd = int(sys.argv[2])
                set_countdown(cd)
            except:
                pass
    print(gen_swaybar_string())
