<<<<<<< HEAD
from pathlib import Path
import pandas as pd
import numpy as np
import joblib
import plotly.express as px
import matplotlib.pyplot as plt
import streamlit as st

st.set_page_config(page_title="DEX Tracker", layout="wide")

=======
import joblib
from pathlib import Path
import pandas as pd
import numpy as np
import plotly.express as px
import streamlit as st

# --- Page Config ---
st.set_page_config(page_title="Ethereum DEX Tracker", layout="wide")

# --- Load Data ---
data_path = Path("backend/Database")
df_tvl = joblib.load(data_path / "USDT-pairs_tvl.pkl")
df_volume = joblib.load(data_path / "USDT-pairs_volume.pkl")
df_fdv = joblib.load(data_path / "USDT-pairs_fdv.pkl")
df_dex = joblib.load(data_path / "USDT-pairs_dex.pkl")
df_transactions = joblib.load(data_path / "USDT-pairs_transactions.pkl")

# --- Sidebar: About ---
with st.sidebar:
    st.markdown(
        """
        ### About Ethereum DEX Tracker
        A tool to monitor decentralized exchange (DEX) activity on Ethereum.
        - Track real-time swaps
        - Monitor liquidity pools
        - Spot volume trends
        - Analyze token metrics
        """
    )

# --- Main Page ---
st.title("Ethereum DEX Tracker Dashboard")

# --- Total TVL ---
df_tvl['pair_reserve_in_usd'] = pd.to_numeric(df_tvl['pair_reserve_in_usd'], errors='coerce')
total_tvl = df_tvl['pair_reserve_in_usd'].sum()
st.metric("Total TVL (USD)", f"${total_tvl:,.2f}")

# --- Top Pools by TVL ---
st.subheader("Top Pools by TVL")
df_sorted_tvl = df_tvl.sort_values("pair_reserve_in_usd", ascending=False)
fig_tvl = px.bar(df_sorted_tvl, x="name", y="pair_reserve_in_usd",
                 labels={"pair_reserve_in_usd": "TVL (USD)", "name": "Pool"},
                 color="pair_reserve_in_usd", color_continuous_scale="Greens")
st.plotly_chart(fig_tvl, use_container_width=True)

# --- Total Volume ---
volume_cols = ['vol_5m', 'vol_15m', 'vol_30m', 'vol_1h', 'vol_6h', 'vol_24h']
df_volume[volume_cols] = df_volume[volume_cols].apply(pd.to_numeric, errors='coerce')
total_volume = df_volume[volume_cols].sum().sum()
st.metric("Total Volume (USD)", f"${total_volume:,.2f}")

# --- Volume by Pool ---
st.subheader("Volume per USDT Pool")
df_volume_melted = df_volume.melt(id_vars="name", value_vars=volume_cols,
                                  var_name="Time Window", value_name="Volume (USD)")
fig_vol = px.bar(df_volume_melted, x="name", y="Volume (USD)", color="Time Window")
st.plotly_chart(fig_vol, use_container_width=True)

# --- Turnover Ratio ---
st.subheader("Turnover Ratio (24h Volume / TVL)")
df = pd.merge(df_volume[['name','vol_24h']], df_tvl[['name','pair_reserve_in_usd']], on="name")
df["turnover_ratio"] = df.apply(lambda x: x["vol_24h"]/x["pair_reserve_in_usd"]
                                if x["pair_reserve_in_usd"]>0 else None, axis=1)
fig_turnover = px.bar(df, x="name", y="turnover_ratio", color="turnover_ratio",
                      color_continuous_scale="Blues", labels={"turnover_ratio":"Turnover Ratio"})
st.plotly_chart(fig_turnover, use_container_width=True)

# --- Liquidity Utilization ---
st.subheader("Liquidity Utilization (TVL / FDV)")
df_fdv = df_fdv[['name','fdv_usd']]
df_fdv['fdv_usd'] = pd.to_numeric(df_fdv['fdv_usd'], errors='coerce')
df_liquidity = pd.merge(df_tvl[['name','pair_reserve_in_usd']], df_fdv, on="name")
df_liquidity['liquidity_utilization'] = df_liquidity.apply(
    lambda x: x['pair_reserve_in_usd']/x['fdv_usd'] if x['fdv_usd']>0 else None, axis=1)
fig_liquidity = px.bar(df_liquidity, x="name", y="liquidity_utilization",
                       color="liquidity_utilization", color_continuous_scale="Oranges",
                       labels={"liquidity_utilization":"Liquidity Utilization"})
st.plotly_chart(fig_liquidity, use_container_width=True)

# --- Traders Summary ---
st.subheader("Traders Summary")
buy_cols = ['buys_5m', 'buys_15m', 'buys_1h', 'buys_24h']
sell_cols = ['sells_5m', 'sells_15m', 'sells_1h', 'sells_24h']
buyer_cols = ['buyers_5m', 'buyers_15m', 'buyers_1h', 'buyers_24h']
seller_cols = ['sellers_5m', 'sellers_15m', 'sellers_1h', 'sellers_24h']

df_transactions[buy_cols + sell_cols + buyer_cols + seller_cols] = df_transactions[buy_cols + sell_cols + buyer_cols + seller_cols].apply(pd.to_numeric, errors='coerce')
df_traders = pd.DataFrame({
    "name": df_transactions["name"],
    "total_buys": df_transactions[buy_cols].sum(axis=1),
    "total_sells": df_transactions[sell_cols].sum(axis=1),
    "total_buyers": df_transactions[buyer_cols].sum(axis=1, skipna=True),
    "total_sellers": df_transactions[seller_cols].sum(axis=1, skipna=True),
})
st.dataframe(df_traders)

# --- DEX Pool Counts ---
st.subheader("Number of Pools per DEX")
df_pools_dex = pd.merge(df_tvl[['name']], df_dex, on="name", how="left")
dex_counts = df_pools_dex.groupby('dex').size().reset_index(name='num_pools')
fig_dex = px.bar(dex_counts, x='dex', y='num_pools', color='num_pools', color_continuous_scale="Viridis")
st.plotly_chart(fig_dex, use_container_width=True)