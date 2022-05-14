import os, socket, netifaces, shutil, time, psutil #Python libraries
from datetime import timedelta
import I2C_LCD_driver#, filesize #Local libraries

'''Gets the local network IP address'''
def ip():
    netifaces.ifaddresses('eth0')
    ip = netifaces.ifaddresses('eth0')[netifaces.AF_INET][0]['addr']
    return ip

'''Get the disk space used on the drives'''
def disk_usage():
    used = shutil.disk_usage("/mnt/md0").used #Get the disk space used
    total = shutil.disk_usage("/mnt/md0").total #Get the total disk space
    percentage = round(((int(used)/int(total))*100), 1) #Get the percentage of the space used
    usage = "{}/{} {}%".format(size(used), size(total), percentage) #Put it into a string
    return usage

suffixes = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
def size(nbytes):
    i = 0
    while nbytes >= 1024 and i < len(suffixes)-1:
        nbytes /= 1024.
        i += 1
    f = float(('%.2f' % nbytes).rstrip('0').rstrip('.'))
    if not (suffixes[i] == "TB") or (suffixes[i] == "PB"):
        f = int(round(f, 0))
    else:
        f = round(f, 1)
    return '%s%s' % (str(f), suffixes[i])
    
suffixes = ['B/s', 'KB/s', 'MB/s', 'GB/s', 'TB/s', 'PB/s']
def write_speed(nbytes):
    i = 0
    while nbytes >= 1024 and i < len(suffixes)-1:
        nbytes /= 1024.
        i += 1
    f = float(('%.2f' % nbytes).rstrip('0').rstrip('.'))
    f = round(f, 3)
    return '%s%s' % (str(f), suffixes[i])

'''Formats the CPU usage from psutils'''
def cpu_usage():
    return "CPU: {}%".format(round(psutil.cpu_percent(), 1))

'''Formats the memory usage from psutils'''
def memory_usage():
    return "RAM: {}%".format(int(round(psutil.virtual_memory().available * 100 / psutil.virtual_memory().total, 0)))

'''Prettify the uptime'''
def pretty_time_delta(seconds):
    sign_string = '-' if seconds < 0 else ''
    seconds = abs(int(seconds))
    days, seconds = divmod(seconds, 86400)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)
    if days > 0:
        if minutes < 10:
            return '%s%dd %dh %dm ' % (sign_string, days, hours, minutes)
        return '%s%dd %dh %dm' % (sign_string, days, hours, minutes)
    elif hours > 0:
        return '%s%dh %dm %ds ' % (sign_string, hours, minutes, seconds)
    elif minutes > 0:
        return '%s%dm %ds ' % (sign_string, minutes, seconds)
    else:
        return '%s%dseconds ' % (sign_string, seconds)

def uptime():
    with open('/proc/uptime', 'r') as f:
        uptime_seconds = float(f.readline().split()[0])
        uptime_string = pretty_time_delta(uptime_seconds)
    return uptime_string

def centre_message(message):
    message_length = round(len(message), 0)
    try:
        return int(10-(message_length/2))
    except:
        print("Too long")
        return 0

def display_uptime():
    up_print = (f"Uptime: {uptime()}")
    if int(centre_message(up_print)) != 0:
        mylcd.lcd_display_string(" {}".format(up_print), 4, int(centre_message(up_print)-1))
    else:
        mylcd.lcd_display_string(up_print, 4, int(centre_message(up_print)))

hostname = socket.gethostname() 

mylcd = I2C_LCD_driver.lcd() #Initialise the I2C display driver
mylcd.lcd_clear() #Clear the display from previous code

host_print = (f"Name: {hostname}")
ip_print = (f"IP: {ip()} ")

blank = "                      "

x = 0

while x<100:

    '''Swaps the name and IP on the top of the display every 10 seconds'''
    if int(round(x/10, 1)%2) == 0:
        mylcd.lcd_display_string(host_print, 1, int(centre_message(host_print)))
    else:
        mylcd.lcd_display_string(ip_print, 1, int(centre_message(ip_print)))

    '''Display the system uptime'''
    if "s" in uptime(): #If the seconds are shown, display every second
        display_uptime()
    else: #If the seconds aren't shown, display every 30 seconds
        if int(round(x/30, 1)%2) == 0:
            display_uptime()

    '''Display the system usage every second'''
    if (x == 30) or (x == 60):
        mylcd.lcd_display_string(blank, 3)
    if int(round(x/30, 1)%2) == 0:
        usage = "{} {}".format(cpu_usage(), memory_usage())
        if int(centre_message(usage)) == 1:
            mylcd.lcd_display_string(" {}".format(usage), 3, int(centre_message(usage)-1))
        else:
            mylcd.lcd_display_string(usage, 3, int(centre_message(usage)))
    else:
        speed = (f"Write Speed: {write_speed()}")
        mylcd.lcd_display_string(speed, 3, int(centre_message(speed))) 

    '''Displays the current disk usage space'''
    if int(round(x/30, 1)%2) == 0: #Update every 30 seconds
        disk_print = (f"{disk_usage()}")
        mylcd.lcd_display_string(disk_print, 2, int(centre_message(disk_print))) 

    x = x + 1
    if x == 60:
        x = 0
        #mylcd.lcd_clear()
        #for i in range(1, 4):
        #    mylcd.lcd_display_string("Cleaning Display", i, int(centre_message("Cleaning Display")))
    time.sleep(1)