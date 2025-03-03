import simpy
import random
import numpy as np

SEED = 42
random.seed(SEED)

Num_procesos = 5 
Capacidad_CPU = 2
Instruc_por_minuto= 3
Intervalo = 3

tiempos_proceso = []

def proceso(env, nombre, cpu, tiempo_ejecuto, instruccion):
    yield env.timeout(tiempo_ejecuto)
    print(f'{nombre}llega en CPU en {env.now}')
 
    while instruccion > 0:
        with cpu.request() as req:
            yield req
            print(f'{nombre} inicia en CPU en {env.now}')
            yield env.timeout(1)
            ejecutar = min(Instruc_por_minuto, instruccion)
            instruccion -= ejecutar
            print(f'{nombre} ejecuto {ejecutar} instrucciones, faltantes {instruccion} en {env.now}')

        if instruccion > 0:
            decision = random.randint(1,2)
            if decision == 1:
                print(f'{nombre} se dirige a estado Waiting en {env.now}')
                yield env.timeout(random.unifrom(1,3))
                print(f'{nombre} regresa a estado Ready en {env.now}')
            else:
                print(f'{nombre} regresa directamente a estado Ready en {env.now}')

        print(f'{nombre} termino de ejecutar las instrucciones en {env.now}')
        tiempos_proceso.append(env.now)

env = simpy.Environment()
cpu = simpy.Resource(env, capacity=Capacidad_CPU)

for i in range(Num_procesos):
    env.process(proceso(env, cpu, i*Intervalo, random.randint(1,10)))

env.run()

print (f'Tiempo que duro la ejecucion de la simulacion: {np.mean(tiempos_proceso):.2f}')


