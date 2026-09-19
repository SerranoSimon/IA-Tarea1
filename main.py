import numpy as np
from entorno import iniciar_entorno,propagar_fuego,calcular_congestion

if __name__ == "__main__":
    mapa,posicion_agentes,celdas_fuego = iniciar_entorno(3,3)
    k = 1 # turnos de propagacion fuego
    turno = 0
    while(len(posicion_agentes)>0 and turno <=200):
        turno +=1
        print(f"TURNO: {turno}")
        print(f"poscicion agentes {posicion_agentes}")
        
        if(turno % k == 0):
            mapa, posicion_agentes, celdas_fuego = propagar_fuego(mapa,posicion_agentes,celdas_fuego)
            print("Se ha propagado el fuego")
        if(len(posicion_agentes)==0):
            print(f"Han muerto todos los agentes en turno {turno}")
            break
        congestion = calcular_congestion(posicion_agentes)
        print(f"congestion: {congestion}")
        print(mapa)

    