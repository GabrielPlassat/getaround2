import streamlit as st
import requests
import pandas as pd

st.set_page_config(layout="wide", page_title="Getaround data.gouv")

st.title("🚗 Getaround France - Données Officielles")
st.markdown("**API transport.data.gouv.fr/datasets/678e6c068a2785ad5b2099f8**")

@st.cache_data(ttl=3600)
def get_dataset_info():
    url = "https://transport.data.gouv.fr/api/datasets/678e6c068a2785ad5b2099f8"
    resp = requests.get(url)
    return resp.json()

dataset = get_dataset_info()
st.success(f"✅ Dataset ID: {dataset['id']}")

# Métadonnées principales
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Titre", dataset['title'][:30] + "...")
with col2:
    st.metric("Organisation", dataset['organization']['name'])
with col3:
    st.metric("Créé le", dataset['created_at'][:10])

# Ressources disponibles
st.subheader("📁 Ressources du dataset")
resources = dataset['resources']
df_resources = pd.DataFrame(resources)

if not df_resources.empty:
    st.dataframe(df_resources[['title', 'format', 'url', 'created_at', 'last_modified']].head(10))
    
    # URLs exploitables
    gbfs_urls = df_resources[df_resources['format'] == 'gbfs']['url'].tolist()
    st.info(f"**{len(gbfs_urls)} URLs GBFS disponibles**")
    
    for url in gbfs_urls[:5]:
        st.code(url)
    
    # Download principal
    main_resource = df_resources.iloc[0]
    if st.button("📥 Télécharger ressource principale"):
        st.download_button(
            "Télécharger CSV/JSON",
            requests.get(main_resource['url']).content,
            main_resource['title'],
            main_resource['format']
        )

# Manifests GBFS listés
st.subheader("🔗 Manifests GBFS officiels")
for resource in resources[:10]:
    if resource['format'] in ['gbfs', 'json']:
        st.markdown(f"**{resource['title']}**")
        st.caption(resource['url'])
        if st.button(f"Test {resource['title'][:20]}...", key=resource['id']):
            try:
                resp = requests.get(resource['url'])
                st.json(resp.json())
            except Exception as e:
                st.error(str(e))

st.markdown("---")
st.caption("Source officielle transport.data.gouv.fr")
