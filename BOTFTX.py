# ใช้สำหรับ PLOT TIME
import ccxt
import json
import pandas as pd
import time
import requests
from datetime import datetime
import csv
from csv import DictWriter
from tkinter import ttk
from tkinter import *
GUI = Tk()
GUI.geometry('500x500')
GUI.title('BOT FTX')
S_apikey = StringVar()
S_secret = StringVar()
S_path = StringVar()
S_subAccount =StringVar()
l_apikey = Label(GUI,text='API KEY',font=40)
l_apikey.pack()
E_apikey = Entry(GUI,textvariable=S_apikey,width=60)
E_apikey.pack()
l_secret = Label(GUI,text='SECRET KEY',font=40)
l_secret.pack()
E_secret = Entry(GUI,textvariable=S_secret,width=60)
E_secret.pack()
l_subaccount = Label(GUI,text='ชื่อ Sub Account  ถ้าไม่มี  ใส่ 0',font=40)
l_subaccount.pack()
E_subaccount = Entry(GUI,textvariable=S_subAccount,width=60)
E_subaccount.pack()
l_path = Label(GUI,text='Path File',font=40)
l_path.pack()
E_path = Entry(GUI,textvariable=S_path,width=60)
E_path.pack()

#from google.colab import drive
#drive.mount('/content/drive')
#%matplotlib inline
def RunProgram(event=None):
    pd.options.mode.chained_assignment = None  # default='warn'
    global x   #gobal ตอนเอาไปลงเครื่อง ต้องเอาไปไว้ด้านบนตัวแปร x = 0
    global d
    x = 0 ##ดึงค่าพาย
    d = 0 ##จำตำเเหน่งของพาย
    koi = 0 ##ลูบของพาย

    # กำหนด PARAMETER ที่จำเป็น
    pair = "XRP-PERP"
    timestampRecordUltil = 1592442000
    maxExposure = 200
    MIN_TPRANGE = 0.001
    timeFrame = "5m"
    countBar = 50
    apiKey = S_apikey.get()
    secret = S_secret.get()
    path = S_path.get()
    pathlog= path.replace('\ ','/')
    path1 = S_path.get()
    pathEXPO = path1.replace('\ ','/')
    password = "0"
    subaccount = S_subAccount.get()
    #databaseAddress = #"drive/My Drive/BOTDATABASE"

    # รวมข้อมูลของ apiKey และ secret สำหรับเอาไว้เรียกใช้งาน
    #exchange = ccxt.deribit({'apiKey': apiKey ,'secret': secret,'enableRateLimit': True,"urls": {"api": "https://test.deribit.com"}}) #สำหรับใช้งาน deribit

    exchange = ccxt.ftx({
        'apiKey' : apiKey ,'secret' : secret  ,
        'password' : password, 
        'enableRateLimit': True,
    })

    # Sub Account Check

    if subaccount == "0":
        print("This is Main Account")
    else:
        exchange.headers = {
            'ftx-SUBACCOUNT': subaccount,
            }

    def getTime():
        named_tuple = time.localtime() # get struct_time
        Time = time.strftime("%m/%d/%Y, %H:%M:%S", named_tuple)
        print(Time)

    #==============================================================================
    # ใช้ json ในการดึงข้อมูลราคา PRODUCT ที่เราสนใจจะเทรด

    def getjsonPrice() :
        r1 = json.dumps(exchange.fetch_ticker('XRP-PERP'))
        dataPriceBTC = json.loads(r1)
        jsonPrice = dataPriceBTC['last']
        print('XRP-PERP=',jsonPrice,'XRP')
        print(' ')
        return jsonPrice

    #==============================================================================
    # ใช้สำหรับประมวลผล SIGNAL เพื่อส่งคำสั่งซื้อขาย
    # CREDIT HEIKIN CODE : 
    # https://stackoverflow.com/questions/40613480/heiken-ashi-using-pandas-python

    def getSignal():

        # ดึงข้อมูลราคาจาก EXCHANGE
        signal = 0
        ohlcv  = exchange.fetch_ohlcv(pair, timeFrame, limit=countBar)
        df =  pd.DataFrame(ohlcv)
        df_rename = df.rename(columns={0: 'Time',1: 'Open',2: 'High',3: 'Low',4: 'Close',5: 'Volume'})
        # CODE สำหรับ PLOT GRAPH CANDLE STICK
        #  fig = go.Figure(data=[go.Candlestick(x=df_rename['Time'],
        #                  open=df_rename['Open'],
        #                  high=df_rename['High'],
        #                  low=df_rename['Low'],
        #                  close=df_rename['Close'])])

        #  fig.update_layout(xaxis_rangeslider_visible=False)
        #  fig.show()

        # แปลงข้อมูลจาก CANDLE STICK เป็น HEIKIN ASHI
        df_HA = df_rename
        df_HA['Close']=(df_rename['Open']+ df_rename['High']+ df_rename['Low']+df_rename['Close'])/4

        for i in range(0, len(df)):
            if i == 0:
                df_HA['Open'][i]= ( (df_rename['Open'][i] + df_rename['Close'][i] )/ 2)
            else:
                df_HA['Open'][i] = ( (df_rename['Open'][i-1] + df_rename['Close'][i-1] )/ 2)

        df_HA['High']=df_rename[['Open','Close','High']].max(axis=1)
        df_HA['Low']=df_rename[['Open','Close','Low']].min(axis=1)
        # CODE สำหรับ PLOT GRAPH HEIKIN ASHI
        #  fig = go.Figure(data=[go.Candlestick(x=df_rename['Time'],
        #                  open=df_HA['Open'],
        #                  high=df_HA['High'],
        #                  low=df_HA['Low'],
        #                  close=df_HA['Close'])])

        #  fig.update_layout(xaxis_rangeslider_visible=False)
        #  fig.show()

        # อ่าน SIGNAL จากกราฟโดยใช้ MATH. เข้ามาช่วย
        print(str(exchange).upper())
        print("PI REBALANCE !","TF",timeFrame)
        '''
        ma = 20 

        response = exchange.fetch_ohlcv(pair,timeFrame,None,ma)
        d = json.dumps(response)  
        data = pd.read_json ( d )

        ma20 = data[4].rolling(window=ma).mean( ).tail(1)
        jsonPrice = getjsonPrice()
        if signal == sumExposure[2] < sumExposure[1] and (sumExposure[0]-markUpExposure[0]) >= MIN_TPRANGE and sumExposure[7] == 0 and sumExposure[9] == 0 :
            signal = "SELL SIGNAL !"
        elif signal == sumExposure[10] < maxExposure and (markUpExposure[0]-sumExposure[0]) >= MIN_TPRANGE and sumExposure[7] == 0 and sumExposure[9] == 0  :
            signal = "BUY SIGNAL !"
        else :
            signal = "WAITING SIGNAL !"

        return signal
        '''
    #==============================================================================
    # ใช้ GOOGLE SHEET ในการกำหนดโซนและ MARK UP EXPOSURE ในแต่ละช่วงราคา

    #def getmarkUpExposure():
    #  url='https://docs.google.com/spreadsheets/d/1XDv-yZtpHSaar3woOTnw8UoHFa3MlDUo_JXs_XeLnd4/export?gid=1643548932&format=csv'

    #  dfgooglesheet = pd.read_csv(url)
    #  header = dfgooglesheet.columns.values.tolist()
    #  body = dfgooglesheet.values.tolist()
    #  markUpExposure = 0

    #print('BTC-PERPETUAL =',dataPriceBTC['last'])
    #  for i in range (len(body)):
    #    if dataPriceBTC['last'] >= body[i][1] and dataPriceBTC['last'] < body[i][2] :
    #      markUpExposure = body[i][4]
    #  return markUpExposure

    #==============================================================================
    # ใช้ EXCEL ในการกำหนดโซนและ MARK UP EXPOSURE ในแต่ละช่วงราคา

    def getmarkUpExposure():
   
        dfExcelmarkUpExposure = pd.read_csv(pathEXPO + '/EXPOSUREscalp.csv')

        header = dfExcelmarkUpExposure.columns.values.tolist()
        body = dfExcelmarkUpExposure.values.tolist()

        markUpExposure = []
        jsonPrice = getjsonPrice()
        #print('BTC-PERPETUAL =',jsonPrice)
        for i in range (len(body)):
            if jsonPrice > body[i][1] and jsonPrice <= body[i][2] :
                markUpExposure.append(body[i][4])
                markUpExposure.append(body[i][1])
                markUpExposure.append(body[i][2])
            
        return markUpExposure

    #==============================================================================
    # คำนวน EXPOSURE และ TRANSACTION ที่เปิดปิดทั้งหมดจาก HISTORY

    def getsumExposure() :

        with open('log.csv', newline='') as f:
            reader = csv.reader(f)
            data = list(reader)
        sumExposure = []
        totalSellExposure = 0
        totalBuyExposure = 0
        countSellExposure = 0
        countBuyExposure = 0

        totalSellLimitExposure = 0
        totalBuyLimitExposure = 0
        countBuyLimitExposure = 0
        countSellLimitExposure = 0

        for i in range (len(data)):
            if data[i][4] == "sell":
                totalSellExposure += float(data[i][6])
                countSellExposure += 1
            elif data[i][4] == "buy":
                totalBuyExposure += float(data[i][6])
                countBuyExposure += 1

        dfMyOrderList = getUpdatePending()

        for i in range (len(dfMyOrderList)) :
            if dfMyOrderList[i][4] == "sell" :
                totalSellLimitExposure += dfMyOrderList[i][6]
                countSellLimitExposure += 1
            elif dfMyOrderList[i][4] == "buy" :
                totalBuyLimitExposure += dfMyOrderList[i][6]
                countBuyLimitExposure += 1

        sumExposureValue = totalBuyExposure - totalSellExposure
        sumExposurePending = totalBuyLimitExposure - totalSellExposure
        allExposure = sumExposureValue+sumExposurePending

    # เก็บ DATA เอาไว้ใน LIST เพื่อดึงไปใช้งานใน FUNCTION อื่นๆ

        sumExposure.append(sumExposureValue)        #sumExposure[0]
        sumExposure.append(totalBuyExposure)        #sumExposure[1]
        sumExposure.append(totalSellExposure)       #sumExposure[2]
        sumExposure.append(countSellExposure)       #sumExposure[3]
        sumExposure.append(countBuyExposure)        #sumExposure[4]
        sumExposure.append(sumExposurePending)      #sumExposure[5]
        sumExposure.append(totalBuyLimitExposure)   #sumExposure[6]
        sumExposure.append(countBuyLimitExposure)   #sumExposure[7]
        sumExposure.append(totalSellLimitExposure)  #sumExposure[8]
        sumExposure.append(countSellLimitExposure)  #sumExposure[9]
        sumExposure.append(allExposure)             #sumExposure[10]


        return sumExposure

    #==============================================================================
    # คำสั่งที่ใช้ในการเปิด ORDER (ใช้คำสั่ง LIMIT ORDER)

    def getOpenOrder():

        getCancelPending()
        markUpExposure = getmarkUpExposure()
        sumExposure = getsumExposure()
        OpenOrder = ''
        dfMyOrderList = getUpdatePending()

        print("TOTAL BUY  EXPOSURE =",sumExposure[1],"XRP")
        print("TOTAL SELL EXPOSURE =",sumExposure[2],"XRP")
        print("TOTAL BUY LIMIT  EXPOSURE =",sumExposure[6],"XRP",',','QTY =',sumExposure[7])
        print("TOTAL SELL LIMIT EXPOSURE =",sumExposure[8],"XRP",',','QTY =',sumExposure[9])
        print("SUM EXPOSURE =",sumExposure[0],"/",maxExposure,"XRP","(ACTUAL / INCLUDE PENDING)")
        print("MAX EXPOSURE =",markUpExposure[0],"XRP","(MARK UP)")
        print(" ")
        print("TOTAL BUY  TRANSACTION =",sumExposure[4])
        print("TOTAL SELL TRANSACTION =",sumExposure[3])
        print("SUM TRANSACTIOB =",sumExposure[3]+sumExposure[4])
        print(" ")
    #print(signal)

        if markUpExposure[0] > sumExposure[0] and (markUpExposure[0] - sumExposure[0]) >= MIN_TPRANGE and sumExposure[7] == 0 and sumExposure[9] == 0 :
            exchange.create_order( pair, "limit" , "buy", (markUpExposure[0]-sumExposure[0]), markUpExposure[1] )#, params={"reduceOnly": False, "ioc": True , "postOnly": True})
            print("BUY LIMIT EXECUTE !",markUpExposure[1],(markUpExposure[0] - sumExposure[0]))
            OpenOrder = 'BUY'

        elif sumExposure[0] > markUpExposure[0] and (sumExposure[0] - markUpExposure[0]) >= MIN_TPRANGE and sumExposure[7] == 0 and sumExposure[9] == 0  :
            exchange.create_order( pair, "limit" , "sell", (sumExposure[0] - markUpExposure[0]) , markUpExposure[2] )#, params={"reduceOnly": False, "ioc": True , "postOnly": True})
            print("SELL LIMIT EXECUTE !",markUpExposure[2],(sumExposure[0] - markUpExposure[0]))
            OpenOrder = 'SELL'
        
        else :
            print("NO ACTION !")

        return OpenOrder

    #==============================================================================
    # บันทึกข้อมูลการเทรดลงใน GOOGLE SHEET

    # INSERT RECORD TO GOOGLE SPREADSHEET
    # LEARNING FROM
    # 1.https://www.youtube.com/watch?v=ktlf3vjo7ik
    # 2.https://colab.research.google.com/drive/1A5sWY1Xm_jjO4Mm0OoB8H8fUatlGRKDj?usp=sharing
    # WRITE CSV : https://stackoverflow.com/questions/28277150/write-a-list-in-a-python-csv-file-one-new-row-per-list
    # READ CSV : https://stackoverflow.com/questions/24662571/python-import-csv-to-list

    def getUpdateRecord() :

        checkIDincsv = []
        with open(pathlog + '/log.csv', newline='') as f:
            reader = csv.reader(f)
            data = list(reader)

        for i in range (len(data)):
            checkIDincsv.append(data[i][0])

        dfMyTrade = pd.DataFrame(exchange.fetchMyTrades(pair,timestampRecordUltil,1000),columns=['id','timestamp','datetime','symbol','side','price','amount'])
        dfMyTradeList = dfMyTrade.values.tolist()

    #  print("UPDATING THE RECORD PLEASE WAIT :)")
        for i in range (len(dfMyTradeList)):
            if dfMyTradeList[i][0] not in checkIDincsv :
                with open(pathlog + "/log.csv", "a+", newline='') as fp:
                    wr = csv.writer(fp, dialect='excel')
                    wr.writerow(dfMyTradeList[i])
                    print(dfMyTradeList[i][0],dfMyTradeList[i][2],dfMyTradeList[i][3],dfMyTradeList[i][4],dfMyTradeList[i][5],dfMyTradeList[i][6])

    #def getBackupRecord():
    #drive.mount('drive')
    #!cp TRADINGLOG.csv "drive/My Drive/BOTDATABASE"
    #print("BACKUP TRADINGLOG IN GOOGLE SHEET SUCCESSFUL!")
    
    #==============================================================================
    # UPDATE PENDING ORDER เพื่อป้องกันการเปิด POSITION เกินกำหนด

    def getUpdatePending():

        dfMyOrder = pd.DataFrame(exchange.fetchOpenOrders(pair,timestampRecordUltil,1000),columns=['id','timestamp','datetime','symbol','side','price','amount'])
        dfMyOrderList = dfMyOrder.values.tolist()

        return dfMyOrderList

    #==============================================================================
    # ยกเลิก PENDING เมื่อราคาห่างจากจุดที่วางเอาไว้ 20$

    def getCancelPending():
        dfMyOrderList = getUpdatePending()

        for i in range (len(dfMyOrderList)):
            
            if (dfMyOrderList[i][5]-jsonPrice) > MIN_TPRANGE and dfMyOrderList[i][4] == "sell" :
                exchange.cancel_order(dfMyOrderList[i][0])
                print("CANCELED :",dfMyOrderList[i])
            elif (jsonPrice-dfMyOrderList[i][5]) > MIN_TPRANGE and dfMyOrderList[i][4] == "buy" :
                exchange.cancel_order(dfMyOrderList[i][0])
                print("CANCELED :",dfMyOrderList[i])

                print(" ")

    #==============================================================================
    # BOT LINE แจ้งเตือนเมื่อมีการ RUN BOT ครั้งแรก และการ EXECUTE ORDER
    #https://medium.com/@pattanapong.sriph/%E0%B8%AA%E0%B8%A3%E0%B9%89%E0%B8%B2%E0%B8%87-line-notify-%E0%B8%94%E0%B9%89%E0%B8%A7%E0%B8%A2%E0%B8%A0%E0%B8%B2%E0%B8%A9%E0%B8%B2-python-%E0%B9%82%E0%B8%94%E0%B8%A2%E0%B9%83%E0%B8%8A%E0%B9%89-pycharm-867de316ced0
    '''
    def getbotLineStart():

    token = 'Wt5mRvYNrSlXbu5h0hBU2jZ89TnLu8hcG1M1ntf7TFQ'
    url = 'https://notify-api.line.me/api/notify'
    headers = {'content-type':'application/x-www-form-urlencoded','Authorization':'Bearer '+token}
    msg = "BOT START WORKING"
    r = requests.post(url, headers=headers, data = {'message':msg})
    print (r.text)
    '''
    '''
    def getbotLineExecute():

    dfMyOrderList = getUpdatePending()
    A1 = str(dfMyOrderList[0][4]).upper()
    A2 = str(dfMyOrderList[0][5]).upper()
    A3 = str(dfMyOrderList[0][6]).upper()
    A4 = str(" ")
    if OpenOrder == "BUY" :
        token = 'Wt5mRvYNrSlXbu5h0hBU2jZ89TnLu8hcG1M1ntf7TFQ'
        url = 'https://notify-api.line.me/api/notify'
        headers = {'content-type':'application/x-www-form-urlencoded','Authorization':'Bearer '+token}
        msg = "BOT SEND "+A1+A4+A2+A4+A3
        r = requests.post(url, headers=headers, data = {'message':msg})
        print (r.text)
    elif OpenOrder == "SELL" :
        token = 'Wt5mRvYNrSlXbu5h0hBU2jZ89TnLu8hcG1M1ntf7TFQ'
        url = 'https://notify-api.line.me/api/notify'
        headers = {'content-type':'application/x-www-form-urlencoded','Authorization':'Bearer '+token}
        msg = "BOT SEND "+A1+A4+A2+A4+A3
        r = requests.post(url, headers=headers, data = {'message':msg})
        print (r.text)
        '''


    # กรณีที่ใช้งาน SUB-ACCOUNT จะต้องกำหนดชื่อลงไปด้วย
    #exchange.headers = {
    #    'FTX-SUBACCOUNT': 'Eleph',
    #}

    #==============================================================================
    # ตรวจเช็คข้อมูล RECORD และบันทึกข้อมูลก่อน RUN BOT

    print("UPDATING THE RECORD PLEASE WAIT :)")
    getUpdateRecord()
    #getBackupRecord()
    #getbotLineStart()

    #==============================================================================
    # เริ่ม RUN BOT โดยการดึง FUNCTION ตามลำดับ


    for symbol in exchange.markets:

        Time = getTime()
        signal = getSignal()
        jsonPrice = getjsonPrice()
        getUpdateRecord()
        markUpExposure = getmarkUpExposure()
        OpenOrder = getOpenOrder()
    

        if OpenOrder == "BUY" or OpenOrder == "SELL" :
            getUpdateRecord()
            #getBackupRecord()
            dfMyOrderList = getUpdatePending()
    
    
        print("================================")
        time.sleep(30)
    
    #############################################################
    '''
    Phi = '314159265358979323846264338327950288419716939937510582097494459230781640628620899862803482534211706798214808651328238644709384'
    #Phix = Phi.replace(' ','')
    lenx = len(Phi)
    #print(Phix)
    #print(type(Phix))
    while d <= lenx:
        x = Phi[koi]
        print('koi = ',koi)
        
        #print('x = ' ,x)
        c= 60*int(x)
        print('Phi =', x)
        print('Time sleep = ', c)
        print("================================")
        #time.sleep(c)
        #koi = koi+1
        asd = 1
        temp_c = c / 60
        while asd <= temp_c :
            print('test = ',asd)
            print('price now =', getjsonPrice())
            time.sleep(60)
            asd = asd + 1
            print('================================')
            d = d+1
            koi = koi+1
            #print('koi + koi = ', koi)
            break

    
    getUpdateRecord()
    markUpExposure = getmarkUpExposure()
    sumExposure = getsumExposure()
    print(sumExposure)
    print('markup = {}'.format(markUpExposure[0]))
    print('smuEx = {}'.format(sumExposure[0]))
    print('totalsell = {}'.format(sumExposure[2]))
    print('totalBUY = {}'.format(sumExposure[1]))
    print('ALL = {}'.format(sumExposure[10]))
    print('max = {}'.format(maxExposure))
    print(markUpExposure)
    print(sumExposure)
'''

submit = Button(GUI,text='SUBMIT',command=RunProgram)
submit.pack()
E_path.bind('<Return>',RunProgram)

GUI.mainloop()