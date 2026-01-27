import streamlit as st
import pandas as pd
import plotly.express as px
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from collections import Counter
import helper
import logic
import plotly.graph_objects as go

# 1. Page Config
st.set_page_config(page_title="AI YouTube Analyzer", page_icon="🤖", layout="wide")

# 2. Custom CSS for Premium UI
# 2. Custom CSS for Premium UI
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Poppins:wght@400;500;600;700&display=swap');
    
    /* Root Design Tokens */
    :root {
        --primary: #6366f1;
        --secondary: #8b5cf6;
        --accent: #ec4899;
        --success: #10b981;
        --warning: #f59e0b;
        --error: #ef4444;
        --bg-dark: #07090e;
        --text-primary: #ffffff;
        --text-secondary: #cbd5e1;
        --text-muted: #94a3b8;
        --glass: rgba(255, 255, 255, 0.03);
        --glass-border: rgba(255, 255, 255, 0.08);
    }
    
    /* Base Layout */
    .stApp {
        background-color: var(--bg-dark);
        font-family: 'Inter', sans-serif;
        color: var(--text-primary) !important;
        overflow-x: hidden;
    }

    /* Refined Animated Mesh (Lower Opacity for Text Contrast) */
    .stApp::before {
        content: "";
        position: fixed;
        top: 0; left: 0; width: 100%; height: 100%;
        background: 
            radial-gradient(circle at 15% 20%, rgba(99, 102, 241, 0.12), transparent 45%),
            radial-gradient(circle at 85% 75%, rgba(16, 185, 129, 0.07), transparent 40%),
            radial-gradient(circle at 50% 50%, rgba(236, 72, 153, 0.06), transparent 50%),
            radial-gradient(circle at 80% 15%, rgba(139, 92, 246, 0.08), transparent 40%);
        z-index: -1;
        filter: blur(120px);
        animation: meshMove 30s infinite alternate ease-in-out;
    }

    @keyframes meshMove {
        0% { transform: scale(1) translate(0px, 0px); }
        50% { transform: scale(1.1) translate(2% , 4%); }
        100% { transform: scale(0.95) translate(-1%, -3%); }
    }
    
    /* Branding Hide */
    #MainMenu, footer, header {visibility: hidden;}
    
    /* Bento Cards */
    .bento-card {
        background: var(--glass);
        backdrop-filter: blur(30px);
        -webkit-backdrop-filter: blur(30px);
        border: 1px solid var(--glass-border);
        border-radius: 24px;
        padding: 24px;
        transition: all 0.5s cubic-bezier(0.19, 1, 0.22, 1);
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
        height: 100%;
        position: relative;
        overflow: hidden;
    }

    .bento-card:hover {
        transform: translateY(-8px);
        background: rgba(255, 255, 255, 0.05);
        border-color: rgba(99, 102, 241, 0.4);
        box-shadow: 0 30px 60px rgba(0, 0, 0, 0.5), 0 0 30px rgba(99, 102, 241, 0.15);
    }

    /* Sidebar Refinement */
    [data-testid="stSidebar"] {
        background: rgba(7, 9, 14, 0.85) !important;
        backdrop-filter: blur(25px);
        border-right: 1px solid var(--glass-border);
    }
    [data-testid="stSidebar"] * { color: var(--text-primary) !important; }
    
    .sidebar-pill {
        background: rgba(99, 102, 241, 0.08);
        border: 1px solid rgba(99, 102, 241, 0.2);
        border-radius: 16px;
        padding: 16px;
        text-align: center;
        margin-bottom: 24px;
    }

    /* Typography & Visibility */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Poppins', sans-serif;
        color: var(--text-primary) !important;
        font-weight: 800;
        letter-spacing: -0.04em;
        margin-bottom: 0.8rem !important;
    }
    
    .glow-header {
        background: linear-gradient(135deg, #ffffff 0%, #cbd5e1 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        filter: drop-shadow(0 0 8px rgba(255, 255, 255, 0.4));
    }

    /* Global Text Contrast (CATCH-ALL) */
    p, span, label, div:not([data-testid="stMetricValue"]) {
        color: var(--text-secondary) !important;
    }
    
    strong, b { color: var(--text-primary) !important; }

    /* Metrics */
    [data-testid="stMetricValue"] {
        font-size: 3.2rem !important;
        font-weight: 800 !important;
        color: var(--text-primary) !important;
        filter: drop-shadow(0 0 12px rgba(99, 102, 241, 0.5));
    }
    
    [data-testid="stMetricLabel"] {
        color: var(--text-muted) !important;
        font-weight: 700 !important;
        text-transform: uppercase;
        letter-spacing: 0.12em;
    }

    .glowing-icon {
        font-size: 3.5rem;
        margin-bottom: 12px;
        filter: drop-shadow(0 0 15px currentColor);
    }

    /* Action Elements */
    .stButton > button {
        background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 18px !important;
        padding: 14px 30px !important;
        font-weight: 800 !important;
        transition: all 0.4s cubic-bezier(0.19, 1, 0.22, 1) !important;
        box-shadow: 0 8px 20px rgba(99, 102, 241, 0.3) !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px) scale(1.02);
        box-shadow: 0 15px 35px rgba(99, 102, 241, 0.5) !important;
    }
    
    .stTextInput > div > div > input {
        background: rgba(255, 255, 255, 0.04) !important;
        border: 1px solid var(--glass-border) !important;
        border-radius: 16px !important;
        color: white !important;
        padding: 14px 20px !important;
        backdrop-filter: blur(10px);
    }

    /* Tabs Visibility */
    .stTabs [data-baseweb="tab-list"] {
        background: rgba(255, 255, 255, 0.03);
        border-radius: 18px;
        padding: 6px;
    }

    .stTabs [data-baseweb="tab"] {
        color: var(--text-muted) !important;
        font-weight: 600;
    }

    .stTabs [aria-selected="true"] {
        background: rgba(99, 102, 241, 0.12) !important;
        color: var(--text-primary) !important;
        border: 1px solid rgba(99, 102, 241, 0.3);
        border-radius: 14px !important;
    }

    /* Dropdowns (Critical Fixes) */
    [data-baseweb="popover"], [data-baseweb="menu"], [role="listbox"] {
        background-color: #0f172a !important;
        border: 1px solid var(--glass-border) !important;
    }

    [role="option"] {
        background-color: #0f172a !important;
        color: white !important;
    }
    [role="option"]:hover { background-color: var(--primary) !important; }

    /* Alerts & Notifications (Force Visibility) */
    [data-baseweb="notification"], .stAlert, div[class*="stAlert"] {
        background: rgba(10, 15, 30, 0.95) !important;
        backdrop-filter: blur(25px) !important;
        border: 1px solid var(--glass-border) !important;
        border-radius: 20px !important;
        box-shadow: 0 15px 45px rgba(0,0,0,0.5) !important;
        margin-bottom: 1.5rem !important;
    }

    /* Force all text inside any kind of alert to white */
    .stAlert p, .stAlert span, .stAlert div, .stAlert label,
    [data-baseweb="notification"] * { 
        color: #ffffff !important; 
        font-weight: 500 !important;
    }
    
    .stAlert[kind="info"] { border-left: 6px solid var(--primary) !important; }
    .stAlert[kind="success"] { border-left: 6px solid var(--success) !important; }
    .stAlert[kind="warning"] { border-left: 6px solid var(--warning) !important; }
    .stAlert[kind="error"] { border-left: 6px solid var(--error) !important; }

    /* Captions and Small Text */
    [data-testid="stCaptionContainer"], .stCaption, small {
        color: var(--text-secondary) !important;
        font-size: 0.95rem !important;
        line-height: 1.5 !important;
    }

    /* Code Blocks (Moderation / AI Code) */
    code, .stCodeBlock {
        background: rgba(0, 0, 0, 0.4) !important;
        border: 1px solid var(--glass-border) !important;
        border-radius: 12px !important;
        color: #ec4899 !important;
        padding: 4px 8px !important;
    }

    /* Raw Data Table Visibility */
    .stDataFrame, [data-testid="stTable"] {
        background: rgba(0,0,0,0.2) !important;
        border-radius: 16px !important;
    }
    .stDataFrame * { color: var(--text-secondary) !important; }

    /* Tables headers */
    [data-testid="StyledDataFrameRowHeaderCell"], [data-testid="StyledDataFrameHeaderCell"] {
        background-color: rgba(99, 102, 241, 0.1) !important;
        color: white !important;
    }

    /* Scrollbar */
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-thumb {
        background: rgba(255, 255, 255, 0.08);
        border-radius: 10px;
    }
    ::-webkit-scrollbar-thumb:hover { background: var(--primary); }
