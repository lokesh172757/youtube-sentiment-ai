import pandas as pd
import logic

# Test Data
data = pd.DataFrame({
    'Clean_Text': [
        "This is amazing", "I love this video", "Great job", "Best content ever",
        "Terrible audio", "Audio is bad", 
        "Make a python tutorial", "Can you do part 2?"
    ],
    'Sentiment': ['Positive', 'Positive', 'Positive', 'Positive', 'Negative', 'Negative', 'Neutral', 'Neutral'],
    'Is_Question': [False, False, False, False, False, False, False, True],
    'Reply_Count': [0, 0, 0, 0, 0, 0, 0, 0]
})

print("Testing Smart Summary Generator...")
try:
    summary = logic.generate_smart_summary(data)
    print("\n--- GENERATED SUMMARY ---")
    print(summary)
    print("-------------------------")
    
    if "Positive" in summary and "Audio" in summary: # 'Audio' might be in bigrams if logic works
        print("SUCCESS: Summary contains expected sentiment.")
    else:
        print("WARNING: Summary text might need checking.")
except Exception as e:
    print(f"FAILED: {e}")
