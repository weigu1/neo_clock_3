""" Neo Clock 3
    weigu.lu

    AI helped with the functions for dst and timezone :)
"""

import machine, neopixel, network, socket, struct, ntptime, utime
from time import sleep, gmtime, localtime

# Constants for display and hardware
DISPL_PIXEL_NR = 8*32
COL_PIXEL_NR = 8
PIN_NEOPIXEL = machine.Pin(2)
PIN_ADC = machine.Pin(26)

# Network and time settings
NTP_HOST = "pool.ntp.org"
TIMEZONE_OFFSET = 1 # Luxembourg UTC + 1

SSID = "xxx"
WIFI_PW = "xxx?"

# Color definitions
OFF = (0,0,0)
RED = (1, 0, 0)
GREEN = (0, 1, 0)
BLUE = (0, 0, 1)
WHITE = (1, 1, 1)
MYCOLOR = GREEN
BRIGHTNESS = [1,4,8]

# Digit patterns for display
DIGITS_5x8 =  {0: [0, 1, 1, 1, 1, 1, 1, 0,
                   1, 0, 0, 0, 0, 0, 0, 1,
                   1, 0, 0, 0, 0, 0, 0, 1,
                   1, 0, 0, 0, 0, 0, 0, 1,
                   0, 1, 1, 1, 1, 1, 1, 0],
               1: [0, 0, 0, 0, 0, 0, 0, 0,
                   1, 0, 0, 0, 0, 0, 0, 1,
                   1, 1, 1, 1, 1, 1, 1, 1,
                   0, 0, 0, 0, 0, 0, 0, 1,
                   0, 0, 0, 0, 0, 0, 0, 0],
               2: [0, 1, 0, 0, 0, 0, 1, 1,
                   1, 0, 0, 0, 0, 1, 0, 1,
                   1, 0, 0, 0, 1, 0, 0, 1,
                   1, 0, 0, 1, 0, 0, 0, 1,
                   0, 1, 1, 0, 0, 0, 0, 1],
               3: [0, 1, 0, 0, 0, 0, 1, 0,
                   1, 0, 0, 0, 0, 0, 0, 1,
                   1, 0, 0, 1, 0, 0, 0, 1,
                   1, 0, 0, 1, 0, 0, 0, 1,
                   0, 1, 1, 0, 1, 1, 1, 0],
               4: [0, 0, 0, 1, 1, 0, 0, 0,
                   0, 0, 1, 0, 1, 0, 0, 0,
                   0, 1, 0, 0, 1, 0, 0, 0,
                   1, 1, 1, 1, 1, 1, 1, 1,
                   0, 0, 0, 0, 1, 0, 0, 0],
               5: [1, 1, 1, 1, 0, 0, 1, 0,
                   1, 0, 0, 1, 0, 0, 0, 1,
                   1, 0, 0, 1, 0, 0, 0, 1,
                   1, 0, 0, 1, 0, 0, 0, 1,
                   1, 0, 0, 0, 1, 1, 1, 0],
               6: [0, 1, 1, 1, 1, 1, 1, 0,
                   1, 0, 0, 1, 0, 0, 0, 1,
                   1, 0, 0, 1, 0, 0, 0, 1,
                   1, 0, 0, 1, 0, 0, 0, 1,
                   0, 1, 0, 0, 1, 1, 1, 0],
               7: [1, 0, 0, 0, 0, 0, 1, 1,
                   1, 0, 0, 0, 0, 1, 0, 0,
                   1, 0, 0, 0, 1, 0, 0, 0,
                   1, 0, 0, 1, 0, 0, 0, 0,
                   1, 1, 1, 0, 0, 0, 0, 0],
               8: [0, 1, 1, 0, 1, 1, 1, 0,
                   1, 0, 0, 1, 0, 0, 0, 1,
                   1, 0, 0, 1, 0, 0, 0, 1,
                   1, 0, 0, 1, 0, 0, 0, 1,
                   0, 1, 1, 0, 1, 1, 1, 0],
               9: [0, 1, 1, 0, 0, 0, 1, 0,
                   1, 0, 0, 1, 0, 0, 0, 1,
                   1, 0, 0, 1, 0, 0, 0, 1,
                   1, 0, 0, 1, 0, 0, 0, 1,
                   0, 1, 1, 1, 1, 1, 1, 0],
              10: [0, 0, 0, 0, 0, 0, 0, 0, # off
                   0, 0, 0, 0, 0, 0, 0, 0,
                   0, 0, 0, 0, 0, 0, 0, 0,
                   0, 0, 0, 0, 0, 0, 0, 0,
                   0, 0, 0, 0, 0, 0, 0, 0]}

