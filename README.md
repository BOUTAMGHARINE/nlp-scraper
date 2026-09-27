# NLP Scraper

## Overview

This project is an NLP-enriched News Intelligence platform developed as part of the Zone01 AI curriculum.

The platform collects recent news articles and enriches them using Natural Language Processing techniques.

The pipeline performs four main NLP tasks:

1. Organization detection using SpaCy NER.
2. Topic classification using a supervised machine learning model.
3. Sentiment analysis using NLTK VADER.
4. Environmental scandal detection using sentence embeddings and cosine similarity.

The final enriched data is stored in:

```text
results/enhanced_news.csv
```

---

## Project Architecture

The project is divided into two independent parts:

```text
News website
     │
     ▼
scraper_news.py
     │
     ▼
SQLite database
     │
     ▼
nlp_enriched_news.py
     │
     ├── Organization detection
     ├── Topic classification
     ├── Sentiment analysis
     └── Environmental scandal detection
     │
     ▼
enhanced_news.csv
```

The scraper and NLP engine are intentionally separated. The scraper first collects and stores the articles, and the NLP engine processes the stored data afterward.

---

## Project Structure

```text
nlp-scraper/
│
├── data/
│
├── news.db
│
├── scraper_news.py
│
├── nlp_enriched_news.py
│
├── requirements.txt
│
├── README.md
│
└── results/
    ├── training_model.py
    ├── topic_classifier.pkl
    ├── enhanced_news.csv
    └── learning_curves.png
```

---

# 1. News Scraper

The scraper collects news articles from BBC RSS feeds.

The `feedparser` library is used to read the RSS feeds and retrieve information such as:

* article title
* article URL
* publication date
* summary

The article URL is then requested using `requests`, and `BeautifulSoup` is used to extract the article body.

The collected information is stored in a SQLite database.

The database contains the following fields:

```text
id
title
link
date
summary
body
```

Only recent articles are collected in order to respect the project requirement of using news from the last week.

Multiple BBC RSS feeds are used to increase the number and diversity of collected articles.

Examples of feeds include:

```text
BBC News
BBC World
BBC Business
BBC Technology
BBC Science & Environment
BBC Health
BBC Politics
BBC Entertainment & Arts
```

Run the scraper with:

```bash
python scraper_news.py
```

The scraper stores the collected articles in:

```text
news.db
```

The project requires at least 300 articles to be collected.

---

# 2. Organization Detection

The first NLP step is Named Entity Recognition.

SpaCy is used with the pretrained:

```text
en_core_web_sm
```

model.

The goal is to detect organizations and companies mentioned in the headline and article body.

Only entities with the `ORG` label are kept.

For example, an article containing:

```text
Microsoft announced a new agreement with OpenAI.
```

may produce organizations such as:

```text
Microsoft
OpenAI
```

The detected organizations are stored in the `Org` column of the final dataset.

The extraction is performed on:

```text
Headline + Body
```

---

# 3. Topic Classification

The topic classifier is trained using the BBC News labelled dataset provided by the project.

The dataset contains five categories:

```text
business
entertainment
politics
sport
tech
```

## Text preprocessing

The classifier uses TF-IDF to transform article text into numerical features.

The configuration uses:

```text
TF-IDF
ngram_range = (1, 2)
stop_words = "english"
```

Both unigrams and bigrams are used.

For example:

```text
"football match"
```

can be represented not only by:

```text
football
match
```

but also by the bigram:

```text
football match
```

## Classification model

Logistic Regression is used as the classification algorithm.

The complete classifier is implemented as a scikit-learn Pipeline:

```text
Raw article text
       │
       ▼
TF-IDF
       │
       ▼
Logistic Regression
       │
       ▼
Predicted topic
```

Using a Pipeline ensures that the TF-IDF transformation is fitted only on the appropriate training data and avoids data leakage during validation.

The trained model is saved as:

```text
results/topic_classifier.pkl
```

The training process is stored in:

```text
results/training_model.py
```

---

## Model Evaluation

The model is evaluated on the provided test dataset.

The final test accuracy obtained during development was approximately:

```text
98.23%
```

The validation accuracy was also above 95%.

Learning curves are generated using 5-fold cross-validation and saved as:

```text
results/learning_curves.png
```

The learning curves are used to observe the relationship between training performance and validation performance as the amount of training data increases.

They help identify potential overfitting or underfitting.

---

# 4. Sentiment Analysis

Sentiment analysis is performed using the pretrained VADER model from NLTK.

The reason for using a pretrained model is that sentiment classification does not require training a new model for this project.

VADER produces four scores:

```text
positive
negative
neutral
compound
```

The `compound` score is used to classify each article.

The classification rule is:

```text
compound > 0  → positive
compound < 0  → negative
compound = 0  → neutral
```

The sentiment is calculated from:

```text
Headline + Body
```

The result is stored in:

```text
Sentiment
```

---

# 5. Environmental Scandal Detection

The goal of this step is to identify articles that may describe an environmental incident involving an organization detected by the NER system.

The methodology follows these steps:

```text
Environmental keywords
        │
        ▼
Keyword embeddings
        │
        │
        ▼
Article sentences containing ORG
        │
        ▼
Sentence embeddings
        │
        ▼
Cosine similarity
        │
        ▼
Article-level score
        │
        ▼
Top 10 articles
```

## Environmental keywords

A set of specific environmental keywords and phrases is defined.

Examples include:

