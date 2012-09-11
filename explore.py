import competition_utilities as cu
import csv
import datetime
import features
import numpy as np
import pandas as pd
import re
import math

##############################################################
###### FEATURE FUNCTIONS
##############################################################

def user_age(pcd,ocd):
    import dateutil.parser
    pcd = dateutil.parser.parse(pcd)
    ocd = dateutil.parser.parse(ocd)
    return (pcd - ocd).total_seconds()

def more_than_one_paragraph(e):
    nb_new_lines = len([ c for c in e if c == '\n' ])
    display_lines = e.split('\n')
    nb_display_lines = 0
    for line in display_lines:
        nb_display_lines += math.ceil(len(line)/102)
    if not nb_new_lines:
        return 1.0
    return nb_display_lines / float(nb_new_lines)

def nb_badges(e):
    from badges import badges
    return badges.get(int(e),0)


###########################################################
import csv, random
def online_extract_features(fn):
    fea = dict()
    fd = open(fn,'rb')
    reader = csv.reader(fd,
                        delimiter=',',
                        quotechar='"',
                        quoting=csv.QUOTE_MINIMAL)
    header = None
    for row in reader:
        if not header:
            header = row
            blen_index = header.index('BodyMarkdown')
            user_index = header.index('OwnerUserId')
            userdate_index = header.index('OwnerCreationDate')
            postdate_index = header.index('PostCreationDate')
            title_index = header.index('Title')
            tags_indexes = [ header.index('Tag%d'%i) for i in range(1,6) ]
            reput_index = header.index('ReputationAtPostCreation')
            st_index = header.index('OpenStatus')
            break

    for f in ('BodyCharLength',
              'BodyWordLength',
              'BodyCodeLines',
              'NumTags',
              'TitleLengthWords',
              'ReputationAtPostCreation',
              'NbBadges',
              'UserAge',
              'MoreThanOneParagraph'):
        print '%s\t'%f,
    print

    log = open('special.csv','w')

    for row in reader:
        if row[st_index] == 'open':
            continue
        print >>log,'\t'.join([ _.replace('\n','\\n') for _ in row ])
        print '%s\t'%row[st_index],
        print '%s\t'%len(row[blen_index]),
        print '%s\t'%len(row[blen_index].split(' ')),
        print '%s\t'%len(row[blen_index].split('\n    ')),
        print '%s\t'%len([ row[i] for i in tags_indexes if len(row[i]) ]),
        print '%s\t'%len(row[title_index].split(' ')),
        print '%s\t'%int(row[reput_index]),
        print '%s\t'%nb_badges(row[user_index]),
        print '%s\t'%user_age(row[postdate_index],row[userdate_index]),
        print '%s\t'%more_than_one_paragraph(row[blen_index])

online_extract_features('data/train.csv')
