#!/usr/bin/env python

from __future__ import print_function

import numpy
import os
import sys


class Entry():

    def __init__(self, ip, timestamp, timezone, duration, method, url, protocol, status, size):
        self.ip = ip
        self.timestamp = timestamp
        self.timezone = timezone
        self.duration = duration
        self.method = method
        self.url = url
        self.protocol = protocol
        self.status = status
        self.size = size

    def __str__(self):
        return '%s - - [%s %s] %.3f "%s %s %s" %d %d' % (self.ip, self.timestamp, self.timezone, self.duration, self.method, self.url, self.protocol, self.status, self.size)


def main():
    entries = []
    with open('20131213.log') as f:
        lines = f.read().splitlines()
        for line in lines:
            parts = line.split()
            if not parts[5].isdigit():
                # skip old log entries without generation time
                continue

            (ip, _, _, timestamp, timezone, duration, method, url, protocol, status, size) = parts[:11]

            timestamp = timestamp[1:]  # strip leading bracket
            timezone =  timezone[:-1]  # strip trailing bracket
            duration = float(int(duration)) / 1000 / 1000
            method = method[1:]  # strip leading quote
            protocol =  protocol[:-1]  # strip trailing quote
            status = int(status)
            if size == '-':  # e.g. for status 304
                size = 0
            else:
                size = int(size)
            e = Entry(ip, timestamp, timezone, duration, method, url, protocol, status, size)
            entries.append(e)

    by_url = {}
    for i, entry in enumerate(entries):
        if entry.url not in by_url:
            by_url[entry.url] = []
        by_url[entry.url].append(entry.duration)

    # output durations for one specific url
    if True:
        for url in sorted(by_url.keys()):
            durations = sorted(by_url[url])
            durations_str = ['%.3f' % d for d in durations]

            if url == '/custom/js/ASCIIMathML.js':
                print('%s: %s' % (url, ' '.join(durations_str)))
                print('Number of requests: %d' % len(durations))
                print('min/avg/max: %.3f/%.3f/%.3f' % (min(durations), sum(durations) / len(durations), max(durations)))
                print('median: %.3f' % numpy.median(durations))
                print('Number of requests: %d' % len(durations))

    # output most requested urls
    if True:
        by_url_count = {}
        for url in by_url:
            by_url_count[url] = len(by_url[url])

        for url in sorted(by_url_count, key=by_url_count.get, reverse=True)[:30]:
            print('%s: %d' % (url, by_url_count[url]))


if __name__ == '__main__':
    main()
