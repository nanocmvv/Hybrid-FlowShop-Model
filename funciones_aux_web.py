# -*- coding: utf-8 -*-
"""
Created on Mon Feb 17 15:06:03 2025

@author: 34608
"""
import random, os
import matplotlib.pyplot as plt
from scheptk.scheptk import Model

def S_random(S):
    S_random = []
    while len(S_random) < len(S):
        trab_aleatorio = random.choice(S)
        if trab_aleatorio not in S_random:
            S_random.append(trab_aleatorio)
    return S_random

def calcular_tiempo_estacion(pt, disp_maquinas, tiempo_previo, job):
    """
    Calcula el instante en que un trabajo terminará en la mejor máquina disponible dentro de la estación actual.

    Parámetros:
    - pt: Lista de listas donde pt[i][job] indica el tiempo de procesamiento del trabajo 'job' en la máquina 'i' de la estación.
    - disp_maquinas: Lista con los tiempos de disponibilidad de cada máquina en la estación actual.
    - tiempo_previo: Momento en que el trabajo está listo para comenzar en la estación.
    - job: Índice del trabajo que se está programando.

    Retorna:
    - min_fin: Instante en que el trabajo terminará en la mejor máquina.
    - maquina_seleccionada: Índice de la máquina donde el trabajo finalizará antes.

    Nota:
    - La máquina óptima es aquella donde el trabajo finaliza más pronto.
    - En caso de empate, se selecciona la primera máquina con el mismo tiempo mínimo de finalización.
    - Se asume que `disp_maquinas` tiene el mismo número de elementos que `pt`, de lo contrario, podría ocurrir un IndexError.
    """
    tiempos = []
    for i in range(len(pt)):
        inicio = max(tiempo_previo, disp_maquinas[i])
        fin = inicio + pt[i][job]
        tiempos.append(fin)
    min_fin = min(tiempos)
    maquina_seleccionada = tiempos.index(min_fin)
    return min_fin, maquina_seleccionada

def calcular_tiempo_inicio_siguiente_estacion(pt, disp_maquinas, tiempo_previo, job):
    """
    Determina el instante en que un trabajo podrá comenzar en la siguiente estación y en qué máquina.

    Parámetros:
    - pt: Lista de listas donde pt[i][job] indica el tiempo de procesamiento del trabajo 'job' en la máquina 'i' de la siguiente estación.
    - disp_maquinas: Lista con los tiempos de disponibilidad de cada máquina en la estación siguiente.
    - tiempo_previo: Momento en que el trabajo terminó en la estación actual.
    - job: Índice del trabajo que se está programando.

    Retorna:
    - inicio_siguiente_est: Instante en que el trabajo puede comenzar en la mejor máquina disponible.
    - maquina_seleccionada: Índice de la máquina donde el trabajo terminará antes.

    Nota:
    - La máquina óptima es aquella donde el trabajo finaliza más pronto.
    - En caso de empate, se selecciona la primera máquina con el mismo tiempo mínimo de finalización.
    - Se asume que `disp_maquinas` tiene el mismo número de elementos que `pt`, de lo contrario, podría ocurrir un IndexError.
    """
    tiempos_fin = []  # Guardará el tiempo en que terminaría el trabajo en cada máquina
    tiempos_inicio = []  # Guardará el tiempo en que comienza en cada máquina
    for i in range(len(pt)):  # Recorremos todas las máquinas de la siguiente estación
        inicio = max(tiempo_previo, disp_maquinas[i])  # Se puede empezar cuando la máquina esté disponible
        fin = inicio + pt[i][job]  # Momento en el que terminaría el trabajo en esta máquina
        tiempos_inicio.append(inicio)
        tiempos_fin.append(fin)

    min_fin = min(tiempos_fin)  # Encontramos la máquina donde terminaría antes
    maquina_seleccionada = tiempos_fin.index(min_fin)  # Índice de esa máquina
    inicio_siguiente_est = tiempos_inicio[maquina_seleccionada]  # Instante en que el trabajo comienza en esa máquina

    return inicio_siguiente_est, maquina_seleccionada


