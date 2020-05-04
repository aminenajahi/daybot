from finviz.screener import Screener

class FinvizScreener(object):

    def __init__(self):
        print("Create Finviz Screener")

    def top_N_biggest(self, N, table=None, stock_list=None):
        filters = ['geo_usa', 'cap_largeover', 'sh_avgvol_o1000']
        if stock_list is None:
            stock_list = Screener(filters=filters, order='-marketcap', rows=N, table=table)
        else:
            stock_list = Screener(tickers=stock_list, order='-marketcap', rows=N, table=table)
        print(stock_list)
        return stock_list

    def top_N_gainer(self, N, table=None, stock_list=None):
        filters = ['geo_usa', 'cap_largeover',  'sh_avgvol_o1000']
        if stock_list is None:
            stock_list = Screener(filters=filters, order='-change', rows=N, table=table)
        else:
            stock_list = Screener(tickers=stock_list, order='-change', rows=N, table=table)
        print(stock_list)
        return stock_list

    def top_N_looser(self, N, table=None, stock_list=None):
        filters = ['geo_usa', 'cap_largeover',  'sh_avgvol_o1000']
        if stock_list is None:
            stock_list = Screener(filters=filters, order='change', rows=N, table=table)
        else:
            stock_list = Screener(tickers=stock_list, order='change', rows=N, table=table)
        print(stock_list)
        return stock_list

    def top_N_high_volume(self, N, table=None, stock_list=None):
        filters = ['geo_usa', 'cap_largeover',  'sh_avgvol_o1000']
        if stock_list is None:
            stock_list = Screener(filters=filters, order='-Volume', rows=N, table=table)
        else:
            stock_list = Screener(tickers=stock_list, order='-Volume', rows=N, table=table)
        print(stock_list)
        return stock_list

    def top_N_bouce_back(self, N, table=None, stock_list=None):
        filters = ['geo_usa', 'cap_largeover',  'sh_avgvol_o1000', 'ta_highlow52w_b30h']
        if stock_list is None:
            stock_list = Screener(filters=filters, order='change', rows=N, table=table)
        else:
            stock_list = Screener(tickers=stock_list, order='change', rows=N, table=table)
        print(stock_list)
        return stock_list

    def top_N_tanking(self, N, table=None, stock_list=None):
        filters = ['geo_usa', 'cap_largeover',  'sh_avgvol_o1000', 'ta_highlow50d_b30h', 'ta_highlow52w_b30h']
        if stock_list is None:
            stock_list = Screener(filters=filters, order='change', rows=N, table=table)
        else:
            stock_list = Screener(tickers=stock_list, order='change', rows=N, table=table)
        print(stock_list)
        return stock_list

    def top_N_volatility(self, N, table=None, stock_list=None):
        filters = ['geo_usa', 'cap_largeover',  'sh_avgvol_o1000']
        if stock_list is None:
            stock_list = Screener(filters=filters, order='-volatility1w', rows=N, table=table)
        else:
            stock_list = Screener(tickers=stock_list, order='-volatility1w', rows=N, table=table)
        print(stock_list)
        return stock_list