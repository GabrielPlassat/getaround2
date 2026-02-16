import streamlit as st
import requests
import pandas as pd

st.set_page_config(layout="wide", page_title="Getaround 06")

st.title("🚗 Getaround Alpes-Maritimes - Mouans-Sartoux")
st.markdown("Dashboard centré 43.66°N, 6.94°E (06)")

# Villes 06
villes_06 = ["cannes", "antibes", "grasse", "nice"]
ville = st.selectbox("Ville 06 :", villes_06, index=0)

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
            
            # Distance Mouans-Sartoux
            dists = ((df['lat'] - MOAINS_LAT)**2 + (df['lon'] - MOAINS_LON)**2)**0.5 * 111
            dist_moyenne = dists.mean()
            
            st.success(f"✅ {len(df)} véhicules trouvés à {ville.title()}")
            
            # Tableau principal
            col1, col2 = st.columns([2,1])
            
            with col1:
                st.subheader("📍 Positions véhicules")
                st.dataframe(
                    df[['lat', 'lon', 'bike_id']].round(4),
                    use_container_width=True,
                    height=400
                )
            
            with col2:
                st.metric("Total véhicules", len(df))
                st.metric("Distance moyenne", f"{dist_moyenne:.1f} km")
                st.metric("Plus proche", f"{dists.min():.1f} km")
                st.metric("Plus loin", f"{dists.max():.1f} km")
            
            # Stats détaillées
            st.subheader("📊 Statistiques")
            col1, col2, col3, col4 = st.columns(4)
            with col1: st.metric("Lat moyenne", f"{df.lat.mean():.4f}°")
            with col2: st.metric("Lon moyenne", f"{df.lon.mean():.4f}°")
            with col3: st.metric("Écart lat", f"{df.lat.std():.4f}")
            with col4: st.metric("Écart lon", f"{df.lon.std():.4f}")
            
        except Exception as e:
            st.error(f"❌ {ville} indisponible sur GBFS")
            st.info("→ Teste Cannes ou Antibes (06 confirmés)")
