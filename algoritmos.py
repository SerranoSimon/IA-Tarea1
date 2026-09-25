import _heapq
from collections import deque
from entorno import obtener_vecinos_validos, calcular_costo,  actualizar_tabla_reservas, iniciar_entorno, propagar_fuego, obtener_agentes_del_piso

# Algoritmos de busqueda no informada
def UCS(mapa, posicion_inicial,tabla_reservas, limite_profundidad):
    #  cola de prioridad como una lista de (costo, posicion de todos los agentes, secuencia de estados)
    pq = []
    ruta_inicial = [posicion_inicial]
    # se transforma en una PQ como tal
    _heapq.heapify(pq)
    # agregamos la posicion inicial con costo acumulado 0
    _heapq.heappush(pq,(0,posicion_inicial, ruta_inicial))
    # diccionario para guardar el menor costo a una posicion determinada
    costos_minimos = {}
    estado_inicial_tiempo = (posicion_inicial[0], posicion_inicial[1], len(ruta_inicial))
    costos_minimos[estado_inicial_tiempo] = 0
    # mientras la pq no esté vacía
    while(pq):
        # sacamos la posicion de todos los agentes
        costo,posicion,ruta = _heapq.heappop(pq)
        # si está en la salida, devolvemos la ruta con la que llegó
        if mapa[posicion] == 3:
            return ruta

        estado_actual_e_t = (posicion[0], posicion[1], len(ruta))

        # si es peor que un costo ya encontrado la ignoramos
        if(costo > costos_minimos[estado_actual_e_t]):
            continue

        # obtenemos todas los movimientos validos
        expansion = obtener_vecinos_validos(mapa,posicion)
        for nuevo_estado in expansion:
            # casteamos a tupla
            nuevo_estado = tuple(nuevo_estado)
            # calculamos la congestion en el mapa del posible estado
            costo_paso = calcular_costo(nuevo_estado, len(ruta),tabla_reservas)

            turno_llegada = len(ruta) + costo_paso
            # podamos las ramas que superan el limite de profundidad
            if turno_llegada > limite_profundidad:
                continue
            costo_nuevo = costo_paso + costo # costo hacia la nueva pos + acumulado
            # si no hemos visitado la posicion o encontramos un camino mejor hacia esa posicion, actualizamos el diccionario
            # y lo insertamos a la pq para visitar esta nueva posicion
            estado_espacio_tiempo = (nuevo_estado[0], nuevo_estado[1], turno_llegada)
            if(estado_espacio_tiempo not in costos_minimos or costo_nuevo<costos_minimos[estado_espacio_tiempo] ):
                #acualizamos nuestra tupla de posiciones de agentes repitiendo la posicion por el costo
                # ej. si el costo es 3 agregamos 2 tuplas extras
                
                turnos_retraso = [posicion] * (costo_paso - 1)
                nueva_ruta = ruta + turnos_retraso + [nuevo_estado]
                costos_minimos[estado_espacio_tiempo] = costo_nuevo

                _heapq.heappush(pq,(costo_nuevo,nuevo_estado, nueva_ruta))
    # si no encuentra la salida retorna una lista vacia  
    return []    