colores = [
    'red','lime','deepskyblue','bisque','mintcream','royalblue',
    'sandybrown','palegreen','pink','violet','cyan',
    'darkseagreen','gold'
]


def custom_print_schedule(schedule, filename=None):
    tick_starting_at = 10
    tick_separation = 20
    task_height = 8
    font_height = 1

    # Crear gráfico
    fig, gantt = plt.subplots()

    # Obtener número de máquinas
    num_machines = max(task.machine for task in schedule.task_list) + 1
    machines = list(range(num_machines))
    max_ct = max([task.ct for task in schedule.task_list] + [nap.ct for nap in schedule.NAP_list])

    gantt.set_xlim(0, max_ct)
    gantt.set_ylim(0, len(machines) * tick_separation + tick_starting_at)

    gantt.set_xlabel('Time')
    gantt.set_ylabel('Machines')
    gantt.set_yticks([
        tick_starting_at + tick_separation * i + task_height / 2 for i in range(len(machines))
    ])
    gantt.set_yticklabels(['M' + str(i) for i in range(len(machines) - 1, -1, -1)])

    for job in schedule.job_order:
        tasks = [t for t in schedule.task_list if t.job == job]
        for task in tasks:
            y = tick_starting_at + tick_separation * (len(machines) - task.machine - 1)
            color = colores[job % len(colores)]
            gantt.broken_barh(
                [(task.st, task.ct - task.st)],
                (y, task_height),
                facecolors=color,
                edgecolors='black'
            )
            gantt.text(
                task.st + (task.ct - task.st)/2,
                y + task_height/2 - font_height,
                f'J{job}',
                ha='center', va='center'
            )

    # Dibujar NAPs si los hay
    for void in schedule.NAP_list:
        y = tick_starting_at + tick_separation * (len(machines) - void.machine - 1)
        if void.ct != void.st:
            gantt.broken_barh(
                [(void.st, void.ct - void.st)],
                (y, task_height),
                facecolors='white',
                edgecolors='black',
                hatch='//'
            )
            gantt.text(
                void.st + (void.ct - void.st)/2,
                y + task_height/2 - font_height,
                void.name,
                ha='center', va='center'
            )

    if filename:
        fig.savefig(filename, dpi=600, facecolor='w')
    else:
        plt.tight_layout()
        plt.show()
        
def print_custom_schedule(self, solution, filename=None):
    gantt = self.create_schedule(solution)
    custom_print_schedule(gantt, filename)
    
# Agregar dinámicamente a la clase Model
setattr(Model, 'print_custom_schedule', print_custom_schedule)
    
    
def mostrar_bloqueos(modelo):
    print("\n📋 Bloqueos registrados:")
    hay_bloqueos = False

    for m, bloqueos in enumerate(modelo.bloqueos):
        for job, t_ini, t_fin in bloqueos:
            print(f"  M{m}: Trabajo {job} bloqueado de t={t_ini} a t={t_fin}")
            hay_bloqueos = True

    if not hay_bloqueos:
        print("  No se ha producido ningún bloqueo.")


def mostrar_buffer_log(modelo):
    print("\n📦 Ocupación registrada de buffers:")
    hay_uso = False

    for k, estacion in enumerate(modelo.buffer_log):
        for m, buffer_m in enumerate(estacion):
            for job, t_ini, t_fin in buffer_m:
                print(f"  Est{k} → M{m}: Trabajo {job} ocupó el buffer de t={t_ini} a t={t_fin}")
                hay_uso = True

    if not hay_uso:
        print("  No se ha registrado uso de ningún buffer.")
        


