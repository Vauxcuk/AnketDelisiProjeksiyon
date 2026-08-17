import streamlit as st
import pandas as pd
from bs4 import BeautifulSoup
import os
import streamlit.components.v1 as components
import plotly.graph_objects as go

# ==========================================
# SAYFA AYARLARI VE DİNAMİK TEMA MOTORU
# ==========================================
st.set_page_config(page_title="AD Projeksiyon", layout="wide")

current_dir = os.path.dirname(os.path.abspath(__file__))
logo_path = os.path.join(current_dir, "logo.svg")

if os.path.exists(logo_path):
    st.sidebar.image(logo_path, use_container_width=True)
else:
    st.sidebar.markdown("### AD PROJEKSİYON")

st.sidebar.write("")
is_light_mode = st.sidebar.toggle("🌞 Açık Tema (Light Mode)", value=False)

if is_light_mode:
    c_bg = "#f8f9fa"          
    c_text = "#181720"        
    c_border = "#181720"      
    t_seat_bg = "#181720"     
    t_bar_bg = "#e9ecef"      
    sidebar_input_bg = "#ffffff"
    sidebar_input_border = "#cccccc"
else:
    c_bg = "#181720"
    c_text = "#ffffff"
    c_border = "#ffffff"
    t_seat_bg = "#333333"
    t_bar_bg = "#23222d"
    sidebar_input_bg = "#23222d"
    sidebar_input_border = "#444444"

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
        border-right: 1px solid {c_border} !important;
        transition: background-color 0.3s;
    }}
    
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] label {{
        color: {c_text} !important;
    }}
    
    section[data-testid="stSidebar"] h1, 
    section[data-testid="stSidebar"] h2, 
    section[data-testid="stSidebar"] h3 {{
        text-shadow: none !important;
        letter-spacing: normal;
        color: {c_text} !important;
        font-weight: 700 !important;
    }}

    section[data-testid="stSidebar"] .stNumberInput input, 
    section[data-testid="stSidebar"] .stMultiSelect div[data-baseweb="select"], 
    section[data-testid="stSidebar"] .stTextInput input,
    [data-baseweb="popover"] {{
        background-color: {sidebar_input_bg} !important;
        color: {c_text} !important;
        border: 1px solid {sidebar_input_border} !important;
        border-radius: 6px !important;
        box-shadow: none !important;
    }}
    
    section[data-testid="stSidebar"] .stNumberInput input:focus, 
    section[data-testid="stSidebar"] .stMultiSelect div[data-baseweb="select"]:focus-within {{
        border-color: #eb252d !important;
        box-shadow: 0 0 0 1px #eb252d !important;
    }}

    hr {{
        border-color: #eb252d !important;
        border-width: 1px !important;
        border-style: solid !important;
        margin-top: 1.5rem !important;
        margin-bottom: 1.5rem !important;
    }}
    
    [data-testid="stDataFrame"], [data-testid="stDataEditor"] {{
        border: 2px solid {c_border};
        box-shadow: 4px 4px 0px #eb252d;
        background-color: {c_bg};
    }}

    .stButton>button {{
        border: 2px solid {c_border} !important;
        box-shadow: 3px 3px 0px #eb252d !important;
        font-weight: 800 !important;
        border-radius: 4px !important;
        text-transform: uppercase !important;
    }}

    .cb-card {{
        background-color: {c_bg};
        border: 2px solid {c_border};
        box-shadow: 4px 4px 0px #eb252d;
        padding: 16px;
        margin-bottom: 15px;
    }}

    .cb-row {{
        display: flex;
        align-items: center;
        margin-bottom: 10px;
        font-family: 'Space Grotesk', sans-serif;
    }}

    .cb-name {{
        width: 140px;
        font-weight: 800;
        font-size: 15px;
        text-transform: uppercase;
        color: {c_text};
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }}

    .cb-bar-bg {{
        flex-grow: 1;
        background-color: {t_bar_bg};
        height: 34px;
        border: 2px solid {c_border};
        box-shadow: 2px 2px 0px #eb252d;
        display: flex;
        overflow: hidden;
    }}

    .cb-bar-fill {{
        height: 100%;
        display: flex;
        align-items: center;
        padding-left: 8px;
        color: #ffffff !important;
        font-weight: 800;
        font-size: 13px;
        white-space: nowrap;
    }}

    [data-testid="stHeader"] {{
        background-color: transparent !important;
    }}
