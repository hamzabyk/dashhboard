import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import yfinance as yf
import plotly.graph_objs as go
import pandas as pd
import numpy as np
import os

external_stylesheets = [dbc.themes.CYBORG]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

bist100_list = [
    ("ASELS", "Aselsan"), ("THYAO", "Türk Hava Yolları"), ("SISE", "Şişecam"), ("BIMAS", "BIM Mağazalar"),
    ("KRDMD", "Kardemir"), ("GARAN", "Garanti BBVA"), ("AKBNK", "Akbank"), ("FROTO", "Ford Otosan"),
    ("EREGL", "Ereğli Demir Çelik"), ("KCHOL", "Koç Holding"), ("ARCLK", "Arçelik"), ("TUPRS", "Tüpraş"),
    ("ISCTR", "İş Bankası"), ("VAKBN", "Vakıfbank"), ("YKBNK", "Yapı Kredi"), ("PGSUS", "Pegasus"),
    ("TCELL", "Turkcell"), ("TTRAK", "Türk Traktör"), ("SAHOL", "Sabancı Holding"), ("TAVHL", "TAV"),
    ("PETKM", "Petkim"), ("TOASO", "Tofaş"), ("HEKTS", "Hektaş"), ("SASA", "Sasa Polyester"),
    ("ALARK", "Alarko"), ("ENKAI", "Enka"), ("ODAS", "Odaş"), ("MGROS", "Migros"), ("KORDS", "Kordsa"),
    ("MAVI", "Mavi Giyim"), ("CCOLA", "Coca Cola"), ("HALKB", "Halkbank"), ("ZOREN", "Zorlu Enerji"),
    ("SELEC", "Selçuk Ecza"), ("SMRTG", "Smart Güneş"), ("GUBRF", "Gübre Fabrikaları"), ("KOZAL", "Koza Altın"),
    ("KOZAA", "Koza Anadolu"), ("AGHOL", "Anadolu Grubu"), ("AEFES", "Anadolu Efes"), ("DOAS", "Doğuş Otomotiv"),
    ("EKGYO", "Emlak Konut"), ("ENJSA", "Enerjisa"), ("BIOEN", "Biotrend"), ("ASTOR", "Astor Enerji"),
    ("VESBE", "Vestel Beyaz Eşya"), ("VESTL", "Vestel"), ("GWIND", "Galata Wind")
]

def fetch_data(symbol):
    try:
        data = yf.Ticker(symbol + ".IS").history(period="35d")
        if len(data) < 30:
            return None
        close = data['Close'][-1]
        prev = data['Close'][-2]
        change = ((close - prev) / prev) * 100
        volume = int(data['Volume'][-1])

        delta = data['Close'].diff()
        gain = delta.where(delta > 0, 0).rolling(14).mean()
        loss = -delta.where(delta < 0, 0).rolling(14).mean()
        rs = gain / loss
        rsi = round(100 - (100 / (1 + rs))[-1], 2)

        mini_fig = go.Figure(layout=dict(margin=dict(l=0, r=0, t=0, b=0), height=60))
        mini_fig.add_trace(go.Scatter(y=data['Close'][-30:], mode='lines', line=dict(color='lightblue', width=1)))
        mini_fig.update_xaxes(visible=False)
        mini_fig.update_yaxes(visible=False)

        return {
            "Fiyat": round(close, 2),
            "Değişim": round(change, 2),
            "Hacim": volume,
            "RSI": rsi,
            "Grafik": dcc.Graph(figure=mini_fig, config={"displayModeBar": False}, style={"height": "60px"})
        }
    except:
        return None

def create_card(symbol, name, data):
    return dbc.Card([
        dbc.CardBody([
            html.H5(f"{symbol} – {name}", className="text-white"),
            html.P(f"Fiyat: {data['Fiyat']} TL", className="text-muted small"),
            html.P(f"Değişim: {data['Değişim']}%", className="text-muted small"),
            html.P(f"Hacim: {data['Hacim']:,}", className="text-muted small"),
            html.P(f"RSI: {data['RSI']}", className="text-muted small"),
            data['Grafik']
        ])
    ], className="mb-3", style={"backgroundColor": "#1f1f1f"})

app.layout = dbc.Container([
    html.H3("📊 BIST 100 Hisse Dashboard", className="text-white my-4"),
    dbc.Button("Verileri Yükle", id="load-button", color="primary", className="mb-3"),
    html.Div(id="cards-container")
], fluid=True)

@app.callback(
    Output("cards-container", "children"),
    Input("load-button", "n_clicks")
)
def load_all_cards(n):
    if not n:
        return []
    cards = []
    for symbol, name in bist100_list:
        hisse = fetch_data(symbol)
        if hisse:
            cards.append(create_card(symbol, name, hisse))
    return cards

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8050))
    app.run(host="0.0.0.0", port=port)
