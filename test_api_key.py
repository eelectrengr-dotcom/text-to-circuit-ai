# test_api_key.py
#
# Run this directly to check your Gemini API key, completely
# independent of app.py / Streamlit:
#
#     python test_api_key.py
#
# It will tell you exactly what's wrong: missing key, wrong format,
# or a real 401 from Google.

import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

print("-" * 55)

if not api_key:
    print("❌ GEMINI_API_KEY was not found in the environment.")
    print("   Check that a .env file exists in this same folder")
    print("   and contains a line like:")
    print("   GEMINI_API_KEY=AIzaSy...")
    raise SystemExit(1)

print(f"✅ Found a key in the environment.")
print(f"   Length: {len(api_key)} characters")
print(f"   Starts with 'AIzaSy': {api_key.startswith('AIzaSy')}")

if not api_key.startswith("AIzaSy"):
    print()
    print("⚠️  This does not look like a standard Gemini Developer API key.")
    print("   Real keys from https://aistudio.google.com/apikey start")
    print("   with 'AIzaSy' and are 39 characters long. Double-check")
    print("   you copied a Developer API key, not an OAuth/Vertex token.")

print("-" * 55)
print("Now trying an actual request to Gemini...")
print("-" * 55)

try:
    from google import genai

    client = genai.Client(api_key=api_key)

    response = client.models.generate_content(
        model="gemini-3.8-flash",
        contents="Reply with exactly one word: OK",
    )

    print("✅ SUCCESS — the key works.")
    print("   Model replied:", response.text.strip())

except Exception as e:
    print("❌ The request failed. Full error below:")
    print()
    print(e)
    print()
    print("If this says 401 / UNAUTHENTICATED, the key itself is the")
    print("problem (wrong value, wrong type, or restricted) — this is")
    print("not something in app.py or ai_parser.py that needs changing.")
