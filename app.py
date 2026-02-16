import streamlit as st
import requests
import pandas as pd

st.set_page_config(layout="wide", page_title="Getaround Stations")

st.title("🚗 Getaround France - Réseau Stations")
st.markdown("**3750 systèmes → Infrastructure complète**")

@st.cache_data(ttl=3600)
def get_stations_france():
    resp = requests.get("https://fr.getaround.com/gbfs/manifest?country_code=FR")
    json_data = resp.json()
    datasets = json_data['data']['datasets']
    
    stations = []
    for system in datasets[:50]:  # Top 50 systèmes
        try:
            ville = system['system_id'].replace('getaround_', '')
            station_url = system['urls']['en']['station_information']
            resp2 = requests.get(station_url, timeout=8)
            station_data = resp2.json()['data']['stations']
            
            for s in station_data:
                s['ville'] = ville
                stations.append(s)
        except:
            continue
    return pd.DataFrame(stations)

df_stations = get_stations_france()
st.success(f"✅ {len(df_stations)} STATIONS Getaround France")

if not df_stations.empty:
    df_stations['lat'] = df_stations['lat'].astype(float)
    df_stations['lon'] = df_stations['lon'].astype(float)
    
    col1, col2 = st.columns([2,1])
    
    with col1:
        st.subheader("🏙️ Stations par ville")
        top_villes = df_stations['ville'].value_counts().head(15)
        st.bar_chart(top_villes)
    
    with col2:
        st.metric("Stations total", len(df_stations))
        st.metric("Villes couvertes", df_stations['ville'].nunique())
        st.metric("Stations/ville", round(len(df_stations)/df_stations['ville'].nunique()))
    
    st.subheader("📍 Top 10 villes stations")
    top10 = (df_stations['ville'].value_counts()
            .head(10)
            .reset_index())
    top10.columns = ['Ville', 'Stations']
    st.dataframe(top10)
    
    st.dataframe(df_stations[['ville', 'name', 'lat', 'lon', 'capacity']].head(20))
    
    csv = df_stations.to_csv(index=False)
    st.download_button("💾 Export CSV Stations", csv, "getaround_stations_france.csv")
