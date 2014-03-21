#!/usr/bin/env python

from __future__ import print_function

import argparse
import os
import shutil
import sys
import time
import yaml


def get_repo_info(package_path):
    repo_info = []
    manifest_path = os.path.join(package_path, 'manifest.yaml')
    if os.path.exists(manifest_path):
        with open(manifest_path, 'r') as f:
            data = yaml.load(f.read())
            if 'repo_name' in data:
                repo_info.append('repo: %s' % data['repo_name'])
            if 'doc_job' in data:
                repo_info.append('doc job: %s' % data['doc_job'])
            if 'vcs_uri' in data and 'vcs_version' in data:
                repo_info.append('vcs: %s : %s' % (data['vcs_uri'], data['vcs_version']))
                return repo_info


def main(argv=sys.argv[1:]):
    parser = argparse.ArgumentParser(description='Find outdated package documentation.')
    parser.add_argument('--docs-path', nargs='?', default='/home/rosbot/docs', help='The base path to docs folders')
    parser.add_argument('--rosdistro', nargs='?', help='Limit the search to a specific ROS distro')
    parser.add_argument('--max-age', default=14, help='The maximum age in days until doc is considered outdated')
    parser.add_argument('--verbose', action='store_true', help='Output additional information formthe manifesst.yaml')
    parser.add_argument('--delete', action='store_true', help='Delete any outdated package documentation')

    args = parser.parse_args(argv)

    now = time.time()
    missing = []
    outdated = []

    for distro_name in sorted(os.listdir(args.docs_path)):
        if args.rosdistro:
            if distro_name != args.rosdistro:
                continue
        elif distro_name in ['diamondback', 'electric', 'fuerte', 'independent', '.to-be-deleted']:
            # ignore older distros
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
                missing.append((package_path, get_repo_info(package_path) if args.verbose else []))
            else:
                mtime = os.path.getmtime(package_path)
                if mtime < now - 60 * 60 * 24 * int(args.max_age):
                    outdated.append((package_path, get_repo_info(package_path) if args.verbose else []))

    if missing:
        print('Missing stamps for packages docs:')
        for path, info in missing:
            print('- %s%s' % (path, ' (%s)' % ', '.join(info) if info else ''))

    if outdated:
        print('Outdated stamps for packages docs:')
        for path, info in outdated:
            print('- %s%s' % (path, ' (%s)' % ', '.join(info) if info else ''))

    if args.delete:
        print('Delete packages docs:')
        for path, _ in missing + outdated:
            print('- %s' % path)
            shutil.rmtree(path)


if __name__ == '__main__':
    main()
