import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State
import pandas as pd
import folium

BOGOTA_COORDS = [4.65, -74.05] 
MAP_ZOOM = 11
df_puntos = pd.DataFrame({
    'Nombre': ['Punto de Recolección Principal'],
    'Latitud': [4.6521],
    'Longitud': [-74.0636],
    'Tipo': ['Centro Procesamiento'],
    'Detalle': ['Direccion Kra juan-mamawebo.']
})

def create_folium_map(df):
    m = folium.Map(
        location=BOGOTA_COORDS, 
        zoom_start=MAP_ZOOM,
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
    srcDoc=create_folium_map(df_puntos),
    style={'width': '100%', 'height': '600px', 'border': 'none'}
)

app.layout = html.Div(style={'backgroundColor': '#f5f5f5'}, children=[
    
    html.Div(className='row', style={'padding': '20px', 'backgroundColor': '#008080', 'color': 'white'}, children=[
        html.H1("Puntos de Reciclaje Bogota", style={'textAlign': 'center'}),
        html.H3("Localiza y agrega puntos de Reciclaje", style={'textAlign': 'center'}),
    ]),

    html.Div(className='row', style={'margin': '20px'}, children=[
        
        html.Div(className='six columns', children=[
            html.H4("📍 Ubicaciones Actuales", style={'color': '#008080'}),
            map_html,
        ]),
        
        html.Div(className='six columns', children=[
            html.H4("➕ Agregar Nuevo Punto", style={'color': '#008080'}),
            html.Div([
                dcc.Input(id='input-nombre', type='text', placeholder='Nombre del Punto (Ej: CC Andino)', style={'width': '100%', 'margin-bottom': '10px'}),
                dcc.Input(id='input-latitud', type='number', placeholder='Latitud (Ej: 4.6521)', style={'width': '49%', 'margin-right': '2%', 'margin-bottom': '10px'}),
                dcc.Input(id='input-longitud', type='number', placeholder='Longitud (Ej: -74.0636)', style={'width': '49%', 'margin-bottom': '10px'}),
                dcc.Input(id='input-tipo', type='text', placeholder='Tipo (Ej: Oficina/Centro Comercial)', style={'width': '100%', 'margin-bottom': '10px'}),
                dcc.Textarea(id='input-detalle', placeholder='Detalles y Horarios (Ej: Piso 1, 8am-5pm)', style={'width': '100%', 'margin-bottom': '10px'}),
                
                html.Button('Guardar Punto', id='submit-button', n_clicks=0, style={'backgroundColor': '#3CB371', 'color': 'white', 'border': 'none', 'padding': '10px 20px', 'cursor': 'pointer'}),
                html.Div(id='output-message', style={'margin-top': '10px', 'color': 'green'}),
            ], style={'padding': '10px', 'border': '1px solid #ddd', 'border-radius': '5px'}),

            html.Hr(),
            
            html.H4("📜 Puntos Agregados (Tabla)", style={'color': '#008080', 'margin-top': '20px'}),
            html.Div(id='table-container')
        ])
    ])
])

def generate_table(dataframe, max_rows=10):
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
def update_map_and_table(n_clicks, nombre, latitud, longitud, tipo, detalle):
    global df_puntos
    
    if n_clicks is None or n_clicks == 0:
        return create_folium_map(df_puntos), "", generate_table(df_puntos)

    if nombre and latitud is not None and longitud is not None:
        nuevo_punto = pd.DataFrame({
            'Nombre': [nombre],
            'Latitud': [latitud],
            'Longitud': [longitud],
            'Tipo': [tipo if tipo else 'Desconocido'],
            'Detalle': [detalle if detalle else 'Sin detalles']
        })
        
        df_puntos = pd.concat([df_puntos, nuevo_punto], ignore_index=True)
        new_map_src = create_folium_map(df_puntos)
        
        message = f"✅ Punto '{nombre}' agregado correctamente."
        return new_map_src, message, generate_table(df_puntos)
    
    return create_folium_map(df_puntos), "❌ Error: Debe ingresar el Nombre, Latitud y Longitud.", generate_table(df_puntos)

if __name__ == '__main__':
    print("App corriendo. Abre http://127.0.0.1:8050/ en tu navegador.")
    app.run(debug=False)
