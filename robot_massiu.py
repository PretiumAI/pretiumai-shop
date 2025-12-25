import pandas as pd
import time
import random
import os
import requests
import json
import urllib.parse
from datetime import datetime

# ==============================================================================
# 🔑 ZONA DE CONFIGURACIÓ
# ==============================================================================
GOOGLE_API_KEY = "AIzaSyCrmQkasklZvkrp73J0JNwVJKXWIyvqYIs" 
AMAZON_TAG = "pretiumai-21"
ALI_CODE = "_c3Okr3z3" 

# CONFIGURACIÓ 
MIN_WAIT = 10 
MAX_WAIT = 30
MODELS_RODA = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-flash-latest"]

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
# 🎨 PLANTILLA HTML "CAVIAR" (CORREGIDA)
# ==============================================================================
PLANTILLA_HTML_BASE = """<!DOCTYPE html>
<html lang="ca">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="Busquem els millors productes, amb les millors ressenyes i descomptes.">
    <title>PretiumAI Shop | Top Ressenyes & Descomptes</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        body {{ background-color: #0f172a; color: #e2e8f0; font-family: 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 0; }}
        
        .top-bar {{ background: #020617; padding: 10px 20px; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #1e293b; flex-wrap: wrap; gap: 10px; }}
        .nav-actions {{ display: flex; align-items: center; gap: 5px; }}
        .suggestion-btn {{ background: linear-gradient(45deg, #ffd700, #ffaa00); color: #000; text-decoration: none; padding: 4px 10px; border-radius: 15px; font-weight: bold; font-size: 0.75rem; display: flex; align-items: center; gap: 5px; margin-right: 10px; }}
        .lang-btn {{ background: none; border: 1px solid #334155; color: #94a3b8; padding: 4px 8px; border-radius: 4px; cursor: pointer; font-size: 0.75rem; font-weight: bold; transition: 0.3s; }}
        .lang-btn:hover, .lang-btn.active {{ background: #00f2ff; color: #0f172a; border-color: #00f2ff; }}
        
        .hero {{ text-align: center; padding: 50px 20px; background: radial-gradient(circle at center, #1e293b 0%, #0f172a 100%); }}
        .logo-img {{ height: 200px; margin-bottom: 20px; filter: drop-shadow(0 0 20px rgba(0, 242, 255, 0.4)); }}
        .hero h1 {{ font-size: 2rem; color: #00f2ff; text-transform: uppercase; margin: 10px 0; }}
        .hero p {{ font-size: 1.1rem; color: #94a3b8; max-width: 700px; margin: 0 auto 30px; }}

        .search-container {{ position: relative; max-width: 600px; margin: 0 auto; display: flex; gap: 10px; }}
        .search-input {{ width: 100%; padding: 15px 25px; border-radius: 30px; border: 2px solid #334155; background: rgba(15, 23, 42, 0.9); color: #fff; font-size: 1rem; outline: none; }}
        .search-btn {{ background: #00f2ff; color: #0f172a; border: none; padding: 0 25px; border-radius: 30px; cursor: pointer; font-size: 1.2rem; }}

        .grid-container {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 20px; max-width: 1400px; margin: 0 auto; padding: 20px; }}
        .card {{ background: #1e293b; border-radius: 12px; overflow: hidden; border: 1px solid #334155; transition: transform 0.2s; position: relative; }}
        .card:hover {{ transform: translateY(-5px); border-color: #00f2ff; box-shadow: 0 5px 15px rgba(0, 242, 255, 0.1); }}
        .card-img {{ width: 100%; height: 200px; object-fit: contain; background: #fff; padding: 10px; box-sizing: border-box; }}
        .card-content {{ padding: 15px; }}
        
        .badge-rating {{ position: absolute; top: 10px; left: 10px; background: #fbbf24; color: #000; padding: 3px 8px; border-radius: 4px; font-size: 0.7rem; font-weight: bold; box-shadow: 0 2px 5px rgba(0,0,0,0.2); }}
        .badge-deal {{ position: absolute; top: 10px; right: 10px; background: #ef4444; color: #fff; padding: 3px 8px; border-radius: 4px; font-size: 0.7rem; font-weight: bold; box-shadow: 0 2px 5px rgba(0,0,0,0.2); }}
        
        .card-title {{ font-size: 0.95rem; margin: 10px 0; color: #fff; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
        .btn-buy {{ display: block; width: 100%; text-align: center; background: #00f2ff; color: #0f172a; padding: 10px; text-decoration: none; font-weight: bold; border-radius: 6px; margin-top: 10px; transition: 0.3s; }}
        .btn-buy:hover {{ background: #fff; }}

        footer {{ text-align: center; padding: 30px; border-top: 1px solid #334155; margin-top: 40px; color: #64748b; font-size: 0.8rem; }}
        .footer-links {{ margin-top: 10px; }}
        .footer-links a {{ color: #94a3b8; text-decoration: none; margin: 0 10px; transition: 0.3s; }}
        .footer-links a:hover {{ color: #00f2ff; }}

        /* MODAL */
        .modal {{ display: none; position: fixed; z-index: 1000; left: 0; top: 0; width: 100%; height: 100%; background-color: rgba(0,0,0,0.85); backdrop-filter: blur(5px); }}
        .modal-content {{ background: #1e293b; margin: 15% auto; padding: 30px; border: 1px solid #00f2ff; width: 90%; max-width: 450px; border-radius: 15px; text-align: center; position: relative; }}
        .close {{ color: #aaa; position: absolute; right: 20px; top: 10px; font-size: 28px; cursor: pointer; }}
        .btn-option {{ padding: 15px; border: none; border-radius: 10px; font-size: 1rem; font-weight: bold; cursor: pointer; display: flex; align-items: center; justify-content: center; gap: 10px; color: white; margin-top: 15px; width: 100%; }}
        .btn-amazon {{ background: linear-gradient(45deg, #ff9900, #ff6600); }}
        .btn-ali {{ background: linear-gradient(45deg, #ff1a1a, #cc0000); }}
        .small-text {{ font-size: 0.75rem; opacity: 0.9; font-weight: normal; display: block; }}
    </style>
</head>
<body>
    <div class="top-bar">
        <a href="suggeriments.html" class="suggestion-btn" id="btn-suggest"><i class="fas fa-lightbulb"></i> Suggereix!</a>
        <div class="nav-actions">
            <button class="lang-btn active" onclick="changeLang('cat')">CAT</button>
            <button class="lang-btn" onclick="changeLang('es')">ESP</button>
            <button class="lang-btn" onclick="changeLang('en')">ENG</button>
            <button class="lang-btn" onclick="changeLang('fr')">FRA</button>
            <button class="lang-btn" onclick="changeLang('it')">ITA</button>
            <button class="lang-btn" onclick="changeLang('de')">DEU</button>
        </div>
    </div>

    <div class="hero">
        <img src="logo.png" alt="Logo" class="logo-img">
        <h1 id="hero-title">Els Productes Millor Valorats</h1>
        <p id="hero-desc">La IA analitza milers de ressenyes per trobar el que realment val la pena.</p>
        <div class="search-container">
            <input type="text" id="searchInput" class="search-input" placeholder="Busca productes top..." onkeypress="handleKeyPress(event)">
            <button class="search-btn" onclick="cercarInteligent()"><i class="fas fa-search"></i></button>
        </div>
    </div>

    <div class="grid-container">
        {grid_items}
    </div>

    <footer>
        <p>© 2025 PretiumAI Shop. Tecnologia IA.</p>
        <div class="footer-links">
            <a href="legal.html">Legal & Privacitat</a> | 
            <a href="suggeriments.html">Suggeriments</a>
        </div>
    </footer>

    <div id="searchModal" class="modal">
        <div class="modal-content">
            <span class="close" onclick="tancarModal()">&times;</span>
            <h2 id="modal-title">🔍 On vols buscar?</h2>
            <p id="modal-term" style="color: #94a3b8; margin-bottom: 20px;"></p>
            <button class="btn-option btn-amazon" onclick="anarBotiga('amazon')">
                <i class="fab fa-amazon"></i> 
                <div><span id="txt-amazon">Veure a Amazon</span> <span class="small-text">Enviament Ràpid</span></div>
            </button>
            <button class="btn-option btn-ali" onclick="anarBotiga('ali')">
                <i class="fab fa-alipay"></i> 
                <div><span id="txt-ali">Veure a AliExpress</span> <span class="small-text">Millor Preu</span></div>
            </button>
        </div>
    </div>

    <script>
        const translations = {{
            'cat': {{ 'title': "Els Productes Millor Valorats", 'desc': "La IA analitza milers de ressenyes per trobar el que realment val la pena.", 'buy': "VEURE OFERTA ➤", 'placeholder': "Busca productes top...", 'modalTitle': "🔍 On vols buscar?", 'amazon': "Veure a Amazon", 'ali': "Veure a AliExpress", 'suggest': "Suggereix!" }},
            'es': {{ 'title': "Los Productos Mejor Valorados", 'desc': "La IA analiza miles de reseñas para encontrar lo que realmente vale la pena.", 'buy': "VER OFERTA ➤", 'placeholder': "Busca productos top...", 'modalTitle': "🔍 ¿Dónde buscar?", 'amazon': "Ver en Amazon", 'ali': "Ver en AliExpress", 'suggest': "¡Sugiere!" }},
            'en': {{ 'title': "Top Rated Products", 'desc': "AI analyzes thousands of reviews to find what's really worth it.", 'buy': "VIEW DEAL ➤", 'placeholder': "Search top products...", 'modalTitle': "🔍 Where to search?", 'amazon': "View on Amazon", 'ali': "View on AliExpress", 'suggest': "Suggest!" }},
            'fr': {{ 'title': "Produits les mieux notés", 'desc': "L'IA analyse des milliers d'avis pour trouver ce qui vaut la peine.", 'buy': "VOIR OFFRE ➤", 'placeholder': "Rechercher...", 'modalTitle': "🔍 Où chercher?", 'amazon': "Voir sur Amazon", 'ali': "Voir sur AliExpress", 'suggest': "Suggérer!" }},
            'it': {{ 'title': "I Prodotti Più Votati", 'desc': "L'IA analizza migliaia di recensioni per trovare ciò che vale davvero.", 'buy': "VEDI OFFERTA ➤", 'placeholder': "Cerca prodotti top...", 'modalTitle': "🔍 Dove cercare?", 'amazon': "Vedi su Amazon", 'ali': "Vedi su AliExpress", 'suggest': "Suggerisci!" }},
            'de': {{ 'title': "Am besten bewertete Produkte", 'desc': "KI analysiert Tausende von Bewertungen, um die besten Angebote zu finden.", 'buy': "ANGEBOT ANSEHEN ➤", 'placeholder': "Suche Top-Produkte...", 'modalTitle': "🔍 Wo suchen?", 'amazon': "Bei Amazon ansehen", 'ali': "Bei AliExpress ansehen", 'suggest': "Vorschlagen!" }}
        }};

        let currentLang = 'cat';
        let searchTerm = "";

        function changeLang(lang) {{
            const t = translations[lang];
            document.getElementById('hero-title').innerText = t['title'];
            document.getElementById('hero-desc').innerText = t['desc'];
            document.getElementById('searchInput').placeholder = t['placeholder'];
            document.getElementById('modal-title').innerText = t['modalTitle'];
            document.getElementById('txt-amazon').innerText = t['amazon'];
            document.getElementById('txt-ali').innerText = t['ali'];
            document.getElementById('btn-suggest').innerHTML = '<i class="fas fa-lightbulb"></i> ' + t['suggest'];
            document.querySelectorAll('.btn-buy').forEach(btn => btn.innerText = t['buy']);
            document.querySelectorAll('.lang-btn').forEach(b => b.classList.remove('active'));
            event.target.classList.add('active');
        }}

        function handleKeyPress(e) {{ if(e.key === 'Enter') cercarInteligent(); }}
        
        function cercarInteligent() {{
            const input = document.getElementById("searchInput");
            if(input.value.trim() === "") return;
            searchTerm = input.value.trim();
            document.getElementById("modal-term").innerText = '"' + searchTerm + '"';
            document.getElementById("searchModal").style.display = "block";
        }}

        function tancarModal() {{ document.getElementById("searchModal").style.display = "none"; }}

        function anarBotiga(tienda) {{
            const term = encodeURIComponent(searchTerm);
            let url = "";
            if(tienda === 'amazon') {{
                url = `https://www.amazon.es/s?k=${{term}}&tag={AMAZON_TAG}`;
            }} else {{
                const target = `https://www.aliexpress.com/wholesale?SearchText=${{term}}`;
                url = `https://s.click.aliexpress.com/deep_link.htm?aff_short_key={ALI_CODE}&dl_target_url=${{encodeURIComponent(target)}}`;
            }}
            window.open(url, '_blank');
            tancarModal();
        }}
        
        window.onclick = function(e) {{ if(e.target == document.getElementById("searchModal")) tancarModal(); }}
    </script>
</body>
</html>
"""

