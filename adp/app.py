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
    [data-testid="stAppViewContainer"] h3 {{
        color: {c_text} !important;
        text-shadow: none !important;
        font-weight: 900 !important;
        text-transform: uppercase;
        letter-spacing: -1px;
        margin-bottom: 1rem !important;
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
    
    [data-testid="stDataFrame"] {{
        border: 2px solid {c_border};
        box-shadow: 4px 4px 0px #eb252d;
        background-color: {c_bg};
    }}

    [data-testid="stHeader"] {{
        background-color: transparent !important;
    }}
</style>
"""
st.markdown(custom_theme_css, unsafe_allow_html=True)

# ==========================================
# 1. GÜÇLÜ İSİM NORMALİZASYONU VE VERİ OKUMA
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
        
        # DIGER temizliği
        if 'DIGER' in df_23['party'].values: df_23 = df_23[df_23['party'] != 'DIGER']
        if 'DIGER' in df_24['party'].values: df_24 = df_24[df_24['party'] != 'DIGER']

        # İlçelere göre ayrı ayrı %100'e normalize ediyoruz
        df_23['base_vote_pct'] = df_23.groupby('district')['base_vote_pct'].transform(lambda x: (x / x.sum()) * 100)
        df_24['base_vote_pct'] = df_24.groupby('district')['base_vote_pct'].transform(lambda x: (x / x.sum()) * 100)

        # Sütun isimlerini karmaşa olmaması için güncelliyoruz
        df_23 = df_23.rename(columns={'base_vote_pct': 'vote_23'})
        df_24 = df_24.rename(columns={'base_vote_pct': 'vote_24'})

        # TBMM vekil sayıları (seat_count) 2023 Genel Seçim dosyasında yer aldığı için onu referans alıyoruz
        seats_df = df_23[['district', 'seat_count']].drop_duplicates()

        # İki verisetini birleştir (Sadece birinde olan partiler NaN olmasın diye 0 ile dolduruyoruz. Örn: SAADET 2023'te 0 sayılır)
        df_merged = pd.merge(df_23[['district', 'party', 'vote_23']], 
                             df_24[['district', 'party', 'vote_24']], 
                             on=['district', 'party'], how='outer').fillna(0)

        # --- AĞIRLIKLI HARMANLAMA (%85 2023 + %15 2024) ---
        df_merged['base_vote_pct'] = (df_merged['vote_23'] * 0.85) + (df_merged['vote_24'] * 0.15)
        
        # Vekil sayılarını tekrar tabloya entegre ediyoruz
        df = pd.merge(df_merged, seats_df, on='district', how='left')

        # Her ilçede harmanlanmış son oyları pivot tablo ile yan yana getirelim
        pivot_base = df.pivot(index='district', columns='party', values='base_vote_pct').fillna(0)
        
        new_rows = []
        for district, row_data in df.groupby('district'):
            seat_count = row_data['seat_count'].iloc[0]
            
            # YENİ PARTİ SENTETİK TABANI (%87.5 CHP + %12.5 İYİ)
            if 'CHP' in pivot_base.columns and 'IYI' in pivot_base.columns:
                yp_vote = (pivot_base.loc[district, 'CHP'] * 0.875) + (pivot_base.loc[district, 'IYI'] * 0.125)
                new_rows.append({'district': district, 'party': 'YENI', 'base_vote_pct': yp_vote, 'seat_count': seat_count})
            
            # A PARTİSİ SENTETİK TABANI (%50 AKP + %20 BBP + %20 MHP + %10 İYİ)
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
        st.info("Lütfen 'ysk_2023_secim_verisi.csv' ve 'ysk_2024_secim_verisi.csv' dosyalarının aynı klasörde olduğundan emin olun.")
        st.stop()

df_base, base_national_dict = load_base_data()

# Tüm partiler eksiksiz tanımlandı
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

def run_simulation(base_df, base_nat, user_nat, alliances, threshold=7.0):
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
        alliance_national_votes[alliance_name] = sum([user_nat.get(p, 0) for p in parties])

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
        
        eligible_votes = {p: norm_votes[p] for p in qualified_parties if p in norm_votes}
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
def render_colored_svg(prov_winners, dist_winners, party_colors, tooltip_dict, district_seats_data, svg_file_name="turkiye.svg"):
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
                
            winning_party = dist_winners.get(svg_id_norm) or prov_winners.get(svg_id_norm)
            if winning_party:
                color = party_colors.get(winning_party, "#CCCCCC")
                if 'style' in path.attrs:
                    style_str = path['style']
                    style_dict = {item.split(':')[0].strip(): item.split(':')[1].strip() for item in style_str.split(';') if ':' in item}
                    style_dict['fill'] = color
                    path['style'] = ';'.join([f"{k}:{v}" for k, v in style_dict.items()])
                else:
                    path['fill'] = color
                    
                path['data-tooltip'] = tooltip_dict.get(svg_id_norm, f"<b>{raw_id}</b><br>1. Parti: {winning_party}")
                path['class'] = path.get('class', []) + ['map-path']
                path['data-norm-id'] = svg_id_norm 
                
                if svg_id_norm not in placed_badges:
                    placed_badges.add(svg_id_norm)
                    parties_won_in_prov = {}
                    for (dist_name, party), seats in district_seats_data.items():
                        dist_str = str(dist_name)
                        dist_norm = normalize_id(dist_str.split('-')[0] if '-' in dist_str else dist_str)
                        if dist_norm == svg_id_norm or normalize_id(dist_str) == svg_id_norm:
                            if seats > 0:
                                parties_won_in_prov[party] = parties_won_in_prov.get(party, 0) + int(seats)
                                
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
                            p_color = party_colors.get(party_name, '#333333')
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
                        
        if badges_group: svg_tag.append(badges_group)
                
        css_style = "<style>body{margin:0;background-color:transparent;display:flex;justify-content:center;}.map-container{position:relative;width:100%;max-width:950px;min-height:550px;display:flex;justify-content:center;}.map-path{cursor:pointer;transition:opacity 0.2s;}.map-path:hover{opacity:0.8;stroke:#000;stroke-width:2px;}#svg-tooltip{position:absolute;display:none;background:white;border:1px solid #ccc;padding:10px 14px;box-shadow:0 4px 15px rgba(0,0,0,0.2);border-radius:6px;pointer-events:none;z-index:9999;font-family:'Segoe UI', Tahoma, sans-serif;font-size:13px;color:#333;min-width:190px;}.tip-header{font-weight:bold;font-size:14px;margin-bottom:6px;border-bottom:1px solid #eee;padding-bottom:4px;color:#111;}.tip-row{display:flex;align-items:center;margin-bottom:3px;}.tip-party{width:50px;font-weight:600;color:#333;}.tip-seat{background:#111;color:#fff;width:24px;text-align:center;font-weight:bold;font-size:11px;margin-right:6px;}.tip-bar-bg{flex-grow:1;background:#eee;height:12px;border-radius:2px;overflow:hidden;}.tip-bar-fill{height:100%;}.tip-pct{margin-left:6px;font-size:11px;color:#666;width:45px;text-align:right;} .badge-group { transition: transform 0.5s ease; opacity: 0; animation: fadeIn 0.5s forwards 0.2s; } @keyframes fadeIn { to { opacity: 1; } }</style>"
        js_script = "<script>document.addEventListener(\"DOMContentLoaded\", function() { const paths = document.querySelectorAll('.map-path'); const tooltip = document.getElementById('svg-tooltip'); const wrapper = document.getElementById('map-wrapper'); paths.forEach(path => { path.addEventListener('mousemove', (e) => { const tooltipData = path.getAttribute('data-tooltip'); if(tooltipData){ tooltip.innerHTML = tooltipData; tooltip.style.display = 'block'; const rect = wrapper.getBoundingClientRect(); const tipRect = tooltip.getBoundingClientRect(); let x = e.clientX - rect.left + 15; let y = e.clientY - rect.top + 15; if(e.clientX - rect.left + tipRect.width + 25 > rect.width){ x = e.clientX - rect.left - tipRect.width - 15; } if(e.clientY - rect.top + tipRect.height + 25 > rect.height){ y = e.clientY - rect.top - tipRect.height - 15; } tooltip.style.left = x + 'px'; tooltip.style.top = y + 'px'; } }); path.addEventListener('mouseleave', () => { tooltip.style.display = 'none'; }); }); setTimeout(() => { const badgeGroups = document.querySelectorAll('.badge-group'); badgeGroups.forEach(bg => { const manualX = bg.getAttribute('data-manual-x'); const manualY = bg.getAttribute('data-manual-y'); if (manualX && manualY) { bg.setAttribute('transform', `translate(${manualX}, ${manualY})`); } else { const pathId = bg.getAttribute('data-path-id'); const targetPath = document.querySelector(`.map-path[data-norm-id=\"${pathId}\"]`); if (targetPath) { const bbox = targetPath.getBBox(); if(bbox.width > 0 && bbox.height > 0) { const centerX = bbox.x + (bbox.width / 2); const centerY = bbox.y + (bbox.height / 2); bg.setAttribute('transform', `translate(${centerX}, ${centerY})`); } } } }); }, 100); });</script>"

        complete_html = f"<!DOCTYPE html><html><head>{css_style}</head><body><div class='map-container' id='map-wrapper'><div id='svg-tooltip'></div>{str(svg_tag)}</div>{js_script}</body></html>"
        return complete_html
    except Exception as e:
        return f"<div style='color:red;'>SVG Hatası: {str(e)}</div>"

# ==========================================
# 4. ARAYÜZ (UI) TASARIMI
# ==========================================
st.title("AD Türkiye Genel Seçim Projeksiyonu")

# --- 1. SIRA: OY GİRİŞİ (EN YUKARI ALINDI) ---
st.sidebar.header("Ulusal Oy Oranları")

custom_start_values = {
    'AKP': 27.4, 'CHP': 1.0, 'MHP': 5.4, 'DEM': 7.6, 
    'IYI': 5.1, 'YRP': 3.8, 'ZAFER': 2.9, 'TIP': 1.1, 
    'YENI': 38.3, 'A': 4.5, 'BBP': 0.9, 'SAADET': 1.1
}

user_inputs = {}
total_input = 0
for p in PARTIES:
    varsayilan_oy = custom_start_values.get(p, float(base_national_dict.get(p, 0)))
    val = st.sidebar.number_input(f"{p} (%)", min_value=0.0, max_value=100.0, value=varsayilan_oy, step=0.1)
    user_inputs[p] = val
    total_input += val

if abs(total_input - 100.0) > 0.1:
    st.sidebar.warning(f"Toplam oy %{total_input:.1f}. Oylar %100'e normalize ediliyor.")

user_inputs_norm = {p: (v / total_input) * 100 if total_input > 0 else 0 for p, v in user_inputs.items()}

st.sidebar.divider()

# --- 2. SIRA: SEÇİM PARAMETRELERİ (BARAJ) ---
st.sidebar.subheader("Seçim Parametreleri")
threshold_input = st.sidebar.number_input("Ülke Barajı (%)", min_value=0.0, max_value=15.0, value=7.0, step=0.5)

st.sidebar.divider()

# --- 3. SIRA: İTTİFAK SEÇENEKLERİ ---
st.sidebar.subheader("İttifak Seçenekleri")
use_alliances = st.sidebar.checkbox("İttifak Sistemini Etkinleştir", value=True)

alliances = {}
if use_alliances:
    st.sidebar.markdown("**Ön Tanımlı İttifaklar:**")
    enable_cumhur = st.sidebar.checkbox("Cumhur İttifakı", value=True)
    if enable_cumhur:
        default_cumhur = [p for p in ['AKP', 'MHP'] if p in PARTIES]
        cumhur_parties = st.sidebar.multiselect("Cumhur İttifakı Üyeleri", PARTIES, default=default_cumhur, key="cumhur_parties")
        if cumhur_parties: alliances["Cumhur İttifakı"] = cumhur_parties
            
    enable_emek = st.sidebar.checkbox("Emek ve Özgürlük İttifakı", value=True)
    if enable_emek:
        default_emek = [p for p in ['DEM', 'TIP'] if p in PARTIES]
        emek_parties = st.sidebar.multiselect("Emek ve Özgürlük İttifakı Üyeleri", PARTIES, default=default_emek, key="emek_parties")
        if emek_parties: alliances["Emek ve Özgürlük İttifakı"] = emek_parties
        
    st.sidebar.markdown("**Özel İttifak Ekle:**")
    custom_aly_name = st.sidebar.text_input("İttifak Adı", placeholder="Örn: Alternatif Blok")
    assigned_parties = [p for parties in alliances.values() for p in parties]
    available_parties_for_custom = [p for p in PARTIES if p not in assigned_parties]
    custom_aly_parties = st.sidebar.multiselect("İttifak Üyesi Partiler", available_parties_for_custom, key="custom_aly_parties")
    if custom_aly_name and custom_aly_parties:
        alliances[custom_aly_name] = custom_aly_parties

# --- BÜTÜN GİRİŞLER TAMAMLANDIKTAN SONRA SİMÜLASYONU ÇALIŞTIR ---
df_results = run_simulation(df_base, base_national_dict, user_inputs_norm, alliances, threshold=threshold_input)

# --- DETAYLI ULUSAL ÖZET TABLOSU ---
summary_data = []
for p in PARTIES:
    seats = df_results[df_results['party'] == p]['seats_won'].sum()
    summary_data.append({
        'Parti': p,
        'Normalize Oy (%)': round(user_inputs_norm.get(p, 0), 2),
        'Vekil': int(seats)
    })

# Ülke geneli oy oranına göre büyükten küçüğe kusursuz sıralama
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
    .custom-seat {{ background-color: {t_seat_bg}; color: #ffffff !important; font-weight: bold; width: 45px; text-align: center; padding: 6px 0; font-size: 15px; margin-right: 10px; border: 2px solid {c_text}; box-shadow: 3px 3px 0px #eb252d; }}
    .custom-bar-bg {{ flex-grow: 1; background-color: {t_bar_bg}; height: 36px; overflow: hidden; display: flex; border: 2px solid {c_text}; box-shadow: 3px 3px 0px #eb252d; }}
    .custom-bar-fill {{ height: 100%; display: flex; align-items: center; padding-left: 8px; color: #ffffff !important; font-weight: 700; font-size: 14px; white-space: nowrap; border-right: 2px solid {c_text}; }}
    </style>
    <div style="max-width: 100%; margin: 10px 0 10px 0;">
    """]

    # Zaten national_summary_df yukarıda sıralandığı için doğrudan basıyoruz
    for index, row in national_summary_df.iterrows():
        party = row['Parti']
        seats = int(row['Vekil'])
        vote_pct = row['Normalize Oy (%)']
        color = party_colors.get(party, "#888888")
        relative_width = (vote_pct / max_vote_pct) * 100
        
        html_blocks.append(f'<div class="custom-row"><div class="custom-party">{party}</div><div class="custom-seat">{seats}</div><div class="custom-bar-bg"><div class="custom-bar-fill" style="width: {relative_width}%; background-color: {color}; min-width: 60px;">%{vote_pct:.2f}</div></div></div>')
        
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

# --- SVG HARİTA BÖLÜMÜ ---
st.subheader("İl Haritası")
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
colored_svg_html = render_colored_svg(prov_winners_dict, dist_winners_dict, party_colors, tooltip_dict, district_seats_data, svg_file_name="turkiye.svg")

components.html(colored_svg_html, height=500, scrolling=False)
st.divider()

# --- TABLO BÖLÜMÜ ---
st.subheader("İl İl Dağılım Tablosu")
pivot_df = df_results.pivot(index='district', columns='party', values=['new_vote_pct', 'seats_won'])

# Ülke geneli oy oranına göre partileri büyükten küçüğe sıralıyoruz
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