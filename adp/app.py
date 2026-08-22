import streamlit as st
import pandas as pd
from bs4 import BeautifulSoup
import os
import streamlit.components.v1 as components
import plotly.graph_objects as go
import json
import copy
import io
import math
import re
import base64
import numpy as np
from PIL import Image

current_dir = os.path.dirname(os.path.abspath(__file__))
logo_path = os.path.join(current_dir, "logo.svg") # Sol menüde gözükecek büyük SVG logon

favicon_path = os.path.join(current_dir, "favicon.png") 

try:
    favicon_img = Image.open(favicon_path)
    st.set_page_config(page_title="AD Projeksiyon | Türkiye Genel Seçim ve Cumhurbaşkanlığı Simülasyonu", page_icon=favicon_img, layout="wide")
except FileNotFoundError:
    st.set_page_config(page_title="AD Projeksiyon | Türkiye Genel Seçim ve Cumhurbaşkanlığı Simülasyonu", page_icon="🗳️", layout="wide")

if os.path.exists(logo_path):
    st.sidebar.image(logo_path, use_container_width=True)
else:
    st.sidebar.markdown("### AD PROJEKSİYON")

st.sidebar.write("")

c_bg = "#181720"
c_text = "#ffffff"
c_border = "#ffffff"
t_seat_bg = "#333333"
t_bar_bg = "#23222d"
sidebar_input_bg = "#23222d"
sidebar_input_border = "#444444"

st.markdown(
    """
    <meta name="description" content="Türkiye genel seçim ve cumhurbaşkanlığı seçim simülasyonu. İlçe bazlı interaktif seçim haritası, D'Hondt hesaplama makinesi ve güncel anket projeksiyon aracı.">
    <meta name="keywords" content="seçim simülasyonu, türkiye seçim haritası, d'hondt hesaplama, anket analizi, poliwave, seçim projeksiyonu, oy kayması, meclis oy dağılımı, pgm projeksiyon, gündemar, projeksiyon">
    """,
    unsafe_allow_html=True
)

