# OpenAI Tool Calling Demo (Lokálna Kalkulačka)

Tento projekt je jednoduchou ukážkou použitia funkcie "Tool Calling" (predtým známe ako "Function Calling") v OpenAI API pomocou Pythonu.

Skript demonštruje, ako môže jazykový model (v tomto príklade `gpt-4o-mini`) identifikovať zámer používateľa a požiadať o spustenie lokálne definovanej Python funkcie (`calculator`) s príslušnými argumentmi.

## Ako to funguje

1. Skript odošle vstup od používateľa modelu GPT spolu so špecifikáciou dostupného nástroja (kalkulačka).
2. Model rozhodne, či je potrebné nástroj použiť na zodpovedanie otázky.
3. Ak áno, model vráti štruktúrovanú požiadavku (JSON) na spustenie nástroja.
4. Python skript lokálne spustí funkciu kalkulačky s danými argumentmi.
5. Výsledok funkcie sa odošle späť modelu GPT.
6. Model sformuluje finálnu, prirodzenú odpoveď pre používateľa.

## Požiadavky

* Python (napr. 3.10+)
* OpenAI API kľúč

## Inštalácia

1. **Naklonujte tento repozitár (alebo stiahnite súbory).**

2. **Nainštalujte potrebné knižnice:**
   Otvorte terminál v priečinku projektu a spustite:
   ```bash
   pip install -r requirements.txt
