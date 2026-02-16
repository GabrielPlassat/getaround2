import streamlit as st
import requests
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide", page_title="Getaround 06")

st.title("🚗 Getaround Alpes-Maritimes - Mouans-Sartoux")
st.markdown("Dashboard centré 43.66°N, 6.94°E (06)")

# Mouans-Sartoux + villes 06 proches
villes_06 = ["mouans-sartoux", "cannes", "antibes", "grasse", "nice"]
ville = st.selectbox("Ville 06 :", villes_06, index=0)

# Coordonnées Mouans-Sartoux pour centrage
MOAINS_LAT, MOAINS_LON = 43.66, 6.94

if st.button("🔄 Actualiser", type="primary"):
    with st.spinner(f"Scan {ville.title()}..."):
        try:
            url = f"https://fr.getaround.com/gbfs/v3/{ville}/gbfs"
            resp = requests.get(f"{url}/free_bike_status.json", timeout=10)
            data = resp.json()['data']['bikes']
            
            df = pd.DataFrame(data)
            df['lat'] = df['lat'].astype(float)
            df['lon'] = df['lon'].astype(float)
            
            st.success(f"✅ {len(df)} véhicules {ville.title()}")
            
            # Carte centrée Mouans-Sartoux
            fig = px.scatter_mapbox(df, 
                                  lat="lat", lon="lon",
                                  hover_data=['bike_id'],
                                  mapbox_style="open-street-map",
                                  center={"lat": MOAINS_LAT, "lon": MOAINS_LON},
                                  zoom=12,
                                  height=500)
            fig.update_layout(title=f"🗺️ {ville.title()} - Voitures libres")
            st.plotly_chart(fig, use_container_width=True)
            
            # Stats localisation
            col1, col2, col3, col4 = st.columns(4)
            with col1: st.metric("Total", len(df))
            with col2: st.metric("Distance centre", f"{((df[['lat','lon']].sub([MOAINS_LAT,MOAINS_LON]).pow(2).sum(1).sqrt()*111).mean():.1f}km")
            with col3: st.metric("Lat min-max", f"{df.lat.min():.3f}-{df.lat.max():.3f}")
            with col4: st.metric("Lon min-max", f"{df.lon.min():.3f}-{df.lon.max():.3f}")
            
            st.dataframe(df[['lat','lon','bike_id']].head(10), use_container_width=True)
            
        except Exception as e:
            st.error(f"❌ {ville} indisponible")
            st.info("Getaround Alpes-Maritimes actif mais GBFS peut être limité.\nTeste 'cannes' ou 'antibes'")
