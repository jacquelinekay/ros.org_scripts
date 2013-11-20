#!/usr/bin/env python

from __future__ import print_function

import argparse
import os
import sys
import time


def main(argv=sys.argv[1:]):
    parser = argparse.ArgumentParser(description='Find outdated package documentation.')
    parser.add_argument('--docs-path', nargs='?', default='/home/rosbot/docs', help='The base path to docs folders')
    parser.add_argument('--max-age', default=14, help='The maximum age in days until doc is considered outdated')

    args = parser.parse_args(argv)

    now = time.time()
    missing = []
    outdated = []

    for distro_name in sorted(os.listdir(args.docs_path)):
        # ignore older distros
        if distro_name in ['diamondback', 'electric', 'independent', '.to-be-deleted']:
            continue

        # ignore symlinked api folder
        distro_path = os.path.join(args.docs_path, distro_name)
        if os.path.islink(distro_path):
            continue

        distro_api_path = os.path.join(distro_path, 'api')
        for package_name in sorted(os.listdir(distro_api_path)):
            package_path = os.path.join(distro_api_path, package_name)
            stamp_path = os.path.join(package_path, 'stamp')
            if not os.path.exists(stamp_path):
                missing.append(package_path)
            else:
                mtime = os.path.getmtime(package_path)
                if mtime < now - 60 * 60 * 24 * int(args.max_age):
                    outdated.append(package_path)

    if missing:
        print('Missing stamps for packages docs:')
        for p in missing:
            print('- %s' % p)

    if outdated:
        print('Outdated stamps for packages docs:')
        for p in outdated:
            print('- %s' % p)


if __name__ == '__main__':
    main()
