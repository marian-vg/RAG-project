#!/usr/bin/env python3
"""
Test script to verify Gemini API is working correctly.
Run: python scripts/test_gemini.py
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv

# Load the .env file
load_dotenv()

from src.unificador import FarmaRAG

def test_gemini():
    print("=" * 60)
    print("Testing Gemini API Connection")
    print("=" * 60)

    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("[ERROR] GOOGLE_API_KEY not found in environment")
        return False

    print(f"[OK] GOOGLE_API_KEY loaded: {api_key[:15]}...")

    try:
        rag = FarmaRAG()

        print("\n[SENDING] Test query to Gemini...")
        test_question = "¿Cuáles son los requisitos para cobertura de medicamentos PAMI?"

        response, provider = rag.ask_with_fallback(
            test_question,
            preferred_provider="gemini"
        )

        print(f"\n[RESPONSE]")
        print(f"   Provider used: {provider}")
        print(f"   Response preview: {response[:200]}...")

        if provider == "gemini":
            print("\n[SUCCESS] Gemini is working correctly!")
            return True
        else:
            print(f"\n[WARNING] Expected 'gemini' but got '{provider}'")
            print("   Gemini might have failed and fallen back to another provider")
            return False

    except Exception as e:
        print(f"\n[ERROR] {type(e).__name__}: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_gemini()
    sys.exit(0 if success else 1)
