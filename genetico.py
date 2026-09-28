from algoritmos import A_star,iniciar_entorno,propagar_fuego,actualizar_tabla_reservas, obtener_agentes_del_piso, distancia_manhattan
from itertools import permutations
import copy 
import random

def formar_individuos(num_agentes, tamano_poblacion):
    """
    Genera individuos al azar, donde cada individuo es una tupla es el orden en que cada agente ejecuta A*
    """
    agentes_ids = list(range(num_agentes))
    poblacion = []
    for i in range(tamano_poblacion):
        individuo = tuple(random.sample(agentes_ids, num_agentes))
        poblacion.append(individuo)
    return poblacion

def obtener_costo_individuo(orden_de_evacuacion, mapa_edificio_original, agentes_piso_2d, piso, posicion_objetivo, k_fuego, posicion_fuego_original, heuristica, limite_profundidad):    
   # clonamos el entorno para que los individuos no cambien el entorno global

    mapa_edificio = copy.deepcopy(mapa_edificio_original)
    posicion_fuego = copy.deepcopy(posicion_fuego_original)
    mapa_2d = mapa_edificio[piso] 
    
    # Usamos un diccionario para no perder la sincronizacion entre indice y posicion si uno muere
    # Ej: {0: (1, 1), 1: (5, 4), 2: (8, 8)}
    agentes_vivos = dict(agentes_piso_2d)
    total_agentes_inicial = len(agentes_vivos)
    
    k = k_fuego
    turno_actual = 0
    rutas = {}
    turno_ultimo_sobreviviente = 0
    sobrevivientes = 0
    while len(agentes_vivos) > 0:
        turno_actual += 1
        
        # propagacion fuego

        if turno_actual % k == 0:
            # convertimos los agentes 2d vivos a 3d para el fuego
            # usamos un diccionario para poder saber qué agente i muere
            posiciones_3d = {id_agente: (piso, pos[0], pos[1]) for id_agente, pos in agentes_vivos.items()}
            lista_3d = list(posiciones_3d.values())
            
        
            mapa_edificio, lista_3d_post_fuego, posicion_fuego = propagar_fuego(
                mapa_edificio, lista_3d, posicion_fuego
            )
            
            # actualizamos el mapa con los avances del fuego
            mapa_2d = mapa_edificio[piso]
            
            # buscamos qué agentes sobrevivieron
            agentes_vivos = {}
            for id_agente, pos_3d in posiciones_3d.items():
                if pos_3d in lista_3d_post_fuego:
                    agentes_vivos[id_agente] = (pos_3d[1], pos_3d[2])
                    
            # Rutas destruidas por el fuego, forzamos recalculo
            rutas = {} 
            
        if len(agentes_vivos) == 0:
            break # Todos murieron
            
        # calcular rutas de los agentes usando el individuo (el orden de evacuacion)
        if not rutas:
            tabla_reservas = {}
            for i in orden_de_evacuacion:
                # Si el agente i murió, lo saltamos
                if i not in agentes_vivos:
                    continue
                    
                pos_agente = agentes_vivos[i]
                ruta = A_star(mapa_2d, pos_agente, posicion_objetivo, tabla_reservas, heuristica, limite_profundidad)
                
                rutas[i] = ruta 
                
                if ruta:
                    tabla_reservas = actualizar_tabla_reservas(tabla_reservas, ruta)
                    
        # simulacion de A*

        llegaron_a_salida_este_turno = []
        
        for id_agente, pos_agente in list(agentes_vivos.items()):
            ruta_actual = rutas.get(id_agente, [])
            
            if len(ruta_actual) > 1:
                siguiente_posicion = ruta_actual[1]
                rutas[id_agente] = ruta_actual[1:] 
            elif len(ruta_actual) == 1:
                siguiente_posicion = ruta_actual[0]
            else:
                siguiente_posicion = pos_agente # Atrapado, se queda quieto
                
            agentes_vivos[id_agente] = siguiente_posicion
            
            # si llegó a la salida se agrega a la lista
            if mapa_2d[siguiente_posicion[0]][siguiente_posicion[1]] == 3:
                sobrevivientes+=1
                turno_ultimo_sobreviviente = turno_actual
                llegaron_a_salida_este_turno.append(id_agente)
                
        # retiramos a los que ya escaparon
        for id_agente in llegaron_a_salida_este_turno:
            del agentes_vivos[id_agente]
            if id_agente in rutas:
                del rutas[id_agente]

   # calculo de costo fitness
    muertos = total_agentes_inicial - sobrevivientes
    
    # penalizacion por muertos para garantizar salvar vidas en lugar de rutas rapidas
    penalizacion_muertes = muertos * 1000

    # calculo del ultimo en llegar a la meta, si nadie sobrevive priorizamos los que mas tiempo duraron vivos
    if(sobrevivientes == 0):
        turno_ultimo_sobreviviente = turno_actual
        costo_fitness =  penalizacion_muertes - turno_actual
    # si vive alguno, priorizamos la huida mas rapida    
    else:
        costo_fitness = turno_ultimo_sobreviviente + penalizacion_muertes
    
    return costo_fitness, sobrevivientes, turno_ultimo_sobreviviente