```text
oil spill
chemical spill
chemical leak
toxic chemical leak
toxic waste dumping
hazardous waste dumping
illegal waste dumping
water pollution
water contamination
air pollution
soil contamination
groundwater contamination
marine pollution
ocean pollution
industrial pollution
toxic pollution
deforestation
illegal deforestation
habitat destruction
environmental contamination
environmental pollution
```

More specific phrases are preferred over ambiguous words in order to reduce false positives.

For example, using only a word such as:

```text
disaster
```

would be too ambiguous because it can describe many types of events that have nothing to do with environmental pollution.

---

## Sentence Embeddings

The embedding model used is:

```text
all-MiniLM-L6-v2
```

from Sentence Transformers.

This model converts sentences and phrases into numerical vectors.

Each sentence is represented by a vector in a 384-dimensional semantic space.

For example:

```text
"chemical leak from a factory"
```

and:

```text
"toxic chemicals escaped from an industrial plant"
```

can have similar vector representations because they express a similar meaning even though they do not contain exactly the same words.

This is useful for the scandal detection task because a sentence does not necessarily have to contain the exact environmental keyword to be semantically related to it.

Sentence Transformers is used instead of SpaCy word vectors because the task compares complete phrases and sentences. The selected model is designed specifically for generating meaningful sentence-level embeddings.

---

## Selecting Sentences

Not every sentence in an article is compared with the environmental keywords.

Only sentences containing at least one detected `ORG` entity are selected.

For example:

```text
The company announced its new financial results.
```

would be selected if `The company` is recognized as an organization.

The reason is that the assignment specifically focuses on detecting environmental disasters involving detected organizations.

The headline and body are processed separately so that missing punctuation or malformed text extraction between the two does not create an artificial sentence.

---

## Similarity Metric

Cosine similarity is used to compare the sentence embeddings with the environmental keyword embeddings.

Cosine similarity measures how similar two vectors are based on their direction.

The value is generally interpreted as:

```text
higher similarity
       ↓
more semantically related
       ↓
greater potential environmental relevance
```

For each ORG-containing sentence, the highest similarity with any environmental keyword is selected.

Then the highest sentence score is used as the article-level score.

Conceptually:

```text
Article
   │
   ├── Sentence 1 → best keyword similarity
   ├── Sentence 2 → best keyword similarity
   ├── Sentence 3 → best keyword similarity
   │
   ▼
Highest sentence score
   │
   ▼
Scandal_distance
```

The column is named `Scandal_distance` because this is the name required by the project specification.

Technically, the value represents cosine similarity rather than a mathematical distance.

Therefore:

```text
higher Scandal_distance
        =
higher semantic similarity
with environmental keywords
```

---

## Top 10 Detection

After calculating one score for every article, the articles are sorted by:

```text
Scandal_distance
```

in descending order.

The 10 articles with the highest scores are flagged:

```text
Top_10 = True
```

All other articles are:

```text
Top_10 = False
```

This produces the final ranking required by the project.

---

# 6. Final Dataset

The final enriched dataset is saved as:

```text
results/enhanced_news.csv
```

It contains the following columns:

```text
Unique ID
URL
Date scraped
Headline
Body
Org
Topics
Sentiment
Scandal_distance
Top_10
```

The processing pipeline is therefore:

```text
Stored news articles
        │
        ▼
Organization detection
        │
        ▼
Topic classification
        │
        ▼
Sentiment analysis
        │
        ▼
Environmental scandal detection
        │
        ▼
Top 10 detection
        │
        ▼
enhanced_news.csv
```

---

# 7. Limitations

The environmental scandal detector is based on semantic similarity, so it can produce false positives.

For example, an article discussing oil markets or an oil agreement may be semantically close to the keyword:

```text
oil spill
```

even when no environmental disaster occurred.

This is a limitation of using embeddings and cosine similarity rather than a dedicated supervised environmental-scandal classifier.

Another limitation is that the article score uses the maximum similarity between sentences and keywords. A single highly similar sentence can therefore increase the score of the entire article.

The system should therefore be considered a relevance detector rather than a definitive environmental-scandal classifier.

The `Top_10` articles require human review before concluding that an actual environmental scandal occurred.

---

# 8. Installation

Install the required Python dependencies:

```bash
pip install -r requirements.txt
```

Download the SpaCy English model:

```bash
python -m spacy download en_core_web_sm
```

The NLTK VADER lexicon is downloaded automatically by the NLP script.

The Sentence Transformers model:

```text
all-MiniLM-L6-v2
```

is downloaded automatically when it is first loaded.

---

# 9. Running the Project

First, run the scraper:

```bash
python scraper_news.py
```

Verify that the SQLite database contains at least 300 articles.

Then train the topic classifier:

```bash
python results/training_model.py
```

This creates:

```text
results/topic_classifier.pkl
results/learning_curves.png
```

Finally, run the NLP enrichment pipeline:

```bash
python nlp_enriched_news.py
```

This creates:

```text
results/enhanced_news.csv
```

---

# 10. Technologies Used

```text
Python
SQLite
Pandas
Requests
BeautifulSoup
Feedparser
SpaCy
Scikit-learn
Joblib
NLTK
Sentence Transformers
Matplotlib
```

Main NLP and Machine Learning components:

```text
SpaCy NER
TF-IDF
Logistic Regression
Learning Curves
VADER Sentiment Analysis
Sentence Embeddings
Cosine Similarity
```

---

# 11. Expected Output

After running the complete pipeline, the `results` directory should contain:

```text
results/
├── training_model.py
├── topic_classifier.pkl
├── enhanced_news.csv
└── learning_curves.png
```

The final CSV provides an enriched representation of each scraped article, combining information extraction, topic classification, sentiment analysis and environmental relevance detection.
