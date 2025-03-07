# Real-time Stock Trading Engine

A high-performance, lock-free trading engine for matching stock buy and sell orders.

## Features

- O(n) time complexity for order matching
- Support for 1,024 different stock tickers
- Price-time priority order matching
- Thread-safe order book operations
- No dictionaries, maps or equivalent data structures
- Zero external dependencies
- Simulated concurrent execution

## Core Components

### 1. Main Trading Engine (`stock-trading-engine.py`)

The main implementation includes:

- `add_order`: Adds buy/sell orders to the order book
- `match_orders`: Matches compatible buy and sell orders
- `simulate_trading`: Simulates random order generation and matching

### 2. CLI Testing Tool (`trading_cli.py`)

While not required by the assessment, I created a simple CLI tool to make testing easier:

- Limited set of pre-defined tickers with market prices
- Interactive commands for adding orders and viewing the order book
- Visual feedback on order prices relative to market prices
- Easy-to-use interface for manual testing

## Usage

### Running the Simulation

```bash
python stock-trading-engine.py
```

This will run a simulation with 1,000 random orders.

### Using the CLI Tool

```bash
python trading_cli.py
```

Available commands:
- `buy TICKER QUANTITY PRICE` - Add a buy order
- `sell TICKER QUANTITY PRICE` - Add a sell order
- `show` - Display the current order book
- `prices` - Show current market prices
- `match` - Match orders
- `help` - Show help message
- `exit` - Exit the program

## Implementation Details

- The order book is implemented as an array-based structure to avoid using dictionaries
- Orders are matched based on price-time priority
- Buy orders with the highest price get matched first
- Sell orders with the lowest price get matched first
- When prices are equal, earlier orders get priority
- The execution price is the sell price

## Design Decisions

- **Array-based Implementation**: Used arrays instead of dictionaries to meet the requirements
- **O(n) Matching Algorithm**: Linear scan to find best orders instead of sorting
- **CLI Tool**: Added a simple CLI for easier testing, though not required by the assessment
- **Market Prices**: Added reference market prices in the CLI to make testing more intuitive

## Performance Considerations

- The matching algorithm is O(n) where n is the number of orders
- Lock-free design allows for concurrent modifications
- Pre-allocation of arrays for tickers minimizes memory reallocation