def torneo(poblacion_evaluada, k=3):
    # Selecciona k individuos al azar y devuelve el mejor individuo (menor costo)
    participantes = random.sample(poblacion_evaluada, k)
    ganador = min(participantes, key=lambda ind: ind[1])
    return ganador[0]

def rellenar_hijo(padre_1, padre_2, punto1,punto2, tamano):
        hijo = [None] * tamano
        # ponemos una seccion de los genes del padre 1 en el hijp
        hijo[punto1:punto2+1] = padre_1[punto1:punto2+1]
        
        # rellenamos el hijo con los genes del padre 2

        elementos_insertados = set(hijo[punto1:punto2+1])
        idx_relleno = 0
        for gen in padre_2:
            if gen not in elementos_insertados:
                # Saltar los espacios ya ocupados por la herencia del padre 1
                while punto1 <= idx_relleno <= punto2:
                    idx_relleno += 1
                hijo[idx_relleno] = gen
                idx_relleno += 1
        return tuple(hijo)

def cruce(padre1, padre2):
    tamano = len(padre1)
    if tamano <= 1: return padre1, padre2
    
    # Puntos de corte al azar
    punto1, punto2 = sorted(random.sample(range(tamano), 2))

    hijo1 = rellenar_hijo(padre1, padre2,punto1,punto2,tamano)
    hijo2 = rellenar_hijo(padre2, padre1,punto1,punto2,tamano)
    return hijo1, hijo2

def mutacion_swap(individuo, prob_mutacion=0.05):
    if random.random() > prob_mutacion or len(individuo) <= 1:
        return individuo
        
    cromosoma = list(individuo)
    idx1, idx2 = random.sample(range(len(cromosoma)), 2)
    # Intercambiamos genes, en nuestro caso cambiamos el orden de dos agentes
    cromosoma[idx1], cromosoma[idx2] = cromosoma[idx2], cromosoma[idx1]
    
    return tuple(cromosoma)

