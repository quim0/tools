import argparse
import os, math

BACKLIGHT_PATH = '/sys/class/backlight/'
BRIGHTNESS_PATH = None

def get_bright_path():
    global BRIGHTNESS_PATH
    if BRIGHTNESS_PATH is not None:
        return BRIGHTNESS_PATH

    for f in os.listdir(BACKLIGHT_PATH):
        f = os.path.join(BACKLIGHT_PATH, f)
        if os.path.isdir(f):
            BRIGHTNESS_PATH = os.path.join(BACKLIGHT_PATH, f)
            return BRIGHTNESS_PATH

POSSIBLE_BRIGHTNESS_FILES = map(
    lambda x: os.path.join(get_bright_path(), x),
    ['actual_brightness', 'brightness']
    )
BRIGHTNESS_FILE = None

def check_bits(f):
    # Checks if file is writable
    w_mask = 0b010000000
    bits = os.stat(f).st_mode
    return (bits & w_mask) != 0

def get_brightness_file():
    global BRIGHTNESS_FILE
    if BRIGHTNESS_FILE is not None:
        return BRIGHTNESS_FILE

    for f in POSSIBLE_BRIGHTNESS_FILES:
        if check_bits(f):
            BRIGHTNESS_FILE = f
            return BRIGHTNESS_FILE

def get_curr_brightness():
    with open(get_brightness_file(), 'r') as f:
        return f.read()

MAX_BRIGHTNESS_FILE = os.path.join(
    get_bright_path(), 
    'max_brightness'
    )

def get_max_brightness():
    with open(MAX_BRIGHTNESS_FILE, 'r') as f:
        return f.read()

def set_brightness(val):
    val = str(val)
    with open(get_brightness_file(), 'w') as f:
        f.write(val)

def main():
    parser = argparse.ArgumentParser('Adjust screen brightness.')
    eg = parser.add_mutually_exclusive_group()
    eg.add_argument('--up', 
        dest='up', 
        action='store_true',
        default=False,
        help='Brightness up')
    eg.add_argument('--down',
        dest='down',
        action='store_true',
        default=False,
        help='Brightness down')
    eg.add_argument('--max',
        dest='max_arg',
        action='store_true',
        default=False,
        help='Set brightness to maximum')
    eg.add_argument('--min',
        dest='min_arg',
        action='store_true',
        default=False,
        help='Set brightness to minimum')
    args = parser.parse_args()

    max_brightness = int(get_max_brightness())
    curr_brightness = int(get_curr_brightness())
    step = math.ceil(max_brightness / 10)

    if args.max_arg:
        set_brightness(get_max_brightness())
    elif args.min_arg:
        set_brightness(step)
    elif args.up:
        if (curr_brightness + step) > max_brightness:
            set_brightness(max_brightness)
        else:
            set_brightness(curr_brightness + step)
    elif args.down:
        if curr_brightness < step*2:
            set_brightness(step)
        else:
            set_brightness(curr_brightness - step)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
