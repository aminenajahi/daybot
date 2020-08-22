#!/bin/bash

#run this script every morning.
PROD_KEY="2XX277IOADP39LCC"
SYMBOLS="AAPL,MSFT,AMZN,GOOG,GOOGL,FB,BABA,JPM,JNJ,MA,WMT,PG,BAC,TSM,TSLA,V,T,TBB,TBC,UNH,M,HD,DIS,KO,VZ,NVS,MRK,PFE,CVX,CSCO"
YESTERDAY="`date +%Y-%m-%d`"

python3 RunBot.py --key $PROD_KEY --email True --watchlist $SYMBOLS --botname MMBot --daily True --backtest True --since $YESTERDAY| tee console.log

