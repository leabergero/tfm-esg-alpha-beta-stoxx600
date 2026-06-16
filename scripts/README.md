# Scripts del TFM

Documentación de los scripts utilizados en el análisis.

## 📋 Orden de Ejecución

### **Fase 1: Carga y Consolidación de Datos**

#### `2. Carga Consolidacion y Analisis.py` (Principal)
- **Lenguaje:** Python
- **Plataforma:** Google Colab (recomendado) o Jupyter local
- **Tiempo estimado:** 15-20 minutos
- **Outputs:**
  - `df_all`: 1.576.944 filas × 26 columnas (dataset completo consolidado)
  - `consolidados`: DataFrame con datos mensuales listos para análisis
  - `df_stoxx`: Retornos diarios del STOXX 600
  - `euribor`: Tasas de interés libres de riesgo
  - Variable `STOXX_VERSION`: etiqueta del índice utilizado

**Decisión metodológica:** Utiliza STOXX 600 **Net Return (NR)**, no Price Return.

**Requisitos:**
- Acceso a Refinitiv Eikon API (requiere licencia)
- Credenciales configuradas en Colab

---

#### `2.3_Preparacion_Datos_H1_H2_H3.txt` (Preparación)
- **Lenguaje:** R
- **Plataforma:** RStudio
- **Tiempo estimado:** 5 minutos (solo preparación)
- **Inputs:** `df_consolidated` de Script 2
- **Outputs:**
  - `df_monthly_raw`: ~74.373 obs × 15 cols (mensual, sin winsorización)
  - `df_monthly_w`: ídem, con winsorización P1-P99
  - `df_annual_raw`: ~6.232 obs × 15 cols (anual)
  - `df_annual_w`: ídem winsorizado

**Limpiezas aplicadas:**
- Price_To_Book: outliers extremos removidos (P1-P99)
- Growth: winsorizado en ambas versiones (M&A events)
- Q_Tobin y ROA: sin winsorizar en RAW (economía real)
- ESG rezagado t-1 (anti look-ahead bias)

---

### **Fase 2: Construcción de Factores**

#### `3.1_Construccion_Factores_Carhart.txt` (Factores Fama-French)
- **Lenguaje:** R
- **Plataforma:** RStudio
- **Tiempo estimado:** 5 minutos
- **Inputs:** `consolidados` de Script 2 + índices (STOXX 600, Euribor)
- **Outputs:**
  - `df_factors`: 132 meses × 8 cols (Rm_Rf, SMB, HML, WML + auxiliares)
  - `df_factors_4f`: 120 meses con los 4 factores completos

**Factores construidos:**
| Factor | Media/mes | Desv anual | Sharpe | Significancia |
|--------|-----------|-----------|--------|---------------|
| Rm_Rf  | +0.022%   | 4.23%     | +0.018 | Positivo con NR ✅ |
| SMB    | −0.083%   | 1.68%     | −0.171 | Grandes > pequeñas |
| HML    | +0.077%   | 3.84%     | +0.070 | Valor > crecimiento |
| WML    | +0.282%   | 3.96%     | +0.247 | **Factor más fuerte** |

**Nota:** Estos factores se construyen **desde el mismo universo STOXX 600** (no Ken French internacional) para coherencia interna.

---

### **Fase 3: Análisis de Hipótesis**

#### `3.2_H1_Regresiones_Carhart.txt` (H1: Green Premium)
- **Lenguaje:** R
- **Plataforma:** RStudio
- **Tiempo estimado:** 10 minutos
- **Inputs:** `consolidados` + `df_factors_4f`
- **Outputs:**
  - Tabla FF: alphas por quintil + spread L-S
  - Diagnósticos (normalidad, autocorrelación)
  - 7 gráficos: series temporales, betas, residuos, etc.
  - Summary tables para anexo

**Modelo:** Carhart 4 Factores + Newey-West (3 lags)
**Universo:** ~107 empresas/quintil, 131 meses portafolios, 120 meses regresión

**Resultado H1:**
```
ESG Score (L-S)
α = −0.5988%/mes (−6.95%/año)
t-NW = −5.218 ***
Decisión: RECHAZAR H1
```

**Interpretación:** Las mejores empresas ESG (Q1) generan menos retorno que las peores (Q5). Patrón monotónico Q1→Q5. Coherente con "Green Premium" (preferencia inversor) y riesgo brown no capturado.

---

#### `3.3_H2_Panel_TobinQ.txt` (H2: ESG y Valuación)
- **Lenguaje:** R
- **Plataforma:** RStudio
- **Tiempo estimado:** 5 minutos
- **Inputs:** `df_annual_raw` y `df_annual_w`
- **Outputs:**
  - Test Hausman (FE vs RE)
  - Diagnósticos: AR(1), Breusch-Pagan, Pesaran CD
  - Matriz 4 especificaciones (1way RAW, 1way WINS, 2way RAW, 2way WINS)
  - 4 gráficos: forest, binscatter, series temporales, distribuciones

**Modelo:** Panel Dinámico con Driscoll-Kraay (FE + spatial-temporal correlación)
**Muestra:** 5.329 obs, 586 empresas, 2016-2025

**Resultado H2:**
```
Modelo Principal (2way RAW): β1 = −0.00704*** (p < 0.001)
Pero con WINS: β1 = −0.00309 (t = −2.18)
Conclusión: SIN EFECTO ROBUSTO en modelo pre-especificado
```

