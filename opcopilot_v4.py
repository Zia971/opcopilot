"""
OPCOPILOT v4.0 - Application Streamlit Complète
Gestion d'opérations immobilières pour ACO SPIC Guadeloupe
Utilise les données JSON des référentiels métier
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import json
from datetime import datetime, timedelta
import sqlite3
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import os

# ---- AUTHENTIFICATION MULTI-ACO ----
# Liste d'ACO démo (login/mdp)
DEMO_ACO_USERS = {
    "aco1": "password1",
    "aco2": "password2",
    "aco3": "password3"
}

def login_form():
    st.markdown(
        """
        <div style="background-color:#23272F; padding:2em; border-radius:10px; box-shadow:0 0 10px #111;">
            <h2 style="color:#E1E1E1;">Authentification ACO</h2>
        </div>
        """, unsafe_allow_html=True
    )
    login = st.text_input("Identifiant ACO", key="login_input")
    pwd = st.text_input("Mot de passe", type="password", key="pwd_input")
    login_btn = st.button("Se connecter", key="login_btn")
    if login_btn:
        if login in DEMO_ACO_USERS and DEMO_ACO_USERS[login] == pwd:
            st.session_state["authenticated"] = True
            st.session_state["aco_user"] = login
            st.rerun()
        else:
            st.error("Identifiant ou mot de passe incorrect.")

def logout():
    if st.button("Se déconnecter", key="logout_btn"):
        st.session_state["authenticated"] = False
        st.session_state["aco_user"] = None
        st.rerun()

# Initialisation de l'état de session
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
    st.session_state["aco_user"] = None

if not st.session_state["authenticated"]:
    st.markdown(
        """
        <style>
        /* Centrage vertical et fond sombre */
        .block-container { display: flex; align-items: center; justify-content: center; height: 100vh; background: #181C22; }
        </style>
        """, unsafe_allow_html=True
    )
    login_form()
    st.stop()
else:
    # Affiche le bouton de déconnexion dans la barre latérale
    with st.sidebar:
        st.markdown(f"**ACO connecté :** {st.session_state['aco_user']}", unsafe_allow_html=True)
        logout()

# Configuration page
st.set_page_config(
    page_title="OPCOPILOT v4.0 - SPIC Guadeloupe",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé pour interface moderne
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
<style>
    html, body, .main, .block-container {
        background: #F9FAFB !important;
        font-family: 'Inter', sans-serif !important;
        color: #222;
    }
    .main-header {
        background: none;
        color: #1e293b;
        padding: 0.5rem 0 2rem 0;
        border-radius: 0;
        margin-bottom: 2rem;
        text-align: left;
        font-size: 2.4rem;
        font-weight: 700;
        letter-spacing: -1px;
    }
    .sidebar-content, .css-1d391kg, .css-1lcbmhc, .css-1v0mbdj {
        background: #F8FAFC !important;
        border-radius: 0 24px 24px 0;
        box-shadow: 2px 0 12px #e5e7eb44;
    }
    .lucide-icon {
        width: 1.3em;
        height: 1.3em;
        vertical-align: middle;
        margin-right: 0.6em;
        stroke-width: 2.2;
    }
    .kpi-card {
        background: #fff;
        border-radius: 14px;
        box-shadow: 0 2px 12px #e5e7eb44;
        padding: 2rem 1.5rem;
        text-align: center;
        margin: 0.5rem;
        transition: transform .15s, box-shadow .15s;
        cursor: pointer;
        border: none;
        font-weight: 600;
    }
    .kpi-card:hover {
        transform: scale(1.025);
        box-shadow: 0 4px 24px #60a5fa33;
        background: #f3f8ff;
    }
    .kpi-blue { color: #3B82F6; }
    .kpi-green { color: #10B981; }
    .kpi-orange { color: #F59E0B; }
    .kpi-red { color: #EF4444; }
    .status-dot {
        display: inline-block;
        width: 0.7em;
        height: 0.7em;
        border-radius: 50%;
        margin-right: 0.5em;
    }
    .status-vert { background: #10B981; }
    .status-orange { background: #F59E0B; }
    .status-rouge { background: #EF4444; }
    .sidebar-btn {
        background: #fff;
        border-radius: 8px;
        padding: 0.7em 1em;
        margin: 0.4em 0;
        font-weight: 500;
        border: none;
        transition: background .15s, box-shadow .15s, transform .13s;
        box-shadow: 0 1px 4px #e5e7eb33;
        display: flex;
        align-items: center;
        font-size: 1.05em;
        color: #222;
        cursor: pointer;
    }
    .sidebar-btn:hover {
        background: #F3F8FF;
        transform: scale(1.03);
        color: #3B82F6;
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 1. CONFIGURATION & CHARGEMENT DONNÉES
# ==============================================================================

@st.cache_data
def load_demo_data():
    """Charge demo_data.json avec gestion d'erreur"""
    try:
        with open('data/demo_data.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        st.error("❌ Fichier data/demo_data.json non trouvé")
        return {}
    except json.JSONDecodeError:
        st.error("❌ Erreur format JSON dans demo_data.json")
        return {}

@st.cache_data
def load_templates_phases():
    """Charge templates_phases.json avec gestion d'erreur"""
    try:
        with open('data/templates_phases.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        st.error("❌ Fichier data/templates_phases.json non trouvé")
        return {}
    except json.JSONDecodeError:
        st.error("❌ Erreur format JSON dans templates_phases.json")
        return {}

def get_couleur_statut(statut):
    """Retourne la couleur selon le statut de phase"""
    couleurs = {
        "VALIDEE": "#4CAF50",         # Vert
        "EN_COURS": "#2196F3",        # Bleu
        "EN_ATTENTE": "#FFC107",      # Jaune
        "RETARD": "#F44336",          # Rouge
        "CRITIQUE": "#E91E63",        # Rose
        "NON_DEMARREE": "#9E9E9E",    # Gris
        "VALIDATION_REQUISE": "#FF9800",  # Orange
        "EN_REVISION": "#673AB7"      # Violet
    }
    return couleurs.get(statut, "#0066cc")

# ==============================================================================
# 2. TIMELINE HORIZONTALE OBLIGATOIRE
# ==============================================================================

def create_timeline_horizontal(operation_data, phases_data):
    """
    Timeline Plotly style INFOGRAPHIQUE MODERNE avec gestion d'erreur robuste
    Reproduit le style roadmap professionnel avec validation complète des données
    """
    
    def create_empty_timeline():
        """Timeline vide en cas de données manquantes"""
        fig = go.Figure()
        fig.add_annotation(
            text="Aucune phase disponible pour cette opération",
            xref="paper", yref="paper",
            x=0.5, y=0.5, 
            showarrow=False,
            font=dict(size=16, color="#666666")
        )
        fig.update_layout(
            title="Timeline - Aucune donnée",
            height=300,
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            plot_bgcolor='white',
            paper_bgcolor='white'
        )
        return fig, {}
    
    def create_fallback_timeline(error_msg=""):
        """Timeline de fallback en cas d'erreur"""
        fig = go.Figure()
        fig.add_annotation(
            text=f"Erreur lors de la génération de la timeline\n{error_msg}",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=14, color="#d32f2f")
        )
        fig.update_layout(
            title="Timeline - Erreur de chargement",
            height=300,
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            plot_bgcolor='white',
            paper_bgcolor='white'
        )
        return fig, {}
    
    try:
        # VALIDATION DONNÉES D'ENTRÉE
        if not operation_data:
            st.warning("⚠️ Données d'opération manquantes")
            return create_empty_timeline()
        
        if not phases_data or len(phases_data) == 0:
            st.info("ℹ️ Aucune phase définie pour cette opération")
            return create_empty_timeline()
        
        # Validation que phases_data est une liste
        if not isinstance(phases_data, list):
            st.error("❌ Format de données phases incorrect")
            return create_fallback_timeline("Format phases_data incorrect")
        
        # PRÉPARATION DONNÉES SÉCURISÉE
        fig = go.Figure()
        
        # Validation et préparation des dates
        dates_debut = []
        dates_fin = []
        phases_valides = []
        
        for i, phase in enumerate(phases_data):
            try:
                # Vérification que phase est un dict
                if not isinstance(phase, dict):
                    continue
                
                # Gestion sécurisée des dates
                date_debut_str = phase.get('date_debut_prevue')
                date_fin_str = phase.get('date_fin_prevue')
                
                # Dates par défaut si manquantes
                if not date_debut_str:
                    debut = datetime.now() + timedelta(days=i*30)
                else:
                    debut = pd.to_datetime(date_debut_str)
                
                if not date_fin_str:
                    fin = debut + timedelta(days=30)
                else:
                    fin = pd.to_datetime(date_fin_str)
                
                # Validation cohérence dates
                if fin < debut:
                    fin = debut + timedelta(days=30)
                
                dates_debut.append(debut)
                dates_fin.append(fin)
                phases_valides.append(phase)
                
            except Exception as e:
                # Log de l'erreur mais continue avec les autres phases
                st.warning(f"⚠️ Erreur phase {i+1}: {str(e)}")
                continue
        
        # Vérification qu'on a au moins une phase valide
        if not phases_valides:
            st.error("❌ Aucune phase valide trouvée")
            return create_fallback_timeline("Aucune phase valide")
        
        # Calcul des bornes temporelles
        date_min = min(dates_debut)
        date_max = max(dates_fin)
        
        # BARRE HORIZONTALE AVEC ESPACEMENT ÉGAL - Timeline chronologique
        if len(phases_valides) > 1:
            # Positions équidistantes (chronologie simple, pas durées)
            x_positions = list(range(len(phases_valides)))
            
            # Couleurs du dégradé (jaune → orange → rouge → violet → bleu)
            couleurs_degrade = [
                "#FFD54F",  # Jaune
                "#FF9800",  # Orange  
                "#F44336",  # Rouge
                "#E91E63",  # Rose/Violet
                "#673AB7",  # Violet
                "#2E7D32"   # Bleu-vert foncé
            ]
            
            # Segments de la barre avec espacement égal
            for i in range(len(phases_valides) - 1):
                debut = x_positions[i]
                fin = x_positions[i + 1]
                
                # Couleur du segment
                couleur_segment = couleurs_degrade[i % len(couleurs_degrade)]
                
                # Segment de barre coloré
                fig.add_trace(go.Scatter(
                    x=[debut, fin],
                    y=[0, 0],
                    mode='lines',
                    line=dict(width=20, color=couleur_segment),
                    showlegend=False,
                    hoverinfo='skip'
                ))
                
                # Triangle/flèche sur la barre (style modèle)
                milieu_segment = debut + (fin - debut) / 2
                y_triangle = 0.15 if i % 2 == 0 else -0.15
                fig.add_trace(go.Scatter(
                    x=[milieu_segment],
                    y=[y_triangle],
                    mode='markers',
                    marker=dict(
                        size=15,
                        color=couleur_segment,
                        symbol='triangle-up' if i % 2 == 0 else 'triangle-down'
                    ),
                    showlegend=False,
                    hoverinfo='skip'
                ))
        
        # CERCLES AVEC DATES MM/YY - Espacement chronologique égal
        for i, phase in enumerate(phases_valides):
            try:
                debut_date = dates_debut[i]  # Date réelle pour format MM/YY
                x_pos = i  # Position équidistante (chronologique)
                statut = phase.get('statut', 'NON_DEMARREE')
                nom_phase = phase.get('nom', f'Phase {i+1}')
                
                # Couleur assortie au dégradé
                couleurs_cercles = [
                    "#FFD54F", "#FF9800", "#F44336", 
                    "#E91E63", "#673AB7", "#2E7D32"
                ]
                couleur = couleurs_cercles[i % len(couleurs_cercles)]
                
                # Position alternée (PRÉSERVER espacement qui fonctionne)
                est_en_haut = i % 2 == 0
                y_cercle = 0.8 if est_en_haut else -0.8
                y_ligne_debut = 0.15 if est_en_haut else -0.15
                
                # LIGNE VERTICALE DE CONNEXION (PRÉSERVÉE)
                fig.add_trace(go.Scatter(
                    x=[x_pos, x_pos],
                    y=[y_ligne_debut, y_cercle - (0.25 if est_en_haut else -0.25)],
                    mode='lines',
                    line=dict(width=3, color=couleur),
                    showlegend=False,
                    hoverinfo='skip'
                ))
                
                # FORMAT DATE MM/YY pour cercle
                date_formatted = debut_date.strftime('%m/%y')  # Format 07/25, 01/26, etc.
                
                # CERCLE PRINCIPAL avec DATE INTÉGRÉE
                fig.add_trace(go.Scatter(
                    x=[x_pos],
                    y=[y_cercle],
                    mode='markers+text',
                    marker=dict(
                        size=80,  # Gros pour date complète
                        color=couleur,
                        symbol='circle',
                        line=dict(width=5, color='white')
                    ),
                    text=[date_formatted],  # DATE MM/YY dans cercle
                    textfont=dict(size=16, color='white', family='Arial Bold'),
                    textposition='middle center',
                    showlegend=False,
                    hovertemplate=f"<b>Phase {i+1}</b><br>{nom_phase}<br>Date: {debut_date.strftime('%d/%m/%Y')}<extra></extra>"
                ))
                
                # TITRE ET DESCRIPTION (ESPACEMENT PRÉSERVÉ)
                # Afficher nom complet (non tronqué)
                nom_complet = nom_phase  # Texte complet
                
                # Titre principal (position préservée)
                y_titre = y_cercle + (0.4 if est_en_haut else -0.4)
                fig.add_trace(go.Scatter(
                    x=[x_pos],
                    y=[y_titre],
                    mode='text',
                    text=[f"<b>PHASE {i+1:02d}</b>"],
                    textfont=dict(size=15, color='#333333', family='Arial Black'),
                    textposition='middle center',
                    showlegend=False,
                    hoverinfo='skip'
                ))
                
                # Description complète (espacement préservé, texte complet)
                y_desc = y_cercle + (0.6 if est_en_haut else -0.6)
                fig.add_trace(go.Scatter(
                    x=[x_pos],
                    y=[y_desc],
                    mode='text',
                    text=[f"{nom_complet}<br><span style='color:#999999;font-size:10px'>Statut: {statut}</span>"],
                    textfont=dict(size=12, color='#666666', family='Arial'),
                    textposition='middle center',
                    showlegend=False,
                    hoverinfo='skip'
                ))
                    
            except Exception as e:
                st.warning(f"⚠️ Erreur phase {i+1}: {str(e)}")
                continue
        
        # LAYOUT TIMELINE CHRONOLOGIQUE (espacement égal, pas durées)
        operation_nom = operation_data.get('nom', 'Opération') if isinstance(operation_data, dict) else 'Opération'
        
        fig.update_layout(
            title={
                'text': f"🗓️ Timeline Interactive - {operation_nom}",
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 22, 'color': '#333333', 'family': 'Arial Black'}
            },
            # Fond gris clair comme modèle
            plot_bgcolor='rgba(240, 240, 240, 0.3)',
            paper_bgcolor='#f5f5f5',
            
            # SUPPRESSION COMPLÈTE AXE X (chronologie dans cercles)
            xaxis=dict(
                range=[-0.5, len(phases_valides) - 0.5],  # Range pour espacement égal
                visible=False,        # Complètement invisible
                showticklabels=False,
                showgrid=False,
                zeroline=False,
                showline=False
            ),
            # AXE Y masqué mais fonctionnel pour alternance
            yaxis=dict(
                range=[-1.8, 1.8],    # Range préservée pour alternance
                visible=False,        # Invisible
                showgrid=False,
                showticklabels=False,
                zeroline=False,
                showline=False
            ),
            height=600,  # Hauteur préservée
            margin=dict(l=50, r=50, t=100, b=50),
            hovermode='closest',
            dragmode='pan',
            font=dict(size=12, color='#333333', family='Arial'),
            showlegend=False
        )
        
        # Configuration outils
        config = {
            'displayModeBar': True,
            'modeBarButtonsToAdd': ['pan2d', 'zoomin2d', 'zoomout2d', 'resetScale2d'],
            'modeBarButtonsToRemove': ['lasso2d', 'select2d', 'autoScale2d'],
            'displaylogo': False,
            'toImageButtonOptions': {
                'format': 'png',
                'filename': f"timeline_{operation_nom.replace(' ', '_')}",
                'height': 500,
                'width': 1200,
                'scale': 2
            }
        }
        
        return fig, config
        
    except Exception as e:
        # Gestion d'erreur globale
        error_msg = str(e)
        st.error(f"❌ Erreur critique timeline: {error_msg}")
        return create_fallback_timeline(error_msg)

# ==============================================================================
# 3. MODULES INTÉGRÉS PAR OPÉRATION
# ==============================================================================

def module_rem(operation_id):
    """Module REM intégré dans l'opération"""
    st.markdown("### 💰 Module REM - Suivi Trimestriel")
    
    # Chargement données REM
    demo_data = load_demo_data()
    rem_data = demo_data.get('rem_demo', {}).get(f'operation_{operation_id}', [])
    
    if not rem_data:
        st.warning("Aucune donnée REM disponible pour cette opération")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📊 Suivi REM")
        
        # Tableau REM
        df_rem = pd.DataFrame(rem_data)
        df_rem_display = df_rem[['trimestre', 'rem_projetee', 'rem_realisee', 'ecart_rem', 'avancement_rem']].copy()
        df_rem_display.columns = ['Trimestre', 'REM Projetée (€)', 'REM Réalisée (€)', 'Écart (€)', '% Avancement']
        
        st.dataframe(df_rem_display, use_container_width=True)
        
        # Graphique REM
        fig_rem = go.Figure()
        fig_rem.add_trace(go.Bar(
            x=df_rem['trimestre'],
            y=df_rem['rem_projetee'],
            name='REM Projetée',
            marker_color='#0066cc'
        ))
        fig_rem.add_trace(go.Bar(
            x=df_rem['trimestre'],
            y=df_rem['rem_realisee'],
            name='REM Réalisée',
            marker_color='#ff6b35'
        ))
        fig_rem.update_layout(
            title="Évolution REM par Trimestre",
            barmode='group',
            height=400
        )
        st.plotly_chart(fig_rem, use_container_width=True)
    
    with col2:
        st.markdown("#### 🏗️ Suivi Dépenses Travaux")
        
        # Tableau Travaux
        df_travaux_display = df_rem[['trimestre', 'depenses_projetees', 'depenses_facturees', 'ecart_depenses', 'avancement_travaux']].copy()
        df_travaux_display.columns = ['Trimestre', 'Dépenses Projetées (€)', 'Dépenses Facturées (€)', 'Écart (€)', '% Avancement']
        
        st.dataframe(df_travaux_display, use_container_width=True)
        
        # Graphique Travaux
        fig_travaux = go.Figure()
        fig_travaux.add_trace(go.Bar(
            x=df_rem['trimestre'],
            y=df_rem['depenses_projetees'],
            name='Dépenses Projetées',
            marker_color='#4CAF50'
        ))
        fig_travaux.add_trace(go.Bar(
            x=df_rem['trimestre'],
            y=df_rem['depenses_facturees'],
            name='Dépenses Facturées',
            marker_color='#FFC107'
        ))
        fig_travaux.update_layout(
            title="Évolution Dépenses par Trimestre",
            barmode='group',
            height=400
        )
        st.plotly_chart(fig_travaux, use_container_width=True)
    
    # Alertes et analyses
    st.markdown("#### 🚨 Alertes et Analyses")
    
    col_alert1, col_alert2, col_alert3 = st.columns(3)
    
    # Calcul des alertes
    ecarts_rem = [abs(x['ecart_rem']) for x in rem_data if x['ecart_rem'] != 0]
    ecart_moyen = sum(ecarts_rem) / len(ecarts_rem) if ecarts_rem else 0
    
    with col_alert1:
        if ecart_moyen < 2000:
            st.markdown("""
            <div class="alert-info">
            ✅ <strong>Corrélation REM/Travaux</strong><br>
            Cohérence globale respectée<br>
            Écart moyen: {:.0f}€
            </div>
            """.format(ecart_moyen), unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="alert-warning">
            ⚠️ <strong>Écart détecté</strong><br>
            Surveillance requise<br>
            Écart moyen: {:.0f}€
            </div>
            """.format(ecart_moyen), unsafe_allow_html=True)
    
    with col_alert2:
        derniere_donnee = rem_data[-2] if len(rem_data) > 1 else rem_data[0]
        if derniere_donnee['avancement_rem'] < 95:
            st.markdown("""
            <div class="alert-warning">
            ⚠️ <strong>Retard REM</strong><br>
            {}% réalisé seulement
            </div>
            """.format(derniere_donnee['avancement_rem']), unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="alert-info">
            ✅ <strong>REM dans les temps</strong><br>
            {}% réalisé
            </div>
            """.format(derniere_donnee['avancement_rem']), unsafe_allow_html=True)
    
    with col_alert3:
        st.markdown("""
        <div class="alert-info">
        📈 <strong>Prévision T4</strong><br>
        Objectif: 95% avancement<br>
        Action: Validation finale
        </div>
        """, unsafe_allow_html=True)

def module_avenants(operation_id):
    """Module Avenants intégré dans l'opération"""
    st.markdown("### 📝 Module Avenants")
    
    # Chargement données avenants
    demo_data = load_demo_data()
    avenants_data = demo_data.get('avenants_demo', {}).get(f'operation_{operation_id}', [])
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("#### Liste des Avenants")
        
        if avenants_data:
            df_avenants = pd.DataFrame(avenants_data)
            df_avenants_display = df_avenants[['numero', 'date', 'motif', 'impact_budget', 'impact_delai', 'statut']].copy()
            df_avenants_display.columns = ['N°', 'Date', 'Motif', 'Impact Budget (€)', 'Impact Délai (j)', 'Statut']
            
            st.dataframe(df_avenants_display, use_container_width=True)
            
            # Synthèse impacts
            impact_budget_total = sum([x['impact_budget'] for x in avenants_data])
            impact_delai_total = sum([x['impact_delai'] for x in avenants_data])
            
            col_synth1, col_synth2, col_synth3 = st.columns(3)
            
            with col_synth1:
                delta_budget = f"+{impact_budget_total:,}€" if impact_budget_total > 0 else f"{impact_budget_total:,}€"
                st.metric("Impact Budget Total", delta_budget, delta=f"{impact_budget_total/25000*100:.1f}%")
            
            with col_synth2:
                delta_delai = f"+{impact_delai_total} jours" if impact_delai_total > 0 else f"{impact_delai_total} jours"
                st.metric("Impact Délai Total", delta_delai, delta=f"{impact_delai_total/550*100:.1f}%")
            
            with col_synth3:
                st.metric("Nombre Avenants", len(avenants_data), delta="+1")
        else:
            st.info("Aucun avenant pour cette opération")
    
    with col2:
        st.markdown("#### Nouvel Avenant")
        
        with st.form("nouvel_avenant"):
            motif = st.selectbox("Motif", [
                "Modification programme",
                "Délai supplémentaire", 
                "Plus-value travaux",
                "Moins-value travaux",
                "Changement MOE",
                "Adaptation réglementaire",
                "Autre"
            ])
            
            impact_budget = st.number_input("Impact Budget (€)", value=0, step=1000)
            impact_delai = st.number_input("Impact Délai (jours)", value=0)
            description = st.text_area("Description détaillée", placeholder="Détaillez les modifications...")
            
            submitted = st.form_submit_button("📝 Créer Avenant")
            if submitted:
                st.success("✅ Avenant créé en brouillon")
                st.info("📧 Notification envoyée pour validation hiérarchique")

def module_med(operation_id):
    """Module MED Automatisé intégré dans l'opération"""
    st.markdown("### ⚖️ Module MED Automatisé")
    
    # Chargement données MED
    demo_data = load_demo_data()
    med_data = demo_data.get('med_demo', {}).get(f'operation_{operation_id}', [])
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("#### Générer MED")
        
        with st.form("generation_med"):
            type_med = st.selectbox("Type MED", [
                "MED_MOE (Maîtrise d'Œuvre)",
                "MED_SPS (Sécurité Protection Santé)",
                "MED_OPC (Ordonnancement Pilotage)",
                "MED_ENTREPRISE (par lot)",
                "MED_CT (Contrôleur Technique)"
            ])
            
            destinataire = st.text_input("Destinataire", placeholder="Nom de l'entreprise/bureau d'études")
            
            motifs = st.multiselect("Motifs", [
                "Retard dans les études",
                "Non-respect du planning",
                "Défaut de coordination",
                "Non-conformité technique",
                "Absence sur chantier",
                "Documents manquants",
                "Malfaçons constatées",
                "Non-respect des règles de sécurité"
            ])
            
            delai_conformite = st.number_input("Délai mise en conformité (jours)", min_value=1, value=15, max_value=60)
            
            details = st.text_area("Détails spécifiques", placeholder="Précisez les éléments de non-conformité...")
            
            submitted = st.form_submit_button("📄 Générer MED Automatique")
            if submitted and motifs and destinataire:
                st.success("✅ MED généré automatiquement")
                st.info("📧 Document Word créé et envoyé par email")
                st.info("📅 Relances programmées automatiquement")
    
    with col2:
        st.markdown("#### Suivi MED Actives")
        
        if med_data:
            df_med = pd.DataFrame(med_data)
            df_med_display = df_med[['reference', 'destinataire', 'date_envoi', 'delai_conformite', 'statut']].copy()
            df_med_display.columns = ['Référence', 'Destinataire', 'Date Envoi', 'Délai (j)', 'Statut']
            
            st.dataframe(df_med_display, use_container_width=True)
            
            # Actions rapides
            st.markdown("#### Actions Rapides")
            
            col_action1, col_action2 = st.columns(2)
            
            with col_action1:
                if st.button("🔄 Relancer MED en attente"):
                    st.success("📧 Relance automatique envoyée")
            
            with col_action2:
                if st.button("📊 Rapport MED mensuel"):
                    st.info("📋 Génération rapport en cours...")
        else:
            st.info("Aucune MED active pour cette opération")
            
            # Suggestions
            st.markdown("#### 💡 Suggestions")
            st.markdown("""
            - Vérifiez les retards de planning
            - Contrôlez la qualité des livrables
            - Surveillez le respect des délais
            """)

def module_concessionnaires(operation_id):
    """Module Concessionnaires intégré dans l'opération"""
    st.markdown("### 🔌 Module Concessionnaires")
    
    # Chargement données concessionnaires
    demo_data = load_demo_data()
    concess_data = demo_data.get('concessionnaires_demo', {}).get(f'operation_{operation_id}', {})
    
    if not concess_data:
        st.warning("Aucune donnée concessionnaire pour cette opération")
        return
    
    # Onglets par concessionnaire
    tab_edf, tab_eau, tab_fibre = st.tabs(["⚡ EDF", "💧 EAU", "🌐 FIBRE"])
    
    with tab_edf:
        st.markdown("#### Processus EDF - Raccordement Électrique")
        
        edf_data = concess_data.get('EDF', {})
        edf_etapes = edf_data.get('etapes', [])
        
        for etape in edf_etapes:
            col_etape, col_statut, col_date = st.columns([3, 1, 1])
            
            with col_etape:
                st.write(f"🔸 {etape['nom']}")
            
            with col_statut:
                if etape['statut'] == 'VALIDEE':
                    st.success("✅ Validé")
                elif etape['statut'] == 'EN_COURS':
                    st.info("🔄 En cours")
                elif etape['statut'] == 'PLANIFIE':
                    st.warning("📅 Planifié")
                else:
                    st.info("⏳ En attente")
            
            with col_date:
                st.write(etape.get('date', 'À programmer'))
        
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("📞 Relancer EDF", key="relance_edf"):
                st.success("📧 Relance EDF programmée")
        with col_btn2:
            if st.button("📋 Rapport EDF", key="rapport_edf"):
                st.info("📊 Génération rapport EDF...")
    
    with tab_eau:
        st.markdown("#### Processus EAU - Branchement")
        
        eau_data = concess_data.get('EAU', {})
        eau_etapes = eau_data.get('etapes', [])
        
        for etape in eau_etapes:
            col_etape, col_statut, col_date = st.columns([3, 1, 1])
            
            with col_etape:
                st.write(f"🔸 {etape['nom']}")
            
            with col_statut:
                if etape['statut'] == 'VALIDEE':
                    st.success("✅ Validé")
                elif etape['statut'] == 'EN_COURS':
                    st.info("🔄 En cours")
                elif etape['statut'] == 'PLANIFIE':
                    st.warning("📅 Planifié")
                else:
                    st.info("⏳ En attente")
            
            with col_date:
                st.write(etape.get('date', 'À programmer'))
        
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("📞 Relancer Compagnie Eau", key="relance_eau"):
                st.success("📧 Relance programmée")
        with col_btn2:
            if st.button("📋 Rapport Eau", key="rapport_eau"):
                st.info("📊 Génération rapport...")
    
    with tab_fibre:
        st.markdown("#### Processus FIBRE - Installation")
        
        fibre_data = concess_data.get('FIBRE', {})
        fibre_etapes = fibre_data.get('etapes', [])
        
        for etape in fibre_etapes:
            col_etape, col_statut, col_date = st.columns([3, 1, 1])
            
            with col_etape:
                st.write(f"🔸 {etape['nom']}")
            
            with col_statut:
                if etape['statut'] == 'VALIDEE':
                    st.success("✅ Validé")
                elif etape['statut'] == 'EN_COURS':
                    st.info("🔄 En cours")
                elif etape['statut'] == 'PLANIFIE':
                    st.warning("📅 Planifié")
                else:
                    st.info("⏳ En attente")
            
            with col_date:
                st.write(etape.get('date', 'À programmer'))
        
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("📞 Relancer Opérateur", key="relance_fibre"):
                st.success("📧 Relance programmée")
        with col_btn2:
            if st.button("📋 Rapport Fibre", key="rapport_fibre"):
                st.info("📊 Génération rapport...")

def module_dgd(operation_id):
    """Module DGD intégré dans l'opération"""
    st.markdown("### 📊 Module DGD - Décompte Général Définitif")
    
    # Chargement données DGD
    demo_data = load_demo_data()
    dgd_data = demo_data.get('dgd_demo', {}).get(f'operation_{operation_id}', {})
    
    if not dgd_data:
        st.info("Module DGD non applicable pour cette opération (phase travaux non atteinte)")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Décompte par Lot")
        
        lots_data = dgd_data.get('lots', [])
        if lots_data:
            df_dgd = pd.DataFrame(lots_data)
            df_dgd_display = df_dgd[['nom', 'marche_initial', 'quantites_reelles', 'plus_moins_value', 'penalites', 'montant_final']].copy()
            df_dgd_display.columns = ['Lot', 'Marché Initial (€)', 'Qtés Réelles (%)', 'Plus/Moins-Value (€)', 'Pénalités (€)', 'Montant Final (€)']
            
            st.dataframe(df_dgd_display, use_container_width=True)
    
    with col2:
        st.markdown("#### Workflow Validation")
        
        workflow_steps = [
            {"nom": "Saisie quantités", "responsable": "ACO", "statut": "✅"},
            {"nom": "Validation entreprise", "responsable": "Entreprise", "statut": "✅"},
            {"nom": "Vérification MOE", "responsable": "MOE", "statut": "🔄"},
            {"nom": "Validation SPIC", "responsable": "SPIC", "statut": "⏳"},
            {"nom": "Génération décompte", "responsable": "Système", "statut": "⏳"}
        ]
        
        for step in workflow_steps:
            st.write(f"{step['statut']} **{step['nom']}** - {step['responsable']}")
    
    # Synthèse financière
    st.markdown("#### 💰 Synthèse Financière")
    
    synthese = dgd_data.get('synthese', {})
    if synthese:
        col_synth1, col_synth2, col_synth3, col_synth4 = st.columns(4)
        
        with col_synth1:
            st.metric("Montant Initial", f"{synthese['montant_initial']:,} €")
        
        with col_synth2:
            delta_pv = synthese['plus_moins_values']
            st.metric("Plus/Moins-Values", f"{delta_pv:,} €", delta=f"{delta_pv/synthese['montant_initial']*100:.1f}%")
        
        with col_synth3:
            st.metric("Pénalités", f"{synthese['penalites']:,} €")
        
        with col_synth4:
            montant_final = synthese['montant_final']
            ecart_pct = synthese['ecart_pourcentage']
            st.metric("Montant Final", f"{montant_final:,} €", delta=f"{ecart_pct:.1f}%")

def module_gpa(operation_id):
    """Module GPA intégré dans l'opération"""
    st.markdown("### 🛡️ Module GPA - Garantie Parfait Achèvement")
    
    # Chargement données GPA
    demo_data = load_demo_data()
    gpa_data = demo_data.get('gpa_demo', {}).get(f'operation_{operation_id}', [])
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Réclamations Locataires")
        
        if gpa_data:
            df_gpa = pd.DataFrame(gpa_data)
            df_gpa_display = df_gpa[['date', 'logement', 'type', 'description', 'statut', 'delai_intervention']].copy()
            df_gpa_display.columns = ['Date', 'Logement', 'Type', 'Description', 'Statut', 'Délai (j)']
            
            st.dataframe(df_gpa_display, use_container_width=True)
        else:
            st.info("Aucune réclamation GPA pour cette opération")
    
    with col2:
        st.markdown("#### Statistiques")
        
        if gpa_data:
            # Répartition par type
            types_count = {}
            for reclamation in gpa_data:
                type_pb = reclamation['type']
                types_count[type_pb] = types_count.get(type_pb, 0) + 1
            
            if types_count:
                fig_gpa = px.pie(
                    values=list(types_count.values()), 
                    names=list(types_count.keys()),
                    title="Répartition Réclamations par Type"
                )
                st.plotly_chart(fig_gpa, use_container_width=True)
        else:
            st.success("🎉 Aucune réclamation GPA - Excellente qualité!")
    
    # Nouvelle réclamation
    st.markdown("#### 📝 Nouvelle Réclamation GPA")
    
    with st.form("nouvelle_reclamation_gpa"):
        col_rec1, col_rec2, col_rec3 = st.columns(3)
        
        with col_rec1:
            logement = st.text_input("N° Logement", placeholder="Ex: A101")
            type_pb = st.selectbox("Type Problème", [
                "Plomberie", 
                "Électricité", 
                "Peinture", 
                "Menuiserie",
                "Carrelage",
                "Ventilation",
                "Autre"
            ])
        
        with col_rec2:
            locataire = st.text_input("Locataire", placeholder="Nom du locataire")
            urgence = st.selectbox("Niveau Urgence", [
                "Normale", 
                "Prioritaire", 
                "Urgente"
            ])
        
        with col_rec3:
            description = st.text_area("Description Problème", placeholder="Décrivez le problème...")
        
        submitted = st.form_submit_button("📨 Enregistrer Réclamation")
        if submitted and logement and locataire and description:
            st.success("✅ Réclamation enregistrée")
            st.info("📧 Transmission automatique à l'ACO")
            st.info("🔄 Entreprise notifiée selon le type de problème")

def module_cloture(operation_id):
    """Module Clôture intégré dans l'opération"""
    st.markdown("### ✅ Module Clôture - Finalisation Opération")
    
    # Checklist de clôture
    st.markdown("#### 📋 Checklist de Clôture")
    
    checklist_items = [
        {"item": "Toutes phases validées", "statut": True, "responsable": "ACO"},
        {"item": "Documents archivés", "statut": True, "responsable": "ACO"},
        {"item": "Soldes financiers validés", "statut": False, "responsable": "Financier"},
        {"item": "Retenue de garantie levée", "statut": False, "responsable": "Financier"},
        {"item": "Bilan opération rédigé", "statut": False, "responsable": "ACO"},
        {"item": "Lessons learned documentées", "statut": False, "responsable": "ACO"}
    ]
    
    col1, col2 = st.columns(2)
    
    with col1:
        for item in checklist_items[:3]:
            status_icon = "✅" if item["statut"] else "⏳"
            st.write(f"{status_icon} **{item['item']}** - {item['responsable']}")
    
    with col2:
        for item in checklist_items[3:]:
            status_icon = "✅" if item["statut"] else "⏳"
            st.write(f"{status_icon} **{item['item']}** - {item['responsable']}")
    
    # Bilan opération
    st.markdown("#### 📊 Bilan Opération")
    
    col_bilan1, col_bilan2, col_bilan3 = st.columns(3)
    
    with col_bilan1:
        st.markdown("##### 💰 Bilan Financier")
        st.metric("Budget Initial", "2 450 000 €")
        st.metric("Budget Final", "2 398 000 €", delta="-52 000 €")
        st.metric("Écart Budget", "-2.1%", delta_color="inverse")
    
    with col_bilan2:
        st.markdown("##### ⏱️ Bilan Planning")
        st.metric("Durée Prévue", "24 mois")
        st.metric("Durée Réelle", "26 mois", delta="+2 mois")
        st.metric("Écart Planning", "+8.3%", delta_color="inverse")
    
    with col_bilan3:
        st.markdown("##### 🎯 Bilan Qualité")
        st.metric("Phases en Retard", "3")
        st.metric("Avenants Total", "3")
        st.metric("Réclamations GPA", "12")
    
    # Actions finales
    st.markdown("#### 🔚 Actions de Clôture")
    
    col_action1, col_action2, col_action3 = st.columns(3)
    
    with col_action1:
        if st.button("📋 Générer Bilan Final", key="bilan_final"):
            st.success("📄 Bilan final généré en Word")
    
    with col_action2:
        if st.button("💾 Archiver Définitivement", key="archiver"):
            st.warning("⚠️ Confirmer archivage définitif")
    
    with col_action3:
        # Vérification que tous les items sont validés
        tous_valides = all(item["statut"] for item in checklist_items)
        if tous_valides:
            if st.button("✅ CLÔTURER OPÉRATION", key="cloturer", type="primary"):
                st.success("🎉 Opération clôturée avec succès!")
                st.balloons()
        else:
            st.button("⏳ Clôture en attente", key="cloturer_attente", disabled=True)
            st.info("Complétez tous les éléments de la checklist")

# ==============================================================================
# 4. NAVIGATION ACO-CENTRIQUE
# ==============================================================================

def page_dashboard():
    """Dashboard principal avec KPIs ACO"""
    st.markdown("""
    <div class="main-header">OPCOPILOT - Tableau de Bord Opérationnel</div>
    <div style='font-size:1.2em;color:#64748b;margin-bottom:2em;'>Mon Tableau de Bord - <b>{}</b></div>
    """.format(st.session_state.get('aco_user','ACO')), unsafe_allow_html=True)
    kpi_cols = st.columns(4)
    kpis = [
        {"label": "23 Opérations Actives", "icon": "<svg class='lucide-icon kpi-blue' fill='none' stroke='currentColor' viewBox='0 0 24 24'><rect x='3' y='7' width='18' height='13' rx='2'/><path d='M16 3v4'/><path d='M8 3v4'/></svg>", "color": "kpi-blue", "page": "portefeuille"},
        {"label": "485k€ REM Mon Portefeuille", "icon": "<svg class='lucide-icon kpi-green' fill='none' stroke='currentColor' viewBox='0 0 24 24'><polyline points='17 6 9 17 7 14'/></svg>", "color": "kpi-green", "page": "rem"},
        {"label": "3 Freins Actifs", "icon": "<svg class='lucide-icon kpi-orange' fill='none' stroke='currentColor' viewBox='0 0 24 24'><polygon points='10 2 2 22 22 22 14 2 10 2'/></svg>", "color": "kpi-orange", "page": "freins"},
        {"label": "5 Échéances Semaine", "icon": "<svg class='lucide-icon kpi-red' fill='none' stroke='currentColor' viewBox='0 0 24 24'><rect x='3' y='4' width='18' height='18' rx='2'/><line x1='16' y1='2' x2='16' y2='6'/><line x1='8' y1='2' x2='8' y2='6'/></svg>", "color": "kpi-red", "page": "planning"}
    ]
    for i, kpi in enumerate(kpis):
        if kpi_cols[i].button(f"{kpi['icon']}<br><span style='font-size:1.1em;'>{kpi['label']}</span>", key=f"kpi_{i}", help=kpi['label']):
            st.session_state['page'] = kpi['page']
            st.rerun()
        kpi_cols[i].markdown(f"<div class='kpi-card {kpi['color']}'>{kpi['icon']}<br><span style='font-size:1.1em;'>{kpi['label']}</span></div>", unsafe_allow_html=True)

# --- SIDEBAR MODERNE ---
with st.sidebar:
    st.markdown(f"""
    <div style='padding-top:1.2em;padding-bottom:0.5em;'>
        <div style='font-size:1.3em;font-weight:700;color:#3B82F6;'>
            {st.session_state.get('aco_user', 'ACO')}<br><span style='font-size:0.85em;font-weight:400;color:#64748b;'>Chargé d'Opérations</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    # Navigation Lucide SVG
    st.markdown("""
    <a href="#" class="sidebar-btn" onclick="window.location.hash='dashboard';window.location.reload();">
        <svg class="lucide-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>
        Dashboard
    </a>
    <a href="#" class="sidebar-btn" onclick="window.location.hash='portefeuille';window.location.reload();">
        <svg class="lucide-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M3 7V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2v2"/><path d="M3 7v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V7"/><path d="M16 3v4"/><path d="M8 3v4"/></svg>
        Mon Portefeuille
    </a>
    <a href="#" class="sidebar-btn" onclick="window.location.hash='nouvelle';window.location.reload();">
        <svg class="lucide-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
        Nouvelle Opération
    </a>
    <a href="#" class="sidebar-btn" onclick="window.location.hash='acces';window.location.reload();">
        <svg class="lucide-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><polyline points="7 17 17 7"/><polyline points="7 7 17 17"/></svg>
        Accès Rapide
    </a>
    """, unsafe_allow_html=True)
    # Liste opérations démo avec pastilles statut
    st.markdown("<div style='margin-top:2em;font-weight:600;color:#64748b;font-size:1.05em;'>Mes Opérations</div>", unsafe_allow_html=True)
    # EXEMPLE (à remplacer par la vraie liste dans la logique)
    for op in [
        {"nom":"ZAC Bellevue", "statut":"vert"},
        {"nom":"Résidence Soleil", "statut":"orange"},
        {"nom":"Collège Nord", "statut":"rouge"}
    ]:
        st.markdown(f"""
        <div class='sidebar-btn' style='padding:0.5em 1em;cursor:pointer;'>
            <span class='status-dot status-{op['statut']}'></span>{op['nom']}
        </div>
        """, unsafe_allow_html=True)
    st.markdown("<hr style='margin:1.5em 0 0.5em 0;border:0;border-top:1px solid #e5e7eb;'/>", unsafe_allow_html=True)
    logout()

# --- NAVIGATION ---
def main():
    if not st.session_state.get('authenticated', False):
        return
    page = st.session_state.get('page', 'dashboard')
    if page == 'dashboard':
        page_dashboard()
    elif page == 'portefeuille':
        page_portefeuille_aco()
    elif page == 'rem':
        st.write('Section REM détaillée à venir.')
    elif page == 'freins':
        st.write('Liste des freins actifs à venir.')
    elif page == 'planning':
        st.write('Planning des échéances à venir.')
    elif page == 'nouvelle':
        page_creation_operation()
    elif page == 'acces':
        st.write('Accès rapide à venir.')
    else:
        page_dashboard()

if __name__ == "__main__":
    main()
