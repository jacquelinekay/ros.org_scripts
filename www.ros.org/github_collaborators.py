# Copyright (c) 2013 Open Source Robotics Foundation
# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:

# 1. Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.

# 2. Redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution.

# 3. Neither the name of the Open Source Robotics Foundation nor the
# names of its contributors may be used to endorse or promote products
# derived from this software without specific prior written
# permission.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.


# needs pygithub, yaml, rosdistro

from github import Github
import yaml
import os

import catkin_pkg.package
import rosdistro

maintainers = set()

ind = rosdistro.get_index(rosdistro.get_index_url())
for d in ind.distributions:
    release_cache = rosdistro.get_release_cache(ind, d)
    for p, x in release_cache.package_xmls.items():
        pkg = catkin_pkg.package.parse_package_string(x)
        for p in pkg.maintainers:
            #print p.email, p.name
            maintainers.add(p)

print "Found %s maintainers in %s" % (len(maintainers), ind.distributions)


g = Github() # Can add Oauth Token for higher rate limits

limit = g.get_rate_limit()
print "remaining API queries", limit.rate.remaining, "until", limit.rate.reset


output_filename = 'output.yaml'

orgs = ['ros',
        'ros-drivers',
        'ros-infrastructure',
        'ros-perception',
        'ros-gbp',
        'ros-manipulation',
        'ros-planning',
        'ros-visualization',
        'ros-simulation',
        'rosjava',
        'ros-control'
        ]

# debugging shortcut
#orgs = ['ros']

collaborators = {}

for o in orgs:
    try:
        print "Fetching collaborators for %s" % o
        gorg = g.get_organization(o)
        for r in gorg.get_repos():
            for u in r.get_collaborators():
                collaborators[u.login] = u
    except Exception as ex:
        print "failed to get org %s with error %s" % (o, ex)
output = {}

if os.path.exists(output_filename):
    with open(output_filename) as fh:
        output = yaml.load(fh.read())

for n, c in collaborators.items():
    if n in output:
        print "skipping %s already loaded" % n
        #continue
    name = c.name
    avatar = c.avatar_url
    email = c.email
    is_maintainer = email in [p.email for p in maintainers] or name in [p.name for p in maintainers]
    print "%s %s %s" % (name, avatar, email)
    output[n] = {'name': name,
                 'avatar': avatar,
                 'maintainer': is_maintainer}

with open(output_filename, 'w') as fh:
    yo = yaml.safe_dump(output)
    fh.write(yo)
print "wrote output to output.yaml"

limit = g.get_rate_limit()
print "remaining API queries", limit.rate.remaining, "until", limit.rate.reset
