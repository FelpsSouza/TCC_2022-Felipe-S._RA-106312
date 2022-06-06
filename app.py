from email import message
from pyexpat.errors import messages
from pytz import timezone
import websocket
import json
from messages import *
import talib
import numpy
import config
from binance.client import Client
from binance.enums import *
from colorama import Style, Fore
import pandas as pd
from art import *
from datetime import datetime as dt

#==========================LINK DE STREAM WEBSOCKET==========================#

SOCKET = "wss://stream.binance.com:9443/ws/bnbbrl@kline_1m"

#=========================CONFIGURAÇÕES DOS INDICADORES=========================#

RSI_PERIOD = 14
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30


#MACD_FASTPERIOD = 12
#MACD_SLOWPERIOD = 26
#MACD_PERIOD = 9
#============================CONFIGURAÇÕES DA CORRETORA============================#

TRADE_SYMBOL = 'BNBBRL'  # Moedas a serem negociadas
TRADE_QUANTITY = 42  # Valor de moeda negociada
closes = []  # Armazenamento de fechamentos
in_position = False  # Valor de posição da vela

client = Client(config.api_key, config.api_secret)

#==============================================================================#


def order(side, quantity, symbol, order_type=ORDER_TYPE_MARKET):
    try:
        print("Enviando ordem: \n")
        order = client.create_order(
            symbol=symbol, side=side, type=order_type, quantity=quantity)
        print(order)
        print("VALOR: ")
        # REGISTRAR EM ARQUIVO OPERAÇÕES FEITAS
        # INFORMAR SE FOI UMA OPERAÇÃO DE LUCRO OU NÃO E INFORMAR QTD LUCRADA
    except Exception as error:
        print(
            Fore.RED + "##############################################################################################")
        print(f"Uma falha foi detectada - {error}")
        print("##############################################################################################" + Style.RESET_ALL)
        # inserir metodo que grave erro em um file
        # EXEMPLO:
        # [25/05/2022 - 14:35 - erro de conexão]
        return False
        # Se erro for igual a \/ \/ \/ \/
        # ('Connection aborted.', RemoteDisconnected('Remote end closed connection without response'))
        # tentar executar a venda novamente
    return True


def on_open(ws):
    # Passar para chamada de função através de classe
    print("\n\n\n#"+"=="*40 + "#")
    print(Fore.GREEN)
    tprint("Robo  Magnata")
    print(Style.RESET_ALL)
    print("#"+"=="*40 + "#\n")


def on_close(ws):
    print('Conexão Fechada')


def on_message(ws, message):
    global closes, in_position, stopLoss

    json_message = json.loads(message)

    candle = json_message['k']

    is_candle_closed = candle['x']
    close = candle['c']

    valorAtual = candle['c']
    moeda = candle['s']
    Timestamp = candle['t']
    tempo = pd.to_datetime(Timestamp, unit='ms')
    pTempo = tempo.strftime("Data:[%d/%m/%Y]\nHora: [%H:%M]\n")
    print(f"Valor negociado: {TRADE_QUANTITY}")

    print("##########[Moeda: " + Fore.BLUE +
          f"{moeda}" + Style.RESET_ALL + "]##########")

    print(f"Valor da moeda: {valorAtual}")
    print(pTempo)

    if is_candle_closed:
        print("#"*10)
        print(f"Vela fechada em {close}")
        closes.append(float(close))
        print("Fechamentos: ")
        print(closes)
        print(f"Qtd Fechamentos: {len(closes)}")

        if len(closes) > RSI_PERIOD:
            np_closes = numpy.array(closes)
            rsi = talib.RSI(np_closes, RSI_PERIOD)

            last_rsi = rsi[-1]

            print(Fore.BLUE +
                  f"Fechamento atual do RSI {last_rsi}" + Style.RESET_ALL)

            if last_rsi > RSI_OVERBOUGHT:
                if in_position:
                    print(Fore.MAGENTA + "Sobrecompra! VENDER! VENDER! VENDER!" +
                          Style.RESET_ALL)
                    print(
                        f"Foram vendidos {TRADE_QUANTITY} de {moeda} as {tempo}")

                    # [Inserir Lógica de VENDA Binance aqui]
                    order_succeeded = order(
                        SIDE_SELL, TRADE_QUANTITY, TRADE_SYMBOL)
                    if order_succeeded:
                        in_position = False
                        stopLoss = 0

                else:
                    print(
                        Fore.GREEN + "####################################################################")
                    print(
                        "Está sobrecomprado, mas não temos nada comprado. Nada a ser feito.")
                    print(
                        "####################################################################" + Style.RESET_ALL)

            if last_rsi < RSI_OVERSOLD:
                if in_position:
                    print(
                        Fore.YELLOW + "###############################################################")
                    print(
                        "Está sobrevendido, mas uma compra ja foi feita. Nada foi feito.")
                    print(
                        "###############################################################" + Style.RESET_ALL)
                else:
                    print(Fore.GREEN + "SOBRECOMPRA! COMPRAR! COMPRAR! COMPRAR!" +
                          Style.RESET_ALL)
                    print(
                        f"Foram comprados {TRADE_QUANTITY} de {moeda} as {tempo}")

                    # [Inserir Lógica de COMPRA Binance aqui]
                    order_succeeded = order(
                        SIDE_BUY, TRADE_QUANTITY, TRADE_SYMBOL)
                    if order_succeeded:
                        in_position = True
        else:
            print(
                "Faltam " + Fore.RED + f"{RSI_PERIOD - len(closes)}" + Style.RESET_ALL + " fechamentos para realizar a analise de RSI")

            if len(closes) == 0:
                print("RSI será analisado a partir do proximo fechamento")
#==============================================================================#


ws = websocket.WebSocketApp(SOCKET, on_open=on_open,
                            on_close=on_close, on_message=on_message)
ws.run_forever()
