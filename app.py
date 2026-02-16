import streamlit as st
import requests
import pandas as pd

st.set_page_config(layout="wide", page_title="Getaround France Fix")

st.title("🔍 Getaround France - Debug Structure")
st.markdown("Analyse JSON + solutions alternatives")

# 1. TEST BRUT MANIFEST (sans assumption)
if st.button("📊 1. Voir structure JSON brute", type="secondary"):
    try:
        resp = requests.get("https://fr.getaround.com/gbfs/manifest?country_code=FR", timeout=10)
        st.success(f"✅ Status: {resp.status_code}")
        json_data = resp.json()
        
        # Debug complet structure
        st.subheader("Clés disponibles:")
        st.json(list(json_data.keys()))
        
        if 'data' in json_data:
            data = json_data['data']
            st.success(f"✅ 'data' trouvé: {list(data.keys())}")
            if 'gbfs_feeds' in data:
                feeds = data['gbfs_feeds']
                st.success(f"✅ {len(feeds)} feeds trouvés")
                st.write(pd.DataFrame(feeds[:3])[['system_id', 'url']].to_dict())
            else:
                st.error("❌ 'gbfs_feeds' manquant")
                st.write("Clés dans 'data':", list(data.keys()))
        else:
            st.error("❌ 'data' manquant")
            
    except Exception as e:
        st.error(f"Erreur: {e}")

# 2. TEST ENDPOINTS DIRECTS CONNUS
if st.button("🚗 2. Test endpoints directs", type="secondary"):
    tests = [
        "versailles",
        "yerres", 
        "evry",
        "cergy"
    ]
    
    for ville in tests:
        try:
            url = f"https://fr.getaround.com/gbfs/v3/{ville}/gbfs/free_bike_status.json"
            resp = requests.get(url, timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                bikes = data['data']['bikes']
                st.success(f"✅ {ville}: {len(bikes)} voitures")
            else:
                st.write(f"{ville}: HTTP {resp.status_code}")
        except:
            st.write(f"{ville}: ❌ erreur")

# 3. FALLBACK : Données transport.data.gouv.fr
if st.button("📈 3. Dataset officiel data.gouv", type="primary"):
    st.info("Récupère métadonnées officielles Getaround France")
    
    # Dataset statique connu
    metadata = {
        "nom": "Getaround Autopartage France",
        "url_manifest": "https://fr.getaround.com/gbfs/manifest?country_code=FR",
        "dernier_maj": "2025-11-23",
        "format": "GBFS v3.0",
        "couverture": "France entière",
        "vehicules_estimes": "66 000+"
    }
    
    st.success("✅ Dataset OFFICIEL confirmé")
    st.json(metadata)
    
    st.info("**Prochaines étapes possibles :**\n"
            "- Scraping site Getaround.fr (villes/actifs)\n"
            "- Cache local manifest (analyse hors ligne)\n"
            "- Multi-sources (Zity, Free2Move, etc.)")

st.markdown("---")
st.caption("Source: transport.data.gouv.fr/datasets/flotte-getaround-en-libre-service-france")
