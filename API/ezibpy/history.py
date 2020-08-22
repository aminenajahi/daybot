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

data_ready = {}
def ibCallback(caller, msg, **kwargs):
        try:
            if caller == "handleHistoricalData":
                #print(caller)
                #print(msg)
                completed = kwargs.get('completed')
                #print("completed:%s" % completed)
                if completed == True:                   
                    #print(msg.reqId)
                    #print(ibConn.contracts[msg.reqId])
                    symbol = ibConn.contracts[msg.reqId].m_symbol
                    data_ready[symbol] = True

                    print("Historical data downloaded for %s" % symbol)                                    
        except:
            print("ERROR HANDLE CALLBACK")

# initialize ezIBpy
ibConn = ezibpy.ezIBpy()
ibConn.connect(clientId=100, host="localhost", port=4001)
ibConn.ibCallback = ibCallback
# create a contract
contract = ibConn.createStockContract("RCL")
print(contract)
print(ibConn.contracts)
print(contract.m_symbol)
data_ready[contract.m_symbol] = False

#2020-07-11 08:12:17,361 [ERROR] ezibpy: [#321] Error validating request:-'bS' : cause - Historical data bar size setting is invalid. Legal ones are: 1 secs, 5 secs, 10 secs, 15 secs, 30 secs, 1 min, 2 mins, 3 mins, 5 mins, 10 mins, 15 mins, 20 mins, 30 mins, 1 hour, 2 hours, 3 hours, 4 hours, 8 hours, 1 day, 1W, 1M
# request 30days of data
print("REQUEST MARKET DATA")
ibConn.requestMarketData(contract)

print("REQUEST HISTORICAL DATA")
ibConn.requestHistoricalData(contract, resolution="1 day", lookback="3 M", csv_path='./')

# wait until stopped using Ctrl-c
while data_ready[contract.m_symbol] == False:
    print("WAITING FOR %s TO COMPLETE" % contract.m_symbol)
    time.sleep(5)

print("CLEANUP")
ibConn.cancelHistoricalData(contract)
ibConn.disconnect()