import json
from src.config import FarmaConfig
from src.auditor import FarmaAuditor

def main():
    # 1. Load config from config.json
    config = FarmaConfig.load("config.json")
    print(f"[*] Config loaded: filter_by_entity={config.filter_by_entity}")

    # 2. Create a FarmaAuditor instance
    auditor = FarmaAuditor(config)
    print("[*] FarmaAuditor instance created")

    # 3. Call _detect_entity_from_query with the test question
    question = "¿Qué sucede con las recetas físicas de OSER desde 2026?"
    detected_entity = auditor._detect_entity_from_query(question)
    print(f"[*] Question: {question}")
    print(f"[*] Detected entity: {detected_entity}")

    # 4. Call ask_with_fallback with the same question
    print("\n[*] Calling ask_with_fallback...")
    try:
        response, provider = auditor.ask_with_fallback(question)
        print(f"[*] Provider used: {provider}")
        print("[*] Full response:")
        print(response)
    except Exception as e:
        print(f"[!] Error during ask_with_fallback: {e}")

if __name__ == "__main__":
    main()
