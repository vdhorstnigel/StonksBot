import sys
import time
import telepot
import string
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineQueryResultArticle, InputTextMessageContent
import bs4
import requests
from bs4 import BeautifulSoup
import yfinance as yf
from array import *
import numpy as np
import pandas as pd
import telegram
import mysql.connector

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  passwd="Password1234!",
  database="Stocks"
)


mycursor = mydb.cursor()

t = time.localtime()
current_time = time.strftime("%H:%M:%S", t)

def handle(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    print(content_type, chat_type, chat_id)
    stock = msg['text']

    if content_type == 'text' and "/price" in stock:
        try :
            stock = stock.split()
            r=requests.get('https://finance.yahoo.com/quote/' + stock[1])
            soup=bs4.BeautifulSoup(r.text,"lxml")
            price=soup.find_all('div',{'class':'My(6px) Pos(r) smartphone_Mt(6px)'})[0].find('span').text
            name=soup.find_all('div',{'Mt(15px)'})[0].find('h1').text
            bot.sendMessage(chat_id, "The Price now for " + name + " is " + str(price))
        except IndexError:
            bot.sendMessage(chat_id, "Could not find " + stock[1])
            
    elif content_type == 'text' and msg["text"] == "/watch":
        sql = ("SELECT * FROM Stocks Where id = %s")
        val = (chat_id, )
        mycursor.execute(sql, val)
        myresult = mycursor.fetchall()
        for row in myresult:
            bot.sendMessage(chat_id, row[2] + " bought at " + row[3] + ", current price at " + row[5] + ", profit of " + row[6] + "%. Notify at " + str(row[7]) + "%")
       
    elif content_type == 'text' and "/watch" in stock:
        try :
            stock = stock.split()
            STOCK = stock[1].upper()
            if len(stock) == 3:
                percentage = 1
            else:
                percentage = stock[3]
            r=requests.get('https://finance.yahoo.com/quote/' + stock[1])
            soup=bs4.BeautifulSoup(r.text,"lxml")
            price=soup.find_all('div',{'class':'My(6px) Pos(r) smartphone_Mt(6px)'})[0].find('span').text
            name=soup.find_all('div',{'Mt(15px)'})[0].find('h1').text
            profit = (float((price))/float((stock[2])))*100 - 100
            profit = "%.2f" % profit
            sql = ("SELECT * FROM Stocks Where Id = %s and Stock = %s")
            val = (chat_id, STOCK)
            mycursor.execute(sql, val)
            myresult = mycursor.fetchall()
            row_count = mycursor.rowcount
            if row_count == 0:
                sql = "INSERT INTO Stocks (Id, Stock, Price, Profit , vPrice , vProfit, Percentage) VALUES (%s, %s, %s, %s, %s ,%s, %s)"
                val = (chat_id, STOCK, stock[2], profit, stock[2], profit, percentage)
                mycursor.execute(sql, val)
                mydb.commit()
                bot.sendMessage(chat_id, "Added to watchlist, bought at " + stock[2])  
            else:
                bot.sendMessage(chat_id, "Already in watchlist, bought at " + myresult[2] + ", current price at " + myresult[5] + ", profit of " + myresult[6] + "%. Notify at " + myresult[7] + "%")
        except IndexError:
            bot.sendMessage(chat_id, "Could not find " + stock[1])

    elif content_type == 'text' and msg["text"] == "/dividend":
            sql = ("SELECT * FROM Stocks Where Id = %s")
            val = (chat_id, )
            mycursor.execute(sql, val)
            myresult = mycursor.fetchall()
            try :
                for row in myresult:
                    r=requests.get('https://finance.yahoo.com/quote/' + row[2])
                    soup=bs4.BeautifulSoup(r.text,"lxml")
                    name=soup.find_all('div',{'Mt(15px)'})[0].find('h1').text
                    share = yf.Ticker(row[2])
                    div = share.dividends
                    df = pd.DataFrame(div)
                    bot.sendMessage(chat_id, "The dividend for " + name + " = " + str(div[-3]) + " on " + str((df.index[-3])))
                    bot.sendMessage(chat_id, "The dividend for " + name + " = " + str(div[-2]) + " on " + str((df.index[-2])))
                    bot.sendMessage(chat_id, "The dividend for " + name + " = " + str(div[-1]) + " on " + str((df.index[-1])))
            except IndexError:
                bot.sendMessage(chat_id, "No dividend for " + name)
                
    elif content_type == 'text' and "/dividend" in stock:
        try :
            stock = stock.split()
            r=requests.get('https://finance.yahoo.com/quote/' + stock[1])
            soup=bs4.BeautifulSoup(r.text,"lxml")
            name=soup.find_all('div',{'Mt(15px)'})[0].find('h1').text
            share = yf.Ticker(stock)
            div = share.dividends
            df = pd.DataFrame(div)
            bot.sendMessage(chat_id, "The dividend for " + name + " = " + str(div[-3]) + " on " + str((df.index[-3])))
            bot.sendMessage(chat_id, "The dividend for " + name + " = " + str(div[-2]) + " on " + str((df.index[-2])))
            bot.sendMessage(chat_id, "The dividend for " + name + " = " + str(div[-1]) + " on " + str((df.index[-1])))
        except IndexError:
            bot.sendMessage(chat_id, "Could not find " + stock[1])

    if content_type == 'text' and "/holding" in stock:
        try :    
            stock = stock.split()
            def get_soup(url): 
                page = requests.get(url)
                soup = bs4.BeautifulSoup(page.content, "lxml")
                return soup
            soup = get_soup('https://sg.finance.yahoo.com/quote/' + stock[1] +'/holdings?p=' + stock [1])
            divs = soup.find_all('div')
            name=soup.find_all('div',{'Mt(15px)'})[0].find('h1').text
            def top_10(divs):
                top10 = []
                top10div = soup.find_all("div", { "class" : "Mb(20px)" })
                top10tr = top10div[0].find_next('table').tbody.find_all('tr')
                for tr in top10tr:
                    top10td = tr.find_all('td')
                    top10.append(top10td[0].text)
                return top10    
            def top_10_Holdings(divs):
                top10_Holdings = []
                top10div = soup.find_all("div", { "class" : "Mb(20px)" })
                top10tr = top10div[0].find_next('table').tbody.find_all('tr')
                for tr in top10tr:
                    top10td = tr.find_all('td')
                    top10_Holdings.append(top10td[2].text)
                return top10_Holdings   
            top10list = top_10(divs)
            top10_Holdings = top_10_Holdings(divs)
            bot.sendMessage(chat_id, "The Top 10 % for \n" + name + "\n" + top10list[0] + " - " + top10_Holdings[0] + "\n" + top10list[1] + " - " + top10_Holdings[1] + "\n" + top10list[2] + " - " + top10_Holdings[2] + "\n" + top10list[3] + " - " + top10_Holdings[3] + "\n" + top10list[4] + " - " + top10_Holdings[4] + "\n" + top10list[5] + " - " + top10_Holdings[5] + "\n" + top10list[6] + " - " + top10_Holdings[6] + "\n" + top10list[7] + " - " + top10_Holdings[7] + "\n" + top10list[8] + " - " + top10_Holdings[8] + "\n" + top10list[9] + " - " + top10_Holdings[9])
        except IndexError:
            bot.sendMessage(chat_id, "Could not find " + stock[1])
            
    if content_type == 'text' and "/gainers" in stock:
        try :    
            stock = stock.split()
            def get_soup(url): 
                page = requests.get(url)
                soup = bs4.BeautifulSoup(page.content, "lxml")
                return soup
            soup = get_soup('https://finance.yahoo.com/gainers')
            divs = soup.find_all('div')
            def top_10(divs):
                top10 = []
                top10div = soup.find_all("div", { "class" : "Mb(20px)" })
                top10tr = top10div[0].find_next('table').tbody.find_all('tr')
                for tr in top10tr:
                    top10td = tr.find_all('td')
                    top10.append(top10td[1].text)
                return top10    
            def top_10_Holdings(divs):
                top10_Holdings = []
                top10div = soup.find_all("div", { "class" : "Mb(20px)" })
                top10tr = top10div[0].find_next('table').tbody.find_all('tr')
                for tr in top10tr:
                    top10td = tr.find_all('td')
                    top10_Holdings.append(top10td[2].text)
                return top10_Holdings
            def top_10_Price(divs):
                top10_Price = []
                top10div = soup.find_all("div", { "class" : "Mb(20px)" })
                top10tr = top10div[0].find_next('table').tbody.find_all('tr')
                for tr in top10tr:
                    top10td = tr.find_all('td')
                    top10_Price.append(top10td[3].text)
                return top10_Price
            def top_10_PriceP(divs):
                top10_PriceP = []
                top10div = soup.find_all("div", { "class" : "Mb(20px)" })
                top10tr = top10div[0].find_next('table').tbody.find_all('tr')
                for tr in top10tr:
                    top10td = tr.find_all('td')
                    top10_PriceP.append(top10td[4].text)
                return top10_PriceP
            top10list = top_10(divs)
            top10_Holdings = top_10_Holdings(divs)
            top10_Price = top_10_Price(divs)
            top10_PriceP = top_10_PriceP(divs)
            bot.sendMessage(chat_id, "The Top 10 Gainers are \n" + top10list[0] + " - " + top10_Holdings[0] + ", Profit of " + top10_Price[0] + ", " + top10_PriceP[0] + "\n" + top10list[1] + " - " + top10_Holdings[1] + ", Profit of " + top10_Price[1] + ", " + top10_PriceP[1] + "\n" + top10list[2] + " - " + top10_Holdings[2] + ", Profit of " + top10_Price[2] + ",  " + top10_PriceP[2] + "\n" + top10list[3] + " - " + top10_Holdings[3] + ", Profit of " + top10_Price[3] + ", " + top10_PriceP[3] + "\n" + top10list[4] + " - " + top10_Holdings[4] + ", Profit of " + top10_Price[4] + ", " + top10_PriceP[4] + "\n" + top10list[5] + " - " + top10_Holdings[5] + ", Profit of " + top10_Price[5] + ", " + top10_PriceP[5] + "\n" + top10list[6] + " - " + top10_Holdings[6] + ", Profit of" + top10_Price[6] + ", " + top10_PriceP[6] + "\n" + top10list[7] + " - " + top10_Holdings[7] + ", Profit of " + top10_Price[7] + ", " + top10_PriceP[7] + "\n" + top10list[8] + " - " + top10_Holdings[8] + ", Profit of  " + top10_Price[8] + ", " + top10_PriceP[8] + "\n" + top10list[9] + " - " + top10_Holdings[9] + ", Profit of " + top10_Price[9] + ", " + top10_PriceP[9])
        except IndexError:
            bot.sendMessage(chat_id, "Could not find that stock")

    if content_type == 'text' and "/losers" in stock:
        try :    
            stock = stock.split()
            def get_soup(url): 
                page = requests.get(url)
                soup = bs4.BeautifulSoup(page.content, "lxml")
                return soup
            soup = get_soup('https://finance.yahoo.com/losers')
            divs = soup.find_all('div')
            def top_10(divs):
                top10 = []
                top10div = soup.find_all("div", { "class" : "Mb(20px)" })
                top10tr = top10div[0].find_next('table').tbody.find_all('tr')
                for tr in top10tr:
                    top10td = tr.find_all('td')
                    top10.append(top10td[1].text)
                return top10    
            def top_10_Holdings(divs):
                top10_Holdings = []
                top10div = soup.find_all("div", { "class" : "Mb(20px)" })
                top10tr = top10div[0].find_next('table').tbody.find_all('tr')
                for tr in top10tr:
                    top10td = tr.find_all('td')
                    top10_Holdings.append(top10td[2].text)
                return top10_Holdings
            def top_10_Price(divs):
                top10_Price = []
                top10div = soup.find_all("div", { "class" : "Mb(20px)" })
                top10tr = top10div[0].find_next('table').tbody.find_all('tr')
                for tr in top10tr:
                    top10td = tr.find_all('td')
                    top10_Price.append(top10td[3].text)
                return top10_Price
            def top_10_PriceP(divs):
                top10_PriceP = []
                top10div = soup.find_all("div", { "class" : "Mb(20px)" })
                top10tr = top10div[0].find_next('table').tbody.find_all('tr')
                for tr in top10tr:
                    top10td = tr.find_all('td')
                    top10_PriceP.append(top10td[4].text)
                return top10_PriceP
            top10list = top_10(divs)
            top10_Holdings = top_10_Holdings(divs)
            top10_Price = top_10_Price(divs)
            top10_PriceP = top_10_PriceP(divs)
            bot.sendMessage(chat_id, "The Top 10 Losers are \n" + top10list[0] + " - " + top10_Holdings[0] + ", Loss of " + top10_Price[0] + ", " + top10_PriceP[0] + "\n" + top10list[1] + " - " + top10_Holdings[1] + ", Loss of " + top10_Price[1] + ", " + top10_PriceP[1] + "\n" + top10list[2] + " - " + top10_Holdings[2] + ", Loss of " + top10_Price[2] + ",  " + top10_PriceP[2] + "\n" + top10list[3] + " - " + top10_Holdings[3] + ", Loss of " + top10_Price[3] + ", " + top10_PriceP[3] + "\n" + top10list[4] + " - " + top10_Holdings[4] + ", Loss of " + top10_Price[4] + ", " + top10_PriceP[4] + "\n" + top10list[5] + " - " + top10_Holdings[5] + ", Loss of " + top10_Price[5] + ", " + top10_PriceP[5] + "\n" + top10list[6] + " - " + top10_Holdings[6] + ", Loss of" + top10_Price[6] + ", " + top10_PriceP[6] + "\n" + top10list[7] + " - " + top10_Holdings[7] + ", Loss of " + top10_Price[7] + ", " + top10_PriceP[7] + "\n" + top10list[8] + " - " + top10_Holdings[8] + ", Loss of  " + top10_Price[8] + ", " + top10_PriceP[8] + "\n" + top10list[9] + " - " + top10_Holdings[9] + ", Loss of " + top10_Price[9] + ", " + top10_PriceP[9])
        except IndexError:
            bot.sendMessage(chat_id, "Could not find that stock")
   
    elif content_type == 'text' and "/unwatch" in stock:
        try :
            stock = stock.split()
            STOCK = stock[1].upper()
            sql = ("DELETE FROM Stocks Where Id = %s and Stock = %s")
            val = (chat_id, STOCK)
            mycursor.execute(sql, val)
            mydb.commit()
            bot.sendMessage(chat_id, "Removed from watchlist")
        except IndexError:
            bot.sendMessage(chat_id, "Error")
            


def check():
    try:
        mycursor.execute("SELECT * FROM Stocks")
        myresult = mycursor.fetchall()
        for row in myresult:
            r=requests.get('https://finance.yahoo.com/quote/' + row[2])
            soup=bs4.BeautifulSoup(r.text,"lxml")
            price=soup.find_all('div',{'class':'My(6px) Pos(r) smartphone_Mt(6px)'})[0].find('span').text
            name=soup.find_all('div',{'Mt(15px)'})[0].find('h1').text
            profit = (float((price))/float((row[3])))*100 - 100
            profit = "%.2f" % profit
            iprofit = float(row[4])
            vprofit = float(row[6])
            percentage = int(row[7])
            if (((vprofit > 0) and (iprofit < 0)) or ((vprofit < 0) and (iprofit > 0))):
                cprofit = vprofit + iprofit
            else:
                cprofit = vprofit - iprofit
            if cprofit >= percentage:
                bot.sendMessage(row[1], row[2] + " bought at " + row[3] + ", current price at " + row[5] + ", original profit of " + str(iprofit) + "%, current profit of " + str(vprofit) + "%, gain of " +  str("%.2f" % cprofit) + "%")
                sql = ("UPDATE Stocks SET Profit = %s WHERE Id = %s AND Stock = %s")
                val = (vprofit, row[1], row[2])
                mycursor.execute(sql, val)
                mydb.commit()
                sql = ("UPDATE Stocks SET vPrice = %s WHERE Id = %s AND Stock = %s")
                val2 = (str(price), row[1], row[2])
                mycursor.execute(sql, val2)
                mydb.commit()
            elif cprofit <= -percentage:
                bot.sendMessage(row[1], row[2] + " bought at " + row[3] + ", current price at " + row[5] + ", original profit of " + str(iprofit) + "%, current profit of " + str(vprofit) + "%, loss of " +  str("%.2f" % cprofit) + "%")
                sql = ("UPDATE Stocks SET Profit = %s WHERE Id = %s AND Stock = %s")
                val = (vprofit, row[1], row[2])
                mycursor.execute(sql, val)
                mydb.commit()
                sql = ("UPDATE Stocks SET vPrice = %s WHERE Id = %s AND Stock = %s")
                val2 = (str(price), row[1], row[2])
                mycursor.execute(sql, val2)
                mydb.commit()
            else:
                sql = ("UPDATE Stocks SET vProfit = %s WHERE Id = %s AND Stock = %s")
                val = (profit, row[1], row[2])
                mycursor.execute(sql, val)
                mydb.commit()
                sql = ("UPDATE Stocks SET vPrice = %s WHERE Id = %s AND Stock = %s")
                val2 = (str(price), row[1], row[2])    
                mycursor.execute(sql, val2)
                mydb.commit()
    except IndexError:
        time.sleep(1)
         
         
TOKEN = ''
    
Tokenfile = open("token.txt", "r")
TOKEN = (Tokenfile.read())
Tokenfile.close()

bot = telepot.Bot(TOKEN)
MessageLoop(bot, handle).run_as_thread()
print ('Listening ...')


# Keep the program running.
while 1:
    check()
    time.sleep(10)



