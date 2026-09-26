import sqlite3
import pandas as pd
import spacy
import joblib
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from sentence_transformers import SentenceTransformer



environmental_keywords = [
    "oil spill",
    "chemical spill",
    "chemical leak",
    "toxic leak",
    "toxic waste",
    "hazardous waste",
    "industrial waste",
    "illegal dumping",
    "waste dumping",
    "water pollution",
    "water contamination",
    "soil contamination",
    "air pollution",
    "toxic pollution",
    "industrial pollution",
    "chemical contamination",
    "oil contamination",
    "marine pollution",
    "ocean pollution",
    "groundwater contamination",
    "deforestation",
    "illegal deforestation",
    "forest destruction",
    "habitat destruction",
    "environmental contamination",
    "industrial contamination",
    "toxic chemicals",
    "hazardous chemicals",
    "chemical discharge",
    "industrial discharge"
]



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



# embedding && Scandal detection



def get_org_sentences(title, body):
    text = f"{title} {body}"

    doc = nlp(text)

    sentences = []

    for sent in doc.sents:
        has_org = any(ent.label_ == "ORG" for ent in sent.ents)

        if has_org:
            sentences.append(sent.text.strip())

    return sentences

model = SentenceTransformer("all-MiniLM-L6-v2")

environmental_keywords_embeddings = model.encode(environmental_keywords)


df["org_sentences"] = df.apply(
    lambda row: get_org_sentences(row["title"], row["body"]),
    axis=1
)

print(df.loc[0, "body"])
print(df.loc[0, "org_sentences"])

















                 












