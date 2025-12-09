import streamlit as st
import pandas as pd
import plotly.express as px
import json
import io 

# --- デフォルト設定値 ---
DEFAULT_CONFIG = {
    "current_age": 33, "end_age": 100,
    "ini_cash": 200, "ini_401k": 300, "ini_nisa": 100, "ini_paypay": 10,
    "r_cash": 0.30, "r_401k": 5.0, "r_nisa": 5.0, "r_paypay": 6.0, "inflation": 2.0,
    "age_work_last": 64,
    "inc_20s": 300, "inc_30s": 400, "inc_40s": 500, "inc_50s": 600, "inc_60s": 400,
    "age_401k_get": 65, "tax_401k": 12.0, "age_pension": 65, "pension_monthly": 200000, "tax_pension": 15.0,
    
    # 支出設定
    "cost_20s": 20, "cost_30s": 25, "cost_40s": 30, "cost_50s": 30, 
    "cost_6064": 28, "cost_65": 25,
    "exp_20s": 50, "exp_30s": 100, "exp_40s": 150, "exp_50s": 100, 
    "exp_6064": 80, "exp_65": 50,

    "nisa_monthly": 50000,
    "nisa_stop_age": 65,
    "paypay_monthly": 300, "paypay_stop_age": 70,
    "k401_monthly": 55000,
    "k401_stop_age": 60,
    "dam_1": 700, "dam_2": 700, "dam_3": 500,
    "priority": "新NISAから先に使う",
    "nisa_start_age": 65, "paypay_start_age": 60,
    
    # 上限設定
    "limit_mode_nisa": "年額定額 (万円)",
    "limit_val_nisa_yen": 0,
    "limit_val_nisa_pct": 4.0,
    "limit_mode_other": "年額定額 (万円)",
    "limit_val_other_yen": 20,
    "limit_val_other_pct": 4.0,
    "tax_rate_other": 0.0,

    "inc1_a": 55, "inc1_v": 500, "inc2_a": 0, "inc2_v": 0, "inc3_a": 0, "inc3_v": 0,
    "dec1_a": 66, "dec1_v": 1000, "dec2_a": 0, "dec2_v": 0, "dec3_a": 0, "dec3_v": 0
}

# --- ヘルパー関数 ---

def load_uploaded_settings(uploaded_file):
    try:
        bytes_data = uploaded_file.getvalue()
        data = json.loads(bytes_data)
        count = 0
        for key, value in data.items():
            if key in st.session_state:
                st.session_state[key] = value
                count += 1
        st.sidebar.success(f"✅ 設定ファイルを読み込みました！ ({count}項目)")
    except Exception as e:
        st.sidebar.error(f"⚠️ ファイル形式エラー: {e}")

def get_download_json():
    save_data = {}
    for key in DEFAULT_CONFIG.keys():
        if key in st.session_state:
            save_data[key] = st.session_state[key]
    return json.dumps(save_data, indent=4, ensure_ascii=False)

def next_step_guide(text):
    st.markdown("---")
    st.info(f"👉 **入力完了ですか？ 上のタブで『{text}』へ進んでください**")

# --- メインアプリ ---
st.set_page_config(page_title="簡易資産シミュレータ v6.2", page_icon="💎", layout="wide")

