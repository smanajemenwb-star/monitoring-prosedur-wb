import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os
import yaml
import streamlit_authenticator as stauth
from yaml.loader import SafeLoader

st.set_page_config(
    page_title="Monitoring Prosedur – WIKA Beton",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Auth Setup ────────────────────────────────────────────────────────────────
config_path = os.path.join(os.path.dirname(__file__), 'config.yaml')
with open(config_path) as f:
    config = yaml.load(f, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
)

# ── Login Page ────────────────────────────────────────────────────────────────
def show_login():
    # Background full page + hapus padding berlebih
    st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #0f2044 0%, #1F3864 50%, #2E75B6 100%) !important;
    }
    [data-testid="stHeader"] { background: transparent !important; }
    [data-testid="stMainBlockContainer"] {
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # Layout: kiri = branding, kanan = form login
    left, right = st.columns([1.2, 1])

    with left:
        st.markdown("""
        <div style='padding:4rem 2rem;color:white;min-height:80vh;
        display:flex;flex-direction:column;justify-content:center'>
            <div style='font-size:3.5rem;margin-bottom:1rem'>🏗️</div>
            <div style='font-size:2rem;font-weight:800;line-height:1.2;
            margin-bottom:0.8rem'>
                PT WIJAYA KARYA<br>BETON Tbk
            </div>
            <div style='width:50px;height:4px;background:#FFC107;
            border-radius:2px;margin-bottom:1.2rem'></div>
            <div style='font-size:1rem;color:#BDD7EE;line-height:1.6;
            margin-bottom:2rem'>
                Dashboard Monitoring<br>
                Daftar Induk Dokumen<br>
                Sistem Manajemen
            </div>
            <div style='background:rgba(255,255,255,0.1);border-radius:12px;
            padding:1rem 1.2rem;display:inline-block;max-width:280px'>
                <div style='font-size:0.7rem;color:#BDD7EE;
                text-transform:uppercase;letter-spacing:0.1em;
                margin-bottom:0.3rem'>Unit Pengelola</div>
                <div style='font-size:0.9rem;font-weight:600;color:white'>
                    DSIM – Kantor Pusat</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with right:
        st.markdown("""
        <div style='padding:3rem 0.5rem'>
        <div style='background:white;border-radius:20px;padding:2.5rem 2rem;
        box-shadow:0 20px 60px rgba(0,0,0,0.3);margin-top:3rem'>
            <div style='text-align:center;margin-bottom:2rem'>
                <div style='background:linear-gradient(135deg,#1F3864,#2E75B6);
                border-radius:14px;padding:0.8rem 1.2rem;
                display:inline-block;margin-bottom:1rem'>
                    <span style='font-size:1.8rem'>📋</span>
                </div>
                <div style='font-size:1.1rem;font-weight:700;color:#1F3864'>
                    Masuk ke Dashboard</div>
                <div style='font-size:0.75rem;color:#999;margin-top:4px'>
                    Gunakan akun yang telah diberikan</div>
            </div>
        </div>
        </div>
        """, unsafe_allow_html=True)

        authenticator.login(location='main', key='login_form')

        if st.session_state.get('authentication_status') is False:
            st.error('❌ Username atau password salah!')
        elif st.session_state.get('authentication_status') is None:
            st.caption('🔒 Silakan masukkan username dan password Anda.')

# ── Welcome Page ──────────────────────────────────────────────────────────────
def show_welcome():
    name = st.session_state.get('name', 'User')
    role = config['credentials']['usernames'].get(
        st.session_state.get('username', ''), {}
    ).get('role', 'user')

    # Load data untuk resume
    try:
        _df = load_data()
        _total   = len(_df)
        _berlaku = int((_df['Keterangan'] == 'Berlaku').sum())
        _tidak   = int((_df['Keterangan'] == 'Tidak Berlaku').sum())
        _kritis  = int(((_df['Keterangan'] == 'Berlaku') & (_df['sisa'] <= 30)).sum())
        _segera  = int(((_df['Keterangan'] == 'Berlaku') & (_df['sisa'] <= 90)).sum())
        _pct     = round(_berlaku / _total * 100, 1) if _total > 0 else 0
        _data_ok = True
    except:
        _data_ok = False

    # Header welcome
    st.markdown(f"""
    <div style='background:linear-gradient(135deg,#1F3864,#2E75B6);
    border-radius:16px;padding:2rem 2rem 1.5rem;text-align:center;margin-bottom:1.5rem'>
        <div style='font-size:2.5rem;margin-bottom:0.5rem'>👋</div>
        <div style='color:white;font-size:1.6rem;font-weight:700'>
            Selamat Datang, {name}!</div>
        <div style='color:#BDD7EE;font-size:0.85rem;margin-top:6px'>
            PT Wijaya Karya Beton Tbk &nbsp;|&nbsp; DSIM – Kantor Pusat</div>
        <div style='background:rgba(255,255,255,0.15);border-radius:8px;
        padding:0.3rem 0.8rem;display:inline-block;margin-top:0.8rem'>
            <span style='color:white;font-size:0.75rem'>Role: {role.upper()}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Resume KPI ──────────────────────────────────────────────────────────
    if _data_ok:
        st.markdown("<div style='font-size:0.8rem;font-weight:700;color:#2E75B6;"
                    "text-transform:uppercase;letter-spacing:0.06em;"
                    "border-left:3px solid #2E75B6;padding-left:8px;"
                    "margin-bottom:0.8rem'>📊 Resume Terkini</div>",
                    unsafe_allow_html=True)

        k1, k2, k3, k4, k5 = st.columns(5)
        def mini_kpi(col, label, val, sub, color):
            col.markdown(f"""
            <div style='background:white;border-radius:10px;padding:0.9rem 0.8rem;
            box-shadow:0 2px 8px rgba(0,0,0,0.07);border-left:4px solid {color};
            margin-bottom:0.5rem'>
                <div style='font-size:0.65rem;color:#888;font-weight:600;
                text-transform:uppercase'>{label}</div>
                <div style='font-size:1.8rem;font-weight:700;color:{color};
                line-height:1.1'>{val}</div>
                <div style='font-size:0.7rem;color:#666'>{sub}</div>
            </div>""", unsafe_allow_html=True)

        mini_kpi(k1, "Total",        _total,   "prosedur",          "#2E75B6")
        mini_kpi(k2, "Berlaku",      _berlaku, f"{_pct}% dari total","#375623")
        mini_kpi(k3, "Tidak Berlaku",_tidak,   "perlu diperbarui",  "#9C0006")
        mini_kpi(k4, "Segera ≤90hr", _segera,  "perlu ditindaklanjuti","#B26800")
        mini_kpi(k5, "Kritis ≤30hr", _kritis,  "harus diperbarui!", "#9C0006")

        # ── Resume per Divisi & Kategori ────────────────────────────────────
        st.markdown("<br>", unsafe_allow_html=True)
        col_div, col_kat = st.columns(2)

        with col_div:
            st.markdown("<div style='font-size:0.8rem;font-weight:700;color:#2E75B6;"
                        "text-transform:uppercase;letter-spacing:0.06em;"
                        "border-left:3px solid #2E75B6;padding-left:8px;"
                        "margin-bottom:0.8rem'>📁 Per Divisi</div>",
                        unsafe_allow_html=True)
            div_sum = (_df.groupby('Divisi Pemilik Proses')
                       .apply(lambda g: pd.Series({
                           'Total':   len(g),
                           'Berlaku': int((g.Keterangan=='Berlaku').sum()),
                           'Tidak':   int((g.Keterangan=='Tidak Berlaku').sum()),
                           '%':       round((g.Keterangan=='Berlaku').sum()/len(g)*100,1),
                       }), include_groups=False)
                       .reset_index()
                       .sort_values('Total', ascending=False))
            div_sum['Divisi'] = div_sum['Divisi Pemilik Proses'].apply(shorten_div)
            div_sum = div_sum[['Divisi','Total','Berlaku','Tidak','%']]
            div_sum.columns = ['Divisi','Total','Berlaku','Tdk Berlaku','% Berlaku']
            st.dataframe(
                div_sum.style.format({'% Berlaku':'{:.1f}%','Total':'{:.0f}',
                                      'Berlaku':'{:.0f}','Tdk Berlaku':'{:.0f}'}),
                use_container_width=True, height=300, hide_index=True
            )

        with col_kat:
            st.markdown("<div style='font-size:0.8rem;font-weight:700;color:#2E75B6;"
                        "text-transform:uppercase;letter-spacing:0.06em;"
                        "border-left:3px solid #2E75B6;padding-left:8px;"
                        "margin-bottom:0.8rem'>🏷️ Per Kategori</div>",
                        unsafe_allow_html=True)
            kat_sum = (_df.groupby('Kategori')
                       .apply(lambda g: pd.Series({
                           'Total':   len(g),
                           'Berlaku': int((g.Keterangan=='Berlaku').sum()),
                           'Tidak':   int((g.Keterangan=='Tidak Berlaku').sum()),
                           '%':       round((g.Keterangan=='Berlaku').sum()/len(g)*100,1),
                       }), include_groups=False)
                       .reset_index()
                       .sort_values('Total', ascending=False))
            kat_sum.columns = ['Kategori','Total','Berlaku','Tdk Berlaku','% Berlaku']
            st.dataframe(
                kat_sum.style.format({'% Berlaku':'{:.1f}%','Total':'{:.0f}',
                                      'Berlaku':'{:.0f}','Tdk Berlaku':'{:.0f}'}),
                use_container_width=True, height=300, hide_index=True
            )

        # ── Tabel Masa Berlaku & Expired ────────────────────────────────────
        st.markdown("<br>", unsafe_allow_html=True)
        col_exp, col_mb = st.columns(2)

        with col_exp:
            st.markdown("<div style='font-size:0.8rem;font-weight:700;color:#9C0006;"
                        "text-transform:uppercase;letter-spacing:0.06em;"
                        "border-left:3px solid #9C0006;padding-left:8px;"
                        "margin-bottom:0.8rem'>⚠️ Sudah / Akan Expired (≤90 hari)</div>",
                        unsafe_allow_html=True)
            _exp = (_df[(_df['Keterangan']=='Berlaku') & (_df['sisa']<=90)]
                    [['Nomor Prosedur','Nama Prosedur','Divisi Pemilik Proses','sisa']]
                    .sort_values('sisa')
                    .reset_index(drop=True))
            _exp.columns = ['Nomor','Nama Prosedur','Divisi','Sisa Hari']
            _exp['Divisi'] = _exp['Divisi'].apply(shorten_div)
            if len(_exp) == 0:
                st.success("✅ Tidak ada prosedur yang akan expired dalam 90 hari!")
            else:
                def style_sisa(val):
                    if val <= 30: return 'color:#9C0006;font-weight:bold'
                    return 'color:#B26800;font-weight:bold'
                st.dataframe(
                    _exp.style.applymap(style_sisa, subset=['Sisa Hari'])
                              .format({'Sisa Hari':'{:.0f}'}),
                    use_container_width=True, height=250, hide_index=True
                )

        with col_mb:
            st.markdown("<div style='font-size:0.8rem;font-weight:700;color:#9C0006;"
                        "text-transform:uppercase;letter-spacing:0.06em;"
                        "border-left:3px solid #9C0006;padding-left:8px;"
                        "margin-bottom:0.8rem'>❌ Tidak Berlaku (Expired)</div>",
                        unsafe_allow_html=True)
            _tdk = (_df[_df['Keterangan']=='Tidak Berlaku']
                    [['Nomor Prosedur','Nama Prosedur','Divisi Pemilik Proses','sisa']]
                    .sort_values('sisa')
                    .reset_index(drop=True))
            _tdk.columns = ['Nomor','Nama Prosedur','Divisi','Sisa Hari']
            _tdk['Divisi'] = _tdk['Divisi'].apply(shorten_div)
            _tdk['Sisa Hari'] = _tdk['Sisa Hari'].abs()
            if len(_tdk) == 0:
                st.success("✅ Semua prosedur masih berlaku!")
            else:
                st.dataframe(
                    _tdk.style.format({'Sisa Hari':'{:.0f} hari lalu'}),
                    use_container_width=True, height=250, hide_index=True
                )

    st.markdown("<br>", unsafe_allow_html=True)
    col_btn1, col_btn2, col_btn3 = st.columns([1,1,1])
    with col_btn2:
        if st.button("🚀 Masuk ke Dashboard Lengkap", use_container_width=True, type="primary"):
            st.session_state['show_welcome'] = False
            st.rerun()

# ── Session State Init ────────────────────────────────────────────────────────
if 'show_welcome' not in st.session_state:
    st.session_state['show_welcome'] = True

# ── Routing ───────────────────────────────────────────────────────────────────
auth_status = st.session_state.get('authentication_status')

if not auth_status:
    show_login()
    st.stop()
elif auth_status and st.session_state.get('show_welcome', True):
    # Tombol logout di sidebar
    with st.sidebar:
        authenticator.logout('🚪 Logout', location='sidebar', key='logout_welcome')
    show_welcome()
    st.stop()

st.markdown("""
<style>
    /* ── Force light mode regardless of OS/browser setting ── */
    html, body, [data-testid="stAppViewContainer"],
    [data-testid="stSidebar"], [data-testid="stHeader"],
    [data-testid="stToolbar"], [data-testid="stDecoration"],
    .main, .block-container, section[data-testid="stSidebar"] > div {
        background-color: #f4f6fa !important;
        color: #1a1a2e !important;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #ffffff !important;
        border-right: 1px solid #e0e4ed !important;
    }
    [data-testid="stSidebar"] * { color: #1a1a2e !important; }

    /* Widget labels & text */
    label, p, span, div, h1, h2, h3, h4, h5, h6,
    .stMarkdown, .stText {
        color: #1a1a2e !important;
    }

    /* Selectbox, slider, multiselect */
    [data-testid="stSelectbox"] > div,
    [data-testid="stMultiSelect"] > div {
        background-color: #ffffff !important;
        border: 1px solid #d0d5e0 !important;
        color: #1a1a2e !important;
    }

    /* Tab styling */
    [data-testid="stTabs"] [role="tablist"] {
        background-color: #ffffff !important;
        border-bottom: 2px solid #e0e4ed !important;
    }
    [data-testid="stTabs"] button[role="tab"] {
        color: #555 !important;
        background: transparent !important;
    }
    [data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
        color: #2E75B6 !important;
        border-bottom: 2px solid #2E75B6 !important;
    }

    /* Dataframe / table */
    [data-testid="stDataFrame"] { background: #ffffff !important; }
    .stDataFrame th { background-color: #eef2f7 !important; color: #1a1a2e !important; }
    .stDataFrame td { background-color: #ffffff !important; color: #1a1a2e !important; }

    /* Metric */
    [data-testid="stMetric"] { background: #ffffff !important; border-radius: 8px; }
    [data-testid="stMetricValue"] { color: #1a1a2e !important; }

    /* Download button */
    .stDownloadButton button {
        background-color: #2E75B6 !important;
        color: white !important;
        border-radius: 8px !important;
    }

    /* Input text */
    [data-testid="stTextInput"] input {
        background-color: #ffffff !important;
        color: #1a1a2e !important;
        border: 1px solid #d0d5e0 !important;
    }

    .block-container { padding: 1.5rem 2rem; }

    /* KPI Cards */
    .kpi-card {
        background: #ffffff; border-radius: 12px;
        padding: 1.1rem 1.2rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.07);
        border-left: 5px solid #ccc; margin-bottom: 0.5rem;
    }
    .kpi-label { font-size: 0.72rem; color: #888 !important; font-weight: 600;
                 text-transform: uppercase; letter-spacing: 0.05em; }
    .kpi-value { font-size: 2.2rem; font-weight: 700; line-height: 1.1; }
    .kpi-sub   { font-size: 0.75rem; color: #666 !important; margin-top: 2px; }
    .kpi-blue   { border-color: #2E75B6; } .kpi-blue   .kpi-value { color: #2E75B6 !important; }
    .kpi-green  { border-color: #375623; } .kpi-green  .kpi-value { color: #375623 !important; }
    .kpi-red    { border-color: #9C0006; } .kpi-red    .kpi-value { color: #9C0006 !important; }
    .kpi-orange { border-color: #B26800; } .kpi-orange .kpi-value { color: #B26800 !important; }

    .alert-box {
        background: #fff3cd; border: 1px solid #ffc107;
        border-radius: 8px; padding: 0.7rem 1rem; margin: 0.3rem 0;
    }
    .alert-box-red {
        background: #fde8e8; border: 1px solid #f87171;
        border-radius: 8px; padding: 0.7rem 1rem; margin: 0.3rem 0;
    }
    .section-title {
        font-size: 0.8rem; font-weight: 600; color: #2E75B6 !important;
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

    # Normalize column names: strip leading/trailing whitespace
    df.columns = df.columns.str.strip()

    # Rename any case/spelling variant of 'Kategori' to the expected name
    kat_candidates = [c for c in df.columns if c.lower() == 'kategori']
    if kat_candidates and kat_candidates[0] != 'Kategori':
        df.rename(columns={kat_candidates[0]: 'Kategori'}, inplace=True)

    # If Kategori column is still missing, create a placeholder
    if 'Kategori' not in df.columns:
        df['Kategori'] = 'Tidak Dikategorikan'

    df['Kategori'] = df['Kategori'].fillna('Tidak Dikategorikan').str.strip()

    df['sisa'] = pd.to_numeric(df['sisa'], errors='coerce').fillna(0).astype(int)
    df['Keterangan'] = df['Keterangan'].str.strip()
    df['Divisi Pemilik Proses'] = df['Divisi Pemilik Proses'].fillna('Tidak Diketahui').str.strip()
    df['Nama Prosedur'] = df['Nama Prosedur'].str.strip()
    df['Nomor Prosedur'] = df['Nomor Prosedur'].str.strip()
    df['Tgl_Berlaku_dt'] = pd.to_datetime(df['Tgl Berlaku'], errors='coerce', dayfirst=True)
    df['Tgl_Review_dt']  = pd.to_datetime(df['Tgl Review'],  errors='coerce', dayfirst=True)
    return df

@st.cache_data
def load_trend():
    """Baca data tren dari data_trend.csv (di-generate dari sheet TrendProsedur)."""
    path = os.path.join(os.path.dirname(__file__), 'data_trend.csv')
    if not os.path.exists(path):
        return None
    try:
        df_t = pd.read_csv(path)
        df_t.columns = df_t.columns.str.strip()
        df_t = df_t.dropna(subset=['Tahun', 'Jumlah Prosedur'])
        df_t['Tahun'] = df_t['Tahun'].astype(int)
        df_t['Jumlah Prosedur'] = df_t['Jumlah Prosedur'].astype(int)
        df_t = df_t.sort_values('Tahun').reset_index(drop=True)
        df_t['Perubahan'] = df_t['Jumlah Prosedur'].diff().fillna(0).astype(int)
        df_t['% Perubahan'] = (df_t['Jumlah Prosedur'].pct_change() * 100).round(1).fillna(0)
        return df_t
    except Exception:
        return None

df = load_data()
df_trend = load_trend()
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
                s = 'background-color:#fff5f5;color:#000000'
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
    st.markdown(f"Update: {today.strftime('%d %B %Y')}  \nDivisi: DSIM  \nTanggal: {today.strftime('%d %b %Y')}")
    st.divider()
    # Info user & logout
    name = st.session_state.get('name', '')
    username = st.session_state.get('username', '')
    role = config['credentials']['usernames'].get(username, {}).get('role', 'user')
    st.markdown(f"👤 **{name}** `{role}`")
    authenticator.logout('🚪 Logout', location='sidebar', key='logout_dashboard')
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

    # ── Admin: Update Data via GitHub ──────────────────────────────────────
    username = st.session_state.get('username', '')
    role = config['credentials']['usernames'].get(username, {}).get('role', 'user')

    if role == 'admin':
        st.divider()
        st.markdown("#### 🔧 Admin — Update Data")

        uploaded_xl = st.file_uploader(
            "Upload Excel terbaru (.xlsx)",
            type=['xlsx'],
            help="Sheet '20 April 2026' atau sheet terbaru akan dibaca otomatis"
        )

        if uploaded_xl is not None:
            st.info(f"File: **{uploaded_xl.name}**")

            if st.button("🚀 Proses & Update ke GitHub", type="primary", use_container_width=True):
                import io, base64, requests
                from datetime import datetime as dt

                try:
                    with st.spinner("Membaca & mengkonversi Excel..."):
                        # Baca semua sheet names
                        xl = pd.ExcelFile(uploaded_xl)
                        sheets = xl.sheet_names

                        # Baca langsung sheet pertama (single sheet)
                        target_sheet = sheets[0]
                        st.write(f"📄 Sheet: **{target_sheet}**")
                        df_raw2 = pd.read_excel(uploaded_xl, sheet_name=0, header=None)
                        today_d = dt.today().date()

                        # Ambil baris yang ada nomor prosedur WB-
                        records2 = []
                        for i, row in df_raw2.iterrows():
                            nomor = str(row.iloc[4]).strip() if row.iloc[4] is not None else ''
                            if nomor.startswith('WB-'):
                                records2.append({
                                    'No':                    row.iloc[0],
                                    'Nomor Prosedur':        nomor,
                                    'Nama Prosedur':         str(row.iloc[12]).strip() if row.iloc[12] else '',
                                    'Rev':                   str(row.iloc[24]).strip() if row.iloc[24] else '',
                                    'Divisi Pemilik Proses': str(row.iloc[68]).strip() if row.iloc[68] else '',
                                    'Tgl Berlaku':           row.iloc[78],
                                    'Tgl Review':            row.iloc[85],
                                })

                        if not records2:
                            st.error("Data prosedur tidak ditemukan di sheet tersebut!")
                            st.stop()

                        df_new = pd.DataFrame(records2)
                        df_new['Kategori'] = df_new['Nomor Prosedur'].str.extract(r'WB-([A-Z]+)-')

                        def parse_tgl2(val):
                            if pd.isnull(val) or val is None: return ''
                            if isinstance(val, (dt,)):
                                return val.strftime('%d/%m/%Y')
                            s = str(val).strip()
                            for fmt in ['%d/%m/%y', '%d/%m/%Y', '%Y-%m-%d']:
                                try: return dt.strptime(s.split(' ')[0], fmt).strftime('%d/%m/%Y')
                                except: pass
                            return s

                        df_new['Tgl Berlaku'] = df_new['Tgl Berlaku'].apply(parse_tgl2)
                        df_new['Tgl Review']  = df_new['Tgl Review'].apply(parse_tgl2)

                        def hitung_sisa2(tgl_str):
                            for fmt in ['%d/%m/%Y', '%d/%m/%y']:
                                try: return (dt.strptime(tgl_str, fmt).date() - today_d).days
                                except: pass
                            return 0

                        df_new['sisa'] = df_new['Tgl Review'].apply(hitung_sisa2)
                        df_new['Masa Berlaku'] = df_new['sisa'].apply(
                            lambda x: f"{abs(x)} hari lagi" if x >= 0 else f"{abs(x)} hari yang lalu"
                        )
                        df_new['Keterangan'] = df_new['sisa'].apply(
                            lambda x: 'Berlaku' if x >= 0 else 'Tidak Berlaku'
                        )
                        df_new['No'] = range(1, len(df_new) + 1)
                        df_new = df_new[['No', 'Nomor Prosedur', 'Nama Prosedur', 'Rev',
                                         'Kategori', 'Divisi Pemilik Proses',
                                         'Tgl Berlaku', 'Tgl Review', 'sisa', 'Masa Berlaku', 'Keterangan']]

                    st.success(f"✅ Konversi berhasil: {len(df_new)} prosedur")

                    # ── Proses sheet TrendProsedur jika ada ──────────────────
                    df_trend_new = None
                    xl2 = pd.ExcelFile(uploaded_xl)
                    if 'TrendProsedur' in xl2.sheet_names:
                        try:
                            raw_trend = pd.read_excel(uploaded_xl, sheet_name='TrendProsedur', header=None)
                            df_trend_new = raw_trend.iloc[1:].copy()
                            df_trend_new.columns = ['No', 'Tahun', 'Jumlah Prosedur']
                            df_trend_new = df_trend_new.dropna(subset=['Tahun', 'Jumlah Prosedur'])
                            df_trend_new['Tahun'] = df_trend_new['Tahun'].astype(int)
                            df_trend_new['Jumlah Prosedur'] = df_trend_new['Jumlah Prosedur'].astype(int)
                            df_trend_new = df_trend_new[['Tahun', 'Jumlah Prosedur']]
                            st.success(f"✅ Data tren berhasil dibaca: {len(df_trend_new)} tahun")
                        except Exception as e_trend:
                            st.warning(f"⚠️ Sheet TrendProsedur gagal dibaca: {e_trend}")
                            df_trend_new = None
                    else:
                        st.info("ℹ️ Sheet 'TrendProsedur' tidak ditemukan — data tren tidak diupdate.")

                    with st.spinner("Mengupload ke GitHub..."):
                        # Ambil config dari Streamlit secrets
                        gh_token  = st.secrets["github"]["token"]
                        gh_owner  = st.secrets["github"]["owner"]
                        gh_repo   = st.secrets["github"]["repo"]
                        gh_branch = st.secrets["github"].get("branch", "main")
                        gh_path   = st.secrets["github"].get("file_path", "data.csv")
                        gh_trend_path = st.secrets["github"].get("trend_file_path", "data_trend.csv")

                        gh_headers = {
                            "Authorization": f"token {gh_token}",
                            "Accept": "application/vnd.github.v3+json"
                        }

                        def push_to_github(file_path, csv_bytes, commit_msg):
                            api_url = f"https://api.github.com/repos/{gh_owner}/{gh_repo}/contents/{file_path}"
                            r_get = requests.get(api_url, headers=gh_headers, params={"ref": gh_branch})
                            sha = r_get.json().get("sha", "") if r_get.status_code == 200 else ""
                            csv_b64 = base64.b64encode(csv_bytes).decode('utf-8')
                            payload = {"message": commit_msg, "content": csv_b64, "branch": gh_branch}
                            if sha:
                                payload["sha"] = sha
                            return requests.put(api_url, headers=gh_headers, json=payload)

                        commit_msg = f"Update data via dashboard - {dt.now().strftime('%d/%m/%Y %H:%M')} by {username}"

                        # Upload data.csv
                        r_put = push_to_github(
                            gh_path,
                            df_new.to_csv(index=False).encode('utf-8'),
                            commit_msg
                        )

                        # Upload data_trend.csv jika ada
                        r_trend = None
                        if df_trend_new is not None:
                            r_trend = push_to_github(
                                gh_trend_path,
                                df_trend_new.to_csv(index=False).encode('utf-8'),
                                commit_msg + " [+trend]"
                            )

                        if r_put.status_code in [200, 201]:
                            st.success("✅ data.csv berhasil diupdate ke GitHub!")
                            if r_trend is not None:
                                if r_trend.status_code in [200, 201]:
                                    st.success("✅ data_trend.csv berhasil diupdate ke GitHub!")
                                else:
                                    st.error(f"❌ Gagal upload data_trend.csv: {r_trend.json().get('message', 'Unknown error')}")
                            st.info("Dashboard akan refresh otomatis dalam beberapa detik...")
                            st.cache_data.clear()
                            st.rerun()
                        else:
                            st.error(f"❌ Gagal upload ke GitHub: {r_put.json().get('message', 'Unknown error')}")

                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")


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
DSIM \u2013 Kantor Pusat &nbsp;|&nbsp; Form: WB-QMS-PS-01-F08 Rev.02</div>
</div>
""", unsafe_allow_html=True)

# ── KPI ───────────────────────────────────────────────────────────────────────
c1, c2, c3, c4, c5 = st.columns(5)
kpi(c1, "Total Prosedur",          total,  f"data per {today.strftime('%d %B %Y')}",  "kpi-blue")
kpi(c2, "Berlaku",                  berl,   f"{pct_b}% dari total",               "kpi-green")
kpi(c3, "Tidak Berlaku",            tidak,  f"{round(tidak/total*100,1) if total else 0}% perlu diperbarui", "kpi-red")
kpi(c4, f"Segera ≤{warn_days}hr",  warn_n, "perlu segera ditindaklanjuti",        "kpi-orange")
kpi(c5, f"Kritis ≤{crit_days}hr",  krit_n, "harus diperbarui sekarang!",          "kpi-red")

st.markdown("<br>", unsafe_allow_html=True)

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "📊 Grafik Utama",
    "🔬 Grafik Lanjutan",
    "📋 Tabel Lengkap",
    "⚠️ Peringatan Expired",
    "🏢 Per Divisi",
    "🗂️ Per Kategori",
    "📈 Tren Historis",
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
        transition={'duration': 600, 'easing': 'cubic-in-out'},
            height=280, margin=dict(t=60, b=20, l=30, r=30),
            paper_bgcolor="rgba(0,0,0,0)", font={"color": "#1F3864"},
        )
        st.plotly_chart(fig_gauge, use_container_width=True, key="chart_gauge")

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
        transition={'duration': 600, 'easing': 'cubic-in-out'},
            height=280, margin=dict(t=20, b=30, l=10, r=10),
            legend=dict(orientation='h', y=-0.15, x=0.5, xanchor='center'),
            paper_bgcolor='rgba(0,0,0,0)',
            annotations=[dict(text=f'<b>{total}</b><br>Total', x=0.5, y=0.5,
                              font_size=14, showarrow=False)],
        )
        st.plotly_chart(fig_pie, use_container_width=True, key="chart_pie")

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
        transition={'duration': 600, 'easing': 'cubic-in-out'},
            barmode='stack', height=360,
            margin=dict(t=10, b=10, l=10, r=40),
            legend=dict(orientation='h', y=1.05, x=0.5, xanchor='center'),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(showgrid=True, gridcolor='#eee'),
            yaxis=dict(tickfont=dict(size=10)),
        )
        st.plotly_chart(fig_bar, use_container_width=True, key="chart_bar")

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
        transition={'duration': 600, 'easing': 'cubic-in-out'},
            barmode='stack', height=360,
            margin=dict(t=10, b=10, l=10, r=10),
            legend=dict(orientation='h', y=1.05, x=0.5, xanchor='center'),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(tickangle=45), yaxis=dict(showgrid=True, gridcolor='#eee'),
        )
        st.plotly_chart(fig_kat, use_container_width=True, key="chart_kat")

    # ── Heatmap Divisi vs Status ───────────────────────────────────────────────
    section("Pencapaian Target Berlaku per Divisi")
    st.markdown("##### Heatmap — Divisi vs Status Prosedur")

    # Pivot: baris=Divisi, kolom=Status, nilai=jumlah
    heat_df = (dff.groupby(['Divisi Pemilik Proses', 'Keterangan'])
               .size().reset_index(name='Jumlah'))
    heat_pivot = heat_df.pivot(index='Divisi Pemilik Proses',
                               columns='Keterangan', values='Jumlah').fillna(0)

    # Pastikan kedua kolom ada
    for col in ['Berlaku', 'Tidak Berlaku']:
        if col not in heat_pivot.columns:
            heat_pivot[col] = 0
    heat_pivot = heat_pivot[['Berlaku', 'Tidak Berlaku']]

    # Tambah kolom % Berlaku dan urutkan
    heat_pivot['% Berlaku'] = (heat_pivot['Berlaku'] /
                                (heat_pivot['Berlaku'] + heat_pivot['Tidak Berlaku']) * 100).round(1)
    heat_pivot = heat_pivot.sort_values('% Berlaku', ascending=False)
    heat_pivot['Label'] = heat_pivot.index.map(shorten_div)

    # Data untuk heatmap: 2 kolom status saja
    z_vals  = heat_pivot[['Berlaku', 'Tidak Berlaku']].values.tolist()
    y_labels = heat_pivot['Label'].tolist()
    x_labels = ['Berlaku', 'Tidak Berlaku']

    # Teks anotasi tiap cell
    text_vals = [[f"{int(row[0])}", f"{int(row[1])}"] for row in z_vals]

    fig_heat = go.Figure(go.Heatmap(
        z=z_vals,
        x=x_labels,
        y=y_labels,
        text=text_vals,
        texttemplate="%{text}",
        textfont=dict(size=12, color='white'),
        colorscale=[
            [0.0, '#fde8e8'],
            [0.3, '#FFC107'],
            [1.0, '#375623'],
        ],
        showscale=True,
        colorbar=dict(title='Jumlah', thickness=12, len=0.8),
        hovertemplate='<b>%{y}</b><br>%{x}: %{text} prosedur<extra></extra>',
    ))

    # Tambah kolom % Berlaku sebagai anotasi di kanan
    for i, (_, row) in enumerate(heat_pivot.iterrows()):
        pct = row['% Berlaku']
        col_pct = '#375623' if pct >= 80 else '#B26800' if pct >= 60 else '#9C0006'
        fig_heat.add_annotation(
            x=2.05, y=row['Label'],
            text=f"<b>{pct}%</b>",
            showarrow=False,
            xref='x', yref='y',
            font=dict(size=10, color=col_pct),
            xanchor='left',
        )

    fig_heat.add_shape(
        type='line', x0=1.5, x1=1.5, y0=-0.5, y1=len(y_labels)-0.5,
        line=dict(color='#ccc', width=1, dash='dot'),
    )

    fig_heat.update_layout(
        transition={'duration': 600, 'easing': 'cubic-in-out'},
        height=max(300, len(y_labels) * 38),
        margin=dict(t=20, b=20, l=10, r=80),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(side='top', tickfont=dict(size=11, color='#333')),
        yaxis=dict(tickfont=dict(size=10), autorange='reversed'),
    )
    st.plotly_chart(fig_heat, use_container_width=True, key="chart_heat_tab1")


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2 – GRAFIK LANJUTAN
# ═══════════════════════════════════════════════════════════════════════════════
with tab2:

    # ── Sunburst ───────────────────────────────────────────────────────────────
    section("Hierarki Drill-Down")
    s1, s2 = st.columns(2)

    with s1:
        st.markdown("##### Multi-line — Berlaku vs Tidak Berlaku per Divisi")

        # Hitung jumlah per Divisi per Status
        ml_df = (dff.groupby(['Divisi Pemilik Proses', 'Keterangan'])
                 .size().reset_index(name='Jumlah'))
        ml_df['Label'] = ml_df['Divisi Pemilik Proses'].apply(shorten_div)

        # Pisahkan berlaku dan tidak berlaku
        ml_berlaku    = ml_df[ml_df['Keterangan'] == 'Berlaku'].sort_values('Label')
        ml_tidak      = ml_df[ml_df['Keterangan'] == 'Tidak Berlaku'].sort_values('Label')

        # Pastikan urutan label sama
        all_labels = sorted(ml_df['Label'].unique())
        berlaku_map = ml_berlaku.set_index('Label')['Jumlah'].reindex(all_labels, fill_value=0)
        tidak_map   = ml_tidak.set_index('Label')['Jumlah'].reindex(all_labels, fill_value=0)

        fig_ml = go.Figure()

        # Garis Berlaku
        fig_ml.add_trace(go.Scatter(
            x=all_labels,
            y=berlaku_map.values,
            mode='lines+markers',
            name='Berlaku',
            line=dict(color='#70AD47', width=2.5),
            marker=dict(size=7, symbol='circle'),
            hovertemplate='<b>%{x}</b><br>Berlaku: %{y}<extra></extra>',
        ))

        # Garis Tidak Berlaku
        fig_ml.add_trace(go.Scatter(
            x=all_labels,
            y=tidak_map.values,
            mode='lines+markers',
            name='Tidak Berlaku',
            line=dict(color='#FF4444', width=2.5),
            marker=dict(size=7, symbol='circle'),
            hovertemplate='<b>%{x}</b><br>Tidak Berlaku: %{y}<extra></extra>',
        ))

        fig_ml.update_layout(
        transition={'duration': 600, 'easing': 'cubic-in-out'},
            height=460,
            margin=dict(t=20, b=100, l=10, r=10),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
            xaxis=dict(tickangle=-35, tickfont=dict(size=9),
                       showgrid=True, gridcolor='#eee'),
            yaxis=dict(showgrid=True, gridcolor='#eee',
                       title='Jumlah Prosedur'),
        )
        st.plotly_chart(fig_ml, use_container_width=True, key="chart_ml")

    with s2:
        st.markdown("##### Area Band — Range Sisa Hari per Divisi (Prosedur Berlaku)")

        # Hitung min, max, rata-rata sisa hari per divisi, hanya Berlaku
        band_df = (dff[dff['Keterangan'] == 'Berlaku']
                   .groupby('Divisi Pemilik Proses')['sisa']
                   .agg(sisa_min='min', sisa_max='max', sisa_avg='mean')
                   .reset_index())
        band_df['Label'] = band_df['Divisi Pemilik Proses'].apply(shorten_div)
        band_df = band_df.sort_values('sisa_avg', ascending=False).reset_index(drop=True)

        fig_band = go.Figure()

        # Area luar: min - max (range penuh) — biru muda
        fig_band.add_trace(go.Scatter(
            x=band_df['Label'].tolist() + band_df['Label'].tolist()[::-1],
            y=band_df['sisa_max'].tolist() + band_df['sisa_min'].tolist()[::-1],
            fill='toself',
            fillcolor='rgba(46,117,182,0.15)',
            line=dict(color='rgba(0,0,0,0)'),
            name='Range (Min–Max)',
            hoverinfo='skip',
        ))

        # Area tengah: avg ± 20% sebagai "band rata-rata" — biru sedang
        fig_band.add_trace(go.Scatter(
            x=band_df['Label'].tolist() + band_df['Label'].tolist()[::-1],
            y=(band_df['sisa_avg'] * 1.15).tolist() + (band_df['sisa_avg'] * 0.85).tolist()[::-1],
            fill='toself',
            fillcolor='rgba(46,117,182,0.30)',
            line=dict(color='rgba(0,0,0,0)'),
            name='Rentang ±15% Rata-rata',
            hoverinfo='skip',
        ))

        # Garis rata-rata — biru tua
        fig_band.add_trace(go.Scatter(
            x=band_df['Label'],
            y=band_df['sisa_avg'].round(0),
            mode='lines+markers',
            name='Rata-rata Sisa Hari',
            line=dict(color='#1F3864', width=2.5),
            marker=dict(size=7),
            hovertemplate='<b>%{x}</b><br>Rata-rata: %{y:.0f} hari<extra></extra>',
        ))

        # Garis threshold 90 hari (peringatan)
        fig_band.add_hline(y=90, line_dash='dot', line_color='#FFC107', line_width=1.5,
                           annotation_text='Peringatan 90hr',
                           annotation_position='top right',
                           annotation=dict(font=dict(size=9, color='#B26800')))

        # Garis threshold 30 hari (kritis)
        fig_band.add_hline(y=30, line_dash='dot', line_color='#FF4444', line_width=1.5,
                           annotation_text='Kritis 30hr',
                           annotation_position='bottom right',
                           annotation=dict(font=dict(size=9, color='#9C0006')))

        fig_band.update_layout(
        transition={'duration': 600, 'easing': 'cubic-in-out'},
            height=460,
            margin=dict(t=20, b=100, l=10, r=10),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1,
                        font=dict(size=9)),
            xaxis=dict(tickangle=-35, tickfont=dict(size=9),
                       showgrid=True, gridcolor='#eee'),
            yaxis=dict(showgrid=True, gridcolor='#eee',
                       title='Sisa Hari'),
        )
        st.plotly_chart(fig_band, use_container_width=True, key="chart_band")

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
        transition={'duration': 600, 'easing': 'cubic-in-out'},
            height=420,
            polar=dict(
                radialaxis=dict(visible=True,
                                range=[0, kat_pol['Berlaku'].max() + 2]),
                angularaxis=dict(tickfont=dict(size=10)),
            ),
            legend=dict(orientation='h', y=-0.1, x=0.5, xanchor='center'),
            paper_bgcolor='rgba(0,0,0,0)',
        )
        st.plotly_chart(fig_polar, use_container_width=True, key="chart_polar")

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
        transition={'duration': 600, 'easing': 'cubic-in-out'},
            height=420, margin=dict(t=20, b=10, l=10, r=10),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(showgrid=True, gridcolor='#eee'),
            yaxis=dict(tickfont=dict(size=10)),
            legend=dict(orientation='h', y=1.05, x=0.5, xanchor='center'),
        )
        st.plotly_chart(fig_sc, use_container_width=True, key="chart_sc")

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
        transition={'duration': 600, 'easing': 'cubic-in-out'},
            height=420, margin=dict(t=20, b=60, l=10, r=10),
            paper_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(tickangle=45, tickfont=dict(size=9)),
            yaxis=dict(tickfont=dict(size=9)),
        )
        st.plotly_chart(fig_heat, use_container_width=True, key="chart_heat_tab5")

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
        transition={'duration': 600, 'easing': 'cubic-in-out'},
            height=320, margin=dict(t=10, b=10, l=10, r=10),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(showgrid=True, gridcolor='#eee'),
            yaxis=dict(showgrid=True, gridcolor='#eee'),
        )
        st.plotly_chart(fig_hist, use_container_width=True, key="chart_hist")

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
        transition={'duration': 600, 'easing': 'cubic-in-out'},
            height=320, margin=dict(t=30, b=20, l=10, r=10),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            yaxis=dict(showgrid=True, gridcolor='#eee'),
            showlegend=False,
        )
        st.plotly_chart(fig_wf, use_container_width=True, key="chart_wf")




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

    int_cols_div = {c: '{:.0f}' for c in ['Total', 'Berlaku', 'Tidak Berlaku', f'Segera (≤{warn_days}hr)']}
    st.dataframe(
        div_sum.style.apply(highlight_pct, axis=1).format({**int_cols_div, '% Berlaku': '{:.1f}%'}),
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

    int_cols_kat = {c: '{:.0f}' for c in ['Total', 'Berlaku', 'Tidak Berlaku', f'Segera (≤{warn_days}hr)']}
    st.dataframe(
        kat_sum.style.apply(highlight_pct, axis=1).format({**int_cols_kat, '% Berlaku': '{:.1f}%'}),
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


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 7 – TREN HISTORIS
# ═══════════════════════════════════════════════════════════════════════════════
with tab7:

    if df_trend is None or df_trend.empty:
        st.warning(
            "⚠️ Data tren belum tersedia. Pastikan file **data_trend.csv** ada di repository, "
            "atau upload Excel yang mengandung sheet **TrendProsedur** (kolom: No | Tahun | Jumlah Prosedur) "
            "melalui menu Admin di sidebar."
        )
    else:
        tahun_awal  = int(df_trend['Tahun'].min())
        tahun_akhir = int(df_trend['Tahun'].max())
        jml_awal    = int(df_trend.loc[df_trend['Tahun'] == tahun_awal,  'Jumlah Prosedur'].values[0])
        jml_akhir   = int(df_trend.loc[df_trend['Tahun'] == tahun_akhir, 'Jumlah Prosedur'].values[0])
        jml_peak    = int(df_trend['Jumlah Prosedur'].max())
        tahun_peak  = int(df_trend.loc[df_trend['Jumlah Prosedur'].idxmax(), 'Tahun'])
        total_delta = jml_akhir - jml_awal
        pct_delta   = round(total_delta / jml_awal * 100, 1)

        # ── KPI ─────────────────────────────────────────────────────────────
        section("Ringkasan Tren Historis")
        tk1, tk2, tk3, tk4 = st.columns(4)
        kpi(tk1, f"Prosedur {tahun_awal}",   jml_awal,  "titik awal data",                          "kpi-blue")
        kpi(tk2, f"Prosedur {tahun_akhir}",  jml_akhir, "kondisi terkini",
            "kpi-green" if total_delta >= 0 else "kpi-red")
        kpi(tk3, f"Puncak ({tahun_peak})",   jml_peak,  "jumlah prosedur tertinggi",                "kpi-orange")
        kpi(tk4, "Total Perubahan",
            f"{'+' if total_delta > 0 else ''}{total_delta}",
            f"{pct_delta:+.1f}% sejak {tahun_awal}",
            "kpi-green" if total_delta >= 0 else "kpi-red")

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Line + Area & Bar YoY ────────────────────────────────────────────
        section("Tren Jumlah Prosedur per Tahun")
        col_line, col_bar = st.columns([1.6, 1])

        with col_line:
            st.markdown("##### Line + Area — Jumlah Prosedur (Historis)")

            # Cari penurunan terbesar YoY
            biggest_drop_idx = df_trend['Perubahan'].idxmin()
            thn_drop  = int(df_trend.loc[biggest_drop_idx, 'Tahun'])
            drop_val  = int(df_trend.loc[biggest_drop_idx, 'Perubahan'])
            drop_jml  = int(df_trend.loc[biggest_drop_idx, 'Jumlah Prosedur'])

            fig_line = go.Figure()
            # Area shading
            fig_line.add_trace(go.Scatter(
                x=df_trend['Tahun'], y=df_trend['Jumlah Prosedur'],
                fill='tozeroy', fillcolor='rgba(46,117,182,0.10)',
                line=dict(color='rgba(0,0,0,0)'), showlegend=False, hoverinfo='skip',
            ))
            # Garis utama
            dot_colors = ['#FF4444' if v < 0 else '#70AD47' if v > 0 else '#2E75B6'
                          for v in df_trend['Perubahan']]
            fig_line.add_trace(go.Scatter(
                x=df_trend['Tahun'], y=df_trend['Jumlah Prosedur'],
                mode='lines+markers+text',
                name='Jumlah Prosedur',
                line=dict(color='#2E75B6', width=3),
                marker=dict(size=11, color=dot_colors,
                            line=dict(color='white', width=2)),
                text=df_trend['Jumlah Prosedur'],
                textposition='top center',
                textfont=dict(size=12, color='#1F3864', family='Arial Black'),
                hovertemplate='<b>%{x}</b><br>Jumlah: <b>%{y}</b><extra></extra>',
            ))
            # Anotasi puncak
            fig_line.add_annotation(
                x=tahun_peak, y=jml_peak,
                text=f"🔺 Puncak {jml_peak}",
                showarrow=True, arrowhead=2, arrowcolor='#B26800',
                font=dict(size=10, color='#B26800'),
                bgcolor='#FFF8E1', bordercolor='#B26800', borderwidth=1, ay=-45,
            )
            # Anotasi penurunan terbesar
            if drop_val < 0:
                fig_line.add_annotation(
                    x=thn_drop, y=drop_jml,
                    text=f"▼ {drop_val}",
                    showarrow=True, arrowhead=2, arrowcolor='#9C0006',
                    font=dict(size=10, color='#9C0006'),
                    bgcolor='#FDE8E8', bordercolor='#9C0006', borderwidth=1, ay=45,
                )
            fig_line.update_layout(
                height=370,
                margin=dict(t=50, b=30, l=10, r=10),
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(tickmode='array',
                           tickvals=df_trend['Tahun'].tolist(),
                           ticktext=df_trend['Tahun'].astype(str).tolist(),
                           showgrid=True, gridcolor='#eee', title='Tahun'),
                yaxis=dict(showgrid=True, gridcolor='#eee', title='Jumlah Prosedur',
                           range=[0, df_trend['Jumlah Prosedur'].max() * 1.22]),
                showlegend=False,
            )
            st.plotly_chart(fig_line, use_container_width=True, key="chart_trend_line")

        with col_bar:
            st.markdown("##### Bar — Perubahan YoY")
            df_yoy = df_trend[df_trend['Perubahan'] != 0].copy()
            bar_colors = ['#70AD47' if v > 0 else '#FF4444' for v in df_yoy['Perubahan']]
            fig_yoy = go.Figure(go.Bar(
                x=df_yoy['Tahun'].astype(str),
                y=df_yoy['Perubahan'],
                marker_color=bar_colors,
                text=[f"{'+' if v > 0 else ''}{v}" for v in df_yoy['Perubahan']],
                textposition='outside',
                textfont=dict(size=12, family='Arial Black'),
                hovertemplate='<b>%{x}</b><br>Perubahan: <b>%{y:+d}</b><extra></extra>',
            ))
            fig_yoy.add_hline(y=0, line_color='#555', line_width=1)
            fig_yoy.update_layout(
                height=370,
                margin=dict(t=50, b=30, l=10, r=10),
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(title='Tahun', showgrid=False),
                yaxis=dict(title='Perubahan (jumlah)', showgrid=True, gridcolor='#eee'),
                showlegend=False,
            )
            st.plotly_chart(fig_yoy, use_container_width=True, key="chart_trend_yoy")

        # ── Waterfall ────────────────────────────────────────────────────────
        section("Waterfall — Akumulasi Perubahan Prosedur")
        st.markdown("##### Waterfall Chart — Perjalanan dari Tahun ke Tahun")

        wf_measures = ['absolute'] + ['relative'] * (len(df_trend) - 2) + ['total']
        wf_x   = df_trend['Tahun'].astype(str).tolist()
        mid_perubahan = df_trend['Perubahan'].iloc[1:-1].tolist()
        wf_y   = [jml_awal] + mid_perubahan + [jml_akhir]
        wf_txt = ([str(jml_awal)] +
                  [f"{'+' if v > 0 else ''}{v}" for v in mid_perubahan] +
                  [str(jml_akhir)])

        fig_wf = go.Figure(go.Waterfall(
            orientation='v', measure=wf_measures,
            x=wf_x, y=wf_y, text=wf_txt,
            textposition='outside', textfont=dict(size=11),
            connector={'line': {'color': '#ccc'}},
            increasing={'marker': {'color': '#70AD47'}},
            decreasing={'marker': {'color': '#FF4444'}},
            totals={'marker': {'color': '#2E75B6', 'line': {'color': '#1F3864', 'width': 2}}},
            hovertemplate='<b>%{x}</b><br>%{y:+d} prosedur<extra></extra>',
        ))
        fig_wf.update_layout(
            height=340, margin=dict(t=40, b=20, l=10, r=10),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            yaxis=dict(showgrid=True, gridcolor='#eee', title='Jumlah Prosedur'),
            showlegend=False,
        )
        st.plotly_chart(fig_wf, use_container_width=True, key="chart_wf_trend")

        # ── Tabel Rekap + Insight ────────────────────────────────────────────
        section("Tabel Rekap & Insight")
        tbl_col, ins_col = st.columns([1, 1.2])

        with tbl_col:
            st.markdown("##### Tabel Rekap Tren")
            tbl_t = df_trend[['Tahun', 'Jumlah Prosedur', 'Perubahan', '% Perubahan']].copy()
            tbl_t.columns = ['Tahun', 'Jumlah Prosedur', 'Δ Jumlah', 'Δ %']

            def color_tren(row):
                styles = []
                for col in row.index:
                    if col in ['Δ Jumlah', 'Δ %']:
                        v = row[col]
                        if v > 0:   styles.append('color:#375623;font-weight:bold')
                        elif v < 0: styles.append('color:#9C0006;font-weight:bold')
                        else:       styles.append('color:#888')
                    else:
                        styles.append('')
                return styles

            st.dataframe(
                tbl_t.style.apply(color_tren, axis=1)
                    .format({'Jumlah Prosedur': '{:.0f}', 'Δ Jumlah': '{:+.0f}', 'Δ %': '{:+.1f}%'}),
                use_container_width=True, height=310, hide_index=True,
            )

        with ins_col:
            st.markdown("##### 📌 Insight Otomatis")
            tahun_turun = df_trend[df_trend['Perubahan'] < 0]['Tahun'].tolist()
            tahun_naik  = df_trend[df_trend['Perubahan'] > 0]['Tahun'].tolist()
            drop_pct    = float(df_trend.loc[biggest_drop_idx, '% Perubahan'])

            st.markdown(f"""
<div style='background:#EEF4FB;border-left:4px solid #2E75B6;border-radius:10px;
padding:1.1rem 1.3rem;font-size:0.87rem;line-height:1.85'>
<b style='color:#1F3864;font-size:0.95rem'>Analisis Tren {tahun_awal}–{tahun_akhir}</b><br><br>
📍 Prosedur mencapai <b>puncak</b> pada <b>{tahun_peak}</b> dengan total <b>{jml_peak} prosedur</b>.<br>
📉 Penurunan terbesar: tahun <b>{thn_drop}</b> sebesar
<span style='color:#9C0006'><b>{drop_val:+d} prosedur ({drop_pct:+.1f}%)</b></span>.<br>
📅 Tahun <b>turun</b>: {', '.join(str(t) for t in tahun_turun) if tahun_turun else '–'}<br>
📅 Tahun <b>naik</b>: {', '.join(str(t) for t in tahun_naik) if tahun_naik else '–'}<br><br>
📊 Total perubahan {tahun_awal}→{tahun_akhir}:
<b style='color:{"#9C0006" if total_delta < 0 else "#375623"}'>{total_delta:+d} prosedur ({pct_delta:+.1f}%)</b><br>
</div>
""", unsafe_allow_html=True)


# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    f"<div style='text-align:center;color:#999;font-size:0.75rem'>"
    f"PT Wijaya Karya Beton Tbk &nbsp;|&nbsp; DSIM – Kantor Pusat &nbsp;|&nbsp; "
    f"Sumber: data per {today.strftime('%d %B %Y')} &nbsp;|&nbsp; "
    f"Form: WB-QMS-PS-01-F08 Rev.02 &nbsp;|&nbsp; "
    f"{today.strftime('%d %B %Y')}</div>",
    unsafe_allow_html=True,
)
