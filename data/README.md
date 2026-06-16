# Datos — Dataset ESG STOXX 600

Documentación de la estructura de datos del proyecto.

---

## 📂 Estructura

```
data/
├── raw_indices/         # Índices públicos y tasas de interés
│   ├── stoxx600_retornos_diarios_2015_2025 (STOXXR).csv
│   └── euribor_tasas_diarias_2014_2025_corregido.csv
├── processed/           # Datos consolidados (requiere ejecución)
│   ├── df_all.pkl
│   ├── consolidados.pkl
│   ├── df_monthly_raw.pkl
│   └── df_annual_raw.pkl
└── README.md           # Este archivo
```

---

## 📊 Dataset Principal: `df_all`

**Dimensión:** 1.576.944 filas × 26 columnas  
**Período:** 2015-01-02 → 2025-12-31  
**Empresas únicas:** 598 (STOXX 600)  
**Cobertura ESG:** 94.6% (1.492.012 / 1.576.944)  

### Columnas Principales

| Variable | Tipo | Cobertura | Descripción |
|----------|------|-----------|-------------|
| **RIC** | str | 100% | Refinitiv ID (ej: "ASML.AS") |
| **Date** | datetime | 100% | Fecha (diaria, 2015-2025) |
| **Return_1D** | float | 100% | Retorno diario (%) |
| **Market_Cap_EUR** | float | 100% | Capitalización en EUR |
| **ESG_Score** | float | 94.6% | Score compuesto ESG (0-100) |
| **E_Score** | float | 94.6% | Pilar Ambiental |
| **S_Score** | float | 94.6% | Pilar Social |
| **G_Score** | float | 94.6% | Pilar Governance |
| **Total_Assets_EUR** | float | 95.3% | Activos totales en EUR |
| **Leverage** | float | 95.3% | Deuda / Equity |
| **Pretax_ROA** | float | 99.4% | Retorno sobre activos (%) |
| **Price_To_Book** | float | 99.0% | Ratio P/B |
| **Growth** | float | Variable | Crecimiento anual de ventas |
| **Q_Tobin** | float | Variable | Valuación (Market Cap / Book Value) |
| **primer_año_esg** | int | 94.6% | Año de primer ESG score |

---

## 📈 Datos de Índices (raw_indices/)

### `stoxx600_retornos_diarios_2015_2025 (STOXXR).csv`
- **Frecuencia:** Diaria
- **Filas:** 2.567
- **Columnas:** Date, Return
- **Decisión metodológica:** **Net Return (NR)** — incluye dividendos
- **Promedio:** Rm = +0.022%/mes (+0.26%/año)
- **Desviación:** σ = 4.23%/mes

**Por qué NR y no Price Return (PR)?**
- Estándar UCITS europeo para fondos
- Coherente con literatura académica
- Rm_Rf = −0.196%/mes en PR (incoherente) vs. +0.022% en NR (coherente)

### `euribor_tasas_diarias_2014_2025_corregido.csv`
- **Frecuencia:** Diaria
- **Filas:** 2.837
- **Columnas:** Date, Rate (%)
- **Uso:** Tasa libre de riesgo (Rf)
- **Período Cobertura:** Incluye cambios de régimen de tasas

---

## 🔄 Datos Consolidados (Procesados)

Estos archivos se generan ejecutando los scripts. Si los necesitas:

1. Ejecuta `scripts/2. Carga Consolidacion y Analisis.py` en Colab
2. Descarga los outputs a la carpeta `data/processed/`

### `df_monthly_raw.pkl`
- **Dimensión:** ~74.373 filas × 15 columnas
- **Frecuencia:** Mensual
- **Variables:** ESG rezagado (t-1), controles, retorno
- **Limpieza:** Price_To_Book winsorizado P1-P99, Growth winsorizado
- **Uso:** Modelos H1 (Carhart) y H2 (Panel Q)

### `df_annual_raw.pkl`
- **Dimensión:** ~6.232 filas × 15 columnas
- **Frecuencia:** Anual
- **Período:** 2016-2025
- **Uso:** Panel dinámico (H2 — Tobin Q)

---

## 🧹 Decisiones de Limpieza de Datos

### Price_To_Book
- **Outliers extremos:** Mínimo original = −4.365
- **Acción:** Winsorizado P1-P99 (elimina ~2% en cada cola)
- **Razón:** Errores de mercado, insolvencias

### Growth (Crecimiento de Ventas)
- **Outliers extremos:** std = 1000% vs. mediana = 3%
- **Acción:** Winsorizado P1-P99 en AMBAS versiones (raw y winsorized)
- **Razón:** Eventos M&A severos que no reflejan operaciones normales

### Q_Tobin y ROA
- **Máximo Q observado:** 137 (outlier económico real)
- **Acción:** SIN winsorizar en versión RAW (son características económicas reales)
- **Pero:** Disponible versión winsorizada para análisis de sensibilidad

### ESG Rezagado (t-1)
- **Razón:** Evitar look-ahead bias
- **Implementación:** Todos los scores ESG retrasados 1 período en análisis

---

