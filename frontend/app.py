import joblib
from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st

# --- Page Config ---
st.set_page_config(
    page_title="Ethereum USDT Pool Tracker",
    page_icon="💵",
    layout="wide"
)

# --- Custom CSS (Glassmorphism / 3D effect + larger tabs) ---
st.markdown("""
    <style>
        .stApp {
            background: linear-gradient(135deg, #f0f5ff, #e6f7ff);
            color: #1c1c1c;
            font-family: "Segoe UI", sans-serif;
        }
        div[data-testid="stMetricValue"] {
            font-size: 1.8rem;
            font-weight: 600;
            color: #0056b3;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
        }
        section[data-testid="stSidebar"] {
            background: rgba(255, 255, 255, 0.7);
            backdrop-filter: blur(12px);
            border-radius: 12px;
        }
        h1, h2, h3 {
            color: #003366 !important;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
        }
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        /* Make tabs bigger */
        button[data-baseweb="tab"] > div {
            font-size: 1.2rem !important;
            font-weight: 600 !important;
            padding: 14px 18px !important;
            border-radius: 10px !important;
        }
        button[data-baseweb="tab"] {
            background: rgba(255, 255, 255, 0.8) !important;
            box-shadow: 0 4px 10px rgba(0,0,0,0.1) !important;
        }
        button[data-baseweb="tab"]:hover {
            background: #cce6ff !important;
        }
        button[data-baseweb="tab"][aria-selected="true"] {
            background: #80bfff !important;
            color: white !important;
        }
    </style>
""", unsafe_allow_html=True)

# --- Load Data ---
data_path = Path("backend/Database")
df_tvl = joblib.load(data_path / "USDT-pairs_tvl.pkl")
df_volume = joblib.load(data_path / "USDT-pairs_volume.pkl")
df_fdv = joblib.load(data_path / "USDT-pairs_fdv.pkl")
df_dex = joblib.load(data_path / "USDT-pairs_dex.pkl")
df_transactions = joblib.load(data_path / "USDT-pairs_transactions.pkl")

# --- Sidebar ---
with st.sidebar:
    st.markdown("## 💵 USDT Pool Tracker")
    st.write(
        """
        Track **Ethereum DEX pools paired with USDT**  

        🔹 **Features:**  
        - 📊 Pool TVL (Total Value Locked)  
        - 🔄 Turnover ratio  
        - 💧 Pool reserves & utilization  
        - 👥 Traders & activity  
        """
    )

    st.markdown("---")
    st.markdown("### ⚙️ Data Sources")
    st.write("On-chain APIs + Python (Pandas, Plotly, Streamlit)")
    st.markdown("---")
    st.markdown("### 👨‍💻 Authors")
    st.write("Built with ❤️ by [Realist](https://github.com/christian-obi) & [vhictoirya](https://github.com/vhictoirya)")
    st.markdown("---")
    st.markdown("🔗 [GitHub Repo](https://github.com/christian-obi/DEX-tracker)")

