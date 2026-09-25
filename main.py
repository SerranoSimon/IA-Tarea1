import numpy as np
from algoritmos import correr_algoritmo_busqueda_informada,correr_algoritmo_busqueda_no_informada, DFS, UCS, busqueda_Greedy, distancia_manhattan, A_star
if __name__ == "__main__":
    # correr_algoritmo_busqueda_no_informada(2,1,20,3,DFS,50)
     correr_algoritmo_busqueda_informada(2,1,100,5,A_star, distancia_manhattan, 50)
    