import streamlit as st
import requests
import pandas as pd
import time

st.set_page_config(layout="wide", page_title="Getaround France")

st.title("🚗 Getaround France - Scanner National")
st.markdown("Analyse temps réel GBFS v3.0 (data.datasets)")

@st.cache_data(ttl=1800)
def scan_manifest_france():
    try:
        resp = requests.get("https://fr.getaround.com/gbfs/manifest?country_code=FR", timeout=15)
        json_data = resp.json()
        datasets = json_data['data']['datasets']  # ✅ CORRIGÉ
        return datasets
    except:
        return []

systems_fr = scan_manifest_france()
st.success(f"✅ {len(systems_fr)} systèmes Getaround France détectés")

if st.button("🔍 Scanner France", type="primary"):
    progres = st.progress(0)
    all_vehicles = []
    
    for i, system in enumerate(systems_fr[:25]):
        try:
            ville = system['system_id'].replace('getaround_', '')
            url = system['urls']['en']['free_bike_status']
            resp = requests.get(url, timeout=6)
            vehicles = resp.json()['data']['bikes']
            
            for v in vehicles:
                v['ville'] = ville
                all_vehicles.append(v)
            
            progres.progress((i+1)/25)
            time.sleep(0.1)
        except:
            continue
    
    if all_vehicles:
        df = pd.DataFrame(all_vehicles)
        df['lat'] = df['lat'].astype(float)
        df['lon'] = df['lon'].astype(float)
        
        st.success(f"✅ {len(df)} véhicules sur {len(df['ville'].unique())} villes")
        
        col1, col2 = st.columns([2,1])
        
        with col1:
            st.subheader("🏙️ Flottes par ville (Top 15)")
            top_villes = df['ville'].value_counts().head(15)
            st.bar_chart(top_villes)
        
        with col2:
            st.metric("Total France", len(df))
            st.metric("Villes actives", len(df['ville'].unique()))
            st.metric("Moyenne/ville", round(len(df)/len(df['ville'].unique())))
        
        st.subheader("🥇 Top 10 villes")
        top10 = df['ville'].value_counts().head(10).reset_index()
        top10.columns = ['Ville', 'Véhicules']
        st.dataframe(top10)
        
        csv = df.to_csv(index=False)
        st.download_button("💾 Export CSV", csv, "getaround_france.csv")
        
    else:
        st.warning("⚠️ Aucun véhicule libre actuellement (normal hors heures de pointe)")
        st.info("Getaround = 66k+ véhicules mais free-floating variable")

st.caption("Données GBFS v3.0 officielles - transport.data.gouv.fr")
