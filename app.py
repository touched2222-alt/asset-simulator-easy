import streamlit as st
import pandas as pd
import plotly.express as px

# ページ設定
st.set_page_config(page_title="簡易資産シミュレータ", page_icon="💰", layout="wide")

def main():
    st.title("💰 簡易資産シミュレータ v2.1")
    st.caption("NISA Limit Edition: 年間360万円上限対応")

    with st.expander("ℹ️ このシミュレータのルール（クリックで開く）"):
        st.markdown("""
        1.  **収入はすべて「現金」へ**：給与・年金・臨時収入はまず現金貯金に入ります。
        2.  **支出は「現金」から**：生活費やイベント費は現金から支払います。
        3.  **現金余剰は「新NISA」へ**：設定した「最低貯蓄額」を超えた分は自動投資されます（**年間上限360万円**）。120、240は意識してません。
        4.  **現金不足時の「取り崩し」**：現金がマイナスになった場合、設定した「解禁年齢」と「優先順位」に従って、資産を取り崩して補填します。
        5.  **退職の概念**：『65歳で退職』と言った場合、よくある概念は65歳の誕生日で退職（64歳の最後の日まで仕事）です。
        """)

    # --- サイドバー設定 ---
    st.sidebar.header("⚙️ 設定パネル")
    tab1, tab2, tab3, tab4, tab5 = st.sidebar.tabs(["基本・初期", "収入・支出", "積立設定", "取崩し戦略", "臨時収支"])

    with tab1: # 基本・初期
        st.subheader("👤 基本情報")
        current_age = st.number_input("現在年齢", 20, 80, 48)
        end_age = st.number_input("終了年齢", 80, 120, 100)
        
        st.markdown("---")
        st.subheader("💰 現在の資産 (万円)")
        ini_cash = st.number_input("貯蓄 (現金)", 0, 10000, 500, step=10) * 10000
        ini_401k = st.number_input("401k (確定拠出)", 0, 10000, 500, step=10) * 10000
        ini_nisa = st.number_input("新NISA", 0, 10000, 100, step=10) * 10000
        ini_paypay = st.number_input("他運用 (ポイント運用なども可)", 0, 10000, 10, step=10) * 10000

        st.markdown("---")
        st.subheader("📈 運用利回り (%)")
        r_cash = st.number_input("貯蓄金利", 0.0, 10.0, 0.01, 0.01, format="%.2f") / 100
        r_401k = st.number_input("401k年利", 0.0, 30.0, 5.0, 0.1, format="%.2f") / 100
        r_nisa = st.number_input("新NISA年利", 0.0, 30.0, 5.0, 0.1, format="%.2f") / 100
        r_paypay = st.number_input("他運用年利", 0.0, 50.0, 6.0, 0.1, format="%.2f") / 100
        inflation = st.number_input("インフレ率", -5.0, 20.0, 2.0, 0.1, format="%.2f") / 100

    with tab2: # 収入・支出
        st.subheader("🏢 働き方と収入")
        age_work_last = st.number_input("何歳まで働く？", 50, 90, 65)
        
        st.markdown("##### 手取り年収 (万円)")
        inc_20s = st.number_input("〜29歳", 0, 5000, 300, step=10) * 10000
        inc_30s = st.number_input("30〜39歳", 0, 5000, 400, step=10) * 10000
        inc_40s = st.number_input("40〜49歳", 0, 5000, 500, step=10) * 10000
        inc_50s = st.number_input("50〜59歳", 0, 5000, 600, step=10) * 10000
        inc_60s = st.number_input("60歳〜", 0, 5000, 400, step=10) * 10000

        st.markdown("---")
        st.subheader("🐢 年金・退職金")
        age_401k_get = st.number_input("401k受取年齢", 50, 80, 65)
        tax_401k = st.number_input("401k受取税率(%)", 0.0, 50.0, 10.0, 0.1, format="%.1f") / 100
        age_pension = st.number_input("年金開始年齢", 60, 75, 70)
        pension_monthly = st.number_input("年金月額(円)", 0, 500000, 150000, step=10000)

        st.markdown("---")
        st.subheader("🛒 支出設定")
        cost_base = st.number_input("基本生活費(月/万円)", 0, 200, 25) * 10000
        
        st.markdown("##### 年間特別支出 (万円/年)")
        exp_20s = st.number_input("〜29歳 特別出費", 0, 5000, 50, step=10) * 10000
        exp_30s = st.number_input("30代 特別出費", 0, 5000, 100, step=10) * 10000
        exp_40s = st.number_input("40代 特別出費", 0, 5000, 150, step=10) * 10000
        exp_50s = st.number_input("50代 特別出費", 0, 5000, 100, step=10) * 10000
        exp_60s = st.number_input("60歳〜 特別出費", 0, 5000, 50, step=10) * 10000

    with tab3: # 積立設定
        st.subheader("🌱 積立投資の設定")
        st.caption("給与がある期間のうち、設定した年齢まで積立を行います。")

        col_t1, col_t2 = st.columns(2)
        with col_t1:
            nisa_monthly = st.number_input("NISA積立(月/円)", 0, 300000, 50000, step=1000)
            nisa_stop_age = st.number_input("NISA積立終了年齢", 20, 100, 65)
        with col_t2:
            paypay_monthly = st.number_input("他運用積立(月/円)", 0, 1000000, 10000, step=1000)
            paypay_stop_age = st.number_input("他運用積立終了年齢", 20, 100, 65)
        
        st.info("※401kは「働く期間」かつ「受取年齢の前」まで自動で積み立てられます。")
        k401_monthly = st.number_input("401k積立(月/円)", 0, 500000, 20000, step=1000)

        st.markdown("---")
        st.subheader("💧 最低貯蓄額 (ダム水位)")
        st.caption("貯蓄が現金を上回った場合、余剰分が自動でNISAに追加投資されます（年間上限あり）。")
        dam_1 = st.number_input("〜49歳 最低貯蓄(万)", 0, 10000, 500, step=50) * 10000
        dam_2 = st.number_input("50代 最低貯蓄(万)", 0, 10000, 700, step=50) * 10000
        dam_3 = st.number_input("60歳〜 最低貯蓄(万)", 0, 10000, 300, step=50) * 10000

    with tab4: # 取崩し戦略
        st.subheader("🍂 取り崩し・補填ルール")
        st.write("現金がマイナスになった時、どの資産を・いつから使うかの設定です。")

        priority = st.radio("取り崩し優先順位 (不足時)", ["新NISAから先に使う", "他運用から先に使う"], horizontal=True)

        col_out1, col_out2 = st.columns(2)
        with col_out1:
            nisa_start_age = st.number_input("新NISA 解禁年齢", 50, 100, 60, help="この年齢になるまでは、現金不足でもNISAには手を付けません")
        with col_out2:
            paypay_start_age = st.number_input("他運用 解禁年齢", 50, 100, 60, help="この年齢になるまでは、現金不足でも他運用には手を付けません")

    with tab5: # 臨時イベント
        st.subheader("💰 臨時収入 (3枠)")
        c_i1_a, c_i1_v = st.columns([1, 2])
        inc1_age = c_i1_a.number_input("収入① 年齢", 0, 100, 0)
        inc1_val = c_i1_v.number_input("収入① 金額(万)", 0, 10000, 0, step=100) * 10000
        c_i2_a, c_i2_v = st.columns([1, 2])
        inc2_age = c_i2_a.number_input("収入② 年齢", 0, 100, 0)
        inc2_val = c_i2_v.number_input("収入② 金額(万)", 0, 10000, 0, step=100) * 10000
        c_i3_a, c_i3_v = st.columns([1, 2])
        inc3_age = c_i3_a.number_input("収入③ 年齢", 0, 100, 0)
        inc3_val = c_i3_v.number_input("収入③ 金額(万)", 0, 10000, 0, step=100) * 10000

        st.markdown("---")
        st.subheader("💸 臨時支出 (3枠)")
        c_d1_a, c_d1_v = st.columns([1, 2])
        dec1_age = c_d1_a.number_input("支出① 年齢", 0, 100, 65)
        dec1_val = c_d1_v.number_input("支出① 金額(万)", 0, 10000, 300, step=100) * 10000
        c_d2_a, c_d2_v = st.columns([1, 2])
        dec2_age = c_d2_a.number_input("支出② 年齢", 0, 100, 0)
        dec2_val = c_d2_v.number_input("支出② 金額(万)", 0, 10000, 0, step=100) * 10000
        c_d3_a, c_d3_v = st.columns([1, 2])
        dec3_age = c_d3_a.number_input("支出③ 年齢", 0, 100, 0)
        dec3_val = c_d3_v.number_input("支出③ 金額(万)", 0, 10000, 0, step=100) * 10000

    # --- 計算ロジック ---
    records = []
    
    # 初期化
    cash = ini_cash
    k401 = ini_401k
    nisa = ini_nisa
    paypay = ini_paypay
    
    NISA_ANNUAL_LIMIT = 3600000 # 年間上限360万円

    # 0歳時点記録
    records.append({
        "Age": current_age,
        "Total": int(cash + k401 + nisa + paypay),
        "Cash": int(cash),
        "401k": int(k401),
        "NISA": int(nisa),
        "Other": int(paypay)
    })

    for age in range(current_age + 1, end_age + 1):
        
        # 1. 運用益の加算
        cash *= (1 + r_cash)
        nisa *= (1 + r_nisa)
        paypay *= (1 + r_paypay)
        if age < age_401k_get:
            k401 *= (1 + r_401k)

        # 2. 収入の決定
        is_working = (age <= age_work_last)
        salary = 0
        annual_extra_exp = 0

        if is_working:
            if age < 30:
                salary = inc_20s; annual_extra_exp = exp_20s
            elif age < 40:
                salary = inc_30s; annual_extra_exp = exp_30s
            elif age < 50:
                salary = inc_40s; annual_extra_exp = exp_40s
            elif age < 60:
                salary = inc_50s; annual_extra_exp = exp_50s
            else:
                salary = inc_60s; annual_extra_exp = exp_60s
        
        pension = pension_monthly * 12 if age >= age_pension else 0

        # 3. 支出の決定（インフレ考慮）
        if age > age_work_last:
            current_cost = cost_base * 12 * ((1 + inflation) ** (age - age_work_last))
        else:
            current_cost = cost_base * 12

        # 4. 積立 (働いていて、かつ設定した積立終了年齢以下なら)
        val_k401_add = k401_monthly * 12 if (is_working and age < age_401k_get) else 0
        
        # NISA積立：ここでまず360万上限チェック
        raw_nisa_add = nisa_monthly * 12 if (is_working and age <= nisa_stop_age) else 0
        val_nisa_add = min(raw_nisa_add, NISA_ANNUAL_LIMIT) # 積立だけで360万超えたらカット
        
        val_paypay_add = paypay_monthly * 12 if (is_working and age <= paypay_stop_age) else 0

        # 5. 資産移動 (積立)
        k401 += val_k401_add
        nisa += val_nisa_add
        paypay += val_paypay_add

        # 6. 401k受取 (一括受取と仮定)
        if age == age_401k_get:
            income_401k = k401 * (1 - tax_401k)
            cash += income_401k
            k401 = 0

        # 7. イベント収支
        event_inc = 0
        if age == inc1_age: event_inc += inc1_val
        if age == inc2_age: event_inc += inc2_val
        if age == inc3_age: event_inc += inc3_val
        
        event_dec = 0
        if age == dec1_age: event_dec += dec1_val
        if age == dec2_age: event_dec += dec2_val
        if age == dec3_age: event_dec += dec3_val

        # 8. 現金キャッシュフロー計算
        # 収入 - (生活費 + 特別費 + イベント支出 + 積立投資)
        cash_flow = (salary + pension + event_inc) - (current_cost + annual_extra_exp + event_dec + val_k401_add + val_nisa_add + val_paypay_add)
        cash += cash_flow

        # 9. 資産取り崩し (補填ロジック)
        if cash < 0:
            shortage = abs(cash)
            
            # 補填関数
            def withdraw_asset(needed, asset_val, asset_name, start_age):
                if age < start_age: # 解禁年齢前なら使えない
                    return 0, asset_val
                
                can_pay = min(needed, asset_val)
                return can_pay, asset_val - can_pay

            # 優先順位分岐
            if priority == "新NISAから先に使う":
                pay_nisa, nisa = withdraw_asset(shortage, nisa, "NISA", nisa_start_age)
                shortage -= pay_nisa
                
                pay_other, paypay = withdraw_asset(shortage, paypay, "Other", paypay_start_age)
                shortage -= pay_other
            else:
                pay_other, paypay = withdraw_asset(shortage, paypay, "Other", paypay_start_age)
                shortage -= pay_other

                pay_nisa, nisa = withdraw_asset(shortage, nisa, "NISA", nisa_start_age)
                shortage -= pay_nisa
            
            cash = -shortage

        # 10. 資産自動移動 (ダム機能)
        # 補填後の現金がターゲットを超えていたらNISAへ (ただし年間上限360万まで)
        if age < 50: target = dam_1
        elif age < 60: target = dam_2
        else: target = dam_3

        if cash > target:
            surplus = cash - target
            
            # 残りのNISA枠を計算
            nisa_remaining_space = max(0, NISA_ANNUAL_LIMIT - val_nisa_add)
            
            # 余剰金 と 残り枠 の小さい方だけ移動
            move = min(surplus, nisa_remaining_space)
            
            cash -= move
            nisa += move

        # 記録
        records.append({
            "Age": age,
            "Total": int(cash + k401 + nisa + paypay),
            "Cash": int(cash),
            "401k": int(k401),
            "NISA": int(nisa),
            "Other": int(paypay)
        })

    # --- 結果表示 ---
    df = pd.DataFrame(records)

    st.markdown("### 📊 資産推移シミュレーション")
    
    # グラフ描画
    df_melt = df.melt(id_vars=["Age"], value_vars=["Cash", "401k", "NISA", "Other"], var_name="Asset", value_name="Amount")
    colors = {"Cash": "#636EFA", "NISA": "#EF553B", "401k": "#00CC96", "Other": "#AB63FA"}
    
    fig = px.area(df_melt, x="Age", y="Amount", color="Asset", 
                  labels={"Amount": "金額 (円)", "Age": "年齢"}, 
                  color_discrete_map=colors,
                  title="総資産の推移 (積み上げ)")
    st.plotly_chart(fig, use_container_width=True)

    # 最終結果カード
    last_row = df.iloc[-1]
    st.markdown("### 🏁 最終結果")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("終了年齢", f"{end_age}歳")
    c2.metric("総資産", f"{last_row['Total']/10000:,.0f}万円")
    c3.metric("うち新NISA", f"{last_row['NISA']/10000:,.0f}万円")
    
    # 判定
    if last_row['Total'] < 0:
        st.error(f"⚠️ {end_age}歳時点で資金が枯渇しています！")
    else:
        st.success(f"🎉 {end_age}歳まで資産寿命が持ちました！")

if __name__ == '__main__':
    main()
