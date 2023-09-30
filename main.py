from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
import pandas as pd

archivo_csv = ('c:/Users/nissi/OneDrive/Escritorio/PI MLOps - STEAM/Total.csv')
df = pd.read_csv(archivo_csv)

app = FastAPI()

@app.get("/AnioConMasHorasJugadas")
def PlayTimeGenre(genero: str):
    
    """
    Se obtiene el año de lanzamiento con más horas jugadas para un género dado.

    Argumento:
        genero (str): El género de los juegos (no es sensible a mayúsculas o minúsculas).

    Returns:
        dict: Un diccionario que contiene el año de lanzamiento con más horas jugadas.
              Ejemplo: {"Año de lanzamiento con más horas jugadas para [genero]": [año]}
    """
    
    # Convierto el género ingresado por el usuario a minúsculas para que lo encuentre
    genero = genero.lower()
    
    # Filtro el df por el género deseado (en minúsculas)
    df_genero = df[df['genres'].str.lower() == genero]
    
    # Verifico si hay o no registros
    if df_genero.empty:
        return {"Mensaje": "No se encontraron registros para el género especificado."}
    
    # Hago un agrupamiento por el release_date (año de lanz.) y que se sumen las horas jugadas para cada año
    gen_agrup = df_genero.groupby('release_year')['playtime_forever'].sum().reset_index()
    
    # Encuentro el año en el que mas tiempo se jugo
    max_year = gen_agrup.loc[gen_agrup['playtime_forever'].idxmax()]
    
    # Convierto playtime_forever de segundos a horas, con dos deciamles
    horas_jugadas = round(max_year['playtime_forever'] / 60 / 60, 2)
    
    # Le doy forma de diccionario al resultado
    resultado = {"Año de lanzamiento con más horas jugadas para " + genero.capitalize(): int(max_year['release_year'])}
    
    return resultado

genero_deseado = input("Ingrese el género: ")
res = PlayTimeGenre(genero_deseado)
print(res)


@app.get("/UsuarioConMasHorasJugadas")
def UserForGenre(genero: str):
    """
    Se obtiene el usuario con más horas jugadas y la acumulación de las mismas por año,
    para un género dado.

    Argumento:
        genero (str): El género de los juegos (no es sensible a mayúsculas o minúsculas).

    Returns:
        dict: Un diccionario que contiene el usuario con más horas jugadas y la acumulación
        de horas para cada año
              Ejemplo: {"Usuario con más horas jugadas para [genero]": [usuario]}
                        "Acumulación de horas jugadas por año para [genero]": [año: horas]
    """
    
    # Convierto lo ingresado a minúsculas
    genero = genero.lower()
    
    # Filtro el df por el género ingresado 
    df_genero = df[df['genres'].str.lower() == genero]
    
    # Verifico si se encontraron registros para el género
    if df_genero.empty:
        return {"Mensaje": "No se encontraron registros para el género especificado."}
    
    # Agrupo por usuario sumando las horas que ha jugado en ese género
    usuario_horas = df_genero.groupby('user_id')['playtime_forever'].sum().reset_index()
    
    # Encuentro el usuario que más horas jugó
    usuario_maximo = usuario_horas.loc[usuario_horas['playtime_forever'].idxmax()]
    
    # Agrupo por año de lanzamiento y a eso le sumo las horas que jugó en ese año y de ese género
    año_horas = df_genero.groupby('release_year')['playtime_forever'].sum().reset_index()
    
    # Renombrar las columnas para que tengan nombres más amigables
    año_horas.rename(columns={'release_year': 'año', 'playtime_forever': 'horas_jugadas'}, inplace=True)
    
    # Convertir playtime_forever de segundos a horas y redondear a dos decimales
    año_horas['horas_jugadas'] = round(año_horas['horas_jugadas'] / 60 / 60, 2)
    
    # Formatear el resultado como un diccionario
    result = {
        "Usuario con más horas jugadas para " + genero.capitalize(): usuario_maximo['user_id'],
        "Acumulación de horas jugadas por año para " + genero.capitalize(): año_horas.astype({'año': int}).to_dict(orient='records')
    }
    
    return result

genero = input("Ingrese el género: ")
resultado = UserForGenre(genero)
print(resultado)





