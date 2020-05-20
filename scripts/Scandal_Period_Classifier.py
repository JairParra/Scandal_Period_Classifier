# -*- coding: utf-8 -*-
"""
Created on Mon Apr 29 20:20:06 2019

@author: Hair Albeiro Parra Barrera 
@id: 260738619

The following is my implementation of a classifier for articles in which the agency 
"PEMEX" is mentioned, which outputs whether such articles were written during 
a scandal period. Details of implementaion with comments follow.  

I had a lot of fun and learned a lot working on this. Looking forward for more!
"""

### Scandal Period Article classifier ###

## **************** CODE *********************** ##

### ??? ### 

# This will make your computer speak
from win32com.client import Dispatch
speak = Dispatch("SAPI.SpVoice")

### Data Preprocessing ###

print("Welcome to the Scandal classifier")
speak.speak("Welcome to the Scandal classifier")

## Imports ##

print("Importing librarires...")
speak.speak("Importing libraries...")

import pandas as pd 
import numpy as np
import matplotlib.pyplot as plt 
import seaborn as sns # data visualization 
 
## Data Loading and Shape ##

print("Loading data...")
speak.speak("Loading data")

# load the data files
path_anomaly = "C:\\Users\\jairp\\Desktop\\INTERVIEW\\InterviewChallenge\\anomaly_periods.csv" # please change PATH accordingly
path_periods = "C:\\Users\\jairp\\Desktop\\INTERVIEW\\InterviewChallenge\\article_data.csv" # please change PATH accordingly
anomaly_periods = pd.read_csv(path_anomaly)
article_data = pd.read_csv(path_periods)

# observe the shape of the data 
print("anomaly_periods data shape: {}".format(anomaly_periods.shape))
print("article_data data shape: {}".format(article_data.shape))

## Data preprocessing ##

print("Preprocessing Data...")
speak.speak("Preprocessing Data")

# Since we are interested in the PEMEX agency, we will 
# subset the anomaly periods data. We will also convert them to 
# time data instead. Also, the first and second column are redundant, 
# so we will eliminate them as well. 
PEMEX_anomaly_p = anomaly_periods[anomaly_periods['agency'].str.match('PEMEX')]
PEMEX_anomaly_p[["start_date","end_date"]].apply(pd.to_datetime)
PEMEX_anomaly_p = PEMEX_anomaly_p.drop('agency', axis=1) # they all are the same agency, redundant
PEMEX_anomaly_p = PEMEX_anomaly_p.drop('Unnamed: 0', axis=1) # index not needed
# This will constitute our labels .

# filter to get only rows that contain the PEMEX agency
# and change the date format. Also fill nan values with NONE
PEMEX_article_data = article_data[article_data['agencies'].str.contains("PEMEX")]
PEMEX_article_data["date"].apply(pd.to_datetime)
PEMEX_article_data = PEMEX_article_data.replace(np.nan, "NONE")
PEMEX_article_data["date"] = PEMEX_article_data["date"].replace("NONE", pd.to_datetime('1-1-1')) # replace by default dates

# Now, we will turn the PEMEX anomaly periods into labels 
PEM_anomp_dict = PEMEX_anomaly_p.to_dict('index')

# LEGEND: 
    # {30: {'start_date': '2007-07-05', 'end_date': '2007-07-18'},
    # 33: {'start_date': '2007-09-08', 'end_date': '2007-09-16'},
    # 45: {'start_date': '2008-03-24', 'end_date': '2008-04-18'},
    # 53: {'start_date': '2008-07-13', 'end_date': '2008-07-30'},
    # 111: {'start_date': '2013-01-27', 'end_date': '2013-02-11'},
    # 117: {'start_date': '2013-08-10', 'end_date': '2013-08-21'},
    # 125: {'start_date': '2014-07-23', 'end_date': '2014-08-05'}}
    
# The previous will facilitate access to training labels.
# NOTE: dict entries are in str format
    
def is_within_scandal(date):
    """ Date is in datetime format. 
        Returns a touple with whether or not it belongs an anomaly, 
        and the anomaly period index where it was found. 
        Index will be -1 if wasn't found. """
    is_within = False
    anomp_index = -1 # anomaly period key where it was found
    date = pd.to_datetime(date) # convert to datatime
    for i in PEM_anomp_dict: # get the key, convert to time format
        lower = pd.to_datetime(PEM_anomp_dict[i]['start_date']) # lower bound date 
        upper = pd.to_datetime(PEM_anomp_dict[i]['end_date']) # upper bound date 
        if( date >= lower and date <= upper):
            is_within = True
            anomp_index = i
            break
    return is_within, anomp_index