def gantt_buffers_y_bloqueos(buffer_log, bloqueos):
    import matplotlib.pyplot as plt

    tick_starting_at = 10
    tick_separation = 30
    task_height = 6
    font_height = 1
    stack_offset = 7  # Espaciado entre trabajos apilados

    colores = [
        'red','lime','deepskyblue','bisque','mintcream','royalblue',
        'sandybrown','palegreen','pink','violet','cyan',
        'darkseagreen','gold'
    ]

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
    max_tiempo = 0

    # ➤ Parte superior: Buffers (orden invertido visualmente)
    etiquetas_buff = []
    posiciones_buff = []

    total_maquinas = sum(len(est) for est in buffer_log)
    machine_id = 0
    buffer_info = []

    for k, estacion in enumerate(buffer_log):
        for m, maquina in enumerate(estacion):
            buffer_info.append((machine_id, buffer_log[k][m]))
            machine_id += 1

    for idx, (m_id, usos_buffer) in enumerate(reversed(buffer_info)):
        y_base = tick_starting_at + tick_separation * idx
        etiquetas_buff.append(f'M{m_id}')
        posiciones_buff.append(y_base + task_height)

        # Apilar trabajos según solape
        niveles = []

        for job_id, t_inicio, t_fin in sorted(usos_buffer, key=lambda x: x[1]):
            color = colores[job_id % len(colores)]

            # Encontrar nivel libre
            for nivel_idx, nivel in enumerate(niveles):
                if all(t_fin <= ini or t_inicio >= fin for _, ini, fin in nivel):
                    nivel.append((job_id, t_inicio, t_fin))
                    break
            else:
                niveles.append([(job_id, t_inicio, t_fin)])
                nivel_idx = len(niveles) - 1

            y = y_base + stack_offset * nivel_idx
            ax1.broken_barh([(t_inicio, t_fin - t_inicio)], (y, task_height), facecolors=color, edgecolors='black')
            ax1.text(
                t_inicio + (t_fin - t_inicio)/2,
                y + task_height / 2 - font_height,
                f'J{job_id}',
                ha='center', va='center'
            )
            max_tiempo = max(max_tiempo, t_fin)

    ax1.set_yticks(posiciones_buff)
    ax1.set_yticklabels(etiquetas_buff)
    ax1.set_ylabel("Buffers")
    ax1.set_title("Gantt de buffers y bloqueos (BUFFER ≥ 0)")
    ax1.grid(True)

    # ➤ Parte inferior: Bloqueos (orden invertido también)
    posiciones_bloqueos = []
    etiquetas_bloqueos = []

    for idx, m in enumerate(reversed(range(len(bloqueos)))):
        y = tick_starting_at + tick_separation * idx
        posiciones_bloqueos.append(y + task_height)
        etiquetas_bloqueos.append(f"M{m}")

        for job_id, t_inicio, t_fin in bloqueos[m]:
            color = colores[job_id % len(colores)]
            ax2.broken_barh([(t_inicio, t_fin - t_inicio)], (y, task_height),
                            facecolors=color, edgecolors='black', hatch='//')
            ax2.text(
                t_inicio + (t_fin - t_inicio)/2,
                y + task_height / 2 - font_height,
                f'J{job_id}',
                ha='center', va='center', fontsize=8
            )
            max_tiempo = max(max_tiempo, t_fin)

    ax2.set_yticks(posiciones_bloqueos)
    ax2.set_yticklabels(etiquetas_bloqueos)
    ax2.set_ylabel("Máquinas")
    ax2.set_xlabel("Tiempo")
    ax2.grid(True)

    ax1.set_xlim(0, max_tiempo + 5)
    ax2.set_xlim(0, max_tiempo + 5)

    plt.tight_layout()
    plt.show()


