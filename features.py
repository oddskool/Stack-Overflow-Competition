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

def what_how(title):
    t = title.lower()
    s = 0
    if 'what' in t:
        s+= 1
    if 'how' in t:
        s+= 1e1
    if 'best' in t:
        s+= 1e2
    if 'compare' in t:
        s+= 1e3
    if 'why' in t:
        s+= 1e4
    if 'favorite' in t:
        s+= 1e5
    if 'new' in t:
        s+= 1e6
    if 'most' in t:
        s+= 1e7
    if 'good' in t:
        s+= 1e8
    if 'which' in t:
        s+= 1e9
    if 'where' in t:
        s+= 1e10
    return s

###########################################################
import csv, random
def online_extract_features(fn, train=1,limit=1e5):
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
            if train:
                st_index = header.index('OpenStatus')
            break

    _ = 0
    for f in ('BodyCharLength',
              'BodyWordLength',
              'BodyCodeLines',
              'NumTags',
              'TitleCharLength',
              'TitleLengthWords',
              'ReputationAtPostCreation',
              'NbBadges',
              'UserAge',
              'MoreThanOneParagraph',
              'WhatHowTitle'):
        fea[f] = []
    status = {}
    status['OpenStatus'] = []
    nb_open = 0
    for row in reader:
        if train:
            if row[st_index] == 'open':
                nb_open += 1
                if not random.random() < 0.50:
                    continue
        _ += 1
        if not _ % 100:
            print "\r%d"%_,
        if _ > limit:
            break
        fea['MoreThanOneParagraph'].append(more_than_one_paragraph(row[blen_index]))
        fea['UserAge'].append(user_age(row[postdate_index],row[userdate_index]))
        fea['NbBadges'].append(nb_badges(row[user_index]))
        fea['TitleLengthWords'].append( len(row[title_index].split(' '))  )
        fea['TitleCharLength'].append( len(row[title_index])  )
        fea['BodyCharLength'].append( len(row[blen_index])  )
        fea['BodyWordLength'].append( len(row[blen_index].split(' '))  )
        fea['BodyCodeLines'].append( len(row[blen_index].split('\n    '))  )
        fea['NumTags'].append(len([ row[i] for i in tags_indexes if len(row[i]) ]))
        fea['ReputationAtPostCreation'].append(int(row[reput_index]))
        fea['WhatHowTitle'].append( what_how(row[title_index])  )
        if train:
            status['OpenStatus'].append(row[st_index])

    print nb_open,'/',_,'open'
    return pd.DataFrame.from_dict(fea),pd.DataFrame.from_dict(status)
