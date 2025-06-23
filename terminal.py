import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt

# Load Data Function
@st.cache_data
def load_data(file_path="tf2_prices.csv"):
    df = pd.read_csv(file_path, header=None, names=["timestamp", "item", "lowest_price", "median_price", "lp_f"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors='coerce')
    df = df.dropna(subset=["lp_f"])
    df["lp_f"] = pd.to_numeric(df["lp_f"], errors='coerce')
    return df

# Set Up the Streamlit App Layout
st.set_page_config(page_title="Steam Market Dashboard", layout="wide")

# Custom Styling for a Drastically Cool, Futuristic Dashboard
st.markdown("""
    <style>
        /* Main Background */
        .main {
            background: linear-gradient(135deg, #2f2f2f, #111);
            color: #e5e5e5;
        }
        
        /* Sidebar */
        .sidebar .sidebar-content {
            background-color: #1d1d1d;
            color: #e5e5e5;
        }
        
        /* Headers */
        h1, h2, h3 {
            color: #00FFAB;
            text-shadow: 3px 3px 12px rgba(0, 255, 171, 0.8);
        }

        /* Button Styling */
        .stButton>button {
            background-color: #00bfae;
            color: #1e1e1e;
            border: none;
            border-radius: 10px;
            padding: 12px 24px;
            font-size: 16px;
            box-shadow: 0px 4px 20px rgba(0, 191, 174, 0.4);
            transition: all 0.3s ease-in-out;
        }

        .stButton>button:hover {
            background-color: #ff4444;
            color: white;
            transform: scale(1.05);
            box-shadow: 0px 6px 25px rgba(255, 68, 68, 0.8);
        }

        /* Graph and Chart */
        .plotly-graph-div {
            border-radius: 15px;
            box-shadow: 0 4px 25px rgba(0, 191, 174, 0.5);
        }

        /* Page Content */
        .block-container {
            padding: 20px;
            font-family: 'Roboto', sans-serif;
        }

        /* Custom Scroll Bar */
        ::-webkit-scrollbar {
            width: 8px;
        }

        ::-webkit-scrollbar-thumb {
            background-color: #00bfae;
            border-radius: 10px;
        }

        ::-webkit-scrollbar-track {
            background-color: #111;
        }
    </style>
""", unsafe_allow_html=True)

# Title and Data Loading
st.title("Steam Market Price Analysis Dashboard")
df = load_data()

# Sidebar Filters and Options
st.sidebar.title("Filters")
item_filter = st.sidebar.selectbox("Select Item to View", options=df['item'].unique())
view_trends = st.sidebar.checkbox("Show Trends")
view_volatility = st.sidebar.checkbox("Show Volatility")
threshold = st.sidebar.slider("Minimum Items per Bin", 1, 10, 2)

# Tabs for Organized View
tab1, tab2, tab3, tab4 = st.tabs(["Overview", "Price History", "Item Stats", "Market Insights"])

# Overview Tab
with tab1:
    st.header(f"Steam Market Overview for {item_filter}")
    
    # Filter Data for the Selected Item
    item_data = df[df['item'] == item_filter]
    latest_price = item_data['lp_f'].iloc[-1]
    avg_price = item_data['lp_f'].mean()
    highest_price = item_data['lp_f'].max()
    lowest_price = item_data['lp_f'].min()
    
    # Display Metrics
    st.metric(label="Latest Price", value=f"{latest_price} ₫", delta=latest_price - avg_price)
    st.metric(label="Highest Price", value=f"{highest_price} ₫")
    st.metric(label="Lowest Price", value=f"{lowest_price} ₫")
    
    # Price History Chart (Interactive)
    fig = px.line(item_data, x='timestamp', y='lp_f', title="Price History", line_shape='spline', markers=True)
    fig.update_traces(line=dict(width=4, color='#00FFAB'), marker=dict(size=10, color='#ff4444', symbol='circle', opacity=0.7))
    fig.update_layout(
        title="Price History (Interactive)",
        title_x=0.5,
        xaxis_title='Timestamp',
        yaxis_title='Price (₫)',
        plot_bgcolor='#121212',
        paper_bgcolor='#121212',
        font=dict(color='white'),
        hovermode='x unified'
    )
    st.plotly_chart(fig)

# Price History Tab
with tab2:
    st.header(f"Price History for {item_filter}")
    
    # Plotting the Price History with Plotly Graph Objects
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=item_data['timestamp'], y=item_data['lp_f'], mode='lines+markers', name=item_filter, line=dict(color='#00bfae', width=4), marker=dict(size=10, color='#ff4444', opacity=0.7)))
    
    # Layout Configuration for Consistency
    fig.update_layout(
        title=f"Price History for {item_filter}",
        xaxis_title='Date',
        yaxis_title='Price (₫)',
        plot_bgcolor='#121212',
        paper_bgcolor='#121212',
        font=dict(color='white'),
        uirevision='price_history',
        hovermode='closest'
    )
    
    st.plotly_chart(fig, use_container_width=True)

