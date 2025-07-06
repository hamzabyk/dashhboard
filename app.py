import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
from dash import dash_table
import yfinance as yf
import pandas as pd
import plotly.graph_objs as go
import plotly.express as px
import os

external_stylesheets = {
    'dark': dbc.themes.CYBORG,
    'light': dbc.themes.FLATLY
}

app = dash.Dash(__name__, external_stylesheets=[external_stylesheets['dark']], suppress_callback_exceptions=True)
server = app.server
app.title = "Kurumsal BIST 100 Dashboard"

app.layout = html.Div([
    dcc.Store(id="theme-store", data="dark"),

    # Tema geçiş düğmesi
    html.Div([
        dbc.Switch(id="theme-toggle", label="Koyu Tema", value=True,
                   className="form-check form-switch text-light")
    ], style={"position": "fixed", "top": "10px", "right": "20px", "zIndex": 9999}),

    # Mobil kart görünümü
    html.Div([
        html.H4("BIST 100 (Mobil Kart Görünümü)", className="text-light mt-4"),
        html.Div(id="mobile-cards-container")
    ], style={"display": "none"}, id="mobile-view-container"),

    # Görünmeyen tablo (mobil kartlara veri kaynağı sağlıyor)
    dash_table.DataTable(
        id='overview-table',
        columns=[
            {'name': 'Sembol', 'id': 'Sembol'},
            {'name': 'Şirket', 'id': 'Şirket'},
            {'name': 'Fiyat', 'id': 'Fiyat'},
            {'name': 'Değişim %', 'id': 'Değişim %'}
        ],
        data=[],  # Başlangıçta boş, ileride callback ile doldurulur
        style_table={'display': 'none'}
    )
])

# Tema toggle callback
@app.callback(
    Output("theme-store", "data"),
    Input("theme-toggle", "value")
)
def toggle_theme(value):
    return "dark" if value else "light"

# Mobil kart görünümü üretme
@app.callback(
    Output("mobile-cards-container", "children"),
    Input("overview-table", "data")
)
def render_mobile_cards(data):
    if not data:
        return []

    cards = []
    for row in data:
        cards.append(
            dbc.Card([
                dbc.CardBody([
                    html.H5(f"{row['Sembol']}", className="card-title"),
                    html.P(row['Şirket'], className="card-text small"),
                    html.P(f"Fiyat: {row['Fiyat']} TL", className="mb-1"),
                    html.P(f"Değişim: {float(row['Değişim %']):+.2f}%", className="mb-0")
                ])
            ], color="dark", outline=True, className="mb-3")
        )
    return cards

# Özel index_string ile responsive görünüm
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            @media (max-width: 768px) {
                #overview-table { display: none !important; }
                #mobile-view-container { display: block !important; }
            }
            @media (min-width: 769px) {
                #mobile-view-container { display: none !important; }
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8050))
    app.run(host="0.0.0.0", port=port, debug=False)




