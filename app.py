import streamlit as st
import pandas as pd
import plotly.express as px
import json
import os

# --- 設定保存用ファイル名 ---
CONFIG_FILE = "asset_config_v2.json"

# --- デフォルト設定値 ---
DEFAULT_CONFIG = {
    "current_age": 48, "end_age": 100,
    "ini_cash": 500, "ini_401k": 500, "ini_nisa": 100, "ini_paypay": 10,
    "r_cash": 0.01, "r_401k": 5.0, "r_nisa": 5.0, "r_paypay": 6.0, "inflation": 2.0,
    "age_work_last": 65,
    "inc_20s": 300, "inc_30s": 400, "inc_40s": 500, "inc_50s": 600, "inc_60s": 400,
    "age_401k_get": 65, "tax_401k": 12.0, "age_pension": 70, "pension_monthly": 200000, "tax_pension": 15.0,
    "cost_20s": 20, "cost_30s": 25, "cost_40s": 30, "cost_50s": 30, "cost_60s": 25,
    "exp_20s": 50, "exp_30s": 100, "exp_40s": 150, "exp_50s": 100, "exp_60s": 50,
    "nisa_monthly": 50000, "nisa_stop_age": 65,
    "paypay_monthly": 10000, "paypay_stop_age": 65,
    "k401_monthly": 20000,
    "dam_1": 500, "dam_2": 700, "dam_3": 300,
    "priority": "新NISAから先に使う",
    "nisa_start_age": 60, "paypay_start_age": 60,
    "withdraw_limit_nisa": 0, 
    "withdraw_limit_other": 0,
    "inc1_a": 0, "inc1_v": 0, "inc2_a": 0, "inc2_v": 0, "inc3_a": 0, "inc3_v": 0,
    "dec1_a": 65, "dec1_v": 300, "dec2_a": 0, "dec2_v": 0, "dec3_a": 0, "dec3_v": 0
}

def load_settings():
    config = DEFAULT_CONFIG.copy()
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                saved_config = json.load(f)
                config.update(saved_config)
        except Exception as e:
            st.error(f"設定読み込みエラー: {e}")
    for key, value in config.items():
        if key not in st.session_state:
            st.session_state[key] = value

def save_settings():
    save_data = {}
    for key in DEFAULT_CONFIG.keys():
        if key in st.session_state:
            save_data[key] = st.session_state[key]
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(save_data, f, indent=4, ensure_ascii=False)
        st.sidebar.success(f"✅ 設定を保存しました！\n(保存先: {CONFIG_FILE})")
    except Exception as e:
        st.sidebar.error(f"保存失敗: {e}")

st.set_page_config(page_title="簡易資産シミュレータ", page_icon="💰", layout="wide")