def gantt_completo(schedule, buffer_log, bloqueos, filename=None):
    import matplotlib.pyplot as plt

    colores = [
        'red', 'lime', 'deepskyblue', 'bisque', 'mintcream', 'royalblue',
        'sandybrown', 'palegreen', 'pink', 'violet', 'cyan',
        'darkseagreen', 'gold'
    ]

    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 10), sharex=True)

    # --- Producción ---
    tick_starting_at = 10
    tick_separation = 20
    task_height = 10
    font_height = 1

    num_machines = max(task.machine for task in schedule.task_list) + 1
    max_ct = max([task.ct for task in schedule.task_list] + [v.ct for v in schedule.NAP_list])

    ax1.set_ylim(0, num_machines * tick_separation + tick_starting_at)
    ax1.set_yticks([tick_starting_at + tick_separation * i + task_height / 2 for i in range(num_machines)])
    ax1.set_yticklabels([f'M{m}' for m in reversed(range(num_machines))])
    ax1.set_title("Diagrama de producción")
    ax1.set_ylabel("Máquinas")

    for job in schedule.job_order:
        for t in [t for t in schedule.task_list if t.job == job]:
            y = tick_starting_at + tick_separation * (num_machines - t.machine - 1)
            color = colores[job % len(colores)]
            ax1.broken_barh([(t.st, t.ct - t.st)], (y, task_height), facecolors=color, edgecolors='black')
            ax1.text(t.st + (t.ct - t.st)/2, y + task_height / 2 - font_height, f'J{job}', ha='center', va='center')

    for void in schedule.NAP_list:
        y = tick_starting_at + tick_separation * (num_machines - void.machine - 1)
        if void.ct != void.st:
            ax1.broken_barh([(void.st, void.ct - void.st)], (y, task_height),
                            facecolors='white', edgecolors='black', hatch='//')
            ax1.text(void.st + (void.ct - void.st)/2, y + task_height / 2 - font_height,
                     void.name, ha='center', va='center')

    # --- Buffers ---
    tick_separation = 30
    task_height = 6
    stack_offset = 7

    posiciones_buff = []
    etiquetas_buff = []
    buffer_info = []
    machine_id = 0
    for k, estacion in enumerate(buffer_log):
        for m, maquina in enumerate(estacion):
            buffer_info.append((machine_id, maquina))
            machine_id += 1

    for idx, (m_id, usos) in enumerate(reversed(buffer_info)):
        y_base = tick_starting_at + tick_separation * idx
        posiciones_buff.append(y_base + task_height)
        etiquetas_buff.append(f'M{m_id}')

        niveles = []
        for job_id, t_inicio, t_fin in sorted(usos, key=lambda x: x[1]):
            color = colores[job_id % len(colores)]
            for nivel_idx, nivel in enumerate(niveles):
                if all(t_fin <= ini or t_inicio >= fin for _, ini, fin in nivel):
                    nivel.append((job_id, t_inicio, t_fin))
                    break
            else:
                niveles.append([(job_id, t_inicio, t_fin)])
                nivel_idx = len(niveles) - 1

            y = y_base + stack_offset * nivel_idx
            ax2.broken_barh([(t_inicio, t_fin - t_inicio)], (y, task_height),
                            facecolors=color, edgecolors='black')
            ax2.text(t_inicio + (t_fin - t_inicio)/2, y + task_height / 2,
                     f'J{job_id}', ha='center', va='center', fontsize=8)

    ax2.set_yticks(posiciones_buff)
    ax2.set_yticklabels(etiquetas_buff)
    ax2.set_ylabel("Buffers")
    ax2.set_title("Buffers ocupados")
    ax2.grid(True)

    # --- Bloqueos ---
    task_height = 10
    posiciones_bloqueos = []
    etiquetas_bloqueos = []

    for idx, m in enumerate(reversed(range(len(bloqueos)))):
        y = tick_starting_at + tick_separation * idx
        posiciones_bloqueos.append(y + task_height)
        etiquetas_bloqueos.append(f'M{m}')

        for job_id, t_inicio, t_fin in bloqueos[m]:
            color = colores[job_id % len(colores)]
            ax3.broken_barh([(t_inicio, t_fin - t_inicio)], (y, task_height),
                            facecolors=color, edgecolors='black', hatch='//')
            ax3.text(t_inicio + (t_fin - t_inicio)/2, y + task_height / 2,
                     f'J{job_id}', ha='center', va='center', fontsize=8)

    ax3.set_yticks(posiciones_bloqueos)
    ax3.set_yticklabels(etiquetas_bloqueos)
    ax3.set_ylabel("Máquinas")
    ax3.set_xlabel("Tiempo")
    ax3.set_title("Bloqueos")
    ax3.grid(True)

    for ax in [ax1, ax2, ax3]:
        ax.set_xlim(0, max_ct + 5)

    plt.tight_layout()

    # ✅ Guardar en archivo para mostrar en web
    if filename:
        fig.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close(fig)




