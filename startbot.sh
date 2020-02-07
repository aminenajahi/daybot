#!/bin/bash

SYMBOLS="AAPL,MSFT,AMZN,GOOG,GOOGL,FB,BABA,JPM,JNJ,MA,WMT,PG,BAC,TSM,TSLA,V,T,TBB,TBC,UNH,M,HD,DIS,KO,VZ,NVS,MRK,PFE,CVX,CSCO"
python3 RunBot.py --email True --watchlist $SYMBOLS --botname MMBot | tee console.log