def DFS(mapa, posicion_inicial, tabla_reservas, limite_profundidad):
    stack = deque()
    visitados = set()
    ruta_inicial = [posicion_inicial]
    # tupla de posicion y turno, representa estado-tiempo
    estado_inicial_e_t= (posicion_inicial[0], posicion_inicial[1], len(ruta_inicial))

    stack.append((estado_inicial_e_t, ruta_inicial))
    # los marcamos como visitados al entrar al stack para ahorrar RAM (evitamos repetir elementos)
    visitados.add(estado_inicial_e_t) 
    stack.append((estado_inicial_e_t, ruta_inicial))
    while(stack):
        estado_actual, ruta = stack.pop()
        pos_actual = (estado_actual[0], estado_actual[1])
        if(mapa[pos_actual] == 3):
            return ruta
        
        
        for pos_valida in obtener_vecinos_validos(mapa,pos_actual):
            # usamos el costo no para elegir un camino, sino para contar los retrasos
            costo_paso = calcular_costo(pos_valida, len(ruta), tabla_reservas)
            turno_llegada = len(ruta) + costo_paso

            if turno_llegada > limite_profundidad:
                continue

            estado_espacio_tiempo = (pos_valida[0], pos_valida[1], turno_llegada)

            if estado_espacio_tiempo not in visitados:
                retrasos = [pos_actual] * (costo_paso - 1)
                stack.append((pos_valida, ruta + retrasos + [pos_valida]))
                visitados.add(estado_espacio_tiempo)
            
    return []

def distancia_manhattan(a,b):
    """
    Heurística distancia manhattan del nodo 'a' respecto del nodo objetivo 'b'
    """
    return abs(b[0] - a[0]) + abs(b[1]-a[1])

# Algoritmos de busqueda informada
def A_star(mapa, posicion_inicial, posicion_objetivo, tabla_reservas, heuristica, limite_profundidad):
    #  cola de prioridad como una lista de (costo, posicion de todos los agentes, secuencia de estados)
    pq = []
    ruta_inicial = [posicion_inicial]
    # se transforma en una PQ como tal
    _heapq.heapify(pq)
    # las tuplas que guarda la PQ son del tipo (f, g, posicion, ruta)
    # agregamos la posicion inicial con el valor de la heuristica (f(pos_inicial) = h(pos_inicial) + 0)
    _heapq.heappush(pq,(heuristica(posicion_inicial, posicion_objetivo),0,posicion_inicial, ruta_inicial))
    # diccionario para guardar los costos
    g_tabla = {}
    estado_inicial_tiempo = (posicion_inicial[0], posicion_inicial[1], len(ruta_inicial))
    g_tabla[estado_inicial_tiempo] = 0
    # mientras la pq no esté vacía
    while(pq):
        # sacamos la posicion de todos los agentes
        f_valor, g_actual, posicion,ruta = _heapq.heappop(pq)

        estado_actual_tiempo = (posicion[0], posicion[1], len(ruta))

        # si el costo es mayor que el ultimo costo registrado, es una ruta que ignoraremos
        if g_actual > g_tabla[estado_actual_tiempo]:
            continue
        # si está en la salida, devolvemos la ruta con la que llegó
        if mapa[posicion] == 3:
            return ruta
       
        # obtenemos todas los movimientos validos
        expansion = obtener_vecinos_validos(mapa,posicion)
        for nuevo_estado in expansion:
            # casteamos a tupla
            nuevo_estado = tuple(nuevo_estado)
            # calculamos la congestion en el mapa del posible estado
            costo_paso = calcular_costo(nuevo_estado, len(ruta),tabla_reservas)
            costo_nuevo = costo_paso + g_actual # costo hacia la nueva pos + acumulado
            # usamos estado_espacio_tiempo para representar en qué turno se llegó a la posicion,
            # es util para no eliminar rutas futuras que tengan menos costo (los agentes se van moviendo).
            # ej. dos agentes en la misma casilla, es mejor que uno espere y luego avance.
            turno_llegada = len(ruta) + costo_paso

            if turno_llegada > limite_profundidad:
                continue

            estado_espacio_tiempo = (nuevo_estado[0], nuevo_estado[1], turno_llegada)

            # si no hemos visitado la posicion o encontramos un camino mejor hacia esa posicion, actualizamos el diccionario
            # y lo insertamos a la pq para visitar esta nueva posicion
            if(estado_espacio_tiempo not in g_tabla or costo_nuevo< g_tabla[estado_espacio_tiempo] ):
                #acualizamos nuestra tupla de posiciones de agentes repitiendo la posicion por el costo
                # ej. si el costo es 3 agregamos 2 tuplas extras
                
                turnos_retraso = [posicion] * (costo_paso - 1)
                nueva_ruta = ruta + turnos_retraso + [nuevo_estado]
                g_tabla[estado_espacio_tiempo] = costo_nuevo
                f_nuevo = heuristica(nuevo_estado,posicion_objetivo) + costo_nuevo
                _heapq.heappush(pq,(f_nuevo,costo_nuevo,nuevo_estado, nueva_ruta))
    # si no encuentra la salida retorna una lista vacia  
    return []    
    

    
