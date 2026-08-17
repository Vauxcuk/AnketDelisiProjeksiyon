import streamlit as st
import pandas as pd
from bs4 import BeautifulSoup
import os

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
        # app.py dosyasının bulunduğu klasörün yolunu tam olarak alır
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
# 2. HESAPLAMA MOTORU (D'Hondt & Swing)
# ==========================================
def calculate_dhondt(votes_dict, seat_count):
    seats_won = {p: 0 for p in votes_dict}
    divisors = {p: 1 for p in votes_dict}
    for _ in range(seat_count):
        winner = max(votes_dict.keys(), key=lambda p: votes_dict[p] / divisors[p])
        seats_won[winner] += 1
        divisors[winner] += 1
    return seats_won

def run_simulation(base_df, base_nat, user_nat, threshold=7.0):
    qualified_parties = [p for p, v in user_nat.items() if v >= threshold]
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
# 3. SVG HARİTA MOTORU (Mutlak Yol Desteğiyle)
# ==========================================
def render_colored_svg(prov_winners, dist_winners, party_colors, tooltip_dict, svg_file_name="turkiye.svg"):
    try:
        # app.py dosyasının bulunduğu klasörün yolunu tam olarak alıyoruz
        current_dir = os.path.dirname(os.path.abspath(__file__))
        svg_file_path = os.path.join(current_dir, svg_file_name)
        
        with open(svg_file_path, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f.read(), 'html.parser')
            
        svg_tag = soup.find('svg') or soup.find('svg:svg')
        
        if svg_tag:
            svg_tag['width'] = "100%"
            svg_tag['height'] = "100%"
            
        paths = soup.find_all('path')
        
        for path in paths:
            raw_id = path.get('id') or path.get('name') or path.get('data-name') or path.get('title') or ""
            svg_id_norm = normalize_id(raw_id)
            
            if not svg_id_norm:
                continue
                
            winning_party = None
            if svg_id_norm in dist_winners:
                winning_party = dist_winners[svg_id_norm]
            elif svg_id_norm in prov_winners:
                winning_party = prov_winners[svg_id_norm]
                
            if winning_party:
                color = party_colors.get(winning_party, "#CCCCCC")
                
                if 'style' in path.attrs:
                    style_str = path['style']
                    style_dict = {}
                    for item in style_str.split(';'):
                        if ':' in item:
                            key, val = item.split(':', 1)
                            style_dict[key.strip()] = val.strip()
                            
                    style_dict['fill'] = color
                    path['style'] = ';'.join([f"{k}:{v}" for k, v in style_dict.items()])
                else:
                    path['fill'] = color
                    
                hover_text = tooltip_dict.get(svg_id_norm, f"{raw_id} - 1. Parti: {winning_party}")
                
                if path.find('title'):
                    path.title.decompose()
                    
                new_title = soup.new_tag('title')
                new_title.string = hover_text
                path.append(new_title)
                    
        return str(svg_tag)
    except FileNotFoundError:
        return f"<div style='color:red;'><b>HATA:</b> '{svg_file_name}' dosyası app.py ile aynı klasörde bulunamadı!</div>"
    except Exception as e:
        return f"<div style='color:red;'>SVG Hatası: {str(e)}</div>"

# ==========================================
# 4. ARAYÜZ (UI) TASARIMI
# ==========================================
st.title("🗳️ Türkiye Seçim Simülatörü & İnteraktif Harita")

st.sidebar.header("Seçim Parametreleri")

threshold_input = st.sidebar.number_input("Ülke Barajı (%)", min_value=0.0, max_value=15.0, value=7.0, step=0.5)
st.sidebar.divider()
st.sidebar.markdown("**Ulusal Oy Oranları**")

# Kendi belirlediğin başlangıç oy oranları (buradan dilediğin gibi değiştirebilirsin)
custom_start_values = {
    'AKP': 29.0,
    'CHP': 39.0,
    'MHP': 7.0,
    'DEM': 8.0,
    'IYI': 5.0,
    'YRP': 4.0,
    'ZAFER': 3.0,
    'TIP': 2.0
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

# Hataya sebep olan değişken burada tanımlanıyor:
user_inputs_norm = {p: (v / total_input) * 100 if total_input > 0 else 0 for p, v in user_inputs.items()}

# Hesaplama Motorunu Çalıştır
df_results = run_simulation(df_base, base_national_dict, user_inputs_norm, threshold=threshold_input)
# --- DETAYLI ULUSAL ÖZET TABLOSU (ÖZEL TASARIM) ---
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
    
    # Markdown'un "Kod Bloğu" sanmasını engellemek için HTML'i tek bir satırda, boşluksuz yazıyoruz
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

for dist, group in df_results.groupby('district'):
    dist_norm = normalize_id(dist)
    sorted_group = group.sort_values(by='new_vote_pct', ascending=False)
    
    lines = [f"📌 Seçim Çevresi: {dist}", "-" * 20]
    for _, row in sorted_group.iterrows():
        if row['new_vote_pct'] > 0:
            vekil_metni = f"({row['seats_won']} Vekil)" if row['seats_won'] > 0 else ""
            lines.append(f"{row['party']}: %{row['new_vote_pct']:.1f} {vekil_metni}")
            
    tooltip_dict[dist_norm] = "\n".join(lines)

for prov, group in df_results.groupby('province'):
    prov_norm = normalize_id(prov)
    prov_agg = group.groupby('party').agg({'new_vote_pct': 'mean', 'seats_won': 'sum'}).reset_index()
    sorted_agg = prov_agg.sort_values(by='new_vote_pct', ascending=False)
    
    lines = [f"📌 İl: {prov}", "-" * 20]
    for _, row in sorted_agg.iterrows():
        if row['new_vote_pct'] > 0:
            vekil_metni = f"({row['seats_won']} Vekil)" if row['seats_won'] > 0 else ""
            lines.append(f"{row['party']}: %{row['new_vote_pct']:.1f} {vekil_metni}")
            
    tooltip_dict[prov_norm] = "\n".join(lines)

colored_svg_html = render_colored_svg(prov_winners_dict, dist_winners_dict, party_colors, tooltip_dict, svg_file_name="turkiye.svg")

st.markdown(f"<div style='display:flex; justify-content:center; width:100%; margin-bottom: 20px;'>{colored_svg_html}</div>", unsafe_allow_html=True)

st.divider()

# --- TABLO BÖLÜMÜ ---
st.subheader("📍 87 Seçim Çevresine Göre İl İl Dağılım Tablosu")
pivot_df = df_results.pivot(index='district', columns='party', values=['new_vote_pct', 'seats_won'])

# Sadece ülke genelinde en az 1 vekil çıkaran partileri tabloda göstermek için listeyi güncelledik
kazanan_partiler = national_summary_df[national_summary_df['Vekil'] > 0]['Parti'].values

display_df = pd.DataFrame()
for p in PARTIES:
    if p in kazanan_partiler:
        display_df[f"{p} (%)"] = pivot_df['new_vote_pct'][p].round(1)
        display_df[f"{p} (Vekil)"] = pivot_df['seats_won'][p].astype(int)

st.dataframe(display_df, use_container_width=True)