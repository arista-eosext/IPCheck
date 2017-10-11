# IPCheck.py

The purpose of this script is to test IP reachability and alert if its down or if it comes back up.

# Author
Jeremy Georges - Arista Networks   - jgeorges@arista.com

# Description
IPCheck Utility

The purpose of this utility is to test next hop reachability and alert if its down.
Additionally, it can be used to monitor via ICMP any IP, such as hosts, and alert via syslog
on your Arista switch when the host goes down or it comes back up.

Add the following configuration snippets to change the default behavior. For the list
of IPs to check, separate with a comma.
```
daemon IPCheck
   exec /usr/local/bin/IPCheck.py
   option CHECKINTERVAL value 2
   option IPv4 value 10.255.2.1,10.255.4.1
   option IPv6 value fd00:dead:beef:2::1,fd00:dead:beef:4::1,fd00:dead:beef:4::3
   option PINGCOUNT value 2
   no shutdown
```
This requires the EOS SDK extension installed if its < EOS 4.17.0 release.
All new EOS releases include the SDK.

## Example

### Output of 'show daemon' command
```
Router-C(config)#show daemon IPCheck
Agent: IPCheck (running)
Configuration:
Option              Value                                            
------------------- ------------------------------------------------ 
CHECKINTERVAL       2                                                
IPv4                10.255.2.1,10.255.4.1                            
IPv6                fd00:dead:beef:2::1,fd00:dead:beef:4::1,         
                    fd00:dead:beef:4::3                              
PINGCOUNT           2                                                

Status:
Data                  Value                                            
--------------------- ------------------------------------------------ 
IPv4 Ping List:       10.255.2.1,10.255.4.1                            
IPv6 Ping List:       fd00:dead:beef:2::1,fd00:dead:beef:4::1,         
                      fd00:dead:beef:4::3                              
Status:               Administratively Up   
```

### Syslog Messages
```
Dec  1 15:01:53 Router-C IPCheck-ALERT-AGENT[3283]: %AGENT-6-INITIALIZED: Agent 'IPCheck' initialized; pid=3283
Dec  1 15:01:53 Router-C IPCheck-ALERT-AGENT[3283]: IPCheck Initialized
Dec  1 15:01:57 Router-C IPCheck-ALERT-AGENT[3283]: Next HOP 10.255.4.1 is down
Dec  1 15:02:01 Router-C IPCheck-ALERT-AGENT[3283]: Next HOP fd00:dead:beef:4::1 is down
Dec  1 15:02:04 Router-C IPCheck-ALERT-AGENT[3283]: Next HOP  fd00:dead:beef:4::3 is down
Dec  1 15:04:13 Router-C IPCheck-ALERT-AGENT[3283]: Next HOP 10.255.4.1 is back up
Dec  1 15:15:15 Router-C IPCheck-ALERT-AGENT[3283]: Next HOP fd00:dead:beef:4::1 is back up
```



# INSTALLATION:
Because newer releases of EOS require a SysdbMountProfile, you'll need two files - IPCheck.py and IPCheck.
IPCheck.py will need to go to an appropriate location such as /mnt/flash and IPCheck will need to be placed in
/usr/lib/SysdbMountProfiles. The mount profile file name MUST match the python file name. In other words, if
you place the mount profile IPCheck in /usr/lib/SysdbMountProfiles as IPCheck, then the executable filename IPCheck.py
must be changed to IPCheck. The filename (agent name) and mount profile name must be the same.

An RPM has been included that allows you to easily just install IPCheck as an extension and it takes care of all
the file requirements. The RPM also installs the IPCheck SDK app in /usr/local/bin. This is the preferred distribution
method for this application.


License
=======
BSD-3, See LICENSE file
