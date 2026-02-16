import streamlit as st
import requests
import pandas as pd
import folium
from streamlit_folium import folium_static

st.set_page_config(layout="wide", page_title="Getaround Dashboard")

st.title("🚗 Getaround France - Voitures partagées")
st.markdown("Visualisation temps réel via GBFS")

villes = ["versailles", "yerres", "paris"]
ville = st.selectbox("Ville :", villes)

if st.button("🔄 Actualiser", type="primary"):
    with st.spinner(f"Chargement {ville}..."):
        try:
            url = f"https://fr.getaround.com/gbfs/v3/{ville}/gbfs"
            resp = requests.get(f"{url}/free_bike_status.json", timeout=10)
            data = resp.json()['data']['bikes']
            
            df = pd.DataFrame(data)
            st.success(f"✅ {len(df)} véhicules trouvés")
            
            col1, col2 = st.columns([3,1])
            with col1:
                m = folium.Map([df['lat'].astype(float).mean(), 
                              df['lon'].astype(float).mean()], zoom_start=13)
                for _, row in df.iterrows():
                    folium.Marker([row['lat'], row['lon']], 
                                popup=row.get('bike_id', 'Voiture'),
                                icon=folium.Icon(color="blue", icon="car")
                    ).add_to(m)
                folium_static(m)
            
            with col2:
                st.metric("Véhicules libres", len(df))
                st.dataframe(df[['lat','lon','bike_id']].head())
        except:
            st.error(f"❌ {ville} indisponible")