@app.get("/MasRecomendados")
def UsersRecommend(anio: int):
    
    """
    Devuelve el top 3 de juegos MÁS recomendados por usuarios para el año dado

    Argumento:
        año (int)

    Returns:
        dict: Un diccionario que contiene los tres juegos mas recomendados y con mas reseñas positivas
        Ejemplo: {"Puesto 1": ['nombre de juego'], "Puesto 2": ['nombre de juego'],"Puesto 3": ['nombre de juego']
    
    """
    
    # Filtro el df por año
    df_year = df[df['release_year'] == anio]
    
    # Verifico si se encontraron registros
    if df_year.empty:
        return {"Mensaje": "No se encontraron registros para el año especificado."}
    
    # Filtro juegos recomendados 
    df_recommended = df_year[(df_year['recommend'] == True) & (df_year['sentiment_analysis'] >= 1)]
    
    # hago el conteo de recomendaciones por juego
    game_recommend_counts = df_recommended['item_name_x'].value_counts()
    
    # Tomo los 3 juegos más recomendados
    top_3_games = game_recommend_counts.head(3).reset_index()
    
    # Formateo el resultado como una lista de diccionarios
    result = [{"Puesto " + str(i + 1): juego} for i, juego in enumerate(top_3_games['item_name_x'])]
    
    return result

anio_deseado = int(input("Ingrese el año: "))
resultado = UsersRecommend(anio_deseado)
print(resultado)



@app.get("/MenosRecomendados")
def UsersNotRecommend(anio: int):
    
    """
    Devuelve el top 3 de juegos MENOS recomendados por usuarios para el año dado

    Argumento:
        año (int)

    Returns:
        dict: Un diccionario que contiene los tres juegos mENOS recomendados y con mas reseñas NEGATIVAS
        Ejemplo: {"Puesto 1": ['nombre de juego'], "Puesto 2": ['nombre de juego'],"Puesto 3": ['nombre de juego']
    
    """
    
    # Filtro el df por el año ingresado
    df_año = df[df['release_year'] == anio]
    
    # Verificar si se encontraron registros para el año
    if df_año.empty:
        return {"Mensaje": "No se encontraron registros para el año especificado."}
    
    # Filtrar juegos no recomendados (reviews.recommend = False y comentarios negativos)
    df_not_recommended = df_año[(df_año['recommend'] == False) & (df_año['sentiment_analysis'] == 0)]
    
    # Contar la cantidad de no recomendaciones por juego
    game_not_recommend_counts = df_not_recommended['item_name_x'].value_counts()
    
    # Tomar los 3 juegos menos recomendados
    top_3_not_recommended = game_not_recommend_counts.head(3).reset_index()
    
    # Formatear el resultado como una lista de diccionarios
    result = [{"Puesto " + str(i + 1): juego} for i, juego in enumerate(top_3_not_recommended['item_name_x'])]
    
    return result

anio_deseado = int(input("Ingrese el año: "))
resultado = UsersNotRecommend(anio_deseado)
print(resultado)

@app.get("/SentReseñas")
def sentiment_analysis(anio:int):
        
    """
    Según el año de lanzamiento, se devuelve una lista con la cantidad de registros de reseñas de 
    usuarios que se encuentren categorizados con un análisis de sentimiento.

    Argumento:
        año (int)

    Returns:
        dict: Un diccionario que contiene las tres categorias de reseñas y sus cantidades
        Ejemplo: {Negative = [cantidad_reseñas], Neutral = [cantidad_reseñas], Positive = [cantidad_reseñas]}
    
    """   
    
    # Filtrar el DataFrame por el año ingresado
    df_año = df[df['release_year'] == anio]
    
    # # Verificar si se encontraron registros para el año
    if df_año.empty:
        return {"Mensaje": "No se encontraron registros para el año especificado."}
    
    # # Contar la cantidad de registros para cada categoría de análisis de sentimiento
    sentiment_analysis_column = df_año['sentiment_analysis']
    sentiment = sentiment_analysis_column.value_counts().to_dict()

    # Crear un diccionario con los resultados
    result = {
        "Negative": sentiment.get(0, 0),
        "Neutral": sentiment.get(1, 0),
        "Positive": sentiment.get(2, 0)
    }
    
    return result

anio_deseado = int(input("Ingrese el año: "))
resultado = sentiment_analysis(anio_deseado)
print(resultado)
