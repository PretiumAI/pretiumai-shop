import pandas as pd
import time
import random
import os
import json
import urllib.parse
from datetime import datetime
import google.generativeai as genai

# ==============================================================================
# 🔑 ZONA DE CONFIGURACIÓ (POSA LA NOVA CLAU AQUÍ)
# ==============================================================================
GOOGLE_API_KEY = "AIzaSyAjwqI8jm_f-jIVwsQcDIrX0F_rXE306Tg" 
# 👆👆👆 RECORDA: Esborra el text i posa la clau AIza...

AMAZON_TAG = "pretiumai-21"
ALI_CODE = "_c3Okr3z3" 

# Configurem la clau
try:
    genai.configure(api_key=GOOGLE_API_KEY)
except Exception as e:
    print(f"❌ Error configurant la clau: {e}")

# CONFIGURACIÓ
MIN_WAIT = 100 
MAX_WAIT = 300

# ⚠️ LLISTA ACTUALITZADA SEGONS EL TEU TEST (Models 2025)
# Fem servir els que sabem segur que tens disponibles
MODELS_RODA = ["gemini-2.0-flash", "gemini-2.5-flash","gemini-2.5-pro","gemini-2.0-flash-exp","gemini-2.0-flash-001","gemini-2.0-flash-lite-001","gemini-2.0-flash-lite","gemini-2.0-flash-lite-preview-02-05","gemini-2.0-flash-lite-preview","gemini-exp-1206","gemini-2.5-flash-preview-tts","gemini-2.5-pro-preview-tts","gemini-2.5-pro-preview-tts","gemma-3-1b-it","gemma-3-4b-it","gemma-3-12b-it","gemma-3-27b-it","gemma-3n-e4b-it","gemma-3n-e2b-it","gemini-flash-latest","gemini-flash-lite-latest","gemini-pro-latest","gemini-2.5-flash-lite","gemini-2.5-flash-image","gemini-2.5-flash-preview-09-2025","gemini-2.5-flash-lite-preview-09-2025","gemini-3-pro-preview","gemini-3-flash-preview","gemini-3-pro-image-preview"]

CATEGORIES = [
    "Cafeteras italianas rojas", "Juguetes de madera para niños",
    "Teclados mecánicos gaming", "Ratones gaming ligeros", 
    "Auriculares inalámbricos cancelación ruido", "Relojes inteligentes calidad precio",
    "Mochilas para portátil impermeables", "Soportes monitor brazo gas",
    "Tiras LED neón flexibles", "Cargadores rápidos GaN 65W",
    "Tablets baratas para estudiar", "Altavoces bluetooth potentes pequeños",
    "Sillas gaming ergonómicas baratas", "Webcams streaming 1080p 60fps",
    "Microfonos USB para podcast", "Discos duros SSD externos 1TB",
    "Hubs USB-C para Macbook", "Fundas teclado iPad con trackpad",
    "Proyectores portátiles mini", "Pulseras de actividad deportivas",
    "Ropa ciclismo maillot culotte", "Bicicletas electricas mtb gravel", 
    "Sistemas almacenamiento NAS", "Discos duros server 4TB 8TB",
    "Impresoras 3D baratas", "Drones con camara 8k", "Smart Home enchufes wifi"
]

FITXER_CSV = "base_dades_final.csv"

# ==============================================================================
# 🎨 PLANTILLA HTML
# ==============================================================================
PLANTILLA_HTML_BASE = """<!DOCTYPE html>
<html lang="ca">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PretiumAI Shop</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        body {{ background-color: #0f172a; color: #e2e8f0; font-family: sans-serif; margin: 0; padding: 20px; }}
        .grid-container {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 20px; max-width: 1400px; margin: 0 auto; }}
        .card {{ background: #1e293b; border-radius: 12px; overflow: hidden; border: 1px solid #334155; padding: 15px; }}
        .card img {{ width: 100%; height: 200px; object-fit: contain; background: #fff; }}
        .btn-buy {{ display: block; width: 100%; text-align: center; background: #00f2ff; color: #000; padding: 10px; margin-top: 10px; text-decoration: none; border-radius: 5px; font-weight: bold; }}
    </style>
</head>
<body>
    <h1 style="text-align:center; color:#00f2ff;">PretiumAI Shop</h1>
    <div class="grid-container">{grid_items}</div>
</body>
</html>
"""

