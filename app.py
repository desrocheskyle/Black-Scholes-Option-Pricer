import streamlit as st
import numpy as np
import pandas as pd
import seaborn as sns
from scipy.stats import norm
import plotly.graph_objects as go
import plotly.express as px

# Import calculation functions from the correct directory structure
from calculations.black_scholes import black_scholes, calculate_greeks
from calculations.monte_carlo import monte_carlo_option_price


# --- UI Configuration and Setup ---
st.set_page_config(
    page_title="Black-Scholes Option Pricer",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
        .stApp {
            background-color: #262730; /* Dark gray background */
            color: #FAFAFA;
        }
        .stButton>button {
            background-color: #4CAF50; /* Green button */
            color: white;
            border-radius: 8px;
        }
        .css-1d391kg { padding-top: 30px; } /* Adjust main content padding */
        
        /* Metric cards styling */
        [data-testid="stMetric"] {
            background-color: #333333;
            border: 1px solid #4F4F4F;
            padding: 15px;
            border-radius: 10px;
            color: #FAFAFA;
        }
    </style>
""", unsafe_allow_html=True)


st.title("💰 Black-Scholes & Monte Carlo Option Pricer")
st.markdown("##### An interactive tool for calculating and visualizing option prices and their sensitivities (Greeks).")


# --- Sidebar for Inputs ---
st.sidebar.header("Option Parameters")

option_type = st.sidebar.radio("Option Type", ["call", "put"], horizontal=True)

S = st.sidebar.slider("Stock Price (S)", 10.0, 300.0, 100.0)
K = st.sidebar.slider("Strike Price (K)", 10.0, 300.0, 100.0)
T = st.sidebar.slider("Time to Expiration (T, years)", 0.05, 5.0, 1.0)
r = st.sidebar.slider("Risk-Free Rate (r)", 0.01, 0.20, 0.05)
sigma = st.sidebar.slider("Volatility (σ)", 0.01, 1.0, 0.20)

# --- Tabbed Layout for Results ---
tab1, tab2, tab3 = st.tabs(["Black-Scholes Price & Greeks", "Monte Carlo Simulation", "Visualization Sandbox"])

with tab1:
    st.header("Black-Scholes Model Results")
    
    # Calculate Results
    bs_price = black_scholes(S, K, T, r, sigma, option_type)
    greeks = calculate_greeks(S, K, T, r, sigma, option_type)

    # Display Price and Greeks using Metric Cards in columns
    col1, col2, col3, col4, col5 = st.columns(5)
    
    col1.metric("Option Price (BS)", f"${bs_price:.4f}")
    col2.metric("Delta", f"{greeks['delta']:.4f}")
    col3.metric("Gamma", f"{greeks['gamma']:.4f}")
    col4.metric("Theta", f"{greeks['theta']:.4f}")
    col5.metric("Vega", f"{greeks['vega']:.4f}")
    
    st.markdown("---")
    st.subheader("Black-Scholes Assumptions")
    st.info("The BS model assumes European options, constant volatility, constant risk-free rate, and log-normal asset returns.")


with tab2:
    st.header("Monte Carlo Simulation")
    
    mc_iterations = st.slider("Monte Carlo Iterations", 1000, 100000, 50000, 1000)
    
    if st.button("Run Monte Carlo Simulation", key="mc_run"):
        mc_price = monte_carlo_option_price(S, K, T, r, sigma, option_type, mc_iterations)
        
        st.metric("Monte Carlo Price", f"${mc_price:.4f}")
        st.markdown(f"**Iterations:** {mc_iterations:,}")
        st.success(f"Simulation completed. Price calculated using {mc_iterations:,} paths.")

        
with tab3:
    st.header("Interactive Option Price Visualization")
    
    # --- 1. Plotly 3D Surface Plot (Interactive & Impressive) ---
    st.subheader("3D Option Price Surface Plot (S vs. Volatility)")
    
    # Define plot parameters (Using 30 points for faster calculation, can be increased)
    sigma_values = np.linspace(0.1, 1.0, 30)
    S_values = np.linspace(50, 150, 30)
    sigma_grid, S_grid = np.meshgrid(sigma_values, S_values)
    
    # Calculate price grid using the fixed Black-Scholes function
    price_grid = np.vectorize(lambda S_val, sig: black_scholes(S_val, K, T, r, sig, option_type))(S_grid, sigma_grid)

    # Create Plotly 3D Surface
    fig = go.Figure(data=[go.Surface(z=price_grid, x=S_grid, y=sigma_grid, 
                                     colorscale='Viridis', 
                                     colorbar=dict(title='Option Price'))])
    
    # Configure Layout for Dark Theme and Interactivity
    fig.update_layout(
        scene=dict(
            xaxis_title='Stock Price (S)',
            yaxis_title='Volatility (σ)',
            zaxis_title='Option Price',
            bgcolor="#333333", # Dark background for the 3D box
            zaxis=dict(showbackground=False) 
        ),
        title=f"{option_type.capitalize()} Option Price Sensitivity",
        height=600,
        margin=dict(l=0, r=0, t=50, b=0),
        plot_bgcolor="#262730",
        paper_bgcolor="#262730",
        font=dict(color="#FAFAFA")
    )
    
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # --- 2. Delta/Gamma Sensitivity Line Plot (High Analytical Value) ---
    st.subheader("Delta & Gamma Sensitivity vs. Stock Price")
    
    # Calculate Sensitivity data across a range of stock prices
    S_range_for_line = np.linspace(50, 150, 100)
    sensitivity_data = []
    
    for S_val in S_range_for_line:
        # We assume calculate_greeks is fixed and working
        greeks_val = calculate_greeks(S_val, K, T, r, sigma, option_type)
        sensitivity_data.append({
            'Stock Price': S_val,
            'Delta': greeks_val['delta'],
            'Gamma': greeks_val['gamma']
        })
        
    df_sens = pd.DataFrame(sensitivity_data)
    
    # Reshape data for Plotly Express (plotting multiple series)
    df_melt = df_sens.melt(id_vars=['Stock Price'], 
                           value_vars=['Delta', 'Gamma'],
                           var_name='Greek', 
                           value_name='Value')

    # Create Line Plot using Plotly Express
    fig_line = px.line(df_melt, x='Stock Price', y='Value', color='Greek',
                       title=f"{option_type.capitalize()} Delta and Gamma vs. Stock Price",
                       color_discrete_map={'Delta': 'yellow', 'Gamma': 'red'})

    # Configure Layout for Dark Theme
    fig_line.update_layout(
        plot_bgcolor="#333333",
        paper_bgcolor="#262730",
        font=dict(color="#FAFAFA"),
        xaxis_title="Stock Price (S)",
        yaxis_title="Value"
    )

    st.plotly_chart(fig_line, use_container_width=True)