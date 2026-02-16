import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(layout="wide", page_title="Getaround Dashboard")

st.title("🚗 Getaround France - Live")
st.markdown("Dashboard voitures partagées via GBFS")

# Menu villes (proche Val-d'Oise)
villes = ["versailles", "yerres", "paris"]
ville = st.selectbox("Ville :", villes)

if st.button("🔄 Actualiser", type="primary"):
    with st.spinner(f"Chargement {ville.title()}..."):
        try:
            url = f"https://fr.getaround.com/gbfs/v3/{ville}/gbfs"
            resp = requests.get(f"{url}/free_bike_status.json", timeout=10)
            data = resp.json()['data']['bikes']
            
            df = pd.DataFrame(data)
            df['lat'] = df['lat'].astype(float)
            df['lon'] = df['lon'].astype(float)
            
            st.success(f"✅ {len(df)} véhicules trouvés")
            
            # Carte Plotly (remplace folium)
            fig = px.scatter_mapbox(df, 
                                  lat="lat", lon="lon",
                                  hover_data=['bike_id'],
                                  mapbox_style="open-street-map",
                                  zoom=13,
                                  height=500)
            fig.update_layout(title=f"🗺️ {ville.title()} - Voitures libres")
            st.plotly_chart(fig, use_container_width=True)
            
            # Stats
            col1, col2, col3 = st.columns(3)
            with col1: st.metric("Total", len(df))
            with col2: st.metric("Centre", f"{df.lat.mean():.4f}°")
            with col3: st.metric("Étendue", f"{df.lat.std():.3f}°")
            
            st.dataframe(df[['lat','lon','bike_id']].head(10))
            
        except Exception as e:
            st.error(f"❌ {ville} indisponible")
            st.info("→ Teste 'versailles' ou 'yerres' (proche Beaumont-sur-Oise)")
