# TCL Scripts
This TCl script monitors the log for a port transitioning from down to up.

When a port goes up, the script looks at the output of "show int Gix/0/x sw"
* It returns the access vlan of the port. 
* If the vlan is vlan 1, it writes a syslog entry so that ManageEngine can report it.

The Cisco-EEM.py script uses netmiko to tftp the tcl script to the switch
