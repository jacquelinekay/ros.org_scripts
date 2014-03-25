"""
Generates wiki formatted output, which summarizes the status of the indigo variants
using the hydro distribution cache and accounting for chanages (like ros_comm_msgs).

To use it, checkout the indigo-devel branch of the metapackages repo at

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
hydro = get_cached_distribution(index, 'hydro')
indigo = get_cached_distribution(index, 'indigo')
dist_file = get_distribution_file(index, 'hydro')
indigo_dist_file = get_distribution_file(index, 'indigo')
dw = DependencyWalker(hydro)
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
            ignore_pkgs=['ros_comm_msgs'] + list(previous_pkgs)
        ))
    # print(" => ", len(mp_sets[mp]))

# Repos by package
repos_by_package = {}
repo_mstatuses = {}
for name, repo in dist_file.repositories.items():
    if not repo.release_repository:
        continue
    if name not in indigo_dist_file.repositories:
        repo_mstatuses[name] = 'not released'
    else:
        indigo_repo = indigo_dist_file.repositories[name]
        if indigo_repo.status:
            repo_mstatuses[name] = indigo_repo.status
    for pkg in repo.release_repository.package_names:
        repos_by_package[pkg] = name
repos_by_package['rosgraph_msgs'] = 'ros_comm_msgs'
repos_by_package['std_srvs'] = 'ros_comm_msgs'
repo_mstatuses['ros_comm_msgs'] = indigo_dist_file.repositories['ros_comm_msgs'].status
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
            pkg_xml = indigo.get_release_package_xml(dep)
        except KeyError:
            pkg_xml = None
        if pkg_xml:
            try:
                pkg = parse_package_string(pkg_xml)
                maintainer = '<<BR>>'.join(['[[mailto:%s|%s]]' % (m.email, m.name) for m in pkg.maintainers])
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
        if 'unmaintained' not in status and 'maintained' in status:
            repo_colors[repo] = '<bgcolor="#77dd77"> '
            status = repo_colors[repo] + status
        if 'unknown' in status:
            repo_colors[repo] = '<bgcolor="#ddd"> '
            status = repo_colors[repo] + status
        if 'end-of-life' in status:
            repo_colors[repo] = '<bgcolor="#ff6961"> '
            status = repo_colors[repo] + status
        if 'not released' in status:
            repo_colors[repo] = '<bgcolor="#ff6961"> '
            status = repo_colors[repo] + status
        print("||<bgcolor=\"#eee\">[[" + repo + "]]||" + status + "|| ||")
        repo_pkgs = mp_repo_sets[key][repo]
        if len(repo_pkgs) == 1 and list(repo_pkgs.keys())[0] == repo:
            continue
        for dep in sorted(repo_pkgs.keys()):
            if dep not in keys:
                print("||<bgcolor=\"#eee\"> ==> [[" + dep + "]]||" + repo_colors[repo] + " ||" + repo_pkgs[dep] + "||")
    print()
