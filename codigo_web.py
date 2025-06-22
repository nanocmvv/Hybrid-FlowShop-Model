# -*- coding: utf-8 -*-
"""
Created on Fri Apr 11 11:08:42 2025

@author: 34608
"""

from scheptk.scheptk import Model 
from scheptk.util import read_tag
from funciones_aux_web import calcular_tiempo_estacion, calcular_tiempo_inicio_siguiente_estacion

class HybridFlowShop(Model):
    def __init__(self, archivo):
        self.machines = read_tag(archivo, 'MACHINES')
        self.jobs = read_tag(archivo, 'JOBS')
        self.pt = read_tag(archivo, 'PT')
        self.dd = read_tag(archivo, 'DD')
        self.w = read_tag(archivo, 'W')
        self.r = read_tag(archivo, 'R')
        self.est = read_tag(archivo, 'EST')
        self.m_est = read_tag(archivo, 'M_EST')
        self.buffer = read_tag(archivo, 'BUFFER')  # ⚠️ Muy importante

    def ct(self, secuencia):
        ct = [[0 for _ in range(self.jobs)] for _ in range(self.machines)]
        disp = [[0 for _ in range(self.m_est[k])] for k in range(self.est)]
    
        self.buffer_log = [[[] for _ in range(self.m_est[k])] for k in range(self.est - 1)]
        self.bloqueos = [[] for _ in range(self.machines)]
    
        for j, job in enumerate(secuencia):
            tiempo_previo = self.r[job]
            for k in range(self.est):
                base = sum(self.m_est[:k])
                pt_est = self.pt[base: base + self.m_est[k]]
    
                min_fin, maq_local = calcular_tiempo_estacion(pt_est, disp[k], tiempo_previo, job)
                ct[base + maq_local][j] = min_fin
    
                if k < self.est - 1:
                    base_sig = sum(self.m_est[:k+1])
                    pt_sig = self.pt[base_sig: base_sig + self.m_est[k+1]]
                    ini_sig_est, maq_sig = calcular_tiempo_inicio_siguiente_estacion(pt_sig, disp[k+1], min_fin, job)
    
                    t_ent = min_fin
                    t_sal = max(min_fin, ini_sig_est)
    
                    if self.buffer == 0:
                        if ini_sig_est > min_fin:
                            maquina_global = base + maq_local
                            self.bloqueos[maquina_global].append((job, min_fin, ini_sig_est))
                        disp[k][maq_local] = t_sal
                        tiempo_previo = t_sal
    
                    elif self.buffer >= 1:
                        # Buscar el primer hueco libre en el buffer a partir de t_ent
                        ocupaciones = [
                            (t_ini, t_fin) for (_, t_ini, t_fin) in self.buffer_log[k][maq_local]
                            if not (t_sal <= t_ini or t_ent >= t_fin)
                        ]
                        if len(ocupaciones) < self.buffer:
                            if t_sal > t_ent:
                                self.buffer_log[k][maq_local].append((job, t_ent, t_sal))
                            disp[k][maq_local] = t_ent
                            disp[k+1][maq_sig] = t_sal
                            tiempo_previo = t_sal
                        else:
                            # Buscar cuándo se libera hueco en el buffer
                            t_libre_buffer = t_ent
                            while True:
                                ocupando = 0
                                for (_, t_ini, t_fin) in self.buffer_log[k][maq_local]:
                                    if t_ini < t_libre_buffer < t_fin:
                                        ocupando += 1
                                if ocupando < self.buffer:
                                    break
                                t_libre_buffer += 1
    
                            t_fin_bloqueo = min(ini_sig_est, t_libre_buffer)
    
                            maquina_global = base + maq_local
                            if t_fin_bloqueo > min_fin:
                                self.bloqueos[maquina_global].append((job, min_fin, t_fin_bloqueo))
    
                            # Decidir si entra al buffer o a la máquina directamente
                            if t_libre_buffer < ini_sig_est:
                                # Entra al buffer
                                self.buffer_log[k][maq_local].append((job, t_fin_bloqueo, ini_sig_est))
                                disp[k][maq_local] = t_fin_bloqueo
                                disp[k+1][maq_sig] = ini_sig_est
                                tiempo_previo = ini_sig_est
                            else:
                                # Va directo a la siguiente estación
                                disp[k][maq_local] = ini_sig_est
                                tiempo_previo = ini_sig_est
                                disp[k+1][maq_sig] = ini_sig_est
    
                    else:
                        # BUFFER infinito
                        disp[k][maq_local] = min_fin
                        disp[k+1][maq_sig] = t_sal
                        tiempo_previo = t_sal
                else:
                    disp[k][maq_local] = min_fin
                    tiempo_previo = min_fin
    
        return ct, secuencia

