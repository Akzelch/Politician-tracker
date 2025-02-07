from Scraper import Scrape
politicians = Scrape(["Michael Guest", "Rick Scott", "Suzan DelBene"])

for politician_name in politicians:
    if politician_name in politicians:
        print(f"Trades for {politician_name}:")
        for trade in politicians[politician_name].getTrades():
            print(trade)
    else:
        print(f"No trades found for {politician_name}")