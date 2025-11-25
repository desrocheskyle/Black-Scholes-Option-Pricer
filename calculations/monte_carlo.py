import numpy as np

def monte_carlo_option_price(S, K, T, r, sigma, option_type='call', iterations=10000):
    np.random.seed(0)  # For reproducibility
    end_prices = S * np.exp((r - 0.5 * sigma ** 2) * T + sigma * np.sqrt(T) * np.random.randn(iterations))
    
    if option_type == 'call':
        payoffs = np.maximum(end_prices - K, 0)
    elif option_type == 'put':
        payoffs = np.maximum(K - end_prices, 0)
    else:
        raise ValueError("Option type must be 'call' or 'put'")
    
    option_price = np.exp(-r * T) * np.mean(payoffs)
    return option_price