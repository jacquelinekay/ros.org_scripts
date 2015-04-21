#!/usr/bin/env python

"""
Generates wiki formatted output, which summarizes the status of the jade variants
using the indigo distribution cache and accounting for chanages.

To use it, checkout the jade-devel branch of the metapackages repo at

https://github.com/ros/metapackages

And then update the `path` variable near the top of the script to point to the directory
containing the metapackages repo and run this script.
"""

from __future__ import print_function

from catkin_pkg.packages import find_packages
from catkin_pkg.package import InvalidPackage
from catkin_pkg.package import parse_package_string

from rosdistro import get_cached_distribution
from rosdistro import get_distribution_file
from rosdistro import get_index
from rosdistro import get_index_url
from rosdistro.dependency_walker import DependencyWalker

path = '/tmp/mp_ws/src'

metapackages = dict([(p.name, p) for pth, p in find_packages(path).items()])

keys = [
    'ros_core',
    'ros_base',
    'robot',
    'viz',
    'desktop',
    'perception',
    'simulators',
    'desktop_full',
]

# Get packages which make up each layer of the veriants
mp_sets = {}
index = get_index(get_index_url())
indigo = get_cached_distribution(index, 'indigo')
jade = get_cached_distribution(index, 'jade')
dist_file = get_distribution_file(index, 'indigo')
jade_dist_file = get_distribution_file(index, 'jade')
dw = DependencyWalker(indigo)
for mp in keys:
    # print("Fetching deps for: ", mp)
    deps = list(set(metapackages[mp].run_depends))
    mp_sets[mp] = set([])
    for dep in deps:
        mp_sets[mp].update(set([dep.name]))
        if dep.name in keys:
            continue
        # print(" ", dep.name)
        previous_pkgs = set([])
        for mp_, mp_set in mp_sets.items():
            if mp == mp_:
                continue
            previous_pkgs.update(mp_set)
        mp_sets[mp].update(dw.get_recursive_depends(
            dep.name,
            ['buildtool', 'build', 'run'],
            ros_packages_only=True,
            ignore_pkgs=list(previous_pkgs)
        ))
    # print(" => ", len(mp_sets[mp]))

# Repos by package
repos_by_package = {}
repo_mstatuses = {}
for name, repo in dist_file.repositories.items():
    if name == 'geometry_angles_utils':
        jade_name = 'angles'
    else:
        jade_name = name
    if not repo.release_repository:
        continue
    if jade_name not in jade_dist_file.repositories:
        repo_mstatuses[name] = 'not released'
    else:
        jade_repo = jade_dist_file.repositories[jade_name]
        if jade_repo.status:
            repo_mstatuses[name] = jade_repo.status
    for pkg in repo.release_repository.package_names:
        repos_by_package[pkg] = name
repos_by_package['map_msgs'] = 'navigation_msgs'
repos_by_package['move_base_msgs'] = 'navigation_msgs'
repo_mstatuses['navigation_msgs'] = jade_dist_file.repositories['navigation_msgs'].status
repos_by_package.update(dict([(k, k) for k in keys]))

# Group packages by repo
mp_repo_sets = {}
for key in keys:
    mp_repo_sets[key] = {}
    for dep in mp_sets[key]:
        if dep not in repos_by_package:
            continue
        repo = repos_by_package[dep]
        mp_repo_sets[key][repo] = mp_repo_sets[key].get(repo, {})
        maintainer = ''
        try:
            pkg_xml = jade.get_release_package_xml(dep)
        except KeyError:
            pkg_xml = None
        if pkg_xml:
            try:
                pkg = parse_package_string(pkg_xml)
                maintainer = '<<BR>>'.join(['<<MailTo(%s, %s)>>' % (
                    m.email.replace('@', ' AT ').replace('.', ' DOT '), m.name) for m in pkg.maintainers]
                )
            except InvalidPackage:
                maintainer = ''
        mp_repo_sets[key][repo][dep] = maintainer

for key in keys:
    print("== " + key + " ==")
    print()
    print("||<tablewidth=\"100%\">'''Repository'''||'''Maintenance Status'''||'''Maintainers'''||")
    for repo in sorted(list(mp_repo_sets[key])):
        if repo in keys:
            print("||<bgcolor=\"#eee\">" + repo + "||<bgcolor=\"#eee\">''Variant''|| ||")
    repo_colors = {}
    for repo in sorted(list(mp_repo_sets[key])):
        if repo in keys:
            continue
        status = repo_mstatuses.get(repo, 'unknown')
        if 'unmaintained' in status:
            repo_colors[repo] = '<bgcolor="#fdfd96"> '
            status = repo_colors[repo] + status
        elif 'unmaintained' not in status and 'maintained' in status:
            repo_colors[repo] = '<bgcolor="#77dd77"> '
            status = repo_colors[repo] + status
        elif 'developed' in status:
            repo_colors[repo] = '<bgcolor="#77dd77"> '
            status = repo_colors[repo] + status
        elif 'end-of-life' in status:
            repo_colors[repo] = '<bgcolor="#ff6961"> '
            status = repo_colors[repo] + status
        elif 'not released' in status:
            repo_colors[repo] = '<bgcolor="#ff6961"> '
            status = repo_colors[repo] + status
        else:
            # Set unknown if not matched any of the above
            repo_colors[repo] = '<bgcolor="#ddd"> '
            status = repo_colors[repo] + status
        repo_pkgs = mp_repo_sets[key][repo]
        repo_msg = "||<bgcolor=\"#eee\">[[" + repo + "]]||" + status + "|| "
        try:
            print(repo_msg + repo_pkgs[repo] + "||")
        except (KeyError, UnicodeEncodeError):
            print(repo_msg + "||")
        if len(repo_pkgs) == 1 and list(repo_pkgs.keys())[0] == repo:
            continue
        for dep in sorted(repo_pkgs.keys()):
            if dep not in keys and dep != repo:
                print("||<bgcolor=\"#eee\"> ==> [[" + dep +
                      "]]||" + repo_colors[repo] +
                      " ||" + repo_pkgs[dep] + "||")
    print()

import time
print("''Generated: {0}''".format(time.strftime("%c")))
