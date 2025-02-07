from bs4 import BeautifulSoup
import requests
import time
from datetime import date

# Making a GET request
r = requests.get('https://www.capitoltrades.com/trades')

# check status code for response received
# success code - 200
print(r)

# Parsing the HTML
soup = BeautifulSoup(r.content, 'html.parser')
politicians = {}

class Politician:
    def __init__(self, name):
        self.name = name
        self.trades = []

    def __str__(self):
        return self.name

    def addTrade(self,name, abbr, publish_date, date, owner, type, amount):
        trade = Trade(name, abbr, publish_date, date, owner, type, amount)

        self.trades.append(trade)

    def removeTrade(self, trade_name):
        self.trades.remove(trade_name)

    def getTrades(self):
        return self.trades
    
    def getName(self):
        return self.name

class Trade:
    def __init__(self, name, abbr, publish_date, date, owner, type, amount):
        self.name = name
        self.abbr = abbr
        self.publish_date = publish_date
        self.date = date
        self.type = type
        self.amount = amount
        self.owner = owner

    def __str__(self):
        return f"{self.name} ({self.abbr}) {self.date}, {self.owner}, {self.type}, {self.amount} "
    
    def getName(self):
        return self.name
    
    def getAbbr(self):
        return self.abbr
    
    def getPublishDate(self):
        return self.publish_date
    
    def getDate(self):
        return self.date
    
    def getOwner(self):
        return self.owner

    def getType(self):
        return self.type

    def getAmount(self):
        return self.amount
    

def createPolitician(politician_name):
    already_added = False
    for politician in politicians:
        if politician == politician_name:
            already_added = True
    
    if already_added:
        pass
    
    else:
        politicians[politician_name] = Politician(politician_name)


def scrapePolitician(trade):
    politician_name_tag = trade.find("h2", class_="politician-name")
    if politician_name_tag:
        try:
            politician_name = politician_name_tag.find('a').text
            createPolitician(politician_name)
            #print(f"Politician Name: {politician_name}")
        except AttributeError:
            print("Error: 'a' tag not found within 'h2' tag")
        return politicians[politician_name]
    

def scrapeTrade(trade):
    trade_name_tag = trade.find("h3", class_="q-fieldset issuer-name")
    trade_name = ""
    abbreviation = ""
    buy_sell = ""
    amount = ""
    date = ""
    owner = ""
    publish_date = ""

    if trade_name_tag:
        trade_name = trade_name_tag.find('a').text
        #print(f"Trade Name: {trade_name}")

    abbreviation_tag = trade.find("span", class_="q-field issuer-ticker")
    if abbreviation_tag:
        abbreviation = abbreviation_tag.text
        #print(f"Abbreviation: {abbreviation}")

    buy_sell_tags = trade.find_all("td", class_="align-middle")
    try:
        buy_sell_tag = buy_sell_tags[6]
        if buy_sell_tag:
            buy_sell_block = buy_sell_tag.find("span", "q-field")
            buy_sell = buy_sell_block.text
            #print(f"Buy/Sell: {buy_sell}")
    except:
        print("Error, buy_sell tag not found")

    amount_symbol_tag = trade.find("div", class_="tx-trade-size-tooltip-wrapper")
    if amount_symbol_tag:
        amount_tag = amount_symbol_tag.find("span")
        if amount_tag:
            amount = amount_tag.text
            #yield amount
            #print(f"Amount: {amount}")

    dateblocks = trade.find_all("div", class_="text-center")
    try:
        dateblock = dateblocks[1]
        if dateblock:
            date_tag = dateblock.find("div", class_="text-size-3 font-medium")
            if date_tag:
                date = date_tag.text
                #print(f"Date: {date}")
            else:
                print("Date tag not found")
        else:
            print("Date block not found")

        publish_dateblock = dateblocks[0]
        if publish_dateblock:
            publish_date_tag = publish_dateblock.find("div", class_="text-size-3 font-medium")
            if publish_date_tag:
                publish_date = publish_date_tag.text
                #print(f"Publish Date: {publish_date}")
            else:
                print("Publish date tag not found")

        else:
            print("Publish date blocks not found")
    except:
        print("Error timeblocks not found")

    owner_blocks = trade.find_all("td", class_="align-middle")
    try:
        owner_block = owner_blocks[5]
        if owner_block:
            owner_tag = owner_block.find("span", class_="q-label")
            if owner_tag:
                owner = owner_block.text
        else:
            print("Owner tag not found")
    except:
        print("no owner blocks found")



    return trade_name,abbreviation,publish_date,date,owner,buy_sell,amount

def scrapeTradeInfo():
    scraped_trade = soup.find_all("tr", class_="border-b")
    for trade in scraped_trade:
        current_politician = scrapePolitician(trade)
        tradeinfo = scrapeTrade(trade)
        if current_politician:
            current_politician.addTrade(tradeinfo[0],tradeinfo[1],tradeinfo[2],tradeinfo[3],tradeinfo[4], tradeinfo[5], tradeinfo[6])

date_conversion_table = {
    "1": "January",
    "2": "February",
    "3": "March",
    "4": "April",
    "5": "May",
    "6": "June",
    "7": "July",
    "8": "August",
    "9": "September",
    "10": "October",
    "11": "November",
    "12": "December"
}

def todaysDate():
    from datetime import date
    unformatted_date = date.today()
    month = str(unformatted_date.month)
    day = unformatted_date.day
    month_name = date_conversion_table[month]
    formatted_date = f"{day} {month_name[0:3]}"
    return formatted_date

def filter(allowed_politicians):
    #Remove irrelevant politicians
    politicians_to_remove = []
    for politician in politicians:
        if not politicians[politician].getName() in allowed_politicians:
            politicians_to_remove.append(politician)

    for politician in politicians_to_remove:
            politicians.pop(politician)

    #Remove old trades
    todays_date = "20 Dec"
    for politician in politicians:
        politician_trades = politicians[politician].getTrades()
        trades_to_remove = []
        for trade in politician_trades:
            publish_date = trade.getPublishDate()
            if  not ":" in publish_date:
                if not publish_date == todays_date:
                    trades_to_remove.append(trade)
            
        
        for trade in trades_to_remove:
            politicians[politician].removeTrade(trade)

    #remove trades made by child
    for politician in politicians:
        trades_to_remove = []
        for trade in politicians[politician].getTrades():
            if trade.getOwner() not in ["Self","Spouse"]:
                trades_to_remove.append(trade)
        
        for trade in trades_to_remove:
            politicians[politician].removeTrade(trade)

    # Remove trades with abbreviation "N/A"
    for politician in politicians:
        trades_to_remove = []
        for trade in politicians[politician].getTrades():
            if trade.getAbbr() == "N/A":
                trades_to_remove.append(trade)
            
        
        for trade in trades_to_remove:
            politicians[politician].removeTrade(trade)


def Scrape(tracked_politicians):
    scrapeTradeInfo()
    filter(tracked_politicians)
    return politicians
