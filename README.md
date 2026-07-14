# TFM: Impacto del Desempeño ESG en Alpha y Beta — STOXX 600

**Autor:** Leandro R. Bergero  
**Universidad:** BSM - UPF (Msc Finance & Banking)  
**Período:** 2015-2025  
**Última actualización:** julio 2026

## 📋 Descripción

Este repositorio contiene el análisis completo de un Trabajo Fin de Master (TFM) que examina el impacto del desempeño ESG (Environmental, Social, Governance) en los retornos anormales (Alpha) y el riesgo sistemático (Beta) de 598 empresas cotizadas en el STOXX 600.

## 🎯 Hipótesis de Investigación

### **H1: Green Premium** — ¿Existe Alpha negativo en empresas con bajo ESG?
- Metodología: Carhart 4 Factores
- Resultado: **RECHAZADA** — Empresas de mejor ESG generan alpha POSITIVO (−0.60%/mes, Q1−Q5)

### **H2: ESG y Valuación** — ¿Afecta el ESG a la valuación (Tobin Q)?
- Metodología: Panel Dinámico (FE + Driscoll-Kraay)
- Resultado: **SIN EFECTO** en modelo principal, pero sensibilidad robusta en 2-way specifications

### **H3: ESG en Crisis** — ¿Se amplifica el beta de empresas low-ESG en mercados bajistas?
- Metodología: Markov-Switching CAPM (2 etapas)
- Resultado: **RECHAZADA** (el ESG alto no reduce el beta en crisis) — hallazgo especular: Q5 (bajo ESG) amplifica beta en crisis (+0.21, p<0.01), significativo solo bajo la definición de régimen MS
- **Robustez (respuesta al tribunal):** el rechazo de H3 es robusto en 3 modelos de régimen (MS, GARCH(1,1)-umbral, LSTAR); el hallazgo especular queda como evidencia sugestiva dependiente de la definición de régimen. Ver `scripts/H3_Robustez_Modelos/` y las celdas finales del notebook.

## 📂 Estructura del Repositorio

```
tfm-esg-alpha-beta-stoxx600/
├── README.md                          # Este archivo
├── requirements.txt                    # Dependencias Python
├── LICENSE                             # Licencia CC-BY 4.0
│
├── thesis/
│   ├── TFM_Bergero_Leandro_Desempeño_ESG_Stoxx600.docx   # Tesis final (Word)
│   └── TFM_Bergero_Leandro_Desempeño_ESG_Stoxx600.pdf    # Tesis final (PDF)
│
├── notebooks/
│   ├── TFM_Impacto_del_desempeño_ESG_..._.ipynb  # Notebook Colab ejecutado (incluye robustez H3)
│   ├── TFM Impacto ... .ipynb - Colab.pdf        # Impresión PDF del notebook ejecutado
│   └── README.md                       # Instrucciones
│
├── scripts/
│   ├── SCRIPT DESCARGA REFINITIV.py               # Descarga de datos crudos (Refinitiv Codebook)
│   ├── limpiar_euribor.py                         # Limpieza de la serie Euribor
│   ├── 2. Carga Consolidacion y Analisis.py       # Script principal — data consolidada
│   ├── 2.3_Preparacion_Datos_H1_H2_H3.txt         # Preparación para análisis
│   ├── 3.1_Construccion_Factores_Carhart.txt      # Factores Fama-French + WML
│   ├── 3.2_H1_Regresiones_Carhart.txt             # H1 — Carhart 4F + CAPM
│   ├── 3.3_H2_Panel_TobinQ.txt                    # H2 — Panel dinámico Tobin Q
│   ├── 3.4_H3_MarkovSwitching_CAPM.txt            # H3 — Markov-Switching CAPM
│   ├── A1_Comparacion_Indices_STOXX600.txt        # Anexo A1 — PR vs NR vs GR
│   ├── analisis_rics_sin_esg.py                   # Análisis de RICs sin data ESG
│   ├── H3_Robustez_Modelos/                       # Robustez H3 (respuesta al tribunal)
│   │   ├── A2_H3_Alt1_GARCH_Umbral.txt            #   Alt. 1 — GARCH(1,1)-t + umbral P75
│   │   ├── A3_H3_Alt2_LSTAR.txt                   #   Alt. 2 — CAPM transición suave (LSTAR)
│   │   ├── A4_H3_Contraste_Modelos.txt            #   Contraste: kappa, RCM, bootstrap, AIC
│   │   ├── A5_H3_Direccional_Bajista.txt          #   Diagnóstico direccional/bajista
│   │   └── README.md
│   └── README.md                       # Documentación de scripts
│
├── presentation/
│   ├── Infografía TFM - Impacto ESG en Alpha y Beta.pdf
│   ├── infografia_linkedin.html        # Versión web interactiva
│   └── README.md                       # Instrucciones
│
└── data/
    ├── raw_indices/                    # Índices y tasa libre de riesgo
    │   ├── stoxx600_retornos_diarios_2015_2025 (STOXXR).csv   # Net Return — ACTIVO
    │   ├── stoxx600_retornos_diarios_2015_2025 (SXXGR).csv    # Gross Return (sensibilidad)
    │   ├── stoxx600_retornos_diarios_2015_2025.csv            # Price Return (Anexo A1)
    │   ├── euribor_tasas_diarias_2014_2025_corregido.csv      # Rf — ACTIVO
    │   └── euribor_tasas_diarias_2014_2025.csv                # Rf sin corregir (trazabilidad)
    ├── raw/                            # Descargas anuales de Refinitiv (2015-2025)
    │   ├── stoxx600_DEFENSA_YYYY.csv              # Panel diario base por año
    │   ├── stoxx600_PTB_CONSOLIDADO_YYYY.csv      # Price-to-Book consolidado
    │   ├── stoxx600_PTB_y_ROAS_diario_YYYY.csv    # PTB y ROA diarios
    │   └── RICS_FALTANTES_PTB_ROA.csv
    ├── consolidados/                   # CONSOLIDADO_YYYY.csv — insumo directo del notebook
    └── README.md                       # Instrucciones de reproducción
```