</style>
""", unsafe_allow_html=True)

# 3. Load Model
@st.cache_resource
def load_ai_model():
    return logic.load_bert_model()

try:
    roberta_model = load_ai_model()
except Exception as e:
    st.error("Error loading AI Model. Please check your internet connection.")
    st.stop()

# 4. Sidebar
st.sidebar.markdown("""
<div class="sidebar-pill">
    <h1 style='font-size: 2.5rem; margin: 0; filter: drop-shadow(0 0 10px #6366f1);'>🤖</h1>
    <h2 class="glow-header" style='font-size: 1.5rem; margin: 0.5rem 0;'>YS Analysis</h2>
</div>
""", unsafe_allow_html=True)
st.sidebar.markdown("""
<div style='background: linear-gradient(135deg, rgba(99, 102, 241, 0.15) 0%, rgba(139, 92, 246, 0.15) 100%); 
            padding: 1rem; 
            border-radius: 12px; 
            border: 1px solid rgba(99, 102, 241, 0.3);
            margin-bottom: 1rem;'>
    <p style='margin: 0; text-align: center; font-size: 0.9rem; line-height: 1.6;'>
        Analyze comments using <strong>State-of-the-Art</strong> Natural Language Processing
    </p>
</div>
""", unsafe_allow_html=True)

# --- MODE SELECTOR ---
app_mode = st.sidebar.radio("Select Mode", ["Single Video Analysis", "⚔️ Battle Mode", "📈 Channel Trends"])

# --- SINGLE MODE FUNCTION ---
def render_single_mode():
    st.markdown("""
    <div style='text-align: center; margin-bottom: 2rem;'>
        <h1 style='font-size: 3rem; margin-bottom: 0.5rem;'>🤖 Deep Learning YouTube Analyzer</h1>
        <p style='font-size: 1.1rem; color: #cbd5e1; margin: 0;'>
            Harness the power of AI to understand your audience sentiment
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    video_url = st.text_input("Paste YouTube Link:", placeholder="https://www.youtube.com/watch?v=...")
    
    if st.button("Run AI Analysis", type="primary"):
        if not video_url:
            st.warning("Please enter a valid link.")
        else:
            with st.spinner("🤖 AI is reading comments..."):
                raw_data = helper.fetch_comments(video_url)
                if isinstance(raw_data, dict) and "error" in raw_data:
                    st.error(f"Error: {raw_data['error']}")
                elif raw_data.empty:
                    st.warning("No comments found.")
                else:
                    processed_data = logic.process_data_deep_learning(raw_data, roberta_model)
                    # Translation Feature
                    if st.session_state.get('enable_translation'):
                        with st.spinner("🌍 Translating comments (this may take a while)..."):
                            processed_data['Clean_Text'] = processed_data['Clean_Text'].apply(logic.translate_comment)
                            
                    st.session_state['single_data'] = processed_data
                    st.success(f"Analyzed {len(processed_data)} comments.")

    # Function to render the dashboard (Persistent)
    if 'single_data' in st.session_state:
        processed_data = st.session_state['single_data']
        
        # Sidebar Filters
        st.sidebar.markdown("---")
        st.sidebar.subheader("🔍 Filter Results")
        
        # Translation Toggle
        if st.sidebar.checkbox("🌍 Translate to English", key="enable_translation"):
             st.sidebar.info("Next analysis will translate foreign comments.")
             
        sentiment_filter = st.sidebar.multiselect("Filter by Sentiment", ["Positive", "Negative", "Neutral"], default=["Positive", "Negative", "Neutral"])
        keyword_filter = st.sidebar.text_input("Filter by Keyword", key="single_kw")
        
        filtered_df = processed_data[processed_data['Sentiment'].isin(sentiment_filter)]
        if keyword_filter:
            filtered_df = filtered_df[filtered_df['Clean_Text'].str.contains(keyword_filter, case=False, na=False)]
        
        st.info(f"Showing {len(filtered_df)} filtered comments out of {len(processed_data)} total.")
        
        # Executive Summary in Bento Card
        st.markdown(f"""
        <div class="bento-card" style="margin-bottom: 20px;">
            <div style="font-size: 0.8rem; color: #6366f1; font-weight: 700; text-transform: uppercase; margin-bottom: 10px; letter-spacing: 0.1em;">
                ✨ AI Insights
            </div>
            {logic.generate_smart_summary(processed_data)}
        </div>
        """, unsafe_allow_html=True)

        # Charts use filtered_data
        data_to_plot = filtered_df
        
        tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs(["📊 Dashboard", "🧠 Deep Insights", "👥 Personas", "🚀 Opportunities", "💬 Community Hub", "🛡️ Moderate", "📂 Raw Data", "🤖 Chat"])
        
        with tab1:
            # Bento Grid Row 1: Key Metrics
            b1, b2 = st.columns([2, 1])
            
            pos = len(data_to_plot[data_to_plot['Sentiment'] == 'Positive'])
            neg = len(data_to_plot[data_to_plot['Sentiment'] == 'Negative'])
            neu = len(data_to_plot[data_to_plot['Sentiment'] == 'Neutral'])
            total_len = len(data_to_plot) if len(data_to_plot) > 0 else 1
            trust_score = logic.calculate_trust_score(data_to_plot)
            
            with b1:
                st.markdown(f"""
                <div class="bento-card" style="justify-content: center; align-items: center; min-height: 250px;">
                    <div class="glowing-icon" style="color: #10b981;">🏆</div>
                    <div style="font-size: 1.2rem; color: #94a3b8; font-weight: 600; text-transform: uppercase;">Overall Positivity</div>
                    <div style="font-size: 4rem; font-weight: 800; color: #ffffff; margin: 10px 0;">{pos/total_len*100:.1f}%</div>
                    <div style="font-size: 1rem; color: #10b981; font-weight: 600;">{pos} Positive Comments</div>
                </div>
                """, unsafe_allow_html=True)
            
            with b2:
                st.markdown(f"""
                <div class="bento-card" style="justify-content: center; align-items: center; min-height: 250px;">
                    <div class="glowing-icon" style="color: #6366f1;">🛡️</div>
                    <div style="font-size: 1rem; color: #94a3b8; font-weight: 600; text-transform: uppercase;">Trust Score</div>
                    <div style="font-size: 3.5rem; font-weight: 800; color: #ffffff; margin: 10px 0;">{trust_score}</div>
                    <div style="font-size: 0.9rem; color: #6366f1; font-weight: 600;">Brand Safety Rating</div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("<div style='margin: 20px 0;'></div>", unsafe_allow_html=True)

            # Bento Grid Row 2: Secondary Metrics
            s1, s2, s3 = st.columns(3)
            with s1:
                st.markdown(f"""
                <div class="bento-card" style="text-align: center;">
                    <div style="color: #ef4444; font-size: 1.5rem; margin-bottom: 5px;">🛑</div>
                    <div style="font-size: 0.9rem; color: #94a3b8; margin-bottom: 5px;">NEGATIVITY</div>
                    <div style="font-size: 2rem; font-weight: 800; color: #ffffff;">{neg}</div>
                </div>
                """, unsafe_allow_html=True)
            with s2:
                st.markdown(f"""
                <div class="bento-card" style="text-align: center;">
                    <div style="color: #3b82f6; font-size: 1.5rem; margin-bottom: 5px;">👋</div>
                    <div style="font-size: 0.9rem; color: #94a3b8; margin-bottom: 5px;">NEUTRAL</div>
                    <div style="font-size: 2rem; font-weight: 800; color: #ffffff;">{neu}</div>
                </div>
                """, unsafe_allow_html=True)
            with s3:
                st.markdown(f"""
                <div class="bento-card" style="text-align: center;">
                    <div style="color: #f59e0b; font-size: 1.5rem; margin-bottom: 5px;">⚡</div>
                    <div style="font-size: 0.9rem; color: #94a3b8; margin-bottom: 5px;">ENGAGEMENT</div>
                    <div style="font-size: 2rem; font-weight: 800; color: #ffffff;">{total_len}</div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("<div style='margin: 30px 0;'></div>", unsafe_allow_html=True)

            # Charts
            c_left, c_right = st.columns(2)
            with c_left:
                fig = px.pie(data_to_plot, names='Sentiment', title='Mood Distribution', color='Sentiment', hole=0.6,
                                color_discrete_map={'Positive':'#10b981', 'Negative':'#ef4444', 'Neutral':'#6366f1'})
                fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="#ffffff", margin=dict(t=50, b=0, l=0, r=0))
                st.plotly_chart(fig, use_container_width=True)
            
            with c_right:
                if 'Published_At' in data_to_plot.columns:
                    fig_time = px.histogram(data_to_plot, x="Published_At", color="Sentiment", title="Sentiment Over Time",
                                            color_discrete_map={'Positive':'#10b981', 'Negative':'#ef4444', 'Neutral':'#6366f1'})
                    fig_time.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="#ffffff")
                    st.plotly_chart(fig_time, use_container_width=True)

            # AI Reply Assistant (In Dashboard)
            st.markdown("### 🗣️ AI Reply Assistant")
            # Pick a random unanswered question/comment to demonstrate
            sample = data_to_plot[data_to_plot['Reply_Count']==0].head(1)
            if not sample.empty:
                row = sample.iloc[0]
                st.info(f"**Comment**: {row['Comment']}")
                if st.button("Draft Reply ✍️"):
                    suggestion = logic.generate_smart_reply(row['Comment'], row['Persona'], row['Sentiment'])
                    st.success(suggestion)
            else:
                st.write("All comments have replies! Good job.")

        with tab2: # Deep Insights
            col_cloud, col_emoji = st.columns(2)
            with col_cloud:
                st.subheader("☁️ Word Cloud")
                if not data_to_plot.empty:
                    text_combined = " ".join(data_to_plot['Clean_Text'])
                    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text_combined)
                    fig, ax = plt.subplots()
                    ax.imshow(wordcloud, interpolation='bilinear')
                    ax.axis("off")
                    st.pyplot(fig)
            with col_emoji:
                st.subheader("🔥 Top Emojis")
                all_emojis = [char for text in data_to_plot['Emojis'] for char in text]
                if all_emojis:
                    emoji_counts = Counter(all_emojis).most_common(10)
                    emoji_df = pd.DataFrame(emoji_counts, columns=['Emoji', 'Count'])
                    st.plotly_chart(px.bar(emoji_df, x='Emoji', y='Count'), use_container_width=True)
            
            st.subheader("🧩 Top Themes (Bi-grams)")
            if not data_to_plot.empty:
                bigrams = logic.extract_bigrams(data_to_plot['Clean_Text'].dropna())
                if bigrams:
                    bg_df = pd.DataFrame(bigrams, columns=['Phrase', 'Count'])
                    st.plotly_chart(px.bar(bg_df, x='Count', y='Phrase', orientation='h'), use_container_width=True)

        with tab3: # Personas
            st.subheader("👥 Audience Squads")
            if 'Persona' in data_to_plot.columns:
                persona_counts = data_to_plot['Persona'].value_counts().reset_index()
                persona_counts.columns = ['Persona', 'Count']
                fig_p = px.pie(persona_counts, names='Persona', values='Count', hole=0.4, title="Audience Breakdown")
                st.plotly_chart(fig_p, use_container_width=True)
                
                st.markdown("### Drill Down")
                selected_persona = st.selectbox("Select Persona", persona_counts['Persona'].unique())
                persona_comments = data_to_plot[data_to_plot['Persona'] == selected_persona]
                for i, row in persona_comments.head(5).iterrows():
                    st.caption(f"**{row['Author']}**: {row['Comment']}")

        with tab4: # Opportunities
                requests_df = data_to_plot[data_to_plot['Is_Request'] == True]
                if not requests_df.empty:
                    st.success(f"Found {len(requests_df)} Video Requests!")
                    for i, row in requests_df.iterrows():
                        st.info(f"**{row['Author']}**: {row['Comment']}")
                else: st.info("No requests found.")

        with tab5: # Community Hub
            col_q, col_gem = st.columns(2)
            with col_q:
                st.subheader("❓ Unanswered Questions")
                q_df = data_to_plot[(data_to_plot['Is_Question'] == True) & (data_to_plot['Reply_Count'] == 0)]
                if not q_df.empty:
                    for i, r in q_df.iterrows(): st.write(f"**{r['Author']}**: {r['Comment']}")
                else: st.success("No unanswered questions!")
            with col_gem:
                st.subheader("💎 Hidden Gems")
                g_df = data_to_plot[(data_to_plot['Sentiment'] == 'Positive') & (data_to_plot['Reply_Count'] == 0)]
                if not g_df.empty:
                    for i, r in g_df.iterrows(): st.caption(f"**{r['Author']}**: {r['Comment']}")

        with tab6: # Moderate
            toxic_df = data_to_plot[data_to_plot['Is_Toxic'] == True]
            if not toxic_df.empty:
                st.error(f"Found {len(toxic_df)} toxic comments.")
                for i, r in toxic_df.head(10).iterrows(): st.code(f"{r['Author']}: {r['Comment']}")
            else: st.success("No toxic comments.")

        with tab7: # Raw Data
            st.dataframe(data_to_plot)
            csv = data_to_plot.to_csv(index=False).encode('utf-8')
            st.download_button("Download CSV", csv, "sentiment.csv", "text/csv")
            
            # PDF Report Download
            st.markdown("---")
            st.subheader("📄 Download Report")
            
            # Generate PDF on the fly for the download button
            if not data_to_plot.empty:
                pdf_bytes = logic.generate_pdf_report(data_to_plot)
                st.download_button("Download PDF Report 📄", pdf_bytes, "sentiment_report.pdf", "application/pdf")
            else:
                st.warning("No data to generate report.")
                
        with tab8: # RAG Chat
            st.markdown("### 🤖 Chat with Data")
            st.info("Ask questions about the comments! (e.g., 'What do they say about the audio quality?')")
            
            user_query = st.text_input("Ask a question:", key="rag_query")
            if user_query:
                results = logic.query_dataframe(data_to_plot, user_query)
                if results:
                    st.markdown(f"**Found {len(results)} relevant comments:**")
                    for author, comment, score in results:
                        st.markdown(f"> **{author}**: {comment} *(Match: {score:.2f})*")
                else:
                    st.warning("No relevant comments found.")

