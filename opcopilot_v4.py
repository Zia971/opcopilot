"""
OPCOPILOT v4.0 - Application Streamlit complète avec authentification
Gestion d'opérations immobilières pour ACO SPIC Guadeloupe
Architecture ACO-centrique avec Timeline horizontale obligatoire
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
from docx import Document
import os
import hashlib

# Configuration page
st.set_page_config(
    page_title="OPCOPILOT v4.0 - SPIC Guadeloupe",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé pour interface MODERNE CLAIRE
st.markdown("""
<style>
    /* THÈME CLAIR MODERNE */
    .stApp {
        background-color: #F9FAFB;
    }
    
    .main-header {
        background: linear-gradient(135deg, #3B82F6 0%, #1E40AF 100%);
        color: white;
        padding: 2rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        box-shadow: 0 10px 25px rgba(59, 130, 246, 0.2);
    }
    
    .login-container {
        background: white;
        border-radius: 16px;
        padding: 3rem;
        box-shadow: 0 20px 50px rgba(0, 0, 0, 0.1);
        border: 1px solid #E5E7EB;
        max-width: 400px;
        margin: 0 auto;
    }
    
    .operation-card {
        background: white;
        border: 1px solid #E5E7EB;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        transition: all 0.3s ease;
    }
    
    .operation-card:hover {
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
        transform: translateY(-2px);
    }
    
    .kpi-card {
        background: white;
        border: 1px solid #E5E7EB;
        border-radius: 12px;
        padding: 2rem;
        text-align: center;
        margin: 0.5rem;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        transition: all 0.3s ease;
        cursor: pointer;
    }
    
    .kpi-card:hover {
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
        transform: translateY(-2px);
    }
    
    .kpi-card.primary {
        background: linear-gradient(135deg, #3B82F6 0%, #1E40AF 100%);
        color: white;
    }
    
    .kpi-card.success {
        background: linear-gradient(135deg, #10B981 0%, #047857 100%);
        color: white;
    }
    
    .kpi-card.warning {
        background: linear-gradient(135deg, #F59E0B 0%, #D97706 100%);
        color: white;
    }
    
    .kpi-card.danger {
        background: linear-gradient(135deg, #EF4444 0%, #DC2626 100%);
        color: white;
    }
    
    .timeline-container {
        background: white;
        border-radius: 12px;
        padding: 2rem;
        margin: 1rem 0;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        border: 1px solid #E5E7EB;
    }
    
    .module-tab {
        background: white;
        border: 1px solid #E5E7EB;
        border-radius: 8px;
        padding: 1.5rem;
        margin: 0.5rem;
        border-left: 4px solid #3B82F6;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    }
    
    .alert-critical { 
        background: #FEF2F2; 
        border-left: 4px solid #EF4444; 
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 8px;
        border: 1px solid #FECACA;
    }
    
    .alert-warning { 
        background: #FFFBEB; 
        border-left: 4px solid #F59E0B; 
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 8px;
        border: 1px solid #FED7AA;
    }
    
    .alert-info { 
        background: #EFF6FF; 
        border-left: 4px solid #3B82F6; 
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 8px;
        border: 1px solid #BFDBFE;
    }
    
    .metric-card {
        background: white;
        border: 1px solid #E5E7EB;
        border-radius: 8px;
        padding: 1.5rem;
        text-align: center;
        margin: 0.5rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    }
    
    .sidebar-header {
        background: linear-gradient(135deg, #1F2937 0%, #111827 100%);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
        text-align: center;
    }
    
    .login-title {
        text-align: center;
        color: #1F2937;
        font-size: 2rem;
        font-weight: bold;
        margin-bottom: 2rem;
    }
    
    .success-message {
        background: #F0FDF4;
        border: 1px solid #BBF7D0;
        color: #166534;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    .error-message {
        background: #FEF2F2;
        border: 1px solid #FECACA;
        color: #DC2626;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# SYSTÈME D'AUTHENTIFICATION
# ==============================================================================

# Base de données ACO pour démonstration
DEMO_ACO_USERS = {
    "marie.admin": {
        "password": "spic2024",
        "nom": "Marie-Claire ADMIN",
        "role": "ACO_SENIOR",
        "secteur": "Les Abymes - Pointe-à-Pitre",
        "operations": 23
    },
    "jean.martin": {
        "password": "aco123",
        "nom": "Jean MARTIN",
        "role": "ACO",
        "secteur": "Basse-Terre - Sainte-Anne", 
        "operations": 15
    },
    "admin": {
        "password": "admin2024",
        "nom": "Administrateur SPIC",
        "role": "ADMIN",
        "secteur": "Tous secteurs",
        "operations": 0
    }
}

def hash_password(password):
    """Hashage simple du mot de passe"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(username, password):
    """Vérification des identifiants"""
    if username in DEMO_ACO_USERS:
        return DEMO_ACO_USERS[username]["password"] == password
    return False

def init_session_state():
    """Initialisation session state authentification"""
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "aco_user" not in st.session_state:
        st.session_state.aco_user = None
    if "user_data" not in st.session_state:
        st.session_state.user_data = None
    if "page" not in st.session_state:
        st.session_state.page = "dashboard"
    if 'selected_operation' not in st.session_state:
        st.session_state.selected_operation = None
    if 'selected_operation_id' not in st.session_state:
        st.session_state.selected_operation_id = None

def logout():
    """Déconnexion utilisateur"""
    st.session_state.authenticated = False
    st.session_state.aco_user = None
    st.session_state.user_data = None
    st.session_state.page = "login"

# ==============================================================================
# PAGES D'AUTHENTIFICATION
# ==============================================================================

def page_login():
    """Page de connexion moderne"""
    st.markdown("""
    <div class="login-title">
        🏗️ OPCOPILOT v4.0<br>
        <small style="font-size: 1rem; color: #6B7280;">SPIC Guadeloupe - Connexion ACO</small>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        
        # Formulaire de connexion
        with st.form("login_form"):
            st.markdown("### 🔐 Connexion")
            
            username = st.text_input(
                "👤 Nom d'utilisateur",
                placeholder="Votre identifiant ACO",
                help="Utilisez votre identifiant SPIC"
            )
            
            password = st.text_input(
                "🔑 Mot de passe",
                type="password",
                placeholder="Votre mot de passe",
                help="Mot de passe fourni par l'administration"
            )
            
            col_btn1, col_btn2 = st.columns(2)
            
            with col_btn1:
                login_submitted = st.form_submit_button(
                    "🚀 Se connecter",
                    use_container_width=True,
                    type="primary"
                )
            
            with col_btn2:
                if st.form_submit_button("🔄 Mot de passe oublié", use_container_width=True):
                    st.session_state.page = "reset_password"
                    st.rerun()
        
        # Traitement connexion
        if login_submitted:
            if username and password:
                if verify_password(username, password):
                    st.session_state.authenticated = True
                    st.session_state.aco_user = username
                    st.session_state.user_data = DEMO_ACO_USERS[username]
                    st.session_state.page = "dashboard"
                    st.success("✅ Connexion réussie !")
                    st.rerun()
                else:
                    st.error("❌ Identifiants incorrects")
            else:
                st.warning("⚠️ Veuillez remplir tous les champs")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Comptes de démonstration
    st.markdown("---")
    st.markdown("### 🎯 Comptes de Démonstration")
    
    col_demo1, col_demo2, col_demo3 = st.columns(3)
    
    with col_demo1:
        st.info("""
        **👩‍💼 ACO Senior**
        - **Login :** marie.admin
        - **Password :** spic2024
        - **Rôle :** ACO Senior
        """)
    
    with col_demo2:
        st.info("""
        **👨‍💼 ACO Standard**
        - **Login :** jean.martin
        - **Password :** aco123
        - **Rôle :** ACO
        """)
    
    with col_demo3:
        st.info("""
        **🔧 Administrateur**
        - **Login :** admin
        - **Password :** admin2024
        - **Rôle :** Administrateur
        """)

def page_reset_password():
    """Page de réinitialisation mot de passe"""
    st.markdown("### 🔄 Réinitialisation Mot de Passe")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        
        with st.form("reset_form"):
            st.markdown("#### 📧 Demande de réinitialisation")
            
            email = st.text_input(
                "📧 Email professionnel",
                placeholder="votre.email@spic-guadeloupe.fr"
            )
            
            username = st.text_input(
                "👤 Nom d'utilisateur",
                placeholder="Votre identifiant ACO"
            )
            
            if st.form_submit_button("📨 Envoyer demande", use_container_width=True, type="primary"):
                if email and username:
                    st.success("✅ Demande envoyée ! Vérifiez vos emails.")
                    st.info("📧 Un lien de réinitialisation vous sera envoyé sous 5 minutes.")
                else:
                    st.warning("⚠️ Veuillez remplir tous les champs")
        
        if st.button("← Retour connexion", use_container_width=True):
            st.session_state.page = "login"
            st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)

def page_admin():
    """Page d'administration"""
    if st.session_state.user_data.get("role") != "ADMIN":
        st.error("❌ Accès refusé - Droits administrateur requis")
        return
    
    st.markdown("### 🔧 Administration OPCOPILOT")
    
    tab_users, tab_stats, tab_config = st.tabs(["👥 Utilisateurs", "📊 Statistiques", "⚙️ Configuration"])
    
    with tab_users:
        st.markdown("#### Gestion des utilisateurs ACO")
        
        # Liste des utilisateurs
        users_data = []
        for username, data in DEMO_ACO_USERS.items():
            users_data.append({
                "Username": username,
                "Nom": data["nom"],
                "Rôle": data["role"],
                "Secteur": data["secteur"],
                "Opérations": data["operations"]
            })
        
        df_users = pd.DataFrame(users_data)
        st.dataframe(df_users, use_container_width=True)
        
        # Ajouter utilisateur
        with st.expander("➕ Ajouter un nouvel ACO"):
            with st.form("add_user"):
                new_username = st.text_input("Nom d'utilisateur")
                new_name = st.text_input("Nom complet")
                new_role = st.selectbox("Rôle", ["ACO", "ACO_SENIOR", "ADMIN"])
                new_sector = st.text_input("Secteur")
                
                if st.form_submit_button("Ajouter"):
                    st.success("Utilisateur ajouté (démonstration)")
    
    with tab_stats:
        st.markdown("#### Statistiques globales")
        
        col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
        
        with col_stat1:
            st.metric("Utilisateurs actifs", "12", delta="2")
        
        with col_stat2:
            st.metric("Connexions aujourd'hui", "8", delta="3")
        
        with col_stat3:
            st.metric("Opérations totales", "156", delta="5")
        
        with col_stat4:
            st.metric("Erreurs système", "0", delta="-2")
    
    with tab_config:
        st.markdown("#### Configuration système")
        
        st.checkbox("Maintenance programmée", value=False)
        st.checkbox("Notifications email", value=True)
        st.checkbox("Sauvegarde automatique", value=True)
        
        if st.button("💾 Sauvegarder configuration"):
            st.success("Configuration sauvegardée")

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
    """Dashboard principal avec KPIs ACO INTERACTIFS"""
    
    # Chargement données
    demo_data = load_demo_data()
    kpis_data = demo_data.get('kpis_aco_demo', {})
    activite_data = demo_data.get('activite_mensuelle_demo', {})
    alertes_data = demo_data.get('alertes_demo', [])
    
    user_data = st.session_state.user_data
    nom_aco = user_data.get('nom', 'ACO')
    
    st.markdown(f"""
    <div class="main-header">
        <h1>🏗️ OPCOPILOT v4.0 - Tableau de Bord Opérationnel</h1>
        <h2>Mon Tableau de Bord - {nom_aco}</h2>
        <p>Interface de Gestion d'Opérations • SPIC Guadeloupe</p>
    </div>
    """, unsafe_allow_html=True)
    
    # KPIs personnels ACO INTERACTIFS
    st.markdown("### 📊 Mes Indicateurs Clés de Performance")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        operations_actives = kpis_data.get('operations_actives', 23)
        operations_cloturees = kpis_data.get('operations_cloturees', 5)
        
        if st.button(f"""
        **{operations_actives}**  
        Opérations Actives  
        {operations_cloturees} clôturées
        """, key="btn_operations", use_container_width=True):
            st.session_state.page = "portefeuille"
            st.rerun()
        
        st.markdown("""
        <div class="kpi-card primary">
            <div onclick="window.location.href='#portefeuille'">
                <h2>{}</h2>
                <p>Opérations Actives</p>
                <small>{} clôturées</small>
            </div>
        </div>
        """.format(operations_actives, operations_cloturees), unsafe_allow_html=True)
    
    with col2:
        rem_realise = kpis_data.get('rem_realisee_2024', 485000)
        rem_prevu = kpis_data.get('rem_prevue_2024', 620000)
        taux_real = kpis_data.get('taux_realisation_rem', 78)
        
        if st.button(f"""
        **{rem_realise/1000:.0f}k€**  
        REM Réalisée 2024  
        {taux_real}% / {rem_prevu/1000:.0f}k€ prévue
        """, key="btn_rem", use_container_width=True):
            # Navigation vers analyse REM
            st.info("📊 Analyse REM détaillée - En développement")
        
        st.markdown("""
        <div class="kpi-card success">
            <h2>{:.0f}k€</h2>
            <p>REM Réalisée 2024</p>
            <small>{}% / {:.0f}k€ prévue</small>
        </div>
        """.format(rem_realise/1000, taux_real, rem_prevu/1000), unsafe_allow_html=True)
    
    with col3:
        freins_actifs = kpis_data.get('freins_actifs', 3)
        freins_critiques = kpis_data.get('freins_critiques', 2)
        
        if st.button(f"""
        **{freins_actifs}**  
        Freins Actifs  
        {freins_critiques} critiques
        """, key="btn_freins", use_container_width=True):
            # Navigation vers détail des freins
            st.session_state.page = "gestion_freins"
            st.rerun()
        
        st.markdown("""
        <div class="kpi-card warning">
            <h2>{}</h2>
            <p>Freins Actifs</p>
            <small>{} critiques</small>
        </div>
        """.format(freins_actifs, freins_critiques), unsafe_allow_html=True)
    
    with col4:
        echeances = kpis_data.get('echeances_semaine', 5)
        validations = kpis_data.get('validations_requises', 12)
        
        if st.button(f"""
        **{echeances}**  
        Échéances Semaine  
        {validations} validations requises
        """, key="btn_echeances", use_container_width=True):
            # Navigation vers planning
            st.session_state.page = "planning_echeances"
            st.rerun()
        
        st.markdown("""
        <div class="kpi-card danger">
            <h2>{}</h2>
            <p>Échéances Semaine</p>
            <small>{} validations requises</small>
        </div>
        """.format(echeances, validations), unsafe_allow_html=True)
    
    # Alertes et actions
    st.markdown("### 🚨 Alertes et Actions Prioritaires")
    
    col_alert1, col_alert2 = st.columns(2)
    
    with col_alert1:
        st.markdown("#### Alertes Critiques")
        
        for alerte in alertes_data:
            alert_class = f"alert-{alerte['type'].lower()}"
            if alerte['type'] == 'CRITIQUE':
                alert_class = "alert-critical"
            elif alerte['type'] == 'WARNING':
                alert_class = "alert-warning"
            else:
                alert_class = "alert-info"
                
            st.markdown(f"""
            <div class="{alert_class}">
                <strong>{alerte['operation']}</strong><br>
                {alerte['message']}<br>
                <em>Action: {alerte['action_requise']}</em>
            </div>
            """, unsafe_allow_html=True)
    
    with col_alert2:
        st.markdown("#### Actions Réalisées Aujourd'hui")
        
        actions_jour = [
            "✅ DGD validé - RÉSIDENCE SOLEIL",
            "✅ Phase ESQ terminée - COUR CHARNEAU", 
            "✅ MED envoyé - MANDAT ÉCOLE",
            "✅ REM T3 saisi - 3 opérations",
            "✅ Timeline mise à jour - VEFA BELCOURT"
        ]
        
        for action in actions_jour:
            st.write(action)
    
    # Graphique d'activité
    st.markdown("### 📈 Activité Mensuelle")
    
    if activite_data:
        fig_dashboard = go.Figure()
        
        # REM mensuelle
        fig_dashboard.add_trace(go.Scatter(
            x=activite_data['mois'],
            y=activite_data['rem_mensuelle'],
            mode='lines+markers',
            name='REM Mensuelle (€)',
            yaxis='y',
            line=dict(color='#3B82F6', width=3),
            marker=dict(size=8)
        ))
        
        # Opérations actives
        fig_dashboard.add_trace(go.Scatter(
            x=activite_data['mois'],
            y=activite_data['operations_actives'],
            mode='lines+markers',
            name='Opérations Actives',
            yaxis='y2',
            line=dict(color='#10B981', width=3),
            marker=dict(size=8)
        ))
        
        fig_dashboard.update_layout(
            title=f"Évolution Activité {nom_aco} - 2024",
            xaxis=dict(title="Mois"),
            yaxis=dict(title="REM (€)", side="left"),
            yaxis2=dict(title="Nb Opérations", side="right", overlaying="y"),
            height=450,
            hovermode='x unified',
            plot_bgcolor='white',
            paper_bgcolor='white'
        )
        
        st.plotly_chart(fig_dashboard, use_container_width=True)

def page_gestion_freins():
    """Page de gestion des freins"""
    st.markdown("### 🚨 Gestion des Freins Opérationnels")
    
    # Liste des freins
    freins_data = [
        {
            "Opération": "COUR CHARNEAU",
            "Phase": "Demande LBU", 
            "Type": "RETARD",
            "Durée": "5 jours",
            "Impact": "Critique",
            "Responsable": "MOE ARCHI-CONSEIL",
            "Action": "Relance urgente"
        },
        {
            "Opération": "MANDAT ÉCOLE",
            "Phase": "Validation budget",
            "Type": "BLOCAGE",
            "Durée": "12 jours", 
            "Impact": "Majeur",
            "Responsable": "Commune Basse-Terre",
            "Action": "RDV programmé"
        },
        {
            "Opération": "VEFA BELCOURT",
            "Phase": "Signature protocole",
            "Type": "ATTENTE",
            "Durée": "3 jours",
            "Impact": "Mineur", 
            "Responsable": "SOGEPROM",
            "Action": "Suivi normal"
        }
    ]
    
    df_freins = pd.DataFrame(freins_data)
    st.dataframe(df_freins, use_container_width=True)
    
    # Actions de résolution
    st.markdown("#### Actions de Résolution")
    
    col_action1, col_action2, col_action3 = st.columns(3)
    
    with col_action1:
        if st.button("📞 Relancer tous les responsables"):
            st.success("📧 Relances envoyées automatiquement")
    
    with col_action2:
        if st.button("📊 Rapport freins hebdomadaire"):
            st.info("📋 Génération rapport en cours...")
    
    with col_action3:
        if st.button("⚠️ Escalade hiérarchique"):
            st.warning("📈 Escalade programmée vers direction")

def page_planning_echeances():
    """Page de planning des échéances"""
    st.markdown("### 📅 Planning des Échéances")
    
    # Échéances de la semaine
    echeances_data = [
        {
            "Date": "Lundi 28/10",
            "Opération": "COUR CHARNEAU",
            "Échéance": "Réception provisoire",
            "Type": "JALON",
            "Priorité": "Haute"
        },
        {
            "Date": "Mercredi 30/10", 
            "Opération": "RÉSIDENCE SOLEIL",
            "Échéance": "Validation DGD",
            "Type": "VALIDATION",
            "Priorité": "Moyenne"
        },
        {
            "Date": "Vendredi 01/11",
            "Opération": "MANDAT ÉCOLE",
            "Échéance": "Remise livrables",
            "Type": "LIVRABLE",
            "Priorité": "Haute"
        }
    ]
    
    df_echeances = pd.DataFrame(echeances_data)
    st.dataframe(df_echeances, use_container_width=True)
    
    # Calendrier de la semaine
    st.markdown("#### 📆 Vue Calendaire")
    
    col_lun, col_mar, col_mer, col_jeu, col_ven = st.columns(5)
    
    with col_lun:
        st.markdown("**Lundi 28**")
        st.info("🏗️ Réception COUR CHARNEAU")
    
    with col_mar:
        st.markdown("**Mardi 29**")
        st.success("✅ Pas d'échéance")
    
    with col_mer:
        st.markdown("**Mercredi 30**")
        st.warning("📊 Validation DGD")
    
    with col_jeu:
        st.markdown("**Jeudi 31**")
        st.success("✅ Pas d'échéance")
    
    with col_ven:
        st.markdown("**Vendredi 01**")
        st.error("📋 Remise livrables")

def page_portefeuille_aco():
    """Portefeuille ACO avec liste des opérations"""
    user_data = st.session_state.user_data
    nom_aco = user_data.get('nom', 'ACO')
    
    st.markdown(f"### 📂 Mon Portefeuille - {nom_aco}")
    
    # Chargement données
    demo_data = load_demo_data()
    operations_data = demo_data.get('operations_demo', [])
    
    # Filtres
    col_filter1, col_filter2, col_filter3, col_filter4 = st.columns(4)
    
    with col_filter1:
        filtre_type = st.selectbox("Type Opération", ["Tous", "OPP", "VEFA", "MANDAT_ETUDES", "MANDAT_REALISATION", "AMO"])
    
    with col_filter2:
        filtre_statut = st.selectbox("Statut", ["Tous", "EN_MONTAGE", "EN_COURS", "EN_RECEPTION", "CLOTUREE"])
    
    with col_filter3:
        filtre_commune = st.selectbox("Commune", ["Toutes", "Les Abymes", "Pointe-à-Pitre", "Basse-Terre", "Sainte-Anne"])
    
    with col_filter4:
        if st.button("➕ Nouvelle Opération", type="primary"):
            st.session_state.page = "creation_operation"
            st.rerun()
    
    # Application des filtres
    operations_filtrees = operations_data
    if filtre_type != "Tous":
        operations_filtrees = [op for op in operations_filtrees if op['type_operation'] == filtre_type]
    if filtre_statut != "Tous":
        operations_filtrees = [op for op in operations_filtrees if op['statut'] == filtre_statut]
    if filtre_commune != "Toutes":
        operations_filtrees = [op for op in operations_filtrees if op['commune'] == filtre_commune]
    
    # Liste des opérations
    st.markdown(f"#### 📋 Mes Opérations ({len(operations_filtrees)} affichées)")
    
    for op in operations_filtrees:
        with st.container():
            st.markdown(f"""
            <div class="operation-card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <h4>🏗️ {op['nom']} - {op['type_operation']}</h4>
                        <p><strong>📍 {op['commune']}</strong> • {op.get('nb_logements_total', 0)} logements • {op.get('budget_total', 0):,} €</p>
                        <p><em>Créé le {op['date_creation']} • Fin prévue {op['date_fin_prevue']}</em></p>
                    </div>
                    <div style="text-align: right;">
                        <p><strong>Avancement: {op['avancement']}%</strong></p>
                        <p>Statut: <span style="color: {'#10B981' if op['statut'] == 'EN_COURS' else '#F59E0B'}">{op['statut']}</span></p>
                        {f"<p style='color: #EF4444;'>⚠️ {op.get('freins_actifs', 0)} frein(s)</p>" if op.get('freins_actifs', 0) > 0 else ""}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 2])
            
            with col_btn1:
                if st.button(f"📂 Ouvrir", key=f"open_{op['id']}"):
                    st.session_state.selected_operation_id = op['id']
                    st.session_state.selected_operation = op
                    st.session_state.page = "operation_details"
                    st.rerun()
            
            with col_btn2:
                if st.button(f"📊 Timeline", key=f"timeline_{op['id']}"):
                    st.session_state.selected_operation_id = op['id']
                    st.session_state.selected_operation = op
                    st.session_state.page = "operation_details"
                    st.session_state.active_tab = "timeline"
                    st.rerun()

def page_operation_details(operation_id=None):
    """Page détail opération avec timeline et modules intégrés"""
    
    # Récupération données utilisateur
    user_data = st.session_state.user_data
    nom_aco = user_data.get('nom', 'ACO')
    
    # Récupération de l'opération
    if operation_id is None and 'selected_operation_id' in st.session_state:
        operation_id = st.session_state.selected_operation_id
    
    if 'selected_operation' in st.session_state:
        operation = st.session_state.selected_operation
    else:
        # Fallback avec données de démo
        demo_data = load_demo_data()
        operations_data = demo_data.get('operations_demo', [])
        operation = operations_data[0] if operations_data else {}
        operation_id = operation.get('id', 1)
    
    # En-tête opération
    st.markdown(f"""
    <div class="main-header">
        <h1>🏗️ {operation.get('nom', 'Opération')} - {operation.get('type_operation', 'OPP')}</h1>
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <p><strong>📍 {operation.get('commune', 'Commune')}</strong> • {operation.get('nb_logements_total', 0)} logements • ACO {nom_aco}</p>
            </div>
            <div>
                <p><strong>Budget:</strong> {operation.get('budget_total', 0):,} € • <strong>Avancement:</strong> {operation.get('avancement', 0)}%</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Bouton retour
    if st.button("← Retour au Portefeuille"):
        st.session_state.page = "portefeuille"
        st.rerun()
    
    # Onglets modules intégrés
    tab_timeline, tab_rem, tab_avenants, tab_med, tab_concess, tab_dgd, tab_gpa, tab_cloture = st.tabs([
        "📅 Timeline", "💰 REM", "📝 Avenants", "⚖️ MED", 
        "🔌 Concess.", "📊 DGD", "🛡️ GPA", "✅ Clôture"
    ])
    
    with tab_timeline:
        st.markdown("### 📅 Timeline Horizontale - Gestion des Phases")
        
        # Chargement des phases
        demo_data = load_demo_data()
        phases_data = demo_data.get('phases_demo', {}).get(f'operation_{operation_id}', [])
        
        # Si pas de phases spécifiques, on charge un template selon le type
        if not phases_data:
            templates = load_templates_phases()
            type_op = operation.get('type_operation', 'OPP')
            template_phases = templates.get(type_op, {}).get('phases', [])
            
            # Conversion template en phases avec dates
            phases_data = []
            date_courante = datetime.now()
            
            for i, phase_template in enumerate(template_phases[:8]):  # Limite pour démo
                debut = date_courante + timedelta(days=i*20)
                fin = debut + timedelta(days=phase_template.get('duree_jours', 30))
                
                statuts_demo = ["VALIDEE", "EN_COURS", "EN_ATTENTE", "NON_DEMARREE"]
                statut = statuts_demo[i % len(statuts_demo)]
                
                phases_data.append({
                    "nom": phase_template['nom'],
                    "date_debut_prevue": debut.isoformat(),
                    "date_fin_prevue": fin.isoformat(),
                    "statut": statut,
                    "responsable": phase_template.get('responsable_type', 'ACO'),
                    "est_critique": phase_template.get('est_critique', False)
                })
        
        # Affichage timeline horizontale
        if phases_data:
            timeline_fig, config = create_timeline_horizontal(operation, phases_data)
            if timeline_fig:
                st.plotly_chart(timeline_fig, use_container_width=True, config=config)
                
                # Gestion des phases
                st.markdown("#### 🔧 Gestion des Phases")
                
                col_phase1, col_phase2, col_phase3, col_phase4 = st.columns(4)
                
                with col_phase1:
                    if st.button("➕ Ajouter Phase"):
                        st.success("✅ Interface d'ajout de phase")
                
                with col_phase2:
                    if st.button("✏️ Modifier Phase"):
                        st.info("🔄 Mode modification activé")
                
                with col_phase3:
                    if st.button("⚠️ Signaler Frein"):
                        st.warning("🚨 Frein signalé sur phase sélectionnée")
                
                with col_phase4:
                    if st.button("📊 Exporter Planning"):
                        st.info("📁 Export Excel en cours...")
        else:
            st.warning("⚠️ Aucune phase définie pour cette opération")
    
    with tab_rem:
        module_rem(operation_id)
    
    with tab_avenants:
        module_avenants(operation_id)
    
    with tab_med:
        module_med(operation_id)
    
    with tab_concess:
        module_concessionnaires(operation_id)
    
    with tab_dgd:
        module_dgd(operation_id)
    
    with tab_gpa:
        module_gpa(operation_id)
    
    with tab_cloture:
        module_cloture(operation_id)

def page_creation_operation():
    """Page de création nouvelle opération"""
    user_data = st.session_state.user_data
    nom_aco = user_data.get('nom', 'ACO')
    
    st.markdown("### ➕ Nouvelle Opération")
    
    # Chargement des templates
    templates = load_templates_phases()
    
    with st.form("creation_operation"):
        st.markdown("#### 📝 Informations Générales")
        
        col1, col2 = st.columns(2)
        
        with col1:
            nom_operation = st.text_input("Nom Opération *", placeholder="Ex: RÉSIDENCE LES JARDINS")
            type_operation = st.selectbox("Type Opération *", list(templates.keys()))
            commune = st.selectbox("Commune *", [
                "Les Abymes", "Pointe-à-Pitre", "Basse-Terre", 
                "Sainte-Anne", "Le Gosier", "Petit-Bourg",
                "Baie-Mahault", "Lamentin"
            ])
        
        with col2:
            aco_responsable = st.text_input("ACO Responsable", value=nom_aco)
            adresse = st.text_area("Adresse")
            parcelle = st.text_input("Parcelle Cadastrale")
        
        # Formulaire adaptatif selon le type
        template_info = templates.get(type_operation, {})
        st.markdown(f"#### 🏠 Spécifique {type_operation}")
        st.info(f"📋 {template_info.get('description', '')} - {template_info.get('nb_phases', 0)} phases")
        
        if type_operation == "OPP":
            col_opp1, col_opp2 = st.columns(2)
            
            with col_opp1:
                nb_logements_total = st.number_input("Nombre Total Logements *", min_value=1, value=40)
                nb_lls = st.number_input("LLS (Logements Locatifs Sociaux)", min_value=0, value=25)
                nb_lts = st.number_input("LTS (Logements Très Sociaux)", min_value=0, value=10)
                nb_pls = st.number_input("PLS (Prêt Locatif Social)", min_value=0, value=5)
                type_logement = st.selectbox("Type", ["Collectif", "Individuel", "Mixte"])
            
            with col_opp2:
                budget_total = st.number_input("Budget Total (€)", min_value=0, value=2000000)
                rem_totale = st.number_input("REM Totale Prévue (€)", min_value=0, value=120000)
                financement = st.multiselect("Financement", ["CDC", "Région", "DEAL", "Fonds Propres"])
        
        elif type_operation == "VEFA":
            col_vefa1, col_vefa2 = st.columns(2)
            
            with col_vefa1:
                promoteur_nom = st.text_input("Nom Promoteur *")
                contact_promoteur = st.text_input("Contact Promoteur")
                nom_programme = st.text_input("Nom Programme")
            
            with col_vefa2:
                nb_logements_reserves = st.number_input("Logements Réservés *", min_value=1, value=20)
                prix_total_reservation = st.number_input("Prix Total Réservation (€)", min_value=0, value=1500000)
                garantie_financiere = st.number_input("Garantie Financière (€)", min_value=0, value=150000)
        
        # Dates prévisionnelles
        st.markdown("#### 📅 Planning Prévisionnel")
        
        col_date1, col_date2 = st.columns(2)
        
        with col_date1:
            date_debut = st.date_input("Date Début Prévue", value=datetime.now())
        
        with col_date2:
            date_fin = st.date_input("Date Fin Prévue", value=datetime.now() + timedelta(days=730))
        
        # Validation
        submitted = st.form_submit_button("🎯 Créer Opération & Générer Timeline", type="primary")
        
        if submitted:
            if nom_operation and type_operation and commune:
                # Génération automatique des phases selon le type
                phases_template = template_info.get('phases', [])
                
                st.success(f"✅ Opération '{nom_operation}' créée avec succès!")
                st.info(f"📋 {len(phases_template)} phases générées automatiquement selon le référentiel {type_operation}")
                
                # Simulation de sauvegarde
                nouvelle_operation = {
                    "id": 999,  # ID temporaire pour la démo
                    "nom": nom_operation,
                    "type_operation": type_operation,
                    "commune": commune,
                    "aco_responsable": aco_responsable,
                    "budget_total": locals().get('budget_total', 0),
                    "avancement": 0,
                    "statut": "EN_MONTAGE",
                    "date_creation": datetime.now().strftime("%Y-%m-%d"),
                    "date_debut_prevue": date_debut.strftime("%Y-%m-%d"),
                    "date_fin_prevue": date_fin.strftime("%Y-%m-%d")
                }
                
                st.session_state.selected_operation = nouvelle_operation
                st.session_state.selected_operation_id = 999
                st.session_state.page = "operation_details"
                
                if st.button("📂 Ouvrir l'opération créée"):
                    st.rerun()
            else:
                st.error("❌ Veuillez remplir tous les champs obligatoires (*)")

# ==============================================================================
# 5. APPLICATION PRINCIPALE
# ==============================================================================

# ==============================================================================
# 5. APPLICATION PRINCIPALE AVEC AUTHENTIFICATION
# ==============================================================================

def main():
    """Point d'entrée avec authentification et navigation moderne"""
    
    # Initialisation session state
    init_session_state()
    
    # Vérification authentification
    if not st.session_state.authenticated:
        # Pages publiques (non authentifiées)
        if st.session_state.get("page") == "reset_password":
            page_reset_password()
        else:
            page_login()
        return
    
    # Navigation authentifiée
    user_data = st.session_state.user_data
    nom_aco = user_data.get('nom', 'ACO')
    role = user_data.get('role', 'ACO')
    
    # Sidebar navigation moderne
    with st.sidebar:
        # Header utilisateur
        st.markdown(f"""
        <div class="sidebar-header">
            <h3>👤 {nom_aco}</h3>
            <p>{role} - Chargé d'Opérations</p>
            <small>🏢 SPIC Guadeloupe</small>
        </div>
        """, unsafe_allow_html=True)
        
        # Navigation principale
        st.markdown("### 🎯 Navigation Principale")
        
        nav_buttons = [
            ("🏠 Dashboard", "dashboard"),
            ("📂 Mon Portefeuille", "portefeuille"),
            ("➕ Nouvelle Opération", "creation_operation"),
        ]
        
        for label, page_key in nav_buttons:
            is_current = st.session_state.page == page_key
            button_type = "primary" if is_current else "secondary"
            
            if st.button(label, use_container_width=True, type=button_type):
                st.session_state.page = page_key
                st.rerun()
        
        st.markdown("---")
        
        # Pages spécialisées
        st.markdown("### 📊 Analyses & Rapports")
        
        special_buttons = [
            ("🚨 Gestion Freins", "gestion_freins"),
            ("📅 Planning Échéances", "planning_echeances"),
        ]
        
        for label, page_key in special_buttons:
            if st.button(label, use_container_width=True):
                st.session_state.page = page_key
                st.rerun()
        
        st.markdown("---")
        
        # Opérations courantes (raccourcis)
        st.markdown("### 📋 Accès Rapide Opérations")
        
        demo_data = load_demo_data()
        operations_demo = demo_data.get('operations_demo', [])
        
        for op in operations_demo[:4]:  # Limite à 4 pour la sidebar
            progress_color = "🟢" if op['avancement'] > 80 else "🟡" if op['avancement'] > 50 else "🔴"
            button_text = f"{progress_color} {op['nom']} ({op['avancement']}%)"
            
            if st.button(button_text, use_container_width=True, key=f"sidebar_{op['id']}"):
                st.session_state.selected_operation = op
                st.session_state.selected_operation_id = op['id']
                st.session_state.page = "operation_details"
                st.rerun()
        
        st.markdown("---")
        
        # Administration (si admin)
        if role == "ADMIN":
            st.markdown("### 🔧 Administration")
            if st.button("⚙️ Panel Admin", use_container_width=True):
                st.session_state.page = "admin"
                st.rerun()
            st.markdown("---")
        
        # Informations système et déconnexion
        st.markdown("### ℹ️ Système")
        
        # Statut données
        if demo_data:
            st.success("✅ Données chargées")
        else:
            st.error("❌ Erreur données")
        
        st.markdown("**OPCOPILOT v4.0**")
        st.markdown("*SPIC Guadeloupe*")
        st.markdown("*Architecture ACO-centrique*")
        
        # Bouton déconnexion
        if st.button("🚪 Déconnexion", use_container_width=True, type="primary"):
            logout()
            st.rerun()
    
    # Routage des pages authentifiées
    current_page = st.session_state.page
    
    if current_page == "dashboard":
        page_dashboard()
    elif current_page == "portefeuille":
        page_portefeuille_aco()
    elif current_page == "creation_operation":
        page_creation_operation()
    elif current_page == "operation_details":
        page_operation_details()
    elif current_page == "gestion_freins":
        page_gestion_freins()
    elif current_page == "planning_echeances":
        page_planning_echeances()
    elif current_page == "admin":
        page_admin()
    else:
        # Page par défaut
        page_dashboard()

if __name__ == "__main__":
    main()
