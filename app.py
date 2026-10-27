import datetime
import json
import os
import re
import urllib.parse
import urllib.request
import numpy as np
import pandas as pd
import streamlit as st
import yfinance as yf

# 1. Page Configuration
st.set_page_config(
    page_title="The Investing Dean Heat Map",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# 2. Institutional Financial Typography Presets (Default: Modern Fintech Inter)
FONT_PRESETS = {
    "Modern Fintech (Inter)": {
        "family": "'Inter', -apple-system, BlinkMacSystemFont, sans-serif",
        "ticker_size": "1.35rem",
        "pct_size": "1.45rem",
        "price_size": "0.95rem",
        "ticker_weight": "800",
        "pct_weight": "700",
        "price_weight": "500",
        "letter_spacing": "-0.01em",
        "badge": "MODERN FINTECH",
        "desc": "The Silicon Valley benchmark used by Stripe and Robinhood. Crisp geometric neo-grotesque with balanced proportions and tabular numbers.",
    },
    "Oswald (Bloomberg Broadcast)": {
        "family": "'Oswald', sans-serif",
        "ticker_size": "1.45rem",
        "pct_size": "1.55rem",
        "price_size": "0.95rem",
        "ticker_weight": "700",
        "pct_weight": "700",
        "price_weight": "600",
        "letter_spacing": "0.5px",
        "badge": "FINANCIAL BROADCAST",
        "desc": "The CNBC & Bloomberg TV ticker standard. High-impact condensed with authoritative, clear numerals.",
    },
    "Roboto Condensed (Market Data)": {
        "family": "'Roboto Condensed', sans-serif",
        "ticker_size": "1.45rem",
        "pct_size": "1.55rem",
        "price_size": "0.95rem",
        "ticker_weight": "800",
        "pct_weight": "700",
        "price_weight": "600",
        "letter_spacing": "0.5px",
        "badge": "MARKET DATA",
        "desc": "Industry-standard condensed sans used across professional trading platforms, TradingView, and live data feeds.",
    },
    "Libre Franklin (Wall Street Press)": {
        "family": "'Libre Franklin', sans-serif",
        "ticker_size": "1.3rem",
        "pct_size": "1.4rem",
        "price_size": "0.95rem",
        "ticker_weight": "900",
        "pct_weight": "800",
        "price_weight": "700",
        "letter_spacing": "-0.2px",
        "badge": "WALL STREET PRESS",
        "desc": "Classic American financial press workhorse (Wall Street Journal editorial heritage). Heavy, serious, authoritative.",
    },
    "Barlow Semi Condensed (Exchange Floor)": {
        "family": "'Barlow Semi Condensed', sans-serif",
        "ticker_size": "1.45rem",
        "pct_size": "1.55rem",
        "price_size": "0.95rem",
        "ticker_weight": "800",
        "pct_weight": "700",
        "price_weight": "600",
        "letter_spacing": "0.5px",
        "badge": "EXCHANGE FLOOR",
        "desc": "Disciplined, geometric condensed market board typography optimized for high-density financial tickers.",
    },
    "IBM Plex Sans (Enterprise Tech)": {
        "family": "'IBM Plex Sans', sans-serif",
        "ticker_size": "1.3rem",
        "pct_size": "1.4rem",
        "price_size": "0.95rem",
        "ticker_weight": "700",
        "pct_weight": "700",
        "price_weight": "600",
        "letter_spacing": "0.2px",
        "badge": "ENTERPRISE TECH",
        "desc": "Engineered by IBM for mission-critical enterprise systems. Crisp, neutral, and mathematically balanced.",
    },
    "Manrope (Asset Management)": {
        "family": "'Manrope', sans-serif",
        "ticker_size": "1.3rem",
        "pct_size": "1.4rem",
        "price_size": "0.95rem",
        "ticker_weight": "800",
        "pct_weight": "700",
        "price_weight": "600",
        "letter_spacing": "-0.2px",
        "badge": "ASSET MANAGEMENT",
        "desc": "Modern corporate grotesque with open geometry and razor-sharp numeric distinction for wealth managers.",
    },
    "Source Sans 3 (Financial UI)": {
        "family": "'Source Sans 3', sans-serif",
        "ticker_size": "1.35rem",
        "pct_size": "1.45rem",
        "price_size": "0.95rem",
        "ticker_weight": "800",
        "pct_weight": "700",
        "price_weight": "600",
        "letter_spacing": "0px",
        "badge": "FINANCIAL UI",
        "desc": "Adobe's premier UI typeface built specifically for data density, tables, and financial dashboards.",
    },
    "Public Sans (Institutional Standard)": {
        "family": "'Public Sans', sans-serif",
        "ticker_size": "1.3rem",
        "pct_size": "1.4rem",
        "price_size": "0.95rem",
        "ticker_weight": "800",
        "pct_weight": "700",
        "price_weight": "600",
        "letter_spacing": "-0.1px",
        "badge": "INSTITUTIONAL",
        "desc": "US Federal design standard. Clean, neutral, high-trust institutional clarity with strong numbers.",
    },
    "Times Square Board (Bebas Neue)": {
        "family": "'Bebas Neue', Impact, sans-serif",
        "ticker_size": "1.65rem",
        "pct_size": "1.75rem",
        "price_size": "1.05rem",
        "ticker_weight": "400",
        "pct_weight": "400",
        "price_weight": "400",
        "letter_spacing": "1.5px",
        "badge": "TICKER BOARD",
        "desc": "All-caps tall condensed display board font from electronic stock exchange screens.",
    },
}

# 3. Session State Initialization
DEFAULT_TICKERS = [
    "NVDA",
    "TSLA",
    "PLTR",
    "AMD",
    "ARM",
    "AVGO",
    "ALAB",
    "ASML",
    "GOOG",
    "MRVL",
    "MU",
    "TSM",
    "MSFT",
    "AAPL",
    "SKHY",
    "META",
    "SMGB.L",
    "XNAQ.L",
    "SPCX",
    "QQQ",
    "VUAG.L",
    "VWRP.L",
]

if "available_options" not in st.session_state:
    st.session_state.available_options = sorted(
        list(
            set(
                DEFAULT_TICKERS
                + [
                    "SPY",
                    "SMH",
                    "SOXX",
                    "MSTR",
                    "BTC-USD",
                    "ETH-USD",
                    "SOL-USD",
                    "EQQQ.L",
                    "VUSA.L",
                    "IITU.L",
                    "VWRL.L",
                    "AAPL",
                    "MSFT",
                    "AMZN",
                    "META",
                    "SKHY",
                ]
            )
        )
    )

# Multi-User Private Profile & Watchlist Persistence
WATCHLISTS_FILE = "watchlists.json"

def get_current_profile_name() -> str:
    raw_user = st.query_params.get("user", "dean")
    if isinstance(raw_user, list):
        raw_user = raw_user[0] if raw_user else "dean"
    clean = re.sub(r"[^a-zA-Z0-9_\-]", "", str(raw_user)).strip().lower()
    return clean if clean else "dean"

def load_user_watchlist(profile: str, default_list: list) -> list:
    if os.path.exists(WATCHLISTS_FILE):
        try:
            with open(WATCHLISTS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if profile in data and isinstance(data[profile], list) and len(data[profile]) > 0:
                    return data[profile]
        except Exception:
            pass
    return list(default_list)

def save_user_watchlist(profile: str, tickers: list):
    data = {}
    if os.path.exists(WATCHLISTS_FILE):
        try:
            with open(WATCHLISTS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            data = {}
    data[profile] = list(tickers)
    try:
        with open(WATCHLISTS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception:
        pass

current_profile = get_current_profile_name()

if "current_profile" not in st.session_state or st.session_state.current_profile != current_profile:
    st.session_state.current_profile = current_profile
    st.session_state.active_tickers = load_user_watchlist(current_profile, DEFAULT_TICKERS)
    for _t in st.session_state.active_tickers:
        if _t not in st.session_state.available_options:
            st.session_state.available_options.append(_t)

# Normalize any existing LSE tickers added without .L extension
if "active_tickers" in st.session_state:
    st.session_state.active_tickers = [
        f"{t}.L" if t in ["VWRP", "VWRL", "VUAG", "SMGB", "XNAQ", "EQQQ", "VUSA", "IITU"] else t
        for t in st.session_state.active_tickers
    ]
if "available_options" in st.session_state:
    st.session_state.available_options = sorted(
        list(
            set(
                [
                    f"{t}.L" if t in ["VWRP", "VWRL", "VUAG", "SMGB", "XNAQ", "EQQQ", "VUSA", "IITU"] else t
                    for t in st.session_state.available_options
                ]
            )
        )
    )

if "card_font" not in st.session_state:
    st.session_state.card_font = "Modern Fintech (Inter)"

active_font_config = FONT_PRESETS.get(
    st.session_state.card_font, FONT_PRESETS["Modern Fintech (Inter)"]
)

# 4. Complete Dark Mode & 3D CSS Injection
css_content = f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Barlow+Semi+Condensed:wght@600;700;800&family=Bebas+Neue&family=IBM+Plex+Sans:wght@600;700&family=Inter:wght@400;500;600;700;800&family=Libre+Franklin:wght@700;800;900&family=Manrope:wght@600;700;800&family=Oswald:wght@600;700&family=Public+Sans:wght@700;800&family=Roboto+Condensed:wght@600;700;800&family=Source+Sans+3:wght@600;700;800&display=swap');

    /* Global Background & Root Viewport Lock */
    html, body, .stApp {{
        background-color: #080808 !important;
        color: #FFFFFF !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        overflow-x: hidden !important;
        width: 100% !important;
    }}

    /* Hide default Streamlit header and GitHub icon on deployed app */
    header[data-testid="stHeader"] {{
        display: none !important;
        visibility: hidden !important;
        background: transparent !important;
    }}

    /* Ensure the top right toolbar (if any) doesn't force a white background */
    .stApp > header {{
        background-color: transparent !important;
    }}

    /* Push the main app container down slightly to space out the title */
    .block-container,
    div[data-testid="stAppViewBlockContainer"],
    section.main > div.block-container {{
        max-width: 1380px !important;
        width: 100% !important;
        padding-top: 3.5rem !important;
        padding-bottom: 3rem !important;
        padding-left: 20px !important;
        padding-right: 20px !important;
        margin-left: auto !important;
        margin-right: auto !important;
        box-sizing: border-box !important;
    }}
    
    /* Institutional Expander Container */
    [data-testid="stExpander"],
    .stExpander {{
        background-color: #0E0E10 !important;
        border: 1px solid #FACC15 !important;
        border-radius: 8px !important;
        box-shadow: 0 0 10px rgba(250, 204, 21, 0.16), 0 4px 14px rgba(0, 0, 0, 0.5) !important;
        transition: border-color 0.2s ease, box-shadow 0.2s ease !important;
        margin-bottom: 12px !important;
    }}
    [data-testid="stExpander"]:hover {{
        border-color: #FDE047 !important;
        box-shadow: 0 0 16px rgba(250, 204, 21, 0.28), 0 4px 14px rgba(0, 0, 0, 0.5) !important;
    }}
    [data-testid="stExpander"] details {{
        border: none !important;
        background-color: transparent !important;
        border-radius: 8px !important;
    }}
    [data-testid="stExpander"] summary {{
        background-color: #0E0E10 !important;
        color: #FFFFFF !important;
        font-size: 0.78rem !important;
        font-weight: 700 !important;
        letter-spacing: 1.2px !important;
        padding: 10px 16px !important;
        border-radius: 8px !important;
        transition: color 0.2s ease !important;
    }}
    [data-testid="stExpander"] summary:hover {{
        color: #FACC15 !important;
    }}
    [data-testid="stExpander"] summary svg {{
        color: #FACC15 !important;
        fill: #FACC15 !important;
        transition: color 0.2s ease, fill 0.2s ease !important;
    }}
    [data-testid="stExpander"] summary:hover svg {{
        color: #FACC15 !important;
        fill: #FACC15 !important;
    }}
    [data-testid="stExpander"] div[role="region"] {{
        background-color: #0E0E10 !important;
        color: #FFFFFF !important;
        padding: 14px 16px 18px 16px !important;
        border-top: 1px solid #1F1F23 !important;
    }}

    /* Tabs Styling Inside Expander */
    [data-testid="stTabs"] button[role="tab"] {{
        color: #888888 !important;
        font-weight: 700 !important;
        font-size: 0.8rem !important;
        letter-spacing: 0.5px !important;
        border: none !important;
        background: transparent !important;
        padding: 6px 14px !important;
    }}
    [data-testid="stTabs"] button[role="tab"][aria-selected="true"] {{
        color: #FACC15 !important;
        border-bottom: 2px solid #FACC15 !important;
    }}

    /* Multiselect Dropdown & Search Field Dark Theming */
    div[data-baseweb="select"] > div,
    [data-testid="stMultiSelect"] div[data-baseweb="select"] > div,
    [data-testid="stMultiSelect"] [data-testid="stMultiSelectTagsContainer"] {{
        background-color: #141416 !important;
        border: 1px solid #2E2E34 !important;
        color: #FFFFFF !important;
        border-radius: 6px !important;
    }}
    div[data-baseweb="select"] input,
    [data-testid="stMultiSelect"] input {{
        color: #FFFFFF !important;
    }}
    
    /* Multiselect Tag Overrides (Signature Snapshot Brand Yellow #FACC15) */
    [data-testid="stMultiSelect"] [data-tag],
    [data-testid="stMultiSelect"] span[data-tag],
    [data-testid="stMultiSelectTagsContainer"] [data-tag],
    [data-tag],
    span[data-tag],
    div[data-baseweb="tag"], 
    span[data-baseweb="tag"] {{
        background-color: #FACC15 !important;
        background: #FACC15 !important;
        color: #000000 !important;
        border: 1px solid #EAB308 !important;
        border-radius: 4px !important;
        font-weight: 700 !important;
    }}
    [data-testid="stMultiSelect"] [data-tag] span,
    [data-testid="stMultiSelectTagsContainer"] [data-tag] span,
    [data-tag] span,
    span[data-tag] span,
    div[data-baseweb="tag"] span, 
    span[data-baseweb="tag"] span {{
        color: #000000 !important;
        font-weight: 700 !important;
    }}
    [data-testid="stMultiSelect"] [data-tag] button,
    [data-testid="stMultiSelectTagsContainer"] [data-tag] button,
    [data-tag] button {{
        color: #000000 !important;
    }}
    [data-testid="stMultiSelect"] [data-tag] svg,
    [data-testid="stMultiSelectTagsContainer"] [data-tag] svg,
    [data-tag] svg,
    div[data-baseweb="tag"] svg, 
    span[data-baseweb="tag"] svg {{
        fill: #000000 !important;
        color: #000000 !important;
    }}

    /* Disable Downward Arrow & Clunky Dropdown Pop-Up on Multiselect */
    .stExpander div[data-baseweb="select"] svg:not([data-baseweb="tag"] svg):not([data-tag] svg),
    details div[data-baseweb="select"] svg:not([data-baseweb="tag"] svg):not([data-tag] svg),
    [data-testid="stExpander"] div[data-baseweb="select"] svg:not([data-baseweb="tag"] svg):not([data-tag] svg),
    [data-testid="stMultiSelect"] svg:not([data-baseweb="tag"] svg):not([data-tag] svg),
    .stExpander div[data-baseweb="select"] > div > div:last-child,
    details div[data-baseweb="select"] > div > div:last-child,
    [data-testid="stExpander"] div[data-baseweb="select"] > div > div:last-child,
    [data-testid="stMultiSelect"] div[data-baseweb="select"] > div > div:last-child {{
        display: none !important;
        visibility: hidden !important;
        width: 0 !important;
        height: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
        pointer-events: none !important;
    }}
    .stExpander div[data-baseweb="select"] input,
    details div[data-baseweb="select"] input,
    [data-testid="stMultiSelect"] input {{
        display: none !important;
        pointer-events: none !important;
        width: 0 !important;
        min-width: 0 !important;
        opacity: 0 !important;
        position: absolute !important;
    }}
    .stExpander div[data-baseweb="select"],
    details div[data-baseweb="select"],
    [data-testid="stMultiSelect"] div[data-baseweb="select"] {{
        cursor: default !important;
    }}
    div[data-baseweb="popover"]:has([aria-multiselectable="true"]),
    div[data-baseweb="popover"]:has(ul[role="listbox"][aria-multiselectable="true"]) {{
        display: none !important;
        visibility: hidden !important;
        pointer-events: none !important;
    }}

    /* Text Input Field Styling */
    [data-testid="stTextInput"] div[data-baseweb="input"],
    [data-testid="stTextInput"] div[data-baseweb="base-input"],
    [data-testid="stTextInput"] div[data-testid="stTextInputRootElement"],
    [data-testid="stTextInput"] > div > div,
    div[data-baseweb="input"] {{
        background-color: #141416 !important;
        background: #141416 !important;
        border: 1px solid #2E2E34 !important;
        border-radius: 6px !important;
    }}
    [data-testid="stTextInput"] input,
    div[data-baseweb="input"] input {{
        background-color: transparent !important;
        background: transparent !important;
        color: #FFFFFF !important;
        border: none !important;
    }}
    [data-testid="stTextInput"] input::placeholder {{
        color: #71717A !important;
    }}
    [data-testid="stTextInput"] div:focus-within,
    [data-testid="stMultiSelect"] div:focus-within {{
        border-color: #FACC15 !important;
        box-shadow: 0 0 10px rgba(250, 204, 21, 0.4) !important;
    }}

    /* Selectbox Dark Styling */
    div[data-testid="stSelectbox"] div[data-baseweb="select"] > div {{
        background-color: #141416 !important;
        border: 1px solid #2E2E34 !important;
        color: #FFFFFF !important;
        border-radius: 6px !important;
        height: 38px !important;
        font-size: 0.82rem !important;
        font-weight: 600 !important;
    }}
    div[data-testid="stSelectbox"] div[data-baseweb="select"] > div:hover {{
        border-color: #FACC15 !important;
    }}
    div[data-testid="stSelectbox"] div[data-baseweb="select"] span {{
        color: #FFFFFF !important;
    }}
    div[data-testid="stSelectbox"] svg {{
        fill: #A1A1AA !important;
    }}

    /* Dropdown Menu Popover */
    div[data-baseweb="popover"],
    div[data-baseweb="menu"],
    ul[role="listbox"] {{
        background-color: #141416 !important;
        border: 1px solid #2D2D32 !important;
    }}
    li[role="option"] {{
        background-color: #141416 !important;
        color: #E2E8F0 !important;
        font-size: 0.82rem !important;
    }}
    li[role="option"]:hover,
    li[role="option"][aria-selected="true"] {{
        background-color: #27272A !important;
        color: #FACC15 !important;
    }}

    /* =========================================================
       TIMEFRAME SWITCHER - PERFECT SYMMETRICAL DEAD-CENTERING
       ========================================================= */
    div[data-testid="stVerticalBlock"] > div:has(div[data-testid="stRadio"]),
    div[data-testid="stVerticalBlock"] > div:has(.stRadio),
    div[data-testid="stElementContainer"]:has(div[data-testid="stRadio"]),
    div[data-testid="stElementContainer"]:has(.stRadio),
    div.element-container:has(div[data-testid="stRadio"]),
    div.element-container:has(.stRadio),
    div[data-testid="stRadio"],
    div.stRadio {{
        width: 100% !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
        margin-left: auto !important;
        margin-right: auto !important;
        text-align: center !important;
    }}

    /* Completely hide top widget label to eliminate ghost box on the left */
    div[data-testid="stRadio"] > label,
    div[data-testid="stRadio"] [data-testid="stWidgetLabel"],
    div[data-testid="stRadio"] label:not([data-testid="stRadioOption"]) {{
        display: none !important;
        width: 0 !important;
        height: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
        border: none !important;
        position: absolute !important;
        left: -9999px !important;
        visibility: hidden !important;
    }}

    /* Radio group grid container (Centered 4x2 on all viewports) */
    div[data-testid="stRadioGroup"],
    div[data-testid="stRadio"] > div[role="radiogroup"],
    div.stRadio > div[role="radiogroup"] {{
        display: grid !important;
        grid-template-columns: repeat(4, 1fr) !important;
        grid-template-rows: repeat(2, auto) !important;
        gap: 6px !important;
        background-color: #121214 !important;
        padding: 6px !important;
        border-radius: 8px !important;
        border: 1px solid #26262B !important;
        width: 100% !important;
        max-width: 580px !important;
        margin-left: auto !important;
        margin-right: auto !important;
        margin-bottom: 14px !important;
        box-sizing: border-box !important;
    }}

    /* Individual option wrapper */
    div[data-testid="stRadioGroup"] > div {{
        display: flex !important;
        width: 100% !important;
        min-width: 0 !important;
        justify-content: center !important;
        margin: 0 !important;
        padding: 0 !important;
    }}

    /* Inactive State - The Pill */
    div[data-testid="stRadioOption"],
    div[data-testid="stRadioGroup"] label {{
        background-color: #18181B !important;
        border: 1px solid #2E2E34 !important;
        border-radius: 6px !important;
        padding: 8px 4px !important;
        margin: 0 !important;
        cursor: pointer !important;
        transition: all 0.2s ease-in-out !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        text-align: center !important;
        width: 100% !important;
        min-width: 0 !important;
        box-sizing: border-box !important;
    }}

    /* Typography inside the Pill */
    div[data-testid="stRadioOption"] [data-testid="stMarkdownContainer"],
    div[data-testid="stRadioOption"] p,
    div[data-testid="stRadioGroup"] label p {{
        color: #FFFFFF !important;
        font-weight: 700 !important;
        font-size: 0.78rem !important;
        white-space: nowrap !important;
        text-align: center !important;
        margin: 0 !important;
        padding: 0 !important;
        width: 100% !important;
    }}

    /* Completely hide radio circles, dots, marks, SVGs across BaseWeb/Streamlit versions */
    div[data-testid="stRadio"] div[class*="e1dm8mpf4"],
    div[data-testid="stRadio"] div[class*="e1dm8mpf5"],
    div[data-testid="stRadioOption"] > div > div:first-child:not([data-testid="stMarkdownContainer"]),
    div[data-testid="stRadioOption"] label > div:first-child:not([data-testid="stMarkdownContainer"]),
    div[data-testid="stRadioOption"] svg,
    div[data-testid="stRadioOption"] input[type="radio"],
    div[data-testid="stRadio"] input[type="radio"],
    div[data-testid="stRadio"] input[type="radio"] + div,
    div[data-testid="stRadio"] [aria-hidden="true"] {{
        display: none !important;
        width: 0 !important;
        height: 0 !important;
        opacity: 0 !important;
        visibility: hidden !important;
        margin: 0 !important;
        padding: 0 !important;
        border: none !important;
        position: absolute !important;
        left: -9999px !important;
        pointer-events: none !important;
    }}

    /* Active State (Signature Brand Yellow #FACC15) */
    div[data-testid="stRadioGroup"] > div:has(input:checked) [data-testid="stRadioOption"],
    div[data-testid="stRadioOption"]:has(input:checked),
    div[data-testid="stRadioGroup"] label:has(input:checked),
    div[data-testid="stRadioOption"][data-selected="true"] {{
        background-color: #FACC15 !important;
        background: #FACC15 !important;
        border-color: #EAB308 !important;
        box-shadow: 0 0 12px rgba(250, 204, 21, 0.45) !important;
    }}
    div[data-testid="stRadioGroup"] > div:has(input:checked) [data-testid="stRadioOption"] p,
    div[data-testid="stRadioOption"]:has(input:checked) p,
    div[data-testid="stRadioGroup"] label:has(input:checked) p,
    div[data-testid="stRadioOption"][data-selected="true"] p {{
        color: #000000 !important;
        font-weight: 800 !important;
    }}

    /* Native Action Buttons */
    .stButton button {{
        background-color: #141416 !important;
        color: #FFFFFF !important;
        border: 1px solid #2E2E34 !important;
        border-radius: 6px !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
    }}
    .stButton button:hover {{
        border-color: #FACC15 !important;
        color: #FACC15 !important;
    }}

    /* =========================================================
       EXTENDED HOURS TOGGLE - CLEAN TRANSPARENT WITH YELLOW SWITCH ONLY
       ========================================================= */
    div[data-testid="stToggle"],
    div[data-testid="stCheckbox"],
    div[class*="st-key-frag_toggle_ext"] {{
        display: flex !important;
        align-items: center !important;
        height: 100% !important;
        background: transparent !important;
        background-color: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }}
    /* Label and text: strictly transparent background, crisp white readable text */
    div[data-testid="stToggle"] label,
    div[data-testid="stCheckbox"] label,
    div[class*="st-key-frag_toggle_ext"] label,
    div[data-testid="stWidgetLabel"] {{
        background: transparent !important;
        background-color: transparent !important;
        border: none !important;
        box-shadow: none !important;
        color: #E5E7EB !important;
        font-size: 0.82rem !important;
        font-weight: 600 !important;
        cursor: pointer !important;
    }}
    div[data-testid="stToggle"] label p,
    div[data-testid="stCheckbox"] label p,
    div[class*="st-key-frag_toggle_ext"] label p,
    div[data-testid="stWidgetLabel"] p,
    div[data-testid="stWidgetLabel"] span {{
        color: #FFFFFF !important;
        background: transparent !important;
        background-color: transparent !important;
    }}
    /* ONLY the small switch track (pill) turns yellow when checked */
    div[data-testid="stCheckbox"]:has(input:checked) div[class*="e1ap2qgk7"],
    div[data-testid="stToggle"]:has(input:checked) div[class*="e1ap2qgk7"],
    div[class*="st-key-frag_toggle_ext"]:has(input:checked) div[class*="e1ap2qgk7"],
    div[data-testid="stCheckbox"]:has(input:checked) label > div:first-of-type,
    div[data-testid="stToggle"]:has(input:checked) label > div:first-of-type,
    div[class*="st-key-frag_toggle_ext"]:has(input:checked) label > div:first-of-type {{
        background-color: #FACC15 !important;
        background: #FACC15 !important;
        border-color: #EAB308 !important;
        box-shadow: 0 0 10px rgba(250, 204, 21, 0.45) !important;
    }}
    /* The round sliding knob stays clean white */
    div[data-testid="stCheckbox"]:has(input:checked) div[class*="e1ap2qgk7"] > div,
    div[data-testid="stToggle"]:has(input:checked) div[class*="e1ap2qgk7"] > div,
    div[class*="st-key-frag_toggle_ext"]:has(input:checked) div[class*="e1ap2qgk7"] > div,
    div[data-testid="stCheckbox"]:has(input:checked) label > div:first-of-type > div,
    div[data-testid="stToggle"]:has(input:checked) label > div:first-of-type > div,
    div[class*="st-key-frag_toggle_ext"]:has(input:checked) label > div:first-of-type > div {{
        background-color: #FFFFFF !important;
        background: #FFFFFF !important;
    }}

    /* 6-to-a-Row Centered Grid Layout (Zero Overflow) */
    .heatmap-container {{
        width: 100% !important;
        max-width: 1340px !important;
        margin: 0 auto !important;
        padding: 0 !important;
        box-sizing: border-box !important;
    }}
    .section-container {{
        width: 100% !important;
        margin-bottom: 26px !important;
    }}
    .section-header {{
        display: flex;
        align-items: center;
        gap: 10px;
        margin-top: 18px;
        margin-bottom: 12px;
        padding-bottom: 8px;
        border-bottom: 1px solid #1E1E22;
    }}
    .section-title {{
        font-size: 0.82rem;
        font-weight: 800;
        letter-spacing: 1.6px;
        color: #E2E8F0;
        text-transform: uppercase;
    }}
    .section-badge {{
        font-size: 0.65rem;
        font-weight: 800;
        letter-spacing: 0.8px;
        color: #000000;
        background: #FACC15;
        padding: 2px 7px;
        border-radius: 4px;
        text-transform: uppercase;
    }}
    .heatmap-grid {{
        display: flex !important;
        flex-wrap: wrap !important;
        justify-content: center !important;
        gap: 10px !important;
        width: 100% !important;
        margin: 0 auto !important;
        box-sizing: border-box !important;
    }}
    @media (max-width: 1100px) and (min-width: 601px) {{
        .heatmap-grid {{
            display: flex !important;
            flex-wrap: wrap !important;
            justify-content: center !important;
            gap: 8px !important;
        }}
        .heatmap-card {{
            flex: 0 0 calc((100% - 16px) / 3) !important;
            max-width: calc((100% - 16px) / 3) !important;
            width: calc((100% - 16px) / 3) !important;
        }}
    }}

    /* 3D Tactile Card Styling with Active Typography Injection */
    .heatmap-card {{
        font-family: {active_font_config['family']} !important;
        font-variant-numeric: tabular-nums;
        font-feature-settings: "tnum" 1;
        flex: 0 0 calc((100% - 50px) / 6) !important;
        max-width: calc((100% - 50px) / 6) !important;
        width: calc((100% - 50px) / 6) !important;
        min-height: 135px;
        min-width: 0 !important;
        box-sizing: border-box !important;
        border-radius: 8px;
        padding: 12px 6px 10px 6px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
        box-shadow: inset 1px 1px 1px rgba(255, 255, 255, 0.2), 
                    inset -1px -1px 2px rgba(0, 0, 0, 0.8), 
                    0 6px 12px rgba(0, 0, 0, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.08);
        transition: transform 0.15s ease, box-shadow 0.15s ease;
        user-select: none;
        overflow: hidden !important;
        cursor: pointer !important;
        text-decoration: none !important;
        color: inherit !important;
    }}
    .heatmap-card:hover {{
        transform: translateY(-3px);
        box-shadow: inset 1px 1px 1px rgba(255, 255, 255, 0.3), 
                    0 8px 20px rgba(250, 204, 21, 0.25);
        border-color: rgba(250, 204, 21, 0.6);
        text-decoration: none !important;
    }}
    .card-ticker {{
        font-family: {active_font_config['family']} !important;
        font-size: clamp(1.1rem, 1.35vw, {active_font_config['ticker_size']}) !important;
        font-weight: {active_font_config['ticker_weight']} !important;
        letter-spacing: {active_font_config['letter_spacing']} !important;
        color: #FACC15;
        margin-bottom: 1px;
        line-height: 1.1;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.9);
        white-space: nowrap;
    }}
    .card-name {{
        font-family: {active_font_config['family']} !important;
        font-size: clamp(0.72rem, 0.82vw, 0.82rem) !important;
        color: #F1F5F9 !important;
        font-weight: 600 !important;
        letter-spacing: 0.2px !important;
        margin-bottom: 4px;
        line-height: 1.2;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        max-width: 95%;
        text-shadow: 0 1px 3px rgba(0, 0, 0, 0.95);
        opacity: 0.92;
    }}
    .card-pct {{
        font-family: {active_font_config['family']} !important;
        font-size: clamp(1.2rem, 1.45vw, {active_font_config['pct_size']}) !important;
        font-weight: {active_font_config['pct_weight']} !important;
        color: #FFFFFF;
        margin-bottom: 2px;
        text-shadow: 0 1px 3px rgba(0,0,0,0.8);
        line-height: 1.15;
        white-space: nowrap;
    }}
    .card-price {{
        font-family: {active_font_config['family']} !important;
        font-size: clamp(0.82rem, 0.95vw, {active_font_config['price_size']}) !important;
        color: #E2E8F0;
        font-weight: {active_font_config['price_weight']} !important;
        line-height: 1.1;
        white-space: nowrap;
    }}

    /* Institutional Extended Session (Pre/Post Market) Pill - Zero Emojis */
    .card-ext {{
        display: inline-flex;
        align-items: center;
        justify-content: center;
        gap: 4px;
        margin-top: 6px;
        padding: 2px 6px;
        border-radius: 4px;
        background: rgba(10, 10, 12, 0.75);
        border: 1px solid rgba(255, 255, 255, 0.1);
        font-size: clamp(0.66rem, 0.74vw, 0.74rem);
        letter-spacing: 0.1px;
        backdrop-filter: blur(4px);
        max-width: 96%;
        box-sizing: border-box;
        white-space: nowrap;
    }}
    .ext-metrics {{
        display: inline-flex;
        align-items: center;
        gap: 4px;
        white-space: nowrap;
    }}
    .ext-tag {{
        display: inline-flex;
        align-items: center;
        gap: 3.5px;
        font-weight: 800;
        font-size: 0.62rem;
        padding: 1.5px 5px;
        border-radius: 3px;
        letter-spacing: 0.8px;
        line-height: 1;
        text-transform: uppercase;
    }}
    .ext-dot {{
        width: 4px;
        height: 4px;
        border-radius: 50%;
        display: inline-block;
    }}
    .ext-pre {{
        background: rgba(245, 158, 11, 0.15);
        color: #FBBF24;
        border: 1px solid rgba(245, 158, 11, 0.4);
    }}
    .ext-pre .ext-dot {{
        background-color: #FBBF24;
        box-shadow: 0 0 4px #FBBF24;
    }}
    .ext-post {{
        background: rgba(56, 189, 248, 0.15);
        color: #38BDF8;
        border: 1px solid rgba(56, 189, 248, 0.4);
    }}
    .ext-post .ext-dot {{
        background-color: #38BDF8;
        box-shadow: 0 0 4px #38BDF8;
    }}
    @keyframes pulse-live {{
        0% {{ opacity: 1; transform: scale(1); }}
        50% {{ opacity: 0.45; transform: scale(0.85); }}
        100% {{ opacity: 1; transform: scale(1); }}
    }}
    .ext-live {{
        background: rgba(34, 197, 94, 0.15) !important;
        color: #4ADE80 !important;
        border: 1px solid rgba(34, 197, 94, 0.4) !important;
    }}
    .ext-live .ext-dot {{
        background-color: #4ADE80 !important;
        box-shadow: 0 0 5px #4ADE80 !important;
        animation: pulse-live 2s infinite ease-in-out !important;
    }}
    .ext-price {{
        color: #E2E8F0;
        font-weight: 600;
        font-size: 0.76rem;
    }}
    .ext-pct.positive {{
        color: #4ADE80;
        font-weight: 700;
        font-size: 0.76rem;
    }}
    .ext-pct.negative {{
        color: #F87171;
        font-weight: 700;
        font-size: 0.76rem;
    }}
    .ext-pct.neutral {{
        color: #9CA3AF;
        font-weight: 600;
        font-size: 0.76rem;
    }}

    /* Tablet & Medium Screens (Max-Width: 768px) - 4 Timeframes per row across 2 rows */
    @media (max-width: 768px) {{
        div[data-testid="stElementContainer"]:has(div[data-testid="stRadio"]),
        div[data-testid="stElementContainer"]:has(.stRadio),
        div.element-container:has(div[data-testid="stRadio"]),
        div.element-container:has(.stRadio) {{
            width: 100% !important;
            display: flex !important;
            flex-direction: column !important;
            align-items: center !important;
            justify-content: center !important;
        }}
        div[data-testid="stRadio"],
        div.stRadio {{
            width: 100% !important;
            display: flex !important;
            justify-content: center !important;
            align-items: center !important;
            margin-left: auto !important;
            margin-right: auto !important;
        }}
        div[data-testid="stRadioGroup"],
        div[data-testid="stRadio"] > div[role="radiogroup"],
        div.stRadio > div[role="radiogroup"] {{
            display: grid !important;
            grid-template-columns: repeat(4, 1fr) !important;
            grid-template-rows: repeat(2, auto) !important;
            gap: 5px !important;
            padding: 5px !important;
            width: 100% !important;
            max-width: 540px !important;
            margin-left: auto !important;
            margin-right: auto !important;
            box-sizing: border-box !important;
        }}
        div[data-testid="stRadioOption"],
        div[data-testid="stRadioGroup"] label {{
            width: 100% !important;
            min-width: 0 !important;
            padding: 7px 2px !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            text-align: center !important;
            box-sizing: border-box !important;
        }}
        div[data-testid="stRadioOption"] p,
        div[data-testid="stRadioGroup"] label p {{
            font-size: 0.70rem !important;
            font-weight: 700 !important;
            white-space: nowrap !important;
            text-align: center !important;
            margin: 0 !important;
        }}
    }}

    /* =========================================================
       MOBILE VIEWPORT OPTIMISATIONS (MAX-WIDTH: 600PX)
       Strict containment, 3-tiles per row, zero overlap
       ========================================================= */
    @media (max-width: 600px) {{
        .block-container,
        .stMainBlockContainer,
        div[data-testid="stAppViewBlockContainer"],
        section.main > div.block-container {{
            padding-left: 8px !important;
            padding-right: 8px !important;
            padding-top: 1.25rem !important;
        }}
        div[data-testid="stElementContainer"]:has(div[data-testid="stRadio"]),
        div[data-testid="stElementContainer"]:has(.stRadio),
        div.element-container:has(div[data-testid="stRadio"]),
        div.element-container:has(.stRadio) {{
            width: 100% !important;
            display: flex !important;
            flex-direction: column !important;
            align-items: center !important;
            justify-content: center !important;
        }}
        div[data-testid="stRadio"],
        div.stRadio {{
            margin-left: auto !important;
            margin-right: auto !important;
            width: 100% !important;
            display: flex !important;
            justify-content: center !important;
            align-items: center !important;
        }}
        div[data-testid="stRadioGroup"],
        div[data-testid="stRadio"] > div[role="radiogroup"],
        div.stRadio > div[role="radiogroup"] {{
            display: grid !important;
            grid-template-columns: repeat(4, 1fr) !important;
            grid-template-rows: repeat(2, auto) !important;
            gap: 4px !important;
            padding: 4px !important;
            width: 100% !important;
            max-width: 100% !important;
            margin-left: auto !important;
            margin-right: auto !important;
            box-sizing: border-box !important;
        }}
        div[data-testid="stRadioOption"],
        div[data-testid="stRadioGroup"] label {{
            width: 100% !important;
            min-width: 0 !important;
            padding: 7px 1px !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            text-align: center !important;
            box-sizing: border-box !important;
            border-radius: 5px !important;
        }}
        div[data-testid="stRadioOption"] p,
        div[data-testid="stRadioGroup"] label p {{
            font-size: clamp(0.55rem, 2.2vw, 0.67rem) !important;
            font-weight: 700 !important;
            white-space: nowrap !important;
            text-align: center !important;
            margin: 0 !important;
            letter-spacing: -0.2px !important;
        }}
        .heatmap-grid {{
            display: grid !important;
            grid-template-columns: repeat(3, minmax(0, 1fr)) !important;
            gap: 6px !important;
        }}
        .heatmap-card {{
            flex: initial !important;
            width: 100% !important;
            max-width: 100% !important;
            min-height: 130px !important;
            padding: 7px 4px 6px 4px !important;
            border-radius: 6px !important;
            display: flex !important;
            flex-direction: column !important;
            justify-content: center !important;
            align-items: center !important;
            overflow: hidden !important;
            box-sizing: border-box !important;
            cursor: pointer !important;
            text-decoration: none !important;
            color: inherit !important;
        }}
        .card-ticker {{
            font-size: 0.94rem !important;
            margin-bottom: 0px !important;
            line-height: 1.05 !important;
        }}
        .card-name {{
            font-size: 0.58rem !important;
            margin-bottom: 2px !important;
            line-height: 1.15 !important;
            max-width: 95% !important;
            overflow: hidden !important;
            text-overflow: ellipsis !important;
            white-space: nowrap !important;
        }}
        .card-pct {{
            font-size: 1.00rem !important;
            margin-bottom: 1px !important;
            line-height: 1.1 !important;
        }}
        .card-price {{
            font-size: 0.72rem !important;
            line-height: 1.05 !important;
            margin-bottom: 0px !important;
        }}
        /* Mobile Extended Session Pill: Clean 2-Row Stack with FULL Price Visibility */
        .card-ext {{
            display: flex !important;
            flex-direction: column !important;
            align-items: center !important;
            justify-content: center !important;
            gap: 2px !important;
            margin-top: 3px !important;
            margin-bottom: 0px !important;
            padding: 2.5px 5px !important;
            border-radius: 4px !important;
            width: calc(100% - 6px) !important;
            max-width: 98% !important;
            box-sizing: border-box !important;
            background: rgba(10, 10, 12, 0.85) !important;
        }}
        .ext-tag {{
            font-size: 0.50rem !important;
            padding: 1px 4px !important;
            gap: 2px !important;
            letter-spacing: 0.5px !important;
            line-height: 1 !important;
        }}
        .ext-dot {{
            width: 3px !important;
            height: 3px !important;
        }}
        .ext-metrics {{
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            gap: 4px !important;
            width: 100% !important;
            white-space: nowrap !important;
        }}
        .ext-price {{
            font-size: 0.65rem !important;
            color: #F1F5F9 !important;
            font-weight: 600 !important;
            white-space: nowrap !important;
            overflow: visible !important;
            max-width: none !important;
            line-height: 1.1 !important;
        }}
        .ext-pct {{
            font-size: 0.65rem !important;
            font-weight: 700 !important;
            white-space: nowrap !important;
            line-height: 1.1 !important;
        }}
    }}

    /* Institutional Asset Modal Dialog Styling */
    div[data-testid="stDialog"],
    .stDialog {{
        background-color: rgba(0, 0, 0, 0.75) !important;
    }}
    section[role="dialog"],
    [data-testid="stDialog"] > div,
    [data-testid="stDialog"] section {{
        background-color: #0A0D14 !important;
        border: 1px solid #1E293B !important;
        border-radius: 16px !important;
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.9) !important;
        color: #FFFFFF !important;
    }}
    div[data-testid="stDialog"] header,
    section[role="dialog"] header,
    div[role="dialog"] header {{
        background: transparent !important;
        border-bottom: none !important;
    }}
    div[data-testid="stDialog"] header button,
    section[role="dialog"] header button,
    div[role="dialog"] header button {{
        color: #94A3B8 !important;
    }}
    div[data-testid="stDialog"] header button:hover,
    section[role="dialog"] header button:hover,
    div[role="dialog"] header button:hover {{
        color: #FACC15 !important;
    }}

    /* Modal Responsive Grids */
    .modal-fundamentals-grid {{
        display: grid !important;
        grid-template-columns: repeat(4, minmax(0, 1fr)) !important;
        gap: 8px !important;
        width: 100% !important;
        box-sizing: border-box !important;
    }}
    .modal-fundamentals-grid > div {{
        min-width: 0 !important;
        box-sizing: border-box !important;
    }}
    .modal-scorecard-grid {{
        display: grid !important;
        grid-template-columns: repeat(4, minmax(0, 1fr)) !important;
        gap: 8px !important;
        width: 100% !important;
        box-sizing: border-box !important;
    }}
    .modal-scorecard-grid > div {{
        min-width: 0 !important;
        box-sizing: border-box !important;
    }}
    .modal-lower-grid {{
        display: grid !important;
        grid-template-columns: 1fr 1fr !important;
        gap: 10px !important;
        margin-bottom: 16px !important;
        width: 100% !important;
        box-sizing: border-box !important;
    }}
    .modal-lower-grid > div {{
        min-width: 0 !important;
        box-sizing: border-box !important;
    }}

    /* Header Title & Subtitle */
    .main-title {{
        margin: 15px 0 0 0 !important;
        font-size: 2.3rem !important;
        font-weight: 800 !important;
        color: #FFFFFF !important;
        letter-spacing: -0.5px !important;
        line-height: 1.15 !important;
    }}
    .title-line-1 {{
        display: inline;
    }}
    .title-line-2 {{
        display: inline;
        margin-left: 0.25em;
    }}
    .main-subtitle {{
        margin: 4px 0 0 0 !important;
        color: #888888 !important;
        font-size: 0.82rem !important;
        letter-spacing: 2px !important;
        font-weight: 600 !important;
        line-height: 1.35 !important;
    }}
    .sub-line-1 {{
        display: inline;
    }}
    .sub-line-2 {{
        display: inline;
        margin-left: 0.35em;
    }}

    /* Mobile Modal & Viewport Lock */
    @media (max-width: 600px) {{
        html, body, .stApp, [data-testid="stAppViewContainer"], .main {{
            overflow-x: hidden !important;
            max-width: 100vw !important;
            width: 100vw !important;
        }}

        /* Force Title & Subtitle 2-line break on all mobile screens and fill screen */
        .main-title {{
            font-size: clamp(2.05rem, 9.8vw, 2.75rem) !important;
            line-height: 1.1 !important;
            letter-spacing: -0.6px !important;
            margin: 6px 0 0 0 !important;
        }}
        .title-line-1 {{
            display: block !important;
            white-space: nowrap !important;
        }}
        .title-line-2 {{
            display: block !important;
            white-space: nowrap !important;
            margin-left: 0 !important;
            margin-top: 3px !important;
        }}
        .main-subtitle {{
            font-size: clamp(0.68rem, 2.7vw, 0.78rem) !important;
            letter-spacing: 2px !important;
            margin-top: 6px !important;
            line-height: 1.35 !important;
        }}
        .sub-line-1 {{
            display: block !important;
            white-space: nowrap !important;
        }}
        .sub-line-2 {{
            display: block !important;
            white-space: nowrap !important;
            margin-left: 0 !important;
            margin-top: 1px !important;
        }}

        /* Fullscreen scrollable backdrop for mobile dialog */
        div[data-testid="stDialog"],
        .stDialog {{
            position: fixed !important;
            top: 0 !important;
            left: 0 !important;
            right: 0 !important;
            bottom: 0 !important;
            width: 100% !important;
            height: 100% !important;
            overflow-y: auto !important;
            overflow-x: hidden !important;
            -webkit-overflow-scrolling: touch !important;
            display: flex !important;
            justify-content: center !important;
            align-items: flex-start !important;
            padding: 10px 6px 36px 6px !important;
            margin: 0 !important;
            box-sizing: border-box !important;
            z-index: 999999 !important;
        }}

        /* Target ONLY the modal window frame */
        div[data-testid="stDialog"] > div,
        div[data-testid="stDialog"] div.ep9mgll1,
        div.stDialog > div,
        div.stDialog div.ep9mgll1,
        [data-testid="stDialog"] section,
        section[role="dialog"] {{
            width: 96vw !important;
            max-width: 96vw !important;
            min-width: 0 !important;
            margin: 8px auto 24px auto !important;
            position: relative !important;
            top: 0 !important;
            left: 0 !important;
            transform: none !important;
            box-sizing: border-box !important;
            border-radius: 14px !important;
        }}

        /* Dialog inner content wrapper padding */
        div[data-testid="stDialog"] section,
        section[role="dialog"],
        div[data-testid="stDialog"] .ep9mgll6 {{
            padding: 10px 8px !important;
            box-sizing: border-box !important;
            width: 100% !important;
            max-width: 100% !important;
        }}

        div[data-testid="stDialog"] header,
        section[role="dialog"] header,
        div[data-testid="stDialog"] h2 {{
            width: 100% !important;
            max-width: 100% !important;
            min-width: 0 !important;
            padding: 4px 6px 0 6px !important;
            box-sizing: border-box !important;
            font-size: 1.0rem !important;
        }}

        .modal-header-container {{
            flex-direction: column !important;
            align-items: flex-start !important;
            gap: 6px !important;
        }}
        .modal-header-price {{
            text-align: left !important;
        }}
        .modal-fundamentals-grid {{
            grid-template-columns: repeat(2, minmax(0, 1fr)) !important;
            gap: 6px !important;
            width: 100% !important;
        }}
        .modal-fundamentals-grid > div {{
            width: 100% !important;
            min-width: 0 !important;
            padding: 8px 4px !important;
            box-sizing: border-box !important;
        }}
        .modal-scorecard-grid {{
            grid-template-columns: repeat(4, minmax(0, 1fr)) !important;
            gap: 4px !important;
            width: 100% !important;
        }}
        .modal-scorecard-grid > div {{
            width: 100% !important;
            min-width: 0 !important;
            padding: 6px 2px !important;
            box-sizing: border-box !important;
        }}
        .modal-lower-grid {{
            grid-template-columns: 1fr !important;
            gap: 8px !important;
            margin-bottom: 12px !important;
            width: 100% !important;
        }}
        .modal-lower-grid > div {{
            width: 100% !important;
            min-width: 0 !important;
            box-sizing: border-box !important;
        }}
    }}
</style>
"""

st.markdown(css_content, unsafe_allow_html=True)


# 5. Colour Interpolation Logic (-5% to +5%)
def get_heat_color(pct):
    if pct is None or np.isnan(pct):
        return "#262626"

    # Clamp value between -5.0 and +5.0
    clamped = max(-5.0, min(5.0, pct))

    if clamped > 0:
        # Interpolate between Neutral Dark (#222222) and Vibrant Green (#15803d)
        ratio = clamped / 5.0
        r = int(34 + ratio * (21 - 34))
        g = int(34 + ratio * (128 - 34))
        b = int(34 + ratio * (61 - 34))
    else:
        # Interpolate between Neutral Dark (#222222) and Deep Red (#991b1b)
        ratio = abs(clamped) / 5.0
        r = int(34 + ratio * (153 - 34))
        g = int(34 + ratio * (27 - 34))
        b = int(34 + ratio * (27 - 34))

    return f"rgb({r}, {g}, {b})"


# Global Currency Mapping for Future Asset Additions
GLOBAL_CURRENCY_SYMBOLS = {
    "USD": "$",
    "GBP": "£",
    "GBp": "£",
    "GBX": "£",
    "EUR": "€",
    "JPY": "¥",
    "CHF": "CHF ",
    "CAD": "C$",
    "AUD": "A$",
    "HKD": "HK$",
    "SGD": "S$",
}

# Curated Asset Names for Beginner Clarity
KNOWN_ASSET_NAMES = {
    "NVDA": "NVIDIA",
    "TSLA": "Tesla",
    "PLTR": "Palantir",
    "AMD": "Advanced Micro Devices",
    "ARM": "Arm Holdings",
    "AVGO": "Broadcom",
    "ALAB": "Astera Labs",
    "ASML": "ASML",
    "GOOG": "Alphabet (Google)",
    "GOOGL": "Alphabet (Google)",
    "MRVL": "Marvell Technology",
    "MU": "Micron Technology",
    "TSM": "TSMC",
    "SMGB.L": "VanEck Semiconductor ETF",
    "XNAQ.L": "Xtrackers Nasdaq 100 ETF",
    "VWRP.L": "Vanguard FTSE All-World",
    "VWRL.L": "Vanguard FTSE All-World",
    "VWRD.L": "Vanguard FTSE All-World (USD)",
    "QQQ": "Invesco QQQ Trust",
    "SPY": "SPDR S&P 500 ETF",
    "SMH": "VanEck Semiconductor ETF",
    "SOXX": "iShares Semiconductor ETF",
    "MSTR": "MicroStrategy",
    "BTC-USD": "Bitcoin",
    "ETH-USD": "Ethereum",
    "SOL-USD": "Solana",
    "VUAG.L": "Vanguard S&P 500 ETF",
    "EQQQ.L": "Invesco Nasdaq 100 ETF",
    "VUSA.L": "Vanguard S&P 500 ETF",
    "IITU.L": "iShares S&P 500 Info Tech",
    "SPCX": "SpaceX Holdings",
    "AAPL": "Apple",
    "MSFT": "Microsoft",
    "SKHY": "SK hynix",
    "AMZN": "Amazon",
    "META": "Meta Platforms",
    "RR.L": "Rolls-Royce Holdings",
    "BA.L": "BAE Systems",
    "AZN.L": "AstraZeneca",
    "SHEL.L": "Shell",
    "BP.L": "BP",
    "HSBA.L": "HSBC Holdings",
    "ULVR.L": "Unilever",
}

def format_display_name(ticker, info):
    t_up = ticker.upper()
    if t_up in KNOWN_ASSET_NAMES:
        return KNOWN_ASSET_NAMES[t_up]
    raw = info.get("shortName") or info.get("longName") or ""
    if not raw:
        return ticker
    # Clean verbose legal entity prefixes
    if raw.upper().startswith("VANGUARD FUNDS PLC "):
        raw = "Vanguard " + raw[19:]
    elif raw.upper().startswith("XTRACKERS (IE) PUBLIC LIMITED C"):
        raw = "Xtrackers " + raw[31:]
    # Clean verbose legal entity suffixes
    for suffix in [", Inc.", " Inc.", " Inc", ", LLC", " LLC", " Corporation", " Corp.", " Corp", " Co.", " plc", " PLC", " Public Limited Company"]:
        if raw.endswith(suffix):
            raw = raw[:-len(suffix)]
    return raw.strip()

# Interactive Ticker & Company Search Functionality
@st.cache_data(ttl=300)
def search_tickers(query: str):
    q_clean = query.strip()
    if not q_clean or len(q_clean) < 2:
        return []
    try:
        url = f"https://query2.finance.yahoo.com/v1/finance/search?q={urllib.parse.quote(q_clean)}&quotesCount=8&newsCount=0"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=3.5) as resp:
            data = json.loads(resp.read().decode())
            results = []
            for q in data.get("quotes", []):
                sym = q.get("symbol")
                if not sym:
                    continue
                qtype = q.get("quoteType", "")
                if qtype in ["EQUITY", "ETF", "MUTUALFUND", "CRYPTOCURRENCY"] or not qtype:
                    name = q.get("shortname") or q.get("longname") or sym
                    if sym.upper() in KNOWN_ASSET_NAMES:
                        display_name = KNOWN_ASSET_NAMES[sym.upper()]
                    else:
                        display_name = name
                    results.append({
                        "symbol": sym,
                        "name": display_name,
                        "type": qtype,
                        "exchange": q.get("exchDisp") or q.get("exchange") or "",
                    })
            return results
    except Exception:
        return []

# 6. Market Data Fetcher with Pre/Post Market Extended Pricing
@st.cache_data(ttl=60)
def fetch_ticker_data(ticker):
    try:
        t = yf.Ticker(ticker)
        # Fetch 5Y history with nominal prices (matching Yahoo Finance web UI)
        hist = t.history(period="5y", auto_adjust=False)
        if hist.empty:
            return None
        # Discard any incomplete or provisional candles where Close is missing or zero (common in delayed ETF reporting)
        hist = hist.dropna(subset=["Close"])
        hist = hist[hist["Close"] > 0]
        if hist.empty or len(hist) < 2:
            return None

        current_price = float(hist["Close"].iloc[-1])
        last_dt = hist.index[-1]

        def get_historical_close(target_dt):
            past = hist[hist.index <= target_dt]
            return float(past["Close"].iloc[-1]) if not past.empty else float(hist["Close"].iloc[0])

        # 1D: Return compared to previous trading day's closing price
        p_1d = float(hist["Close"].iloc[-2])

        # 1W: Return compared to 7 calendar days ago (closest trading session on or before)
        p_1w = get_historical_close(last_dt - pd.Timedelta(days=7))

        # 1M: Return compared to 1 calendar month ago (closest trading session on or before)
        p_1m = get_historical_close(last_dt - pd.DateOffset(months=1))

        # 3M: Return compared to 3 calendar months ago (closest trading session on or before)
        p_3m = get_historical_close(last_dt - pd.DateOffset(months=3))

        # 6M: Return compared to 6 calendar months ago (closest trading session on or before)
        p_6m = get_historical_close(last_dt - pd.DateOffset(months=6))

        # YTD: Return compared to the final close of the previous calendar year
        cur_year = last_dt.year
        prev_year_df = hist[hist.index.year < cur_year]
        if not prev_year_df.empty:
            p_ytd = float(prev_year_df["Close"].iloc[-1])
        else:
            p_ytd = float(hist["Close"].iloc[0])

        # 1Y: Return compared to 1 calendar year ago (closest trading session on or before)
        p_1y = get_historical_close(last_dt - pd.DateOffset(years=1))

        # 5Y: Return compared to 5 calendar years ago (closest trading session on or before)
        p_5y = get_historical_close(last_dt - pd.DateOffset(years=5))

        # Determine currency and detect whether quote is in pence (GBp) or pounds (GBP)
        info = t.info if hasattr(t, "info") else {}
        raw_currency = getattr(t.fast_info, "currency", None) or info.get("currency", None)
        currency = GLOBAL_CURRENCY_SYMBOLS.get(raw_currency, "£" if ticker.upper().endswith(".L") else "$")

        is_pence = False
        if raw_currency in ["GBp", "GBX"]:
            is_pence = True
        elif raw_currency is None and ticker.upper().endswith(".L") and current_price > 800:
            is_pence = True

        # Fetch Pre-Market and Post-Market Extended Hours info (with Cloud-resilient fallback)
        ext_data = None
        pre_p = info.get("preMarketPrice") if info else None
        pre_pct = info.get("preMarketChangePercent") if info else None
        post_p = info.get("postMarketPrice") if info else None
        post_pct = info.get("postMarketChangePercent") if info else None

        if pre_p is not None and pre_p > 0 and pre_pct is not None:
            ext_price = float(pre_p)
            if is_pence:
                ext_price = ext_price / 100.0
            ext_data = {
                "session": "PRE",
                "price": ext_price,
                "pct": float(pre_pct),
            }
        elif post_p is not None and post_p > 0 and post_pct is not None:
            ext_price = float(post_p)
            if is_pence:
                ext_price = ext_price / 100.0
            ext_data = {
                "session": "POST",
                "price": ext_price,
                "pct": float(post_pct),
            }
        else:
            # Cloud-resilient fallback: t.get_history_metadata() is loaded with t.history() and NEVER blocked on cloud IPs
            try:
                meta = t.get_history_metadata() or {}
                periods = meta.get("currentTradingPeriod", {})
                now_utc = pd.Timestamp.now(tz="UTC")
                pre_info = periods.get("pre", {})
                post_info = periods.get("post", {})

                is_pre = (pre_info.get("start") <= now_utc <= pre_info.get("end")) if (pre_info.get("start") and pre_info.get("end")) else False
                is_post = (post_info.get("start") <= now_utc <= post_info.get("end")) if (post_info.get("start") and post_info.get("end")) else False

                fullday_p = meta.get("fulldayPrice")
                fullday_pct = meta.get("fulldayChangePercent")
                reg_p = meta.get("regularMarketPrice") or current_price

                if is_pre and fullday_p and fullday_p > 0 and fullday_p != reg_p:
                    ext_price = float(fullday_p)
                    if is_pence:
                        ext_price = ext_price / 100.0
                    ext_pct = float(fullday_pct) if fullday_pct is not None else (((ext_price - current_price) / current_price) * 100.0 if current_price > 0 else 0.0)
                    ext_data = {
                        "session": "PRE",
                        "price": ext_price,
                        "pct": ext_pct,
                    }
                elif is_post and fullday_p and fullday_p > 0 and fullday_p != reg_p:
                    ext_price = float(fullday_p)
                    if is_pence:
                        ext_price = ext_price / 100.0
                    ext_pct = float(fullday_pct) if fullday_pct is not None else (((ext_price - current_price) / current_price) * 100.0 if current_price > 0 else 0.0)
                    ext_data = {
                        "session": "POST",
                        "price": ext_price,
                        "pct": ext_pct,
                    }
            except Exception:
                ext_data = None

        # Determine whether the regular exchange market session is actively open right now
        is_reg_open = False
        try:
            meta = t.get_history_metadata() or {}
            periods = meta.get("currentTradingPeriod", {})
            now_utc = pd.Timestamp.now(tz="UTC")
            reg_info = periods.get("regular", {})
            is_reg_open = (reg_info.get("start") <= now_utc <= reg_info.get("end")) if (reg_info.get("start") and reg_info.get("end")) else False
        except Exception:
            is_reg_open = False

        # Convert pence (GBp) to pounds (GBP) ONLY when the feed quotes in pence
        if is_pence:
            current_price = current_price / 100.0
            p_1d = p_1d / 100.0
            p_1w = p_1w / 100.0
            p_1m = p_1m / 100.0
            p_3m = p_3m / 100.0
            p_6m = p_6m / 100.0
            p_ytd = p_ytd / 100.0
            p_1y = p_1y / 100.0
            p_5y = p_5y / 100.0

        quote_type = getattr(t.fast_info, "quote_type", None) or info.get("quoteType", "EQUITY")
        if not quote_type:
            quote_type = "EQUITY"

        # Market Cap from yf.Ticker(ticker).info
        market_cap = float(info.get("marketCap", 0) or getattr(t.fast_info, "market_cap", 0) or 0)

        # Volume & 52-Week High/Low (Speed Optimization: Extracted directly from historical dataframe)
        daily_volume = float(hist["Volume"].iloc[-1]) if ("Volume" in hist.columns and not pd.isna(hist["Volume"].iloc[-1])) else 0.0

        dt_1y = last_dt - pd.DateOffset(years=1)
        hist_1y = hist[hist.index >= dt_1y]
        fifty_two_week_high = float(hist_1y["High"].max()) if not hist_1y.empty else float(hist["High"].max())
        fifty_two_week_low = float(hist_1y["Low"].min()) if not hist_1y.empty else float(hist["Low"].min())

        day_low = float(hist["Low"].iloc[-1]) if ("Low" in hist.columns and not pd.isna(hist["Low"].iloc[-1])) else current_price
        day_high = float(hist["High"].iloc[-1]) if ("High" in hist.columns and not pd.isna(hist["High"].iloc[-1])) else current_price

        if is_pence:
            fifty_two_week_high = fifty_two_week_high / 100.0
            fifty_two_week_low = fifty_two_week_low / 100.0
            day_low = day_low / 100.0
            day_high = day_high / 100.0

        distance_from_high = (current_price / fifty_two_week_high) - 1.0 if fifty_two_week_high > 0 else -1.0

        avg_volume = float(info.get("averageVolume") or info.get("averageVolume10days") or (hist["Volume"].tail(30).mean() if "Volume" in hist.columns else 0.0) or 0.0)

        # Fundamentals & Valuation
        trailing_pe = info.get("trailingPE")
        forward_pe = info.get("forwardPE")
        div_yield = info.get("dividendYield") or info.get("trailingAnnualDividendYield")

        sector_str = info.get("sector")
        if not sector_str:
            sector_str = "ETF / Index Fund" if quote_type == "ETF" else ("Digital Asset" if quote_type == "CRYPTOCURRENCY" else "Equity")
        industry_str = info.get("industry") or info.get("category") or ("Index Basket" if quote_type == "ETF" else "")

        # Analyst Consensus
        target_mean_price = info.get("targetMeanPrice") or info.get("targetMedianPrice")
        if target_mean_price is not None and is_pence and target_mean_price > 800:
            target_mean_price = target_mean_price / 100.0

        rec_key = info.get("recommendationKey")
        num_analysts = info.get("numberOfAnalystOpinions")

        # Ensure accurate market cap for SpaceX (SPCX): $1.94 Trillion
        if ticker.upper() == "SPCX":
            market_cap = 1_940_000_000_000.0
            sector_str = "Aerospace & Defense"
            industry_str = "Commercial Spaceflight & Satellite"

        r_1d = ((current_price - p_1d) / p_1d) * 100.0 if p_1d > 0 and not np.isnan(p_1d) else 0.0
        r_1w = ((current_price - p_1w) / p_1w) * 100.0 if p_1w > 0 and not np.isnan(p_1w) else 0.0
        r_1m = ((current_price - p_1m) / p_1m) * 100.0 if p_1m > 0 and not np.isnan(p_1m) else 0.0
        r_3m = ((current_price - p_3m) / p_3m) * 100.0 if p_3m > 0 and not np.isnan(p_3m) else 0.0
        r_6m = ((current_price - p_6m) / p_6m) * 100.0 if p_6m > 0 and not np.isnan(p_6m) else 0.0
        r_ytd = ((current_price - p_ytd) / p_ytd) * 100.0 if p_ytd > 0 and not np.isnan(p_ytd) else 0.0
        r_1y = ((current_price - p_1y) / p_1y) * 100.0 if p_1y > 0 and not np.isnan(p_1y) else 0.0
        r_5y = ((current_price - p_5y) / p_5y) * 100.0 if p_5y > 0 and not np.isnan(p_5y) else 0.0

        return {
            "name": format_display_name(ticker, info),
            "ticker": ticker.upper(),
            "price": current_price,
            "currency": currency,
            "quote_type": str(quote_type).upper(),
            "1D": r_1d,
            "1 Day": r_1d,
            "1W": r_1w,
            "1 Week": r_1w,
            "1M": r_1m,
            "1 Month": r_1m,
            "3M": r_3m,
            "3 Months": r_3m,
            "6M": r_6m,
            "6 Months": r_6m,
            "YTD": r_ytd,
            "Year to Date": r_ytd,
            "Year-to-Date": r_ytd,
            "1Y": r_1y,
            "1 Year": r_1y,
            "5Y": r_5y,
            "5 Year": r_5y,
            "5 Years": r_5y,
            "marketCap": market_cap,
            "volume": daily_volume,
            "avg_volume": avg_volume,
            "fifty_two_week_high": fifty_two_week_high,
            "fifty_two_week_low": fifty_two_week_low,
            "day_low": day_low,
            "day_high": day_high,
            "distance_from_high": distance_from_high,
            "trailing_pe": trailing_pe,
            "forward_pe": forward_pe,
            "dividend_yield": div_yield,
            "sector": sector_str,
            "industry": industry_str,
            "target_mean_price": target_mean_price,
            "recommendation_key": rec_key,
            "number_of_analysts": num_analysts,
            "ext": ext_data,
            "is_open": is_reg_open,
        }
    except Exception:
        return None


# Helper Formatting Utilities for Asset Modal
def format_market_cap_str(mc, curr="$"):
    if not mc or mc <= 0 or np.isnan(mc):
        return "N/A"
    if mc >= 1e12:
        return f"{curr}{mc / 1e12:.2f}T"
    elif mc >= 1e9:
        return f"{curr}{mc / 1e9:.2f}B"
    elif mc >= 1e6:
        return f"{curr}{mc / 1e6:.2f}M"
    else:
        return f"{curr}{mc:,.0f}"


def format_volume_str(vol):
    if not vol or vol <= 0 or np.isnan(vol):
        return "N/A"
    if vol >= 1e9:
        return f"{vol / 1e9:.2f}B"
    elif vol >= 1e6:
        return f"{vol / 1e6:.2f}M"
    elif vol >= 1e3:
        return f"{vol / 1e3:.1f}K"
    else:
        return f"{vol:,.0f}"


def format_div_yield_str(val):
    if val is None or np.isnan(val) or val <= 0:
        return "N/A"
    if val < 0.05:
        return f"{val * 100:.2f}%"
    return f"{val:.2f}%"


# 6b. Institutional Asset Breakdown Modal Dialog (@st.dialog)
@st.dialog("Institutional Asset Overview", width="small")
def show_stock_breakdown_dialog(ticker: str):
    data = fetch_ticker_data(ticker)
    if not data:
        st.error(f"Unable to retrieve market data for {ticker}.")
        if st.button("✕ Close", key="close_modal_err", use_container_width=True):
            if "stock" in st.query_params:
                del st.query_params["stock"]
            st.rerun()
        return

    curr = data.get("currency", "$")
    price = data.get("price", 0.0)
    name = data.get("name", ticker)
    sector = data.get("sector", "")
    industry = data.get("industry", "")
    sec_ind = f"{sector} • {industry}" if (sector and industry) else (sector or industry)

    # 1D return
    r_1d = data.get("1D", 0.0)
    sign_1d = "+" if r_1d > 0 else ""
    clr_1d = "#22C55E" if r_1d > 0 else ("#EF4444" if r_1d < 0 else "#94A3B8")

    # Ext session
    ext = data.get("ext")
    ext_html = ""
    if ext:
        sess = ext["session"]
        ep = ext["price"]
        epct = ext["pct"]
        esign = "+" if epct > 0 else ""
        eclr = "#22C55E" if epct > 0 else "#EF4444"
        ext_html = (
            f'<div style="font-size: 0.85rem; color: #94A3B8; margin-top: 3px;">'
            f'<span style="background: #EAB308; color: #000000; font-weight: 800; padding: 2px 6px; border-radius: 4px; font-size: 0.72rem; margin-right: 6px;">{sess}</span>'
            f'<span style="color: #FFFFFF; font-weight: 700;">{curr}{ep:,.2f}</span>'
            f'<span style="color: {eclr}; font-weight: 700; margin-left: 4px;">({esign}{epct:.2f}%)</span>'
            f'</div>'
        )

    # Asset Header Block
    header_block = (
        f'<div style="background: #11141A; border: 1px solid #1E293B; border-radius: 12px; padding: 14px 16px; margin-bottom: 10px;">'
        f'<div class="modal-header-container" style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 8px;">'
        f'<div>'
        f'<div style="display: flex; align-items: center; gap: 8px;">'
        f'<span style="font-size: 1.35rem; font-weight: 800; color: #FFFFFF; letter-spacing: -0.3px;">{name}</span>'
        f'<span style="background: #FACC15; color: #000000; font-weight: 800; padding: 2px 7px; border-radius: 4px; font-size: 0.80rem;">{ticker}</span>'
        f'</div>'
        f'<div style="color: #94A3B8; font-size: 0.76rem; font-weight: 600; margin-top: 3px;">{sec_ind}</div>'
        f'</div>'
        f'<div class="modal-header-price" style="text-align: right;">'
        f'<div style="font-size: 1.50rem; font-weight: 800; color: #FFFFFF; letter-spacing: -0.5px;">'
        f'{curr}{price:,.2f}'
        f'<span style="font-size: 0.90rem; font-weight: 700; color: {clr_1d}; margin-left: 6px;">{sign_1d}{r_1d:.2f}%</span>'
        f'</div>'
        f'{ext_html}'
        f'</div>'
        f'</div>'
        f'</div>'
    )
    st.markdown(header_block, unsafe_allow_html=True)

    # 1. 52-Week Range Progress Meter & Day Range
    low_52 = data.get("fifty_two_week_low", price)
    high_52 = data.get("fifty_two_week_high", price)
    day_l = data.get("day_low", price)
    day_h = data.get("day_high", price)
    span_52 = high_52 - low_52
    pct_pos = max(0.0, min(100.0, ((price - low_52) / span_52) * 100.0)) if span_52 > 0 else 50.0

    range_block = (
        f'<div style="background: #11141A; border: 1px solid #1E293B; border-radius: 12px; padding: 12px 14px; margin-bottom: 10px;">'
        f'<div style="display: flex; justify-content: space-between; align-items: center;">'
        f'<span style="font-size: 0.72rem; font-weight: 800; color: #94A3B8; letter-spacing: 0.8px; text-transform: uppercase;">52-Week Price Range</span>'
        f'<span style="font-size: 0.76rem; font-weight: 800; color: #FACC15;">{pct_pos:.0f}% of Range</span>'
        f'</div>'
        f'<div style="position: relative; width: 100%; height: 8px; background: #27272A; border-radius: 4px; margin: 10px 0 8px 0;">'
        f'<div style="position: absolute; left: 0; width: {pct_pos}%; height: 100%; background: linear-gradient(90deg, #EF4444 0%, #EAB308 50%, #22C55E 100%); border-radius: 4px;"></div>'
        f'<div style="position: absolute; left: {pct_pos}%; top: -5px; width: 18px; height: 18px; border-radius: 50%; background: #FFFFFF; border: 3px solid #FACC15; box-shadow: 0 0 8px rgba(250, 204, 21, 0.9); transform: translateX(-50%);"></div>'
        f'</div>'
        f'<div style="display: flex; justify-content: space-between; font-size: 0.74rem; color: #94A3B8; flex-wrap: wrap; gap: 4px;">'
        f'<div><span style="color: #64748B;">52W Low:</span> <strong style="color: #FFFFFF;">{curr}{low_52:,.2f}</strong></div>'
        f'<div><span style="color: #64748B;">Day Range:</span> <strong style="color: #FFFFFF;">{curr}{day_l:,.2f} – {curr}{day_h:,.2f}</strong></div>'
        f'<div><span style="color: #64748B;">52W High:</span> <strong style="color: #FFFFFF;">{curr}{high_52:,.2f}</strong></div>'
        f'</div>'
        f'</div>'
    )
    st.markdown(range_block, unsafe_allow_html=True)

    # 2. Valuation & Key Fundamentals (4 Tiles)
    mc_str = format_market_cap_str(data.get("marketCap"), curr)
    trailing_pe = data.get("trailing_pe")
    pe_str = f"{trailing_pe:.1f}x" if (trailing_pe and trailing_pe > 0 and not np.isnan(trailing_pe)) else "N/A"
    forward_pe = data.get("forward_pe")
    fwd_pe_str = f"{forward_pe:.1f}x" if (forward_pe and forward_pe > 0 and not np.isnan(forward_pe)) else "N/A"
    div_yield = data.get("dividend_yield")
    div_str = format_div_yield_str(div_yield)

    val_block = (
        f'<div style="background: #11141A; border: 1px solid #1E293B; border-radius: 12px; padding: 12px 14px; margin-bottom: 10px;">'
        f'<div style="font-size: 0.72rem; font-weight: 800; color: #94A3B8; letter-spacing: 0.8px; text-transform: uppercase; margin-bottom: 8px;">Valuation & Key Fundamentals</div>'
        f'<div class="modal-fundamentals-grid">'
        f'<div style="background: #181D26; padding: 8px 6px; border-radius: 8px; text-align: center; border: 1px solid #232B38;">'
        f'<div style="font-size: 0.66rem; color: #888888; font-weight: 700; text-transform: uppercase;">Market Cap</div>'
        f'<div style="font-size: 0.95rem; font-weight: 800; color: #FFFFFF; margin-top: 2px;">{mc_str}</div>'
        f'</div>'
        f'<div style="background: #181D26; padding: 8px 6px; border-radius: 8px; text-align: center; border: 1px solid #232B38;">'
        f'<div style="font-size: 0.66rem; color: #888888; font-weight: 700; text-transform: uppercase;">Trailing P/E</div>'
        f'<div style="font-size: 0.95rem; font-weight: 800; color: #FFFFFF; margin-top: 2px;">{pe_str}</div>'
        f'</div>'
        f'<div style="background: #181D26; padding: 8px 6px; border-radius: 8px; text-align: center; border: 1px solid #232B38;">'
        f'<div style="font-size: 0.66rem; color: #888888; font-weight: 700; text-transform: uppercase;">Forward P/E</div>'
        f'<div style="font-size: 0.95rem; font-weight: 800; color: #FFFFFF; margin-top: 2px;">{fwd_pe_str}</div>'
        f'</div>'
        f'<div style="background: #181D26; padding: 8px 6px; border-radius: 8px; text-align: center; border: 1px solid #232B38;">'
        f'<div style="font-size: 0.66rem; color: #888888; font-weight: 700; text-transform: uppercase;">Div Yield</div>'
        f'<div style="font-size: 0.95rem; font-weight: 800; color: #FFFFFF; margin-top: 2px;">{div_str}</div>'
        f'</div>'
        f'</div>'
        f'</div>'
    )
    st.markdown(val_block, unsafe_allow_html=True)

    # 3. Multi-Timeframe Return Scorecard (8 Tiles)
    tf_keys = [
        ("1D", "1 Day"),
        ("1W", "1 Week"),
        ("1M", "1 Month"),
        ("3M", "3 Months"),
        ("6M", "6 Months"),
        ("YTD", "Year to Date"),
        ("1Y", "1 Year"),
        ("5Y", "5 Year"),
    ]
    tf_tiles_html = []
    for short_lbl, full_key in tf_keys:
        val = data.get(full_key)
        if val is None or np.isnan(val):
            val_bg = "#222222"
            val_str = "N/A"
        else:
            val_bg = get_heat_color(val)
            v_sign = "+" if val > 0 else ""
            val_str = f"{v_sign}{val:.2f}%"
        tf_tiles_html.append(
            f'<div style="background-color: {val_bg}; padding: 7px 3px; border-radius: 6px; text-align: center; border: 1px solid rgba(255,255,255,0.08); box-shadow: inset 1px 1px 1px rgba(255,255,255,0.15), 0 3px 6px rgba(0,0,0,0.5);">'
            f'<div style="font-size: 0.65rem; font-weight: 800; color: #E2E8F0; letter-spacing: 0.5px;">{short_lbl}</div>'
            f'<div style="font-size: 0.85rem; font-weight: 800; color: #FFFFFF; margin-top: 2px;">{val_str}</div>'
            f'</div>'
        )
    scorecard_grid = "".join(tf_tiles_html)

    scorecard_block = (
        f'<div style="background: #11141A; border: 1px solid #1E293B; border-radius: 12px; padding: 12px 14px; margin-bottom: 10px;">'
        f'<div style="font-size: 0.72rem; font-weight: 800; color: #94A3B8; letter-spacing: 0.8px; text-transform: uppercase; margin-bottom: 8px;">Multi-Timeframe Return Scorecard</div>'
        f'<div class="modal-scorecard-grid">'
        f'{scorecard_grid}'
        f'</div>'
        f'</div>'
    )
    st.markdown(scorecard_block, unsafe_allow_html=True)

    # 4. Trading Volume & Activity
    d_vol = data.get("volume", 0.0)
    avg_vol = data.get("avg_volume", 0.0)
    d_vol_str = format_volume_str(d_vol)
    avg_vol_str = format_volume_str(avg_vol)
    rvol = (d_vol / avg_vol) if (avg_vol > 0 and d_vol > 0) else 1.0
    if rvol >= 1.25:
        rvol_badge = f'<span style="background: #15803D; color: #FFFFFF; font-weight: 800; padding: 2px 7px; border-radius: 4px; font-size: 0.70rem;">⚡ Elevated ({rvol:.2f}x)</span>'
    elif rvol <= 0.75 and rvol > 0:
        rvol_badge = f'<span style="background: #374151; color: #D1D5DB; font-weight: 800; padding: 2px 7px; border-radius: 4px; font-size: 0.70rem;">💤 Light ({rvol:.2f}x)</span>'
    else:
        rvol_badge = f'<span style="background: #1F2937; color: #9CA3AF; font-weight: 700; padding: 2px 7px; border-radius: 4px; font-size: 0.70rem;">Normal ({rvol:.2f}x)</span>'

    # 5. Wall Street / Analyst Consensus
    rec_key = data.get("recommendation_key")
    target_price = data.get("target_mean_price")
    num_analysts = data.get("number_of_analysts")
    quote_type = data.get("quote_type", "EQUITY")

    if target_price and target_price > 0 and price > 0:
        implied_upside = ((target_price - price) / price) * 100.0
        up_sign = "+" if implied_upside > 0 else ""
        up_clr = "#22C55E" if implied_upside > 0 else "#EF4444"
        up_str = f'<span style="color: {up_clr}; font-weight: 800;">{up_sign}{implied_upside:.1f}%</span>'
        target_display = f"{curr}{target_price:,.2f} ({up_str} Implied)"
    else:
        target_display = "N/A"

    if rec_key:
        rec_clean = str(rec_key).replace("_", " ").upper()
        if "BUY" in rec_clean:
            rec_pill = f'<span style="background: #15803D; color: #FFFFFF; font-weight: 800; padding: 2px 8px; border-radius: 4px; font-size: 0.72rem;">{rec_clean}</span>'
        elif "HOLD" in rec_clean:
            rec_pill = f'<span style="background: #854D0E; color: #FEF08A; font-weight: 800; padding: 2px 8px; border-radius: 4px; font-size: 0.72rem;">{rec_clean}</span>'
        else:
            rec_pill = f'<span style="background: #991B1B; color: #FFFFFF; font-weight: 800; padding: 2px 8px; border-radius: 4px; font-size: 0.72rem;">{rec_clean}</span>'
    else:
        rec_pill = '<span style="color: #64748B; font-weight: 600; font-size: 0.72rem;">N/A</span>'

    coverage_str = f"Based on {num_analysts} Wall Street analysts" if (num_analysts and num_analysts > 0) else ""

    # Combine 4 & 5 into an intuitive lower block
    lower_block = (
        f'<div class="modal-lower-grid">'
        f'<div style="background: #11141A; border: 1px solid #1E293B; border-radius: 12px; padding: 12px 14px;">'
        f'<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">'
        f'<span style="font-size: 0.70rem; font-weight: 800; color: #94A3B8; letter-spacing: 0.8px; text-transform: uppercase;">Volume & Liquidity</span>'
        f'{rvol_badge}'
        f'</div>'
        f'<div style="display: flex; justify-content: space-between; margin-top: 6px; font-size: 0.78rem;">'
        f'<div><span style="color: #64748B;">Today:</span> <strong style="color: #FFFFFF;">{d_vol_str}</strong></div>'
        f'<div><span style="color: #64748B;">3M Avg:</span> <strong style="color: #FFFFFF;">{avg_vol_str}</strong></div>'
        f'</div>'
        f'</div>'
        f'<div style="background: #11141A; border: 1px solid #1E293B; border-radius: 12px; padding: 12px 14px;">'
        f'<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">'
        f'<span style="font-size: 0.70rem; font-weight: 800; color: #94A3B8; letter-spacing: 0.8px; text-transform: uppercase;">Analyst Consensus</span>'
        f'{rec_pill}'
        f'</div>'
        f'<div style="font-size: 0.78rem; margin-top: 6px;">'
        f'<span style="color: #64748B;">12M Target:</span> <strong style="color: #FFFFFF;">{target_display}</strong>'
        f'</div>'
        f'<div style="color: #64748B; font-size: 0.66rem; margin-top: 3px;">{coverage_str if coverage_str else ("Broad Index Basket" if quote_type == "ETF" else "Private Asset" if ticker == "SPCX" else "")}</div>'
        f'</div>'
        f'</div>'
    )
    st.markdown(lower_block, unsafe_allow_html=True)

    if st.button("✕ Close Asset Breakdown", use_container_width=True, key="close_stock_modal_btn"):
        if "stock" in st.query_params:
            del st.query_params["stock"]
        st.rerun()


# Trigger Asset Breakdown Modal if a stock card was clicked
clicked_stock = st.query_params.get("stock")
if clicked_stock:
    del st.query_params["stock"]
    show_stock_breakdown_dialog(clicked_stock)


# 7. Header (UK English: INSTITUTIONAL MULTI-ASSET REAL-TIME VISUALISER)
st.markdown(
    """
    <div style="text-align: center; margin-bottom: 16px;">
        <h1 class="main-title"><span class="title-line-1">The Investing Dean</span><span class="title-line-2">Heat Map</span></h1>
        <p class="main-subtitle"><span class="sub-line-1">INSTITUTIONAL MULTI-ASSET REAL-TIME</span><span class="sub-line-2">VISUALISER</span></p>
    </div>
    """,
    unsafe_allow_html=True,
)

# 8. Institutional Collapsible Watchlist Manager
with st.expander("Customise Watchlist", expanded=False):
    col_input, col_btn = st.columns([4, 1])
    with col_input:
        new_ticker = st.text_input(
            "Search & Add Assets",
            placeholder="Search company or fund name (e.g. Rolls Royce, Vanguard All World, Microsoft, Apple, NVDA)...",
            label_visibility="collapsed",
            key="asset_search_input",
        )
    with col_btn:
        if st.button("Add Ticker", use_container_width=True):
            if new_ticker.strip():
                formatted_ticker = new_ticker.strip().upper()
                if formatted_ticker in ["VWRP", "VWRL", "VUAG", "SMGB", "XNAQ", "EQQQ", "VUSA", "IITU"]:
                    formatted_ticker = f"{formatted_ticker}.L"
                if formatted_ticker not in st.session_state.available_options:
                    st.session_state.available_options.append(formatted_ticker)
                if formatted_ticker not in st.session_state.active_tickers:
                    st.session_state.active_tickers.append(formatted_ticker)
                save_user_watchlist(st.session_state.current_profile, st.session_state.active_tickers)
                st.rerun()

    # Dynamic Search Suggestions for Beginners
    search_query = new_ticker.strip()
    if len(search_query) >= 2:
        suggestions = search_tickers(search_query)
        if suggestions:
            st.markdown(
                '<div style="font-size: 0.74rem; font-weight: 800; color: #FACC15; letter-spacing: 1px; margin: 10px 0 6px 0;">SEARCH SUGGESTIONS (CLICK TO ADD)</div>',
                unsafe_allow_html=True,
            )
            for idx, item in enumerate(suggestions[:5]):
                sym = item["symbol"]
                name = item["name"]
                qtype = item["type"]
                exch = item["exchange"]
                is_active = sym in st.session_state.active_tickers

                c_info, c_action = st.columns([4.2, 0.8])
                with c_info:
                    st.markdown(
                        f"""
                        <div style="background: #141416; border: 1px solid #27272A; border-radius: 6px; padding: 7px 12px; margin-bottom: 4px; display: flex; align-items: center; justify-content: space-between;">
                            <div style="display: flex; align-items: center; gap: 10px; overflow: hidden;">
                                <span style="font-weight: 800; color: #FACC15; font-size: 0.88rem; white-space: nowrap;">{sym}</span>
                                <span style="color: #FFFFFF; font-size: 0.82rem; font-weight: 600; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{name}</span>
                            </div>
                            <div style="font-size: 0.70rem; color: #888888; background: #1F1F24; padding: 2px 7px; border-radius: 4px; white-space: nowrap; margin-left: 8px;">{exch} • {qtype}</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                with c_action:
                    btn_label = "✓ Added" if is_active else "+ Add"
                    if st.button(
                        btn_label,
                        key=f"btn_add_sugg_{idx}_{sym}",
                        use_container_width=True,
                        disabled=is_active,
                    ):
                        if sym not in st.session_state.available_options:
                            st.session_state.available_options.append(sym)
                        if sym not in st.session_state.active_tickers:
                            st.session_state.active_tickers.append(sym)
                        save_user_watchlist(st.session_state.current_profile, st.session_state.active_tickers)
                        st.rerun()

    st.markdown(
        '<div style="font-size: 0.74rem; font-weight: 800; color: #A1A1AA; letter-spacing: 1px; margin: 14px 0 6px 0;">ACTIVE WATCHLIST ASSETS</div>',
        unsafe_allow_html=True,
    )
    selected = st.multiselect(
        "Active Watchlist Assets",
        options=st.session_state.active_tickers,
        default=st.session_state.active_tickers,
        label_visibility="collapsed",
    )
    if selected != st.session_state.active_tickers:
        st.session_state.active_tickers = selected
        save_user_watchlist(st.session_state.current_profile, selected)
        st.rerun()

    st.markdown(
        '<div style="font-size: 0.73rem; color: #71717A; margin-top: 6px;">Note: London Stock Exchange tickers (<code>.L</code>) automatically detect pence (GBp) vs pounds (GBP) and format with £.</div>',
        unsafe_allow_html=True,
    )

# 9. Timeframe Switcher (Symmetrically Centered: 4 per row on mobile, full word labels)
timeframe = st.radio(
    "Select Timeframe",
    options=["1 Day", "1 Week", "1 Month", "3 Months", "6 Months", "Year to Date", "1 Year", "5 Year"],
    horizontal=True,
    label_visibility="collapsed",
)

# 10. Asset Categorisation Definitions
KNOWN_ETFS = {"QQQ", "SPY", "SMH", "SOXX", "SMGB.L", "XNAQ.L", "VUAG.L", "EQQQ.L", "VUSA.L", "IITU.L", "VWRP.L", "VWRL.L"}
KNOWN_CRYPTO = {"BTC-USD", "ETH-USD", "SOL-USD"}

def get_ticker_category(ticker, data):
    t_up = ticker.upper()
    qt = data.get("quote_type", "EQUITY") if data else "EQUITY"
    if qt in ["ETF", "MUTUALFUND"] or t_up in KNOWN_ETFS:
        return "ETFS_FUNDS"
    elif qt == "CRYPTOCURRENCY" or t_up in KNOWN_CRYPTO or t_up.endswith("-USD"):
        return "CRYPTO"
    else:
        return "EQUITIES"

# 11. Asynchronous Fragment Rendering for Dynamic Heat Map Grid
def on_refresh_market_data():
    fetch_ticker_data.clear()
    st.cache_data.clear()
    st.session_state["just_refreshed_data"] = True

def _render_heatmap_grid_core(
    timeframe: str,
    card_font: str,
    active_tickers: list,
    is_desktop: bool = True,
):
    # Action Bar inside Fragment: Clean 4-column layout with vertical alignment
    frag_c1, frag_c2, frag_c3, frag_c4 = st.columns([1.6, 1.4, 1.1, 1.5], vertical_alignment="center")

    with frag_c1:
        st.button(
            "🔄 Refresh Market Data",
            on_click=on_refresh_market_data,
            use_container_width=True,
            key="frag_refresh_btn",
        )

    with frag_c2:
        now_str = datetime.datetime.now().strftime("%b %d, %I:%M:%S %p")
        auto_label = '<span style="color: #64748B; font-size: 0.68rem; margin-left: 2px;">(Auto 3m)</span>' if is_desktop else ""
        st.markdown(
            f"""
            <div style="display: flex; align-items: center; justify-content: center; height: 38px; gap: 6px; font-size: 0.78rem; color: #FFFFFF; white-space: nowrap;">
                <span style="background: #FACC15; color: #000000; font-weight: 800; padding: 2px 6px; border-radius: 4px;">SNAPSHOT</span>
                <span>{now_str}</span>
                {auto_label}
            </div>
            """,
            unsafe_allow_html=True,
        )

    with frag_c3:
        show_ext = st.toggle(
            "Extended Hours",
            value=True,
            help="Toggle pre-market and post-market (after-hours) pricing on tiles",
            key="frag_toggle_ext",
        )

    with frag_c4:
        sort_by = st.selectbox(
            "Sort By",
            options=[
                "Alphabetical (A-Z)",
                "Biggest Gain",
                "Biggest Dip",
                "Biggest Market Cap",
                "Highest Daily Volume",
                "Closest to 52-Week High",
            ],
            index=0,
            label_visibility="collapsed",
            key="frag_sort_by",
            help="Sort heat map tiles dynamically",
        )

    if st.session_state.get("just_refreshed_data", False):
        st.session_state["just_refreshed_data"] = False
        st.toast("Market data refreshed successfully!", icon="✅")

    # Pre-fetch and Sort Logic
    with st.spinner("Fetching latest live market data..."):
        fetched_items = []
        for ticker in active_tickers:
            t_data = fetch_ticker_data(ticker)
            fetched_items.append({"ticker": ticker, "data": t_data})

    def get_sort_pct(x):
        d = x.get("data")
        if not d:
            return None
        # When Extended Hours is toggled ON and viewing 1 Day, rank by active Pre/Post market return
        if show_ext and timeframe in ["1 Day", "1D"] and d.get("ext"):
            ext_p = d["ext"].get("pct")
            if ext_p is not None and not np.isnan(ext_p):
                return float(ext_p)
        val = d.get(timeframe)
        if val is not None and not np.isnan(val):
            return float(val)
        return None

    if sort_by == "Alphabetical (A-Z)":
        sorted_items = sorted(
            fetched_items,
            key=lambda x: (1 if x["data"] is None else 0, x["ticker"].upper()),
        )
    elif sort_by == "Biggest Gain":
        sorted_items = sorted(
            fetched_items,
            key=lambda x: (
                1 if get_sort_pct(x) is not None else 0,
                get_sort_pct(x) if get_sort_pct(x) is not None else float("-inf"),
            ),
            reverse=True,
        )
    elif sort_by == "Biggest Dip":
        sorted_items = sorted(
            fetched_items,
            key=lambda x: (
                0 if get_sort_pct(x) is not None else 1,
                get_sort_pct(x) if get_sort_pct(x) is not None else float("inf"),
            ),
        )
    elif sort_by == "Biggest Market Cap":
        sorted_items = sorted(
            fetched_items,
            key=lambda x: (
                1 if (x["data"] and x["data"].get("marketCap", 0) > 0) else 0,
                x["data"].get("marketCap", 0) if x["data"] else 0,
            ),
            reverse=True,
        )
    elif sort_by == "Highest Daily Volume":
        sorted_items = sorted(
            fetched_items,
            key=lambda x: (
                1 if (x["data"] and x["data"].get("volume", 0) > 0) else 0,
                x["data"].get("volume", 0) if x["data"] else 0,
            ),
            reverse=True,
        )
    elif sort_by == "Closest to 52-Week High":
        sorted_items = sorted(
            fetched_items,
            key=lambda x: (
                1 if (x["data"] and x["data"].get("distance_from_high") is not None and not np.isnan(x["data"].get("distance_from_high"))) else 0,
                x["data"].get("distance_from_high", float("-inf")) if x["data"] else float("-inf"),
            ),
            reverse=True,
        )
    else:
        sorted_items = fetched_items

    sections = {
        "EQUITIES": {"title": "Equities & Stocks", "cards": []},
        "ETFS_FUNDS": {"title": "ETFs & Index Funds", "cards": []},
        "CRYPTO": {"title": "Digital Assets & Crypto", "cards": []},
    }

    for item in sorted_items:
        ticker = item["ticker"]
        data = item["data"]
        if data:
            pct_val = data.get(timeframe)
            price_val = data.get("price")
            curr_symbol = data.get("currency", "$")

            if pct_val is None or np.isnan(pct_val):
                bg_color = "#222222"
                formatted_pct = "N/A"
            else:
                bg_color = get_heat_color(pct_val)
                prefix = "+" if pct_val > 0 else ""
                formatted_pct = f"{prefix}{pct_val:.2f}%"

            if price_val is None or np.isnan(price_val):
                formatted_price = "Unavailable"
            else:
                formatted_price = f"{curr_symbol}{price_val:,.2f}"

            # High-Grade Pre-market, Post-market, or Live Regular Market Badge (Zero Emojis)
            ext_markup = ""
            ext_info = data.get("ext")
            is_open = data.get("is_open", False)

            if show_ext and ext_info:
                session_label = ext_info["session"]  # "PRE" or "POST"
                badge_class = "ext-pre" if session_label == "PRE" else "ext-post"
                ext_p = ext_info["price"]
                ext_pct = ext_info["pct"]
                ext_sign = "+" if ext_pct > 0 else ""
                pct_class = "positive" if ext_pct > 0 else "negative" if ext_pct < 0 else "neutral"

                ext_markup = (
                    f'<div class="card-ext">'
                    f'<span class="ext-tag {badge_class}"><span class="ext-dot"></span>{session_label}</span>'
                    f'<div class="ext-metrics">'
                    f'<span class="ext-price">{curr_symbol}{ext_p:,.2f}</span>'
                    f'<span class="ext-pct {pct_class}">{ext_sign}{ext_pct:.2f}%</span>'
                    f'</div>'
                    f'</div>'
                )
            elif is_open:
                ext_markup = (
                    f'<div class="card-ext">'
                    f'<span class="ext-tag ext-live"><span class="ext-dot"></span>LIVE</span>'
                    f'</div>'
                )
        else:
            bg_color = "#222222"
            formatted_pct = "N/A"
            formatted_price = "Unavailable"
            ext_markup = ""

        asset_name = data.get("name") if data else KNOWN_ASSET_NAMES.get(ticker.upper(), ticker)

        card_html = (
            f'<a href="?stock={ticker}" target="_self" class="heatmap-card" style="background-color: {bg_color}; text-decoration: none;">'
            f'<div class="card-ticker">{ticker}</div>'
            f'<div class="card-name" title="{asset_name}">{asset_name}</div>'
            f'<div class="card-pct">{formatted_pct}</div>'
            f'<div class="card-price">{formatted_price}</div>'
            f'{ext_markup}'
            f'</a>'
        )

        cat = get_ticker_category(ticker, data)
        sections[cat]["cards"].append(card_html)

    section_blocks = []
    for cat_key, section_data in sections.items():
        cards = section_data["cards"]
        if cards:
            sec_title = section_data["title"]
            count = len(cards)
            count_label = "Asset" if count == 1 else "Assets"
            sec_header = (
                f'<div class="section-header">'
                f'<span class="section-title">{sec_title}</span>'
                f'<span class="section-badge">{count} {count_label}</span>'
                f'</div>'
            )
            grid_markup = "".join(cards)
            section_blocks.append(
                f'<div class="section-container">{sec_header}<div class="heatmap-grid">{grid_markup}</div></div>'
            )

    all_sections_html = "".join(section_blocks)
    st.markdown(
        f'<div class="heatmap-container">{all_sections_html}</div>',
        unsafe_allow_html=True,
    )

    # Colour Scale Footer (UK English)
    st.markdown(
        f"""
        <div style="text-align: center; margin-top: 14px; margin-bottom: 20px;">
            <div style="display: inline-block; width: 280px; height: 6px; background: linear-gradient(90deg, #991b1b 0%, #222222 50%, #15803d 100%); border-radius: 3px;"></div>
            <div style="display: flex; justify-content: space-between; width: 280px; margin: 4px auto 0 auto; font-size: 0.72rem; color: #888888;">
                <span>≤ -5%</span>
                <span>0%</span>
                <span>≥ +5%</span>
            </div>
            <p style="color: #666666; font-size: 0.75rem; margin-top: 6px;">Full red to full green at -5% to +5% for {timeframe}. Grey = not available.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

# 12. Top-Level Fragment Definitions (Desktop Auto-refreshes every 3 mins; Mobile on-demand)
@st.fragment(run_every=180)
def render_heatmap_desktop(timeframe: str, card_font: str, active_tickers: list):
    _render_heatmap_grid_core(timeframe, card_font, active_tickers, is_desktop=True)

@st.fragment
def render_heatmap_mobile(timeframe: str, card_font: str, active_tickers: list):
    _render_heatmap_grid_core(timeframe, card_font, active_tickers, is_desktop=False)

# 13. Render Heatmap Fragment with Synchronised State
ua = ""
try:
    ua = st.context.headers.get("user-agent", "").lower()
except Exception:
    ua = ""

is_mobile = any(m in ua for m in ["mobile", "android", "iphone", "ipad", "ipod", "phone"])

if is_mobile:
    render_heatmap_mobile(
        timeframe=timeframe,
        card_font=st.session_state.card_font,
        active_tickers=st.session_state.active_tickers,
    )
else:
    render_heatmap_desktop(
        timeframe=timeframe,
        card_font=st.session_state.card_font,
        active_tickers=st.session_state.active_tickers,
    )
