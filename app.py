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
    "cost_20s": 20, "cost_30s": 25, "cost_40s": 30, "cost_50s": 30, "cost_60s": 25,
    "exp_20s": 50, "exp_30s": 100, "exp_40s": 150, "exp_50s": 100, "exp_60s": 50,
    "nisa_monthly": 50000,
    "nisa_stop_age": 65,
    "paypay_monthly": 300, "paypay_stop_age": 70,
    "k401_monthly": 55000,
    "dam_1": 700, "dam_2": 700, "dam_3": 500,
    "priority": "新NISAから先に使う",
    "nisa_start_age": 65, "paypay_start_age": 60,
    # ★変更: 上限値だけでなく「方式」も保存
    "limit_mode_nisa": "年額定額 (万円)",
    "withdraw_limit_nisa": 0.0, 
    "limit_mode_other": "年額定額 (万円)",
    "withdraw_limit_other": 20.0,
    "inc1_a": 55, "inc1_v": 500, "inc2_a": 0, "inc2_v": 0, "inc3_a": 0, "inc3_v": 0,
    "dec1_a": 66, "dec1_v": 1000, "dec2_a": 0, "dec2_v": 0, "dec3_a": 0, "dec3_v": 0
}

# --- ヘルパー関数: 設定の読み込み・保存 ---

def load_uploaded_settings(uploaded_file):
    """アップロードされたJSONデータを処理し、st.session_stateに反映"""
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
    """現在の設定をJSON文字列として取得"""
    save_data = {}
    for key in DEFAULT_CONFIG.keys():
        if key in st.session_state:
            save_data[key] = st.session_state[key]
    
    return json.dumps(save_data, indent=4, ensure_ascii=False)

# --- メインアプリ ---
st.set_page_config(page_title="簡易資産シミュレータ", page_icon="💰", layout="wide")

