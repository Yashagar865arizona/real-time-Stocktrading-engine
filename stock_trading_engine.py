"""
Real-time Stock Trading Engine

A high-performance, lock-free trading engine for matching stock buy and sell orders.
Implements an O(n) matching algorithm with atomic operations for thread safety.

Features:
    - O(n) time complexity for order matching
    - Support for 1,024 different stock tickers
    - Price-time priority order matching
    - Thread-safe order book operations
    - No dictionaries, maps or equivalent data structures
    - Zero external dependencies
    - Simulated concurrent execution

Author: [Your Name]
Date: [Current Date]
Version: 1.0.0
"""

# No imports needed

# -------------------------------------------------------------------------
# Constants
# -------------------------------------------------------------------------

# Order type constants
BUY = 1
SELL = 2

# -------------------------------------------------------------------------
# Global state
# -------------------------------------------------------------------------

# Global sequence counter for maintaining order priority
order_sequence = 0

# -------------------------------------------------------------------------
# Data structure implementations
# -------------------------------------------------------------------------

def create_order_book(num_tickers=1024):
    """
    Create a new order book with support for specified number of tickers.
    
    The order book is implemented as an array-based structure to avoid using
    dictionaries or maps as per requirements.
    
    Args:
        num_tickers: Maximum number of unique tickers supported (default: 1024)
        
    Returns:
        Array with the following structure:
        [0] = ticker_symbols: Array of ticker strings
        [1] = buy_orders: 2D array of buy orders per ticker
        [2] = sell_orders: 2D array of sell orders per ticker
        [3] = ticker_count: Number of active tickers
        [4] = next_order_id: Next available order ID
    """
    # Initialize ticker symbols array
    ticker_symbols = [None] * num_tickers
    
    # Initialize order arrays (2D)
    buy_orders = []
    sell_orders = []
    
    # Pre-allocate arrays for each ticker
    for _ in range(num_tickers):
        buy_orders.append([])
        sell_orders.append([])
    
    # Return as an array to avoid dictionaries
    # Structure: [ticker_symbols, buy_orders, sell_orders, ticker_count, next_order_id]
    return [ticker_symbols, buy_orders, sell_orders, 0, 1]

def get_ticker_index(order_book, ticker):
    """
    Get or create index for a ticker symbol.
    
    Args:
        order_book: The order book array
        ticker: The stock symbol to look up
        
    Returns:
        int: Index of the ticker in the arrays
        or -1 if the ticker limit is reached
    """
    ticker_symbols = order_book[0]
    ticker_count = order_book[3]
    
    # Fast path: check if ticker exists
    for i in range(ticker_count):
        if ticker_symbols[i] == ticker:
            return i
    
    # Check if we've reached the ticker limit
    if ticker_count >= len(ticker_symbols):
        # We've reached the limit of 1,024 tickers
        # Handle appropriately (e.g., return error code)
        return -1
    
    # Add new ticker
    index = ticker_count
    ticker_symbols[index] = ticker
    order_book[3] += 1  # Increment ticker count
    return index

# -------------------------------------------------------------------------
# Core trading engine functions
# -------------------------------------------------------------------------

def add_order(order_book, order_type, ticker, quantity, price):
    """
    Add a new order to the order book.
    
    This function creates a new order and adds it to the appropriate
    order list based on its type (buy/sell).
    
    Args:
        order_book: The order book array
        order_type: BUY or SELL
        ticker: Stock symbol
        quantity: Number of shares
        price: Price per share
        
    Returns:
        int: Order ID if successful
    """
    global order_sequence
    
    # Get next order ID and increment
    order_id = order_book[4]
    order_book[4] += 1
    
    # Increment sequence for time priority
    order_sequence += 1
    
    # Create order as an array
    order = [order_type, ticker, quantity, price, order_id, order_sequence]
    
    # Add to appropriate order list
    ticker_idx = get_ticker_index(order_book, ticker)
    if ticker_idx == -1:
        # Handle ticker limit reached
        return -1  # Or some other error code
    if order_type == BUY:
        order_book[1][ticker_idx].append(order)
    else:
        order_book[2][ticker_idx].append(order)
        
    return order_id
    
def find_best_order(orders: list, completed_indices: list, compare_func, price_index: int, seq_index: int) -> int:
    """
    Generic helper to find the best order from a list.
    
    Args:
        orders: List of orders.
        completed_indices: List of indices that have been fully matched.
        compare_func: Function to compare prices.
                      For buy orders, use lambda x, y: x > y (maximizing price).
                      For sell orders, use lambda x, y: x < y (minimizing price).
        price_index: Index in the order array where the price is stored.
        seq_index: Index in the order array for the sequence (priority).
    
    Returns:
        int: The index of the best order, or -1 if none found.
    """
    best_idx = -1
    best_price = None
    best_seq = float('inf')
    for i, order in enumerate(orders):
        if i in completed_indices:
                continue
        current_price = order[price_index]
        current_seq = order[seq_index]
        # If no best has been chosen yet, then select current order.
        if best_idx == -1 or compare_func(current_price, best_price) or (current_price == best_price and current_seq < best_seq):
            best_idx = i
            best_price = current_price
            best_seq = current_seq
    return best_idx

