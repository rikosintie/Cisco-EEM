# Cisco EEM  
My journey down the Embedded Event Manager trail  

[Cisco IOS Embedded Event Manager (EEM)](https://www.cisco.com/c/en/us/products/ios-nx-os-software/ios-embedded-event-manager-eem/index.html)  
[Understanding Cisco EEM by examples Part 1](https://learningnetwork.cisco.com/s/article/understanding-cisco-eem-by-examples-part-1)  
[Understand Best Practices and Useful Scripts for EEM](https://www.cisco.com/c/en/us/support/docs/ios-nx-os-software/ios-xe-16/216091-best-practices-and-useful-scripts-for-ee.html)  
[Cisco IOS Embedded Event Manager Command Reference](https://www.cisco.com/c/en/us/td/docs/ios-xml/ios/eem/command/eem-cr-book/eem-cr-e1.html)  
[Embedded Event Manager Examples - Roger Perkins](https://www.rogerperkin.co.uk/eem/embedded-event-manager-examples/)  
[tcl scripting for IOS](https://books.google.com/books?id=RFfvqHQ0plsC&pg=PT162&lpg=PT162&dq=sl_intf_down.tcl&source=bl&ots=bmJ9ml7_Aw&sig=ACfU3U00Vqs6bnPvtV00jHO18PUh1DYWfA&hl=en&sa=X&ved=2ahUKEwj0z-CblNX7AhX6MUQIHX--ArAQ6AF6BAglEAM#v=onepage&q=sl_intf_down.tcl&f=false) - Google book preview.  
[EEM Built-in "Action" Variables](https://community.cisco.com/t5/networking-knowledge-base/eem-built-in-quot-action-quot-variables/ta-p/3123406)  


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
