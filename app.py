import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide", page_title="Citiz Dataviz")

st.title("🚗 Citiz France - DataViz Autopartage Associatif")
st.markdown("**Réseau 35+ villes - Analyse infrastructure**")

@st.cache_data(ttl=3600)
def load_citiz_data():
    # Données Citiz simulées (API down → fallback stable)
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
    df['taux_dispo'] = df['disponibles'] / df['vehicules'] * 100
    return df

df_citiz = load_citiz_data()
st.success(f"✅ {len(df_citiz)} villes Citiz analysées")

# 1. CARTE INTERACTIVE
st.subheader("🗺️ Carte Citiz France")
fig_map = px.scatter_mapbox(df_citiz, 
                          lat='lat', lon='lon',
                          size='vehicules',
                          color='taux_dispo',
                          size_max=25,
                          hover_name='ville',
                          hover_data=['stations', 'vehicules', 'disponibles'],
                          mapbox_style="open-street-map",
                          zoom=5,
                          height=500,
                          title="Taille = capacité, Couleur = taux dispo")
st.plotly_chart(fig_map, use_container_width=True)

# 2. METRICS KPI
col1, col2, col3, col4 = st.columns(4)
with col1: st.metric("Villes", len(df_citiz))
with col2: st.metric("Véhicules", f"{df_citiz['vehicules'].sum():,}")
with col3: st.metric("Disponibles", df_citiz['disponibles'].sum())
with col4: st.metric("Taux dispo", f"{df_citiz['taux_dispo'].mean():.1f}%")

# 3. GRAPHIQUES
col1, col2 = st.columns(2)
with col1:
    st.subheader("📊 Top 10 capacité")
    top_capacite = df_citiz.nlargest(10, 'vehicules')[['ville', 'vehicules']]
    fig_bar = px.bar(top_capacite, x='ville', y='vehicules', 
                    color='taux_dispo',
                    title="Véhicules par ville")
    st.plotly_chart(fig_bar, use_container_width=True)

with col2:
    st.subheader("🎯 Disponibilité")
    fig_scatter = px.scatter(df_citiz, x='vehicules', y='taux_dispo',
                           size='disponibles', color='bornes_ev',
                           hover_name='ville',
                           title="Capacité vs Taux dispo")
    st.plotly_chart(fig_scatter, use_container_width=True)

# 4. MATRICE DÉTAIL (SAFE COLUMNS)
st.subheader("📋 Analyse détaillée")
display_cols = ['ville', 'stations', 'vehicules', 'disponibles', 'taux_dispo', 'bornes_ev', 'lat', 'lon']
st.dataframe(df_citiz[display_cols].round(1).sort_values('vehicules', ascending=False), 
             use_container_width=True)

# 5. EXPORT FabMob
csv = df_citiz.to_csv(index=False)
st.download_button("💾 Export CSV (FabMob)", csv, "citiz_france.csv", "text/csv")

st.markdown("---")
st.caption("Citiz - Autopartage associatif français | Données synthétiques (API fallback)")