def gantt_solo_buffers(buffer_log):
    import matplotlib.pyplot as plt

    tick_starting_at = 10
    tick_separation = 30
    task_height = 6
    font_height = 1
    stack_offset = 7

    colores = [
        'red','lime','deepskyblue','bisque','mintcream','royalblue',
        'sandybrown','palegreen','pink','violet','cyan',
        'darkseagreen','gold'
    ]

    fig, ax = plt.subplots(figsize=(12, 5))

    etiquetas_buff = []
    posiciones_buff = []
    buffer_info = []
    machine_id = 0

    # Recorrer todas las estaciones excepto la última
    for estacion in buffer_log:
        for usos in estacion:
            buffer_info.append((machine_id, usos))
            machine_id += 1

    max_tiempo = 0

    for idx, (m_id, usos_buffer) in enumerate(reversed(buffer_info)):
        y_base = tick_starting_at + tick_separation * idx
        etiquetas_buff.append(f'M{m_id}')
        posiciones_buff.append(y_base + task_height)

        niveles = []

        for job_id, t_inicio, t_fin in sorted(usos_buffer, key=lambda x: x[1]):
            color = colores[job_id % len(colores)]

            # Apilamiento según solapamientos
            for nivel_idx, nivel in enumerate(niveles):
                if all(t_fin <= ini or t_inicio >= fin for _, ini, fin in nivel):
                    nivel.append((job_id, t_inicio, t_fin))
                    break
            else:
                niveles.append([(job_id, t_inicio, t_fin)])
                nivel_idx = len(niveles) - 1

            y = y_base + stack_offset * nivel_idx
            ax.broken_barh([(t_inicio, t_fin - t_inicio)], (y, task_height),
                           facecolors=color, edgecolors='black')
            ax.text(t_inicio + (t_fin - t_inicio)/2, y + task_height / 2 - font_height,
                    f'J{job_id}', ha='center', va='center')

            max_tiempo = max(max_tiempo, t_fin)

    ax.set_yticks(posiciones_buff)
    ax.set_yticklabels(etiquetas_buff)
    ax.set_ylabel("Buffers")
    ax.set_title("Diagrama de ocupación de buffers")
    ax.set_xlabel("Tiempo")
    ax.grid(True)
    ax.set_xlim(0, max_tiempo + 5)

    plt.tight_layout()
    plt.show()




def gantt_solo_bloqueos(bloqueos):
    import matplotlib.pyplot as plt

    tick_starting_at = 10
    tick_separation = 30
    task_height = 10  # más ancho
    font_height = 1

    colores = [
        'red','lime','deepskyblue','bisque','mintcream','royalblue',
        'sandybrown','palegreen','pink','violet','cyan',
        'darkseagreen','gold'
    ]

    fig, ax = plt.subplots(figsize=(12, 5))
    posiciones = []
    etiquetas = []
    max_tiempo = 0

    for idx, m in enumerate(reversed(range(len(bloqueos)))):
        y = tick_starting_at + tick_separation * idx
        posiciones.append(y + task_height)
        etiquetas.append(f"M{m}")

        for job_id, t_inicio, t_fin in bloqueos[m]:
            color = colores[job_id % len(colores)]
            ax.broken_barh([(t_inicio, t_fin - t_inicio)], (y, task_height),
                           facecolors=color, edgecolors='black', hatch='//')
            ax.text(
                t_inicio + (t_fin - t_inicio)/2,
                y + task_height / 2 - font_height,
                f'J{job_id}',
                ha='center', va='center'
            )
            max_tiempo = max(max_tiempo, t_fin)

    ax.set_yticks(posiciones)
    ax.set_yticklabels(etiquetas)
    ax.set_ylabel("Máquinas")
    ax.set_xlabel("Tiempo")
    ax.set_title("Diagrama de bloqueos")
    ax.grid(True)
    ax.set_xlim(0, max_tiempo + 5)

    plt.tight_layout()
    plt.show()


