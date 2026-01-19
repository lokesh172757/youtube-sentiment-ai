import streamlit as st
import pandas as pd
import plotly.express as px
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from collections import Counter
import helper
import logic

# 1. Page Config
st.set_page_config(page_title="AI YouTube Analyzer", page_icon="🤖", layout="wide")

# 2. Load Model (Cached so it doesn't reload every time)
@st.cache_resource
def load_ai_model():
    return logic.load_bert_model()

try:
    roberta_model = load_ai_model()
except Exception as e:
    st.error("Error loading AI Model. Please check your internet connection.")
    st.stop()

# 3. Sidebar
st.sidebar.title("🤖 AI Sentiment Pro")
st.sidebar.info("This app uses a **RoBERTa Deep Learning Model** (trained on 58M tweets) to understand sarcasm, slang, and context.")

# 4. Main UI
st.title("🤖 Deep Learning YouTube Analyzer")
st.markdown("Analyze comments using State-of-the-Art Natural Language Processing.")

video_url = st.text_input("Paste YouTube Link:", placeholder="https://www.youtube.com/watch?v=...")

if st.button("Run AI Analysis", type="primary"):
    if not video_url:
        st.warning("Please enter a valid link.")
    else:
        with st.spinner("🤖 AI is reading comments... (This might take a moment)"):
            # A. Fetch Data
            raw_data = helper.fetch_comments(video_url)
            
            if isinstance(raw_data, dict) and "error" in raw_data:
                st.error(f"Error: {raw_data['error']}")
            elif raw_data.empty:
                st.warning("No comments found.")
            else:
                # B. Process with Deep Learning
                processed_data = logic.process_data_deep_learning(raw_data, roberta_model)
                
                # C. Success & Metrics
                st.success(f"Analyzed {len(processed_data)} comments using RoBERTa!")
                
                # Create Tabs for better UI
                tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "🧠 Deep Insights", "📂 Raw Data"])
                
                # --- TAB 1: OVERVIEW ---
                with tab1:
                    col1, col2, col3 = st.columns(3)
                    pos = len(processed_data[processed_data['Sentiment'] == 'Positive'])
                    neg = len(processed_data[processed_data['Sentiment'] == 'Negative'])
                    neu = len(processed_data[processed_data['Sentiment'] == 'Neutral'])
                    
                    col1.metric("Positivity", f"{pos}", delta=f"{pos/len(processed_data)*100:.1f}%")
                    col2.metric("Negativity", f"{neg}", delta_color="inverse", delta=f"{neg/len(processed_data)*100:.1f}%")
                    col3.metric("Neutral", f"{neu}")
                    
                    # Sentiment Pie Chart
                    fig = px.pie(processed_data, names='Sentiment', 
                                 title='Audience Mood',
                                 color='Sentiment',
                                 color_discrete_map={'Positive':'#00CC96', 'Negative':'#EF553B', 'Neutral':'#636EFA'})
                    st.plotly_chart(fig, use_container_width=True)

                # --- TAB 2: DEEP INSIGHTS ---
                with tab2:
                    col_cloud, col_emoji = st.columns(2)
                    
                    with col_cloud:
                        st.subheader("☁️ What are they saying?")
                        # Generate Word Cloud
                        text_combined = " ".join(processed_data['Clean_Text'])
                        wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text_combined)
                        
                        fig, ax = plt.subplots()
                        ax.imshow(wordcloud, interpolation='bilinear')
                        ax.axis("off")
                        st.pyplot(fig)

                    with col_emoji:
                        st.subheader("🔥 Top Emojis Used")
                        # Extract all emojis into a single list
                        all_emojis = [char for text in processed_data['Emojis'] for char in text]
                        if all_emojis:
                            emoji_counts = Counter(all_emojis).most_common(10)
                            emoji_df = pd.DataFrame(emoji_counts, columns=['Emoji', 'Count'])
                            
                            fig_bar = px.bar(emoji_df, x='Emoji', y='Count', title="Most Popular Reactions")
                            st.plotly_chart(fig_bar, use_container_width=True)
                        else:
                            st.info("No emojis found in these comments.")

                # --- TAB 3: DATA & EXPORT ---
                with tab3:
                    st.dataframe(processed_data)
                    
                    # CSV Download Button
                    csv = processed_data.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="📥 Download Data as CSV",
                        data=csv,
                        file_name='sentiment_analysis.csv',
                        mime='text/csv',
                    )