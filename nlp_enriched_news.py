import sqlite3
import pandas as pd
import spacy
import joblib
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer







nlp = spacy.load("en_core_web_sm")

conn = sqlite3.connect("news.db")
query = "SELECT * FROM articles "
df = pd.read_sql_query(query,conn)
conn.close()
extracted_orgs = []

for doc in nlp.pipe((df["title"]+" "+df["body"]).astype(str)):
        # Extract only ORG entities from each row
    orgs =[ent.text for ent in doc.ents if ent.label_ == "ORG"]
    extracted_orgs.append(orgs)
df["organizations"] = extracted_orgs


# Load trained model && add Topics 

model = joblib.load("results/topic_classifier.pkl")


text = (
    df["title"].fillna("") + " " + df["body"].fillna("")
)

df["Topics"] = model.predict(text)

# use nltk && add Sentiment column





nltk.download("vader_lexicon")

sia = SentimentIntensityAnalyzer()

def get_sentiment(text):
    scores = sia.polarity_scores(text)
    
    compound = scores["compound"]
    
    if compound > 0 :
        return "positive"
    elif compound < 0 :
        return "negative"
    else:
        return "neutral"




texts = (
    df["title"].fillna("")
    + " "
    + df["body"].fillna("")
)
df["Sentiment"] = texts.apply(get_sentiment)