def main():
    if "first_load_done" not in st.session_state:
        load_settings()
        st.session_state["first_load_done"] = True

    # タイトル
    st.title("💰 簡易資産シミュレータ v2.8")
    st.caption("Ver. Layout Optimization")

    # --- サイドバー設定 ---
    st.sidebar.header("⚙️ 設定パネル")
    if st.sidebar.button("💾 設定をPCに保存"):
        save_settings()

    tab1, tab2, tab3, tab4, tab5 = st.sidebar.tabs(["基本・初期", "収入・支出", "積立設定", "取崩し戦略", "臨時収支"])

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
            nisa_monthly = st.number_input("NISA積立(月/円)", 0, 300000, step=1000, key="nisa_monthly")
            nisa_stop_age = st.number_input("NISA積立終了年齢", 20, 100, key="nisa_stop_age")
        with col_t2:
            paypay_monthly = st.number_input("他運用積立(月/円)", 0, 1000000, step=1000, key="paypay_monthly")
            paypay_stop_age = st.number_input("他運用積立終了年齢", 20, 100, key="paypay_stop_age")
        k401_monthly = st.number_input("401k積立(月/円)", 0, 500000, step=1000, key="k401_monthly")
        st.markdown("---")
        st.subheader("💧 最低貯蓄額 (ダム水位)")
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
        st.write("▼ 年間取り崩し上限 (0は無制限)")
        c_lim1, c_lim2 = st.columns(2)
        with c_lim1:
            withdraw_limit_nisa = st.number_input("新NISA 上限(万円)", 0, 5000, step=10, key="withdraw_limit_nisa") * 10000
        with c_lim2:
            withdraw_limit_other = st.number_input("他運用 上限(万円)", 0, 5000, step=10, key="withdraw_limit_other") * 10000

    with tab5:
        st.subheader("💰 臨時収入 (3枠)")
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
        st.subheader("💸 臨時支出 (3枠)")
        c_d1_a, c_d1_v = st.columns([1, 2])
        dec1_age = c_d1_a.number_input("支出① 年齢", 0, 100, key="dec1_a")
        dec1_val = c_d1_v.number_input("支出① 金額(万)", 0, 10000, step=100, key="dec1_v") * 10000
        c_d2_a, c_d2_v = st.columns([1, 2])
        dec2_age = c_d2_a.number_input("支出② 年齢", 0, 100, key="dec2_a")
        dec2_val = c_d2_v.number_input("支出② 金額(万)", 0, 10000, step=100, key="dec2_v") * 10000
        c_d3_a, c_d3_v = st.columns([1, 2])
        dec3_age = c_d3_a.number_input("支出③ 年齢", 0, 100, key="dec3_a")
        dec3_val = c_d3_v.number_input("支出③ 金額(万)", 0, 10000, step=100, key="dec3_v") * 10000

    # --- 計算ロジック ---
    records = []
    
    cash = ini_cash
    k401 = ini_401k
    nisa = ini_nisa
    paypay = ini_paypay
    nisa_principal = ini_nisa 

    NISA_ANNUAL_LIMIT = 3600000
    NISA_LIFETIME_LIMIT = 18000000

    records.append({
        "Age": current_age,
        "Total": int(cash + k401 + nisa + paypay),
        "Cash": int(cash),
        "401k": int(k401),
        "NISA": int(nisa),
        "NISA元本": int(nisa_principal),
        "Other": int(paypay)
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

        # 4. 積立
        val_k401_add = k401_monthly * 12 if (is_working and age < age_401k_get) else 0
        
        raw_nisa_add = nisa_monthly * 12 if (is_working and age <= nisa_stop_age) else 0
        lifetime_room = max(0, NISA_LIFETIME_LIMIT - nisa_principal)
        val_nisa_add = min(raw_nisa_add, NISA_ANNUAL_LIMIT, lifetime_room)
        
        val_paypay_add = paypay_monthly * 12 if (is_working and age <= paypay_stop_age) else 0

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

        # 9. 補填 (リレーロジック)
        if cash < 0:
            shortage = abs(cash)
            
            def withdraw_asset_logic(needed, current_val, principal_val, is_nisa, limit_setting):
                actual_limit = float('inf') if limit_setting == 0 else limit_setting
                can_pay = min(needed, current_val, actual_limit)
                new_val = current_val - can_pay
                new_principal = principal_val
                if is_nisa and current_val > 0 and can_pay > 0:
                    ratio = can_pay / current_val
                    new_principal = principal_val * (1 - ratio)
                return can_pay, new_val, new_principal

            if priority == "新NISAから先に使う":
                if age >= nisa_start_age:
                    pay_nisa, nisa, nisa_principal = withdraw_asset_logic(shortage, nisa, nisa_principal, True, withdraw_limit_nisa)
                    shortage -= pay_nisa
                if age >= paypay_start_age:
                    pay_other, paypay, _ = withdraw_asset_logic(shortage, paypay, 0, False, withdraw_limit_other)
                    shortage -= pay_other
            else:
                if age >= paypay_start_age:
                    pay_other, paypay, _ = withdraw_asset_logic(shortage, paypay, 0, False, withdraw_limit_other)
                    shortage -= pay_other
                if age >= nisa_start_age:
                    pay_nisa, nisa, nisa_principal = withdraw_asset_logic(shortage, nisa, nisa_principal, True, withdraw_limit_nisa)
                    shortage -= pay_nisa
            
            cash = -shortage

        # 10. ダム機能
        if age < 50: target = dam_1
        elif age < 6
