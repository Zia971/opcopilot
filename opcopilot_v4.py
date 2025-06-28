import streamlit as st
import pandas as pd
import plotly.express as px

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="OPCOPILOT - Tableau de Bord Opérationnel",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS CUSTOM ---
st.markdown("""
<style>
    .main { background-color: #F9FAFB; }
    .stSidebar { background-color: #F8FAFC; }
    .stButton>button { background-color: #2563eb; color: white; border-radius: 6px; }
    .stButton>button:hover { background-color: #1d4ed8; }
    .stMetric { background: #fff; border-radius: 10px; padding: 10px; }
    .stTabs [data-baseweb="tab-list"] { background: #f1f5f9; }
    /* Ajoute ici d'autres styles pour affiner l'UI */
</style>
""", unsafe_allow_html=True)

# --- GESTION DU STATE ---
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "current_page" not in st.session_state:
    st.session_state["current_page"] = "login"
if "user_type" not in st.session_state:
    st.session_state["user_type"] = None
if "aco_user" not in st.session_state:
    st.session_state["aco_user"] = None

# --- AUTHENTIFICATION ---
def login_form():
    st.markdown("<h2 style='text-align:center;'>Connexion à OPCOPILOT</h2>", unsafe_allow_html=True)
    with st.form("login_form", clear_on_submit=False):
        username = st.text_input("Identifiant", key="login_user")
        password = st.text_input("Mot de passe", type="password", key="login_pass")
        col1, col2, col3 = st.columns([2,1,2])
        with col2:
            submit = st.form_submit_button("Se connecter")
        st.markdown(
            """
            <div style='text-align:center; margin-top:10px;'>
                <button style='background:none; border:none; color:#2563eb; cursor:pointer;'>Mot de passe oublié ?</button>
                <span style='margin:0 8px;'></span>
                <button style='background:none; border:none; color:#2563eb; cursor:pointer;'>Admin</button>
            </div>
            """, unsafe_allow_html=True
        )

        if submit:
            # Remplace par ta logique d'authentification réelle
            if username == "aco" and password == "test":
                st.session_state["authenticated"] = True
                st.session_state["current_page"] = "dashboard"
                st.session_state["user_type"] = "aco"
                st.session_state["aco_user"] = username
                st.success("Connexion réussie !")
                st.experimental_rerun()
            elif username == "admin" and password == "admin":
                st.session_state["authenticated"] = True
                st.session_state["current_page"] = "admin"
                st.session_state["user_type"] = "admin"
                st.session_state["aco_user"] = username
                st.success("Connexion admin réussie !")
                st.experimental_rerun()
            else:
                st.error("Identifiant ou mot de passe incorrect.")

# --- SIDEBAR ---
def sidebar():
    st.sidebar.markdown("## 🏗️ OPCOPILOT")
    if st.session_state["authenticated"]:
        st.sidebar.write(f"👤 {st.session_state['aco_user']} ({st.session_state['user_type']})")
        if st.sidebar.button("🏠 Tableau de bord", key="dashboard_btn"):
            st.session_state["current_page"] = "dashboard"
            st.experimental_rerun()
        if st.session_state["user_type"] == "admin":
            if st.sidebar.button("⚙️ Admin", key="admin_btn"):
                st.session_state["current_page"] = "admin"
                st.experimental_rerun()
        if st.sidebar.button("🚪 Déconnexion", key="logout_btn"):
            st.session_state["authenticated"] = False
            st.session_state["current_page"] = "login"
            st.session_state["user_type"] = None
            st.session_state["aco_user"] = None
            st.experimental_rerun()
    else:
        st.sidebar.info("Veuillez vous connecter.")

# --- DASHBOARD ---
def dashboard_page():
    st.markdown("## Tableau de Bord Opérationnel")
    kpis = [
        {"label": "KPI 1", "value": 120, "delta": "+10%"},
        {"label": "KPI 2", "value": 80, "delta": "-5%"},
        {"label": "KPI 3", "value": 45, "delta": "+2%"},
        {"label": "KPI 4", "value": 300, "delta": "+15%"},
    ]
    cols = st.columns(4)
    for i, kpi in enumerate(kpis):
        with cols[i]:
            st.metric(label=kpi["label"], value=kpi["value"], delta=kpi["delta"])

    st.markdown("---")
    col1, col2 = st.columns([2,1])
    with col1:
        df = pd.DataFrame({
            "Catégorie": ["A", "B", "C", "D"],
            "Valeur": [10, 20, 30, 40]
        })
        fig = px.bar(df, x="Catégorie", y="Valeur", title="Exemple de graphique Plotly")
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        st.dataframe(df, use_container_width=True)

    with st.expander("Voir plus de détails"):
        st.write("Contenu additionnel du dashboard...")

# --- PAGE ADMIN ---
def admin_page():
    st.markdown("## Espace Administrateur")
    st.info("Fonctionnalités d'administration à compléter.")

# --- ROUTAGE DES PAGES ---
def main():
    sidebar()
    if not st.session_state["authenticated"]:
        login_form()
    else:
        if st.session_state["current_page"] == "dashboard":
            dashboard_page()
        elif st.session_state["current_page"] == "admin":
            admin_page()
        else:
            st.warning("Page inconnue.")

if __name__ == "__main__":
    main()