def main():
    if "first_load_done" not in st.session_state:
        for key, value in DEFAULT_CONFIG.items():
            if key not in st.session_state:
                st.session_state[key] = value
        st.session_state["first_load_done"] = True
    
    # ★デザインカスタマイズ
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Shippori+Mincho:wght@400;500;700&family=Zen+Kaku+Gothic+New:wght@300;400;500&display=swap');
        
        html, body, [class*="css"] {
            font-family: 'Zen Kaku Gothic New', sans-serif;
            color: #4a4a4a;
        }
        .stApp {
            background-color: #fcfcfc;
            background-image: 
                linear-gradient(#f0f0f0 1px, transparent 1px),
                linear-gradient(90deg, #f0f0f0 1px, transparent 1px);
            background-size: 40px 40px;
        }

        [data-testid="stSidebar"] {
            background-color: #f7f7f5;
            border-right: 1px solid #e0e0e0;
        }
        [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
            color: #5c5c5c !important;
        }

        h1, h2, h3 {
            font-family: 'Shippori Mincho', serif;
            color: #8d6e63 !important;
            font-weight: 700 !important;
            letter-spacing: 0.05em;
        }
        h4, h5, h6 {
            color: #6d4c41 !important;
            font-weight: 600 !important;
        }
        
        /* タブデザイン */
        .stTabs [data-baseweb="tab-list"] {
            gap: 0px;
            border-bottom: none;
            padding-bottom: 20px;
            flex-wrap: wrap;
        }
        .stTabs [data-baseweb="tab"] {
            background-color: #e0e0e0;
            color: #757575;
            border: none;
            border-radius: 0;
            padding: 12px 10px 12px 25px;
            margin-right: -12px;
            font-family: 'Zen Kaku Gothic New', sans-serif;
            font-weight: 500;
            font-size: 0.9rem;
            clip-path: polygon(90% 0, 100% 50%, 90% 100%, 0% 100%, 10% 50%, 0% 0%);
            z-index: 1;
            transition: all 0.2s ease;
            flex-grow: 1;
            justify-content: center;
            text-align: center;
            min-width: 100px;
        }
        .stTabs [data-baseweb="tab"]:first-child {
            clip-path: polygon(90% 0, 100% 50%, 90% 100%, 0% 100%, 0% 0%);
            padding-left: 10px;
        }
        .stTabs [aria-selected="true"] {
            background: linear-gradient(to right, #a1887f, #d7ccc8) !important;
            color: #3e2723 !important;
            z-index: 10;
            font-weight: 700;
            text-shadow: 0px 1px 1px rgba(255,255,255,0.3);
        }
        .stTabs [data-baseweb="tab"]:hover {
            background-color: #d7ccc8;
            color: #5d4037;
            z-index: 5;
        }

        [data-testid="stMetric"] {
            background-color: #ffffff;
            border: 1px solid #eeeeee;
            border-radius: 4px;
            padding: 16px;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
            border-left: 4px solid #bcaaa4;
        }
        [data-testid="stMetricLabel"] {
            color: #8d6e63 !important;
            font-size: 0.85rem !important;
        }
        [data-testid="stMetricValue"] {
            color: #4e342e !important;
            font-family: 'Shippori Mincho', serif;
        }
        [data-testid="stMetricDelta"] {
            color: #7cb342 !important;
        }

        .custom-card {
            background-color: #fff;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            padding: 30px;
            text-align: center;
            box-shadow: 0 4px 10px rgba(0,0,0,0.05);
        }

        .stButton button {
            background-color: #d7ccc8;
            color: #4e342e !important;
            border: 1px solid #a1887f;
            border-radius: 4px;
            font-weight: 600;
        }
        .stButton button:hover {
            background-color: #a1887f;
            color: white !important;
        }
        
        .stNumberInput input, .stSelectbox div[data-baseweb="select"] {
            border-radius: 4px;
            border: 1px solid #d0d0d0 !important;
            background-color: #fafafa;
        }
        
        hr { border-color: #e0e0e0; }
        .stAlert {
            background-color: #f5f5f5;
            color: #424242;
            border: 1px solid #e0e0e0;
        }
        div.stButton > button:first-child { width: 100%; }
        </style>
    """, unsafe_allow_html=True)

    st.title("💎 簡易資産シミュレータ v6.2")
    st.caption("Ver. Graph V-Line & Total Tooltip")

    # --- サイドバー設定 ---
    c_head, c_share = st.sidebar.columns([1, 0.5])
    with c_head:
        st.header("⚙️ 設定")
    with c_share:
        if st.button("🔗 共有"):
            st.sidebar.info("👇 URLをコピー")
            st.sidebar.code("https://asset-simulator-easy.streamlit.app/", language=None)
            
    st.sidebar.subheader("📁 設定ファイル")
    col_dl, col_ul = st.sidebar.columns(2)
    with col_dl:
        st.download_button(
            label="💾 保存",
            data=get_download_json(),
            file_name="asset_config.json",
            mime="application/json",
            help="現在の設定を保存します"
        )
    with col_ul:
        uploaded_file = st.file_uploader(
            "📤 読込", type=["json"], accept_multiple_files=False, label_visibility="collapsed"
        )
    if uploaded_file is not None:
        load_uploaded_settings(uploaded_file)
    
    st.sidebar.markdown("---") 
    
    tab1, tab2, tab3, tab4, tab5, tab6 = st.sidebar.tabs([
        "1.基本", "2.収支", "3.積立", "4.取崩", "5.臨時", "6.完了"
    ])

    # --- 入力 UI (以下、ロジック変更なし) ---
    with tab1:
        st.subheader("👤 基本情報の入力")
        current_age = st.number_input("現在年齢", 20, 80, key="current_age")
        end_age = st.number_input("終了年齢", 80, 120, key="end_age")
        st.markdown("---")
        st.subheader("💰 現在の資産 (万円)")
        ini_cash = st.number_input("貯蓄 (現金)", 0, 10000, step=10, key="ini_cash") * 10000
        ini_401k = st.number_input("401k (確定拠出)", 0, 10000, step=10, key="ini_401k") * 10000
        ini_nisa = st.number_input("新NISA", 0, 10000, step=10, key="ini_nisa") * 10000
        ini_paypay = st.number_input("他運用 (ポイント運用など)", 0, 10000, step=10, key="ini_paypay") * 10000
        st.markdown("---")
        st.subheader("📈 運用利回り (%)")
        r_cash = st.number_input("貯蓄金利", 0.0, 10.0, step=0.01, format="%.2f", key="r_cash") / 100
        r_401k = st.number_input("401k年利", 0.0, 30.0, step=0.1, format="%.2f", key="r_401k") / 100
        r_nisa = st.number_input("新NISA年利", 0.0, 30.0, step=0.1, format="%.2f", key="r_nisa") / 100
        r_paypay = st.number_input("他運用年利", 0.0, 50.0, step=0.1, format="%.2f", key="r_paypay") / 100
        inflation = st.number_input("インフレ率", -5.0, 20.0, step=0.1, format="%.2f", key="inflation") / 100
        next_step_guide("STEP 2: 収支")

    with tab2:
        st.subheader("🏢 働き方と収入の入力")
        age_work_last = st.number_input("何歳まで働く？", 50, 90, key="age_work_last")
        st.markdown("##### 手取り年収 (万円)")
        inc_help = "ボーナスを含めた、年間の手取り収入の合計を入力してください。"
        inc_20s = st.number_input("〜29歳", 0, 5000, step=10, key="inc_20s", help=inc_help) * 10000
        inc_30s = st.number_input("30〜39歳", 0, 5000, step=10, key="inc_30s", help=inc_help) * 10000
        inc_40s = st.number_input("40〜49歳", 0, 5000, step=10, key="inc_40s", help=inc_help) * 10000
        inc_50s = st.number_input("50〜59歳", 0, 5000, step=10, key="inc_50s", help=inc_help) * 10000
        inc_60s = st.number_input("60歳〜", 0, 5000, step=10, key="inc_60s", help=inc_help) * 10000
        st.markdown("---")
        st.subheader("🐢 年金・退職金")
        age_401k_get = st.number_input("401k受取年齢", 50, 80, key="age_401k_get")
        tax_401k = st.number_input("401k受取税率(%)", 0.0, 50.0, step=0.1, format="%.1f", key="tax_401k") / 100
        age_pension = st.number_input("年金開始年齢", 60, 75, key="age_pension")
        pension_monthly = st.number_input("年金月額(額面・円)", 0, 500000, step=10000, key="pension_monthly")
        tax_pension = st.number_input("年金税・社会保険料率(%)", 0.0, 50.0, step=0.1, format="%.1f", key="tax_pension") / 100
        st.markdown("---")
        st.subheader("🛒 支出設定")
        st.markdown("##### 基本生活費 (月/万円)")
        cost_help = "家賃、食費、光熱費など、毎月必ず出ていくお金です。"
        cost_20s = st.number_input("〜29歳 生活費", 0, 500, step=1, key="cost_20s", help=cost_help) * 10000
        cost_30s = st.number_input("30代 生活費", 0, 500, step=1, key="cost_30s", help=cost_help) * 10000
        cost_40s = st.number_input("40代 生活費", 0, 500, step=1, key="cost_40s", help=cost_help) * 10000
        cost_50s = st.number_input("50代 生活費", 0, 500, step=1, key="cost_50s", help=cost_help) * 10000
        c_60, c_65 = st.columns(2)
        with c_60:
            cost_6064 = st.number_input("60〜64歳 生活費", 0, 500, step=1, key="cost_6064", help="再雇用期間など") * 10000
        with c_65:
            cost_65 = st.number_input("65歳〜 生活費", 0, 500, step=1, key="cost_65", help="年金生活など") * 10000
        st.markdown("##### 年間特別支出 (万円/年)")
        exp_help = "旅行、帰省、家電買替、車検など、年単位で発生する特別なお金です。"
        exp_20s = st.number_input("〜29歳 特別出費", 0, 5000, step=10, key="exp_20s", help=exp_help) * 10000
        exp_30s = st.number_input("30代 特別出費", 0, 5000, step=10, key="exp_30s", help=exp_help) * 10000
        exp_40s = st.number_input("40代 特別出費", 0, 5000, step=10, key="exp_40s", help=exp_help) * 10000
        exp_50s = st.number_input("50代 特別出費", 0, 5000, step=10, key="exp_50s", help=exp_help) * 10000
        c_e60, c_e65 = st.columns(2)
        with c_e60:
            exp_6064 = st.number_input("60〜64歳 特別出費", 0, 5000, step=10, key="exp_6064") * 10000
        with c_e65:
            exp_65 = st.number_input("65歳〜 特別出費", 0, 5000, step=10, key="exp_65") * 10000
        next_step_guide("STEP 3: 積立")

    with tab3:
        st.subheader("🌱 積立投資の設定")
        col_t1, col_t2 = st.columns(2)
        with col_t1:
            st.markdown("**1. NISA つみたて投資枠**")
            nisa_monthly = st.number_input("月額積立(円)", 0, 500000, step=1000, key="nisa_monthly")
            nisa_year_val = nisa_monthly * 12
            if nisa_year_val <= 1200000:
                st.info(f"✅ 年間 {nisa_year_val/10000:.0f}万 / 120万")
            else:
                st.warning(f"⚠️ 年間120万を超えています。")
            nisa_stop_age = st.number_input("NISA積立終了年齢", 20, 100, key="nisa_stop_age")
        with col_t2:
            st.markdown("**2. 他運用 (特定口座など)**")
            paypay_monthly = st.number_input("他運用積立(月/円)", 0, 1000000, step=1000, key="paypay_monthly")
            st.write(f"(年間 {paypay_monthly*12/10000:.0f}万円)")
            paypay_stop_age = st.number_input("他運用積立終了年齢", 20, 100, key="paypay_stop_age")
        st.markdown("---")
        st.markdown("**3. 401k/iDeCo (確定拠出年金)**")
        c_k1, c_k2 = st.columns(2)
        with c_k1:
            k401_monthly = st.number_input("401k積立(月/円)", 0, 500000, step=1000, key="k401_monthly", help="給与天引きされる掛金です。")
        with c_k2:
            k401_stop_age = st.number_input("401k積立終了年齢", 20, 70, key="k401_stop_age", help="拠出が終了する年齢です（例: 60歳）。")
        st.markdown("---")
        st.subheader("💧 最低貯蓄額 (ダム水位)")
        st.caption("最低貯蓄額を超えた余剰金は、**「NISA 成長投資枠 (最大年240万)」** を埋めるために自動投資されます。")
        dam_help = "生活防衛資金として、投資に回さずに現金で持っておきたい最低金額です。"
        dam_1 = st.number_input("〜49歳 最低貯蓄(万)", 0, 10000, step=50, key="dam_1", help=dam_help) * 10000
        dam_2 = st.number_input("50代 最低貯蓄(万)", 0, 10000, step=50, key="dam_2", help=dam_help) * 10000
        dam_3 = st.number_input("60歳〜 最低貯蓄(万)", 0, 10000, step=50, key="dam_3", help=dam_help) * 10000
        next_step_guide("STEP 4: 取崩")

    with tab4:
        st.subheader("🍂 取崩し・補填ルール")
        priority = st.radio("取り崩し優先順位 (不足時)", ["新NISAから先に使う", "他運用から先に使う"], horizontal=True, key="priority")
        col_out1, col_out2 = st.columns(2)
        with col_out1:
            nisa_start_age = st.number_input("新NISA 解禁年齢", 50, 100, key="nisa_start_age")
        with col_out2:
            paypay_start_age = st.number_input("他運用 解禁年齢", 50, 100, key="paypay_start_age")
        st.markdown("---")
        st.write("▼ 取り崩し上限設定")
        c_n_mode, c_n_val = st.columns([3, 2])
        limit_mode_options = ["年額定額 (万円)", "総資産比率 (%)", "残高比率 (%)"]
        limit_mode_nisa = c_n_mode.selectbox("NISA上限方式", limit_mode_options, key="limit_mode_nisa", label_visibility="collapsed")
        if limit_mode_nisa == "年額定額 (万円)":
            limit_val_nisa = c_n_val.number_input("NISA金額", 0, 10000, step=10, key="limit_val_nisa_yen", label_visibility="collapsed", format="%d")
            st.caption(f"年間 **{limit_val_nisa}万円** まで")
            nisa_limit_yen_calc = limit_val_nisa * 10000
        else:
            limit_val_nisa = c_n_val.number_input("NISA割合", 0.0, 100.0, step=0.1, key="limit_val_nisa_pct", label_visibility="collapsed", format="%.1f")
            if limit_mode_nisa == "総資産比率 (%)": st.caption(f"その年の **総資産の {limit_val_nisa:.1f}%** まで")
            else: st.caption(f"その年の **NISA残高の {limit_val_nisa:.1f}%** まで")
            nisa_limit_yen_calc = limit_val_nisa
        c_o_mode, c_o_val = st.columns([3, 2])
        limit_mode_other = c_o_mode.selectbox("他運用上限方式", limit_mode_options, key="limit_mode_other", label_visibility="collapsed")
        if limit_mode_other == "年額定額 (万円)":
            limit_val_other = c_o_val.number_input("他運用金額", 0, 10000, step=10, key="limit_val_other_yen", label_visibility="collapsed", format="%d")
            st.caption(f"年間 **{limit_val_other}万円** まで")
            other_limit_yen_calc = limit_val_other * 10000
        else:
            limit_val_other = c_o_val.number_input("他運用割合", 0.0, 100.0, step=0.1, key="limit_val_other_pct", label_visibility="collapsed", format="%.1f")
            if limit_mode_other == "総資産比率 (%)": st.caption(f"その年の **総資産の {limit_val_other:.1f}%** まで")
            else: st.caption(f"その年の **他運用残高の {limit_val_other:.1f}%** まで")
            other_limit_yen_calc = limit_val_other
        st.markdown("**他運用 取崩し税率 (%)**")
        tax_rate_other = st.number_input("他運用 取崩し税率", 0.0, 50.0, step=0.1, format="%.1f", key="tax_rate_other") / 100
        next_step_guide("STEP 5: 臨時")

    with tab5:
        st.subheader("🎀 臨時収入・支出")
        c_i1_a, c_i1_v = st.columns([1, 2])
        inc1_age = c_i1_a.number_input("収入① 年齢", 0, 100, key="inc1_a")
        inc1_val = c_i1_v.number_input("収入① 金額(万)", 0, 10000, step=100, key="inc1_v") * 10000
        c_i2_a, c_i2_v = st.columns([1, 2])
        inc2_age = c_i2_a.number_input("収入② 年齢", 0, 100, key="inc2_a")
        inc2_val = c_i2_v.number_input("収入② 金額(万)", 0, 10000, step=100, key="inc2_v") * 10000
        c_i3_a, c_i3_v = st.columns([1, 2])
        inc3_age = c_i3_a.number_input("収入③ 年齢", 0, 100, key="inc3_a")
        inc3_val = c_i3_v.number_input("収入③ 金額(万)", 0, 10000, step=100, key="inc3_v") * 10000
        st.markdown("---")
        c_d1_a, c_d1_v = st.columns([1, 2])
        dec1_age = c_d1_a.number_input("支出① 年齢", 0, 100, key="dec1_a")
        dec1_val = c_d1_v.number_input("支出① 金額(万)", 0, 10000, step=100, key="dec1_v") * 10000
        c_d2_a, c_d2_v = st.columns([1, 2])
        dec2_age = c_d2_a.number_input("支出② 年齢", 0, 100, key="dec2_a")
        dec2_val = c_d2_v.number_input("支出② 金額(万)", 0, 10000, step=100, key="dec2_v") * 10000
        c_d3_a, c_d3_v = st.columns([1, 2])
        dec3_age = c_d3_a.number_input("支出③ 年齢", 0, 100, key="dec3_a")
        dec3_val = c_d3_v.number_input("支出③ 金額(万)", 0, 10000, step=100, key="dec3_v") * 10000
        next_step_guide("STEP 6: 完了・オマケ")

    with tab6:
        st.subheader("✨ 必要資産額シミュレータ")
        st.markdown("#### ステップ1: 目標の設定")
        target_yearly_income = st.number_input("希望する年間取崩し額 (万円)", 0, 5000, 240, step=10, format="%d")
        target_interest_rate = st.number_input("想定利回り (年利 %)", 0.1, 20.0, 4.0, step=0.1, format="%.1f")
        st.markdown("---")
        st.markdown("#### ステップ2: 計算結果")
        if target_interest_rate > 0:
            required_asset = (target_yearly_income * 10000) / (target_interest_rate / 100)
            st.markdown(f"""
                <div class="custom-card">
                    <h4 style="color: #5d4037; margin-bottom: 5px; font-family: 'Shippori Mincho', serif;">必要な総資産額</h4>
                    <p style="font-size: 2.8rem; font-weight: 700; color: #4e342e; margin: 0; font-family: 'Shippori Mincho', serif; letter-spacing: 0.05em;">
                        {required_asset/10000:,.0f}<span style="font-size: 1.2rem; color: #8d6e63;"> 万円</span>
                    </p>
                    <p style="color: #757575; margin-top: 5px; font-size: 0.9rem;">(年利 {target_interest_rate}% で運用した場合)</p>
                </div>
            """, unsafe_allow_html=True)
            st.markdown("---")
            with st.expander("📚 4%ルールとは？（豆知識）"):
                st.markdown("""
                **「年間支出の25倍の資産を築けば、年利4%の運用益で生活費をまかなえる」** という、米国発の有名な経験則です。
                * **計算式:** 年間支出 ÷ 4%（0.04）＝ **年間支出 × 25**
                """)
        else:
            st.warning("利回りを0より大きく設定してください。")

    st.sidebar.markdown("---")
    st.sidebar.caption("👀 訪問者数")
    st.sidebar.markdown(f"![Visitor Count](https://visitor-badge.laobi.icu/badge?page_id=touched2222_asset_simulator_v6)")

    # --- 計算ロジック ---
    records = []
    cash = ini_cash
    k401 = ini_401k
    nisa = ini_nisa
    paypay = ini_paypay
    nisa_principal = ini_nisa 
    NISA_TSUMITATE_LIMIT = 1200000 
    NISA_GROWTH_LIMIT = 2400000
    NISA_LIFETIME_LIMIT = 18000000 

    records.append({
        "Age": current_age,
        "Total": int(cash + k401 + nisa + paypay),
        "Cash": int(cash),
        "401k": int(k401),
        "NISA": int(nisa),
        "Other": int(paypay),
        "NISA積立枠": 0,
        "NISA成長枠": 0,
        "NISA元本": int(nisa_principal) 
    })

    for age in range(current_age + 1, end_age + 1):
        cash *= (1 + r_cash)
        nisa *= (1 + r_nisa)
        paypay *= (1 + r_paypay)
        if age < age_401k_get: k401 *= (1 + r_401k)

        is_working = (age <= age_work_last)
        salary = 0
        if is_working:
            if age < 30: salary = inc_20s
            elif age < 40: salary = inc_30s
            elif age < 50: salary = inc_40s
            elif age < 60: salary = inc_50s
            else: salary = inc_60s

        annual_extra_exp = 0
        if age < 30: annual_extra_exp = exp_20s
        elif age < 40: annual_extra_exp = exp_30s
        elif age < 50: annual_extra_exp = exp_40s
        elif age < 60: annual_extra_exp = exp_50s
        elif age < 65: annual_extra_exp = exp_6064
        else: annual_extra_exp = exp_65
        
        pension = 0
        if age >= age_pension:
            pension = pension_monthly * 12 * (1 - tax_pension)

        base_monthly_cost = 0
        if age < 30: base_monthly_cost = cost_20s
        elif age < 40: base_monthly_cost = cost_30s
        elif age < 50: base_monthly_cost = cost_40s
        elif age < 60: base_monthly_cost = cost_50s
        elif age < 65: base_monthly_cost = cost_6064
        else: base_monthly_cost = cost_65

        if age > age_work_last:
            current_cost = base_monthly_cost * 12 * ((1 + inflation) ** (age - age_work_last))
        else:
            current_cost = base_monthly_cost * 12

        val_k401_add = k401_monthly * 12 if (is_working and age < age_401k_get and age <= k401_stop_age) else 0 
        
        nisa_tsumitate_year = 0
        nisa_growth_year = 0
        can_invest = (cash > 0 or is_working)

        val_nisa_add = 0
        if can_invest and age <= nisa_stop_age:
            raw_nisa_add = nisa_monthly * 12
            lifetime_room = max(0, NISA_LIFETIME_LIMIT - nisa_principal)
            val_nisa_add = min(raw_nisa_add, NISA_TSUMITATE_LIMIT, lifetime_room)
            nisa_tsumitate_year = val_nisa_add
            
        val_paypay_add = paypay_monthly * 12 if (can_invest and age <= paypay_stop_age) else 0

        k401 += val_k401_add
        nisa += val_nisa_add
        nisa_principal += val_nisa_add
        paypay += val_paypay_add

        if age == age_401k_get:
            income_401k = k401 * (1 - tax_401k)
            cash += income_401k
            k401 = 0

        event_inc = 0
        if age == inc1_age: event_inc += inc1_val
        if age == inc2_age: event_inc += inc2_val
        if age == inc3_age: event_inc += inc3_val
        
        event_dec = 0
        if age == dec1_age: event_dec += dec1_val
        if age == dec2_age: event_dec += dec2_val
        if age == dec3_age: event_dec += dec3_val

        cash_flow = (salary + pension + event_inc) - (current_cost + annual_extra_exp + event_dec + val_k401_add + val_nisa_add + val_paypay_add)
        cash += cash_flow

        if cash < 0:
            shortage = abs(cash)
            current_total_investments = nisa + paypay + k401

            def calc_actual_limit(mode, val, current_asset, total_assets):
                if mode == "年額定額 (万円)":
                    if val == 0: return float('inf') 
                    return val 
                elif mode == "総資産比率 (%)":
                    return total_assets * (val / 100)
                elif mode == "残高比率 (%)":
                    return current_asset * (val / 100)
                return float('inf')

            limit_nisa_yen = calc_actual_limit(limit_mode_nisa, nisa_limit_yen_calc, nisa, current_total_investments)
            limit_other_yen = calc_actual_limit(limit_mode_other, other_limit_yen_calc, paypay, current_total_investments)

            def withdraw_asset_logic(needed, current_val, principal_val, is_nisa, limit_yen, tax_rate=0.0):
                gross_needed = needed / (1 - tax_rate) if (1 - tax_rate) > 0 else needed
                can_withdraw_gross = min(gross_needed, current_val, limit_yen)
                net_cash_obtained = can_withdraw_gross * (1 - tax_rate)
                new_val = current_val - can_withdraw_gross
                new_principal = principal_val
                if is_nisa and current_val > 0 and can_withdraw_gross > 0:
                    ratio = can_withdraw_gross / current_val
                    new_principal = principal_val * (1 - ratio)
                return net_cash_obtained, new_val, new_principal

            if priority == "新NISAから先に使う":
                if age >= nisa_start_age:
                    pay_nisa, nisa, nisa_principal = withdraw_asset_logic(shortage, nisa, nisa_principal, True, limit_nisa_yen, 0.0)
                    shortage -= pay_nisa
                if age >= paypay_start_age:
                    pay_other, paypay, _ = withdraw_asset_logic(shortage, paypay, 0, False, limit_other_yen, tax_rate_other)
                    shortage -= pay_other
            else:
                if age >= paypay_start_age:
                    pay_other, paypay, _ = withdraw_asset_logic(shortage, paypay, 0, False, limit_other_yen, tax_rate_other)
                    shortage -= pay_other
                if age >= nisa_start_age:
                    pay_nisa, nisa, nisa_principal = withdraw_asset_logic(shortage, nisa, nisa_principal, True, limit_nisa_yen, 0.0)
                    shortage -= pay_nisa
            
            cash = -shortage

        if age < 50: target = dam_1
        elif age < 60: target = dam_2
        else: target = dam_3

        if cash > target and age <= nisa_stop_age:
            surplus = cash - target
            nisa_remaining_space = NISA_GROWTH_LIMIT 
            lifetime_room = max(0, NISA_LIFETIME_LIMIT - nisa_principal)
            move = min(surplus, nisa_remaining_space, lifetime_room)
            cash -= move
            nisa += move
            nisa_principal += move
            nisa_growth_year = move

        records.append({
            "Age": age,
            "Total": int(cash + k401 + nisa + paypay),
            "Cash": int(cash),
            "401k": int(k401),
            "NISA": int(nisa),
            "Other": int(paypay),
            "NISA積立枠": int(nisa_tsumitate_year),
            "NISA成長枠": int(nisa_growth_year),
            "NISA元本": int(nisa_principal) 
        })

    # --- 1. スライダー (レイアウト変更: グラフの上に配置) ---
    st.markdown("### 📅 年齢別 資産チェック")
    target_age = st.slider("確認したい年齢を選択してください", current_age, end_age, 65, label_visibility="collapsed")
    
    df = pd.DataFrame(records)
    
    try:
        row = df[df["Age"] == target_age].iloc[0]
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric(f"🎂 {target_age}歳の総資産", f"{row['Total']/10000:,.0f}万円")
        c2.metric("💴 現金・預金", f"{row['Cash']/10000:,.0f}万円")
        c3.metric("📈 新NISA", f"{row['NISA']/10000:,.0f}万円", delta=f"元本 {row['NISA元本']/10000:,.0f}万円")
        c4.metric("🐢 401k/iDeCo", f"{row['401k']/10000:,.0f}万円")
        c5.metric("✨ その他運用", f"{row['Other']/10000:,.0f}万円")
    except: st.error("データ取得エラー")

    # --- 2. グラフ (縦線を追加 & ツールチップ修正) ---
    st.markdown("<br>", unsafe_allow_html=True)
    
    if "graph_mode" not in st.session_state:
        st.session_state["graph_mode"] = "積み上げ (総資産)"
    current_mode = st.session_state["graph_mode"]

    df_melt = df.melt(id_vars=["Age"], value_vars=["Cash", "401k", "NISA", "Other"], var_name="Asset", value_name="Amount")
    
    # ★追加: 総資産データをマージしてツールチップ用に準備
    df_melt = pd.merge(df_melt, df[["Age", "Total"]], on="Age", how="left")

    colors = {"Cash": "#90a4ae", "NISA": "#e57373", "401k": "#81c784", "Other": "#ba68c8"}
    
    if current_mode == "積み上げ (総資産)":
        fig = px.area(df_melt, x="Age", y="Amount", color="Asset", 
                      labels={"Amount": "金額 (円)", "Age": "年齢"}, 
                      color_discrete_map=colors,
                      custom_data=["Total"]) # Totalをカスタムデータに追加
    else:
        fig = px.line(df_melt, x="Age", y="Amount", color="Asset", 
                      labels={"Amount": "金額 (円)", "Age": "年齢"}, 
                      color_discrete_map=colors,
                      custom_data=["Total"])

    # ★修正: ツールチップに総資産を表示
    fig.update_traces(
        hovertemplate="<b>%{data.name}</b>: %{y:,.0f}円<br><b>総資産</b>: %{customdata[0]:,.0f}円<extra></extra>"
    )

    fig.update_layout(
        hovermode="x unified",
        plot_bgcolor="white",
        paper_bgcolor="white",
        font={"family": "Zen Kaku Gothic New", "color": "#5d5555"},
        margin=dict(l=20, r=20, t=40, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    # ★追加: スライダー連動の縦線
    fig.add_vline(x=target_age, line_width=2, line_dash="dash", line_color="#831843")

    st.plotly_chart(fig, use_container_width=True)

    # --- 3. その他表示 ---
    st.radio("グラフ表示モード", ["積み上げ (総資産)", "折れ線 (個別推移)"], 
             key="graph_mode", horizontal=True)

    st.markdown("<br>", unsafe_allow_html=True)
    with st.expander("📝 年単位の資産明細を表示"):
        st.dataframe(df, use_container_width=True, height=300)

    st.markdown("<br>", unsafe_allow_html=True)
    with st.expander("ℹ️ このシミュレータのルール（クリックで開く）"):
        st.markdown("""
        1.  **収入はすべて「現金」へ**：給与・年金・臨時収入はまず現金貯金に入ります。
        2.  **年金の手取り**：入力した年金月額から、設定した税率（社会保険料含む）を引いた額が収入となります。
        3.  **つみたて枠（年120万）**：「NISA積立」で設定した金額が優先的に充てられます。
        4.  **成長枠（年240万）**：「最低貯蓄額」を超えた余剰金が、この枠を使って自動投資されます。
        5.  **現金不足時の「取り崩し」**：現金がマイナスになった場合、設定した優先順位に従って補填します。
        6.  **取り崩し上限**：年額固定、総資産比率、残高比率の3パターンから選択できます。
        7.  **他運用の税金**：設定された税率分を差し引いて、手取り額で現金の不足を埋めます。
        8.  **積立停止**：現金がマイナス（借金）の年は、新規の積立投資を行いません。
        """)

if __name__ == '__main__':
    main()