def generar_instancia_aleatoria(nombre_archivo="instancias/instancia_nueva.txt", buffer=None):
    # Asegúrate de que la carpeta 'instancias' exista
    if not os.path.exists("instancias"):
        os.makedirs("instancias")

    # Parámetros aleatorios
    num_estaciones = random.randint(3, 5)
    maquinas_por_estacion = [random.randint(1, 3) for _ in range(num_estaciones)]
    num_trabajos = random.randint(5, 10)
    total_maquinas = sum(maquinas_por_estacion)

    # Usar el valor de `buffer` pasado desde el formulario, si está presente
    if buffer is None:
        buffer = random.randint(0, 3)  # Si no se pasa un valor de buffer, generamos uno aleatorio

    max_pt = 8

    # Generar matriz PT
    pt = []
    for _ in range(total_maquinas):
        fila = [random.randint(1, max_pt) for _ in range(num_trabajos)]
        pt.append(fila)

    dd = [random.randint(15, 40) for _ in range(num_trabajos)]
    w = [random.randint(10, 20) for _ in range(num_trabajos)]
    r = [0 for j in range(num_trabajos)]

    # Escribir el archivo en la carpeta 'instancias/'
    with open(f"{nombre_archivo}", "w") as f:
        f.write(f"[MACHINES={total_maquinas}]\n")
        f.write(f"[JOBS={num_trabajos}]\n")
        f.write("[PT= " + " ; ".join([",".join(map(str, fila)) for fila in pt]) + "]\n")
        f.write("[DD= " + ",".join(map(str, dd)) + "]\n")
        f.write("[W=" + ",".join(map(str, w)) + "]\n")
        f.write("[R=" + ",".join(map(str, r)) + "]\n")
        f.write(f"[EST={num_estaciones}]\n")
        f.write("[M_EST=" + ",".join(map(str, maquinas_por_estacion)) + "]\n")
        f.write(f"[BUFFER={buffer}]\n")  # Usar el valor de `buffer` aquí

    print(f"✅ Instancia aleatoria generada en instancias/{nombre_archivo}")
    with open(f"{nombre_archivo}", "r") as f:
        print(f.read())  # Imprimir el contenido del archivo recién creado

"----------------------------------------------------------------------------------------"


