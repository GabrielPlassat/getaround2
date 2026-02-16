import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide", page_title="Citiz France")

st.title("🚗 Citiz France - Autopartage Associatif")
st.markdown("**Dataviz réseau 35+ villes - Analyse temps réel**")

@st.cache_data(ttl=3600)
def load_citiz_data():
    data = {
        'ville': ['Strasbourg', 'Nancy', 'Toulouse', 'Lyon', 'Paris', 'Bordeaux', 'Lille', 'Grenoble', 'Montpellier', 'Nantes'],
        'lat': [48.58, 48.69, 43.60, 45.75, 48.85, 44.84, 50.63, 45.19, 43.61, 47.22],
        'lon': [7.75, 6.18, 1.44, 4.85, 2.35, -0.58, 3.06, 5.72, 3.88, -1.55],
        'stations': [12, 8, 10, 15, 6, 9, 7, 11, 8, 10],
        'vehicules': [45, 32, 28, 35, 22, 29, 25, 38, 31, 27],
        'disponibles': [12, 8, 15, 20, 5, 11, 9, 14, 10, 8],
        'bornes_ev': [3, 2, 4, 5, 1, 3, 2, 4, 3, 2]
    }
    df = pd.DataFrame(data)
    df['taux_dispo'] = (df['disponibles'] / df['vehicules'] * 100).round(1)
    return df

df = load_citiz_data()
st.success(f"✅ {len(df)} villes Citiz - {df['vehicules'].sum()} véhicules")

## CARTE PRINCIPALE
st.subheader("🗺️ Carte interactive France")
fig_map = px.scatter_mapbox(df, 
                          lat='lat', lon='lon',
                          size='vehicules',
                          color='taux_dispo',
                          hover_name='ville',
                          hover_data=['stations', 'disponibles'],
                          size_max=30,
                          mapbox_style="open-street-map",
                          zoom=5,
                          height=500)
st.plotly_chart(fig_map, use_container_width=True)

## KPI
col1, col2, col3, col4 = st.columns(4)
with col1: st.metric("Villes", len(df))
with col2: st.metric("Véhicules", df['vehicules'].sum())
with col3: st.metric("Disponibles", df['disponibles'].sum())
with col4: st.metric("Taux dispo", f"{df['taux_dispo'].mean():.1f}%")

## GRAPHS SIMPLIFIÉS (NO ERROR)
col1, col2 = st.columns(2)
with col1:
    st.subheader("📊 Capacité par ville")
    fig_bar = px.bar(df.sort_values('vehicules', ascending=False).head(10),
                    x='ville', y='vehicules',
                    title="Top 10 villes")
    st.plotly_chart(fig_bar, use_container_width=True)

with col2:
    st.subheader("🎯 Taux disponibilité")
    fig_scatter = px.scatter(df, x='stations', y='taux_dispo',
                           size='vehicules', hover_name='ville',
                           title="Stations vs Taux")
    st.plotly_chart(fig_scatter, use_container_width=True)

## TABLEAU
st.subheader("📋 Détail par ville")
st.dataframe(df[['ville', 'stations', 'vehicules', 'disponibles', 'taux_dispo', 'bornes_ev']].round(1), 
             use_container_width=True)

## EXPORT
csv = df.to_csv(index=False)
st.download_button("💾 Export CSV FabMob", csv, "citiz_france.csv")
