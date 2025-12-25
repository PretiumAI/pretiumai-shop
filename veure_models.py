import google.generativeai as genai

# --- POSA LA TEVA CLAU AQUÍ ---
CLAU_SECRETA = "AIzaSyAjwqI8jm_f-jIVwsQcDIrX0F_rXE306Tg" 
# ------------------------------

genai.configure(api_key=CLAU_SECRETA)

print("🔍 PREGUNTANT A GOOGLE QUINS MODELS TENIM DISPONIBLES...")
print("---------------------------------------------------------")

try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"✅ DISPONIBLE: {m.name}")
except Exception as e:
    print(f"❌ Error connectant: {e}")

print("---------------------------------------------------------")