def gantt_completo_mod(schedule, buffer_log, bloqueos):
    import matplotlib.pyplot as plt

    colores = [
        'red','lime','deepskyblue','bisque','mintcream','royalblue',
        'sandybrown','palegreen','pink','violet','cyan',
        'darkseagreen','gold'
    ]

    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 10), sharex=True)

    # 🎯 PARTE 1: Producción
    tick_starting_at = 10
    tick_separation = 20
    task_height = 10
    font_height = 1

    num_machines = max(task.machine for task in schedule.task_list) + 1
    machines = list(range(num_machines))
    max_ct = max([task.ct for task in schedule.task_list] + [v.ct for v in schedule.NAP_list])

    ax1.set_ylim(0, len(machines) * tick_separation + tick_starting_at)
    ax1.set_yticks([tick_starting_at + tick_separation * i + task_height / 2 for i in range(len(machines))])
    ax1.set_yticklabels(['M' + str(i) for i in range(len(machines) - 1, -1, -1)])
    ax1.set_title("Diagrama de producción")
    ax1.set_ylabel("Máquinas")

    for job in schedule.job_order:
        for t in [t for t in schedule.task_list if t.job == job]:
            y = tick_starting_at + tick_separation * (len(machines) - t.machine - 1)
            color = colores[job % len(colores)]
            ax1.broken_barh([(t.st, t.ct - t.st)], (y, task_height), facecolors=color, edgecolors='black')
            ax1.text(t.st + (t.ct - t.st)/2, y + task_height / 2 - font_height, f'J{job}', ha='center', va='center')

    for void in schedule.NAP_list:
        y = tick_starting_at + tick_separation * (len(machines) - void.machine - 1)
        if void.ct != void.st:
            ax1.broken_barh([(void.st, void.ct - void.st)], (y, task_height),
                            facecolors='white', edgecolors='black', hatch='//')
            ax1.text(void.st + (void.ct - void.st)/2, y + task_height / 2 - font_height,
                     void.name, ha='center', va='center')

        # 🧱 PARTE 2: Buffers (mostrar todas aunque estén vacías y apiladas)
    tick_starting_at = 10
    tick_separation = 30
    task_height = 6
    font_height = 1
    stack_offset = 7

    etiquetas_buff = []
    posiciones_buff = []

    machine_id = 0
    total_maquinas = sum(len(estacion) for estacion in buffer_log)

    # Creamos una lista con todas las máquinas y sus usos de buffer
    buffer_info = []
    for k, estacion in enumerate(buffer_log):
        for m, usos in enumerate(estacion):
            buffer_info.append((machine_id, usos))
            machine_id += 1

    # Si faltan máquinas para completar el total, se añaden vacías
    while len(buffer_info) < total_maquinas:
        buffer_info.append((len(buffer_info), []))

    for idx, (m_id, usos_buffer) in enumerate(reversed(buffer_info)):
        y_base = tick_starting_at + tick_separation * idx
        etiquetas_buff.append(f'M{m_id}')
        posiciones_buff.append(y_base + task_height)

        niveles = []
        for job_id, t_inicio, t_fin in sorted(usos_buffer, key=lambda x: x[1]):
            color = colores[job_id % len(colores)]
            for nivel_idx, nivel in enumerate(niveles):
                if all(t_fin <= ini or t_inicio >= fin for _, ini, fin in nivel):
                    nivel.append((job_id, t_inicio, t_fin))
                    break
            else:
                niveles.append([(job_id, t_inicio, t_fin)])
                nivel_idx = len(niveles) - 1

            y = y_base + stack_offset * nivel_idx
            ax2.broken_barh([(t_inicio, t_fin - t_inicio)], (y, task_height),
                            facecolors=color, edgecolors='black')
            ax2.text(t_inicio + (t_fin - t_inicio)/2, y + task_height / 2 - font_height,
                     f'J{job_id}', ha='center', va='center')

    ax2.set_yticks(posiciones_buff)
    ax2.set_yticklabels(etiquetas_buff)
    ax2.set_ylabel("Buffers")
    ax2.set_title("Buffers ocupados")
    ax2.grid(True)



    # 🚫 PARTE 3: Bloqueos
    task_height = 10
    posiciones_bloqueos = []
    etiquetas_bloqueos = []

    total_maquinas = len(bloqueos)
    for idx, m in enumerate(reversed(range(total_maquinas))):
        y = tick_starting_at + tick_separation * idx
        posiciones_bloqueos.append(y + task_height)
        etiquetas_bloqueos.append(f"M{m}")

        for job_id, t_inicio, t_fin in bloqueos[m]:
            color = colores[job_id % len(colores)]
            ax3.broken_barh([(t_inicio, t_fin - t_inicio)], (y, task_height),
                            facecolors=color, edgecolors='black', hatch='//')
            ax3.text(t_inicio + (t_fin - t_inicio)/2, y + task_height / 2 - font_height,
                     f'J{job_id}', ha='center', va='center', fontsize=8)

    ax3.set_yticks(posiciones_bloqueos)
    ax3.set_yticklabels(etiquetas_bloqueos)
    ax3.set_ylabel("Máquinas")
    ax3.set_xlabel("Tiempo")
    ax3.set_title("Bloqueos")
    ax3.grid(True)

    for ax in [ax1, ax2, ax3]:
        ax.set_xlim(0, max_ct + 5)

    plt.tight_layout()
    plt.show()
    
    