</style>
"""
st.markdown(custom_theme_css, unsafe_allow_html=True)

# ==========================================
# 1. VERİ OKUMA VE NORMALİZASYON
# ==========================================
def normalize_id(text):
    if not isinstance(text, str): return ""
    replacements = {
        'I': 'i', 'ı': 'i', 'İ': 'i',
        'Ğ': 'g', 'ğ': 'g', 
        'Ü': 'u', 'ü': 'u', 
        'Ş': 's', 'ş': 's', 
        'Ö': 'o', 'ö': 'o', 
        'Ç': 'c', 'ç': 'c'
    }
    for search, replace in replacements.items():
        text = text.replace(search, replace)
    return text.lower().replace('-', '').replace('_', '').replace(' ', '')

@st.cache_data
def load_base_data():
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        file_23 = os.path.join(current_dir, "ysk_2023_secim_verisi.csv")
        file_24 = os.path.join(current_dir, "ysk_2024_secim_verisi.csv")
        
        df_23 = pd.read_csv(file_23)
        df_24 = pd.read_csv(file_24)
        
        if 'DIGER' in df_23['party'].values: df_23 = df_23[df_23['party'] != 'DIGER']
        if 'DIGER' in df_24['party'].values: df_24 = df_24[df_24['party'] != 'DIGER']

        df_23_clean = df_23.groupby(['district', 'party'], as_index=False)['base_vote_pct'].sum()
        df_24_clean = df_24.groupby(['district', 'party'], as_index=False)['base_vote_pct'].sum()

        df_23_clean['vote_23'] = df_23_clean.groupby('district')['base_vote_pct'].transform(lambda x: (x / x.sum()) * 100)
        df_24_clean['vote_24'] = df_24_clean.groupby('district')['base_vote_pct'].transform(lambda x: (x / x.sum()) * 100)

        seats_df = df_23[['district', 'seat_count']].drop_duplicates(subset=['district'])

        df_merged = pd.merge(df_23_clean[['district', 'party', 'vote_23']], 
                             df_24_clean[['district', 'party', 'vote_24']], 
                             on=['district', 'party'], how='outer').fillna(0)

        df_merged['base_vote_pct'] = (df_merged['vote_23'] * 0.85) + (df_merged['vote_24'] * 0.15)
        df = pd.merge(df_merged, seats_df, on='district', how='left')

        pivot_base = df.pivot_table(index='district', columns='party', values='base_vote_pct', aggfunc='sum').fillna(0)
        
        new_rows = []
        for district, row_data in df.groupby('district'):
            seat_count = row_data['seat_count'].iloc[0] if not pd.isna(row_data['seat_count'].iloc[0]) else 0
            
            if 'CHP' in pivot_base.columns and 'IYI' in pivot_base.columns:
                yp_vote = (pivot_base.loc[district, 'CHP'] * 0.875) + (pivot_base.loc[district, 'IYI'] * 0.125)
                new_rows.append({'district': district, 'party': 'YENI', 'base_vote_pct': yp_vote, 'seat_count': seat_count})
            
            if all(col in pivot_base.columns for col in ['AKP', 'BBP', 'MHP', 'IYI']):
                a_vote = (pivot_base.loc[district, 'AKP'] * 0.50) + (pivot_base.loc[district, 'BBP'] * 0.20) + (pivot_base.loc[district, 'MHP'] * 0.20) + (pivot_base.loc[district, 'IYI'] * 0.10)
                new_rows.append({'district': district, 'party': 'A', 'base_vote_pct': a_vote, 'seat_count': seat_count})
        
        if new_rows:
            df_synth = pd.DataFrame(new_rows)
            df = pd.concat([df, df_synth], ignore_index=True)

        df['weighted_vote'] = df['base_vote_pct'] * df['seat_count']
        national_totals = df.groupby('party')['weighted_vote'].sum()
        total_seats = df.groupby('district')['seat_count'].first().sum()
        
        national_totals = national_totals / total_seats
        return df, national_totals.to_dict()
        
    except FileNotFoundError as e:
        st.error(f"🚨 HATA: Dosya eksik - {str(e)}")
        st.info("Lütfen 'ysk_2023_secim_verisi.csv' ve 'ysk_2024_secim_verisi.csv' dosyalarının app.py ile aynı klasörde olduğundan emin olun.")
        st.stop()

df_base, base_national_dict = load_base_data()

PARTIES = ['AKP', 'CHP', 'IYI', 'DEM', 'MHP', 'YRP', 'TIP', 'ZAFER', 'YENI', 'A', 'BBP', 'SAADET']
PARTIES = [p for p in PARTIES if p in base_national_dict]

party_colors = {
    'AKP': '#FDA000', 'CHP': '#3485fd', 'MHP': '#137BBB', 
    'DEM': '#90268F', 'IYI': '#FFC107', 'YRP': '#009840', 
    'TIP': '#FF1D25', 'ZAFER': '#474647', 'YENI': '#A7050E',
    'A': '#20379f', 'BBP': '#B22222', 'SAADET': '#ff2e84'
}

# ==========================================
# 2. HESAPLAMA MOTORU (D'Hondt & Baraj)
# ==========================================
def calculate_dhondt(votes_dict, seat_count):
    seats_won = {p: 0 for p in votes_dict}
    divisors = {p: 1 for p in votes_dict}
    for _ in range(seat_count):
        winner = max(votes_dict.keys(), key=lambda p: votes_dict[p] / divisors[p])
        seats_won[winner] += 1
        divisors[winner] += 1
    return seats_won

def run_simulation(base_df, base_nat, user_nat, alliances, joint_lists, threshold=7.0):
    working_nat = user_nat.copy()
    for umbrella, joiners in joint_lists.items():
        for jp in joiners:
            working_nat[umbrella] += working_nat.get(jp, 0)
            working_nat[jp] = 0.0

    party_to_alliance = {}
    for alliance_name, parties in alliances.items():
        for p in parties:
            party_to_alliance[p] = alliance_name
            
    for p in PARTIES:
        if p not in party_to_alliance:
            party_to_alliance[p] = p
            alliances[p] = [p]

    alliance_national_votes = {}
    for alliance_name, parties in alliances.items():
        alliance_national_votes[alliance_name] = sum([working_nat.get(p, 0) for p in parties])

    qualified_alliances = [aly for aly, vote in alliance_national_votes.items() if vote >= threshold]
    
    qualified_parties = []
    for aly in qualified_alliances:
        qualified_parties.extend(alliances[aly])

    multipliers = {p: (user_nat[p] / base_nat[p]) if base_nat.get(p, 0) > 0 else 0 for p in PARTIES}
    
    results = []
    for district, group in base_df.groupby('district'):
        seat_count = group['seat_count'].iloc[0]
        
        proj_votes = {row['party']: row['base_vote_pct'] * multipliers.get(row['party'], 1.0) for _, row in group.iterrows()}
        total_proj = sum(proj_votes.values())
        norm_votes = {p: (v / total_proj) * 100 for p, v in proj_votes.items()} if total_proj > 0 else {p: 0 for p in proj_votes}
        
        for umbrella, joiners in joint_lists.items():
            if umbrella in norm_votes:
                for jp in joiners:
                    if jp in norm_votes:
                        norm_votes[umbrella] += norm_votes[jp]
                        norm_votes[jp] = 0.0
                        
        eligible_votes = {p: norm_votes[p] for p in qualified_parties if p in norm_votes and norm_votes[p] > 0}
        district_seats = calculate_dhondt(eligible_votes, seat_count) if eligible_votes else {}
            
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

# ==========================================
# 3. SVG HARİTA MOTORU
# ==========================================
def render_colored_svg(prov_winners, dist_winners, colors_dict, tooltip_dict, district_seats_data=None, svg_file_name="turkiye.svg", show_badges=True):
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        svg_file_path = os.path.join(current_dir, svg_file_name)
        
        with open(svg_file_path, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f.read(), 'html.parser')
            
        svg_tag = soup.find('svg') or soup.find('svg:svg')
        if svg_tag:
            svg_tag['width'] = "100%"
            svg_tag['height'] = "100%"
            
        paths = soup.find_all('path')
        badges_group = soup.new_tag('g', id='district-badges')
        placed_badges = set()
        
        custom_positions = {
            'kars': (1935, 260), 'tunceli': (1520, 460), 'karaman': (830, 750),
            'ankara1': (750, 410), 'konya': (730, 620), 'izmir2': (80, 500),
            'elazig': (1510, 535), 'malatya': (1350, 540), 'afyonkarahisar': (510, 525),
            'erzincan': (1510, 370), 'burdur': (455, 705), 'bursa2': (390, 260),
            'bursa1': (310, 310), 'ordu': (1310, 190), 'adana': (1060, 740),
            'giresun': (1415, 210), 'osmaniye': (1155, 745), 'ankara3': (690, 300),
            'ankara2': (790, 300), 'agri': (1925, 375), 'kayseri': (1100, 525),
            'sakarya': (510, 215), 'gaziantep': (1300, 760), 'denizli': (370, 670),
        }
        
        for path in paths:
            raw_id = path.get('id') or path.get('name') or path.get('data-name') or path.get('title') or ""
            svg_id_norm = normalize_id(raw_id)
            if not svg_id_norm: continue
                
            winner = dist_winners.get(svg_id_norm) or prov_winners.get(svg_id_norm)
            if winner:
                color = colors_dict.get(winner, "#CCCCCC")
                if 'style' in path.attrs:
                    style_str = path['style']
                    style_dict = {item.split(':')[0].strip(): item.split(':')[1].strip() for item in style_str.split(';') if ':' in item}
                    style_dict['fill'] = color
                    path['style'] = ';'.join([f"{k}:{v}" for k, v in style_dict.items()])
                else:
                    path['fill'] = color
                    
                path['data-tooltip'] = tooltip_dict.get(svg_id_norm, f"<b>{raw_id}</b><br>1. Sırada: {winner}")
                path['class'] = path.get('class', []) + ['map-path']
                path['data-norm-id'] = svg_id_norm 
                
                if show_badges and district_seats_data and svg_id_norm not in placed_badges:
                    placed_badges.add(svg_id_norm)
                    parties_won_in_prov = {}
                    for (dist_name, p_name), seats in district_seats_data.items():
                        dist_str = str(dist_name)
                        dist_norm = normalize_id(dist_str.split('-')[0] if '-' in dist_str else dist_str)
                        if dist_norm == svg_id_norm or normalize_id(dist_str) == svg_id_norm:
                            if seats > 0:
                                parties_won_in_prov[p_name] = parties_won_in_prov.get(p_name, 0) + int(seats)
                                
                    sorted_winners = sorted(parties_won_in_prov.items(), key=lambda x: x[1], reverse=True)
                    if sorted_winners:
                        man_x, man_y = custom_positions.get(svg_id_norm, ("", ""))
                        city_badge_g = soup.new_tag('g', **{
                            'class': 'badge-group', 'data-path-id': svg_id_norm,
                            'data-manual-x': str(man_x), 'data-manual-y': str(man_y)
                        })
                        
                        is_metro = any(m in svg_id_norm for m in ['istanbul'])
                        r_val = '9.5' if is_metro else '15'
                        f_size = '9px' if is_metro else '16px'
                        y_offset = 3 if is_metro else 4.5
                        spacing_x = 21 if is_metro else 32
                        spacing_y = 21 if is_metro else 32
                        
                        cols = 2 if len(sorted_winners) > 2 else len(sorted_winners)
                        rows = (len(sorted_winners) + cols - 1) // cols
                        base_start_y = -((rows - 1) * spacing_y) / 2
                        
                        for i, (party_name, seat_num) in enumerate(sorted_winners):
                            p_color = colors_dict.get(party_name, '#333333')
                            row_idx = i // cols
                            col_idx = i % cols
                            items_in_this_row = cols if row_idx < rows - 1 else (len(sorted_winners) - (rows - 1) * cols)
                            start_x = -((items_in_this_row - 1) * spacing_x) / 2
                            
                            current_x = start_x + (col_idx * spacing_x)
                            current_y = base_start_y + (row_idx * spacing_y)
                            
                            circle = soup.new_tag('circle', cx=str(current_x), cy=str(current_y), r=r_val, fill=p_color, stroke='#ffffff', **{'stroke-width': '1.5'})
                            city_badge_g.append(circle)
                            
                            text = soup.new_tag('text', x=str(current_x), y=str(current_y + y_offset), **{
                                'text-anchor': 'middle', 'fill': '#ffffff', 'font-size': f_size,
                                'font-family': 'Segoe UI, sans-serif', 'font-weight': 'bold', 'pointer-events': 'none'
                            })
                            text.string = str(seat_num)
                            city_badge_g.append(text)
                            
                        badges_group.append(city_badge_g)
                        
        if show_badges and badges_group: svg_tag.append(badges_group)
                
        css_style = "<style>body{margin:0;background-color:transparent;display:flex;justify-content:center;}.map-container{position:relative;width:100%;max-width:950px;min-height:550px;display:flex;justify-content:center;}.map-path{cursor:pointer;transition:opacity 0.2s;}.map-path:hover{opacity:0.8;stroke:#000;stroke-width:2px;}#svg-tooltip{position:absolute;display:none;background:white;border:1px solid #ccc;padding:10px 14px;box-shadow:0 4px 15px rgba(0,0,0,0.2);border-radius:6px;pointer-events:none;z-index:9999;font-family:'Segoe UI', Tahoma, sans-serif;font-size:13px;color:#333;min-width:190px;}.tip-header{font-weight:bold;font-size:14px;margin-bottom:6px;border-bottom:1px solid #eee;padding-bottom:4px;color:#111;}.tip-row{display:flex;align-items:center;margin-bottom:3px;}.tip-party{width:80px;font-weight:600;color:#333;}.tip-seat{background:#111;color:#fff;width:24px;text-align:center;font-weight:bold;font-size:11px;margin-right:6px;}.tip-bar-bg{flex-grow:1;background:#eee;height:12px;border-radius:2px;overflow:hidden;}.tip-bar-fill{height:100%;}.tip-pct{margin-left:6px;font-size:11px;color:#666;width:45px;text-align:right;} .badge-group { transition: transform 0.5s ease; opacity: 0; animation: fadeIn 0.5s forwards 0.2s; } @keyframes fadeIn { to { opacity: 1; } }</style>"
        js_script = "<script>document.addEventListener(\"DOMContentLoaded\", function() { const paths = document.querySelectorAll('.map-path'); const tooltip = document.getElementById('svg-tooltip'); const wrapper = document.getElementById('map-wrapper'); paths.forEach(path => { path.addEventListener('mousemove', (e) => { const tooltipData = path.getAttribute('data-tooltip'); if(tooltipData){ tooltip.innerHTML = tooltipData; tooltip.style.display = 'block'; const rect = wrapper.getBoundingClientRect(); const tipRect = tooltip.getBoundingClientRect(); let x = e.clientX - rect.left + 15; let y = e.clientY - rect.top + 15; if(e.clientX - rect.left + tipRect.width + 25 > rect.width){ x = e.clientX - rect.left - tipRect.width - 15; } if(e.clientY - rect.top + tipRect.height + 25 > rect.height){ y = e.clientY - rect.top - tipRect.height - 15; } tooltip.style.left = x + 'px'; tooltip.style.top = y + 'px'; } }); path.addEventListener('mouseleave', () => { tooltip.style.display = 'none'; }); }); setTimeout(() => { const badgeGroups = document.querySelectorAll('.badge-group'); badgeGroups.forEach(bg => { const manualX = bg.getAttribute('data-manual-x'); const manualY = bg.getAttribute('data-manual-y'); if (manualX && manualY) { bg.setAttribute('transform', `translate(${manualX}, ${manualY})`); } else { const pathId = bg.getAttribute('data-path-id'); const targetPath = document.querySelector(`.map-path[data-norm-id=\"${pathId}\"]`); if (targetPath) { const bbox = targetPath.getBBox(); if(bbox.width > 0 && bbox.height > 0) { const centerX = bbox.x + (bbox.width / 2); const centerY = bbox.y + (bbox.height / 2); bg.setAttribute('transform', `translate(${centerX}, ${centerY})`); } } } }); }, 100); });</script>"

        complete_html = f"<!DOCTYPE html><html><head>{css_style}</head><body><div class='map-container' id='map-wrapper'><div id='svg-tooltip'></div>{str(svg_tag)}</div>{js_script}</body></html>"
        return complete_html
    except Exception as e:
        return f"<div style='color:red;'>SVG Hatası: {str(e)}</div>"

# ==========================================
# 4. ARAYÜZ (UI) TASARIMI & SİDEBAR
# ==========================================
st.title("AD Türkiye Genel Seçim Projeksiyonu")

custom_start_values = {
    'AKP': 27.4, 'CHP': 1.0, 'MHP': 5.4, 'DEM': 7.6, 
    'IYI': 5.1, 'YRP': 3.8, 'ZAFER': 2.9, 'TIP': 1.1, 
    'YENI': 38.3, 'A': 4.5, 'BBP': 0.9, 'SAADET': 1.1
}

# --- İTTİFAK VE ORTAK LİSTE HAFIZA YÖNETİMİ ---
if 'alliance_list' not in st.session_state:
    st.session_state.alliance_list = [
        {"id": "aly_1", "name": "Cumhur İttifakı", "parties": [p for p in ['AKP', 'MHP', 'BBP'] if p in PARTIES]},
        {"id": "aly_2", "name": "Emek ve Özgürlük İttifakı", "parties": [p for p in ['DEM', 'TIP'] if p in PARTIES]}
    ]
    st.session_state.next_aly_id = 3

if 'joint_list' not in st.session_state:
    st.session_state.joint_list = []
    st.session_state.next_jl_id = 1

# --- SİDEBAR FORM ---
with st.sidebar.form("main_simulation_form"):
    st.header("Ulusal Oy Oranları")
    
    user_inputs = {}
    total_input = 0
    for p in PARTIES:
        varsayilan_oy = custom_start_values.get(p, float(base_national_dict.get(p, 0)))
        val = st.number_input(f"{p} (%)", min_value=0.0, max_value=100.0, value=varsayilan_oy, step=0.1, key=f"inp_{p}")
        user_inputs[p] = val
        total_input += val

    st.divider()
    st.subheader("Seçim Parametreleri")
    threshold_input = st.number_input("Ülke Barajı (%)", min_value=0.0, max_value=15.0, value=7.0, step=0.5)

    st.divider()
    st.subheader("İttifak Seçenekleri")
    for aly in st.session_state.alliance_list:
        new_name = st.text_input("İttifak Adı", value=aly['name'], key=f"name_{aly['id']}")
        aly['name'] = new_name
        current_parties = [p for p in aly['parties'] if p in PARTIES]
        new_parties = st.multiselect("Partiler", options=PARTIES, default=current_parties, key=f"parties_{aly['id']}")
        aly['parties'] = new_parties
        st.write("")

    st.divider()
    st.subheader("Ortak Liste Seçenekleri")
    st.caption("Seçilen İLK parti çatı (logo) parti olur.")
    for idx, jl in enumerate(st.session_state.joint_list):
        list_title = f"{jl['parties'][0]} Listesi" if jl.get('parties') and len(jl['parties']) > 0 else f"Yeni Liste {idx + 1}"
        selected_parties = st.multiselect(list_title, options=PARTIES, default=jl.get('parties', []), key=f"join_{jl['id']}")
        jl['parties'] = selected_parties

    st.markdown("<br>", unsafe_allow_html=True)
    submit_button = st.form_submit_button("🚀 SİMÜLASYONU ÇALIŞTIR", type="primary", use_container_width=True)

# Yalnızca tek bir dinamik yönetim alanı
with st.sidebar.expander("⚙️ İttifak / Liste Ekle & Çıkar", expanded=False):
    c_btn1, c_btn2 = st.columns(2)
    with c_btn1:
        if st.button("➕ İttifak Ekle", use_container_width=True):
            st.session_state.alliance_list.append({
                "id": f"aly_{st.session_state.next_aly_id}",
                "name": f"Yeni Blok {st.session_state.next_aly_id}",
                "parties": []
            })
            st.session_state.next_aly_id += 1
            st.rerun()
    with c_btn2:
        if st.button("➕ Liste Ekle", use_container_width=True):
            st.session_state.joint_list.append({
                "id": f"jl_{st.session_state.next_jl_id}",
                "parties": []
            })
            st.session_state.next_jl_id += 1
            st.rerun()
            
    if len(st.session_state.alliance_list) > 0 and st.button("🗑️ Son İttifakı Sil", use_container_width=True):
        st.session_state.alliance_list.pop()
        st.rerun()
        
    if len(st.session_state.joint_list) > 0 and st.button("🗑️ Son Listeyi Sil", use_container_width=True):
        st.session_state.joint_list.pop()
        st.rerun()

# Simülasyon Verilerini Hazırla
if abs(total_input - 100.0) > 0.1:
    st.sidebar.warning(f"Toplam oy %{total_input:.1f}. Oylar %100'e normalize ediliyor.")

user_inputs_norm = {p: (v / total_input) * 100 if total_input > 0 else 0 for p, v in user_inputs.items()}

alliances = {}
for aly in st.session_state.alliance_list:
    if aly['name'].strip() and len(aly['parties']) > 0:
        alliances[aly['name']] = aly['parties']

joint_lists = {}
for jl in st.session_state.joint_list:
    if len(jl['parties']) > 1:
        joint_lists[jl['parties'][0]] = jl['parties'][1:]

df_results = run_simulation(df_base, base_national_dict, user_inputs_norm, alliances, joint_lists, threshold=threshold_input)

display_user_nat = user_inputs_norm.copy()
for umbrella, joiners in joint_lists.items():
    for jp in joiners:
        display_user_nat[umbrella] += display_user_nat.get(jp, 0)
        display_user_nat[jp] = 0.0

# --- DETAYLI ULUSAL ÖZET TABLOSU VE DEĞİŞİM (DELTA) GÖSTERGELERİ ---
base_seats_2023 = {
    'AKP': 268, 'CHP': 169, 'DEM': 61, 'MHP': 50, 'IYI': 43, 
    'YRP': 5, 'TIP': 4, 'ZAFER': 0, 'YENI': 0, 'A': 0, 'BBP': 0, 'SAADET': 0
}

base_votes_2023 = {
    'AKP': 35.6, 'CHP': 25.3, 'MHP': 10.1, 'IYI': 9.7, 
    'DEM': 8.8, 'YRP': 2.8, 'ZAFER': 2.2, 'TIP': 1.8,
    'BBP': 1.0, 'SAADET': 0.0, 'YENI': 0.0, 'A': 0.0
}

summary_data = []
for p in PARTIES:
    seats = df_results[df_results['party'] == p]['seats_won'].sum()
    base_vote = base_votes_2023.get(p, 0.0)
    new_vote = display_user_nat.get(p, 0)
    vote_delta = new_vote - base_vote
    base_seat = base_seats_2023.get(p, 0)
    seat_delta = seats - base_seat

    summary_data.append({
        'Parti': p,
        'Normalize Oy (%)': round(new_vote, 2),
        'Oy Değişimi': round(vote_delta, 2),
        'Vekil': int(seats),
        'Vekil Değişimi': int(seat_delta)
    })

national_summary_df = pd.DataFrame(summary_data).sort_values(by=['Normalize Oy (%)', 'Vekil'], ascending=[False, False])

st.subheader("TBMM Sandalye Dağılımı ve Oy Oranları")

col1, col2 = st.columns([1.5, 1])

with col1:
    max_vote_pct = national_summary_df['Normalize Oy (%)'].max()
    if max_vote_pct == 0: max_vote_pct = 1.0

    html_blocks = [f"""
    <style>
    .custom-row {{ display: flex; align-items: center; margin-bottom: 8px; font-family: 'Space Grotesk', 'Segoe UI', sans-serif; }}
    .custom-party {{ width: 110px; text-align: right; padding-right: 12px; font-weight: 900; color: {c_text}; font-size: 16px; text-transform: uppercase; }}
    .custom-seat {{ background-color: {t_seat_bg}; color: #ffffff !important; font-weight: bold; width: 60px; text-align: center; padding: 4px 0; margin-right: 10px; border: 2px solid {c_text}; box-shadow: 3px 3px 0px #eb252d; display: flex; flex-direction: column; justify-content: center; line-height: 1.1; }}
    .seat-num {{ font-size: 16px; }}
    .seat-delta {{ font-size: 10.5px; font-weight: 900; }}
    .delta-pos {{ color: #00E676; }}
    .delta-neg {{ color: #FF3D00; }}
    .delta-neu {{ color: #9E9E9E; }}
    .custom-bar-bg {{ flex-grow: 1; background-color: {t_bar_bg}; height: 42px; overflow: hidden; display: flex; border: 2px solid {c_text}; box-shadow: 3px 3px 0px #eb252d; }}
    .custom-bar-fill {{ height: 100%; display: flex; align-items: center; padding-left: 8px; color: #ffffff !important; font-weight: 700; font-size: 14px; white-space: nowrap; border-right: 2px solid {c_text}; }}
    .vote-delta {{ font-size: 11px; margin-left: 6px; font-weight: 400; opacity: 0.9; }}
    </style>
    <div style="max-width: 100%; margin: 10px 0 10px 0;">
    """]

    for index, row in national_summary_df.iterrows():
        party = row['Parti']
        seats = int(row['Vekil'])
        vote_pct = row['Normalize Oy (%)']
        seat_delta = int(row['Vekil Değişimi'])
        vote_delta = row['Oy Değişimi']
        
        color = party_colors.get(party, "#888888")
        relative_width = (vote_pct / max_vote_pct) * 100
        
        if seat_delta > 0:
            s_delta_html = f"<span class='seat-delta delta-pos'>▲ {seat_delta}</span>"
        elif seat_delta < 0:
            s_delta_html = f"<span class='seat-delta delta-neg'>▼ {abs(seat_delta)}</span>"
        else:
            s_delta_html = f"<span class='seat-delta delta-neu'>-</span>"
            
        if vote_delta > 0:
            v_delta_str = f"(+{vote_delta:.1f})"
        elif vote_delta < 0:
            v_delta_str = f"({vote_delta:.1f})"
        else:
            v_delta_str = ""
            
        html_blocks.append(
            f'<div class="custom-row">'
            f'<div class="custom-party">{party}</div>'
            f'<div class="custom-seat"><span class="seat-num">{seats}</span>{s_delta_html}</div>'
            f'<div class="custom-bar-bg">'
            f'<div class="custom-bar-fill" style="width: {relative_width}%; background-color: {color}; min-width: 90px;">'
            f'%{vote_pct:.1f} <span class="vote-delta">{v_delta_str}</span>'
            f'</div></div></div>'
        )
        
    html_blocks.append("</div>")
    st.markdown("".join(html_blocks), unsafe_allow_html=True)

with col2:
    df_plot = national_summary_df[national_summary_df['Vekil'] > 0].copy()
    toplam_vekil = df_plot['Vekil'].sum()

    istenen_sira = ['TIP', 'DEM', 'CHP', 'YENI', 'IYI', 'SAADET', 'ZAFER', 'A', 'AKP', 'MHP', 'BBP', 'YRP']
    sirali_partiler = [p for p in istenen_sira if p in df_plot['Parti'].values]
    for p in df_plot['Parti'].values:
        if p not in sirali_partiler: sirali_partiler.append(p)

    ordered_values = [df_plot[df_plot['Parti'] == p]['Vekil'].values[0] for p in sirali_partiler]
    ordered_colors = [party_colors.get(p, "#888888") for p in sirali_partiler]

    labels = sirali_partiler + ["Gizli_Yari"]
    values = ordered_values + [toplam_vekil]
    colors = ordered_colors + ["rgba(0,0,0,0)"]
    line_widths = [2] * len(sirali_partiler) + [0]

    fig = go.Figure(data=[go.Pie(
        labels=labels, values=values, hole=0.55, rotation=-90, direction="clockwise", sort=False,
        marker=dict(colors=colors, line=dict(color=c_bg, width=line_widths)),
        textinfo='label+value', textposition='inside', insidetextorientation='horizontal', hoverinfo='none'
    )])

    fig.update_layout(
        showlegend=False, margin=dict(t=0, b=0, l=0, r=0), height=320,
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        annotations=[dict(text=f"<b><span style='font-size:34px; color:{c_text}'>{toplam_vekil}</span></b>", x=0.5, y=0.5, yanchor='bottom', showarrow=False)]
    )
    fig.update_traces(texttemplate="%{label}<br>%{value}", selector=dict(type='pie'))
    fig.data[0].texttemplate = [f"{l}<br>{v}" for l, v in zip(sirali_partiler, ordered_values)] + [""]

    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

st.divider()

# --- MECLİS SVG HARİTA BÖLÜMÜ ---
st.subheader("Genel Seçim İl Haritası")
province_summary = df_results.groupby(['province', 'party'])['new_vote_pct'].mean().reset_index()
first_parties_prov = province_summary.loc[province_summary.groupby('province')['new_vote_pct'].idxmax()]
prov_winners_dict = {normalize_id(row['province']): row['party'] for _, row in first_parties_prov.iterrows()}

first_parties_dist = df_results.loc[df_results.groupby('district')['new_vote_pct'].idxmax()]
dist_winners_dict = {normalize_id(row['district']): row['party'] for _, row in first_parties_dist.iterrows()}

tooltip_dict = {}
def create_tooltip_html(title_str, group_data):
    sorted_g = group_data.sort_values(by='new_vote_pct', ascending=False).head(5)
    html = f'<div class="tip-header">{title_str}</div>'
    for _, r in sorted_g.iterrows():
        pct = r['new_vote_pct']
        if pct > 0.0:
            party = r['party']
            seats = int(r['seats_won'])
            color = party_colors.get(party, '#888888')
            html += f'''
            <div class="tip-row">
                <div class="tip-party">{party}</div>
                <div class="tip-seat">{seats}</div>
                <div class="tip-bar-bg"><div class="tip-bar-fill" style="width: {pct}%; background-color: {color};"></div></div>
                <div class="tip-pct">%{pct:.1f}</div>
            </div>
            '''
    return html

for dist, group in df_results.groupby('district'):
    tooltip_dict[normalize_id(dist)] = create_tooltip_html(f"📌 {dist}", group)

for prov, group in df_results.groupby('province'):
    prov_agg = group.groupby('party').agg({'new_vote_pct': 'mean', 'seats_won': 'sum'}).reset_index()
    tooltip_dict[normalize_id(prov)] = create_tooltip_html(f"📌 {prov}", prov_agg)

district_seats_data = df_results.groupby(['district', 'party'])['seats_won'].sum().to_dict()
colored_svg_html = render_colored_svg(prov_winners_dict, dist_winners_dict, party_colors, tooltip_dict, district_seats_data, svg_file_name="turkiye.svg", show_badges=True)

components.html(colored_svg_html, height=500, scrolling=False)
st.divider()

# --- TABLO BÖLÜMÜ (COLLAPSIBLE) ---
with st.expander("📊 İl İl Dağılım Tablosu", expanded=False):
    pivot_df = df_results.pivot(index='district', columns='party', values=['new_vote_pct', 'seats_won'])
    sirali_partiler_tablo = national_summary_df['Parti'].tolist()

    display_df = pd.DataFrame()
    for p in sirali_partiler_tablo:
        if p in pivot_df['new_vote_pct'].columns:
            display_df[f"{p} (%)"] = pivot_df['new_vote_pct'][p].round(1)
            display_df[f"{p} (Vekil)"] = pivot_df['seats_won'][p].astype(int)

    def highlight_first_party(row):
        styles = [''] * len(row)
        vote_cols = [col for col in row.index if '(%)' in col]
        if not vote_cols: return styles
        
        max_val = -1
        best_col = None
        for col in vote_cols:
            if row[col] > max_val:
                max_val = row[col]
                best_col = col
                
        if best_col:
            party_name = best_col.split(' ')[0]
            color = party_colors.get(party_name, '#CCCCCC')
            for i, col in enumerate(row.index):
                if col.startswith(party_name):
                    styles[i] = f'background-color: {color}; color: white; font-weight: bold;'
        return styles

    styled_table = display_df.style.apply(highlight_first_party, axis=1).format(lambda x: f"%{x:.1f}" if isinstance(x, float) else x)
    st.dataframe(styled_table, use_container_width=True)

# --- SWING MODÜLÜ (COLLAPSIBLE) ---
with st.expander("🎯 Fırsat ve Risk Analizi (Swing Modülü)", expanded=False):
    st.info("Bu modül, en az oy farkıyla kazanılan veya el değiştirmeye en yakın vekillikleri gösterir. Stratejik odaklanma için kritik bölgelerdir.")

    target_party_swing = st.selectbox(
        "Hangi parti için fırsat / risk analizi yapılsın?", 
        options=[p for p in PARTIES if national_summary_df[national_summary_df['Parti'] == p]['Vekil'].values[0] > 0 or display_user_nat.get(p, 0) > 1.0],
        index=0
    )

    swing_data = []
    party_to_alliance_sw = {}
    temp_alliances_sw = alliances.copy()
    for alliance_name, parties in temp_alliances_sw.items():
        for p in parties:
            party_to_alliance_sw[p] = alliance_name
            
    for p in PARTIES:
        if p not in party_to_alliance_sw:
            temp_alliances_sw[p] = [p]

    alliance_national_votes_sw = {}
    for alliance_name, parties in temp_alliances_sw.items():
        alliance_national_votes_sw[alliance_name] = sum([display_user_nat.get(p, 0) for p in parties])

    qualified_parties_sw = [p for aly, vote in alliance_national_votes_sw.items() if vote >= threshold_input for p in temp_alliances_sw[aly]]

    for district, group in df_base.groupby('district'):
        seat_count = group['seat_count'].iloc[0]
        multipliers_swing = {p: (user_inputs_norm[p] / base_national_dict[p]) if base_national_dict.get(p, 0) > 0 else 0 for p in PARTIES}
        proj_votes_sw = {row['party']: row['base_vote_pct'] * multipliers_swing.get(row['party'], 1.0) for _, row in group.iterrows()}
        total_proj_sw = sum(proj_votes_sw.values())
        norm_votes_sw = {p: (v / total_proj_sw) * 100 for p, v in proj_votes_sw.items()} if total_proj_sw > 0 else {p: 0 for p in proj_votes_sw}
        
        for umbrella, joiners in joint_lists.items():
            if umbrella in norm_votes_sw:
                for jp in joiners:
                    if jp in norm_votes_sw:
                        norm_votes_sw[umbrella] += norm_votes_sw[jp]
                        norm_votes_sw[jp] = 0.0
                        
        eligible_votes_sw = {p: norm_votes_sw[p] for p in qualified_parties_sw if p in norm_votes_sw and norm_votes_sw[p] > 0}
        
        if not eligible_votes_sw: continue
            
        quotients = []
        for p, v in eligible_votes_sw.items():
            for i in range(1, int(seat_count) + 2):
                quotients.append({'party': p, 'quotient': v / i, 'seat_idx': i})
                
        quotients.sort(key=lambda x: x['quotient'], reverse=True)
        
        if len(quotients) >= int(seat_count) + 1:
            last_winning = quotients[int(seat_count) - 1]
            first_losing = quotients[int(seat_count)]
            
            if last_winning['party'] == target_party_swing:
                margin = last_winning['quotient'] - first_losing['quotient']
                swing_data.append({
                    'İlçe': district,
                    'Durum': 'Riskli (Kıl Payı Kazandı)',
                    'Rakip': first_losing['party'],
                    'Fark Skoru': margin,
                    'Açıklama': f"Son vekil {margin:.2f} puan farkla {first_losing['party']}'den kurtarıldı."
                })
            elif first_losing['party'] == target_party_swing:
                margin = last_winning['quotient'] - first_losing['quotient']
                swing_data.append({
                    'İlçe': district,
                    'Durum': 'Fırsat (Kıl Payı Kaçırdı)',
                    'Rakip': last_winning['party'],
                    'Fark Skoru': margin,
                    'Açıklama': f"Son vekil {margin:.2f} puan farkla {last_winning['party']}'ye kaybedildi."
                })

    if swing_data:
        swing_df = pd.DataFrame(swing_data)
        firsatlar = swing_df[swing_df['Durum'].str.contains('Fırsat')].sort_values(by='Fark Skoru').head(10)
        riskler = swing_df[swing_df['Durum'].str.contains('Riskli')].sort_values(by='Fark Skoru').head(10)
        
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            st.markdown(f"### 🔴 Kılpayı Kaybedilenler")
            if not firsatlar.empty:
                for _, row in firsatlar.iterrows():
                    st.info(f"**{row['İlçe']}** ⚔️ Rakip: {row['Rakip']}  \n*{row['Açıklama']}*")
            else:
                st.write("Belirgin bir fırsat bölgesi bulunamadı.")
                
        with col_s2:
            st.markdown(f"### 🟢 Ucundan Alınanlar")
            if not riskler.empty:
                for _, row in riskler.iterrows():
                    st.warning(f"**{row['İlçe']}** ⚔️ Rakip: {row['Rakip']}  \n*{row['Açıklama']}*")
            else:
                st.write("Riskli bir bölge bulunamadı.")

# ==========================================
# 6. CUMHURBAŞKANLIĞI SEÇİMİ VE HARİTASI
# ==========================================
st.divider()
st.header("🗳️ Cumhurbaşkanlığı Seçimi Projeksiyonu")
st.markdown("Adayları ve renklerini belirleyin, partilerin tabanlarından alacakları destek oranlarını girip simülasyonu başlatın.")

cb_parties = [p for p in PARTIES if display_user_nat.get(p, 0) > 0.0]

default_candidate_palette = ['#e63946', '#1d3557', '#2a9d8f', '#e76f51', '#f4a261', '#457b9d', '#9b5de5', '#00f5d4']

if 'candidate_colors_dict' not in st.session_state:
    st.session_state.candidate_colors_dict = {
        "Cumhur Adayı": "#FDA000",
        "Muhalefet Adayı 1": "#A7050E",
        "Muhalefet Adayı 2": "#20379f"
    }

if 'cb_df_1' not in st.session_state:
    init_data = {"Aday Adı": ["Cumhur Adayı", "Muhalefet Adayı 1", "Muhalefet Adayı 2"]}
    for p in cb_parties:
        init_data[p] = [0.0, 0.0, 0.0]
    st.session_state.cb_df_1 = pd.DataFrame(init_data)

st.subheader("1. Tur Senaryosu")
cb_edited_1 = st.data_editor(
    st.session_state.cb_df_1, 
    num_rows="dynamic",
    use_container_width=True, 
    hide_index=True,
    key="editor_tour1"
)

# Aday Renk Seçimi Bölümü
with st.expander("🎨 Aday Renklerini Özelleştir", expanded=False):
    cols_color = st.columns(4)
    c_idx = 0
    for ad in cb_edited_1["Aday Adı"]:
        ad_str = str(ad).strip()
        if ad_str and pd.notna(ad):
            default_c = st.session_state.candidate_colors_dict.get(ad_str, default_candidate_palette[c_idx % len(default_candidate_palette)])
            with cols_color[c_idx % 4]:
                new_c = st.color_picker(f"{ad_str}", value=default_c, key=f"cp_{ad_str}")
                st.session_state.candidate_colors_dict[ad_str] = new_c
            c_idx += 1

def calculate_cb_district_results(cb_df, df_results_data, colors_override):
    cb_dist_records = []
    pivot_dist_votes = df_results_data.pivot(index='district', columns='party', values='new_vote_pct').fillna(0)
    
    for district, row_party in pivot_dist_votes.iterrows():
        cand_votes_dist = {}
        for _, c_row in cb_df.iterrows():
            aday = str(c_row["Aday Adı"]).strip()
            if not aday: continue
            
            c_vote = 0.0
            for p in cb_parties:
                if p in c_row and not pd.isna(c_row[p]):
                    p_vote = row_party.get(p, 0.0)
                    share = float(c_row[p]) / 100.0
                    c_vote += p_vote * share
            cand_votes_dist[aday] = c_vote
            
        tot_c = sum(cand_votes_dist.values())
        norm_c = {ad: (v / tot_c) * 100 if tot_c > 0 else 0 for ad, v in cand_votes_dist.items()}
        
        for ad, pct in norm_c.items():
            cb_dist_records.append({
                'district': district,
                'province': district.split('-')[0],
                'candidate': ad,
                'pct': pct
            })
            
    df_cb_dist = pd.DataFrame(cb_dist_records)
    prov_summary = df_cb_dist.groupby(['province', 'candidate'])['pct'].mean().reset_index()
    first_prov = prov_summary.loc[prov_summary.groupby('province')['pct'].idxmax()]
    cb_prov_winners = {normalize_id(r['province']): r['candidate'] for _, r in first_prov.iterrows()}

    first_dist = df_cb_dist.loc[df_cb_dist.groupby('district')['pct'].idxmax()]
    cb_dist_winners = {normalize_id(r['district']): r['candidate'] for _, r in first_dist.iterrows()}
    
    cb_tooltips = {}
    for d_name, grp in df_cb_dist.groupby('district'):
        sorted_g = grp.sort_values(by='pct', ascending=False)
        html = f'<div class="tip-header">📌 {d_name} (CB Seçimi)</div>'
        for _, r in sorted_g.iterrows():
            col_ad = colors_override.get(r['candidate'], '#888')
            html += f'''
            <div class="tip-row">
                <div class="tip-party" style="width:100px;">{r['candidate']}</div>
                <div class="tip-bar-bg"><div class="tip-bar-fill" style="width: {r['pct']}%; background-color: {col_ad};"></div></div>
                <div class="tip-pct">%{r['pct']:.1f}</div>
            </div>
            '''
        cb_tooltips[normalize_id(d_name)] = html

    for p_name, grp in df_cb_dist.groupby('province'):
        prov_agg = grp.groupby('candidate')['pct'].mean().reset_index().sort_values(by='pct', ascending=False)
        html = f'<div class="tip-header">📌 {p_name} (CB Seçimi)</div>'
        for _, r in prov_agg.iterrows():
            col_ad = colors_override.get(r['candidate'], '#888')
            html += f'''
            <div class="tip-row">
                <div class="tip-party" style="width:100px;">{r['candidate']}</div>
                <div class="tip-bar-bg"><div class="tip-bar-fill" style="width: {r['pct']}%; background-color: {col_ad};"></div></div>
                <div class="tip-pct">%{r['pct']:.1f}</div>
            </div>
            '''
        cb_tooltips[normalize_id(p_name)] = html
        
    return cb_prov_winners, cb_dist_winners, colors_override, cb_tooltips

# 1. TUR HESAPLAMA BUTONU
cb_calc_button_1 = st.button("🗳️ 1. Tur Sonuçlarını & Haritasını Hesapla", type="primary", use_container_width=True)

if cb_calc_button_1 or ('cb_res_1_saved' in st.session_state):
    st.session_state.cb_res_1_saved = True
    
    cb_res_1 = {}
    for idx, row in cb_edited_1.iterrows():
        aday = row["Aday Adı"]
        if pd.isna(aday) or str(aday).strip() == "": continue
        votes = sum([display_user_nat.get(p, 0) * (float(row.get(p, 0)) / 100.0) for p in cb_parties if p in row and not pd.isna(row[p])])
        cb_res_1[str(aday).strip()] = votes

    total_cb_1 = sum(cb_res_1.values())

    if total_cb_1 > 0:
        st.markdown("### 📊 1. Tur Sonuçları")
        sorted_1 = sorted(cb_res_1.items(), key=lambda x: x[1], reverse=True)
        max_cb_pct1 = (sorted_1[0][1] / total_cb_1) * 100 if total_cb_1 > 0 else 1.0
        
        col_cb_bars, col_cb_map = st.columns([1.1, 1.3])
        
        with col_cb_bars:
            st.markdown("<div class='cb-card'>", unsafe_allow_html=True)
            for aday, votes in sorted_1:
                pct = (votes / total_cb_1) * 100
                cand_color = st.session_state.candidate_colors_dict.get(aday, "#457b9d")
                bar_width = (pct / max_cb_pct1) * 100
                st.markdown(f"""
                <div class='cb-row'>
                    <div class='cb-name'>{aday}</div>
                    <div class='cb-bar-bg'>
                        <div class='cb-bar-fill' style='width: {bar_width}%; background-color: {cand_color}; min-width: 60px;'>%{pct:.2f}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
                
            kazanan_orani = (sorted_1[0][1] / total_cb_1) * 100
            if kazanan_orani > 50.0:
                st.success(f"🎉 Seçim 1. Turda Bitti! **{sorted_1[0][0]}** %{kazanan_orani:.2f} ile Cumhurbaşkanı seçildi.")
            else:
                st.warning(f"⚖️ Hiçbir aday %50+1'e ulaşamadı. **{sorted_1[0][0]}** ve **{sorted_1[1][0]}** 2. tura kaldı.")
        
        with col_cb_map:
            st.markdown("#### 1. Tur Harita Dağılımı")
            p_win1, d_win1, c_cols1, t_tips1 = calculate_cb_district_results(cb_edited_1, df_results, st.session_state.candidate_colors_dict)
            svg_cb_html_1 = render_colored_svg(p_win1, d_win1, c_cols1, t_tips1, svg_file_name="turkiye.svg", show_badges=False)
            components.html(svg_cb_html_1, height=450, scrolling=False)

        # --- 2. TUR SENARYOSU ---
        if kazanan_orani <= 50.0 and len(sorted_1) > 1:
            st.divider()
            top1, top2 = sorted_1[0][0], sorted_1[1][0]
            st.subheader(f"2. Tur Senaryosu ({top1} vs {top2})")
            
            if 'cb_df_2' not in st.session_state or list(st.session_state.cb_df_2["Aday Adı"]) != [top1, top2]:
                init_data_2 = {"Aday Adı": [top1, top2]}
                for p in cb_parties:
                    val1 = cb_edited_1.loc[cb_edited_1['Aday Adı'] == top1, p].values
                    val2 = cb_edited_1.loc[cb_edited_1['Aday Adı'] == top2, p].values
                    init_data_2[p] = [val1[0] if len(val1)>0 else 0.0, val2[0] if len(val2)>0 else 0.0]
                st.session_state.cb_df_2 = pd.DataFrame(init_data_2)
                
            cb_edited_2 = st.data_editor(
                st.session_state.cb_df_2, 
                num_rows="fixed",
                use_container_width=True, 
                hide_index=True,
                key="editor_tour2"
            )
            
            cb_calc_button_2 = st.button("🏆 2. Tur Sonuçlarını & Haritasını Hesapla", type="primary", use_container_width=True)
            
            if cb_calc_button_2 or ('cb_res_2_saved' in st.session_state):
                st.session_state.cb_res_2_saved = True
                cb_res_2 = {}
                for idx, row in cb_edited_2.iterrows():
                    aday = str(row["Aday Adı"]).strip()
                    votes = sum([display_user_nat.get(p, 0) * (float(row.get(p, 0)) / 100.0) for p in cb_parties if p in row and not pd.isna(row[p])])
                    cb_res_2[aday] = votes
                    
                total_cb_2 = sum(cb_res_2.values())
                
                if total_cb_2 > 0:
                    st.markdown("### 🏆 2. Tur Kesin Sonuçları")
                    sorted_2 = sorted(cb_res_2.items(), key=lambda x: x[1], reverse=True)
                    max_cb_pct2 = (sorted_2[0][1] / total_cb_2) * 100 if total_cb_2 > 0 else 1.0
                    
                    col_cb2_bars, col_cb2_map = st.columns([1.1, 1.3])
                    
                    with col_cb2_bars:
                        st.markdown("<div class='cb-card'>", unsafe_allow_html=True)
                        for aday, votes in sorted_2:
                            pct = (votes / total_cb_2) * 100
                            cand_color = st.session_state.candidate_colors_dict.get(aday, "#2a9d8f")
                            bar_width = (pct / max_cb_pct2) * 100
                            st.markdown(f"""
                            <div class='cb-row'>
                                <div class='cb-name'>{aday}</div>
                                <div class='cb-bar-bg'>
                                    <div class='cb-bar-fill' style='width: {bar_width}%; background-color: {cand_color}; min-width: 60px;'>%{pct:.2f}</div>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                        st.markdown("</div>", unsafe_allow_html=True)
                        st.success(f"🇹🇷 Türkiye'nin 13. Cumhurbaşkanı: **{sorted_2[0][0]}** (%{ (sorted_2[0][1]/total_cb_2)*100:.2f})")
                        
                    with col_cb2_map:
                        st.markdown("#### 2. Tur Harita Dağılımı")
                        p_win2, d_win2, c_cols2, t_tips2 = calculate_cb_district_results(cb_edited_2, df_results, st.session_state.candidate_colors_dict)
                        svg_cb_html_2 = render_colored_svg(p_win2, d_win2, c_cols2, t_tips2, svg_file_name="turkiye.svg", show_badges=False)
                        components.html(svg_cb_html_2, height=450, scrolling=False)