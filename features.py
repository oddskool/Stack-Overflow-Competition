import competition_utilities as cu
import csv
import datetime
import features
import numpy as np
import pandas as pd
import re, sys
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

def what_how(title):
    t = title.lower()
    s = 0
    if 'what' in t:
        return 1
    if 'how' in t:
        return 1e1
    if 'best' in t:
        return 1e2
    if 'compare' in t:
        return 1e3
    if 'why' in t:
        return 1e4
    if 'favorite' in t:
        return 1e5
    if 'new' in t:
        return 1e6
    if 'most' in t:
        return 1e7
    if 'good' in t:
        return 1e8
    if 'which' in t:
        return 1e9
    if 'where' in t:
        return 1e10
    return s

def nb_ref(txt):
    n = 0
    for i in range(10):
        if '  [%d]'%i in txt:
            n += 1
    return n

def nb_lists(txt):
    n = 0
    for i in range(10):
        if '  %d. '%i in txt:
            n += 1
    return n

def nb_qmarks(txt):
    return len([ c for c in txt if c == '?' ])

###########################################################
import csv, random
def online_extract_features(fn, train, limit):
    fea = dict()
    fd = open(fn,'rb')
    reader = csv.reader(fd,
                        delimiter=',',
                        quotechar='"',
                        quoting=csv.QUOTE_MINIMAL)
    header = reader.next()
    
    blen_index = header.index('BodyMarkdown')
    user_index = header.index('OwnerUserId')
    userdate_index = header.index('OwnerCreationDate')
    postdate_index = header.index('PostCreationDate')
    title_index = header.index('Title')
    tags_indexes = [ header.index('Tag%d'%i) for i in range(1,6) ]
    reput_index = header.index('ReputationAtPostCreation')
    if train:
        st_index = header.index('OpenStatus')

    for f in ('BodyCharLength',
              'BodyWordLength',
              'BodyCodeLines',
              'NumTags',
              'TitleCharLength',
              'TitleLengthWords',
              'ReputationAtPostCreation',
              'UserAge',
              'MoreThanOneParagraph',
              'WhatHowTitle',
              'NbRef',
              'NbLists',
              'NbQMarks'):
        fea[f] = []
    status = {}
    status['OpenStatus'] = []
    nb_open = 0
    nb_open_kept = 0
    nb_other = 0
    _i = 0
    for row in reader:
        _i += 1
        if _i > limit:
            break
        if train:
            if row[st_index] == 'open':
                nb_open += 1
                if not random.random() < 0.60:
                    nb_open_kept += 1
                    continue
            else:
                nb_other += 1
        print >>sys.stderr, "\ro:%d        k:%d        n:%d    i:%d"%(nb_open,
                                                                      nb_open_kept,
                                                                      nb_other,
                                                                      _i),
        fea['MoreThanOneParagraph'].append(more_than_one_paragraph(row[blen_index]))
        fea['UserAge'].append(user_age(row[postdate_index],row[userdate_index]))
        fea['TitleLengthWords'].append( len(row[title_index].split(' '))  )
        fea['TitleCharLength'].append( len(row[title_index])  )
        fea['BodyCharLength'].append( len(row[blen_index])  )
        fea['BodyWordLength'].append( len(row[blen_index].split(' '))  )
        fea['BodyCodeLines'].append( len(row[blen_index].split('\n    '))  )
        fea['NumTags'].append(len([ row[i] for i in tags_indexes if len(row[i]) ]))
        fea['ReputationAtPostCreation'].append(int(row[reput_index]))
        fea['WhatHowTitle'].append( what_how(row[title_index])  )
        fea['NbRef'].append(nb_ref(row[blen_index]))
        fea['NbLists'].append(nb_lists(row[blen_index]))
        fea['NbQMarks'].append(nb_qmarks(row[blen_index]))
        if train:
            status['OpenStatus'].append(row[st_index])

    print >>sys.stderr,""
    return pd.DataFrame.from_dict(fea),pd.DataFrame.from_dict(status)
