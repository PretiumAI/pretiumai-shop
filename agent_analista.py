import google.generativeai as genai
import json
import csv
import os
import time

# 1. CONFIGURACIÓ
# ---------------------------------------------------------
CLAU_SECRETA = "AIzaSyCrmQkasklZvkrp73J0JNwVJKXWIyvqYIs" # <--- POSA LA TEVA CLAU AQUÍ
# ---------------------------------------------------------

genai.configure(api_key=CLAU_SECRETA)
model = genai.GenerativeModel('models/gemini-2.0-flash')

# 2. LA MATÈRIA PRIMERA (Ara amb FOTOS!)
# He posat imatges reals d'internet perquè vegis l'efecte immediatament.
llista_bruta = [

        {
        "text": """NOU 2024!! BUTURE VC90 Aspiradora sense fils potent 450W.
                   La bateria dura fins a 55 minuts. Pantalla tàctil.""",
        "link": "https://es.aliexpress.com/item/exemple-aspiradora",
        # He canviat l'enllaç de la imatge per un que segur que funciona:
        # Imatge de prova segura (un rectangle gris amb text)
        "img": "https://ae-pic-a1.aliexpress-media.com/kf/S4f7ba75919b347269271b8369f6ad8b18.jpg_220x220q75.jpg_.avif"
    },
    {
        "text": """Auriculars inalàmbrics estil Pods Pro 2, cancel·lació de soroll.
                   Bateria de 30 hores amb l'estoig. Blanc pur.""",
        "link": "https://es.aliexpress.com/item/exemple-auriculars",
        "img": "https://m.media-amazon.com/images/I/61SUj2aKoEL._AC_SX679_.jpg"
    },
    {
        "text": """Rellotge Intel·ligent S8 Ultra, caixa robusta titani.
                   Monitor de salut, GPS esportiu. Corretja taronja.""",
        "link": "https://es.aliexpress.com/item/exemple-rellotge",
        "img": "https://m.media-amazon.com/images/I/71XMTLtZd5L._AC_SX679_.jpg"
    }
]

print(f"🏭 Fàbrica iniciada: Processant {len(llista_bruta)} productes amb FOTOS...")

# 3. EL PROMPT (El mateix, funciona bé)
prompt_base = """
Ets un expert en dades d'e-commerce. Analitza aquest text:
'''{text_input}'''

TASQUES:
1. Extreu el nom del producte (curt i atractiu).
2. Extreu la dada tècnica clau.
3. Digues si és vàlid.

IMPORTANT: Respon NOMÉS amb aquest JSON:
{{ "nom_net": "...", "dada_clau": "...", "es_valid": true }}
"""

# 4. EL BUCLE QUE GUARDA IMATGES
nom_fitxer = "base_dades_productes.csv"
fitxer_nou = not os.path.exists(nom_fitxer)

with open(nom_fitxer, mode='a', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    # ATENCIÓ: Nova columna "Imatge" a la capçalera
    if fitxer_nou:
        writer.writerow(["Nom Producte", "Dada Clau", "Enllac Compra", "Imatge", "Valid"])

    for producte in llista_bruta:
        print(f"📸 Processant imatge i dades de: {producte['text'][:15]}...")
        
        try:
            prompt_actual = prompt_base.format(text_input=producte['text'])
            resposta = model.generate_content(prompt_actual)
            
            try:
                text_net = resposta.text.replace("```json", "").replace("```", "").strip()
                dades = json.loads(text_net)
                
                if dades['es_valid']:
                    # Guardem TOT al CSV, inclosa la foto que tenim a la llista
                    writer.writerow([
                        dades['nom_net'], 
                        dades['dada_clau'], 
                        producte['link'], 
                        producte['img'],  # <--- NOVA PEÇA GUARDADA
                        dades['es_valid']
                    ])
                    print(f"   ✅ Guardat amb èxit!")
                else:
                    print("   ⚠️  Producte no vàlid.")

            except Exception:
                print("   ⛔ Error llegint JSON de la IA.")

        except Exception as e:
            print(f"   ❌ Error general: {e}")

        time.sleep(1.5) 

print("\n✨ CSV ACTUALITZAT AMB FOTOS! Ara executa el generador web.")