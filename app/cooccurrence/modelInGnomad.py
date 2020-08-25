from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn import tree
import pandas as pd
from sklearn import preprocessing
import pickle
import sys
import matplotlib.pyplot as plt
import sklearn


def main():
    if len(sys.argv) != 5:
        print('input-dir output-dir test_pct normalize')
        sys.exit(1)

    inputDir =sys.argv[1]
    outputDir = sys.argv[2]
    test_pct = float(sys.argv[3])
    normalize = bool(sys.argv[4])

    le = preprocessing.LabelEncoder()

    # build model based on f5 copd
    df1 = pd.read_csv(inputDir + '/F5/f5_chr17_brca1_copdhmb_report.tsv', sep='\t')
    df2 = pd.read_csv(inputDir + '/F5/f5_chr13_brca2_copdhmb_report.tsv', sep='\t')

    features = ['popFreq', 'AF', 'hail_hweafp', 'chisquare', 'class']
    features = ['popFreq', 'AF', 'hail_hweafp', 'chisquare']


    #model_1_dt = buildModel(df1, features, tree.DecisionTreeClassifier(max_depth=2), test_pct)
    #model_2_dt = buildModel(df2, features, tree.DecisionTreeClassifier(max_depth=2), test_pct)

    model_1_rf = buildModel(df1, features, RandomForestClassifier(n_estimators=100), test_pct, normalize, le)
    model_2_rf = buildModel(df2, features, RandomForestClassifier(n_estimators=100), test_pct, normalize, le)

    # save RF models
    f = open(outputDir + '/brca1_rf_model', 'wb')
    pickle.dump(model_1_rf, f)
    f.close()
    f = open(outputDir + '/brca2_rf_model', 'wb')
    pickle.dump(model_2_rf, f)
    f.close()

    # predict for f8 gru + hmb
    brca1_f8_report_DF = pd.read_csv(inputDir + '/F8/f8_chr17_brca1_gruhmb_report.tsv', header=0, sep='\t')
    brca2_f8_report_DF = pd.read_csv(inputDir + '/F8/f8_chr13_brca2_gruhmb_report.tsv', header=0, sep='\t')

    brca1_f8_predictions = getPredictions(brca1_f8_report_DF, model_1_rf, features, normalize, le)
    brca2_f8_predictions = getPredictions(brca2_f8_report_DF, model_2_rf, features, normalize, le)

    # save to disk
    brca1_f8_predictions.to_csv(outputDir + '/F8/f8_chr17_brca1_predictions_report.tsv', sep='\t')
    brca2_f8_predictions.to_csv(outputDir + '/F8/f8_chr13_brca2_predictions_report.tsv', sep='\t')

    brca1_f8_predictions = pd.read_csv(inputDir + '/F8/f8_chr17_brca1_predictions_report.tsv', header=0, sep='\t')
    brca2_f8_predictions = pd.read_csv(inputDir + '/F8/f8_chr13_brca2_predictions_report.tsv', header=0, sep='\t')

    # shave off variants from df that are predicted to be in gnomad and save to disk
    brca1_in = brca1_f8_predictions.loc[(brca1_f8_predictions['gnomadPrediction'] == True)]['variant']
    brca2_in = brca2_f8_predictions.loc[(brca2_f8_predictions['gnomadPrediction'] == True)]['variant']

    brca1_in.to_csv(outputDir + '/F8/brca1_in.txt', index=False, header=0)
    brca2_in.to_csv(outputDir + '/F8/brca2_in.txt', index=False, header=0)



def getPredictions(df, model, features, normalize, le):
    predictions = list()

    for f in features:
        if isinstance(df[f].iloc[0], str):
            df[f] = le.fit_transform(df[f])

    if normalize:
        X = preprocessing.normalize(df[features])

    for i in range(len(X)):
        variant = df.iloc[i]
        predicted = model.predict([list(variant[features])])
        predictions.append(predicted[0])
    df['gnomadPrediction'] = predictions
    return df

def buildModel(df, features, model, testPctg, normalize, le):
    print('building model type ' + str(type(model)))

    # transform boolean to numerica
    for f in features:
        if isinstance(df[f].iloc[0], str):
            df[f] = le.fit_transform(df[f])

    # define features and labels
    if normalize:
        X = preprocessing.normalize(df[features])
        Y = df[['inGnomad']]

    # find fraction of true false in data set
    Y_true = len(Y[Y['inGnomad'] == True])
    Y_false = len(Y[Y['inGnomad'] == False])
    print("fraction of false in df1 = " + str(Y_false/(Y_true + Y_false)))

    # split data
    X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=testPctg)

    # build model
    model.fit(X_train, y_train)
    y_predict_train = model.predict(X_train)
    print('unnormalized train accuracy = ' + str(accuracy_score(y_train, y_predict_train)))
    y_predict_test = model.predict(X_test)
    print('unnormalized test accuracy = ' + str(accuracy_score(y_test, y_predict_test)))

    if isinstance(model, sklearn.tree.DecisionTreeClassifier):
        plt.figure()
        tree.plot_tree(model,filled=True)
        plt.show()
        #plt.savefig('/content/gdrive/My Drive/RESEARCH/TOPMED/brca1-dtree.eps',format='eps',bbox_inches = "tight")

    elif isinstance(model, sklearn.ensemble.forest.RandomForestClassifier):
        print('feature importance: ' + str(model.feature_importances_))

    return model

if __name__ == "__main__":
    main()