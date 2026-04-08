import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, date
import os

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Monitoring Prosedur – WIKA Beton",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main { background-color: #f8f9fb; }
    .block-container { padding: 1.5rem 2rem; }
    h1 { color: #1F3864; font-size: 1.5rem !important; }
    h2 { color: #1F3864; font-size: 1.1rem !important; }
    h3 { color: #2E75B6; font-size: 1rem !important; }

    .kpi-card {
        background: white;
        border-radius: 12px;
        padding: 1.1rem 1.2rem;
        box-shadow: 0 1px 4px rgba(0,0,0,0.08);
        border-left: 5px solid #ccc;
        margin-bottom: 0.5rem;
    }
    .kpi-label { font-size: 0.72rem; color: #888; font-weight: 600;
                 text-transform: uppercase; letter-spacing: 0.05em; }
    .kpi-value { font-size: 2.2rem; font-weight: 700; line-height: 1.1; }
    .kpi-sub   { font-size: 0.75rem; color: #666; margin-top: 2px; }

    .kpi-blue   { border-color: #2E75B6; }
    .kpi-green  { border-color: #375623; }
    .kpi-red    { border-color: #9C0006; }
    .kpi-orange { border-color: #B26800; }
    .kpi-blue  .kpi-value { color: #2E75B6; }
    .kpi-green .kpi-value { color: #375623; }
    .kpi-red   .kpi-value { color: #9C0006; }
    .kpi-orange .kpi-value { color: #B26800; }

    .badge {
        display: inline-block; padding: 3px 10px; border-radius: 20px;
        font-size: 0.7rem; font-weight: 700;
    }
    .badge-berlaku   { background:#e2efda; color:#375623; }
    .badge-tidak     { background:#ffc7ce; color:#9C0006; }
    .badge-segera    { background:#ffeb9c; color:#7D4E00; }
    .badge-kritis    { background:#ff9999; color:#7B0000; }

    .section-header {
        background: linear-gradient(90deg, #1F3864, #2E75B6);
        color: white; padding: 0.5rem 1rem; border-radius: 8px;
        font-weight: 600; font-size: 0.9rem; margin: 1rem 0 0.5rem 0;
    }
    .alert-box {
        background: #fff3cd; border: 1px solid #ffc107;
        border-radius: 8px; padding: 0.7rem 1rem; margin: 0.3rem 0;
    }
    .alert-box-red {
        background: #fde8e8; border: 1px solid #f87171;
        border-radius: 8px; padding: 0.7rem 1rem; margin: 0.3rem 0;
    }
    div[data-testid="stDataFrame"] { border-radius: 10px; overflow: hidden; }
    .stSelectbox label, .stMultiSelect label { color: #1F3864; font-weight: 600; }
</style>
""", unsafe_allow_html=True)


# ── Load data ─────────────────────────────────────────────────────────────────
@st.cache_data
def load_data(path):
    df = pd.read_csv(path)
    df['sisa'] = pd.to_numeric(df['sisa'], errors='coerce').fillna(0).astype(int)
    df['Keterangan'] = df['Keterangan'].str.strip()
    df['Divisi Pemilik Proses'] = df['Divisi Pemilik Proses'].fillna('Tidak Diketahui')
    return df

DATA_PATH = os.path.join(os.path.dirname(__file__), 'data.csv')
df = load_data(DATA_PATH)
today = datetime.today()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/5/5a/Wika_Beton_logo.png/200px-Wika_Beton_logo.png",
             width=160, use_column_width=False)
    st.markdown("### 📋 Monitoring Prosedur")
    st.markdown(f"**Update:** 9 Maret 2026  \n**Divisi:** DSIM  \n**Tanggal:** {today.strftime('%d %b %Y')}")
    st.divider()

    st.markdown("#### 🔍 Filter Data")

    div_options = ['Semua Divisi'] + sorted(df['Divisi Pemilik Proses'].unique().tolist())
    sel_div = st.selectbox("Divisi Pemilik Proses", div_options)

    kat_options = ['Semua Kategori'] + sorted(df['Kategori'].unique().tolist())
    sel_kat = st.selectbox("Kategori", kat_options)

    sel_sts = st.multiselect("Status", ['Berlaku', 'Tidak Berlaku'],
                              default=['Berlaku', 'Tidak Berlaku'])

    st.divider()
    st.markdown("#### ⚙️ Pengaturan")
    warn_days = st.slider("Threshold peringatan (hari)", 30, 180, 90, step=10)
    crit_days = st.slider("Threshold kritis (hari)", 10, 60, 30, step=5)

    st.divider()
    st.markdown("#### 📥 Export")
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("⬇ Download CSV", csv, "monitoring_prosedur.csv", "text/csv")


# ── Apply filters ─────────────────────────────────────────────────────────────
dff = df.copy()
if sel_div != 'Semua Divisi':
    dff = dff[dff['Divisi Pemilik Proses'] == sel_div]
if sel_kat != 'Semua Kategori':
    dff = dff[dff['Kategori'] == sel_kat]
if sel_sts:
    dff = dff[dff['Keterangan'].isin(sel_sts)]

total   = len(dff)
berlaku = (dff['Keterangan'] == 'Berlaku').sum()
tidak   = total - berlaku
warn    = ((dff['Keterangan'] == 'Berlaku') & (dff['sisa'] <= warn_days)).sum()
kritis  = ((dff['Keterangan'] == 'Berlaku') & (dff['sisa'] <= crit_days)).sum()
pct_b   = round(berlaku / total * 100, 1) if total > 0 else 0


# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style='background:linear-gradient(90deg,#1F3864,#2E75B6);padding:1rem 1.5rem;
border-radius:12px;margin-bottom:1rem'>
<h1 style='color:white;margin:0;font-size:1.4rem'>
PT WIJAYA KARYA BETON Tbk</h1>
<p style='color:#BDD7EE;margin:4px 0 0;font-size:0.85rem'>
DASHBOARD MONITORING DAFTAR INDUK DOKUMEN SISTEM MANAJEMEN &nbsp;|&nbsp;
DSIM – Kantor Pusat &nbsp;|&nbsp; Form: WB-QMS-PS-01-F08 Rev.02</p>
</div>
""", unsafe_allow_html=True)


# ── KPI Cards ─────────────────────────────────────────────────────────────────
c1, c2, c3, c4, c5 = st.columns(5)

def kpi(col, label, value, sub, cls):
    col.markdown(f"""<div class="kpi-card {cls}">
    <div class="kpi-label">{label}</div>
    <div class="kpi-value">{value}</div>
    <div class="kpi-sub">{sub}</div>
    </div>""", unsafe_allow_html=True)

kpi(c1, "Total Prosedur",   total,   f"{'filter aktif' if sel_div!='Semua Divisi' or sel_kat!='Semua Kategori' else 'semua divisi'}", "kpi-blue")
kpi(c2, "Berlaku",          berlaku, f"{pct_b}% dari total",                    "kpi-green")
kpi(c3, "Tidak Berlaku",    tidak,   f"{round(tidak/total*100,1) if total else 0}% perlu diperbarui", "kpi-red")
kpi(c4, f"Segera Expired ≤{warn_days}hr", warn,   f"perlu segera ditindaklanjuti",    "kpi-orange")
kpi(c5, f"KRITIS ≤{crit_days}hr",  kritis, "harus segera diperbarui sekarang!", "kpi-red")

st.markdown("<br>", unsafe_allow_html=True)


# ── Tab layout ────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Grafik & Analisis",
    "📋 Tabel Lengkap",
    "⚠️ Peringatan Expired",
    "🏢 Per Divisi",
    "🗂️ Per Kategori",
])


# ══════════════════════════════════════════════════════════════
# TAB 1 – GRAFIK & ANALISIS
# ══════════════════════════════════════════════════════════════
with tab1:
    row1_l, row1_r = st.columns([1, 1.6])

    # Donut chart
    with row1_l:
        st.markdown("#### Komposisi Status Keseluruhan")
        pie_df = dff['Keterangan'].value_counts().reset_index()
        pie_df.columns = ['Status', 'Jumlah']
        fig_pie = px.pie(
            pie_df, values='Jumlah', names='Status', hole=0.55,
            color='Status',
            color_discrete_map={'Berlaku': '#70AD47', 'Tidak Berlaku': '#FF4444'},
        )
        fig_pie.update_traces(textposition='outside', textinfo='label+percent+value',
                              textfont_size=12)
        fig_pie.update_layout(
            showlegend=True, height=320, margin=dict(t=10, b=10, l=10, r=10),
            legend=dict(orientation='h', yanchor='bottom', y=-0.15, x=0.5, xanchor='center'),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            annotations=[dict(text=f'<b>{total}</b><br>Total', x=0.5, y=0.5,
                              font_size=14, showarrow=False)]
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    # Bar per divisi
    with row1_r:
        st.markdown("#### Status Berlaku per Divisi")
        div_grp = dff.groupby('Divisi Pemilik Proses').apply(
            lambda g: pd.Series({
                'Berlaku': (g['Keterangan']=='Berlaku').sum(),
                'Tidak Berlaku': (g['Keterangan']=='Tidak Berlaku').sum(),
                'Total': len(g),
                'Pct': round((g['Keterangan']=='Berlaku').sum()/len(g)*100, 1)
            })
        ).reset_index().sort_values('Total', ascending=True)
        div_grp['Label'] = div_grp['Divisi Pemilik Proses'].str.replace('DIVISI ','').str.replace('SEKRETARIAT PERUSAHAAN','SEKRETARIAT').str.replace('SATUAN PENGAWASAN INTERNAL','SPI')

        fig_bar = go.Figure()
        fig_bar.add_trace(go.Bar(
            y=div_grp['Label'], x=div_grp['Berlaku'], name='Berlaku',
            orientation='h', marker_color='#70AD47',
            text=div_grp['Berlaku'], textposition='inside', insidetextanchor='middle',
        ))
        fig_bar.add_trace(go.Bar(
            y=div_grp['Label'], x=div_grp['Tidak Berlaku'], name='Tidak Berlaku',
            orientation='h', marker_color='#FF6B6B',
            text=div_grp['Tidak Berlaku'].apply(lambda x: str(x) if x>0 else ''),
            textposition='inside', insidetextanchor='middle',
        ))
        fig_bar.update_layout(
            barmode='stack', height=340, margin=dict(t=10, b=10, l=10, r=60),
            legend=dict(orientation='h', y=1.05, x=0.5, xanchor='center'),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(showgrid=True, gridcolor='#eee'),
            yaxis=dict(tickfont=dict(size=10)),
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    # Row 2
    row2_l, row2_r = st.columns(2)

    with row2_l:
        st.markdown("#### Jumlah Prosedur per Kategori")
        kat_grp = dff.groupby('Kategori').apply(
            lambda g: pd.Series({'Berlaku':(g.Keterangan=='Berlaku').sum(),
                                 'Tidak Berlaku':(g.Keterangan=='Tidak Berlaku').sum()})
        ).reset_index().sort_values('Berlaku', ascending=False)

        fig_kat = go.Figure()
        fig_kat.add_trace(go.Bar(x=kat_grp['Kategori'], y=kat_grp['Berlaku'],
            name='Berlaku', marker_color='#70AD47'))
        fig_kat.add_trace(go.Bar(x=kat_grp['Kategori'], y=kat_grp['Tidak Berlaku'],
            name='Tidak Berlaku', marker_color='#FF6B6B'))
        fig_kat.update_layout(
            barmode='stack', height=300, margin=dict(t=10, b=10, l=10, r=10),
            legend=dict(orientation='h', y=1.05, x=0.5, xanchor='center'),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(tickangle=45), yaxis=dict(showgrid=True, gridcolor='#eee'),
        )
        st.plotly_chart(fig_kat, use_container_width=True)

    with row2_r:
        st.markdown("#### Distribusi Sisa Hari Masa Berlaku")
        berlaku_df = dff[dff['Keterangan'] == 'Berlaku']
        fig_hist = px.histogram(
            berlaku_df, x='sisa', nbins=20,
            color_discrete_sequence=['#2E75B6'],
            labels={'sisa': 'Sisa Hari', 'count': 'Jumlah Prosedur'},
        )
        fig_hist.add_vline(x=warn_days, line_dash='dash', line_color='orange',
                           annotation_text=f'Threshold {warn_days}hr',
                           annotation_position='top right')
        fig_hist.add_vline(x=crit_days, line_dash='dash', line_color='red',
                           annotation_text=f'Kritis {crit_days}hr',
                           annotation_position='top left')
        fig_hist.add_vrect(x0=0, x1=crit_days, fillcolor='red', opacity=0.07, line_width=0)
        fig_hist.add_vrect(x0=crit_days, x1=warn_days, fillcolor='orange', opacity=0.07, line_width=0)
        fig_hist.update_layout(
            height=300, margin=dict(t=10, b=10, l=10, r=10),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(showgrid=True, gridcolor='#eee'),
            yaxis=dict(showgrid=True, gridcolor='#eee'),
        )
        st.plotly_chart(fig_hist, use_container_width=True)

    # % berlaku per divisi gauge-style
    st.markdown("#### Persentase Berlaku per Divisi")
    div_pct = dff.groupby('Divisi Pemilik Proses').apply(
        lambda g: round((g.Keterangan=='Berlaku').sum()/len(g)*100, 1)
    ).reset_index()
    div_pct.columns=['Divisi','% Berlaku']
    div_pct['Label']=div_pct['Divisi'].str.replace('DIVISI ','').str.replace('SEKRETARIAT PERUSAHAAN','SEKRETARIAT').str.replace('SATUAN PENGAWASAN INTERNAL','SPI')
    div_pct=div_pct.sort_values('% Berlaku', ascending=True)

    fig_pct=px.bar(div_pct, x='% Berlaku', y='Label', orientation='h',
        text='% Berlaku',
        color='% Berlaku',
        color_continuous_scale=[(0,'#FF4444'),(0.7,'#FFC107'),(1,'#70AD47')],
        range_color=[0,100])
    fig_pct.update_traces(texttemplate='%{text}%', textposition='outside')
    fig_pct.update_layout(
        height=320, margin=dict(t=10, b=10, l=10, r=60),
        coloraxis_showscale=False,
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(range=[0,110], showgrid=True, gridcolor='#eee', ticksuffix='%'),
        yaxis=dict(tickfont=dict(size=10)),
        showlegend=False,
    )
    fig_pct.add_vline(x=100, line_dash='dot', line_color='#70AD47', opacity=0.5)
    fig_pct.add_vline(x=70,  line_dash='dot', line_color='orange',  opacity=0.5)
    st.plotly_chart(fig_pct, use_container_width=True)


# ══════════════════════════════════════════════════════════════
# TAB 2 – TABEL LENGKAP
# ══════════════════════════════════════════════════════════════
with tab2:
    cl, cr = st.columns([3, 1])
    with cl:
        search = st.text_input("🔍 Cari nomor / nama prosedur...", placeholder="Ketik untuk mencari...")
    with cr:
        st.metric("Prosedur ditampilkan", len(dff))

    tbl = dff.copy()
    if search:
        mask = (tbl['Nomor Prosedur'].str.contains(search, case=False, na=False) |
                tbl['Nama Prosedur'].str.contains(search, case=False, na=False))
        tbl = tbl[mask]

    def color_status(val):
        if val == 'Berlaku':   return 'background-color:#e2efda;color:#375623;font-weight:bold'
        return 'background-color:#ffc7ce;color:#9C0006;font-weight:bold'

    def color_sisa(val):
        if val < 0:        return 'color:#9C0006;font-weight:bold'
        if val <= crit_days: return 'color:#9C0006;font-weight:bold'
        if val <= warn_days: return 'color:#7D4E00;font-weight:bold'
        return 'color:#375623'

    display_cols = ['No','Nomor Prosedur','Nama Prosedur','Rev','Kategori',
                    'Divisi Pemilik Proses','Tgl Berlaku','Tgl Review','sisa','Keterangan']
    styled = (tbl[display_cols]
              .rename(columns={'sisa':'Sisa Hari'})
              .style
              .applymap(color_status, subset=['Keterangan'])
              .applymap(color_sisa,   subset=['Sisa Hari'])
              .set_properties(subset=['Nama Prosedur'], **{'text-align':'left'})
              .set_properties(subset=['No','Rev','Kategori','Sisa Hari'], **{'text-align':'center'})
             )
    st.dataframe(styled, use_container_width=True, height=500)

    col_dl1, col_dl2 = st.columns([1,4])
    with col_dl1:
        csv_tbl = tbl[display_cols].to_csv(index=False).encode('utf-8')
        st.download_button("⬇ Download tabel ini", csv_tbl, "filtered_data.csv", "text/csv")


# ══════════════════════════════════════════════════════════════
# TAB 3 – PERINGATAN EXPIRED
# ══════════════════════════════════════════════════════════════
with tab3:
    exp_all = dff[(dff['Keterangan']=='Berlaku') & (dff['sisa'] <= warn_days)].sort_values('sisa')

    if len(exp_all) == 0:
        st.success(f"✅ Tidak ada prosedur yang akan expired dalam {warn_days} hari ke depan.")
    else:
        krit_df = exp_all[exp_all['sisa'] <= crit_days]
        warn_df = exp_all[exp_all['sisa'] > crit_days]

        if len(krit_df) > 0:
            st.error(f"🚨 **{len(krit_df)} PROSEDUR KRITIS** — akan expired dalam {crit_days} hari atau kurang!")
            for _, r in krit_df.iterrows():
                st.markdown(f"""<div class="alert-box-red">
                <b>🔴 {r['Nomor Prosedur']}</b> — {r['Nama Prosedur']}<br>
                <small>📂 {r['Divisi Pemilik Proses']} &nbsp;|&nbsp; 📅 Review: {r['Tgl Review']} &nbsp;|&nbsp;
                ⏰ <b style='color:#9C0006'>{r['sisa']} hari lagi</b></small>
                </div>""", unsafe_allow_html=True)
            st.markdown("")

        if len(warn_df) > 0:
            st.warning(f"⚠️ **{len(warn_df)} prosedur** — akan expired dalam {warn_days} hari")
            for _, r in warn_df.iterrows():
                st.markdown(f"""<div class="alert-box">
                <b>🟡 {r['Nomor Prosedur']}</b> — {r['Nama Prosedur']}<br>
                <small>📂 {r['Divisi Pemilik Proses']} &nbsp;|&nbsp; 📅 Review: {r['Tgl Review']} &nbsp;|&nbsp;
                ⏰ <b style='color:#7D4E00'>{r['sisa']} hari lagi</b></small>
                </div>""", unsafe_allow_html=True)

        st.markdown("")
        # Timeline chart
        st.markdown("#### Timeline Masa Berlaku (Berlaku ≤ 2 tahun ke depan)")
        timeline_df = dff[(dff['Keterangan']=='Berlaku') & (dff['sisa'] <= 730)].sort_values('sisa')
        if len(timeline_df) > 0:
            timeline_df['Warna'] = timeline_df['sisa'].apply(
                lambda x: '🔴 Kritis' if x<=crit_days else ('🟡 Segera' if x<=warn_days else '🟢 Aman'))
            fig_tl = px.bar(
                timeline_df, x='sisa', y='Nomor Prosedur', orientation='h',
                color='Warna',
                color_discrete_map={'🔴 Kritis':'#FF4444','🟡 Segera':'#FFC107','🟢 Aman':'#70AD47'},
                hover_data=['Nama Prosedur','Divisi Pemilik Proses','Tgl Review'],
                labels={'sisa':'Sisa Hari'},
            )
            fig_tl.add_vline(x=crit_days, line_dash='dash', line_color='red',
                             annotation_text=f'{crit_days} hr')
            fig_tl.add_vline(x=warn_days, line_dash='dash', line_color='orange',
                             annotation_text=f'{warn_days} hr')
            fig_tl.update_layout(
                height=max(300, len(timeline_df)*22),
                margin=dict(t=10, b=10, l=10, r=10),
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                yaxis=dict(tickfont=dict(size=9)),
                legend=dict(orientation='h', y=1.05),
            )
            st.plotly_chart(fig_tl, use_container_width=True)


# ══════════════════════════════════════════════════════════════
# TAB 4 – PER DIVISI
# ══════════════════════════════════════════════════════════════
with tab4:
    div_summary = dff.groupby('Divisi Pemilik Proses').apply(lambda g: pd.Series({
        'Total': len(g),
        'Berlaku': (g.Keterangan=='Berlaku').sum(),
        'Tidak Berlaku': (g.Keterangan=='Tidak Berlaku').sum(),
        '% Berlaku': round((g.Keterangan=='Berlaku').sum()/len(g)*100,1),
        f'Segera (≤{warn_days}hr)': ((g.Keterangan=='Berlaku')&(g.sisa<=warn_days)).sum(),
    })).reset_index().sort_values('Total', ascending=False)

    styled_div = (div_summary.style
        .background_gradient(subset=['% Berlaku'], cmap='RdYlGn', vmin=0, vmax=100)
        .format({'% Berlaku': '{:.1f}%'})
        .applymap(lambda v: 'color:#9C0006;font-weight:bold' if v>0 else '',
                  subset=['Tidak Berlaku'])
    )
    st.dataframe(styled_div, use_container_width=True, height=380)

    st.markdown("#### Detail Prosedur per Divisi")
    divisi_sel = st.selectbox("Pilih Divisi", sorted(dff['Divisi Pemilik Proses'].unique()))
    sub = dff[dff['Divisi Pemilik Proses']==divisi_sel].reset_index(drop=True)

    b = (sub.Keterangan=='Berlaku').sum(); t = len(sub)-b
    mc1, mc2, mc3 = st.columns(3)
    mc1.metric("Total",   len(sub))
    mc2.metric("Berlaku", b, delta=f"{round(b/len(sub)*100,1)}%")
    mc3.metric("Tidak Berlaku", t, delta=f"-{t}" if t>0 else "0", delta_color="inverse")

    def style_sub(val, col):
        if col == 'Keterangan':
            return 'background:#e2efda;color:#375623;font-weight:bold' if val=='Berlaku' else 'background:#ffc7ce;color:#9C0006;font-weight:bold'
        if col == 'sisa':
            if val<0: return 'color:#9C0006;font-weight:bold'
            if val<=warn_days: return 'color:#7D4E00;font-weight:bold'
            return 'color:#375623'
        return ''

    sub_display = sub[['No','Nomor Prosedur','Nama Prosedur','Rev','Kategori','Tgl Berlaku','Tgl Review','sisa','Keterangan']].rename(columns={'sisa':'Sisa Hari'})
    styled_sub = sub_display.style.applymap(lambda v: style_sub(v,'Keterangan'), subset=['Keterangan']).applymap(lambda v: style_sub(v,'sisa'), subset=['Sisa Hari'])
    st.dataframe(styled_sub, use_container_width=True, height=350)


# ══════════════════════════════════════════════════════════════
# TAB 5 – PER KATEGORI
# ══════════════════════════════════════════════════════════════
with tab5:
    kat_summary = dff.groupby('Kategori').apply(lambda g: pd.Series({
        'Total': len(g),
        'Berlaku': (g.Keterangan=='Berlaku').sum(),
        'Tidak Berlaku': (g.Keterangan=='Tidak Berlaku').sum(),
        '% Berlaku': round((g.Keterangan=='Berlaku').sum()/len(g)*100,1),
        f'Segera (≤{warn_days}hr)': ((g.Keterangan=='Berlaku')&(g.sisa<=warn_days)).sum(),
    })).reset_index().sort_values('Total', ascending=False)

    styled_kat = (kat_summary.style
        .background_gradient(subset=['% Berlaku'], cmap='RdYlGn', vmin=0, vmax=100)
        .format({'% Berlaku': '{:.1f}%'})
        .applymap(lambda v: 'color:#9C0006;font-weight:bold' if v>0 else '',
                  subset=['Tidak Berlaku'])
    )
    st.dataframe(styled_kat, use_container_width=True, height=380)

    st.markdown("#### Treemap – Proporsi Prosedur per Kategori & Status")
    tree_df = dff.groupby(['Kategori','Keterangan']).size().reset_index(name='Jumlah')
    fig_tree = px.treemap(
        tree_df, path=['Kategori','Keterangan'], values='Jumlah',
        color='Keterangan',
        color_discrete_map={'Berlaku':'#70AD47','Tidak Berlaku':'#FF4444','(?)':'#ccc'},
    )
    fig_tree.update_traces(textinfo='label+value+percent parent')
    fig_tree.update_layout(height=420, margin=dict(t=10,b=10,l=10,r=10),
                           paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_tree, use_container_width=True)

    st.markdown("#### Detail Prosedur per Kategori")
    kat_sel = st.selectbox("Pilih Kategori", sorted(dff['Kategori'].unique()))
    sub_k = dff[dff['Kategori']==kat_sel].reset_index(drop=True)
    bk=(sub_k.Keterangan=='Berlaku').sum(); tk=len(sub_k)-bk
    kc1, kc2, kc3 = st.columns(3)
    kc1.metric("Total",len(sub_k)); kc2.metric("Berlaku",bk); kc3.metric("Tidak Berlaku",tk, delta_color="inverse")

    sub_k_display = sub_k[['No','Nomor Prosedur','Nama Prosedur','Rev','Divisi Pemilik Proses','Tgl Review','sisa','Keterangan']].rename(columns={'sisa':'Sisa Hari'})
    styled_sk = sub_k_display.style.applymap(lambda v: 'background:#e2efda;color:#375623;font-weight:bold' if v=='Berlaku' else 'background:#ffc7ce;color:#9C0006;font-weight:bold', subset=['Keterangan'])
    st.dataframe(styled_sk, use_container_width=True, height=320)


# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(f"""<div style='text-align:center;color:#999;font-size:0.75rem'>
PT Wijaya Karya Beton Tbk &nbsp;|&nbsp; DSIM – Kantor Pusat &nbsp;|&nbsp;
Sumber Data: Sheet "9 Maret 2026" &nbsp;|&nbsp; Form: WB-QMS-PS-01-F08 Rev.02 &nbsp;|&nbsp;
{today.strftime('%d %B %Y')}
</div>""", unsafe_allow_html=True)
