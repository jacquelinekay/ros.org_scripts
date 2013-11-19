#!/usr/bin/env python

from __future__ import print_function

import argparse
import datetime
import os
import re
import sys
import urllib2


def search(pages_path, search):
    results = {}
    for page_name in sorted(os.listdir(pages_path)):
        page_path = os.path.join(pages_path, page_name)
        if not os.path.isdir(page_path):
            continue
        current_file = os.path.join(page_path, 'current')
        if not os.path.isfile(current_file):
            continue
        try:
            with open(current_file, 'r') as f:
                revision = f.read().strip()
        except IOError:
            continue
        latest_page_file = os.path.join(page_path, 'revisions', revision)
        if not os.path.isfile(latest_page_file):
            continue
        try:
            with open(latest_page_file, 'r') as f:
                content = f.read().splitlines()
        except IOError:
            continue
        for index, line in enumerate(content):
            if search in line:
                if page_name not in results:
                    results[page_name] = []
                results[page_name].append((index + 1, line))
    return results


def convert_link(old_uri):
    print('convert_link old = ', old_uri)
    if not check_link('http://code.ros.org/lurker/%s.en.html' % old_uri):
        print('source does not exist: %s' % old_uri, file=sys.stderr)
        return None

    type_, identifier = old_uri.split('/', 2)
    date, time, hashcode = identifier.split('.', 3)
    year, month, day = int(date[0:4]), int(date[4:6]), int(date[6:8])
    date = datetime.date(year, month, day)
    hour, minute, second = int(time[0:2]), int(time[2:4]), int(time[4:6])

    new_date, new_hour = get_mod_date(date, hour, -7)
    new_uri = find_url(type_, new_date.year, new_date.month, new_date.day, new_hour, minute, second, hashcode, 1, 90)
    if not new_uri:
        new_uri = find_url(type_, new_date.year, new_date.month, new_date.day, new_hour, minute, second, hashcode, -1, 90)
    if not new_uri:
        new_date, new_hour = get_mod_date(date, hour, -8)
        new_uri = find_url(type_, new_date.year, new_date.month, new_date.day, new_hour, minute, second, hashcode, 1, 90)
    if not new_uri:
        new_uri = find_url(type_, new_date.year, new_date.month, new_date.day, new_hour, minute, second, hashcode, -1, 90)
    if not new_uri:
        print('destination not found', file=sys.stderr)
    return new_uri


def get_mod_date(date, hour, hour_offset):
    # compensate timezone difference
    hour += hour_offset
    if hour < 0:
        hour += 24
        # subtract one day
        date = date - datetime.timedelta(0, 0, 0, 0, 0, 24)
    elif hour > 23:
        hour -= 24
        # add one day
        date = date + datetime.timedelta(0, 0, 0, 0, 0, 24)
    return date, hour


def find_url(type_, year, month, day, hour, minute, second, hashcode, second_offset, max_tests):
    while max_tests > 0:
        max_tests -= 1
        new_uri = '%s/%04d%02d%02d.%02d%02d%02d.%s' % (type_, year, month, day, hour, minute, second, hashcode)
        if check_link('http://lists.ros.org/lurker/%s.en.html' % new_uri):
            sys.stdout.write('\n')
            print('convert_link new = ', new_uri)
            return new_uri
        sys.stdout.write('.')
        sys.stdout.flush()
        #print('destination does not exist: %s - trying alternative seconds' % new_uri, file=sys.stderr)
        second += second_offset
        if second < 0:
            second += 60
            minute -= 1
            if minute < 0:
                minute += 60
                hour -= 1
                if hour < 0:
                    sys.stdout.write('\n')
                    return None
        elif second > 59:
            second -= 60
            minute += 1
            if minute > 59:
                minute -= 60
                hour += 1
                if hour > 23:
                    sys.stdout.write('\n')
                    return None
    sys.stdout.write('\n')
    return None



def check_link(url):
    h = urllib2.urlopen(url)
    data = h.read()
    #print('check_link(%s) %s' % (url, data))
    return not 'failed to render page' in data


def main(argv=sys.argv[1:]):
    parser = argparse.ArgumentParser(description='Find content in moinmoin pages')
    parser.add_argument('--pages-path', nargs='?', default='/var/www/wiki.ros.org/data/pages', help='The base path to pages folder')

    args = parser.parse_args(argv)

    mapping = {}
    results = search(args.pages_path, '<<LurkerLink(')
    for _, lines in results.items():
        for _, line in lines:
            matches = re.findall('<<LurkerLink\(([^)]+)\)>>', line)
            for match in matches:
                if match in mapping:
                    continue
                new_uri = convert_link(match)
                if new_uri:
                    mapping[match] = mapping


if __name__ == '__main__':
    main()
