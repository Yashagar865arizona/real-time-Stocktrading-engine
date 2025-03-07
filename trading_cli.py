"""
Improved Stock Trading CLI

A user-friendly command-line interface for testing the stock trading engine
with a small set of pre-defined tickers and current market prices.
"""

# Constants
BUY = 1
SELL = 2

# Pre-defined tickers with current market prices
AVAILABLE_TICKERS = {
    "AAPL": 175.50,  # Apple
    "MSFT": 330.75,  # Microsoft
    "GOOGL": 140.25, # Google
    "AMZN": 145.80,  # Amazon
    "TSLA": 250.20   # Tesla
}

def create_order_book():
    """Create a simplified order book with just the pre-defined tickers."""
    ticker_symbols = list(AVAILABLE_TICKERS.keys()) + [None] * (1024 - len(AVAILABLE_TICKERS))
    buy_orders = [[] for _ in range(1024)]
    sell_orders = [[] for _ in range(1024)]
    return [ticker_symbols, buy_orders, sell_orders, len(AVAILABLE_TICKERS), 1]

def add_order(order_book, order_type, ticker, quantity, price):
    """Add a new order to the order book."""
    # Get next order ID
    order_id = order_book[4]
    order_book[4] += 1
    
    # Create order
    order = [order_type, ticker, quantity, price, order_id, order_id]  # Using order_id as sequence
    
    # Find ticker index
    ticker_idx = -1
    for i, t in enumerate(AVAILABLE_TICKERS.keys()):
        if t == ticker:
            ticker_idx = i
            break
    
    if ticker_idx == -1:
        print(f"Error: Ticker {ticker} not in available tickers: {', '.join(AVAILABLE_TICKERS.keys())}")
        return -1
    
    # Add to appropriate order list
    if order_type == BUY:
        order_book[1][ticker_idx].append(order)
    else:
        order_book[2][ticker_idx].append(order)
    
    return order_id

def match_orders(order_book):
    """Match buy and sell orders."""
    matches = []
    
    # Only process our pre-defined tickers
    for ticker_idx in range(len(AVAILABLE_TICKERS)):
        buy_orders = order_book[1][ticker_idx]
        sell_orders = order_book[2][ticker_idx]
        
        if not buy_orders or not sell_orders:
            continue
        
        # Track completed orders
        completed_buys = []
        completed_sells = []
        
        # Simple matching algorithm
        for buy_idx, buy in enumerate(buy_orders):
            if buy_idx in completed_buys:
                continue
                
            for sell_idx, sell in enumerate(sell_orders):
                if sell_idx in completed_sells:
                    continue
                
                # Match if buy price >= sell price
                if buy[3] >= sell[3]:
                    match_quantity = min(buy[2], sell[2])
                    
                    # Record match
                    matches.append([buy[4], sell[4], buy[1], match_quantity, sell[3]])
                    
                    # Update quantities
                    buy[2] -= match_quantity
                    sell[2] -= match_quantity
                    
                    # Mark completed orders
                    if buy[2] == 0:
                        completed_buys.append(buy_idx)
                    if sell[2] == 0:
                        completed_sells.append(sell_idx)
        
        # Remove completed orders
        if completed_buys:
            order_book[1][ticker_idx] = [buy for i, buy in enumerate(buy_orders) if i not in completed_buys]
        if completed_sells:
            order_book[2][ticker_idx] = [sell for i, sell in enumerate(sell_orders) if i not in completed_sells]
    
    return matches

