import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
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
    .kpi-blue   .kpi-value { color: #2E75B6; }
    .kpi-green  .kpi-value { color: #375623; }
    .kpi-red    .kpi-value { color: #9C0006; }
    .kpi-orange .kpi-value { color: #B26800; }

    .alert-box {
        background: #fff3cd; border: 1px solid #ffc107;
        border-radius: 8px; padding: 0.7rem 1rem; margin: 0.3rem 0;
    }
    .alert-box-red {
        background: #fde8e8; border: 1px solid #f87171;
        border-radius: 8px; padding: 0.7rem 1rem; margin: 0.3rem 0;
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
    return df

df = load_data()
today = datetime.today()


# ── Helper: row styler (dipakai di beberapa tab) ──────────────────────────────
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

def shorten_div(s):
    return (s.replace('DIVISI ', '')
             .replace('SEKRETARIAT PERUSAHAAN', 'SEKRETARIAT')
             .replace('SATUAN PENGAWASAN INTERNAL', 'SPI'))


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📋 Monitoring Prosedur")
    st.markdown("**PT Wijaya Karya Beton Tbk**")
    st.markdown(
        f"Update: 9 Maret 2026  \n"
        f"Divisi: DSIM  \n"
        f"Tanggal: {today.strftime('%d %b %Y')}"
    )
    st.divider()

    st.markdown("#### 🔍 Filter Data")
    div_opts = ['Semua Divisi'] + sorted(df['Divisi Pemilik Proses'].unique().tolist())
    sel_div  = st.selectbox("Divisi Pemilik Proses", div_opts)

    kat_opts = ['Semua Kategori'] + sorted(df['Kategori'].unique().tolist())
    sel_kat  = st.selectbox("Kategori", kat_opts)

    sel_sts = st.multiselect(
        "Status", ['Berlaku', 'Tidak Berlaku'],
        default=['Berlaku', 'Tidak Berlaku']
    )

    st.divider()
    st.markdown("#### ⚙️ Pengaturan")
    warn_days = st.slider("Threshold peringatan (hari)", 30, 180, 90, step=10)
    crit_days = st.slider("Threshold kritis (hari)", 10, 60, 30, step=5)

    st.divider()
    st.download_button(
        "⬇ Download CSV",
        df.to_csv(index=False).encode('utf-8'),
        "monitoring_prosedur.csv", "text/csv"
    )


# ── Apply filters ─────────────────────────────────────────────────────────────
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


# ── KPI Cards ─────────────────────────────────────────────────────────────────
def kpi(col, label, value, sub, cls):
    col.markdown(f"""<div class="kpi-card {cls}">
<div class="kpi-label">{label}</div>
<div class="kpi-value">{value}</div>
<div class="kpi-sub">{sub}</div>
</div>""", unsafe_allow_html=True)

c1, c2, c3, c4, c5 = st.columns(5)
kpi(c1, "Total Prosedur",           total,  "data per 9 Maret 2026",              "kpi-blue")
kpi(c2, "Berlaku",                   berl,   f"{pct_b}% dari total",               "kpi-green")
kpi(c3, "Tidak Berlaku",             tidak,  f"{round(tidak/total*100,1) if total else 0}% perlu diperbarui", "kpi-red")
kpi(c4, f"Segera Expired ≤{warn_days}hr", warn_n, "perlu segera ditindaklanjuti", "kpi-orange")
kpi(c5, f"KRITIS ≤{crit_days}hr",   krit_n, "harus diperbarui sekarang!",         "kpi-red")

st.markdown("<br>", unsafe_allow_html=True)


# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Grafik & Analisis",
    "📋 Tabel Lengkap",
    "⚠️ Peringatan Expired",
    "🏢 Per Divisi",
    "🗂️ Per Kategori",
])


# ══════ TAB 1 – GRAFIK ═══════════════════════════════════════════════════════
with tab1:
    col_l, col_r = st.columns([1, 1.6])

    # Donut
    with col_l:
        st.markdown("#### Komposisi Status Keseluruhan")
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
            showlegend=True, height=320,
            margin=dict(t=10, b=30, l=10, r=10),
            legend=dict(orientation='h', yanchor='bottom', y=-0.2, x=0.5, xanchor='center'),
            paper_bgcolor='rgba(0,0,0,0)',
            annotations=[dict(text=f'<b>{total}</b><br>Total', x=0.5, y=0.5,
                              font_size=14, showarrow=False)]
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    # Bar per divisi
    with col_r:
        st.markdown("#### Status Berlaku per Divisi")
        div_grp = (dff.groupby('Divisi Pemilik Proses')
                   .apply(lambda g: pd.Series({
                       'Berlaku':       int((g['Keterangan'] == 'Berlaku').sum()),
                       'Tidak Berlaku': int((g['Keterangan'] == 'Tidak Berlaku').sum()),
                       'Total':         len(g),
                   }), include_groups=False)
                   .reset_index()
                   .sort_values('Total', ascending=True))
        div_grp['Label'] = div_grp['Divisi Pemilik Proses'].apply(shorten_div)

        fig_bar = go.Figure()
        fig_bar.add_trace(go.Bar(
            y=div_grp['Label'], x=div_grp['Berlaku'], name='Berlaku',
            orientation='h', marker_color='#70AD47',
            text=div_grp['Berlaku'], textposition='inside',
        ))
        fig_bar.add_trace(go.Bar(
            y=div_grp['Label'], x=div_grp['Tidak Berlaku'], name='Tidak Berlaku',
            orientation='h', marker_color='#FF6B6B',
            text=div_grp['Tidak Berlaku'].apply(lambda x: str(x) if x > 0 else ''),
            textposition='inside',
        ))
        fig_bar.update_layout(
            barmode='stack', height=340,
            margin=dict(t=10, b=10, l=10, r=40),
            legend=dict(orientation='h', y=1.05, x=0.5, xanchor='center'),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(showgrid=True, gridcolor='#eee'),
            yaxis=dict(tickfont=dict(size=10)),
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    col2_l, col2_r = st.columns(2)

    # Bar per kategori
    with col2_l:
        st.markdown("#### Jumlah Prosedur per Kategori")
        kat_grp = (dff.groupby('Kategori')
                   .apply(lambda g: pd.Series({
                       'Berlaku':       int((g.Keterangan == 'Berlaku').sum()),
                       'Tidak Berlaku': int((g.Keterangan == 'Tidak Berlaku').sum()),
                   }), include_groups=False)
                   .reset_index()
                   .sort_values('Berlaku', ascending=False))
        fig_kat = go.Figure()
        fig_kat.add_trace(go.Bar(x=kat_grp['Kategori'], y=kat_grp['Berlaku'],
            name='Berlaku', marker_color='#70AD47'))
        fig_kat.add_trace(go.Bar(x=kat_grp['Kategori'], y=kat_grp['Tidak Berlaku'],
            name='Tidak Berlaku', marker_color='#FF6B6B'))
        fig_kat.update_layout(
            barmode='stack', height=300,
            margin=dict(t=10, b=10, l=10, r=10),
            legend=dict(orientation='h', y=1.05, x=0.5, xanchor='center'),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(tickangle=45),
            yaxis=dict(showgrid=True, gridcolor='#eee'),
        )
        st.plotly_chart(fig_kat, use_container_width=True)

    # Histogram sisa hari
    with col2_r:
        st.markdown("#### Distribusi Sisa Hari Masa Berlaku")
        berl_only = dff[dff['Keterangan'] == 'Berlaku']
        fig_hist = px.histogram(berl_only, x='sisa', nbins=20,
            color_discrete_sequence=['#2E75B6'],
            labels={'sisa': 'Sisa Hari', 'count': 'Jumlah Prosedur'})
        fig_hist.add_vline(x=warn_days, line_dash='dash', line_color='orange',
            annotation_text=f'Threshold {warn_days}hr', annotation_position='top right')
        fig_hist.add_vline(x=crit_days, line_dash='dash', line_color='red',
            annotation_text=f'Kritis {crit_days}hr', annotation_position='top left')
        fig_hist.add_vrect(x0=0, x1=crit_days,        fillcolor='red',    opacity=0.07, line_width=0)
        fig_hist.add_vrect(x0=crit_days, x1=warn_days, fillcolor='orange', opacity=0.07, line_width=0)
        fig_hist.update_layout(
            height=300, margin=dict(t=10, b=10, l=10, r=10),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(showgrid=True, gridcolor='#eee'),
            yaxis=dict(showgrid=True, gridcolor='#eee'),
        )
        st.plotly_chart(fig_hist, use_container_width=True)

    # % berlaku per divisi
    st.markdown("#### Persentase Berlaku per Divisi")
    div_pct = (dff.groupby('Divisi Pemilik Proses')
               .apply(lambda g: round((g.Keterangan == 'Berlaku').sum() / len(g) * 100, 1),
                      include_groups=False)
               .reset_index())
    div_pct.columns = ['Divisi', '% Berlaku']
    div_pct['Label'] = div_pct['Divisi'].apply(shorten_div)
    div_pct = div_pct.sort_values('% Berlaku', ascending=True)

    fig_pct = px.bar(div_pct, x='% Berlaku', y='Label', orientation='h',
        text='% Berlaku', color='% Berlaku',
        color_continuous_scale=[(0,'#FF4444'),(0.7,'#FFC107'),(1,'#70AD47')],
        range_color=[0, 100])
    fig_pct.update_traces(texttemplate='%{text}%', textposition='outside')
    fig_pct.update_layout(
        height=320, margin=dict(t=10, b=10, l=10, r=60),
        coloraxis_showscale=False,
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(range=[0,110], showgrid=True, gridcolor='#eee', ticksuffix='%'),
        yaxis=dict(tickfont=dict(size=10)),
    )
    fig_pct.add_vline(x=100, line_dash='dot', line_color='#70AD47', opacity=0.5)
    fig_pct.add_vline(x=70,  line_dash='dot', line_color='orange',  opacity=0.5)
    st.plotly_chart(fig_pct, use_container_width=True)


# ══════ TAB 2 – TABEL LENGKAP ════════════════════════════════════════════════
with tab2:
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

    tbl_show = (tbl[['No','Nomor Prosedur','Nama Prosedur','Rev','Kategori',
                      'Divisi Pemilik Proses','Tgl Berlaku','Tgl Review','sisa','Keterangan']]
                .rename(columns={'sisa':'Sisa Hari'})
                .reset_index(drop=True))

    styled_tbl = tbl_show.style.apply(
        lambda row: color_row(row, warn_days, crit_days), axis=1)
    st.dataframe(styled_tbl, use_container_width=True, height=500)

    st.download_button("⬇ Download tabel ini",
                       tbl_show.to_csv(index=False).encode('utf-8'),
                       "filtered_data.csv", "text/csv")


# ══════ TAB 3 – PERINGATAN EXPIRED ═══════════════════════════════════════════
with tab3:
    exp_all = (dff[(dff['Keterangan'] == 'Berlaku') & (dff['sisa'] <= warn_days)]
               .sort_values('sisa').reset_index(drop=True))

    if len(exp_all) == 0:
        st.success(f"✅ Tidak ada prosedur yang akan expired dalam {warn_days} hari ke depan.")
    else:
        krit_df  = exp_all[exp_all['sisa'] <= crit_days]
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

        st.markdown("#### Timeline Masa Berlaku (≤ 2 tahun ke depan)")
        tl_df = (dff[(dff['Keterangan'] == 'Berlaku') & (dff['sisa'] <= 730)]
                 .sort_values('sisa').reset_index(drop=True))
        if len(tl_df) > 0:
            tl_df['Status'] = tl_df['sisa'].apply(
                lambda x: '🔴 Kritis' if x <= crit_days
                else ('🟡 Segera' if x <= warn_days else '🟢 Aman'))
            fig_tl = px.bar(
                tl_df, x='sisa', y='Nomor Prosedur', orientation='h',
                color='Status',
                color_discrete_map={
                    '🔴 Kritis': '#FF4444', '🟡 Segera': '#FFC107', '🟢 Aman': '#70AD47'},
                hover_data=['Nama Prosedur', 'Divisi Pemilik Proses', 'Tgl Review'],
                labels={'sisa': 'Sisa Hari'},
            )
            fig_tl.add_vline(x=crit_days, line_dash='dash', line_color='red',
                             annotation_text=f'{crit_days} hr')
            fig_tl.add_vline(x=warn_days, line_dash='dash', line_color='orange',
                             annotation_text=f'{warn_days} hr')
            fig_tl.update_layout(
                height=max(300, len(tl_df) * 22),
                margin=dict(t=10, b=10, l=10, r=10),
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                yaxis=dict(tickfont=dict(size=9)),
                legend=dict(orientation='h', y=1.05),
            )
            st.plotly_chart(fig_tl, use_container_width=True)


# ══════ TAB 4 – PER DIVISI ═══════════════════════════════════════════════════
with tab4:
    div_sum = (dff.groupby('Divisi Pemilik Proses')
               .apply(lambda g: pd.Series({
                   'Total':         len(g),
                   'Berlaku':       int((g.Keterangan == 'Berlaku').sum()),
                   'Tidak Berlaku': int((g.Keterangan == 'Tidak Berlaku').sum()),
                   '% Berlaku':     round((g.Keterangan == 'Berlaku').sum() / len(g) * 100, 1),
                   f'Segera (≤{warn_days}hr)': int(((g.Keterangan == 'Berlaku') & (g.sisa <= warn_days)).sum()),
               }), include_groups=False)
               .reset_index()
               .sort_values('Total', ascending=False))

    styled_div = (div_sum.style
                  .apply(highlight_pct, axis=1)
                  .format({'% Berlaku': '{:.1f}%'}))
    st.dataframe(styled_div, use_container_width=True, height=380)

    st.markdown("#### Detail per Divisi")
    divisi_sel = st.selectbox("Pilih Divisi", sorted(dff['Divisi Pemilik Proses'].unique()))
    sub = dff[dff['Divisi Pemilik Proses'] == divisi_sel].reset_index(drop=True)

    b_s = int((sub.Keterangan == 'Berlaku').sum())
    t_s = len(sub) - b_s
    mc1, mc2, mc3 = st.columns(3)
    mc1.metric("Total", len(sub))
    mc2.metric("Berlaku", b_s)
    mc3.metric("Tidak Berlaku", t_s)

    sub_show = (sub[['No','Nomor Prosedur','Nama Prosedur','Rev','Kategori',
                      'Tgl Berlaku','Tgl Review','sisa','Keterangan']]
                .rename(columns={'sisa':'Sisa Hari'}))
    st.dataframe(
        sub_show.style.apply(lambda row: color_row(row, warn_days, crit_days), axis=1),
        use_container_width=True, height=350)


# ══════ TAB 5 – PER KATEGORI ═════════════════════════════════════════════════
with tab5:
    kat_sum = (dff.groupby('Kategori')
               .apply(lambda g: pd.Series({
                   'Total':         len(g),
                   'Berlaku':       int((g.Keterangan == 'Berlaku').sum()),
                   'Tidak Berlaku': int((g.Keterangan == 'Tidak Berlaku').sum()),
                   '% Berlaku':     round((g.Keterangan == 'Berlaku').sum() / len(g) * 100, 1),
                   f'Segera (≤{warn_days}hr)': int(((g.Keterangan == 'Berlaku') & (g.sisa <= warn_days)).sum()),
               }), include_groups=False)
               .reset_index()
               .sort_values('Total', ascending=False))

    styled_kat = (kat_sum.style
                  .apply(highlight_pct, axis=1)
                  .format({'% Berlaku': '{:.1f}%'}))
    st.dataframe(styled_kat, use_container_width=True, height=380)

    st.markdown("#### Treemap – Proporsi per Kategori & Status")
    tree_df = dff.groupby(['Kategori', 'Keterangan']).size().reset_index(name='Jumlah')
    fig_tree = px.treemap(
        tree_df, path=['Kategori', 'Keterangan'], values='Jumlah',
        color='Keterangan',
        color_discrete_map={'Berlaku': '#70AD47', 'Tidak Berlaku': '#FF4444'},
    )
    fig_tree.update_traces(textinfo='label+value+percent parent')
    fig_tree.update_layout(height=420, margin=dict(t=10, b=10, l=10, r=10),
                           paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_tree, use_container_width=True)

    st.markdown("#### Detail per Kategori")
    kat_sel = st.selectbox("Pilih Kategori", sorted(dff['Kategori'].unique()))
    sub_k = dff[dff['Kategori'] == kat_sel].reset_index(drop=True)
    bk = int((sub_k.Keterangan == 'Berlaku').sum())
    tk = len(sub_k) - bk
    kc1, kc2, kc3 = st.columns(3)
    kc1.metric("Total", len(sub_k))
    kc2.metric("Berlaku", bk)
    kc3.metric("Tidak Berlaku", tk)

    sub_k_show = (sub_k[['No','Nomor Prosedur','Nama Prosedur','Rev',
                          'Divisi Pemilik Proses','Tgl Review','sisa','Keterangan']]
                  .rename(columns={'sisa':'Sisa Hari'}))
    st.dataframe(
        sub_k_show.style.apply(lambda row: color_row(row, warn_days, crit_days), axis=1),
        use_container_width=True, height=320)


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
