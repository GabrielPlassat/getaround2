import streamlit as st
import requests
import pandas as pd

st.set_page_config(layout="wide", page_title="Getaround data.gouv")

st.title("🚗 Getaround France - API Officielle")
st.markdown("Dataset: https://transport.data.gouv.fr/api/datasets/678e6c068a2785ad5b2099f8")

@st.cache_data(ttl=3600)
def get_dataset_info():
    url = "https://transport.data.gouv.fr/api/datasets/678e6c068a2785ad5b2099f8"
    resp = requests.get(url)
    return resp.json()

dataset = get_dataset_info()
st.success(f"✅ Dataset chargé: {dataset.get('id', 'N/A')}")

# Métadonnées robustes
col1, col2, col3 = st.columns(3)
st.metric("Titre", str(dataset.get('title', 'N/A'))[:40])
st.metric("Organisation", str(dataset.get('organization', {}).get('name', 'N/A')))
st.metric("Date création", str(dataset.get('created_at', 'N/A'))[:10])

# Debug: voir TOUTES les clés
st.subheader("🔍 Structure JSON")
st.json(list(dataset.keys())[:10])  # Top 10 clés

# Ressources SAFES
st.subheader("📁 Ressources (colonnes disponibles)")
resources = dataset.get('resources', [])
st.write(f"**{len(resources)} ressources trouvées**")

if resources:
    # Colonnes DISPONIBLES uniquement
    df_resources = pd.DataFrame(resources)
    cols_available = [col for col in df_resources.columns if col in ['title', 'format', 'url', 'last_modified', 'created_at', 'size']]
    st.write(f"Colonnes: {list(df_resources.columns)}")
    
    if cols_available:
        display_cols = [col for col in ['title', 'format', 'url', 'last_modified'] if col in df_resources.columns]
        st.dataframe(df_resources[display_cols].head(10), use_container_width=True)
    else:
        st.write("Aucune colonne standard trouvée")
        st.dataframe(df_resources.head(3))
    
    # URLs exploitables
    urls = df_resources[df_resources['format'].isin(['gbfs', 'json', 'csv']) if 'format' in df_resources.columns else df_resources].get('url', '').tolist()
    st.info(f"🔗 {len(urls)} URLs détectées")
    
    for i, url in enumerate(urls[:5]):
        st.code(str(url))
        if st.button(f"🔍 Tester {i+1}", key=f"test{i}"):
            try:
                resp = requests.get(url, timeout=10)
                st.success(f"✅ {resp.status_code}")
                st.json(resp.json())
            except Exception as e:
                st.error(f"❌ {e}")

st.markdown("---")
st.caption("API transport.data.gouv.fr - Standard FabMob")
