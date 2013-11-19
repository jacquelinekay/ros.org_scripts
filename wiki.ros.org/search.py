#!/usr/bin/env python

import argparse
import os
import sys


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


def main(argv=sys.argv[1:]):
    parser = argparse.ArgumentParser(description='Find content in moinmoin pages')
    parser.add_argument('search', help='The term to search for')
    parser.add_argument('--pages-path', nargs='?', default='/var/www/wiki.ros.org/data/pages', help='The base path to pages folder')

    args = parser.parse_args(argv)

    results = search(args.pages_path, args.search)
    for page_name, lines in results.items():
        for line_number, line in lines:
            print('%s:%d: %s' % (page_name, line_number, line))


if __name__ == '__main__':
    main()
