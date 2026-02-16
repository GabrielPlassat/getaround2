import streamlit as st
import requests
import pandas as pd

st.set_page_config(layout="wide", page_title="Getaround data.gouv")

st.title("🚗 Getaround France - API data.gouv.fr")
st.markdown("Dataset officiel: https://transport.data.gouv.fr/api/datasets/678e6c068a2785ad5b2099f8")

@st.cache_data(ttl=3600)
def get_dataset_info():
    url = "https://transport.data.gouv.fr/api/datasets/678e6c068a2785ad5b2099f8"
    resp = requests.get(url)
    return resp.json()

dataset = get_dataset_info()
st.success(f"✅ Dataset ID: {dataset.get('id', 'N/A')}")

# Métadonnées SAFE
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Titre", str(dataset.get('title', 'N/A'))[:30])
with col2:
    org_name = dataset.get('organization', {}).get('name', 'N/A')
    st.metric("Organisation", str(org_name))
with col3:
    st.metric("Créé", str(dataset.get('created_at', 'N/A'))[:10])

# TOUTES les ressources
st.subheader("📁 Ressources disponibles")
resources = dataset.get('resources', [])
df_resources = pd.DataFrame(resources)

if not df_resources.empty:
    st.dataframe(df_resources[['title', 'format', 'url', 'last_modified']].head(10), use_container_width=True)
    
    # URLs GBFS/JSON
    gbfs_urls = df_resources[df_resources['format'].isin(['gbfs', 'json'])]['url'].tolist()
    st.info(f"🔗 {len(gbfs_urls)} URLs GBFS/JSON disponibles")
    
    for i, url in enumerate(gbfs_urls[:5]):
        st.code(url)
        if st.button(f"Test URL {i+1}", key=f"test_{i}"):
            try:
                resp = requests.get(url, timeout=10)
                st.json(resp.json())
            except Exception as e:
                st.error(f"Erreur: {e}")

# Download fichiers principaux
if not df_resources.empty:
    st.subheader("📥 Téléchargements")
    for idx, resource in df_resources.head(3).iterrows():
        if st.button(f"Télécharger {resource['title'][:30]}", key=f"dl_{idx}"):
            try:
                content = requests.get(resource['url']).content
                st.download_button(
                    label=f"💾 {resource['format'].upper()}",
                    data=content,
                    file_name=f"getaround_{resource['title'][:20]}.{resource['format']}",
                    mime=resource.get('mime', None)
                )
            except:
                st.error("Download échoué")

st.markdown("---")
st.caption("Source officielle transport.data.gouv.fr API")
