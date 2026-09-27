import sqlite3
import os
import pandas as pd
import spacy
import joblib
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


environmental_keywords = [
    "oil spill",
    "chemical spill",
    "chemical leak",
    "toxic chemical leak",
    "toxic waste dumping",
    "hazardous waste dumping",
    "illegal waste dumping",
    "industrial waste dumping",
    "water pollution",
    "water contamination",
    "air pollution",
    "soil contamination",
    "groundwater contamination",
    "marine pollution",
    "ocean pollution",
    "industrial pollution",
    "toxic pollution",
    "industrial chemical pollution",
    "deforestation",
    "illegal deforestation",
    "habitat destruction",
    "environmental contamination",
    "environmental pollution"
]


# Load news database

nlp = spacy.load("en_core_web_sm")

conn = sqlite3.connect("news.db")
query = "SELECT * FROM articles"
df = pd.read_sql_query(query, conn)
conn.close()


# Extract ORG entities

extracted_orgs = []

for doc in nlp.pipe(
    (df["title"] + " " + df["body"]).astype(str)
):
    orgs = [
        ent.text
        for ent in doc.ents
        if ent.label_ == "ORG"
    ]

    extracted_orgs.append(orgs)

df["organizations"] = extracted_orgs


# Topic classification

model = joblib.load(
    "results/topic_classifier.pkl"
)

text = (
    df["title"].fillna("")
    + " "
    + df["body"].fillna("")
)

df["Topics"] = model.predict(text)


# Sentiment analysis

nltk.download("vader_lexicon")

sia = SentimentIntensityAnalyzer()


def get_sentiment(text):
    scores = sia.polarity_scores(text)

    compound = scores["compound"]

    if compound > 0:
        return "positive"
    elif compound < 0:
        return "negative"
    else:
        return "neutral"


texts = (
    df["title"].fillna("")
    + " "
    + df["body"].fillna("")
)

df["Sentiment"] = texts.apply(get_sentiment)


# Embeddings & Environmental Scandal Detection

def get_org_sentences(title, body):
    """
    Extract sentences containing at least one ORG entity.
    Title and body are processed separately to avoid merging them.
    """

    org_sentences = []

    for text in [str(title), str(body)]:

        doc = nlp(text)

        for sent in doc.sents:

            has_org = any(
                ent.label_ == "ORG"
                for ent in sent.ents
            )

            if has_org:
                org_sentences.append(
                    sent.text.strip()
                )

    return org_sentences


# Load sentence embedding model
model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)


# Create embeddings for environmental keywords
environmental_keywords_embeddings = model.encode(
    environmental_keywords
)


# Extract ORG-containing sentences
df["org_sentences"] = df.apply(
    lambda row: get_org_sentences(
        row["title"],
        row["body"]
    ),
    axis=1
)


def get_article_scandal_score(sentences):
    """
    Compute one environmental similarity score per article.

    The score is the highest cosine similarity between:
    - an ORG-containing sentence
    - an environmental keyword
    """

    if not sentences:
        return 0.0

    # Convert article sentences into embeddings
    sentence_embeddings = model.encode(
        sentences
    )

    # Compare sentences with environmental keywords
    similarities = cosine_similarity(
        sentence_embeddings,
        environmental_keywords_embeddings
    )

    # Best keyword similarity for each sentence
    sentence_scores = similarities.max(axis=1)

    # Best sentence score for the article
    return sentence_scores.max()


# Compute one scandal score per article
df["Scandal_distance"] = df[
    "org_sentences"
].apply(
    get_article_scandal_score
)


# Select Top 10 articles

if not df.empty:

    # Sort by scandal similarity score
    df = df.sort_values(
        by="Scandal_distance",
        ascending=False,
        na_position="last"
    )

    # Initialize Top_10 column
    df["Top_10"] = False

    # Select the 10 highest valid scores
    valid_mask = df[
        "Scandal_distance"
    ].notna()

    top_10_indices = (
        df[valid_mask]
        .head(10)
        .index
    )

    # Mark selected articles
    df.loc[
        top_10_indices,
        "Top_10"
    ] = True


# Create final enhanced_news.csv

# Convert organizations list to a readable string
df["Org"] = df["organizations"].apply(
    lambda orgs: ", ".join(orgs)
)


# Select required columns
final_df = df[
    [
        "id",
        "link",
        "date",
        "title",
        "body",
        "Org",
        "Topics",
        "Sentiment",
        "Scandal_distance",
        "Top_10"
    ]
].rename(
    columns={
        "id": "Unique ID",
        "link": "URL",
        "date": "Date scraped",
        "title": "Headline",
        "body": "Body"
    }
)


# Create results directory
os.makedirs(
    "results",
    exist_ok=True
)


# Save final CSV
final_df.to_csv(
    "results/enhanced_news.csv",
    index=False
)


print("\nEnhanced news saved to results/enhanced_news.csv!")

print(f"Rows: {len(final_df)}")

print("Columns:")
print(final_df.columns.tolist())

print("\nTop 10 distribution:")
print(final_df["Top_10"].value_counts())