import statistics
import time
import os

# Importa tus funciones desde tus propios archivos (ajusta los nombres si es necesario)
# from entorno import iniciar_entorno
from algoritmos import correr_algoritmo_busqueda_informada, correr_algoritmo_busqueda_no_informada, busqueda_Greedy, BFS, UCS,A_star, distancia_manhattan
from genetico import correr_algoritmo_genetico

def ejecutar_benchmark(iteraciones_por_config=80, nombre_archivo="resultados_UCS_1_2.txt"):
    """
    Ejecuta simulaciones automatizadas y calcula estadísticas descriptivas
    para evaluar el rendimiento de los algoritmos de evacuación.
    """
    
    

  
    
    # Abrimos el archivo en modo escritura ("w" crea o sobreescribe el archivo)
    with open(nombre_archivo, "w", encoding="utf-8") as archivo:
        archivo.write("========================================================\n")
        archivo.write("        REPORTE DE BENCHMARKING - EVACUACIÓN MAPF       \n")
        archivo.write("========================================================\n\n")

        for mapa in range(1,4):
            
            
            resultados_turnos = []
            resultados_supervivencia = []
            
            for i in range(iteraciones_por_config):
                
                
              
              
                
                
                sob, turnos = correr_algoritmo_busqueda_no_informada(
                    eleccion_mapa=mapa,
                    num_pisos=2,
                    cantidad_agentes=4,
                    k_fuego=3,
                    algoritmo=UCS,
                    limite_profundidad=20
                )
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
                                    cantidad_agentes=80,
                                    k_fuego=3,
                                    algoritmo=A_star,
                                    heuristica= distancia_manhattan,
                                    limite_profundidad=20
                                ) """
               
                
                # Cálculo de la tasa de supervivencia de esta iteración (0.0 a 1.0)
                tasa_supervivencia = sob / 4
                
                resultados_turnos.append(turnos)
                resultados_supervivencia.append(tasa_supervivencia)
                print(f"  Iteración {i+1}: Turnos = {turnos}, Supervivencia = {tasa_supervivencia:.1%}")

            # 2. Calcular Estadísticos Descriptivos
            tasa_media_supervivencia = statistics.mean(resultados_supervivencia)
            
            media_turnos = statistics.mean(resultados_turnos)
            min_turnos = min(resultados_turnos)
            max_turnos = max(resultados_turnos)
            
            # La desviación estándar requiere al menos 2 datos
            if iteraciones_por_config > 1:
                stdev_turnos = statistics.stdev(resultados_turnos)
            else:
                stdev_turnos = 0.0

            # 3. Escribir resultados en el archivo
            archivo.write(f"--- A* 2 ---\n")
            archivo.write(f"Configuración: 2 pisos | 80 agentes |  Mapa {mapa} | Fuego c/3 turnos\n")
            archivo.write(f"Iteraciones ejecutadas: {iteraciones_por_config}\n\n")
            
            archivo.write(" Tasa de Supervivencia:\n")
            archivo.write(f"   - Promedio: {tasa_media_supervivencia:.2%}\n" )
            
            archivo.write(" Estadísticos de Tiempo de Despeje (Turnos):\n")
            archivo.write(f"   - Media              : {media_turnos:.2f} turnos\n")
            archivo.write(f"   - Desviación Estándar: {stdev_turnos:.2f}\n")
            archivo.write(f"   - Mínimo (Mejor caso): {min_turnos} turnos\n")
            archivo.write(f"   - Máximo (Peor caso) : {max_turnos} turnos\n")
            archivo.write("-" * 56 + "\n\n")
            
    print(f"\n¡Benchmark finalizado! Revisa el archivo '{nombre_archivo}' para ver los resultados.")

# Ejecutar si se llama directamente
if __name__ == "__main__":
    ejecutar_benchmark(iteraciones_por_config=10)