def busqueda_Greedy(mapa, posicion_inicial, posicion_objetivo, tabla_reservas, heuristica, limite_profundidad):
    #  cola de prioridad como una lista de (costo, posicion de todos los agentes, secuencia de estados)
    pq = []
    ruta_inicial = [posicion_inicial]
    # se transforma en una PQ como tal
    _heapq.heapify(pq)
    # agregamos la posicion inicial con costo acumulado 0
    _heapq.heappush(pq,( heuristica(posicion_inicial, posicion_objetivo),posicion_inicial, ruta_inicial))

    visitados = set()
    #podemos marcar antes igual que en DFS, ya que dentro del mismo estado guardamos el costo  (turnos),
    # por ende si llegamos a la misma posicion pero en distintos turnos, es un estado diferente.

    estado_inicial_e_t = (posicion_inicial[0], posicion_inicial[1], len(ruta_inicial))
    visitados.add(estado_inicial_e_t)
    # mientras la pq no esté vacía
    while(pq):
        # sacamos la posicion de todos los agentes
        valor_h,posicion,ruta = _heapq.heappop(pq)
        # si está en la salida, devolvemos la ruta con la que llegó
        if mapa[posicion] == 3:
            return ruta

        if(posicion not in visitados):
            visitados.add(posicion)
            # obtenemos todas los movimientos validos
            expansion = obtener_vecinos_validos(mapa,posicion)
            for nuevo_estado in expansion:
                # casteamos a tupla
                nuevo_estado = tuple(nuevo_estado)
                # calculamos la congestion en el mapa del posible estado
                costo_paso = calcular_costo(nuevo_estado, len(ruta),tabla_reservas)

                turno_llegada = len(ruta) + costo_paso
                if turno_llegada > limite_profundidad:
                    continue

                estado_e_t = (nuevo_estado[0], nuevo_estado[1], turno_llegada)
                 
                if estado_inicial_e_t not in visitados:
                    # valor heurística
                    h = distancia_manhattan(nuevo_estado, posicion_objetivo)
                    # usamos el costo_paso solo para ver cuantos turnos de penalizacion se usan    
                    turnos_retraso = [posicion] * (costo_paso - 1)
                    nueva_ruta = ruta + turnos_retraso + [nuevo_estado]
                    _heapq.heappush(pq,(h,nuevo_estado, nueva_ruta))
    # si no encuentra la salida retorna una lista vacia  
    return []        

def genetico()
            
def correr_algoritmo_busqueda_no_informada(eleccion_mapa,num_pisos,cantidad_agentes,k_fuego, algoritmo, limite_profundidad):
    mapa_edificio,posiciones_globales,posicion_fuego = iniciar_entorno(eleccion_mapa,num_pisos,cantidad_agentes, False)
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
                    ruta = algoritmo(mapa_2d,pos_agente,tabla_reservas,limite_profundidad)
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
def correr_algoritmo_busqueda_informada(eleccion_mapa,num_pisos,cantidad_agentes,k_fuego, algoritmo, heuristica, limite_profundidad):
    mapa_edificio,posiciones_globales,posicion_fuego, posicion_objetivo = iniciar_entorno(eleccion_mapa,num_pisos,cantidad_agentes, True)
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
                    ruta = algoritmo(mapa_2d,pos_agente,posicion_objetivo, tabla_reservas, heuristica, limite_profundidad)
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