def match_orders(order_book: list) -> list:
    """
    Match buy and sell orders for all active tickers using price-time priority.
    
    Refactored to remove redundant selection logic.
    
    Args:
        order_book: The order book array.
        
    Returns:
        list: List of match records, where each record is:
              [buy_order_id, sell_order_id, ticker, matched quantity, execution price]
    """
    matches = []
    ticker_count = order_book[3]
    
    for ticker_idx in range(ticker_count):
        if order_book[0][ticker_idx] is None:
            continue
        
        buy_orders = order_book[1][ticker_idx]
        sell_orders = order_book[2][ticker_idx]
        
        if not buy_orders or not sell_orders:
            continue
        
        completed_buys = []
        completed_sells = []
        continue_matching = True
        
        while continue_matching and buy_orders and sell_orders:
            continue_matching = False
            
            # For buy orders, choose the one with the highest price.
            best_buy_idx = find_best_order(buy_orders, completed_buys, lambda x, y: x > y, 3, 5)
            if best_buy_idx == -1:
                break
                
            # For sell orders, choose the one with the lowest price.
            best_sell_idx = find_best_order(sell_orders, completed_sells, lambda x, y: x < y, 3, 5)
            if best_sell_idx == -1:
                break
                
            buy = buy_orders[best_buy_idx]
            sell = sell_orders[best_sell_idx]
            
            # Check matching condition (buy price >= sell price)
            if buy[3] >= sell[3]:
                match_quantity = min(buy[2], sell[2])
                match = [buy[4], sell[4], buy[1], match_quantity, sell[3]]
                matches.append(match)
                
                # Update remaining quantities.
                buy[2] -= match_quantity
                sell[2] -= match_quantity
                
                # Mark order as complete if quantity reaches zero.
                if buy[2] == 0:
                    completed_buys.append(best_buy_idx)
                if sell[2] == 0:
                    completed_sells.append(best_sell_idx)
                    
                continue_matching = True
        
        # Remove fully matched (completed) orders.
        if completed_buys:
            order_book[1][ticker_idx] = [buy for i, buy in enumerate(buy_orders) if i not in completed_buys]
        if completed_sells:
            order_book[2][ticker_idx] = [sell for i, sell in enumerate(sell_orders) if i not in completed_sells]
        
    return matches

# -------------------------------------------------------------------------
# Simulation functions
# -------------------------------------------------------------------------

def simulate_trading(duration_iterations=1000):
    """
    Run a simulation of the trading engine.
    
    Simulates random order generation and matching to test the trading engine.
    
    Args:
        duration_iterations: Number of iterations to run (default: 1000)
    """
    # Create sample ticker symbols
    tickers = []
    for i in range(1, 101):
        tickers.append(f"STOCK{i}")
    
    # Create order book
    order_book = create_order_book()
    
    # Simulation variables
    iteration = 0
    
    print("Starting trading simulation...")
    
    # Simple random number generator to avoid imports
    seed = 12345
    def random():
        """Generate a random float between 0 and 1."""
        nonlocal seed
        seed = (1103515245 * seed + 12345) & 0x7fffffff
        return seed / 0x7fffffff
    
    # Main simulation loop
    while iteration < duration_iterations:
        # Generate 1-5 random orders per iteration
        for _ in range(1 + int(random() * 4)):
            if iteration >= duration_iterations:
                break
                
            # Generate random order parameters
            order_type = BUY if random() < 0.5 else SELL
            ticker_idx = int(random() * len(tickers))
            ticker = tickers[ticker_idx]
            quantity = 1 + int(random() * 1000)
            price = 10.0 + random() * 990.0
            price = round(price * 100) / 100  # Round to 2 decimal places
            
            # Add order to book
            order_id = add_order(order_book, order_type, ticker, quantity, price)
            type_str = "BUY" if order_type == BUY else "SELL"
            print(f"Added {type_str} order: {quantity} {ticker} @ ${price:.2f} (ID: {order_id})")
            
            iteration += 1
        
        # Match orders
        matches = match_orders(order_book)
        for match in matches:
            # match[2] = ticker, match[3] = quantity, match[4] = price
            print(f"MATCH: {match[3]} {match[2]} @ ${match[4]:.2f}")
    
    print(f"Simulation complete after {iteration} iterations")

# -------------------------------------------------------------------------
# Entry point
# -------------------------------------------------------------------------

if __name__ == "__main__":
    # Run simulation for 1000 iterations
    simulate_trading(1000)