# --- Hero Section ---
st.markdown(
    """
    <div style="background: rgba(255,255,255,0.8);
                backdrop-filter: blur(15px);
                padding:20px;
                border-radius:15px;
                box-shadow:0 8px 18px rgba(0,0,0,0.15);
                margin-bottom:25px;">
        <h1 style="color:#003366;">💵 Ethereum USDT Pool Tracker</h1>
        <p style="color:#333;">
        Monitor Ethereum liquidity pools paired with <b>USDT</b>:  
        🔹 Track TVL • 🔹 Volume • 🔹 Turnover • 🔹 Traders
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

# --- Preprocess ---
df_tvl['pair_reserve_in_usd'] = pd.to_numeric(df_tvl['pair_reserve_in_usd'], errors='coerce')
df_fdv['fdv_usd'] = pd.to_numeric(df_fdv['fdv_usd'], errors='coerce')
volume_cols = ['vol_5m', 'vol_15m', 'vol_30m', 'vol_1h', 'vol_6h', 'vol_24h']
df_volume[volume_cols] = df_volume[volume_cols].apply(pd.to_numeric, errors='coerce')

# --- KPIs ---
total_tvl = df_tvl['pair_reserve_in_usd'].sum()
total_volume = df_volume[volume_cols].sum().sum()
avg_turnover = (df_volume['vol_24h'] / df_tvl['pair_reserve_in_usd']).mean()

col1, col2, col3 = st.columns(3)
col1.metric("🌊 Total TVL", f"${total_tvl:,.0f}")
col2.metric("📈 Total Volume", f"${total_volume:,.0f}")
col3.metric("🔄 Avg Turnover", f"{avg_turnover:.2f}x")

# --- Tabs for Charts ---
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 TVL",
    "📈 Volume",
    "🔄 Turnover",
    "👥 Traders",
    "🏦 DEX Overview"
])

# TVL
with tab1:
    st.subheader("Top Pools by TVL")
    df_sorted_tvl = df_tvl.sort_values("pair_reserve_in_usd", ascending=False)
    fig_tvl = px.bar(df_sorted_tvl, x="name", y="pair_reserve_in_usd",
                     labels={"pair_reserve_in_usd": "TVL (USD)", "name": "Pool"},
                     color="pair_reserve_in_usd", color_continuous_scale="Blues")
    st.plotly_chart(fig_tvl, use_container_width=True)

# Volume
with tab2:
    st.subheader("Volume per Pool")
    df_volume_melted = df_volume.melt(
        id_vars="name", value_vars=volume_cols,
        var_name="Time Window", value_name="Volume (USD)"
    )
    fig_vol = px.bar(df_volume_melted, x="name", y="Volume (USD)", color="Time Window")
    st.plotly_chart(fig_vol, use_container_width=True)

# Turnover
with tab3:
    st.subheader("Turnover Ratio (24h Volume / TVL)")
    df_turnover = pd.merge(df_volume[['name','vol_24h']], df_tvl[['name','pair_reserve_in_usd']], on="name")
    df_turnover["turnover_ratio"] = df_turnover.apply(
        lambda x: x["vol_24h"]/x["pair_reserve_in_usd"] if x["pair_reserve_in_usd"]>0 else None, axis=1
    )
    fig_turnover = px.bar(
        df_turnover, x="name", y="turnover_ratio", color="turnover_ratio",
        color_continuous_scale="Teal", labels={"turnover_ratio":"Turnover Ratio"}
    )
    st.plotly_chart(fig_turnover, use_container_width=True)

# Traders
with tab4:
    st.subheader("Traders Summary")
    buy_cols = ['buys_5m', 'buys_15m', 'buys_1h', 'buys_24h']
    sell_cols = ['sells_5m', 'sells_15m', 'sells_1h', 'sells_24h']
    buyer_cols = ['buyers_5m', 'buyers_15m', 'buyers_1h', 'buyers_24h']
    seller_cols = ['sellers_5m', 'sellers_15m', 'sellers_1h', 'sellers_24h']

    df_transactions[buy_cols + sell_cols + buyer_cols + seller_cols] = df_transactions[
        buy_cols + sell_cols + buyer_cols + seller_cols].apply(pd.to_numeric, errors='coerce')

    df_traders = pd.DataFrame({
        "name": df_transactions["name"],
        "total_buys": df_transactions[buy_cols].sum(axis=1),
        "total_sells": df_transactions[sell_cols].sum(axis=1),
        "total_buyers": df_transactions[buyer_cols].sum(axis=1, skipna=True),
        "total_sellers": df_transactions[seller_cols].sum(axis=1, skipna=True),
    })
    st.dataframe(df_traders)

# DEX Overview
with tab5:
    st.subheader("Number of Pools per DEX")
    df_pools_dex = pd.merge(df_tvl[['name']], df_dex, on="name", how="left")
    dex_counts = df_pools_dex.groupby('dex').size().reset_index(name='num_pools')
    fig_dex = px.bar(
        dex_counts, x='dex', y='num_pools',
        color='num_pools', color_continuous_scale="Viridis"
    )
    st.plotly_chart(fig_dex, use_container_width=True)

# --- Footer ---
st.markdown(
    """
    <hr>
    <center>
    <b>Built with ❤️ for Web3 analysts • Powered by Ethereum on-chain data</b>  
    <br>
    Follow <a href="https://x.com/_christian_obi" target="_blank">@christian_obi</a> 
    and <a href="https://x.com/vhictoirya" target="_blank">@vhictoirya</a> for updates
    </center>

    """,
    unsafe_allow_html=True
)