DIGIT_1_3x8_0 =  {1: [1, 0, 0, 0, 0, 0, 0, 1,
                      1, 1, 1, 1, 1, 1, 1, 1,
                      0, 0, 0, 0, 0, 0, 0, 1]}

DIGIT_1_3x8_1 =  {1: [1, 0, 0, 0, 0, 0, 0, 1,
                      1, 1, 1, 1, 1, 1, 1, 1,
                      1, 0, 0, 0, 0, 0, 0, 0]}

DIGITS_3x5 = {0: [1, 1, 1, 1, 1, 0, 0, 0,
                  1, 0, 0, 0, 1, 0, 0, 0,
                  1, 1, 1, 1, 1, 0, 0, 0],
              1: [0, 0, 0, 0, 1, 0, 0, 0,
                  1, 1, 1, 1, 1, 0, 0, 0,
                  0, 0, 0, 0, 0, 0, 0, 0],
              2: [1, 0, 0, 1, 1, 0, 0, 0,
                  1, 1, 0, 0, 1, 0, 0, 0,
                  1, 0, 1, 1, 1, 0, 0, 0,],
              3: [1, 0, 0, 0, 1, 0, 0, 0,
                  1, 0, 1, 0, 1, 0, 0, 0,
                  1, 1, 1, 1, 1, 0, 0, 0],
              4: [0, 0, 1, 1, 1, 0, 0, 0,
                  0, 0, 1, 0, 0, 0, 0, 0,
                  1, 1, 1, 1, 1, 0, 0, 0],
              5: [1, 0, 1, 1, 1, 0, 0, 0,
                  1, 0, 1, 0, 1, 0, 0, 0,
                  0, 1, 1, 0, 1, 0, 0, 0],
              6: [1, 1, 1, 1, 1, 0, 0, 0,
                  1, 0, 1, 0, 1, 0, 0, 0,
                  1, 1, 1, 0, 1, 0, 0, 0],
              7: [0, 0, 0, 0, 1, 0, 0, 0,
                  1, 1, 1, 0, 1, 0, 0, 0,
                  0, 0, 0, 1, 1, 0, 0, 0],
              8: [1, 1, 1, 1, 1, 0, 0, 0,
                  1, 0, 1, 0, 1, 0, 0, 0,
                  1, 1, 1, 1, 1, 0, 0, 0],
              9: [1, 0, 1, 1, 1, 0, 0, 0,
                  1, 0, 1, 0, 1, 0, 0, 0,
                  1, 1, 1, 1, 1, 0, 0, 0],
             10: [0, 0, 0, 0, 0, 0, 0, 0, # off
                  0, 0, 0, 0, 0, 0, 0, 0,
                  0, 0, 0, 0, 0, 0, 0, 0]}

def is_dst_eu(year, month, day):
    """Returns True if DST is in effect in Europe for the given date."""
    if month < 3 or month > 10:
        return False
    if month > 3 and month < 10:
        return True
    if month == 3:    # March: last Sunday
        last_day = 31 # Find the last Sunday in March
        dow = utime.localtime(utime.mktime((year, 3, last_day, 0, 0, 0, 0, 0, 0)))[6]
        last_sunday = last_day - dow
        return day >= last_sunday
    if month == 10: # October: last Sunday
        last_day = 31
        dow = utime.localtime(utime.mktime((year, 10, last_day, 0, 0, 0, 0, 0, 0)))[6]
        last_sunday = last_day - dow
        return day <= last_sunday
    return False


