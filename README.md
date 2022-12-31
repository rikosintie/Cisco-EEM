# Cisco EEM  
My journey down the Embedded Event Manager trail  

[Cisco IOS Embedded Event Manager (EEM)](https://www.cisco.com/c/en/us/products/ios-nx-os-software/ios-embedded-event-manager-eem/index.html)  
[Understanding Cisco EEM by examples Part 1](https://learningnetwork.cisco.com/s/article/understanding-cisco-eem-by-examples-part-1)  
[Understand Best Practices and Useful Scripts for EEM](https://www.cisco.com/c/en/us/support/docs/ios-nx-os-software/ios-xe-16/216091-best-practices-and-useful-scripts-for-ee.html)  
[Cisco IOS Embedded Event Manager Command Reference](https://www.cisco.com/c/en/us/td/docs/ios-xml/ios/eem/command/eem-cr-book/eem-cr-e1.html)  
[Embedded Event Manager Examples - Roger Perkins](https://www.rogerperkin.co.uk/eem/embedded-event-manager-examples/)  
[tcl scripting for IOS](https://books.google.com/books?id=RFfvqHQ0plsC&pg=PT162&lpg=PT162&dq=sl_intf_down.tcl&source=bl&ots=bmJ9ml7_Aw&sig=ACfU3U00Vqs6bnPvtV00jHO18PUh1DYWfA&hl=en&sa=X&ved=2ahUKEwj0z-CblNX7AhX6MUQIHX--ArAQ6AF6BAglEAM#v=onepage&q=sl_intf_down.tcl&f=false) - Google book preview.  
[EEM Built-in "Action" Variables](https://community.cisco.com/t5/networking-knowledge-base/eem-built-in-quot-action-quot-variables/ta-p/3123406)  
[Variable for finding a port in syslog](https://community.cisco.com/t5/network-management/eem-variables/m-p/4586627) - This example shows how to watch syslog for a specific port being disabled by port security.  
[EEM variable $_syslog_msg not working](https://community.cisco.com/t5/routing/eem-variable-syslog-msg-not-working/m-p/4505375)  
[Convert an EEM Applet to a Tcl Policy](https://www.marcuscom.com/convert_applet/) = Joe Clarke's 


## EEM Overview

From Cisco's documentation  

* Embedded Event manager is a software component of cisco IOS, XR, and NX-OS

Cisco IOS Embedded Event Manager (EEM) is a powerful and flexible subsystem that provides real-time network event detection and onboard automation. It gives you the ability to adapt the behavior of your network devices to align with your business needs.

IOS Embedded Event Manager supports more than 20 event detectors that are highly integrated with different Cisco IOS Software components to trigger actions in response to network events. Your business logic can be injected into network operations using IOS Embedded Event Manager policies. These policies are programmed using either simple command-line interface (CLi) or using a scripting language called Tool Command Language (Tcl).


**EEM Types:**

There are two EEM independent pieces (types): Applets and Scripting

* Applets are a collection of CLI commands
* Scripts are actions coded up in TCL(interpreter language)


EEM Actions:

EEM can take many actions once event happens , actions could be :

* Sending a email messages
* Executing or disabling a cisco command.
* Generating SNMP traps
* Reloading the router
* Generating priotized syslog messages
* Switching to a secondary processor in a redundant platform
* Requesting system information when an event occurs(like sh tech,sh proccess cpu history).


**Common regular expressions:**

During creating your EEM Applet you can use some regular expressions, the following are common used ones :
```
^ = Start of string  
$ = End of string  
. = Any single character  
* = Zero or more instances  
+ = One or more instance  
? = Zero or one instance  
```  



**Avoid Out-of-order Execution**

As described in the EEM documentation, the order of execution for action statements is controlled by their label (for example, action 0001 cli command enable has a label of 0001). This label value is NOT a number, but rather alphanumeric. Actions are sorted in ascending alphanumeric key sequence, use the label argument as the sort key, and they are run in this sequence. This can lead to unexpected order of execution, based on how you structure your action labels.
Consider this example:
    event manager applet test authorization bypass
    event timer watchdog time 60 maxrun 60
    action 13 syslog msg "You would expect to see this message first"
    action 120 syslog msg "This message prints first"

Since 120 is before 13 in an alphanumeric comparison, this script does not run in the order you expect. 

To avoid this, it is useful to use a system of padding like this:
    event manager applet test authorization bypass
    event timer watchdog time 60 maxrun 60
    action 0010 syslog msg "This message appears first"
    action 0020 syslog msg "This message appears second"
    action 0120 syslog msg "This message appears third"

Disable Pagination

EEM looks for the device prompt to determine when command output is complete. Commands that output more data than can be displayed on one screen (as configured by your terminal length), can prevent EEM scripts from completion (and eventually killed via the maxrun timer) as the device prompt is not shown until all pages of the output are viewed. Configure term len 0 at the start of EEM scripts that examine large outputs.

**Design Scripts for Future Maintainability**

When you design an EEM script, leave gaps between action labels to make it easier to update the EEM script logic in the future. When appropriate gaps are available (that is, two statements such as action 0010 and action 0020 leave a gap of 9 labels that can be inserted), new statements can be added as required without renumber or recheck of the action labels and ensure the actions continue to execute in the expected order.

There are common commands that you need to run at the beginning of your EEM scripts. 
This can include:
```
    event manager applet <applet Name> auth bypass
    action 0001 cli command "enable"
    action 0002 cli command "term exec prompt timestamp"
    action 0003 cli command "term length 0"
```  


This is a common pattern in the examples shown in this document, where many of the scripts begin with the same 3 action statements to configure this.

**A simple example of using variables**  
The increment, decrement, set, and append actions do not actually use a built-in result variable.  
You pass the variable name to the actions, and the variable is mutated.  For example:  
```
action 1.0 set var 1  
action 2.0 decrement var  
action 3.0 puts "Value of Var: " $var  
```

The value of 0 will be printed.


## Useful EEM Scripts
Track Specific MAC Address for MAC Address Learn

In this example, the MAC address b4e9.b0d3.6a41 is tracked. The script checks every 30 seconds to see if the specified MAC address has been learned in the ARP or MAC tables.  
If the MAC is seen, the script takes these actions:  
outputs a syslog message (This is useful when you want to confirm where a MAC address is learned, or when/how often it is learned).  

**Implementation**  
```
event manager applet mac_trace authorization bypass  
event timer watchdog time 30  
action 0001 cli command "enable"  
action 0002 cli command "term exec prompt timestamp"  
action 0003 cli command "term length 0"  
action 0010 cli command "show ip arp | in b4e9.b0d3.6a41"  
action 0020 regexp ".*(ARPA).*" $_cli_result  
action 0030 if $_regexp_result eq 1  
action 0040 syslog msg $_cli_result  
action 0050 end  
action 0060 cli command "show mac add vlan 1 | in b4e9.b0d3.6a41"  
action 0070 regexp ".*(DYNAMIC).*" $_cli_result  
action 0080 if $_regexp_result eq 1  
action 0090 syslog msg $_cli_result  
action 0100 end  
```




## Debugging
* show event manager history events
* show event manager history traps
* show event manager policy registered
* show event manager directory user repository
* show event manager directory user library
* show event manager directory user policy  
* show event manager session cli username 
* show event manager scheduler thread detailed
* show event manager version 
* show event manager detector syslog detailed

## Detectors
show event manager detector all    


| No. |  Name              | Version   | Node    |    Type  | 
| :--:| :--:               |  :--:       | :--:     | :--:  | 
|1    | application        | 01.00   |  node0/0  |  RP  |
|2    | routing            | 03.00   |  node0/0   | RP      
|3    | syslog             | 01.00   |  node0/0   | RP      
|4    | identity           | 01.00   |  node0/0   | RP      
|5    | neighbor-discovery | 01.00   |  node0/0   | RP      
|6    | mat                | 01.00   |  node0/0   | RP      
|7    | cli                | 01.00   |  node0/0   | RP      
|8    | config             | 01.00   |  node0/0   | RP      
|9    | counter            | 01.00   |  node0/0   | RP      
|10   | env                | 01.00   |  node0/0   | RP      
|11   | gold               | 01.00   | node0/0    | RP      
|12   | interface          | 01.00   | node0/0    | RP      
|13   | ioswdsysmon        | 01.00   | node0/0    | RP      
|14   | ipsla              | 01.00   | node0/0    | RP      
|15   | none               | 01.00   | node0/0    | RP      
|16   | oir                | 01.00   | node0/0    | RP      
|17   | rpc                | 01.00   | node0/0    | RP      
|18   | snmp               | 01.00   | node0/0    | RP      
|19   | snmp-object        | 01.00   | node0/0    | RP      
|20   | snmp-notification  | 01.00   | node0/0    | RP      
|21   | test               | 01.00   | node0/0    | RP      
|22   | timer              | 01.00   | node0/0    | RP      

 
</br>  
  
## Using TCL scripts
For this example, we will be using a file called int-UP.tcl.  
We will create a folder called `policies` to store the file in.  
This is not required but is a common practice to keep the scripts organized.

**Just for fun, let's verify the version of EEM on the switch**
```
3750x#show event manager version
Embedded Event Manager Version 4.00
Component Versions:
eem: (rel9)1.2.21
eem-gold: (rel1)1.0.2
eem-call-home: (rel2)1.0.4
Event Detectors:
Name                Version   Node        Type
application         01.00     node0/0     RP
identity            01.00     node0/0     RP
mat                 01.00     node0/0     RP
neighbor-discovery  01.00     node0/0     RP
generic             01.00     node0/0     RP
routing             03.00     node0/0     RP
syslog              01.00     node0/0     RP
msp                 03.00     node0/0     RP
cli                 01.00     node0/0     RP
config              01.00     node0/0     RP
counter             01.00     node0/0     RP
crash               01.00     node0/0     RP
ds                  01.00     node0/0     RP
env                 01.00     node0/0     RP
gold                01.00     node0/0     RP
interface           01.00     node0/0     RP
ioswdsysmon         01.00     node0/0     RP
ipsla               01.00     node0/0     RP
none                01.00     node0/0     RP
oir                 01.00     node0/0     RP
rpc                 01.00     node0/0     RP
snmp                01.00     node0/0     RP
snmp-object         01.00     node0/0     RP
snmp-notification   01.00     node0/0     RP
test                01.00     node0/0     RP
timer               01.00     node0/0     RP
```

**Create the folder**
```
3750x#pwd !print the current working directory  
flash:/  
3750x#mkdir policies !make the folder  
```


**Copy the script to the policies folder**  
`copy tftp://192.168.10.103/int-UP.tcl flash:/policies`  

Verify that the script copied  
```
cd policies  
pwd
flash:/policies/
dir  
Directory of flash:/policies/

  612  -rwx        2431  Dec 20 2022 20:05:48 -08:00  int-UP.tcl
cd ..
```
**Alternatively, from the flash folder**  
```
3750x#dir flash:/policies  
Directory of flash:/policies/  
  
  612  -rwx        2431  Dec 20 2022 20:05:48 -08:00  int-UP.tcl  
```

**Display the file**  
IOS supports the `more` Linux command to display text files.  
`3750x#more flash:/policies/int-UP.tcl`  


**Register the location where scripts are stored on flash with the EEM server:**  
`event manager directory user policy flash:/policies`  

**Verify the location**
```
3750x#show event manager directory user policy  
flash:/policies 
```  

**Register the EEM Tcl policy:**  
`event manager policy int-UP.tcl type user`  

**Verify that the script is registered:**  
```
3750x#show event manager policy registered
No.  Class     Type    Event Type          Trap  Time Registered           Name
1    script    user    syslog              Off   Sun Jan 1 16:09:34 2006   int-UP.tcl
 pattern {.*%LINEPROTO-5-UPDOWN: Line protocol on Interface GigabitEthernet[0-9\/]+, changed state to up.*}
 nice 0 queue-priority normal maxrun 20.000 scheduler rp_primary Secu none
```

### Create a file from the console  
From a blog by Valter Popeskic  
[Create or Edit a File on Cisco IOS Flash](https://howdoesinternetwork.com/2018/create-file-cisco-ios)  

With this trick, you can write or edit a file from Flash memory directly from Cisco IOS console.  

I used Cisco IOS Tcl shell which is available on Cisco devices to allow running Tcl scripts and commands directly from the Cisco IOS CLI prompt. I think that this is the only way of changing text files from Cisco console, correct me in the comments if you know of something else.  

Next example will create a text file named test.txt, put some words inside and save the file on Cisco device flash.  

```
R2#tclsh
R2(tcl)#puts [open "flash:test.txt" w+] {
+>(tcl)#With this trick, you can write or edit a file
+>(tcl)#from Flash memory directly from Cisco IOS console. 
+>(tcl)#} 
R2(tcl)#tclquit
```  

This method is great if you don't have an enterprise wide tftp server running.

