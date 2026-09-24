import _heapq
from collections import deque
from entorno import obtener_vecinos_validos, calcular_costo,  actualizar_tabla_reservas, iniciar_entorno, propagar_fuego, obtener_agentes_del_piso

def UCS(mapa, posicion_inicial,tabla_reservas):
    #  cola de prioridad como una lista de (costo, posicion de todos los agentes, secuencia de estados)
    pq = []
    ruta_inicial = [posicion_inicial]
    # se transforma en una PQ como tal
    _heapq.heapify(pq)
    # agregamos la posicion inicial con costo acumulado 0
    _heapq.heappush(pq,(0,posicion_inicial, ruta_inicial))
    # diccionario para guardar el menor costo a una posicion determinada
    costos_minimos = {}
    costos_minimos[posicion_inicial] = 0
    # mientras la pq no esté vacía
    while(pq):
        # sacamos la posicion de todos los agentes
        costo,posicion,ruta = _heapq.heappop(pq)
        # si está en la salida, devolvemos la ruta con la que llegó
        if mapa[posicion] == 3:
            return ruta
        # si es peor que un costo ya encontrado la ignoramos
        if(costo > costos_minimos[posicion]):
            continue

        # obtenemos todas los movimientos validos
        expansion = obtener_vecinos_validos(mapa,posicion)
        for nuevo_estado in expansion:
            # casteamos a tupla
            nuevo_estado = tuple(nuevo_estado)
            # calculamos la congestion en el mapa del posible estado
            costo_paso = calcular_costo(nuevo_estado, len(ruta),tabla_reservas)
            costo_nuevo = costo_paso + costo # costo hacia la nueva pos + acumulado
            # si no hemos visitado la posicion o encontramos un camino mejor hacia esa posicion, actualizamos el diccionario
            # y lo insertamos a la pq para visitar esta nueva posicion
            if(nuevo_estado not in costos_minimos or costo_nuevo<costos_minimos[nuevo_estado] ):
                #acualizamos nuestra tupla de posiciones de agentes repitiendo la posicion por el costo
                # ej. si el costo es 3 agregamos 2 tuplas extras
                
                turnos_retraso = [posicion] * (costo - 1)
                nueva_ruta = ruta + turnos_retraso + [nuevo_estado]
                costos_minimos[nuevo_estado] = costo_nuevo

                _heapq.heappush(pq,(costo_nuevo,nuevo_estado, nueva_ruta))
    # si no encuentra la salida retorna una lista vacia  
    return []    



def DFS(mapa, posicicion_inical, tabla_reservas):
    stack = deque()
    visitados = set()
    ruta_inicial = [posicicion_inical]
    stack.append((posicicion_inical, ruta_inicial))

    while(stack):
        pos_actual, ruta = stack.pop()
        if(mapa[pos_actual] == 3):
            return ruta
        
        if(pos_actual not in visitados):
            visitados.add(pos_actual)
            for pos_valida in obtener_vecinos_validos(mapa,pos_actual):
                # usamos el costo no para elegir un camino, sino para contar los retrasos
                costo_paso = calcular_costo(pos_valida, len(ruta), tabla_reservas)
                retrasos = [pos_actual] * (costo_paso - 1)
                stack.append((pos_valida, ruta + retrasos + [pos_valida]))
    return []

def correr_algoritmo(eleccion_mapa,num_pisos,cantidad_agentes,k_fuego, algoritmo):
    mapa_edificio,posiciones_globales,posicion_fuego = iniciar_entorno(eleccion_mapa,num_pisos,cantidad_agentes)
    k = k_fuego # cada k turnos avanza el fuego
    turno_actual = 0
    sobrevivientes_totales = 0

    # Diccionario para agrupar las rutas individuales separadas por piso
    rutas_por_piso = {piso: {} for piso in range(mapa_edificio.shape[0])} 

    print("Iniciando evacuación del edificio")
    
    while len(posiciones_globales) > 0:
        turno_actual += 1
        print(mapa_edificio)
        print(f"posciones agentes {posiciones_globales}")
        
        # Propagacion fuego
        if turno_actual % k == 0:
            mapa_edificio, posiciones_globales, posicion_fuego = propagar_fuego(
                mapa_edificio, posiciones_globales, posicion_fuego
            )
            # Como el fuego altera la estrucutura, se recalculan los caminos, por ende borramos los calculados anteriormente
            rutas_por_piso = {piso: {} for piso in range(mapa_edificio.shape[0])}
            
        if len(posiciones_globales) == 0:
            print("todos murieron")
            break
            
        # Planificacion por cada piso
        nuevas_posiciones_globales = []
        
        for piso_actual in range(mapa_edificio.shape[0]):
            agentes_2d = obtener_agentes_del_piso(posiciones_globales, piso_actual)
            
            if not agentes_2d:
                continue 
                
            mapa_2d = mapa_edificio[piso_actual]
            
            # si ya llegaron todos (los que estan vivos) a la salida, contamos y continua otro piso
            if all(mapa_2d[agente] == 3 for agente in agentes_2d):
                sobrevivientes_totales += len(agentes_2d)
                continue 
                
            # si se destruyeron las rutas existentes por el avance del fuego se recalcula
            if not rutas_por_piso[piso_actual]:
                tabla_reservas = {}
                for i, pos_agente in enumerate(agentes_2d):
                    ruta = algoritmo(mapa_2d,pos_agente,tabla_reservas)
                    rutas_por_piso[piso_actual][i] = ruta # asignamos la ruta encontrada al agente i
                    # si se encontró una ruta, actualizamos la tabla de reservas
                    if(ruta):
                        tabla_reservas = actualizar_tabla_reservas(tabla_reservas,ruta)
            # simulamos el movimiento            
            for i, pos_agente in enumerate(agentes_2d):
                ruta_actual = rutas_por_piso[piso_actual].get(i,[]) # dado el piso, obtenemos la ruta del agente i
                # si no se encontró un camino, es porque quedo atrapado

                # si tenemos una ruta que no es la salida (len(ruta)>1), guardamos las siguientes posiciones 
                if(len(ruta_actual) > 1):
                    siguiente_posicion = ruta_actual[1]
                    rutas_por_piso[piso_actual][i] = ruta_actual[1:] # la ruta del agente i en el piso actual guarda los siguientes pasos
                # si contiene un solo elemento, es la salida    
                elif (len(ruta_actual) == 1):
                    siguiente_posicion = ruta_actual[0]
                # si la lista es vacia, es porque ya no tiene un camino a la salida (quedó atrapado por el fuego)
                else:
                    siguiente_posicion = pos_agente
                nuevas_posiciones_globales.append( (piso_actual, siguiente_posicion[0], siguiente_posicion[1]) ) # agregamos la posicion
                
        posiciones_globales = tuple(nuevas_posiciones_globales)

    print(f"Evacuación finalizada en {turno_actual} turnos. Sobrevivientes: {sobrevivientes_totales}")


