# StonksBot
Telegram Bot for Stocks
This bot is running as a service in a raspberry pi, it may die at any moment

Tickername = name of the stocks ticker (e.g. AAPL for Apple Inc. NASDAQ: AAPL)

List of commands
watch  - /watch Tickername PriceofStock | If no price is written , the command will fail | if no ticker is written, the bot will send you a list of your current watchlist
unwatch - /unwatch Tickername | Removes stock from watchlist
price - /price Tickername | Get price for current stock 
dividend - /dividend Tickername | /dividend CheckAllYourStockDividends(beta)
holding - /holding Tickername | Get holdings for an etf 
gainers - /gainers | Top 10 Stock Gainers
losers - /losers | Top 10 Stock Losers
