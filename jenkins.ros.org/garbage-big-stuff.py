#!/usr/bin/env python

from __future__ import print_function
import argparse
import os
import sys


def recursive_delete(path):
    for root, dirs, files in os.walk(path, topdown=False):
        for name in files:
            os.remove(os.path.join(root, name))
        for name in dirs:
            os.rmdir(os.path.join(root, name))


def main():
    parser = argparse.ArgumentParser(description='Garbage shit.')
    parser.add_argument(
        '--delete',
        action='store_true',
        help='Delete matching folders')
    args = parser.parse_args()

    root_dir = '/var/lib/jenkins/jobs'

    checked = set([])
    lines = []
    size_sum = 0
    i = 0
    for job in sorted(os.listdir(root_dir)):
        if not os.path.isdir(os.path.join(root_dir, job)):
            continue
        job_builds = os.path.join(root_dir, job, 'builds')
        if not os.path.exists(job_builds):
            continue
        sys.stdout.write(job)
        for build in sorted(os.listdir(job_builds)):
            path = os.path.join(job_builds, build)
            if not os.path.isdir(path):
                continue

            path = os.path.realpath(path)
            if path in checked:
                continue
            checked.add(path)

            for filename in sorted(os.listdir(path)):
                filepath = os.path.join(path, filename)
                if not os.path.isfile(filepath):
                    continue
                i += 1
                fullpath = os.path.abspath(filepath)
                size = os.path.getsize(fullpath)
                if size > 10 * 1024 * 1024:
                    line = fullpath + " " + '%d' % (size / 1024 / 1024) + \
                        ' ' + ','.join(os.listdir(path))
                    lines.append(line)
                    size_sum += size
                    if args.delete:
                        print('delete: ' + os.path.dirname(fullpath))
                        recursive_delete(os.path.dirname(fullpath))
                    break
        sys.stdout.write('\n')
    if not args.delete:
        lines.sort()
        print('i = %d' % i)
        print('\n'.join(lines))
        print('size: %d GB in %d folders' %
              ((size_sum / 1024 / 1024 / 1024), len(lines)))


if __name__ == '__main__':
    main()
