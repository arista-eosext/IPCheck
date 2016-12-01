# IPCheck.py

The purpose of this script is to test IP reachability and alert if its down or if it comes back up.

# Author
Jeremy Georges - Arista Networks   - jgeorges@arista.com

# Description
IPCheck Utility

The purpose of this utility is to test next hop reachability and alert if its down.
Additionally, it can be used to monitor via ICMP any IP, such as hosts, and alert via syslog
on your Arista switch when the host goes down or is comes back up.

Add the following configuration snippets to change the default behavior. For the list
of IPs to check, separate with a comma.
```
daemon IPCheck
   exec /mnt/flash/IPCheck.py
   option CHECKINTERVAL value 2
   option IPv4 value 10.1.1.1,10.1.1.2
   option IPv6 value fc00:DEAD:BEEF::1
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
Copy to the /mnt/flash directory of each Arista switch that you want to use IPCheck.



License
=======
BSD-3, See LICENSE file