def algoritmo_genetico(num_agentes, tamano_poblacion, num_generaciones, 
                                mapa_edificio_original, agentes_piso_2d, piso, 
                                posicion_objetivo, k_fuego, posicion_fuego_original, 
                                heuristica, limite_profundidad):
    mejor_individuo_historico = None
    mejor_costo_historico = float('inf')
    mejor_sobrevivientes_historico = 0 # sobreviventes del mejor individuo
    mejor_turno_historico = float('inf') # turnos del mejor individuo
    
    poblacion = formar_individuos(num_agentes,tamano_poblacion)
    
        
    mejor_individuo_historico = None
    mejor_costo_historico = float('inf')
    
    #print(f"Iniciando AG: {num_generaciones} generaciones | Población: {tamano_poblacion}")

    # 2. El Bucle Evolutivo
    for generacion in range(num_generaciones):
        poblacion_evaluada = []
        todos_los_costos = []
        # A) Evaluación
        for individuo in poblacion:
            # Llamamos a tu función de simulación pesada
            costo_fitness, sob_indiv, turno_indiv = obtener_costo_individuo(
                individuo, mapa_edificio_original, agentes_piso_2d, piso, 
                posicion_objetivo, k_fuego, posicion_fuego_original, 
                heuristica, limite_profundidad
            )
            poblacion_evaluada.append((individuo, costo_fitness, sob_indiv, turno_indiv))
            todos_los_costos.append(costo_fitness)
            
        # Ordenamos de mejor (menor costo) a peor
        poblacion_evaluada.sort(key=lambda x: x[1])
        
        # B) Registro del mejor global
        mejor_actual, costo_actual, sob_actual, turno_escape = poblacion_evaluada[0]
        if costo_actual < mejor_costo_historico:
            mejor_individuo_historico = mejor_actual
            mejor_costo_historico = costo_actual
            mejor_sobrevivientes_historico = sob_actual
            mejor_turno_historico = turno_escape

        #print(f" todos los costos: {todos_los_costos}")        
        #print(f"Generación {generacion} | ind {individuo} |Muertos: {num_agentes - sob_actual} | sob : {sob_actual} | Turno escape: {turno_escape} | Mejor Costo Actual: {costo_actual}")
        #print(f"Mejor Global: {mejor_individuo_historico} con costo {mejor_costo_historico}")

        # Si llegamos a la última generación, no necesitamos crear otra
        if generacion == num_generaciones - 1:
            break

        # C) Selección y Reproducción
        nueva_generacion = []
        
        # Elitismo: Los 2 mejores pasan intactos a la siguiente ronda
        nueva_generacion.append(poblacion_evaluada[0][0])
        nueva_generacion.append(poblacion_evaluada[1][0])
        
        # Cruces para rellenar los cupos faltantes
        cupos_faltantes = tamano_poblacion - 2
        
        # Como cada cruce da 2 hijos, iteramos cupos_faltantes / 2 veces
        for i in range(cupos_faltantes // 2):
            padre1 = torneo(poblacion_evaluada, k=3)
            padre2 = torneo(poblacion_evaluada, k=3)
            
            hijo1, hijo2 = cruce(padre1, padre2)
            
            hijo1 = mutacion_swap(hijo1, prob_mutacion=0.05)
            hijo2 = mutacion_swap(hijo2, prob_mutacion=0.05)
            
            nueva_generacion.extend([hijo1, hijo2])
            
        # Reemplazamos la vieja población por la nueva
        poblacion = nueva_generacion

    # Fin de la evolución
    #print("\n--- Evolución Finalizada ---")
    #print(f"Orden de Evacuación Óptimo: {mejor_individuo_historico}")
    #print(f"Costo Mínimo Logrado: {mejor_costo_historico}")
    
    return mejor_turno_historico, mejor_sobrevivientes_historico, mejor_individuo_historico

def correr_algoritmo_genetico(eleccion_mapa, num_pisos, cantidad_agentes, tamano_poblacion, num_generaciones, 
                                 k_fuego, 
                                 limite_profundidad):
    mapa_edificio,tupla_posiciones,posicion_fuego, posicion_objetivo = iniciar_entorno(eleccion_mapa,num_pisos,cantidad_agentes, True)
    
    posiciones_globales = {i: pos for i, pos in enumerate(tupla_posiciones)}
    sobrevivientes_totales = 0
    ultimos_turnos = []
   
      
    for piso in range(num_pisos):

        agentes_2d = [(id_ag, (pos[1], pos[2])) 
                          for id_ag, pos in posiciones_globales.items() 
                          if pos[0] == piso]
            
        if not agentes_2d:
            continue
        turno_ultimo_sobreviviente, sobrevivientes, orden_evacuacion = algoritmo_genetico(len(agentes_2d),tamano_poblacion,num_generaciones,mapa_edificio,agentes_2d,piso,posicion_objetivo,k_fuego,posicion_fuego,distancia_manhattan,limite_profundidad) 
        sobrevivientes_totales+=sobrevivientes
        ultimos_turnos.append(turno_ultimo_sobreviviente)  
        
    turnos_tomados = max(ultimos_turnos)   
    return sobrevivientes_totales, turnos_tomados
