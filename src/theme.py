"""
Streamlit custom styling - SIMPLIFIED & CLEAN
Minimal, sustainable design with breathing room
"""

import streamlit as st

CUSTOM_THEME = """
<style>
    /* Root variables */
    :root {
        --primary-teal: #00796B;
        --secondary-teal: #00897B;
        --accent-green: #4CAF50;
        --light-bg: #F1F8F6;
    }

    /* Minimal background */
    .stApp {
        background-color: #F8FFFE;
    }

    /* Typography */
    h1 {
        color: #00796B !important;
        font-weight: 700 !important;
        margin-bottom: 0.3rem !important;
    }

    h2 {
        color: #00897B !important;
        font-weight: 600 !important;
        margin-top: 1.5rem !important;
        margin-bottom: 1rem !important;
    }

    h3 {
        color: #0097A7 !important;
        font-weight: 600 !important;
    }

    /* Clean metric containers */
    [data-testid="metric-container"] {
        background: transparent !important;
        border: none !important;
        padding: 0.8rem !important;
    }

    /* Simple button style */
    button {
        background: #00796B !important;
        color: white !important;
        border: none !important;
        border-radius: 6px !important;
        font-weight: 600 !important;
        transition: background 0.2s ease !important;
    }

    button:hover {
        background: #005A47 !important;
    }

    /* Clean divider */
    hr {
        border-color: #E0E0E0 !important;
        margin: 2rem 0 !important;
    }

    /* Message styling - minimal */
    .stAlert {
        border-radius: 6px !important;
        border: none !important;
    }

    .stAlert-success {
        background-color: #E8F5E9 !important;
        color: #1B5E20 !important;
    }

    .stAlert-info {
        background-color: #E0F2F1 !important;
        color: #00695C !important;
    }

    .stAlert-warning {
        background-color: #FFF3E0 !important;
        color: #E65100 !important;
    }

    .stAlert-error {
        background-color: #FFEBEE !important;
        color: #B71C1C !important;
    }

    /* Simple input styling */
    input, select {
        border: 1px solid #CCC !important;
        border-radius: 4px !important;
        padding: 0.5rem !important;
    }

    input:focus, select:focus {
        border-color: #00796B !important;
        outline: none !important;
    }

    /* Data table */
    [data-testid="stDataframe"] {
        border-radius: 4px !important;
    }

    /* Reduce padding on containers */
    [data-testid="stVerticalBlock"] {
        gap: 1rem !important;
    }
</style>
"""

def apply_custom_theme():
    """Apply minimal custom theme"""
    st.markdown(CUSTOM_THEME, unsafe_allow_html=True)


ICONS = {
    "water": "💧",
    "efficiency": "⚡",
    "save": "🌱",
    "chart": "📊",
    "report": "📋",
    "check": "✅",
    "warning": "⚠️",
    "error": "❌",
    "leaf": "🍃",
    "earth": "🌍",
    "drop": "💧",
    "recycle": "♻️",
}
