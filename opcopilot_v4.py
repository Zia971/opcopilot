"""
OPCOPILOT v4.0 - Application Streamlit complète avec authentification CORRIGÉE
Gestion d'opérations immobilières pour ACO SPIC Guadeloupe
Architecture ACO-centrique avec Timeline horizontale obligatoire
VERSION MODERNISÉE - Dégradé violet-bleu-vert
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

# CSS personnalisé MODERNISÉ avec dégradé violet-bleu-vert
st.markdown("""
<style>
    /* THÈME MODERNE VIOLET-BLEU-VERT - GLOBAL */
    .stApp {
        background-color: #F9FAFB !important;
        font-family: 'Inter', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* SUPPRESSION DU THÈME SOMBRE */
    .stApp > div {
        background-color: #F9FAFB !important;
    }
    
    .main-header {
        background: linear-gradient(135deg, #8B5CF6 0%, #3B82F6 50%, #10B981 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 10px 25px rgba(139, 92, 246, 0.2);
        text-align: center;
    }
    
    .main-header h1 {
        margin: 0;
        font-size: 2.5rem;
        font-weight: 700;
        text-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .main-header h2 {
        margin: 0.5rem 0 0 0;
        font-size: 1.5rem;
        font-weight: 400;
        opacity: 0.9;
    }
    
    .main-header p {
        margin: 0.5rem 0 0 0;
        font-size: 1.1rem;
        opacity: 0.8;
    }
    
    /* PAGE DE CONNEXION - MODE CLAIR MODERNE */
    .login-container {
        background: white !important;
        border-radius: 16px;
        padding: 3rem;
        box-shadow: 0 20px 50px rgba(139, 92, 246, 0.15);
        border: 1px solid #E5E7EB;
        max-width: 450px;
        margin: 2rem auto;
    }
    
    .login-title {
        text-align: center;
        color: #1F2937 !important;
        font-size: 2.2rem;
        font-weight: 700;
        margin-bottom: 1rem;
        background: linear-gradient(135deg, #8B5CF6, #3B82F6, #10B981);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .login-subtitle {
        text-align: center;
        color: #6B7280 !important;
        font-size: 1rem;
        margin-bottom: 2rem;
        font-weight: 400;
    }
    
    /* FORMULAIRES MODE CLAIR */
    .stTextInput > div > div > input {
        background-color: #F9FAFB !important;
        border: 2px solid #E5E7EB !important;
        border-radius: 10px !important;
        color: #1F2937 !important;
        padding: 0.75rem !important;
        font-size: 1rem !important;
        transition: all 0.3s ease !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #8B5CF6 !important;
        box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.1) !important;
    }
    
    /* BOUTONS MODERNES DÉGRADÉ */
    .stButton > button {
        background: linear-gradient(135deg, #8B5CF6 0%, #3B82F6 50%, #10B981 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.75rem 1.5rem !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 8px 32px rgba(139, 92, 246, 0.25) !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 12px 40px rgba(139, 92, 246, 0.35) !important;
    }
    
    /* BOUTONS SECONDAIRES */
    .stButton > button[kind="secondary"] {
        background: white !important;
        color: #8B5CF6 !important;
        border: 2px solid #8B5CF6 !important;
        box-shadow: 0 4px 12px rgba(139, 92, 246, 0.15) !important;
    }
    
    .stButton > button[kind="secondary"]:hover {
        background: linear-gradient(135deg, #8B5CF6 0%, #3B82F6 50%, #10B981 100%) !important;
        color: white !important;
    }
    
    .operation-card {
        background: white;
        border: 1px solid #E5E7EB;
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 8px 32px rgba(139, 92, 246, 0.1);
        border-left: 4px solid;
        border-image: linear-gradient(135deg, #8B5CF6, #3B82F6, #10B981) 1;
        transition: all 0.3s ease;
    }
    
    .operation-card:hover {
        box-shadow: 0 12px 40px rgba(139, 92, 246, 0.2);
        transform: translateY(-2px);
    }
    
    .kpi-card {
        background: white;
        border: 1px solid #E5E7EB;
        border-radius: 20px;
        padding: 2rem;
        text-align: center;
        margin: 0.5rem;
        box-shadow: 0 10px 40px rgba(139, 92, 246, 0.15);
        border: 2px solid transparent;
        background-clip: padding-box;
        transition: all 0.4s ease;
        cursor: pointer;
        position: relative;
        overflow: hidden;
    }
    
    .kpi-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        border-radius: 20px;
        padding: 2px;
        background: linear-gradient(135deg, #8B5CF6, #3B82F6, #10B981);
        -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
        -webkit-mask-composite: xor;
        mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
        mask-composite: exclude;
    }
    
    .kpi-card:hover {
        box-shadow: 0 20px 60px rgba(139, 92, 246, 0.25);
        transform: translateY(-5px) scale(1.02);
    }
    
    .kpi-card.primary {
        background: linear-gradient(135deg, #8B5CF6 0%, #3B82F6 50%, #10B981 100%);
        color: white;
        border: none;
    }
    
    .kpi-card.primary::before {
        display: none;
    }
    
    .kpi-card.success {
        background: linear-gradient(135deg, #10B981 0%, #059669 100%);
        color: white;
        border: none;
    }
    
    .kpi-card.success::before {
        display: none;
    }
    
    .kpi-card.warning {
        background: linear-gradient(135deg, #F59E0B 0%, #D97706 100%);
        color: white;
        border: none;
    }
    
    .kpi-card.warning::before {
        display: none;
    }
    
    .kpi-card.danger {
        background: linear-gradient(135deg, #EF4444 0%, #DC2626 100%);
        color: white;
        border: none;
    }
    
    .kpi-card.danger::before {
        display: none;
    }
    
    .timeline-container {
        background: white;
        border-radius: 15px;
        padding: 2rem;
        margin: 1rem 0;
        box-shadow: 0 8px 32px rgba(139, 92, 246, 0.15);
        border-left: 4px solid;
        border-image: linear-gradient(135deg, #8B5CF6, #3B82F6, #10B981) 1;
    }
    
    .module-tab {
        background: white;
        border: 1px solid #E5E7EB;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 0.5rem;
        border-left: 4px solid;
        border-image: linear-gradient(135deg, #8B5CF6, #3B82F6, #10B981) 1;
        box-shadow: 0 4px 16px rgba(139, 92, 246, 0.1);
    }
    
    .alert-critical { 
        background: #FEF2F2; 
        border-left: 4px solid #EF4444; 
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 10px;
        border: 1px solid #FECACA;
    }
    
    .alert-warning { 
        background: #FFFBEB; 
        border-left: 4px solid #F59E0B; 
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 10px;
        border: 1px solid #FED7AA;
    }
    
    .alert-info { 
        background: #EFF6FF; 
        border-left: 4px solid #8B5CF6; 
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 10px;
        border: 1px solid #BFDBFE;
    }
    
    .metric-card {
        background: white;
        border: 1px solid #E5E7EB;
        border-radius: 10px;
        padding: 1.5rem;
        text-align: center;
        margin: 0.5rem;
        box-shadow: 0 4px 16px rgba(139, 92, 246, 0.1);
        border-left: 4px solid;
        border-image: linear-gradient(135deg, #8B5CF6, #3B82F6, #10B981) 1;
    }
    
    .sidebar-header {
        background: linear-gradient(135deg, #8B5CF6 0%, #3B82F6 50%, #10B981 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        text-align: center;
        box-shadow: 0 4px 16px rgba(139, 92, 246, 0.2);
    }
    
    .success-message {
        background: #F0FDF4;
        border: 1px solid #BBF7D0;
        color: #166534;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        font-weight: 500;
        border-left: 4px solid #10B981;
    }
    
    .error-message {
        background: #FEF2F2;
        border: 1px solid #FECACA;
        color: #DC2626;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        font-weight: 500;
        border-left: 4px solid #EF4444;
    }
    
    /* LABELS ET TEXTES */
    .stMarkdown p, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        color: #1F2937 !important;
    }
    
    /* SIDEBAR RESTAURÉE à l'état original */
    .css-1d391kg {
        background-color: #F8FAFC !important;
    }
    
    .stSidebar {
        background-color: #F8FAFC !important;
    }
    
    /* MESSAGES STREAMLIT MODERNISÉS */
    .stSuccess {
        background: linear-gradient(135deg, #F0FDF4 0%, #ECFDF5 100%) !important;
        border: 1px solid #BBF7D0 !important;
        color: #166534 !important;
        border-radius: 10px !important;
        border-left: 4px solid #10B981 !important;
    }
    
    .stError {
        background: linear-gradient(135deg, #FEF2F2 0%, #FEF2F2 100%) !important;
        border: 1px solid #FECACA !important;
        color: #DC2626 !important;
        border-radius: 10px !important;
        border-left: 4px solid #EF4444 !important;
    }
    
    .stWarning {
        background: linear-gradient(135deg, #FFFBEB 0%, #FFFBEB 100%) !important;
        border: 1px solid #FED7AA !important;
        color: #D97706 !important;
        border-radius: 10px !important;
        border-left: 4px solid #F59E0B !important;
    }
    
    .stInfo {
        background: linear-gradient(135deg, #EFF6FF 0%, #DBEAFE 100%) !important;
        border: 1px solid #BFDBFE !important;
        color: #1E40AF !important;
        border-radius: 10px !important;
        border-left: 4px solid #8B5CF6 !important;
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# SYSTÈME D'AUTHENTIFICATION CORRIGÉ
# ==============================================================================

# Base de données ACO CORRIGÉE avec les identifiants requis
DEMO_ACO_USERS = {
    # IDENTIFIANTS REQUIS POUR LES TESTS
    "aco1": {
        "password": "password1",
        "nom": "Pierre DUPONT",
        "role": "ACO",
        "secteur": "Les Abymes - Pointe-à-Pitre",
        "operations": 18
    },
    "aco2": {
        "password": "password2",
        "nom": "Sophie MARTIN",
        "role": "ACO_SENIOR",
        "secteur": "Basse-Terre - Sainte-Anne",
        "operations": 25
    },
    "aco3": {
        "password": "password3",
        "nom": "Alexandre BERNARD",
        "role": "ACO",
        "secteur": "Baie-Mahault - Lamentin",
        "operations": 12
    },
    # IDENTIFIANTS DEMO ORIGINAUX
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
    """Vérification des identifiants CORRIGÉE"""
    if username in DEMO_ACO_USERS:
        stored_password = DEMO_ACO_USERS[username]["password"]
        return stored_password == password  # Comparaison directe pour la démo
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
        st.session_state.page = "login"
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
# PAGES D'AUTHENTIFICATION CORRIGÉES ET MODERNISÉES
# ==============================================================================

def page_login():
    """Page de connexion moderne CORRIGÉE - ÉLÉMENTS TEST SUPPRIMÉS"""
    
    # En-tête moderne avec dégradé violet-bleu-vert
    st.markdown("""
    <div class="main-header">
        <h1>🏗️ OPCOPILOT v4.0</h1>
        <h2>Tableau de Bord Opérationnel</h2>
        <p>SPIC Guadeloupe - Interface de Gestion d'Opérations Immobilières</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Container principal centré
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        
        # Titre de connexion
        st.markdown("""
        <div class="login-title">🔐 Connexion ACO</div>
        <div class="login-subtitle">Accédez à votre espace de travail sécurisé</div>
        """, unsafe_allow_html=True)
        
        # Formulaire de connexion CORRIGÉ
        with st.form("login_form", clear_on_submit=False):
            
            username = st.text_input(
                "👤 Identifiant",
                placeholder="Saisissez votre identifiant ACO",
                help="Utilisez votre identifiant personnel SPIC",
                key="login_username"
            )
            
            password = st.text_input(
                "🔑 Mot de passe",
                type="password",
                placeholder="Saisissez votre mot de passe",
                help="Mot de passe fourni par l'administration",
                key="login_password"
            )
            
            col_btn1, col_btn2 = st.columns([2, 1])
            
            with col_btn1:
                login_submitted = st.form_submit_button(
                    "🚀 Se connecter",
                    use_container_width=True,
                    type="primary"
                )
            
            with col_btn2:
                if st.form_submit_button("🔄 Mot de passe oublié?", use_container_width=True):
                    st.session_state.page = "reset_password"
                    st.rerun()
        
        # TRAITEMENT CONNEXION CORRIGÉ
        if login_submitted:
            if username and password:
                if verify_password(username, password):
                    # Connexion réussie
                    st.session_state.authenticated = True
                    st.session_state.aco_user = username
                    st.session_state.user_data = DEMO_ACO_USERS[username]
                    st.session_state.page = "dashboard"
                    
                    # Message de succès
                    st.markdown("""
                    <div class="success-message">
                        ✅ <strong>Connexion réussie !</strong><br>
                        Redirection vers votre tableau de bord...
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Redirection automatique
                    st.rerun()
                else:
                    # Erreur d'authentification
                    st.markdown("""
                    <div class="error-message">
                        ❌ <strong>Identifiants incorrects</strong><br>
                        Vérifiez votre nom d'utilisateur et mot de passe.
                    </div>
                    """, unsafe_allow_html=True)
            else:
                # Champs manquants
                st.markdown("""
                <div class="error-message">
                    ⚠️ <strong>Champs obligatoires</strong><br>
                    Veuillez remplir votre identifiant et mot de passe.
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # ÉLÉMENTS TEST SUPPRIMÉS - Plus de comptes de démonstration ni de boutons rapides
    # Interface épurée et professionnelle

def page_reset_password():
    """Page de réinitialisation mot de passe"""
    st.markdown("""
    <div class="main-header">
        <h1>🔄 Réinitialisation Mot de Passe</h1>
        <p>OPCOPILOT v4.0 - SPIC Guadeloupe</p>
    </div>
    """, unsafe_allow_html=True)
    
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
# 1. CONFIGURATION & CHARGEMENT DONNÉES (CRÉER DONNÉES DEMO SI NÉCESSAIRE)
# ==============================================================================

@st.cache_data
def load_demo_data():
    """Charge demo_data.json avec données de fallback"""
    try:
        with open('data/demo_data.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        # Données de fallback si le fichier n'existe pas
        return create_fallback_demo_data()
    except json.JSONDecodeError:
        st.error("❌ Erreur format JSON dans demo_data.json")
        return create_fallback_demo_data()

def create_fallback_demo_data():
    """Crée des données de démonstration de fallback"""
    return {
        'operations_demo': [
            {
                'id': 1,
                'nom': 'RÉSIDENCE SOLEIL',
                'type_operation': 'OPP',
                'commune': 'Les Abymes',
                'statut': 'EN_COURS',
                'avancement': 75,
                'budget_total': 2450000,
                'nb_logements_total': 45,
                'date_creation': '2023-03-15',
                'date_debut_prevue': '2023-06-01',
                'date_fin_prevue': '2025-12-31',
                'freins_actifs': 1
            },
            {
                'id': 2,
                'nom': 'COUR CHARNEAU',
                'type_operation': 'OPP',
                'commune': 'Pointe-à-Pitre',
                'statut': 'EN_RECEPTION',
                'avancement': 95,
                'budget_total': 1850000,
                'nb_logements_total': 32,
                'date_creation': '2022-09-10',
                'date_debut_prevue': '2023-01-15',
                'date_fin_prevue': '2024-11-30',
                'freins_actifs': 0
            },
            {
                'id': 3,
                'nom': 'VEFA BELCOURT',
                'type_operation': 'VEFA',
                'commune': 'Basse-Terre',
                'statut': 'EN_COURS',
                'avancement': 45,
                'budget_total': 1650000,
                'nb_logements_total': 28,
                'date_creation': '2024-01-20',
                'date_debut_prevue': '2024-03-01',
                'date_fin_prevue': '2026-06-30',
                'freins_actifs': 2
            }
        ],
        'phases_demo': {
            'operation_1': [
                {
                    'nom': 'Faisabilité',
                    'date_debut_prevue': '2023-06-01',
                    'date_fin_prevue': '2023-08-31',
                    'statut': 'VALIDEE',
                    'responsable': 'ACO',
                    'est_critique': True
                },
                {
                    'nom': 'Esquisse',
                    'date_debut_prevue': '2023-09-01',
                    'date_fin_prevue': '2023-11-30',
                    'statut': 'VALIDEE',
                    'responsable': 'MOE',
                    'est_critique': True
                },
                {
                    'nom': 'Avant-Projet',
                    'date_debut_prevue': '2023-12-01',
                    'date_fin_prevue': '2024-03-31',
                    'statut': 'EN_COURS',
                    'responsable': 'MOE',
                    'est_critique': True
                },
                {
                    'nom': 'Permis de Construire',
                    'date_debut_prevue': '2024-04-01',
                    'date_fin_prevue': '2024-10-31',
                    'statut': 'EN_ATTENTE',
                    'responsable': 'Commune',
                    'est_critique': True
                },
                {
                    'nom': 'Consultation Entreprises',
                    'date_debut_prevue': '2024-11-01',
                    'date_fin_prevue': '2025-02-28',
                    'statut': 'NON_DEMARREE',
                    'responsable': 'ACO',
                    'est_critique': False
                },
                {
                    'nom': 'Travaux',
                    'date_debut_prevue': '2025-03-01',
                    'date_fin_prevue': '2025-10-31',
                    'statut': 'NON_DEMARREE',
                    'responsable': 'Entreprise',
                    'est_critique': True
                }
            ]
        },
        'kpis_aco_demo': {
            'operations_actives': 23,
            'operations_cloturees': 5,
            'rem_realisee_2024': 485000,
            'rem_prevue_2024': 620000,
            'taux_realisation_rem': 78,
            'freins_actifs': 3,
            'freins_critiques': 2,
            'echeances_semaine': 5,
            'validations_requises': 12
        },
        'activite_mensuelle_demo': {
            'mois': ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Jun', 'Jul', 'Aoû', 'Sep', 'Oct'],
            'rem_mensuelle': [45000, 52000, 48000, 55000, 49000, 61000, 58000, 47000, 53000, 62000],
            'operations_actives': [18, 19, 20, 22, 21, 23, 24, 23, 22, 23]
        },
        'alertes_demo': [
            {
                'operation': 'COUR CHARNEAU',
                'type': 'CRITIQUE',
                'message': 'Retard 5 jours sur réception provisoire',
                'action_requise': 'Relancer MOE immédiatement'
            },
            {
                'operation': 'VEFA BELCOURT',
                'type': 'WARNING',
                'message': 'Validation promoteur en attente',
                'action_requise': 'RDV programmé cette semaine'
            },
            {
                'operation': 'RÉSIDENCE SOLEIL',
                'type': 'INFO',
                'message': 'Phase Travaux en cours - bon avancement',
                'action_requise': 'Suivi hebdomadaire maintenu'
            }
        ]
    }

@st.cache_data
def load_templates_phases():
    """Charge templates_phases.json avec données de fallback"""
    try:
        with open('data/templates_phases.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        # Template de fallback
        return {
            'OPP': {
                'nom': 'Opération Propre Programmée',
                'description': 'Construction neuve de logements sociaux',
                'nb_phases': 8,
                'phases': [
                    {'nom': 'Faisabilité', 'duree_jours': 90, 'responsable_type': 'ACO', 'est_critique': True},
                    {'nom': 'Esquisse', 'duree_jours': 60, 'responsable_type': 'MOE', 'est_critique': True},
                    {'nom': 'Avant-Projet', 'duree_jours': 120, 'responsable_type': 'MOE', 'est_critique': True},
                    {'nom': 'Permis de Construire', 'duree_jours': 180, 'responsable_type': 'Commune', 'est_critique': True},
                    {'nom': 'Consultation Entreprises', 'duree_jours': 90, 'responsable_type': 'ACO', 'est_critique': False},
                    {'nom': 'Travaux', 'duree_jours': 360, 'responsable_type': 'Entreprise', 'est_critique': True},
                    {'nom': 'Réception', 'duree_jours': 30, 'responsable_type': 'ACO', 'est_critique': True},
                    {'nom': 'Livraison', 'duree_jours': 30, 'responsable_type': 'ACO', 'est_critique': False}
                ]
            },
            'VEFA': {
                'nom': 'Vente en État Futur d\'Achèvement',
                'description': 'Acquisition de logements sur plan',
                'nb_phases': 6,
                'phases': [
                    {'nom': 'Négociation promoteur', 'duree_jours': 60, 'responsable_type': 'ACO', 'est_critique': True},
                    {'nom': 'Signature protocole', 'duree_jours': 30, 'responsable_type': 'ACO', 'est_critique': True},
                    {'nom': 'Suivi travaux', 'duree_jours': 300, 'responsable_type': 'Promoteur', 'est_critique': False},
                    {'nom': 'Réception logements', 'duree_jours': 30, 'responsable_type': 'ACO', 'est_critique': True},
                    {'nom': 'Mise en location', 'duree_jours': 60, 'responsable_type': 'SPIC', 'est_critique': False},
                    {'nom': 'Garantie parfait achèvement', 'duree_jours': 365, 'responsable_type': 'ACO', 'est_critique': False}
                ]
            }
        }
    except json.JSONDecodeError:
        st.error("❌ Erreur format JSON dans templates_phases.json")
        return {}

def get_couleur_statut(statut):
    """Retourne la couleur selon le statut de phase"""
    couleurs = {
        "VALIDEE": "#10B981",         # Vert du dégradé
        "EN_COURS": "#3B82F6",        # Bleu du dégradé
        "EN_ATTENTE": "#8B5CF6",      # Violet du dégradé
        "RETARD": "#F44336",          # Rouge
        "CRITIQUE": "#E91E63",        # Rose
        "NON_DEMARREE": "#9E9E9E",    # Gris
        "VALIDATION_REQUISE": "#FF9800",  # Orange
        "EN_REVISION": "#8B5CF6"      # Violet du dégradé
    }
    return couleurs.get(statut, "#8B5CF6")

# ==============================================================================
# 2. TIMELINE HORIZONTALE OBLIGATOIRE (IDENTIQUE MAIS COULEURS MODERNISÉES)
# ==============================================================================

def create_timeline_horizontal(operation_data, phases_data):
    """
    Timeline Plotly style INFOGRAPHIQUE MODERNE avec gestion d'erreur robuste
    Reproduit le style roadmap professionnel avec validation complète des données
    MODERNISÉE avec dégradé violet-bleu-vert
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
# 3. MODULES INTÉGRÉS PAR OPÉRATION (SIMPLIFIÉS POUR LA DÉMO)
# ==============================================================================

def module_rem(operation_id):
    """Module REM intégré dans l'opération"""
    st.markdown("### 💰 Module REM - Suivi Trimestriel")
    st.info("📊 Module REM en cours de développement - Version complète disponible prochainement")

def module_avenants(operation_id):
    """Module Avenants intégré dans l'opération"""
    st.markdown("### 📝 Module Avenants")
    st.info("📝 Module Avenants en cours de développement - Version complète disponible prochainement")

def module_med(operation_id):
    """Module MED Automatisé intégré dans l'opération"""
    st.markdown("### ⚖️ Module MED Automatisé")
    st.info("⚖️ Module MED en cours de développement - Version complète disponible prochainement")

def module_concessionnaires(operation_id):
    """Module Concessionnaires intégré dans l'opération"""
    st.markdown("### 🔌 Module Concessionnaires")
    st.info("🔌 Module Concessionnaires en cours de développement - Version complète disponible prochainement")

def module_dgd(operation_id):
    """Module DGD intégré dans l'opération"""
    st.markdown("### 📊 Module DGD - Décompte Général Définitif")
    st.info("📊 Module DGD en cours de développement - Version complète disponible prochainement")

def module_gpa(operation_id):
    """Module GPA intégré dans l'opération"""
    st.markdown("### 🛡️ Module GPA - Garantie Parfait Achèvement")
    st.info("🛡️ Module GPA en cours de développement - Version complète disponible prochainement")

def module_cloture(operation_id):
    """Module Clôture intégré dans l'opération"""
    st.markdown("### ✅ Module Clôture - Finalisation Opération")
    st.info("✅ Module Clôture en cours de développement - Version complète disponible prochainement")

# ==============================================================================
# 4. NAVIGATION ACO-CENTRIQUE
# ==============================================================================

def page_dashboard():
    """Dashboard principal avec KPIs ACO INTERACTIFS MODERNISÉS"""
    
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
    
    # KPIs personnels ACO INTERACTIFS MODERNISÉS
    st.markdown("### 📊 Mes Indicateurs Clés de Performance")
    
    # CSS spécifique pour KPIs UNIQUEMENT
    st.markdown("""
    <style>
    /* STYLES KPIs UNIQUEMENT - COULEURS STRATÉGIQUES MÉTIER */
    
    /* KPI OPÉRATIONS - Bleu professionnel (confiance, stabilité) */
    .kpi-operations {
        background: linear-gradient(145deg, #3B82F6, #2563EB);
        color: white;
        min-height: 180px !important;
        max-height: 180px !important;
        border-radius: 20px;
        padding: 1.5rem;
        box-shadow: 0 10px 40px rgba(59, 130, 246, 0.3);
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        cursor: pointer;
        margin-bottom: 1rem;
    }
    
    /* KPI REM - Vert performance (succès, croissance) */
    .kpi-rem {
        background: linear-gradient(145deg, #10B981, #059669);
        color: white;
        min-height: 180px !important;
        max-height: 180px !important;
        border-radius: 20px;
        padding: 1.5rem;
        box-shadow: 0 10px 40px rgba(16, 185, 129, 0.3);
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        cursor: pointer;
        margin-bottom: 1rem;
    }
    
    /* KPI FREINS - Orange vigilance (attention, action requise) */
    .kpi-freins {
        background: linear-gradient(145deg, #F59E0B, #D97706);
        color: white;
        min-height: 180px !important;
        max-height: 180px !important;
        border-radius: 20px;
        padding: 1.5rem;
        box-shadow: 0 10px 40px rgba(245, 158, 11, 0.3);
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        cursor: pointer;
        margin-bottom: 1rem;
    }
    
    /* KPI ÉCHÉANCES - Rouge urgence (priorité absolue) */
    .kpi-echeances {
        background: linear-gradient(145deg, #EF4444, #DC2626);
        color: white;
        min-height: 180px !important;
        max-height: 180px !important;
        border-radius: 20px;
        padding: 1.5rem;
        box-shadow: 0 10px 40px rgba(239, 68, 68, 0.3);
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        cursor: pointer;
        margin-bottom: 1rem;
    }
    
    /* ICÔNES 3D MODERNES AVEC EFFETS */
    .kpi-icon-operations {
        background: linear-gradient(145deg, #60A5FA, #3B82F6);
        width: 60px;
        height: 60px;
        border-radius: 16px;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 
            0 8px 16px rgba(0, 0, 0, 0.1),
            inset 0 1px 2px rgba(255, 255, 255, 0.2);
        margin: 0 auto 1rem auto;
        position: relative;
    }
    
    .kpi-icon-operations::before {
        content: "📁";
        font-size: 32px;
        filter: drop-shadow(4px 4px 8px rgba(59, 130, 246, 0.6));
    }
    
    .kpi-icon-rem {
        background: linear-gradient(145deg, #34D399, #10B981);
        width: 60px;
        height: 60px;
        border-radius: 16px;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 
            0 8px 16px rgba(0, 0, 0, 0.1),
            inset 0 1px 2px rgba(255, 255, 255, 0.2);
        margin: 0 auto 1rem auto;
        position: relative;
    }
    
    .kpi-icon-rem::before {
        content: "€";
        font-size: 32px;
        color: #FFD700;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
        filter: drop-shadow(3px 3px 6px rgba(255, 215, 0, 0.8));
        font-weight: bold;
    }
    
    .kpi-icon-freins {
        background: linear-gradient(145deg, #FBBF24, #F59E0B);
        width: 60px;
        height: 60px;
        border-radius: 16px;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 
            0 8px 16px rgba(0, 0, 0, 0.1),
            inset 0 1px 2px rgba(255, 255, 255, 0.2);
        margin: 0 auto 1rem auto;
        position: relative;
    }
    
    .kpi-icon-freins::before {
        content: "⚠️";
        font-size: 32px;
        filter: drop-shadow(3px 3px 6px rgba(245, 158, 11, 0.8));
    }
    
    .kpi-icon-echeances {
        background: linear-gradient(145deg, #F87171, #EF4444);
        width: 60px;
        height: 60px;
        border-radius: 16px;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 
            0 8px 16px rgba(0, 0, 0, 0.1),
            inset 0 1px 2px rgba(255, 255, 255, 0.2);
        margin: 0 auto 1rem auto;
        position: relative;
    }
    
    .kpi-icon-echeances::before {
        content: "📅";
        font-size: 32px;
        filter: drop-shadow(3px 3px 6px rgba(239, 68, 68, 0.8));
    }
    
    /* BOUTONS UNIFORMES 45px */
    .kpi-button {
        background: rgba(255, 255, 255, 0.2) !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
        min-height: 45px !important;
        max-height: 45px !important;
        border-radius: 12px !important;
        color: white !important;
        font-weight: 600 !important;
        margin-top: auto;
        transition: all 0.3s ease;
        padding: 0.5rem 1rem;
    }
    
    .kpi-button:hover {
        background: rgba(255, 255, 255, 0.3) !important;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }
    
    /* EFFETS HOVER CARDS */
    .kpi-operations:hover, .kpi-rem:hover, .kpi-freins:hover, .kpi-echeances:hover {
        transform: translateY(-8px);
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
    }
    
    /* CONTENU CENTRÉ DANS LES CARDS */
    .kpi-content {
        flex-grow: 1;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        text-align: center;
        color: white !important;
    }
    
    /* GROS CHIFFRE BLANC */
    .kpi-value {
        font-size: 2.5rem !important;
        font-weight: bold !important;
        color: white !important;
        margin: 0.5rem 0 !important;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
    }
    
    /* LABEL PRINCIPAL BLANC */
    .kpi-label {
        font-size: 1rem !important;
        font-weight: 600 !important;
        color: white !important;
        margin-bottom: 0.25rem !important;
        text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
    }
    
    /* DÉTAIL BLANC */
    .kpi-detail {
        font-size: 0.875rem !important;
        color: rgba(255, 255, 255, 0.9) !important;
        margin-bottom: 1rem !important;
        text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
    }
    </style>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4, gap="medium")
    
    with col1:
        operations_actives = kpis_data.get('operations_actives', 23)
        operations_cloturees = kpis_data.get('operations_cloturees', 5)
        
        st.markdown(f"""
        <div style="background: linear-gradient(145deg, #3B82F6, #2563EB); color: white; min-height: 180px; border-radius: 20px; padding: 1.5rem; box-shadow: 0 10px 40px rgba(59, 130, 246, 0.3); display: flex; flex-direction: column; justify-content: space-between; margin-bottom: 1rem;">
            <div style="flex-grow: 1; display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center;">
                <div class="kpi-icon-operations"></div>
                <div style="font-size: 2.5rem; font-weight: bold; color: white; margin: 0.5rem 0; text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);">{operations_actives}</div>
                <div style="font-size: 1rem; font-weight: 600; color: white; margin-bottom: 0.25rem;">Opérations Actives</div>
                <div style="font-size: 0.875rem; color: rgba(255, 255, 255, 0.9);">{operations_cloturees} clôturées</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("📂 Voir Portfolio", key="btn_operations", use_container_width=True, type="primary"):
            st.session_state.page = "portefeuille"
            st.rerun()
    
    with col2:
        rem_realise = kpis_data.get('rem_realisee_2024', 485000)
        rem_prevu = kpis_data.get('rem_prevue_2024', 620000)
        taux_real = kpis_data.get('taux_realisation_rem', 78)
        
        st.markdown(f"""
        <div style="background: linear-gradient(145deg, #10B981, #059669); color: white; min-height: 180px; border-radius: 20px; padding: 1.5rem; box-shadow: 0 10px 40px rgba(16, 185, 129, 0.3); display: flex; flex-direction: column; justify-content: space-between; margin-bottom: 1rem;">
            <div style="flex-grow: 1; display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center;">
                <div class="kpi-icon-rem"></div>
                <div style="font-size: 2.5rem; font-weight: bold; color: white; margin: 0.5rem 0; text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);">{rem_realise/1000:.0f}k€</div>
                <div style="font-size: 1rem; font-weight: 600; color: white; margin-bottom: 0.25rem;">REM Réalisée 2024</div>
                <div style="font-size: 0.875rem; color: rgba(255, 255, 255, 0.9);">{taux_real}% / {rem_prevu/1000:.0f}k€ prévue</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("💰 Analyse REM", key="btn_rem", use_container_width=True, type="primary"):
            st.info("📊 Analyse REM détaillée - En développement")
    
    with col3:
        freins_actifs = kpis_data.get('freins_actifs', 3)
        freins_critiques = kpis_data.get('freins_critiques', 2)
        
        st.markdown(f"""
        <div style="background: linear-gradient(145deg, #F59E0B, #D97706); color: white; min-height: 180px; border-radius: 20px; padding: 1.5rem; box-shadow: 0 10px 40px rgba(245, 158, 11, 0.3); display: flex; flex-direction: column; justify-content: space-between; margin-bottom: 1rem;">
            <div style="flex-grow: 1; display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center;">
                <div class="kpi-icon-freins"></div>
                <div style="font-size: 2.5rem; font-weight: bold; color: white; margin: 0.5rem 0; text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);">{freins_actifs}</div>
                <div style="font-size: 1rem; font-weight: 600; color: white; margin-bottom: 0.25rem;">Freins Actifs</div>
                <div style="font-size: 0.875rem; color: rgba(255, 255, 255, 0.9);">{freins_critiques} critiques</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🚨 Gérer Freins", key="btn_freins", use_container_width=True, type="primary"):
            st.session_state.page = "gestion_freins"
            st.rerun()
    
    with col4:
        echeances = kpis_data.get('echeances_semaine', 5)
        validations = kpis_data.get('validations_requises', 12)
        
        st.markdown(f"""
        <div style="background: linear-gradient(145deg, #EF4444, #DC2626); color: white; min-height: 180px; border-radius: 20px; padding: 1.5rem; box-shadow: 0 10px 40px rgba(239, 68, 68, 0.3); display: flex; flex-direction: column; justify-content: space-between; margin-bottom: 1rem;">
            <div style="flex-grow: 1; display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center;">
                <div class="kpi-icon-echeances"></div>
                <div style="font-size: 2.5rem; font-weight: bold; color: white; margin: 0.5rem 0; text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);">{echeances}</div>
                <div style="font-size: 1rem; font-weight: 600; color: white; margin-bottom: 0.25rem;">Échéances Semaine</div>
                <div style="font-size: 0.875rem; color: rgba(255, 255, 255, 0.9);">{validations} validations requises</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("📅 Planning", key="btn_echeances", use_container_width=True, type="primary"):
            st.session_state.page = "planning_echeances"
            st.rerun()
    
    # Alertes et actions MODERNISÉES ET SIMPLIFIÉES
    st.markdown("### 🚨 Alertes et Actions Prioritaires")
    
    # CSS simplifié pour actions réalisées uniquement
    st.markdown("""
    <style>
    /* SIDEBAR RESTAURÉE à l'état original */
    .css-1d391kg {
        background-color: #F8FAFC !important;
    }
    
    .stSidebar {
        background-color: #F8FAFC !important;
    }
    
    /* ACTIONS RÉALISÉES - VERT FORCÉ (pas violet) */
    .stButton > button[data-testid="baseButton-primary"] {
        background: linear-gradient(145deg, #10B981, #D1FAE5) !important;
        border: none !important;
        border-left: 4px solid #10B981 !important;
        border-radius: 15px !important;
        padding: 1rem !important;
        box-shadow: 0 4px 15px rgba(16, 185, 129, 0.15) !important;
        transition: all 0.3s ease !important;
        width: 100% !important;
        color: white !important;
        font-weight: 600 !important;
        text-align: left !important;
        white-space: pre-line !important;
    }
    
    .stButton > button[data-testid="baseButton-primary"]:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(16, 185, 129, 0.25) !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    col_alert1, col_alert2 = st.columns(2)
    
    with col_alert1:
        st.markdown("#### Alertes Critiques")
        
        # Boutons cachés pour la navigation (invisibles)
        if st.button("nav_cour_charneau", key="hidden_cour_charneau"):
            # Navigation vers COUR CHARNEAU
            demo_data = load_demo_data()
            operations = demo_data.get('operations_demo', [])
            cour_charneau = next((op for op in operations if "COUR CHARNEAU" in op['nom']), None)
            if cour_charneau:
                st.session_state.selected_operation = cour_charneau
                st.session_state.selected_operation_id = cour_charneau['id']
                st.session_state.page = "operation_details"
                st.rerun()
        
        if st.button("nav_vefa_belcourt", key="hidden_vefa_belcourt"):
            # Navigation vers VEFA BELCOURT
            demo_data = load_demo_data()
            operations = demo_data.get('operations_demo', [])
            vefa_belcourt = next((op for op in operations if "VEFA BELCOURT" in op['nom']), None)
            if vefa_belcourt:
                st.session_state.selected_operation = vefa_belcourt
                st.session_state.selected_operation_id = vefa_belcourt['id']
                st.session_state.page = "operation_details"
                st.rerun()
        
        if st.button("nav_residence_soleil", key="hidden_residence_soleil"):
            # Navigation vers RÉSIDENCE SOLEIL
            demo_data = load_demo_data()
            operations = demo_data.get('operations_demo', [])
            residence_soleil = next((op for op in operations if "RÉSIDENCE SOLEIL" in op['nom']), None)
            if residence_soleil:
                st.session_state.selected_operation = residence_soleil
                st.session_state.selected_operation_id = residence_soleil['id']
                st.session_state.page = "operation_details"
                st.rerun()
            # Navigation vers RÉSIDENCE SOLEIL
            demo_data = load_demo_data()
            operations = demo_data.get('operations_demo', [])
            residence_soleil = next((op for op in operations if "RÉSIDENCE SOLEIL" in op['nom']), None)
            if residence_soleil:
                st.session_state.selected_operation = residence_soleil
                st.session_state.selected_operation_id = residence_soleil['id']
                st.session_state.page = "operation_details"
                st.rerun()
        
        # CSS pour cacher les boutons
        st.markdown("""
        <style>
        button[key="hidden_cour_charneau"],
        button[key="hidden_vefa_belcourt"], 
        button[key="hidden_residence_soleil"],
        button[key="hidden_action_1"],
        button[key="hidden_action_2"],
        button[key="hidden_action_3"],
        button[key="hidden_action_4"],
        button[key="hidden_action_5"] {
            display: none !important;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # ALERTE 1 - CRITIQUE ROUGE (Card cliquable)
        st.markdown("""
        <div style="background: linear-gradient(145deg, #FEE2E2, #FECACA); 
                    border-left: 4px solid #EF4444; 
                    border-radius: 15px; 
                    padding: 1.25rem; 
                    margin: 0.75rem 0; 
                    box-shadow: 0 6px 20px rgba(239, 68, 68, 0.15); 
                    cursor: pointer; 
                    transition: all 0.3s ease;"
             onmouseover="this.style.transform='translateY(-3px)'; this.style.boxShadow='0 8px 30px rgba(239, 68, 68, 0.25)'"
             onmouseout="this.style.transform='translateY(0px)'; this.style.boxShadow='0 6px 20px rgba(239, 68, 68, 0.15)'"
             onclick="document.querySelector('button[key=hidden_cour_charneau]').click()">
            <div style="font-weight: 700; font-size: 1.1rem; color: #DC2626; margin-bottom: 0.5rem;">🏗️ COUR CHARNEAU</div>
            <div style="color: #DC2626; margin: 0.5rem 0; font-size: 0.95rem;">Retard MOE 5 jours sur phase LBU</div>
            <div style="color: #DC2626; font-style: italic; font-size: 0.9rem; opacity: 0.9;">Action: Relance urgente MOE</div>
        </div>
        """, unsafe_allow_html=True)
        
        # ALERTE 2 - ATTENTION JAUNE (Card cliquable)
        st.markdown("""
        <div style="background: linear-gradient(145deg, #FEF3C7, #FDE68A); 
                    border-left: 4px solid #F59E0B; 
                    border-radius: 15px; 
                    padding: 1.25rem; 
                    margin: 0.75rem 0; 
                    box-shadow: 0 6px 20px rgba(245, 158, 11, 0.15); 
                    cursor: pointer; 
                    transition: all 0.3s ease;"
             onmouseover="this.style.transform='translateY(-3px)'; this.style.boxShadow='0 8px 30px rgba(245, 158, 11, 0.25)'"
             onmouseout="this.style.transform='translateY(0px)'; this.style.boxShadow='0 6px 20px rgba(245, 158, 11, 0.15)'"
             onclick="document.querySelector('button[key=hidden_vefa_belcourt]').click()">
            <div style="font-weight: 700; font-size: 1.1rem; color: #D97706; margin-bottom: 0.5rem;">🏠 VEFA BELCOURT</div>
            <div style="color: #D97706; margin: 0.5rem 0; font-size: 0.95rem;">Validation promoteur en attente</div>
            <div style="color: #D97706; font-style: italic; font-size: 0.9rem; opacity: 0.9;">Action: RDV programmé cette semaine</div>
        </div>
        """, unsafe_allow_html=True)
        
        # ALERTE 3 - INFORMATION BLEU CLAIR (Card cliquable)
        st.markdown("""
        <div style="background: linear-gradient(145deg, #DBEAFE, #BFDBFE); 
                    border-left: 4px solid #3B82F6; 
                    border-radius: 15px; 
                    padding: 1.25rem; 
                    margin: 0.75rem 0; 
                    box-shadow: 0 6px 20px rgba(59, 130, 246, 0.15); 
                    cursor: pointer; 
                    transition: all 0.3s ease;"
             onmouseover="this.style.transform='translateY(-3px)'; this.style.boxShadow='0 8px 30px rgba(59, 130, 246, 0.25)'"
             onmouseout="this.style.transform='translateY(0px)'; this.style.boxShadow='0 6px 20px rgba(59, 130, 246, 0.15)'"
             onclick="document.querySelector('button[key=hidden_residence_soleil]').click()">
            <div style="font-weight: 700; font-size: 1.1rem; color: #2563EB; margin-bottom: 0.5rem;">🏗️ RÉSIDENCE SOLEIL</div>
            <div style="color: #2563EB; margin: 0.5rem 0; font-size: 0.95rem;">Phase Travaux en cours - bon avancement</div>
            <div style="color: #2563EB; font-style: italic; font-size: 0.9rem; opacity: 0.9;">Action: Suivi hebdomadaire maintenu</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col_alert2:
        st.markdown("#### Actions Réalisées Aujourd'hui")
        
        # Boutons cachés pour les actions réalisées
        if st.button("nav_action_1", key="hidden_action_1"):
            # Navigation vers RÉSIDENCE SOLEIL + module DGD
            demo_data = load_demo_data()
            operations = demo_data.get('operations_demo', [])
            residence_soleil = next((op for op in operations if "RÉSIDENCE SOLEIL" in op['nom']), None)
            if residence_soleil:
                st.session_state.selected_operation = residence_soleil
                st.session_state.selected_operation_id = residence_soleil['id']
                st.session_state.page = "operation_details"
                st.session_state.active_tab = "dgd"
                st.rerun()
        
        if st.button("nav_action_2", key="hidden_action_2"):
            # Navigation vers COUR CHARNEAU + timeline
            demo_data = load_demo_data()
            operations = demo_data.get('operations_demo', [])
            cour_charneau = next((op for op in operations if "COUR CHARNEAU" in op['nom']), None)
            if cour_charneau:
                st.session_state.selected_operation = cour_charneau
                st.session_state.selected_operation_id = cour_charneau['id']
                st.session_state.page = "operation_details"
                st.session_state.active_tab = "timeline"
                st.rerun()
        
        if st.button("nav_action_3", key="hidden_action_3"):
            # Navigation vers gestion MED (page générale)
            st.session_state.page = "gestion_freins"
            st.rerun()
        
        if st.button("nav_action_4", key="hidden_action_4"):
            # Navigation vers analyse REM
            st.info("📊 Analyse REM détaillée - En développement")
        
        if st.button("nav_action_5", key="hidden_action_5"):
            # Navigation vers VEFA BELCOURT + timeline
            demo_data = load_demo_data()
            operations = demo_data.get('operations_demo', [])
            vefa_belcourt = next((op for op in operations if "VEFA BELCOURT" in op['nom']), None)
            if vefa_belcourt:
                st.session_state.selected_operation = vefa_belcourt
                st.session_state.selected_operation_id = vefa_belcourt['id']
                st.session_state.page = "operation_details"
                st.session_state.active_tab = "timeline"
                st.rerun()
            # Navigation vers VEFA BELCOURT + timeline
            demo_data = load_demo_data()
            operations = demo_data.get('operations_demo', [])
            vefa_belcourt = next((op for op in operations if "VEFA BELCOURT" in op['nom']), None)
            if vefa_belcourt:
                st.session_state.selected_operation = vefa_belcourt
                st.session_state.selected_operation_id = vefa_belcourt['id']
                st.session_state.page = "operation_details"
                st.session_state.active_tab = "timeline"
                st.rerun()
        
        # ACTION 1 - VERTE avec coche alignée à gauche (HTML direct cliquable)
        st.markdown("""
        <div style="background: linear-gradient(145deg, #10B981, #D1FAE5); 
                    border-left: 4px solid #10B981; 
                    border-radius: 15px; 
                    padding: 1rem; 
                    margin: 0.5rem 0; 
                    box-shadow: 0 4px 15px rgba(16, 185, 129, 0.15); 
                    cursor: pointer; 
                    transition: all 0.3s ease;
                    display: flex;
                    align-items: flex-start;"
             onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 6px 20px rgba(16, 185, 129, 0.25)'"
             onmouseout="this.style.transform='translateY(0px)'; this.style.boxShadow='0 4px 15px rgba(16, 185, 129, 0.15)'"
             onclick="document.querySelector('button[key=hidden_action_1]').click()">
            <div style="margin-right: 0.75rem; flex-shrink: 0; font-size: 1.2rem; color: white;">✅</div>
            <div style="flex-grow: 1; color: white;">
                <div style="font-weight: 600; font-size: 1rem;">DGD validé - RÉSIDENCE SOLEIL</div>
                <div style="font-size: 0.9rem; margin-top: 0.25rem; opacity: 0.9;">Décompte général définitif approuvé</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # ACTION 2 - VERTE avec coche alignée à gauche (HTML direct cliquable)
        st.markdown("""
        <div style="background: linear-gradient(145deg, #10B981, #D1FAE5); 
                    border-left: 4px solid #10B981; 
                    border-radius: 15px; 
                    padding: 1rem; 
                    margin: 0.5rem 0; 
                    box-shadow: 0 4px 15px rgba(16, 185, 129, 0.15); 
                    cursor: pointer; 
                    transition: all 0.3s ease;
                    display: flex;
                    align-items: flex-start;"
             onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 6px 20px rgba(16, 185, 129, 0.25)'"
             onmouseout="this.style.transform='translateY(0px)'; this.style.boxShadow='0 4px 15px rgba(16, 185, 129, 0.15)'"
             onclick="document.querySelector('button[key=hidden_action_2]').click()">
            <div style="margin-right: 0.75rem; flex-shrink: 0; font-size: 1.2rem; color: white;">✅</div>
            <div style="flex-grow: 1; color: white;">
                <div style="font-weight: 600; font-size: 1rem;">Phase ESQ terminée - COUR CHARNEAU</div>
                <div style="font-size: 0.9rem; margin-top: 0.25rem; opacity: 0.9;">Études esquisse validées par SPIC</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # ACTION 3 - VERTE avec coche alignée à gauche (HTML direct cliquable)
        st.markdown("""
        <div style="background: linear-gradient(145deg, #10B981, #D1FAE5); 
                    border-left: 4px solid #10B981; 
                    border-radius: 15px; 
                    padding: 1rem; 
                    margin: 0.5rem 0; 
                    box-shadow: 0 4px 15px rgba(16, 185, 129, 0.15); 
                    cursor: pointer; 
                    transition: all 0.3s ease;
                    display: flex;
                    align-items: flex-start;"
             onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 6px 20px rgba(16, 185, 129, 0.25)'"
             onmouseout="this.style.transform='translateY(0px)'; this.style.boxShadow='0 4px 15px rgba(16, 185, 129, 0.15)'"
             onclick="document.querySelector('button[key=hidden_action_3]').click()">
            <div style="margin-right: 0.75rem; flex-shrink: 0; font-size: 1.2rem; color: white;">✅</div>
            <div style="flex-grow: 1; color: white;">
                <div style="font-weight: 600; font-size: 1rem;">MED envoyé - MANDAT ÉCOLE</div>
                <div style="font-size: 0.9rem; margin-top: 0.25rem; opacity: 0.9;">Mise en demeure promoteur envoyée</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # ACTION 4 - VERTE avec coche alignée à gauche (HTML direct cliquable)
        st.markdown("""
        <div style="background: linear-gradient(145deg, #10B981, #D1FAE5); 
                    border-left: 4px solid #10B981; 
                    border-radius: 15px; 
                    padding: 1rem; 
                    margin: 0.5rem 0; 
                    box-shadow: 0 4px 15px rgba(16, 185, 129, 0.15); 
                    cursor: pointer; 
                    transition: all 0.3s ease;
                    display: flex;
                    align-items: flex-start;"
             onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 6px 20px rgba(16, 185, 129, 0.25)'"
             onmouseout="this.style.transform='translateY(0px)'; this.style.boxShadow='0 4px 15px rgba(16, 185, 129, 0.15)'"
             onclick="document.querySelector('button[key=hidden_action_4]').click()">
            <div style="margin-right: 0.75rem; flex-shrink: 0; font-size: 1.2rem; color: white;">✅</div>
            <div style="flex-grow: 1; color: white;">
                <div style="font-weight: 600; font-size: 1rem;">REM T3 saisi - 3 opérations</div>
                <div style="font-size: 0.9rem; margin-top: 0.25rem; opacity: 0.9;">Trimestre 3 validé et saisi</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # ACTION 5 - VERTE avec coche alignée à gauche (HTML direct cliquable)
        st.markdown("""
        <div style="background: linear-gradient(145deg, #10B981, #D1FAE5); 
                    border-left: 4px solid #10B981; 
                    border-radius: 15px; 
                    padding: 1rem; 
                    margin: 0.5rem 0; 
                    box-shadow: 0 4px 15px rgba(16, 185, 129, 0.15); 
                    cursor: pointer; 
                    transition: all 0.3s ease;
                    display: flex;
                    align-items: flex-start;"
             onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 6px 20px rgba(16, 185, 129, 0.25)'"
             onmouseout="this.style.transform='translateY(0px)'; this.style.boxShadow='0 4px 15px rgba(16, 185, 129, 0.15)'"
             onclick="document.querySelector('button[key=hidden_action_5]').click()">
            <div style="margin-right: 0.75rem; flex-shrink: 0; font-size: 1.2rem; color: white;">✅</div>
            <div style="flex-grow: 1; color: white;">
                <div style="font-weight: 600; font-size: 1rem;">Timeline mise à jour - VEFA BELCOURT</div>
                <div style="font-size: 0.9rem; margin-top: 0.25rem; opacity: 0.9;">Planning actualisé avec nouvelles échéances</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Graphique d'activité MODERNISÉ
    st.markdown("### 📈 Activité Mensuelle")
    
    if activite_data and activite_data.get('mois'):
        fig_dashboard = go.Figure()
        
        # REM mensuelle avec dégradé modernisé
        fig_dashboard.add_trace(go.Scatter(
            x=activite_data['mois'],
            y=activite_data['rem_mensuelle'],
            mode='lines+markers',
            name='REM Mensuelle (€)',
            yaxis='y',
            line=dict(color='#8B5CF6', width=3),
            marker=dict(size=8, color='#8B5CF6')
        ))
        
        # Opérations actives
        fig_dashboard.add_trace(go.Scatter(
            x=activite_data['mois'],
            y=activite_data['operations_actives'],
            mode='lines+markers',
            name='Opérations Actives',
            yaxis='y2',
            line=dict(color='#10B981', width=3),
            marker=dict(size=8, color='#10B981')
        ))
        
        fig_dashboard.update_layout(
            title=f"Évolution Activité {nom_aco} - 2024",
            xaxis=dict(title="Mois"),
            yaxis=dict(title="REM (€)", side="left"),
            yaxis2=dict(title="Nb Opérations", side="right", overlaying="y"),
            height=450,
            hovermode='x unified',
            plot_bgcolor='rgba(139, 92, 246, 0.02)',
            paper_bgcolor='#f9fafb'
        )
        
        st.plotly_chart(fig_dashboard, use_container_width=True)
    else:
        st.info("📊 Données d'activité en cours de chargement...")

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
# 5. APPLICATION PRINCIPALE AVEC AUTHENTIFICATION CORRIGÉE
# ==============================================================================

def main():
    """Point d'entrée avec authentification et navigation moderne CORRIGÉE"""
    
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
            
            if st.button(label, use_container_width=True, type=button_type, key=f"nav_{page_key}"):
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
            if st.button(label, use_container_width=True, key=f"special_{page_key}"):
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
            if st.button("⚙️ Panel Admin", use_container_width=True, key="admin_panel"):
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
        if st.button("🚪 Déconnexion", use_container_width=True, type="primary", key="logout_btn"):
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