def carregar_base_dades():
    if os.path.exists(FITXER_CSV): return pd.read_csv(FITXER_CSV)
    return pd.DataFrame(columns=["Nom Producte", "Dada Clau", "Enllac Compra", "Imatge", "Valid", "Tienda", "Rating"])

def guardar_producte(producte):
    df = carregar_base_dades()
    if not df.empty and producte['Nom Producte'] in df['Nom Producte'].values:
        print(f"   ⚠️ Duplicat ignorat.")
        return False
    nou_df = pd.DataFrame([producte])
    if "Rating" not in df.columns: df["Rating"] = "4.5"
    df = pd.concat([df, nou_df], ignore_index=True)
    df.to_csv(FITXER_CSV, index=False)
    print(f"   💾 GUARDAT: {producte['Nom Producte'][:30]}...")
    return True

def netejar_text(text):
    return text.replace("*", "").replace('"', "").strip()

def generar_oferta_multi_model(categoria):
    es_amazon = random.random() > 0.5
    tienda = "Amazon" if es_amazon else "AliExpress"
    prompt = f"Genera un objecte JSON amb un producte real de {tienda} per '{categoria}'. Format: nom | oferta. Exemple: iPhone 15 | 10% OFF. No xerris, només dades."
    
    for model_name in MODELS_RODA:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            
            if not response.text:
                print(f"   ❌ {model_name}: Resposta buida.")
                continue
                
            text_brut = response.text.strip()
            
            linia_bona = ""
            for linia in text_brut.split("\n"):
                if "|" in linia:
                    linia_bona = linia
                    break
            
            if linia_bona:
                parts = linia_bona.split("|")
                nom = netejar_text(parts[0]) 
                clau = parts[1].strip()
                
                nom_safe = urllib.parse.quote(nom)
                link = f"https://www.amazon.es/s?k={nom_safe}&tag={AMAZON_TAG}" if es_amazon else f"https://s.click.aliexpress.com/deep_link.htm?aff_short_key={ALI_CODE}&dl_target_url={urllib.parse.quote(f'https://www.aliexpress.com/wholesale?SearchText={nom_safe}')}"
                img = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(nom)}?width=400&height=400&nologo=true"
                
                return {"Nom Producte": nom, "Dada Clau": clau, "Enllac Compra": link, "Imatge": img, "Valid": "Si", "Tienda": tienda, "Rating": 4.8}
        except Exception as e:
            print(f"   🔥 ERROR {model_name}: {e}")
            continue
            
    return None

def regenerar_web():
    df = carregar_base_dades()
    items_html = ""
    for _, row in df.iloc[::-1].iterrows():
        items_html += f"""<div class="card"><img src="{row['Imatge']}"><h3>{row['Nom Producte']}</h3><p>{row['Dada Clau']}</p><a href="{row['Enllac Compra']}" class="btn-buy">VEURE</a></div>"""
    with open("index.html", "w", encoding="utf-8") as f: f.write(PLANTILLA_HTML_BASE.format(grid_items=items_html))
    try:
        os.system("git add . >nul 2>&1")
        os.system('git commit -m "update" >nul 2>&1')
        os.system("git push >nul 2>&1")
    except: pass

print("🕵️‍♂️ ROBOT V14 (MODELS ACTUALITZATS 2.0/2.5)...")
while True:
    for cat in CATEGORIES:
        print(f"\n🔎 Buscant: {cat}...")
        oferta = generar_oferta_multi_model(cat)
        if oferta: 
            if guardar_producte(oferta): regenerar_web()
        else:
            print("⚠️ Cap model ha pogut generar una oferta (Revisa la clau API).")
        time.sleep(random.randint(MIN_WAIT, MAX_WAIT))