custom_theme_css = f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;700;900&display=swap');

    .stApp {{
        background-color: {c_bg};
        transition: background-color 0.3s;
        font-family: 'Space Grotesk', sans-serif;
    }}
    
    [data-testid="stAppViewContainer"] h1, 
    [data-testid="stAppViewContainer"] h2, 
    [data-testid="stAppViewContainer"] h3,
    [data-testid="stAppViewContainer"] h4 {{
        color: {c_text} !important;
        text-shadow: none !important;
        font-weight: 900 !important;
        text-transform: uppercase;
        letter-spacing: -0.5px;
        margin-bottom: 0.8rem !important;
    }}

    [data-testid="stAppViewContainer"] p, 
    [data-testid="stAppViewContainer"] label,
    [data-testid="stAppViewContainer"] span,
    [data-testid="stAppViewContainer"] .stMarkdown {{
        color: {c_text} !important;
    }}

    section[data-testid="stSidebar"] {{
        background-color: {c_bg} !important;
        border-right: 3px solid {c_text} !important;
        transition: background-color 0.3s;
    }}
    
    div[data-baseweb="input"], div[data-baseweb="base-input"], div[data-baseweb="select"], div[data-baseweb="select"] > div,
    [data-testid="stNumberInput"] div[data-baseweb="input"], [data-testid="stTextInput"] div[data-baseweb="input"],
    section[data-testid="stSidebar"] .stNumberInput input, section[data-testid="stSidebar"] .stTextInput input,
    [data-testid="stNumberInput"] input, [data-testid="stTextInput"] input, [data-baseweb="popover"] {{
        background-color: {sidebar_input_bg} !important;
        color: {c_text} !important;
        border: 2px solid {c_text} !important;
        border-radius: 0px !important;
        box-shadow: 3px 3px 0px #eb252d !important;
    }}

    div[data-baseweb="input"]:focus-within, div[data-baseweb="select"]:focus-within,
    [data-testid="stNumberInput"] div[data-baseweb="input"]:focus-within, [data-testid="stTextInput"] div[data-baseweb="input"]:focus-within {{
        border-color: #eb252d !important;
        box-shadow: 0 0 0 2px #eb252d !important;
    }}

    [data-testid="stNumberInput"] button {{ border-radius: 0px !important; border: 1px solid {c_text} !important; }}

    hr {{ border-color: #eb252d !important; border-width: 3px !important; margin-top: 1.5rem !important; margin-bottom: 1.5rem !important; }}
    
    div[data-testid="stVerticalBlockBorderWrapper"], div[data-testid="stExpander"] {{
        border: 3px solid {c_text} !important; box-shadow: 6px 6px 0px #eb252d !important;
        background-color: {c_bg} !important; border-radius: 0px !important; margin-bottom: 1.5rem !important;
    }}

    div[data-testid="stVerticalBlockBorderWrapper"] *, div[data-testid="stExpander"] * {{ border-radius: 0px !important; }}
    
    div[data-testid="stExpander"] details summary p {{ font-weight: 900 !important; font-size: 1.2rem !important; text-transform: uppercase !important; }}

    [data-testid="stDataFrame"] {{ border-radius: 0px !important; border: 3px solid {c_text} !important; box-shadow: 5px 5px 0px #eb252d !important; background-color: {c_bg}; }}

    .stButton>button {{
        border: 3px solid {c_text} !important; box-shadow: 4px 4px 0px #eb252d !important;
        font-weight: 900 !important; border-radius: 0px !important; text-transform: uppercase !important;
        color: {c_text} !important; transition: all 0.1s ease-in-out;
    }}
    
    .stButton>button:hover {{ transform: translate(2px, 2px); box-shadow: 2px 2px 0px #eb252d !important; }}

    .cb-card {{ background-color: {c_bg}; border: 3px solid {c_text}; box-shadow: 5px 5px 0px #eb252d; padding: 16px; margin-bottom: 15px; border-radius: 0px !important; }}
    .cb-row {{ display: flex; align-items: center; margin-bottom: 10px; font-family: 'Space Grotesk', sans-serif; }}
    .cb-name {{ width: 140px; font-weight: 800; font-size: 15px; text-transform: uppercase; color: {c_text}; }}
    .cb-bar-bg {{ flex-grow: 1; background-color: {t_bar_bg}; height: 34px; border: 2px solid {c_text}; box-shadow: 3px 3px 0px #eb252d; display: flex; overflow: hidden; border-radius: 0px !important; }}
    .cb-bar-fill {{ height: 100%; display: flex; align-items: center; padding-left: 8px; color: #ffffff !important; font-weight: 800; font-size: 13px; white-space: nowrap; border-radius: 0px !important; }}

    [data-testid="stHeader"] {{ background-color: transparent !important; }}

    @media (max-width: 768px) {{
        [data-testid="stHorizontalBlock"] {{ flex-direction: column !important; }}
        [data-testid="column"] {{ width: 100% !important; flex: 1 1 auto !important; min-width: 100% !important; }}
    }}

    div[data-testid="stVerticalBlockBorderWrapper"] {{ max-width: 100% !important; overflow-x: auto !important; padding: 1.5rem !important; }}
    
    [data-testid="stTabs"] [data-baseweb="tab-list"] {{ display: flex; width: 100%; }}
    [data-testid="stTabs"] button[data-baseweb="tab"] {{
        background-color: transparent !important; color: {c_text} !important; font-weight: 900 !important;
        font-size: 20px !important; border-radius: 0px !important; border: none !important;
        text-transform: uppercase; padding: 16px 20px; flex: 1 !important; justify-content: center !important;
    }}
    [data-testid="stTabs"] button[data-baseweb="tab"][aria-selected="true"] {{
        background-color: #eb252d !important; color: #ffffff !important; border: 2px solid {c_text} !important; box-shadow: 3px 3px 0px {c_text} !important;
    }}
</style>
"""
st.markdown(custom_theme_css, unsafe_allow_html=True)

# Partiler
if 'custom_parties_def' not in st.session_state:
    st.session_state.custom_parties_def = {}

if 'YENI' in st.session_state.custom_parties_def: del st.session_state.custom_parties_def['YENI']
if 'A' in st.session_state.custom_parties_def: del st.session_state.custom_parties_def['A']

DEFAULT_TRANSITIONS = {
    'AKP': {'AKP': 95.0, 'MHP': 3.0, 'YRP': 2.0},
    'YENI': {'CHP': 85.0, 'IYI': 10.0, 'DEM': 3.0, 'MHP': 3.0},
    'IYI': {'IYI': 85.0, 'CHP': 10.0, 'MHP': 5.0},
    'DEM': {'DEM': 95.0, 'TIP': 5.0},
    'MHP': {'MHP': 95.0, 'AKP': 5.0},
    'YRP': {'YRP': 90.0, 'AKP': 10.0},
    'A': {'AKP': 50.0, 'BBP': 20.0, 'MHP': 20.0, 'IYI': 10.0},
    'ZAFER': {'ZAFER': 85.0, 'IYI': 10.0, 'CHP': 5.0},
    'TIP': {'TIP': 90.0, 'CHP': 10.0},
    'SAADET': {'SAADET': 70.0, 'YRP': 20.0, 'AKP': 10.0},
    'BBP': {'BBP': 90.0, 'MHP': 10.0},
    'CHP': {'CHP': 85.0, 'DEM': 7.5, 'MHP': 2.5, 'AKP': 2.5 }
}

def normalize_id(text):
    if not isinstance(text, str): return ""
    replacements = {'I': 'i', 'ı': 'i', 'İ': 'i', 'Ğ': 'g', 'ğ': 'g', 'Ü': 'u', 'ü': 'u', 'Ş': 's', 'ş': 's', 'Ö': 'o', 'ö': 'o', 'Ç': 'c', 'ç': 'c'}
    for search, replace in replacements.items(): text = text.replace(search, replace)
    return text.lower().replace('-', '').replace('_', '').replace(' ', '')

JOINT_LIST_2023_CORRECTIONS = {
    'adiyaman': {'from_party': 'CHP', 'to_party': 'IYI', 'transfer_rate': 0.3},
    'corum': {'from_party': 'CHP', 'to_party': 'IYI', 'transfer_rate': 0.35},
    'erzincan': {'from_party': 'CHP', 'to_party': 'IYI', 'transfer_rate': 0.2},
    'hakkari': {'from_party': 'CHP', 'to_party': 'IYI', 'transfer_rate': 0.2},
    'batman': {'from_party': 'CHP', 'to_party': 'IYI', 'transfer_rate': 0.2},
    'duzce': {'from_party': 'CHP', 'to_party': 'IYI', 'transfer_rate': 0.3},
    'bartin': {'from_party': 'CHP', 'to_party': 'IYI', 'transfer_rate': 0.25},
    'rize': {'from_party': 'CHP', 'to_party': 'IYI', 'transfer_rate': 0.3},
    'van': {'from_party': 'CHP', 'to_party': 'IYI', 'transfer_rate': 0.2},
    'yozgat': {'from_party': 'IYI', 'to_party': 'CHP', 'transfer_rate': 0.55},
    'aksaray': {'from_party': 'IYI', 'to_party': 'CHP', 'transfer_rate': 0.4},
    'bitlis': {'from_party': 'IYI', 'to_party': 'CHP', 'transfer_rate': 0.4},
    'mus': {'from_party': 'IYI', 'to_party': 'CHP', 'transfer_rate': 0.3},
    'bayburt': {'from_party': 'IYI', 'to_party': 'CHP', 'transfer_rate': 0.4},
    'gumushane': {'from_party': 'IYI', 'to_party': 'CHP', 'transfer_rate': 0.4},
    'cankiri': {'from_party': 'IYI', 'to_party': 'CHP', 'transfer_rate': 0.4},
    'trabzon': {'from_party': 'AKP', 'to_party': 'A', 'transfer_rate': 0.1},
    'tunceli': {'from_party': 'CHP', 'to_party': 'DEM', 'transfer_rate': 0.25},
}

@st.cache_data(show_spinner=False)
def load_base_data(w23, w24):
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        df_23 = pd.read_csv(os.path.join(current_dir, "ysk_2023_secim_verisi.csv"))
        df_24 = pd.read_csv(os.path.join(current_dir, "ysk_2024_secim_verisi.csv"))
        
        if 'DIGER' in df_23['party'].values: df_23 = df_23[df_23['party'] != 'DIGER']
        if 'DIGER' in df_24['party'].values: df_24 = df_24[df_24['party'] != 'DIGER']

        df_23_clean = df_23.groupby(['district', 'party'], as_index=False)['base_vote_pct'].sum()
        df_24_clean = df_24.groupby(['district', 'party'], as_index=False)['base_vote_pct'].sum()

        df_23_clean['vote_23'] = df_23_clean.groupby('district')['base_vote_pct'].transform(lambda x: (x / x.sum()) * 100)
        df_24_clean['vote_24'] = df_24_clean.groupby('district')['base_vote_pct'].transform(lambda x: (x / x.sum()) * 100)

        df_23_clean['province'] = df_23_clean['district'].apply(lambda x: normalize_id(str(x).split('-')[0]))
        
        for prov, correction in JOINT_LIST_2023_CORRECTIONS.items():
            prov_mask = df_23_clean['province'] == prov
            if not prov_mask.any(): continue
            
            from_p, to_p, rate = correction['from_party'], correction['to_party'], correction['transfer_rate']
            
            for dist in df_23_clean[prov_mask]['district'].unique():
                dist_mask = (df_23_clean['district'] == dist)
                from_mask = dist_mask & (df_23_clean['party'] == from_p)
                to_mask = dist_mask & (df_23_clean['party'] == to_p)
                
                if from_mask.any():
                    transfer_amount = df_23_clean.loc[from_mask, 'vote_23'].values[0] * rate
                    df_23_clean.loc[from_mask, 'vote_23'] -= transfer_amount
                    
                    if to_mask.any():
                        df_23_clean.loc[to_mask, 'vote_23'] += transfer_amount
                    else:
                        new_row = pd.DataFrame([{'district': dist, 'party': to_p, 'base_vote_pct': 0, 'vote_23': transfer_amount, 'province': prov}])
                        df_23_clean = pd.concat([df_23_clean, new_row], ignore_index=True)

        seats_df = df_23[['district', 'seat_count']].drop_duplicates(subset=['district'])

        df_merged = pd.merge(df_23_clean[['district', 'party', 'vote_23']], df_24_clean[['district', 'party', 'vote_24']], on=['district', 'party'], how='outer').fillna(0)
        
        df_merged['base_vote_pct'] = (df_merged['vote_23'] * (w23 / 100.0)) + (df_merged['vote_24'] * (w24 / 100.0))
        df = pd.merge(df_merged, seats_df, on='district', how='left')
        return df
    except FileNotFoundError as e:
        st.error(f"🚨 HATA: Dosya eksik - {str(e)}")
        st.stop()

@st.cache_data(show_spinner=False)
def apply_custom_parties(df, custom_parties_dict):
    pivot_base = df.pivot_table(index='district', columns='party', values='base_vote_pct', aggfunc='sum').fillna(0)
    new_rows = []
    
    all_party_defs = DEFAULT_TRANSITIONS.copy()
    for cp_name, cp_data in custom_parties_dict.items():
        all_party_defs[cp_name] = cp_data['bases']
        
    for district, row_data in df.groupby('district'):
        seat_count = row_data['seat_count'].iloc[0] if not pd.isna(row_data['seat_count'].iloc[0]) else 0
        
        for cp_name, bases in all_party_defs.items():
            cp_vote = sum([pivot_base.loc[district, bp] * (weight / 100.0) for bp, weight in bases.items() if bp in pivot_base.columns])
            new_rows.append({'district': district, 'party': cp_name, 'base_vote_pct': cp_vote, 'seat_count': seat_count})
            
    new_df = pd.DataFrame(new_rows)
    new_df['weighted_vote'] = new_df['base_vote_pct'] * new_df['seat_count']
    national_totals = new_df.groupby('party')['weighted_vote'].sum()
    total_seats = new_df.groupby('district')['seat_count'].first().sum()
    
    return new_df, (national_totals / total_seats).to_dict()

w24_val = st.session_state.get("w24_weight", 10)
w23_val = 100 - w24_val

raw_df = load_base_data(w23_val, w24_val)
df_base, base_national_dict = apply_custom_parties(raw_df, st.session_state.custom_parties_def)

PARTIES = list(DEFAULT_TRANSITIONS.keys()) + list(st.session_state.custom_parties_def.keys())

party_colors = {
    'AKP': '#FDA000', 'CHP': '#d33943', 'MHP': '#137BBB', 'DEM': '#90268F', 
    'IYI': '#63bbed', 'YRP': '#009840', 'TIP': '#FF1D25', 'ZAFER': '#474647', 
    'BBP': '#824d5d', 'SAADET': '#ff2e84', 'YENI': '#A7050E', 'A': '#20379f'
}
for cp_name, cp_data in st.session_state.custom_parties_def.items():
    party_colors[cp_name] = cp_data['color']

def calculate_dhondt(votes_dict, seat_count):
    seats_won = {p: 0 for p in votes_dict}
    divisors = {p: 1 for p in votes_dict}
    for _ in range(seat_count):
        winner = max(votes_dict.keys(), key=lambda p: votes_dict[p] / divisors[p])
        seats_won[winner] += 1
        divisors[winner] += 1
    return seats_won

@st.cache_data(show_spinner=False)
def run_simulation(base_df, base_nat, user_nat, alliances, joint_lists, threshold):
    working_nat = user_nat.copy()
    for umbrella, joiners in joint_lists.items():
        for jp in joiners:
            working_nat[umbrella] += working_nat.get(jp, 0)
            working_nat[jp] = 0.0

    party_to_alliance = {}
    for alliance_name, parties in alliances.items():
        for p in parties: party_to_alliance[p] = alliance_name
    for p in PARTIES:
        if p not in party_to_alliance:
            party_to_alliance[p] = p
            alliances[p] = [p]

    alliance_national_votes = {aly: sum([working_nat.get(p, 0) for p in parties]) for aly, parties in alliances.items()}
    qualified_parties = set([p for aly, vote in alliance_national_votes.items() if vote >= threshold for p in alliances[aly]])

    df = base_df.copy()
    
    df['P_c'] = df['party'].map(lambda p: user_nat.get(p, 0.0))
    df['B_c'] = df['party'].map(lambda p: base_nat.get(p, 0.0))
    df['R'] = df['base_vote_pct']
    
    R_clip = np.clip(df['R'], 0.001, 99.999)
    P_c_clip = np.clip(df['P_c'], 0.001, 99.999)
    B_c_clip = np.clip(df['B_c'], 0.001, 99.999)
    
    logit_R = np.log(R_clip / (100 - R_clip))
    logit_Pc = np.log(P_c_clip / (100 - P_c_clip))
    logit_Bc = np.log(B_c_clip / (100 - B_c_clip))
    
    logit_P_prop = logit_R + logit_Pc - logit_Bc
    P_prop = 100 / (1 + np.exp(-logit_P_prop))
    
    P_uni = df['R'] + (df['P_c'] - df['B_c'])
    
    kemik_kitle = df['R'] * 0.03
    P_uni_safe = np.maximum(kemik_kitle, P_uni)
    
    df['proj_vote'] = np.sqrt(np.maximum(0.001, P_prop) * P_uni_safe)
    
    df.loc[df['P_c'] <= 0.0, 'proj_vote'] = 0.0
    
    df['total_proj'] = df.groupby('district')['proj_vote'].transform('sum')
    df['norm_vote'] = (df['proj_vote'] / df['total_proj']) * 100
    df['norm_vote'] = df['norm_vote'].fillna(0)

    results = []
    for district, group in df.groupby('district'):
        seat_count = group['seat_count'].iloc[0]
        norm_votes = dict(zip(group['party'], group['norm_vote']))
        
        for umbrella, joiners in joint_lists.items():
            if umbrella in norm_votes:
                for jp in joiners:
                    if jp in norm_votes:
                        norm_votes[umbrella] += norm_votes[jp]
                        norm_votes[jp] = 0.0
                        
        eligible_votes = {p: norm_votes[p] for p in qualified_parties if p in norm_votes and norm_votes[p] > 0}
        district_seats = calculate_dhondt(eligible_votes, int(seat_count)) if eligible_votes else {}
            
        for party in PARTIES:
            results.append({
                'district': district,
                'province': district.split('-')[0],
                'seat_count': seat_count,
                'party': party,
                'new_vote_pct': norm_votes.get(party, 0),
                'seats_won': district_seats.get(party, 0)
            })
    return pd.DataFrame(results)

# Harita Çizim
@st.cache_data(show_spinner=False)
def load_raw_svg(svg_file_name="turkiye.svg"):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    if svg_file_name != "turkiye.svg":
        file_path = os.path.join(current_dir, "ilce", "harita", svg_file_name)
    else:
        file_path = os.path.join(current_dir, svg_file_name)
        
    try:
        with open(file_path, 'r', encoding='utf-8') as f: 
            return f.read()
    except Exception as e:
        return f"<svg viewBox='0 0 500 100'><text x='10' y='50' fill='red'>Harita dosyası bulunamadı: {svg_file_name}</text></svg>"

@st.cache_data(show_spinner=False)
def load_city_data(city_name, w23, w24):
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        df_23 = pd.read_csv(os.path.join(current_dir, "ilce", "veri", f"{city_name}2023.csv"))
        df_24 = pd.read_csv(os.path.join(current_dir, "ilce", "veri", f"{city_name}2024.csv"))
        
        if 'base_vote_pct' in df_23.columns:
            df_23['base_vote_pct'] = df_23['base_vote_pct'].astype(str).str.replace(',', '.').str.replace('%', '').astype(float)
        if 'base_vote_pct' in df_24.columns:
            df_24['base_vote_pct'] = df_24['base_vote_pct'].astype(str).str.replace(',', '.').str.replace('%', '').astype(float)

        df_23_clean = df_23.groupby(['district', 'party'], as_index=False)['base_vote_pct'].sum()
        df_24_clean = df_24.groupby(['district', 'party'], as_index=False)['base_vote_pct'].sum()

        df_23_clean['vote_23'] = df_23_clean.groupby('district')['base_vote_pct'].transform(lambda x: (x / x.sum()) * 100)
        df_24_clean['vote_24'] = df_24_clean.groupby('district')['base_vote_pct'].transform(lambda x: (x / x.sum()) * 100)

        norm_city = normalize_id(city_name)
        if norm_city in JOINT_LIST_2023_CORRECTIONS:
            correction = JOINT_LIST_2023_CORRECTIONS[norm_city]
            from_p, to_p, rate = correction['from_party'], correction['to_party'], correction['transfer_rate']
            
            for dist in df_23_clean['district'].unique():
                dist_mask = (df_23_clean['district'] == dist)
                from_mask = dist_mask & (df_23_clean['party'] == from_p)
                to_mask = dist_mask & (df_23_clean['party'] == to_p)
                
                if from_mask.any():
                    transfer_amount = df_23_clean.loc[from_mask, 'vote_23'].values[0] * rate
                    df_23_clean.loc[from_mask, 'vote_23'] -= transfer_amount
                    
                    if to_mask.any():
                        df_23_clean.loc[to_mask, 'vote_23'] += transfer_amount
                    else:
                        new_row = pd.DataFrame([{'district': dist, 'party': to_p, 'base_vote_pct': 0, 'vote_23': transfer_amount}])
                        df_23_clean = pd.concat([df_23_clean, new_row], ignore_index=True)

        df_merged = pd.merge(df_23_clean[['district', 'party', 'vote_23']], df_24_clean[['district', 'party', 'vote_24']], on=['district', 'party'], how='outer').fillna(0)
        
        df_merged['base_vote_pct'] = (df_merged['vote_23'] * (w23 / 100.0)) + (df_merged['vote_24'] * (w24 / 100.0))
        df_merged['province'] = city_name
        df_merged['seat_count'] = 0 
        return df_merged
    except FileNotFoundError:
        return pd.DataFrame()

def hex_to_rgb(hex_str):
    hex_str = hex_str.lstrip('#')
    return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))

def get_heatmap_color(base_hex, ratio):
    
    norm_ratio = max(0.0, min(1.0, (ratio - 0.25) / 0.35))
    
    curve = math.pow(norm_ratio, 3)
    
    hex_str = base_hex.lstrip('#')
    r, g, b = tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))
    
    fade_factor = 0.55
    
    fade_r = r + (200 - r) * fade_factor
    fade_g = g + (200 - g) * fade_factor
    fade_b = b + (200 - b) * fade_factor
    
    new_r = fade_r + (r - fade_r) * curve
    new_g = fade_g + (g - fade_g) * curve
    new_b = fade_b + (b - fade_b) * curve
    
    return f"#{int(new_r):02x}{int(new_g):02x}{int(new_b):02x}"

def get_svg_file_base64(file_path):
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            encoded = base64.b64encode(f.read()).decode("utf-8")
            return f"data:image/svg+xml;base64,{encoded}"
    return None

def get_party_logo_base64(party_name):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    normalized_p = normalize_id(party_name)
    variations = [party_name, party_name.lower(), party_name.upper(), normalized_p]
    
    if normalized_p in ['saadet', 'saadetpartisi', 'sp']: variations.extend(['SP', 'sp', 'SAADET', 'saadet_partisi'])
    elif normalized_p in ['dem', 'hedef', 'hdp']: variations.extend(['DEM', 'DEM_Parti'])
    elif normalized_p in ['iyi', 'iyiparti']: variations.extend(['IYI', 'iyi_parti'])

    for directory in [current_dir, os.path.join(current_dir, "logos")]:
        if not os.path.exists(directory): continue
        for var in set(variations):
            for ext in ['.svg', '.SVG', '.png', '.PNG']:
                target = os.path.join(directory, f"{var}{ext}")
                if os.path.exists(target):
                    with open(target, "rb") as f:
                        encoded = base64.b64encode(f.read()).decode("utf-8")
                        mime = "image/svg+xml" if ext.lower() == '.svg' else "image/png"
                        return f"data:{mime};base64,{encoded}"
    return None

ALL_PROVINCE_COORDS = {
    'kars': (1935, 260), 'tunceli': (1520, 460), 'karaman': (830, 750), 'ankara1': (750, 410), 'konya': (730, 620),
    'izmir2': (80, 500), 'elazig': (1510, 535), 'malatya': (1350, 540), 'afyonkarahisar': (510, 525), 'erzincan': (1510, 370),
    'burdur': (455, 705), 'bursa2': (390, 260), 'bursa1': (310, 310), 'ordu': (1310, 190), 'adana': (1060, 740),
    'giresun': (1415, 210), 'osmaniye': (1155, 745), 'ankara3': (690, 300), 'ankara2': (790, 300), 'agri': (1925, 375),
    'kayseri': (1100, 525), 'sakarya': (510, 215), 'gaziantep': (1300, 760), 'denizli': (370, 670), 'kutahya': (395, 430),
    'amasya': (1100, 210), 'trabzon': (1560, 185), 'artvin': (1790, 145), 'diyarbakir': (1615, 610), 'duzce': (580, 180), 'sinop': (1015, 65)
}

@st.cache_data(show_spinner=False)
def render_colored_svg(prov_winners, dist_winners, colors_dict, tooltip_dict, district_seats_data=None, svg_file_name="turkiye.svg", show_badges=True, custom_colors=None):
    custom_colors = custom_colors or {}
    try:
        raw_svg = load_raw_svg(svg_file_name)
        if not raw_svg or "<svg" not in raw_svg: 
            return "<div style='color:red;'>Geçersiz SVG dosyası.</div>"

        def fix_header(m):
            header = m.group(0)
            
            if 'viewBox' not in header and 'width' in header and 'height' in header:
                w_m = re.search(r'width=["\']([\d\.]+)px["\']', header)
                h_m = re.search(r'height=["\']([\d\.]+)px["\']', header)
                if w_m and h_m:
                    header = re.sub(r'\bwidth=["\'][^"\']*["\']', '', header)
                    header = re.sub(r'\bheight=["\'][^"\']*["\']', '', header)
                    header = header.replace('>', f' viewBox="0 0 {w_m.group(1)} {h_m.group(1)}">')
            
            vb_m = re.search(r'viewBox=["\']([\-\d\.\s,]+)["\']', header, re.IGNORECASE)
            if vb_m:
                parts = re.split(r'[, \t]+', vb_m.group(1).strip())
                if len(parts) == 4:
                    vx, vy, vw, vh = map(float, parts)
                    pad = 15.0
                    new_vb = f"{vx - pad} {vy - pad} {vw + (pad*2)} {vh + (pad*2)}"
                    header = header.replace(vb_m.group(0), f'viewBox="{new_vb}"')

            header = re.sub(r'\b(width|height|style)=["\'][^"\']*["\']', '', header)
            
            suffix = ' width="100%" height="100%" overflow="visible" style="max-width: 100%; max-height: 100%; object-fit: contain;" />' if header.endswith('/>') else ' width="100%" height="100%" overflow="visible" style="max-width: 100%; max-height: 100%; object-fit: contain;">'
            
            return header[:-2] + suffix if header.endswith('/>') else header[:-1] + suffix

        svg_content = re.sub(r'<svg\b[^>]*>', fix_header, raw_svg, count=1)
        
        badges_elements = []
        placed_badges = set()
        
        def fix_paths(m):
            path_tag = m.group(0)
            id_m = re.search(r'\b(id|name|data-name|title)=["\']([^"\']+)["\']', path_tag, re.IGNORECASE)
            if not id_m: return path_tag
            
            svg_id_norm = normalize_id(id_m.group(2))
            if not svg_id_norm: return path_tag
            
            winner = dist_winners.get(svg_id_norm) or prov_winners.get(svg_id_norm)
            if winner:
                color = custom_colors.get(svg_id_norm, colors_dict.get(winner, "#CCCCCC"))
                is_district = svg_file_name != "turkiye.svg"
                
                s_col = "#181720"
                s_wid = "2.5" if is_district else "8" 
                
                clean = re.sub(r'\b(style|fill|stroke|stroke-width|stroke-linejoin|class|data-tooltip|data-norm-id)=["\'][^"\']*["\']', '', path_tag, flags=re.IGNORECASE)
                
                new_attrs = f'style="fill: {color}; stroke: {s_col}; stroke-width: {s_wid}; stroke-linejoin: round; paint-order: stroke fill;" data-norm-id="{svg_id_norm}"'
                
                if tooltip_dict:
                    tip_raw = tooltip_dict.get(svg_id_norm, f"<b>{id_m.group(2)}</b><br>1. Sırada: {winner}")
                    tip_safe = tip_raw.replace('"', '&quot;')
                    new_attrs += f' data-tooltip="{tip_safe}" class="map-path"'
                
                if show_badges and district_seats_data and svg_id_norm not in placed_badges:
                    placed_badges.add(svg_id_norm)
                    parties_won_in_prov = {}
                    for (dist_tuple, seats) in district_seats_data.items():
                        dist_norm = normalize_id(dist_tuple[0].split('-')[0] if '-' in dist_tuple[0] else dist_tuple[0])
                        if dist_norm == svg_id_norm or normalize_id(dist_tuple[0]) == svg_id_norm:
                            if seats > 0: parties_won_in_prov[dist_tuple[1]] = parties_won_in_prov.get(dist_tuple[1], 0) + int(seats)
                    
                    sorted_winners = sorted(parties_won_in_prov.items(), key=lambda x: x[1], reverse=True)
                    if sorted_winners:
                        man_x, man_y = ALL_PROVINCE_COORDS.get(svg_id_norm, ("", ""))
                        is_metro = any(m in svg_id_norm for m in ['istanbul'])
                        r_val, f_size, y_offset, spacing = ('9.5', '9px', 3, 21) if is_metro else ('15', '16px', 4.5, 32)
                        
                        cols = 2 if len(sorted_winners) > 2 else len(sorted_winners)
                        rows = (len(sorted_winners) + cols - 1) // cols
                        base_start_y = -((rows - 1) * spacing) / 2
                        
                        b_str = f'<g class="badge-group" data-path-id="{svg_id_norm}" data-manual-x="{man_x}" data-manual-y="{man_y}">'
                        for i, (p_name, seat_num) in enumerate(sorted_winners):
                            p_color = colors_dict.get(p_name, '#333333')
                            row_idx, col_idx = i // cols, i % cols
                            items_in_row = cols if row_idx < rows - 1 else (len(sorted_winners) - (rows - 1) * cols)
                            start_x = -((items_in_row - 1) * spacing) / 2
                            cx, cy = start_x + (col_idx * spacing), base_start_y + (row_idx * spacing)
                            b_str += f'<circle cx="{cx}" cy="{cy}" r="{r_val}" fill="{p_color}" stroke="#ffffff" stroke-width="1.5"/>'
                            b_str += f'<text x="{cx}" y="{cy + y_offset}" text-anchor="middle" fill="#ffffff" font-size="{f_size}" font-family="Segoe UI, sans-serif" font-weight="bold" pointer-events="none">{seat_num}</text>'
                        b_str += '</g>'
                        badges_elements.append(b_str)
                
                if clean.endswith('/>'): return clean[:-2] + f' {new_attrs} />'
                else: return clean[:-1] + f' {new_attrs} >'
            return path_tag
            
        svg_content = re.sub(r'<path\b[^>]*>', fix_paths, svg_content)
        
        if show_badges and badges_elements:
            all_badges = '<g id="district-badges">' + "".join(badges_elements) + '</g>'
            svg_content = svg_content.replace('</svg>', f'{all_badges}</svg>')

        css_style = "<style>body{margin:0;overflow:hidden;background-color:transparent;display:flex;justify-content:center;align-items:center;height:100vh;}.map-container{position:relative;width:100%;height:100%;display:flex;justify-content:center;align-items:center;}svg{max-width:100%;max-height:100%;object-fit:contain;}.map-path{cursor:pointer;transition:opacity 0.2s;}.map-path:hover{opacity:0.8;}#svg-tooltip{position:absolute;display:none;background:white;border:1px solid #ccc;padding:10px 14px;box-shadow:0 4px 15px rgba(0,0,0,0.2);border-radius:6px;pointer-events:none;z-index:9999;font-family:'Segoe UI', Tahoma, sans-serif;font-size:13px;color:#333;min-width:190px;}.tip-header{font-weight:bold;font-size:14px;margin-bottom:6px;border-bottom:1px solid #eee;padding-bottom:4px;color:#111;}.tip-row{display:flex;align-items:center;margin-bottom:3px;}.tip-party{width:80px;font-weight:600;color:#333;}.tip-seat{background:#111;color:#fff;width:24px;text-align:center;font-weight:bold;font-size:11px;margin-right:6px;}.tip-bar-bg{flex-grow:1;background:#eee;height:12px;border-radius:2px;overflow:hidden;}.tip-bar-fill{height:100%;}.tip-pct{margin-left:6px;font-size:11px;color:#666;width:45px;text-align:right;} .badge-group { transition: transform 0.5s ease; }</style>"
        
        js_script = """
        <script>
        document.addEventListener("DOMContentLoaded", function() { 
            const paths = document.querySelectorAll('.map-path'); 
            const tooltip = document.getElementById('svg-tooltip'); 
            const wrapper = document.getElementById('map-wrapper'); 
            
            paths.forEach(path => { 
                path.addEventListener('mousemove', (e) => { 
                    const tooltipData = path.getAttribute('data-tooltip'); 
                    if(tooltipData) { 
                        tooltip.innerHTML = tooltipData; 
                        tooltip.style.display = 'block'; 
                        
                        const rect = wrapper.getBoundingClientRect(); 
                        const tipRect = tooltip.getBoundingClientRect(); 
                        
                        let x = e.clientX - rect.left + 15; 
                        let y = e.clientY - rect.top + 15; 
                        
                        if (x + tipRect.width + 15 > rect.width) { x = e.clientX - rect.left - tipRect.width - 15; } 
                        if (y + tipRect.height + 15 > rect.height) { y = e.clientY - rect.top - tipRect.height - 15; } 
                        if (x < 10) x = 10;
                        if (y < 10) y = 10;
                        
                        tooltip.style.left = x + 'px'; 
                        tooltip.style.top = y + 'px'; 
                    } 
                }); 
                
                path.addEventListener('mouseleave', () => { tooltip.style.display = 'none'; }); 
            }); 
            
            setTimeout(() => { 
                const badgeGroups = document.querySelectorAll('.badge-group'); 
                badgeGroups.forEach(bg => { 
                    const manualX = bg.getAttribute('data-manual-x'); 
                    const manualY = bg.getAttribute('data-manual-y'); 
                    if (manualX && manualY) { 
                        bg.setAttribute('transform', `translate(${manualX}, ${manualY})`); 
                    } else { 
                        const pathId = bg.getAttribute('data-path-id'); 
                        const targetPath = document.querySelector(`.map-path[data-norm-id="${pathId}"]`); 
                        if (targetPath) { 
                            const bbox = targetPath.getBBox(); 
                            if(bbox.width > 0 && bbox.height > 0) { 
                                const centerX = bbox.x + (bbox.width / 2); 
                                const centerY = bbox.y + (bbox.height / 2); 
                                bg.setAttribute('transform', `translate(${centerX}, ${centerY})`); 
                            } 
                        } 
                    } 
                }); 
            }, 100); 
        });
        </script>
        """

        if not tooltip_dict:
            return svg_content
        return f"<!DOCTYPE html><html><head>{css_style}</head><body><div class='map-container' id='map-wrapper'><div id='svg-tooltip'></div>{svg_content}</div>{js_script}</body></html>"
    except Exception as e:
        return f"<div style='color:red;'>SVG Hatası: {str(e)}</div>"

# İnfografik
def generate_infographic_svg(national_summary_df, map_svg_str, total_seats, assigned_parties, party_colors, alliances_dict):
    svg = '<svg width="1200" height="980" viewBox="0 0 1200 980" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" style="background-color: white; font-family: \'Space Grotesk\', sans-serif;">'
    svg += '<rect width="100%" height="100%" fill="#ffffff" />'

    party_to_aly = {p: aly for aly, pts in alliances_dict.items() for p in pts}
    winning_df = national_summary_df[national_summary_df['Vekil'] > 0].copy()

    blocks = {}
    for _, row in winning_df.iterrows():
        aly = party_to_aly.get(row['Parti'], row['Parti'])
        blocks.setdefault(aly, []).append(row)

    sorted_blocks = sorted(blocks.items(), key=lambda b: sum(r['Normalize Oy (%)'] for r in b[1]), reverse=True)
    sorted_party_rows, block_spans = [], []

    for aly_name, p_rows in sorted_blocks:
        start_idx = len(sorted_party_rows)
        sorted_party_rows.extend(sorted(p_rows, key=lambda r: r['Normalize Oy (%)'], reverse=True))
        
        if len(sorted_party_rows) - 1 >= start_idx and aly_name in alliances_dict and len(p_rows) > 1:
            block_spans.append((aly_name, start_idx, len(sorted_party_rows) - 1))

    if not sorted_party_rows: sorted_party_rows = [row for _, row in national_summary_df.head(4).iterrows()]

    card_size, card_spacing = 80, 22
    start_x = (1200 - (len(sorted_party_rows) * card_size + (len(sorted_party_rows) - 1) * card_spacing)) / 2

    for aly_name, s_idx, e_idx in block_spans:
        bx1, bx2 = start_x + s_idx * (card_size + card_spacing), start_x + e_idx * (card_size + card_spacing) + card_size
        svg += f'<line x1="{bx1}" y1="36" x2="{bx2}" y2="36" stroke="#181720" stroke-width="2.5"/><text x="{(bx1 + bx2)/2}" y="25" text-anchor="middle" font-size="12" font-weight="900" fill="#181720">{aly_name}</text>'

    for idx, row in enumerate(sorted_party_rows):
        p_name, seats, vote = row['Parti'], int(row['Vekil']), float(row['Normalize Oy (%)'])
        color, cx = party_colors.get(p_name, '#888888'), start_x + idx * (card_size + card_spacing)
        logo_data = get_party_logo_base64(p_name)

        svg += f'<rect x="{cx + 4}" y="56" width="{card_size}" height="{card_size}" fill="#181720" rx="2"/><rect x="{cx}" y="52" width="{card_size}" height="{card_size}" fill="{color}" stroke="#181720" stroke-width="2.5" rx="2"/>'
        if logo_data:
            svg += f'<image href="{logo_data}" x="{cx + 10}" y="{62}" width="{card_size - 20}" height="{card_size - 20}" preserveAspectRatio="xMidYMid meet" />'
        else:
            svg += f'<text x="{cx + card_size/2}" y="{52 + card_size/2 + 7}" text-anchor="middle" fill="#ffffff" font-weight="900" font-size="18">{p_name}</text>'
        svg += f'<text x="{cx + card_size/2}" y="160" text-anchor="middle" fill="#181720" font-weight="900" font-size="24">{seats}</text><text x="{cx + card_size/2}" y="180" text-anchor="middle" fill="#666666" font-weight="700" font-size="13">% {vote:.2f}</text>'

    map_svg_clean = re.sub(r"<\?xml.*?\?>", "", map_svg_str)
    svg += f'<svg x="30" y="195" width="1120" height="520">{map_svg_clean}</svg>'

    main_logo_data = get_svg_file_base64(os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo.svg"))
    svg += '<g transform="translate(30, 870)">'
    if main_logo_data:
        svg += f'<image href="{main_logo_data}" x="0" y="0" width="320" height="75" preserveAspectRatio="xMinYMin meet" />'
    else:
        svg += '<text x="0" y="50" font-size="32" font-weight="900" fill="#eb252d">AD PROJEKSİYON</text>'
    svg += '</g>'

    radii = list(range(125, 245, 10)) 
    sum_radii = sum(radii)
    seats_per_row = [round(total_seats * (r / sum_radii)) for r in radii]
    if sum(seats_per_row) != total_seats: seats_per_row[-1] += (total_seats - sum(seats_per_row))
    
    points = sorted([{'x': r * math.cos(math.pi - (math.pi * j) / max(1, (s - 1))), 'y': r * math.sin(math.pi - (math.pi * j) / max(1, (s - 1))), 'angle': math.pi - (math.pi * j) / max(1, (s - 1)), 'r': r} for r, s in zip(radii, seats_per_row) if s > 0 for j in range(s)], key=lambda p: (p['angle'], -p['r']), reverse=True)

    svg += '<g transform="translate(910, 930)">'
    
    for i, party in enumerate(assigned_parties):
        if i < len(points): svg += f'<circle cx="{points[i]["x"]}" cy="{-points[i]["y"]}" r="4.3" fill="{party_colors.get(party, "#888")}" />'
    
    svg += f'<text x="0" y="-250" text-anchor="middle" font-size="14" font-weight="900" fill="#181720">Çoğunluk</text>'
    svg += f'<line x1="0" y1="-242" x2="0" y2="-122" stroke="#181720" stroke-width="2.5" stroke-dasharray="5,5"/>'
    svg += f'<text x="0" y="-12" text-anchor="middle" font-size="44" font-weight="900" fill="#181720">{total_seats}</text></g></svg>'
    
    return svg

def generate_regional_infographic_svg(province_name, top_parties_df, map_svg_str, party_colors):
    svg = '<svg width="1200" height="980" viewBox="0 0 1200 980" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" style="background-color: white; font-family: \'Space Grotesk\', sans-serif;">'
    svg += '<rect width="100%" height="100%" fill="#ffffff" />'
    
    card_size = 80
    card_spacing = 22
    
    sorted_party_rows = [row for row in top_parties_df.itertuples()]
    start_x = (1200 - (len(sorted_party_rows) * card_size + (len(sorted_party_rows) - 1) * card_spacing)) / 2

    svg += f'<text x="600" y="30" text-anchor="middle" font-size="20" font-weight="900" fill="#181720" letter-spacing="1px">{province_name} İLİ SEÇİM SONUÇLARI</text>'
    
    for idx, row in enumerate(sorted_party_rows):
        p_name = row.party
        vote_pct = float(row.new_vote_pct)
        seats = int(row.seats_won) if hasattr(row, 'seats_won') else 0
        color = party_colors.get(p_name, '#888888')
        cx = start_x + idx * (card_size + card_spacing)
        logo_data = get_party_logo_base64(p_name)
        
        svg += f'<rect x="{cx + 4}" y="56" width="{card_size}" height="{card_size}" fill="#181720" rx="2"/>'
        svg += f'<rect x="{cx}" y="52" width="{card_size}" height="{card_size}" fill="{color}" stroke="#181720" stroke-width="2.5" rx="2"/>'
        
        if logo_data:
            svg += f'<image href="{logo_data}" x="{cx + 10}" y="{62}" width="{card_size - 20}" height="{card_size - 20}" preserveAspectRatio="xMidYMid meet" />'
        else:
            svg += f'<text x="{cx + card_size/2}" y="{52 + card_size/2 + 7}" text-anchor="middle" fill="#ffffff" font-weight="900" font-size="18">{p_name}</text>'
        
        svg += f'<text x="{cx + card_size/2}" y="160" text-anchor="middle" fill="#181720" font-weight="900" font-size="24">{seats}</text>'
        svg += f'<text x="{cx + card_size/2}" y="180" text-anchor="middle" fill="#666666" font-weight="700" font-size="13">% {vote_pct:.2f}</text>'

    map_svg_clean = re.sub(r"<\?xml.*?\?>", "", map_svg_str)
    svg += f'<svg x="20" y="210" width="1160" height="630">{map_svg_clean}</svg>'
    
    main_logo_data = get_svg_file_base64(os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo.svg"))
    svg += '<g transform="translate(30, 880)">'
    if main_logo_data:
        svg += f'<image href="{main_logo_data}" x="0" y="0" width="320" height="75" preserveAspectRatio="xMinYMin meet" />'
    else:
        svg += '<text x="0" y="50" font-size="32" font-weight="900" fill="#eb252d">AD PROJEKSİYON</text>'
    svg += '</g>'
        
    svg += '</svg>'
    return svg

# Arayüz ve Yan Menü
st.title("AD Türkiye Genel Seçim Projeksiyonu")

PREDEFINED_SCENARIOS = {
    "2023 Genel Seçim Sonuçları": {'AKP': 35.6, 'CHP': 25.3, 'MHP': 10.1, 'IYI': 9.7, 'DEM': 8.8, 'YRP': 2.8, 'ZAFER': 2.2, 'TIP': 1.8, 'BBP': 1.0, 'SAADET': 0.0, 'YENI': 0.0, 'A': 0.0},
    "2024 Yerel Seçim Sonuçları": {'AKP': 32.4, 'CHP': 34.5, 'MHP': 6.6, 'IYI': 4.6, 'DEM': 5.8, 'YRP': 7, 'ZAFER': 2.4, 'TIP': 0.6, 'YENI': 0.0, 'A': 0.0},
    "Anket Delisi Projeksiyon": {'AKP': 27.4, 'CHP': 1.0, 'MHP': 6.4, 'DEM': 7.6, 'IYI': 5.1, 'YRP': 3.8, 'ZAFER': 2.6, 'TIP': 1.5, 'YENI': 37.0, 'A': 4.1, 'BBP': 0.9, 'SAADET': 1.2}
}

custom_start_values = PREDEFINED_SCENARIOS["Anket Delisi Projeksiyon"]

if 'alliance_list' not in st.session_state:
    st.session_state.alliance_list = [{"id": "aly_1", "name": "Cumhur İttifakı", "parties": [p for p in ['AKP', 'MHP', 'BBP'] if p in PARTIES]}, {"id": "aly_2", "name": "Emek ve Özgürlük İttifakı", "parties": [p for p in ['DEM', 'TIP'] if p in PARTIES]}]
    st.session_state.next_aly_id = 3

if 'joint_list' not in st.session_state:
    st.session_state.joint_list = []
    st.session_state.next_jl_id = 1

if 'active_parties' not in st.session_state:
    ozel_sira = ["AKP", "YENI", "DEM", "MHP", "IYI", "YRP", "A", "ZAFER", "TIP", "SAADET", "BBP", "CHP"]
    st.session_state.active_parties = [p for p in ozel_sira if p in PARTIES] + [p for p in PARTIES if p not in ozel_sira]

with st.sidebar.expander("📌 Proje Hakkında", expanded=False):
    st.markdown("""
    **AD Projeksiyon**, Türkiye genel seçimleri ve cumhurbaşkanlığı seçimleri için geliştirilmiş gelişmiş bir veri analizi ve simülasyon aracıdır. 
    
    Log-odds ve geometrik ortalama tabanlı algoritmalarla ilçe bazlı **oy kayması (swing)** hesaplar, **D'Hondt sistemi** ile milletvekili dağılımını yansıtır ve sonuçları interaktif haritalara döker.
    """)

st.sidebar.markdown(f"""
<style>
/* Daha az yer kaplayan, ince kart yapısı */
section[data-testid="stSidebar"] div[data-testid="stVerticalBlockBorderWrapper"] {{
    padding: 4px 8px !important;
    margin-bottom: 8px !important;
    border: 3px solid {c_text} !important;
    border-left: 8px solid #eb252d !important;
    box-shadow: 3px 3px 0px {c_text} !important;
    border-radius: 0px !important;
    background-color: {sidebar_input_bg} !important;
}}
/* Tüm Sütunları Dikeyde Tam Ortala (CSS Güvencesi) */
section[data-testid="stSidebar"] div[data-testid="stVerticalBlockBorderWrapper"] div[data-testid="stHorizontalBlock"] {{
    align-items: center !important;
}}
/* Streamlit'in kendi bıraktığı gereksiz boşlukları sıfırlama */
section[data-testid="stSidebar"] div[data-testid="stVerticalBlockBorderWrapper"] .stMarkdown {{
    margin-bottom: 0px !important;
}}
/* Oy Giriş Kutusu */
section[data-testid="stSidebar"] div[data-testid="stVerticalBlockBorderWrapper"] div[data-baseweb="input"] {{
    height: 32px !important;
    border: 2px solid {c_text} !important;
    box-shadow: none !important;
    background-color: #ffffff !important;
    min-width: 55px !important; 
}}
section[data-testid="stSidebar"] div[data-testid="stVerticalBlockBorderWrapper"] input {{
    padding: 0px 4px !important;
    font-weight: 900 !important;
    color: #3485fd !important;
    font-size: 15px !important;
    text-align: center !important;
}}
/* Hiza Düzeltmeleri */
.party-card-name {{ font-weight: 900; font-size: 16px; color: {c_text}; white-space: nowrap; overflow: visible; display: flex; align-items: center; height: 32px; }}
.party-logo-box {{ width: 32px; height: 32px; border: 2px solid {c_text}; display: flex; align-items: center; justify-content: center; }}
.party-logo-box img {{ max-width: 80%; max-height: 80%; object-fit: contain; }}
.pct-sign {{ font-weight: 900; font-size: 15px; color: {c_text}; display: flex; align-items: center; justify-content: center; height: 32px; }}
/* Silme Tuşu */
section[data-testid="stSidebar"] div[data-testid="stVerticalBlockBorderWrapper"] button {{ background-color: #eb252d !important; color: white !important; border: 2px solid {c_text} !important; padding: 0px !important; height: 32px !important; width: 100% !important; min-width: 32px !important; box-shadow: 2px 2px 0px {c_text} !important; border-radius: 0px !important; display: flex; align-items: center; justify-content: center; }}
section[data-testid="stSidebar"] div[data-testid="stVerticalBlockBorderWrapper"] button p {{ font-size: 16px !important; margin: 0 !important; line-height: 1 !important; }}
section[data-testid="stSidebar"] div[data-testid="stVerticalBlockBorderWrapper"] button:hover {{ background-color: #181720 !important; transform: translate(2px, 2px); box-shadow: 0px 0px 0px {c_text} !important; }}
</style>
""", unsafe_allow_html=True)

st.sidebar.header("📂 Senaryo Yönetimi")

selected_scenario = st.sidebar.selectbox("Hazır Senaryo Yükle:", options=["Seçiniz..."] + list(PREDEFINED_SCENARIOS.keys()), key="scenario_selector")
if selected_scenario != "Seçiniz...":
    if st.sidebar.button("Yukarıdaki Senaryoyu Uygula", use_container_width=True):
        for p in PARTIES:
            if f"inp_{p}" in st.session_state: 
                del st.session_state[f"inp_{p}"]
        for p, val in PREDEFINED_SCENARIOS[selected_scenario].items():
            st.session_state[f"inp_{p}"] = float(val)
        
        ozel_sira = ["AKP", "YENI", "DEM", "MHP", "IYI", "YRP", "A", "ZAFER", "TIP", "SAADET", "BBP", "CHP"]
        st.session_state.active_parties = [p for p in ozel_sira if p in PARTIES] + [p for p in PARTIES if p not in ozel_sira]
        st.rerun()

# JSON ile İçe / Dışa Aktarma
with st.sidebar.expander("💾 Veriyi İçe / Dışa Aktar", expanded=False):
    st.caption("Mevcut partileri, oranları ve ittifakları bilgisayarınıza kaydedin veya daha önce kaydettiğiniz bir senaryoyu yükleyin.")
    
    # Dışa Aktarma Butonu
    export_data = {
        "active_parties": st.session_state.active_parties,
        "votes": {p: st.session_state.get(f"inp_{p}", custom_start_values.get(p, float(base_national_dict.get(p, 0.0)))) for p in st.session_state.active_parties},
        "custom_parties": st.session_state.custom_parties_def,
        "alliances": st.session_state.alliance_list,
        "joints": st.session_state.joint_list
    }
    json_str = json.dumps(export_data, indent=4)
    st.download_button("⬇️ Senaryoyu İndir (JSON)", data=json_str, file_name="ad_projeksiyon_senaryo.json", mime="application/json", use_container_width=True)
    
    st.markdown("<hr style='margin: 10px 0;'>", unsafe_allow_html=True)
    
    # İçe Aktarma Kutusu
    uploaded_file = st.file_uploader("⬆️ Senaryo Yükle (JSON)", type="json")
    if uploaded_file is not None:
        if st.button("Yüklenen Dosyayı Uygula", use_container_width=True):
            try:
                imported_data = json.load(uploaded_file)
                st.session_state.active_parties = imported_data.get("active_parties", st.session_state.active_parties)
                
                for p, v in imported_data.get("votes", {}).items():
                    st.session_state[f"inp_{p}"] = float(v)
                    
                st.session_state.custom_parties_def = imported_data.get("custom_parties", {})
                st.session_state.alliance_list = imported_data.get("alliances", [])
                st.session_state.joint_list = imported_data.get("joints", [])
                
                if st.session_state.alliance_list:
                    st.session_state.next_aly_id = max([int(a['id'].split('_')[1]) for a in st.session_state.alliance_list if '_' in a['id']] + [0]) + 1
                if st.session_state.joint_list:
                    st.session_state.next_jl_id = max([int(a['id'].split('_')[1]) for a in st.session_state.joint_list if '_' in a['id']] + [0]) + 1
                    
                st.rerun()
            except Exception as e:
                st.error("Dosya okunurken hata oluştu! Geçerli bir JSON olduğundan emin olun.")

st.sidebar.divider()
st.sidebar.header("⚖️ Veri Seti Ağırlıkları")
st.sidebar.caption("Simülasyonun tabanını oluştururken 2023 Genel ve 2024 Yerel seçim verilerinin hangi oranda harmanlanacağını belirleyin.")

weight_24_input = st.sidebar.number_input(
    "2024 Yerel Seçim Etkisi (%)", 
    min_value=0.0, 
    max_value=100.0, 
    value=float(st.session_state.get("w24_weight", 10.0)), 
    step=1.0, 
    key="w24_weight"
)

weight_23_input = 100.0 - weight_24_input

st.sidebar.info(f"Geçerli Taban: **%{weight_23_input:.1f}** (2023) + **%{weight_24_input:.1f}** (2024)")

st.sidebar.divider()
st.sidebar.header("Ulusal Oy Oranları")

user_inputs = {}
parties_to_remove = []

for p in st.session_state.active_parties:
    varsayilan_oy = custom_start_values.get(p, float(base_national_dict.get(p, 0.0)))
    party_color = party_colors.get(p, "#888")
    
    with st.sidebar.container(border=True):
        try:
            cols = st.columns([0.16, 0.32, 0.32, 0.05, 0.15], gap="small", vertical_alignment="center")
        except TypeError:
            cols = st.columns([0.16, 0.32, 0.32, 0.05, 0.15], gap="small")
        
        with cols[0]:
            logo_data = get_party_logo_base64(p)
            if logo_data:
                st.markdown(f'<div class="party-logo-box" style="background-color: {party_color};"><img src="{logo_data}"></div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="party-logo-box" style="background-color: {party_color};"></div>', unsafe_allow_html=True)
        
        with cols[1]:
            st.markdown(f'<div class="party-card-name">{p}</div>', unsafe_allow_html=True)
            
        with cols[2]:
            val = st.number_input(f"oy_{p}", min_value=0.0, max_value=100.0, value=st.session_state.get(f"inp_{p}", varsayilan_oy), step=0.1, key=f"inp_{p}", label_visibility="collapsed")
            user_inputs[p] = val
            
        with cols[3]:
            st.markdown('<div class="pct-sign">%</div>', unsafe_allow_html=True)
            
        with cols[4]:
            if st.button("🗑️", key=f"del_p_{p}"):
                parties_to_remove.append(p)

for p in PARTIES:
    if p not in st.session_state.active_parties:
        user_inputs[p] = 0.0

if parties_to_remove:
    for rp in parties_to_remove:
        st.session_state.active_parties.remove(rp)
        if f"inp_{rp}" in st.session_state:
            del st.session_state[f"inp_{rp}"]
    st.rerun()

if len(st.session_state.active_parties) < len(PARTIES):
    st.sidebar.markdown("<br>", unsafe_allow_html=True)
    if st.sidebar.button("🔄 Çıkarılan Partileri Geri Getir", use_container_width=True):
        st.session_state.active_parties = PARTIES.copy()
        st.rerun()

with st.sidebar.expander("🛠️ YENİ PARTİ EKLE", expanded=False):
    st.caption("Yeni partinin hangi partilerin tabanından yüzde kaç oy çekeceğini ve rengini belirleyin.")
    new_p_name = st.text_input("Parti Kısaltması (Örn: VKP)", max_chars=12).upper()
    new_p_color = st.color_picker("Parti Rengi", "#610030")
    
    base_ps = st.multiselect("Hangi Partilerin Tabanından Oy Alacak?", list(DEFAULT_TRANSITIONS.keys()), key="new_party_bases")
    
    new_p_bases = {}
    for bp in base_ps:
        new_p_bases[bp] = st.number_input(f"{bp} seçmeninin % kaçı geçecek?", min_value=0.0, max_value=100.0, value=50.0, step=5.0, key=f"base_ratio_{bp}")
        
    if st.button("Partiyi Sisteme Ekle", use_container_width=True):
        if new_p_name and new_p_bases:
            st.session_state.custom_parties_def[new_p_name] = {'color': new_p_color, 'bases': new_p_bases}
            st.rerun()
        elif not new_p_name:
            st.error("Lütfen parti kısaltması giriniz.")
        else:
            st.error("Lütfen en az bir adet taban partisi seçiniz.")

    if st.session_state.custom_parties_def:
        st.markdown("---")
        st.markdown("**Eklenmiş Özel Partiler:**")
        party_to_delete = st.selectbox("Silinecek Partiyi Seçin", options=list(st.session_state.custom_parties_def.keys()), key="del_custom_party_selectbox")
        if st.button("Seçilen Partiyi Sil", use_container_width=True):
            if party_to_delete in st.session_state.custom_parties_def:
                del st.session_state.custom_parties_def[party_to_delete]
                if f"inp_{party_to_delete}" in st.session_state:
                    del st.session_state[f"inp_{party_to_delete}"]
                st.rerun()

st.sidebar.divider()
threshold_input = st.sidebar.number_input("Ülke Barajı (%)", min_value=0.0, max_value=15.0, value=7.0, step=0.5)

st.sidebar.divider()
st.sidebar.subheader("İttifak Seçenekleri")
alliances_to_remove = []
for aly in st.session_state.alliance_list:
    col1, col2 = st.sidebar.columns([0.85, 0.15])
    aly['name'] = col1.text_input("İttifak Adı", value=aly['name'], key=f"name_{aly['id']}", label_visibility="collapsed")
    if col2.button("🗑️", key=f"del_{aly['id']}", help="Bu ittifakı sil"): alliances_to_remove.append(aly)
    aly['parties'] = st.sidebar.multiselect("Partiler", options=PARTIES, default=[p for p in aly['parties'] if p in PARTIES], key=f"parties_{aly['id']}", label_visibility="collapsed")
    st.sidebar.write("")

for aly in alliances_to_remove: st.session_state.alliance_list.remove(aly)
if alliances_to_remove: st.rerun()

if st.sidebar.button("➕ Yeni İttifak Ekle", use_container_width=True):
    st.session_state.alliance_list.append({"id": f"aly_{st.session_state.next_aly_id}", "name": f"Yeni Blok {st.session_state.next_aly_id}", "parties": []})
    st.session_state.next_aly_id += 1
    st.rerun()

st.sidebar.divider()
st.sidebar.subheader("Ortak Liste Seçenekleri")
st.sidebar.caption("Seçilen İLK parti çatı (logo) parti olur.")
jl_to_remove = []

for idx, jl in enumerate(st.session_state.joint_list):
    col1, col2 = st.sidebar.columns([0.85, 0.15])
    jl['parties'] = col1.multiselect(f"{jl['parties'][0]} Listesi" if jl.get('parties') else f"Yeni Liste {idx + 1}", options=PARTIES, default=jl.get('parties', []), key=f"join_{jl['id']}")
    st.sidebar.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
    if col2.button("🗑️", key=f"del_jl_{jl['id']}", help="Sil"): jl_to_remove.append(jl)

for jl in jl_to_remove: st.session_state.joint_list.remove(jl)
if jl_to_remove: st.rerun()

if st.sidebar.button("➕ Ortak Liste Ekle", use_container_width=True):
    st.session_state.joint_list.append({"id": f"jl_{st.session_state.next_jl_id}", "parties": []})
    st.session_state.next_jl_id += 1
    st.rerun()

st.sidebar.markdown("<br>", unsafe_allow_html=True)

if st.sidebar.button("🚀 SİMÜLASYONU ÇALIŞTIR", type="primary", use_container_width=True):
    st.session_state.calc_params = {"user_inputs": copy.deepcopy(user_inputs), "threshold_input": threshold_input, "alliance_list": copy.deepcopy(st.session_state.alliance_list), "joint_list": copy.deepcopy(st.session_state.joint_list)}

if "calc_params" not in st.session_state:
    st.session_state.calc_params = {"user_inputs": copy.deepcopy(user_inputs), "threshold_input": threshold_input, "alliance_list": copy.deepcopy(st.session_state.alliance_list), "joint_list": copy.deepcopy(st.session_state.joint_list)}

# Projeksiyonu Çalıştırma
params = st.session_state.calc_params
p_threshold = params["threshold_input"]
total_input = sum(params["user_inputs"].values())
if abs(total_input - 100.0) > 0.1: st.sidebar.warning(f"Simülasyondaki toplam oy %{total_input:.1f}. Oylar %100'e normalize ediliyor.")
user_inputs_norm = {p: (v / total_input) * 100 if total_input > 0 else 0 for p, v in params["user_inputs"].items()}

alliances = {aly['name']: aly['parties'] for aly in params["alliance_list"] if aly['name'].strip() and aly['parties']}
joint_lists = {jl['parties'][0]: jl['parties'][1:] for jl in params["joint_list"] if len(jl['parties']) > 1}

df_results = run_simulation(df_base, base_national_dict, user_inputs_norm, alliances, joint_lists, params["threshold_input"])

display_user_nat = user_inputs_norm.copy()
for umbrella, joiners in joint_lists.items():
    for jp in joiners:
        display_user_nat[umbrella] += display_user_nat.get(jp, 0)
        display_user_nat[jp] = 0.0

base_seats_2023 = {'AKP': 268, 'CHP': 169, 'DEM': 61, 'MHP': 50, 'IYI': 43, 'YRP': 5, 'TIP': 4, 'ZAFER': 0, 'YENI': 0, 'A': 0, 'BBP': 0, 'SAADET': 0}
base_votes_2023 = {'AKP': 35.6, 'CHP': 25.3, 'MHP': 10.1, 'IYI': 9.7, 'DEM': 8.8, 'YRP': 2.8, 'ZAFER': 2.2, 'TIP': 1.8, 'BBP': 1.0, 'SAADET': 0.0, 'YENI': 0.0, 'A': 0.0}
katilan_partiler = [jp for joiners in joint_lists.values() for jp in joiners]

summary_data = [{'Parti': p, 'Normalize Oy (%)': round(display_user_nat.get(p, 0), 2), 'Oy Değişimi': round(display_user_nat.get(p, 0) - base_votes_2023.get(p, 0.0), 2), 'Vekil': int(df_results[df_results['party'] == p]['seats_won'].sum()), 'Vekil Değişimi': int(df_results[df_results['party'] == p]['seats_won'].sum() - base_seats_2023.get(p, 0))} for p in st.session_state.active_parties if p not in katilan_partiler]
national_summary_df = pd.DataFrame(summary_data).sort_values(by=['Normalize Oy (%)', 'Vekil'], ascending=[False, False])

PROVINCE_NAMES = {
        'adana': 'Adana', 'adiyaman': 'Adıyaman', 'afyonkarahisar': 'Afyonkarahisar', 'agri': 'Ağrı',
        'amasya': 'Amasya', 'ankara': 'Ankara', 'antalya': 'Antalya', 'artvin': 'Artvin', 'aydin': 'Aydın',
        'balikesir': 'Balıkesir', 'bilecik': 'Bilecik', 'bingol': 'Bingöl', 'bitlis': 'Bitlis',
        'bolu': 'Bolu', 'burdur': 'Burdur', 'bursa': 'Bursa', 'canakkale': 'Çanakkale', 'cankiri': 'Çankırı',
        'corum': 'Çorum', 'denizli': 'Denizli', 'diyarbakir': 'Diyarbakır', 'edirne': 'Edirne',
        'elazig': 'Elazığ', 'erzincan': 'Erzincan', 'erzurum': 'Erzurum', 'eskisehir': 'Eskişehir',
        'gaziantep': 'Gaziantep', 'giresun': 'Giresun', 'gumushane': 'Gümüşhane', 'hakkari': 'Hakkari',
        'hatay': 'Hatay', 'isparta': 'Isparta', 'mersin': 'Mersin', 'istanbul': 'İstanbul', 'izmir': 'İzmir',
        'kars': 'Kars', 'kastamonu': 'Kastamonu', 'kayseri': 'Kayseri', 'kirklareli': 'Kırklareli',
        'kirsehir': 'Kırşehir', 'kocaeli': 'Kocaeli', 'konya': 'Konya', 'kutahya': 'Kütahya',
        'malatya': 'Malatya', 'manisa': 'Manisa', 'kahramanmaras': 'Kahramanmaraş', 'mardin': 'Mardin',
        'mugla': 'Muğla', 'mus': 'Muş', 'nevsehir': 'Nevşehir', 'nigde': 'Niğde', 'ordu': 'Ordu',
        'rize': 'Rize', 'sakarya': 'Sakarya', 'samsun': 'Samsun', 'siirt': 'Siirt', 'sinop': 'Sinop',
        'sivas': 'Sivas', 'tekirdag': 'Tekirdağ', 'tokat': 'Tokat', 'trabzon': 'Trabzon', 'tunceli': 'Tunceli',
        'sanliurfa': 'Şanlıurfa', 'usak': 'Uşak', 'van': 'Van', 'yozgat': 'Yozgat', 'zonguldak': 'Zonguldak',
        'aksaray': 'Aksaray', 'bayburt': 'Bayburt', 'karaman': 'Karaman', 'kirikkale': 'Kırıkkale',
        'batman': 'Batman', 'sirnak': 'Şırnak', 'bartin': 'Bartın', 'ardahan': 'Ardahan', 'igdir': 'Iğdır',
        'yalova': 'Yalova', 'karabuk': 'Karabük', 'kilis': 'Kilis', 'osmaniye': 'Osmaniye', 'duzce': 'Düzce'
    }

def get_display_name(norm_id):
    return PROVINCE_NAMES.get(norm_id, norm_id.title())

def get_available_cities():
    harita_dir = os.path.join(current_dir, "ilce", "harita")
    cities = []
    if os.path.exists(harita_dir):
        for file in os.listdir(harita_dir):
            if file.lower().endswith(".svg"):
                cities.append(normalize_id(file[:-4]))
    return sorted(list(set(cities)))

available_cities = get_available_cities()
all_provinces_norm = sorted(list(set([normalize_id(p) for p in df_results['province'].unique()])))

#Sekmeler
tab_meclis, tab_cb = st.tabs(["🏛️ Parlamento", "🗳️ Cumhurbaşkanlığı"])

with tab_meclis:
    st.header("🏛️ TBMM SANDALYE DAĞILIMI VE OY ORANLARI")
    col1, col2 = st.columns([1.2, 1])

    with col1:
        st.markdown("<h3 style='text-align: center; margin-top: 0;'>OY ORANLARI</h3>", unsafe_allow_html=True)
        max_vote_pct = national_summary_df['Normalize Oy (%)'].max() or 1.0
        html_blocks = ["<style>.custom-row { display: flex; align-items: center; margin-bottom: 8px; font-family: 'Space Grotesk', sans-serif; } .custom-party { width: 110px; text-align: right; padding-right: 12px; font-weight: 900; color: " + c_text + "; font-size: 16px; text-transform: uppercase; } .custom-seat { background-color: " + t_seat_bg + "; color: #ffffff !important; font-weight: bold; width: 60px; text-align: center; padding: 4px 0; margin-right: 10px; border: 2px solid " + c_text + "; box-shadow: 3px 3px 0px #eb252d; display: flex; flex-direction: column; justify-content: center; line-height: 1.1; } .seat-num { font-size: 16px; } .seat-delta { font-size: 10.5px; font-weight: 900; } .delta-pos { color: #00E676; } .delta-neg { color: #FF3D00; } .delta-neu { color: #9E9E9E; } .custom-bar-bg { flex-grow: 1; background-color: " + t_bar_bg + "; height: 42px; overflow: hidden; display: flex; border: 2px solid " + c_text + "; box-shadow: 3px 3px 0px #eb252d; } .custom-bar-fill { height: 100%; display: flex; align-items: center; padding-left: 8px; color: #ffffff !important; font-weight: 700; font-size: 14px; white-space: nowrap; border-right: 2px solid " + c_text + "; } .vote-delta { font-size: 11px; margin-left: 6px; font-weight: 400; opacity: 0.9; }</style><div style='max-width: 100%; margin: 10px 0 10px 0;'>"]
        
        for _, row in national_summary_df.iterrows():
            if row['Normalize Oy (%)'] <= 0.0:
                continue
            
            s_delta_html = f"<span class='seat-delta delta-pos'>▲ {int(row['Vekil Değişimi'])}</span>" if row['Vekil Değişimi'] > 0 else (f"<span class='seat-delta delta-neg'>▼ {abs(int(row['Vekil Değişimi']))}</span>" if row['Vekil Değişimi'] < 0 else "<span class='seat-delta delta-neu'>-</span>")
            v_delta_str = f"(+{row['Oy Değişimi']:.1f})" if row['Oy Değişimi'] > 0 else (f"({row['Oy Değişimi']:.1f})" if row['Oy Değişimi'] < 0 else "")
            html_blocks.append(f"<div class='custom-row'><div class='custom-party'>{row['Parti']}</div><div class='custom-seat'><span class='seat-num'>{int(row['Vekil'])}</span>{s_delta_html}</div><div class='custom-bar-bg'><div class='custom-bar-fill' style='width: {(row['Normalize Oy (%)'] / max_vote_pct) * 100}%; background-color: {party_colors.get(row['Parti'], '#888888')}; min-width: 90px;'>%{row['Normalize Oy (%)']:.1f} <span class='vote-delta'>{v_delta_str}</span></div></div></div>")
        
        st.markdown("".join(html_blocks) + "</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("<h3 style='text-align: center; margin-top: 0;'>MECLİS GRAFİĞİ</h3>", unsafe_allow_html=True)
        toplam_vekil = int(national_summary_df['Vekil'].sum())
        sirali_partiler = [p for p in ['TIP', 'DEM', 'CHP', 'YENI', 'IYI', 'SAADET', 'ZAFER', 'A', 'AKP', 'MHP', 'BBP', 'YRP'] if p in national_summary_df['Parti'].values] + [p for p in national_summary_df['Parti'].values if p not in ['TIP', 'DEM', 'CHP', 'YENI', 'IYI', 'SAADET', 'ZAFER', 'A', 'AKP', 'MHP', 'BBP', 'YRP']]
        assigned_parties = [p for p in sirali_partiler for _ in range(int(national_summary_df[national_summary_df['Parti'] == p]['Vekil'].values[0]))]

        if toplam_vekil > 0:
            radii = list(range(125, 245, 10)) 
            sum_radii = sum(radii)
            seats_per_row = [round(toplam_vekil * (r / sum_radii)) for r in radii]
            if sum(seats_per_row) != toplam_vekil: seats_per_row[-1] += (toplam_vekil - sum(seats_per_row))
            
            points = sorted([{'x': r * math.cos(math.pi - (math.pi * j) / max(1, (s - 1))), 'y': r * math.sin(math.pi - (math.pi * j) / max(1, (s - 1))), 'angle': math.pi - (math.pi * j) / max(1, (s - 1)), 'r': r} for r, s in zip(radii, seats_per_row) if s > 0 for j in range(s)], key=lambda p: (p['angle'], -p['r']), reverse=True)

            ui_svg = f'<svg viewBox="0 -5 500 270" width="100%" height="100%" xmlns="http://www.w3.org/2000/svg">'
            
            for i, party in enumerate(assigned_parties):
                if i < len(points):
                    cx = 250 + points[i]['x']
                    cy = 250 - points[i]['y']
                    color = party_colors.get(party, "#888888")
                    ui_svg += f'<circle cx="{cx}" cy="{cy}" r="4.3" fill="{color}" />'
            
            ui_svg += f'<text x="250" y="5" text-anchor="middle" font-size="12" font-weight="bold" fill="{c_text}">Çoğunluk</text>'
            ui_svg += f'<line x1="250" y1="12" x2="250" y2="130" stroke="{c_text}" stroke-width="2" stroke-dasharray="4,4"/>'
            
            ui_svg += f'<text x="250" y="240" text-anchor="middle" font-size="46" font-weight="900" fill="{c_text}">{toplam_vekil}</text>'
            ui_svg += '</svg>'
            
            st.markdown(f"<div style='text-align:center; padding: 20px 0;'>{ui_svg}</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("🗺️ Bölgesel Seçim Analizi ve Haritalar")

    col_m_scope, col_m_filter = st.columns([1, 1])
    with col_m_scope:
        master_region = st.selectbox("İncelenecek Bölge / İl Seçin:", options=["Türkiye Geneli"] + [get_display_name(p) for p in all_provinces_norm], key="master_region_select")
    with col_m_filter:
        map_mode = st.selectbox("Harita Görünüm Modu:", options=["1. Partiler (Varsayılan)"] + PARTIES, key="map_display_mode")

    prov_winners_dict, dist_winners_dict, custom_heatmap_colors = {}, {}, {}
    selected_norm = normalize_id(master_region) if master_region != "Türkiye Geneli" else "turkiye"

    if master_region == "Türkiye Geneli":
        target_svg = "turkiye.svg"
        df_map_data = df_results.copy()
        show_badges_flag = True if map_mode == "1. Partiler (Varsayılan)" else False
    else:
        if selected_norm in available_cities:
            target_svg = f"{selected_norm}.svg"
            raw_city_df = load_city_data(selected_norm, w23_val, w24_val)
            if not raw_city_df.empty:
                city_df_base, _ = apply_custom_parties(raw_city_df, st.session_state.custom_parties_def)
                df_map_data = run_simulation(city_df_base, base_national_dict, user_inputs_norm, alliances, joint_lists, params["threshold_input"])
            else:
                st.error(f"🚨 {master_region} veri dosyaları bulunamadı! (ilce/veri/{selected_norm}2023.csv ve 2024.csv)")
                df_map_data = pd.DataFrame()
            show_badges_flag = False
        else:
            target_svg = "turkiye.svg"
            df_map_data = df_results.copy()
            show_badges_flag = True if map_mode == "1. Partiler (Varsayılan)" else False
            st.info(f"ℹ️ **{master_region}** için ilçe haritası (.svg) henüz yüklenmediğinden Türkiye geneli haritası üzerinden gösteriliyor.")

    #  RENK VE TOOLTIP HESAPLAMALARI
    if not df_map_data.empty:
        if map_mode == "1. Partiler (Varsayılan)":
            if target_svg == "turkiye.svg":
                prov_max_df = df_map_data.groupby(['province', 'party'])['new_vote_pct'].mean().reset_index()
                prov_max_df = prov_max_df.loc[prov_max_df.groupby('province')['new_vote_pct'].idxmax()]
                
                for _, r in prov_max_df.iterrows():
                    norm_prov = normalize_id(r['province'])
                    winner = r['party']
                    vote = r['new_vote_pct']
                    prov_winners_dict[norm_prov] = winner
                    
                    base_hex = party_colors.get(winner, "#888888")
                    ratio = max(0.3, min(1.0, vote / 65.0)) 
                    custom_heatmap_colors[norm_prov] = get_heatmap_color(base_hex, ratio)
                    
                    if norm_prov in ['istanbul', 'ankara', 'izmir', 'bursa']:
                        for sub_id in [f"{norm_prov}1", f"{norm_prov}2", f"{norm_prov}3"]: 
                            custom_heatmap_colors[sub_id] = custom_heatmap_colors[norm_prov]

            dist_max_df = df_map_data.loc[df_map_data.groupby('district')['new_vote_pct'].idxmax()]
            for _, r in dist_max_df.iterrows():
                norm_dist = normalize_id(r['district'])
                winner = r['party']
                vote = r['new_vote_pct']
                dist_winners_dict[norm_dist] = winner
                
                base_hex = party_colors.get(winner, "#888888")
                ratio = max(0.3, min(1.0, vote / 65.0))
                custom_heatmap_colors[norm_dist] = get_heatmap_color(base_hex, ratio)
        else:
            selected_party = map_mode.split(" ")[0]
            base_hex = party_colors.get(selected_party, "#3485fd")
            prov_votes_map = df_map_data[df_map_data['party'] == selected_party].groupby('province')['new_vote_pct'].mean().to_dict()
            dist_votes_map = df_map_data[df_map_data['party'] == selected_party].set_index('district')['new_vote_pct'].to_dict()
            
            all_vals = list(prov_votes_map.values()) + list(dist_votes_map.values())
            min_v, v_range = (min(all_vals) if all_vals else 0.0), ((max(all_vals) if all_vals else 100.0) - (min(all_vals) if all_vals else 0.0)) or 1.0

            if target_svg == "turkiye.svg":
                for prov in df_map_data['province'].unique():
                    norm_id = normalize_id(prov)
                    prov_winners_dict[norm_id] = selected_party
                    custom_heatmap_colors[norm_id] = get_heatmap_color(base_hex, (prov_votes_map.get(prov, 0.0) - min_v) / v_range)
                    if norm_id in ['istanbul', 'ankara', 'izmir', 'bursa']:
                        for sub_id in [f"{norm_id}1", f"{norm_id}2", f"{norm_id}3"]: custom_heatmap_colors[sub_id] = custom_heatmap_colors[norm_id]
            for dist in df_map_data['district'].unique():
                norm_dist = normalize_id(dist)
                dist_winners_dict[norm_dist] = selected_party
                custom_heatmap_colors[norm_dist] = get_heatmap_color(base_hex, (dist_votes_map.get(dist, 0.0) - min_v) / v_range)

        tooltip_dict = {}
        for dist, group in df_map_data.groupby('district'):
            html = f'<div class="tip-header">📌 {dist}</div>'
            for _, r in (group.sort_values(by='new_vote_pct', ascending=False).head(5) if map_mode == "1. Partiler (Varsayılan)" else group[group['party'] == selected_party]).iterrows():
                if r['new_vote_pct'] > 0.0: html += f'<div class="tip-row"><div class="tip-party">{r["party"]}</div><div class="tip-bar-bg"><div class="tip-bar-fill" style="width: {r["new_vote_pct"]}%; background-color: {party_colors.get(r["party"], "#888888")};"></div></div><div class="tip-pct">%{r["new_vote_pct"]:.1f}</div></div>'
            tooltip_dict[normalize_id(dist)] = html

        if target_svg == "turkiye.svg":
            for prov, group in df_map_data.groupby('province'):
                norm_prov = normalize_id(prov)
                html = f'<div class="tip-header">📌 {prov}</div>'
                for _, r in (group.groupby('party').agg({'new_vote_pct': 'mean', 'seats_won': 'sum'}).reset_index().sort_values(by='new_vote_pct', ascending=False).head(5) if map_mode == "1. Partiler (Varsayılan)" else group.groupby('party').agg({'new_vote_pct': 'mean', 'seats_won': 'sum'}).reset_index()[group.groupby('party').agg({'new_vote_pct': 'mean', 'seats_won': 'sum'}).reset_index()['party'] == selected_party]).iterrows():
                    if r['new_vote_pct'] > 0.0: html += f'<div class="tip-row"><div class="tip-party">{r["party"]}</div><div class="tip-seat">{int(r["seats_won"])}</div><div class="tip-bar-bg"><div class="tip-bar-fill" style="width: {r["new_vote_pct"]}%; background-color: {party_colors.get(r["party"], "#888888")};"></div></div><div class="tip-pct">%{r["new_vote_pct"]:.1f}</div></div>'
                tooltip_dict[norm_prov] = html

        if master_region == "Türkiye Geneli":
            components.html(render_colored_svg(prov_winners_dict, dist_winners_dict, party_colors, tooltip_dict, df_results.groupby(['district', 'party'])['seats_won'].sum().to_dict(), svg_file_name=target_svg, show_badges=show_badges_flag, custom_colors=custom_heatmap_colors), height=550, scrolling=False)
        else:
            col_map_view, col_bar_view = st.columns([1.3, 1])
            
            with col_map_view:
                components.html(render_colored_svg(prov_winners_dict, dist_winners_dict, party_colors, tooltip_dict, df_results.groupby(['district', 'party'])['seats_won'].sum().to_dict(), svg_file_name=target_svg, show_badges=show_badges_flag, custom_colors=custom_heatmap_colors), height=550, scrolling=False)
            
            with col_bar_view:
                with st.container(border=True):
                    prov_23_subset = pd.read_csv(os.path.join(current_dir, "ysk_2023_secim_verisi.csv"))
                    prov_23_subset = prov_23_subset[prov_23_subset['district'].apply(lambda x: normalize_id(str(x).split('-')[0])) == selected_norm]
                    base_23_seats_dict = prov_23_subset.groupby('party')['seats_won_2023'].sum().to_dict()
                    prov_23_subset['vote_23_pct'] = prov_23_subset.groupby('district')['base_vote_pct'].transform(lambda x: (x / x.sum()) * 100)
                    base_23_prov_dict = prov_23_subset.groupby('party')['vote_23_pct'].mean().to_dict()
                    
                    prov_summary_bar = df_results[df_results['province'].apply(normalize_id) == selected_norm].groupby('party').agg({'new_vote_pct': 'mean','seats_won': 'sum'}).reset_index().sort_values(by=['new_vote_pct', 'seats_won'], ascending=[False, False])
                    
                    display_header = master_region.replace('i', 'İ').upper()
                    st.markdown(f"<h3 style='text-align: center; margin-bottom: 20px;'>{display_header} SONUÇLARI</h3>", unsafe_allow_html=True)
                    max_prov_vote = prov_summary_bar['new_vote_pct'].max() or 1.0
                    
                    prov_html_blocks = ["<style>.prov-vote-delta { font-size: 11px; margin-left: 6px; font-weight: 400; opacity: 0.9; } .prov-seat-delta { font-size: 10px; font-weight: 900; display: block; line-height: 1; } .delta-pos { color: #00E676; } .delta-neg { color: #FF3D00; } .delta-neu { color: #9E9E9E; }</style><div style='max-width: 100%; margin: 10px 0 10px 0;'>"]
                    for _, row in prov_summary_bar.iterrows():
                        if row['new_vote_pct'] <= 0.0 and row['seats_won'] <= 0: continue
                        vote_delta = row['new_vote_pct'] - base_23_prov_dict.get(row['party'], 0.0)
                        seat_delta = int(row['seats_won']) - base_23_seats_dict.get(row['party'], 0)
                        v_delta_str = f"(+{vote_delta:.1f})" if vote_delta > 0 else (f"({vote_delta:.1f})" if vote_delta < 0 else "")
                        s_delta_html = f"<span class='prov-seat-delta delta-pos'>▲ {seat_delta}</span>" if seat_delta > 0 else (f"<span class='prov-seat-delta delta-neg'>▼ {abs(seat_delta)}</span>" if seat_delta < 0 else "<span class='prov-seat-delta delta-neu'>-</span>")
                        prov_html_blocks.append(f"<div class='custom-row'><div class='custom-party'>{row['party']}</div><div class='custom-seat'><span class='seat-num'>{int(row['seats_won'])}</span>{s_delta_html}</div><div class='custom-bar-bg'><div class='custom-bar-fill' style='width: {(row['new_vote_pct'] / max_prov_vote) * 100}%; background-color: {party_colors.get(row['party'], '#888888')}; min-width: 90px;'>%{row['new_vote_pct']:.1f} <span class='prov-vote-delta'>{v_delta_str}</span></div></div></div>")
                    st.markdown("".join(prov_html_blocks) + "</div>", unsafe_allow_html=True)

    if master_region == "Türkiye Geneli":
        info_prov_winners_dict = {}
        info_dist_winners_dict = {}
        
        infographic_heatmap_colors = {}
        for prov, group in df_results.groupby('province'):
            norm_prov = normalize_id(prov)
            top_row = group.groupby('party')['new_vote_pct'].mean().reset_index().sort_values(by='new_vote_pct', ascending=False).iloc[0]
            winner = top_row['party']
            vote = top_row['new_vote_pct']
            info_prov_winners_dict[norm_prov] = winner
            
            base_hex = party_colors.get(winner, "#888888")
            ratio = max(0.3, min(1.0, vote / 65.0))
            infographic_heatmap_colors[norm_prov] = get_heatmap_color(base_hex, ratio)
            
            if norm_prov in ['istanbul', 'ankara', 'izmir', 'bursa']:
                for sub_id in [f"{norm_prov}1", f"{norm_prov}2", f"{norm_prov}3"]: 
                    infographic_heatmap_colors[sub_id] = infographic_heatmap_colors[norm_prov]

        dist_max_df = df_results.loc[df_results.groupby('district')['new_vote_pct'].idxmax()]
        for _, r in dist_max_df.iterrows():
            norm_dist = normalize_id(r['district'])
            winner = r['party']
            vote = r['new_vote_pct']
            info_dist_winners_dict[norm_dist] = winner
            
            base_hex = party_colors.get(winner, "#888888")
            ratio = max(0.3, min(1.0, vote / 65.0))
            infographic_heatmap_colors[norm_dist] = get_heatmap_color(base_hex, ratio)

        rendered_map = render_colored_svg(
            info_prov_winners_dict, 
            info_dist_winners_dict, 
            party_colors, 
            dict(), 
            df_results.groupby(['district', 'party'])['seats_won'].sum().to_dict(), 
            svg_file_name="turkiye.svg",
            show_badges=False,
            custom_colors=infographic_heatmap_colors
        )
        final_svg = generate_infographic_svg(national_summary_df, rendered_map, toplam_vekil, assigned_parties, party_colors, alliances)
        
        btn_text = "📸 İnfografiği PNG Olarak İndir (Türkiye Geneli)"
        dl_name = "turkiye_secim_infografik.png"
    else:
        display_header = master_region.replace('i', 'İ').upper()
        
        top_5 = prov_summary_bar.head(5) 
        winners = prov_summary_bar[prov_summary_bar['seats_won'] > 0]
        top_parties_df = pd.concat([top_5, winners]).drop_duplicates(subset=['party']).sort_values(by=['new_vote_pct', 'seats_won'], ascending=[False, False])
        
        regional_map_svg = render_colored_svg(
            prov_winners_dict, 
            dist_winners_dict, 
            party_colors, 
            dict(), 
            df_results.groupby(['district', 'party'])['seats_won'].sum().to_dict(), 
            svg_file_name=target_svg, 
            show_badges=show_badges_flag, 
            custom_colors=custom_heatmap_colors
        )
        
        final_svg = generate_regional_infographic_svg(display_header, top_parties_df, regional_map_svg, party_colors)
        
        btn_text = f"📸 {display_header} İnfografiğini PNG Olarak İndir"
        dl_name = f"{selected_norm}_secim_infografik.png"
        
    components.html(f"""
    <div id="infographic-container" style="display:none;">
        {final_svg}
    </div>
    <button id="download-btn" style="background-color: #eb252d; color: white; border: 3px solid #ffffff; box-shadow: 4px 4px 0px #ffffff; font-weight: 900; padding: 14px 20px; font-family: 'Space Grotesk', sans-serif; text-transform: uppercase; cursor: pointer; width: 100%; margin-top: 15px; margin-bottom: 25px;">{btn_text}</button>
    <script>
    document.getElementById('download-btn').addEventListener('click', function() {{
        var btn = this; 
        var originalText = btn.innerText;
        btn.innerText = "Görsel Hazırlanıyor...";
        
        var canvas = document.createElement("canvas");
        var scale = 2; // Yüksek çözünürlük için
        canvas.width = 1200 * scale; 
        canvas.height = 980 * scale;
        var ctx = canvas.getContext("2d"); 
        ctx.scale(scale, scale);
        
        var img = new Image();
        img.onload = function() {{
            ctx.fillStyle = "#ffffff"; 
            ctx.fillRect(0, 0, canvas.width, canvas.height); 
            ctx.drawImage(img, 0, 0);
            
            var a = document.createElement("a"); 
            a.download = "{dl_name}"; 
            a.href = canvas.toDataURL("image/png"); 
            a.click();
            
            btn.innerText = originalText;
        }};
        img.src = URL.createObjectURL(new Blob([new XMLSerializer().serializeToString(document.querySelector("#infographic-container svg"))], {{type: "image/svg+xml;charset=utf-8"}}));
    }});
    </script>
    """, height=90)

    #İl İl Dağılım Tablosu
    with st.expander("📊 İl İl Dağılım Tablosu", expanded=False):
        pivot_df = df_results.pivot(index='district', columns='party', values=['new_vote_pct', 'seats_won'])
        display_df = pd.DataFrame({f"{p} (%)": pivot_df['new_vote_pct'][p].round(1) if p in pivot_df['new_vote_pct'] else 0.0 for p in national_summary_df['Parti']})
        for p in national_summary_df['Parti']:
            if p in pivot_df['seats_won']: display_df[f"{p} (Vekil)"] = pivot_df['seats_won'][p].astype(int)

        def highlight_first_party(row):
            styles, vote_cols = [''] * len(row), [col for col in row.index if '(%)' in col]
            if not vote_cols: return styles
            best_col = max(vote_cols, key=lambda col: row[col])
            if row[best_col] > 0:
                color = party_colors.get(best_col.split(' ')[0], '#CCCCCC')
                styles = [f'background-color: {color}; color: white; font-weight: bold;' if col.startswith(best_col.split(' ')[0]) else '' for col in row.index]
            return styles
        st.dataframe(display_df.style.apply(highlight_first_party, axis=1).format(lambda x: f"%{x:.1f}" if isinstance(x, float) else x), use_container_width=True)

    #Fırsat ve Risk Analizi
    with st.expander("🎯 Fırsat ve Risk Analizi", expanded=False):
        st.info("Bu modül, en az oy farkıyla kazanılan veya el değiştirmeye en yakın vekillikleri gösterir. Stratejik odaklanma için kritik bölgelerdir.")
        target_party_swing = st.selectbox("Hangi parti için fırsat / risk analizi yapılsın?", options=[p for p in national_summary_df['Parti'].tolist() if national_summary_df[national_summary_df['Parti'] == p]['Vekil'].values[0] > 0 or display_user_nat.get(p, 0) > 1.0], index=0)

        qualified_parties_sw = [p for aly, vote in {aly: sum([display_user_nat.get(pt, 0) for pt in pts]) for aly, pts in alliances.items()}.items() if vote >= p_threshold for p in alliances[aly]]
        multipliers = {p: (user_inputs_norm.get(p, 0) / base_national_dict[p]) if base_national_dict.get(p, 0) > 0 else 0 for p in PARTIES}
        swing_data = []

        for district, group in df_base.groupby('district'):
            seat_count = group['seat_count'].iloc[0]

        for district, group in df_base.groupby('district'):
            seat_count = group['seat_count'].iloc[0]
            norm_votes_sw = {row['party']: (row['base_vote_pct'] * multipliers.get(row['party'], 1.0)) for _, row in group.iterrows()}
            total_proj_sw = sum(norm_votes_sw.values())
            norm_votes_sw = {p: (v / total_proj_sw) * 100 for p, v in norm_votes_sw.items()} if total_proj_sw > 0 else {p: 0 for p in norm_votes_sw}
            
            for umbrella, joiners in joint_lists.items():
                if umbrella in norm_votes_sw:
                    for jp in joiners:
                        if jp in norm_votes_sw: norm_votes_sw[umbrella], norm_votes_sw[jp] = norm_votes_sw[umbrella] + norm_votes_sw[jp], 0.0
                            
            eligible_votes_sw = {p: norm_votes_sw[p] for p in qualified_parties_sw if p in norm_votes_sw and norm_votes_sw[p] > 0}
            if not eligible_votes_sw: continue
                
            quotients = sorted([{'party': p, 'quotient': v / i, 'seat_idx': i} for p, v in eligible_votes_sw.items() for i in range(1, int(seat_count) + 2)], key=lambda x: x['quotient'], reverse=True)
            if len(quotients) >= int(seat_count) + 1:
                last_winning, first_losing = quotients[int(seat_count) - 1], quotients[int(seat_count)]
                if last_winning['party'] == target_party_swing: swing_data.append({'İlçe': district, 'Durum': 'Riskli (Kıl Payı Kazandı)', 'Rakip': first_losing['party'], 'Fark Skoru': last_winning['quotient'] - first_losing['quotient'], 'Açıklama': f"Son vekil {last_winning['quotient'] - first_losing['quotient']:.2f} puan farkla {first_losing['party']}'den kurtarıldı."})
                elif first_losing['party'] == target_party_swing: swing_data.append({'İlçe': district, 'Durum': 'Fırsat (Kıl Payı Kaçırdı)', 'Rakip': last_winning['party'], 'Fark Skoru': last_winning['quotient'] - first_losing['quotient'], 'Açıklama': f"Son vekil {last_winning['quotient'] - first_losing['quotient']:.2f} puan farkla {last_winning['party']}'ye kaybedildi."})

        if swing_data:
            swing_df = pd.DataFrame(swing_data)
            col_s1, col_s2 = st.columns(2)
            with col_s1:
                st.markdown("### 🔴 Kılpayı Kaybedilenler")
                for _, row in swing_df[swing_df['Durum'].str.contains('Fırsat')].sort_values(by='Fark Skoru').head(10).iterrows(): st.info(f"**{row['İlçe']}** ⚔️ Rakip: {row['Rakip']}  \n*{row['Açıklama']}*")
            with col_s2:
                st.markdown("### 🟢 Ucundan Alınanlar")
                for _, row in swing_df[swing_df['Durum'].str.contains('Riskli')].sort_values(by='Fark Skoru').head(10).iterrows(): st.warning(f"**{row['İlçe']}** ⚔️ Rakip: {row['Rakip']}  \n*{row['Açıklama']}*")

with tab_cb:
    # Cumhurbaşkanlığı Simülasyonu
    st.header("🗳️ CUMHURBAŞKANLIĞI SEÇİMİ PROJEKSİYONU")
    cb_parties = [p for p in PARTIES if display_user_nat.get(p, 0) > 0.0]

    if 'next_c1_id' not in st.session_state:
        st.session_state.next_c1_id = 100

    if 'cb_cands_1' not in st.session_state:
        st.session_state.cb_cands_1 = [
            {"id": "c1_1", "name": "Erdoğan", "votes": {p: {"AKP": 90, "IYI": 5, "DEM": 10, "MHP": 90, "YRP": 20, "A": 20, "BBP": 90, "SAADET": 20}.get(p, 0) for p in cb_parties}},
            {"id": "c1_2", "name": "İmamoğlu", "votes": {p: {"IYI": 30, "DEM": 40, "TIP": 90, "ZAFER": 20, "YENI": 100, "SAADET": 10}.get(p, 0) for p in cb_parties}},
            {"id": "c1_3", "name": "Bakırhan", "votes": {p: {"DEM": 50, "TIP": 10}.get(p, 0) for p in cb_parties}},
            {"id": "c1_4", "name": "Ağıralioğlu", "votes": {p: {"AKP": 5, "IYI": 10, "MHP": 10, "A": 80, "BBP": 10}.get(p, 0) for p in cb_parties}},
            {"id": "c1_5", "name": "Erbakan", "votes": {p: {"AKP": 5, "YRP": 80, "SAADET": 80}.get(p, 0) for p in cb_parties}},
            {"id": "c1_6", "name": "Dervişoğlu", "votes": {p: {"IYI": 85}.get(p, 0) for p in cb_parties}},
            {"id": "c1_7", "name": "Özdağ", "votes": {p: {"ZAFER": 80}.get(p, 0) for p in cb_parties}},
            {"id": "c1_8", "name": "Kılıçdaroğlu", "votes": {p: {"CHP": 100}.get(p, 0) for p in cb_parties}}
        ]

    st.subheader("1. Tur Senaryosu")

    with st.container():
        top_col1, top_col2 = st.columns([4, 1])
        with top_col1: st.markdown("<p style='font-size:12px; color:#888; margin-bottom:10px;'>Adayların partilerden alacağı oy oranlarını (%) aşağıdaki kartlardan düzenleyin:</p>", unsafe_allow_html=True)
        with top_col2:
            if st.button("🔄 Sıfırla", key="reset_cands_1", help="Adayların isimlerini ve oylarını varsayılan duruma getir"):
                st.session_state.cb_cands_1 = [
                    {"id": f"c1_{st.session_state.next_c1_id}", "name": "Erdoğan", "votes": {p: 0 for p in cb_parties}}, 
                    {"id": f"c1_{st.session_state.next_c1_id+1}", "name": "Diğer Aday", "votes": {p: 0 for p in cb_parties}}
                ]
                st.session_state.next_c1_id += 2
                st.rerun()

        cand_to_delete = None

        for idx, cand in enumerate(st.session_state.cb_cands_1):
            c_id = cand.get("id", f"old_{idx}") 
            
            with st.container(border=True):
                col_name, col_del = st.columns([5, 1])
                cand["name"] = col_name.text_input("Aday Adı", value=cand["name"], key=f"c1_n_{c_id}", label_visibility="collapsed")
                st.markdown("<div style='font-size: 11px; font-weight: bold; margin: 10px 0 5px 0;'>Parti Oy Oranları (%)</div>", unsafe_allow_html=True)
                
                cols = st.columns(4)
                for i, p in enumerate(cb_parties):
                    cols[i % 4].markdown(f"<div style='font-size:10px; font-weight:900; color:{party_colors.get(p, '#888')}; margin-bottom:-5px;'>{p}</div>", unsafe_allow_html=True)
                    cand["votes"][p] = cols[i % 4].number_input(f"v_{c_id}_{p}", value=float(cand["votes"].get(p, 0.0)), min_value=0.0, max_value=100.0, label_visibility="collapsed", key=f"c1_v_{c_id}_{p}")

                col_del.markdown("<br>", unsafe_allow_html=True)
                if len(st.session_state.cb_cands_1) > 1 and col_del.button("🗑️", key=f"del_{c_id}", help="Bu adayı sil"):
                    cand_to_delete = cand

        if cand_to_delete:
            st.session_state.cb_cands_1.remove(cand_to_delete)
            st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("➕ Yeni Aday Ekle", key="add_candidate_btn_1"):
            st.session_state.cb_cands_1.append({"id": f"c1_{st.session_state.next_c1_id}", "name": f"Aday {len(st.session_state.cb_cands_1)+1}", "votes": {p: 0 for p in cb_parties}})
            st.session_state.next_c1_id += 1
            st.rerun()

    @st.cache_data(show_spinner=False)
    def calculate_cb_votes_and_colors(cands_state_list, cb_parties_list, display_user_nat_dict, party_colors_dict):
        cand_data = []
        for cand in cands_state_list:
            aday = str(cand["name"]).strip()
            if not aday: continue
            
            contributions = []
            votes = 0.0
            for p in cb_parties_list:
                contrib = display_user_nat_dict.get(p, 0) * (cand["votes"].get(p, 0) / 100.0)
                votes += contrib
                if contrib > 0: contributions.append((p, contrib))
                    
            contributions.sort(key=lambda x: x[1], reverse=True)
            cand_data.append({"name": aday, "votes": votes, "contribs": contributions})
            
        cand_data.sort(key=lambda x: x["votes"], reverse=True)
        cb_res, cand_color_map, used_colors = {}, {}, set()
        
        for cd in cand_data:
            aday = cd["name"]
            cb_res[aday] = cd["votes"]
            assigned_color = "#888888"
            for p, contrib in cd["contribs"]:
                color = party_colors_dict.get(p, "#888888")
                if color not in used_colors:
                    assigned_color = color
                    used_colors.add(color)
                    break
            else:
                if cd["contribs"]: assigned_color = party_colors_dict.get(cd["contribs"][0][0], "#888888")
            cand_color_map[aday] = assigned_color
            
        return cb_res, cand_color_map

    @st.cache_data(show_spinner=False)
    def calculate_cb_district_results(cands_list, df_results_data, colors_override, cb_parties_list):
        pivot_dist_votes = df_results_data.pivot(index='district', columns='party', values='new_vote_pct').fillna(0)
        weight_df = pd.DataFrame({cand["name"]: {p: float(cand["votes"].get(p, 0)) / 100.0 for p in cb_parties_list} for cand in cands_list if str(cand["name"]).strip()}).fillna(0)
        
        common_parties = [p for p in cb_parties_list if p in pivot_dist_votes.columns]
        cand_votes_dist_norm = pivot_dist_votes[common_parties].dot(weight_df.loc[common_parties])
        
        row_sums = cand_votes_dist_norm.sum(axis=1)
        row_sums[row_sums == 0] = 1
        cand_votes_dist_norm = cand_votes_dist_norm.div(row_sums, axis=0).fillna(0) * 100
        
        df_cb_dist = cand_votes_dist_norm.reset_index().melt(id_vars='district', var_name='candidate', value_name='pct')
        df_cb_dist['province'] = df_cb_dist['district'].apply(lambda x: x.split('-')[0])
        
        cb_prov_winners, cb_dist_winners, cb_heatmap_colors = {}, {}, {}
        
        dist_max_df = df_cb_dist.loc[df_cb_dist.groupby('district')['pct'].idxmax()]
        for _, r in dist_max_df.iterrows():
            n_dist = normalize_id(r['district'])
            cand, vote = r['candidate'], r['pct']
            cb_dist_winners[n_dist] = cand
            cb_heatmap_colors[n_dist] = get_heatmap_color(colors_override.get(cand, "#888888"), max(0.3, min(1.0, vote / 65.0)))
            
        prov_max_df = df_cb_dist.groupby(['province', 'candidate'])['pct'].mean().reset_index()
        prov_max_df = prov_max_df.loc[prov_max_df.groupby('province')['pct'].idxmax()]
        for _, r in prov_max_df.iterrows():
            n_prov = normalize_id(r['province'])
            cand, vote = r['candidate'], r['pct']
            cb_prov_winners[n_prov] = cand
            cb_heatmap_colors[n_prov] = get_heatmap_color(colors_override.get(cand, "#888888"), max(0.3, min(1.0, vote / 65.0)))
            if n_prov in ['istanbul', 'ankara', 'izmir', 'bursa']:
                for sub_id in [f"{n_prov}1", f"{n_prov}2", f"{n_prov}3"]: cb_heatmap_colors[sub_id] = cb_heatmap_colors[n_prov]
        
        cb_tooltips = {}
        for d_name, grp in df_cb_dist.groupby('district'):
            cb_tooltips[normalize_id(d_name)] = f'<div class="tip-header">📌 {d_name} (CB Seçimi)</div>' + "".join([f'<div class="tip-row"><div class="tip-party" style="width:100px;">{r["candidate"]}</div><div class="tip-bar-bg"><div class="tip-bar-fill" style="width: {r["pct"]}%; background-color: {colors_override.get(r["candidate"], "#888888")};"></div></div><div class="tip-pct">%{r["pct"]:.1f}</div></div>' for _, r in grp.sort_values(by='pct', ascending=False).iterrows()])
        for p_name, grp in df_cb_dist.groupby('province'):
            cb_tooltips[normalize_id(p_name)] = f'<div class="tip-header">📌 {p_name} (CB Seçimi)</div>' + "".join([f'<div class="tip-row"><div class="tip-party" style="width:100px;">{r["candidate"]}</div><div class="tip-bar-bg"><div class="tip-bar-fill" style="width: {r["pct"]}%; background-color: {colors_override.get(r["candidate"], "#888888")};"></div></div><div class="tip-pct">%{r["pct"]:.1f}</div></div>' for _, r in grp.groupby('candidate')['pct'].mean().reset_index().sort_values(by='pct', ascending=False).iterrows()])
            
        return cb_prov_winners, cb_dist_winners, cb_heatmap_colors, cb_tooltips, df_cb_dist

    if st.button("🗳️ 1. Tur Sonuçlarını & Haritasını Hesapla", type="primary", use_container_width=True) or ('cb_res_1_saved' in st.session_state):
        st.session_state.cb_res_1_saved = True
        
        cb_res_1, cand_color_map_1 = calculate_cb_votes_and_colors(st.session_state.cb_cands_1, cb_parties, display_user_nat, party_colors)
        total_cb_1 = sum(cb_res_1.values())

        if total_cb_1 > 0:
            st.markdown("### 📊 1. Tur Sonuçları")
            with st.container(border=True):
                col_cb_bars, col_cb_map = st.columns([1.1, 1.3])
                
                with col_cb_map:
                    cb_master_region_1 = st.selectbox("Harita Bölgesi (1. Tur):", options=["Türkiye Geneli"] + [get_display_name(p) for p in all_provinces_norm], key="cb_map_region_1")
                    
                    if cb_master_region_1 == "Türkiye Geneli":
                        current_df_results_1 = df_results
                        cb_target_svg_1 = "turkiye.svg"
                    else:
                        selected_norm_1 = normalize_id(cb_master_region_1)
                        if selected_norm_1 in available_cities:
                            raw_city_df_1 = load_city_data(selected_norm_1, w23_val, w24_val)
                            city_df_base_1, _ = apply_custom_parties(raw_city_df_1, st.session_state.custom_parties_def)
                            current_df_results_1 = run_simulation(city_df_base_1, base_national_dict, user_inputs_norm, alliances, joint_lists, params["threshold_input"])
                            cb_target_svg_1 = f"{selected_norm_1}.svg"
                        else:
                            current_df_results_1 = df_results
                            cb_target_svg_1 = "turkiye.svg"
                    
                    p_win1, d_win1, c_heatmap_cols1, t_tips1, df_cb_dist_1 = calculate_cb_district_results(st.session_state.cb_cands_1, current_df_results_1, cand_color_map_1, cb_parties)
                    components.html(render_colored_svg(p_win1, d_win1, cand_color_map_1, t_tips1, show_badges=False, custom_colors=c_heatmap_cols1, svg_file_name=cb_target_svg_1), height=450, scrolling=False)

                with col_cb_bars:
                    if cb_master_region_1 == "Türkiye Geneli":
                        sorted_1 = sorted(cb_res_1.items(), key=lambda x: x[1], reverse=True)
                        bar_data_1 = [(aday, (votes / total_cb_1) * 100) for aday, votes in sorted_1]
                    else:
                        prov_res_1 = df_cb_dist_1.groupby('candidate')['pct'].mean().to_dict()
                        sorted_prov_1 = sorted(prov_res_1.items(), key=lambda x: x[1], reverse=True)
                        bar_data_1 = [(aday, pct) for aday, pct in sorted_prov_1]

                    max_cb_pct1 = bar_data_1[0][1] if bar_data_1 else 1.0
                    st.markdown("<div class='cb-card'>" + "".join([f"<div class='cb-row'><div class='cb-name'>{aday}</div><div class='cb-bar-bg'><div class='cb-bar-fill' style='width: {((pct / max_cb_pct1) * 100) if max_cb_pct1 > 0 else 0}%; background-color: {cand_color_map_1.get(aday, '#888888')}; min-width: 60px;'>%{pct:.2f}</div></div></div>" for aday, pct in bar_data_1]) + "</div>", unsafe_allow_html=True)
                    
                    sorted_1_nat = sorted(cb_res_1.items(), key=lambda x: x[1], reverse=True)
                    kazanan_orani_nat = (sorted_1_nat[0][1] / total_cb_1) * 100
                    if kazanan_orani_nat > 50.0: 
                        st.success(f"🎉 Seçim 1. Turda Bitti! **{sorted_1_nat[0][0]}** %{kazanan_orani_nat:.2f} ile Cumhurbaşkanı seçildi.")
                    else: 
                        st.warning(f"⚖️ Hiçbir aday %50+1'e ulaşamadı. **{sorted_1_nat[0][0]}** ve **{sorted_1_nat[1][0]}** 2. tura kaldı.")

            # 2. Tur
            if kazanan_orani_nat <= 50.0 and len(sorted_1_nat) > 1:
                st.divider()
                top1, top2 = sorted_1_nat[0][0], sorted_1_nat[1][0]
                st.subheader(f"2. Tur Senaryosu ({top1} vs {top2})")
                
                if 'cb_cands_2' not in st.session_state or len(st.session_state.cb_cands_2) < 2 or st.session_state.cb_cands_2[0]["name"] != top1 or st.session_state.cb_cands_2[1]["name"] != top2:
                    st.session_state.cb_cands_2 = [
                        {"name": top1, "votes": copy.deepcopy(next((c["votes"] for c in st.session_state.cb_cands_1 if c["name"] == top1), {p: 0 for p in cb_parties}))},
                        {"name": top2, "votes": copy.deepcopy(next((c["votes"] for c in st.session_state.cb_cands_1 if c["name"] == top2), {p: 0 for p in cb_parties}))}
                    ]
                
                with st.container():
                    col_baslik2 = st.columns([2.5] + [1]*len(cb_parties))
                    col_baslik2[0].markdown("<div style='font-weight:900; color:#888; font-size:14px; margin-top:10px;'>ADAY ADI</div>", unsafe_allow_html=True)
                    for i, p in enumerate(cb_parties): col_baslik2[i+1].markdown(f"<div style='text-align:center; font-weight:900; color:{party_colors.get(p, c_text)}; font-size:15px; margin-top:10px;'>{p}</div>", unsafe_allow_html=True)
                    st.markdown("<hr style='margin: 10px 0; border-width: 2px;'>", unsafe_allow_html=True)
                    
                    for idx, cand in enumerate(st.session_state.cb_cands_2):
                        r_cols = st.columns([2.5] + [1]*len(cb_parties))
                        r_cols[0].markdown(f"**{cand['name']}**")
                        for i, p in enumerate(cb_parties): cand["votes"][p] = r_cols[i+1].number_input(f"{p}_{idx}_2", value=float(cand["votes"].get(p, 0.0)), min_value=0.0, max_value=100.0, label_visibility="collapsed", key=f"c2_v_{idx}_{p}")

                if st.button("🏆 2. Tur Sonuçlarını & Haritasını Hesapla", type="primary", use_container_width=True) or ('cb_res_2_saved' in st.session_state):
                    st.session_state.cb_res_2_saved = True
                    
                    cb_res_2, cand_color_map_2 = calculate_cb_votes_and_colors(st.session_state.cb_cands_2, cb_parties, display_user_nat, party_colors)
                    total_cb_2 = sum(cb_res_2.values())
                    
                    if total_cb_2 > 0:
                        st.markdown("### 🏆 2. Tur Kesin Sonuçları")
                        with st.container(border=True):
                            col_cb2_bars, col_cb2_map = st.columns([1.1, 1.3])
                            
                            with col_cb2_map:
                                cb_master_region_2 = st.selectbox("Harita Bölgesi (2. Tur):", options=["Türkiye Geneli"] + [get_display_name(p) for p in all_provinces_norm], key="cb_map_region_2")
                                
                                if cb_master_region_2 == "Türkiye Geneli":
                                    current_df_results_2 = df_results
                                    cb_target_svg_2 = "turkiye.svg"
                                else:
                                    selected_norm_2 = normalize_id(cb_master_region_2)
                                    if selected_norm_2 in available_cities:
                                        raw_city_df_2 = load_city_data(selected_norm_2, w23_val, w24_val)
                                        city_df_base_2, _ = apply_custom_parties(raw_city_df_2, st.session_state.custom_parties_def)
                                        current_df_results_2 = run_simulation(city_df_base_2, base_national_dict, user_inputs_norm, alliances, joint_lists, params["threshold_input"])
                                        cb_target_svg_2 = f"{selected_norm_2}.svg"
                                    else:
                                        current_df_results_2 = df_results
                                        cb_target_svg_2 = "turkiye.svg"
                                
                                p_win2, d_win2, c_heatmap_cols2, t_tips2, df_cb_dist_2 = calculate_cb_district_results(st.session_state.cb_cands_2, current_df_results_2, cand_color_map_2, cb_parties)
                                components.html(render_colored_svg(p_win2, d_win2, cand_color_map_2, t_tips2, show_badges=False, custom_colors=c_heatmap_cols2, svg_file_name=cb_target_svg_2), height=450, scrolling=False)

                            with col_cb2_bars:
                                if cb_master_region_2 == "Türkiye Geneli":
                                    sorted_2 = sorted(cb_res_2.items(), key=lambda x: x[1], reverse=True)
                                    bar_data_2 = [(aday, (votes / total_cb_2) * 100) for aday, votes in sorted_2]
                                else:
                                    prov_res_2 = df_cb_dist_2.groupby('candidate')['pct'].mean().to_dict()
                                    sorted_prov_2 = sorted(prov_res_2.items(), key=lambda x: x[1], reverse=True)
                                    bar_data_2 = [(aday, pct) for aday, pct in sorted_prov_2]

                                max_cb_pct2 = bar_data_2[0][1] if bar_data_2 else 1.0
                                st.markdown("<div class='cb-card'>" + "".join([f"<div class='cb-row'><div class='cb-name'>{aday}</div><div class='cb-bar-bg'><div class='cb-bar-fill' style='width: {((pct / max_cb_pct2) * 100) if max_cb_pct2 > 0 else 0}%; background-color: {cand_color_map_2.get(aday, '#888888')}; min-width: 60px;'>%{pct:.2f}</div></div></div>" for aday, pct in bar_data_2]) + "</div>", unsafe_allow_html=True)
                                
                                sorted_2_nat = sorted(cb_res_2.items(), key=lambda x: x[1], reverse=True)
                                st.success(f"🇹🇷 Türkiye'nin Cumhurbaşkanı: **{sorted_2_nat[0][0]}** (%{ (sorted_2_nat[0][1]/total_cb_2)*100:.2f})")                                
#FOOTER
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #888888; font-size: 13px; font-family: "Space Grotesk", sans-serif; padding: 10px 0;'>
        <strong>AD PROJEKSİYON</strong> © 2026<br>
        Projeksiyon için veri toplamada yardımcı olan @levificmete, @solunoktasi, @eypiuus, @yenipartilinsan ve @sdpgenko19 dostlarıma teşekkür ediyorum. Onlar olmadan olmazdı.<br><br>
        <span style='font-size: 10px; color: #333333;'>Anahtar Kelimeler: Seçim simülasyonu, ilçe bazlı seçim haritası, anket projeksiyonu, D'Hondt hesaplama makinesi, Türkiye siyasi analizi, oy dağılımı grafiği.</span>
    </div>
    """, 
    unsafe_allow_html=True
)