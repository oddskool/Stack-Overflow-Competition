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

feature_names = [ "BodyLength",
                  "ReputationAtPostCreation",
                  "NumTags",
                  "OwnerUndeletedAnswerCountAtPostTime",
                  "TitleLength",
                  "UserAge",
                  "ReputationAtPostCreationOverUserAgeRatio",
                  #"UndeletedAnswersOverUserAgeRatio",
                  #"MoreThanOneParagraph",
                  "NbBadges"
                ]

def make_submission():
    data = None
    if os.path.exists('data.pik'):
        print("Unpickeling the data")
        data = pickle.load(open('data.pik'))
    else:
        print("Reading the data")
        data = cu.get_dataframe(full_train_file)
        pickle.dump(data,open('data.pik','w'))

    fea = None
    if os.path.exists('fea.pik'):
        print("Unpickeling the fea")
        fea = pickle.load(open('fea.pik'))
    else:
        print("Extracting features")
        fea = features.extract_features(feature_names, data)
        pickle.dump(fea,open('fea.pik','w'))
    
    print("Training the model")
    rf = RandomForestClassifier(n_estimators=50,
                                verbose=2,
                                compute_importances=True,
                                oob_score=True,
                                #criterion='entropy',
                                n_jobs=2)
    
    rf.fit(fea, data["OpenStatus"])
    print "Features Importance:"
    imps = zip(rf.feature_importances_,
               feature_names,)
    imps.sort(reverse=True)
    print '\n'.join([ str(_) for _ in imps ])
    print "Generalization Error:", rf.oob_score_

    print("Reading test file and making predictions")
    data = cu.get_dataframe(test_file)
    test_features = features.extract_features(feature_names, data)
    probs = rf.predict_proba(test_features)

    if True:
        print("Calculating priors and updating posteriors")
        new_priors = cu.get_priors(full_train_file)
        old_priors = cu.get_priors(train_file)
        probs = cu.cap_and_update_priors(old_priors, probs, new_priors, 0.001)
    
    print("Saving submission to %s" % submission_file)
    cu.write_submission(submission_file, probs)


def llfun(act, pred):
    epsilon = 1e-15
    pred = sp.maximum(epsilon, pred)
    pred = sp.minimum(1-epsilon, pred)
    ll = sum(act*sp.log(pred) + sp.subtract(1,act)*sp.log(sp.subtract(1,pred)))
    ll = ll * -1.0/len(act)
    return ll

def cross_validate():
    print("Reading the data")
    data = cu.get_dataframe(train_file)

    print("Cross-Validating")
    rf = RandomForestClassifier(n_estimators=10,
                                verbose=1,
                                compute_importances=True,
                                n_jobs=2)
    cv = cross_validation.KFold(len(data),
                                k=10,
                                indices=False)
    results = []
    for traincv, testcv in cv:
        print "\t-- cv [%d]"%len(results)
        print "\t","extracting features"
        #...
        feacv = features.extract_features(feature_names,
                                          traincv)
        print "\t","learning"
        rf.fit(feacv, data["OpenStatus"])
        print "\t","predicting"
        probs = rf.predict_proba(testcv)
        print "\t","evaluating"
        results.append( llfun(target[testcv],
                              [x["OpenStatus"] for x in probas]) )
    print "LogLoss: " + str( np.array(results).mean() )

if __name__=="__main__":
    if not len(sys.argv) == 2:
        print "usage: %s submit|cv"%sys.argv[0]
        sys.exit(-1)
    if sys.argv[1] == 'submit':
        make_submission()
    else:
        cross_validate()
