import sys

badges = {}

with open('./data/badges.xml') as fd:
    _ = 0
    for line in fd:
        _ += 1
        l = line.strip()
        if not 'UserId' in l:
            continue
        elements = l.split(' ')
        uid = int(elements[2].split('"')[1])
        badges[uid] = badges.get(uid,0) + 1


