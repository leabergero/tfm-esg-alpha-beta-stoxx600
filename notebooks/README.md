# Notebooks — Google Colab

## 📓 Notebook Principal

### `TFM_Impacto_del_desempeño_ESG_en_la_Rentabilidad_y_el_Riesgo_de_las_empresas_del_STOXX_600_.ipynb`

**Tamaño:** 3.2 MB (con outputs ejecutados)  
**Plataforma:** Google Colab (recomendado)  
**Tiempo de ejecución:** ~25 minutos  
**Última ejecución auditada:** 11 de junio de 2026  

---

## 🚀 Cómo Ejecutar

### Opción 1: Google Colab (Recomendado)

1. Abre el archivo `.ipynb` en Google Colab:
   - Sube el archivo a Google Drive
   - O haz clic derecho → "Abrir con" → "Google Colaboratory"

2. Ejecuta celda por celda (`Shift + Enter`)

3. **Requisitos de autenticación:**
   ```python
   # Google Drive (para datos)
   from google.colab import auth
   auth.authenticate_user()
   
   # Refinitiv Eikon (credenciales opcionales)
   # Requiere acceso a cuenta Refinitiv con licencia
   ```

### Opción 2: Jupyter Local

```bash
# Instalar dependencias
pip install -r ../requirements.txt

# Abrir Jupyter
jupyter notebook TFM_Impacto_del_desempeño_ESG_en_la_Rentabilidad_y_el_Riesgo_de_las_empresas_del_STOXX_600_.ipynb
```

---

## 📑 Estructura del Notebook

### Sección 1-3: Setup y Carga de Datos
- Imports (pandas, numpy, statsmodels, etc.)
- Configuración de variables globales
- Descarga/carga de datos desde Refinitiv o Drive

### Sección 4-5: Consolidación y EDA
- Dataset principal: 1.576.944 obs × 26 cols
- Estadísticas descriptivas por quintil ESG
- Análisis de cobertura ESG (94.6%)

### Sección 6-8: Preparación para H1/H2/H3
- Construcción de portafolios (equal-weighted, quintiles)
- Cálculo de retornos mensuales
- Winsorización y limpieza de outliers

### Sección 9-10: Hipótesis 1 (H1) — Green Premium
- Construcción de factores Fama-French
- Regresiones Carhart 4F
- Análisis de alphas por quintil
- Diagnósticos: JB, DW, Pesaran CD

### Sección 11-12: Hipótesis 2 (H2) — Valuación
- Panel dinámico con Tobin Q
- Modelos FE + Driscoll-Kraay
- Test Hausman y especificaciones múltiples

### Sección 13-14: Hipótesis 3 (H3) — Estrés de Mercado
- Markov-Switching en retornos del STOXX 600
- Detección de regímenes (Calma vs. Crisis)
- CAPM condicional por régimen

### Sección 15-16: Resultados Agregados
- 19 gráficos principales
- Tablas de outputs para anexos
- Validación de robustez

---

## 📊 Outputs Principales

| Variable | Dimensión | Descripción |
|----------|-----------|-------------|
| `df_all` | 1.576.944 × 26 | Dataset completo consolidado |
| `consolidados` | Dinámico | Datos mensuales listos para análisis |
| `df_stoxx` | 2.567 días | Retornos diarios STOXX 600 NR |
| `euribor` | 2.837 días | Tasas libres de riesgo |
| `df_factors` | 132 meses × 8 | Factores Fama-French + WML |
| `df_monthly_raw` | ~74.373 × 15 | Datos mensuales sin winsorización |
| `df_annual_raw` | ~6.232 × 15 | Datos anuales sin winsorización |

---

## 🎯 Resultados Clave (Pre-calculados)

### H1: Green Premium ✅
```
ESG Score (L-S): α = −0.5988%/mes (t = −5.218***)
Interpretación: Mejor ESG → menor retorno (paradoja)
```

### H2: Valuación ⚪
```
Modelo principal: SIN EFECTO significativo
Pero: Sensibilidad robusta en 2-way FE (β1 = −0.00309, t = −2.18)
```

### H3: Estrés de Mercado 🔴
```
ESG Score, Q5: δ = +0.211 en crisis (p = 0.0024***)
Interpretación: Bajo ESG amplifica beta en mercados bajistas
```

---

## 📈 Gráficos Principales (19 total)

### H1
- `h1_alphas_por_quintil`: Barra de alphas por quintil ESG
- `h1_serie_temporal_ls`: Serie temporal del spread L-S
- `h1_betas_por_quintil`: Beta de mercado por quintil
- `h1_distribucion_residuos`: Q-Q plot para normalidad
- `h1_factor_loadings`: Tabla de factor loadings (FF4)
- `h1_variograma_residuos`: Autocorrelación residuos

### H2
- `h2_forest_beta1`: Forest plot: β1 por especificación
- `h2_binscatter_q_esg`: Scatter: Tobin Q vs. ESG Score
- `h2_evolucion_q_terciles`: Series temporales por terciles
- `h2_dist_qtobin`: Distribución de Q (raw vs. winsorizado)

### H3
- `h3_regimen_mercado`: Gráfico de regímenes (STOXX 600)
- `h3_betas_regimen`: Betas por cartera y régimen
- `h3_ls_regimen`: Spread L-S por régimen

### Generales
- `correlacion_factores_heatmap`: Correlaciones FF4 + WML
- `cobertura_esg_timeline`: Evolución temporal cobertura ESG

---

## ⚠️ Limitaciones y Consideraciones

1. **Acceso a Datos:**
   - Refinitiv Eikon requiere licencia (caro)
   - Datos procesados ya están disponibles en `data/processed/`

2. **Período:**
   - 2015-2025: incluye crisis COVID (mar-jun 2020) y Ucrania (feb-sep 2022)
   - Posible agotamiento Green Premium post-2021

3. **Correlaciones de Factores:**
   - HML ↔ WML = −0.528 (multicolinealidad leve)
   - Considerar en interpretación combinada

4. **Muestra Dinámica:**
   - Empresas entran/salen del universo
   - Muestra principal: 589 empresas (598 menos 9 sin ESG)

---

## 🔧 Troubleshooting

| Problema | Solución |
|----------|----------|
| "ModuleNotFoundError: No module named 'refinitiv-data'" | Ejecuta `pip install refinitiv-data` |
| "PermissionError: Google Drive" | Ejecuta la celda de autenticación (`auth.authenticate_user()`) |
| "Memory error" en Colab | Reinicia runtime, ejecuta una sección a la vez |
| Factores con valores NaN | Asegúrate de que `df_stoxx` y `euribor` cargaron correctamente |

---

## 📚 Referencias para Reproducción

1. **Fama & French (1993):** Construcción de factores SMB/HML
2. **Carhart (1997):** Factor WML (momentum)
3. **Newey & West (1987):** Estimadores robustos a autocorrelación
4. **Hamilton (1989):** Markov-Switching models

---

## 💾 Guardando Outputs

El notebook guarda automáticamente:
- Tablas CSV en `data/processed/`
- Gráficos PNG en `results/figures/`
- Modelos en formato pickle para reutilización

---

**Última actualización:** 16 de junio de 2026  
**Status:** ✅ Completamente auditado y funcional