def generar_instancia_personalizada(nombre_archivo, num_estaciones, maquinas_por_estacion, num_trabajos, buffer):
    """
    Crea un archivo de instancia con los parámetros que el usuario ha escogido.
    - num_estaciones: int
    - maquinas_por_estacion: lista de ints de longitud num_estaciones
    - num_trabajos: int
    - buffer: int
    """
    import random
    # Calculamos total de máquinas
    total_maquinas = sum(maquinas_por_estacion)
    max_pt = 8

    # ✅ Generar matriz PT: total_maquinas x num_trabajos
    pt = [[random.randint(1, max_pt) for _ in range(num_trabajos)]
          for __ in range(total_maquinas)]

    # Fechas de entrega (DD), pesos (W), release (R)
    dd = [random.randint(15, 40) for _ in range(num_trabajos)]
    w  = [random.randint(10, 20) for _ in range(num_trabajos)]
    r  = [0 for j in range(num_trabajos)]

    # Escribir archivo
    with open(nombre_archivo, "w") as f:
        f.write(f"[MACHINES={total_maquinas}]\n")
        f.write(f"[JOBS={num_trabajos}]\n")
        f.write("[PT= " + " ; ".join(",".join(map(str,row)) for row in pt) + "]\n")
        f.write("[DD= " + ",".join(map(str,dd)) + "]\n")
        f.write("[W="  + ",".join(map(str,w))  + "]\n")
        f.write("[R="  + ",".join(map(str,r))  + "]\n")
        f.write(f"[EST={num_estaciones}]\n")
        f.write("[M_EST=" + ",".join(map(str,maquinas_por_estacion)) + "]\n")
        f.write(f"[BUFFER={buffer}]\n")


def NEH(instancia):
    """
    Heurístico NEH para el problema de flowshop (permuta–makespan).

    Parámetros:
      instancia: objeto que define
        - instancia.jobs      -> número de trabajos (n)
        - instancia.machines  -> número de máquinas (m)
        - instancia.pt        -> matriz pt[i][j] tiempo de proc. del trabajo j en máquina i
        - instancia.Cmax(seq) -> método que devuelve el makespan de la secuencia seq

    Retorna:
      seq: lista con el orden de los trabajos construido por NEH.
    """
    n = instancia.jobs
    m = instancia.machines

    # 1) Cálculo de carga total de cada trabajo
    sum_pt = [sum(instancia.pt[i][j] for i in range(m)) for j in range(n)]

    # 2) Ordenar trabajos por carga descendente
    lista_ordenada = sorted(range(n), key=lambda j: -sum_pt[j])

    # 3) Iniciar con los dos primeros trabajos, probando ambas permutaciones
    j1, j2 = lista_ordenada[0], lista_ordenada[1]
    mejor_seq = [j1, j2]
    if instancia.Cmax([j2, j1]) < instancia.Cmax(mejor_seq):
        mejor_seq = [j2, j1]

    # 4) Insertar sucesivamente el resto de trabajos
    for j in lista_ordenada[2:]:
        mejor_obj = float('inf')
        mejor_insercion = None
        # probar todas las posiciones posibles
        for pos in range(len(mejor_seq) + 1):
            candidato = mejor_seq[:pos] + [j] + mejor_seq[pos:]
            obj = instancia.Cmax(candidato)
            if obj < mejor_obj:
                mejor_obj = obj
                mejor_insercion = candidato
        mejor_seq = mejor_insercion

    return mejor_seq

import time, math

def IG(instancia, T, delta, max_time=0.5):
    # 1) Solución inicial NEH
    pi     = NEH(instancia)[:]
    obj    = instancia.Cmax(pi)
    pi_b   = pi[:]
    obj_b  = obj
    #max_time = (instancia.jobs * (instancia.machines/2) * 20) / 1000.0
    max_time = 0.5
    start = time.time()
    while time.time() - start < max_time:
        # 2) Destrucción
        pi_d = pi[:]
        pi_r = []
        for _ in range(delta):
            j = random.randrange(len(pi_d))
            pi_r.append(pi_d.pop(j))

        # 3) Construcción (reinserción NEH-style)
        for job in pi_r:
            best_cost = float('inf')
            best_seq  = None
            for pos in range(len(pi_d) + 1):
                cand = pi_d[:]
                cand.insert(pos, job)
                c    = instancia.Cmax(cand)
                if c < best_cost:
                    best_cost = c
                    best_seq  = cand
            pi_d = best_seq

        # 4) Candidato y evaluación
        pi_prima  = pi_d[:]
        obj_prima = instancia.Cmax(pi_prima)

        # 5) Aceptación
        if obj_prima < obj or random.random() <= math.exp(-(obj_prima - obj)/T):
            pi  = pi_prima[:]
            obj = obj_prima
            if obj < obj_b:
                pi_b   = pi[:]
                obj_b  = obj

    return pi_b, obj_b