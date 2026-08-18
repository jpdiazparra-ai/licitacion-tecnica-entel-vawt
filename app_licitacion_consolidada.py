import streamlit as st
import streamlit.components.v1 as components
import copy
import numpy as np
import pandas as pd
import plotly.express as px
from math import gamma, pi, sqrt
from contextlib import contextmanager
from html import escape
from pathlib import Path
import base64
import io
import os
import re
import urllib.request
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image,
    PageBreak,
)
import plotly.graph_objects as go
from plotly.subplots import make_subplots


# Paleta fija para TODOS los gráficos Plotly
COLOR_SEQ = [
    "#194BC9",  # azul profundo
    "#eb0a0a",  # verde
    "#74d1f5",  # rosado
    "#eaf63b",  # azul medio
    "#22c55e",  # verde extra
    "#a855f7",  # violeta
]
px.defaults.color_discrete_sequence = COLOR_SEQ
os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib-cache")

st.set_page_config(
    page_title="Licitación técnica consolidada",
    layout="wide",
    initial_sidebar_state="collapsed",
)
st.markdown('<div id="top"></div>', unsafe_allow_html=True)
st.markdown(
    """
    <style>
    /* Vista dedicada: conserva sidebar, oculta bloques principales colapsados y deja activa la primera pestaña. */
    .main .block-container div[data-testid="stExpander"] details:not([open]) {
        display: none !important;
    }
    .main .block-container div[data-baseweb="tab-list"] {
        display: none !important;
    }
    .entel-elec-panel {
        border: 1px solid rgba(79,90,105,0.18);
        border-left: 6px solid #2f5f73;
        border-radius: 8px;
        background:
            linear-gradient(rgba(79,90,105,0.035) 1px, transparent 1px),
            linear-gradient(90deg, rgba(79,90,105,0.035) 1px, transparent 1px),
            linear-gradient(180deg, #ffffff 0%, #f7fafb 100%);
        background-size: 22px 22px, 22px 22px, auto;
        padding: 0.95rem 1.05rem;
        margin: 0.35rem 0 1.0rem 0;
        box-shadow: 0 10px 24px rgba(31,41,51,0.08);
    }
    .entel-elec-panel__eyebrow {
        color: #2f5f73;
        font-size: 0.68rem;
        font-weight: 900;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        margin-bottom: 0.25rem;
    }
    .entel-elec-panel__title {
        color: #1f2933;
        font-size: 1.02rem;
        font-weight: 850;
        line-height: 1.22;
    }
    .entel-elec-kpi-grid {
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: 0.78rem;
        margin: 0.35rem 0 1.05rem 0;
    }
    .entel-elec-kpi {
        min-height: 106px;
        border: 1px solid rgba(79,90,105,0.18);
        border-top: 4px solid var(--accent);
        border-radius: 8px;
        background: linear-gradient(180deg, #ffffff 0%, #f7f9fb 100%);
        padding: 0.78rem 0.82rem;
        box-shadow: 0 8px 18px rgba(31,41,51,0.07);
    }
    .entel-elec-kpi__label {
        color: #52606d;
        font-size: 0.72rem;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 0.28rem;
    }
    .entel-elec-kpi__value {
        color: #1f2933;
        font-size: 1.34rem;
        font-weight: 900;
        line-height: 1.05;
    }
    .entel-elec-kpi__sub {
        color: #6b7280;
        font-size: 0.76rem;
        line-height: 1.25;
        margin-top: 0.35rem;
    }
    .entel-elec-section {
        display: flex;
        align-items: center;
        gap: 0.55rem;
        margin: 1.15rem 0 0.55rem 0;
        color: #1f2933;
        font-size: 1.02rem;
        font-weight: 900;
    }
    .entel-elec-section::before {
        content: "";
        width: 9px;
        height: 26px;
        border-radius: 3px;
        background: linear-gradient(180deg, #2f5f73, #d9a766);
        display: inline-block;
    }
    @media (max-width: 900px) {
        .entel-elec-kpi-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ====== ESTILO GLOBAL (comentarios + KPIs) ======


st.markdown("""
<style>

.main .block-container {
    padding-top: 0rem;
    max-width: min(100%, 1840px);
    width: 100%;
    padding-left: 1.4rem;
    padding-right: 1.4rem;
}

.main .block-container > div.element-container:has(> div[data-testid="stExpander"]) {
    margin: 0 0 1.05rem 0 !important;
    padding: 0 !important;
}

.main .block-container > div.element-container:has(> div[data-testid="stExpander"]) + div.element-container:has(> div[data-testid="stExpander"]) {
    margin-top: 0 !important;
}

.main .block-container div[data-testid="stExpander"] {
    margin: 0 !important;
}

.main .block-container div[data-testid="stExpander"] details {
    position: relative !important;
    border-radius: 10px !important;
    border: 1px solid rgba(71, 85, 105, 0.22) !important;
    border-top: 4px solid #3d5a80 !important;
    background:
        linear-gradient(rgba(15, 23, 42, 0.035) 1px, transparent 1px),
        linear-gradient(90deg, rgba(15, 23, 42, 0.035) 1px, transparent 1px),
        linear-gradient(180deg, #ffffff 0%, #f7fafc 100%) !important;
    background-size: 24px 24px, 24px 24px, auto !important;
    box-shadow: 0 10px 22px rgba(15, 23, 42, 0.08), inset 0 1px 0 rgba(255,255,255,0.9) !important;
    overflow: hidden !important;
}

.main .block-container div[data-testid="stExpander"] details::before {
    content: "";
    position: absolute;
    left: 0;
    top: 0;
    bottom: 0;
    width: 8px;
    background: linear-gradient(180deg, #3d5a80 0%, #2a9d8f 48%, #d9a766 100%);
    opacity: 0.95;
    z-index: 1;
}

.main .block-container div[data-testid="stExpander"] details[open] {
    border-color: rgba(61, 90, 128, 0.36) !important;
    box-shadow: 0 16px 34px rgba(15, 23, 42, 0.12), inset 0 1px 0 rgba(255,255,255,0.95) !important;
}

.main .block-container div[data-testid="stExpander"] summary {
    position: relative !important;
    padding: 0.95rem 1.2rem 0.95rem 1.6rem !important;
    background:
        linear-gradient(90deg, rgba(15, 23, 42, 0.04), rgba(255,255,255,0.76) 32%, rgba(244,247,250,0.92)),
        linear-gradient(180deg, rgba(255,255,255,0.98), rgba(240,245,248,0.98)) !important;
    border-radius: 0 !important;
    border-bottom: 1px solid rgba(71,85,105,0.12) !important;
    font-weight: 800 !important;
    color: #182235 !important;
    min-height: 58px !important;
    display: flex !important;
    align-items: center !important;
}

.main .block-container div[data-testid="stExpander"] summary:hover {
    background:
        linear-gradient(90deg, rgba(42, 157, 143, 0.09), rgba(255,255,255,0.9) 34%, rgba(239,246,249,1)),
        linear-gradient(180deg, rgba(255,255,255,1), rgba(238,244,247,1)) !important;
}

.main .block-container div[data-testid="stExpander"] summary::before {
    content: "ENG";
    position: absolute;
    right: 3.7rem;
    top: 50%;
    transform: translateY(-50%);
    padding: 0.25rem 0.52rem;
    border-radius: 6px;
    border: 1px solid rgba(61,90,128,0.20);
    background: rgba(255,255,255,0.72);
    color: #3d5a80;
    font-size: 0.58rem;
    line-height: 1;
    letter-spacing: 0.14em;
    font-weight: 900;
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.75);
}

.main .block-container div[data-testid="stExpander"] summary::after {
    content: "";
    position: absolute;
    left: 1.55rem;
    right: 1.2rem;
    bottom: 0;
    height: 1px;
    background: linear-gradient(90deg, rgba(61,90,128,0.38), rgba(42,157,143,0.24), transparent);
}

.main .block-container div[data-testid="stExpander"] summary p {
    font-size: 1.02rem !important;
    line-height: 1.2 !important;
    letter-spacing: 0 !important;
    color: #182235 !important;
    text-transform: none !important;
}

.main .block-container div[data-testid="stExpanderDetails"] {
    padding: 0.8rem 1rem 0.95rem 1.35rem !important;
    margin-bottom: 0 !important;
    background:
        linear-gradient(180deg, rgba(255,255,255,0.72), rgba(248,250,252,0.88)) !important;
}

.main .block-container div[data-testid="stExpanderDetails"] > div {
    padding-top: 0 !important;
    margin-top: 0 !important;
}

.main .block-container div[data-testid="stExpanderDetails"] [data-testid="stMetric"] {
    border-radius: 8px !important;
    border: 1px solid rgba(71,85,105,0.14) !important;
    background: rgba(255,255,255,0.72) !important;
    padding: 0.55rem 0.65rem !important;
}

.main .block-container > div.element-container:has(style),
.main .block-container > div.element-container:has(#alertas),
.main .block-container > div.element-container:has(#top) {
    margin: 0 !important;
    padding: 0 !important;
}

.kpi-card {
    background: linear-gradient(135deg, #0E1525 0%, #1A2233 100%);
    border-radius: 12px;
    padding: 0.7rem 1.0rem;       /* MÁS COMPACTO */
    border: 1px solid rgba(255,255,255,0.05);
    box-shadow: 0 2px 8px rgba(0,0,0,0.35);
    transition: 0.15s ease-in-out;
    min-height: 115px;           /* ALTURA REDUCIDA */
    display: flex;
    flex-direction: column;
    justify-content: center;
}

.kpi-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 14px rgba(0,0,0,0.45);
}

.hero-banner {
    width: 100%;
    aspect-ratio: 4.9 / 1;
    min-height: 168px;
    max-height: 182px;
    border-radius: 24px;
    background-size: cover;
    background-position: center 38%;
    margin: -4.7rem 0 2.9rem;
    box-shadow: 0 20px 40px rgba(79,90,105,0.18);
    border: 1px solid rgba(79,90,105,0.14);
    position: relative;
    overflow: hidden;
    display: flex;
    align-items: stretch;
}

.hero-banner::before {
    content: "";
    position: absolute;
    inset: 0;
    background:
        linear-gradient(90deg, rgba(255,255,255,0.88) 0%, rgba(255,255,255,0.76) 28%, rgba(255,255,255,0.42) 60%, rgba(255,255,255,0.18) 100%),
        linear-gradient(180deg, rgba(255,255,255,0.18), rgba(255,255,255,0.04));
}

.hero-banner__content {
    position: relative;
    z-index: 1;
    width: 100%;
    padding: 1.1rem 1.55rem 1rem;
    display: flex;
    flex-direction: column;
    justify-content: center;
    gap: 0.45rem;
}

.hero-banner__eyebrow {
    display: inline-flex;
    align-items: center;
    gap: 0.8rem;
}

.hero-banner__icon {
    width: 58px;
    height: 58px;
    border-radius: 18px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-size: 1.7rem;
    background: rgba(255,255,255,0.78);
    border: 1px solid rgba(183,180,178,0.4);
    box-shadow: 0 8px 18px rgba(79,90,105,0.12);
    backdrop-filter: blur(8px);
}

.hero-banner__chip {
    display: inline-flex;
    align-items: center;
    padding: 0.4rem 0.78rem;
    border-radius: 999px;
    background: rgba(255,255,255,0.76);
    border: 1px solid rgba(79,90,105,0.12);
    color: #4f5a69;
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 0.11em;
    text-transform: uppercase;
}

.hero-banner__title {
    max-width: 940px;
    margin: 0;
    font-size: clamp(1.6rem, 1.1rem + 2.3vw, 2.45rem);
    line-height: 1.02;
    letter-spacing: -0.05em;
    font-weight: 800;
    color: #1a2333;
    text-wrap: balance;
}

.hero-banner__subtitle {
    max-width: 980px;
    margin: 0;
    font-size: clamp(0.76rem, 0.72rem + 0.22vw, 0.93rem);
    line-height: 1.42;
    color: rgba(79, 90, 105, 0.96);
}

@media (max-width: 900px) {
    .hero-banner {
        width: 100%;
        aspect-ratio: 2.35 / 1;
        min-height: 190px;
        max-height: none;
        background-position: center center;
        margin: -2.6rem 0 2rem;
    }

    .hero-banner__content {
        width: 100%;
        padding: 0.9rem 1rem 1rem;
        gap: 0.55rem;
    }

    .hero-banner__icon {
        width: 50px;
        height: 50px;
        border-radius: 16px;
        font-size: 1.45rem;
    }

    .hero-banner__title {
        line-height: 1.02;
    }
}

.kpi-title {
    font-size: 0.65rem;          /* MÁS CHICO */
    text-transform: uppercase;
    letter-spacing: 0.09em;
    color: #8BA2BF;
    margin-bottom: 0.35rem;      /* TEXTO MÁS ARRIBA */
}

.kpi-value {
    font-size: 1.55rem;          /* REDUCIDO */
    font-weight: 700;
    color: #FFFFFF;
    margin-bottom: 0.1rem;
}

.kpi-sub {
    font-size: 0.75rem;
    color: #9BA6B9;
    margin-top: 0.15rem;
}

/* Menos espacio entre filas */
.kpi-container {
    margin-bottom: 0.7rem;
}

</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>

.comment-box {
    background: #F6F9FC;
    border-left: 6px solid #2B73FF;
    padding: 1rem 1.3rem;
    border-radius: 6px;
    margin-top: 1.2rem;
    margin-bottom: 1.2rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.08);
}

.comment-title {
    font-weight: 700;
    font-size: 1rem;
    color: #1A3C78;
    margin-bottom: 0.4rem;
    display: flex;
    align-items: center;
}

.comment-title::before {
    content: " ";
    font-size: 1.1rem;
    margin-right: 0.3rem;
}

.comment-box p {
    font-size: 0.95rem;
    line-height: 1.45;
    color: #333;
}

.design-summary {
    position: relative;
    overflow: hidden;
    margin: 0.35rem 0 1.1rem;
    padding: 1.15rem 1.2rem 1.15rem 1.2rem;
    border-radius: 22px;
    border: 1px solid rgba(79,90,105,0.12);
    background:
        radial-gradient(circle at top right, rgba(132,169,164,0.16), transparent 32%),
        linear-gradient(135deg, rgba(255,255,255,0.98), rgba(244,240,236,0.98));
    box-shadow: 0 14px 30px rgba(79,90,105,0.10);
}

.design-summary::before {
    content: "";
    position: absolute;
    inset: 0 auto 0 0;
    width: 7px;
    background: linear-gradient(180deg, #d95f5f, #d9a766, #84a9a4);
}

.design-summary__eyebrow {
    font-size: 0.66rem;
    font-weight: 800;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    color: #7a8793;
    margin-bottom: 0.35rem;
}

.design-summary__title {
    margin: 0;
    font-size: clamp(1.25rem, 1.05rem + 0.7vw, 1.8rem);
    line-height: 1.04;
    letter-spacing: -0.03em;
    font-weight: 800;
    color: #233046;
}

.design-summary__sub {
    margin-top: 0.45rem;
    font-size: 0.92rem;
    line-height: 1.45;
    color: #5f6b77;
    max-width: 920px;
}

.design-summary__grid {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 0.8rem;
    margin-top: 1rem;
}

.design-summary__metric {
    border-radius: 16px;
    border: 1px solid rgba(79,90,105,0.10);
    background: rgba(255,255,255,0.72);
    padding: 0.85rem 0.9rem;
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.65);
}

.design-summary__metric-label {
    font-size: 0.68rem;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: #7a8793;
    margin-bottom: 0.3rem;
}

.design-summary__metric-value {
    font-size: 1.28rem;
    line-height: 1.05;
    letter-spacing: -0.03em;
    font-weight: 800;
    color: #4f5a69;
}

.design-summary__footer {
    margin-top: 0.85rem;
    padding-top: 0.75rem;
    border-top: 1px solid rgba(79,90,105,0.10);
    font-size: 0.82rem;
    line-height: 1.45;
    color: #66737f;
}

@media (max-width: 900px) {
    .design-summary__grid {
        grid-template-columns: repeat(2, minmax(0, 1fr));
    }
}

.sidebar-section {
    margin: 1.2rem 0 0.4rem;
    padding: 0.35rem 0.7rem;
    border-left: 4px solid #84a9a4;
    border-radius: 12px;
    background: linear-gradient(90deg, rgba(183,180,178,0.18), rgba(132,169,164,0.12));
    font-size: 0.95rem;
    font-weight: 700;
    color: #334155;
}

[data-testid="stSidebar"] [data-testid="stExpander"] details {
    border-radius: 16px !important;
    border: 1px solid rgba(79,90,105,0.12) !important;
    background: linear-gradient(180deg, #fbfaf8 0%, #f1ede9 100%) !important;
    box-shadow: 0 8px 18px rgba(79,90,105,0.08) !important;
    overflow: hidden !important;
}

[data-testid="stSidebar"] [data-testid="stExpander"] summary {
    position: relative !important;
    padding: 0.78rem 0.85rem 0.78rem 1rem !important;
    border-radius: 16px !important;
    background:
        radial-gradient(circle at top right, rgba(132,169,164,0.08), transparent 34%),
        linear-gradient(180deg, rgba(255,255,255,0.96), rgba(244,240,236,0.98)) !important;
    color: #3f4958 !important;
    font-weight: 650 !important;
}

[data-testid="stSidebar"] [data-testid="stExpander"] summary::before {
    content: "";
    position: absolute;
    left: 0;
    top: 14%;
    bottom: 14%;
    width: 5px;
    border-radius: 0 8px 8px 0;
    background: linear-gradient(180deg, #d95f5f, #84a9a4);
}

[data-testid="stSidebar"] [data-testid="stExpander"] summary:hover {
    background:
        radial-gradient(circle at top right, rgba(217,167,102,0.10), transparent 36%),
        linear-gradient(180deg, rgba(255,255,255,1), rgba(241,237,233,1)) !important;
}

[data-testid="stSidebar"] [data-testid="stExpander"] summary p {
    font-size: 0.98rem !important;
    line-height: 1.25 !important;
    color: #4f5a69 !important;
}

[data-testid="stSidebar"] [data-testid="stExpander"] + [data-testid="stExpander"] {
    margin-top: 0.55rem !important;
}

/* ===== BLOQUES DESPLEGABLES DEL CUERPO PRINCIPAL — ESTILO INGENIERÍA ===== */
[data-testid="stMain"] div[data-testid="stExpander"] details {
    position: relative !important;
    border-radius: 10px !important;
    border: 1px solid rgba(51, 65, 85, 0.28) !important;
    border-top: 4px solid #3d5a80 !important;
    background:
        linear-gradient(rgba(15, 23, 42, 0.035) 1px, transparent 1px),
        linear-gradient(90deg, rgba(15, 23, 42, 0.035) 1px, transparent 1px),
        linear-gradient(180deg, #ffffff 0%, #f8fafc 100%) !important;
    background-size: 22px 22px, 22px 22px, auto !important;
    box-shadow: 0 12px 26px rgba(15, 23, 42, 0.10), inset 0 1px 0 rgba(255,255,255,0.92) !important;
    overflow: hidden !important;
}

[data-testid="stMain"] div[data-testid="stExpander"] details::before {
    content: "" !important;
    position: absolute !important;
    left: 0 !important;
    top: 0 !important;
    bottom: 0 !important;
    width: 9px !important;
    background: linear-gradient(180deg, #3d5a80 0%, #2a9d8f 52%, #d9a766 100%) !important;
    z-index: 1 !important;
}

[data-testid="stMain"] div[data-testid="stExpander"] details[open] {
    border-color: rgba(61, 90, 128, 0.44) !important;
    box-shadow: 0 18px 38px rgba(15, 23, 42, 0.14), inset 0 1px 0 rgba(255,255,255,0.95) !important;
}

[data-testid="stMain"] div[data-testid="stExpander"] summary {
    position: relative !important;
    min-height: 64px !important;
    padding: 1rem 1.25rem 1rem 1.75rem !important;
    border-radius: 0 !important;
    border-bottom: 1px solid rgba(71,85,105,0.14) !important;
    background:
        linear-gradient(90deg, rgba(15, 23, 42, 0.055), rgba(255,255,255,0.86) 34%, rgba(241,245,249,0.96)),
        linear-gradient(180deg, #ffffff, #eef4f7) !important;
    color: #182235 !important;
    font-weight: 850 !important;
    display: flex !important;
    align-items: center !important;
}

[data-testid="stMain"] div[data-testid="stExpander"] summary:hover {
    background:
        linear-gradient(90deg, rgba(42, 157, 143, 0.12), rgba(255,255,255,0.94) 36%, rgba(236,244,247,1)),
        linear-gradient(180deg, #ffffff, #eaf2f5) !important;
}

[data-testid="stMain"] div[data-testid="stExpander"] summary::before {
    content: "ENG" !important;
    position: absolute !important;
    right: 3.9rem !important;
    top: 50% !important;
    transform: translateY(-50%) !important;
    padding: 0.28rem 0.56rem !important;
    border-radius: 6px !important;
    border: 1px solid rgba(61,90,128,0.26) !important;
    background: rgba(255,255,255,0.82) !important;
    color: #3d5a80 !important;
    font-size: 0.58rem !important;
    line-height: 1 !important;
    letter-spacing: 0.14em !important;
    font-weight: 900 !important;
}

[data-testid="stMain"] div[data-testid="stExpander"] summary p {
    font-size: 1.03rem !important;
    line-height: 1.22 !important;
    letter-spacing: 0 !important;
    color: #182235 !important;
    font-weight: 850 !important;
}

[data-testid="stMain"] div[data-testid="stExpander"] div[data-testid="stExpanderDetails"] {
    padding: 0.95rem 1rem 1.05rem 1.45rem !important;
    background: linear-gradient(180deg, rgba(255,255,255,0.82), rgba(248,250,252,0.92)) !important;
}

.section-header {
    margin: 2rem 0 1rem;
    padding: 0.85rem 1.1rem;
    border-left: 6px solid #2563eb;
    border: 1px solid rgba(37, 99, 235, 0.25);
    border-radius: 10px;
    background: linear-gradient(90deg, rgba(219,234,254,0.55), rgba(255,255,255,0.9));
    font-size: 1.25rem;
    font-weight: 600;
    color: #0f172a;
    box-shadow: 0 6px 14px rgba(15, 23, 42, 0.08);
}

.section-subheader {
    margin: 1.5rem 0 0.75rem;
    padding: 0.7rem 0.95rem;
    border-left: 5px solid #f97316;
    border: 1px solid rgba(249, 115, 22, 0.35);
    border-radius: 10px;
    background: linear-gradient(90deg, rgba(255, 237, 213, 0.55), rgba(255, 255, 255, 0.9));
    font-size: 1.05rem;
    font-weight: 600;
    color: #7c2d12;
    box-shadow: 0 4px 10px rgba(120, 53, 15, 0.08);
}

.macro-section {
    position: relative;
    overflow: hidden;
    margin: 2.35rem 0 1.1rem;
    padding: 1rem 1.15rem 1.05rem;
    border-radius: 18px;
    border: 1px solid color-mix(in srgb, var(--macro-accent) 24%, rgba(148,163,184,0.2));
    background:
        radial-gradient(circle at top right, color-mix(in srgb, var(--macro-accent) 14%, transparent), transparent 32%),
        linear-gradient(135deg, color-mix(in srgb, var(--macro-accent) 8%, #ffffff), #f8fbff 52%, #ffffff 100%);
    box-shadow: 0 14px 30px rgba(15, 23, 42, 0.08);
}

.macro-section::before {
    content: "";
    position: absolute;
    inset: 0 auto 0 0;
    width: 7px;
    background: linear-gradient(180deg, var(--macro-accent), color-mix(in srgb, var(--macro-accent) 58%, #ffffff));
}

.macro-section__eyebrow {
    display: inline-flex;
    align-items: center;
    gap: 0.45rem;
    margin-bottom: 0.45rem;
    font-size: 0.68rem;
    font-weight: 800;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    color: color-mix(in srgb, var(--macro-accent) 62%, #334155);
}

.macro-section__title {
    margin: 0;
    font-size: 1.42rem;
    font-weight: 800;
    line-height: 1.08;
    letter-spacing: -0.03em;
    color: #0f172a;
}

.macro-section__sub {
    margin-top: 0.38rem;
    font-size: 0.9rem;
    line-height: 1.45;
    color: #5b6b80;
    max-width: 880px;
}

.sub-block {
    position: relative;
    margin: 1.15rem 0 0.8rem;
    padding: 0.78rem 0.95rem 0.8rem 1rem;
    border-radius: 14px;
    border: 1px solid color-mix(in srgb, var(--sub-accent) 22%, rgba(148,163,184,0.22));
    background:
        linear-gradient(90deg, color-mix(in srgb, var(--sub-accent) 8%, #ffffff), rgba(255,255,255,0.98)),
        #ffffff;
    box-shadow: 0 8px 18px rgba(15, 23, 42, 0.06);
}

.sub-block::before {
    content: "";
    position: absolute;
    inset: 0 auto 0 0;
    width: 5px;
    border-radius: 14px 0 0 14px;
    background: linear-gradient(180deg, var(--sub-accent), color-mix(in srgb, var(--sub-accent) 60%, #ffffff));
}

.sub-block__eyebrow {
    font-size: 0.62rem;
    font-weight: 800;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    color: color-mix(in srgb, var(--sub-accent) 60%, #475569);
    margin-bottom: 0.24rem;
}

.sub-block__title {
    margin: 0;
    font-size: 1.06rem;
    line-height: 1.15;
    font-weight: 800;
    letter-spacing: -0.02em;
    color: #0f172a;
}

.sub-block__sub {
    margin-top: 0.22rem;
    font-size: 0.82rem;
    line-height: 1.4;
    color: #64748b;
    max-width: 860px;
}

.analysis-switcher {
    margin: 2rem 0 1.2rem;
    padding: 1rem 1.05rem 1.1rem;
    border-radius: 18px;
    border: 1px solid rgba(203,213,225,0.95);
    background: linear-gradient(180deg, #ffffff 0%, #f8fbff 100%);
    box-shadow: 0 12px 28px rgba(15,23,42,0.08);
}

.analysis-switcher__eyebrow {
    font-size: 0.66rem;
    font-weight: 800;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    color: #94a3b8;
    margin-bottom: 0.35rem;
}

.analysis-switcher__title {
    margin: 0;
    font-size: 1.45rem;
    line-height: 1.06;
    letter-spacing: -0.03em;
    font-weight: 800;
    color: #0f172a;
}

.analysis-switcher__sub {
    margin-top: 0.35rem;
    color: #64748b;
    font-size: 0.9rem;
    line-height: 1.45;
}

.analysis-card {
    position: relative;
    overflow: hidden;
    min-height: 138px;
    padding: 0.8rem 0.78rem 0.72rem 0.82rem;
    border-radius: 18px;
    border: 1px solid var(--analysis-border, rgba(203,213,225,0.92));
    background:
        linear-gradient(90deg, var(--analysis-bg, #f8fbff), rgba(255,255,255,0.98)),
        #ffffff;
    box-shadow: 0 10px 20px rgba(15,23,42,0.06);
    margin-bottom: 0.5rem;
}

.analysis-card::before {
    content: "";
    position: absolute;
    inset: 0 auto 0 0;
    width: 7px;
    background: linear-gradient(180deg, var(--analysis-accent), var(--analysis-accent-soft, var(--analysis-accent)));
}

.analysis-card__eyebrow {
    font-size: 0.58rem;
    font-weight: 800;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: var(--analysis-label, #475569);
    margin-bottom: 0.55rem;
}

.analysis-card__title {
    margin: 0;
    font-size: 1.02rem;
    line-height: 1.08;
    font-weight: 800;
    letter-spacing: -0.025em;
    color: #172036;
    max-width: 100%;
}

.analysis-card__sub {
    margin-top: 0.55rem;
    font-size: 0.74rem;
    line-height: 1.32;
    color: #475569;
}

</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
.question-prompt {
    margin: 0.5rem 0 1rem 0;
    padding: 0.75rem 1rem;
    border-left: 4px solid #f97316;
    background: rgba(249,115,22,0.08);
    border-radius: 6px;
    font-weight: 500;
    color: #7c2d12;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
.margin-card {
    background:
        radial-gradient(circle at top right, rgba(132,169,164,0.16), transparent 34%),
        linear-gradient(180deg, #f5f4f2 0%, #ebe8e5 100%);
    border-radius: 14px;
    padding: 0.75rem 0.9rem;
    border: 1px solid rgba(79,90,105,0.14);
    box-shadow: 0 8px 22px rgba(79,90,105,0.12);
    height: 170px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    gap: 0.4rem;
    position: relative;
    overflow: hidden;
}
.margin-card::before {
    content: "";
    position: absolute;
    inset: 0 auto 0 0;
    width: 6px;
    background: linear-gradient(180deg, #84a9a4, #4f5a69);
}
.margin-card__title {
    font-size: 0.78rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #4f5a69;
    display: flex;
    align-items: center;
    justify-content: space-between;
    min-height: 3.2rem;
    padding-right: 0.15rem;
}
.margin-card__value {
    font-size: clamp(1.35rem, 1rem + 0.8vw, 1.95rem);
    font-weight: 700;
    color: #4f5a69;
    line-height: 1;
    white-space: nowrap;
    font-variant-numeric: tabular-nums;
    letter-spacing: -0.03em;
}
.margin-card__badge {
    width: 20px;
    height: 20px;
    border-radius: 50%;
    background: rgba(79,90,105,0.10);
    color: #4f5a69;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-size: 0.65rem;
    cursor: help;
}
.margin-ok .margin-card__value {
    color: #84a9a4;
}
.margin-warn .margin-card__value {
    color: #d9a766;
}
.margin-danger .margin-card__value {
    color: #d95f5f;
}
.margin-neutral .margin-card__value {
    color: #b7b4b2;
}
.range-card {
    position: relative;
    overflow: hidden;
    background:
        radial-gradient(circle at top right, color-mix(in srgb, var(--range-accent, #84a9a4) 16%, transparent), transparent 34%),
        linear-gradient(180deg, #f5f4f2 0%, #ece9e6 100%);
    border-radius: 18px;
    padding: 0.95rem 1rem 0.9rem;
    border: 1px solid rgba(79,90,105,0.14);
    box-shadow: 0 10px 24px rgba(79,90,105,0.12);
    min-height: 122px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    gap: 0.35rem;
}
.range-card::before {
    content: "";
    position: absolute;
    inset: 0 auto auto 0;
    width: 100%;
    height: 4px;
    background: linear-gradient(90deg, var(--range-accent, #38bdf8), rgba(255,255,255,0));
}
.range-card__top {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 0.6rem;
}
.range-card__badge {
    flex: 0 0 auto;
    padding: 0.22rem 0.5rem;
    border-radius: 999px;
    background: color-mix(in srgb, var(--range-accent, #84a9a4) 12%, #ffffff);
    border: 1px solid color-mix(in srgb, var(--range-accent, #84a9a4) 34%, rgba(79,90,105,0.12));
    color: #4f5a69;
    font-size: 0.6rem;
    font-weight: 800;
    letter-spacing: 0.14em;
    line-height: 1;
}
.range-card__label {
    font-size: 0.68rem;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: #6b7280;
    max-width: 78%;
}
.range-card__value {
    font-size: clamp(1.85rem, 1.55rem + 0.5vw, 2.3rem);
    font-weight: 800;
    letter-spacing: -0.03em;
    line-height: 1.04;
    color: var(--range-accent, #84a9a4);
}
.range-card__sub {
    font-size: 0.78rem;
    line-height: 1.42;
    color: #5f6b77;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
.alert-jump-link {
    display: block;
    font-weight: 600;
    text-align: center;
    padding: 0.6rem 0.4rem;
    border-radius: 8px;
    background: linear-gradient(120deg, #f97316, #f43f5e);
    color: #fff !important;
    text-decoration: none !important;
    margin-bottom: 0.8rem;
    box-shadow: 0 3px 8px rgba(0,0,0,0.25);
}
.alert-jump-link:hover {
    filter: brightness(1.05);
}
.alert-jump-floating {
    position: fixed;
    right: 1.8rem;
    top: 50%;
    transform: translateY(-50%);
    z-index: 999;
    writing-mode: vertical-rl;
    text-orientation: mixed;
    padding: 0.35rem 0.24rem;
    border-radius: 10px;
    background: linear-gradient(180deg, rgba(217,95,95,0.92), rgba(217,167,102,0.92));
    color: #fff !important;
    text-decoration: none !important;
    box-shadow: 0 4px 10px rgba(79,90,105,0.18);
    font-size: 0.84rem;
}
.alert-jump-floating:hover {
    filter: brightness(1.08);
}
.top-jump-floating {
    position: fixed;
    right: 1.8rem;
    bottom: 2.2rem;
    z-index: 999;
    padding: 0.45rem 0.8rem;
    border-radius: 999px;
    background: linear-gradient(120deg, rgba(79,90,105,0.94), rgba(132,169,164,0.94));
    color: #fff !important;
    text-decoration: none !important;
    font-weight: 600;
    box-shadow: 0 4px 10px rgba(79,90,105,0.18);
}
.top-jump-floating:hover {
    filter: brightness(1.12);
}
@media print {
    .alert-jump-link,
    .alert-jump-floating,
    .top-jump-floating {
        display: none !important;
    }
}
</style>
""", unsafe_allow_html=True)

st.markdown(
    '<a href="#alertas" class="alert-jump-floating">🚨 Alertas</a>',
    unsafe_allow_html=True
)
st.markdown(
    '<a href="#top" class="top-jump-floating">⬆️ Inicio</a>',
    unsafe_allow_html=True
)


def kpi_card(title: str, value: str, subtitle: str, accent: str = "blue") -> None:
    """
    Tarjeta KPI homogénea para todo el dashboard.
    accent: 'blue', 'green', 'orange' o cualquier color hex.
    """
    color_map = {
        "blue":   "#38bdf8",
        "green":  "#22c55e",
        "orange": "#f97316",
        "red":    "#ef4444",
        "yellow": "#eab308",
        "warm_gray": PALETTE_WARM_GRAY,
        "coral": PALETTE_CORAL,
        "mustard": PALETTE_MUSTARD,
        "sage": PALETTE_SAGE,
        "slate": PALETTE_SLATE,
    }
    accent_color = color_map.get(accent, accent if accent.startswith("#") else "#38bdf8")
    accent_label = {
        "blue": "AERO",
        "green": "OK",
        "orange": "CTRL",
        "red": "LIM",
        "yellow": "REF",
        "warm_gray": "BASE",
        "coral": "CARGA",
        "mustard": "TREN",
        "sage": "ROTOR",
        "slate": "SIST",
    }.get(accent, "KPI")

    st.markdown(
        f"""
        <div class="kpi-card" style="--kpi-accent:{accent_color};">
          <div class="kpi-card__top">
            <div class="kpi-title">{title}</div>
            <div class="kpi-badge">{accent_label}</div>
          </div>
          <div class="kpi-value">
            {value}
          </div>
          <div class="kpi-subtitle">
            {subtitle}
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def question_prompt(text: str) -> None:
    st.markdown(f"<div class='question-prompt'>❓ {text}</div>", unsafe_allow_html=True)


def section_header(text: str, level: int = 2, anchor: str | None = None) -> None:
    """
    Renderiza un encabezado destacado; level<=2 usa estilo principal, level>=3 usa variante compacta.
    """
    cls = "section-header" if level <= 2 else "section-subheader"
    anchor_attr = f" id='{anchor}'" if anchor else ""
    st.markdown(f"<div class='{cls}'{anchor_attr}>{escape(text)}</div>", unsafe_allow_html=True)


def restore_scroll_to_anchor(anchor_id: str) -> None:
    """Reposiciona la vista en un ancla del documento principal tras el rerun de Streamlit."""
    safe_anchor = escape(anchor_id, quote=True)
    components.html(
        f"""
        <script>
        const anchorId = "{safe_anchor}";
        const scrollToAnchor = () => {{
          const anchor = window.parent.document.getElementById(anchorId);
          if (!anchor) return;
          anchor.scrollIntoView({{ behavior: "auto", block: "start" }});
        }};
        window.parent.requestAnimationFrame(() => {{
          scrollToAnchor();
          window.parent.setTimeout(scrollToAnchor, 120);
        }});
        </script>
        """,
        height=0,
    )


def select_analysis_block(block_key: str, scroll_anchor_id: str) -> None:
    """Actualiza el bloque activo sin forzar un rerun adicional."""
    st.session_state["active_analysis_block"] = block_key
    st.session_state["analysis_map_open"] = True
    st.session_state["pending_scroll_anchor"] = scroll_anchor_id


PALETTE_WARM_GRAY = "#b7b4b2"
PALETTE_CORAL = "#d95f5f"
PALETTE_MUSTARD = "#d9a766"
PALETTE_SAGE = "#84a9a4"
PALETTE_SLATE = "#4f5a69"


def macro_section_header(text: str, subtitle: str, accent: str = PALETTE_SLATE) -> None:
    return


def sub_block_header(text: str, subtitle: str, accent: str = PALETTE_SAGE) -> None:
    st.markdown(
        f"""
        <div class="sub-block" style="--sub-accent:{accent};">
          <div class="sub-block__eyebrow">Sub-bloque</div>
          <div class="sub-block__title">{escape(text)}</div>
          <div class="sub-block__sub">{escape(subtitle)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if "render_section_download_button" in globals():
        render_section_download_button(
            label=f"Descargar sub-bloque: {text}",
            section_title=text,
            section_rows=[
                {"Campo": "Sub-bloque", "Valor": text},
                {"Campo": "Descripción", "Valor": subtitle},
                {"Campo": "Bloque activo", "Valor": st.session_state.get("active_analysis_block", "Mapa técnico")},
            ],
            key_suffix=f"mapa_{st.session_state.get('active_analysis_block', 'sin_bloque')}_{text}",
            extra_sheets=analysis_block_export_sheets(st.session_state.get("active_analysis_block")),
            help_text="Descarga el contexto principal y los datos relevantes de este sub-bloque del mapa técnico.",
        )


def render_analysis_switcher():
    scroll_anchor_id = "analysis-map-anchor"
    blocks = [
        ("aero", "BLOQUE 1", "🌀 Aerodinámica y comportamiento del perfil", "Abrir vista estratégica", PALETTE_SAGE, "#d8e5e2", "#f4faf8", "#6f8f8b", "#c6d8d4"),
        ("control", "BLOQUE 2", "⚙️ Operación y control del rotor", "Abrir vista estratégica", PALETTE_MUSTARD, "#ead7b0", "#fdf8ef", "#967a4f", "#efdcbf"),
        ("power", "BLOQUE 3", "📈 Potencia y eficiencia global", "Abrir vista estratégica", PALETTE_CORAL, "#e8b8b8", "#fdf4f4", "#9e5858", "#ebbcbc"),
        ("mechanical", "BLOQUE 4", "🛠️ Tren mecánico y cargas", "Abrir vista estratégica", PALETTE_SLATE, "#c7cfda", "#f5f8fc", "#5f6c80", "#d0d6e0"),
        ("electrical", "BLOQUE 5", "🔌 Sistema eléctrico y vibraciones", "Abrir vista estratégica", PALETTE_SLATE, "#c7cfda", "#f5f8fc", "#5f6c80", "#d0d6e0"),
        ("resource", "BLOQUE 6", "🌬️ Recurso y energía anual", "Abrir vista estratégica", PALETTE_SAGE, "#d8e5e2", "#f4faf8", "#6f8f8b", "#c6d8d4"),
    ]
    if "active_analysis_block" not in st.session_state:
        st.session_state["active_analysis_block"] = None
    if "analysis_map_open" not in st.session_state:
        st.session_state["analysis_map_open"] = False
    if "pending_scroll_anchor" not in st.session_state:
        st.session_state["pending_scroll_anchor"] = None
    valid_keys = {block[0] for block in blocks}
    if st.session_state["active_analysis_block"] not in valid_keys:
        st.session_state["active_analysis_block"] = None

    active_key = st.session_state["active_analysis_block"]

    st.markdown(f"<div id='{scroll_anchor_id}'></div>", unsafe_allow_html=True)
    with st.expander("🗺️ Mapa de análisis técnico", expanded=st.session_state["analysis_map_open"]):
        cols = st.columns(len(blocks))
        for col, (key, block_name, title, subtitle, accent, border_color, bg_color, label_color, soft_accent) in zip(cols, blocks):
            with col:
                is_active = active_key == key
                st.markdown(
                    f"""
                    <div class="analysis-card" style="--analysis-accent:{accent}; --analysis-border:{border_color}; --analysis-bg:{bg_color}; --analysis-label:{label_color}; --analysis-accent-soft:{soft_accent};">
                      <div class="analysis-card__eyebrow">{block_name}</div>
                      <div class="analysis-card__title">{escape(title)}</div>
                      <div class="analysis-card__sub">{'Vista activa para análisis' if is_active else escape(subtitle)}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                if st.button(
                    "Seleccionado" if is_active else "Abrir",
                    key=f"analysis_block_{key}",
                    use_container_width=True,
                    type="primary" if is_active else "secondary",
                    on_click=select_analysis_block,
                    args=(key, scroll_anchor_id),
                ):
                    pass

        content_container = st.container()

    if st.session_state.get("pending_scroll_anchor") == scroll_anchor_id:
        restore_scroll_to_anchor(scroll_anchor_id)
        st.session_state["pending_scroll_anchor"] = None

    return active_key, content_container


@contextmanager
def section_block(title: str, expanded: bool = True):
    """Crea un bloque plegable con encabezado estilizado."""
    with st.expander(title, expanded=expanded):
        section_header(title)
        yield


def sidebar_section(title: str) -> None:
    st.markdown(f"<div class='sidebar-section'>{escape(title)}</div>", unsafe_allow_html=True)


def comment_box(title: str, body_segments) -> str:
    """Construye un bloque HTML reutilizable para notas de interpretación."""
    if isinstance(body_segments, str):
        body = body_segments
    else:
        body = "".join(body_segments)
    return f"<div class='comment-box'><div class='comment-title'>{title}</div>{body}</div>"


def comment_paragraph(text: str) -> str:
    return f"<p>{text}</p>"


# Recursos compartidos (imágenes hero, etc.)
_HERO_CANDIDATES = [
    (Path(__file__).parent / "pages" / "assets" / "hero_vawt.jpg").resolve(),
    (Path(__file__).parent / "pages" / "hero_vawt.jpg").resolve(),
    (Path(__file__).parent / "assets" / "hero_vawt.jpg").resolve(),
    (Path(__file__).parent / "hero_vawt.jpg").resolve(),
]
_HERO_CANDIDATES[0].parent.mkdir(parents=True, exist_ok=True)


def _hero_path():
    for candidate in _HERO_CANDIDATES:
        if candidate.exists():
            return candidate
    return None


def render_hero_banner() -> None:
    """Inserta la imagen panorámica superior de manera responsiva."""
    hero_title = "Plataforma técnica VAWT"
    hero_subtitle = (
        "Panel interactivo para analizar aerodinámica, tren mecánico, generador y operación "
        "del piloto de turbina eólica vertical híbrida."
    )
    path = _hero_path()
    if path:
        suffix = path.suffix.lower()
        mime = "image/jpeg"
        if suffix == ".png":
            mime = "image/png"
        elif suffix == ".webp":
            mime = "image/webp"
        encoded = base64.b64encode(path.read_bytes()).decode()
        st.markdown(
            f"""
            <div class='hero-banner' style="background-image:url('data:{mime};base64,{encoded}');">
              <div class='hero-banner__content'>
                <div class='hero-banner__eyebrow'>
                  <div class='hero-banner__icon'>📊</div>
                  <div class='hero-banner__chip'>Ingeniería y análisis</div>
                </div>
                <h1 class='hero-banner__title'>{escape(hero_title)}</h1>
                <p class='hero-banner__subtitle'>{escape(hero_subtitle)}</p>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.info(
            "Agrega la imagen panorámica en `pages/assets/hero_vawt.jpg` "
            "o en `pages/hero_vawt.jpg` para mostrarla en el encabezado.",
            icon="🖼️",
        )


def parse_float_list(text: str) -> list[float]:
    """
    Convierte una cadena separada por comas en una lista de floats.
    Ignora entradas vacías o no numéricas.
    """
    values = []
    for raw in str(text).split(","):
        token = raw.strip()
        if not token:
            continue
        try:
            values.append(float(token))
        except ValueError:
            continue
    return values


@st.cache_data(show_spinner=False)
def read_uploaded_csv(file_bytes: bytes) -> pd.DataFrame:
    return pd.read_csv(io.BytesIO(file_bytes))


def _numeric_column_name(value) -> float | None:
    try:
        text = str(value).strip().replace(",", ".")
        if not text:
            return None
        return float(text)
    except Exception:
        return None


def detect_wind_height_profile(df_in: pd.DataFrame) -> tuple[bool, list[str], str | None]:
    height_cols = []
    for col in df_in.columns:
        height = _numeric_column_name(col)
        if height is None or height <= 0:
            continue
        series = pd.to_numeric(df_in[col], errors="coerce")
        if series.notna().sum() >= max(5, int(len(df_in) * 0.2)):
            height_cols.append(col)
    time_col = None
    for col in df_in.columns:
        if col in height_cols:
            continue
        parsed = pd.to_datetime(df_in[col], errors="coerce")
        if parsed.notna().sum() >= max(5, int(len(df_in) * 0.2)):
            time_col = col
            break
    return len(height_cols) >= 3, height_cols, time_col


def default_turbine_resource_height(p_nom_kw: float) -> float:
    """Altura efectiva de recurso acordada para cada tamaño de turbina."""
    try:
        return 24.0 if float(p_nom_kw) >= 40.0 else 14.0
    except Exception:
        return 14.0


def _fit_power_law_speed(row: np.ndarray, heights_arr: np.ndarray, target_height: float) -> tuple[float, float]:
    valid = np.isfinite(row) & np.isfinite(heights_arr) & (row > 0) & (heights_arr > 0)
    if valid.sum() < 2:
        return np.nan, np.nan
    x = np.log(heights_arr[valid])
    y = np.log(row[valid])
    alpha, log_v_ref = np.polyfit(x, y, 1)
    target_speed = float(np.exp(log_v_ref + alpha * np.log(target_height)))
    return target_speed, float(alpha)


def build_wind_profile_inputs(df_in: pd.DataFrame, height_cols: list[str], target_height: float, time_col: str | None = None) -> dict:
    numeric_profile = pd.DataFrame()
    heights = []
    for col in height_cols:
        height = _numeric_column_name(col)
        if height is None:
            continue
        numeric_profile[str(height)] = pd.to_numeric(df_in[col], errors="coerce")
        heights.append(float(height))
    if numeric_profile.empty:
        return {}

    ordered = sorted(zip(heights, numeric_profile.columns), key=lambda item: item[0])
    heights_arr = np.array([item[0] for item in ordered], dtype=float)
    data = numeric_profile[[item[1] for item in ordered]].copy()
    data.columns = [item[0] for item in ordered]
    data = data.dropna(how="all")
    if data.empty:
        return {}

    values = data.to_numpy(dtype=float)
    row_valid = np.isfinite(values).sum(axis=1) >= 2
    valid_index = data.index[row_valid]
    values = values[row_valid]
    if values.size == 0:
        return {}

    target_height = float(target_height) if np.isfinite(target_height) and target_height > 0 else float(heights_arr[0])
    fitted = [_fit_power_law_speed(row, heights_arr, target_height) for row in values]
    target_series_full = np.array([item[0] for item in fitted], dtype=float)
    alpha_series = np.array([item[1] for item in fitted], dtype=float)
    target_series = target_series_full[np.isfinite(target_series_full) & (target_series_full >= 0)]
    if target_series.size < 5:
        return {}

    v_mean = float(np.mean(target_series))
    v_std = float(np.std(target_series, ddof=1)) if target_series.size > 1 else 0.0
    if v_mean > 0 and v_std > 0:
        k_est = float(np.clip((v_std / v_mean) ** -1.086, 1.0, 10.0))
        c_est = float(v_mean / gamma(1.0 + 1.0 / k_est))
    else:
        k_est = 2.0
        c_est = max(v_mean, 0.1) / gamma(1.5)

    mean_by_height = np.nanmean(values, axis=0)
    profile_summary = pd.DataFrame(
        {
            "Altura m": heights_arr,
            "Velocidad media m/s": mean_by_height,
            "P10 m/s": np.nanpercentile(values, 10, axis=0),
            "P50 m/s": np.nanpercentile(values, 50, axis=0),
            "P90 m/s": np.nanpercentile(values, 90, axis=0),
        }
    )
    profile_summary = profile_summary[np.isfinite(profile_summary["Velocidad media m/s"]) & (profile_summary["Velocidad media m/s"] > 0)]
    if len(profile_summary) >= 2:
        x = np.log(profile_summary["Altura m"].to_numpy(dtype=float))
        y = np.log(profile_summary["Velocidad media m/s"].to_numpy(dtype=float))
        alpha = float(np.polyfit(x, y, 1)[0])
    else:
        alpha = np.nan

    result = {
        "active": True,
        "mode": "wind_height_profile",
        "method": "Ley de potencia por timestamp: V(z)=a·z^alpha",
        "time_col": time_col,
        "target_height_m": target_height,
        "source_height_min_m": float(np.nanmin(heights_arr)),
        "source_height_max_m": float(np.nanmax(heights_arr)),
        "sample_count": int(target_series.size),
        "v_mean": v_mean,
        "v_std": v_std,
        "weibull_k": k_est,
        "weibull_c": c_est,
        "shear_alpha": alpha,
        "shear_alpha_median": float(np.nanmedian(alpha_series)) if np.isfinite(alpha_series).any() else np.nan,
        "target_series_sample": target_series[:5000].tolist(),
        "profile_summary": profile_summary.to_dict("records"),
    }
    if time_col and time_col in df_in.columns:
        parsed_time = pd.to_datetime(df_in.loc[valid_index, time_col], errors="coerce")
        if parsed_time.notna().any():
            result["start"] = str(parsed_time.min())
            result["end"] = str(parsed_time.max())
            aligned = pd.DataFrame(
                {
                    "timestamp": parsed_time,
                    "v_target_m_s": target_series_full,
                    "alpha": alpha_series,
                }
            )
            aligned = aligned[
                aligned["timestamp"].notna()
                & np.isfinite(aligned["v_target_m_s"])
                & (aligned["v_target_m_s"] >= 0)
            ].sort_values("timestamp")
            if not aligned.empty:
                result["target_series_records"] = aligned.to_dict("records")
    return result


ENTEL_POWER_CURVE_URL = (
    "https://docs.google.com/spreadsheets/d/e/"
    "2PACX-1vS8Ms69pErI9GaORqBL2179NtK0E-H05Gvu26_kpkzl8EcY9U1CEJT1PtrZ7mbJMA/"
    "pub?output=csv"
)
ENTEL_MONITORING_URL = (
    "https://docs.google.com/spreadsheets/d/e/"
    "2PACX-1vSvumwJujnRf9GWUaSpv-1ztBrd2eTmGwtG2yfb8ceTBzL_6UQWMAdu2JUAyRENCw/"
    "pub?output=csv"
)
ENTEL_PROPOSAL_7810_URL = (
    "https://docs.google.com/spreadsheets/d/e/"
    "2PACX-1vTMbuG9VMHtxEYLcLIHmw4s5Y6MHF1HwsMOD_sfyt8ZliE2c2_JRZaO7fRi-uacYQ/"
    "pub?output=csv&gid=2125370755"
)
ENTEL_INTRODUCTION_URL = (
    "https://docs.google.com/spreadsheets/d/e/"
    "2PACX-1vTMbuG9VMHtxEYLcLIHmw4s5Y6MHF1HwsMOD_sfyt8ZliE2c2_JRZaO7fRi-uacYQ/"
    "pub?output=csv&gid=1506621143"
)
ENTEL_INSTALLATION_CONDITIONS_URL = (
    "https://docs.google.com/spreadsheets/d/e/"
    "2PACX-1vTMbuG9VMHtxEYLcLIHmw4s5Y6MHF1HwsMOD_sfyt8ZliE2c2_JRZaO7fRi-uacYQ/"
    "pub?output=csv&gid=39270918"
)
ENTEL_SUPPLIER_EXPERIENCE_URL = (
    "https://docs.google.com/spreadsheets/d/e/"
    "2PACX-1vTMbuG9VMHtxEYLcLIHmw4s5Y6MHF1HwsMOD_sfyt8ZliE2c2_JRZaO7fRi-uacYQ/"
    "pub?output=csv&gid=563161092"
)
ENTEL_REQ_EXC_URL = (
    "https://docs.google.com/spreadsheets/d/e/"
    "2PACX-1vTMbuG9VMHtxEYLcLIHmw4s5Y6MHF1HwsMOD_sfyt8ZliE2c2_JRZaO7fRi-uacYQ/"
    "pub?output=csv&gid=1654158352"
)
ENTEL_OFFER_DIAMETER_M = 5.0
ENTEL_OFFER_ROTOR_HEIGHT_M = 7.0
ENTEL_OFFER_INSTALLATION_HEIGHT_M_10KW = 14.0
ENTEL_OFFER_MAST_HEIGHT_M = 6.0
ENTEL_OFFER_AREA_M2 = ENTEL_OFFER_DIAMETER_M * ENTEL_OFFER_ROTOR_HEIGHT_M


def _parse_locale_number(value) -> float:
    text = str(value).strip().replace("%", "")
    if not text or text.lower() in {"nan", "none"}:
        return np.nan
    if "," in text:
        text = text.replace(".", "").replace(",", ".")
    elif re.fullmatch(r"\d{1,3}(\.\d{3})+", text):
        text = text.replace(".", "")
    try:
        return float(text)
    except Exception:
        return np.nan


def _read_remote_csv_with_timeout(url: str, timeout: float = 5.0, **kwargs) -> pd.DataFrame:
    with urllib.request.urlopen(url, timeout=timeout) as response:
        payload = response.read()
    return pd.read_csv(io.BytesIO(payload), **kwargs)


@st.cache_data(show_spinner=False, ttl=900)
def load_entel_introduction_from_url(url: str = ENTEL_INTRODUCTION_URL) -> dict:
    fallback_text = (
        "Introducción de la Propuesta Técnica\n"
        "Fluxial Wind SpA presenta su propuesta técnica para el suministro de una solución "
        "de generación eólica distribuida de 10 kW, orientada a infraestructura de "
        "telecomunicaciones y condiciones de viento variable."
    )
    try:
        raw = _read_remote_csv_with_timeout(url, timeout=5.0, header=None, dtype=str).fillna("")
        flat_values = [
            str(value).replace("\xa0", " ").strip()
            for value in raw.to_numpy().ravel().tolist()
            if str(value).replace("\xa0", " ").strip()
        ]
        source = "URL Google Sheets - Introducción"
    except Exception:
        flat_values = [fallback_text]
        source = "Fallback local"

    text = "\n".join(flat_values).strip()
    lines = [re.sub(r"\s+", " ", line).strip() for line in re.split(r"[\r\n]+", text) if line.strip()]
    title = lines[0] if lines else "Introducción de la Propuesta Técnica"
    paragraphs = lines[1:] if len(lines) > 1 else []
    return {
        "title": title,
        "paragraphs": paragraphs,
        "source": source,
        "url": url,
        "df": pd.DataFrame({"Sección": [title] * max(len(paragraphs), 1), "Texto": paragraphs or [text]}),
    }


@st.cache_data(show_spinner=False, ttl=900)
def load_entel_installation_conditions_from_url(url: str = ENTEL_INSTALLATION_CONDITIONS_URL) -> dict:
    fallback_df = pd.DataFrame([
        {"Documentación técnica solicitada": "Planos de montaje.", "Anexo de respaldo": "Anexo 1"},
        {"Documentación técnica solicitada": "Requerimientos de obra civil.", "Anexo de respaldo": "Anexo 2"},
        {"Documentación técnica solicitada": "Memoria de cálculo estructural.", "Anexo de respaldo": "Anexo 3"},
        {"Documentación técnica solicitada": "Cargas transmitidas a la fundación.", "Anexo de respaldo": "Anexo 4"},
        {"Documentación técnica solicitada": "Requisitos de puesta a tierra.", "Anexo de respaldo": "Anexo 5"},
        {"Documentación técnica solicitada": "Requisitos de seguridad operacional.", "Anexo de respaldo": "Anexo 6"},
    ])
    try:
        raw = _read_remote_csv_with_timeout(url, timeout=5.0, dtype=str).fillna("")
        raw = raw.map(lambda value: str(value).replace("\xa0", " ").strip())
        source = "URL Google Sheets - 5. Condiciones de Instalación"
    except Exception:
        return {
            "df": fallback_df,
            "source": "Fallback local",
            "url": url,
        }

    if raw.empty:
        clean_df = fallback_df
    else:
        raw.columns = [re.sub(r"\s+", " ", str(col).replace("\xa0", " ").strip()) for col in raw.columns]
        doc_col = next((col for col in raw.columns if "doc" in col.lower()), raw.columns[0])
        annex_col = next((col for col in raw.columns if "anexo" in col.lower()), raw.columns[1] if len(raw.columns) > 1 else raw.columns[0])
        clean_df = (
            raw[[doc_col, annex_col]]
            .rename(columns={doc_col: "Documentación técnica solicitada", annex_col: "Anexo de respaldo"})
            .replace("", np.nan)
            .dropna(how="all")
            .fillna("")
            .reset_index(drop=True)
        )
        clean_df = clean_df[clean_df["Documentación técnica solicitada"].astype(str).str.strip().ne("")]
        if clean_df.empty:
            clean_df = fallback_df

    return {
        "df": clean_df,
        "source": source,
        "url": url,
    }


@st.cache_data(show_spinner=False, ttl=900)
def load_entel_supplier_experience_from_url(url: str = ENTEL_SUPPLIER_EXPERIENCE_URL) -> dict:
    fallback_main = pd.DataFrame([
        {
            "N.º": "1",
            "Eje de experiencia": "Base tecnológica VAWT",
            "Evidencia declarada": "Capacidades especializadas en investigación, diseño, ingeniería e integración de aerogeneradores de eje vertical.",
        }
    ])
    fallback_docs = pd.DataFrame(columns=["N.º", "Tipo de respaldo", "Disponibilidad / alcance"])
    fallback_areas = pd.DataFrame(columns=["N.º", "Área técnica", "Aplicación principal"])
    try:
        raw = _read_remote_csv_with_timeout(url, timeout=5.0, header=None, dtype=str).fillna("")
        raw = raw.map(lambda value: str(value).replace("\xa0", " ").strip())
        source = "URL Google Sheets - 6-Experiencia proveedor"
    except Exception:
        return {
            "title": "6. EXPERIENCIA DEL PROVEEDOR",
            "subtitle": "",
            "main": fallback_main,
            "documents": fallback_docs,
            "areas": fallback_areas,
            "note": "",
            "source": "Fallback local",
            "url": url,
        }

    title = ""
    subtitle = ""
    section = ""
    main_rows = []
    document_rows = []
    area_rows = []
    note = ""

    for _, row in raw.iterrows():
        values = [str(value).strip() for value in row.tolist()[:3]]
        first, second, third = (values + ["", "", ""])[:3]
        if not any(values):
            continue
        first_norm = re.sub(r"\s+", " ", first)
        if first_norm.startswith("Nota:"):
            note = first_norm
            continue
        upper_first = first_norm.upper()
        if upper_first == "6. EXPERIENCIA DEL PROVEEDOR":
            title = first_norm
            section = ""
            continue
        if first_norm.startswith("Proceso "):
            subtitle = first_norm
            continue
        if upper_first == "RESPALDO DOCUMENTAL":
            section = "documents"
            continue
        if upper_first == "ÁREAS TÉCNICAS DE EXPERIENCIA":
            section = "areas"
            continue
        if first_norm in {"N.º", "N°", "Nº"}:
            if second == "Eje de experiencia":
                section = "main"
            elif second == "Tipo de respaldo":
                section = "documents"
            elif second == "Área técnica":
                section = "areas"
            continue
        if section == "main" and first_norm and second and third:
            main_rows.append({"N.º": first_norm, "Eje de experiencia": second, "Evidencia declarada": third})
        elif section == "documents" and first_norm and second and third:
            document_rows.append({"N.º": first_norm, "Tipo de respaldo": second, "Disponibilidad / alcance": third})
        elif section == "areas" and first_norm and second and third:
            area_rows.append({"N.º": first_norm, "Área técnica": second, "Aplicación principal": third})

    main_df = pd.DataFrame(main_rows) if main_rows else fallback_main
    docs_df = pd.DataFrame(document_rows) if document_rows else fallback_docs
    areas_df = pd.DataFrame(area_rows) if area_rows else fallback_areas
    return {
        "title": title or "6. EXPERIENCIA DEL PROVEEDOR",
        "subtitle": subtitle,
        "main": main_df,
        "documents": docs_df,
        "areas": areas_df,
        "note": note,
        "source": source,
        "url": url,
    }


@st.cache_data(show_spinner=False, ttl=900)
def load_entel_power_curve_from_url(url: str = ENTEL_POWER_CURVE_URL) -> pd.DataFrame:
    def fallback_df() -> pd.DataFrame:
        return pd.DataFrame({
            "v (m/s)": [0.0, 3.0, 4.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0, 14.0, 16.0, 17.9, 19.9],
            "rpm_rotor": [0.0, 21.8, 29.0, 43.5, 50.8, 58.1, 65.3, 77.0, 77.0, 77.0, 77.0, 77.0, 77.0, 0.0],
            "λ_efectiva": [np.nan, 1.9, 1.9, 1.9, 1.9, 1.9, 1.9, 2.0, 1.8, 1.7, 1.4, 1.3, 1.1, np.nan],
            "P_aero (kW)": [0.0, 0.200, 0.506, 1.854, 3.009, 4.564, 6.578, 9.084, 11.831, 10.305, 9.667, 10.194, 10.194, 0.0],
            "P_mec_gen (kW)": [0.0, 0.200, 0.506, 1.854, 3.009, 4.564, 6.578, 9.084, 11.831, 10.305, 9.667, 10.194, 10.194, 0.0],
            "P_el (kW)": [0.0, 0.043, 0.279, 1.415, 2.414, 3.767, 5.523, 7.705, 10.090, 8.772, 8.216, 8.676, 8.676, 0.0],
            "P_out (clip) kW": [0.0, 0.043, 0.279, 1.415, 2.414, 3.767, 5.523, 7.705, 10.090, 8.772, 8.216, 8.676, 8.676, 0.0],
            "η_gen (curve)": [np.nan, 0.216, 0.551, 0.763, 0.802, 0.825, 0.840, 0.848, 0.853, 0.851, 0.850, 0.851, 0.851, np.nan],
            "Cp_el_equiv": [np.nan, 0.346, 0.369, 0.400, 0.409, 0.416, 0.421, 0.424, 0.415, 0.278, 0.164, 0.116, 0.083, np.nan],
            "Cp_aero_equiv": [np.nan, 0.346, 0.369, 0.400, 0.409, 0.416, 0.421, 0.424, 0.415, 0.278, 0.164, 0.116, 0.083, np.nan],
            "Cp(λ_efectiva)": [np.nan, 0.346, 0.369, 0.400, 0.409, 0.416, 0.421, 0.424, 0.415, 0.278, 0.164, 0.116, 0.083, np.nan],
            "Estado curva URL": [
                "Detenida (bajo cut-in)", "Seguimiento λ=1,90", "Seguimiento λ=1,90", "Seguimiento λ=1,90",
                "Seguimiento λ=1,90", "Seguimiento λ=1,90", "Seguimiento λ=1,90", "Régimen nominal (77 rpm)",
                "Régimen nominal (77 rpm)", "Régimen nominal (77 rpm)", "Régimen nominal (77 rpm)",
                "Régimen nominal (77 rpm)", "Velocidad de corte (cut-out)", "Detenida (sobre cut-out)",
            ],
        })

    try:
        raw = _read_remote_csv_with_timeout(url, timeout=5.0, skiprows=3, dtype=str)
    except Exception:
        return fallback_df()
    if raw.empty:
        return fallback_df()

    norm_cols = {
        col: re.sub(r"\s+", " ", str(col).replace("\n", " ")).strip().lower()
        for col in raw.columns
    }

    def pick_col(*patterns: str):
        for col, normalized in norm_cols.items():
            if all(pattern in normalized for pattern in patterns):
                return col
        return None

    v_col = pick_col("velocidad", "viento")
    rpm_col = pick_col("velocidad", "giro")
    tsr_col = pick_col("tsr")
    p_mec_col = pick_col("potencia", "mec")
    p_net_col = pick_col("potencia", "el", "neta")
    eta_col = pick_col("rendimiento")
    cp_col = pick_col("cp")
    estado_col = pick_col("estado")
    if not v_col or not p_net_col:
        return fallback_df()

    out = pd.DataFrame()
    out["v (m/s)"] = raw[v_col].map(_parse_locale_number)
    out["rpm_rotor"] = raw[rpm_col].map(_parse_locale_number) if rpm_col else np.nan
    out["λ_efectiva"] = raw[tsr_col].map(_parse_locale_number) if tsr_col else np.nan
    p_mec_w = raw[p_mec_col].map(_parse_locale_number) if p_mec_col else np.nan
    p_net_w = raw[p_net_col].map(_parse_locale_number)
    out["P_aero (kW)"] = pd.to_numeric(p_mec_w, errors="coerce") / 1000.0
    out["P_mec_gen (kW)"] = pd.to_numeric(p_mec_w, errors="coerce") / 1000.0
    out["P_el (kW)"] = pd.to_numeric(p_net_w, errors="coerce") / 1000.0
    out["P_out (clip) kW"] = pd.to_numeric(p_net_w, errors="coerce") / 1000.0
    out["η_gen (curve)"] = raw[eta_col].map(_parse_locale_number) / 100.0 if eta_col else np.nan
    out["Cp_el_equiv"] = raw[cp_col].map(_parse_locale_number) if cp_col else np.nan
    out["Cp_aero_equiv"] = out["Cp_el_equiv"]
    out["Cp(λ_efectiva)"] = out["Cp_el_equiv"]
    out["Estado curva URL"] = raw[estado_col].astype(str) if estado_col else ""

    out = out[np.isfinite(out["v (m/s)"]) & np.isfinite(out["P_out (clip) kW"])].copy()
    out = out.sort_values("v (m/s)").drop_duplicates("v (m/s)", keep="last")
    out = out[out["v (m/s)"] >= 0]
    return out.reset_index(drop=True) if not out.empty else fallback_df()


@st.cache_data(show_spinner=False, ttl=900)
def load_entel_monitoring_from_url(url: str = ENTEL_MONITORING_URL) -> dict:
    def fallback_payload() -> dict:
        rows = [
            ("Monitoreo en Tiempo Real", "Potencia instantánea", "Visualización en tiempo real de la potencia generada por el aerogenerador y de la potencia gestionada por el sistema eléctrico.", "Controlador eléctrico del aerogenerador / Inversor híbrido trifásico", "Plataforma de monitoreo del aerogenerador / plataforma de gestión energética. Tecnología: telemetría digital remota, medición de variables eléctricas y supervisión web/app.", "Cumple"),
            ("Monitoreo en Tiempo Real", "Energía acumulada", "Registro y consulta de la energía acumulada durante la operación del piloto.", "Inversor híbrido trifásico", "Plataforma de gestión y monitoreo energético. Tecnología: medición digital de energía, registro histórico y consulta remota.", "Cumple"),
            ("Monitoreo en Tiempo Real", "Velocidad del viento", "Monitoreo en tiempo real de la velocidad del viento y de las principales variables meteorológicas del emplazamiento.", "Estación meteorológica multiparámetro para monitoreo eólico y ambiental", "Plataforma de monitoreo meteorológico remoto. Tecnología: sensores digitales multiparámetro, transmisión inalámbrica y registro remoto de datos.", "Cumple"),
            ("Monitoreo en Tiempo Real", "RPM del rotor", "Monitoreo en tiempo real de las RPM del rotor del aerogenerador.", "Controlador eléctrico del aerogenerador", "Plataforma de monitoreo del aerogenerador. Tecnología: telemetría digital de velocidad de rotación y registro remoto de la variable.", "Cumple"),
            ("Monitoreo en Tiempo Real", "Estado operativo", "Visualización del estado de operación del aerogenerador y del sistema eléctrico asociado.", "Controlador eléctrico del aerogenerador / Inversor híbrido trifásico", "Plataformas de monitoreo operacional y energético. Tecnología: telemetría digital de estados de operación y supervisión remota.", "Cumple"),
            ("Monitoreo en Tiempo Real", "Alarmas y eventos", "Visualización y registro de alarmas, protecciones y eventos operacionales relevantes.", "Controlador eléctrico del aerogenerador / Inversor híbrido trifásico", "Plataformas de monitoreo operacional y energético. Tecnología: registro digital de eventos y alarmas con supervisión remota.", "Cumple"),
            ("Plataforma", "Acceso vía navegador web", "Acceso remoto a las principales variables y registros mediante navegador web.", "Sistemas de monitoreo del aerogenerador, sistema eléctrico y estación meteorológica", "Plataformas web de monitoreo remoto. Tecnología: telemetría remota con acceso web mediante conexión a Internet.", "Cumple"),
            ("Plataforma", "Aplicación móvil (deseable)", "Acceso móvil a las principales variables de operación, energía y condiciones meteorológicas.", "Sistemas de monitoreo del aerogenerador, sistema eléctrico y estación meteorológica", "Aplicaciones móviles de monitoreo remoto. Tecnología: aplicaciones conectadas a plataformas de telemetría y monitoreo remoto.", "Cumple"),
            ("Plataforma", "Históricos de al menos 24 meses", "Se contempla almacenamiento histórico de al menos 24 meses para las variables definidas del piloto.", "Sistema de adquisición y almacenamiento de datos", "Plataforma de almacenamiento y monitoreo histórico. Tecnología: registro digital con almacenamiento remoto y consulta histórica de datos.", "Contemplado"),
            ("Plataforma", "Exportación de datos en CSV o Excel", "Se contempla exportación de los registros del piloto en formatos CSV y/o Excel.", "Sistema de adquisición y almacenamiento de datos", "Plataforma de gestión y exportación de datos. Tecnología: exportación digital de registros históricos en formatos abiertos.", "Contemplado"),
            ("Plataforma", "Dashboard configurable", "Se contempla un dashboard configurable para visualizar las principales variables operacionales, energéticas y meteorológicas.", "Sistema de adquisición y monitoreo de datos", "Plataforma de visualización y gestión. Tecnología: paneles web configurables, indicadores y tendencias históricas.", "Contemplado"),
            ("Integración - Se valorará", "API abierta", "Capacidad de integración mediante API considerada dentro de la evolución de la plataforma de monitoreo.", "Sistema de comunicaciones e integración de datos", "Plataforma de integración. Tecnología: intercambio estructurado de datos mediante interfaces de software.", "En desarrollo"),
            ("Integración - Se valorará", "MQTT", "Integración mediante MQTT considerada dentro de la evolución del sistema de comunicaciones.", "Sistema de comunicaciones e integración de datos", "Plataforma de integración. Tecnología: mensajería ligera para telemetría e intercambio de datos.", "En desarrollo"),
            ("Integración - Se valorará", "Modbus TCP/IP", "Se contempla integración mediante Modbus TCP/IP para intercambio de variables con sistemas externos.", "Controlador / Sistema de comunicaciones e integración de datos", "Plataforma de integración. Tecnología: comunicación industrial sobre red Ethernet.", "Contemplado"),
            ("Integración - Se valorará", "SNMP", "Integración mediante SNMP considerada dentro de la evolución de las interfaces de supervisión.", "Sistema de comunicaciones e integración de datos", "Plataforma de integración. Tecnología: supervisión y gestión de dispositivos mediante protocolo de administración de red.", "En desarrollo"),
            ("Integración - Se valorará", "Integración con SCADA", "Se contempla capacidad de integración con plataformas SCADA para supervisión centralizada de variables y estados.", "Sistema de comunicaciones e integración de datos", "Plataforma SCADA / plataforma de integración. Tecnología: intercambio de datos mediante protocolos industriales compatibles.", "Contemplado"),
        ]
        df_monitor = pd.DataFrame(rows, columns=["Familia", "Requisito ENTEL", "Respuesta propuesta FW Axial", "Equipo", "Plataforma / tecnología de monitoreo", "Estado"])
        return {
            "title": "ENTEL - Ítem 4: Sistema de Monitoreo",
            "intro": "El sistema de monitoreo permitirá supervisar variables operacionales, energéticas y meteorológicas relevantes para evaluar el desempeño del piloto.",
            "source_note": "Fallback local: matriz de monitoreo embebida.",
            "df": df_monitor,
            "source": "Fallback local",
        }

    try:
        raw = _read_remote_csv_with_timeout(url, timeout=5.0, header=None, dtype=str).fillna("")
    except Exception:
        return fallback_payload()
    if raw.empty:
        return fallback_payload()

    title = str(raw.iloc[0, 0]).strip() if raw.shape[0] else "ENTEL - Ítem 4: Sistema de Monitoreo"
    intro = str(raw.iloc[1, 0]).strip() if raw.shape[0] > 1 else ""
    source_note = ""
    header_idx = None
    for idx, row in raw.iterrows():
        first = str(row.iloc[0]).strip().lower()
        if "requisito" in first and "entel" in first:
            header_idx = idx
            break
        if "fuente:" in first:
            source_note = str(row.iloc[0]).strip()
    if header_idx is None:
        return fallback_payload()

    records = []
    current_family = ""
    for _, row in raw.iloc[header_idx + 1:].iterrows():
        values = [str(value).strip() for value in row.tolist()[:5]]
        first = values[0] if values else ""
        if not any(values):
            continue
        if first.lower().startswith("estado:"):
            continue
        if first.lower().startswith("fuente:"):
            source_note = first
            continue
        if first and not any(values[1:]):
            current_family = first
            continue
        if not first:
            continue
        records.append({
            "Familia": current_family or "Sin clasificación",
            "Requisito ENTEL": values[0],
            "Respuesta propuesta FW Axial": values[1] if len(values) > 1 else "",
            "Equipo": values[2] if len(values) > 2 else "",
            "Plataforma / tecnología de monitoreo": values[3] if len(values) > 3 else "",
            "Estado": values[4] if len(values) > 4 else "",
        })

    df_monitor = pd.DataFrame(records)
    if df_monitor.empty:
        return fallback_payload()
    df_monitor["Estado"] = df_monitor["Estado"].replace("", "Sin estado")
    return {
        "title": title or "ENTEL - Ítem 4: Sistema de Monitoreo",
        "intro": intro,
        "source_note": source_note,
        "df": df_monitor,
        "source": "URL Google Sheets",
    }


def _entel_proposal_status(text: str) -> str:
    normalized = str(text or "").strip().lower()
    if not normalized:
        return "Sin respuesta"
    if "pendiente" in normalized:
        return "Pendiente"
    if "no contamos" in normalized:
        return "Brecha declarada"
    if "no aplica" in normalized:
        return "No aplica"
    if "una vez adjudicado" in normalized or "una vez iniciado" in normalized or "se entregará" in normalized:
        return "Entrega posterior"
    if "confirmado" in normalized:
        return "Confirmado"
    if "se adjunta" in normalized or "se indica" in normalized:
        return "Adjuntado / indicado"
    if "incluido" in normalized or "se incluye" in normalized:
        return "Incluido"
    return "Declarado"


def _entel_proposal_reading(point: str, status: str, concept: str) -> str:
    if status in {"Confirmado", "Incluido", "Adjuntado / indicado"}:
        return "Respuesta apta para respaldo de oferta; debe quedar trazada en anexo, contrato o protocolo de entrega."
    if status == "Entrega posterior":
        return "Compromiso aceptable solo si se fija hito de entrega, responsable y condición de aceptación previa al despacho o fabricación."
    if status == "Pendiente":
        return "Riesgo de postulación: debe cerrarse antes de presentar oferta final o declararse como desviación controlada."
    if status == "Brecha declarada":
        return "Brecha comercial/técnica explícita; requiere plan alternativo, alcance excluido o compromiso futuro documentado."
    if status == "No aplica":
        return "No aplica al suministro declarado; conviene justificarlo para evitar observación del evaluador."
    return "Requiere respaldo documental y trazabilidad para evaluación de licitación."


@st.cache_data(show_spinner=False, ttl=900)
def load_entel_proposal_7810_from_url(url: str = ENTEL_PROPOSAL_7810_URL) -> dict:
    def fallback_df() -> pd.DataFrame:
        rows = [
            ("7", "7.- Garantias", "Lista de repuestos críticos", "", "Se Adjunta en oferta técnica"),
            ("7", "7.- Garantias", "Capacitación", "", "Se incluye, capacitación presencial."),
            ("7", "7.- Garantias", "Asistencia en terreno", "Acompañamiento en el montaje y puesta en marcha", "Se incluye, traslado y hospedaje a costo reembolsable."),
            ("7", "7.- Garantias", "Equipos y Fabricación", "24 meses desde aceptación provisional o 30 meses desde entrega, lo que ocurra primero, sujeto a negociación", "Confirmado"),
            ("7", "7.- Garantias", "Reparaciones/reemplazos", "12 meses desde la intervención o saldo de garantía, el período mayor.", "Confirmado"),
            ("8", "8. Repuestos y Servicio Local", "Inventario local", "El oferente deberá indicar", "Se indica en listado de repuestos críticos, Se adjunta Anexo"),
            ("8", "Repuestos Críticos", "Rodamientos", "El oferente deberá indicar", "Se indica en listado de repuestos críticos, Se adjunta Anexo"),
            ("8", "Servicio Técnico", "Personal técnico certificado en Chile", "El oferente deberá indicar", "FW cuenta con un equipo técnico especializado, disponible durante el servicio, montaje y puesta en marcha."),
            ("8", "Servicio Técnico", "Contratos de mantenimiento preventivo y correctivo", "El oferente deberá indicar", "Actualmente no contamos con servicios de este tipo, debido a que aún estamos en una etapa de pilotaje."),
            ("9", "9. Importación y Logística", "Plazo, bodegaje y entrega física en Santiago de Chile", "", "Entrega física en Santiago en plazo máximo de 110 días corridos, con bodegaje de hasta dos meses sin costo adicional."),
            ("10", "10. Documentación Técnica Requerida", "Datasheet oficial", "La propuesta deberá incluir", "Se Adjunta en oferta técnica"),
            ("10", "10. Documentación Técnica Requerida", "Certificaciones", "La propuesta deberá incluir", "Se compartiran una vez adjudicado el servicio e iniciado el proceso de fabricación"),
            ("10", "10. Documentación Técnica Requerida", "Plan de mantenimiento", "La propuesta deberá incluir", "PENDIENTE - JOSE"),
            ("11", "11- Requisitos de Seguridad", "Normativa eléctrica", "SEC - RGR N°03/2020", "Cumple"),
            ("11", "11- Requisitos de Seguridad", "Prevención de riesgos", "Ley N°16.744", "Cumple"),
            ("12", "12- ALCANCES, SALVEDADES Y EXCEPCIONES DE LA OFERTA TÉCNICA", "Alcance General de la Oferta y Naturaleza del Suministro", "Alcance del suministro", "Unidad piloto VAWT de 10 kW para validación técnica y operacional."),
        ]
        return pd.DataFrame(rows, columns=["Punto RFP", "Subcapítulo", "Concepto", "Solicitud / recomendación RFP", "Respuesta incluida en oferta"])

    try:
        raw = _read_remote_csv_with_timeout(url, timeout=5.0, header=None, dtype=str).fillna("")
    except Exception:
        raw = pd.DataFrame()
    if raw.empty:
        parsed = fallback_df()
        source = "Fallback local"
    else:
        records = []
        current_point = ""
        current_subchapter = ""
        last_concept = ""
        header_mode = "three_col"
        for _, row in raw.iterrows():
            values = [str(value).replace("\xa0", " ").strip() for value in row.tolist()[:5]]
            first = values[0] if len(values) > 0 else ""
            second = values[1] if len(values) > 1 else ""
            third = values[2] if len(values) > 2 else ""
            fifth = values[4] if len(values) > 4 else ""
            if not any(values):
                continue
            first_clean = re.sub(r"\s+", " ", first)
            if current_point == "6" and first_clean.lower() == "eje de experiencia":
                continue
            if current_point == "6" and first_clean.lower() in {"n°", "nº", "n"}:
                if fifth and fifth.lower() != "etapa ejecutada":
                    records.append({
                        "Punto RFP": current_point,
                        "Subcapítulo": "6.2 Etapas de desarrollo tecnológico ejecutadas",
                        "Concepto": "",
                        "Solicitud / recomendación RFP": "",
                        "Respuesta incluida en oferta": fifth,
                    })
                continue
            if first_clean.lower() in {"conceptos", "concepto"}:
                second_norm = second.lower()
                third_norm = third.lower()
                if "incluido" in second_norm and not third:
                    header_mode = "two_col"
                    if current_point == "7":
                        current_subchapter = "7.- Garantias - Conceptos incluidos"
                elif "recomend" in second_norm and "incluido" in third_norm:
                    header_mode = "three_col"
                    if current_point == "7":
                        current_subchapter = "7.- Garantias - Recomendación / Solicitud RFP"
                continue
            if first_clean.lower() in {"categoría", "categoria"} and "normativa" in second.lower():
                header_mode = "three_col"
                continue
            if first_clean.lower() in {"tema / categoría", "tema / categoria"} and second.lower() == "punto":
                header_mode = "three_col"
                continue
            is_security_category = current_point == "11" and bool(re.match(r"^\d+\.", first_clean))
            if not is_security_category and re.match(r"^8\.\d+", first_clean):
                current_point = "8"
                current_subchapter = first_clean
                header_mode = "three_col"
                continue
            point_match = None if is_security_category else re.match(r"^(5|6|7|8|9|10|11|12)(?:\.|-)", first_clean)
            if point_match:
                current_point = point_match.group(1)
                if current_point == "5":
                    current_subchapter = "5. Condiciones de Instalación"
                elif current_point == "6":
                    current_subchapter = "6. Experiencia del Proveedor"
                elif current_point == "7":
                    current_subchapter = "7.- Garantias"
                elif current_point == "8":
                    current_subchapter = "8. Repuestos y Servicio Local"
                elif current_point == "9":
                    current_subchapter = "9. Importación y Logística"
                elif current_point == "10":
                    current_subchapter = "10. Documentación Técnica Requerida"
                elif current_point == "11":
                    current_subchapter = "11- Requisitos de Seguridad"
                elif current_point == "12":
                    current_subchapter = "12- ALCANCES, SALVEDADES Y EXCEPCIONES DE LA OFERTA TÉCNICA"
                else:
                    current_subchapter = re.sub(r"^(5|6|7|8|9|10|11|12)\s*[\.\-]*\s*", "", first_clean).strip() or f"Punto {current_point}"
                header_mode = "three_col"
                last_concept = ""
                continue
            if current_point == "7" and first_clean in {"Garantía de Disponibilidad", "SLA de soporte (Service Level Agreement) - Acuerdo de Nivel de Servicio"}:
                current_subchapter = "Garantía de Disponibilidad / SLA de soporte (Service Level Agreement) - Acuerdo de Nivel de Servicio"
                header_mode = "three_col"
                continue
            if current_point not in {"5", "6", "7", "8", "9", "10", "11", "12"}:
                continue
            if current_point == "6":
                is_numbered_stage = bool(re.match(r"^\d+$", first_clean))
                valid_summary_axis = first_clean in {
                    "Base tecnológica VAWT",
                    "Investigación y selección de configuración",
                    "Validación piloto e industrialización",
                    "Respaldo documental",
                }
                if is_numbered_stage:
                    if fifth:
                        records.append({
                            "Punto RFP": current_point,
                            "Subcapítulo": "6.2 Etapas de desarrollo tecnológico ejecutadas",
                            "Concepto": first_clean,
                            "Solicitud / recomendación RFP": second,
                            "Respuesta incluida en oferta": fifth,
                        })
                else:
                    if valid_summary_axis and second:
                        records.append({
                            "Punto RFP": current_point,
                            "Subcapítulo": "6.1 Síntesis de experiencia declarada",
                            "Concepto": first_clean or "Eje de experiencia",
                            "Solicitud / recomendación RFP": "",
                            "Respuesta incluida en oferta": second,
                        })
                    if fifth:
                        records.append({
                            "Punto RFP": current_point,
                            "Subcapítulo": "6.2 Etapas de desarrollo tecnológico ejecutadas",
                            "Concepto": "",
                            "Solicitud / recomendación RFP": "",
                            "Respuesta incluida en oferta": fifth,
                        })
                if first_clean:
                    last_concept = first_clean
                continue
            if current_point in {"9", "11", "12"}:
                concept = first_clean or last_concept or "Continuación"
            else:
                concept = first_clean or (f"Continuación - {last_concept}" if last_concept else "Continuación")
            if first_clean:
                last_concept = first_clean
            request_value = "" if header_mode == "two_col" else second
            response_value = second if header_mode == "two_col" else third
            records.append({
                "Punto RFP": current_point,
                "Subcapítulo": current_subchapter or f"Punto {current_point}",
                "Concepto": concept,
                "Solicitud / recomendación RFP": request_value,
                "Respuesta incluida en oferta": response_value,
            })
        parsed = pd.DataFrame(records) if records else fallback_df()
        source = "URL Google Sheets" if records else "Fallback local"

    parsed = parsed.copy()
    parsed["Estado de postulación"] = parsed["Respuesta incluida en oferta"].map(_entel_proposal_status)
    parsed["Lectura para licitación"] = parsed.apply(
        lambda row: _entel_proposal_reading(str(row["Punto RFP"]), str(row["Estado de postulación"]), str(row["Concepto"])),
        axis=1,
    )
    return {
        "df": parsed,
        "source": source,
        "title": "Puntos 7, 8 y 10 - Propuesta RFP",
        "url": url,
    }


@st.cache_data(show_spinner=False, ttl=900)
def load_entel_req_exc_from_url(url: str = ENTEL_REQ_EXC_URL) -> dict:
    def fallback_df() -> pd.DataFrame:
        rows = [
            (
                "Solución de eje vertical VAWT compatible con la envolvente e interfaz del proyecto.",
                "Plano general, ficha técnica y modelo 3D o plano de conjunto.",
                "Pendiente de validación documental",
            ),
            (
                "Potencia nominal de 10 kW o capacidad equivalente, declarando velocidad de viento, densidad, rpm y condiciones eléctricas.",
                "Curva de potencia y tabla por bins.",
                "Curva de potencia cargada en simulador",
            ),
            (
                "Instrumentación y SCADA con registro de viento, potencia, rpm, tensión, corriente, estados, alarmas y disponibilidad.",
                "Lista de señales y arquitectura de datos.",
                "Cubierto en sistema de monitoreo",
            ),
        ]
        return pd.DataFrame(rows, columns=["Requisito excluyente", "Evidencia mínima", "Estado"])

    try:
        raw = _read_remote_csv_with_timeout(url, timeout=5.0, dtype=str).fillna("")
    except Exception:
        raw = pd.DataFrame()
    if raw.empty:
        req_df = fallback_df()
        source = "Fallback local"
    else:
        raw.columns = [re.sub(r"\s+", " ", str(col)).strip() for col in raw.columns]
        req_col = next((col for col in raw.columns if "requisito" in col.lower()), None)
        evidence_col = next((col for col in raw.columns if "evidencia" in col.lower()), None)
        status_col = next((col for col in raw.columns if "estado" in col.lower()), None)
        if not req_col:
            req_df = fallback_df()
            source = "Fallback local"
        else:
            req_df = pd.DataFrame({
                "Requisito excluyente": raw[req_col].astype(str).str.strip(),
                "Evidencia mínima": raw[evidence_col].astype(str).str.strip() if evidence_col else "",
                "Estado": raw[status_col].astype(str).str.strip() if status_col else "",
            })
            req_df = req_df[req_df["Requisito excluyente"].astype(str).str.len() > 0].reset_index(drop=True)
            if req_df.empty:
                req_df = fallback_df()
                source = "Fallback local"
            else:
                req_df["Estado"] = req_df["Estado"].replace("", "Sin estado declarado")
                source = "URL Google Sheets - Req.exc"
    return {
        "df": req_df,
        "source": source,
        "title": "3.1 Características Generales",
        "url": url,
    }


@st.cache_data(show_spinner=False)
def build_default_polar_rows() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "alpha_deg": list(range(-10, 21, 5)),
            "Cl": [-0.90, -0.45, 0.00, 0.52, 0.90, 1.10, 1.20],
            "Cd": [0.020, 0.015, 0.012, 0.017, 0.025, 0.030, 0.035],
        }
    )


def normalize_polar_table_state(value) -> pd.DataFrame:
    default_df = build_default_polar_rows().copy()
    expected_cols = ["alpha_deg", "Cl", "Cd"]

    if isinstance(value, pd.DataFrame):
        df_value = value.copy()
    elif isinstance(value, list):
        df_value = pd.DataFrame(value)
    elif isinstance(value, dict):
        try:
            df_value = pd.DataFrame(value)
        except Exception:
            try:
                df_value = pd.DataFrame.from_records(value)
            except Exception:
                return default_df
    else:
        return default_df

    if df_value.empty:
        return default_df

    for col in expected_cols:
        if col not in df_value.columns:
            df_value[col] = default_df[col]

    return df_value[expected_cols]


st.markdown("""
<style>

.block-container {
    padding-top: 1.2rem !important;     /* Estaba en 5–6rem → reducimos a ~1 */
    max-width: min(100%, 1840px) !important;
    width: 100% !important;
    padding-left: 1.4rem !important;
    padding-right: 1.4rem !important;
}

div[data-testid="stAppViewContainer"] .main {
    width: 100% !important;
}

div[data-testid="stMain"],
main[data-testid="stMain"],
section.main,
.main {
    width: 100% !important;
    max-width: none !important;
}

div[data-testid="stMain"] > div,
main[data-testid="stMain"] > div {
    width: 100% !important;
    max-width: none !important;
}

section[data-testid="stSidebar"][aria-expanded="false"] ~ div[data-testid="stAppViewContainer"] .main .block-container,
section[data-testid="stSidebar"][aria-expanded="false"] ~ div[data-testid="stAppViewContainer"] .block-container {
    max-width: 100% !important;
    width: 100% !important;
    padding-left: 1.2rem !important;
    padding-right: 1.2rem !important;
}

section[data-testid="stSidebar"][aria-expanded="true"] {
    width: 252px !important;
    min-width: 252px !important;
    max-width: 252px !important;
}

section[data-testid="stSidebar"][aria-expanded="true"] > div {
    width: 252px !important;
    min-width: 252px !important;
    max-width: 252px !important;
}

section[data-testid="stSidebar"][aria-expanded="false"] {
    width: 0 !important;
    min-width: 0 !important;
    max-width: 0 !important;
    margin: 0 !important;
    padding: 0 !important;
}

section[data-testid="stSidebar"][aria-expanded="false"] > div {
    width: 0 !important;
    min-width: 0 !important;
    max-width: 0 !important;
    margin: 0 !important;
    padding: 0 !important;
}

@media (max-width: 900px) {
    .main .block-container,
    .block-container {
        max-width: 100% !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }

    section[data-testid="stSidebar"],
    section[data-testid="stSidebar"] > div {
        width: auto !important;
        min-width: auto !important;
        max-width: none !important;
    }
}

header[data-testid="stHeader"] {
    height: 2rem;
    padding-top: 0rem !important;
    padding-bottom: 0rem !important;
}

</style>
""", unsafe_allow_html=True)


st.markdown("""
<style>

/* Caja de recomendaciones (modo dark, tipo panel técnico) */
.rec-wrapper {
    margin-top: 1.4rem;
    margin-bottom: 1.6rem;
    padding: 1rem 1.3rem;
    border-radius: 12px;
    background: #0F172A;
    border: 1px solid rgba(148,163,184,0.45);
    box-shadow: 0 8px 22px rgba(15,23,42,0.65);
    color: #E5E7EB;
}

/* Cabecera de la sección */
.rec-header {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    margin-bottom: 0.7rem;
}

.rec-header-icon {
    font-size: 1.4rem;
}

.rec-header-text-main {
    font-size: 1.05rem;
    font-weight: 600;
}

.rec-header-chip {
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 0.16em;
    color: #9CA3AF;
}

/* Lista de recomendaciones */
.rec-item {
    font-size: 0.9rem;
    margin-bottom: 0.35rem;
    padding-left: 0.6rem;
    position: relative;
}

.rec-item::before {
    content: "●";
    position: absolute;
    left: -0.1rem;
    top: 0.05rem;
    font-size: 0.6rem;
    color: #22C55E;   /* punto verde tipo “OK técnico” */
}

/* Bloque de fórmulas dentro de la misma caja */
.formula-box {
    margin-top: 1rem;
    padding: 0.8rem 1rem;
    border-radius: 10px;
    background: rgba(15,23,42,0.96);
    border: 1px dashed rgba(148,163,184,0.8);
    font-size: 0.85rem;
}

.formula-title {
    font-weight: 600;
    margin-bottom: 0.45rem;
    color: #E5E7EB;
}

.formula-box ul {
    padding-left: 1.1rem;
    margin: 0;
}

.formula-box li {
    margin-bottom: 0.25rem;
}

</style>
""", unsafe_allow_html=True)



# =========================================================
# Utilidades base
# =========================================================
def rpm_from_tsr(v, D, tsr):
    R = D / 2.0
    return (30.0 / (pi * R)) * tsr * v


def tip_speed(v, tsr):
    return tsr * v


def solidity_int(N, c, R):
    """
    Solidez interna: σ_int = (N·c)/R ≈ π·σ_convencional.
    La solidez convencional es σ_conv = N·c / (π·R).
    """
    return (N * c) / R

def rpm_rotor_mppt(v_array, D, lam_opt, v_cut_in, v_rated, v_cut_out, rpm_rotor_rated):
    """
    Ley de control MPPT por regiones:
    - v < v_cut_in            -> rotor parado (rpm = 0)
    - v_cut_in ≤ v ≤ v_rated  -> MPPT: λ ≈ λ_opt  → rpm ∝ v
    - v_rated < v ≤ v_cut_out -> potencia limitada: rpm ≈ rpm_rotor_rated
    - v > v_cut_out           -> rotor parado (rpm = 0)
    """
    R = D / 2.0
    v_array = np.asarray(v_array, dtype=float)

    # rpm que mantiene λ = λ_opt (MPPT puro)
    rpm_mppt = (30.0 / (pi * R)) * lam_opt * v_array

    # iniciamos todo en 0 (parado)
    rpm = np.zeros_like(v_array)

    # Región MPPT (λ ≈ λ_opt)
    mask_reg2 = (v_array >= v_cut_in) & (v_array <= v_rated)
    rpm[mask_reg2] = rpm_mppt[mask_reg2]

    # Región potencia limitada (rpm constante)
    mask_reg3 = (v_array > v_rated) & (v_array <= v_cut_out)
    rpm[mask_reg3] = rpm_rotor_rated

    # v < cut-in o v > cut-out → rpm = 0
    return rpm


# =========================================================
# Modelo Cp(λ) con efectos de perfil de pala
# =========================================================
def build_cp_params(
    lam_opt_base=2.6,
    cmax_base=0.33,
    shape=1.0,
    sigma=0.24,
    helical=True,
    helix_angle_deg=60.0,      # 👈 NUEVO PARÁMETRO
    endplates=True,
    trips=True,
    struts_perf=True,
    airfoil_thickness=18.0,
    symmetric=True,
    pitch_deg=0.0,
):
    """
    Modelo paramétrico para Cp(λ) incluyendo:
    - Solidez σ
    - Helicoidal (con ángulo), end-plates, trips, struts perfilados
    - Perfil de pala: espesor relativo, simetría, ángulo de calaje
    - Efectos upwind / downwind (dynamic stall lumped)
    """
    lam_opt = lam_opt_base
    cmax    = cmax_base

    # -------------------------------
    # 0) Factor helicoidal (0–1)
    # -------------------------------
    # φ = 0° → f_h = 0  (pala recta)
    # φ = 90° → f_h = 1 (helicoidal "plena")
    helix_angle_deg = float(np.clip(helix_angle_deg, 0.0, 90.0))
    helix_factor = helix_angle_deg / 90.0

    # 1) Solidez: más σ → Cp↑ pero λ_opt↓
    lam_opt -= 0.30 * (sigma - 0.20)
    cmax    += 0.05 * (sigma - 0.20)

    # 2) Configuración global del rotor
    #    Aquí es donde la hélice entra en Cp_max y λ_opt
    if helical:
        # Cp_max(φ) = Cp_max,0 * (1 + k_Cp * f_h)
        cmax    += 0.03 * helix_factor
        # λ_opt(φ) = λ_opt,0 * (1 + k_λ * f_h) (lo aproximamos sumando)
        lam_opt += 0.10 * helix_factor

    if endplates:
        cmax += 0.01
    if trips:
        cmax += 0.015
    if not struts_perf:
        cmax -= 0.03

    # 3) Efectos del perfil: espesor relativo
    delta_t = (airfoil_thickness - 18.0) / 18.0
    drag_factor = 1.0 + 0.40 * max(delta_t, 0.0)      # >18% => más drag
    lam_opt *= (1.0 - 0.15 * delta_t)
    cmax    *= (1.0 - 0.25 * delta_t) / drag_factor

    # 4) Simetría vs asimétrico
    if not symmetric:
        cmax *= 1.08

    # 5) Pitch (calaje) y stall efectivo
    pitch_abs = abs(pitch_deg)
    stall_factor = np.exp(- (pitch_abs / 7.0) ** 2)   # α_char ~ 7°
    cmax *= stall_factor
    lam_opt *= (1.0 - 0.03 * pitch_abs / 5.0)

    # 6) Dynamic stall / upwind vs downwind
    f_up = 1.0
    f_down = 0.85 if symmetric else 0.80

    if helical:
        # f_up(φ)   = f_up,0   * (1 + k_up   * f_h)
        # f_down(φ) = f_down,0 * (1 + k_down * f_h)
        f_up   *= 1.0 + 0.03 * helix_factor
        f_down *= 1.0 + 0.05 * helix_factor

    f_avg = 0.5 * (f_up + f_down)
    if f_avg <= 0:
        f_avg = 1.0
    f_up_norm   = f_up   / f_avg
    f_down_norm = f_down / f_avg

    # 7) Límites físicos razonables
    lam_opt = float(np.clip(lam_opt, 1.6, 3.5))
    cmax    = float(np.clip(cmax,   0.15, 0.42))

    return {
        "lam_opt": lam_opt,
        "cmax":    cmax,
        "shape":   shape,
        "f_up":    f_up_norm,
        "f_down":  f_down_norm,
        "airfoil": {
            "t_rel":        airfoil_thickness,
            "symmetric":    symmetric,
            "pitch_deg":    pitch_deg,
            "stall_factor": stall_factor,
            "drag_factor":  drag_factor,
        },
        "helical": {
            "active":         helical,
            "helix_angle_deg": helix_angle_deg,
            "helix_factor":   helix_factor,
        }
    }



def cp_components(lambda_val, params):
    lam_opt = params["lam_opt"]
    cmax    = params["cmax"]
    shape   = params["shape"]
    f_up    = params.get("f_up", 1.0)
    f_down  = params.get("f_down", 1.0)

    lam = np.asarray(lambda_val, dtype=float)
    x = np.maximum(lam, 1e-6) / lam_opt

    cp_base = cmax * x * np.exp(1 - x) ** shape
    cp_base = np.clip(cp_base, 0.0, 0.5)

    f_avg = 0.5 * (f_up + f_down)
    if f_avg <= 0:
        f_avg = 1.0

    cp_up   = cp_base * (f_up   / f_avg)
    cp_down = cp_base * (f_down / f_avg)
    cp_avg  = cp_base

    return cp_avg, cp_up, cp_down


def cp_model(lambda_val, params):
    cp_avg, _, _ = cp_components(lambda_val, params)
    return cp_avg


def cp_curve_for_plot(cp_params):
    lam_vals = np.linspace(1.0, 4.0, 200)
    cp_avg, cp_up, cp_down = cp_components(lam_vals, cp_params)
    return pd.DataFrame({
        "λ":           lam_vals,
        "Cp_prom":     cp_avg,
        "Cp_upwind":   cp_up,
        "Cp_downwind": cp_down,
    })
# =========================================================
# Polar genérica Lift–Drag del perfil (modelo simplificado)
# =========================================================
def build_lift_drag_polar(t_rel: float, symmetric: bool):
    """
    Genera un polar Cl(α), Cd(α) y Cl/Cd(α) simplificado:
    - α en [-10°, 20°]
    - Pendiente dCl/dα ≈ 0.11 1/deg
    - α0 ≈ 0° simétrico, ≈ -2° camberado
    - Cd0 aumenta con espesor relativo
    - k_ind fija (drag inducido ~ Cl^2)
    """
    alpha_deg = np.linspace(-10.0, 20.0, 61)
    alpha0 = 0.0 if symmetric else -2.0          # α de sustentación nula

    # Pendiente de Cl (aprox. 2π rad ≈ 0.11 /deg)
    cl_slope = 0.11
    cl_lin = cl_slope * (alpha_deg - alpha0)

    # Stall suave usando saturación tipo tanh
    stall_deg = 12.0 if symmetric else 10.0
    cl_max_ref = cl_slope * (stall_deg - alpha0)
    cl_max = cl_max_ref * (1.0 if symmetric else 1.1)
    Cl = cl_max * np.tanh(cl_lin / max(cl_max, 1e-3))

    # Drag: Cd = Cd0 + k * Cl^2
    base_cd0 = 0.01 + 0.002 * (t_rel - 12.0) / 10.0
    base_cd0 = float(np.clip(base_cd0, 0.008, 0.04))
    k_ind = 0.02
    Cd = base_cd0 + k_ind * (Cl ** 2)

    ClCd = np.divide(Cl, Cd, out=np.zeros_like(Cl), where=(Cd > 0))

    return pd.DataFrame({
        "alpha_deg": alpha_deg,
        "Cl": Cl,
        "Cd": Cd,
        "ClCd": ClCd,
    })




# Potencia aerodinámica → eje generador (aplica solo pérdidas mecánicas)
def power_to_generator(v, D, H, lambda_eff, rho, eta_mec, cp_params):
    A   = D * H
    v   = np.asarray(v, dtype=float)
    lam = np.asarray(lambda_eff, dtype=float)

    cp_arr = cp_model(lam, cp_params)     # Cp(λ_efectiva)
    P_a = 0.5 * rho * A * (v ** 3) * cp_arr       # W rotor
    P_m = P_a * eta_mec                           # W eje generador
    return P_a, P_m, cp_arr


# Weibull
def weibull_pdf(v, k, c):
    return (k / c) * (v / c) ** (k - 1) * np.exp(-(v / c) ** k)


def aep_from_weibull(v_grid, P_grid_W, k, c):
    pdf = weibull_pdf(v_grid, k, c)
    Pw  = P_grid_W * pdf
    P_mean = np.trapz(Pw, v_grid)                 # W
    AEP_kWh = P_mean * 8760.0 / 1000.0           # kWh/año
    return AEP_kWh, P_mean


@st.cache_data(show_spinner=False)
def compute_base_results(
    D, H, N, c, eta_bear, eta_gear, helical, helix_angle_deg, endplates, trips,
    struts_perf, t_rel, is_symmetric, pitch_deg, control_mode, lam_opt_ctrl,
    v_cut_in, v_rated, v_cut_out, rpm_rotor_rated, G, rpm_gen_rated, rpm_v_exp,
    rho, mu, m_blade, lever_arm_pala, struts_per_blade, section_modulus_root,
    sigma_y_pala_mpa, strut_area_cm2, sigma_allow_strut_mpa, safety_target,
    T_gen_max, eta_gen_max, eta_elec, P_nom_kW, poles_total, pf_setpoint,
    Kt_nm_per_A, Ke_vsr_default, V_dc_nom, I_dc_nom, use_noise, Lw_ref_dB, r_obs,
    n_noise, v_min, v_max, tab_power_rpm, tab_power_kw, tab_volt_rpm, tab_volt_vll,
):
    R = D / 2.0
    A = D * H
    sig_int = solidity_int(N, c, R)
    sig_conv = sig_int / pi
    eta_mec = eta_bear * eta_gear

    cp_params = build_cp_params(
        lam_opt_base=2.6,
        cmax_base=0.33,
        shape=1.0,
        sigma=sig_int,
        helical=helical,
        helix_angle_deg=helix_angle_deg,
        endplates=endplates,
        trips=trips,
        struts_perf=struts_perf,
        airfoil_thickness=t_rel,
        symmetric=is_symmetric,
        pitch_deg=pitch_deg,
    )
    lambda_opt_teo = cp_params["lam_opt"]
    lambda_mppt = lam_opt_ctrl if control_mode == "MPPT (λ constante)" else None

    v_grid = np.arange(v_min, v_max + 1e-9, 0.5 if v_max - v_min > 1 else 0.1)

    if control_mode == "MPPT (λ constante)":
        rpm_rotor = rpm_rotor_mppt(
            v_array=v_grid,
            D=D,
            lam_opt=lam_opt_ctrl,
            v_cut_in=v_cut_in,
            v_rated=v_rated,
            v_cut_out=v_cut_out,
            rpm_rotor_rated=rpm_rotor_rated,
        )
        rpm_gen = rpm_rotor * G
    else:
        rpm_gen = np.zeros_like(v_grid)
        mask_reg2 = (v_grid >= v_cut_in) & (v_grid <= v_rated)
        if v_rated > 0:
            rpm_gen[mask_reg2] = rpm_gen_rated * (v_grid[mask_reg2] / v_rated) ** rpm_v_exp
        mask_reg3 = (v_grid > v_rated) & (v_grid <= v_cut_out)
        rpm_gen[mask_reg3] = rpm_gen_rated
        rpm_rotor = rpm_gen / max(G, 1e-6)

    rpm_rated_val = rpm_from_tsr(v_rated, D, lambda_mppt) if lambda_mppt is not None else np.nan
    rpm_rated_ctrl = float(np.interp(v_rated, v_grid, rpm_rotor)) if control_mode == "MPPT (λ constante)" else np.nan

    omega_rot = 2 * pi * rpm_rotor / 60.0
    omega_gen = 2 * pi * rpm_gen / 60.0

    lambda_eff = np.zeros_like(v_grid, dtype=float)
    mask_v = v_grid > 0
    lambda_eff[mask_v] = (omega_rot[mask_v] * R) / v_grid[mask_v]
    U_tip = lambda_eff * v_grid

    tsr_ref = (
        float(lam_opt_ctrl if lam_opt_ctrl is not None else lambda_mppt)
        if control_mode == "MPPT (λ constante)"
        else float(np.interp(v_rated, v_grid, lambda_eff)) if v_grid.size else np.nan
    )

    P_aero_W, P_mec_gen_W, cp_used = power_to_generator(v_grid, D, H, lambda_eff, rho, eta_mec, cp_params)

    tab_power_rpm = np.asarray(tab_power_rpm, dtype=float)
    tab_power_kw = np.asarray(tab_power_kw, dtype=float)
    tab_volt_rpm = np.asarray(tab_volt_rpm, dtype=float)
    tab_volt_vll = np.asarray(tab_volt_vll, dtype=float)

    P_gen_curve_W = interp_curve(rpm_gen, tab_power_rpm, tab_power_kw) * 1000.0
    V_LL_curve = interp_curve(rpm_gen, tab_volt_rpm, tab_volt_vll)

    T_rotor_Nm = np.divide(P_aero_W, np.maximum(omega_rot, 1e-6))
    T_gen_raw = np.divide(P_mec_gen_W, np.maximum(omega_gen, 1e-6))

    F_centripetal_series = m_blade * R * (omega_rot ** 2)
    g_per_blade_series = np.divide(
        F_centripetal_series,
        max(m_blade * 9.81, 1e-3),
        out=np.zeros_like(F_centripetal_series),
        where=(m_blade > 0),
    )
    M_root_series_Nm = np.divide(T_rotor_Nm, max(N, 1)) + F_centripetal_series * lever_arm_pala
    M_strut_series_Nm = np.divide(M_root_series_Nm, max(struts_per_blade, 1))

    W_root = max(section_modulus_root, 1e-6)
    sigma_root_MPa = (M_root_series_Nm / W_root) / 1e6
    allow_root_MPa = sigma_y_pala_mpa / max(safety_target, 1e-6)
    margin_root = np.divide(
        (allow_root_MPa - sigma_root_MPa),
        max(allow_root_MPa, 1e-6),
        out=np.zeros_like(sigma_root_MPa),
        where=np.isfinite(sigma_root_MPa),
    )

    strut_area_m2 = max(strut_area_cm2 * 1e-4, 1e-9)
    F_strut_series_N = np.divide(M_strut_series_Nm, max(lever_arm_pala, 1e-3))
    sigma_strut_MPa = (F_strut_series_N / strut_area_m2) / 1e6
    allow_strut_MPa = sigma_allow_strut_mpa / max(safety_target, 1e-6)
    margin_strut = np.divide(
        (allow_strut_MPa - sigma_strut_MPa),
        max(allow_strut_MPa, 1e-6),
        out=np.zeros_like(sigma_strut_MPa),
        where=np.isfinite(sigma_strut_MPa),
    )

    T_gen_Nm = np.minimum(T_gen_raw, T_gen_max) if T_gen_max > 0 else T_gen_raw
    P_mec_to_gen_W = np.minimum(P_mec_gen_W, T_gen_Nm * omega_gen)

    mask_reg3_ctrl = (v_grid > v_rated) & (v_grid <= v_cut_out)
    mask_off_ctrl = (v_grid < v_cut_in) | (v_grid > v_cut_out)
    eta_chain = max(eta_gen_max * eta_elec, 1e-6)
    P_mec_cap_nom_W = (P_nom_kW * 1000.0) / eta_chain if P_nom_kW > 0 else np.inf
    P_mec_cap_curve_W = P_gen_curve_W / max(eta_gen_max, 1e-6)
    P_mec_cap_W = np.minimum(P_mec_cap_nom_W, P_mec_cap_curve_W)

    P_mec_to_gen_W = np.where(mask_reg3_ctrl, np.minimum(P_mec_to_gen_W, P_mec_cap_W), P_mec_to_gen_W)
    P_mec_to_gen_W = np.where(mask_off_ctrl, 0.0, P_mec_to_gen_W)
    T_gen_Nm = np.minimum(T_gen_Nm, np.divide(P_mec_to_gen_W, np.maximum(omega_gen, 1e-6)))
    P_mec_gen_W = P_mec_to_gen_W.copy()

    P_el_gen_W = np.minimum(P_mec_to_gen_W * eta_gen_max, P_gen_curve_W)
    P_el_ac = P_el_gen_W * eta_elec
    P_el_ac_clip = np.minimum(P_el_ac, P_nom_kW * 1000.0)

    eta_gen_curve = np.divide(
        P_el_gen_W,
        np.maximum(P_mec_to_gen_W, 1.0),
        out=np.zeros_like(P_el_gen_W),
        where=(P_mec_to_gen_W > 0),
    )
    eta_gen_curve = np.clip(eta_gen_curve, 0.0, eta_gen_max)

    p_pairs = poles_total / 2.0
    f_e_Hz = p_pairs * rpm_gen / 60.0

    V_eff = np.maximum(V_LL_curve, 1.0)
    P_for_I = P_el_gen_W.copy()
    I_from_power = np.where(
        V_LL_curve < 10.0,
        0.0,
        np.divide(P_for_I, np.sqrt(3) * V_eff * pf_setpoint, out=np.zeros_like(P_for_I), where=(P_for_I > 0)),
    )
    Kt_safe = max(float(Kt_nm_per_A), 1e-6)
    I_from_torque = T_gen_Nm / Kt_safe
    I_A = np.maximum(I_from_power, I_from_torque)
    max_I_inv = float(np.nanmax(I_A)) if I_A.size else 0.0

    V_LL_from_Ke = Ke_vsr_default * omega_gen
    dc_link_capacity_W = max(V_dc_nom * I_dc_nom, 1e3)
    dc_util_series = np.divide(
        P_el_gen_W,
        dc_link_capacity_W,
        out=np.zeros_like(P_el_gen_W),
        where=(dc_link_capacity_W > 0),
    )

    denom = 0.5 * rho * A * (v_grid ** 3)
    Cp_aero = np.divide(P_aero_W, denom, out=np.zeros_like(v_grid), where=(v_grid > 0))
    Cp_shaft = np.divide(P_mec_to_gen_W, denom, out=np.zeros_like(v_grid), where=(v_grid > 0))
    P_out_W = P_el_ac_clip
    Cp_el = np.divide(P_out_W, denom, out=np.zeros_like(v_grid), where=(v_grid > 0))

    U_rel = np.sqrt((lambda_eff * v_grid) ** 2 + v_grid ** 2)
    Re_mid = np.zeros_like(v_grid)
    if mu > 0:
        Re_mid = rho * U_rel * c / mu

    Lw_dB = np.full_like(v_grid, np.nan, dtype=float)
    Lp_dB = np.full_like(v_grid, np.nan, dtype=float)
    if use_noise:
        U_tip_ref = float(np.interp(v_rated, v_grid, U_tip)) if v_grid[0] <= v_rated <= v_grid[-1] else float(U_tip[-1])
        U_ratio = np.divide(U_tip, max(U_tip_ref, 1e-3), out=np.ones_like(U_tip), where=(U_tip_ref > 0))
        Lw_dB = Lw_ref_dB + 10.0 * n_noise * np.log10(np.maximum(U_ratio, 1e-6))
        Lp_dB = Lw_dB - 20.0 * np.log10(max(r_obs, 1.0)) - 11.0

    f_1P = rpm_rotor / 60.0
    f_3P = 3.0 * f_1P

    df = pd.DataFrame({
        "v (m/s)": np.round(v_grid, 3),
        "rpm_rotor": np.round(rpm_rotor, 2),
        "rpm_gen": np.round(rpm_gen, 2),
        "λ_efectiva": np.round(lambda_eff, 2),
        "U_tip (m/s)": np.round(U_tip, 2),
        "Cp(λ_efectiva)": np.round(cp_used, 3),
        "Cp_aero_equiv": np.round(Cp_aero, 3),
        "Cp_shaft_equiv": np.round(Cp_shaft, 3),
        "Cp_el_equiv": np.round(Cp_el, 3),
        "Re (mid-span)": np.round(Re_mid, 0),
        "P_aero (kW)": np.round(P_aero_W / 1000.0, 2),
        "P_mec_gen (kW)": np.round(P_mec_gen_W / 1000.0, 2),
        "P_gen_curve (kW)": np.round(P_gen_curve_W / 1000.0, 2),
        "η_gen (curve)": np.round(eta_gen_curve, 3),
        "V_LL (V)": np.round(V_LL_curve, 1),
        "V_LL (Ke) [V]": np.round(V_LL_from_Ke, 1),
        "f_e (Hz)": np.round(f_e_Hz, 1),
        "f_1P (Hz)": np.round(f_1P, 2),
        "f_3P (Hz)": np.round(f_3P, 2),
        "T_rotor (N·m)": np.round(T_rotor_Nm, 0),
        "T_gen (N·m)": np.round(T_gen_Nm, 0),
        "F_cen/pala (kN)": np.round(F_centripetal_series / 1000.0, 2),
        "a_cen (g)": np.round(g_per_blade_series, 2),
        "M_base (kN·m)": np.round(M_root_series_Nm / 1000.0, 2),
        "M_por_strut (kN·m)": np.round(M_strut_series_Nm / 1000.0, 2),
        "sigma_root (MPa)": np.round(sigma_root_MPa, 2),
        "sigma_strut (MPa)": np.round(sigma_strut_MPa, 2),
        "margen_root (%)": np.round(margin_root * 100.0, 1),
        "margen_strut (%)": np.round(margin_strut * 100.0, 1),
        "P_el (kW)": np.round(P_el_ac / 1000.0, 2),
        "P_out (clip) kW": np.round(P_el_ac_clip / 1000.0, 2),
        "I_est (A)": np.round(I_A, 1),
        "Duty_DC (%)": np.round(dc_util_series * 100.0, 1),
        "Lw (dB)": np.round(Lw_dB, 1),
        "Lp_obs (dB)": np.round(Lp_dB, 1),
    })

    P_loss_mec_W = np.maximum(P_aero_W - P_mec_to_gen_W, 0.0)
    P_loss_gen_W = np.maximum(P_mec_to_gen_W - P_el_gen_W, 0.0)
    P_loss_elec_W = np.maximum(P_el_gen_W - P_el_ac, 0.0)
    P_loss_clip_W = np.maximum(P_el_ac - P_el_ac_clip, 0.0)
    df["P_loss_mec (kW)"] = np.round(P_loss_mec_W / 1000.0, 2)
    df["P_loss_gen (kW)"] = np.round(P_loss_gen_W / 1000.0, 2)
    df["P_loss_elec (kW)"] = np.round(P_loss_elec_W / 1000.0, 2)
    df["P_loss_clip (kW)"] = np.round(P_loss_clip_W / 1000.0, 2)

    return {
        "R": R, "A": A, "sig_int": sig_int, "sig_conv": sig_conv, "eta_mec": eta_mec,
        "cp_params": cp_params, "lambda_opt_teo": lambda_opt_teo, "lambda_mppt": lambda_mppt,
        "rpm_rated_val": rpm_rated_val, "rpm_rated_ctrl": rpm_rated_ctrl, "v_grid": v_grid,
        "rpm_rotor": rpm_rotor, "rpm_gen": rpm_gen, "omega_rot": omega_rot, "omega_gen": omega_gen,
        "lambda_eff": lambda_eff, "U_tip": U_tip, "tsr_ref": tsr_ref, "P_aero_W": P_aero_W,
        "P_mec_gen_W": P_mec_gen_W, "cp_used": cp_used, "P_gen_curve_W": P_gen_curve_W,
        "V_LL_curve": V_LL_curve, "T_rotor_Nm": T_rotor_Nm, "T_gen_Nm": T_gen_Nm,
        "F_centripetal_series": F_centripetal_series, "g_per_blade_series": g_per_blade_series,
        "M_root_series_Nm": M_root_series_Nm, "M_strut_series_Nm": M_strut_series_Nm,
        "sigma_root_MPa": sigma_root_MPa, "allow_root_MPa": allow_root_MPa,
        "margin_root": margin_root, "F_strut_series_N": F_strut_series_N,
        "sigma_strut_MPa": sigma_strut_MPa, "allow_strut_MPa": allow_strut_MPa,
        "margin_strut": margin_strut, "P_el_gen_W": P_el_gen_W, "P_el_ac": P_el_ac,
        "P_el_ac_clip": P_el_ac_clip, "eta_gen_curve": eta_gen_curve, "f_e_Hz": f_e_Hz,
        "I_A": I_A, "max_I_inv": max_I_inv, "V_LL_from_Ke": V_LL_from_Ke,
        "dc_util_series": dc_util_series, "P_out_W": P_out_W, "Cp_aero": Cp_aero,
        "Cp_shaft": Cp_shaft, "Cp_el": Cp_el, "Re_mid": Re_mid, "Lw_dB": Lw_dB,
        "Lp_dB": Lp_dB, "f_1P": f_1P, "f_3P": f_3P, "df": df,
        "P_loss_mec_W": P_loss_mec_W, "P_loss_gen_W": P_loss_gen_W,
        "P_loss_elec_W": P_loss_elec_W, "P_loss_clip_W": P_loss_clip_W,
    }

def alpha_cycle_deg(theta_deg, lam, pitch_deg=0.0):
    """
    Ángulo de ataque cinemático (modelo 2D ideal).
    alpha(θ) = atan2(sinθ, λ - cosθ) + pitch
    Retorna α en grados.
    """
    th = np.deg2rad(np.asarray(theta_deg, dtype=float))
    alpha_rad = np.arctan2(np.sin(th), (lam - np.cos(th)))
    return np.rad2deg(alpha_rad) + float(pitch_deg)



# =========================================================
# PDF
# =========================================================
def build_pdf_report(df_view, figs_dict, kpi_text=""):
    """
    Genera un PDF en memoria con:
    - Portada simple
    - Comentario de alto nivel
    - Tabla (vista actual, primeras 15 filas)
    - Gráficos clave como imágenes, cada uno con título + interpretación
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []

    # Portada
    story.append(Paragraph("Reporte técnico – VAWT + Generador", styles["Title"]))
    story.append(Spacer(1, 12))
    story.append(Paragraph("Síntesis para ingeniería de alto nivel", styles["Heading2"]))
    story.append(Spacer(1, 18))

    if kpi_text:
        story.append(Paragraph(kpi_text, styles["BodyText"]))
        story.append(Spacer(1, 18))

    # Tabla principal (vista actual)
    story.append(Paragraph(
        "Tabla de resultados (vista actual – primeras 15 filas)",
        styles["Heading2"]
    ))
    story.append(Spacer(1, 6))

    df_short = df_view.head(10).reset_index(drop=True)

    if not df_short.empty:
        df_horizontal = df_short.T.reset_index()
        df_horizontal = df_horizontal.rename(columns={"index": "Variable"})

        bin_labels = []
        for idx in range(df_short.shape[0]):
            v_val = df_short.loc[idx].get("v (m/s)")
            if pd.notna(v_val):
                bin_labels.append(f"Bin {idx+1} | v={v_val:.1f} m/s")
            else:
                bin_labels.append(f"Bin {idx+1}")

        df_horizontal.columns = ["Variable"] + bin_labels
        table_data = [df_horizontal.columns.tolist()] + df_horizontal.values.tolist()
    else:
        table_data = [["Sin datos"]]

    # Mejorar legibilidad de los encabezados (salto de línea Bin / velocidad)
    header_style = styles["BodyText"].clone("HeaderTable")
    header_style.textColor = colors.whitesmoke
    header_style.fontName = "Helvetica-Bold"

    header_cells = []
    for col_name in table_data[0]:
        text = str(col_name)
        if text.startswith("Bin"):
            text = text.replace(" | ", "<br/>")
        header_cells.append(Paragraph(text, header_style))
    table_data[0] = header_cells

    # Ajustar ancho de columnas
    page_width, _ = A4
    table_width = page_width - 2 * cm
    n_cols = len(table_data[0])
    col_widths = [table_width / max(n_cols, 1)] * n_cols

    table = Table(table_data, colWidths=col_widths, repeatRows=1)

    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0b1120")),
        ("TEXTCOLOR",  (0, 0), (-1, 0), colors.whitesmoke),
        ("ALIGN",      (0, 0), (-1, -1), "CENTER"),
        ("FONTNAME",   (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",   (0, 0), (-1, 0), 8),
        ("FONTSIZE",   (0, 1), (-1, -1), 7),
        ("GRID",       (0, 0), (-1, -1), 0.25, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1),
         [colors.whitesmoke, colors.lightgrey]),
    ]))

    story.append(table)
    story.append(Spacer(1, 12))
    story.append(PageBreak())

    interpretaciones = {
        "rpm rotor / generador vs velocidad de viento":
            "Muestra cómo crecen las rpm del rotor y del generador según la ley de control por regiones.",
        "Curva de potencia (según vista seleccionada)":
            "Relaciona potencia aerodinámica, mecánica y eléctrica para validar la integración aero–generador.",
        "Par en rotor / generador":
            "Dimensiona ejes y confirma que no se exceden los límites IEC ni los de ficha del generador.",
        "Momento flector en unión pala–struts":
            "Evolución del momento flector combinado (torque + fuerza centrífuga) para validar límites FEM/IEC en la raíz de pala.",
        "Cp equivalente por etapa":
            "Localiza la etapa con mayor degradación de rendimiento (rotor, tren mecánico o electrónica).",
        "Pérdidas por etapa":
            "Cuantifica dónde se concentran las pérdidas para priorizar rediseños.",
        "Corriente estimada vs velocidad de viento":
            "Asegura compatibilidad eléctrica y evita sobrecorrientes.",
        "Frecuencias 1P / 3P del rotor":
            "Chequea resonancias entre cargas periódicas y modos estructurales.",
        "Curva Cp(λ) – promedio y componentes":
            "Verifica que el TSR de control coincida con el máximo Cp disponible.",
        "Ruido estimado vs velocidad de viento":
            "Valida el cumplimiento acústico en el receptor crítico.",
        "🌬️ Distribución de viento vs curva de potencia":
            "Mezcla Weibull del sitio con la curva de potencia para derivar AEP y factor de planta."
    }

    if isinstance(figs_dict, dict):
        figs_iter = figs_dict.items()
    else:
        figs_iter = figs_dict

    # Gráficos
    for title, fig in figs_iter:
        story.append(Paragraph(title, styles["Heading2"]))
        story.append(Spacer(1, 6))

        png_bytes = fig.to_image(format="png", scale=2)
        img_buffer = io.BytesIO(png_bytes)
        img = Image(img_buffer, width=480, height=280)
        story.append(img)
        story.append(Spacer(1, 6))

        if title in interpretaciones:
            story.append(Paragraph(interpretaciones[title], styles["BodyText"]))
            story.append(Spacer(1, 18))

        story.append(PageBreak())

    doc.build(story)
    pdf_value = buffer.getvalue()
    buffer.close()
    return pdf_value


# =========================================================
# Descargas por pestaña / sub-bloque
# =========================================================
def _download_slug(text: str, max_len: int = 70) -> str:
    slug = re.sub(r"[^A-Za-z0-9]+", "_", str(text)).strip("_").lower()
    return (slug or "reporte")[:max_len]


def _sheet_name(name: str) -> str:
    safe = re.sub(r"[\[\]\:\*\?\/\\]", " ", str(name)).strip()
    return (safe or "Hoja")[:31]


def _rows_df(rows) -> pd.DataFrame:
    if isinstance(rows, pd.DataFrame):
        return rows.copy()
    return pd.DataFrame(rows or [])


def _unique_sheet_name(raw_name: str, used_names: set[str]) -> str:
    base = _sheet_name(raw_name)
    candidate = base
    counter = 2
    while candidate in used_names:
        suffix = f" {counter}"
        candidate = f"{base[:31 - len(suffix)]}{suffix}"
        counter += 1
    used_names.add(candidate)
    return candidate


def build_section_workbook(section_title: str, section_rows=None, extra_sheets=None) -> bytes:
    buffer = io.BytesIO()
    try:
        import xlsxwriter  # noqa: F401
        excel_engine = "xlsxwriter"
    except ModuleNotFoundError:
        excel_engine = "openpyxl"

    with pd.ExcelWriter(buffer, engine=excel_engine) as writer:
        used_sheet_names = set()
        context_df = globals().get("download_context_df", pd.DataFrame())
        if isinstance(context_df, pd.DataFrame) and not context_df.empty:
            context_df.to_excel(writer, sheet_name=_unique_sheet_name("Panel principal", used_sheet_names), index=False)

        section_df = _rows_df(section_rows)
        if not section_df.empty:
            section_df.to_excel(writer, sheet_name=_unique_sheet_name(section_title, used_sheet_names), index=False)

        for raw_name, raw_df in (extra_sheets or {}).items():
            sheet_df = _rows_df(raw_df)
            if not sheet_df.empty:
                sheet_df.to_excel(writer, sheet_name=_unique_sheet_name(raw_name, used_sheet_names), index=False)

        if excel_engine == "xlsxwriter":
            workbook = writer.book
            header_fmt = workbook.add_format({
                "bold": True,
                "font_color": "white",
                "bg_color": "#334155",
                "border": 1,
            })
            for worksheet in writer.sheets.values():
                worksheet.freeze_panes(1, 0)
                worksheet.set_row(0, None, header_fmt)
                worksheet.set_column(0, 0, 26)
                worksheet.set_column(1, 20, 18)
        else:
            from openpyxl.styles import Font, PatternFill

            for worksheet in writer.sheets.values():
                worksheet.freeze_panes = "A2"
                for cell in worksheet[1]:
                    cell.font = Font(bold=True, color="FFFFFF")
                    cell.fill = PatternFill("solid", fgColor="334155")
                worksheet.column_dimensions["A"].width = 26
                for col_letter in "BCDEFGHIJKLMNOPQRSTU":
                    worksheet.column_dimensions[col_letter].width = 18

    return buffer.getvalue()


def default_pdf_figures():
    return build_all_plotly_export_figures()


def _style_export_fig(title, fig, xaxis_title=None, yaxis_title=None, add_wind_lines=True):
    fig.update_layout(
        title=title,
        template="plotly_white",
        hovermode="x unified",
        legend_title=None,
        margin=dict(l=56, r=24, t=58, b=46),
    )
    if xaxis_title:
        fig.update_xaxes(title_text=xaxis_title)
    if yaxis_title:
        fig.update_yaxes(title_text=yaxis_title)
    if add_wind_lines:
        for x_val, color, label in [
            (globals().get("v_cut_in", np.nan), "rgba(100,116,139,0.7)", "v_cut-in"),
            (globals().get("v_rated", np.nan), "rgba(217,167,102,0.85)", "v_rated"),
            (globals().get("v_cut_out", np.nan), "rgba(217,95,95,0.8)", "v_cut-out"),
        ]:
            try:
                if np.isfinite(float(x_val)):
                    fig.add_vline(x=float(x_val), line_dash="dot", line_color=color, annotation_text=label)
            except Exception:
                pass
    return fig


def build_all_plotly_export_figures():
    df_src = globals().get("df", pd.DataFrame())
    if not isinstance(df_src, pd.DataFrame) or df_src.empty or "v (m/s)" not in df_src.columns:
        return []

    figs = []

    try:
        df_polar_export = build_lift_drag_polar(t_rel=t_rel, symmetric=is_symmetric)
        fig_polar_export = make_subplots(specs=[[{"secondary_y": True}]])
        fig_polar_export.add_trace(go.Scatter(x=df_polar_export["alpha_deg"], y=df_polar_export["Cl"], mode="lines", name="Cl"), secondary_y=False)
        fig_polar_export.add_trace(go.Scatter(x=df_polar_export["alpha_deg"], y=df_polar_export["Cd"], mode="lines", name="Cd"), secondary_y=True)
        fig_polar_export.add_trace(go.Scatter(x=df_polar_export["alpha_deg"], y=df_polar_export["ClCd"], mode="lines", name="Cl/Cd"), secondary_y=False)
        fig_polar_export.update_yaxes(title_text="Cl / ClCd", secondary_y=False)
        fig_polar_export.update_yaxes(title_text="Cd", secondary_y=True)
        figs.append(("🌀 Aerodinámica - Polar Lift-Drag del perfil", _style_export_fig("Polar Lift-Drag del perfil", fig_polar_export, "alpha [deg]", "Cl / ClCd", add_wind_lines=False)))
    except Exception:
        pass

    try:
        theta_deg_export = np.linspace(0, 360, 361)
        theta_rad_export = np.deg2rad(theta_deg_export)
        lam_used_export = max(float(tsr_ref), 0.1)
        alpha_base_export = np.rad2deg(np.arctan2(np.sin(theta_rad_export), lam_used_export + np.cos(theta_rad_export))) + float(pitch_deg)
        df_alpha_export = pd.DataFrame({"theta_deg": theta_deg_export, "alpha_deg": alpha_base_export})
        fig_alpha_export = px.line(df_alpha_export, x="theta_deg", y="alpha_deg", markers=False)
        figs.append(("🌀 Aerodinámica - Ciclo de ángulo de ataque", _style_export_fig("Ciclo de ángulo de ataque alpha(theta)", fig_alpha_export, "theta [deg]", "alpha [deg]", add_wind_lines=False)))
    except Exception:
        pass

    try:
        df_cp_export = cp_curve_for_plot(cp_params)
        fig_cp_curve_export = px.line(df_cp_export, x="λ", y=["Cp_prom", "Cp_upwind", "Cp_downwind"], markers=False)
        figs.append(("🌀 Aerodinámica - Curva Cp(lambda)", _style_export_fig("Curva Cp(lambda) promedio y componentes", fig_cp_curve_export, "lambda", "Cp", add_wind_lines=False)))
    except Exception:
        pass

    figure_specs = [
        ("⚙️ Operación - rpm rotor / generador", ["rpm_rotor", "rpm_gen"], "rpm"),
        ("⚙️ Operación - lambda, U_tip y frecuencia eléctrica", ["λ_efectiva", "U_tip (m/s)", "f_e (Hz)"], "valor"),
        ("📈 Potencia - Curva de potencia por etapa", ["P_aero (kW)", "P_mec_gen (kW)", "P_gen_curve (kW)", "P_el (kW)", "P_out (clip) kW"], "kW"),
        ("📈 Potencia - Cp equivalente por etapa", ["Cp(λ_efectiva)", "Cp_aero_equiv", "Cp_shaft_equiv", "Cp_el_equiv"], "Cp"),
        ("📈 Potencia - Pérdidas por etapa", ["P_loss_mec (kW)", "P_loss_gen (kW)", "P_loss_elec (kW)", "P_loss_clip (kW)"], "kW"),
        ("🛠️ Tren mecánico - Momentos y aceleración", ["M_base (kN·m)", "M_por_strut (kN·m)", "a_cen (g)"], "valor"),
        ("🛠️ Tren mecánico - Tensiones y márgenes", ["sigma_root (MPa)", "sigma_strut (MPa)", "margen_root (%)", "margen_strut (%)"], "valor"),
        ("🛠️ Tren mecánico - Par rotor / generador", ["T_rotor (N·m)", "T_gen (N·m)"], "N·m"),
        ("🛠️ Tren mecánico - Frecuencias 1P / 3P", ["f_1P (Hz)", "f_3P (Hz)"], "Hz"),
        ("🔌 Eléctrico - Tensión, frecuencia y corriente", ["V_LL (V)", "V_LL (Ke) [V]", "f_e (Hz)", "I_est (A)"], "valor"),
        ("🔌 Eléctrico - Potencia, eficiencia y duty DC", ["P_gen_curve (kW)", "P_el (kW)", "P_out (clip) kW", "η_gen (curve)", "Duty_DC (%)"], "valor"),
        ("🌬️ Recurso - Ruido estimado", ["Lw (dB)", "Lp_obs (dB)"], "dB"),
    ]
    for title, cols, y_label in figure_specs:
        y_cols = [col for col in cols if col in df_src.columns]
        if y_cols:
            fig = px.line(df_src, x="v (m/s)", y=y_cols, markers=True)
            figs.append((title, _style_export_fig(title, fig, "v (m/s)", y_label)))

    try:
        v_w_export = np.linspace(0.01, max(v_cut_out, v_max, 20.0), 400)
        P_curve_W_export = df_src["P_out (clip) kW"].values * 1000.0
        P_curve_W_export[df_src["v (m/s)"].values < v_cut_in] = 0.0
        P_curve_W_export[df_src["v (m/s)"].values > v_cut_out] = 0.0
        P_interp_export = np.interp(v_w_export, df_src["v (m/s)"].values, P_curve_W_export, left=0.0, right=0.0) / 1000.0
        pdf_w_export = weibull_pdf(v_w_export, k_w, c_w)
        fig_weib_export = make_subplots(specs=[[{"secondary_y": True}]])
        fig_weib_export.add_trace(go.Scatter(x=v_w_export, y=P_interp_export, mode="lines", name="P_out [kW]"), secondary_y=False)
        fig_weib_export.add_trace(go.Scatter(x=v_w_export, y=pdf_w_export, mode="lines", name="Weibull PDF"), secondary_y=True)
        fig_weib_export.update_yaxes(title_text="P_out [kW]", secondary_y=False)
        fig_weib_export.update_yaxes(title_text="Probabilidad", secondary_y=True)
        figs.append(("🌬️ Recurso - Weibull y curva de potencia", _style_export_fig("Distribución Weibull y curva de potencia", fig_weib_export, "v (m/s)", "P_out [kW]")))
    except Exception:
        pass

    return figs


def default_pdf_chart_specs():
    df_src = globals().get("df", pd.DataFrame())
    if not isinstance(df_src, pd.DataFrame) or df_src.empty or "v (m/s)" not in df_src.columns:
        return []

    candidates = [
        ("lambda efectiva, U_tip y frecuencia eléctrica", ["λ_efectiva", "U_tip (m/s)", "f_e (Hz)"], "valor"),
        ("rpm rotor / generador vs velocidad de viento", ["rpm_rotor", "rpm_gen"], "rpm"),
        ("Curva de potencia por etapa vs velocidad de viento", ["P_aero (kW)", "P_mec_gen (kW)", "P_gen_curve (kW)", "P_el (kW)", "P_out (clip) kW"], "kW"),
        ("Pérdidas por etapa", ["P_loss_mec (kW)", "P_loss_gen (kW)", "P_loss_elec (kW)", "P_loss_clip (kW)"], "kW"),
        ("Par en rotor / generador", ["T_rotor (N·m)", "T_gen (N·m)"], "N·m"),
        ("Cp equivalente por etapa", ["Cp(λ_efectiva)", "Cp_aero_equiv", "Cp_shaft_equiv", "Cp_el_equiv"], "Cp"),
        ("Cargas principales vs velocidad de viento", ["M_base (kN·m)", "M_por_strut (kN·m)", "a_cen (g)"], "valor"),
        ("Tensiones y márgenes estructurales", ["sigma_root (MPa)", "sigma_strut (MPa)", "margen_root (%)", "margen_strut (%)"], "valor"),
        ("Corriente estimada vs velocidad de viento", ["I_est (A)"], "A"),
        ("Tensión, frecuencia y corriente", ["V_LL (V)", "V_LL (Ke) [V]", "f_e (Hz)", "I_est (A)"], "valor"),
        ("Potencia, eficiencia y duty DC", ["P_gen_curve (kW)", "P_el (kW)", "P_out (clip) kW", "η_gen (curve)", "Duty_DC (%)"], "valor"),
        ("Frecuencias 1P / 3P del rotor", ["f_1P (Hz)", "f_3P (Hz)"], "Hz"),
        ("Ruido estimado vs velocidad de viento", ["Lw (dB)", "Lp_obs (dB)"], "dB"),
    ]

    specs = []
    for title, cols, y_label in candidates:
        y_cols = [col for col in cols if col in df_src.columns]
        if y_cols:
            specs.append({
                "title": title,
                "df": df_src[["v (m/s)"] + y_cols].copy(),
                "x_col": "v (m/s)",
                "y_cols": y_cols,
                "y_label": y_label,
            })
    try:
        df_polar_pdf = build_lift_drag_polar(t_rel=t_rel, symmetric=is_symmetric)
        specs.insert(0, {
            "title": "Aerodinámica - Polar Lift-Drag",
            "df": df_polar_pdf.copy(),
            "x_col": "alpha_deg",
            "y_cols": ["Cl", "Cd", "ClCd"],
            "y_label": "valor",
            "wind_lines": False,
        })
    except Exception:
        pass
    try:
        df_cp_pdf = cp_curve_for_plot(cp_params)
        specs.insert(1, {
            "title": "Aerodinámica - Curva Cp(lambda)",
            "df": df_cp_pdf.copy(),
            "x_col": "λ",
            "y_cols": ["Cp_prom", "Cp_upwind", "Cp_downwind"],
            "y_label": "Cp",
            "wind_lines": False,
        })
    except Exception:
        pass
    return specs


def matplotlib_chart_png(spec) -> bytes:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    chart_df = spec["df"].copy()
    x_col = spec["x_col"]
    y_cols = spec["y_cols"]

    fig, ax = plt.subplots(figsize=(8.2, 4.6), dpi=150)
    for idx, col in enumerate(y_cols):
        ax.plot(chart_df[x_col], chart_df[col], marker="o", linewidth=1.7, markersize=3.5, label=col)

    if spec.get("wind_lines", True) and x_col == "v (m/s)":
        for x_val, color, label in [
            (globals().get("v_cut_in", np.nan), "#64748b", "cut-in"),
            (globals().get("v_rated", np.nan), "#d9a766", "rated"),
            (globals().get("v_cut_out", np.nan), "#d95f5f", "cut-out"),
        ]:
            if np.isfinite(x_val):
                ax.axvline(float(x_val), linestyle="--", linewidth=1.0, color=color, alpha=0.75)
                ax.text(float(x_val), 0.98, label, transform=ax.get_xaxis_transform(), rotation=90, va="top", ha="right", fontsize=7, color=color)

    ax.set_title(spec["title"], fontsize=11, fontweight="bold")
    ax.set_xlabel(x_col)
    ax.set_ylabel(spec.get("y_label", "valor"))
    ax.grid(True, alpha=0.25)
    ax.legend(loc="best", fontsize=7)
    fig.tight_layout()

    img_buffer = io.BytesIO()
    fig.savefig(img_buffer, format="png", bbox_inches="tight")
    plt.close(fig)
    return img_buffer.getvalue()


def build_section_pdf(section_title: str, section_rows=None, extra_sheets=None, figures=None) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=1.1 * cm, leftMargin=1.1 * cm)
    styles = getSampleStyleSheet()
    story = [
        Paragraph(section_title, styles["Title"]),
        Spacer(1, 10),
        Paragraph("Exportación técnica de pestaña con contexto del panel principal y gráficos del modelo.", styles["BodyText"]),
        Spacer(1, 12),
    ]

    context_df = globals().get("download_context_df", pd.DataFrame())
    if isinstance(context_df, pd.DataFrame) and not context_df.empty:
        story.append(Paragraph("Parámetros de prueba del panel izquierdo", styles["Heading2"]))
        ctx = context_df[["Grupo", "Campo", "Valor"]].copy()
        ctx["Valor"] = ctx["Valor"].astype(str)
        table_data = [ctx.columns.tolist()] + ctx.values.tolist()
        table = Table(table_data, repeatRows=1)
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#334155")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 7),
            ("GRID", (0, 0), (-1, -1), 0.25, colors.lightgrey),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ]))
        story.append(table)
        story.append(Spacer(1, 12))

    section_df = _rows_df(section_rows)
    if not section_df.empty:
        story.append(Paragraph("Información de la pestaña", styles["Heading2"]))
        sec = section_df.head(35).copy()
        sec = sec.astype(str)
        table_data = [sec.columns.tolist()] + sec.values.tolist()
        table = Table(table_data, repeatRows=1)
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#475569")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 7),
            ("GRID", (0, 0), (-1, -1), 0.25, colors.lightgrey),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ]))
        story.append(table)
        story.append(PageBreak())

    chart_specs = default_pdf_chart_specs()
    for spec in chart_specs:
        story.append(Paragraph(str(spec["title"]), styles["Heading2"]))
        story.append(Spacer(1, 6))
        try:
            png_bytes = matplotlib_chart_png(spec)
            img = Image(io.BytesIO(png_bytes), width=480, height=280)
            story.append(img)
        except Exception as exc:
            story.append(Paragraph(
                f"No se pudo renderizar este gráfico en PDF. Detalle: {escape(str(exc))}",
                styles["BodyText"],
            ))
        story.append(PageBreak())

    for raw_name, raw_df in (extra_sheets or {}).items():
        sheet_df = _rows_df(raw_df)
        if sheet_df.empty:
            continue
        story.append(Paragraph(f"Datos anexos: {raw_name}", styles["Heading2"]))
        short_df = sheet_df.head(18).copy().astype(str)
        table_data = [short_df.columns.tolist()] + short_df.values.tolist()
        table = Table(table_data, repeatRows=1)
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#334155")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 6),
            ("GRID", (0, 0), (-1, -1), 0.25, colors.lightgrey),
        ]))
        story.append(table)
        story.append(PageBreak())

    doc.build(story)
    pdf_value = buffer.getvalue()
    buffer.close()
    return pdf_value


def design_assumption_rows():
    return [
        {"Campo": "Geometría", "Valor": f"D {D:.1f} m · H {H:.1f} m · A {A:.1f} m²"},
        {"Campo": "Rotor", "Valor": f"N {int(N)} · c {c:.2f} m · σ_int {sig_int:.2f} · σ_conv {sig_conv:.2f}"},
        {"Campo": "Control", "Valor": f"{control_mode} · TSR ref {tsr_ref:.2f} · rpm nominal {rpm_rotor_rated:.1f}"},
        {"Campo": "Transmisión", "Valor": f"G {G:.2f} · η_mec {eta_mec:.3f} · η_elec {eta_elec:.3f}"},
        {"Campo": "Perfil", "Valor": f"{airfoil_name} · {tipo_perfil} · e/c {t_rel:.1f}%"},
        {"Campo": "Viento", "Valor": f"cut-in {v_cut_in:.1f} · rated {v_rated:.1f} · cut-out {v_cut_out:.1f} m/s"},
        {"Campo": "Generador", "Valor": GEN["label"] if "GEN" in globals() else ""},
    ]


def kpi_export_frames():
    return {
        "KPIs rotor aero": pd.DataFrame([
            {"KPI": "Área barrida A = D·H", "Valor": A, "Unidad": "m²"},
            {"KPI": "Solidez σ_int", "Valor": sig_int, "Unidad": "-"},
            {"KPI": "Solidez σ_conv", "Valor": sig_conv, "Unidad": "-"},
            {"KPI": "TSR referencia", "Valor": tsr_ref, "Unidad": "-"},
            {"KPI": "λ_opt estimado", "Valor": cp_params["lam_opt"], "Unidad": "-"},
            {"KPI": "Cp_max estimado", "Valor": cp_params["cmax"], "Unidad": "-"},
            {"KPI": "U_tip @ v_max", "Valor": U_tip[-1], "Unidad": "m/s"},
            {"KPI": "λ_efectiva @ v_rated", "Valor": np.interp(v_rated, v_grid, lambda_eff), "Unidad": "-"},
            {"KPI": "Cp_el_equiv @ v_rated", "Valor": np.interp(v_rated, v_grid, Cp_el), "Unidad": "-"},
        ]),
        "KPIs tren potencia": pd.DataFrame([
            {"KPI": "Relación G", "Valor": G, "Unidad": "-"},
            {"KPI": "Polos totales", "Valor": poles_total, "Unidad": "-"},
            {"KPI": "T_rated", "Valor": T_rated, "Unidad": "N·m"},
            {"KPI": "k_MPPT", "Valor": k_mppt, "Unidad": "N·m·s²"},
            {"KPI": "η_mec", "Valor": eta_mec, "Unidad": "-"},
            {"KPI": "η_elec", "Valor": eta_elec, "Unidad": "-"},
            {"KPI": "rpm rotor nominal", "Valor": rpm_rotor_rated, "Unidad": "rpm"},
            {"KPI": "rpm generador nominal", "Valor": rpm_gen_rated, "Unidad": "rpm"},
        ]),
        "KPIs pala cargas": pd.DataFrame([
            {"KPI": "Perfil aerodinámico", "Valor": airfoil_name, "Unidad": ""},
            {"KPI": "Tipo de perfil", "Valor": tipo_perfil, "Unidad": ""},
            {"KPI": "Espesor relativo", "Valor": t_rel, "Unidad": "%"},
            {"KPI": "Masa total palas", "Valor": mass_total_blades, "Unidad": "kg"},
            {"KPI": "Inercia palas", "Valor": I_blades, "Unidad": "kg·m²"},
            {"KPI": "F centrípeta por pala", "Valor": F_centripetal_per_blade / 1000.0, "Unidad": "kN"},
            {"KPI": "a centrípeta nominal", "Valor": g_per_blade_rated, "Unidad": "g"},
            {"KPI": "Re @ 8 m/s", "Valor": Re_8, "Unidad": "-"},
            {"KPI": "Re @ v_max", "Valor": Re_max, "Unidad": "-"},
            {"KPI": "M_base nominal", "Valor": M_root_rated / 1000.0, "Unidad": "kN·m"},
            {"KPI": "M_por_strut nominal", "Valor": M_strut_rated / 1000.0, "Unidad": "kN·m/strut"},
        ]),
    }


def global_export_index_rows():
    subblocks = [
        ("Mapa técnico", "Aerodinámica", "Polar Lift-Drag del perfil seleccionado"),
        ("Mapa técnico", "Aerodinámica", "Ciclo de ángulo de ataque alpha(theta)"),
        ("Mapa técnico", "Control", "rpm rotor / rpm generador"),
        ("Mapa técnico", "Control", "lambda efectiva, U_tip y frecuencia eléctrica"),
        ("Mapa técnico", "Control", "Curva Cp(lambda)"),
        ("Mapa técnico", "Potencia", "Curva de potencia por etapa"),
        ("Mapa técnico", "Potencia", "Cp equivalente por etapa"),
        ("Mapa técnico", "Potencia", "Pérdidas por etapa"),
        ("Mapa técnico", "Mecánico", "Momentos y cargas en pala/struts"),
        ("Mapa técnico", "Mecánico", "Par en rotor/generador"),
        ("Mapa técnico", "Mecánico", "Frecuencias 1P/3P"),
        ("Mapa técnico", "Eléctrico", "Curvas eléctricas y corriente"),
        ("Mapa técnico", "Eléctrico", "Sistema eléctrico y vibraciones"),
        ("Mapa técnico", "Recurso", "Distribución Weibull y AEP"),
        ("Mapa técnico", "Recurso", "Ruido estimado"),
    ]
    rows = [
        {"Tipo": "Pestaña", "Bloque": "Panel principal", "Contenido": "Contexto global del diseño"},
        {"Tipo": "Pestaña", "Bloque": "Supuestos", "Contenido": "Supuestos y parámetros de diseño"},
        {"Tipo": "Pestaña", "Bloque": "KPIs", "Contenido": "Rotor, tren de potencia, pala y cargas"},
        {"Tipo": "Pestaña", "Bloque": "Resultados", "Contenido": "Resultados operativos por velocidad de viento"},
        {"Tipo": "Pestaña", "Bloque": "Riesgos", "Contenido": "Alertas y márgenes IEC"},
        {"Tipo": "Pestaña", "Bloque": "Escenarios", "Contenido": "Escenarios y comparación"},
    ]
    rows.extend({"Tipo": tipo, "Bloque": bloque, "Contenido": contenido} for tipo, bloque, contenido in subblocks)
    return rows


def build_global_export_sheets():
    theta_deg_export = np.linspace(0, 360, 361)
    theta_rad_export = np.deg2rad(theta_deg_export)
    lam_used_export = max(float(tsr_ref), 0.1)
    alpha_base_export = np.rad2deg(np.arctan2(np.sin(theta_rad_export), lam_used_export + np.cos(theta_rad_export))) + float(pitch_deg)
    sheets = {
        "Parametros panel": globals().get("download_context_df", pd.DataFrame()).copy(),
        "Indice": pd.DataFrame(global_export_index_rows()),
        "Supuestos": pd.DataFrame(design_assumption_rows()),
        "Polar Lift Drag": build_lift_drag_polar(t_rel=t_rel, symmetric=is_symmetric),
        "Curva Cp lambda": cp_curve_for_plot(cp_params),
        "Alpha theta": pd.DataFrame({"theta_deg": theta_deg_export, "alpha_deg": alpha_base_export}),
        "Resultados completos": df.copy(),
    }
    sheets.update(kpi_export_frames())
    for block_key, block_label in [
        ("aero", "Mapa aero"),
        ("control", "Mapa control"),
        ("power", "Mapa potencia"),
        ("mechanical", "Mapa mecanico"),
        ("electrical", "Mapa electrico"),
        ("resource", "Mapa recurso"),
    ]:
        for sheet_name, sheet_df in analysis_block_export_sheets(block_key).items():
            sheets[f"{block_label} {sheet_name}"] = sheet_df

    alert_rows = []
    for name, value, limit in [
        ("T_gen (N·m)", globals().get("max_T_gen", np.nan), globals().get("T_gen_max", np.nan)),
        ("T_rotor (N·m)", globals().get("max_T_rotor", np.nan), globals().get("T_rotor_max_iec", np.nan)),
        ("I_est (A)", globals().get("max_I_est", np.nan), globals().get("GDG_RATED_I", np.nan)),
        ("P_out (kW)", globals().get("max_P_out", np.nan), globals().get("P_nom_kW", np.nan)),
        ("M_base (kN·m)", globals().get("max_M_base", np.nan), globals().get("M_base_max_iec", np.nan)),
    ]:
        usage = value / limit * 100 if np.isfinite(value) and np.isfinite(limit) and limit > 0 else np.nan
        alert_rows.append({"Indicador": name, "Máximo": value, "Límite": limit, "Uso_%": usage, "Margen_%": 100 - usage if np.isfinite(usage) else np.nan})
    sheets["Riesgos alertas"] = pd.DataFrame(alert_rows)

    escenarios = st.session_state.get("escenarios", [])
    if escenarios:
        sheets["Escenarios"] = pd.DataFrame(escenarios)
    return sheets


def build_global_html_report() -> bytes:
    context_html = download_context_df.to_html(index=False, classes="data-table", border=0) if "download_context_df" in globals() else ""
    index_html = pd.DataFrame(global_export_index_rows()).to_html(index=False, classes="data-table", border=0)
    figs_html = []
    for title, fig in default_pdf_figures():
        figs_html.append(f"<section><h2>{escape(title)}</h2>{fig.to_html(full_html=False, include_plotlyjs='cdn')}</section>")
    html = f"""
<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <title>Reporte completo VAWT</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; margin: 28px; color: #182235; background: #f8fafc; }}
    h1 {{ margin-bottom: 4px; }}
    h2 {{ border-left: 6px solid #3d5a80; padding-left: 10px; margin-top: 28px; }}
    .panel {{ background: white; border: 1px solid #cbd5e1; border-radius: 10px; padding: 16px; margin: 16px 0; box-shadow: 0 10px 24px rgba(15,23,42,.08); }}
    .data-table {{ border-collapse: collapse; width: 100%; background: white; font-size: 13px; }}
    .data-table th {{ background: #334155; color: white; text-align: left; padding: 8px; }}
    .data-table td {{ border-bottom: 1px solid #e2e8f0; padding: 7px 8px; vertical-align: top; }}
  </style>
</head>
<body>
  <h1>Reporte completo VAWT</h1>
  <p>Exportación integral del panel principal, pestañas, sub-bloques y gráficos interactivos.</p>
  <div class="panel"><h2>Parámetros de prueba del panel izquierdo</h2>{context_html}</div>
  <div class="panel"><h2>Índice exportado</h2>{index_html}</div>
  {''.join(figs_html)}
</body>
</html>
"""
    return html.encode("utf-8")


def render_section_download_button(
    label: str,
    section_title: str,
    section_rows=None,
    key_suffix: str = "",
    extra_sheets=None,
    help_text: str | None = None,
    pdf_figures=None,
):
    safe_key = _download_slug(key_suffix or section_title, 90)
    st.download_button(
        label=f"📥 {label}",
        data=build_section_workbook(section_title, section_rows, extra_sheets),
        file_name=f"{_download_slug(section_title)}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        key=f"download_{safe_key}",
        help=help_text,
        use_container_width=True,
    )
    if st.button(
        f"📄 Generar PDF – {section_title}",
        key=f"make_pdf_{safe_key}",
        use_container_width=True,
        help="Genera un PDF con contexto, tablas resumidas y gráficos técnicos del modelo.",
    ):
        pdf_bytes = build_section_pdf(section_title, section_rows, extra_sheets, pdf_figures)
        st.download_button(
            label=f"📥 Descargar PDF – {section_title}",
            data=pdf_bytes,
            file_name=f"{_download_slug(section_title)}.pdf",
            mime="application/pdf",
            key=f"download_pdf_{safe_key}",
            use_container_width=True,
        )


def analysis_block_export_sheets(block_key):
    df_src = globals().get("df", pd.DataFrame())
    if not isinstance(df_src, pd.DataFrame) or df_src.empty:
        return {}

    column_groups = {
        "aero": [
            "v (m/s)", "λ_efectiva", "U_tip (m/s)", "Re (mid-span)",
            "Cp(λ_efectiva)", "Cp_aero_equiv", "P_aero (kW)",
        ],
        "control": [
            "v (m/s)", "rpm_rotor", "rpm_gen", "λ_efectiva",
            "T_rotor (N·m)", "T_gen (N·m)", "P_out (clip) kW",
        ],
        "power": [
            "v (m/s)", "P_aero (kW)", "P_mec_gen (kW)", "P_gen_curve (kW)",
            "P_el (kW)", "P_out (clip) kW", "Cp_el_equiv",
            "P_loss_mec (kW)", "P_loss_gen (kW)", "P_loss_elec (kW)", "P_loss_clip (kW)",
        ],
        "mechanical": [
            "v (m/s)", "T_rotor (N·m)", "T_gen (N·m)", "F_cen/pala (kN)",
            "a_cen (g)", "M_base (kN·m)", "M_por_strut (kN·m)",
            "sigma_root (MPa)", "sigma_strut (MPa)", "margen_root (%)", "margen_strut (%)",
            "f_1P (Hz)", "f_3P (Hz)",
        ],
        "electrical": [
            "v (m/s)", "rpm_gen", "P_gen_curve (kW)", "V_LL (V)", "V_LL (Ke) [V]",
            "f_e (Hz)", "η_gen (curve)", "T_gen (N·m)", "P_el (kW)",
            "P_out (clip) kW", "I_est (A)", "Duty_DC (%)",
        ],
        "resource": [
            "v (m/s)", "P_out (clip) kW", "Cp_el_equiv", "Lw (dB)", "Lp_obs (dB)",
        ],
    }
    cols = [c for c in column_groups.get(block_key, list(df_src.columns)) if c in df_src.columns]
    sheets = {"Datos del bloque": df_src[cols].copy() if cols else df_src.copy()}
    if "df_alerts_top" in globals():
        sheets["Alertas principales"] = globals()["df_alerts_top"]
    return sheets


# =========================================================
# Curvas de generadores axiales (80 kW y 10 kW)
# =========================================================

# --- GDG-1100 – 80 kW (lo que ya tenías) ---
GDG_POWER_TABLE_80 = pd.DataFrame(
    [
        (0, 0),
        (24, 2),
        (48, 3),
        (72, 7),
        (96, 12),
        (120, 19),
        (144, 28),
        (168, 38),
        (192, 50),
        (216, 64),
        (240, 80),
        (264, 97),
    ],
    columns=["rpm", "P_kW"],
)

GDG_VOLT_TABLE_80 = pd.DataFrame(
    [
        (0, 0),
        (24, 40),
        (48, 80),
        (72, 120),
        (96, 160),
        (120, 200),
        (144, 240),
        (168, 280),
        (192, 320),
        (216, 360),
        (240, 400),
        (264, 440),
    ],
    columns=["rpm", "V_LL"],
)

GDG_RATED_RPM_80   = 240.0
GDG_RATED_PkW_80   = 80.0
GDG_RATED_VLL_80   = 400.0
GDG_RATED_I_80     = 115.0
GDG_RATED_T_Nm_80  = 3460.0
GDG_POLES_80       = 48
GDG_OMEGA_RATED_80 = 2 * pi * GDG_RATED_RPM_80 / 60.0
GDG_KE_DEFAULT_80  = GDG_RATED_VLL_80 / GDG_OMEGA_RATED_80
GDG_KT_DEFAULT_80  = GDG_RATED_T_Nm_80 / GDG_RATED_I_80

# --- GDG-860 – 10 kW (desde la ficha adjunta) ---
GDG_POWER_TABLE_10 = pd.DataFrame(
    [
        (0, 0),
        (7, 0.2),
        (14, 0.4),
        (21, 0.9),
        (28, 1.5),
        (35, 2.4),
        (42, 3.5),
        (49, 4.7),
        (56, 6.2),
        (63, 8.0),
        (70, 10.0),
        (77, 12.1),
    ],
    columns=["rpm", "P_kW"],
)

GDG_VOLT_TABLE_10 = pd.DataFrame(
    [
        (0, 0),
        (7, 40),
        (14, 80),
        (21, 120),
        (28, 160),
        (35, 200),
        (42, 240),
        (49, 280),
        (56, 320),
        (63, 360),
        (70, 400),
        (77, 440),
    ],
    columns=["rpm", "V_LL"],
)

GDG_RATED_RPM_10   = 70.0
GDG_RATED_PkW_10   = 10.0
GDG_RATED_VLL_10   = 400.0
GDG_RATED_I_10     = 14.0
GDG_RATED_T_Nm_10  = 1483.0     # según ficha GDG-860
GDG_POLES_10       = 20
GDG_OMEGA_RATED_10 = 2 * pi * GDG_RATED_RPM_10 / 60.0
GDG_KE_DEFAULT_10  = GDG_RATED_VLL_10 / GDG_OMEGA_RATED_10
GDG_KT_DEFAULT_10  = GDG_RATED_T_Nm_10 / GDG_RATED_I_10

# --- Catálogo común de generadores para la UI ---
GENERATORS = {
    "GDG_80k": {
        "label": "GDG-1100 – 80 kW",
        "P_nom_kW": GDG_RATED_PkW_80,
        "rpm_nom": GDG_RATED_RPM_80,
        "V_LL_nom": GDG_RATED_VLL_80,
        "I_nom": GDG_RATED_I_80,
        "T_nom": GDG_RATED_T_Nm_80,
        "poles": GDG_POLES_80,
        "Ke_default": GDG_KE_DEFAULT_80,
        "Kt_default": GDG_KT_DEFAULT_80,
        "power_table": GDG_POWER_TABLE_80,
        "volt_table": GDG_VOLT_TABLE_80,
    },
    "GDG_10k": {
        "label": "GDG-860 – 10 kW",
        "P_nom_kW": GDG_RATED_PkW_10,
        "rpm_nom": GDG_RATED_RPM_10,
        "V_LL_nom": GDG_RATED_VLL_10,
        "I_nom": GDG_RATED_I_10,
        "T_nom": GDG_RATED_T_Nm_10,
        "poles": GDG_POLES_10,
        "Ke_default": GDG_KE_DEFAULT_10,
        "Kt_default": GDG_KT_DEFAULT_10,
        "power_table": GDG_POWER_TABLE_10,
        "volt_table": GDG_VOLT_TABLE_10,
    },
}


def interp_curve(x, x_tab, y_tab):
    """
    Interpolación lineal sencilla con extrapolación plana
    (mantiene el primer y último valor fuera de rango).
    """
    x = np.asarray(x)
    return np.interp(x, x_tab, y_tab, left=y_tab[0], right=y_tab[-1])



# =========================================================
# UI – Entradas
# =========================================================
render_hero_banner()

# =========================================================
# Catálogo de perfiles aerodinámicos (NACA + típicos eólicos)
# =========================================================

AIRFOIL_LIBRARY = {
    # ---- SIMÉTRICOS (buenos para Darrieus / VAWT) ----
    "NACA 0012": {
        "t_rel": 12.0,
        "symmetric": True,
        "descripcion": "Perfil simétrico clásico, drag bajo y uso extendido en turbinas de eje horizontal."
    },
    "NACA 0015": {
        "t_rel": 15.0,
        "symmetric": True,
        "descripcion": "Simétrico, compromiso entre arrastre y rigidez. Muy usado en prototipos VAWT."
    },
    "NACA 0018": {
        "t_rel": 18.0,
        "symmetric": True,
        "descripcion": "Más grueso, mayor rigidez estructural, buen comportamiento en Re moderados."
    },
    "NACA 0021": {
        "t_rel": 21.0,
        "symmetric": True,
        "descripcion": "Perfil robusto; buena opción para palas con mayores cargas y fabricación FRP."
    },
    "NACA 0024": {
        "t_rel": 24.0,
        "symmetric": True,
        "descripcion": "Muy grueso, prioriza rigidez y fatiga sobre rendimiento aerodinámico máximo."
    },

    # ---- CAMBERADOS (más lift, más sensibilidad a ángulo) ----
    "NACA 2412": {
        "t_rel": 12.0,
        "symmetric": False,
        "descripcion": "Camber moderado, usado históricamente en alas; mayor Cl/Cd pero más sensible a pitch."
    },
    "NACA 4412": {
        "t_rel": 12.0,
        "symmetric": False,
        "descripcion": "Muy utilizado en eólica HAWT; buen rendimiento en Cl, mayor complejidad en control."
    },
    "NACA 4415": {
        "t_rel": 15.0,
        "symmetric": False,
        "descripcion": "Similar al 4412 pero más grueso; buena combinación de aerodinámica y rigidez."
    },
    "NACA 4418": {
        "t_rel": 18.0,
        "symmetric": False,
        "descripcion": "Perfil con camber y espesor altos; pensado para cargas importantes y alta sustentación."
    },

    # ---- Ejemplo “VAWT-friendly” genérico ----
    "NACA 0022 (VAWT FRP)": {
        "t_rel": 22.0,
        "symmetric": True,
        "descripcion": "Perfil grueso y simétrico como el que estás usando en el piloto; robusto y tolerante a stall dinámico."
    },
}


with st.sidebar:
    st.markdown(
        f"""
        <div class="section-header" style="
            margin: 0 0 0.9rem;
            font-size: 1.05rem;
            padding: 0.75rem 0.9rem;
            border-left: 6px solid {PALETTE_CORAL};
            border-color: rgba(217,95,95,0.28);
            background: linear-gradient(90deg, rgba(217,95,95,0.16), rgba(217,167,102,0.10), rgba(255,255,255,0.92));
            color: {PALETTE_SLATE};
        ">
            Variables a editar
        </div>
        """,
        unsafe_allow_html=True,
    )

    sidebar_section("1️⃣ Geometría y pala")
    # Geometría
    with st.expander("Geometría", expanded=False):
        D = st.number_input("Diámetro D [m]",  min_value=2.0, value=11.0, step=0.5)
        H = st.number_input("Altura H [m]",    min_value=2.0, value=18.0, step=0.5)
        N = st.number_input("Nº de palas N",   min_value=2,   value=3, step=1)
        c = st.number_input("Cuerda c [m]",    min_value=0.1, value=0.80, step=0.05)
    
    # Perfil de pala / masa
    with st.expander("Perfil de pala / masa", expanded=False):
        # === Modo de selección de perfil ===
        modo_perfil = st.radio(
            "Modo de selección de perfil",
            ["Catálogo NACA", "Personalizado"],
            horizontal=True
        )

        if modo_perfil == "Catálogo NACA":
            # Ordenamos para que quede bonito en el selector
            airfoil_keys = sorted(AIRFOIL_LIBRARY.keys())

            airfoil_name = st.selectbox(
                "Perfil NACA",
                airfoil_keys,
                index=airfoil_keys.index("NACA 0022 (VAWT FRP)") if "NACA 0022 (VAWT FRP)" in airfoil_keys else 0,
            )

            af_data = AIRFOIL_LIBRARY[airfoil_name]
            t_rel = af_data["t_rel"]
            is_symmetric = af_data["symmetric"]
            tipo_perfil = "Simétrico" if is_symmetric else "Asimétrico"

            st.caption(
                f"e/c ≈ {t_rel:.0f} % – {af_data['descripcion']}"
            )

            # Permitimos ajustar finamente el pitch aunque el perfil venga predefinido
            pitch_deg = st.slider(
                "Ángulo de calaje (pitch) [°]",
                min_value=-10.0, max_value=10.0,
                value=0.0,
                step=0.25,
                help="Controla el pitch del perfil seleccionado y refresca α(θ) en tiempo real."
            )

        else:
            # === Modo completamente personalizado ===
            airfoil_name = st.text_input("Perfil (ej: NACA 0018)", "NACA 0022")
            tipo_perfil  = st.selectbox("Tipo de perfil", ["Simétrico", "Asimétrico"])
            is_symmetric = (tipo_perfil == "Simétrico")

            t_rel = st.number_input(
                "Espesor relativo e/c [%]",
                min_value=8.0,
                max_value=40.0,
                value=22.0,
                step=1.0
            )

            pitch_deg = st.slider(
                "Ángulo de calaje (pitch) [°]",
                min_value=-10.0, max_value=10.0,
                value=0.0,
                step=0.25,
                help="Controla el pitch del perfil seleccionado y refresca α(θ) en tiempo real."
            )

        # ---- Parámetros de masa / geometría helicoidal (comunes a ambos modos) ----
        st.markdown("**Tweaks aerodinámicos / masa**")
        helical     = st.checkbox("Helicoidal 60–90°", True, help="Activa la pala helicoidal y aplica su ángulo en Cp(λ).")
        endplates   = st.checkbox("End-plates / winglets", False)
        trips       = st.checkbox("Trips / micro-tabs", False)
        struts_perf = st.checkbox("Struts perfilados (0012)", False)
        m_blade = st.number_input(
            "Masa por pala [kg]",
            min_value=10.0,
            value=180.0,
            step=10.0
        )

        helix_angle_deg = st.number_input(
            "Ángulo helicoidal pala [°]",
            min_value=0.0, max_value=90.0,
            value=60.0,
            step=5.0
        )

        helix_rad = np.deg2rad(helix_angle_deg)
        blade_span = H / max(np.cos(helix_rad), 1e-3)
        st.caption(f"Longitud de pala estimada ≈ {blade_span:.1f} m (helix {helix_angle_deg:.0f}°)")

        struts_per_blade = st.number_input(
            "N° de struts por pala",
            min_value=1,
            value=3,
            step=1,
            help="Cantidad de vigas/brazos que conectan cada pala con la torre; se usa para repartir el momento flector."
        )

        # Configuración detallada por strut
        default_distances = np.array([13.0, 11.0, 13.0], dtype=float)
        default_weights = np.full(int(struts_per_blade), 1.0 / max(struts_per_blade, 1))

        if "strut_dist_input" not in st.session_state or st.session_state.get("strut_dist_count") != int(struts_per_blade):
            st.session_state["strut_dist_input"] = ", ".join(f"{d:.1f}" for d in default_distances)
            st.session_state["strut_dist_count"] = int(struts_per_blade)

        if "strut_weight_input" not in st.session_state or st.session_state.get("strut_weight_count") != int(struts_per_blade):
            st.session_state["strut_weight_input"] = ", ".join(f"{w:.2f}" for w in default_weights)
            st.session_state["strut_weight_count"] = int(struts_per_blade)

        strut_dist_input = st.text_input(
            "Distancias de struts [m] (separadas por coma)",
            key="strut_dist_input",
            help="Ejemplo: 17, 9, 2  → representa las distancias desde el eje a cada viga."
        )
        strut_weight_input = st.text_input(
            "Ponderación relativa por strut",
            key="strut_weight_input",
            help="Normaliza cómo reparte el momento cada viga (por defecto iguales)."
        )

        strut_distances = parse_float_list(strut_dist_input)
        if not strut_distances:
            strut_distances = default_distances.tolist()
        if len(strut_distances) < int(struts_per_blade):
            strut_distances.extend([strut_distances[-1]] * (int(struts_per_blade) - len(strut_distances)))
        elif len(strut_distances) > int(struts_per_blade):
            strut_distances = strut_distances[: int(struts_per_blade)]

        strut_weights = parse_float_list(strut_weight_input)
        if len(strut_weights) != len(strut_distances) or not strut_weights:
            strut_weights = [1.0] * len(strut_distances)

        total_weight = sum(strut_weights)
        if total_weight <= 0:
            total_weight = len(strut_weights)
            strut_weights = [1.0] * len(strut_distances)
        lever_arm_pala = float(np.dot(strut_distances, strut_weights) / total_weight)
        weights_norm = [w / total_weight for w in strut_weights]

        df_struts = pd.DataFrame({
            "Strut #": list(range(1, len(strut_distances) + 1)),
            "Distancia [m]": np.round(strut_distances, 2),
            "Peso relativo": np.round(weights_norm, 3),
        })
        st.dataframe(df_struts, hide_index=True, use_container_width=True)
        st.caption(
            f"Brazo efectivo calculado ≈ {lever_arm_pala:.2f} m (suma de ponderaciones = {sum(weights_norm):.2f})."
        )
        st.caption(
            "Tip: ingresa las alturas reales de unión (ej. 2, 9, 17 m para una pala de 18 m) y asigna pesos mayores a "
            "los struts que capturan más carga según tu FEM. Si todos comparten la misma palanca, deja distancias iguales "
            "y solo ajusta la ponderación."
        )

    with st.expander("Propiedades estructurales avanzadas", expanded=False):
        section_modulus_root = st.number_input(
            "Módulo resistente raíz W [m³]",
            min_value=0.001,
            value=0.075,
            step=0.005,
            help="Define la capacidad a flexión en la unión pala–struts. Valores mayores implican perfiles más robustos."
        )
        sigma_y_pala_mpa = st.number_input(
            "σ_y pala / raíz [MPa]",
            min_value=50.0,
            value=180.0,
            step=5.0,
            help="Límite de fluencia o admisible del laminado / unión en la raíz."
        )
        strut_area_cm2 = st.number_input(
            "Área efectiva strut [cm²]",
            min_value=5.0,
            value=40.0,
            step=1.0,
            help="Área metálica equivalente por strut para estimar esfuerzos axiales."
        )
        sigma_allow_strut_mpa = st.number_input(
            "σ admisible strut [MPa]",
            min_value=50.0,
            value=250.0,
            step=5.0,
            help="Tensión axial permitida en los struts (considera material + soldaduras)."
        )
        safety_target = st.number_input(
            "Factor de seguridad objetivo",
            min_value=1.0,
            value=1.5,
            step=0.1,
            help="Usado como referencia para sombrear los gráficos de stress."
        )
        show_guides = st.checkbox("Mostrar guías y rangos sugeridos", value=False)
        if show_guides:
            st.markdown("""
**Raíz FRP / aluminio (pilotos 10–60 kW)**
- Módulo resistente W: 0.04–0.10 m³ según espesor del laminado.
- σ_y pala: 120–200 MPa (laminados infundidos + insertos metálicos).

**Struts tubulares de acero ASTM A500**
- Área efectiva típica: 30–60 cm² (tubos 120–180 mm, t=5–8 mm).
- σ admisible: 200–260 MPa (fluencia 345 MPa con FS≈1.5).

**Struts de aluminio 6061-T6**
- Área efectiva: 45–80 cm² (perfiles más gruesos para compensar módulo).
- σ admisible: 140–180 MPa (fluencia 240 MPa / FS 1.3–1.5).

**Recomendaciones**
- FS objetivo ≥1.3 para operación normal, ≥1.7 si el sitio tiene ráfagas severas.
- Si no tienes FEM, arranca por W ≈ (π·c·t³)/6 para el bloque de raíz y ajusta con datos de pruebas.
""")

    sidebar_section("2️⃣ Operación y entorno")
    # Precalcular λ_opt estimado con la configuración actual
    R_preview = D / 2.0
    sig_int_preview = solidity_int(N, c, R_preview)
    lam_ctrl_default = 2.5
    cp_preview = None
    try:
        cp_preview = build_cp_params(
            lam_opt_base=2.6,
            cmax_base=0.33,
            shape=1.0,
            sigma=sig_int_preview,
            helical=helical,
            helix_angle_deg=helix_angle_deg,
            endplates=endplates,
            trips=trips,
            struts_perf=struts_perf,
            airfoil_thickness=t_rel,
            symmetric=is_symmetric,
            pitch_deg=pitch_deg,
        )
        lam_ctrl_default = float(cp_preview.get("lam_opt", lam_ctrl_default))
    except Exception:
        pass

    # Operación / control
    with st.expander("Operación / Control", expanded=False):
        rpm_v_exp = 0.85

        control_mode = st.radio(
            "Modo de control",
            options=["MPPT (λ constante)", "RPM fija (sin MPPT)"],
            index=0,
            help="MPPT mantiene λ≈constante en Región 2; sin MPPT usa rpm fija entre cut-in y cut-out.",
        )

        if control_mode == "MPPT (λ constante)":
            lam_opt_ctrl = st.number_input(
                "TSR objetivo λ (control)",
                min_value=1.5,
                max_value=5.0,
                value=lam_ctrl_default,
                step=0.01,
                help="Setpoint MPPT utilizado para la ley rpm–v en Región 2. Por defecto igual al λ_opt estimado."
            )
            tsr_ctrl = lam_opt_ctrl
        else:
            lam_opt_ctrl = lam_ctrl_default
            tsr_ctrl = None
            rpm_v_exp = st.slider(
                "Exponente rpm vs viento (sin MPPT)",
                min_value=0.50,
                max_value=1.50,
                value=0.85,
                step=0.05,
                help="rpm_gen ∝ (v/v_rated)^a. a=1 mantiene TSR casi constante; a≠1 hace variar TSR y Cp."
            )
            st.caption(
                "Modo sin MPPT: la TSR y el Cp resultan de la velocidad del viento y la rpm fijada, "
                "no de un setpoint constante."
            )

        rho = st.number_input("Densidad aire ρ [kg/m³]", min_value=1.0, value=1.225, step=0.025)
        mu  = st.number_input(
            "Viscosidad dinámica μ [Pa·s]",
            min_value=1.0e-5, max_value=3.0e-5,
            value=1.8e-5, step=0.1e-5, format="%.6f"
        )
        v_cut_in  = st.number_input("v_cut-in [m/s]",  min_value=0.5, value=3.0, step=0.5)
        v_rated   = st.number_input("v_rated [m/s]",   min_value=v_cut_in + 0.5, value=12.0, step=0.5)
        v_cut_out = st.number_input("v_cut-out [m/s]", min_value=v_rated + 0.5, value=20.0, step=0.5)

    # Rango de vientos
    with st.expander("Rango de vientos / Muestreo", expanded=False):
        v_min  = st.number_input("v mín [m/s]", min_value=0.5, value=4.0, step=0.5)
        v_max  = st.number_input("v máx [m/s]", min_value=v_min+0.5, value=20.0, step=0.5)

    # Ruido aeroacústico
    with st.expander("Ruido aeroacústico (dB)", expanded=False):
        use_noise = st.checkbox("Estimar ruido (Lw / Lp)", True)
        Lw_ref_dB = st.number_input(
            "Lw_ref @ v_rated [dB]",
            min_value=0.0, max_value=150.0,
            value=100.0, step=1.0,
            help="Nivel de potencia sonora de referencia a v_rated"
        )
        r_obs = st.number_input(
            "Distancia observador [m]",
            min_value=1.0, max_value=1000.0,
            value=50.0, step=5.0
        )
        n_noise = st.number_input(
            "Exponente n (U_tip^n)",
            min_value=1.0, max_value=8.0,
            value=5.0, step=0.5,
            help="Sensibilidad del ruido a la velocidad de punta"
        )

    sidebar_section("3️⃣ Tren de potencia y electrónica")
    # --- Tren de potencia / Generador ---
    with st.expander("Tren de potencia / Generador", expanded=False):

        # Modelo fijo para licitación Entel: turbina VAWT 10 kW.
        gen_key = "GDG_10k"
        GEN = GENERATORS[gen_key]

        # --- Alias globales para compatibilidad con el resto del código ---
        GDG_RATED_T_Nm = GEN["T_nom"]
        GDG_RATED_I    = GEN["I_nom"]
        GDG_RATED_RPM  = GEN["rpm_nom"]

        st.markdown(
            f"""
**Generador seleccionado**

- Modelo: `{GEN['label']}`
- P_nom: **{GEN['P_nom_kW']:.1f} kW**
- rpm_nom: **{GEN['rpm_nom']:.0f} rpm**
- V_LL_nom: **{GEN['V_LL_nom']:.0f} Vac**
- I_nom: **{GEN['I_nom']:.1f} A**
- T_nom: **{GEN['T_nom']:.0f} N·m**
- Nº de polos: **{GEN['poles']}**
"""
        )

        # rpm sugerida por aerodinámica (referencia si no hay MPPT)
        tsr_sugerida = lam_opt_ctrl if control_mode == "MPPT (λ constante)" else lam_ctrl_default
        rpm_sugerida = float(rpm_from_tsr(v_rated, D, tsr_sugerida))
        st.caption(
            f"rpm rotor rated sugerida por diseño aerodinámico (TSR ref y v_rated): "
            f"≈ **{rpm_sugerida:.1f} rpm**"
        )

        usar_rpm_auto = st.checkbox(
            "Usar rpm sugerida (TSR y v_rated)",
            value=True,
            help="Si está activo, la rpm nominal del rotor se toma del diseño aerodinámico."
        )

        if usar_rpm_auto:
            rpm_rotor_rated = rpm_sugerida
            st.write(f"rpm_rotor_rated (auto) = **{rpm_rotor_rated:.1f} rpm**")
        else:
            rpm_rotor_rated = st.number_input(
                "rpm rotor rated",
                min_value=10.0,
                value=float(rpm_sugerida),
                step=1.0,
            )

        # Generador + relación G
        rpm_gen_rated = st.number_input(
            "rpm gen rated",
            min_value=10.0,
            value=float(GEN["rpm_nom"]),
            step=1.0,
        )

        auto_G = st.checkbox("Calcular G con rpm rated", True)
        if auto_G:
            G = rpm_gen_rated / max(rpm_rotor_rated, 1e-6)
            st.write(f"**G (calc)** = {G:.2f}")
        else:
            G = st.number_input(
                "Relación G = rpm_gen/rpm_rotor",
                min_value=1.0,
                value=6.0,
                step=0.05,
            )

        # Eficiencias mecánicas
        eta_bear = st.number_input("η rodamientos", min_value=0.90, value=0.98, step=0.005)
        eta_gear = st.number_input("η caja",       min_value=0.85, value=0.96, step=0.005)

        # Parámetros del generador
        poles_total    = st.number_input("N° de polos (total)", min_value=4, value=int(GEN["poles"]), step=2)
        eta_gen_max    = st.number_input("η_gen máx (tope)", min_value=0.80, value=0.93, step=0.005)
        Ke_vsr_default = st.number_input("Ke [V·s/rad]", min_value=1.0, value=float(GEN["Ke_default"]), step=0.1)
        Kt_nm_per_A    = st.number_input("Kt [N·m/A]", min_value=1.0, value=float(GEN["Kt_default"]), step=0.1)

        gen_csv = None
        st.caption("Curva de generador fija para la oferta de 10 kW; no se solicita carga manual de CSV.")

        eta_elec = st.number_input("η electrónica (rect+inv)", min_value=0.90, value=0.975, step=0.005)

        P_nom_kW  = st.number_input(
            "P_nom [kW]",
            min_value=1.0,
            value=float(GEN["P_nom_kW"]),
            step=1.0,
        )
        T_gen_max = st.number_input(
            "T_gen máx [N·m] (opcional)",
            min_value=0.0,
            value=float(GEN["T_nom"]),
            step=50.0,
        )

    with st.expander("Electrónica / red avanzada", expanded=False):
        pf_setpoint = st.slider(
            "PF operativo (cos φ)",
            min_value=0.80,
            max_value=1.00,
            value=0.95,
            step=0.01,
            help="Setpoint de control de factor de potencia que usará la electrónica."
        )
        pf_min_grid = st.slider(
            "PF mínimo exigido por red",
            min_value=0.80,
            max_value=1.00,
            value=0.90,
            step=0.01,
        )
        thd_cap_pct = st.number_input(
            "THD estimada (filtro LCL) [%]",
            min_value=1.0,
            value=3.0,
            step=0.5,
            help="Distorsión armónica total esperada en bornes de red tras filtros."
        )
        thd_req_pct = st.number_input(
            "THD límite normativa [%]",
            min_value=2.0,
            value=5.0,
            step=0.5,
        )
        lvrt_cap_voltage_pu = st.number_input(
            "LVRT tensión soportada [pu]",
            min_value=0.05,
            max_value=1.00,
            value=0.15,
            step=0.01,
            help="Profundidad de hueco (pu) que el inversor soporta sin dispararse."
        )
        lvrt_req_voltage_pu = st.number_input(
            "LVRT tensión requerida [pu]",
            min_value=0.05,
            max_value=1.00,
            value=0.20,
            step=0.01,
            help="Requisito del código de red (normalmente 0.2–0.3 pu)."
        )
        lvrt_cap_time_ms = st.number_input(
            "LVRT tiempo soportado [ms]",
            min_value=50.0,
            value=180.0,
            step=5.0,
        )
        lvrt_req_time_ms = st.number_input(
            "LVRT tiempo requerido [ms]",
            min_value=50.0,
            value=150.0,
            step=5.0,
        )
        I_inv_thermal_A = st.number_input(
            "Corriente térmica inversor [A]",
            min_value=50.0,
            value=140.0,
            step=1.0,
            help="Corriente RMS máxima continua que soporta el inversor."
        )
        V_dc_nom = st.number_input(
            "Tensión DC nominal [V]",
            min_value=400.0,
            value=750.0,
            step=10.0,
        )
        I_dc_nom = st.number_input(
            "Corriente DC nominal [A]",
            min_value=20.0,
            value=120.0,
            step=5.0,
        )

    sidebar_section("4️⃣ Normativa, recurso y datos")
    # --- IEC 61400-2 – límites de diseño ---
    with st.expander("Límites IEC 61400-2 (diseño)", expanded=False):
        rpm_rotor_max_iec = st.number_input(
            "rpm_rotor máx IEC",
            min_value=10.0,
            value=40.0,
            step=1.0,
            help="Límite estructural de rpm del rotor definido por IEC 61400-2 (fatiga, estabilidad)."
        )
        T_rotor_max_iec = st.number_input(
            "T_rotor máx IEC [N·m]",
            min_value=1000.0,
            value=20000.0,
            step=500.0,
            help="Torque máximo admisible en el eje rotor según diseño estructural IEC-61400-2."
        )
        v_shutdown_iec = st.number_input(
            "v_shutdown IEC [m/s]",
            min_value=v_rated,
            value=v_cut_out,
            step=0.5,
            help="Velocidad de viento a la cual el sistema debe ejecutar parada segura (shutdown)."
        )
        g_max_pala_iec = st.number_input(
            "Aceleración radial máx en pala [g]",
            min_value=5.0,
            value=25.0,
            step=1.0,
            help="Máximo n° de g admisible en la raíz de la pala según criterio estructural/FEM."
        )
        M_base_max_iec = st.number_input(
            "Momento flector máx en raíz [kN·m]",
            min_value=10.0,
            value=350.0,
            step=10.0,
            help="Límite estructural de momento flector en la raíz de la pala / base de torre."
        )

    # Weibull
    with st.expander("Weibull", expanded=False):
        k_w = st.number_input("k (forma)",  min_value=1.0, value=2.0, step=0.1)
        c_w = st.number_input("c (escala) [m/s]", min_value=2.0, value=7.5, step=0.5)

    # Datos piloto (SCADA) para calibración
    with st.expander("Datos piloto (SCADA)", expanded=False):
        default_scada_path = Path(__file__).resolve().parent / "assets" / "MG888.csv"
        if default_scada_path.exists():
            df_scada = read_uploaded_csv(default_scada_path.read_bytes())
            st.session_state["df_scada_raw"] = df_scada
            st.session_state["df_scada_filename"] = default_scada_path.name
            st.caption(f"Archivo SCADA cargado por defecto: {default_scada_path.name}")

            st.caption(f"Columnas detectadas: {', '.join(df_scada.columns.astype(str))}")

            cols = df_scada.columns.tolist()
            is_height_profile, height_cols, time_col = detect_wind_height_profile(df_scada)

            if is_height_profile:
                height_values = [_numeric_column_name(c) for c in height_cols]
                height_values = [float(v) for v in height_values if v is not None]
                auto_target_height = default_turbine_resource_height(P_nom_kW)
                target_height = st.number_input(
                    "Altura efectiva de extrapolación [m]",
                    min_value=1.0,
                    value=float(auto_target_height),
                    step=0.5,
                    help=(
                        "La app usa 14 m para la turbina de 10 kW y 24 m para la de 80 kW. "
                        "Con archivos de perfil vertical se calcula V(z)=a·z^alpha por timestamp."
                    ),
                )
                scada_resource_inputs = build_wind_profile_inputs(df_scada, height_cols, target_height, time_col)
                st.session_state["scada_resource_inputs"] = scada_resource_inputs
                st.session_state["scada_map"] = {
                    "mode": "wind_height_profile",
                    "v": f"{target_height:.1f} m extrapolado",
                    "P": None,
                    "rpm_rotor": None,
                    "rpm_gen": None,
                    "I": None,
                }

                if scada_resource_inputs:
                    c_sc1, c_sc2, c_sc3 = st.columns(3)
                    c_sc1.metric("Viento medio rotor [m/s]", f"{scada_resource_inputs['v_mean']:.2f}")
                    c_sc2.metric("Weibull k / c", f"{scada_resource_inputs['weibull_k']:.2f} / {scada_resource_inputs['weibull_c']:.2f}")
                    c_sc3.metric("Alpha vertical", f"{scada_resource_inputs['shear_alpha']:.3f}" if np.isfinite(scada_resource_inputs["shear_alpha"]) else "-")
                    if scada_resource_inputs.get("start") and scada_resource_inputs.get("end"):
                        st.caption(f"Periodo detectado: {scada_resource_inputs['start']} → {scada_resource_inputs['end']} · {scada_resource_inputs['sample_count']:,} registros válidos.")
                    else:
                        st.caption(f"{scada_resource_inputs['sample_count']:,} registros válidos para cálculo eólico.")
                    st.caption(
                        f"Método: {scada_resource_inputs.get('method', 'ley de potencia')} · "
                        f"alturas fuente {scada_resource_inputs.get('source_height_min_m', np.nan):.1f}-"
                        f"{scada_resource_inputs.get('source_height_max_m', np.nan):.1f} m · "
                        f"altura objetivo {scada_resource_inputs.get('target_height_m', np.nan):.1f} m."
                    )

                    profile_table = pd.DataFrame(scada_resource_inputs["profile_summary"])
                    st.dataframe(
                        profile_table.style.format(
                            {
                                "Altura m": "{:.1f}",
                                "Velocidad media m/s": "{:.2f}",
                                "P10 m/s": "{:.2f}",
                                "P50 m/s": "{:.2f}",
                                "P90 m/s": "{:.2f}",
                            }
                        ),
                        use_container_width=True,
                        hide_index=True,
                    )
                    st.caption(
                        "Este perfil vertical alimenta el bloque de Recurso y energía anual: "
                        "viento medio, Weibull k/c y altura efectiva para estimar producción."
                    )
                else:
                    st.warning("El CSV parece tener alturas, pero no se pudo construir un perfil eólico válido.")

            else:
                st.session_state["scada_resource_inputs"] = {}

                # Heurística simple para defaults
                def guess_col(substr, default_idx=0):
                    substr = substr.lower()
                    for i, c in enumerate(cols):
                        if substr in str(c).lower():
                            return i
                    return default_idx

                v_col = st.selectbox(
                    "Columna velocidad viento [m/s]",
                    cols,
                    index=guess_col("viento"),
                )
                P_col = st.selectbox(
                    "Columna potencia [kW]",
                    cols,
                    index=guess_col("pot"),
                )
                rpm_rotor_col = st.selectbox(
                    "Columna rpm rotor (opcional)",
                    ["(ninguna)"] + cols,
                    index=0,
                )
                rpm_gen_col = st.selectbox(
                    "Columna rpm generador (opcional)",
                    ["(ninguna)"] + cols,
                    index=0,
                )
                I_col = st.selectbox(
                    "Columna corriente [A] (opcional)",
                    ["(ninguna)"] + cols,
                    index=0,
                )

                st.session_state["scada_map"] = {
                    "mode": "classic_scada",
                    "v": v_col,
                    "P": P_col,
                    "rpm_rotor": None if rpm_rotor_col == "(ninguna)" else rpm_rotor_col,
                    "rpm_gen":  None if rpm_gen_col   == "(ninguna)" else rpm_gen_col,
                    "I":        None if I_col          == "(ninguna)" else I_col,
                }

                st.caption("La calibración se mostrará en el cuerpo principal cuando se complete la simulación.")
        else:
            st.error("No se encontró el archivo SCADA por defecto: assets/MG888.csv")

        

# =========================================================
# Cálculos base
# =========================================================
if gen_csv is not None:
    df_gen = read_uploaded_csv(gen_csv.getvalue())
    if not {"rpm", "P_kW", "V_LL"}.issubset(df_gen.columns):
        st.error("El CSV debe tener columnas: rpm, P_kW, V_LL")
        st.stop()
    tab_power = df_gen[["rpm", "P_kW"]].sort_values("rpm").reset_index(drop=True)
    tab_volt  = df_gen[["rpm", "V_LL"]].sort_values("rpm").reset_index(drop=True)
else:
    tab_power = GEN["power_table"][["rpm", "P_kW"]].sort_values("rpm").reset_index(drop=True)
    tab_volt  = GEN["volt_table"][["rpm", "V_LL"]].sort_values("rpm").reset_index(drop=True)

base_results = compute_base_results(
    D, H, N, c, eta_bear, eta_gear, helical, helix_angle_deg, endplates, trips,
    struts_perf, t_rel, is_symmetric, pitch_deg, control_mode, lam_opt_ctrl,
    v_cut_in, v_rated, v_cut_out, rpm_rotor_rated, G, rpm_gen_rated, rpm_v_exp,
    rho, mu, m_blade, lever_arm_pala, struts_per_blade, section_modulus_root,
    sigma_y_pala_mpa, strut_area_cm2, sigma_allow_strut_mpa, safety_target,
    T_gen_max, eta_gen_max, eta_elec, P_nom_kW, poles_total, pf_setpoint,
    Kt_nm_per_A, Ke_vsr_default, V_dc_nom, I_dc_nom, use_noise, Lw_ref_dB, r_obs,
    n_noise, v_min, v_max,
    tuple(tab_power["rpm"].tolist()),
    tuple(tab_power["P_kW"].tolist()),
    tuple(tab_volt["rpm"].tolist()),
    tuple(tab_volt["V_LL"].tolist()),
)

R = base_results["R"]
A = base_results["A"]
sig_int = base_results["sig_int"]
sig_conv = base_results["sig_conv"]
eta_mec = base_results["eta_mec"]
cp_params = base_results["cp_params"]
lambda_opt_teo = base_results["lambda_opt_teo"]
lambda_mppt = base_results["lambda_mppt"]
rpm_rated_val = base_results["rpm_rated_val"]
rpm_rated_ctrl = base_results["rpm_rated_ctrl"]
v_grid = base_results["v_grid"]
rpm_rotor = base_results["rpm_rotor"]
rpm_gen = base_results["rpm_gen"]
omega_rot = base_results["omega_rot"]
omega_gen = base_results["omega_gen"]
lambda_eff = base_results["lambda_eff"]
U_tip = base_results["U_tip"]
tsr_ref = base_results["tsr_ref"]
P_aero_W = base_results["P_aero_W"]
P_mec_gen_W = base_results["P_mec_gen_W"]
cp_used = base_results["cp_used"]
P_gen_curve_W = base_results["P_gen_curve_W"]
V_LL_curve = base_results["V_LL_curve"]
T_rotor_Nm = base_results["T_rotor_Nm"]
T_gen_Nm = base_results["T_gen_Nm"]
F_centripetal_series = base_results["F_centripetal_series"]
g_per_blade_series = base_results["g_per_blade_series"]
M_root_series_Nm = base_results["M_root_series_Nm"]
M_strut_series_Nm = base_results["M_strut_series_Nm"]
sigma_root_MPa = base_results["sigma_root_MPa"]
allow_root_MPa = base_results["allow_root_MPa"]
margin_root = base_results["margin_root"]
F_strut_series_N = base_results["F_strut_series_N"]
sigma_strut_MPa = base_results["sigma_strut_MPa"]
allow_strut_MPa = base_results["allow_strut_MPa"]
margin_strut = base_results["margin_strut"]
P_el_gen_W = base_results["P_el_gen_W"]
P_el_ac = base_results["P_el_ac"]
P_el_ac_clip = base_results["P_el_ac_clip"]
eta_gen_curve = base_results["eta_gen_curve"]
f_e_Hz = base_results["f_e_Hz"]
I_A = base_results["I_A"]
max_I_inv = base_results["max_I_inv"]
V_LL_from_Ke = base_results["V_LL_from_Ke"]
dc_util_series = base_results["dc_util_series"]
P_out_W = base_results["P_out_W"]
Cp_aero = base_results["Cp_aero"]
Cp_shaft = base_results["Cp_shaft"]
Cp_el = base_results["Cp_el"]
Re_mid = base_results["Re_mid"]
Lw_dB = base_results["Lw_dB"]
Lp_dB = base_results["Lp_dB"]
f_1P = base_results["f_1P"]
f_3P = base_results["f_3P"]
df = base_results["df"]
P_loss_mec_W = base_results["P_loss_mec_W"]
P_loss_gen_W = base_results["P_loss_gen_W"]
P_loss_elec_W = base_results["P_loss_elec_W"]
P_loss_clip_W = base_results["P_loss_clip_W"]

if control_mode == "MPPT (λ constante)" and abs(lambda_mppt - lambda_opt_teo) > 0.05:
    st.warning(
        f"λ_control ({lambda_mppt:.2f}) difiere del λ óptimo aerodinámico estimado ({lambda_opt_teo:.2f}). "
        "Operarás fuera de Cp_max a menos que alinees TSR de control y geometría."
    )

if control_mode == "MPPT (λ constante)" and abs(rpm_rotor_rated - rpm_rated_ctrl) > 5:
    st.warning(
        f"⚠️ rpm_rotor_rated ({rpm_rotor_rated:.1f} rpm) difiere de la rpm MPPT @ v_rated "
        f"({rpm_rated_ctrl:.1f} rpm). Revisa consistencia entre diseño aerodinámico, λ_opt y control MPPT."
    )

st.markdown("""
<style>

/* ===== Tabs del panel de KPIs ===== */
[data-testid="stTabs"] button {
    font-weight: 600;
    font-size: 0.9rem;          /* un poco más chico */
    padding-top: 0.5rem;
    padding-bottom: 0.5rem;
}

[data-testid="stTabs"] button[aria-selected="true"] {
    border-bottom: 3px solid #f97316 !important;
    color: #f97316 !important;
}

/* ===== Tarjetas KPI (25% más pequeñas) ===== */
.kpi-card {
    position: relative;
    overflow: hidden;
    background:
        radial-gradient(circle at top right, color-mix(in srgb, var(--kpi-accent) 9%, transparent), transparent 34%),
        linear-gradient(180deg, #f7f5f2 0%, #efeae5 100%);
    border-radius: 18px;
    padding: 0.9rem 1.05rem 0.95rem;
    border: 1px solid rgba(79,90,105,0.12);
    box-shadow: 0 8px 18px rgba(79,90,105,0.10);
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    gap: 0.5rem;
    height: 100%;
    min-height: 150px;
}

.kpi-card::before {
    content: "";
    position: absolute;
    inset: 0 auto auto 0;
    width: 100%;
    height: 4px;
    background: linear-gradient(90deg, var(--kpi-accent), rgba(255,255,255,0));
    opacity: 0.95;
}

.kpi-card::after {
    content: "";
    position: absolute;
    top: 14px;
    right: 14px;
    width: 72px;
    height: 72px;
    border-radius: 999px;
    background: radial-gradient(circle, color-mix(in srgb, var(--kpi-accent) 24%, transparent), transparent 68%);
    pointer-events: none;
}

.kpi-card__top {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: 0.75rem;
}

.kpi-badge {
    flex: 0 0 auto;
    padding: 0.22rem 0.5rem;
    border-radius: 999px;
    border: 1px solid color-mix(in srgb, var(--kpi-accent) 30%, rgba(79,90,105,0.10));
    background: color-mix(in srgb, var(--kpi-accent) 12%, #ffffff);
    color: #4f5a69;
    font-size: 0.62rem;
    letter-spacing: 0.14em;
    font-weight: 800;
    line-height: 1;
}

.kpi-title {
    text-transform: uppercase;
    letter-spacing: 0.11em;
    font-size: 0.64rem;
    line-height: 1.35;
    color: #6a7481;
    max-width: 80%;
}

.kpi-value {
    font-size: clamp(1.55rem, 1.2rem + 0.9vw, 2.1rem);
    font-weight: 800;
    line-height: 1.05;
    letter-spacing: -0.03em;
    color: var(--kpi-accent);
    text-wrap: balance;
}

.kpi-subtitle {
    font-size: 0.78rem;
    line-height: 1.4;
    color: #5f6b77;
    max-width: 92%;
}

/* Menos espacio vertical entre elementos del panel */
.element-container:has(.kpi-card) {
    margin-bottom: 0.72rem !important;
}

</style>
""", unsafe_allow_html=True)


# INICIO DEL WRAPPER
st.markdown('<div id="kpi-wrapper">', unsafe_allow_html=True)


# =========================================================
# Panel técnico de KPIs
# =========================================================
omega_rated = 2 * pi * rpm_rotor_rated / 60.0
P_rated_W   = P_nom_kW * 1000.0
T_rated     = P_rated_W / omega_rated if omega_rated > 0 else 0.0
k_mppt      = T_rated / (omega_rated ** 2) if omega_rated > 0 else 0.0

mass_total_blades = N * m_blade
I_blades = N * m_blade * (R ** 2)
F_centripetal_per_blade = m_blade * R * (omega_rated ** 2)
g_per_blade_rated = (R * (omega_rated ** 2) / 9.81) if omega_rated > 0 else 0.0
M_root_rated = (T_rated / max(N, 1)) + F_centripetal_per_blade * lever_arm_pala
M_strut_rated = M_root_rated / max(struts_per_blade, 1)

Re_8 = np.interp(8.0, v_grid, Re_mid) if (v_grid[0] <= 8.0 <= v_grid[-1]) else Re_mid[-1]
Re_max = Re_mid[-1] if len(Re_mid) > 0 else 0.0
active_resource_inputs = st.session_state.get("scada_resource_inputs", {}) or {}
use_extrapolated_resource = bool(active_resource_inputs.get("active")) and active_resource_inputs.get("mode") == "wind_height_profile"
k_energy = float(active_resource_inputs.get("weibull_k", k_w)) if use_extrapolated_resource else k_w
c_energy = float(active_resource_inputs.get("weibull_c", c_w)) if use_extrapolated_resource else c_w
resource_height_m = float(active_resource_inputs.get("target_height_m", default_turbine_resource_height(P_nom_kW))) if use_extrapolated_resource else default_turbine_resource_height(P_nom_kW)
scada_filename = st.session_state.get("df_scada_filename", "")
scada_source_label = f"CSV {scada_filename}" if scada_filename else "CSV cargado"
resource_origin = f"{scada_source_label} - perfil vertical extrapolado" if use_extrapolated_resource else "Weibull manual"

_P_curve_W_export = df["P_out (clip) kW"].values * 1000.0
_P_curve_W_export[v_grid < v_cut_in] = 0.0
_P_curve_W_export[v_grid > v_cut_out] = 0.0
_v_w_export = np.linspace(0.01, max(v_cut_out, v_max, 20.0), 400)
_P_interp_W_export = np.interp(_v_w_export, v_grid, _P_curve_W_export, left=0.0, right=0.0)
AEP_kWh, _P_mean_W_export = aep_from_weibull(_v_w_export, _P_interp_W_export, k_energy, c_energy)
CF = _P_mean_W_export / (P_nom_kW * 1000.0) if P_nom_kW > 0 else np.nan
download_aep_kwh = globals().get("AEP_kWh", np.nan)
download_cf = globals().get("CF", np.nan)

download_context_df = pd.DataFrame([
    {"Grupo": "Geometría", "Campo": "Diámetro D [m]", "Valor": D},
    {"Grupo": "Geometría", "Campo": "Altura H [m]", "Valor": H},
    {"Grupo": "Geometría", "Campo": "Área barrida A [m²]", "Valor": A},
    {"Grupo": "Geometría", "Campo": "Número de palas", "Valor": N},
    {"Grupo": "Geometría", "Campo": "Cuerda c [m]", "Valor": c},
    {"Grupo": "Geometría", "Campo": "Solidez σ_int", "Valor": sig_int},
    {"Grupo": "Geometría", "Campo": "Solidez σ_conv", "Valor": sig_conv},
    {"Grupo": "Perfil", "Campo": "Perfil aerodinámico", "Valor": airfoil_name},
    {"Grupo": "Perfil", "Campo": "Tipo de perfil", "Valor": tipo_perfil},
    {"Grupo": "Perfil", "Campo": "Espesor relativo [%]", "Valor": t_rel},
    {"Grupo": "Control", "Campo": "Modo operativo", "Valor": control_mode},
    {"Grupo": "Control", "Campo": "TSR referencia", "Valor": tsr_ref},
    {"Grupo": "Control", "Campo": "rpm rotor nominal", "Valor": rpm_rotor_rated},
    {"Grupo": "Viento", "Campo": "v_cut_in [m/s]", "Valor": v_cut_in},
    {"Grupo": "Viento", "Campo": "v_rated [m/s]", "Valor": v_rated},
    {"Grupo": "Viento", "Campo": "v_cut_out [m/s]", "Valor": v_cut_out},
    {"Grupo": "Viento", "Campo": "Weibull k", "Valor": k_w},
    {"Grupo": "Viento", "Campo": "Weibull c [m/s]", "Valor": c_w},
    {"Grupo": "Viento", "Campo": "Origen recurso activo", "Valor": resource_origin},
    {"Grupo": "Viento", "Campo": "Altura recurso activa [m]", "Valor": resource_height_m},
    {"Grupo": "Viento", "Campo": "Weibull k activo", "Valor": k_energy},
    {"Grupo": "Viento", "Campo": "Weibull c activo [m/s]", "Valor": c_energy},
    {"Grupo": "Tren de potencia", "Campo": "Relación G", "Valor": G},
    {"Grupo": "Tren de potencia", "Campo": "η_mec", "Valor": eta_mec},
    {"Grupo": "Tren de potencia", "Campo": "η_elec", "Valor": eta_elec},
    {"Grupo": "Tren de potencia", "Campo": "Potencia nominal [kW]", "Valor": P_nom_kW},
    {"Grupo": "Generador", "Campo": "Generador", "Valor": GEN["label"] if "GEN" in globals() else ""},
    {"Grupo": "Generador", "Campo": "Polos totales", "Valor": poles_total},
    {"Grupo": "Generador", "Campo": "I nominal [A]", "Valor": GDG_RATED_I},
    {"Grupo": "Generador", "Campo": "T nominal [N·m]", "Valor": GDG_RATED_T_Nm},
    {"Grupo": "Energía", "Campo": "AEP [kWh/año]", "Valor": download_aep_kwh},
    {"Grupo": "Energía", "Campo": "Factor de planta", "Valor": download_cf},
    {"Grupo": "Cargas", "Campo": "Masa total palas [kg]", "Valor": mass_total_blades},
    {"Grupo": "Cargas", "Campo": "T_rated [N·m]", "Valor": T_rated},
    {"Grupo": "Cargas", "Campo": "F centrípeta/pala nominal [kN]", "Valor": F_centripetal_per_blade / 1000.0},
    {"Grupo": "Cargas", "Campo": "M_base nominal [kN·m]", "Valor": M_root_rated / 1000.0},
])

entel_delivery_rows = [
    {"Capítulo RFP": "3.1 Características generales", "Entregable solicitado": "Plano general, ficha técnica y modelo 3D o plano de conjunto", "Evidencia en esta pestaña": "Ficha técnica resumida del rotor y parámetros principales", "Estado": "Parcial: adjuntar plano/modelo 3D"},
    {"Capítulo RFP": "3.1 Características generales", "Entregable solicitado": "Potencia nominal de 10 kW o capacidad equivalente con velocidad, densidad, rpm y condiciones eléctricas", "Evidencia en esta pestaña": "KPIs nominales, rpm rotor/generador y tabla por viento", "Estado": "Calculado"},
    {"Capítulo RFP": "3.1 Características generales", "Entregable solicitado": "Curva de potencia completa desde cut-in hasta cut-out, metodología y pérdidas", "Evidencia en esta pestaña": "Curva de potencia, tabla por bins y pérdidas por etapa", "Estado": "Calculado"},
    {"Capítulo RFP": "3.1 Características generales", "Entregable solicitado": "Disponibilidad >= 95% y vida útil esperada >= 20 años", "Evidencia en esta pestaña": "Supuesto de disponibilidad y compromiso de vida útil", "Estado": "A declarar comercialmente"},
    {"Capítulo RFP": "3.1 Características generales", "Entregable solicitado": "Control de velocidad, potencia, sobrevelocidad y parada segura independiente", "Evidencia en esta pestaña": "Filosofía de control y matriz causa-efecto preliminar", "Estado": "Preliminar"},
    {"Capítulo RFP": "3.1 Características generales", "Entregable solicitado": "Ingeniería estructural e interfaces para mástil y fundación", "Evidencia en esta pestaña": "Cargas, momentos, aceleraciones y checklist de planos de interfaz", "Estado": "Parcial: validar por cálculo estructural/FEM"},
    {"Capítulo RFP": "3.1 Características generales", "Entregable solicitado": "Protecciones eléctricas, seccionamiento, puesta a tierra y parada de emergencia", "Evidencia en esta pestaña": "Checklist eléctrico y parámetros preliminares", "Estado": "Preliminar"},
    {"Capítulo RFP": "3.1 Características generales", "Entregable solicitado": "Instrumentación y SCADA con viento, potencia, rpm, tensión, corriente, estados, alarmas y disponibilidad", "Evidencia en esta pestaña": "Lista de señales e integración de datos", "Estado": "Definido para propuesta"},
    {"Capítulo RFP": "3.1 Características generales", "Entregable solicitado": "Plan de calidad, trazabilidad y protocolos FAT/SAT", "Evidencia en esta pestaña": "Checklist ITP/QCP y ensayos", "Estado": "A formalizar"},
    {"Capítulo RFP": "3.1 Características generales", "Entregable solicitado": "Garantía técnica, repuestos y soporte disponible en Chile", "Evidencia en esta pestaña": "Matriz de garantías, SLA y repuestos críticos", "Estado": "A declarar comercialmente"},
    {"Capítulo RFP": "3.1 Características generales", "Entregable solicitado": "Matriz de cumplimiento y desviaciones completa", "Evidencia en esta pestaña": "Matriz exportable de cumplimiento Entel", "Estado": "Lista para completar/firma"},
    {"Capítulo RFP": "3.2 Producción energética", "Entregable solicitado": "Energy Yield Assessment con P50, sensibilidades, disponibilidad, pérdidas, incertidumbre y degradación", "Evidencia en esta pestaña": "Resumen energético y tabla de sensibilidades", "Estado": "Calculado con supuestos del simulador"},
    {"Capítulo RFP": "3.3 Desempeño aerodinámico", "Entregable solicitado": "Cut-in, nominal, máxima operación, cut-out, Cp y AEP para 4 a 8 m/s", "Evidencia en esta pestaña": "Tabla aerodinámica y sensibilidad por viento medio", "Estado": "Calculado"},
    {"Capítulo RFP": "3.4 Características eléctricas", "Entregable solicitado": "Tensión, frecuencia, inversor, on-grid, off-grid, baterías, rendimiento, anti-isla y tierra", "Evidencia en esta pestaña": "Checklist eléctrico preliminar", "Estado": "Parcial: completar con proveedor/inversor"},
    {"Capítulo RFP": "4 Sistema de monitoreo", "Entregable solicitado": "Monitoreo web/móvil, históricos 24 meses, exportación CSV/Excel, API/MQTT/Modbus/SNMP/SCADA", "Evidencia en esta pestaña": "Arquitectura y lista de señales", "Estado": "Definido para integración"},
    {"Capítulo RFP": "5 Instalación", "Entregable solicitado": "Planos montaje, obra civil, cálculo estructural, cargas fundación, tierra y seguridad operacional", "Evidencia en esta pestaña": "Checklist de instalación y cargas principales", "Estado": "Parcial"},
    {"Capítulo RFP": "6 Experiencia proveedor", "Entregable solicitado": "Experiencia desarrollando tecnología VAWT", "Evidencia en esta pestaña": "Lista de antecedentes a adjuntar", "Estado": "A adjuntar"},
    {"Capítulo RFP": "7 Garantías", "Entregable solicitado": "Garantías, repuestos, soporte remoto/presencial, SLA y disponibilidad anual", "Evidencia en esta pestaña": "Tabla de garantía y SLA objetivo", "Estado": "A validar comercialmente"},
    {"Capítulo RFP": "8 Repuestos y servicio local", "Entregable solicitado": "Inventario en Chile, bodega, tiempos de entrega, repuestos críticos y técnicos certificados", "Evidencia en esta pestaña": "Lista de repuestos críticos y servicio", "Estado": "A completar"},
    {"Capítulo RFP": "9 Importación y logística", "Entregable solicitado": "Entrega en Santiago, bodegaje 2 meses y plazo menor a 120 días deseable", "Evidencia en esta pestaña": "Checklist logístico", "Estado": "A declarar"},
    {"Capítulo RFP": "10 Documentación técnica", "Entregable solicitado": "Datasheet, curvas, certificaciones, unilineales, O&M, repuestos, catálogo, garantías y mantenimiento", "Evidencia en esta pestaña": "Índice documental", "Estado": "Checklist listo"},
    {"Capítulo RFP": "11 Seguridad", "Entregable solicitado": "Normativa eléctrica, estructural, prevención de riesgos, LOTO y protección atmosférica", "Evidencia en esta pestaña": "Matriz de seguridad", "Estado": "A validar por especialidad"},
]
entel_delivery_df = pd.DataFrame(entel_delivery_rows)
entel_explanation_map = {
    "3.1 Características generales": "Define si la solución es técnicamente aceptable: potencia, curva de potencia, control, estructura, protecciones, SCADA, calidad, garantías y matriz de desviaciones.",
    "3.2 Producción energética": "Permite comparar tecnologías por energía útil anual y factor de planta en el sitio, no solo por potencia nominal de catálogo.",
    "3.3 Desempeño aerodinámico": "Documenta velocidades operativas, Cp, estabilidad, ruido, vibración y producción esperada a vientos medios de 4 a 8 m/s.",
    "3.4 Características eléctricas": "Aterriza la compatibilidad con red, baterías, inversor, protecciones anti-isla, rendimiento y puesta a tierra.",
    "4 Sistema de monitoreo": "Asegura trazabilidad operativa del piloto: datos históricos, señales críticas, alarmas, disponibilidad e integración SCADA.",
    "5 Instalación": "Entrega las bases para que ENTEL o terceros diseñen mástil, fundación, montaje, puesta a tierra y seguridad operacional.",
    "6 Experiencia proveedor": "Acredita capacidad real de desarrollo/fabricación/pruebas VAWT con antecedentes verificables.",
    "7 Garantías": "Fija cobertura técnica, SLA, soporte remoto/presencial, tratamiento de defectos críticos y garantía de disponibilidad.",
    "8 Repuestos y servicio local": "Reduce riesgo operacional declarando inventario, tiempos de reposición, técnicos disponibles y estrategia de obsolescencia.",
    "9 Importación y logística": "Ordena entrega en Santiago, bodegaje mínimo y plazo comprometido desde adjudicación hasta entrega física.",
    "10 Documentación técnica": "Lista los anexos exigidos para revisión técnica, operación, mantenimiento, garantías y aceptación del piloto.",
    "11 Seguridad": "Cubre normativa eléctrica/estructural, prevención de riesgos, bloqueo-etiquetado y protección contra descargas atmosféricas.",
}
entel_delivery_df["Explicación técnica"] = entel_delivery_df["Capítulo RFP"].map(entel_explanation_map).fillna(
    "Evidencia requerida para responder la solicitud técnica de ENTEL."
)
entel_delivery_df["Acción propuesta"] = np.where(
    entel_delivery_df["Estado"].str.contains("Calculado|Definido|Lista", case=False, na=False),
    "Usar datos de esta app y exportar anexo.",
    "Adjuntar documento externo o completar compromiso del proveedor.",
)

entel_url_curve_df = load_entel_power_curve_from_url()
if not entel_url_curve_df.empty:
    entel_curve_df = entel_url_curve_df.copy()
    entel_curve_source = "Curva de potencia URL Google Sheets"
    entel_curve_source_detail = ENTEL_POWER_CURVE_URL
else:
    entel_curve_df = df.copy()
    entel_curve_source = "Curva interna del simulador"
    entel_curve_source_detail = "Fallback automático: el URL no respondió o no tuvo columnas válidas."

for supplemental_col in [
    "rpm_gen", "I_est (A)", "Duty_DC (%)", "V_LL (V)", "V_LL (Ke) [V]",
    "f_e (Hz)", "P_gen_curve (kW)", "U_tip (m/s)", "a_cen (g)",
    "f_1P (Hz)", "f_3P (Hz)", "Lw (dB)", "Lp_obs (dB)",
]:
    if supplemental_col not in entel_curve_df.columns and supplemental_col in df.columns and "v (m/s)" in entel_curve_df.columns:
        entel_curve_df[supplemental_col] = np.interp(
            entel_curve_df["v (m/s)"].to_numpy(dtype=float),
            df["v (m/s)"].to_numpy(dtype=float),
            pd.to_numeric(df[supplemental_col], errors="coerce").fillna(0.0).to_numpy(dtype=float),
            left=np.nan,
            right=np.nan,
        )

v_curve = entel_curve_df["v (m/s)"].values if "v (m/s)" in entel_curve_df.columns else np.array([])
p_curve_kw = entel_curve_df["P_out (clip) kW"].values if "P_out (clip) kW" in entel_curve_df.columns else np.array([])
entel_D_m = ENTEL_OFFER_DIAMETER_M
entel_H_m = ENTEL_OFFER_ROTOR_HEIGHT_M
entel_installation_height_m = ENTEL_OFFER_INSTALLATION_HEIGHT_M_10KW
entel_mast_height_m = ENTEL_OFFER_MAST_HEIGHT_M
entel_A_m2 = ENTEL_OFFER_AREA_M2
entel_state_series = entel_curve_df.get("Estado curva URL", pd.Series(dtype=str)).astype(str).str.lower()
entel_positive_power_mask = pd.to_numeric(entel_curve_df.get("P_out (clip) kW", pd.Series(dtype=float)), errors="coerce").fillna(0.0) > 0
entel_nominal_mask = entel_state_series.str.contains("nominal", na=False)
entel_cutout_state_mask = entel_state_series.str.contains("velocidad de corte|cut-out", na=False)
entel_stopped_high_mask = entel_state_series.str.contains("sobre cut-out", na=False)
entel_v_cut_in = (
    float(entel_curve_df.loc[entel_positive_power_mask, "v (m/s)"].min())
    if entel_positive_power_mask.any()
    else float(v_cut_in)
)
entel_v_rated = (
    float(entel_curve_df.loc[entel_nominal_mask, "v (m/s)"].min())
    if entel_nominal_mask.any()
    else float(entel_curve_df.loc[pd.to_numeric(entel_curve_df["P_out (clip) kW"], errors="coerce").idxmax(), "v (m/s)"])
    if "P_out (clip) kW" in entel_curve_df.columns and entel_curve_df["P_out (clip) kW"].notna().any()
    else float(v_rated)
)
entel_v_cut_out = (
    float(entel_curve_df.loc[entel_cutout_state_mask & ~entel_stopped_high_mask, "v (m/s)"].max())
    if (entel_cutout_state_mask & ~entel_stopped_high_mask).any()
    else float(entel_curve_df.loc[entel_positive_power_mask, "v (m/s)"].max())
    if entel_positive_power_mask.any()
    else float(v_cut_out)
)
entel_v_max_plot = max(entel_v_cut_out, float(np.nanmax(v_curve)) if len(v_curve) else 20.0, 20.0)
entel_p_nom_kw = float(np.nanmax(p_curve_kw)) if len(p_curve_kw) else P_nom_kW
v_w_entel_base = np.linspace(0.01, entel_v_max_plot, 700)
p_interp_entel_w = np.interp(v_w_entel_base, v_curve, p_curve_kw * 1000.0, left=0.0, right=0.0) if len(v_curve) and len(p_curve_kw) else np.zeros_like(v_w_entel_base)
p_interp_entel_w[v_w_entel_base < entel_v_cut_in] = 0.0
p_interp_entel_w[v_w_entel_base > entel_v_cut_out] = 0.0
entel_AEP_kWh, entel_P_mean_W = aep_from_weibull(v_w_entel_base, p_interp_entel_w, k_energy, c_energy)
entel_CF = entel_AEP_kWh / (entel_p_nom_kw * 8760.0) if entel_p_nom_kw > 0 else np.nan

def entel_num_es(value, decimals: int = 1, suffix: str = "") -> str:
    try:
        numeric_value = float(value)
    except (TypeError, ValueError):
        return str(value) if value is not None else "-"
    if not np.isfinite(numeric_value):
        return "-"
    text = f"{numeric_value:,.{decimals}f}"
    text = text.replace(",", "§").replace(".", ",").replace("§", ".")
    return f"{text}{suffix}"

def entel_int_es(value, suffix: str = "") -> str:
    return entel_num_es(value, 0, suffix)

entel_summary_rows = [
    {"Campo": "Proyecto", "Valor": "Aerogenerador de eje vertical para sitio ENTEL zona austral"},
    {"Campo": "Alcance RFP", "Valor": "Suministro VAWT, transporte/entrega Santiago, documentación, capacitación, monitoreo, datos y soporte postventa"},
    {"Campo": "Potencia objetivo RFP [kW]", "Valor": 10.0},
    {"Campo": "Potencia nominal curva Entel [kW]", "Valor": entel_p_nom_kw},
    {"Campo": "Diámetro rotor D Entel [m]", "Valor": entel_D_m},
    {"Campo": "Altura rotor H Entel [m]", "Valor": entel_H_m},
    {"Campo": "Altura instalación Entel [m]", "Valor": entel_installation_height_m},
    {"Campo": "Altura mástil Entel [m]", "Valor": entel_mast_height_m},
    {"Campo": "Área barrida Entel [m²]", "Valor": entel_A_m2},
    {"Campo": "Cut-in Entel [m/s]", "Valor": entel_v_cut_in},
    {"Campo": "Velocidad nominal Entel [m/s]", "Valor": entel_v_rated},
    {"Campo": "Cut-out Entel [m/s]", "Valor": entel_v_cut_out},
    {"Campo": "TSR referencia", "Valor": tsr_ref},
    {"Campo": "Relación transmisión G", "Valor": G},
    {"Campo": "Generador", "Valor": GEN["label"] if "GEN" in globals() else ""},
    {"Campo": "Origen recurso eólico", "Valor": resource_origin},
    {"Campo": "Altura instalación/recurso Entel [m]", "Valor": entel_installation_height_m},
    {"Campo": "Weibull activo k", "Valor": k_energy},
    {"Campo": "Weibull activo c [m/s]", "Valor": c_energy},
    {"Campo": "Fuente curva de potencia Entel", "Valor": entel_curve_source},
    {"Campo": "Detalle fuente curva", "Valor": entel_curve_source_detail},
    {"Campo": "AEP P50 técnico [kWh/año]", "Valor": entel_AEP_kWh},
    {"Campo": "Factor de planta P50 [%]", "Valor": entel_CF * 100},
    {"Campo": "Disponibilidad mínima RFP [%]", "Valor": 95.0},
    {"Campo": "Vida útil esperada RFP [años]", "Valor": 20},
]
entel_summary_df = pd.DataFrame(entel_summary_rows)

entel_mean_wind_rows = []
for mean_v in [4, 5, 6, 7, 8]:
    try:
        c_mean = mean_v / gamma(1.0 + 1.0 / max(float(k_energy), 0.1))
        v_w_entel = np.linspace(0.01, entel_v_max_plot, 500)
        p_interp_w = np.interp(v_w_entel, v_curve, p_curve_kw * 1000.0, left=0.0, right=0.0)
        p_interp_w[v_w_entel < entel_v_cut_in] = 0.0
        p_interp_w[v_w_entel > entel_v_cut_out] = 0.0
        aep_mean, p_mean_w = aep_from_weibull(v_w_entel, p_interp_w, k_energy, c_mean)
        cf_mean = aep_mean / (entel_p_nom_kw * 8760.0) if entel_p_nom_kw > 0 else np.nan
    except Exception:
        aep_mean, p_mean_w, cf_mean = np.nan, np.nan, np.nan
    entel_mean_wind_rows.append({
        "Viento medio [m/s]": mean_v,
        "AEP estimado [kWh/año]": aep_mean,
        "Potencia promedio [kW]": p_mean_w / 1000.0 if np.isfinite(p_mean_w) else np.nan,
        "Factor planta [%]": cf_mean * 100 if np.isfinite(cf_mean) else np.nan,
        "Base técnica verificable": f"Cálculo Weibull con k activo {entel_num_es(k_energy, 2)}",
    })
entel_mean_wind_df = pd.DataFrame(entel_mean_wind_rows)

entel_sensitivity_df = pd.DataFrame([
    {"Caso": "P50 técnico base", "Supuesto": entel_curve_source, "AEP [kWh/año]": entel_AEP_kWh, "Factor planta [%]": entel_CF * 100},
    {"Caso": "P50 con disponibilidad RFP", "Supuesto": "Disponibilidad 95%", "AEP [kWh/año]": entel_AEP_kWh * 0.95, "Factor planta [%]": entel_CF * 95},
    {"Caso": "Sensibilidad recurso -10%", "Supuesto": "Incertidumbre recurso baja", "AEP [kWh/año]": entel_AEP_kWh * 0.90, "Factor planta [%]": entel_CF * 90},
    {"Caso": "Sensibilidad recurso +10%", "Supuesto": "Incertidumbre recurso alta", "AEP [kWh/año]": entel_AEP_kWh * 1.10, "Factor planta [%]": entel_CF * 110},
    {"Caso": "Pérdidas eléctricas adicionales", "Supuesto": "Pérdida adicional 3%", "AEP [kWh/año]": entel_AEP_kWh * 0.97, "Factor planta [%]": entel_CF * 97},
    {"Caso": "Degradación año 1", "Supuesto": "Degradación anual 0,5%", "AEP [kWh/año]": entel_AEP_kWh * 0.995, "Factor planta [%]": entel_CF * 99.5},
])

month_names_entel = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
    5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
    9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre",
}

def build_entel_monthly_energy_df() -> pd.DataFrame:
    records = active_resource_inputs.get("target_series_records", []) if use_extrapolated_resource else []
    if records:
        monthly_source = pd.DataFrame(records)
        if {"timestamp", "v_target_m_s"}.issubset(monthly_source.columns):
            monthly_source["timestamp"] = pd.to_datetime(monthly_source["timestamp"], errors="coerce")
            monthly_source["v_target_m_s"] = pd.to_numeric(monthly_source["v_target_m_s"], errors="coerce")
            monthly_source = monthly_source.dropna(subset=["timestamp", "v_target_m_s"]).sort_values("timestamp")
            if not monthly_source.empty:
                diffs_h = monthly_source["timestamp"].diff().dt.total_seconds().div(3600.0)
                dt_h = float(diffs_h[(diffs_h > 0) & np.isfinite(diffs_h)].median()) if diffs_h.notna().any() else 1.0
                if not np.isfinite(dt_h) or dt_h <= 0:
                    dt_h = 1.0
                monthly_source["P_est_kW"] = np.interp(
                    monthly_source["v_target_m_s"].to_numpy(dtype=float),
                    v_curve,
                    p_curve_kw,
                    left=0.0,
                    right=0.0,
                )
                monthly_source.loc[monthly_source["v_target_m_s"] < entel_v_cut_in, "P_est_kW"] = 0.0
                monthly_source.loc[monthly_source["v_target_m_s"] > entel_v_cut_out, "P_est_kW"] = 0.0
                monthly_source["E_direct_kWh"] = monthly_source["P_est_kW"] * dt_h
                grouped = monthly_source.groupby(monthly_source["timestamp"].dt.month)["E_direct_kWh"].sum()
                direct_total = float(grouped.sum())
                if direct_total > 0 and np.isfinite(entel_AEP_kWh):
                    rows = []
                    for month_idx in range(1, 13):
                        direct_kwh = float(grouped.get(month_idx, 0.0))
                        share = direct_kwh / direct_total if direct_total > 0 else 0.0
                        rows.append({
                            "Mes": month_names_entel[month_idx],
                            "Producción esperada [kWh/mes]": entel_AEP_kWh * share,
                            "Participación anual [%]": share * 100.0,
                            "Producción serie directa [kWh/periodo]": direct_kwh,
                            "Base técnica verificable": f"Distribución mensual desde {scada_source_label} extrapolado; escalada al AEP P50 técnico anual",
                        })
                    return pd.DataFrame(rows)

    return pd.DataFrame([
        {
            "Mes": mes,
            "Producción esperada [kWh/mes]": entel_AEP_kWh / 12.0,
            "Participación anual [%]": 100.0 / 12.0,
            "Producción serie directa [kWh/periodo]": np.nan,
            "Base técnica verificable": "Distribución uniforme referencial; cargar serie SCADA con fecha para estacionalidad mensual",
        }
        for mes in month_names_entel.values()
    ])

entel_monthly_df = build_entel_monthly_energy_df()

active_resource_df = pd.DataFrame(active_resource_inputs.get("profile_summary", [])) if use_extrapolated_resource else pd.DataFrame()
entel_resource_summary_df = pd.DataFrame([
    {"Parámetro": "Origen", "Valor": resource_origin},
    {"Parámetro": "Altura objetivo Entel [m]", "Valor": entel_num_es(entel_installation_height_m, 1)},
    {"Parámetro": "Método extrapolación", "Valor": active_resource_inputs.get("method", "No aplica")},
    {"Parámetro": "Alturas fuente [m]", "Valor": f"{entel_num_es(active_resource_inputs.get('source_height_min_m', np.nan), 1)} a {entel_num_es(active_resource_inputs.get('source_height_max_m', np.nan), 1)}" if use_extrapolated_resource else "No aplica"},
    {"Parámetro": "Velocidad media a altura objetivo [m/s]", "Valor": entel_num_es(active_resource_inputs.get("v_mean", np.nan), 2) if use_extrapolated_resource else "No aplica"},
    {"Parámetro": "Alpha vertical medio", "Valor": entel_num_es(active_resource_inputs.get("shear_alpha", np.nan), 3) if use_extrapolated_resource else "No aplica"},
    {"Parámetro": "Alpha vertical mediano", "Valor": entel_num_es(active_resource_inputs.get("shear_alpha_median", np.nan), 3) if use_extrapolated_resource else "No aplica"},
    {"Parámetro": "Registros válidos", "Valor": entel_int_es(active_resource_inputs.get("sample_count", np.nan)) if use_extrapolated_resource else "No aplica"},
])

entel_control_df = pd.DataFrame([
    {"Evento": "Viento bajo cut-in", "Condición": f"v < {entel_num_es(entel_v_cut_in, 1)} m/s", "Acción": "Rotor disponible, sin inyección de potencia", "Señales": "viento, rpm, estado"},
    {"Evento": "Región MPPT", "Condición": f"{entel_num_es(entel_v_cut_in, 1)} <= v < {entel_num_es(entel_v_rated, 1)} m/s", "Acción": "Seguimiento TSR y optimización de potencia", "Señales": "rpm, potencia, torque/corriente"},
    {"Evento": "Potencia limitada", "Condición": f"{entel_num_es(entel_v_rated, 1)} <= v <= {entel_num_es(entel_v_cut_out, 1)} m/s", "Acción": "Limitación de potencia/corriente y control de rpm", "Señales": "P_out, I_est, rpm_gen"},
    {"Evento": "Sobre cut-out", "Condición": f"v > {entel_num_es(entel_v_cut_out, 1)} m/s", "Acción": "Parada segura y bloqueo hasta condición de rearme", "Señales": "alarma viento alto, estado freno"},
    {"Evento": "Falla crítica", "Condición": "Sobrevelocidad, sobrecorriente, vibración, E-stop o pérdida comunicación crítica", "Acción": "Parada independiente fail-safe y alarma SCADA", "Señales": "alarmas, estados, disponibilidad"},
])

entel_scada_df = pd.DataFrame([
    {"Grupo": "Tiempo real", "Señal": "Potencia instantánea", "Formato/uso": "kW, tendencia y alarma"},
    {"Grupo": "Tiempo real", "Señal": "Energía acumulada", "Formato/uso": "kWh, acumulado diario/mensual/anual"},
    {"Grupo": "Tiempo real", "Señal": "Velocidad de viento", "Formato/uso": "m/s, bin energético y protección"},
    {"Grupo": "Tiempo real", "Señal": "RPM rotor/generador", "Formato/uso": "rpm, control y sobrevelocidad"},
    {"Grupo": "Eléctrico", "Señal": "Tensión, corriente y frecuencia", "Formato/uso": "V, A, Hz para calidad eléctrica"},
    {"Grupo": "Operación", "Señal": "Estado operativo", "Formato/uso": "Disponible, operando, limitada, detenida, falla"},
    {"Grupo": "Operación", "Señal": "Alarmas y eventos", "Formato/uso": "Registro con timestamp"},
    {"Grupo": "Disponibilidad", "Señal": "Horas disponibles y no disponibles", "Formato/uso": "Cálculo SLA >= 95%"},
    {"Grupo": "Plataforma", "Señal": "Históricos", "Formato/uso": "24 meses mínimo, exportación CSV/Excel"},
    {"Grupo": "Integración", "Señal": "API/MQTT/Modbus TCP/IP/SNMP", "Formato/uso": "Conexión con SCADA ENTEL"},
])

entel_electrical_df = pd.DataFrame([
    {"Ítem": "Tensión nominal de salida", "Respuesta preliminar": "Completar según inversor/controlador ofertado"},
    {"Ítem": "Frecuencia", "Respuesta preliminar": "50 Hz para integración AC cuando aplique"},
    {"Ítem": "Tipo de inversor", "Respuesta preliminar": "On-grid/off-grid/híbrido según arquitectura del sitio"},
    {"Ítem": "Compatibilidad on-grid", "Respuesta preliminar": "A confirmar con protecciones anti-isla y norma local"},
    {"Ítem": "Compatibilidad off-grid/baterías", "Respuesta preliminar": "A confirmar con bus DC/BMS/controlador"},
    {"Ítem": "Rendimiento inversor", "Respuesta preliminar": "Declarar curva y eficiencia europea/ponderada"},
    {"Ítem": "Protección anti-isla", "Respuesta preliminar": "Requerida si existe paralelismo con red"},
    {"Ítem": "Puesta a tierra y descargas atmosféricas", "Respuesta preliminar": "Malla/tierra, SPD y coordinación con mástil/fundación"},
    {"Ítem": "Seccionamiento y parada emergencia", "Respuesta preliminar": "Seccionador bloqueable, E-stop y LOTO"},
])

entel_service_df = pd.DataFrame([
    {"Categoría": "Garantía equipos/fabricación", "Compromiso RFP": "24 meses desde aceptación provisional o 30 meses desde entrega"},
    {"Categoría": "Reparaciones/reemplazos", "Compromiso RFP": "12 meses desde intervención o saldo de garantía, el período mayor"},
    {"Categoría": "Software/configuración", "Compromiso RFP": "Corrección de defectos, respaldo y compatibilidad durante garantía"},
    {"Categoría": "Defectos críticos", "Compromiso RFP": "Atención remota prioritaria y plan documentado"},
    {"Categoría": "SLA remoto", "Compromiso RFP": "Respuesta remota <= 24 horas"},
    {"Categoría": "SLA presencial", "Compromiso RFP": "Atención presencial <= 72 horas"},
    {"Categoría": "Repuestos críticos", "Compromiso RFP": "Rodamientos, controladores, sensores, freno, inversores, módulos comunicación"},
    {"Categoría": "Logística", "Compromiso RFP": "Entrega Santiago, bodegaje 2 meses, plazo deseable < 120 días"},
])

entel_docs_df = pd.DataFrame([
    {"Documento": "Datasheet oficial", "Uso Entel": "Ficha técnica y condiciones nominales", "Responsable": "Proveedor"},
    {"Documento": "Curva de potencia y CSV/planilla editable", "Uso Entel": "Evaluación energética objetiva", "Responsable": "Simulador/proveedor"},
    {"Documento": "Certificaciones", "Uso Entel": "Cumplimiento normativo y calidad", "Responsable": "Proveedor"},
    {"Documento": "Diagramas unilineales", "Uso Entel": "Integración eléctrica y protecciones", "Responsable": "Ingeniería eléctrica"},
    {"Documento": "Manual O&M", "Uso Entel": "Operación y mantenimiento", "Responsable": "Proveedor"},
    {"Documento": "Lista de repuestos", "Uso Entel": "Soporte 2 años y obsolescencia", "Responsable": "Proveedor"},
    {"Documento": "Catálogo técnico", "Uso Entel": "Información comercial/técnica", "Responsable": "Proveedor"},
    {"Documento": "Garantías", "Uso Entel": "Cobertura contractual", "Responsable": "Comercial/proveedor"},
    {"Documento": "Plan de mantenimiento", "Uso Entel": "Preventivo/correctivo", "Responsable": "Proveedor/O&M"},
    {"Documento": "Planos montaje e interfaz", "Uso Entel": "Mástil, fundación y montaje", "Responsable": "Ingeniería mecánica/civil"},
    {"Documento": "Memoria estructural y cargas", "Uso Entel": "Diseño fundación/mástil", "Responsable": "Ingeniería estructural"},
    {"Documento": "Protocolos FAT/SAT e ITP/QCP", "Uso Entel": "Calidad, ensayos y aceptación", "Responsable": "Calidad/proveedor"},
])

entel_color_map = {
    "P_aero (kW)": "#4f8a8b",
    "Potencia aerodinámica [kW]": "#4f8a8b",
    "P_mec_gen (kW)": "#2f5f73",
    "Potencia mecánica [kW]": "#2f5f73",
    "P_gen_curve (kW)": "#2f5f73",
    "P_el (kW)": "#c47a3c",
    "Potencia eléctrica [kW]": "#c47a3c",
    "P_out (clip) kW": "#9b4f5f",
    "Potencia eléctrica neta [kW]": "#9b4f5f",
    "Cp(λ_efectiva)": "#d9a766",
    "Cp_aero_equiv": "#a36a2d",
    "Cp_el_equiv": "#7c4d8b",
    "η_gen (curve)": "#5f7f75",
    "V_LL (V)": "#2f5f73",
    "V_LL (Ke) [V]": "#84a9a4",
    "f_e (Hz)": "#d9a766",
    "I_est (A)": "#9b4f5f",
    "Duty_DC (%)": "#6b7280",
    "U_tip (m/s)": "#2f5f73",
    "f_1P (Hz)": "#c47a3c",
    "f_3P (Hz)": "#d95f5f",
    "Lp_obs (dB)": "#6b7280",
    "Horas/año": "#6b7280",
    "Energía bin": "#2f5f73",
    "Energía neta": "#5f7f75",
    "Pérdida": "#d95f5f",
    "Producción mensual": "#2f5f73",
    "Acumulado": "#5f7f75",
    "Base": "#2f5f73",
    "Disponibilidad": "#d95f5f",
    "Pérdidas eléctricas": "#c47a3c",
    "Incertidumbre recurso": "#d9a766",
    "Degradación": "#6b7280",
    "Combinado conservador": "#5f7f75",
    "Cumple": "#5f7f75",
    "Contemplado": "#d9a766",
    "En desarrollo": "#9b4f5f",
    "Sin estado": "#6b7280",
    "Confirmado": "#5f7f75",
    "Incluido": "#5f7f75",
    "Adjuntado / indicado": "#2f5f73",
    "Entrega posterior": "#d9a766",
    "Pendiente": "#d95f5f",
    "Brecha declarada": "#9b4f5f",
    "No aplica": "#6b7280",
    "Declarado": "#84a9a4",
    "Sin respuesta": "#6b7280",
}

entel_monitoring_payload = load_entel_monitoring_from_url()
entel_monitoring_df = entel_monitoring_payload["df"].copy()
entel_monitoring_title = entel_monitoring_payload.get("title", "ENTEL - Ítem 4: Sistema de Monitoreo")
entel_monitoring_intro = entel_monitoring_payload.get("intro", "")
entel_monitoring_source_note = entel_monitoring_payload.get("source_note", "")
entel_monitoring_source = entel_monitoring_payload.get("source", "URL Google Sheets")
entel_monitoring_total = int(len(entel_monitoring_df))
entel_monitoring_status_df = (
    entel_monitoring_df.groupby("Estado", dropna=False)
    .size()
    .reset_index(name="Cantidad")
    .sort_values("Cantidad", ascending=False)
)
entel_monitoring_status_df["Participación [%]"] = (
    entel_monitoring_status_df["Cantidad"] / max(entel_monitoring_total, 1) * 100.0
)
entel_monitoring_section_df = (
    entel_monitoring_df.groupby(["Familia", "Estado"], dropna=False)
    .size()
    .reset_index(name="Cantidad")
)
entel_monitoring_section_pivot_df = (
    entel_monitoring_section_df.pivot_table(
        index="Familia",
        columns="Estado",
        values="Cantidad",
        aggfunc="sum",
        fill_value=0,
    )
    .reset_index()
)
for status_name in ["Cumple", "Contemplado", "En desarrollo", "Sin estado"]:
    if status_name not in entel_monitoring_section_pivot_df.columns:
        entel_monitoring_section_pivot_df[status_name] = 0
entel_monitoring_section_pivot_df["Total requisitos"] = entel_monitoring_section_pivot_df[
    ["Cumple", "Contemplado", "En desarrollo", "Sin estado"]
].sum(axis=1)
entel_monitoring_section_pivot_df["Cobertura lista o contemplada [%]"] = (
    (entel_monitoring_section_pivot_df["Cumple"] + entel_monitoring_section_pivot_df["Contemplado"])
    / entel_monitoring_section_pivot_df["Total requisitos"].replace(0, np.nan)
    * 100.0
)
entel_monitoring_section_pivot_df = entel_monitoring_section_pivot_df[
    ["Familia", "Total requisitos", "Cumple", "Contemplado", "En desarrollo", "Sin estado", "Cobertura lista o contemplada [%]"]
]
entel_monitoring_integration_df = entel_monitoring_df[
    entel_monitoring_df["Familia"].astype(str).str.contains("Integración", case=False, na=False)
].copy()
entel_monitoring_architecture_df = pd.DataFrame([
    {
        "Bloque funcional": "Aerogenerador",
        "Función monitoreada": "Potencia instantánea, RPM del rotor, estado operativo, alarmas y eventos.",
        "Equipo / plataforma": "Controlador eléctrico del aerogenerador y plataforma de monitoreo operacional.",
        "Estado": "Cumple",
        "Cierre requerido": "Validar tags, frecuencia de muestreo, timestamp, estados normalizados y lógica de alarmas en SAT.",
    },
    {
        "Bloque funcional": "Gestión energética",
        "Función monitoreada": "Energía acumulada, potencia gestionada y variables eléctricas asociadas al sistema híbrido.",
        "Equipo / plataforma": "Inversor híbrido trifásico y plataforma de gestión energética.",
        "Estado": "Cumple",
        "Cierre requerido": "Confirmar medición neta, acumulados diarios/mensuales/anuales y consistencia con exportación de datos.",
    },
    {
        "Bloque funcional": "Recurso eólico y meteorología",
        "Función monitoreada": "Velocidad de viento y variables meteorológicas relevantes para desempeño del piloto.",
        "Equipo / plataforma": "Estación meteorológica multiparámetro y plataforma de monitoreo meteorológico remoto.",
        "Estado": "Cumple",
        "Cierre requerido": "Definir ubicación, altura de medición, calibración, intervalo de registro y trazabilidad del sensor.",
    },
    {
        "Bloque funcional": "Datos históricos y dashboard",
        "Función monitoreada": "Históricos 24 meses, exportación CSV/Excel, panel configurable y acceso web/móvil.",
        "Equipo / plataforma": "Sistema de adquisición, almacenamiento y visualización de datos.",
        "Estado": "Contemplado",
        "Cierre requerido": "Definir retención, granularidad, roles de acceso, respaldo, exportación y propietario del dato.",
    },
    {
        "Bloque funcional": "Integración externa",
        "Función monitoreada": "Interoperabilidad con API, MQTT, Modbus TCP/IP, SNMP y SCADA.",
        "Equipo / plataforma": "Sistema de comunicaciones e integración de datos.",
        "Estado": "Mixto",
        "Cierre requerido": "Priorizar Modbus TCP/IP y SCADA; cerrar mapa de registros, ciberseguridad, red/APN/VPN y pruebas de interoperabilidad.",
    },
])
entel_monitoring_analysis_df = pd.DataFrame([
    {
        "Eje de análisis": "Variables críticas en tiempo real",
        "Lectura técnica": "Potencia, energía, viento, rpm, estado operativo, alarmas y eventos quedan declarados como señales disponibles para puesta en marcha o primeros meses.",
        "Evidencia desde matriz": f"{int((entel_monitoring_df['Familia'] == 'Monitoreo en Tiempo Real').sum())} requisitos en monitoreo operacional.",
        "Prioridad de cierre": "Validar tags, frecuencia de muestreo, timestamp, unidades y lógica de alarmas en protocolo SAT.",
    },
    {
        "Eje de análisis": "Plataforma y trazabilidad histórica",
        "Lectura técnica": "El acceso web/móvil está cubierto; históricos de 24 meses, exportación CSV/Excel y dashboard configurable se tratan como capacidades contempladas.",
        "Evidencia desde matriz": f"{int((entel_monitoring_df['Familia'] == 'Plataforma').sum())} requisitos de plataforma y datos.",
        "Prioridad de cierre": "Definir retención, granularidad, respaldo, propietario del dato y procedimiento de exportación.",
    },
    {
        "Eje de análisis": "Integración con sistemas externos",
        "Lectura técnica": "Modbus TCP/IP y SCADA quedan contemplados; API, MQTT y SNMP figuran como evolución en desarrollo.",
        "Evidencia desde matriz": f"{len(entel_monitoring_integration_df)} requisitos de integración valorizables.",
        "Prioridad de cierre": "Congelar protocolo principal, mapa de registros, ciberseguridad, red/APN/VPN y pruebas de interoperabilidad.",
    },
])

entel_req_exc_payload = load_entel_req_exc_from_url()
entel_req_exc_df = entel_req_exc_payload["df"].copy()
entel_req_exc_source = entel_req_exc_payload.get("source", "URL Google Sheets - Req.exc")
entel_introduction_payload = load_entel_introduction_from_url()
entel_introduction_title = entel_introduction_payload.get("title", "Introducción de la Propuesta Técnica")
entel_introduction_paragraphs = entel_introduction_payload.get("paragraphs", [])
entel_introduction_df = entel_introduction_payload.get("df", pd.DataFrame())
entel_introduction_source = entel_introduction_payload.get("source", "URL Google Sheets - Introducción")
entel_installation_conditions_payload = load_entel_installation_conditions_from_url()
entel_installation_conditions_source = entel_installation_conditions_payload.get("source", "URL Google Sheets - 5. Condiciones de Instalación")
entel_supplier_experience_payload = load_entel_supplier_experience_from_url()
entel_supplier_experience_title = entel_supplier_experience_payload.get("title", "6. EXPERIENCIA DEL PROVEEDOR")
entel_supplier_experience_subtitle = entel_supplier_experience_payload.get("subtitle", "")
entel_supplier_experience_source = entel_supplier_experience_payload.get("source", "URL Google Sheets - 6-Experiencia proveedor")
entel_supplier_experience_note = entel_supplier_experience_payload.get("note", "")

entel_proposal_7810_payload = load_entel_proposal_7810_from_url()
entel_proposal_7810_df = entel_proposal_7810_payload["df"].copy()
entel_proposal_7810_source = entel_proposal_7810_payload.get("source", "URL Google Sheets")
entel_proposal_section_names = {
    "5": "5. Condiciones de Instalación",
    "6": "6. Experiencia del Proveedor",
    "7": "7.- Garantias",
    "8": "8. Repuestos y Servicio Local",
    "9": "9. Importación y Logística",
    "10": "10. Documentación Técnica Requerida",
    "11": "11- Requisitos de Seguridad",
    "12": "12- ALCANCES, SALVEDADES Y EXCEPCIONES DE LA OFERTA TÉCNICA",
}
entel_proposal_7810_df["Sección RFP"] = entel_proposal_7810_df["Punto RFP"].map(entel_proposal_section_names).fillna(entel_proposal_7810_df["Punto RFP"])
entel_proposal_5_df = entel_proposal_7810_df[entel_proposal_7810_df["Punto RFP"] == "5"].copy()
entel_proposal_6_df = entel_proposal_7810_df[entel_proposal_7810_df["Punto RFP"] == "6"].copy()
entel_proposal_7_df = entel_proposal_7810_df[entel_proposal_7810_df["Punto RFP"] == "7"].copy()
entel_proposal_8_df = entel_proposal_7810_df[entel_proposal_7810_df["Punto RFP"] == "8"].copy()
entel_proposal_9_df = entel_proposal_7810_df[entel_proposal_7810_df["Punto RFP"] == "9"].copy()
entel_proposal_10_df = entel_proposal_7810_df[entel_proposal_7810_df["Punto RFP"] == "10"].copy()
entel_proposal_11_df = entel_proposal_7810_df[entel_proposal_7810_df["Punto RFP"] == "11"].copy()
entel_proposal_12_df = entel_proposal_7810_df[entel_proposal_7810_df["Punto RFP"] == "12"].copy()
entel_proposal_visible_cols = [
    "Subcapítulo", "Concepto", "Solicitud / recomendación RFP", "Respuesta incluida en oferta"
]
entel_proposal_5_display_df = entel_proposal_5_df[entel_proposal_visible_cols].copy()
entel_proposal_6_display_df = entel_proposal_6_df[entel_proposal_visible_cols].copy()
entel_proposal_7_display_df = entel_proposal_7_df[entel_proposal_visible_cols].copy()
entel_proposal_8_display_df = entel_proposal_8_df[entel_proposal_visible_cols].copy()
entel_proposal_9_display_df = entel_proposal_9_df[entel_proposal_visible_cols].copy()
entel_proposal_10_display_df = entel_proposal_10_df[entel_proposal_visible_cols].copy()
entel_proposal_11_display_df = entel_proposal_11_df[entel_proposal_visible_cols].copy()
entel_proposal_12_display_df = entel_proposal_12_df[entel_proposal_visible_cols].copy()
entel_proposal_7_concepts_df = entel_proposal_7_display_df[
    entel_proposal_7_display_df["Subcapítulo"] == "7.- Garantias - Conceptos incluidos"
].copy()
entel_proposal_7_rfp_df = entel_proposal_7_display_df[
    entel_proposal_7_display_df["Subcapítulo"] == "7.- Garantias - Recomendación / Solicitud RFP"
].copy()
entel_proposal_7_sla_df = entel_proposal_7_display_df[
    entel_proposal_7_display_df["Subcapítulo"] == "Garantía de Disponibilidad / SLA de soporte (Service Level Agreement) - Acuerdo de Nivel de Servicio"
].copy()
entel_proposal_7_other_df = entel_proposal_7_display_df[
    ~entel_proposal_7_display_df.index.isin(
        entel_proposal_7_concepts_df.index
        .union(entel_proposal_7_rfp_df.index)
        .union(entel_proposal_7_sla_df.index)
    )
].copy()
entel_proposal_table_cols = ["Concepto", "Solicitud / recomendación RFP", "Respuesta incluida en oferta"]
entel_proposal_concepts_cols = ["Concepto", "Respuesta incluida en oferta"]
entel_proposal_5_view_df = entel_proposal_5_display_df[entel_proposal_table_cols].copy()
if entel_proposal_5_view_df.empty:
    entel_proposal_5_view_df = (
        entel_delivery_df.loc[
            entel_delivery_df["Capítulo RFP"].eq("5 Instalación"),
            ["Entregable solicitado", "Evidencia en esta pestaña", "Estado", "Explicación técnica", "Acción propuesta"],
        ]
        .rename(columns={
            "Entregable solicitado": "Condición de instalación",
            "Evidencia en esta pestaña": "Evidencia técnica",
            "Explicación técnica": "Criterio de ingeniería",
        })
        .reset_index(drop=True)
    )
entel_proposal_5_view_df = entel_installation_conditions_payload.get("df", pd.DataFrame()).copy()
entel_proposal_6_view_df = entel_proposal_6_display_df[entel_proposal_table_cols].copy()
if entel_proposal_6_view_df.empty:
    entel_proposal_6_view_df = (
        entel_delivery_df.loc[
            entel_delivery_df["Capítulo RFP"].eq("6 Experiencia proveedor"),
            ["Entregable solicitado", "Evidencia en esta pestaña", "Estado", "Explicación técnica", "Acción propuesta"],
        ]
        .rename(columns={
            "Entregable solicitado": "Requisito de experiencia",
            "Evidencia en esta pestaña": "Evidencia técnica",
            "Explicación técnica": "Criterio de evaluación",
        })
        .reset_index(drop=True)
    )
entel_proposal_6_summary_df = (
    entel_proposal_6_display_df[
        entel_proposal_6_display_df["Subcapítulo"].eq("6.1 Síntesis de experiencia declarada")
    ][["Concepto", "Respuesta incluida en oferta"]]
    .rename(columns={"Concepto": "Eje de experiencia", "Respuesta incluida en oferta": "Evidencia declarada"})
    .reset_index(drop=True)
)
entel_proposal_6_stages_df = (
    entel_proposal_6_display_df[
        entel_proposal_6_display_df["Subcapítulo"].eq("6.2 Etapas de desarrollo tecnológico ejecutadas")
    ][["Concepto", "Solicitud / recomendación RFP", "Respuesta incluida en oferta"]]
    .rename(columns={
        "Concepto": "N°",
        "Solicitud / recomendación RFP": "Área técnica",
        "Respuesta incluida en oferta": "Etapa ejecutada",
    })
    .reset_index(drop=True)
)
entel_proposal_6_summary_df = entel_supplier_experience_payload.get("main", pd.DataFrame()).copy()
entel_proposal_6_documents_df = entel_supplier_experience_payload.get("documents", pd.DataFrame()).copy()
entel_proposal_6_areas_df = entel_supplier_experience_payload.get("areas", pd.DataFrame()).copy()
if entel_proposal_6_summary_df.empty:
    entel_proposal_6_summary_df = entel_proposal_6_view_df.copy()
if entel_proposal_6_documents_df.empty:
    entel_proposal_6_documents_df = pd.DataFrame()
if entel_proposal_6_areas_df.empty:
    entel_proposal_6_areas_df = pd.DataFrame()
entel_proposal_7_concepts_view_df = entel_proposal_7_concepts_df[entel_proposal_concepts_cols].copy()
entel_proposal_7_rfp_view_df = entel_proposal_7_rfp_df[entel_proposal_table_cols].copy()
entel_proposal_7_sla_view_df = entel_proposal_7_sla_df[entel_proposal_table_cols].copy()
entel_proposal_7_other_view_df = entel_proposal_7_other_df[entel_proposal_table_cols].copy()
entel_proposal_8_view_df = entel_proposal_8_display_df[entel_proposal_table_cols].copy()
entel_proposal_9_view_df = entel_proposal_9_display_df[["Concepto"]].rename(columns={"Concepto": "Declaración logística"}).copy()
entel_proposal_10_view_df = entel_proposal_10_display_df[entel_proposal_table_cols].copy()
entel_proposal_11_view_df = entel_proposal_11_display_df[entel_proposal_table_cols].rename(columns={
    "Concepto": "Categoría",
    "Solicitud / recomendación RFP": "Normativa / estándar",
    "Respuesta incluida en oferta": "Cumplimiento declarado",
}).copy()
entel_proposal_12_view_df = entel_proposal_12_display_df[entel_proposal_table_cols].rename(columns={
    "Concepto": "Tema / Categoría",
    "Solicitud / recomendación RFP": "Punto",
    "Respuesta incluida en oferta": "Alcance, Salvedad o Excepción",
}).copy()
entel_proposal_status_summary_df = (
    entel_proposal_7810_df.groupby(["Sección RFP", "Estado de postulación"], dropna=False)
    .size()
    .reset_index(name="Cantidad")
)
entel_proposal_point_summary_df = (
    entel_proposal_7810_df.groupby("Sección RFP", dropna=False)
    .agg(
        Requisitos=("Concepto", "count"),
        Incluidos=("Estado de postulación", lambda s: int(s.isin(["Confirmado", "Incluido", "Adjuntado / indicado"]).sum())),
        Posteriores=("Estado de postulación", lambda s: int((s == "Entrega posterior").sum())),
        Pendientes=("Estado de postulación", lambda s: int(s.isin(["Pendiente", "Brecha declarada", "Sin respuesta"]).sum())),
    )
    .reset_index()
)
entel_proposal_point_summary_df["Cobertura oferta [%]"] = (
    entel_proposal_point_summary_df["Incluidos"] / entel_proposal_point_summary_df["Requisitos"].replace(0, np.nan) * 100.0
)
entel_proposal_point_summary_df["Lectura de postulación"] = entel_proposal_point_summary_df["Sección RFP"].map({
    "7.- Garantias": "Prioriza confirmar cobertura contractual, respuesta remota/presencial y respaldo de garantías.",
    "8. Repuestos y Servicio Local": "Evidencia inventario crítico, soporte en Chile y brechas de mantenimiento recurrente.",
    "10. Documentación Técnica Requerida": "Separa anexos adjuntos, documentos posteriores y pendientes que deben cerrarse antes de oferta final.",
})
entel_proposal_status_fig = px.bar(
    entel_proposal_status_summary_df,
    x="Sección RFP",
    y="Cantidad",
    color="Estado de postulación",
    text="Cantidad",
    color_discrete_map=entel_color_map,
    title="Estado de respaldo de la propuesta por sección RFP",
)
entel_proposal_status_fig.update_traces(
    texttemplate="%{text}",
    textposition="inside",
    hovertemplate="<b>%{x}</b><br>Estado: %{fullData.name}<br>Ítems: %{y}<extra></extra>",
)
entel_proposal_status_fig.update_layout(
    xaxis_title="",
    yaxis_title="N° ítems",
    barmode="stack",
    legend_title=None,
)

entel_power_curve_df = entel_curve_df.copy()
entel_power_fig = go.Figure()
entel_power_series = [
    ("P_mec_gen (kW)", "Potencia mecánica [kW]", entel_color_map["Potencia mecánica [kW]"]),
    ("P_out (clip) kW", "Potencia eléctrica neta [kW]", entel_color_map["Potencia eléctrica neta [kW]"]),
]
for col_name, display_name, color in entel_power_series:
    if col_name not in entel_power_curve_df.columns:
        continue
    entel_power_fig.add_trace(go.Scatter(
        x=entel_power_curve_df["v (m/s)"],
        y=entel_power_curve_df[col_name],
        mode="lines+markers",
        name=display_name,
        line=dict(color=color, width=3),
        marker=dict(size=7, color=color, line=dict(width=1.2, color="#ffffff")),
        hovertemplate="Viento: %{x:.1f} m/s<br>" + display_name + ": %{y:.3f}<extra></extra>",
    ))
entel_power_fig.update_layout(title="Curva de potencia y pérdidas por etapa para anexo Entel")
entel_power_fig.update_layout(xaxis_title="Velocidad de viento [m/s]", yaxis_title="Potencia [kW]", legend_title=None)
for x_val, label in [(entel_v_cut_in, "cut-in"), (entel_v_rated, "nominal"), (entel_v_cut_out, "cut-out")]:
    if np.isfinite(x_val):
        entel_power_fig.add_vline(x=float(x_val), line_dash="dot", annotation_text=label)

entel_sens_fig = px.bar(
    entel_sensitivity_df,
    x="Caso",
    y="AEP [kWh/año]",
    text="Factor planta [%]",
    title="P50 técnico y sensibilidades solicitadas por Entel",
)
entel_sens_fig.update_traces(texttemplate="%{text:.1f}% FP", textposition="outside")
entel_sens_fig.update_layout(xaxis_title="", yaxis_title="AEP [kWh/año]")

entel_mean_fig = px.line(
    entel_mean_wind_df,
    x="Viento medio [m/s]",
    y="AEP estimado [kWh/año]",
    markers=True,
    title="Producción anual estimada para vientos medios 4 a 8 m/s",
)
entel_mean_fig.update_layout(yaxis_title="AEP [kWh/año]")

entel_month_plot_df = entel_monthly_df.copy()
entel_month_plot_df["Producción esperada [kWh/mes]"] = pd.to_numeric(
    entel_month_plot_df["Producción esperada [kWh/mes]"], errors="coerce"
)
entel_month_plot_df["Participación anual [%]"] = pd.to_numeric(
    entel_month_plot_df.get("Participación anual [%]", np.nan), errors="coerce"
)
monthly_avg_kwh = float(entel_month_plot_df["Producción esperada [kWh/mes]"].mean())
entel_month_plot_df["Delta vs promedio [kWh]"] = entel_month_plot_df["Producción esperada [kWh/mes]"] - monthly_avg_kwh
entel_month_plot_df["Acumulado [kWh]"] = entel_month_plot_df["Producción esperada [kWh/mes]"].cumsum()
entel_month_plot_df["Color"] = np.where(entel_month_plot_df["Delta vs promedio [kWh]"] >= 0, entel_color_map["Producción mensual"], "#d9a766")
entel_month_fig = go.Figure()
entel_month_fig.add_trace(go.Bar(
    x=entel_month_plot_df["Mes"],
    y=entel_month_plot_df["Producción esperada [kWh/mes]"],
    name="Producción mensual",
    marker_color=entel_month_plot_df["Color"],
    text=entel_month_plot_df["Producción esperada [kWh/mes]"],
    texttemplate="%{text:,.0f}",
    textposition="outside",
    cliponaxis=False,
    customdata=np.stack([
        entel_month_plot_df["Participación anual [%]"].fillna(0.0),
        entel_month_plot_df["Delta vs promedio [kWh]"].fillna(0.0),
        entel_month_plot_df["Acumulado [kWh]"].fillna(0.0),
    ], axis=-1),
    hovertemplate=(
        "<b>%{x}</b><br>"
        "Producción: %{y:,.1f} kWh/mes<br>"
        "Participación anual: %{customdata[0]:.2f}%<br>"
        "Delta vs promedio: %{customdata[1]:+,.1f} kWh<br>"
        "Acumulado anual: %{customdata[2]:,.1f} kWh"
        "<extra></extra>"
    ),
))
entel_month_fig.add_trace(go.Scatter(
    x=entel_month_plot_df["Mes"],
    y=entel_month_plot_df["Acumulado [kWh]"],
    name="Acumulado",
    mode="lines+markers",
    yaxis="y2",
    line=dict(color=entel_color_map["Acumulado"], width=3, shape="spline"),
    marker=dict(size=8, color=entel_color_map["Acumulado"], line=dict(width=1.2, color="#ffffff")),
    hovertemplate="<b>%{x}</b><br>Acumulado: %{y:,.1f} kWh<extra></extra>",
))
entel_month_fig.add_hline(
    y=monthly_avg_kwh,
    line_dash="dot",
    line_color="rgba(79,90,105,0.70)",
    annotation_text=f"Promedio {entel_int_es(monthly_avg_kwh)} kWh/mes",
    annotation_font_size=11,
    annotation_font_color="#4f5a69",
)
entel_month_fig.update_layout(
    title="Producción mensual esperada y acumulado anual",
    xaxis_title="",
    yaxis=dict(title="kWh/mes"),
    yaxis2=dict(title="Acumulado [kWh]", overlaying="y", side="right", rangemode="tozero"),
    legend_title=None,
)

entel_availability = 0.95

def entel_annual_kwh_from_col(col_name: str) -> float:
    if col_name not in entel_curve_df.columns:
        return np.nan
    p_kw = pd.to_numeric(entel_curve_df[col_name], errors="coerce").fillna(0.0).to_numpy(dtype=float)
    v_col = pd.to_numeric(entel_curve_df["v (m/s)"], errors="coerce").fillna(0.0).to_numpy(dtype=float)
    p_w = np.interp(v_w_entel_base, v_col, p_kw * 1000.0, left=0.0, right=0.0)
    p_w[v_w_entel_base < entel_v_cut_in] = 0.0
    p_w[v_w_entel_base > entel_v_cut_out] = 0.0
    aep_col, _ = aep_from_weibull(v_w_entel_base, p_w, k_energy, c_energy)
    return aep_col

aep_aero_kwh = entel_annual_kwh_from_col("P_aero (kW)")
aep_mec_kwh = entel_annual_kwh_from_col("P_mec_gen (kW)")
aep_elec_kwh = entel_annual_kwh_from_col("P_el (kW)")
aep_net_kwh = entel_annual_kwh_from_col("P_out (clip) kW")
p_avg_kw = entel_AEP_kWh / 8760.0 if np.isfinite(entel_AEP_kWh) else np.nan
equivalent_hours = entel_AEP_kWh / entel_p_nom_kw if entel_p_nom_kw > 0 else np.nan
aep_with_availability = entel_AEP_kWh * entel_availability if np.isfinite(entel_AEP_kWh) else np.nan

entel_performance_kpi_df = pd.DataFrame([
    {"Indicador": "Producción energética anual esperada", "Valor": entel_AEP_kWh, "Unidad": "kWh/año", "Criterio técnico del oferente": f"AEP P50 técnico antes de disponibilidad; curva usada: {entel_curve_source}."},
    {"Indicador": "Producción anual con disponibilidad considerada", "Valor": aep_with_availability, "Unidad": "kWh/año", "Criterio técnico del oferente": "AEP neto aplicando disponibilidad mínima RFP de 95%."},
    {"Indicador": "Potencia promedio generada", "Valor": p_avg_kw, "Unidad": "kW", "Criterio técnico del oferente": "Potencia media equivalente sobre 8.760 h/año."},
    {"Indicador": "Horas equivalentes de operación", "Valor": equivalent_hours, "Unidad": "h/año", "Criterio técnico del oferente": "AEP dividido por potencia nominal AC declarada en curva Entel."},
    {"Indicador": "Factor de planta esperado", "Valor": entel_CF * 100, "Unidad": "%", "Criterio técnico del oferente": "Relación entre potencia media y potencia nominal de la curva Entel."},
    {"Indicador": "Disponibilidad considerada", "Valor": entel_availability * 100, "Unidad": "%", "Criterio técnico del oferente": "Supuesto mínimo indicado por RFP Entel."},
])

entel_losses_df = pd.DataFrame([
    {"Etapa": "Aerodinámica bruta", "Energía anual [kWh/año]": aep_aero_kwh, "Pérdida aplicada [kWh/año]": 0.0, "Explicación": "Energía disponible desde la curva aerodinámica base antes del tren de potencia."},
    {"Etapa": "Pérdidas mecánicas", "Energía anual [kWh/año]": aep_mec_kwh, "Pérdida aplicada [kWh/año]": max(aep_aero_kwh - aep_mec_kwh, 0.0) if np.isfinite(aep_aero_kwh) and np.isfinite(aep_mec_kwh) else np.nan, "Explicación": "Diferencia entre potencia aerodinámica y potencia mecánica en generador."},
    {"Etapa": "Pérdidas eléctricas", "Energía anual [kWh/año]": aep_elec_kwh, "Pérdida aplicada [kWh/año]": max(aep_mec_kwh - aep_elec_kwh, 0.0) if np.isfinite(aep_mec_kwh) and np.isfinite(aep_elec_kwh) else np.nan, "Explicación": "Pérdidas de generador, rectificación e inversión modeladas."},
    {"Etapa": "Clipping / limitación", "Energía anual [kWh/año]": aep_net_kwh, "Pérdida aplicada [kWh/año]": max(aep_elec_kwh - aep_net_kwh, 0.0) if np.isfinite(aep_elec_kwh) and np.isfinite(aep_net_kwh) else np.nan, "Explicación": "Energía no inyectada por límite de potencia nominal o control."},
    {"Etapa": "Disponibilidad", "Energía anual [kWh/año]": aep_with_availability, "Pérdida aplicada [kWh/año]": entel_AEP_kWh * (1.0 - entel_availability) if np.isfinite(entel_AEP_kWh) else np.nan, "Explicación": "Corrección contractual por disponibilidad anual considerada."},
])
base_loss = aep_aero_kwh if np.isfinite(aep_aero_kwh) and aep_aero_kwh > 0 else np.nan
entel_losses_df["Pérdida sobre aero [%]"] = entel_losses_df["Pérdida aplicada [kWh/año]"] / base_loss * 100.0

entel_yield_site_df = pd.DataFrame([
    {"Ítem solicitado 3.2": "Distribución de velocidades de viento", "Estado en app": "Calculada desde recurso activo", "Valor / evidencia": f"Weibull k={entel_num_es(k_energy, 2)}, c={entel_num_es(c_energy, 2)} m/s", "Criterio técnico del oferente": "La distribución se integra contra la curva de potencia para obtener AEP y factor de planta."},
    {"Ítem solicitado 3.2": "Coordenadas del sitio", "Estado en app": "Por completar con estudio mandante", "Valor / evidencia": "Latitud / longitud no declaradas en el archivo cargado", "Criterio técnico del oferente": "Debe incorporarse la coordenada oficial Entel para trazabilidad de rugosidad, exposición, densidad y restricciones del emplazamiento."},
    {"Ítem solicitado 3.2": "Altura de instalación considerada", "Estado en app": "Fija desde oferta Entel", "Valor / evidencia": entel_num_es(entel_installation_height_m, 1, " m"), "Criterio técnico del oferente": f"Altura total de instalación con mástil de {entel_num_es(entel_mast_height_m, 1)} m; para área barrida se usa H rotor={entel_num_es(entel_H_m, 1)} m y D={entel_num_es(entel_D_m, 1)} m."},
    {"Ítem solicitado 3.2": "Estudio de recurso eólico", "Estado en app": resource_origin, "Valor / evidencia": resource_origin if use_extrapolated_resource else "Parámetros Weibull manuales", "Criterio técnico del oferente": "Si Entel entrega serie o matriz por alturas, la app extrapola a la altura efectiva antes de calcular la producción."},
])

entel_yield_methodology_df = pd.DataFrame([
    {"Paso metodológico": "1. Normalización del recurso", "Aplicación en esta propuesta": f"Se usa el recurso activo del panel lateral o {scada_source_label} cuando queda como perfil vertical cargado.", "Salida verificable": "Weibull k/c, velocidad media y altura de recurso."},
    {"Paso metodológico": "2. Ajuste / extrapolación vertical", "Aplicación en esta propuesta": "Cuando hay columnas por altura, se ajusta ley de potencia por timestamp y se estima viento a la altura de instalación.", "Salida verificable": "Altura objetivo, alpha vertical medio/mediano y registros válidos."},
    {"Paso metodológico": "3. Curva de potencia", "Aplicación en esta propuesta": f"La curva P_out (clip) kW se integra por bin de velocidad usando {entel_curve_source}.", "Salida verificable": "Tabla de curva por bin y gráfico potencia-viento."},
    {"Paso metodológico": "4. Energy Yield Assessment", "Aplicación en esta propuesta": "Integración de distribución Weibull activa contra la curva de potencia neta.", "Salida verificable": "AEP P50 técnico, potencia promedio, horas equivalentes y factor de planta."},
    {"Paso metodológico": "5. Sensibilidades", "Aplicación en esta propuesta": "Se calculan escenarios para disponibilidad, pérdidas eléctricas, incertidumbre de recurso y degradación.", "Salida verificable": "Tabla y gráfico de P50 + sensibilidades."},
    {"Paso metodológico": "6. Pérdidas y turbulencia", "Aplicación en esta propuesta": "Las pérdidas se separan por etapa; la turbulencia se declara como criterio de revisión y proxy de variabilidad cuando existe serie temporal.", "Salida verificable": "Matriz de pérdidas y consideraciones de turbulencia."},
])

entel_distribution_grid = np.linspace(0.01, entel_v_max_plot, 900)
entel_distribution_pdf = weibull_pdf(entel_distribution_grid, k_energy, c_energy)
entel_distribution_power_kw = np.interp(
    entel_distribution_grid,
    v_curve,
    p_curve_kw,
    left=0.0,
    right=0.0,
) if len(v_curve) and len(p_curve_kw) else np.zeros_like(entel_distribution_grid)
entel_distribution_power_kw[entel_distribution_grid < entel_v_cut_in] = 0.0
entel_distribution_power_kw[entel_distribution_grid > entel_v_cut_out] = 0.0

entel_speed_edges = [0, 3, 4, 5, 6, 7, 8, 10, 12, 15, float(entel_v_max_plot)]
entel_distribution_rows = []
for lower, upper in zip(entel_speed_edges[:-1], entel_speed_edges[1:]):
    mask = (entel_distribution_grid >= lower) & (entel_distribution_grid < upper)
    if not np.any(mask):
        probability = 0.0
        energy_bin = 0.0
        p_bin = 0.0
    else:
        probability = float(np.trapz(entel_distribution_pdf[mask], entel_distribution_grid[mask]))
        energy_bin = float(np.trapz(entel_distribution_power_kw[mask] * entel_distribution_pdf[mask], entel_distribution_grid[mask]) * 8760.0)
        p_bin = energy_bin / (probability * 8760.0) if probability > 0 else 0.0
    entel_distribution_rows.append({
        "Bin viento [m/s]": f"{lower:.0f}-{upper:.0f}",
        "Probabilidad [%]": probability * 100.0,
        "Horas/año": probability * 8760.0,
        "Potencia media bin [kW]": p_bin,
        "Energía bin [kWh/año]": energy_bin,
        "Estado operativo del bin": "Bajo cut-in" if upper <= entel_v_cut_in else ("Zona productiva" if lower < entel_v_cut_out else "Fuera de operación"),
    })
entel_wind_distribution_df = pd.DataFrame(entel_distribution_rows)

entel_yield_assessment_df = pd.DataFrame([
    {"Indicador EYA 3.2": "AEP P50 técnico", "Valor": entel_AEP_kWh, "Unidad": "kWh/año", "Base técnica verificable": f"Distribución Weibull activa x curva de potencia neta ({entel_curve_source})."},
    {"Indicador EYA 3.2": "AEP P50 con disponibilidad 95%", "Valor": aep_with_availability, "Unidad": "kWh/año", "Base técnica verificable": "AEP P50 técnico corregido por disponibilidad contractual."},
    {"Indicador EYA 3.2": "Potencia promedio neta", "Valor": p_avg_kw, "Unidad": "kW", "Base técnica verificable": "AEP / 8.760 h."},
    {"Indicador EYA 3.2": "Horas equivalentes", "Valor": equivalent_hours, "Unidad": "h/año", "Base técnica verificable": "AEP / potencia nominal de la curva Entel."},
    {"Indicador EYA 3.2": "Factor de planta P50", "Valor": entel_CF * 100, "Unidad": "%", "Base técnica verificable": "Potencia media / potencia nominal de la curva Entel."},
    {"Indicador EYA 3.2": "Velocidad media Weibull", "Valor": c_energy * gamma(1.0 + 1.0 / max(float(k_energy), 0.1)), "Unidad": "m/s", "Base técnica verificable": "Media de la distribución estadística activa."},
])

entel_yield_sensitivity_df = pd.DataFrame([
    {"Familia": "Base", "Caso": "P50 técnico esperado", "Ajuste aplicado": "Sin castigo adicional", "AEP [kWh/año]": entel_AEP_kWh, "Factor planta [%]": entel_CF * 100, "Uso en evaluación": "Caso central de comparación técnica."},
    {"Familia": "Disponibilidad", "Caso": "Disponibilidad 95%", "Ajuste aplicado": "-5,0% energía", "AEP [kWh/año]": entel_AEP_kWh * 0.95, "Factor planta [%]": entel_CF * 95, "Uso en evaluación": "Disponibilidad mínima exigida por RFP."},
    {"Familia": "Pérdidas eléctricas", "Caso": "Pérdida eléctrica adicional", "Ajuste aplicado": "-3,0% energía", "AEP [kWh/año]": entel_AEP_kWh * 0.97, "Factor planta [%]": entel_CF * 97, "Uso en evaluación": "Margen para inversor, cableado, rectificación y calidad eléctrica."},
    {"Familia": "Incertidumbre recurso", "Caso": "Recurso bajo P50", "Ajuste aplicado": "-10,0% energía", "AEP [kWh/año]": entel_AEP_kWh * 0.90, "Factor planta [%]": entel_CF * 90, "Uso en evaluación": "Sensibilidad por medición, extrapolación, rugosidad y representatividad temporal."},
    {"Familia": "Incertidumbre recurso", "Caso": "Recurso alto P50", "Ajuste aplicado": "+10,0% energía", "AEP [kWh/año]": entel_AEP_kWh * 1.10, "Factor planta [%]": entel_CF * 110, "Uso en evaluación": "Escenario superior para comparar upside técnico."},
    {"Familia": "Degradación", "Caso": "Año 1 degradado", "Ajuste aplicado": "-0,5% energía", "AEP [kWh/año]": entel_AEP_kWh * 0.995, "Factor planta [%]": entel_CF * 99.5, "Uso en evaluación": "Sensibilidad por envejecimiento inicial de rotor, generador y electrónica."},
    {"Familia": "Combinado conservador", "Caso": "Disponibilidad + pérdidas + degradación", "Ajuste aplicado": "95% x 97% x 99,5%", "AEP [kWh/año]": entel_AEP_kWh * 0.95 * 0.97 * 0.995, "Factor planta [%]": entel_CF * 95 * 0.97 * 0.995, "Uso en evaluación": "Caso de estrés para revisión contractual."},
])

turbulence_proxy = (
    float(active_resource_inputs.get("v_std", np.nan)) / float(active_resource_inputs.get("v_mean", np.nan)) * 100.0
    if use_extrapolated_resource and float(active_resource_inputs.get("v_mean", np.nan)) > 0
    else np.nan
)
entel_turbulence_losses_df = pd.DataFrame([
    {"Aspecto solicitado": "Consideración de turbulencia", "Tratamiento en esta versión": f"Declaración técnica + proxy de variabilidad temporal si existe {scada_source_label}", "Valor / criterio": f"{entel_num_es(turbulence_proxy, 1)}% proxy σ/μ" if np.isfinite(turbulence_proxy) else "Requiere TI o serie de alta frecuencia del estudio mandante", "Impacto en EYA": "Puede reducir producción efectiva y aumentar cargas/fatiga; debe validarse con IEC/sitio."},
    {"Aspecto solicitado": "Pérdidas mecánicas", "Tratamiento en esta versión": "Eficiencias de rodamientos, caja/transmisión y tren mecánico", "Valor / criterio": f"η_mec={entel_num_es(eta_mec, 3)}; η_rodamientos={entel_num_es(eta_bear, 3)}; η_caja={entel_num_es(eta_gear, 3)}", "Impacto en EYA": "Castigan la energía entre rotor y generador."},
    {"Aspecto solicitado": "Pérdidas eléctricas", "Tratamiento en esta versión": "Eficiencia electrónica/inversor y curva de generador", "Valor / criterio": f"η_elec={entel_num_es(eta_elec, 3)}", "Impacto en EYA": "Castigan salida útil AC/DC y definen sensibilidad eléctrica."},
    {"Aspecto solicitado": "Clipping / control", "Tratamiento en esta versión": "Limitación por potencia nominal y ventana cut-in/cut-out", "Valor / criterio": f"P_nom={entel_num_es(entel_p_nom_kw, 1)} kW; cut-in={entel_num_es(entel_v_cut_in, 1)}; cut-out={entel_num_es(entel_v_cut_out, 1)} m/s", "Impacto en EYA": "Evita sobrepotencia pero reduce energía en vientos altos."},
    {"Aspecto solicitado": "Disponibilidad", "Tratamiento en esta versión": "Disponibilidad mínima RFP", "Valor / criterio": f"{entel_num_es(entel_availability * 100, 1)}%", "Impacto en EYA": "Transforma P50 técnico en P50 neto disponible."},
])

entel_wind_distribution_plot_df = entel_wind_distribution_df.copy()
entel_wind_distribution_plot_df["Bin viento [m/s]"] = (
    entel_wind_distribution_plot_df["Bin viento [m/s]"]
    .astype(str)
    .str.replace("-", " a ", regex=False)
)
entel_wind_distribution_fig = make_subplots(
    rows=2,
    cols=1,
    shared_xaxes=True,
    vertical_spacing=0.16,
    subplot_titles=("Frecuencia anual del viento por bin", "Energía anual aportada por bin"),
)
entel_wind_distribution_fig.add_trace(
    go.Bar(
        x=entel_wind_distribution_plot_df["Bin viento [m/s]"],
        y=entel_wind_distribution_plot_df["Horas/año"],
        name="Horas/año",
        marker_color="#2f5f73",
        text=entel_wind_distribution_plot_df["Probabilidad [%]"],
        texttemplate="%{text:.1f}%",
        textposition="outside",
        cliponaxis=False,
        hovertemplate="Bin %{x} m/s<br>Horas: %{y:,.0f}<br>Probabilidad: %{text:.2f}%<extra></extra>",
    ),
    row=1,
    col=1,
)
entel_wind_distribution_fig.add_trace(
    go.Bar(
        x=entel_wind_distribution_plot_df["Bin viento [m/s]"],
        y=entel_wind_distribution_plot_df["Energía bin [kWh/año]"],
        name="Energía bin",
        marker_color="#c47a3c",
        text=entel_wind_distribution_plot_df["Potencia media bin [kW]"],
        texttemplate="%{text:.2f} kW",
        textposition="outside",
        cliponaxis=False,
        hovertemplate="Bin %{x} m/s<br>Energía: %{y:,.0f} kWh/año<br>Potencia media bin: %{text:.3f} kW<extra></extra>",
    ),
    row=2,
    col=1,
)
entel_wind_distribution_fig.update_layout(
    title="Distribución estadística del viento y contribución energética por bin",
    xaxis2_title="Bin de velocidad [m/s]",
    yaxis=dict(title="Horas/año"),
    yaxis2=dict(title="kWh/año"),
    legend_title=None,
    height=640,
    bargap=0.24,
)
entel_wind_distribution_fig.update_xaxes(type="category", tickangle=0)

entel_yield_sensitivity_fig = px.bar(
    entel_yield_sensitivity_df,
    x="Caso",
    y="AEP [kWh/año]",
    color="Familia",
    color_discrete_map=entel_color_map,
    text="Factor planta [%]",
    title="EYA 3.2: P50 técnico y sensibilidades de factor de planta",
)
entel_yield_sensitivity_fig.update_traces(texttemplate="%{text:.1f}% FP", textposition="outside", cliponaxis=False)
entel_yield_sensitivity_fig.update_layout(xaxis_title="", yaxis_title="AEP [kWh/año]", legend_title=None)

entel_assumptions_df = pd.DataFrame([
    {"Supuesto requerido RFP": "Curva de potencia utilizada", "Valor declarado": entel_curve_source, "Criterio técnico del oferente": f"Fuente usada para cálculos Entel: {entel_curve_source_detail}"},
    {"Supuesto requerido RFP": "Altura de instalación considerada", "Valor declarado": entel_num_es(entel_installation_height_m, 1, " m"), "Criterio técnico del oferente": f"Altura de instalación Entel independiente del panel. Área barrida calculada con D={entel_num_es(entel_D_m, 1)} m y H rotor={entel_num_es(entel_H_m, 1)} m."},
    {"Supuesto requerido RFP": "Factores de corrección", "Valor declarado": f"Densidad {entel_num_es(rho, 3)} kg/m³, Weibull k={entel_num_es(k_energy, 2)}, c={entel_num_es(c_energy, 2)} m/s", "Criterio técnico del oferente": "Incluye recurso activo y condiciones configuradas para la evaluación de producción."},
    {"Supuesto requerido RFP": "Pérdidas eléctricas", "Valor declarado": f"η_elec={entel_num_es(eta_elec, 3)}", "Criterio técnico del oferente": "Incluye electrónica de conversión según modelo actual."},
    {"Supuesto requerido RFP": "Pérdidas mecánicas", "Valor declarado": f"η_mec={entel_num_es(eta_mec, 3)}; η_rodamientos={entel_num_es(eta_bear, 3)}; η_caja={entel_num_es(eta_gear, 3)}", "Criterio técnico del oferente": "Pérdidas de transmisión desde rotor hacia generador."},
    {"Supuesto requerido RFP": "Pérdidas por disponibilidad", "Valor declarado": f"{entel_num_es((1.0 - entel_availability) * 100, 1)}% de indisponibilidad", "Criterio técnico del oferente": "Se aplica disponibilidad considerada de 95%."},
])

entel_performance_curve_df = entel_curve_df[[
    col for col in [
        "v (m/s)", "P_aero (kW)", "P_mec_gen (kW)", "P_el (kW)", "P_out (clip) kW",
        "Cp_el_equiv", "rpm_rotor", "rpm_gen", "I_est (A)", "Estado curva URL"
    ]
    if col in entel_curve_df.columns
]].copy()

loss_mechanical = max(aep_aero_kwh - aep_mec_kwh, 0.0) if np.isfinite(aep_aero_kwh) and np.isfinite(aep_mec_kwh) else 0.0
loss_electrical = max(aep_mec_kwh - aep_elec_kwh, 0.0) if np.isfinite(aep_mec_kwh) and np.isfinite(aep_elec_kwh) else 0.0
loss_clipping = max(aep_elec_kwh - aep_net_kwh, 0.0) if np.isfinite(aep_elec_kwh) and np.isfinite(aep_net_kwh) else 0.0
loss_availability = entel_AEP_kWh * (1.0 - entel_availability) if np.isfinite(entel_AEP_kWh) else 0.0
waterfall_values = [
    aep_aero_kwh,
    -loss_mechanical,
    -loss_electrical,
    -loss_clipping,
    -loss_availability,
    0,
]
waterfall_labels = [
    "Energía bruta",
    "Pérdida mecánica",
    "Pérdida eléctrica",
    "Clipping",
    "Disponibilidad",
    "Energía neta",
]
waterfall_custom = np.array([
    [aep_aero_kwh, 0.0],
    [aep_mec_kwh, loss_mechanical],
    [aep_elec_kwh, loss_electrical],
    [aep_net_kwh, loss_clipping],
    [aep_with_availability, loss_availability],
    [aep_with_availability, 0.0],
], dtype=float)
waterfall_text = [
    entel_int_es(aep_aero_kwh, " kWh"),
    f"-{entel_int_es(loss_mechanical, ' kWh')}",
    f"-{entel_int_es(loss_electrical, ' kWh')}",
    f"-{entel_int_es(loss_clipping, ' kWh')}",
    f"-{entel_int_es(loss_availability, ' kWh')}",
    entel_int_es(aep_with_availability, " kWh"),
]
waterfall_max = max(
    [
        value
        for value in [aep_aero_kwh, aep_mec_kwh, aep_elec_kwh, aep_net_kwh, aep_with_availability]
        if np.isfinite(value)
    ] or [1.0]
)
entel_energy_waterfall_fig = go.Figure(go.Waterfall(
    name="Balance energético",
    orientation="v",
    measure=["absolute", "relative", "relative", "relative", "relative", "total"],
    x=waterfall_labels,
    y=waterfall_values,
    text=waterfall_text,
    textposition="outside",
    textfont=dict(size=13, color="#1f2a3a"),
    cliponaxis=False,
    customdata=waterfall_custom,
    decreasing={"marker": {"color": entel_color_map["Pérdida"]}},
    increasing={"marker": {"color": entel_color_map["Potencia aerodinámica [kW]"]}},
    totals={"marker": {"color": entel_color_map["Energía neta"]}},
    connector={"line": {"color": "rgba(79,90,105,0.50)", "width": 1.5}},
    hovertemplate=(
        "<b>%{x}</b><br>"
        "Movimiento: %{y:,.1f} kWh/año<br>"
        "Energía después de etapa: %{customdata[0]:,.1f} kWh/año<br>"
        "Pérdida etapa: %{customdata[1]:,.1f} kWh/año"
        "<extra></extra>"
    ),
))
entel_energy_waterfall_fig.update_layout(
    title="Balance anual de energía: desde recurso bruto hasta energía neta disponible",
    yaxis_title="kWh/año",
    showlegend=False,
    height=520,
    bargap=0.28,
    hoverlabel=dict(bgcolor="#ffffff", bordercolor="#d7dee8", font_size=13, font_color="#1f2a3a"),
)
entel_energy_waterfall_fig.update_yaxes(range=[0, waterfall_max * 1.22], tickformat=",.0f")
entel_energy_waterfall_fig.update_xaxes(tickangle=0, automargin=True)

entel_cp_fig = px.line(
    entel_performance_curve_df,
    x="v (m/s)",
    y=[col for col in ["P_out (clip) kW", "Cp_el_equiv"] if col in entel_performance_curve_df.columns],
    color_discrete_map=entel_color_map,
    markers=True,
    title="Curva certificable usada en simulación: potencia neta y Cp equivalente",
)
entel_cp_fig.update_layout(xaxis_title="Velocidad de viento [m/s]", yaxis_title="Valor", legend_title=None)

entel_aero_operating_df = pd.DataFrame([
    {"Parámetro solicitado": "Velocidad de arranque (cut-in)", "Valor": entel_v_cut_in, "Unidad": "m/s", "Criterio técnico del oferente": "Inicio de producción útil; bajo cut-in la turbina permanece disponible sin inyección."},
    {"Parámetro solicitado": "Velocidad nominal", "Valor": entel_v_rated, "Unidad": "m/s", "Criterio técnico del oferente": "Punto de transición hacia potencia limitada y control de carga."},
    {"Parámetro solicitado": "Velocidad máxima de operación", "Valor": entel_v_cut_out, "Unidad": "m/s", "Criterio técnico del oferente": "Límite operativo previo a estrategia de parada segura según curva URL."},
    {"Parámetro solicitado": "Velocidad de corte (cut-out)", "Valor": entel_v_cut_out, "Unidad": "m/s", "Criterio técnico del oferente": "Sobre este umbral no se considera producción y debe dominar protección estructural."},
    {"Parámetro solicitado": "Cp máximo eléctrico equivalente", "Valor": float(np.nanmax(entel_curve_df["Cp_el_equiv"])) if "Cp_el_equiv" in entel_curve_df.columns else np.nan, "Unidad": "-", "Criterio técnico del oferente": "Eficiencia global viento a salida AC; revisar que no se logre a costa de sobrecarga."},
    {"Parámetro solicitado": "Cp a velocidad nominal", "Valor": float(np.interp(entel_v_rated, entel_curve_df["v (m/s)"], entel_curve_df["Cp_el_equiv"])) if "Cp_el_equiv" in entel_curve_df.columns else np.nan, "Unidad": "-", "Criterio técnico del oferente": "Eficiencia esperada en el punto de diseño declarado."},
    {"Parámetro solicitado": "Potencia neta a velocidad nominal", "Valor": float(np.interp(entel_v_rated, entel_curve_df["v (m/s)"], entel_curve_df["P_out (clip) kW"])) if "P_out (clip) kW" in entel_curve_df.columns else np.nan, "Unidad": "kW", "Criterio técnico del oferente": "Debe ser consistente con la potencia nominal ofertada y la curva certificada."},
])

entel_aero_curve_df = entel_curve_df[[
    col for col in [
        "v (m/s)", "P_out (clip) kW", "P_aero (kW)", "Cp(λ_efectiva)", "Cp_aero_equiv",
        "Cp_el_equiv", "λ_efectiva", "U_tip (m/s)", "rpm_rotor", "a_cen (g)",
        "f_1P (Hz)", "f_3P (Hz)", "Lw (dB)", "Lp_obs (dB)", "Estado curva URL"
    ]
    if col in entel_curve_df.columns
]].copy()

entel_aero_stability_df = pd.DataFrame([
    {"Criterio valorado": "Bajo nivel de vibración", "Indicador usado": "Frecuencias 1P/3P, aceleración centrípeta y rpm", "Resultado modelo": f"f_1P máx {entel_num_es(np.nanmax(df['f_1P (Hz)']), 2)} Hz; f_3P máx {entel_num_es(np.nanmax(df['f_3P (Hz)']), 2)} Hz" if "f_1P (Hz)" in df.columns and "f_3P (Hz)" in df.columns else "No disponible", "Criterio técnico del oferente": "Cruzar estas bandas con modos propios de mástil, struts y fundación antes de liberar fabricación."},
    {"Criterio valorado": "Bajo nivel de ruido", "Indicador usado": "Lp_obs y velocidad de punta", "Resultado modelo": f"Lp_obs máx {entel_num_es(np.nanmax(df['Lp_obs (dB)']), 1)} dB; U_tip máx {entel_num_es(np.nanmax(df['U_tip (m/s)']), 1)} m/s" if "Lp_obs (dB)" in df.columns and "U_tip (m/s)" in df.columns else "No disponible", "Criterio técnico del oferente": "La aceptabilidad depende de distancia al receptor y norma/criterio acústico del sitio."},
    {"Criterio valorado": "Operación estable urbana/semiurbana", "Indicador usado": "Cut-in bajo, control de rpm, potencia limitada y margen de cut-out", "Resultado modelo": f"Ventana útil {entel_num_es(entel_v_cut_in, 1)}-{entel_num_es(entel_v_cut_out, 1)} m/s; rated {entel_num_es(entel_v_rated, 1)} m/s", "Criterio técnico del oferente": "La curva debe subir de forma progresiva y limitar potencia sin saltos abruptos de rpm o corriente."},
])

entel_aero_power_fig = px.line(
    entel_aero_curve_df,
    x="v (m/s)",
    y=[col for col in ["P_out (clip) kW", "P_aero (kW)"] if col in entel_aero_curve_df.columns],
    color_discrete_map=entel_color_map,
    markers=True,
    title="Desempeño aerodinámico: curva de potencia ofertada",
)
entel_aero_power_fig.update_layout(xaxis_title="Velocidad de viento [m/s]", yaxis_title="Potencia [kW]", legend_title=None)
for x_val, label in [(entel_v_cut_in, "cut-in"), (entel_v_rated, "nominal"), (entel_v_cut_out, "cut-out")]:
    if np.isfinite(x_val):
        entel_aero_power_fig.add_vline(x=float(x_val), line_dash="dot", annotation_text=label)

entel_aero_cp_fig = px.line(
    entel_aero_curve_df,
    x="v (m/s)",
    y=[col for col in ["Cp(λ_efectiva)", "Cp_aero_equiv", "Cp_el_equiv"] if col in entel_aero_curve_df.columns],
    color_discrete_map=entel_color_map,
    markers=True,
    title="Coeficiente de potencia Cp por velocidad de viento",
)
entel_aero_cp_fig.update_layout(xaxis_title="Velocidad de viento [m/s]", yaxis_title="Cp [-]", legend_title=None)

entel_aero_energy_fig = px.bar(
    entel_mean_wind_df,
    x="Viento medio [m/s]",
    y="AEP estimado [kWh/año]",
    color_discrete_sequence=[entel_color_map["Energía bin"]],
    text="Factor planta [%]",
    title="Producción anual estimada para 4, 5, 6, 7 y 8 m/s",
)
entel_aero_energy_fig.update_traces(texttemplate="%{text:.1f}% FP", textposition="outside")
entel_aero_energy_fig.update_layout(xaxis_title="Viento medio [m/s]", yaxis_title="AEP [kWh/año]")

entel_aero_stability_fig = px.line(
    entel_aero_curve_df,
    x="v (m/s)",
    y=[col for col in ["U_tip (m/s)", "f_1P (Hz)", "f_3P (Hz)", "Lp_obs (dB)"] if col in entel_aero_curve_df.columns],
    color_discrete_map=entel_color_map,
    markers=True,
    title="Indicadores de ruido, vibración y estabilidad operativa",
)
entel_aero_stability_fig.update_layout(xaxis_title="Velocidad de viento [m/s]", yaxis_title="Indicador", legend_title=None)

entel_electrical_specs_df = pd.DataFrame([
    {"Requisito Entel": "Tensión nominal de salida", "Valor declarado": f"{entel_int_es(GEN['V_LL_nom'])} Vac L-L" if "GEN" in globals() else "A definir", "Base técnica verificable": "Ficha del generador seleccionado y curva V_LL vs rpm", "Criterio técnico del oferente": "Debe coordinarse con rectificador/inversor, protecciones y tensión de acoplamiento del sitio."},
    {"Requisito Entel": "Frecuencia", "Valor declarado": "50 Hz en salida AC del inversor; frecuencia eléctrica variable en generador", "Base técnica verificable": f"f_e máx modelo {entel_num_es(np.nanmax(df['f_e (Hz)']), 1)} Hz" if "f_e (Hz)" in df.columns else "Modelo eléctrico", "Criterio técnico del oferente": "El inversor desacopla la frecuencia variable del generador de la frecuencia AC del sitio."},
    {"Requisito Entel": "Tipo de inversor", "Valor declarado": "Inversor eólico/híbrido con rectificación, MPPT, anti-isla y comunicación SCADA", "Base técnica verificable": "Arquitectura recomendada para on-grid/off-grid", "Criterio técnico del oferente": "Debe aceptar bus DC, rango de tensión, corriente térmica y estrategia de frenado."},
    {"Requisito Entel": "Compatibilidad on-grid", "Valor declarado": "Compatible con on-grid sujeto a anti-isla, PF, THD, protecciones y código de red", "Base técnica verificable": f"PF {entel_num_es(pf_setpoint, 2)}; THD {entel_num_es(thd_cap_pct, 1)}% estimada", "Criterio técnico del oferente": "Requiere estudio de protecciones, seccionamiento, sincronismo y coordinación con red existente."},
    {"Requisito Entel": "Compatibilidad off-grid", "Valor declarado": "Compatible con off-grid/híbrido sujeto a controlador DC, baterías/BMS y dump load/freno", "Base técnica verificable": f"Bus DC nominal {entel_int_es(V_dc_nom)} V; corriente DC nominal {entel_int_es(I_dc_nom)} A", "Criterio técnico del oferente": "Debe validarse con perfil de carga telecom, baterías y lógica de prioridad energética."},
])

entel_electrical_curve_df = entel_curve_df[[
    col for col in [
        "v (m/s)", "rpm_gen", "V_LL (V)", "V_LL (Ke) [V]", "f_e (Hz)", "I_est (A)",
        "P_mec_gen (kW)", "P_el (kW)", "P_out (clip) kW", "η_gen (curve)", "Duty_DC (%)"
    ]
    if col in entel_curve_df.columns
]].copy()
max_I_est = (
    float(pd.to_numeric(df["I_est (A)"], errors="coerce").max())
    if "I_est (A)" in df.columns
    else np.nan
)

entel_electrical_limits_df = pd.DataFrame([
    {"Indicador": "Tensión nominal generador", "Valor modelo": GEN["V_LL_nom"] if "GEN" in globals() else np.nan, "Límite/referencia": GEN["V_LL_nom"] if "GEN" in globals() else np.nan, "Unidad": "Vac L-L", "Criterio técnico del oferente": "Nivel nominal para coordinación de rectificador e inversor."},
    {"Indicador": "Tensión máxima curva V_LL", "Valor modelo": float(np.nanmax(df["V_LL (V)"])) if "V_LL (V)" in df.columns else np.nan, "Límite/referencia": GEN["V_LL_nom"] if "GEN" in globals() else np.nan, "Unidad": "Vac L-L", "Criterio técnico del oferente": "Verifica rango de entrada AC/DC y margen de aislamiento."},
    {"Indicador": "Frecuencia eléctrica máxima generador", "Valor modelo": float(np.nanmax(df["f_e (Hz)"])) if "f_e (Hz)" in df.columns else np.nan, "Límite/referencia": 50.0, "Unidad": "Hz", "Criterio técnico del oferente": "Frecuencia interna del generador; salida a sitio debe ser 50 Hz mediante inversor."},
    {"Indicador": "Corriente estimada máxima", "Valor modelo": max_I_est, "Límite/referencia": GDG_RATED_I, "Unidad": "A", "Criterio técnico del oferente": "Dimensiona cables, breaker, térmica de inversor y márgenes de generador."},
    {"Indicador": "Corriente térmica inversor", "Valor modelo": I_inv_thermal_A, "Límite/referencia": max_I_est, "Unidad": "A", "Criterio técnico del oferente": "Debe exceder corriente RMS continua esperada con margen."},
    {"Indicador": "Factor de potencia operativo", "Valor modelo": pf_setpoint, "Límite/referencia": pf_min_grid, "Unidad": "-", "Criterio técnico del oferente": "Requisito típico de interconexión y penalizaciones por reactivos."},
    {"Indicador": "THD estimada", "Valor modelo": thd_cap_pct, "Límite/referencia": thd_req_pct, "Unidad": "%", "Criterio técnico del oferente": "Evalúa necesidad de filtro LCL y calidad de onda."},
    {"Indicador": "Duty bus DC máximo", "Valor modelo": float(np.nanmax(df["Duty_DC (%)"])) if "Duty_DC (%)" in df.columns else np.nan, "Límite/referencia": 100.0, "Unidad": "%", "Criterio técnico del oferente": "Margen de utilización energética del bus DC."},
])
entel_electrical_limits_df["Margen [%]"] = np.where(
    pd.to_numeric(entel_electrical_limits_df["Límite/referencia"], errors="coerce") > 0,
    (
        pd.to_numeric(entel_electrical_limits_df["Límite/referencia"], errors="coerce")
        - pd.to_numeric(entel_electrical_limits_df["Valor modelo"], errors="coerce")
    )
    / pd.to_numeric(entel_electrical_limits_df["Límite/referencia"], errors="coerce")
    * 100.0,
    np.nan,
)

entel_grid_modes_df = pd.DataFrame([
    {"Modo": "On-grid", "Compatibilidad": "Sí, condicionada", "Elementos requeridos": "Inversor on-grid, anti-isla, seccionamiento, protecciones AC/DC, PF/THD dentro de norma, puesta a tierra", "Riesgo a cerrar": "Coordinación con red existente, selectividad de protecciones y permisos de conexión."},
    {"Modo": "Off-grid", "Compatibilidad": "Sí, condicionada", "Elementos requeridos": "Controlador DC, banco de baterías, BMS, dump load/freno, lógica de carga prioritaria, protecciones DC", "Riesgo a cerrar": "Estabilidad del bus, absorción de excedentes y compatibilidad con cargas telecom."},
    {"Modo": "Híbrido", "Compatibilidad": "Recomendado para piloto", "Elementos requeridos": "Inversor híbrido o arquitectura rectificador + bus DC + inversor, SCADA y control de disponibilidad", "Riesgo a cerrar": "Definir interfaz exacta con energía existente, baterías y monitoreo Entel."},
])

entel_electrical_closing_df = pd.DataFrame([
    {"Punto solicitado": "Compatibilidad con bancos de baterías", "Declaración técnica": "Compatible en arquitectura off-grid/híbrida mediante bus DC, controlador de carga, BMS y protecciones DC coordinadas.", "Parámetro de referencia": f"Bus DC nominal {entel_int_es(V_dc_nom)} V; I_dc nominal {entel_int_es(I_dc_nom)} A", "Condición para oferta": "Definir tensión del banco, química, BMS, potencia de carga/descarga, límites SOC y lógica de prioridad con la carga telecom."},
    {"Punto solicitado": "Rendimiento del inversor", "Declaración técnica": "El rendimiento del inversor/electrónica queda representado por la eficiencia electrónica configurada y debe respaldarse con curva del fabricante.", "Parámetro de referencia": f"η_elec configurada {entel_num_es(eta_elec, 3)}; η_gen máx {entel_num_es(eta_gen_max, 3)}", "Condición para oferta": "Adjuntar curva de eficiencia vs carga y confirmar rendimiento ponderado en la ventana de operación del sitio."},
    {"Punto solicitado": "Protección anti-isla", "Declaración técnica": "Requerida para operación on-grid; debe venir integrada en el inversor o en relé externo certificado.", "Parámetro de referencia": f"PF operativo {entel_num_es(pf_setpoint, 2)}; THD estimada {entel_num_es(thd_cap_pct, 1)}%", "Condición para oferta": "Declarar norma/certificación del equipo, tiempos de despeje, umbrales V/f y procedimiento de prueba SAT."},
    {"Punto solicitado": "Sistema de puesta a tierra", "Declaración técnica": "Debe integrar puesta a tierra de generador, inversor, mástil, tablero, SPD y protección contra descargas atmosféricas.", "Parámetro de referencia": "Malla/tierra del sitio + coordinación AC/DC + protección atmosférica", "Condición para oferta": "Entregar esquema de tierra, criterios de equipotencialidad, SPD, conductor PE y puntos de medición/ensayo."},
])

entel_voltage_fig = px.line(
    entel_electrical_curve_df,
    x="v (m/s)",
    y=[col for col in ["V_LL (V)", "V_LL (Ke) [V]", "f_e (Hz)"] if col in entel_electrical_curve_df.columns],
    color_discrete_map=entel_color_map,
    markers=True,
    title="Tensión y frecuencia eléctrica del generador",
)
entel_voltage_fig.update_layout(xaxis_title="Velocidad de viento [m/s]", yaxis_title="V / Hz", legend_title=None)

entel_current_fig = px.line(
    entel_electrical_curve_df,
    x="v (m/s)",
    y=[col for col in ["I_est (A)", "Duty_DC (%)"] if col in entel_electrical_curve_df.columns],
    color_discrete_map=entel_color_map,
    markers=True,
    title="Corriente estimada y utilización del bus DC",
)
entel_current_fig.update_layout(xaxis_title="Velocidad de viento [m/s]", yaxis_title="A / %", legend_title=None)
if np.isfinite(GDG_RATED_I) and GDG_RATED_I > 0:
    entel_current_fig.add_hline(y=float(GDG_RATED_I), line_dash="dot", annotation_text="I_nom generador")
if np.isfinite(I_inv_thermal_A):
    entel_current_fig.add_hline(y=float(I_inv_thermal_A), line_dash="dash", annotation_text="I térmica inversor")

entel_power_elec_fig = px.line(
    entel_electrical_curve_df,
    x="v (m/s)",
    y=[col for col in ["P_mec_gen (kW)", "P_out (clip) kW", "η_gen (curve)"] if col in entel_electrical_curve_df.columns],
    color_discrete_map=entel_color_map,
    markers=True,
    title="Potencia mecánica, salida neta URL y eficiencia de generador",
)
entel_power_elec_fig.update_layout(xaxis_title="Velocidad de viento [m/s]", yaxis_title="kW / eficiencia", legend_title=None)

entel_monitoring_status_fig = px.bar(
    entel_monitoring_status_df,
    x="Estado",
    y="Cantidad",
    color="Estado",
    text="Cantidad",
    color_discrete_map=entel_color_map,
    title="Sistema de monitoreo: cobertura por estado de implementación",
)
entel_monitoring_status_fig.update_traces(
    texttemplate="%{text}",
    textposition="outside",
    cliponaxis=False,
    hovertemplate="<b>%{x}</b><br>Requisitos: %{y}<extra></extra>",
)
entel_monitoring_status_fig.update_layout(xaxis_title="", yaxis_title="N° requisitos", showlegend=False)

entel_monitoring_section_fig = px.bar(
    entel_monitoring_section_df,
    x="Familia",
    y="Cantidad",
    color="Estado",
    text="Cantidad",
    color_discrete_map=entel_color_map,
    title="Sistema de monitoreo: estado por familia técnica",
)
entel_monitoring_section_fig.update_traces(
    texttemplate="%{text}",
    textposition="inside",
    hovertemplate="<b>%{x}</b><br>Estado: %{fullData.name}<br>Requisitos: %{y}<extra></extra>",
)
entel_monitoring_section_fig.update_layout(
    xaxis_title="",
    yaxis_title="N° requisitos",
    legend_title=None,
    barmode="stack",
)

entel_electrical_chart_colors = [
    entel_color_map["P_mec_gen (kW)"],
    entel_color_map["P_out (clip) kW"],
    entel_color_map["P_el (kW)"],
    entel_color_map["Cp_el_equiv"],
    entel_color_map["Energía bin"],
    entel_color_map["Disponibilidad"],
    entel_color_map["Duty_DC (%)"],
]

def style_entel_electrical_fig(fig, height: int = 430, add_wind_refs: bool = True):
    for trace in fig.data:
        trace_type = getattr(trace, "type", "")
        trace_name = str(getattr(trace, "name", "") or "")
        mapped_color = entel_color_map.get(trace_name)
        if trace_type == "scatter":
            line_style = dict(color=mapped_color or getattr(getattr(trace, "line", None), "color", None), width=3)
            trace.line = line_style
            trace.marker = dict(
                size=7,
                color=mapped_color or getattr(getattr(trace, "marker", None), "color", None),
                symbol="circle",
                line=dict(width=1.2, color="#ffffff"),
            )
        elif trace_type == "bar":
            if mapped_color:
                trace.marker.color = mapped_color
            trace.marker.line = dict(width=1.1, color="#ffffff")
        elif trace_type == "waterfall":
            trace.connector = dict(line=dict(color="rgba(79,90,105,0.35)", width=1))
        elif hasattr(trace, "line"):
            trace.line = dict(color=mapped_color or getattr(getattr(trace, "line", None), "color", None), width=3)
    fig.update_layout(
        template="plotly_white",
        height=height,
        colorway=entel_electrical_chart_colors,
        separators=",.",
        font=dict(family="Inter, Arial, sans-serif", color="#1f2933", size=12),
        title=dict(font=dict(size=17, color="#243447"), x=0.01, xanchor="left"),
        margin=dict(l=58, r=34, t=76, b=128),
        plot_bgcolor="#fbfcfd",
        paper_bgcolor="#ffffff",
        hovermode="x unified",
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.24,
            xanchor="center",
            x=0.5,
            bgcolor="rgba(255,255,255,0.84)",
            bordercolor="rgba(79,90,105,0.16)",
            borderwidth=1,
        ),
        xaxis=dict(
            showgrid=True,
            gridcolor="rgba(79,90,105,0.13)",
            zeroline=False,
            linecolor="rgba(79,90,105,0.35)",
            ticks="outside",
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="rgba(79,90,105,0.13)",
            zeroline=False,
            linecolor="rgba(79,90,105,0.35)",
            ticks="outside",
        ),
    )
    if add_wind_refs:
        for x_val, label in [(entel_v_cut_in, "cut-in"), (entel_v_rated, "nominal"), (entel_v_cut_out, "cut-out")]:
            if np.isfinite(x_val):
                fig.add_vline(
                    x=float(x_val),
                    line_width=1.1,
                    line_dash="dot",
                    line_color="rgba(79,90,105,0.45)",
                    annotation_text=label,
                    annotation_font_size=10,
                    annotation_font_color="#4f5a69",
                )
    return fig

entel_voltage_fig = style_entel_electrical_fig(entel_voltage_fig, height=420)
entel_current_fig = style_entel_electrical_fig(entel_current_fig, height=420)
entel_power_elec_fig = style_entel_electrical_fig(entel_power_elec_fig, height=450)

def entel_electrical_table_style(styler):
    return styler.set_table_styles([
        {"selector": "thead th", "props": [
            ("background-color", "#263447"),
            ("color", "#ffffff"),
            ("font-weight", "800"),
            ("border", "1px solid #d7dde4"),
            ("text-align", "left"),
            ("padding", "9px 10px"),
        ]},
        {"selector": "tbody td", "props": [
            ("border", "1px solid #e2e7ed"),
            ("padding", "9px 10px"),
            ("vertical-align", "top"),
            ("font-size", "12px"),
            ("color", "#1f2933"),
        ]},
        {"selector": "tbody tr:nth-child(even)", "props": [("background-color", "#f7f9fb")]},
        {"selector": "tbody tr:nth-child(odd)", "props": [("background-color", "#ffffff")]},
    ]).set_properties(**{"white-space": "normal"})

def format_entel_display_table(
    df_table: pd.DataFrame,
    formats: dict[str, str] | None = None,
    precision: int | None = None,
) -> pd.DataFrame:
    display_df = df_table.copy()
    formats = formats or {}

    def _format_cell(value, fmt: str | None):
        if pd.isna(value):
            return "-"
        if fmt:
            try:
                formatted = fmt.format(value)
                if isinstance(value, (int, float, np.integer, np.floating)):
                    return formatted.replace(",", "§").replace(".", ",").replace("§", ".")
                return formatted
            except (ValueError, TypeError):
                return str(value)
        if precision is not None and isinstance(value, (int, float, np.integer, np.floating)):
            return entel_num_es(value, precision)
        if isinstance(value, (int, float, np.integer, np.floating)):
            return entel_num_es(value, 3)
        return str(value)

    for col in display_df.columns:
        fmt = formats.get(col)
        display_df[col] = display_df[col].map(lambda value, fmt=fmt: _format_cell(value, fmt))
    return display_df

def render_entel_fixed_table(df_table: pd.DataFrame, widths: list[int] | None = None) -> None:
    widths = widths or [28, 46, 26]
    column_count = len(df_table.columns)
    if len(widths) < column_count:
        widths = widths + [widths[-1]] * (column_count - len(widths))
    elif len(widths) > column_count:
        widths = widths[:column_count]
    total_width = float(sum(widths)) if sum(widths) else 100.0
    normalized_widths = [width / total_width * 100.0 for width in widths]
    header_cells = "".join(
        f'<th style="width:{normalized_widths[i]:.3f}%;">{escape(str(col))}</th>'
        for i, col in enumerate(df_table.columns)
    )
    body_rows = []
    for _, row in df_table.iterrows():
        cells = "".join(f"<td>{escape(str(value))}</td>" for value in row)
        body_rows.append(f"<tr>{cells}</tr>")
    st.markdown(
        f"""
        <div class="entel-fixed-table-wrap">
          <table class="entel-fixed-table">
            <thead><tr>{header_cells}</tr></thead>
            <tbody>{''.join(body_rows)}</tbody>
          </table>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_entel_print_safe_chart(fig, key: str, width: int = 920, height: int | None = None) -> None:
    fig_print = copy.deepcopy(fig)
    base_height = height or int(fig_print.layout.height or 470)
    margin = fig_print.layout.margin
    fig_print.update_layout(
        autosize=False,
        width=width,
        height=min(max(base_height, 390), 540),
        margin=dict(
            l=max(int(margin.l or 60), 58),
            r=min(max(int(margin.r or 34), 28), 44),
            t=min(max(int(margin.t or 78), 64), 102),
            b=min(max(int(margin.b or 82), 74), 132),
        ),
    )
    st.plotly_chart(
        fig_print,
        use_container_width=False,
        config={"displayModeBar": False, "responsive": False},
        key=key,
    )


entel_wind_distribution_fig = style_entel_electrical_fig(entel_wind_distribution_fig, height=640, add_wind_refs=False)
entel_wind_distribution_fig.update_layout(margin=dict(l=64, r=38, t=112, b=138))
entel_wind_distribution_fig.update_yaxes(rangemode="tozero", automargin=True)
entel_yield_sensitivity_fig = style_entel_electrical_fig(entel_yield_sensitivity_fig, height=600, add_wind_refs=False)
entel_yield_sensitivity_fig.update_layout(
    margin=dict(l=64, r=38, t=104, b=196),
    legend=dict(
        orientation="h",
        yanchor="top",
        y=-0.36,
        xanchor="center",
        x=0.5,
        bgcolor="rgba(255,255,255,0.88)",
        bordercolor="rgba(79,90,105,0.16)",
        borderwidth=1,
    ),
)
entel_yield_sensitivity_fig.update_xaxes(tickangle=-20, automargin=True)
entel_yield_sensitivity_fig.update_yaxes(rangemode="tozero", automargin=True)
entel_month_fig = style_entel_electrical_fig(entel_month_fig, height=560, add_wind_refs=False)
entel_month_fig.update_layout(margin=dict(l=64, r=38, t=104, b=132), bargap=0.22)
entel_month_fig.update_yaxes(rangemode="tozero", automargin=True)
entel_energy_waterfall_fig = style_entel_electrical_fig(entel_energy_waterfall_fig, height=620, add_wind_refs=False)
entel_energy_waterfall_fig.update_layout(margin=dict(l=72, r=42, t=128, b=142))
entel_energy_waterfall_fig.update_yaxes(range=[0, waterfall_max * 1.24], automargin=True)
entel_power_fig = style_entel_electrical_fig(entel_power_fig, height=450)
entel_cp_fig = style_entel_electrical_fig(entel_cp_fig, height=430)
entel_aero_power_fig = style_entel_electrical_fig(entel_aero_power_fig, height=430, add_wind_refs=False)
entel_aero_cp_fig = style_entel_electrical_fig(entel_aero_cp_fig, height=430)
entel_aero_energy_fig = style_entel_electrical_fig(entel_aero_energy_fig, height=430, add_wind_refs=False)
entel_aero_stability_fig = style_entel_electrical_fig(entel_aero_stability_fig, height=430)
entel_monitoring_status_fig = style_entel_electrical_fig(entel_monitoring_status_fig, height=430, add_wind_refs=False)
entel_monitoring_status_fig.update_yaxes(range=[0, max(float(entel_monitoring_status_df["Cantidad"].max()) * 1.22, 1.0)], automargin=True)
entel_monitoring_section_fig = style_entel_electrical_fig(entel_monitoring_section_fig, height=470, add_wind_refs=False)
entel_monitoring_section_fig.update_layout(margin=dict(l=64, r=38, t=92, b=150))
entel_monitoring_section_fig.update_xaxes(tickangle=-12, automargin=True)
entel_monitoring_section_fig.update_yaxes(rangemode="tozero", automargin=True)
entel_proposal_status_fig = style_entel_electrical_fig(entel_proposal_status_fig, height=470, add_wind_refs=False)
entel_proposal_status_fig.update_layout(margin=dict(l=64, r=38, t=92, b=164))
entel_proposal_status_fig.update_xaxes(tickangle=-12, automargin=True)
entel_proposal_status_fig.update_yaxes(rangemode="tozero", automargin=True)

st.markdown(
    """
    <style>
    .entel-eng-panel {
        border: 1px solid rgba(79,90,105,0.18);
        border-left: 6px solid var(--accent);
        border-radius: 8px;
        background:
            linear-gradient(rgba(79,90,105,0.035) 1px, transparent 1px),
            linear-gradient(90deg, rgba(79,90,105,0.035) 1px, transparent 1px),
            linear-gradient(180deg, #ffffff 0%, #f7fafb 100%);
        background-size: 22px 22px, 22px 22px, auto;
        padding: 0.95rem 1.05rem;
        margin: 0.35rem 0 1.0rem 0;
        box-shadow: 0 10px 24px rgba(31,41,51,0.08);
    }
    .entel-eng-panel__eyebrow {
        color: var(--accent);
        font-size: 0.68rem;
        font-weight: 900;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        margin-bottom: 0.25rem;
    }
    .entel-eng-panel__title {
        color: #1f2933;
        font-size: 1.02rem;
        font-weight: 850;
        line-height: 1.22;
    }
    .entel-intro-panel {
        border: 1px solid rgba(79,90,105,0.16);
        border-left: 6px solid var(--accent);
        border-radius: 8px;
        background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
        padding: 1.05rem 1.18rem;
        margin: 0.15rem 0 1.12rem 0;
        box-shadow: 0 10px 24px rgba(31,41,51,0.07);
    }
    .entel-intro-panel__title {
        color: #173b57;
        font-size: 1.0rem;
        font-weight: 900;
        margin-bottom: 0.62rem;
    }
    .entel-intro-panel__body p {
        color: #2f3b4a;
        font-size: 0.88rem;
        line-height: 1.58;
        margin: 0 0 0.72rem 0;
        text-align: justify;
    }
    .entel-intro-panel__body p:last-child {
        margin-bottom: 0;
    }
    .entel-eng-kpi-grid {
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: 0.78rem;
        margin: 0.35rem 0 1.05rem 0;
    }
    .entel-eng-kpi-grid--three {
        grid-template-columns: repeat(3, minmax(0, 1fr));
    }
    .entel-eng-kpi {
        min-height: 106px;
        border: 1px solid rgba(79,90,105,0.18);
        border-top: 4px solid var(--accent);
        border-radius: 8px;
        background: linear-gradient(180deg, #ffffff 0%, #f7f9fb 100%);
        padding: 0.78rem 0.82rem;
        box-shadow: 0 8px 18px rgba(31,41,51,0.07);
    }
    .entel-eng-kpi__label {
        color: #52606d;
        font-size: 0.72rem;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 0.28rem;
    }
    .entel-eng-kpi__value {
        color: #1f2933;
        font-size: 1.34rem;
        font-weight: 900;
        line-height: 1.05;
    }
    .entel-eng-kpi__sub {
        color: #6b7280;
        font-size: 0.76rem;
        line-height: 1.25;
        margin-top: 0.35rem;
    }
    .entel-eng-section {
        display: flex;
        align-items: center;
        gap: 0.55rem;
        margin: 1.15rem 0 0.55rem 0;
        color: #1f2933;
        font-size: 1.02rem;
        font-weight: 900;
    }
    .entel-eng-section::before {
        content: "";
        width: 9px;
        height: 26px;
        border-radius: 3px;
        background: linear-gradient(180deg, var(--accent), #d9a766);
        display: inline-block;
    }
    .entel-fixed-table-wrap {
        width: 100%;
        max-width: 100%;
        overflow-x: hidden;
        margin: 0.15rem 0 1.0rem 0;
        border: 1px solid rgba(79,90,105,0.18);
        border-radius: 8px;
        background: #ffffff;
        box-shadow: 0 10px 24px rgba(31,41,51,0.07);
    }
    .entel-fixed-table {
        width: 100%;
        max-width: 100%;
        table-layout: fixed;
        border-collapse: collapse;
        font-size: 0.78rem;
        color: #1f2933;
    }
    .entel-fixed-table th {
        background: #263447;
        color: #ffffff;
        font-weight: 850;
        text-align: left;
        padding: 0.62rem 0.7rem;
        border-right: 1px solid rgba(255,255,255,0.16);
        line-height: 1.22;
        white-space: normal;
        overflow-wrap: anywhere;
    }
    .entel-fixed-table td {
        padding: 0.68rem 0.7rem;
        border-top: 1px solid #e2e7ed;
        border-right: 1px solid #e2e7ed;
        vertical-align: top;
        line-height: 1.32;
        white-space: normal;
        overflow-wrap: anywhere;
        word-break: normal;
        hyphens: auto;
    }
    .entel-fixed-table tr:nth-child(even) td {
        background: #f7f9fb;
    }
    .entel-fixed-table tr:nth-child(odd) td {
        background: #ffffff;
    }
    @media (max-width: 900px) {
        .entel-eng-kpi-grid,
        .entel-eng-kpi-grid--three { grid-template-columns: repeat(2, minmax(0, 1fr)); }
        .entel-fixed-table { font-size: 0.72rem; }
        .entel-fixed-table th,
        .entel-fixed-table td { padding: 0.52rem 0.48rem; }
    }
    .entel-print-page-break {
        height: 0;
        margin: 0;
        padding: 0;
    }
    @media print {
        @page {
            size: Letter portrait;
            margin: 10mm 8mm 11mm 8mm;
        }
        html,
        body {
            width: 216mm !important;
            min-height: 279mm !important;
            margin: 0 !important;
            background: #ffffff !important;
            -webkit-print-color-adjust: exact !important;
            print-color-adjust: exact !important;
        }
        .stApp,
        [data-testid="stAppViewContainer"],
        section.main,
        .main {
            width: 100% !important;
            max-width: 100% !important;
            background: #ffffff !important;
            overflow: visible !important;
        }
        [data-testid="stHeader"],
        [data-testid="stToolbar"],
        [data-testid="stDecoration"],
        [data-testid="stSidebar"],
        [data-testid="collapsedControl"],
        .alert-jump-link,
        .alert-jump-floating,
        .top-jump-floating,
        .stDeployButton,
        button[kind="header"],
        .stButton,
        iframe[title="streamlit_floating_button"] {
            display: none !important;
        }
        .main .block-container {
            max-width: 196mm !important;
            width: 196mm !important;
            padding: 0 !important;
            margin: 0 auto !important;
            overflow: visible !important;
        }
        .main .block-container > div,
        .main .block-container > div > div,
        div[data-testid="stVerticalBlock"],
        div[data-testid="stVerticalBlock"] > div,
        div[data-testid="stHorizontalBlock"],
        div[data-testid="stHorizontalBlock"] > div,
        div[data-testid="stElementContainer"],
        div[data-testid="element-container"] {
            gap: 0 !important;
            row-gap: 0 !important;
            margin-top: 0 !important;
            margin-bottom: 0 !important;
            overflow: visible !important;
        }
        div[data-testid="stHorizontalBlock"] {
            display: block !important;
        }
        div[data-testid="stHorizontalBlock"] > div {
            width: 100% !important;
            max-width: 100% !important;
            flex: 0 0 100% !important;
        }
        .entel-eng-panel,
        .entel-intro-panel,
        .comment-box,
        .entel-eng-kpi-grid,
        .entel-eng-kpi,
        .js-plotly-plot,
        div[data-testid="stPlotlyChart"] {
            break-inside: avoid !important;
            page-break-inside: avoid !important;
        }
        .entel-eng-section {
            break-after: avoid !important;
            page-break-after: avoid !important;
            margin-top: 3.2mm !important;
            margin-bottom: 1.8mm !important;
            font-size: 9.6pt !important;
            line-height: 1.12 !important;
        }
        .entel-eng-section::before {
            height: 6.5mm !important;
            width: 2.2mm !important;
            min-width: 2.2mm !important;
        }
        .entel-eng-panel {
            padding: 3.0mm 3.4mm !important;
            margin: 0 0 3.2mm 0 !important;
            box-shadow: none !important;
            background-size: 10mm 10mm, 10mm 10mm, auto !important;
        }
        .entel-eng-panel__eyebrow {
            font-size: 6.2pt !important;
            margin-bottom: 1mm !important;
        }
        .entel-eng-panel__title {
            font-size: 8.8pt !important;
            line-height: 1.18 !important;
        }
        .entel-intro-panel {
            padding: 3.2mm 3.6mm !important;
            margin: 0 0 3.6mm 0 !important;
            box-shadow: none !important;
        }
        .entel-intro-panel__title {
            font-size: 9.2pt !important;
            margin-bottom: 2mm !important;
        }
        .entel-intro-panel__body p {
            font-size: 7.4pt !important;
            line-height: 1.25 !important;
            margin: 0 0 2mm 0 !important;
        }
        .comment-box {
            padding: 2.6mm 3.2mm !important;
            margin: 1.6mm 0 3.2mm 0 !important;
            box-shadow: none !important;
        }
        .comment-box h4,
        .comment-box strong {
            font-size: 8.2pt !important;
            line-height: 1.18 !important;
        }
        .comment-box p {
            font-size: 7.2pt !important;
            line-height: 1.2 !important;
            margin: 1.2mm 0 !important;
        }
        .entel-fixed-table-wrap {
            margin: 1.2mm 0 3.6mm 0 !important;
            border-radius: 4px !important;
            box-shadow: none !important;
            overflow: visible !important;
        }
        .entel-fixed-table {
            font-size: 6.25pt !important;
            table-layout: fixed !important;
            width: 100% !important;
            border-collapse: collapse !important;
        }
        .entel-fixed-table thead {
            display: table-header-group !important;
        }
        .entel-fixed-table tbody {
            display: table-row-group !important;
        }
        .entel-fixed-table th {
            padding: 1.8mm 2mm !important;
            line-height: 1.14 !important;
        }
        .entel-fixed-table td {
            padding: 1.55mm 2mm !important;
            line-height: 1.16 !important;
            overflow-wrap: break-word !important;
            word-break: normal !important;
        }
        .entel-fixed-table tr {
            break-inside: avoid !important;
            page-break-inside: avoid !important;
        }
        .entel-eng-kpi-grid {
            grid-template-columns: repeat(4, minmax(0, 1fr)) !important;
            gap: 2.4mm !important;
            margin: 1.8mm 0 3.6mm 0 !important;
        }
        .entel-eng-kpi {
            min-height: auto !important;
            padding: 2.4mm 2.8mm !important;
            box-shadow: none !important;
            border-radius: 4px !important;
        }
        .entel-eng-kpi__label {
            font-size: 5.8pt !important;
            margin-bottom: 1mm !important;
        }
        .entel-eng-kpi__value {
            font-size: 11pt !important;
        }
        .entel-eng-kpi__sub {
            font-size: 6.2pt !important;
            line-height: 1.12 !important;
            margin-top: 1.2mm !important;
        }
        div[data-testid="stPlotlyChart"],
        .js-plotly-plot {
            width: 190mm !important;
            max-width: 190mm !important;
            height: 106mm !important;
            min-height: 0 !important;
            margin: 0 auto 5mm auto !important;
            overflow: hidden !important;
        }
        div[data-testid="stPlotlyChart"] > div,
        div[data-testid="stPlotlyChart"] > div > div,
        .js-plotly-plot .plot-container,
        .js-plotly-plot .user-select-none,
        .js-plotly-plot .svg-container {
            width: 190mm !important;
            max-width: 190mm !important;
            height: 106mm !important;
            overflow: hidden !important;
        }
        .js-plotly-plot .modebar,
        .modebar-container {
            display: none !important;
        }
        .js-plotly-plot .svg-container,
        .js-plotly-plot .main-svg {
            width: 190mm !important;
            max-width: 190mm !important;
        }
        .js-plotly-plot .svg-container {
            height: 106mm !important;
        }
        .js-plotly-plot .main-svg {
            height: 106mm !important;
        }
        .element-container:has(.js-plotly-plot) {
            margin: 0 0 5mm 0 !important;
            break-inside: avoid !important;
            page-break-inside: avoid !important;
            overflow: hidden !important;
        }
        div[data-testid="stElementContainer"]:has(div[data-testid="stPlotlyChart"]),
        div[data-testid="element-container"]:has(div[data-testid="stPlotlyChart"]) {
            width: 190mm !important;
            max-width: 190mm !important;
            margin: 0 0 5mm 0 !important;
            break-inside: avoid !important;
            page-break-inside: avoid !important;
            overflow: hidden !important;
        }
        .entel-print-page-break {
            break-before: page !important;
            page-break-before: always !important;
            height: 0 !important;
            margin: 0 !important;
            padding: 0 !important;
        }
        .entel-print-page-break + div,
        .entel-print-page-break + div .entel-eng-section {
            margin-top: 0 !important;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


proposal_total = int(len(entel_proposal_7810_df))
proposal_included = int(entel_proposal_7810_df["Estado de postulación"].isin(["Confirmado", "Incluido", "Adjuntado / indicado"]).sum())
proposal_later = int((entel_proposal_7810_df["Estado de postulación"] == "Entrega posterior").sum())
proposal_pending = int(entel_proposal_7810_df["Estado de postulación"].isin(["Pendiente", "Brecha declarada", "Sin respuesta"]).sum())
proposal_coverage = proposal_included / max(proposal_total, 1) * 100.0
monitoring_cumple = int(entel_monitoring_status_df.loc[entel_monitoring_status_df["Estado"] == "Cumple", "Cantidad"].sum())
monitoring_contemplado = int(entel_monitoring_status_df.loc[entel_monitoring_status_df["Estado"] == "Contemplado", "Cantidad"].sum())
monitoring_ready_pct = (monitoring_cumple + monitoring_contemplado) / max(entel_monitoring_total, 1) * 100.0

st.markdown("### Licitación técnica consolidada")
st.markdown(
    """
    <div class="entel-eng-panel" style="--accent:#2f5f73;">
      <div class="entel-eng-panel__eyebrow">Vista consolidada RFP</div>
      <div class="entel-eng-panel__title">Compilado técnico continuo de todas las pestañas Entel, conservando el orden de revisión de izquierda a derecha.</div>
    </div>
    """,
    unsafe_allow_html=True,
)
intro_body_html = "".join(
    f"<p>{escape(paragraph)}</p>"
    for paragraph in entel_introduction_paragraphs
)
st.markdown(
    f"""
    <div class="entel-intro-panel" style="--accent:#2f5f73;">
      <div class="entel-intro-panel__title">{escape(entel_introduction_title)}</div>
      <div class="entel-intro-panel__body">{intro_body_html}</div>
    </div>
    """,
    unsafe_allow_html=True,
)
st.caption(f"Fuente trazable: {entel_introduction_source}. Hoja publicada: Introducción.")

st.markdown('<div class="entel-eng-section" style="--accent:#2f5f73;">3. Requerimientos Técnicos Mínimos</div>', unsafe_allow_html=True)
st.markdown('<div class="entel-eng-section" style="--accent:#5f7f75;">3.1 Características Generales</div>', unsafe_allow_html=True)
render_entel_fixed_table(entel_req_exc_df, widths=[46, 34, 20])
st.caption(f"Fuente trazable: {entel_req_exc_source}. Hoja publicada: Req.exc.")
st.markdown('<div class="entel-print-page-break"></div>', unsafe_allow_html=True)

st.markdown('<div class="entel-eng-section" style="--accent:#5f7f75;">3.2 Estudio de Producción Energética y Factor de Planta</div>', unsafe_allow_html=True)
st.markdown(
    comment_box(
        "Alcance del Energy Yield Assessment",
        [
            comment_paragraph("Esta pestaña responde el punto 3.2 del RFP: estimar el desempeño energético de la turbina propuesta para el sitio definido por Entel usando el recurso eólico disponible, la distribución de velocidades y la curva de potencia de la oferta."),
            comment_paragraph("El resultado principal es el P50 técnico esperado y sus sensibilidades para disponibilidad, pérdidas eléctricas, incertidumbre del recurso, degradación y factor de planta. La lectura está ordenada para revisión de ingeniería de proyectos eólicos."),
        ],
    ),
    unsafe_allow_html=True,
)
st.markdown(
    f"""
    <div class="entel-eng-kpi-grid">
      <div class="entel-eng-kpi" style="--accent:#5f7f75;"><div class="entel-eng-kpi__label">AEP P50 técnico</div><div class="entel-eng-kpi__value">{entel_int_es(entel_AEP_kWh, " kWh/año") if np.isfinite(entel_AEP_kWh) else "-"}</div><div class="entel-eng-kpi__sub">Caso central de producción energética esperada.</div></div>
      <div class="entel-eng-kpi" style="--accent:#2f5f73;"><div class="entel-eng-kpi__label">Factor planta P50</div><div class="entel-eng-kpi__value">{entel_num_es(entel_CF * 100, 1, "%") if np.isfinite(entel_CF) else "-"}</div><div class="entel-eng-kpi__sub">Relación entre potencia media y potencia nominal.</div></div>
      <div class="entel-eng-kpi" style="--accent:#d9a766;"><div class="entel-eng-kpi__label">Altura recurso</div><div class="entel-eng-kpi__value">{entel_num_es(entel_installation_height_m, 1, " m")}</div><div class="entel-eng-kpi__sub">Altura efectiva usada para extrapolación/cálculo.</div></div>
      <div class="entel-eng-kpi" style="--accent:#d95f5f;"><div class="entel-eng-kpi__label">Weibull k / c</div><div class="entel-eng-kpi__value">{entel_num_es(k_energy, 2)} / {entel_num_es(c_energy, 2)}</div><div class="entel-eng-kpi__sub">Distribución estadística activa del sitio.</div></div>
    </div>
    """,
    unsafe_allow_html=True,
)
st.markdown('<div class="entel-eng-section" style="--accent:#5f7f75;">Información base entregada por el mandante</div>', unsafe_allow_html=True)
render_entel_fixed_table(entel_yield_site_df, widths=[20, 21, 29, 30])
st.markdown('<div class="entel-eng-section" style="--accent:#5f7f75;">Metodología utilizada</div>', unsafe_allow_html=True)
render_entel_fixed_table(entel_yield_methodology_df, widths=[22, 52, 26])
st.markdown('<div class="entel-eng-section" style="--accent:#5f7f75;">Resultados Energy Yield Assessment</div>', unsafe_allow_html=True)
render_entel_fixed_table(format_entel_display_table(entel_yield_assessment_df, formats={"Valor": "{:,.3f}"}), widths=[28, 16, 14, 42])
render_entel_print_safe_chart(entel_wind_distribution_fig, key="consolidated_wind_distribution")
st.markdown('<div class="entel-eng-section" style="--accent:#5f7f75;">P50 técnico y sensibilidades</div>', unsafe_allow_html=True)
render_entel_fixed_table(
    format_entel_display_table(entel_yield_sensitivity_df, formats={"AEP [kWh/año]": "{:,.1f}", "Factor planta [%]": "{:.2f}"}),
    widths=[11, 16, 15, 13, 11, 34],
)
render_entel_print_safe_chart(entel_yield_sensitivity_fig, key="consolidated_yield_sensitivity")
st.markdown('<div class="entel-eng-section" style="--accent:#5f7f75;">Distribución estadística de velocidades</div>', unsafe_allow_html=True)
render_entel_fixed_table(
    format_entel_display_table(entel_wind_distribution_df, formats={"Probabilidad [%]": "{:.2f}", "Horas/año": "{:,.1f}", "Potencia media bin [kW]": "{:,.3f}", "Energía bin [kWh/año]": "{:,.1f}"}),
    widths=[19, 18, 18, 21, 24],
)
st.markdown('<div class="entel-eng-section" style="--accent:#5f7f75;">Ajustes, extrapolaciones, turbulencia y pérdidas</div>', unsafe_allow_html=True)
render_entel_fixed_table(entel_resource_summary_df.astype({"Valor": "string"}), widths=[24, 76])
render_entel_fixed_table(entel_turbulence_losses_df, widths=[16, 22, 25, 37])
st.markdown(
    comment_box(
        "Declaración técnica del oferente",
        [
            comment_paragraph("La estimación de producción se basa en el recurso eólico cargado, la altura de instalación declarada para la oferta y la curva de potencia utilizada en el cálculo. La trazabilidad queda separada por origen del recurso, altura, distribución Weibull k/c y método de extrapolación."),
            comment_paragraph("Las sensibilidades presentadas cuantifican el impacto técnico de disponibilidad, pérdidas eléctricas, incertidumbre de recurso y degradación sobre el P50. Esto permite revisar el desempeño esperado y sus márgenes de riesgo de forma transparente."),
            comment_paragraph("La consideración de turbulencia se declara como supuesto de ingeniería y, cuando existe serie temporal, se incorpora un indicador de variabilidad del recurso. La validación final de cargas, vibración y fatiga debe quedar respaldada en los anexos técnicos de la oferta."),
        ],
    ),
    unsafe_allow_html=True,
)

st.markdown('<div class="entel-print-page-break"></div>', unsafe_allow_html=True)
st.markdown('<div class="entel-eng-section" style="--accent:#2f5f73;">3.2.1 Simulación de desempeño</div>', unsafe_allow_html=True)
st.markdown(
    comment_box(
        "Alcance del cálculo de desempeño",
        [
            comment_paragraph("La simulación consolida producción mensual, producción anual, potencia promedio, horas equivalentes, factor de planta, disponibilidad y pérdidas aplicadas para la turbina ofertada."),
            comment_paragraph(f"La curva `P_out (clip) kW` usada en el cálculo proviene de: {entel_curve_source}. La trazabilidad conserva origen de curva, bins de viento y supuestos energéticos asociados."),
        ],
    ),
    unsafe_allow_html=True,
)
st.markdown(
    f"""
    <div class="entel-eng-kpi-grid entel-eng-kpi-grid--three">
      <div class="entel-eng-kpi" style="--accent:#2f5f73;"><div class="entel-eng-kpi__label">AEP esperado</div><div class="entel-eng-kpi__value">{entel_int_es(entel_AEP_kWh, " kWh/año") if np.isfinite(entel_AEP_kWh) else "-"}</div><div class="entel-eng-kpi__sub">Producción anual P50 técnico.</div></div>
      <div class="entel-eng-kpi" style="--accent:#84a9a4;"><div class="entel-eng-kpi__label">Potencia promedio</div><div class="entel-eng-kpi__value">{entel_num_es(p_avg_kw, 2, " kW") if np.isfinite(p_avg_kw) else "-"}</div><div class="entel-eng-kpi__sub">Potencia equivalente sobre 8.760 h/año.</div></div>
      <div class="entel-eng-kpi" style="--accent:#d9a766;"><div class="entel-eng-kpi__label">Factor planta</div><div class="entel-eng-kpi__value">{entel_num_es(entel_CF * 100, 1, "%") if np.isfinite(entel_CF) else "-"}</div><div class="entel-eng-kpi__sub">Relación producción nominal anual.</div></div>
      <div class="entel-eng-kpi" style="--accent:#6b7280;"><div class="entel-eng-kpi__label">Horas equivalentes</div><div class="entel-eng-kpi__value">{entel_int_es(equivalent_hours, " h/año") if np.isfinite(equivalent_hours) else "-"}</div><div class="entel-eng-kpi__sub">AEP dividido por potencia nominal.</div></div>
      <div class="entel-eng-kpi" style="--accent:#d95f5f;"><div class="entel-eng-kpi__label">Disponibilidad</div><div class="entel-eng-kpi__value">{entel_num_es(entel_availability * 100, 1, "%")}</div><div class="entel-eng-kpi__sub">Disponibilidad considerada en cálculo.</div></div>
      <div class="entel-eng-kpi" style="--accent:#5f7f75;"><div class="entel-eng-kpi__label">AEP con disponibilidad</div><div class="entel-eng-kpi__value">{entel_int_es(aep_with_availability, " kWh/año") if np.isfinite(aep_with_availability) else "-"}</div><div class="entel-eng-kpi__sub">Producción neta con disponibilidad RFP.</div></div>
    </div>
    """,
    unsafe_allow_html=True,
)
st.markdown('<div class="entel-eng-section" style="--accent:#2f5f73;">Resultados mínimos exigidos por Entel</div>', unsafe_allow_html=True)
render_entel_fixed_table(format_entel_display_table(entel_performance_kpi_df, formats={"Valor": "{:,.2f}"}), widths=[31, 16, 14, 39])
st.markdown('<div class="entel-eng-section" style="--accent:#2f5f73;">Producción energética mensual esperada</div>', unsafe_allow_html=True)
render_entel_fixed_table(
    format_entel_display_table(entel_monthly_df, formats={"Producción esperada [kWh/mes]": "{:,.1f}", "Participación anual [%]": "{:.2f}", "Producción serie directa [kWh/periodo]": "{:,.1f}"}),
    widths=[10, 17, 13, 18, 42],
)
render_entel_print_safe_chart(entel_month_fig, key="consolidated_month")
st.markdown('<div class="entel-eng-section" style="--accent:#2f5f73;">Producción energética anual y pérdidas</div>', unsafe_allow_html=True)
render_entel_fixed_table(
    format_entel_display_table(entel_losses_df, formats={"Energía anual [kWh/año]": "{:,.1f}", "Pérdida aplicada [kWh/año]": "{:,.1f}", "Pérdida sobre aero [%]": "{:.2f}"}),
    widths=[15, 15, 15, 40, 15],
)
render_entel_print_safe_chart(entel_energy_waterfall_fig, key="consolidated_energy_waterfall")
st.markdown('<div class="entel-eng-section" style="--accent:#2f5f73;">Curva de potencia utilizada en la simulación</div>', unsafe_allow_html=True)
render_entel_print_safe_chart(entel_power_fig, key="consolidated_power")
render_entel_print_safe_chart(entel_cp_fig, key="consolidated_cp")
render_entel_fixed_table(format_entel_display_table(entel_performance_curve_df, precision=3), widths=[7, 9, 10, 8, 16, 13, 7, 7, 7, 16])
st.markdown('<div class="entel-eng-section" style="--accent:#2f5f73;">3.2.3 Supuestos del cálculo</div>', unsafe_allow_html=True)
render_entel_fixed_table(entel_assumptions_df, widths=[24, 28, 48])
st.markdown(
    comment_box(
        "Conclusiones técnicas del simulador",
        [
            comment_paragraph("El AEP P50 técnico queda determinado por la curva de potencia declarada y la distribución Weibull activa del sitio; la trazabilidad del cálculo se mantiene separada entre recurso, curva, altura de instalación y disponibilidad."),
            comment_paragraph("El balance anual identifica la energía bruta, las pérdidas mecánicas, las pérdidas eléctricas, el clipping y la disponibilidad como etapas independientes; esta separación permite auditar el impacto energético de cada supuesto."),
            comment_paragraph("Las horas equivalentes y el factor de planta quedan definidos como indicadores de desempeño contractual de la oferta; ambos dependen de la producción neta anual y de la potencia nominal declarada en la curva Entel."),
        ],
    ),
    unsafe_allow_html=True,
)
st.markdown('<div class="entel-eng-section" style="--accent:#2f5f73;">Recurso usado para la simulación</div>', unsafe_allow_html=True)
render_entel_fixed_table(entel_resource_summary_df.astype({"Valor": "string"}), widths=[28, 72])

st.markdown('<div class="entel-print-page-break"></div>', unsafe_allow_html=True)
st.markdown('<div class="entel-eng-section" style="--accent:#d9a766;">3.3 Desempeño Aerodinámico</div>', unsafe_allow_html=True)
st.markdown(
    comment_box(
        "Alcance aerodinámico declarado",
        [
            comment_paragraph("La sección documenta velocidades características, curva de potencia, coeficientes Cp y producción anual estimada para vientos medios entre 4 y 8 m/s."),
            comment_paragraph("El desempeño aerodinámico se presenta junto con indicadores de estabilidad, vibración y ruido para respaldar la consistencia técnica de la oferta."),
        ],
    ),
    unsafe_allow_html=True,
)
st.markdown(
    f"""
    <div class="entel-eng-kpi-grid">
      <div class="entel-eng-kpi" style="--accent:#5f7f75;"><div class="entel-eng-kpi__label">Cut-in</div><div class="entel-eng-kpi__value">{entel_num_es(entel_v_cut_in, 1, " m/s")}</div><div class="entel-eng-kpi__sub">Inicio de producción útil.</div></div>
      <div class="entel-eng-kpi" style="--accent:#d9a766;"><div class="entel-eng-kpi__label">Vel. nominal</div><div class="entel-eng-kpi__value">{entel_num_es(entel_v_rated, 1, " m/s")}</div><div class="entel-eng-kpi__sub">Punto de transición a control/limitación.</div></div>
      <div class="entel-eng-kpi" style="--accent:#d95f5f;"><div class="entel-eng-kpi__label">Cut-out</div><div class="entel-eng-kpi__value">{entel_num_es(entel_v_cut_out, 1, " m/s")}</div><div class="entel-eng-kpi__sub">Umbral de parada segura por viento alto.</div></div>
      <div class="entel-eng-kpi" style="--accent:#2f5f73;"><div class="entel-eng-kpi__label">Cp_el máx</div><div class="entel-eng-kpi__value">{entel_num_es(float(np.nanmax(entel_curve_df['Cp_el_equiv'])), 3) if "Cp_el_equiv" in entel_curve_df.columns else "-"}</div><div class="entel-eng-kpi__sub">Eficiencia eléctrica equivalente máxima.</div></div>
    </div>
    """,
    unsafe_allow_html=True,
)
st.markdown('<div class="entel-eng-section" style="--accent:#d9a766;">Velocidades características y coeficiente de potencia</div>', unsafe_allow_html=True)
render_entel_fixed_table(format_entel_display_table(entel_aero_operating_df, formats={"Valor": "{:,.3f}"}), widths=[28, 15, 13, 44])
aero_con_col1, aero_con_col2 = st.columns(2)
with aero_con_col1:
    render_entel_print_safe_chart(entel_aero_power_fig, key="consolidated_aero_power")
with aero_con_col2:
    render_entel_print_safe_chart(entel_aero_cp_fig, key="consolidated_aero_cp")
st.markdown('<div class="entel-eng-section" style="--accent:#d9a766;">Producción energética anual estimada por viento medio</div>', unsafe_allow_html=True)
render_entel_fixed_table(format_entel_display_table(entel_mean_wind_df, formats={"AEP estimado [kWh/año]": "{:,.1f}", "Potencia promedio [kW]": "{:,.3f}", "Factor planta [%]": "{:.2f}"}), widths=[18, 24, 22, 18, 18])
render_entel_print_safe_chart(entel_aero_energy_fig, key="consolidated_aero_energy")
st.markdown('<div class="entel-eng-section" style="--accent:#d9a766;">Ruido, vibración y estabilidad operacional</div>', unsafe_allow_html=True)
render_entel_fixed_table(entel_aero_stability_df, widths=[18, 17, 21, 44])
render_entel_print_safe_chart(entel_aero_stability_fig, key="consolidated_aero_stability")
st.markdown(
    comment_box(
        "Conclusiones aerodinámicas relevantes",
        [
            comment_paragraph("La evaluación de vibración se resume mediante frecuencias 1P/3P, rpm y aceleración centrípeta; estos indicadores permiten identificar bandas críticas para validación estructural."),
            comment_paragraph("La evaluación acústica considera Lp_obs y velocidad de punta; ambos indicadores permiten revisar la aptitud de operación en entornos urbanos o semiurbanos."),
            comment_paragraph("La estabilidad operacional se verifica por continuidad de la curva de potencia entre cut-in, régimen nominal y cut-out, evitando saltos de rpm, corriente o carga."),
        ],
    ),
    unsafe_allow_html=True,
)
st.markdown('<div class="entel-eng-section" style="--accent:#d9a766;">Tabla aerodinámica por bin de viento</div>', unsafe_allow_html=True)
render_entel_fixed_table(format_entel_display_table(entel_aero_curve_df, precision=3), widths=[6, 7, 7, 6, 6, 6, 5, 6, 5, 5, 5, 5, 5, 5, 21])

st.markdown('<div class="entel-print-page-break"></div>', unsafe_allow_html=True)
st.markdown('<div class="entel-eng-section" style="--accent:#2f5f73;">3.4 Características Eléctricas</div>', unsafe_allow_html=True)
st.markdown(
    comment_box(
        "Alcance eléctrico declarado",
        [
            comment_paragraph("La sección resume tensión nominal, frecuencia, arquitectura de inversor, compatibilidad on-grid/off-grid, baterías, rendimiento, anti-isla y puesta a tierra."),
            comment_paragraph("La arquitectura separa variables internas del generador y salida útil al sitio: el generador opera con tensión/frecuencia variable y el inversor entrega interfaz AC regulada o bus DC híbrido."),
        ],
    ),
    unsafe_allow_html=True,
)
st.markdown(
    f"""
    <div class="entel-elec-kpi-grid">
      <div class="entel-elec-kpi" style="--accent:#2f5f73;"><div class="entel-elec-kpi__label">V_LL nominal</div><div class="entel-elec-kpi__value">{entel_int_es(GEN['V_LL_nom'], " Vac") if "GEN" in globals() else "-"}</div><div class="entel-elec-kpi__sub">Referencia de coordinación generador / rectificador / inversor.</div></div>
      <div class="entel-elec-kpi" style="--accent:#d9a766;"><div class="entel-elec-kpi__label">Salida AC</div><div class="entel-elec-kpi__value">50 Hz</div><div class="entel-elec-kpi__sub">Frecuencia regulada en salida útil del inversor.</div></div>
      <div class="entel-elec-kpi" style="--accent:#84a9a4;"><div class="entel-elec-kpi__label">I_est máx</div><div class="entel-elec-kpi__value">{entel_num_es(max_I_est, 1, " A") if np.isfinite(max_I_est) else "-"}</div><div class="entel-elec-kpi__sub">Base para cableado, protecciones y margen térmico.</div></div>
      <div class="entel-elec-kpi" style="--accent:#d95f5f;"><div class="entel-elec-kpi__label">PF operativo</div><div class="entel-elec-kpi__value">{entel_num_es(pf_setpoint, 2)}</div><div class="entel-elec-kpi__sub">Referencia de calidad eléctrica e interconexión.</div></div>
    </div>
    """,
    unsafe_allow_html=True,
)
st.markdown('<div class="entel-eng-section" style="--accent:#2f5f73;">Requisitos eléctricos solicitados por Entel</div>', unsafe_allow_html=True)
render_entel_fixed_table(entel_electrical_specs_df, widths=[18, 25, 22, 35])
st.markdown('<div class="entel-eng-section" style="--accent:#2f5f73;">Comportamiento eléctrico por velocidad de viento</div>', unsafe_allow_html=True)
elec_con_col1, elec_con_col2 = st.columns(2)
with elec_con_col1:
    render_entel_print_safe_chart(entel_voltage_fig, key="consolidated_voltage")
with elec_con_col2:
    render_entel_print_safe_chart(entel_current_fig, key="consolidated_current")
render_entel_print_safe_chart(entel_power_elec_fig, key="consolidated_power_elec")
st.markdown('<div class="entel-eng-section" style="--accent:#2f5f73;">Límites, márgenes y calidad eléctrica</div>', unsafe_allow_html=True)
render_entel_fixed_table(format_entel_display_table(entel_electrical_limits_df, formats={"Valor modelo": "{:,.2f}", "Límite/referencia": "{:,.2f}", "Margen [%]": "{:,.2f}"}), widths=[22, 13, 15, 10, 28, 12])
st.markdown('<div class="entel-eng-section" style="--accent:#2f5f73;">Compatibilidad on-grid / off-grid</div>', unsafe_allow_html=True)
render_entel_fixed_table(entel_grid_modes_df, widths=[12, 18, 38, 32])
st.markdown('<div class="entel-eng-section" style="--accent:#2f5f73;">Cierre eléctrico requerido por Entel</div>', unsafe_allow_html=True)
render_entel_fixed_table(entel_electrical_closing_df, widths=[18, 31, 21, 30])
st.markdown(
    comment_box(
        "Conclusiones de integración eléctrica",
        [
            comment_paragraph("La compatibilidad on-grid requiere anti-isla, seccionamiento, factor de potencia, THD, puesta a tierra, protecciones y cumplimiento del código de red aplicable."),
            comment_paragraph("La compatibilidad off-grid requiere estabilidad de bus DC, banco de baterías, BMS, absorción de excedentes y lógica de prioridad energética para continuidad de servicio."),
            comment_paragraph("Los anexos eléctricos deben respaldar arquitectura DC/BMS, certificado anti-isla, esquema de puesta a tierra, SPD y criterios de prueba SAT."),
            comment_paragraph("La tabla por bin entrega corriente, tensión, frecuencia y potencia para dimensionamiento de cables, breaker, inversor, rectificador e integración SCADA."),
        ],
    ),
    unsafe_allow_html=True,
)
st.markdown('<div class="entel-eng-section" style="--accent:#2f5f73;">Tabla eléctrica por bin de viento</div>', unsafe_allow_html=True)
render_entel_fixed_table(format_entel_display_table(entel_electrical_curve_df, precision=3), widths=[9, 9, 10, 10, 10, 9, 11, 10, 12, 10, 10])

st.markdown('<div class="entel-print-page-break"></div>', unsafe_allow_html=True)
st.markdown('<div class="entel-eng-section" style="--accent:#5f7f75;">4. Sistema de Monitoreo</div>', unsafe_allow_html=True)
st.markdown(
    comment_box(
        "Propuesta técnica de monitoreo para la licitación",
        [
            comment_paragraph(entel_monitoring_intro or "La solución propuesta consolida monitoreo operacional, energético, meteorológico, histórico e integración con sistemas externos para evaluar el piloto en operación real."),
            comment_paragraph("El enfoque de postulación separa capacidades disponibles, capacidades contempladas dentro del primer año y desarrollos de integración evolutiva. Esta separación permite evaluar madurez, riesgo de implementación y cierres requeridos antes de adjudicación/SAT."),
            comment_paragraph(f"Fuente trazable de la matriz: {entel_monitoring_source}. URL: {ENTEL_MONITORING_URL}"),
        ],
    ),
    unsafe_allow_html=True,
)
st.markdown('<div class="entel-eng-section" style="--accent:#5f7f75;">Arquitectura funcional propuesta</div>', unsafe_allow_html=True)
render_entel_fixed_table(entel_monitoring_architecture_df, widths=[15, 28, 24, 8, 25])
st.markdown('<div class="entel-eng-section" style="--accent:#5f7f75;">Lectura estratégica de postulación</div>', unsafe_allow_html=True)
render_entel_fixed_table(entel_monitoring_analysis_df, widths=[18, 35, 17, 30])
st.markdown(
    comment_box(
        "Posicionamiento técnico de la oferta",
        [
            comment_paragraph("La oferta se estructura para entregar visibilidad operacional del piloto desde la puesta en marcha: generación, recurso eólico, rpm, estado, alarmas y eventos quedan como variables base de seguimiento."),
            comment_paragraph("La plataforma propuesta deja trazabilidad para revisión contractual y técnica: históricos, exportación de datos y dashboard deben quedar parametrizados en SAT con frecuencia de registro, permisos de acceso y respaldo definidos."),
            comment_paragraph("Para integración con infraestructura del mandante, la ruta recomendada es cerrar primero Modbus TCP/IP y SCADA; API, MQTT y SNMP se declaran como capacidades evolutivas sujetas a definición de red, seguridad y mapa de variables."),
        ],
    ),
    unsafe_allow_html=True,
)
st.markdown(
    f"""
    <div class="entel-eng-kpi-grid">
      <div class="entel-eng-kpi" style="--accent:#2f5f73;"><div class="entel-eng-kpi__label">Requisitos monitoreo</div><div class="entel-eng-kpi__value">{entel_int_es(entel_monitoring_total)}</div><div class="entel-eng-kpi__sub">Ítems técnicos leídos desde la matriz vinculada.</div></div>
      <div class="entel-eng-kpi" style="--accent:#5f7f75;"><div class="entel-eng-kpi__label">Cumple</div><div class="entel-eng-kpi__value">{entel_int_es(monitoring_cumple)}</div><div class="entel-eng-kpi__sub">Capacidades disponibles desde puesta en marcha o primeros meses.</div></div>
      <div class="entel-eng-kpi" style="--accent:#d9a766;"><div class="entel-eng-kpi__label">Contemplado</div><div class="entel-eng-kpi__value">{entel_int_es(monitoring_contemplado)}</div><div class="entel-eng-kpi__sub">Integraciones planificadas dentro del primer año.</div></div>
      <div class="entel-eng-kpi" style="--accent:#9b4f5f;"><div class="entel-eng-kpi__label">Cobertura lista/plan</div><div class="entel-eng-kpi__value">{entel_num_es(monitoring_ready_pct, 1, "%")}</div><div class="entel-eng-kpi__sub">Suma de capacidades cumplidas y contempladas.</div></div>
    </div>
    """,
    unsafe_allow_html=True,
)
st.markdown('<div class="entel-eng-section" style="--accent:#5f7f75;">Indicadores de cobertura de la postulación</div>', unsafe_allow_html=True)
render_entel_fixed_table(format_entel_display_table(entel_monitoring_status_df, formats={"Participación [%]": "{:.1f}"}), widths=[36, 24, 40])
monitor_con_col1, monitor_con_col2 = st.columns(2)
with monitor_con_col1:
    render_entel_print_safe_chart(entel_monitoring_status_fig, key="consolidated_monitor_status")
with monitor_con_col2:
    render_entel_print_safe_chart(entel_monitoring_section_fig, key="consolidated_monitor_section")
st.markdown('<div class="entel-eng-section" style="--accent:#5f7f75;">Cobertura por familia técnica</div>', unsafe_allow_html=True)
render_entel_fixed_table(format_entel_display_table(entel_monitoring_section_pivot_df, formats={"Cobertura lista o contemplada [%]": "{:.1f}"}), widths=[26, 13, 10, 12, 13, 10, 16])
st.markdown('<div class="entel-eng-section" style="--accent:#5f7f75;">Integración valorada para continuidad operacional</div>', unsafe_allow_html=True)
render_entel_fixed_table(entel_monitoring_integration_df, widths=[13, 16, 27, 18, 20, 6])
st.markdown('<div class="entel-eng-section" style="--accent:#5f7f75;">4. Sistema de Monitoreo</div>', unsafe_allow_html=True)
for family_idx, (family, family_df) in enumerate(entel_monitoring_df.groupby("Familia", sort=False, dropna=False), start=1):
    family_title = str(family).strip() or "Sin familia"
    st.markdown(
        f'<div class="entel-eng-section" style="--accent:#5f7f75;">4.{family_idx} {escape(family_title)}</div>',
        unsafe_allow_html=True,
    )
    render_entel_fixed_table(
        family_df.drop(columns=["Familia"], errors="ignore").reset_index(drop=True),
        widths=[18, 31, 21, 23, 7],
    )
if entel_monitoring_source_note:
    st.caption(entel_monitoring_source_note)

st.markdown('<div class="entel-print-page-break"></div>', unsafe_allow_html=True)
st.markdown('<div class="entel-eng-section" style="--accent:#5f7f75;">5. Condiciones de Instalación</div>', unsafe_allow_html=True)
st.markdown(
    """
    <div class="entel-eng-panel" style="--accent:#5f7f75;">
      <div class="entel-eng-panel__eyebrow">Base documental de instalación</div>
      <div class="entel-eng-panel__title">Documentación técnica y anexos requeridos para montaje, obra civil, fundación, puesta a tierra y seguridad operacional.</div>
    </div>
    """,
    unsafe_allow_html=True,
)
render_entel_fixed_table(entel_proposal_5_view_df, widths=[72, 28])
st.caption(f"Fuente trazable: {entel_installation_conditions_source}. Hoja publicada: 5. Condiciones de Instalación.")

st.markdown('<div class="entel-eng-section" style="--accent:#5f7f75;">6. Experiencia del Proveedor</div>', unsafe_allow_html=True)
if entel_supplier_experience_subtitle:
    st.markdown(
        f"""
        <div class="entel-eng-panel" style="--accent:#5f7f75;">
          <div class="entel-eng-panel__eyebrow">Fuente técnica específica</div>
          <div class="entel-eng-panel__title">{escape(entel_supplier_experience_subtitle)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
st.markdown('<div class="entel-eng-section" style="--accent:#5f7f75;">6.1 Ejes de experiencia y evidencia declarada</div>', unsafe_allow_html=True)
render_entel_fixed_table(entel_proposal_6_summary_df, widths=[7, 23, 70])
if not entel_proposal_6_documents_df.empty:
    st.markdown('<div class="entel-eng-section" style="--accent:#5f7f75;">6.2 Respaldo documental</div>', unsafe_allow_html=True)
    render_entel_fixed_table(entel_proposal_6_documents_df, widths=[7, 63, 30])
if not entel_proposal_6_areas_df.empty:
    st.markdown('<div class="entel-eng-section" style="--accent:#5f7f75;">6.3 Áreas técnicas de experiencia</div>', unsafe_allow_html=True)
    render_entel_fixed_table(entel_proposal_6_areas_df, widths=[7, 38, 55])
if entel_supplier_experience_note:
    st.markdown(
        comment_box("Nota de alcance tecnológico", [comment_paragraph(entel_supplier_experience_note)]),
        unsafe_allow_html=True,
    )
st.caption(f"Fuente trazable: {entel_supplier_experience_source}. Hoja publicada: 6-Experiencia proveedor.")

st.markdown('<div class="entel-print-page-break"></div>', unsafe_allow_html=True)
st.markdown('<div class="entel-eng-section" style="--accent:#d9a766;">7.- Garantias</div>', unsafe_allow_html=True)
if not entel_proposal_7_concepts_df.empty:
    st.markdown('<div class="entel-eng-section" style="--accent:#d9a766;">7.1 Conceptos incluidos</div>', unsafe_allow_html=True)
    render_entel_fixed_table(entel_proposal_7_concepts_view_df, widths=[42, 58])
if not entel_proposal_7_rfp_df.empty:
    st.markdown('<div class="entel-eng-section" style="--accent:#d9a766;">7.2 Recomendación / Solicitud RFP</div>', unsafe_allow_html=True)
    render_entel_fixed_table(entel_proposal_7_rfp_view_df, widths=[28, 37, 35])
if not entel_proposal_7_sla_df.empty:
    st.markdown('<div class="entel-eng-section" style="--accent:#d9a766;">7.3 Garantía de Disponibilidad / SLA de soporte</div>', unsafe_allow_html=True)
    render_entel_fixed_table(entel_proposal_7_sla_view_df, widths=[28, 37, 35])
if not entel_proposal_7_other_df.empty:
    render_entel_fixed_table(entel_proposal_7_other_view_df, widths=[28, 37, 35])
st.markdown('<div class="entel-eng-section" style="--accent:#d9a766;">8. Repuestos y Servicio Local</div>', unsafe_allow_html=True)
for subchapter, subchapter_df in entel_proposal_8_display_df.groupby("Subcapítulo", sort=False, dropna=False):
    subchapter_title = str(subchapter).strip() or "8. Repuestos y Servicio Local"
    if subchapter_title != "8. Repuestos y Servicio Local":
        st.markdown(
            f'<div class="entel-eng-section" style="--accent:#d9a766;">{escape(subchapter_title)}</div>',
            unsafe_allow_html=True,
        )
    render_entel_fixed_table(
        subchapter_df[entel_proposal_table_cols].reset_index(drop=True),
        widths=[28, 37, 35],
    )
if not entel_proposal_9_view_df.empty:
    st.markdown('<div class="entel-eng-section" style="--accent:#d9a766;">9. Importación y Logística</div>', unsafe_allow_html=True)
    render_entel_fixed_table(entel_proposal_9_view_df, widths=[100])
st.markdown('<div class="entel-eng-section" style="--accent:#d9a766;">10. Documentación Técnica Requerida</div>', unsafe_allow_html=True)
render_entel_fixed_table(entel_proposal_10_view_df, widths=[28, 37, 35])
if not entel_proposal_11_view_df.empty:
    st.markdown('<div class="entel-eng-section" style="--accent:#d9a766;">11 - Requisitos de seguridad</div>', unsafe_allow_html=True)
    for category, category_df in entel_proposal_11_view_df.groupby("Categoría", sort=False, dropna=False):
        category_title = str(category).strip() or "Sin categoría"
        category_title = re.sub(r"^(\d+)\.\s*", r"11.\1 ", category_title)
        st.markdown(
            f'<div class="entel-eng-section" style="--accent:#d9a766;">{escape(category_title)}</div>',
            unsafe_allow_html=True,
        )
        render_entel_fixed_table(
            category_df[["Normativa / estándar", "Cumplimiento declarado"]].reset_index(drop=True),
            widths=[72, 28],
        )
if not entel_proposal_12_view_df.empty:
    st.markdown('<div class="entel-eng-section" style="--accent:#d9a766;">12- ALCANCES, SALVEDADES Y EXCEPCIONES DE LA OFERTA TÉCNICA</div>', unsafe_allow_html=True)
    render_entel_fixed_table(entel_proposal_12_view_df, widths=[24, 22, 54])

render_section_download_button(
label="Descargar entregables Entel",
section_title="Entel - entregables RFP",
section_rows=entel_summary_df,
key_suffix="entel_entregables_rfp",
extra_sheets={
    "Introducción": entel_introduction_df,
    "Matriz cumplimiento": entel_delivery_df,
    "Resumen técnico": entel_summary_df,
    "EYA 3.2 sitio": entel_yield_site_df,
    "EYA 3.2 metodología": entel_yield_methodology_df,
    "EYA 3.2 resultados": entel_yield_assessment_df,
    "EYA 3.2 sensibilidades": entel_yield_sensitivity_df,
    "EYA 3.2 dist viento": entel_wind_distribution_df,
    "EYA 3.2 turbul pérdidas": entel_turbulence_losses_df,
    "Sim desempeño KPIs": entel_performance_kpi_df,
    "Sim desempeño supuestos": entel_assumptions_df,
    "Sim desempeño pérdidas": entel_losses_df,
    "Sim curva potencia": entel_performance_curve_df,
    "Aero velocidades Cp": entel_aero_operating_df,
    "Aero curva bins": entel_aero_curve_df,
    "Aero ruido vibración": entel_aero_stability_df,
    "Elect especificación": entel_electrical_specs_df,
    "Elect curva bins": entel_electrical_curve_df,
    "Elect límites": entel_electrical_limits_df,
    "Elect on off grid": entel_grid_modes_df,
    "Elect cierre Entel": entel_electrical_closing_df,
    "Monitoreo matriz": entel_monitoring_df,
    "Monitoreo estados": entel_monitoring_status_df,
    "Monitoreo familias": entel_monitoring_section_pivot_df,
    "Monitoreo arquitectura": entel_monitoring_architecture_df,
    "Monitoreo análisis": entel_monitoring_analysis_df,
    "Monitoreo integración": entel_monitoring_integration_df,
    "Propuesta 5 instalación": entel_proposal_5_view_df,
    "6 experiencia ejes": entel_proposal_6_summary_df,
    "6 experiencia respaldo": entel_proposal_6_documents_df,
    "6 experiencia áreas": entel_proposal_6_areas_df,
    "Propuesta 7 resumen": entel_proposal_point_summary_df,
    "Prop 7 conceptos": entel_proposal_7_concepts_view_df,
    "Prop 7 recomendación": entel_proposal_7_rfp_view_df,
    "Prop 7 disponibilidad": entel_proposal_7_sla_view_df,
    "Propuesta 8 repuestos": entel_proposal_8_view_df,
    "Propuesta 9 logística": entel_proposal_9_view_df,
    "Propuesta 10 docs": entel_proposal_10_view_df,
    "Propuesta 11 seguridad": entel_proposal_11_view_df,
    "Propuesta 12 alcances": entel_proposal_12_view_df,
    "Sensibilidades P50": entel_sensitivity_df,
    "AEP viento medio 4-8": entel_mean_wind_df,
    "Producción mensual": entel_monthly_df,
    "Recurso extrapolado": entel_resource_summary_df,
    "Perfil vertical": active_resource_df,
    "Control parada segura": entel_control_df,
    "SCADA señales": entel_scada_df,
    "Características eléctricas": entel_electrical_df,
    "Garantías SLA logística": entel_service_df,
    "Índice documental": entel_docs_df,
    "Curva potencia bins": entel_power_curve_df,
    "IEC resumen": df_iec.copy() if "df_iec" in globals() else pd.DataFrame(),
},
help_text="Exporta la matriz de cumplimiento y anexos técnicos solicitados en el RFP de Entel.",
)
