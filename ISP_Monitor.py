"""
Monitor Internet connection, logging failures
"""
from msvcrt import kbhit, getch
import os
import platform
import subprocess
import time

log_file_name = 'ISP_Monitor.log'
host = '8.8.8.8'    # Google DNS
monitor_timeout = 4 # Check every 4+1 seconds
reconnect_time = 1  # Check for reconnect every second

def pingOk(sHost, timeout):
    num_switch= 'n' if platform.system().lower()=="windows" else 'c'
    try:
        output = subprocess.check_output(
            "ping -{} 1 -w {} {}".
            format(num_switch, timeout, sHost),
            shell=True)

    except Exception as e:
        return False

    return True

def tracert(sHost, timeout, hops):
    try:
        output = subprocess.check_output(
            "tracert -w {} -h {} {}".
            format(timeout, hops, sHost),
            shell=True).decode('utf-8')
        # Get rid of double-spaced lines.
        _o = output.split('\r\n')
        output = '\n'.join(_o)
        print(output)
        pass

    except Exception as e:
        return False, e

    return True, output

if __name__ == "__main__":
    print(f'Checking connection to {host}')

    tracert_OK_done = False
    tracert_fail_done = False

    if not os.path.exists(log_file_name):
        with open(log_file_name, 'w') as log:
            log.write('Written by ISP_monitor.py\n\n')

    print('Press Esc to quit')
    with open(log_file_name, 'a') as log:
        log_msg = '\n\n---------------------------------------------\n\n'

        log_msg += 'Fresh log started at {}\n'. \
            format(time.ctime())
        log.write(log_msg)
        log.flush()

        try:
            while True:
                ok_count = 0
                while pingOk(host, 1000):
                    if kbhit() and getch() == b'\x1B':
                        raise
                    time.sleep(monitor_timeout)
                    ok_count += monitor_timeout+1
                    if not tracert_OK_done:
                        print('\nRunning tracert when connected...')
                        tracert_OK_done,log_msg = tracert(host, 50, 15)
                        if tracert_OK_done:
                            log.write('tracert when connected:\n')
                            log.write(log_msg)
                            log.flush()
                        ok_count += 10
                    print(f'\rOK for {ok_count} seconds', end='')

                print(f'\nFailed at {time.ctime()}')
                log_msg = 'Failed at {}, {} seconds after last failure ended\n'. \
                    format(time.ctime(), ok_count)
                log.write(log_msg)
                log.flush()
                fail_count = 0
                while not pingOk(host, 1000):
                    # Check for reconnect every second
                    if kbhit() and getch() == b'\x1B':
                        raise
                    # ping timeout has already taken a second
                    # time.sleep(reconnect_time)
                    fail_count += 1
                    if not tracert_fail_done and fail_count > 5:
                        print('\nRunning tracert when not connected...')
                        tracert_fail_done,log_msg = tracert(host, 50, 15)
                        if tracert_fail_done:
                            log.write('tracert when connected:\n')
                            log.write(log_msg)
                            log.flush()
                        fail_count += 10
                    print(f'\rFailed for {fail_count} seconds', end='')

                print('\nReconnected at {}'.format(time.ctime()))
                log_msg = 'Reconnected at {} after {} second failure\n'. \
                    format(time.ctime(), fail_count)
                log.write(log_msg)
                log.flush()

        except:
            pass # Esc pressed
        log_msg = '\n\nLogging stopped by user at {}\n'. \
            format(time.ctime())
        log.write(log_msg)
        log.flush()
        print(log_msg)