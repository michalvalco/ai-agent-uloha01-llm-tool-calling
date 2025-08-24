import json
import os
from openai import OpenAI
from dotenv import load_dotenv  # Import knižnice
from typing import Dict, Any, List

load_dotenv()  # Načíta premenné zo súboru .env

# Inicializácia klienta. Knižnica automaticky načíta kľúč z premennej prostredia OPENAI_API_KEY.
try:
    client = OpenAI()
except Exception as e:
    print(f"Chyba pri inicializácii OpenAI klienta: {e}")
    print("Uistite sa, že máte nastavenú premennú prostredia OPENAI_API_KEY.")
    # Ukončíme skript, ak nemáme prístup k API
    exit()

# -----------------------------------------------------------------
# Krok 1: Definícia lokálneho nástroja (Python Funkcia)
# -----------------------------------------------------------------

def calculator(a: float, b: float, operation: str) -> str:
    """Vykoná jednoduchú matematickú operáciu."""
    if operation == "add":
        result = a + b
    elif operation == "subtract":
        result = a - b
    elif operation == "multiply":
        result = a * b
    elif operation == "divide":
        if b == 0:
            return "Chyba: Delenie nulou."
        result = a / b
    else:
        return f"Chyba: Neznáma operácia '{operation}'."
    
    # Vrátime výsledok ako string, aby sme ho mohli ľahko poslať späť LLM.
    return str(result)

# -----------------------------------------------------------------
# Krok 2: Definícia špecifikácie nástroja (JSON Schema pre LLM)
# Toto hovorí LLM, ako sa funkcia volá a aké parametre očakáva.
# -----------------------------------------------------------------

TOOLS_SPECIFICATION = [
    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": "Vykoná základné aritmetické operácie (sčítanie, odčítanie, násobenie, delenie).",
            "parameters": {
                "type": "object",
                "properties": {
                    "a": {
                        "type": "number",
                        "description": "Prvé číslo.",
                    },
                    "b": {
                        "type": "number",
                        "description": "Druhé číslo.",
                    },
                    "operation": {
                        "type": "string",
                        "description": "Operácia, ktorá sa má vykonať.",
                        # Enum obmedzuje možné hodnoty, čo pomáha LLM byť presnejší
                        "enum": ["add", "subtract", "multiply", "divide"],
                    },
                },
                "required": ["a", "b", "operation"],
            },
        },
    }
]

# -----------------------------------------------------------------
# Krok 3: Logika konverzácie (Orchestrácia)
# -----------------------------------------------------------------

def run_conversation(user_prompt: str) -> None:
    print(f"Používateľ: {user_prompt}")
    
    # Inicializácia histórie konverzácie
    messages: List[Dict[str, Any]] = [{"role": "user", "content": user_prompt}]
    
    # Mapa dostupných funkcií v našom skripte
    available_functions = {
        "calculator": calculator,
    }

    # --- Prvé volanie API ---
    # Posielame otázku a definíciu nástrojov
    response = client.chat.completions.create(
        model="gpt-4o-mini", # Moderný a efektívny model (alebo gpt-3.5-turbo)
        messages=messages,
        tools=TOOLS_SPECIFICATION,
        tool_choice="auto",  # LLM sa rozhodne, či nástroj použiť
    )
    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls

    # --- Spracovanie odpovede ---
    if not tool_calls:
        # Ak LLM nechce použiť nástroj
        print(f"\nAI Odpoveď (priama): {response_message.content}")
        return

    print("LLM požaduje použitie nástroja...")
    
    # Pridáme odpoveď LLM (ktorá obsahuje požiadavku na nástroj) do histórie
    messages.append(response_message)

    # --- Vykonanie nástroja lokálne ---
    for tool_call in tool_calls:
        function_name = tool_call.function.name
        
        if function_name not in available_functions:
            print(f"Chyba: LLM sa pokúsilo zavolať neexistujúcu funkciu {function_name}.")
            continue
            
        function_to_call = available_functions[function_name]
        
        # Načítame argumenty (prichádzajú ako JSON string)
        function_args = json.loads(tool_call.function.arguments)
        
        print(f"Spúšťam funkciu: {function_name} s argumentami: {function_args}")
        
        # Spustíme SKUTOČNÚ Python funkciu (použitím ** rozbalíme slovník argumentov)
        function_response = function_to_call(**function_args)
        
        print(f"Výsledok funkcie: {function_response}")

        # Pridáme výsledok nástroja do histórie konverzácie
        messages.append(
            {
                "tool_call_id": tool_call.id,
                "role": "tool",
                "name": function_name,
                "content": function_response,
            }
        )

    # --- Druhé volanie API ---
    # Pošleme celú históriu (vrátane výsledku nástroja) späť LLM, aby sformulovalo finálnu odpoveď
    second_response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
    )
    final_answer = second_response.choices[0].message.content
    print(f"\nAI Odpoveď (finálna): {final_answer}")

# -----------------------------------------------------------------
# Spustenie príkladu
# -----------------------------------------------------------------

if __name__ == "__main__":
    print("--- Test 1: Výpočet (Očakáva sa použitie nástroja) ---")
    run_conversation("Ahoj, potrebujem vypočítať, koľko je 42 vynásobené číslom 19.5?")
    
    print("\n--- Test 2: Bežná konverzácia (Nástroj nie je potrebný) ---")
    run_conversation("Ahoj, ako sa máš?")