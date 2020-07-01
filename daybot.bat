cd C:\Users\workstation\Desktop\daybot
taskkill /F /IM python.exe
python.exe RunBot.py --finviz 10 --watchlist AAPL,MSFT,AMZN,GOOG,GOOGL,FB,BABA,JPM,JNJ,MA,WMT,PG,BAC,TSM,TSLA,V,T,TBB,UNH,M,HD,DIS,KO,VZ,MRK,CVX,CSCO,NVDA,AMD,WFC,BA,AAL,OXY,GE,UBER,BYND,PSX,QSR,SPG,DD,HLT,MAR,MRNA,SBUX,MA,V,T,INT,DIS,MS,GIS,SQ,GM --liquidate True --period 5 --botname MMBot --ibk True --email True --quota 2000 --budget 50000
