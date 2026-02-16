import streamlit as st
import requests
import pandas as pd
import time

st.set_page_config(layout="wide", page_title="Getaround 06 Scanner")

st.title("🚗 Getaround 06 - Scanner Départemental")
st.markdown("**Mouans-Sartoux + Alpes-Maritimes**")

# Centre Mouans-Sartoux
MOAINS_LAT, MOAINS_LON = 43.66, 6.94

# Scan manifest France
@st.cache_data(ttl=1800)  # 30min cache
def get_all_systems():
    try:
        manifest = requests.get("https://fr.getaround.com/gbfs/manifest?country_code=FR")
        data = manifest.json()['data']['gbfs_feeds']
        return [s for s in data if any(x in s['system_id'] for x in ['06', 'alpes', 'cannes', 'nice', 'antibes', 'grasse'])]
    except:
        return []

systems_06 = get_all_systems()
st.info(f"📡 **{len(systems_06)} systèmes détectés** dans le 06")

if st.button("🔍 Scanner 06 Complet", type="primary"):
    progres = st.progress(0)
    
    all_vehicles = []
    for i, system in enumerate(systems_06[:20]):  # Top 20
        try:
            ville = system['system_id'].replace('getaround_', '')
            url = system['urls']['en']['free_bike_status']
            resp = requests.get(url, timeout=8)
            vehicles = resp.json()['data']['bikes']
            
            for v in vehicles:
                v['system_id'] = ville
                all_vehicles.append(v)
            
            progres.progress(i/len(systems_06))
            time.sleep(0.2)  # Rate limit
            
        except:
            continue
    
    if all_vehicles:
        df = pd.DataFrame(all_vehicles)
        df['lat'] = df['lat'].astype(float)
        df['lon'] = df['lon'].astype(float)
        
        # Distance Mouans-Sartoux
        df['dist_km'] = ((df['lat'] - MOAINS_LAT)**2 + (df['lon'] - MOAINS_LON)**2)**0.5 * 111
        
        st.success(f"✅ **{len(df)} véhicules** sur {len(df['system_id'].unique())} villes 06")
        
        # Tableau principal
        col1, col2 = st.columns([2,1])
        with col1:
            st.subheader("📍 Voitures Getaround 06")
            st.dataframe(df[['system_id', 'lat', 'lon', 'dist_km', 'bike_id']].sort_values('dist_km').round(2), height=400)
        
        with col2:
            st.metric("Total 06", len(df))
            st.metric("Rayon moyen", f"{df.dist_km.mean():.1f} km")
            st.metric("Plus proche MS", f"{df.dist_km.min():.1f} km")
            st.metric("Villes actives", len(df['system_id'].unique()))
        
        # Top 10 proches Mouans-Sartoux
        st.subheader("🎯 Top 10 - Proches Mouans-Sartoux")
        proches = df.nsmallest(10, 'dist_km')[['system_id', 'lat', 'lon', 'dist_km', 'bike_id']]
        st.dataframe(proches.round(2))
        
    else:
        st.warning("❌ Aucun véhicule GBFS 06 actif actuellement")
        st.info("Getaround 06 existe mais free-floating peut être limité")

# Alternative : Scraping direct site Getaround
if st.button("🌐 Site Getaround 06 (Plan B)"):
    st.info("🔄 Scan page Alpes-Maritimes...")
    # À implémenter si GBFS vide
    st.code("https://fr.getaround.com/areas/alpes-maritimes")
