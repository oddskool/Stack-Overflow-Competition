import sys, os
import competition_utilities as cu
import features

from sklearn.ensemble import RandomForestClassifier
from sklearn import cross_validation
import scipy as sp
import cPickle as pickle
import numpy as np

train_file = "train-sample.csv"
full_train_file = "train.csv"
test_file = "public_leaderboard.csv"
submission_file = "submission.csv"

def learn(X,y):
    print "\t-- learning model..."
    model = RandomForestClassifier(n_estimators=50,
                                   verbose=2,
                                   compute_importances=True,
                                   oob_score=True,
                                   #criterion='entropy',
                                   n_jobs=1)
    
    model.fit(X,y)
    print "\t-- computing feature importances"
    imps = zip(model.feature_importances_,
               X.keys())
    imps.sort(reverse=True)
    print '\n'.join([ '\t'+str(_) for _ in imps ])
    print "\t-- generalization error:", model.oob_score_
    return model

def or_binarize(e):
    if e == 'open':
        return 'open'
    else:
        return 'not_open'

def _dim(df,txt):
    print 'dim(%s)'%txt
    if type(df) == list:
        print len(df)
    else:        
        print [ f for f in df.keys() ]
        print [ len(df[f]) for f in df.keys() ]

def make_submission():
    print("Reading data")
    fea, status = features.online_extract_features('data/train.csv',
                                                   train=True,
                                                   limit=1e9)
    _dim(fea,'fea')
    print("Training Level 1 : Open/Rest model")
    open_status = [ or_binarize(e) for e in status['OpenStatus']  ]
    is_not_open_status = [ s != 'open' for s in open_status ]
    or_model = learn(fea,open_status)

    print("Training Level 2 : Not Open Split model")
    not_open_status = [ status['OpenStatus'][i] for i in range(len(is_not_open_status)) if is_not_open_status[i] ]
    no_fea = fea[is_not_open_status]
    _dim(no_fea,'no_fea')
    no_model = learn(no_fea,not_open_status)
    
    print("Reading test file and making predictions")
    test_features = features.online_extract_features('data/'+test_file,
                                                     train=False,
                                                     limit=1e9)[0]
    _dim(test_features,'test_features')
    or_probs = or_model.predict_proba(test_features)
    probs = []
    for i in range(0,len(or_probs)):
        or_prob = or_probs[i]
        if or_prob[0] > or_prob[1]:
            probs.append(np.array([1.0,0.0,0.0,0.0,0.0]))
        else:
            f = [ test_features[ff][i] for ff in test_features.keys() ]
            a = no_model.predict_proba(f)
            aa = np.insert(a,0,[0.0])
            probs.append(aa)
    probs = np.array(probs)

    if False:
        print("Calculating priors and updating posteriors")
        new_priors = cu.get_priors(full_train_file)
        old_priors = cu.get_priors(train_file)
        probs = cu.cap_and_update_priors(old_priors, probs, new_priors, 0.001)
    
    print("Saving submission to %s" % submission_file)
    cu.write_submission(submission_file, probs)

if __name__=="__main__":
    make_submission()

