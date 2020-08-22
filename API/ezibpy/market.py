#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# ezIBpy: a Pythonic Client for Interactive Brokers API
# https://github.com/ranaroussi/ezibpy
#
# Copyright 2015 Ran Aroussi
#
# Licensed under the GNU Lesser General Public License, v3.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.gnu.org/licenses/lgpl-3.0.en.html
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import ezibpy
import time

def ibCallback(caller, msg, **kwargs):
        print(caller)
        print(msg)
        #if caller == "handleTickGeneric":
        #    print("====Tick generic===")
        #    print(msg)
        #    print("====Tick generic===")

        #if caller == "handleTickPrice":
        #    print("====Tick price===")
        #    print(msg)
        #    print("====Tick price===")
        

# initialize ezIBpy
ibConn = ezibpy.ezIBpy()

# connect to IB (7496/7497 = TWS, 4001 = IBGateway)
ibConn.connect(clientId=111, host="localhost", port=4001)
ibConn.ibCallback = ibCallback

# create some contracts using dedicated methods
stk_contract0 = ibConn.createStockContract("AAPL")
stk_contract1 = ibConn.createStockContract("MSFT")
stk_contract2 = ibConn.createStockContract("TSLA")
stk_contract3 = ibConn.createStockContract("F")
stk_contract4 = ibConn.createStockContract("GE")
stk_contract5 = ibConn.createStockContract("F")
stk_contract6 = ibConn.createStockContract("QCOM")
stk_contract7 = ibConn.createStockContract("NFLX")
stk_contract8 = ibConn.createStockContract("GOOG")
stk_contract9 = ibConn.createStockContract("AMD")

# request market data for all created contracts
ibConn.requestRealTimeBars(rth=False)

# wait 30 seconds
while True:
    time.sleep(10)
    # print market data
    print("Market Data")
    print(ibConn.marketData)
    print("")

# cancel market data request & disconnect
ibConn.cancelMarketData()
ibConn.disconnect()