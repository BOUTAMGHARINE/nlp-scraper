import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split, learning_curve
from sklearn.metrics import accuracy_score
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
import matplotlib.pyplot as plt
import joblib


# =========================
# 1. Load data
# =========================

train = pd.read_csv("../data/train.csv")
test = pd.read_csv("../data/test.csv")

X = train["Text"]
y = train["Category"]


# =========================
# 2. Train / Validation split
# =========================

X_train, X_val, y_train, y_val = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)


# =========================
# 3. TF-IDF
# =========================

vectorizer = TfidfVectorizer(
    ngram_range=(1, 2),
    stop_words="english"
)

X_train_tfidf = vectorizer.fit_transform(X_train)
X_val_tfidf = vectorizer.transform(X_val)


# =========================
# 4. Train Logistic Regression
# =========================

model = LogisticRegression(max_iter=1000)

model.fit(X_train_tfidf, y_train)


# =========================
# 5. Validation prediction
# =========================

y_pred = model.predict(X_val_tfidf)

accuracy = accuracy_score(y_val, y_pred)

print("Validation accuracy =", accuracy)


# =========================
# 6. Pipeline for Learning Curve
# =========================

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


# =========================
# 7. Learning Curve
# =========================

train_sizes, train_scores, val_scores = learning_curve(
    pipeline,
    X,
    y,
    cv=5,
    scoring="accuracy",
    train_sizes=np.linspace(0.1, 1.0, 5)
)


# =========================
# 8. Calculate mean and std
# =========================

train_mean = train_scores.mean(axis=1)
val_mean = val_scores.mean(axis=1)

train_std = train_scores.std(axis=1)
val_std = val_scores.std(axis=1)


# =========================
# 9. Plot
# =========================

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


# Training variation

plt.fill_between(
    train_sizes,
    train_mean - train_std,
    train_mean + train_std,
    alpha=0.2
)


# Validation variation

plt.fill_between(
    train_sizes,
    val_mean - val_std,
    val_mean + val_std,
    alpha=0.2
)


# =========================
# 10. Labels
# =========================

plt.xlabel("Training examples")
plt.ylabel("Accuracy")
plt.title("Learning Curve")

plt.legend()
plt.grid()

plt.savefig("learning_curves.png")

plt.show()


# =========================
# 11. sinal test accyracy
# =========================
X_test = test["Text"]
y_test = test["Category"]

X_test_tfidf = vectorizer.transform(X_test)

y_test_pred = model.predict(X_test_tfidf)

test_accuracy = accuracy_score(y_test, y_test_pred)

print("Final test accuracy =", test_accuracy)

# =========================
# 12. Train final pipeline
# =========================

pipeline.fit(X, y)


# =========================
# 13. Save final pipeline
# =========================

joblib.dump(pipeline, "topic_classifier.pkl")

print("Model saved successfully.")