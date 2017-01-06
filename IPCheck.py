#!/usr/bin/env python
# Copyright (c) 2016 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.
'''
IPCheck Utility

The purpose of this utility is to test next hop reachability and alert if its down.
Additionally, it can be used to monitor via ICMP any IP, such as hosts, and alert via syslog
on your Arista switch when it goes down or it comes back up.

Add the following configuration snippets to change the default behavior. For the list
of IPs to check, separate with a comma.

daemon IPCheck 
   exec /mnt/flash/IPCheck.py
   option CHECKINTERVAL value 2
   option IPv4 value 10.1.1.1,10.1.1.2
   option IPv6 value fc00:DEAD:BEEF::1
   option PINGCOUNT value 2
   no shutdown

This requires the EOS SDK extension installed if its < EOS 4.17.0 release. 
All new EOS releases include the SDK.
'''
#************************************************************************************
# Change log
# ----------
# Version 1.0.0  - 11/14/2016 - Jeremy Georges -- jgeorges@arista.com --  Initial Version
#
#*************************************************************************************
#
#
#****************************
#GLOBAL VARIABLES -         *
#****************************
# These are the defaults. The config can override these
#Set Check Interval in seconds
CHECKINTERVAL=5
#
#Number of pings per interation
PINGCOUNT=3
#
#We need a global list that will be there between iterations. Including after a reconfiguration
DEADIPV4=[]
DEADIPV6=[]


#****************************
#*     MODULES              *
#****************************
#
import sys
import syslog
import eossdk

#***************************
#*     FUNCTIONS           *
#***************************
def pingDUT(protocol,hostname, pingcount):
    """
    Ping a DUT(s).

    Pass the following to the function:
        protocol (Version 4 or 6)
        host
        pingcount (number of ICMP pings to send)

        return False if ping fails
        return True if ping succeeds
    """
    import subprocess as sp
    if protocol == 4:
        process=sp.Popen("ping -c %s %s " % (pingcount,hostname), shell = True, stdout = sp.PIPE, stderr = sp.PIPE)
        output, error = process.communicate()
        failed = process.returncode
    elif protocol == 6:
        process=sp.Popen("ping6 -c %s %s " % (pingcount,hostname), shell = True, stdout = sp.PIPE, stderr = sp.PIPE)
        output, error = process.communicate()
        failed = process.returncode
    else:
        #Something is wrong if we land here. We want this as a belt and suspender test
        print "Wrong protocol specified for ping check"
        sys.exit(1)
    #returns Failed if it failed....
    if failed:
        return False
    else:
        return True

class IPCheckAgent(eossdk.AgentHandler,eossdk.TimeoutHandler):
   def __init__(self, sdk, timeoutMgr):
      self.agentMgr = sdk.get_agent_mgr()
      self.tracer = eossdk.Tracer("IPCheckPythonAgent")
      eossdk.AgentHandler.__init__(self, self.agentMgr)
      #Setup timeout handler
      eossdk.TimeoutHandler.__init__(self, timeoutMgr)
      self.tracer.trace0("Python agent constructed")


   def on_initialized(self):
      self.tracer.trace0("Initialized")
      syslog.syslog("IPCheck Initialized")
      self.agentMgr.status_set("Status:", "Administratively Up")
      IPv4 = self.agentMgr.agent_option("IPv4")
      if not IPv4:
         # No IPv4 list of IPs initially set
         self.agentMgr.status_set("IPv4 Ping List:", "None")
      else:
         # Handle the initial state
         self.on_agent_option("IPv4", IPv4)
      IPv6 = self.agentMgr.agent_option("IPv6")
      if not IPv6:
         # No IPv6 list of IPs initially set
         self.agentMgr.status_set("IPv6 Ping List:", "None")
      else:
         # Handle the initial state
         self.on_agent_option("IPv6", IPv6)
      #Lets check the extra parameters and see if we should override the defaults
      TESTINTERVAL = self.agentMgr.agent_option("CHECKINTERVAL")
      if TESTINTERVAL:
          global CHECKINTERVAL
          CHECKINTERVAL=TESTINTERVAL
      PINGS = self.agentMgr.agent_option("PINGCOUNT")
      if PINGS:
          global PINGCOUNT
          PINGCOUNT=PINGS


      #Start our handler now.
      self.timeout_time_is(eossdk.now())

   def on_timeout(self):
      #Create a blank list of IPs that are dead. We'll use that to suppress notification
      global DEADIPV4
      global DEADIPV6
      IPv4 = self.agentMgr.agent_option("IPv4")
      if IPv4:
          EachAddress = IPv4.split(',')
          for host in EachAddress:
              pingstatus = pingDUT(4,str(host),PINGCOUNT)
              #After ping status, lets go over all the various test cases below
              if pingstatus == True:
                  #Its alive
                  #Check to see if it was in our dead list
                  if host in DEADIPV4:
                      #Notify that its back up.
                      syslog.syslog('Next HOP %s is back up' % str(host))
                      DEADIPV4.remove(host)
              else:
                  #Its not alive
                  if host not in DEADIPV4:
                      syslog.syslog('Next HOP %s is down' % str(host))
                      DEADIPV4.append(host)

      #Do an IPv6 section now
      IPv6 = self.agentMgr.agent_option("IPv6")
      if IPv6:
          EachAddress = IPv6.split(',')
          for host in EachAddress:
              for host in EachAddress:
                  pingstatus = pingDUT(6,str(host),PINGCOUNT)
                  #After ping status, lets go over all the various test cases below
                  if pingstatus == True:
                      #Its alive
                      #Check to see if it was in our dead list
                      if host in DEADIPV6:
                          #Notify that its back up.
                          syslog.syslog('Next HOP %s is back up' % str(host))
                          DEADIPV6.remove(host)
                  else:
                      #Its not alive
                      if host not in DEADIPV6:
                          syslog.syslog('Next HOP %s is down' % str(host))
                          DEADIPV6.append(host)

      self.timeout_time_is(eossdk.now() + int(CHECKINTERVAL))

   def on_agent_option(self, optionName, value):
      #options are a key/value pair
      if optionName == "IPv4":
         if not value:
            self.tracer.trace3("IPv4 List Deleted")
            self.agentMgr.status_set("IPv4 Ping List:", "None")
         else:
            self.tracer.trace3("Adding IPv4 Ping list to %s" % value)
            self.agentMgr.status_set("IPv4 Ping List:", "%s" % value)
      if optionName == "IPv6":
         if not value:
            self.tracer.trace3("IPv6 List Deleted")
            self.agentMgr.status_set("IPv6 Ping List:", "None")
         else:
            self.tracer.trace3("Adding IPv6 Ping list to %s" % value)
            self.agentMgr.status_set("IPv6 Ping List:", "%s" % value)

   def on_agent_enabled(self, enabled):
      #When shutdown set status and then shutdown
      if not enabled:
         self.tracer.trace0("Shutting down")
         self.agentMgr.status_del("Status:")
         self.agentMgr.status_set("Status:", "Administratively Down")
         self.agentMgr.agent_shutdown_complete_is(True)

#=============================================
# MAIN
#=============================================
def main():
    syslog.openlog(ident="IPCheck-ALERT-AGENT",logoption=syslog.LOG_PID, facility=syslog.LOG_LOCAL0)
    sdk = eossdk.Sdk()
    IPCheck = IPCheckAgent(sdk, sdk.get_timeout_mgr())
    sdk.main_loop(sys.argv)
    # Run the agent until terminated by a signal

if __name__ == "__main__":
    main()
