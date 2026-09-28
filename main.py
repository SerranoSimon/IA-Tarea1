import numpy as np
from benchmarking import ejecutar_benchmark
from genetico import correr_algoritmo_genetico
from algoritmos import correr_algoritmo_busqueda_informada,correr_algoritmo_busqueda_no_informada, BFS, UCS, busqueda_Greedy, distancia_manhattan, A_star
if __name__ == "__main__":
    ejecutar_benchmark()
    """ sob, turnos = correr_algoritmo_busqueda_no_informada(
                        eleccion_mapa=mapa,
                        num_pisos=2,
                        cantidad_agentes=4,
                        k_fuego=3,
                        algoritmo=BFS,
                        limite_profundidad=20
                    ) """
    """ sob,turnos = correr_algoritmo_genetico(
                        eleccion_mapa=mapa,
                        num_pisos=2,
                        cantidad_agentes=4,
                        tamano_poblacion= 15,
                        num_generaciones= 10,
                        k_fuego=3,
                        limite_profundidad=20
                    ) """
                    
                    
                    
    """ sob, turnos = correr_algoritmo_busqueda_informada(
                        eleccion_mapa=mapa,
                        num_pisos=2,
                        cantidad_agentes=4,
                        k_fuego=3,
                        algoritmo=A_star,
                        heuristica= distancia_manhattan,
                        limite_profundidad=20
                    ) """
   