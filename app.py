import streamlit as st
import requests
import pandas as pd

st.set_page_config(layout="wide", page_title="Getaround France Debug")

st.title("Getaround France - Diagnostic Complet")
st.markdown("Analyse manifest + endpoints + solutions")

# 1. TEST MANIFEST
if st.button("1. Test Manifest FR", type="secondary"):
    try:
        resp = requests.get("https://fr.getaround.com/gbfs/manifest?country_code=FR", timeout=10)
        data = resp.json()['data']['gbfs_feeds']
        st.success(f"✅ Manifest OK: {len(data)} systèmes")
        
        # Top 10 systèmes
        top10 = pd.DataFrame(data[:10])[['system_id', 'url']]
        st.dataframe(top10)
        st.json({"total_systems": len(data)})
        
    except Exception as e:
        st.error(f"❌ Manifest erreur: {e}")

# 2. TEST VILLES CONNUES
villes_test = ["versailles", "yerres", "paris"]
if st.button("2. Test 3 villes connues", type="secondary"):
    for ville in villes_test:
        try:
            url = f"https://fr.getaround.com/gbfs/v3/{ville}/gbfs/free_bike_status.json"
            resp = requests.get(url, timeout=5)
            count = len(resp.json()['data']['bikes'])
            st.write(f"**{ville}**: {count} voitures")
        except:
            st.write(f"**{ville}**: ❌ indisponible")

# 3. SOLUTION : Manifest + system_info.json (stations)
if st.button("3. Scanner Stations France", type="primary"):
    st.info("🔄 Récupère les STATIONS Getaround (pas les voitures live)")
    
    try:
        resp = requests.get("https://fr.getaround.com/gbfs/manifest?country_code=FR")
        systems = resp.json()['data']['gbfs_feeds'][:15]
        
        stations = []
        for system in systems:
            try:
                ville = system['system_id'].replace('getaround_', '')
                station_url = system['urls']['en']['station_information']
                resp2 = requests.get(station_url)
                stat_data = resp2.json()['data']['stations']
                for s in stat_data:
                    s['ville'] = ville
                    stations.append(s)
            except:
                continue
        
        if stations:
            df_stations = pd.DataFrame(stations)
            st.success(f"✅ {len(df_stations)} STATIONS sur {len(df_stations['ville'].unique())} villes")
            st.dataframe(df_stations[['ville', 'name', 'lat', 'lon']].head(20))
            st.download_button("Export Stations", df_stations.to_csv(index=False), "getaround_stations.csv")
        else:
            st.warning("Aucune station trouvée")
            
    except Exception as e:
        st.error(f"Erreur scan: {e}")

st.markdown("---")
st.info("**Explication**: GBFS = voitures DISPONIBLES MAINTENANT seulement. Getaround = 60k+ véhicules mais pas tous free-floating 24/7")
st.caption("Dataset officiel: transport.data.gouv.fr/datasets/flotte-getaround-en-libre-service-france")

