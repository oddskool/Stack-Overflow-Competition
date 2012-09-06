import sys, os
import competition_utilities as cu
import features

from sklearn.ensemble import RandomForestClassifier
from sklearn import cross_validation
import scipy as sp
import cPickle as pickle

train_file = "train-sample.csv"
full_train_file = "train.csv"
test_file = "public_leaderboard.csv"
submission_file = "submission.csv"

def make_submission():
    print("Reading data")
    fea, status = features.online_extract_features('data/train.csv',
                                                   limit=5e6)
    print("Training the model")
    rf = RandomForestClassifier(n_estimators=50,
                                verbose=2,
                                compute_importances=True,
                                oob_score=True,
                                #criterion='entropy',
                                n_jobs=1)
    
    rf.fit(fea, status['OpenStatus'])
    print "Features Importance:"
    imps = zip(rf.feature_importances_,
               fea.keys())
    imps.sort(reverse=True)
    print '\n'.join([ str(_) for _ in imps ])
    print "Generalization Error:", rf.oob_score_

    print("Reading test file and making predictions")
    data = cu.get_dataframe(test_file)
    test_features = features.online_extract_features('data/'+test_file,
                                                     train=False,
                                                     limit=1e12)[0]
    probs = rf.predict_proba(test_features)

    if True:
        print("Calculating priors and updating posteriors")
        new_priors = cu.get_priors(full_train_file)
        old_priors = cu.get_priors(train_file)
        probs = cu.cap_and_update_priors(old_priors, probs, new_priors, 0.001)
    
    print("Saving submission to %s" % submission_file)
    cu.write_submission(submission_file, probs)

if __name__=="__main__":
    make_submission()