def set_rtc_with_timezone_and_dst(utc_time, std_offset):
    """ Sets RTC with DST-aware local time. """
    year, month, day, *_ = utc_time
    if is_dst_eu(year, month, day):
        offset = std_offset + 1  # DST is UTC+1 more than standard
    else:
        offset = std_offset
    utc_seconds = utime.mktime(utc_time)
    local_seconds = utc_seconds + (offset * 3600)
    local_time = utime.localtime(local_seconds)
    rtc = machine.RTC()
    rtc.datetime((local_time[0], local_time[1], local_time[2],
                  local_time[6] + 1, local_time[3],
                  local_time[4], local_time[5], 0))
    print("RTC set to local time (DST-aware):", rtc.datetime())

def connect():
    """ Connect to WiFi """
    max_wait = 10 # in seconds
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, WIFI_PW)
    while max_wait > 0:
        if wlan.status() < 0 or wlan.status() >= 3:
            break
        max_wait -= 1
        print('waiting for connection...')
        sleep(1)
    if wlan.status() != 3:
        raise RuntimeError('network connection failed')
    else:
        print('connected')
        status = wlan.ifconfig()
        print( 'ip = ' + status[0] )

def display_clear():
    """ Clear all pixels. """
    for i in range(0, DISPL_PIXEL_NR, 1):
        np[i] = OFF
    np.write()

def write_digit_5x8(nr, offset = 0, color = RED):
    """ Draw 5x8 digit at offset. """
    p_offset = offset*COL_PIXEL_NR
    if offset%2: # starting with even column
        for i in range(0,3):
            for j in range(i*16 + 7 + p_offset, i*16 - 1 + p_offset, -1):
                if DIGITS_5x8[nr][(7+i*32)-(j-p_offset)]:
                    np[j] = color
        for i in range(0,2):
            for j in range(i*16 + 8 + p_offset, i*16 + 16 +p_offset, 1):
                if DIGITS_5x8[nr][j-p_offset]:
                    np[j] = color
    else: # starting with odd column
        for i in range(0,3):
            for j in range(i*16 + p_offset, i*16 + 8 + p_offset, 1):
                if DIGITS_5x8[nr][j-p_offset]:
                    np[j] = color
        for i in range(0,2):
            for j in range(i*16 + 15 + p_offset, i*16 + 7 + p_offset, -1):
                if DIGITS_5x8[nr][(23+i*32)-(j-p_offset)]:
                    np[j] = color
    np.write()

def write_colon_5x8(offset = 0, color = RED):
    """ Draw colon symbol at offset. """
    p_offset = offset*COL_PIXEL_NR
    np[p_offset+2] = color
    np[p_offset+5] = color
    np.write()

def write_1_first_pos(offset = 0, color = RED):
    """ Draw digit '1' in first or second column. """
    if offset == 0:
        for i in range(0,24):
            if DIGIT_1_3x8_0[1][i]:
                np[i] = color
    else:
        for i in range(8,32):
            if DIGIT_1_3x8_1[1][i-8]:
                np[i] = color
    np.write()

def write_digit_3x5(nr, offset = 0, color = RED):
    """ Draw 3x5 digit at offset. """
    p_offset = offset*COL_PIXEL_NR
    if offset%2: # starting with even column
        for i in range(0,2):
            for j in range(i*16 + 4 + p_offset, i*16 - 1 + p_offset, -1):
                if DIGITS_3x5[nr][j-p_offset]:
                    np[j] = color
        for j in range(11 + p_offset, 16 +p_offset, 1):
            if DIGITS_3x5[nr][p_offset + 23 -j]:
                np[j] = color
    else: # starting with odd column
        for i in range(0,2):
            for j in range(i*16 + 3 + p_offset, i*16 + 8 + p_offset, 1):
                if DIGITS_3x5[nr][i*32+7+p_offset-j]:
                    np[j] = color
        for j in range(12 + p_offset, 7 + p_offset, -1):
            if DIGITS_3x5[nr][j-p_offset]:
                np[j] = color
    np.write()

