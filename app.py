import streamlit as st
import requests
import pandas as pd
import time

st.set_page_config(layout="wide", page_title="Getaround France")

st.title("Getaround France - Scanner National")
st.markdown("Analyse temps reel de tous les systemes GBFS")

@st.cache_data(ttl=1800)
def scan_manifest_france():
    try:
        resp = requests.get("https://fr.getaround.com/gbfs/manifest?country_code=FR", timeout=15)
        data = resp.json()['data']['gbfs_feeds']
        return data
    except:
        return []

systems_fr = scan_manifest_france()
st.info(f"{len(systems_fr)} systemes Getaround France detectes")

if st.button("Scanner France", type="primary"):
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
        
        st.success(f"{len(df)} vehicules sur {len(df['ville'].unique())} villes")
        
        col1, col2 = st.columns([2,1])
        
        with col1:
            st.subheader("Flottes par ville")
            top_villes = df['ville'].value_counts().head(15)
            st.bar_chart(top_villes)
        
        with col2:
            total = len(df)
            villes_actives = len(df['ville'].unique())
            st.metric("Total France", total)
            st.metric("Villes actives", villes_actives)
            st.metric("Moyenne/ville", total//villes_actives)
        
        st.subheader("Top 10 villes")
        top10 = (df['ville'].value_counts()
                .head(10)
                .reset_index())
        top10.columns = ['Ville', 'Vehicules']
        st.dataframe(top10)
        
        csv = df.to_csv(index=False)
        st.download_button("Export CSV", csv, "getaround_france.csv")
        
    else:
        st.warning("Aucun vehicule actif")
        st.info("Flotte variable selon heure/jour")

st.markdown("Donnees GBFS officielles Getaround France")