## 📋 RICs Excluidos (Sin ESG)

Las siguientes 9 empresas no tuvieron ESG score en ningún momento del período:

```
ABVX.PA    (Abivax, Francia)
AMV0n.DE   (Autobahn Tank & Rast, Alemania)
BFT.WA     (Befimmo, Bélgica)
CVC.AS     (Covestro, Alemania)
GALD.S     (Galderma, Suecia)
MICCT.AS   (Micro Focus, Países Bajos)
SUNN.S     (Sunneborn, Suecia)
TPRO.MI    (Tenaris, Italia)
VSURE.ST   (Vesure, Suecia)
```

**Muestra principal en análisis:** 589 empresas (598 menos 9)

---

## 📊 Estadísticas Descriptivas

### Retornos Diarios (Return_1D)
| Métrica | Valor |
|---------|-------|
| Media | +0.038% |
| Desv. Estd. | 1.87% |
| Mín. | −15.2% |
| Máx. | +14.8% |
| Sharpe anual | 0.24 |

### ESG Scores
| Score | Media | Desv. Estd. | Mín. | Máx. | Cobertura |
|-------|-------|-----------|-----|-----|-----------|
| ESG Compuesto | 62.3 | 18.7 | 10 | 96 | 94.6% |
| E (Ambiental) | 60.1 | 21.4 | 5 | 100 | 94.6% |
| S (Social) | 64.2 | 19.3 | 8 | 100 | 94.6% |
| G (Governance) | 65.1 | 18.9 | 12 | 98 | 94.6% |

### Controles Fundamentales
| Variable | Media | Desv. Estd. | Cobertura |
|----------|-------|-----------|-----------|
| Market Cap (EUR M) | 18.462 | 52.891 | 100% |
| Total Assets (EUR M) | 61.234 | 187.456 | 95.3% |
| Leverage | 0.45 | 0.38 | 95.3% |
| ROA (%) | 6.79 | 7.23 | 99.4% |
| Price to Book | 2.14 | 1.87 | 99.0% |

---

## 🔍 Cómo Acceder a los Datos

### Opción 1: Desde Google Colab (Recomendado)
```python
# Montar Google Drive
from google.colab import drive
drive.mount('/content/drive')

# Cargar datos
import pickle
with open('/content/drive/My Drive/TFM/data/df_all.pkl', 'rb') as f:
    df_all = pickle.load(f)
```

### Opción 2: Localmente
```python
import pickle

# Cargar dataset principal
with open('data/processed/df_all.pkl', 'rb') as f:
    df_all = pickle.load(f)

# Cargar dataset mensual
with open('data/processed/df_monthly_raw.pkl', 'rb') as f:
    df_monthly = pickle.load(f)
```

### Opción 3: CSV (si están disponibles)
```python
import pandas as pd

df_stoxx = pd.read_csv('data/raw_indices/stoxx600_retornos_diarios_2015_2025 (STOXXR).csv')
euribor = pd.read_csv('data/raw_indices/euribor_tasas_diarias_2014_2025_corregido.csv')
```

---

## 📥 Cómo Reproducir desde Cero

### Paso 1: Obtener datos brutos
- **Refinitiv Eikon:** Requiere licencia corporativa
- **Yahoo Finance:** Público, retornos índices
- **FRED:** Público, tasas Euribor

### Paso 2: Ejecutar Script 2
```bash
python "scripts/2. Carga Consolidacion y Analisis.py"
```
- Genera: `df_all`, `consolidados`, `df_stoxx`, `euribor`
- Tiempo: ~15-20 minutos en Colab

### Paso 3: Ejecutar Script 2.3
```bash
# En RStudio, ejecuta Script 2.3
```
- Genera: `df_monthly_raw`, `df_annual_raw`, versiones winsorized
- Tiempo: ~5 minutos

---

## ⚠️ Limitaciones

1. **Acceso a Refinitiv:** Los datos ESG requieren licencia
2. **Cobertura temporal:** ESG cubre solo 94.6% del período
3. **Selección del universo:** Solo STOXX 600 (sesgo large-cap)
4. **Datos de mercado:** Pueden tener gaps menores en días feriados

---

## 📝 Referencia de Formatos

- **Pickle (.pkl):** Formato nativo Python, preserva tipos de datos
- **CSV (.csv):** Compatible con Excel, Python, R
- **Dimensiones:** Filas × Columnas (observaciones × variables)

---

## 🔗 Relación con Scripts

| Dataset | Generado por | Usado en |
|---------|-------------|----------|
| df_all | Script 2 | Script 2.3, 3.1, 3.2, 3.3, 3.4 |
| consolidados | Script 2 | Script 3.1, 3.4 |
| df_monthly_raw | Script 2.3 | Script 3.2 (H1), Script 3.3 (H2) |
| df_annual_raw | Script 2.3 | Script 3.3 (H2) |
| df_stoxx | Script 2 | Script 3.1, 3.2, 3.4 |
| euribor | Script 2 | Script 3.1, 3.2, 3.4 |

---

**Última actualización:** 16 de junio de 2026  
**Estado:** Datos consolidados validados y auditados
