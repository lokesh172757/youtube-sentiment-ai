import pandas as pd
import re
import emoji
from transformers import pipeline
from sklearn.feature_extraction.text import CountVectorizer

# Load the Deep Learning pipeline (RoBERTa - optimized for social media)
# We use @st.cache_resource in app.py later to make sure this only loads once!
def load_bert_model():
    model_path = "cardiffnlp/twitter-roberta-base-sentiment"
    sentiment_task = pipeline("sentiment-analysis", model=model_path, tokenizer=model_path)
    return sentiment_task

def clean_text(text):
    """
    Minimal cleaning. Deep Learning models actually LIKE emojis and punctuation
    because they add context. We only remove links.
    """
    text = str(text)
    # Remove Links
    text = re.sub(r'http\S+', '', text)
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    return text

def extract_emojis(text):
    """
    Helper to find all emojis in a text string
    """
    return ''.join(c for c in text if c in emoji.EMOJI_DATA)

def check_video_request(text):
    """
    Heuristic to check if a comment is requesting a new video.
    """
    text = text.lower()
    keywords = ["make a video", "do a video", "tutorial on", "please make", "next video", "can you", "could you", "requesting"]
    for k in keywords:
        if k in text:
            return True
    return False

def is_question(text):
    """
    Checks if the comment is a question.
    """
    return "?" in text or text.strip().lower().startswith(("how", "what", "why", "when", "can", "is", "do"))

def is_toxic(sentiment, confidence):
    """
    Heuristic: Toxic if Negative and High Confidence (> 0.90)
    """
    return sentiment == 'Negative' and confidence > 0.90

def extract_bigrams(text_list):
    """
    Extracts top 10 bi-grams (2-word phrases) using sklearn.
    """
    try:
        # Stop words 'english' removes common words like "the", "is", etc.
        vectorizer = CountVectorizer(ngram_range=(2, 2), stop_words='english', max_features=10)
        X = vectorizer.fit_transform(text_list)
        
        # Get counts
        counts = X.toarray().sum(axis=0)
        feature_names = vectorizer.get_feature_names_out()
        
        # Zip and sort
        bigrams = sorted(zip(feature_names, counts), key=lambda x: x[1], reverse=True)
        return bigrams
    except:
        return []

def generate_smart_summary(df):
    """
    Generates a natural language executive summary based on the data.
    """
    if df.empty:
        return "No data available for summary."
    
    total = len(df)
    positives = len(df[df['Sentiment'] == 'Positive'])
    negatives = len(df[df['Sentiment'] == 'Negative'])
    neutrals = len(df[df['Sentiment'] == 'Neutral'])
    
    pos_pct = (positives / total) * 100
    
    # 1. Overall Vibe
    if pos_pct >= 70:
        vibe = "exceptionally positive 🎉"
        action = "Keep doing what you're doing!"
    elif pos_pct >= 50:
        vibe = "generally positive 👍"
        action = "Good, but room for improvement."
    elif negatives > positives:
        vibe = "critical ⚠️"
        action = "Consider addressing viewer concerns."
    else:
        vibe = "mixed 😐"
        action = "Engage more to understand the audience."
        
    # 2. Key Topics
    bigrams = extract_bigrams(df['Clean_Text'].dropna())
    topics_str = ""
    if bigrams:
        top_3 = [b[0] for b in bigrams[:3]]
        topics_str = f"Viewers are discussing **'{', '.join(top_3)}'**."
        
    # 3. Unanswered
    questions = len(df[(df['Is_Question'] == True) & (df['Reply_Count'] == 0)])
    
    summary = f"""
    ### 📝 Executive Summary
    The overall response is **{vibe}** ({pos_pct:.1f}% Positive).
    {topics_str}
    There are **{questions}** unanswered questions that might need your attention.
    **Advice:** {action}
    """
    return summary

