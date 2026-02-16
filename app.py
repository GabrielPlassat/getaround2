import streamlit as st
import requests
import pandas as pd
import time

st.set_page_config(layout="wide", page_title="Getaround France")

st.title("🚗 Getaround France - Scanner National")
st.markdown("**~400 systèmes GBFS** - Analyse temps réel")

@st.cache_data(ttl=1800)  # Cache 30min
def scan_manifest_france():
    try:
        resp = requests.get("https://fr.getaround.com/gbfs/manifest?country_code=FR", timeout=15)
        data = resp.json()['data']['gbfs_feeds']
        return data
    except:
        return []

# Manifest France
systems_fr = scan_manifest_france()
st.info(f"📡 **{len(systems_fr)} systèmes Getaround France** détectés")

if st.button("🔍 Scanner France Complète", type="primary"):
    progres = st.progress(0)
    all_vehicles = []
    
    for i, system in enumerate(systems_fr[:50]):  # Top 50 systèmes (évite timeout)
        try:
            ville = system['system_id'].replace('getaround_', '')
            url = system['urls']['en']['free_bike_status']
            resp = requests.get(url, timeout=8)
            vehicles = resp.json()['data']['bikes']
            
            for v in vehicles:
                v['ville'] = ville
                all_vehicles.append(v)
            
            progres.progress((i+1)/50)
            time.sleep(0.1)  # Rate limit
            
        except:
            continue
    
    if all_vehicles:
        df = pd.DataFrame(all_vehicles)
        df['lat'] = df['lat'].astype(float)
        df['lon'] = df['lon'].astype(float)
        
        st.success(f"✅ **{len(df)} véhicules** sur **{len(df['ville'].unique())} villes**")
        
        # Dashboard principal
        col1, col2 = st.columns([2,1])
        
        with col1:
            st.subheader("🏙️ Flottes par ville (Top 20)")
            top_villes = df['ville'].value_counts().head(20)
            st.bar_chart(top_villes)
            
            st.subheader("📍 Toutes les positions")
            st.dataframe(df[['ville','lat','lon','bike_id']].head(1000), height=300)
        
        with col2:
            st.metric("Total France", f"{len(df):,}")
            st.metric("Villes actives", len(df['ville'].unique()))
            st.metric("Véhicule moyen/ville", f"{len(df)/len(df['ville'].unique()):.0f}")
            st.metric("Lat moyenne", f"{df.lat.
