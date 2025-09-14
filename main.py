import requests
import datetime
import time
from telegram import Bot
import asyncio

symbols = ["BTCUSDT", "SOLUSDT", "XRPUSDT"]
urlApi = "https://api.binance.com/api/v3/ticker/price"

precios_anteriores = {}

# Configuración de Telegram
bot_token = "8398438764:AAENEaFJfb6lBZxhymwYJq3YqRL0dJwb9bE"
chatID = "@criptomonedasreto"

def get_crypto_precio():
    precios = {}
    for symbol in symbols:
        response = requests.get(urlApi, params={"symbol": symbol})
        if response.status_code == 200:
            data = response.json()
            precios[symbol] = float(data["price"])
        else: 
            precios[symbol] = None
    return precios

def get_usdt_to_cop():
    """Obtiene la tasa USDT → COP directamente de Binance"""
    response = requests.get(urlApi, params={"symbol": "USDTCOP"})
    if response.status_code == 200:
        data = response.json()
        return float(data["price"])
    else:
        return None

async def enviar_telegram_mensaje(mensaje):
    bot = Bot(token=bot_token)
    await bot.send_message(chat_id=chatID, text=mensaje)

if __name__ == "__main__":
    while True:
        precios = get_crypto_precio()
        tasa_cop = get_usdt_to_cop()

        print(f"\nConsulta realizada: {datetime.datetime.now()}")

        if tasa_cop is None:
            print("⚠️ Error al obtener tasa USDT → COP")
            time.sleep(10)
            continue
        
        for symbol, precio_actual in precios.items():
            if precio_actual:
                # convertir a COP
                precio_cop = precio_actual * tasa_cop

                if symbol in precios_anteriores and precios_anteriores[symbol]:
                    precio_anterior = precios_anteriores[symbol]
                    variacion = ((precio_actual - precio_anterior) / precio_anterior) * 100

                    if variacion > 0.5:
                        tendencia = "Sube 📈"
                    elif variacion < -0.5:
                        tendencia = "Baja 📉"
                    else: 
                        tendencia = "Estable ➡️"

                    mensaje = (
                        f"{symbol}: {precio_actual:.2f} USDT "
                        f"({precio_cop:,.0f} COP) | "
                        f"Variación: {variacion:.2f}% | {tendencia}"
                    )
                    print(mensaje)

                    # Enviar alerta a Telegram
                    asyncio.run(enviar_telegram_mensaje(mensaje))

                else:
                    print(f"{symbol}: {precio_actual:.2f} USDT ({precio_cop:,.0f} COP) | Sin datos previos")

                precios_anteriores[symbol] = precio_actual
            else:
                print(f"{symbol}: Error al obtener precio")

        time.sleep(5)  # espera antes de volver a consultar