import streamlit as st
import pandas as pd
from bs4 import BeautifulSoup
import os
import streamlit.components.v1 as components

# ==========================================
# SAYFA AYARLARI
# ==========================================
st.set_page_config(page_title="Türkiye Seçim Simülatörü", layout="wide")

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
        file_path = os.path.join(current_dir, "ysk_2023_secim_verisi.csv")
        
        df = pd.read_csv(file_path)
        
        if 'DIGER' in df['party'].values:
            df = df[df['party'] != 'DIGER']
            df['base_vote_pct'] = df.groupby('district')['base_vote_pct'].transform(lambda x: (x / x.sum()) * 100)

        df['weighted_vote'] = df['base_vote_pct'] * df['seat_count']
        national_totals = df.groupby('party')['weighted_vote'].sum()
        total_seats = df.groupby('district')['seat_count'].first().sum()
        
        national_totals = national_totals / total_seats
        return df, national_totals.to_dict()
        
    except FileNotFoundError:
        st.error("🚨 HATA: 'ysk_2023_secim_verisi.csv' dosyası bulunamadı!")
        st.info("Lütfen CSV dosyanızın 'app.py' ile aynı klasörde bulunduğundan emin olun.")
        st.stop()

df_base, base_national_dict = load_base_data()

PARTIES = ['AKP', 'CHP', 'IYI', 'DEM', 'MHP', 'YRP', 'TIP', 'ZAFER']
PARTIES = [p for p in PARTIES if p in base_national_dict]

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
# 3. SVG HARİTA MOTORU (Izgara Matris & Metropol Ölçeklendirmesi)
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
        
        # --- SORUNLU İLLER İÇİN MANUEL MÜDAHALE ---
        custom_positions = {
            'kars': (1935, 260),
            'tunceli': (1520, 460),
            'karaman': (830, 750),
            'ankara1': (750, 410),
            'konya': (730, 620),
            'izmir2': (80, 500),
            'elazig': (1510, 535),
            'malatya': (1350, 540),
            'afyonkarahisar': (510, 525),
            'erzincan': (1510, 370),
            'burdur': (455, 705),
            'bursa2': (390, 260),
            'bursa1': (310, 310),
            'ordu': (1310, 190),
            'adana': (1060, 740),
            'giresun': (1415, 210),
            'osmaniye': (1155, 745),
            'ankara3': (690, 300),
            'ankara2': (790, 300),
            'agri': (1925, 375),
            'kayseri': (1100, 525),
            'sakarya': (510, 215),
            'gaziantep': (1300, 760),
            'denizli': (370, 670),
        }
        
        for path in paths:
            raw_id = path.get('id') or path.get('name') or path.get('data-name') or path.get('title') or ""
            svg_id_norm = normalize_id(raw_id)
            
            if not svg_id_norm:
                continue
                
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
                            'class': 'badge-group', 
                            'data-path-id': svg_id_norm,
                            'data-manual-x': str(man_x),
                            'data-manual-y': str(man_y)
                        })
                        
                        # --- METROPOL TESPİTİ VE ÖLÇEKLENDİRME ---
                        is_metro = any(m in svg_id_norm for m in ['istanbul'])
                        
                        # Metropollerde daha küçük, diğer illerde standart boyut
                        r_val = '9.5' if is_metro else '15'
                        f_size = '9px' if is_metro else '16px'
                        y_offset = 3 if is_metro else 4.5
                        spacing_x = 21 if is_metro else 32
                        spacing_y = 21 if is_metro else 32
                        
                        # --- IZGARA (GRID) DİZİLİM MANTIĞI ---
                        cols = 2 if len(sorted_winners) > 2 else len(sorted_winners)
                        rows = (len(sorted_winners) + cols - 1) // cols
                        base_start_y = -((rows - 1) * spacing_y) / 2
                        
                        for i, (party_name, seat_num) in enumerate(sorted_winners):
                            p_color = party_colors.get(party_name, '#333333')
                            
                            row_idx = i // cols
                            col_idx = i % cols
                            
                            # O satırda kaç rozet olduğunu bulup merkezliyoruz (Örn: Alt satırda 1 rozet varsa tam ortaya koy)
                            items_in_this_row = cols if row_idx < rows - 1 else (len(sorted_winners) - (rows - 1) * cols)
                            start_x = -((items_in_this_row - 1) * spacing_x) / 2
                            
                            current_x = start_x + (col_idx * spacing_x)
                            current_y = base_start_y + (row_idx * spacing_y)
                            
                            circle = soup.new_tag('circle', cx=str(current_x), cy=str(current_y), r=r_val, fill=p_color, stroke='#ffffff', **{'stroke-width': '1.5'})
                            city_badge_g.append(circle)
                            
                            text = soup.new_tag('text', x=str(current_x), y=str(current_y + y_offset), **{
                                'text-anchor': 'middle',
                                'fill': '#ffffff',
                                'font-size': f_size,
                                'font-family': 'Segoe UI, sans-serif',
                                'font-weight': 'bold',
                                'pointer-events': 'none'
                            })
                            text.string = str(seat_num)
                            city_badge_g.append(text)
                            
                        badges_group.append(city_badge_g)
                        
        if badges_group:
            svg_tag.append(badges_group)
                
        css_style = "<style>body{margin:0;background-color:transparent;display:flex;justify-content:center;}.map-container{position:relative;width:100%;max-width:950px;min-height:550px;display:flex;justify-content:center;}.map-path{cursor:pointer;transition:opacity 0.2s;}.map-path:hover{opacity:0.8;stroke:#000;stroke-width:2px;}#svg-tooltip{position:absolute;display:none;background:white;border:1px solid #ccc;padding:10px 14px;box-shadow:0 4px 15px rgba(0,0,0,0.2);border-radius:6px;pointer-events:none;z-index:9999;font-family:'Segoe UI', Tahoma, sans-serif;font-size:13px;color:#333;min-width:190px;}.tip-header{font-weight:bold;font-size:14px;margin-bottom:6px;border-bottom:1px solid #eee;padding-bottom:4px;color:#111;}.tip-row{display:flex;align-items:center;margin-bottom:3px;}.tip-party{width:50px;font-weight:600;color:#333;}.tip-seat{background:#111;color:#fff;width:24px;text-align:center;font-weight:bold;font-size:11px;margin-right:6px;}.tip-bar-bg{flex-grow:1;background:#eee;height:12px;border-radius:2px;overflow:hidden;}.tip-bar-fill{height:100%;}.tip-pct{margin-left:6px;font-size:11px;color:#666;width:45px;text-align:right;} .badge-group { transition: transform 0.5s ease; opacity: 0; animation: fadeIn 0.5s forwards 0.2s; } @keyframes fadeIn { to { opacity: 1; } }</style>"
        
        js_script = """
        <script>
            document.addEventListener("DOMContentLoaded", function() {
                const paths = document.querySelectorAll('.map-path');
                const tooltip = document.getElementById('svg-tooltip');
                const wrapper = document.getElementById('map-wrapper');

                paths.forEach(path => {
                    path.addEventListener('mousemove', (e) => {
                        const tooltipData = path.getAttribute('data-tooltip');
                        if(tooltipData){
                            tooltip.innerHTML = tooltipData;
                            tooltip.style.display = 'block';
                            const rect = wrapper.getBoundingClientRect();
                            const tipRect = tooltip.getBoundingClientRect();
                            let x = e.clientX - rect.left + 15;
                            let y = e.clientY - rect.top + 15;
                            if(e.clientX - rect.left + tipRect.width + 25 > rect.width){ x = e.clientX - rect.left - tipRect.width - 15; }
                            if(e.clientY - rect.top + tipRect.height + 25 > rect.height){ y = e.clientY - rect.top - tipRect.height - 15; }
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

        complete_html = f"<!DOCTYPE html><html><head>{css_style}</head><body><div class='map-container' id='map-wrapper'><div id='svg-tooltip'></div>{str(svg_tag)}</div>{js_script}</body></html>"
        return complete_html
        
    except FileNotFoundError:
        return f"<div style='color:red;'><b>HATA:</b> '{svg_file_name}' dosyası bulunamadı!</div>"
    except Exception as e:
        return f"<div style='color:red;'>SVG Hatası: {str(e)}</div>"

# ==========================================
# 4. ARAYÜZ (UI) TASARIMI
# ==========================================
st.title("🗳️ Türkiye Seçim Simülatörü & İnteraktif Harita")

st.sidebar.header("Seçim Parametreleri")

threshold_input = st.sidebar.number_input("Ülke Barajı (%)", min_value=0.0, max_value=15.0, value=7.0, step=0.5)
st.sidebar.divider()

st.sidebar.subheader("🤝 İttifak Seçenekleri")
use_alliances = st.sidebar.checkbox("İttifak Sistemini Etkinleştir", value=True)

alliances = {}
if use_alliances:
    st.sidebar.markdown("**Ön Tanımlı İttifaklar:**")
    
    enable_cumhur = st.sidebar.checkbox("Cumhur İttifakı", value=True)
    if enable_cumhur:
        default_cumhur = [p for p in ['AKP', 'MHP'] if p in PARTIES]
        cumhur_parties = st.sidebar.multiselect("Cumhur İttifakı Üyeleri", PARTIES, default=default_cumhur, key="cumhur_parties")
        if cumhur_parties:
            alliances["Cumhur İttifakı"] = cumhur_parties
            
    enable_emek = st.sidebar.checkbox("Emek ve Özgürlük İttifakı", value=True)
    if enable_emek:
        default_emek = [p for p in ['DEM', 'TIP'] if p in PARTIES]
        emek_parties = st.sidebar.multiselect("Emek ve Özgürlük İttifakı Üyeleri", PARTIES, default=default_emek, key="emek_parties")
        if emek_parties:
            alliances["Emek ve Özgürlük İttifakı"] = emek_parties
        
    st.sidebar.markdown("**Özel İttifak Ekle:**")
    custom_aly_name = st.sidebar.text_input("İttifak Adı", placeholder="Örn: Alternatif Blok")
    
    assigned_parties = [p for parties in alliances.values() for p in parties]
    available_parties_for_custom = [p for p in PARTIES if p not in assigned_parties]
    
    custom_aly_parties = st.sidebar.multiselect("İttifak Üyesi Partiler", available_parties_for_custom, key="custom_aly_parties")
    
    if custom_aly_name and custom_aly_parties:
        alliances[custom_aly_name] = custom_aly_parties

st.sidebar.divider()
st.sidebar.markdown("**Ulusal Oy Oranları**")

custom_start_values = {
    'AKP': 29.0, 'CHP': 39.0, 'MHP': 7.0, 'DEM': 8.0, 
    'IYI': 5.0, 'YRP': 4.0, 'ZAFER': 3.0, 'TIP': 2.0
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

national_summary_df = pd.DataFrame(summary_data).sort_values(by=['Vekil', 'Normalize Oy (%)'], ascending=[False, False])

party_colors = {
    'AKP': '#FDA000', 'CHP': '#A7050E', 'MHP': '#137BBB', 
    'DEM': '#90268F', 'IYI': '#FFC107', 'YRP': '#009840', 
    'TIP': '#FF1D25', 'ZAFER': '#474647'
}

st.subheader(f"TBMM Sandalye Dağılımı (Toplam {national_summary_df['Vekil'].sum()} Vekil)")

html_blocks = ["""
<style>
.custom-row { display: flex; align-items: center; margin-bottom: 6px; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
.custom-party { width: 110px; text-align: right; padding-right: 12px; font-weight: 600; color: #555; font-size: 15px; }
.custom-seat { background-color: #111; color: white; font-weight: bold; width: 45px; text-align: center; padding: 6px 0; font-size: 15px; margin-right: 10px; }
.custom-bar-bg { flex-grow: 1; background-color: #f7f7f7; height: 34px; overflow: hidden; display: flex; box-shadow: inset 0 1px 3px rgba(0,0,0,0.05); }
.custom-bar-fill { height: 100%; display: flex; align-items: center; padding-left: 8px; color: white; font-weight: 700; font-size: 14px; transition: width 0.5s ease-in-out; white-space: nowrap; }
</style>
<div style="max-width: 900px; margin: 10px 0 30px 0;">
"""]

for index, row in national_summary_df.iterrows():
    party = row['Parti']
    seats = int(row['Vekil'])
    vote_pct = row['Normalize Oy (%)']
    color = party_colors.get(party, "#888888")
    
    width = vote_pct
    html_blocks.append(f'<div class="custom-row"><div class="custom-party">{party}</div><div class="custom-seat">{seats}</div><div class="custom-bar-bg"><div class="custom-bar-fill" style="width: {width}%; background-color: {color}; min-width: 60px;">%{vote_pct:.2f}</div></div></div>')
    
html_blocks.append("</div>")
st.markdown("".join(html_blocks), unsafe_allow_html=True)
st.divider()

# --- SVG HARİTA BÖLÜMÜ ---
st.subheader("🗺️ İl ve Bölge Bazında Birinci Partiler (SVG)")

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
    dist_norm = normalize_id(dist)
    tooltip_dict[dist_norm] = create_tooltip_html(f"📌 {dist}", group)

for prov, group in df_results.groupby('province'):
    prov_norm = normalize_id(prov)
    prov_agg = group.groupby('party').agg({'new_vote_pct': 'mean', 'seats_won': 'sum'}).reset_index()
    tooltip_dict[prov_norm] = create_tooltip_html(f"📌 {prov}", prov_agg)

district_seats_data = df_results.groupby(['district', 'party'])['seats_won'].sum().to_dict()

colored_svg_html = render_colored_svg(
    prov_winners_dict, 
    dist_winners_dict, 
    party_colors, 
    tooltip_dict, 
    district_seats_data,  
    svg_file_name="turkiye.svg"
)

components.html(colored_svg_html, height=620, scrolling=False)
st.divider()

# --- TABLO BÖLÜMÜ ---
st.subheader("📍 87 Seçim Çevresine Göre İl İl Dağılım Tablosu")
pivot_df = df_results.pivot(index='district', columns='party', values=['new_vote_pct', 'seats_won'])

kazanan_partiler = national_summary_df[national_summary_df['Vekil'] > 0]['Parti'].values

display_df = pd.DataFrame()
for p in PARTIES:
    if p in kazanan_partiler:
        display_df[f"{p} (%)"] = pivot_df['new_vote_pct'][p].round(1)
        display_df[f"{p} (Vekil)"] = pivot_df['seats_won'][p].astype(int)

def highlight_first_party(row):
    styles = [''] * len(row)
    vote_cols = [col for col in row.index if '(%)' in col]
    if not vote_cols:
        return styles
    
    max_val = -1
    best_col = None
    for col in vote_cols:
        val = row[col]
        if val > max_val:
            max_val = val
            best_col = col
            
    if best_col:
        party_name = best_col.split(' ')[0]
        color = party_colors.get(party_name, '#CCCCCC')
        
        for i, col in enumerate(row.index):
            if col.startswith(party_name):
                styles[i] = f'background-color: {color}; color: white; font-weight: bold;'
                
    return styles

styled_table = display_df.style.apply(highlight_first_party, axis=1).format(
    lambda x: f"%{x:.1f}" if isinstance(x, float) else x
)

st.dataframe(styled_table, use_container_width=True)