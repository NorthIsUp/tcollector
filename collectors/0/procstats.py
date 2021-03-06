#!/usr/bin/python
# This file is part of tcollector.
# Copyright (C) 2010  StumbleUpon, Inc.
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.  This program is distributed in the hope that it
# will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty
# of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser
# General Public License for more details.  You should have received a copy
# of the GNU Lesser General Public License along with this program.  If not,
# see <http://www.gnu.org/licenses/>.
#
"""import various /proc stats from /proc into TSDB"""

import os
import sys
import time
import socket
import re

COLLECTION_INTERVAL = 15  # seconds


def main():
    """procstats main loop"""

    f_uptime = open("/proc/uptime", "r")
    f_meminfo = open("/proc/meminfo", "r")
    f_vmstat = open("/proc/vmstat", "r")
    f_stat = open("/proc/stat", "r")
    f_loadavg = open("/proc/loadavg", "r")

    while True:
        # proc.uptime
        f_uptime.seek(0)
        ts = int(time.time())
        for line in f_uptime:
            m = re.match("(\S+)\s+(\S+)", line)
            if m:
                print "proc.uptime.total %d %s" % (ts, m.group(1))
                print "proc.uptime.now %d %s" % (ts, m.group(2))

        # proc.meminfo
        f_meminfo.seek(0)
        ts = int(time.time())
        for line in f_meminfo:
            m = re.match("(\w+):\s+(\d+)", line)
            if m:
                print ("proc.meminfo.%s %d %s"
                        % (m.group(1).lower(), ts, m.group(2)))

        # proc.vmstat
        f_vmstat.seek(0)
        ts = int(time.time())
        for line in f_vmstat:
            m = re.match("(\w+)\s+(\d+)", line)
            if not m:
                continue
            if m.group(1) in ("pgpgin", "pgpgout", "pswpin",
                              "pswpout", "pgfault", "pgmajfault"):
                print "proc.vmstat.%s %d %s" % (m.group(1), ts, m.group(2))

        # proc.stat
        f_stat.seek(0)
        ts = int(time.time())
        for line in f_stat:
            m = re.match("(\w+)\s+(.*)", line)
            if not m:
                continue
            if m.group(1) == "cpu":
                fields = m.group(2).split()
                print "proc.stat.cpu %d %s type=user" % (ts, fields[0])
                print "proc.stat.cpu %d %s type=nice" % (ts, fields[1])
                print "proc.stat.cpu %d %s type=system" % (ts, fields[2])
                print "proc.stat.cpu %d %s type=idle" % (ts, fields[3])
                print "proc.stat.cpu %d %s type=iowait" % (ts, fields[4])
                print "proc.stat.cpu %d %s type=irq" % (ts, fields[5])
                print "proc.stat.cpu %d %s type=softirq" % (ts, fields[6])
                # really old kernels don't have this field
                if len(fields) > 7:
                    print ("proc.stat.cpu %d %s type=guest"
                           % (ts, fields[7]))
                    # old kernels don't have this field
                    if len(fields) > 8:
                        print ("proc.stat.cpu %d %s type=guest_nice"
                               % (ts, fields[8]))
            elif m.group(1) == "intr":
                print ("proc.stat.intr %d %s"
                        % (ts, m.group(2).split()[0]))
            elif m.group(1) == "ctxt":
                print "proc.stat.ctxt %d %s" % (ts, m.group(2))
            elif m.group(1) == "processes":
                print "proc.stat.processes %d %s" % (ts, m.group(2))
            elif m.group(1) == "procs_blocked":
                print "proc.stat.procs_blocked %d %s" % (ts, m.group(2))

        f_loadavg.seek(0)
        ts = int(time.time())
        for line in f_loadavg:
            m = re.match("(\S+)\s+(\S+)\s+(\S+)\s+(\d+)/(\d+)\s+", line)
            if not m:
                continue
            print "proc.loadavg.1min %d %s" % (ts, m.group(1))
            print "proc.loadavg.5min %d %s" % (ts, m.group(2))
            print "proc.loadavg.15min %d %s" % (ts, m.group(3))
            print "proc.loadavg.runnable %d %s" % (ts, m.group(4))
            print "proc.loadavg.total_threads %d %s" % (ts, m.group(5))

        sys.stdout.flush()
        time.sleep(COLLECTION_INTERVAL)

if __name__ == "__main__":
    main()