def analyze_roberta(text, model):
    """
    Uses the HuggingFace Transformer model.
    Returns: Label (Positive/Negative/Neutral) and Confidence Score.
    """
    try:
        # Truncate text to 512 tokens (model limit)
        result = model(text[:512])[0]
        label = result['label']
        score = result['score']
        
        # Map RoBERTa labels to Human labels
        if label == 'LABEL_0':
            return 'Negative', score
        elif label == 'LABEL_1':
            return 'Neutral', score
        else:
            return 'Positive', score
    except:
        return 'Neutral', 0.0

def process_data_deep_learning(df, model):
    """
    Main Pipeline using Deep Learning
    """
    # 1. Clean
    df['Clean_Text'] = df['Comment'].apply(clean_text)
    
    # 2. Extract Emojis (For the visualization feature)
    df['Emojis'] = df['Comment'].apply(extract_emojis)
    
    # 3. New Creator Features
    df['Is_Request'] = df['Clean_Text'].apply(check_video_request)
    df['Is_Question'] = df['Clean_Text'].apply(is_question)
    
    # Ensure Date is Datetime for Time Series
    if 'Published_At' in df.columns:
        df['Published_At'] = pd.to_datetime(df['Published_At'])
    
    # 4. Analyze (This takes time, so we show a progress bar in app.py usually)
    # Applying the model row by row
    results = df['Clean_Text'].apply(lambda x: analyze_roberta(x, model))
    
    # Unpack results into two columns
    df['Sentiment'] = [res[0] for res in results]
    df['Confidence'] = [res[1] for res in results]
    
    # 5. Toxicity Check
    df['Is_Toxic'] = df.apply(lambda x: is_toxic(x['Sentiment'], x['Confidence']), axis=1)
    
    # 6. Persona Assignment
    df['Persona'] = df.apply(assign_persona, axis=1)
    
    return df

def assign_persona(row):
    """
    Classifies a user into a persona based on their comment.
    """
    text = row['Clean_Text'].lower()
    sent = row['Sentiment']
    conf = row['Confidence']
    is_q = row['Is_Question']
    is_tox = row['Is_Toxic']
    
    # 1. Super Fan: Positive + (keywords OR High Confidence)
    fan_keywords = ['love', 'best', 'awesome', 'amazing', 'great', 'fan']
    if sent == 'Positive' and (conf > 0.95 or any(k in text for k in fan_keywords)):
        return "🏆 Super Fan"
    
    # 2. Hater: Negative + (Toxic OR keywords)
    hater_keywords = ['worst', 'bad', 'trash', 'garbage', 'stupid', 'hate']
    if sent == 'Negative' and (is_tox or any(k in text for k in hater_keywords)):
        return "🛑 Hater"
        
    # 3. Learner: Questions
    if is_q or any(k in text for k in ['how', 'why', 'help']):
        return "🎓 Learner"
        
    # 4. Casual (Default)
    return "👋 Casual"

# --- NEW FEATURES: SMART REPLY & PDF ---
from fpdf import FPDF

def generate_smart_reply(comment, persona, sentiment):
    """
    Simulates an AI drafting a reply based on context.
    IN REALITY: This would call GPT-4/Gemini.
    HERE: We use smart templates for speed & privacy.
    """
    templates = {
        "🏆 Super Fan": [
            "Thank you so much! ❤️ Your support means the world to us!",
            "You are awesome! Glad you enjoyed it! 🔥",
            "Thanks for watching! Stay tuned for more! 🚀"
        ],
        "🛑 Hater": [
            "We appreciate the feedback, even if it's tough. helping us improve! 👍",
            "Sorry you felt that way! We'll try to do better next time.",
            "Thanks for watching anyway! peace ✌️"
        ],
        "🎓 Learner": [
            "Great question! We will cover this in detail soon! 📝",
            "Thanks for asking! Basically, it depends on the context. Hope that helps!",
            "Good catch! Let me explain that in the next video! 💡"
        ],
        "👋 Casual": [
            "Thanks for the comment! 🙌",
            "Appreciate you stopping by!",
            "Glad you're here! 😄"
        ]
    }
    
    import random
    base_reply = random.choice(templates.get(persona, templates["👋 Casual"]))
    return f"AI Suggestion: \"{base_reply}\""

