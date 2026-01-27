import pandas as pd
import logic
import helper

# Test Data
data = [
    "This is a great video, I love it.",
    "Make a tutorial on Python please.",
    "This is the worst video ever, stupid.",
    "Great video, waiting for next part.",
    "Next part please.",
    "How do I install this?"
]

print("1. Testing Bigrams...")
try:
    bigrams = logic.extract_bigrams(data)
    print("Sucess:", bigrams)
except Exception as e:
    print("FAILED Bigrams:", e)

print("\n2. Testing Toxicity...")
try:
    # Toxic: Negative + High Confidence
    is_tox = logic.is_toxic('Negative', 0.99)
    # Not Toxic: Negative + Low Confidence
    not_tox = logic.is_toxic('Negative', 0.60)
    
    if is_tox and not not_tox:
        print("Success: Toxicity logic works.")
    else:
        print("FAILED Toxicity Logic")
except Exception as e:
    print("FAILED Toxicity:", e)

print("\n3. Testing Helper Date Fetching (Simulated)")
# We can't easily test API without quota, but we can check if helper code compiles
print("Helper module imported successfully.")