# Using the function defined above, we want to further filter the data to only those rows 
# that belong to some anomaly period. 
    
anomaly_index = [] # will store the index where scandal was found
within_scandal = [] # 1 if included, 0 if not 


# Pandas(Index=77896, _1=77896, id=8462, source='El Universal (Mexico)', date='2014-01-10', 
#        title='México tiene rumbo claro y está en movimiento, dice Peña', 
#        byline='BYLINE: Agencia el Universal', story='MÉXICO ... ', 
#        agencies="['CFE' 'PEMEX']")

# WARNING: not  efficient, but I couldn't think of a faster way for now... 
for row in PEMEX_article_data.itertuples():
    date = str(row.date)
    is_within, anomp_index = is_within_scandal(date)
    print("index: {}  date: {}  source: {} agency: {}".format(row.Index,date, str(row.source), str(row.agencies)))
    if(is_within):
        anomaly_index.append(anomp_index)
        within_scandal.append(1) # True
    else: 
        anomaly_index.append(-1)
        within_scandal.append(0) # False

# Now that we have the data of whether the articles belong to the scandal period, 
# we can append these to PEMEX_article_data dataset. 
PEMEX_article_data['within_scandal'] = within_scandal
PEMEX_article_data['anomaly_index'] = anomaly_index 
# Note: we would use the anomaly_index if we wanted to in addition perform a multi-way classification

print("Done")
speak.speak("Done")

## OPTIONAL: Countplot for anomaly periods

PEMEX_article_data_scandal = PEMEX_article_data[PEMEX_article_data['anomaly_index'] != -1] 
plt.figure(1)
sns.countplot(PEMEX_article_data_scandal['anomaly_index'] ,label="Count")
plt.show()

### Building the Classifier ###

print("Classifier building stage starting...")
speak.speak("Classifier building stage starting")
speak.speak("Spanish stop words will be used")

#from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model.logistic import LogisticRegression
from sklearn.model_selection import train_test_split, cross_val_score, cross_val_predict
from nltk.corpus import stopwords
spanish_stopwords = stopwords.words('spanish') # to ginore unimportant content 

print("Splitting data into features and labels...")
speak.speak("Splitting data into features and labels")

# Split the data into labels and features 
Y = PEMEX_article_data['within_scandal'] # Labels =  {0,1}
X = PEMEX_article_data[['title','byline', 'story']] # Factors 

# Split the data into training and testing sets 
X_train_raw, X_test_raw, y_train, y_test = train_test_split(X,Y, test_size=0.25) 

### Vectorize the inputs ###   

print("Beginning input vectorization and model building...")
speak.speak("Beginning vector vectorization and model building")

print("Classifiers will be build on the features 'title', 'byline' and 'story' separatedly")
speak.speak("Classifiers will be build on the features 'title', 'byline' and 'story' separatedly")
print("Logistic regression will be performed to fit the models. Finally, a combined model will be analyzed.")
speak.speak("Logistic regression will be performed to fit the models. Finally, a combined model will be analyzed.")


## NLP by 'title' feature

print("Beginning fit by 'title' feature")
speak.speak("Fitting model with the 'title' feature ")

X1 = PEMEX_article_data['title']
X1_train_raw, X1_test_raw, y_train, y_test = train_test_split(X1,Y, test_size=0.25) 
cvec = CountVectorizer(stop_words = spanish_stopwords).fit(X1_train_raw)
df_train1 = pd.DataFrame(cvec.transform(X1_train_raw).todense(), 
                         columns = cvec.get_feature_names())
df_test1 = pd.DataFrame(cvec.transform(X1_test_raw).todense(), 
                        columns = cvec.get_feature_names())

print("Done")

# After transforming these to a dense matrix, want to verify that the amount of features match
print(df_train1.shape)
print(y_train.shape)
print(df_test1.shape)
print(y_test.shape)

# Fit the model 
lr = LogisticRegression() 
lr.fit(df_train1, y_train) # fit the model
accuracy_title = round(lr.score(df_test1, y_test)*100,2) # round to 2 decimal places 
print("Model accuracy: {}%".format(accuracy_title))
speak.speak("The model fits the data with {}% accuracy".format(accuracy_title))

# After fitting the model with only the title feature, we obtained a prediction score of nearly 
# 92.91% on the test set!!!! 


## NLP by 'byline'

print("Beginning fit by 'byline' feature")
speak.speak("Fitting model with the 'byline' feature ")


X2 = PEMEX_article_data['byline']
X2_train_raw, X2_test_raw, y_train, y_test = train_test_split(X2,Y, test_size=0.25) 
cvec = CountVectorizer(stop_words = spanish_stopwords).fit(X2_train_raw)
df_train2 = pd.DataFrame(cvec.transform(X2_train_raw).todense(), 
                         columns = cvec.get_feature_names())