def generate_pdf_report(df):
    """
    Generates a PDF analysis report.
    Returns: Bytes of the PDF file.
    """
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    # Title
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, txt="AI YouTube Sentiment Report", ln=True, align='C')
    pdf.ln(10)
    
    # Summary Metrics
    pdf.set_font("Arial", size=12)
    total = len(df)
    pos = len(df[df['Sentiment']=='Positive'])
    neg = len(df[df['Sentiment']=='Negative'])
    
    pdf.cell(200, 10, txt=f"Total Comments: {total}", ln=True)
    pdf.cell(200, 10, txt=f"Positive: {pos} ({pos/total*100:.1f}%)", ln=True)
    pdf.cell(200, 10, txt=f"Negative: {neg} ({neg/total*100:.1f}%)", ln=True)
    pdf.ln(10)
    
    # Top Topics
    pdf.set_font("Arial", "B", 14)
    pdf.cell(200, 10, txt="Top Discussion Topics", ln=True)
    pdf.set_font("Arial", size=12)
    
    bigrams = extract_bigrams(df['Clean_Text'])
    for phrase, count in bigrams[:5]:
        pdf.cell(200, 10, txt=f"- {phrase} ({count} mentions)", ln=True)
        
    pdf.ln(10)
    
    # Action Items
    pdf.set_font("Arial", "B", 14)
    pdf.cell(200, 10, txt="Action Items / Requests", ln=True)
    pdf.set_font("Arial", size=12)
    
    reqs = df[df['Is_Request']==True]
    if not reqs.empty:
        for i, row in reqs.head(3).iterrows():
            pdf.multi_cell(0, 10, txt=f"Request: {row['Comment'][:100]}...")
    else:
        pdf.cell(200, 10, txt="No specific requests found.", ln=True)
        
    # Return as string (Latin-1 encoding required for FPDF legacy)
    return pdf.output(dest='S').encode('latin-1', 'ignore')

# --- GOD MODE LOGIC ---
from deep_translator import GoogleTranslator
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

def calculate_trust_score(df):
    """
    Calculates a Brand Safety / Trust Score (0-100).
    """
    if df.empty: return 0
    
    # 1. Base Score
    score = 100
    
    # 2. Penalties
    # Toxicity Penalty
    toxic_count = len(df[df['Is_Toxic']==True])
    toxic_ratio = toxic_count / len(df)
    score -= (toxic_ratio * 100) * 1.5 # Heavy penalty for toxicity
    
    # Negativity Penalty
    neg_count = len(df[df['Sentiment']=='Negative'])
    neg_ratio = neg_count / len(df)
    score -= (neg_ratio * 100) * 0.5 # Moderate penalty for negativity
    
    # 3. Bonuses
    # Engagement Bonus (if highly liked/replied)
    avg_likes = df['Likes'].mean()
    if avg_likes > 10: score += 5
    
    return max(0, min(100, int(score)))

def translate_comment(text):
    """
    Translates a single text to English.
    """
    try:
        # Check if text is likely not English (simple heuristic or just force translate)
        # Deep Translator automatically detects language
        return GoogleTranslator(source='auto', target='en').translate(text)
    except:
        return text

def query_dataframe(df, query):
    """
    RAG: Semantic Search over the dataframe.
    """
    try:
        # Create Corpus
        documents = df['Clean_Text'].fillna("").tolist()
        documents.append(query)
        
        # TF-IDF Vectorization
        tfidf = TfidfVectorizer(stop_words='english')
        tfidf_matrix = tfidf.fit_transform(documents)
        
        # Compute Cosine Similarity
        cosine_sim = cosine_similarity(tfidf_matrix[-1], tfidf_matrix[:-1])
        
        # Get Top 3 Matches
        scores = cosine_sim[0]
        top_indices = scores.argsort()[-3:][::-1]
        
        results = []
        for idx in top_indices:
            if scores[idx] > 0.1: # Threshold to match
                results.append((df.iloc[idx]['Author'], df.iloc[idx]['Comment'], scores[idx]))
        
        return results
    except Exception as e:
        return []