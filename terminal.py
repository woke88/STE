import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import json
from datetime import datetime, timedelta
import time
import os
import glob

# CSV file loading functions
@st.cache_data(ttl=30)  # Cache for 30 seconds for live updates
def get_steam_prices_data():
    try:
        if os.path.exists("steam_prices.csv"):
            df = pd.read_csv("steam_prices.csv")
            if not df.empty:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                df['created_at'] = pd.to_datetime(df['created_at'])
            return df
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error loading steam prices: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=30)
def get_tf2_market_data():
    try:
        order_df = pd.DataFrame()
        listing_df = pd.DataFrame()
        
        if os.path.exists("tf2_orders.csv"):
            order_df = pd.read_csv("tf2_orders.csv")
            if not order_df.empty:
                order_df['created_at'] = pd.to_datetime(order_df['created_at'])
        
        if os.path.exists("tf2_listings.csv"):
            listing_df = pd.read_csv("tf2_listings.csv")
            if not listing_df.empty:
                listing_df['created_at'] = pd.to_datetime(listing_df['created_at'])
            
        return order_df, listing_df
    except Exception as e:
        st.error(f"Error loading TF2 market data: {e}")
        return pd.DataFrame(), pd.DataFrame()

@st.cache_data(ttl=30)
def get_supply_data():
    try:
        if os.path.exists("supply_data.csv"):
            df = pd.read_csv("supply_data.csv")
            if not df.empty:
                df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
                df['created_at'] = pd.to_datetime(df['created_at'])
            return df
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error loading supply data: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=30)
def get_monitor_data():
    try:
        history_df = pd.DataFrame()
        alerts_df = pd.DataFrame()
        
        if os.path.exists("monitor_data.csv"):
            history_df = pd.read_csv("monitor_data.csv")
            if not history_df.empty:
                history_df['timestamp'] = pd.to_datetime(history_df['timestamp'], unit='s')
                history_df['created_at'] = pd.to_datetime(history_df['created_at'])
        
        if os.path.exists("alerts.csv"):
            alerts_df = pd.read_csv("alerts.csv")
            if not alerts_df.empty:
                alerts_df['timestamp'] = pd.to_datetime(alerts_df['timestamp'], unit='s')
                alerts_df['created_at'] = pd.to_datetime(alerts_df['created_at'])
            
        return history_df, alerts_df
    except Exception as e:
        st.error(f"Error loading monitor data: {e}")
        return pd.DataFrame(), pd.DataFrame()

