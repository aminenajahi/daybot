#!/bin/bash

SYMBOLS="AAPL,MSFT,TSLA,GOOG,FB,V,T,NIO,INTC,QCOM"
python3 RunBot.py --email True --symbol $SYMBOLS | tee console.log


