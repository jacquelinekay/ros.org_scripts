with open('robots_dump.txt', 'r') as f:
    raw_robots = f.read()

robot_cells = [r.strip() for r in raw_robots.split('||') if r.strip()]

robot_entries = []
assert(len(robot_cells) % 2 == 0)
for x in range(len(robot_cells)):
    if x % 2 != 0:
        continue
    image = robot_cells[x]
    name = robot_cells[x + 1]
    link = None
    if image.startswith('[['):
        image.strip('[]')
        link_split = image.split('|')
        image = '|'.join(link_split[1:])
        link_split = image.split('}}')
        image = link_split[0] + '}}'
        if len(link_split) == 3:
            link = link_split[2]
    if image.startswith('{{'):
        image = image.strip('{}')
        assert not image.startswith('{') and not image.endswith('}')
    if '|' in image:
        image_split = image.split('|')
        image = image_split[0]
    name = name.strip('[]')
    name_split = name.split('|')
    if link:
        assert link == name_split[0], (link, name_split[0])
    if not link and len(name_split) > 1:
        link = name_split[0]
    if len(name_split) != 2 and link is None:
        link = name
    if len(name_split) == 1:
        name = name_split[0]
    else:
        assert len(name_split) == 2
        name = name_split[1]
    robot_entries.append({
        'image': image,
        'name': name,
        'link': link
    })

lines = []
for entry in robot_entries:
    lines += ["<<RobotEntry({name}, {image}, {link})>>".format(**entry)]

print("\n".join(lines))
