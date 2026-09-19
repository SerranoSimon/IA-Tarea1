import numpy as np
# 0: libre
# 1: muro
# 2: fuego
# 3: salida


def obtener_vecinos_validos(mapa, posicion_actual):
    """
    Funcion que recibe un mapa de numpy y la posicion actual como tupla y devuelve una
    lista de tuplas que representan las celdas validas para desplazarse.
    """
    vecinos_validos = []
    r = posicion_actual[0]
    c = posicion_actual[1]
    movimientos_posibles = [(-1,0),(1,0), (0,-1), (0,1), (0,0)] # (0,0) es esperar
    for m in movimientos_posibles:
        nuevo_r =r + m[0]
        nuevo_c =c + m[1]
        # verificamos limites
        if( 0<= nuevo_r<mapa.shape[0] and 0<= nuevo_c < mapa.shape[1]):
            #verificamos que sean transitables o sea el objetivo
            if(mapa[nuevo_r][nuevo_c] in [0,3]):
                vecinos_validos.append((nuevo_r,nuevo_c))
    return vecinos_validos

def generar_posicion_fuego(mapa):
    coordenadas_libres = np.argwhere(mapa == 0)
    indice_aleatorio = np.random.randint(0, len(coordenadas_libres))
    celda_elegida = tuple(coordenadas_libres[indice_aleatorio])
    mapa[celda_elegida] = 2
    return mapa,celda_elegida

def generar_posicion_agentes(mapa, cantidad_agentes):
    # se buscan las celdas libres
    coordenadas_libres = np.argwhere(mapa == 0)
    if len(coordenadas_libres) == 0:
        raise ValueError("No hay casillas libres en el mapa.")
        
    # seleccionamos indices al azar, con replace=true permite que se repitan (asi tenemos congestion inicial)
    indices_aleatorios = np.random.choice(len(coordenadas_libres), size=cantidad_agentes, replace=True)
    
    # construimos la tupla de coordenadas
    posicion_agentes = tuple(tuple(coordenadas_libres[i]) for i in indices_aleatorios)
    return posicion_agentes


def iniciar_entorno(pisos_totales, cantidad_agentes):

    

    # 22 x 22
    #uno solo pasillo, unico camino a la salida
    piso_base = np.array([
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1],
        [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 0, 0, 0, 1],
        [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 0, 1],
        [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 0, 0, 0, 1],
        [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 0, 1],
        [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 0, 0, 1, 0, 1, 0, 1, 0, 0, 1],
        [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1],
        [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 0, 1],
        [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 0, 1],
        [1, 0, 1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 1, 0, 0, 1],
        [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 0, 1],
        [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 0, 1],
        [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 0, 1],
        [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 0, 1],
        [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 0, 1],
        [1, 0, 1, 0, 1, 0, 1, 0, 0, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 0, 1],
        [1, 0, 1, 0, 1, 0, 1, 0, 0, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 0, 1],
        [1, 0, 1, 0, 0, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 0, 1],
        [1, 0, 0, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1],
        [1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 3],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    ], dtype=np.int8)
   

    mapa = np.array([piso_base] * pisos_totales, dtype=np.int8) # es 3d al considerar los pisos
    mapa,celda_elegida = generar_posicion_fuego(mapa)
    celdas_fuego = {celda_elegida}
    posicion_agentes = generar_posicion_agentes(mapa,cantidad_agentes)
    return mapa, posicion_agentes,celdas_fuego

def calcular_congestion(posicion_agentes):
    """ Dado la tupla de posiciones de los agentes, llevamos un diccionario como contador
    de cuantos agentes hay en las posiciones ocupadas"""
    congestion = {}
    for pos in posicion_agentes:
        congestion[pos] = congestion.get(pos,0 ) + 1 # si no existe la clave inicia en 0 la cuenta
    return congestion

def calcular_costo(celda):
    """
    Calculamos el costo a una celda usando 2^(ocupantes) + 1
    """
    congestion = calcular_congestion
    ocupantes = congestion.get(celda,0) # 0 si no hay ningun agente en dicha celda
    costo = 2**(ocupantes) + 1 #costo exponencial
    return costo

def propagar_fuego(mapa,posicion_agentes,celdas_fuego):

    nuevas_celdas = set()
    movimientos = [(0,1),(1,0),(-1,0),(0,-1)]
    for fuego in celdas_fuego:
        for mov in movimientos:
            r = fuego[1] + mov[0]
            c = fuego[2] + mov[1]
            # revisamos que estemos dentro de los limites del mapa
            if(0 <= r < mapa.shape[1] and 0<= c< mapa.shape[2]):
                # si es un muro o fuego, saltamos a otra casilla
                if(mapa[fuego[0],r,c] in [1,2]):
                    continue
                # si es una escalera (salida del piso excepto piso 0), propagamos hacia otros pisos    
                if(mapa[fuego[0],r,c] == 3):
                    # si es el piso de arriba solo propaga hacia abajo
                    if(fuego[0] == mapa.shape[0] - 1):
                        mapa[mapa.shape[0] - 2, r,c] = 2
                        nuevas_celdas.add((mapa.shape[0] - 2,r,c))
                    # si es el primer piso, se propaga hacia arriba
                    elif(fuego[0] == 0):
                        mapa[1, r,c] = 2
                        nuevas_celdas.add((1,r,c))
                    # si es piso intermedio se progpaga hacia arriba y hacia abajo
                    else:
                        mapa[fuego[0] + 1, r, c] = 2
                        nuevas_celdas.add((fuego[0] + 1,r,c))
                        mapa[fuego[0] - 1, r, c] = 2
                        nuevas_celdas.add((fuego[0] - 1,r,c))
                # si es libre o la escalera, se propaga
                mapa[fuego[0],r,c]=2
                nuevas_celdas.add((fuego[0],r,c))
               
    # si nuevas_celdas no es vacío
    if nuevas_celdas:
        # quitamos los agentes que fueron alcanzados por el fuego
        nuevas_posicion_agentes = tuple(
            agente for agente in posicion_agentes if agente not in nuevas_celdas
        )
        
    else:
        nuevas_posicion_agentes = posicion_agentes
    celdas_fuego.update(nuevas_celdas)
    return mapa, nuevas_posicion_agentes,celdas_fuego