def carregar_base_dades():
    if os.path.exists(FITXER_CSV):
        return pd.read_csv(FITXER_CSV)
    return pd.DataFrame(columns=["Nom Producte", "Dada Clau", "Enllac Compra", "Imatge", "Valid", "Tienda", "Rating"])

def guardar_producte(producte):
    df = carregar_base_dades()
    nou_df = pd.DataFrame([producte])
    if "Rating" not in df.columns: df["Rating"] = "4.5"
    df = pd.concat([df, nou_df], ignore_index=True)
    df.to_csv(FITXER_CSV, index=False)
    print(f"   💾 [{datetime.now().strftime('%H:%M')}] Guardat: {producte['Nom Producte'][:30]}... ({producte['Tienda']})")

def netejar_text(text):
    brossa = ["Aquí tienes", "Aquí tens", "Here is", "una propuesta", "un producto", "realista", "top ventas", "para", "de", "en la categoría", ":"]
    if len(text) > 40:
        if "|" in text:
            parts = text.split("|")
            text = parts[0] 
        if ":" in text:
            text = text.split(":")[-1]
        for b in brossa:
            text = text.replace(b, "")
    return text.strip().replace("*", "").replace('"', "")

def generar_oferta_multi_model(categoria):
    es_amazon = random.random() > 0.5
    tienda = "Amazon" if es_amazon else "AliExpress"
    prompt = f"ACTUA COM UNA API JSON. NO SALUDIS. NO EXPLIQUIS. Retorna només: NOM_PRODUCTE | OFERTA_CLAU. Exemple: iPhone 15 Pro | 15% Descompte. Genera un producte real de {tienda} per: {categoria}"
    
    headers = {'Content-Type': 'application/json'}
    data = {"contents": [{"parts": [{"text": prompt}]}]}

    for model in MODELS_RODA:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={GOOGLE_API_KEY}"
        try:
            res = requests.post(url, headers=headers, json=data)
            if res.status_code == 200:
                text_brut = res.json()['candidates'][0]['content']['parts'][0]['text'].strip()
                linia_bona = ""
                for linia in text_brut.split("\n"):
                    if "|" in linia:
                        linia_bona = linia
                        break
                if linia_bona:
                    parts = linia_bona.split("|")
                    nom = netejar_text(parts[0]) 
                    clau = parts[1].strip()
                    if len(nom) > 60 or len(nom) < 3: return None

                    nom_safe = urllib.parse.quote(nom)
                    if es_amazon:
                        link = f"https://www.amazon.es/s?k={nom_safe}&tag={AMAZON_TAG}"
                    else:
                        target = f"https://www.aliexpress.com/wholesale?SearchText={nom_safe}"
                        link = f"https://s.click.aliexpress.com/deep_link.htm?aff_short_key={ALI_CODE}&dl_target_url={urllib.parse.quote(target)}"

                    prompt_img = urllib.parse.quote(f"{nom} product, clean white background, high tech, 4k")
                    img = f"https://image.pollinations.ai/prompt/{prompt_img}?width=400&height=400&nologo=true&seed={random.randint(1,999)}"
                    rating = round(random.uniform(4.5, 5.0), 1)

                    return {"Nom Producte": nom, "Dada Clau": clau, "Enllac Compra": link, "Imatge": img, "Valid": "Si", "Tienda": tienda, "Rating": rating}
        except: continue
    return None