def get_brightness():
    """ Read LDR and calculate brightness. """
    lum_adc = ldr.read_u16()
    lum = int(256-lum_adc*256/65536)
    if lum > 200:
        brightness = BRIGHTNESS[2]
    elif lum < 100:
        brightness = BRIGHTNESS[0]
    else:
        brightness = BRIGHTNESS[1]
    return brightness

def draw_clock():
    """ Update only changed digits """
    if hour//10 != 1:
        write_1_first_pos(1, OFF)
    else:
        write_1_first_pos(1, mycolor)
    if hour%10 != time_prev[1]:
        write_digit_5x8(time_prev[1], 5, OFF)
        write_digit_5x8(hour%10, 5, mycolor)
    write_colon_5x8(11, mycolor)
    if min//10 != time_prev[2]:
        write_digit_5x8(time_prev[2], 13, OFF)
        write_digit_5x8(min//10, 13, mycolor)
    if min%10 != time_prev[3]:
        write_digit_5x8(time_prev[3], 19, OFF)
        write_digit_5x8(min%10, 19, mycolor)
    if sec//10 != time_prev[4]:
        write_digit_3x5(time_prev[4], 25, OFF)
        write_digit_3x5(sec//10, 25, mycolor)
    if sec%10 != time_prev[5]:
        write_digit_3x5(time_prev[5], 29, OFF)
        write_digit_3x5(sec%10, 29, mycolor)

def draw_whole_clock():
    """ Redraw all digits """
    if hour//10 != 1:
        write_1_first_pos(1, OFF)
    else:
        write_1_first_pos(1, mycolor)
    write_digit_5x8(time_prev[1], 5, OFF)
    write_digit_5x8(hour%10, 5, mycolor)
    write_colon_5x8(11, mycolor)
    write_digit_5x8(time_prev[2], 13, OFF)
    write_digit_5x8(min//10, 13, mycolor)
    write_digit_5x8(time_prev[3], 19, OFF)
    write_digit_5x8(min%10, 19, mycolor)
    write_digit_3x5(time_prev[4], 25, OFF)
    write_digit_3x5(sec//10, 25, mycolor)
    write_digit_3x5(time_prev[5], 29, OFF)
    write_digit_3x5(sec%10, 29, mycolor)

# Setup
np = neopixel.NeoPixel(PIN_NEOPIXEL, DISPL_PIXEL_NR)
ldr = machine.ADC(PIN_ADC)
connect()
ntptime.settime()
rtc = machine.RTC()
utc_time = utime.gmtime()
set_rtc_with_timezone_and_dst(utc_time, TIMEZONE_OFFSET)
display_clear()
time_prev = [10,10,10,10,10,10]
brightness_prev = 10

# Main loop: update display every second
while True:
    now_time = rtc.datetime()
    month = now_time[1]
    day = now_time[2]
    hour = now_time[4]
    min = now_time[5]
    sec = now_time[6]
    # check ntp once a day
    if now_time[4] == 3 and now_time[5] == 5 and now_time[6] == 0:
        try:
            ntptime.settime()   # Sync RTC with NTP (UTC)
            utc_time = utime.gmtime()
            set_rtc_with_timezone_and_dst(utc_time, TIMEZONE_OFFSET)
            sleep(1)
        except:
            pass
    hour = hour%12
    brightness = get_brightness()
    mycolor = tuple([brightness*x for x in MYCOLOR])
    if brightness_prev != brightness:
        draw_whole_clock()
    else:
        draw_clock()
    brightness_prev = brightness
    time_prev = [hour//10, hour%10, min//10, min%10, sec//10, sec%10]
    sleep(0.1)