# --- BATTLE MODE FUNCTION ---
def render_battle_mode():
    st.markdown("""
    <div style='text-align: center; margin-bottom: 2rem;'>
        <h1 style='font-size: 3rem; margin-bottom: 0.5rem;'>⚔️ Battle Mode: Video A vs Video B</h1>
        <p style='font-size: 1.1rem; color: #cbd5e1; margin: 0;'>
            Compare two videos to find the winner and steal winning strategies!
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        url_a = st.text_input("Video A URL (Yours)", placeholder="Your Video Link")
    with col2:
        url_b = st.text_input("Video B URL (Competitor)", placeholder="Competitor Video Link")
        
    if st.button("Start Battle 🥊", type="primary"):
        if not url_a or not url_b:
            st.warning("Please enter both URLs.")
        else:
            with st.spinner("Analyzing both videos..."):
                # Fetch
                raw_a = helper.fetch_comments(url_a)
                raw_b = helper.fetch_comments(url_b)
                
                if isinstance(raw_a, dict) or isinstance(raw_b, dict):
                    st.error("Error fetching one of the videos. Check links/API quota.")
                else:
                    # Process
                    df_a = logic.process_data_deep_learning(raw_a, roberta_model)
                    df_b = logic.process_data_deep_learning(raw_b, roberta_model)
                    
                    # --- 1. KEY METRICS COMPARISON ---
                    st.markdown("## 🥊 Tale of the Tape")
                    col_a, col_mid, col_b = st.columns([1, 0.2, 1])
                    
                    # Calculate Metrics
                    def get_metrics(df):
                        pos_pct = len(df[df['Sentiment']=='Positive']) / len(df) * 100
                        likes = df['Likes'].astype(int).sum()
                        replies = df['Reply_Count'].astype(int).sum()
                        requests = len(df[df['Is_Request']==True])
                        toxic = len(df[df['Is_Toxic']==True])
                        return pos_pct, likes, replies, requests, toxic

                    m_a = get_metrics(df_a)
                    m_b = get_metrics(df_b)
                    
                    with col_a:
                        st.markdown(f"""
                        <div class="bento-card" style="border-color: rgba(16, 185, 129, 0.3); text-align: center;">
                            <div style="font-size: 1.5rem; margin-bottom: 10px;">🎯</div>
                            <div style="font-size: 1rem; color: #94a3b8; font-weight: 600; text-transform: uppercase;">Video A (You)</div>
                            <div style="font-size: 3rem; font-weight: 800; color: #10b981; margin: 15px 0;">{m_a[0]:.1f}%</div>
                            <div style="font-size: 0.9rem; color: #cbd5e1;">Positive Sentiment</div>
                        </div>
                        """, unsafe_allow_html=True)
                        st.markdown("<div style='margin: 20px 0;'></div>", unsafe_allow_html=True)
                        st.metric("Total Comments", len(df_a))
                        st.metric("Total Likes", m_a[1])
                        st.metric("Total Replies (Heat)", m_a[2])
                        st.metric("Video Requests", m_a[3])
                        st.metric("Toxic Comments", m_a[4])

                    with col_b:
                        st.markdown(f"""
                        <div class="bento-card" style="border-color: rgba(239, 68, 68, 0.3); text-align: center;">
                            <div style="font-size: 1.5rem; margin-bottom: 10px;">⚔️</div>
                            <div style="font-size: 1rem; color: #94a3b8; font-weight: 600; text-transform: uppercase;">Video B (Competitor)</div>
                            <div style="font-size: 3rem; font-weight: 800; color: #ef4444; margin: 15px 0;">{m_b[0]:.1f}%</div>
                            <div style="font-size: 0.9rem; color: #cbd5e1;">Positive Sentiment</div>
                        </div>
                        """, unsafe_allow_html=True)
                        st.markdown("<div style='margin: 20px 0;'></div>", unsafe_allow_html=True)
                        st.metric("Total Comments", len(df_b))
                        st.metric("Total Likes", m_b[1], delta=f"{m_b[1]-m_a[1]}")
                        st.metric("Total Replies (Heat)", m_b[2], delta=f"{m_b[2]-m_a[2]}")
                        st.metric("Video Requests", m_b[3], delta=f"{m_b[3]-m_a[3]}")
                        st.metric("Toxic Comments", m_b[4])
                    
                    with col_mid:
                        st.markdown("""
                        <div style='display: flex; align-items: center; justify-content: center; height: 100%; padding-top: 150px;'>
                            <div class="bento-card" style="padding: 10px 20px; border-radius: 100px; border-color: rgba(99, 102, 241, 0.5);">
                                <h1 style='margin: 0; font-size: 2rem; background: linear-gradient(135deg, #10b981 0%, #6366f1 50%, #ef4444 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>VS</h1>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                    st.divider()

                    # --- 2. SENTIMENT & PERSONA BATTLE ---
                    c1, c2 = st.columns(2)
                    with c1:
                        st.subheader("📊 Sentiment Face-off")
                        # Combine for plotting
                        df_a['Video'] = 'Video A'
                        df_b['Video'] = 'Video B'
                        combined_df = pd.concat([df_a, df_b])
                        
                        fig_sent = px.histogram(combined_df, x="Sentiment", color="Video", barmode="group",
                                              color_discrete_map={'Video A': '#00CC96', 'Video B': '#EF553B'})
                        st.plotly_chart(fig_sent, use_container_width=True)
                        
                    with c2:
                        st.subheader("👥 Audience Composition")
                        if 'Persona' in combined_df.columns:
                            fig_pers = px.histogram(combined_df, x="Persona", color="Video", barmode="group",
                                                  color_discrete_map={'Video A': '#00CC96', 'Video B': '#EF553B'})
                            st.plotly_chart(fig_pers, use_container_width=True)

                    st.divider()

                    # --- 3. TOPIC WAR ---
                    st.subheader("🗣️ Topic War")
                    cw1, cw2 = st.columns(2)
                    
                    with cw1:
                        st.info("Video A Top Topics")
                        bg_a = logic.extract_bigrams(df_a['Clean_Text'])
                        if bg_a:
                            st.dataframe(pd.DataFrame(bg_a, columns=['Phrase', 'Count']).head(5), hide_index=True)
                        else: st.write("Not enough data.")

                    with cw2:
                        st.error("Video B Top Topics")
                        bg_b = logic.extract_bigrams(df_b['Clean_Text'])
                        if bg_b:
                            st.dataframe(pd.DataFrame(bg_b, columns=['Phrase', 'Count']).head(5), hide_index=True)
                        else: st.write("Not enough data.")

                    st.divider()

                    # --- 4. STRATEGY ZONE (OPPORTUNITY STEALER) ---
                    st.markdown("## 🕵️ Strategy Zone: Steal from Competitor")
                    st.markdown("Here are insights from **Video B** that you can use for your next video.")
                    
                    sz1, sz2 = st.columns(2)
                    
                    with sz1:
                        st.subheader("💎 Topics to Steal")
                        # Simply showing Video B's topics again but framed as opportunity
                        if bg_b:
                            st.write("People are talking about these in the competitor's video:")
                            for phrase, count in bg_b[:5]:
                                st.markdown(f"- **{phrase}** ({count} mentions)")
                    
                    with sz2:
                        st.subheader("❓ Unanswered Questions (Market Gap)")
                        ua_b = df_b[(df_b['Is_Question']==True) & (df_b['Reply_Count']==0)]
                        if not ua_b.empty:
                            st.write("Your competitor hasn't answered these. **You should!**")
                            for i, row in ua_b.head(5).iterrows():
                                st.info(f"\"{row['Comment']}\"")
                        else:
                            st.success("Competitor has answered most questions. Tough crowd!")

                    st.divider()

                    # --- 5. EMOJI VIBE CHECK ---
                    st.subheader("🔥 Vibe Check (Emojis)")
                    ec1, ec2 = st.columns(2)
                    
                    def plot_emojis(d, title, color):
                        all_e = [c for t in d['Emojis'] for c in t]
                        if not all_e:
                            st.info("No emojis found.")
                            return
                        counts = Counter(all_e).most_common(5)
                        emoji_df = pd.DataFrame(counts, columns=['Emoji', 'Count'])
                        
                        # Use Plotly for a better look
                        fig = px.bar(emoji_df, x='Emoji', y='Count', title=title, 
                                     text='Count', color_discrete_sequence=[color])
                        fig.update_layout(xaxis_title="", yaxis_title="", showlegend=False)
                        st.plotly_chart(fig, use_container_width=True)
                    
                    with ec1:
                        plot_emojis(df_a, "Video A Top Emojis", '#00CC96')
                    with ec2:
                        plot_emojis(df_b, "Video B Top Emojis", '#EF553B')

                    # Raw Data
                    with st.expander("See Raw Comparison Data"):
                        st.write("Video A", df_a.head())
                        st.write("Video B", df_b.head())

# --- CHANNEL TRENDS MODE ---
def render_channel_mode():
    st.markdown("""
    <div style='text-align: center; margin-bottom: 2rem;'>
        <h1 style='font-size: 3rem; margin-bottom: 0.5rem;'>📈 Channel Trends Analysis</h1>
        <p style='font-size: 1.1rem; color: #cbd5e1; margin: 0;'>
            Analyze the last 5 videos to track growth and sentiment consistency
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    url = st.text_input("Enter Channel or Video URL", placeholder="https://www.youtube.com/@ChannelName")
    
    if st.button("Analyze Channel 🚀"):
        if not url:
            st.warning("Please enter a URL.")
            return

        with st.spinner("Fetching channel videos..."):
            # Get Channel ID and Videos
            cid = helper.get_channel_id(url)
            if not cid:
                st.error("Could not find channel. Try a video link from that channel.")
                return
            
            videos = helper.fetch_channel_videos(cid, limit=5)
            if isinstance(videos, dict): # Error
                st.error(videos['error'])
                return
                
            st.success(f"Found {len(videos)} recent videos. Analyzing sentiment...")
            
            # Analyze each video
            results = []
            progress_bar = st.progress(0)
            
            for i, vid in enumerate(videos):
                # Fetch comments
                raw = helper.fetch_comments(vid['url'])
                if isinstance(raw, dict): continue # Skip errors
                if raw.empty: continue
                
                # Analyze
                processed = logic.process_data_deep_learning(raw, roberta_model)
                
                # Metrics
                pos_pct = len(processed[processed['Sentiment']=='Positive']) / len(processed) * 100
                likes = processed['Likes'].astype(int).sum()
                replies = processed['Reply_Count'].astype(int).sum()
                
                results.append({
                    "Title": vid['title'],
                    "Published": vid['published'],
                    "Positivity": pos_pct,
                    "Likes": likes,
                    "Replies": replies
                })
                progress_bar.progress((i + 1) / len(videos))
            
            if not results:
                st.error("No data collected.")
                return
                
            # Visualization
            trend_df = pd.DataFrame(results)
            trend_df['Published'] = pd.to_datetime(trend_df['Published'])
            trend_df = trend_df.sort_values('Published')
            
            # Bento Summary for Channel
            st.divider()
            avg_pos = trend_df['Positivity'].mean()
            total_likes = trend_df['Likes'].sum()
            
            c1, c2 = st.columns(2)
            with c1:
                st.markdown(f"""
                <div class="bento-card" style="text-align: center;">
                    <div class="glowing-icon" style="color: #6366f1;">📈</div>
                    <div style="font-size: 0.9rem; color: #94a3b8; font-weight: 600; text-transform: uppercase;">Average Positivity</div>
                    <div style="font-size: 2.5rem; font-weight: 800; color: #ffffff; margin: 10px 0;">{avg_pos:.1f}%</div>
                </div>
                """, unsafe_allow_html=True)
            with c2:
                st.markdown(f"""
                <div class="bento-card" style="text-align: center;">
                    <div class="glowing-icon" style="color: #10b981;">🚀</div>
                    <div style="font-size: 0.9rem; color: #94a3b8; font-weight: 600; text-transform: uppercase;">Engagement (Likes)</div>
                    <div style="font-size: 2.5rem; font-weight: 800; color: #ffffff; margin: 10px 0;">{total_likes:,}</div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("<div style='margin: 30px 0;'></div>", unsafe_allow_html=True)
            
            # 1. Sentiment Trend
            st.subheader("😊 Sentiment Consistency")
            fig_sent = px.line(trend_df, x='Published', y='Positivity', markers=True, 
                             title="Positivity % Over Last 5 Videos",
                             hover_data=['Title'])
            fig_sent.update_traces(line_color='#00CC96')
            st.plotly_chart(fig_sent, use_container_width=True)
            
            # 2. Engagement Trend
            st.subheader("🔥 Engagement Growth")
            fig_eng = px.bar(trend_df, x='Published', y='Likes', 
                           title="Total Likes per Video",
                           hover_data=['Title'], color='Likes')
            st.plotly_chart(fig_eng, use_container_width=True)
            
            # Table
            with st.expander("View Raw Stats"):
                st.dataframe(trend_df)

# --- MAIN APP LOGIC ---
if app_mode == "Single Video Analysis":
    render_single_mode()
elif app_mode == "⚔️ Battle Mode":
    render_battle_mode()
else:
    render_channel_mode()