def display_order_book(order_book):
    """Display the current state of the order book in a user-friendly format."""
    print("\n===== CURRENT ORDER BOOK =====")
    
    for ticker_idx, ticker in enumerate(list(AVAILABLE_TICKERS.keys())):
        market_price = AVAILABLE_TICKERS[ticker]
        buy_orders = order_book[1][ticker_idx]
        sell_orders = order_book[2][ticker_idx]
        
        print(f"\n{ticker} (Current Market Price: ${market_price:.2f}):")
        
        if not buy_orders and not sell_orders:
            print("  No orders")
            continue
            
        print("  BUY ORDERS:")
        if not buy_orders:
            print("    None")
        else:
            # Sort by price (highest first)
            for order in sorted(buy_orders, key=lambda x: (-x[3], x[5])):
                price_diff = ((order[3] - market_price) / market_price) * 100
                print(f"    ID: {order[4]}, {order[2]} shares @ ${order[3]:.2f} ({price_diff:.2f}% from market)")
        
        print("  SELL ORDERS:")
        if not sell_orders:
            print("    None")
        else:
            # Sort by price (lowest first)
            for order in sorted(sell_orders, key=lambda x: (x[3], x[5])):
                price_diff = ((order[3] - market_price) / market_price) * 100
                print(f"    ID: {order[4]}, {order[2]} shares @ ${order[3]:.2f} ({price_diff:.2f}% from market)")

def display_market_prices():
    """Display current market prices for all available tickers."""
    print("\n===== CURRENT MARKET PRICES =====")
    for ticker, price in AVAILABLE_TICKERS.items():
        print(f"{ticker}: ${price:.2f}")

def display_help():
    """Display available commands."""
    print("\nAvailable Commands:")
    print("  buy TICKER QUANTITY PRICE - Add a buy order")
    print("  sell TICKER QUANTITY PRICE - Add a sell order")
    print("  show - Display the current order book")
    print("  prices - Show current market prices")
    print("  match - Match orders")
    print("  help - Show this help message")
    print("  exit - Exit the program")
    print(f"\nAvailable Tickers: {', '.join(AVAILABLE_TICKERS.keys())}")

def main():
    """Main CLI loop."""
    order_book = create_order_book()
    
    print("Welcome to the Stock Trading CLI!")
    display_market_prices()
    display_help()
    
    while True:
        try:
            command = input("\nEnter command: ").strip().lower()
            
            if command in ["exit", "quit"]:
                break
                
            elif command == "show":
                display_order_book(order_book)
                
            elif command == "prices":
                display_market_prices()
                
            elif command == "match":
                matches = match_orders(order_book)
                if matches:
                    print("\n===== MATCHED ORDERS =====")
                    for match in matches:
                        ticker = match[2]
                        market_price = AVAILABLE_TICKERS[ticker]
                        price_diff = ((match[4] - market_price) / market_price) * 100
                        print(f"Match: {match[3]} {ticker} @ ${match[4]:.2f} ({price_diff:.2f}% from market)")
                        print(f"  Buy ID: {match[0]}, Sell ID: {match[1]}")
                else:
                    print("No matches found")
                
            elif command == "help":
                display_help()
                
            elif command.startswith(("buy", "sell")):
                parts = command.split()
                if len(parts) != 4:
                    print("Error: Invalid format. Use: buy/sell TICKER QUANTITY PRICE")
                    continue
                
                order_type = BUY if parts[0] == "buy" else SELL
                ticker = parts[1].upper()
                
                if ticker not in AVAILABLE_TICKERS:
                    print(f"Error: Unknown ticker. Available tickers: {', '.join(AVAILABLE_TICKERS.keys())}")
                    continue
                
                try:
                    quantity = int(parts[2])
                    price = float(parts[3])
                except ValueError:
                    print("Error: Quantity must be an integer and price must be a number")
                    continue
                
                if quantity <= 0 or price <= 0:
                    print("Error: Quantity and price must be positive")
                    continue
                
                # Show market price comparison
                market_price = AVAILABLE_TICKERS[ticker]
                price_diff = ((price - market_price) / market_price) * 100
                diff_str = "above" if price > market_price else "below"
                
                print(f"Market price for {ticker} is ${market_price:.2f}")
                print(f"Your order price (${price:.2f}) is {abs(price_diff):.2f}% {diff_str} market price")
                
                confirm = input(f"Confirm {parts[0].upper()} order? (y/n): ").strip().lower()
                if confirm != 'y':
                    print("Order cancelled")
                    continue
                
                order_id = add_order(order_book, order_type, ticker, quantity, price)
                if order_id != -1:
                    print(f"Order added successfully. Order ID: {order_id}")
            
            else:
                print(f"Unknown command: {command}")
                print("Type 'help' to see available commands")
                
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"Error: {str(e)}")

if __name__ == "__main__":
    main() 