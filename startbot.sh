#!/bin/bash

SYMBOLS="AAPL,MSFT,TSLA,GOOG,FB,V,T,NIO,INTC,QCOM,BYND,SBUX,MA,AMD,GE,PG,NFLX,LLY,NVDA,CRM,DHR,LMT,NEE,PYPL"
python3 daybot.py --email True --symbol $SYMBOLS | tee console.log


