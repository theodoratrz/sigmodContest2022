import string
import pandas as pd 
import numpy as np 
import matplotlib.pyplot as plt 
import seaborn as sns 

from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler, normalize
from sklearn.metrics import silhouette_score 
from sklearn.feature_extraction import text


def cluster(n):
	#read , clean , etc
	X_filepath = "X1.csv"
	Y_filepath = "Y1.csv"
	X = pd.read_csv(X_filepath)
	Y = pd.read_csv(Y_filepath)
	X_fixed = X.drop(columns=['id'])
	X_fixed.fillna(" ", inplace=True)
	X_sum = [' '.join([j[:100] for j in X_fixed.iloc[i]]) for i in range(X_fixed.shape[0])]
	X_sum = [i.translate(str.maketrans('', '', string.punctuation)) for i in X_sum]



	# vectorize data 
	vectorizer = text.TfidfVectorizer(min_df = 0.1 ,k max_df=0.9, stop_words=text.ENGLISH_STOP_WORDS)
	X_tfidf = vectorizer.fit_transform(X_sum).toarray()


	#create kmeans 
	kmeans = KMeans(n)
	kmeans.fit(X_tfidf)
	labels = kmeans.labels_
	# print(type(labels))

	#for every cluster save points and indices 
	# points hold the vectorized data for each cluster
	# indices hold the index of each row for each cluster
	points = {}
	indices = {}
	for i in range(n):
		points[i] = []
		indices[i] = [] 
	for i in range(len(labels)):
		points[labels[i]].append(X_tfidf[i])
		indices[labels[i]].append(i)

	for key, cluster in points.items():
		print(len(cluster))	


	return points,indices

