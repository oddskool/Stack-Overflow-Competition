import competition_utilities as cu
import csv
import datetime
import features
import numpy as np
import pandas as pd
import re
import math

def camel_to_underscores(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

##############################################################
###### FEATURE FUNCTIONS
##############################################################

def body_length(data):
    return data["BodyMarkdown"].apply(len)

def num_tags(data):
    return pd.DataFrame.from_dict({"NumTags": [sum(map(lambda x:
                    pd.isnull(x), row)) for row in (data[["Tag%d" % d
                    for d in range(1,6)]].values)] } ) ["NumTags"]

def title_length(data):
    return data["Title"].apply(len)

def user_age(data):
    return pd.DataFrame.from_dict({"UserAge": (data["PostCreationDate"]
            - data["OwnerCreationDate"]).apply(lambda x: x.total_seconds())})

def reputation_at_post_creation_over_user_age_ratio(data):
    return pd.DataFrame.from_dict({"ReputationAtPostCreationOverUserAgeRatio": data["ReputationAtPostCreation"] / (data["PostCreationDate"] - data["OwnerCreationDate"]).apply(lambda x: x.days)})

def undeleted_answers_over_user_age_ratio(data):
    return pd.DataFrame.from_dict({"UndeletedAnswersOverUserAgeRatio": data["OwnerUndeletedAnswerCountAtPostTime"] / (data["PostCreationDate"] - data["OwnerCreationDate"]).apply(lambda x: x.days)})

def more_than_one_paragraph(data):
    def computer(e):
        nb_new_lines = len([ c for c in e if c == '\n' ])
        display_lines = e.split('\n')
        nb_display_lines = 0
        for line in display_lines:
            nb_display_lines += math.ceil(len(line)/102)
        if not nb_new_lines:
            return 1.0
        return nb_display_lines / float(nb_new_lines)
    return pd.DataFrame.from_dict({"MoreThanOneParagraph":data["BodyMarkdown"].apply(computer)})

###########################################################

def extract_features(feature_names, data):
    fea = pd.DataFrame(index=data.index)
    for name in feature_names:
        if name in data:
            fea = fea.join(data[name])
        else:
            fea = fea.join(getattr(features, 
                                   camel_to_underscores(name))(data))
    return fea

if __name__=="__main__":
    feature_names = [ "BodyLength"
                    , "NumTags"
                    , "OwnerUndeletedAnswerCountAtPostTime"
                    , "ReputationAtPostCreation"
                    , "TitleLength"
                    , "UserAge"
                    ]
              
    data = cu.get_dataframe("C:\\Users\\Ben\\Temp\\StackOverflow\\train-sample.csv")
    features = extract_features(feature_names, data)
    print(features)