def main():
    # 1. アプリ起動時の初期化
    if "first_load_done" not in st.session_state:
        for key, value in DEFAULT_CONFIG.items():
            if key not in st.session_state:
                st.session_state[key] = value
        st.session_state["first_load_done"] = True
    
    # 2. CSSスタイル設定
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;700&display=swap');
        html, body, p, h1, h2, h3, h4, h5, h6, li, span, div.stDataFrame {
            font-family: 'Noto Sans JP', sans-serif;
        }
        h3 { font-weight: 700 !important; }
        .streamlit-expanderHeader { margin-top: 0.5rem; margin-bottom: 0.5rem; font-family: 'Noto Sans JP', sans-serif; }
        .material-icons { font-family: 'Material Icons' !important; }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("### 💰 簡易資産シミュレータ v2.3")
    st.caption("Ver. Advanced Withdrawal Strategy (3-Way Limit)")

    # --- サイドバー設定 ---
    st.sidebar.header("⚙️ 設定パネル")
    
    # ダウンロード・アップロード機能
    st.sidebar.subheader("📁 設定ファイル")
    st.sidebar.download_button(
        label="💾 設定をダウンロード (PCに保存)",
        data=get_download_json(),
        file_name="asset_simulator_config.json",
        mime="application/json"
    )

    uploaded_file = st.sidebar.file_uploader(
        "📤 設定ファイルをアップロード", 
        type=["json"], 
        accept_multiple_files=False,
        help="ダウンロードしたJSONファイルを選択すると、設定が反映されます。"
    )

    if uploaded_file is not None:
        load_uploaded_settings(uploaded_file)
    
    st.sidebar.markdown("---") 
    
    tab1, tab2, tab3, tab4, tab5 = st.sidebar.tabs(["基本・初期", "収入・支出", "積立設定", "取崩し戦略", "臨時収支"])

    # --- 入力 UI ---
    with tab1:
        st.subheader("👤 基本情報")
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

    with tab2:
        st.subheader("🏢 働き方と収入")
        age_work_last = st.number_input("何歳まで働く？", 50, 90, key="age_work_last")
        st.markdown("##### 手取り年収 (万円)")
        inc_20s = st.number_input("〜29歳", 0, 5000, step=10, key="inc_20s") * 10000
        inc_30s = st.number_input("30〜39歳", 0, 5000, step=10, key="inc_30s") * 10000
        inc_40s = st.number_input("40〜49歳", 0, 5000, step=10, key="inc_40s") * 10000
        inc_50s = st.number_input("50〜59歳", 0, 5000, step=10, key="inc_50s") * 10000
        inc_60s = st.number_input("60歳〜", 0, 5000, step=10, key="inc_60s") * 10000
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
        cost_20s = st.number_input("〜29歳 生活費", 0, 500, step=1, key="cost_20s") * 10000
        cost_30s = st.number_input("30代 生活費", 0, 500, step=1, key="cost_30s") * 10000
        cost_40s = st.number_input("40代 生活費", 0, 500, step=1, key="cost_40s") * 10000
        cost_50s = st.number_input("50代 生活費", 0, 500, step=1, key="cost_50s") * 10000
        cost_60s = st.number_input("60歳〜 生活費", 0, 500, step=1, key="cost_60s") * 10000
        st.markdown("##### 年間特別支出 (万円/年)")
        exp_20s = st.number_input("〜29歳 特別出費", 0, 5000, step=10, key="exp_20s") * 10000
        exp_30s = st.number_input("30代 特別出費", 0, 5000, step=10, key="exp_30s") * 10000
        exp_40s = st.number_input("40代 特別出費", 0, 5000, step=10, key="exp_40s") * 10000
        exp_50s = st.number_input("50代 特別出費", 0, 5000, step=10, key="exp_50s") * 10000
        exp_60s = st.number_input("60歳〜 特別出費", 0, 5000, step=10, key="exp_60s") * 10000

    with tab3:
        st.subheader("🌱 積立投資の設定")
        col_t1, col_t2 = st.columns(2)
        with col_t1:
            st.markdown("**1. NISA つみたて投資枠**")
            nisa_monthly = st.number_input("月額積立(円)", 0, 500000, step=1000, key="nisa_monthly", help="ここは年間120万円が上限として計算されます")
            
            nisa_year_val = nisa_monthly * 12
            if nisa_year_val <= 1200000:
                st.info(f"✅ 年間 {nisa_year_val/10000:.0f}万 / 120万")
            else:
                st.warning(f"⚠️ 年間120万を超えています。シミュレーション上は120万として計算します。")

            nisa_stop_age = st.number_input("NISA積立終了年齢", 20, 100, key="nisa_stop_age")
        with col_t2:
            st.markdown("**2. 他運用 (特定口座など)**")
            paypay_monthly = st.number_input("他運用積立(月/円)", 0, 1000000, step=1000, key="paypay_monthly")
            st.write(f"(年間 {paypay_monthly*12/10000:.0f}万円)")
            paypay_stop_age = st.number_input("他運用積立終了年齢", 20, 100, key="paypay_stop_age")
            
        st.markdown("---")
        st.write("※401kは「働く期間」かつ「受取年齢の前」まで積立を行います。")
        k401_monthly = st.number_input("401k積立(月/円)", 0, 500000, step=1000, key="k401_monthly")
        
        st.markdown("---")
        st.subheader("💧 最低貯蓄額 (ダム水位)")
        st.caption("最低貯蓄額を超えた余剰金は、**「NISA 成長投資枠 (最大年240万)」** を埋めるために自動投資されます。")
        dam_1 = st.number_input("〜49歳 最低貯蓄(万)", 0, 10000, step=50, key="dam_1") * 10000
        dam_2 = st.number_input("50代 最低貯蓄(万)", 0, 10000, step=50, key="dam_2") * 10000
        dam_3 = st.number_input("60歳〜 最低貯蓄(万)", 0, 10000, step=50, key="dam_3") * 10000

    with tab4:
        st.subheader("🍂 取り崩し・補填ルール")
        priority = st.radio("取り崩し優先順位 (不足時)", ["新NISAから先に使う", "他運用から先に使う"], horizontal=True, key="priority")
        
        col_out1, col_out2 = st.columns(2)
        with col_out1:
            nisa_start_age = st.number_input("新NISA 解禁年齢", 50, 100, key="nisa_start_age")
        with col_out2:
            paypay_start_age = st.number_input("他運用 解禁年齢", 50, 100, key="paypay_start_age")
        
        st.markdown("---")
        st.write("▼ 取り崩し上限設定 (3つの方式から選択)")
        
        # --- NISA上限設定 ---
        st.markdown("**新NISA の年間上限**")
        c_n_mode, c_n_val = st.columns([3, 2])
        limit_mode_options = ["年額定額 (万円)", "総資産比率 (%)", "残高比率 (%)"]
        
        limit_mode_nisa = c_n_mode.selectbox("NISA上限方式", limit_mode_options, key="limit_mode_nisa", label_visibility="collapsed")
        withdraw_limit_nisa = c_n_val.number_input("NISA上限値", 0.0, 10000.0, step=0.1, key="withdraw_limit_nisa", label_visibility="collapsed")
        
        if limit_mode_nisa == "年額定額 (万円)":
            st.caption(f"年間 **{withdraw_limit_nisa:.0f}万円** まで取り崩します。(0は無制限)")
            nisa_limit_val = withdraw_limit_nisa * 10000
        elif limit_mode_nisa == "総資産比率 (%)":
            st.caption(f"その年の **総資産の {withdraw_limit_nisa:.1f}%** まで取り崩します。")
            nisa_limit_val = withdraw_limit_nisa
        else:
            st.caption(f"その年の **NISA残高の {withdraw_limit_nisa:.1f}%** まで取り崩します。")
            nisa_limit_val = withdraw_limit_nisa

        # --- 他運用上限設定 ---
        st.markdown("**他運用 の年間上限**")
        c_o_mode, c_o_val = st.columns([3, 2])
        
        limit_mode_other = c_o_mode.selectbox("他運用上限方式", limit_mode_options, key="limit_mode_other", label_visibility="collapsed")
        withdraw_limit_other = c_o_val.number_input("他運用上限値", 0.0, 10000.0, step=0.1, key="withdraw_limit_other", label_visibility="collapsed")
        
        if limit_mode_other == "年額定額 (万円)":
            st.caption(f"年間 **{withdraw_limit_other:.0f}万円** まで取り崩します。(0は無制限)")
            other_limit_val = withdraw_limit_other * 10000
        elif limit_mode_other == "総資産比率 (%)":
            st.caption(f"その年の **総資産の {withdraw_limit_other:.1f}%** まで取り崩します。")
            other_limit_val = withdraw_limit_other
        else:
            st.caption(f"その年の **他運用残高の {withdraw_limit_other:.1f}%** まで取り崩します。")
            other_limit_val = withdraw_limit_other

    with tab5:
        st.subheader("💰 臨時収入 (3枠)")
        c_i1_a, c_i1_v = st.columns([1, 2])
        inc1_age = st.number_input("収入① 年齢", 0, 100, key="inc1_a")
        inc1_val = c_i1_v.number_input("収入① 金額(万)", 0, 10000, step=100, key="inc1_v") * 10000
        c_i2_a, c_i2_v = st.columns([1, 2])
        inc2_age = st.number_input("収入② 年齢", 0, 100, key="inc2_a")
        inc2_val = c_i2_v.number_input("収入② 金額(万)", 0, 10000, step=100, key="inc2_v") * 10000
        c_i3_a, c_i3_v = st.columns([1, 2])
        inc3_age = st.number_input("収入③ 年齢", 0, 100, key="inc3_a")
        inc3_val = c_i3_v.number_input("収入③ 金額(万)", 0, 10000, step=100, key="inc3_v") * 10000
        st.markdown("---")
        st.subheader("💸 臨時支出 (3枠)")
        c_d1_a, c_d1_v = st.columns([1, 2])
        dec1_age = st.number_input("支出① 年齢", 0, 100, key="dec1_a")
        dec1_val = c_d1_v.number_input("支出① 金額(万)", 0, 10000, step=100, key="dec1_v") * 10000
        c_d2_a, c_d2_v = st.columns([1, 2])
        dec2_age = st.number_input("支出② 年齢", 0, 100, key="dec2_a")
        dec2_val = c_d2_v.number_input("支出② 金額(万)", 0, 10000, step=100, key="dec2_v") * 10000
        c_d3_a, c_d3_v = st.columns([1, 2])
        dec3_age = st.number_input("支出③ 年齢", 0, 100, key="dec3_a")
        dec3_val = c_d3_v.number_input("支出③ 金額(万)", 0, 10000, step=100, key="dec3_v") * 10000

    # --- 計算ロジック ---
    records = []
    
    cash = ini_cash
    k401 = ini_401k
    nisa = ini_nisa
    paypay = ini_paypay
    nisa_principal = ini_nisa 

    # ★定数
    NISA_TSUMITATE_LIMIT = 1200000 # 年120万
    NISA_GROWTH_LIMIT = 2400000     # 年240万
    NISA_LIFETIME_LIMIT = 18000000 # 生涯1800万

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
        
        # 1. 運用
        cash *= (1 + r_cash)
        nisa *= (1 + r_nisa)
        paypay *= (1 + r_paypay)
        if age < age_401k_get: k401 *= (1 + r_401k)

        # 2. 収入
        is_working = (age <= age_work_last)
        salary = 0
        annual_extra_exp = 0

        if is_working:
            if age < 30: salary = inc_20s; annual_extra_exp = exp_20s
            elif age < 40: salary = inc_30s; annual_extra_exp = exp_30s
            elif age < 50: salary = inc_40s; annual_extra_exp = exp_40s
            elif age < 60: salary = inc_50s; annual_extra_exp = exp_50s
            else: salary = inc_60s; annual_extra_exp = exp_60s
        
        pension = 0
        if age >= age_pension:
            pension = pension_monthly * 12 * (1 - tax_pension)

        # 3. 支出
        base_monthly_cost = 0
        if age < 30: base_monthly_cost = cost_20s
        elif age < 40: base_monthly_cost = cost_30s
        elif age < 50: base_monthly_cost = cost_40s
        elif age < 60: base_monthly_cost = cost_50s
        else: base_monthly_cost = cost_60s

        if age > age_work_last:
            current_cost = base_monthly_cost * 12 * ((1 + inflation) ** (age - age_work_last))
        else:
            current_cost = base_monthly_cost * 12

        # 4. 積立 (つみたて投資枠)
        val_k401_add = k401_monthly * 12 if (is_working and age < age_401k_get) else 0
        
        nisa_tsumitate_year = 0
        nisa_growth_year = 0
        
        # 積立 (cash > 0 or working)
        can_invest = (cash > 0 or is_working)

        val_nisa_add = 0
        if can_invest and age <= nisa_stop_age:
            raw_nisa_add = nisa_monthly * 12
            lifetime_room = max(0, NISA_LIFETIME_LIMIT - nisa_principal)
            
            # 積立枠上限(120万)と生涯枠上限をチェック
            val_nisa_add = min(raw_nisa_add, NISA_TSUMITATE_LIMIT, lifetime_room)
            
            nisa_tsumitate_year = val_nisa_add
            
        val_paypay_add = paypay_monthly * 12 if (can_invest and age <= paypay_stop_age) else 0

        # 5. 資産移動
        k401 += val_k401_add
        nisa += val_nisa_add
        nisa_principal += val_nisa_add
        paypay += val_paypay_add

        # 6. 401k受取
        if age == age_401k_get:
            income_401k = k401 * (1 - tax_401k)
            cash += income_401k
            k401 = 0

        # 7. イベント
        event_inc = 0
        if age == inc1_age: event_inc += inc1_val
        if age == inc2_age: event_inc += inc2_val
        if age == inc3_age: event_inc += inc3_val
        
        event_dec = 0
        if age == dec1_age: event_dec += dec1_val
        if age == dec2_age: event_dec += dec2_val
        if age == dec3_age: event_dec += dec3_val

        # 8. キャッシュフロー
        cash_flow = (salary + pension + event_inc) - (current_cost + annual_extra_exp + event_dec + val_k401_add + val_nisa_add + val_paypay_add)
        cash += cash_flow

        # 9. 補填
        if cash < 0:
            shortage = abs(cash)
            
            # ★現在の総資産（投資資産）を計算
            current_total_investments = nisa + paypay + k401

            # ★上限額の計算関数 (その年の状況に応じて上限額を決定)
            def calc_actual_limit(mode, val, current_asset, total_assets):
                if mode == "年額定額 (万円)":
                    if val == 0: return float('inf') # 0なら無制限
                    return val # 万円単位は後で合わせる? いや、UIで計算済みとするか、ここで計算するか
                    # UIで既に万円単位で入力されているが、ロジック内で合わせる方が安全
                    # いや、変数 nisa_limit_val 等はUIで処理済み
                elif mode == "総資産比率 (%)":
                    return total_assets * (val / 100)
                elif mode == "残高比率 (%)":
                    return current_asset * (val / 100)
                return float('inf')

            # NISAと他運用のその年の上限額(円)を決定
            limit_nisa_yen = calc_actual_limit(limit_mode_nisa, nisa_limit_val, nisa, current_total_investments)
            limit_other_yen = calc_actual_limit(limit_mode_other, other_limit_val, paypay, current_total_investments)

            # 引出し処理関数 (計算済みの上限額を使う)
            def withdraw_asset_logic(needed, current_val, principal_val, is_nisa, limit_yen):
                can_pay = min(needed, current_val, limit_yen)
                
                new_val = current_val - can_pay
                new_principal = principal_val
                
                if is_nisa and current_val > 0 and can_pay > 0:
                    ratio = can_pay / current_val
                    new_principal = principal_val * (1 - ratio)
                
                return can_pay, new_val, new_principal

            # 優先順位分岐
            if priority == "新NISAから先に使う":
                if age >= nisa_start_age:
                    pay_nisa, nisa, nisa_principal = withdraw_asset_logic(shortage, nisa, nisa_principal, True, limit_nisa_yen)
                    shortage -= pay_nisa
                
                if age >= paypay_start_age:
                    pay_other, paypay, _ = withdraw_asset_logic(shortage, paypay, 0, False, limit_other_yen)
                    shortage -= pay_other
            else:
                if age >= paypay_start_age:
                    pay_other, paypay, _ = withdraw_asset_logic(shortage, paypay, 0, False, limit_other_yen)
                    shortage -= pay_other

                if age >= nisa_start_age:
                    pay_nisa, nisa, nisa_principal = withdraw_asset_logic(shortage, nisa, nisa_principal, True, limit_nisa_yen)
                    shortage -= pay_nisa
            
            cash = -shortage

        # 10. ダム機能 (成長投資枠)
        if age < 50: target = dam_1
        elif age < 60: target = dam_2
        else: target = dam_3

        # 現金がターゲットを超えていて、かつ積立終了年齢以下ならNISAへ
        if cash > target and age <= nisa_stop_age:
            surplus = cash - target
            
            # 成長枠上限(240万)と生涯枠残りを計算
            nisa_remaining_space = max(0, NISA_GROWTH_LIMIT - nisa_tsumitate_year) # 成長枠は積立枠と重複可能だが、ここでは分かりやすく別枠として計算
            lifetime_room = max(0, NISA_LIFETIME_LIMIT - nisa_principal)
            
            # 余剰金、成長枠、生涯枠 の中で最も小さい額を移動
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

    # --- 結果表示 ---
    df = pd.DataFrame(records)

    # 1. グラフ
    if "graph_mode" not in st.session_state:
        st.session_state["graph_mode"] = "積み上げ (総資産)"
    current_mode = st.session_state["graph_mode"]

    df_melt = df.melt(id_vars=["Age"], value_vars=["Cash", "401k", "NISA", "Other"], var_name="Asset", value_name="Amount")
    colors = {"Cash": "#636EFA", "NISA": "#EF553B", "401k": "#00CC96", "Other": "#AB63FA"}
    
    if current_mode == "積み上げ (総資産)":
        fig = px.area(df_melt, x="Age", y="Amount", color="Asset", 
                      labels={"Amount": "金額 (円)", "Age": "年齢"}, 
                      color_discrete_map=colors)
    else:
        fig = px.line(df_melt, x="Age", y="Amount", color="Asset", 
                      labels={"Amount": "金額 (円)", "Age": "年齢"}, 
                      color_discrete_map=colors)
    
    fig.update_layout(hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True)

    # 2. スライダー
    st.markdown("<br>", unsafe_allow_html=True)
    target_age = st.slider("確認したい年齢", current_age, end_age, 65)
    try:
        row = df[df["Age"] == target_age].iloc[0]
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric(f"{target_age}歳の総資産", f"{row['Total']/10000:,.0f}万円")
        c2.metric("うち現金", f"{row['Cash']/10000:,.0f}万円")
        c3.metric("うち新NISA", f"{row['NISA']/10000:,.0f}万円", delta=f"元本 {row['NISA元本']/10000:,.0f}万円")
        c4.metric("うち401k", f"{row['401k']/10000:,.0f}万円")
        c5.metric("うち他運用", f"{row['Other']/10000:,.0f}万円")
    except: st.error("データ取得エラー")

    # 3. グラフ切替ボタン
    st.markdown("<br>", unsafe_allow_html=True)
    st.radio("グラフ表示モード", ["積み上げ (総資産)", "折れ線 (個別推移)"], 
             key="graph_mode", horizontal=True)

    # 4. 明細
    st.markdown("<br>", unsafe_allow_html=True)
    with st.expander("📝 年単位の資産明細を表示", expanded=True):
        st.dataframe(df, use_container_width=True)

    # 5. ルール
    st.markdown("<br>", unsafe_allow_html=True)
    with st.expander("ℹ️ このシミュレータのルール（クリックで開く）"):
        st.markdown("""
        1.  **収入はすべて「現金」へ**：給与・年金・臨時収入はまず現金貯金に入ります。
        2.  **年金の手取り**：入力した年金月額から、設定した税率（社会保険料含む）を引いた額が収入となります。
        3.  **つみたて枠（年120万）**：「NISA積立」で設定した金額が優先的に充てられます。
        4.  **成長枠（年240万）**：「最低貯蓄額」を超えた余剰金が、この枠を使って自動投資されます。
        5.  **現金不足時の「取り崩し」**：現金がマイナスになった場合、設定した優先順位に従って補填します。
        6.  **取り崩し上限**：年額固定、総資産比率、残高比率の3パターンから選択できます。
        7.  **積立停止**：現金がマイナス（借金）の年は、新規の積立投資を行いません。
        """)

if __name__ == '__main__':
    main()