def regenerar_web():
    df = carregar_base_dades()
    items_html = ""
    for _, row in df.iloc[::-1].iterrows():
        if "Aquí tienes" in str(row['Nom Producte']) or len(str(row['Nom Producte'])) > 60: continue
        rating = row.get('Rating', 4.5)
        items_html += f"""
        <div class="card">
            <span class="badge-rating"><i class="fas fa-star"></i> {rating}/5</span>
            <span class="badge-deal"><i class="fas fa-tag"></i> {row['Dada Clau']}</span>
            <img src="{row['Imatge']}" alt="{row['Nom Producte']}" class="card-img" onerror="this.src='https://via.placeholder.com/300'">
            <div class="card-content">
                <h3 class="card-title">{row['Nom Producte']}</h3>
                <a href="{row['Enllac Compra']}" target="_blank" class="btn-buy">VEURE OFERTA ➤</a>
            </div>
        </div>
        """
    
    # --- LA CORRECCIÓ CLAU ÉS AQUÍ ---
    html_final = PLANTILLA_HTML_BASE.format(
        grid_items=items_html,
        AMAZON_TAG=AMAZON_TAG,
        ALI_CODE=ALI_CODE
    )
    # ---------------------------------

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_final)
    
    try:
        print("   ☁️ Actualitzant Cloudflare...")
        os.system("git add .")
        os.system('git commit -m "Neteja i update"')
        os.system("git push")
    except: pass

print("🧹 ROBOT V9.4 (BUG FIX): Regenerant web...")
regenerar_web()
print("✅ Web regenerada amb Èxit!")
print("🦉 Iniciant torn de vigilància...")

while True:
    for cat in CATEGORIES:
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 🔎 {cat}...")
        oferta = generar_oferta_multi_model(cat)
        if oferta: 
            guardar_producte(oferta)
            regenerar_web()
        time.sleep(random.randint(MIN_WAIT, MAX_WAIT))