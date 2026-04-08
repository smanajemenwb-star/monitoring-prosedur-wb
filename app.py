import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os

st.set_page_config(
    page_title="Monitoring Prosedur – WIKA Beton",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    .main { background-color: #f8f9fb; }
    .block-container { padding: 1.5rem 2rem; }
    .kpi-card {
        background: white; border-radius: 12px;
        padding: 1.1rem 1.2rem;
        box-shadow: 0 1px 4px rgba(0,0,0,0.08);
        border-left: 5px solid #ccc; margin-bottom: 0.5rem;
    }
    .kpi-label { font-size: 0.72rem; color: #888; font-weight: 600;
                 text-transform: uppercase; letter-spacing: 0.05em; }
    .kpi-value { font-size: 2.2rem; font-weight: 700; line-height: 1.1; }
    .kpi-sub   { font-size: 0.75rem; color: #666; margin-top: 2px; }
    .kpi-blue   { border-color: #2E75B6; } .kpi-blue   .kpi-value { color: #2E75B6; }
    .kpi-green  { border-color: #375623; } .kpi-green  .kpi-value { color: #375623; }
    .kpi-red    { border-color: #9C0006; } .kpi-red    .kpi-value { color: #9C0006; }
    .kpi-orange { border-color: #B26800; } .kpi-orange .kpi-value { color: #B26800; }
    .alert-box {
        background: #fff3cd; border: 1px solid #ffc107;
        border-radius: 8px; padding: 0.7rem 1rem; margin: 0.3rem 0;
    }
    .alert-box-red {
        background: #fde8e8; border: 1px solid #f87171;
        border-radius: 8px; padding: 0.7rem 1rem; margin: 0.3rem 0;
    }
    .section-title {
        font-size: 0.8rem; font-weight: 600; color: #2E75B6;
        text-transform: uppercase; letter-spacing: 0.06em;
        border-left: 3px solid #2E75B6; padding-left: 8px;
        margin: 1.2rem 0 0.6rem;
    }
</style>
""", unsafe_allow_html=True)


# ── Load data ─────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    path = os.path.join(os.path.dirname(__file__), 'data.csv')
    df = pd.read_csv(path)
    df['sisa'] = pd.to_numeric(df['sisa'], errors='coerce').fillna(0).astype(int)
    df['Keterangan'] = df['Keterangan'].str.strip()
    df['Divisi Pemilik Proses'] = df['Divisi Pemilik Proses'].fillna('Tidak Diketahui').str.strip()
    df['Nama Prosedur'] = df['Nama Prosedur'].str.strip()
    df['Nomor Prosedur'] = df['Nomor Prosedur'].str.strip()
    df['Tgl_Berlaku_dt'] = pd.to_datetime(df['Tgl Berlaku'], errors='coerce', dayfirst=True)
    df['Tgl_Review_dt']  = pd.to_datetime(df['Tgl Review'],  errors='coerce', dayfirst=True)
    return df

df = load_data()
today = datetime.today()


# ── Helpers ───────────────────────────────────────────────────────────────────
def shorten_div(s):
    return (str(s)
            .replace('DIVISI ', '')
            .replace('SEKRETARIAT PERUSAHAAN', 'SEKRETARIAT')
            .replace('SATUAN PENGAWASAN INTERNAL', 'SPI'))

def color_row(row, warn_days=90, crit_days=30):
    ket  = row.get('Keterangan', '')
    sisa = row.get('Sisa Hari', row.get('sisa', 9999))
    styles = []
    for col in row.index:
        if col == 'Keterangan':
            if ket == 'Berlaku' and sisa > warn_days:
                s = 'background-color:#e2efda;color:#375623;font-weight:bold'
            elif ket == 'Berlaku':
                s = 'background-color:#fff3cd;color:#7D4E00;font-weight:bold'
            else:
                s = 'background-color:#ffc7ce;color:#9C0006;font-weight:bold'
        elif col == 'Sisa Hari':
            if sisa < 0:
                s = 'color:#9C0006;font-weight:bold'
            elif sisa <= crit_days:
                s = 'color:#9C0006;font-weight:bold;background-color:#fde8e8'
            elif sisa <= warn_days:
                s = 'color:#7D4E00;font-weight:bold;background-color:#fff3cd'
            else:
                s = 'color:#375623'
        else:
            if ket == 'Tidak Berlaku':
                s = 'background-color:#fff5f5'
            elif sisa <= crit_days and ket == 'Berlaku':
                s = 'background-color:#fff5f5'
            elif sisa <= warn_days and ket == 'Berlaku':
                s = 'background-color:#fffdf0'
            else:
                s = ''
        styles.append(s)
    return styles

def highlight_pct(row):
    styles = []
    for col in row.index:
        if col == '% Berlaku':
            v = row[col]
            if v == 100:
                styles.append('background-color:#e2efda;color:#375623;font-weight:bold')
            elif v < 70:
                styles.append('background-color:#ffc7ce;color:#9C0006;font-weight:bold')
            else:
                styles.append('')
        elif col == 'Tidak Berlaku' and row[col] > 0:
            styles.append('color:#9C0006;font-weight:bold')
        else:
            styles.append('')
    return styles

def kpi(col, label, value, sub, cls):
    col.markdown(f"""<div class="kpi-card {cls}">
<div class="kpi-label">{label}</div>
<div class="kpi-value">{value}</div>
<div class="kpi-sub">{sub}</div>
</div>""", unsafe_allow_html=True)

def section(text):
    st.markdown(f'<div class="section-title">{text}</div>', unsafe_allow_html=True)


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📋 Monitoring Prosedur")
    st.markdown("**PT Wijaya Karya Beton Tbk**")
    st.markdown(f"Update: 9 Maret 2026  \nDivisi: DSIM  \nTanggal: {today.strftime('%d %b %Y')}")
    st.divider()

    st.markdown("#### 🔍 Filter Data")
    sel_div = st.selectbox("Divisi",
        ['Semua Divisi'] + sorted(df['Divisi Pemilik Proses'].unique().tolist()))
    sel_kat = st.selectbox("Kategori",
        ['Semua Kategori'] + sorted(df['Kategori'].unique().tolist()))
    sel_sts = st.multiselect("Status", ['Berlaku', 'Tidak Berlaku'],
                              default=['Berlaku', 'Tidak Berlaku'])

    st.divider()
    st.markdown("#### ⚙️ Pengaturan")
    warn_days = st.slider("Threshold peringatan (hari)", 30, 180, 90, step=10)
    crit_days = st.slider("Threshold kritis (hari)", 10, 60, 30, step=5)

    st.divider()
    st.download_button("⬇ Download CSV",
        df.to_csv(index=False).encode('utf-8'),
        "monitoring_prosedur.csv", "text/csv")


# ── Filter ────────────────────────────────────────────────────────────────────
dff = df.copy()
if sel_div != 'Semua Divisi':
    dff = dff[dff['Divisi Pemilik Proses'] == sel_div]
if sel_kat != 'Semua Kategori':
    dff = dff[dff['Kategori'] == sel_kat]
if sel_sts:
    dff = dff[dff['Keterangan'].isin(sel_sts)]

total  = len(dff)
berl   = int((dff['Keterangan'] == 'Berlaku').sum())
tidak  = total - berl
warn_n = int(((dff['Keterangan'] == 'Berlaku') & (dff['sisa'] <= warn_days)).sum())
krit_n = int(((dff['Keterangan'] == 'Berlaku') & (dff['sisa'] <= crit_days)).sum())
pct_b  = round(berl / total * 100, 1) if total > 0 else 0


# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style='background:linear-gradient(90deg,#1F3864,#2E75B6);
padding:1rem 1.5rem;border-radius:12px;margin-bottom:1rem'>
<div style='color:white;font-size:1.4rem;font-weight:700'>
PT WIJAYA KARYA BETON Tbk</div>
<div style='color:#BDD7EE;font-size:0.85rem;margin-top:4px'>
DASHBOARD MONITORING DAFTAR INDUK DOKUMEN SISTEM MANAJEMEN &nbsp;|&nbsp;
DSIM – Kantor Pusat &nbsp;|&nbsp; Form: WB-QMS-PS-01-F08 Rev.02</div>
</div>
""", unsafe_allow_html=True)

# ── KPI ───────────────────────────────────────────────────────────────────────
c1, c2, c3, c4, c5 = st.columns(5)
kpi(c1, "Total Prosedur",          total,  "data per 9 Maret 2026",              "kpi-blue")
kpi(c2, "Berlaku",                  berl,   f"{pct_b}% dari total",               "kpi-green")
kpi(c3, "Tidak Berlaku",            tidak,  f"{round(tidak/total*100,1) if total else 0}% perlu diperbarui", "kpi-red")
kpi(c4, f"Segera ≤{warn_days}hr",  warn_n, "perlu segera ditindaklanjuti",        "kpi-orange")
kpi(c5, f"Kritis ≤{crit_days}hr",  krit_n, "harus diperbarui sekarang!",          "kpi-red")

st.markdown("<br>", unsafe_allow_html=True)

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📊 Grafik Utama",
    "🔬 Grafik Lanjutan",
    "📋 Tabel Lengkap",
    "⚠️ Peringatan Expired",
    "🏢 Per Divisi",
    "🗂️ Per Kategori",
])


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1 – GRAFIK UTAMA
# ═══════════════════════════════════════════════════════════════════════════════
with tab1:

    # ── Gauge + Donut ──────────────────────────────────────────────────────────
    section("Komposisi & Persentase Status")
    g1, g2 = st.columns(2)

    with g1:
        st.markdown("##### Gauge — % Prosedur Berlaku")
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=pct_b,
            delta={"reference": 80, "suffix": "%"},
            title={"text": "% Berlaku", "font": {"size": 15}},
            number={"suffix": "%", "font": {"size": 48}},
            gauge={
                "axis": {"range": [0, 100], "tickwidth": 1, "tickcolor": "#666"},
                "bar": {"color": "#70AD47", "thickness": 0.25},
                "bgcolor": "white",
                "borderwidth": 0,
                "steps": [
                    {"range": [0, 60],  "color": "#FFE0E0"},
                    {"range": [60, 80], "color": "#FFF2CC"},
                    {"range": [80, 100],"color": "#E2EFDA"},
                ],
                "threshold": {
                    "line": {"color": "#1F3864", "width": 3},
                    "thickness": 0.8,
                    "value": 80,
                },
            },
        ))
        fig_gauge.update_layout(
            height=280, margin=dict(t=60, b=20, l=30, r=30),
            paper_bgcolor="rgba(0,0,0,0)", font={"color": "#1F3864"},
        )
        st.plotly_chart(fig_gauge, use_container_width=True)

    with g2:
        st.markdown("##### Donut — Komposisi Status")
        pie_data = dff['Keterangan'].value_counts().reset_index()
        pie_data.columns = ['Status', 'Jumlah']
        fig_pie = px.pie(
            pie_data, values='Jumlah', names='Status', hole=0.55,
            color='Status',
            color_discrete_map={'Berlaku': '#70AD47', 'Tidak Berlaku': '#FF4444'},
        )
        fig_pie.update_traces(textposition='outside', textinfo='label+percent+value',
                              textfont_size=12)
        fig_pie.update_layout(
            height=280, margin=dict(t=20, b=30, l=10, r=10),
            legend=dict(orientation='h', y=-0.15, x=0.5, xanchor='center'),
            paper_bgcolor='rgba(0,0,0,0)',
            annotations=[dict(text=f'<b>{total}</b><br>Total', x=0.5, y=0.5,
                              font_size=14, showarrow=False)],
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    # ── Bar per Divisi ─────────────────────────────────────────────────────────
    section("Status per Divisi & Kategori")
    b1, b2 = st.columns([1.6, 1])

    with b1:
        st.markdown("##### Stacked Bar — Status per Divisi")
        div_grp = (dff.groupby('Divisi Pemilik Proses')
                   .apply(lambda g: pd.Series({
                       'Berlaku':       int((g['Keterangan'] == 'Berlaku').sum()),
                       'Tidak Berlaku': int((g['Keterangan'] == 'Tidak Berlaku').sum()),
                       'Total': len(g),
                   }), include_groups=False)
                   .reset_index().sort_values('Total', ascending=True))
        div_grp['Label'] = div_grp['Divisi Pemilik Proses'].apply(shorten_div)

        fig_bar = go.Figure()
        fig_bar.add_trace(go.Bar(y=div_grp['Label'], x=div_grp['Berlaku'],
            name='Berlaku', orientation='h', marker_color='#70AD47',
            text=div_grp['Berlaku'], textposition='inside'))
        fig_bar.add_trace(go.Bar(y=div_grp['Label'], x=div_grp['Tidak Berlaku'],
            name='Tidak Berlaku', orientation='h', marker_color='#FF6B6B',
            text=div_grp['Tidak Berlaku'].apply(lambda x: str(x) if x > 0 else ''),
            textposition='inside'))
        fig_bar.update_layout(
            barmode='stack', height=360,
            margin=dict(t=10, b=10, l=10, r=40),
            legend=dict(orientation='h', y=1.05, x=0.5, xanchor='center'),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(showgrid=True, gridcolor='#eee'),
            yaxis=dict(tickfont=dict(size=10)),
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with b2:
        st.markdown("##### Bar — Jumlah per Kategori")
        kat_grp = (dff.groupby('Kategori')
                   .apply(lambda g: pd.Series({
                       'Berlaku':       int((g.Keterangan == 'Berlaku').sum()),
                       'Tidak Berlaku': int((g.Keterangan == 'Tidak Berlaku').sum()),
                   }), include_groups=False)
                   .reset_index().sort_values('Berlaku', ascending=False))
        fig_kat = go.Figure()
        fig_kat.add_trace(go.Bar(x=kat_grp['Kategori'], y=kat_grp['Berlaku'],
            name='Berlaku', marker_color='#70AD47'))
        fig_kat.add_trace(go.Bar(x=kat_grp['Kategori'], y=kat_grp['Tidak Berlaku'],
            name='Tidak Berlaku', marker_color='#FF6B6B'))
        fig_kat.update_layout(
            barmode='stack', height=360,
            margin=dict(t=10, b=10, l=10, r=10),
            legend=dict(orientation='h', y=1.05, x=0.5, xanchor='center'),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(tickangle=45), yaxis=dict(showgrid=True, gridcolor='#eee'),
        )
        st.plotly_chart(fig_kat, use_container_width=True)

    # ── % per Divisi Bullet ────────────────────────────────────────────────────
    section("Pencapaian Target Berlaku per Divisi")
    st.markdown("##### Bullet Chart — % Berlaku vs Target 80%")

    div_pct = (dff.groupby('Divisi Pemilik Proses')
               .apply(lambda g: round((g.Keterangan == 'Berlaku').sum() / len(g) * 100, 1),
                      include_groups=False)
               .reset_index())
    div_pct.columns = ['Divisi', '% Berlaku']
    div_pct['Label'] = div_pct['Divisi'].apply(shorten_div)
    div_pct = div_pct.sort_values('% Berlaku', ascending=True)

    fig_bullet = go.Figure()
    for _, row in div_pct.iterrows():
        color = '#70AD47' if row['% Berlaku'] >= 80 else '#FFC107' if row['% Berlaku'] >= 60 else '#FF4444'
        fig_bullet.add_trace(go.Bar(
            y=[row['Label']], x=[row['% Berlaku']],
            orientation='h', marker_color=color,
            text=f"{row['% Berlaku']}%", textposition='outside',
            showlegend=False,
        ))
    fig_bullet.add_vline(x=80, line_dash='dash', line_color='#1F3864', line_width=2,
                         annotation_text='Target 80%', annotation_position='top right',
                         annotation=dict(font=dict(size=10, color='#1F3864')))
    fig_bullet.update_layout(
        height=340, margin=dict(t=30, b=10, l=10, r=60),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(range=[0, 115], ticksuffix='%', showgrid=True, gridcolor='#eee'),
        yaxis=dict(tickfont=dict(size=10)),
        barmode='overlay',
    )
    st.plotly_chart(fig_bullet, use_container_width=True)


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2 – GRAFIK LANJUTAN
# ═══════════════════════════════════════════════════════════════════════════════
with tab2:

    # ── Sunburst ───────────────────────────────────────────────────────────────
    section("Hierarki Drill-Down")
    s1, s2 = st.columns(2)

    with s1:
        st.markdown("##### Sunburst — Divisi › Kategori › Status")
        fig_sun = px.sunburst(
            dff,
            path=['Divisi Pemilik Proses', 'Kategori', 'Keterangan'],
            color='Keterangan',
            color_discrete_map={'Berlaku': '#70AD47', 'Tidak Berlaku': '#FF4444', '(?)': '#ccc'},
        )
        fig_sun.update_traces(
            textinfo='label+percent parent',
            insidetextorientation='radial',
        )
        fig_sun.update_layout(
            height=460, margin=dict(t=20, b=10, l=10, r=10),
            paper_bgcolor='rgba(0,0,0,0)',
        )
        st.plotly_chart(fig_sun, use_container_width=True)

    with s2:
        st.markdown("##### Treemap — Kategori › Status")
        tree_df = dff.groupby(['Kategori', 'Keterangan']).size().reset_index(name='Jumlah')
        fig_tree = px.treemap(
            tree_df, path=['Kategori', 'Keterangan'], values='Jumlah',
            color='Keterangan',
            color_discrete_map={'Berlaku': '#70AD47', 'Tidak Berlaku': '#FF4444'},
        )
        fig_tree.update_traces(textinfo='label+value+percent parent')
        fig_tree.update_layout(
            height=460, margin=dict(t=20, b=10, l=10, r=10),
            paper_bgcolor='rgba(0,0,0,0)',
        )
        st.plotly_chart(fig_tree, use_container_width=True)

    # ── Polar Bar ──────────────────────────────────────────────────────────────
    section("Distribusi Polar & Scatter Urgensi")
    p1, p2 = st.columns(2)

    with p1:
        st.markdown("##### Polar Bar — Distribusi per Kategori")
        kat_pol = (dff.groupby('Kategori')
                   .apply(lambda g: pd.Series({
                       'Berlaku':       int((g.Keterangan == 'Berlaku').sum()),
                       'Tidak Berlaku': int((g.Keterangan == 'Tidak Berlaku').sum()),
                   }), include_groups=False)
                   .reset_index())
        fig_polar = go.Figure()
        fig_polar.add_trace(go.Barpolar(
            r=kat_pol['Berlaku'], theta=kat_pol['Kategori'],
            name='Berlaku', marker_color='#70AD47',
            marker_line_color='#375623', marker_line_width=1, opacity=0.9,
        ))
        fig_polar.add_trace(go.Barpolar(
            r=kat_pol['Tidak Berlaku'], theta=kat_pol['Kategori'],
            name='Tidak Berlaku', marker_color='#FF6B6B',
            marker_line_color='#9C0006', marker_line_width=1, opacity=0.9,
        ))
        fig_polar.update_layout(
            height=420,
            polar=dict(
                radialaxis=dict(visible=True,
                                range=[0, kat_pol['Berlaku'].max() + 2]),
                angularaxis=dict(tickfont=dict(size=10)),
            ),
            legend=dict(orientation='h', y=-0.1, x=0.5, xanchor='center'),
            paper_bgcolor='rgba(0,0,0,0)',
        )
        st.plotly_chart(fig_polar, use_container_width=True)

    with p2:
        st.markdown("##### Scatter — Peta Urgensi Review")
        berl_sc = dff[dff.Keterangan == 'Berlaku'].copy()
        berl_sc['Urgensi'] = berl_sc['sisa'].apply(
            lambda x: 'Kritis' if x <= crit_days
            else 'Segera' if x <= warn_days else 'Aman')
        berl_sc['Label'] = berl_sc['Divisi Pemilik Proses'].apply(shorten_div)
        berl_sc['size_val'] = berl_sc['sisa'].apply(lambda x: max(5, min(30, x / 30)))

        fig_sc = px.scatter(
            berl_sc, x='sisa', y='Label', color='Urgensi',
            size='size_val', size_max=22,
            color_discrete_map={'Kritis': '#FF4444', 'Segera': '#FFC107', 'Aman': '#70AD47'},
            hover_data=['Nomor Prosedur', 'Nama Prosedur', 'Tgl Review'],
            labels={'sisa': 'Sisa Hari', 'Label': 'Divisi'},
        )
        fig_sc.add_vline(x=crit_days, line_dash='dash', line_color='red',
                         annotation_text=f'{crit_days}hr')
        fig_sc.add_vline(x=warn_days, line_dash='dash', line_color='orange',
                         annotation_text=f'{warn_days}hr')
        fig_sc.update_layout(
            height=420, margin=dict(t=20, b=10, l=10, r=10),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(showgrid=True, gridcolor='#eee'),
            yaxis=dict(tickfont=dict(size=10)),
            legend=dict(orientation='h', y=1.05, x=0.5, xanchor='center'),
        )
        st.plotly_chart(fig_sc, use_container_width=True)

    # ── Heatmap ────────────────────────────────────────────────────────────────
    section("Heatmap Kalender Expired")
    st.markdown("##### Heatmap — Jumlah Prosedur Expire per Bulan & Divisi")

    df_ht = dff.copy()
    df_ht = df_ht.dropna(subset=['Tgl_Review_dt'])
    df_ht['Bulan'] = df_ht['Tgl_Review_dt'].dt.strftime('%Y-%m')
    df_ht['Bulan_lbl'] = df_ht['Tgl_Review_dt'].dt.strftime('%b %Y')
    df_ht['Div_s'] = df_ht['Divisi Pemilik Proses'].apply(shorten_div)

    if len(df_ht) > 0:
        pivot = (df_ht.groupby(['Div_s', 'Bulan_lbl'])
                 .size().unstack(fill_value=0))
        pivot = pivot.reindex(
            columns=sorted(pivot.columns,
                           key=lambda x: pd.to_datetime(x, format='%b %Y', errors='coerce')))
        fig_heat = go.Figure(go.Heatmap(
            z=pivot.values,
            x=pivot.columns.tolist(),
            y=pivot.index.tolist(),
            colorscale=[
                [0,   '#E8F5E9'],
                [0.3, '#FFF9C4'],
                [0.7, '#FFE0B2'],
                [1,   '#FFCDD2'],
            ],
            text=pivot.values,
            texttemplate='%{text}',
            textfont={'size': 10},
            hoverongaps=False,
        ))
        fig_heat.update_layout(
            height=420, margin=dict(t=20, b=60, l=10, r=10),
            paper_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(tickangle=45, tickfont=dict(size=9)),
            yaxis=dict(tickfont=dict(size=9)),
        )
        st.plotly_chart(fig_heat, use_container_width=True)

    # ── Histogram + Waterfall ──────────────────────────────────────────────────
    section("Distribusi & Perubahan")
    w1, w2 = st.columns(2)

    with w1:
        st.markdown("##### Histogram — Distribusi Sisa Hari")
        berl_only = dff[dff['Keterangan'] == 'Berlaku']
        fig_hist = px.histogram(berl_only, x='sisa', nbins=20,
            color_discrete_sequence=['#2E75B6'],
            labels={'sisa': 'Sisa Hari', 'count': 'Jumlah Prosedur'})
        fig_hist.add_vline(x=warn_days, line_dash='dash', line_color='orange',
            annotation_text=f'{warn_days}hr', annotation_position='top right')
        fig_hist.add_vline(x=crit_days, line_dash='dash', line_color='red',
            annotation_text=f'{crit_days}hr', annotation_position='top left')
        fig_hist.add_vrect(x0=0, x1=crit_days,
            fillcolor='red', opacity=0.07, line_width=0)
        fig_hist.add_vrect(x0=crit_days, x1=warn_days,
            fillcolor='orange', opacity=0.07, line_width=0)
        fig_hist.update_layout(
            height=320, margin=dict(t=10, b=10, l=10, r=10),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(showgrid=True, gridcolor='#eee'),
            yaxis=dict(showgrid=True, gridcolor='#eee'),
        )
        st.plotly_chart(fig_hist, use_container_width=True)

    with w2:
        st.markdown("##### Waterfall — Perubahan Jumlah Prosedur")
        fig_wf = go.Figure(go.Waterfall(
            name="Perubahan",
            orientation="v",
            measure=["absolute", "relative", "relative", "relative", "total"],
            x=["Sep 2025", "Dihapus", "Diperpanjang", "Baru Expired", "Mar 2026"],
            y=[93, -4, 2, -5, 89],
            text=["93", "-4", "+2", "-5", "89"],
            textposition="outside",
            connector={"line": {"color": "#ccc"}},
            increasing={"marker": {"color": "#70AD47"}},
            decreasing={"marker": {"color": "#FF4444"}},
            totals={"marker": {"color": "#2E75B6",
                               "line": {"color": "#1F3864", "width": 2}}},
        ))
        fig_wf.update_layout(
            height=320, margin=dict(t=30, b=20, l=10, r=10),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            yaxis=dict(showgrid=True, gridcolor='#eee'),
            showlegend=False,
        )
        st.plotly_chart(fig_wf, use_container_width=True)




# ═══════════════════════════════════════════════════════════════════════════════
# TAB 3 – TABEL LENGKAP
# ═══════════════════════════════════════════════════════════════════════════════
with tab3:
    col_srch, col_cnt = st.columns([3, 1])
    with col_srch:
        search = st.text_input("🔍 Cari nomor / nama prosedur...",
                               placeholder="Ketik untuk mencari...")
    with col_cnt:
        st.metric("Ditampilkan", len(dff))

    tbl = dff.copy()
    if search:
        mask = (tbl['Nomor Prosedur'].str.contains(search, case=False, na=False) |
                tbl['Nama Prosedur'].str.contains(search, case=False, na=False))
        tbl = tbl[mask]

    tbl_show = (tbl[['No', 'Nomor Prosedur', 'Nama Prosedur', 'Rev', 'Kategori',
                      'Divisi Pemilik Proses', 'Tgl Berlaku', 'Tgl Review', 'sisa', 'Keterangan']]
                .rename(columns={'sisa': 'Sisa Hari'})
                .reset_index(drop=True))

    styled_tbl = tbl_show.style.apply(
        lambda row: color_row(row, warn_days, crit_days), axis=1)
    st.dataframe(styled_tbl, use_container_width=True, height=520)

    st.download_button("⬇ Download tabel ini",
                       tbl_show.to_csv(index=False).encode('utf-8'),
                       "filtered_data.csv", "text/csv")


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 4 – PERINGATAN EXPIRED
# ═══════════════════════════════════════════════════════════════════════════════
with tab4:
    exp_all = (dff[(dff['Keterangan'] == 'Berlaku') & (dff['sisa'] <= warn_days)]
               .sort_values('sisa').reset_index(drop=True))

    if len(exp_all) == 0:
        st.success(f"✅ Tidak ada prosedur yang akan expired dalam {warn_days} hari ke depan.")
    else:
        krit_df   = exp_all[exp_all['sisa'] <= crit_days]
        segera_df = exp_all[exp_all['sisa'] > crit_days]

        if len(krit_df) > 0:
            st.error(f"🚨 **{len(krit_df)} PROSEDUR KRITIS** — expired dalam {crit_days} hari atau kurang!")
            for _, r in krit_df.iterrows():
                st.markdown(f"""<div class="alert-box-red">
<b>🔴 {r['Nomor Prosedur']}</b> — {r['Nama Prosedur']}<br>
<small>📂 {r['Divisi Pemilik Proses']} &nbsp;|&nbsp;
📅 Review: {r['Tgl Review']} &nbsp;|&nbsp;
⏰ <b style='color:#9C0006'>{r['sisa']} hari lagi</b></small>
</div>""", unsafe_allow_html=True)

        if len(segera_df) > 0:
            st.markdown("")
            st.warning(f"⚠️ **{len(segera_df)} prosedur** — akan expired dalam {warn_days} hari")
            for _, r in segera_df.iterrows():
                st.markdown(f"""<div class="alert-box">
<b>🟡 {r['Nomor Prosedur']}</b> — {r['Nama Prosedur']}<br>
<small>📂 {r['Divisi Pemilik Proses']} &nbsp;|&nbsp;
📅 Review: {r['Tgl Review']} &nbsp;|&nbsp;
⏰ <b style='color:#7D4E00'>{r['sisa']} hari lagi</b></small>
</div>""", unsafe_allow_html=True)




# ═══════════════════════════════════════════════════════════════════════════════
# TAB 5 – PER DIVISI
# ═══════════════════════════════════════════════════════════════════════════════
with tab5:
    div_sum = (dff.groupby('Divisi Pemilik Proses')
               .apply(lambda g: pd.Series({
                   'Total':         len(g),
                   'Berlaku':       int((g.Keterangan == 'Berlaku').sum()),
                   'Tidak Berlaku': int((g.Keterangan == 'Tidak Berlaku').sum()),
                   '% Berlaku':     round((g.Keterangan == 'Berlaku').sum() / len(g) * 100, 1),
                   f'Segera (≤{warn_days}hr)': int(((g.Keterangan == 'Berlaku') & (g.sisa <= warn_days)).sum()),
               }), include_groups=False)
               .reset_index().sort_values('Total', ascending=False))

    st.dataframe(
        div_sum.style.apply(highlight_pct, axis=1).format({'% Berlaku': '{:.1f}%'}),
        use_container_width=True, height=380)

    section("Detail per Divisi")
    divisi_sel = st.selectbox("Pilih Divisi", sorted(dff['Divisi Pemilik Proses'].unique()))
    sub = dff[dff['Divisi Pemilik Proses'] == divisi_sel].reset_index(drop=True)
    b_s = int((sub.Keterangan == 'Berlaku').sum()); t_s = len(sub) - b_s
    mc1, mc2, mc3 = st.columns(3)
    mc1.metric("Total", len(sub)); mc2.metric("Berlaku", b_s); mc3.metric("Tidak Berlaku", t_s)

    sub_show = (sub[['No', 'Nomor Prosedur', 'Nama Prosedur', 'Rev', 'Kategori',
                      'Tgl Berlaku', 'Tgl Review', 'sisa', 'Keterangan']]
                .rename(columns={'sisa': 'Sisa Hari'}))
    st.dataframe(
        sub_show.style.apply(lambda row: color_row(row, warn_days, crit_days), axis=1),
        use_container_width=True, height=380)


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 6 – PER KATEGORI
# ═══════════════════════════════════════════════════════════════════════════════
with tab6:
    kat_sum = (dff.groupby('Kategori')
               .apply(lambda g: pd.Series({
                   'Total':         len(g),
                   'Berlaku':       int((g.Keterangan == 'Berlaku').sum()),
                   'Tidak Berlaku': int((g.Keterangan == 'Tidak Berlaku').sum()),
                   '% Berlaku':     round((g.Keterangan == 'Berlaku').sum() / len(g) * 100, 1),
                   f'Segera (≤{warn_days}hr)': int(((g.Keterangan == 'Berlaku') & (g.sisa <= warn_days)).sum()),
               }), include_groups=False)
               .reset_index().sort_values('Total', ascending=False))

    st.dataframe(
        kat_sum.style.apply(highlight_pct, axis=1).format({'% Berlaku': '{:.1f}%'}),
        use_container_width=True, height=380)

    section("Detail per Kategori")
    kat_sel = st.selectbox("Pilih Kategori", sorted(dff['Kategori'].unique()))
    sub_k = dff[dff['Kategori'] == kat_sel].reset_index(drop=True)
    bk = int((sub_k.Keterangan == 'Berlaku').sum()); tk = len(sub_k) - bk
    kc1, kc2, kc3 = st.columns(3)
    kc1.metric("Total", len(sub_k)); kc2.metric("Berlaku", bk); kc3.metric("Tidak Berlaku", tk)

    sub_k_show = (sub_k[['No', 'Nomor Prosedur', 'Nama Prosedur', 'Rev',
                          'Divisi Pemilik Proses', 'Tgl Review', 'sisa', 'Keterangan']]
                  .rename(columns={'sisa': 'Sisa Hari'}))
    st.dataframe(
        sub_k_show.style.apply(lambda row: color_row(row, warn_days, crit_days), axis=1),
        use_container_width=True, height=350)


# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    f"<div style='text-align:center;color:#999;font-size:0.75rem'>"
    f"PT Wijaya Karya Beton Tbk &nbsp;|&nbsp; DSIM – Kantor Pusat &nbsp;|&nbsp; "
    f"Sumber: Sheet \"9 Maret 2026\" &nbsp;|&nbsp; "
    f"Form: WB-QMS-PS-01-F08 Rev.02 &nbsp;|&nbsp; "
    f"{today.strftime('%d %B %Y')}</div>",
    unsafe_allow_html=True,
)
