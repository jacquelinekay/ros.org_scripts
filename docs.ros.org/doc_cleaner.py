#!/usr/bin/env python

from __future__ import print_function

import argparse
import os
import shutil
import sys


def main(argv=sys.argv[1:]):
    parser = argparse.ArgumentParser(description='Move latex and search folder to an external location and symlink placebo search folder into package documentation')
    parser.add_argument('--path', nargs='?', default='.', help='The DISTRO/api folder')

    args = parser.parse_args(argv)

    if os.path.basename(args.path) != 'api':
        print('The passed path must be named "api"', file=sys.stderr)
        sys.exit(1)

    dst = os.path.join(os.path.dirname(args.path), 'api_garbage')
    if not os.path.exists(dst):
        os.mkdir(dst)

    results = {}
    for package_name in sorted(os.listdir(args.path)):
        package_path = os.path.join(args.path, package_name)
        html_path = os.path.join(package_path, 'html')
        latex_path = os.path.join(html_path, 'latex')
        search_path = os.path.join(html_path, 'search')
        if not os.path.exists(latex_path) and (not os.path.exists(search_path) or os.path.islink(search_path)):
            continue

        html_dst_path = os.path.join(dst, package_name, 'html')
        if not os.path.exists(html_dst_path):
            print('create', html_dst_path)
            os.makedirs(html_dst_path)

        if os.path.exists(latex_path):
            print('move latex', latex_path, html_dst_path)
            shutil.move(latex_path, html_dst_path)
        if os.path.exists(search_path) and not os.path.islink(search_path):
            print('move search', search_path, html_dst_path)
            shutil.move(search_path, html_dst_path)
            print('create symlink', search_path)
            os.symlink('../../_search', search_path)
        break


if __name__ == '__main__':
    main()