## 🔧 Instalación y Reproducción

### Requisitos
- Python 3.8+
- R 4.0+ (para análisis estatístico, opcional)
- Google Colab (recomendado para facilidad)

### Instalar dependencias Python

```bash
pip install -r requirements.txt
```

### Ejecutar análisis completo

**Opción 1: Google Colab (recomendado)**
1. Abre `notebooks/TFM_Impacto_del_desempeño_ESG_..._.ipynb` en Google Colab
2. Ejecuta celda por celda — todas las salidas están precalculadas

**Opción 2: Localmente**
1. Asegúrate de tener acceso a datos (Refinitiv Eikon, Yahoo Finance, etc.)
2. Ejecuta `scripts/2. Carga Consolidacion y Analisis.py`
3. Luego `2.3_Preparacion_Datos_H1_H2_H3.txt` en RStudio
4. Finalmente scripts 3.1 → 3.2 → 3.3 → 3.4

## 📊 Estadísticas del Dataset

| Métrica | Valor |
|---------|-------|
| Empresas únicas | 598 (STOXX 600) |
| Observaciones totales | 1.576.944 filas |
| Cobertura ESG | 94.6% |
| Período | 2015-01-02 → 2025-12-31 |
| Frecuencia análisis | Diaria, mensual, anual |

## 📈 Hallazgos Clave

### **Resultado Principal (H1)**
Las empresas del **Q1 (mejor ESG)** generan alpha positivo de **+0.34%/mes** vs. Q5 (peor ESG) que genera **+0.94%/mes**.

**Spread L-S: −0.60%/mes (t = −5.22***, p < 0.001)**

Controlando por factores Fama-French, la brecha se mantiene robusta → indica que inversores pagan un premio por ESG bajo (green premium paradoja).

### **Resultado Secundario (H3)**
En períodos de estrés (Markov Crisis State):
- Q1 estable: β ≈ 1.05
- Q5 amplifica: β = 1.26 (+0.21, p = 0.0024***)

Evidencia de riesgo "brown" no capturado en modelos estándar.

## 📚 Metodología Resumida

| Hipótesis | Enfoque | Frecuencia | Modelo | Muestra |
|-----------|---------|-----------|--------|---------|
| **H1** | Cross-section | Mensual | Carhart 4F + Newey-West | 107 emp/quintil |
| **H2** | Panel | Anual | FE + Driscoll-Kraay | 586 emp, 2016-2025 |
| **H3** | Tiempo | Mensual | MS(2) + CAPM condicional | 2.567 días |

## 🔍 Datos Utilizados

### Fuentes de Datos
- **Retornos de empresas:** Refinitiv Eikon (Python SDK)
- **Scores ESG:** Refinitiv ESG API
- **STOXX 600:** Yahoo Finance / Refinitiv
- **Euribor:** FRED (Banco de la Reserva Federal de St. Louis)

### Decisión Metodológica Clave: STOXX 600 Net Return (NR)
Se utiliza STOXX 600 **Net Return** en lugar de Price Return:
- Incluye dividendos (estándar UCITS europeo)
- Rm_Rf = +0.022%/mes (vs. −0.196%/mes en PR)
- El spread H1 es invariante con cambio PR → NR (prueba de robustez)

## 📖 Cómo Leer Este Repositorio

1. **Para el trabajo completo:** lee la tesis final en `thesis/` (Word y PDF)
2. **Para una visión rápida:** lee esta sección y consulta `presentation/`
3. **Para metodología:** ve a `scripts/` y lee comentarios de cada archivo
4. **Para reproducción:** sigue instrucciones en `notebooks/README.md` — todas las bases de datos necesarias están incluidas en `data/`
5. **Para data:** revisa `data/README.md` para la descripción de cada archivo

## 📝 Citas

Si utilizas este trabajo, por favor cita:

```bibtex
@mastersthesis{bergero2026esg,
  author = {Bergero, Leandro},
  title = {Impacto del desempeño ESG en Alpha y Beta de empresas del STOXX 600},
  school = {BSM UNIV. POMPEU FABRA, Master en Finanzas y Banca},
  year = {2026}
}
```

## 📄 Licencia

Este proyecto está bajo licencia **Creative Commons Attribution 4.0** (CC-BY 4.0).

- **Eres libre de:** compartir, adaptar, redistribuir
- **Con la condición de:** dar crédito al autor original (Leandro Bergero)

Consulta `LICENSE` para detalles completos.

## 🤝 Contribuciones

Si encuentras errores o tienes sugerencias, abre un **Issue** o contacta a [estudiocontablebergero+github@gmail.com](mailto:estudiocontablebergero+github@gmail.com).

## 📞 Contacto

- **Email:** estudiocontablebergero+github@gmail.com
- **LinkedIn:** [linkedin.com/in/leandro-bergero](https://linkedin.com/in/leandro-raul-bergero)

---

**Última actualización:** 14 de julio de 2026  
**Estado:** Tesis final entregada — análisis completo, robustez H3 incluida, bases de datos publicadas
