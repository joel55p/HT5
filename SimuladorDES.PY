import simpy
import random
import numpy as np

# Parámetros de la simulación
SEED = 42
random.seed(SEED)

Num_procesos = 25
Capacidad_CPU = 1
Instruc_por_minuto = 3
Intervalo = 10
Capacidad_RAM = 100  # Capacidad de la memoria RAM

tiempos_proceso = []  # Lista para registrar los tiempos de ejecución

def proceso(env, nombre, cpu, ram, instrucciones, memoria):
    """Simula el ciclo de vida de un proceso en el sistema operativo"""
    
    # El proceso llega al sistema
    llegada = env.now
    print(f'{nombre} llega al sistema en {llegada:.2f} esperando por RAM ({memoria} unidades)')

    # Espera hasta que haya suficiente RAM disponible
    with ram.get(memoria) as req:
        yield req  # Bloquea hasta que haya memoria suficiente
        print(f'{nombre} obtiene {memoria} unidades de RAM en {env.now:.2f}, pasando a READY')

        while instrucciones > 0:
            with cpu.request() as req_cpu:
                yield req_cpu  # Espera a que el CPU esté disponible
                print(f'{nombre} inicia en CPU en {env.now:.2f}')
                
                yield env.timeout(1)  # Simula 1 unidad de tiempo en CPU
                ejecutar = min(Instruc_por_minuto, instrucciones)
                instrucciones -= ejecutar
                print(f'{nombre} ejecutó {ejecutar} instrucciones, faltantes {instrucciones} en {env.now:.2f}')

            # Decidir siguiente estado
            if instrucciones <= 0:
                print(f'{nombre} terminó en {env.now:.2f}')
                tiempos_proceso.append(env.now - llegada)
                break  # El proceso termina

            decision = random.randint(1, 2)
            if decision == 1:
                print(f'{nombre} entra a WAITING en {env.now:.2f}')
                yield env.timeout(random.uniform(1, 3))  # Simula operación de I/O
                print(f'{nombre} regresa a READY en {env.now:.2f}')
            else:
                print(f'{nombre} regresa directamente a READY en {env.now:.2f}')

    # Liberar memoria RAM
    ram.put(memoria)
    print(f'{nombre} libera {memoria} unidades de RAM en {env.now:.2f}')

def generar_procesos(env, num_procesos, cpu, ram, intervalo):
    """Genera procesos de acuerdo a la distribución exponencial de tiempo"""
    for i in range(num_procesos):
        instrucciones = random.randint(1, 10)  # Instrucciones totales del proceso
        memoria = random.randint(1, 10)  # Memoria requerida
        env.process(proceso(env, f'Proceso{i}', cpu, ram, instrucciones, memoria))
        yield env.timeout(random.expovariate(1.0 / intervalo))  # Tiempo de llegada exponencial

# Configurar entorno de simulación
env = simpy.Environment()
cpu = simpy.Resource(env, capacity=Capacidad_CPU)
ram = simpy.Container(env, init=Capacidad_RAM, capacity=Capacidad_RAM)

# Iniciar la generación de procesos
env.process(generar_procesos(env, Num_procesos, cpu, ram, Intervalo))

# Ejecutar simulación
env.run()

# Mostrar resultados
print(f'Tiempo promedio de ejecución: {np.mean(tiempos_proceso):.2f}')
print(f'Desviación estándar del tiempo de ejecución: {np.std(tiempos_proceso):.2f}')
