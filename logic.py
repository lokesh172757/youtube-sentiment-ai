import pandas as pd
import re
import emoji
from transformers import pipeline

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
    
    # 3. Analyze (This takes time, so we show a progress bar in app.py usually)
    # Applying the model row by row
    results = df['Clean_Text'].apply(lambda x: analyze_roberta(x, model))
    
    # Unpack results into two columns
    df['Sentiment'] = [res[0] for res in results]
    df['Confidence'] = [res[1] for res in results]
    
    return df