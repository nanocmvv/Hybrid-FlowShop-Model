from flask import Flask, render_template, request, send_from_directory, abort
import os, io, contextlib, random

from funciones_aux_web import (
    generar_instancia_aleatoria,
    generar_instancia_personalizada,
    mostrar_bloqueos,
    mostrar_buffer_log,
    S_random,
    IG,
    gantt_completo
)
from codigo_web import HybridFlowShop

app = Flask(__name__)

# Directorios para instancias e imágenes
INST_DIR   = "instancias"
STATIC_DIR = os.path.join(app.root_path, "static")
os.makedirs(INST_DIR, exist_ok=True)
os.makedirs(STATIC_DIR, exist_ok=True)

# Capacidades de buffer a probar
CAPACITIES = [0, 1, 2, 100]

def procesar_con_contexts(path_inst):
    inst = HybridFlowShop(path_inst)
    base_jobs = list(range(inst.jobs))

    # Definimos las tres secuencias
    seqs = {
        "Ordenada": base_jobs,
        "Aleatoria": S_random(base_jobs),
        "IG": IG(inst, T=1.0, delta=2)[0]
    }

    contexts = {}
    for name, seq in seqs.items():
        contexts[name] = {}
        for cap in CAPACITIES:
            modelo = HybridFlowShop(path_inst)
            modelo.buffer = cap  # Ajustamos la capacidad

            # Gantt de producción
            prod_img = f"{name.lower()}_buf{cap}_prod.png"
            modelo.print_custom_schedule(seq, filename=os.path.join(STATIC_DIR, prod_img))

            # Gantt completo
            comp_img = f"{name.lower()}_buf{cap}_comp.png"
            gantt_completo(
                modelo.create_schedule(seq),
                modelo.buffer_log,
                modelo.bloqueos,
                filename=os.path.join(STATIC_DIR, comp_img)
            )

            # Capturar texto de bloqueos
            with io.StringIO() as buf:
                with contextlib.redirect_stdout(buf):
                    mostrar_bloqueos(modelo)
                bloq = buf.getvalue()

            # Capturar texto de buffers
            with io.StringIO() as buf:
                with contextlib.redirect_stdout(buf):
                    mostrar_buffer_log(modelo)
                buffs = buf.getvalue()

            contexts[name][cap] = {
                "sequence": seq,
                "prod_img": prod_img,
                "comp_img": comp_img,
                "cmax": modelo.Cmax(seq),
                "bloqueos": bloq,
                "buffers": buffs
            }

    # Información de la instancia
    inst2 = HybridFlowShop(path_inst)
    info = {
        "machines": inst2.machines,
        "jobs":     inst2.jobs,
        "pt":       inst2.pt,
        "dd":       inst2.dd,
        "w":        inst2.w,
        "r":        inst2.r,
        "est":      inst2.est,
        "m_est":    inst2.m_est,
        "buffer":   inst2.buffer
    }

    return {
        "contexts": contexts,
        "instancia_info": info,
        "capacities": CAPACITIES
    }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generar_random', methods=['POST'])
def generar_random():
    buf = int(request.form['buffer'])
    file_inst = os.path.join(INST_DIR, "aleatoria.txt")
    generar_instancia_aleatoria(file_inst, buf)
    ctx = procesar_con_contexts(file_inst)
    return render_template('index.html', **ctx)

@app.route('/generar_custom', methods=['POST'])
def generar_custom():
    try:
        ne  = int(request.form['num_estaciones'])
        me  = [int(x) for x in request.form['m_est'].split(',')]
        nt  = int(request.form['num_trabajos'])
        buf = int(request.form['buffer'])

        file_inst = os.path.join(INST_DIR, "personalizada.txt")
        generar_instancia_personalizada(file_inst, ne, me, nt, buf)
        ctx = procesar_con_contexts(file_inst)
        return render_template('index.html', **ctx)
    except Exception as e:
        return abort(400, f"Error en formulario personalizado: {e}")

@app.route('/static/<filename>')
def serve_image(filename):
    return send_from_directory(STATIC_DIR, filename)

if __name__ == '__main__':
    app.run(debug=True)
