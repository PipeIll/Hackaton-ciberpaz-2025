import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State
import pandas as pd
import folium
import os
Datos = 'puntos_reciclaje.csv'
cordenadas = [4.65, -74.05] 
zoom  = 11
def cargar():
    if os.path.exists(Datos):
        return pd.read_csv(Datos)
    else:
        return pd.DataFrame({
            'Nombre': ['ejmeplo'],
            'Latitud': [4.6521],
            'Longitud': [-74.0636],
            'Tipo': ['Como no funcione la base de datos los mato a lo bien'],
            'Detalle': ['juan-mamawebo.']
        })
df_puntos = cargar()
def mapa_bogoyork(df):
    m = folium.Map(
        location=cordenadas, 
        zoom_start=zoom,
        tiles="cartodbdarkmatter"
    )
    for index, row in df.iterrows():
        html_popup = f"""
            <h4>♻️ {row['Nombre']}</h4>
            <p><strong>Tipo:</strong> {row['Tipo']}</p>
            <p>{row['Detalle']}</p>
        """
        iframe = folium.IFrame(html_popup, width=250, height=100)
        popup = folium.Popup(iframe, max_width=300)
        icon = folium.Icon(color="green", icon="recycle", prefix="fa") 
        folium.Marker(
            location=[row['Latitud'], row['Longitud']],
            popup=popup,
            tooltip=row['Nombre'],
            icon=icon
        ).add_to(m)
    m.save("temp_map.html")
    return m._repr_html_()
app = dash.Dash(__name__, external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css'])
map_html = html.Iframe(
    id='map-iframe',
    srcDoc=mapa_bogoyork(df_puntos),
    style={'width': '100%', 'height': '600px', 'border': 'none'}
)
app.layout = html.Div(style={'backgroundColor': '#f5f5f5'}, children=[  
    html.Div(className='row', style={'padding': '20px', 'backgroundColor': '#008080', 'color': 'white'}, children=[
        html.H1("Puntos de Reciclaje Bogota", style={'textAlign': 'center'}),
        html.H3("Agrega puntos de Reciclaje", style={'textAlign': 'center'}),
    ]),
    html.Div(className='row', style={'margin': '20px'}, children=[  
        html.Div(className='six columns', children=[
            html.H4("Ubicaciones Actuales", style={'color': '#008080'}),
            map_html,
        ]),
        html.Div(className='six columns', children=[
            html.H4("Agregar Nuevo Punto", style={'color': '#008080'}),
            html.Div([
                dcc.Input(id='input-nombre', type='text', placeholder='Nombre del lugar', style={'width': '100%', 'margin-bottom': '10px'}),
                dcc.Input(id='input-latitud', type='number', placeholder='Latitud', style={'width': '49%', 'margin-right': '2%', 'margin-bottom': '10px'}),
                dcc.Input(id='input-longitud', type='number', placeholder='Longitud', style={'width': '49%', 'margin-bottom': '10px'}),
                dcc.Input(id='input-tipo', type='text', placeholder='Tipo de lugar', style={'width': '100%', 'margin-bottom': '10px'}),
                dcc.Textarea(id='input-detalle', placeholder='Detalles', style={'width': '100%', 'margin-bottom': '10px'}),
                html.Button('Guardar Punto', id='submit-button', n_clicks=0, style={'backgroundColor': '#3CB371', 'color': 'white', 'border': 'none', 'padding': '10px 20px', 'cursor': 'pointer'}),
                html.Div(id='output-message', style={'margin-top': '10px', 'color': 'green'}),
            ], style={'padding': '10px', 'border': '1px solid #ddd', 'border-radius': '5px'}),
            html.Hr(),            
            html.H4("Puntos Reciclaje", style={'color': '#008080', 'margin-top': '20px'}),
            html.Div(id='table-container')
        ])
    ])
])
def tabla(dataframe, max_rows=10):
    return html.Table([
        html.Thead(
            html.Tr([html.Th(col) for col in dataframe.columns])
        ),
        html.Tbody([
            html.Tr([
                html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
            ]) for i in range(min(len(dataframe), max_rows))
        ])
    ], style={'border-collapse': 'collapse', 'width': '100%'})
@app.callback(
    [Output('map-iframe', 'srcDoc'),
     Output('output-message', 'children'),
     Output('table-container', 'children')],
    [Input('submit-button', 'n_clicks')],
    [State('input-nombre', 'value'),
     State('input-latitud', 'value'),
     State('input-longitud', 'value'),
     State('input-tipo', 'value'),
     State('input-detalle', 'value')]
)
def ctutablaa(n_clicks, nombre, latitud, longitud, tipo, detalle):   
    PuntosInic = cargar()    
    if n_clicks is None or n_clicks == 0:
        return mapa_bogoyork(PuntosInic), "", tabla(PuntosInic)
    if nombre and latitud is not None and longitud is not None:
        nuevo_punto = pd.DataFrame({
            'Nombre': [nombre],
            'Latitud': [latitud],
            'Longitud': [longitud],
            'Tipo': [tipo if tipo else 'Desconocido'],
            'Detalle': [detalle if detalle else 'Sin detalles']
        })        
        PuntosInic = pd.concat([PuntosInic, nuevo_punto], ignore_index=True)
        PuntosInic.to_csv(Datos, index=False)        
        new_map_src = mapa_bogoyork(PuntosInic)        
        mensj = f"Punto '{nombre}' agregado y guardado."
        return new_map_src, mensj, tabla(PuntosInic)    
    return mapa_bogoyork(PuntosInic), "Error: Debe ingresar el Nombre, Latitud y Longitud.", tabla(PuntosInic)
if __name__ == '__main__':
    print("De milagro corre esto y si esta en blanco pues juan habra tocado algo http://127.0.0.1:8050/.")
    app.run(debug=False)