# Bloomberg Terminal CSS
st.set_page_config(
    page_title="TF2 MARKET TERMINAL - LIVE DATA", 
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap');
        
        .main {
            background-color: #000000;
            color: #ffffff;
            font-family: 'JetBrains Mono', monospace;
        }
        
        .sidebar .sidebar-content {
            background-color: #0a0a0a;
            border-right: 2px solid #ff6600;
        }
        
        h1 {
            color: #ff6600;
            font-family: 'JetBrains Mono', monospace;
            font-weight: 700;
            font-size: 2.8rem;
            margin-bottom: 0.5rem;
            border-bottom: 3px solid #ff6600;
            padding-bottom: 15px;
            text-transform: uppercase;
            letter-spacing: 2px;
        }
        
        .metric-container {
            background-color: #0a0a0a;
            border: 2px solid #333333;
            border-radius: 2px;
            padding: 20px;
            margin: 8px 0;
            transition: all 0.3s ease;
        }
        
        .metric-container:hover {
            border-color: #ff6600;
            box-shadow: 0 0 20px rgba(255, 102, 0, 0.3);
        }
        
        .metric-value {
            font-size: 2.2rem;
            font-weight: 700;
            font-family: 'JetBrains Mono', monospace;
        }
        
        .metric-label {
            font-size: 0.85rem;
            color: #cccccc;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .positive { color: #00ff00; }
        .negative { color: #ff0000; }
        .neutral { color: #ffffff; }
        .warning { color: #ffff00; }
        
        .terminal-header {
            background-color: #ff6600;
            color: #000000;
            padding: 10px;
            font-family: 'JetBrains Mono', monospace;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 2px;
            margin-bottom: 20px;
        }
        
        .alert-box {
            background-color: #1a0000;
            border: 2px solid #ff0000;
            padding: 15px;
            margin: 10px 0;
            font-family: 'JetBrains Mono', monospace;
            font-weight: 700;
        }
        
        .live-indicator {
            background-color: #00ff00;
            color: #000000;
            padding: 5px 10px;
            border-radius: 15px;
            font-size: 0.8rem;
            font-weight: bold;
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }
    </style>
""", unsafe_allow_html=True)

# Terminal Header
st.markdown('<div class="terminal-header">TF2 MARKET TERMINAL - LIVE CSV DATA FEED</div>', unsafe_allow_html=True)

# Live status indicator
col1, col2, col3 = st.columns([1, 1, 2])
with col1:
    st.markdown('<div class="live-indicator">🔴 LIVE</div>', unsafe_allow_html=True)
with col2:
    st.markdown(f"**LAST UPDATE:** {datetime.now().strftime('%H:%M:%S')}")
with col3:
    if st.button("🔄 REFRESH DATA"):
        st.cache_data.clear()
        st.rerun()

# Load all data
steam_prices_df = get_steam_prices_data()
order_df, listing_df = get_tf2_market_data()
supply_df = get_supply_data()
history_df, alerts_df = get_monitor_data()

# Sidebar - Live Market Overview
st.sidebar.markdown("## 📊 LIVE MARKET STATUS")

# CSV file status indicators
csv_files = [
    ("Steam Prices", "steam_prices.csv", len(steam_prices_df)),
    ("TF2 Orders", "tf2_orders.csv", len(order_df)),
    ("Supply Data", "supply_data.csv", len(supply_df)),
    ("Monitor Data", "monitor_data.csv", len(history_df))
]

for file_name, file_path, record_count in csv_files:
    file_exists = os.path.exists(file_path)
    status_color = "#00ff00" if file_exists and record_count > 0 else "#ff0000"
    file_size = os.path.getsize(file_path) if file_exists else 0
    
    st.sidebar.markdown(f"""
    <div style="background-color: #1a1a1a; padding: 10px; margin: 5px 0; border-left: 4px solid {status_color};">
        <div style="color: {status_color}; font-weight: bold;">{file_name}</div>
        <div style="color: #ffffff;">{record_count:,} records</div>
        <div style="color: #cccccc; font-size: 0.8rem;">{file_size/1024:.1f} KB</div>
    </div>
    """, unsafe_allow_html=True)

# Recent alerts
if not alerts_df.empty:
    st.sidebar.markdown("## 🚨 RECENT ALERTS")
    recent_alerts = alerts_df.head(5)
    for _, alert in recent_alerts.iterrows():
        st.sidebar.markdown(f"""
        <div class="alert-box" style="font-size: 0.8rem; padding: 8px;">
            <strong>{alert['item_name']}</strong><br>
            {alert['message']}<br>
            <small>{alert['created_at'].strftime('%H:%M:%S')}</small>
        </div>
        """, unsafe_allow_html=True)

# Main dashboard tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📈 LIVE PRICES", "📦 SUPPLY TRACKING", "📊 MARKET DEPTH", "🔔 ALERTS", "📋 RAW DATA"])

with tab1:
    st.markdown("## LIVE PRICE FEED")
    
    if not steam_prices_df.empty:
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_items = steam_prices_df['item_name'].nunique()
            st.markdown(f"""
            <div class="metric-container">
                <div class="metric-label">TRACKED ITEMS</div>
                <div class="metric-value neutral">{total_items}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            if 'created_at' in steam_prices_df.columns:
                latest_update = steam_prices_df['created_at'].max()
                minutes_ago = (datetime.now() - latest_update).total_seconds() / 60
            else:
                minutes_ago = 0
            st.markdown(f"""
            <div class="metric-container">
                <div class="metric-label">LAST UPDATE</div>
                <div class="metric-value neutral">{minutes_ago:.0f}m ago</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            total_records = len(steam_prices_df)
            st.markdown(f"""
            <div class="metric-container">
                <div class="metric-label">TOTAL RECORDS</div>
                <div class="metric-value neutral">{total_records:,}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            if 'lowest_price_float' in steam_prices_df.columns:
                avg_price = steam_prices_df['lowest_price_float'].mean()
            else:
                avg_price = 0
            st.markdown(f"""
            <div class="metric-container">
                <div class="metric-label">AVG PRICE</div>
                <div class="metric-value neutral">{avg_price:.0f} ₫</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Item selector
        items = sorted(steam_prices_df['item_name'].unique())
        selected_item = st.selectbox("SELECT ITEM", items)
        
        if selected_item:
            item_data = steam_prices_df[steam_prices_df['item_name'] == selected_item].sort_values('created_at')
            
            if len(item_data) > 1 and 'lowest_price_float' in item_data.columns:
                # Price chart
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=item_data['created_at'],
                    y=item_data['lowest_price_float'],
                    mode='lines+markers',
                    name='Price',
                    line=dict(color='#ff6600', width=3),
                    marker=dict(size=6)
                ))
                
                fig.update_layout(
                    title=f"{selected_item} - LIVE PRICE TRACKING",
                    plot_bgcolor='#000000',
                    paper_bgcolor='#000000',
                    font=dict(color='white', family="JetBrains Mono"),
                    xaxis_title="TIME",
                    yaxis_title="PRICE (₫)",
                    height=500
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Latest price info
                latest = item_data.iloc[-1]
                previous = item_data.iloc[-2] if len(item_data) > 1 else latest
                change = latest['lowest_price_float'] - previous['lowest_price_float']
                change_pct = (change / previous['lowest_price_float'] * 100) if previous['lowest_price_float'] > 0 else 0
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("CURRENT PRICE", f"{latest['lowest_price_float']:.0f} ₫", f"{change:+.0f} ₫")
                with col2:
                    st.metric("CHANGE %", f"{change_pct:+.2f}%")
                with col3:
                    volume_val = latest['volume'] if 'volume' in latest and latest['volume'] else "N/A"
                    st.metric("VOLUME", volume_val)
    else:
        st.info("No steam price data available. Run steam_price.py to collect data.")

with tab2:
    st.markdown("## SUPPLY TRACKING")
    
    if not supply_df.empty:
        # Supply overview
        col1, col2, col3 = st.columns(3)
        
        with col1:
            total_supply_items = supply_df['item_name'].nunique()
            st.markdown(f"""
            <div class="metric-container">
                <div class="metric-label">TRACKED ITEMS</div>
                <div class="metric-value neutral">{total_supply_items}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            if 'created_at' in supply_df.columns:
                latest_supply_update = supply_df['created_at'].max()
                supply_minutes_ago = (datetime.now() - latest_supply_update).total_seconds() / 60
            else:
                supply_minutes_ago = 0
            st.markdown(f"""
            <div class="metric-container">
                <div class="metric-label">LAST UPDATE</div>
                <div class="metric-value neutral">{supply_minutes_ago:.0f}m ago</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            total_supply = supply_df.groupby('item_name')['supply_count'].last().sum()
            st.markdown(f"""
            <div class="metric-container">
                <div class="metric-label">TOTAL SUPPLY</div>
                <div class="metric-value neutral">{total_supply:,}</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Supply chart
        supply_items = sorted(supply_df['item_name'].unique())
        selected_supply_item = st.selectbox("SELECT ITEM FOR SUPPLY TRACKING", supply_items)
        
        if selected_supply_item:
            supply_item_data = supply_df[supply_df['item_name'] == selected_supply_item].sort_values('created_at')
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=supply_item_data['created_at'],
                y=supply_item_data['supply_count'],
                mode='lines+markers',
                name='Supply Count',
                line=dict(color='#00ff00', width=3),
                marker=dict(size=6)
            ))
            
            fig.update_layout(
                title=f"{selected_supply_item} - SUPPLY TRACKING",
                plot_bgcolor='#000000',
                paper_bgcolor='#000000',
                font=dict(color='white', family="JetBrains Mono"),
                xaxis_title="TIME",
                yaxis_title="SUPPLY COUNT",
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No supply data available. Run supply.py to collect data.")

# >>>>>>>>>>>>>>>>>>>> UPDATED TAB3 <<<<<<<<<<<<<<<<<<<<
with tab3:
    st.markdown("## MARKET DEPTH & ORDER BOOK (Per-Item CSVs)")
    import glob
    ignore = set([
        "steam_prices.csv", "tf2_orders.csv", "tf2_listings.csv", "supply_data.csv",
        "monitor_data.csv", "alerts.csv", "supply.csv"
    ])
    possible_csvs = sorted([f for f in glob.glob("*.csv") if f not in ignore])
    orderbook_files = []
    for f in possible_csvs:
        try:
            df_tmp = pd.read_csv(f, nrows=2)
            if set(['side', 'price_vnd', 'quantity']).issubset(df_tmp.columns):
                orderbook_files.append(f)
        except Exception:
            continue
    if not orderbook_files:
        st.info("No per-item order book CSVs found. Please collect data with bids/asks/price/quantity.")
    else:
        item_map = {f: f.replace(".csv", "") for f in orderbook_files}
        selected_file = st.selectbox("Select item", list(item_map.keys()), format_func=lambda x: item_map[x])
        item_name = item_map[selected_file]
        df = pd.read_csv(selected_file)
        # Parse timestamps if present
        if "timestamp" in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
        if "created_at" in df.columns:
            df['created_at'] = pd.to_datetime(df['created_at'])
        snap_col = "timestamp" if "timestamp" in df.columns else "created_at" if "created_at" in df.columns else None
        if snap_col:
            available_snaps = sorted(df[snap_col].unique(), reverse=True)
            selected_snap = st.selectbox("Select snapshot", [str(x) for x in available_snaps])
            snap_df = df[df[snap_col] == pd.to_datetime(selected_snap)]
        else:
            snap_df = df
        bids = snap_df[snap_df['side'] == 'bid'].sort_values("price_vnd", ascending=False)
        asks = snap_df[snap_df['side'] == 'ask'].sort_values("price_vnd", ascending=True)
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### BIDS")
            st.dataframe(bids[["price_vnd", "quantity"]].rename(
                columns={"price_vnd": "Price (₫)", "quantity": "Qty"}).reset_index(drop=True),
                use_container_width=True)
        with col2:
            st.markdown("#### ASKS")
            st.dataframe(asks[["price_vnd", "quantity"]].rename(
                columns={"price_vnd": "Price (₫)", "quantity": "Qty"}).reset_index(drop=True),
                use_container_width=True)
        # Depth chart
        fig = go.Figure()
        if not bids.empty:
            bid_depth = bids.copy()
            bid_depth["cum_qty"] = bid_depth["quantity"].cumsum()
            fig.add_trace(go.Scatter(
                x=bid_depth["price_vnd"], y=bid_depth["cum_qty"],
                mode="lines+markers", name="Bids", line_color="#00ff00", fill='tozeroy'
            ))
        if not asks.empty:
            ask_depth = asks.copy()
            ask_depth["cum_qty"] = ask_depth["quantity"].cumsum()
            fig.add_trace(go.Scatter(
                x=ask_depth["price_vnd"], y=ask_depth["cum_qty"],
                mode="lines+markers", name="Asks", line_color="#ff3300", fill='tozeroy'
            ))
        fig.update_layout(
            title=f"Market Depth for {item_name} at {selected_snap if snap_col else ''}",
            xaxis_title="Price (₫)",
            yaxis_title="Cumulative Quantity",
            plot_bgcolor='#000000',
            paper_bgcolor='#000000',
            font=dict(color='#fff', family="JetBrains Mono"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig, use_container_width=True)
        with st.expander("Download raw snapshot as CSV"):
            st.download_button(
                label="Download CSV",
                data=snap_df.to_csv(index=False),
                file_name=f"{item_name}_orderbook_{str(selected_snap).replace(':','-') if snap_col else 'all'}.csv",
                mime="text/csv"
            )

# >>>>>>>>>>>>>>>>>>>> END TAB3 <<<<<<<<<<<<<<<<<<<<

with tab4:
    st.markdown("## ALERT SYSTEM")
    
    if not alerts_df.empty:
        # Alert statistics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            total_alerts = len(alerts_df)
            st.markdown(f"""
            <div class="metric-container">
                <div class="metric-label">TOTAL ALERTS</div>
                <div class="metric-value warning">{total_alerts}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            recent_alerts = len(alerts_df[alerts_df['created_at'] > datetime.now() - timedelta(hours=24)])
            st.markdown(f"""
            <div class="metric-container">
                <div class="metric-label">24H ALERTS</div>
                <div class="metric-value warning">{recent_alerts}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            alert_types = alerts_df['alert_type'].nunique()
            st.markdown(f"""
            <div class="metric-container">
                <div class="metric-label">ALERT TYPES</div>
                <div class="metric-value neutral">{alert_types}</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Recent alerts table
        st.markdown("### RECENT ALERTS")
        recent_alerts_df = alerts_df.head(20)[['item_name', 'alert_type', 'message', 'created_at']]
        recent_alerts_df.columns = ['ITEM', 'TYPE', 'MESSAGE', 'TIME']
        st.dataframe(recent_alerts_df, use_container_width=True, hide_index=True)
    else:
        st.info("No alerts available. Run monitor.py to start monitoring.")

with tab5:
    st.markdown("## RAW DATA ACCESS")
    
    # Data source selector
    data_source = st.selectbox("SELECT DATA SOURCE", [
        "Steam Prices", "TF2 Market Orders", "TF2 Market Listings", 
        "Supply Data", "Monitor History", "Alerts"
    ])
    
    if data_source == "Steam Prices" and not steam_prices_df.empty:
        st.dataframe(steam_prices_df.head(100), use_container_width=True)
        
    elif data_source == "TF2 Market Orders" and not order_df.empty:
        st.dataframe(order_df.head(100), use_container_width=True)
        
    elif data_source == "TF2 Market Listings" and not listing_df.empty:
        st.dataframe(listing_df.head(100), use_container_width=True)
        
    elif data_source == "Supply Data" and not supply_df.empty:
        st.dataframe(supply_df.head(100), use_container_width=True)
        
    elif data_source == "Monitor History" and not history_df.empty:
        st.dataframe(history_df.head(100), use_container_width=True)
        
    elif data_source == "Alerts" and not alerts_df.empty:
        st.dataframe(alerts_df.head(100), use_container_width=True)
    
    else:
        st.info(f"No data available for {data_source}")

# Auto-refresh functionality
if st.sidebar.checkbox("AUTO REFRESH (30s)"):
    time.sleep(30)
    st.rerun()
