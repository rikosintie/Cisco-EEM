'''
Usage
1. Create a new folder and copy Cisco-EEM.py and EEM.txt
into it.

2. Create a file named device-inventory-<site>.
Example
device-inventory-test

Place the information for each switch in the file. Format is
<IP Address>,cisco_ios,<hostname>,<username>,<password>
Example
192.168.10.52,cisco_ios,ANTO-IDF1,mhubbard,7Snb7*BF^8

3. Execute
python3 Cisco-EEM.py -s test


The script will read the device-inventory-<sitename> file:
create a folder called policies
copy int-UP.tcl into the folder
execute the contents of the EEM.txt for each switch.

For each switch in the inventory file the config commands that were
executed will be saved to 01_<hostname>-config-output.txt.


Use this file as an audit trail for the configuration commands.
'''

from datetime import datetime
from netmiko import ConnectHandler
from netmiko import exceptions
from paramiko.ssh_exception import SSHException
import os
import argparse
import sys
import logging

logging.basicConfig(filename="test.txt", level=logging.DEBUG) # It will log all reads and writes on the SSH channel
logger = logging.getLogger("netmiko")

def remove_empty_lines(filename):
    if not os.path.isfile(filename):
        print("{} does not exist ".format(filename))
        return
    with open(filename) as filehandle:
        lines = filehandle.readlines()

    with open(filename, 'w') as filehandle:
        lines = filter(lambda x: x.strip(), lines)
        filehandle.writelines(lines)


parser = argparse.ArgumentParser()
parser.add_argument("-s", "--site", help="Site name - ex. MVMS")
args = parser.parse_args()
site = args.site

if site is None:
    print('-s site name is a required argument')
    sys.exit()
else:
    dev_inv_file = 'device-inventory-' + site

# check if site's device inventory file exists
if not os.path.isfile(dev_inv_file):
    print("{} doesn't exist ".format(dev_inv_file))
    sys.exit()

remove_empty_lines(dev_inv_file)

with open(dev_inv_file) as devices_file:
    fabric = devices_file.readlines()

print('-' * (len(dev_inv_file) + 23))
print(f'Reading devices from: {dev_inv_file}')
print('-' * (len(dev_inv_file) + 23))

for line in fabric:
    line = line.strip("\n")
    ipaddr = line.split(",")[0]
    vendor = line.split(",")[1]
    hostname = line.split(",")[2]
    username = line.split(",")[3]
    password = line.split(",")[4]
    if vendor.lower() == "cisco_ios":
        print((str(datetime.now()) +
              " Connecting to Switch {}".format(hostname)))
        try:
            net_connect = ConnectHandler(device_type=vendor,
                                         ip=ipaddr,
                                         username=username,
                                         password=password,
                                         )
        except (EOFError, SSHException):
            print(f'Could not connect to {hostname}, remove it'
                  ' from the device inventory file')
            break
        print('Configuring {}'.format(hostname))
        print(net_connect.find_prompt())

        # Check to see if the file exists
        result = net_connect.send_command('sh run | i int-UP')
        if 'int-UP.tcl' not in result:
            # Create the folder for the tcl file
            cmd_list = [
                [f"mkdir flash:policies", r"Create"],
                ["\n", r"Created"],
                ]
            output = net_connect.send_multiline(cmd_list)

            # copy int-UP.tcl to flash:policies folder
            Tftp_server = '192.168.10.109'
            cmd1 = "copy tftp:int-UP.tcl flash:/policies/int-UP.tcl"
            result = net_connect.send_command_timing(cmd1)
            if 'Address or name of remote host' in result:
                result += net_connect.send_command_timing(Tftp_server)
            if 'Destination filename' in result:
                result += net_connect.send_command_timing('\n',
                                                          delay_factor=2)

            #  register int-UP.tcl
            cfg_file = "EEM.txt"
            print(net_connect.find_prompt())

            output = net_connect.send_config_from_file(cfg_file)
            print(output)
            int_report = "01_" + hostname + "-EEM-output.txt"
            with open(int_report, 'w') as file:
                file.write(output)
            print()
            net_connect.disconnect()
            print('-' * (len(hostname) + 26))
            print(f'Successfully configured {hostname}')
            print('-' * (len(hostname) + 26))
        else:
            print('Device is already configured')
            continue
