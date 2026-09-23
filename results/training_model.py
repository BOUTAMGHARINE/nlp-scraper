import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer


train = pd.read_csv("../data/train.csv")
test = pd.read_csv("../data/test.csv")
print(test.head())





X = train.drop("Category",axis=1)
y=train["Category"] 
X_train, X_val, y_train, y_val = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)
print(train.columns)
print(train.head())
print(train.shape)
print(train["Category"].value_counts())