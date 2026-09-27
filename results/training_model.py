import pandas as pd
import numpy as np

from sklearn.model_selection import learning_curve
from sklearn.metrics import accuracy_score
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

import matplotlib.pyplot as plt
import joblib


# 1. Load data

train = pd.read_csv("../data/train.csv")
test = pd.read_csv("../data/test.csv")

X = train["Text"]
y = train["Category"]


# 2. Create Pipeline
#  TF-IDF preprocessing &&  LogisticRegression() modul
pipeline = Pipeline([
    (
        "tfidf",
        TfidfVectorizer(
            ngram_range=(1, 2),
            stop_words="english"
        )
    ),
    (
        "classifier",
        LogisticRegression(max_iter=1000)
    )
])


# 3. Learning Curve

train_sizes, train_scores, val_scores = learning_curve(
    pipeline,
    X,
    y,
    cv=5,
    scoring="accuracy",
    train_sizes=np.linspace(0.1, 1.0, 5)
)


# 4. Mean and std

train_mean = train_scores.mean(axis=1)
val_mean = val_scores.mean(axis=1)

train_std = train_scores.std(axis=1)
val_std = val_scores.std(axis=1)


# 5. Plot

plt.plot(
    train_sizes,
    train_mean,
    label="Training score"
)

plt.plot(
    train_sizes,
    val_mean,
    label="Validation score"
)

plt.fill_between(
    train_sizes,
    train_mean - train_std,
    train_mean + train_std,
    alpha=0.2
)

plt.fill_between(
    train_sizes,
    val_mean - val_std,
    val_mean + val_std,
    alpha=0.2
)

plt.xlabel("Training examples")
plt.ylabel("Accuracy")
plt.title("Learning Curve")
plt.legend()
plt.grid()

plt.savefig("learning_curves.png")
plt.show()


# 6. Train final model

pipeline.fit(X, y)


# 7. Final test accuracy

X_test = test["Text"]
y_test = test["Category"]

y_test_pred = pipeline.predict(X_test)

test_accuracy = accuracy_score(
    y_test,
    y_test_pred
)

print("Final test accuracy =", test_accuracy)


# 8. Save model

joblib.dump(
    pipeline,
    "topic_classifier.pkl"
)

print("Model saved successfully.")