"""
PACT-OS
Main Entry Point
"""

from exchange.tabdeal_client import TabdealClient


def banner():
    print("=" * 60)
    print("           PACT-OS v0.1")
    print(" Personal AI Crypto Trading Assistant")
    print("=" * 60)


def main():
    banner()

    client = TabdealClient()

    print("\nAPI Ping")
    print("----------------------------")
    print(client.ping())

    print("\nServer Time")
    print("----------------------------")
    print(client.server_time())

    print("\nExchange")
    print("----------------------------")
    print("Markets :", len(client.symbols()))

    btc = client.find_symbol("BTCIRT")

    print("\nBTCIRT")
    print("----------------------------")
    print("Status :", btc["status"])
    print("Base   :", btc["baseAsset"])
    print("Quote  :", btc["quoteAsset"])

    trade = client.trades("BTCIRT", 1)[0]

    print("\nLast Trade")
    print("----------------------------")
    print(f"Price      : {trade.price:,.0f}")
    print(f"Quantity   : {trade.quantity}")
    print(f"Timestamp  : {trade.timestamp}")

    book = client.depth("BTCIRT", 5)

    print("\nOrder Book")
    print("----------------------------")
    print(f"Best Bid   : {book.best_bid:,.0f}")
    print(f"Best Ask   : {book.best_ask:,.0f}")
    print(f"Spread     : {book.spread:,.0f}")
    print(f"Spread %   : {book.spread_percent:.4f}")

    print("\n==============================")
    print("PACT-OS READY")
    print("==============================")


if __name__ == "__main__":
    main()