# Item Stats Tab
with tab3:
    st.subheader("Item Stats")
    
    # Displaying Item Statistics
    st.write(f"**Latest Price**: {latest_price}")
    st.write(f"**Average Price**: {avg_price:.2f}")
    st.write(f"**Highest Price**: {highest_price}")
    st.write(f"**Lowest Price**: {lowest_price}")
    
    # Price Distribution (Binned)
    price_bins = pd.cut(item_data['lp_f'], bins=10)
    price_dist = price_bins.value_counts().sort_index()

    # Filter price distribution by threshold
    filtered_price_dist = price_dist[price_dist >= threshold]

    # Manually convert Interval to String for Plotly
    price_dist_labels = [f'{interval.left:.2f}-{interval.right:.2f}' for interval in filtered_price_dist.index]

    # Pie Chart for Price Distribution
    fig = px.pie(values=filtered_price_dist.values, names=price_dist_labels, title="Price Distribution", color=filtered_price_dist.index, color_discrete_sequence=px.colors.sequential.Plasma)
    fig.update_traces(textinfo="percent+label", hoverinfo="label+percent", pull=[0.1]*len(filtered_price_dist))
    st.plotly_chart(fig)
    
    # Price Distribution Histogram
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.hist(item_data['lp_f'], bins=30, color='#00bfae', edgecolor='black')
    ax.set_title("Price Distribution Histogram", fontsize=20, color='white', fontweight='bold')
    ax.set_xlabel('Price (₫)', fontsize=16, color='white')
    ax.set_ylabel('Frequency', fontsize=16, color='white')
    ax.grid(True, linestyle='--', alpha=0.5)
    st.pyplot(fig)
    
    # Box Plot for Price Distribution
    fig = px.box(item_data, y='lp_f', title="Price Distribution Box Plot", color_discrete_sequence=["#ff4444"])
    fig.update_traces(marker=dict(size=12))
    st.plotly_chart(fig)

# Market Insights Tab (Trends & Volatility)
with tab4:
    if view_trends:
        # Price Trend Analysis
        item_data['price_change'] = item_data['lp_f'].pct_change() * 100
        st.subheader("Price Trends")
        st.line_chart(item_data['price_change'])
    
    if view_volatility:
        # Volatility Analysis
        item_data['daily_returns'] = item_data['lp_f'].pct_change()
        volatility = item_data['daily_returns'].std()
        st.subheader("Price Volatility")
        st.write(f"Volatility: {volatility * 100:.2f}%")

# Price Alert Button in Sidebar
st.sidebar.subheader("Set Price Alerts")
alert_threshold = st.sidebar.number_input("Set Price Alert Threshold", min_value=0, value=50)
if latest_price > alert_threshold:
    if st.sidebar.button("Set Alert"):
        st.sidebar.success(f"Alert: {item_filter} price exceeds {alert_threshold}₫!")