df_test2 = pd.DataFrame(cvec.transform(X2_test_raw).todense(), 
                        columns = cvec.get_feature_names())

print("Done")

# After transforming these to a dense matrix, want to verify that the amount of features match
print(df_train2.shape)
print(y_train.shape)
print(df_test2.shape)
print(y_test.shape)

# Fit the model 
lr = LogisticRegression()
lr.fit(df_train2, y_train)
accuracy_byline = round(lr.score(df_test2, y_test)*100,2) # round to 2 decimal places 
print("Model accuracy: {}%".format(accuracy_byline))
speak.speak("The model fits the data with {}% accuracy".format(accuracy_byline))


# Using the byline feature along, we can fit a model that is 92.92% accurate 


### NLP by 'story' : Warning: possible Memory error, de-comment if want to see results
#
## WARNING: By doing this, the number of resultant classes from the vectorizor become HUGE
## so this process is extremely slow. I need to think of a better way of treatint these data.
#
#print("Beginning fit by 'story' feature ")
#print("WARNING: Fitting the model by this feature is extremely slow. Please be patient.")
#speak.speak("Fitting model with the 'story' feature ")
#speak.speak("WARNING: Fitting the model by this feature is extremely slow. Please be patient.")
#
#X3 = PEMEX_article_data['story']
#X3_train_raw, X3_test_raw, y_train, y_test = train_test_split(X3,Y, test_size=0.50) 
#cvec = CountVectorizer(stop_words = spanish_stopwords).fit(X3_train_raw)
#df_train3 = pd.DataFrame(cvec.transform(X3_train_raw).todense(), 
#                         columns = cvec.get_feature_names())
#df_test3 = pd.DataFrame(cvec.transform(X3_test_raw).todense(), 
#                        columns = cvec.get_feature_names())
#
#print("Done")
#
## After transforming these to a dense matrix, want to verify that the amount of features match
#print(df_train3.shape)
#print(y_train.shape)
#print(df_test3.shape)
#print(y_test.shape)
#
## Fit the model 
#lr = LogisticRegression()
#lr.fit(df_train3, y_train)
#accuracy_story = round(lr.score(df_test3, y_test)*100,2) # round to 2 decimal places 
#print("Model accuracy: {}%".format(accuracy_story))
#speak.speak("The model fits the data with {}% accuracy".format(accuracy_story))
#
#
## Appllying the vectorization algorithm to the actual stories, we also get an accuracy of
## approximatedly 93.62% ! That is not bad, but the computational expense is very big. 


## NLP by concatenating 

print("Buiding classifier with models 1 and 2")
speak.speak("Building classifiers with models 1 and 2")
    
# Now , we will use the first two models to create a model which makes users of the 
# 'title'and 'byline' features;  we will not use the third feature model as it takes a huge 
# amount of memory and it can be pretty slow too. 

train_catted = pd.concat([df_train1,df_train2], axis=1 ) 
test_catted= pd.concat([df_test1, df_test2], axis=1 )

print(train_catted.shape)
print(test_catted.shape)
print(y_train.shape)
print(y_test.shape)

print("Done")

lr = LogisticRegression()
lr.fit(train_catted, y_train)
accuracy_mix = round(lr.score(test_catted, y_test)*100,2) # round to 2 decimal places 
print("Model accuracy: {}%".format(accuracy_mix))
speak.speak("The model fits the data with {}% accuracy".format(accuracy_mix))

# We see by this by this new model that although the score is not bad, it is just about the same 
# as the previous three models! 

### Summary ### 

print("Summary")

print("Model 1: Logistic Regression by 'title' ")
print("Accuracy: {}".format(accuracy_title))
print("Model 2: Logistic Regression by 'byline' ")
print("Accuracy: {}".format(accuracy_byline))
print("Model 3: Logistic Regression by 'story' ")
print("Accuracy: ???")
print("Model 4: Logistic Regression by 'title' and 'byline' ")
print("Accuracy: {}".format(accuracy_mix))

speak.speak("End of the program")


### Conclusion ### 

# All in all, based on the prvious observations, I would choose the classifier either model 1 'title'
# or model 2 'byline' for the classifier, since the thirs model is computationally expensive to use 
# while not providing any significant better score. Moreover, when joining models together, we also don't 
# get a significantlt better score. 


### Comments ### 

# I had a lot of fun and learned a lot working on this assignment!!! It costed me a lot of work, try and error, 
# research and patience, but I'm definitely going to keep learning and imporving. 




 





    






