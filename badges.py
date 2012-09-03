import sys

badges = {}

with open('/home/ediemert/datasets/stackoverflow/badges.xml') as fd:
    _ = 0
    print "reading badges..."
    for line in fd:
        _ += 1
        print "\r%d"%_,
        l = line.strip()
        if not 'UserId' in l:
            continue
        elements = l.split(' ')
        uid = int(elements[2].split('"')[1])
        badges[uid] = badges.get(uid,0) + 1
    print