**Hallazgo secundario:** ESG compuesto y Pilar G → β1 NEGATIVO within-year robusto (Green Premium). Coherente con H1.

---

#### `3.4_H3_MarkovSwitching_CAPM.txt` (H3: ESG en Crisis)
- **Lenguaje:** R
- **Plataforma:** RStudio
- **Tiempo estimado:** 10 minutos
- **Inputs:** `consolidados` + índices
- **Outputs:**
  - Regímenes MS(2): Calma (μ=+0.08%/día) vs. Crisis (μ=−0.19%/día)
  - Betas condicionales por cartera y régimen
  - 3 gráficos: regímenes, betas por estado, spreads L-S

**Diseño 2 etapas:**
1. **Etapa 1:** MS(2) en retornos diarios STOXX 600 NR → detecta regímenes comunes
2. **Etapa 2:** CAPM condicional mensual → β condicional por cartera

**Resultado H3:**
```
ESG Score, Q5 (peor ESG):
δ (Δβ crisis−calma) = +0.211 (p = 0.0024***)
Conclusión: HALLAZGO ESPECULAR

Q1 (mejor ESG): β estable ~1.05 en ambos regímenes
Q5 (peor ESG): β amplifica en crisis (1.05 → 1.26)
```

**Interpretación:** Las empresas low-ESG incrementan su riesgo sistemático en mercados bajistas (riesgo "brown" materializado). Las high-ESG proporcionan protección relativa.

---

#### `A1_Comparacion_Indices_STOXX600.txt` (Anexo: Índices)
- **Lenguaje:** R
- **Plataforma:** RStudio
- **Tiempo estimado:** 2 minutos
- **Outputs:** Tablas y gráficos comparativos PR vs NR vs GR

**Justificación:** Valida la elección de STOXX 600 Net Return (NR):
- Tests estadísticos: t > 22, p < 1e-100 (diferencias significativas)
- Rm_Rf con PR = −2.35%/año (incoherente)
- Rm_Rf con NR = +0.022%/mes (coherente con mercado)
- Spread H1 invariante PR → NR (prueba de robustez)

---

### **Análisis Auxiliares**

#### `analisis_rics_sin_esg.py`
- **Lenguaje:** Python
- **Propósito:** Identificar y documentar los 9 RICs sin cobertura ESG
- **Output:** Tabla de empresas excluidas del análisis
- **Uso:** Nota sobre limitaciones del dataset

**RICs excluidos:** `ABVX.PA`, `AMV0n.DE`, `BFT.WA`, `CVC.AS`, `GALD.S`, `MICCT.AS`, `SUNN.S`, `TPRO.MI`, `VSURE.ST`

---

## 🛠️ Requisitos Técnicos

### Python
- pandas, numpy, scipy, statsmodels
- yfinance (índices públicos)
- refinitiv-data (acceso API, requiere licencia)

### R (≥4.0)
- tidyverse
- lmtest, sandwich (diagnósticos)
- plm (panel regressions)
- markovchain (Markov-Switching)
- ggplot2, gridExtra (visualización)
- linearmodels (FE + DK)

---

## 📊 Variables Clave en los Datasets

### `df_consolidated` (Script 2 output)
```
RIC, Date, Return_1D, Market_Cap_EUR, ESG_Score, E_Score, S_Score, G_Score,
Total_Assets_EUR, Leverage, Pretax_ROA, Price_To_Book, Growth, 
Q_Tobin, primer_año_esg, ...
```

### `df_monthly_raw` / `df_annual_raw` (Script 2.3 output)
```
RIC, Year, Month (o Year para annual),
ESG_Score_lag1, E_Score_lag1, S_Score_lag1, G_Score_lag1,
Size, Leverage, Growth, Q_Tobin, ROA, Return_portfolio, ...
```

### `df_factors` (Script 3.1 output)
```
Date, Rm_Rf, SMB, HML, WML, Market_Cap_lag, ... (132 meses)
```

---

## ⚠️ Notas Importantes

1. **STOXX_VERSION:** Variable definida en Script 2, viaja a través de toda la sesión. Permite cambiar fácilmente de índice comentando/descomentando una línea.

2. **Reproducibilidad:** Los datos brutos requieren acceso a Refinitiv Eikon. Los datos consolidados (`data/processed/`) ya están precalculados.

3. **Sensibilidad:** En H2, los resultados cambiar significativamente si se incluyen/excluyen outliers → ver matriz de 4 especificaciones.

4. **Validación:** Todos los resultados han sido auditados en el Notebook completo de Colab (3.2 MB, con outputs).

---

## 🔗 Referencias

- Fama & French (1993): "Common Risk Factors in the Returns on Stocks and Bonds"
- Carhart (1997): "On Persistence in Mutual Fund Performance"
- Newey & West (1987): "A Simple, Positive Semi-Definite, Heteroskedasticity and Autocorrelation Consistent Covariance Matrix"
- Driscoll & Kraay (1998): "Consistent Covariance Matrix Estimation with Spatially Dependent Panel Data"
- Pástor, Stambaugh & Taylor (2021): "Sustainable Investing in Equilibrium"
- Bolton & Kacperczyk (2021): "Do Investors Care About Carbon Risk?"

---

**Última actualización:** 16 de junio de 2026  
**Auditoría:** ✅ Completa — resultados verificados en Colab
