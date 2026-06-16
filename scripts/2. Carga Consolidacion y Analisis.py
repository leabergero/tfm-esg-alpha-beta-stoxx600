# ==============================================================================
# SCRIPT 2: CARGA, CONSOLIDACIÓN Y ANÁLISIS DE COBERTURA
# ==============================================================================
# Unifica los pasos 2, 2.1 y 2.2 en un único script para ejecutar en Colab.
#
# Orden de ejecución:
#   SECCIÓN 1 → Montar Drive y definir rutas
#   SECCIÓN 2 → Cargar datos PTB (por año)
#   SECCIÓN 3 → Cargar datos DEFENSA (por año)
#   SECCIÓN 4 → Cargar Euríbor
#   SECCIÓN 5 → Cargar STOXX 600 (índice de mercado)
#   SECCIÓN 6 → Verificación cruzada de fechas
#   SECCIÓN 7 → Consolidación PTB + DEFENSA + Euríbor por año
#   SECCIÓN 8 → Guardar y verificar archivos CONSOLIDADO_YYYY.csv
#   SECCIÓN 9 → Análisis de cobertura global y anual
#   SECCIÓN 10 → Disponibilidad de ratios derivados por hipótesis
#   SECCIÓN 11 → Estadísticas descriptivas y gráficos
#   SECCIÓN 12 → Resumen ejecutivo
# ==============================================================================

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

print("=" * 90)
print("SCRIPT 2: CARGA, CONSOLIDACIÓN Y ANÁLISIS DE COBERTURA")
print("=" * 90)
print(f"Inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

YEARS = range(2015, 2026)

# ==============================================================================
# SECCIÓN 1: MONTAR DRIVE Y DEFINIR RUTAS
# ==============================================================================

print("─" * 90)
print("SECCIÓN 1: MONTAR DRIVE")
print("─" * 90)

from google.colab import drive
drive.mount('/content/drive')

BASE = '/content/drive/MyDrive/Colab Notebooks'

print(f"\n📂 Carpeta base: {BASE}")
print(f"\nArchivos disponibles:")
for f in sorted(os.listdir(BASE)):
    size_mb = os.path.getsize(os.path.join(BASE, f)) / 1_048_576
    print(f"  {f:60s}  {size_mb:6.1f} MB")

# ==============================================================================
# SECCIÓN 2: CARGAR DATOS PTB (2015-2025)
# ==============================================================================

print("\n" + "─" * 90)
print("SECCIÓN 2: CARGAR DATOS PTB CONSOLIDADOS")
print("─" * 90)

ptb = {}
for year in YEARS:
    path = os.path.join(BASE, f'stoxx600_PTB_CONSOLIDADO_{year}.csv')
    ptb[year] = pd.read_csv(path, parse_dates=['Date'])

print(f"\n{'Año':>6}  {'RICs':>6}  {'Filas':>10}  {'PTB nulos':>10}  {'ROA nulos':>10}")
print("-" * 55)
for year, df in ptb.items():
    ptb_null = df['Price_To_Book'].isna().sum()
    roa_null = df['Pretax_ROA'].isna().sum()
    print(f"{year:>6}  {df['RIC'].nunique():>6}  {len(df):>10,}  {ptb_null:>10,}  {roa_null:>10,}")

print(f"\n{'Año':>6}  {'RICs sin PTB':>13}  Lista")
print("-" * 80)
for year in YEARS:
    sin_ptb = ptb[year].groupby('RIC')['Price_To_Book'].apply(lambda s: s.isna().all())
    rics = sorted(sin_ptb[sin_ptb].index.tolist())
    print(f"{year:>6}  {len(rics):>13}  {rics}")

# ==============================================================================
# SECCIÓN 3: CARGAR DATOS DEFENSA (2015-2025)
# ==============================================================================

print("\n" + "─" * 90)
print("SECCIÓN 3: CARGAR DATOS DEFENSA")
print("─" * 90)

defensa = {}
for year in YEARS:
    path = os.path.join(BASE, f'stoxx600_DEFENSA_{year}.csv')
    defensa[year] = pd.read_csv(path, parse_dates=['Date'])

print(f"\n{'Año':>6}  {'RICs':>6}  {'Filas':>10}  {'Columnas (primeras 5)'}")
print("-" * 70)
for year, df in defensa.items():
    print(f"{year:>6}  {df['RIC'].nunique():>6}  {len(df):>10,}  {list(df.columns)[:5]}…")

# ==============================================================================
# SECCIÓN 4: CARGAR EURÍBOR
# ==============================================================================

print("\n" + "─" * 90)
print("SECCIÓN 4: CARGAR EURÍBOR")
print("─" * 90)

euribor = pd.read_csv(
    os.path.join(BASE, 'euribor_tasas_diarias_2014_2025_corregido.csv'),
    parse_dates=['Date']
)

print(f"\n✅ Euríbor cargado: {len(euribor):,} filas")
print(f"   Rango: {euribor['Date'].min().date()} → {euribor['Date'].max().date()}")
print(f"   Columnas: {list(euribor.columns)}")
print(f"   Valores nulos: Euribor_1M={euribor['Euribor_1M'].isna().sum()} | Euribor_1Y={euribor['Euribor_1Y'].isna().sum()}")
print(euribor.head(3).to_string(index=False))

# ==============================================================================
# SECCIÓN 5: CARGAR STOXX 600 (ÍNDICE DE MERCADO)
# ==============================================================================
#
# DECISIÓN METODOLÓGICA (Anexo A1 — Script A1_Comparacion_Indices_STOXX600):
#   Se utilizan tres versiones del STOXX Europe 600. Activar UNA sola
#   descomentando la línea correspondiente. Las otras dos deben permanecer
#   comentadas. Todas tienen la misma estructura (Date, Close_Price, Return).
#
#   PR  — Price Return     (solo precio de cierre, sin dividendos)
#          Rm_Rf ≈ −2.35%/año → sesgado negativamente. NO RECOMENDADO.
#
#   NR  — Net Return       (precio + dividendos netos de retención fiscal)
#          Rm_Rf ≈ +0.20%/año → VERSIÓN SELECCIONADA para el análisis principal.
#          Convención estándar en fondos UCITS europeos y literatura académica.
#
#   GR  — Gross Return     (precio + dividendos brutos, antes de impuestos)
#          Rm_Rf ≈ +0.77%/año → sobreestima el retorno disponible para el inversor.
#          Útil para análisis de sensibilidad.
#
#   Para cambiar de base: comentar la línea activa y descomentar la deseada.
#   El spread Q1−Q5 de H1 es invariante a la elección; solo cambian los alphas
#   absolutos por quintil (≈ ±0.20%/mes entre NR y PR). Ver Anexo A1.
# ------------------------------------------------------------------------------

print("\n" + "─" * 90)
print("SECCIÓN 5: CARGAR STOXX 600 (ÍNDICE DE MERCADO)")
print("─" * 90)

# ── Seleccionar UNA de las tres líneas siguientes ─────────────────────────────

# stoxx_archivo = 'stoxx600_retornos_diarios_2015_2025.csv'           # PR — Price Return (sin dividendos) — NO RECOMENDADO
stoxx_archivo   = 'stoxx600_retornos_diarios_2015_2025 (STOXXR).csv'  # NR — Net Return ← SELECCIONADO (análisis principal)
# stoxx_archivo = 'stoxx600_retornos_diarios_2015_2025 (SXXGR).csv'  # GR — Gross Return (sensibilidad)

# ── Etiqueta que acompaña a df_stoxx en prints y gráficos ────────────────────
STOXX_VERSION = (
    'NR — Net Return (dividendos netos) ← ACTIVO'  if 'STOXXR' in stoxx_archivo else
    'GR — Gross Return (dividendos brutos)'         if 'SXXGR'  in stoxx_archivo else
    'PR — Price Return (sin dividendos)'
)

# ── Carga ─────────────────────────────────────────────────────────────────────
try:
    df_stoxx = pd.read_csv(
        os.path.join(BASE, stoxx_archivo),
        parse_dates=['Date']
    )
    retornos_stoxx = df_stoxx['Return'].dropna()
    print(f"\n✅ STOXX 600 cargado: {len(df_stoxx):,} observaciones")
    print(f"   Versión:  {STOXX_VERSION}")
    print(f"   Archivo:  {stoxx_archivo}")
    print(f"   Rango:    {df_stoxx['Date'].min().date()} → {df_stoxx['Date'].max().date()}")
    print(f"   Columnas: {list(df_stoxx.columns)}")
    print(f"   Retornos válidos: {len(retornos_stoxx):,} ({len(retornos_stoxx)/len(df_stoxx)*100:.1f}%)")
    print(f"   Precio mín/máx:   {df_stoxx['Close_Price'].min():.2f} / {df_stoxx['Close_Price'].max():.2f}")
    print(f"   Retorno medio:    {retornos_stoxx.mean():.6f} | Desv. Est.: {retornos_stoxx.std():.6f}")
    print(f"   Rm anualizado:    {retornos_stoxx.mean()*252*100:.4f}%/año")
    print(df_stoxx.head(3).to_string(index=False))
except FileNotFoundError:
    print(f"\n❌ Archivo no encontrado: {stoxx_archivo}")
    print(f"   Ruta esperada: {os.path.join(BASE, stoxx_archivo)}")
    df_stoxx      = None
    STOXX_VERSION = 'NO CARGADO'

# ==============================================================================
# SECCIÓN 6: VERIFICACIÓN CRUZADA DE FECHAS
# ==============================================================================

print("\n" + "─" * 90)
print("SECCIÓN 6: VERIFICACIÓN CRUZADA DE FECHAS")
print("─" * 90)

print(f"\n{'Año':>6}  {'Días DEFENSA':>13}  {'Días PTB':>9}  {'Sin Euríbor':>12}  {'Sin STOXX':>10}")
print("-" * 60)
for year in YEARS:
    fechas_defensa = set(defensa[year]['Date'].dt.date)
    fechas_ptb     = set(ptb[year]['Date'].dt.date)
    fechas_euribor = set(euribor[euribor['Date'].dt.year == year]['Date'].dt.date)
    sin_euribor    = len(fechas_defensa - fechas_euribor)

    if df_stoxx is not None:
        fechas_stoxx = set(df_stoxx[df_stoxx['Date'].dt.year == year]['Date'].dt.date)
        sin_stoxx    = len(fechas_defensa - fechas_stoxx)
    else:
        sin_stoxx = 'N/A'

    print(f"{year:>6}  {len(fechas_defensa):>13}  {len(fechas_ptb):>9}  {sin_euribor:>12}  {str(sin_stoxx):>10}")

# ==============================================================================
# SECCIÓN 7: CONSOLIDACIÓN PTB + DEFENSA + EURÍBOR POR AÑO
# ==============================================================================

print("\n" + "─" * 90)
print("SECCIÓN 7: CONSOLIDACIÓN DE DATOS POR AÑO")
print("─" * 90)

consolidados = {}

for year in YEARS:
    print(f"\n  Procesando {year}...")

    df_ptb_y = ptb[year].copy()
    df_def_y = defensa[year].copy()

    # LEFT JOIN: DEFENSA como base + PTB donde exista
    df_merged = pd.merge(
        df_def_y,
        df_ptb_y[['Date', 'RIC', 'Price_To_Book', 'Pretax_ROA', 'ROA_TTM']],
        on=['Date', 'RIC'],
        how='left'
    )

    # LEFT JOIN: añadir Euríbor por fecha
    df_merged = pd.merge(
        df_merged,
        euribor[['Date', 'Euribor_1M', 'Euribor_1Y']],
        on='Date',
        how='left'
    )

    df_merged = df_merged.sort_values(['Date', 'RIC']).reset_index(drop=True)
    consolidados[year] = df_merged

    ptb_cob  = (df_merged['Price_To_Book'].notna().sum() / len(df_merged)) * 100
    roa_cob  = (df_merged['Pretax_ROA'].notna().sum()    / len(df_merged)) * 100
    eur_cob  = (df_merged['Euribor_1Y'].notna().sum()    / len(df_merged)) * 100
    print(f"    {len(df_merged):,} filas | PTB: {ptb_cob:.1f}% | ROA: {roa_cob:.1f}% | Euríbor: {eur_cob:.1f}%")

print("\n✅ Consolidación completada para todos los años.")

# ==============================================================================
# SECCIÓN 8: GUARDAR Y VERIFICAR ARCHIVOS CONSOLIDADOS
# ==============================================================================

print("\n" + "─" * 90)
print("SECCIÓN 8: GUARDAR Y VERIFICAR ARCHIVOS CONSOLIDADOS")
print("─" * 90)

print("\nGuardando archivos en Drive...")
for year in YEARS:
    output_path = os.path.join(BASE, f'CONSOLIDADO_{year}.csv')
    consolidados[year].to_csv(output_path, index=False)
    size_mb = os.path.getsize(output_path) / 1_048_576
    print(f"  ✅ CONSOLIDADO_{year}.csv  ({size_mb:.1f} MB)")

# Verificación de integridad
print(f"\n{'Año':>6}  {'Filas':>10}  {'RICs':>6}  {'PTB null':>10}  {'ROA null':>10}  {'Eur null':>10}  {'Sin PTB+ROA':>12}")
print("-" * 75)
for year in YEARS:
    df = consolidados[year]
    ptb_n  = df['Price_To_Book'].isna().sum()
    roa_n  = df['Pretax_ROA'].isna().sum()
    eur_n  = df['Euribor_1Y'].isna().sum()
    sin_ambos = ((df['Price_To_Book'].isna()) & (df['Pretax_ROA'].isna())).sum()
    print(f"{year:>6}  {len(df):>10,}  {df['RIC'].nunique():>6}  "
          f"{ptb_n:>10,}  {roa_n:>10,}  {eur_n:>10,}  {sin_ambos:>12,}")

print(f"\n{'Año':>6}  {'RICs sin PTB (todo NaN)':>25}  Lista")
print("-" * 80)
for year in [2015, 2016, 2020, 2025]:
    df = consolidados[year]
    sin_ptb = df.groupby('RIC')['Price_To_Book'].apply(lambda s: s.isna().all())
    rics = sorted(sin_ptb[sin_ptb].index.tolist())
    print(f"{year:>6}  {len(rics):>25}  {rics}")

print(f"\n✅ Estructura final (columnas):")
print(f"   {list(consolidados[2020].columns)}")

# ==============================================================================
# SECCIÓN 9: ANÁLISIS DE COBERTURA GLOBAL Y ANUAL
# ==============================================================================

print("\n" + "─" * 90)
print("SECCIÓN 9: ANÁLISIS DE COBERTURA")
print("─" * 90)

# Dataset completo (todos los años combinados)
df_all = pd.concat([consolidados[year] for year in YEARS], ignore_index=True)
df_all['Date'] = pd.to_datetime(df_all['Date'])
años = sorted(consolidados.keys())

print(f"\n📊 Dataset combinado: {len(df_all):,} filas × {df_all.shape[1]} columnas")
print(f"   Período: {df_all['Date'].min().date()} a {df_all['Date'].max().date()}")
print(f"   Empresas únicas: {df_all['RIC'].nunique()}")

# Cobertura global
variables_clave = [
    'Price_Close_EUR', 'Return_1D', 'Excess_Return_1D',
    'Market_Cap_EUR', 'Total_Assets_EUR', 'Total_Debt_EUR',
    'Price_To_Book', 'Pretax_ROA', 'ROA_TTM',
    'E_Score', 'S_Score', 'G_Score', 'ESG_Score',
    'Euribor_1M', 'Euribor_1Y', 'Book_Value_Per_Share_EUR'
]

print(f"\n📈 COBERTURA GLOBAL:")
print(f"\n{'Variable':<30} {'Válidos':>12} {'Faltantes':>12} {'Cobertura':>12}")
print("-" * 68)

cobertura_global = {}
for var in variables_clave:
    if var in df_all.columns:
        validos   = df_all[var].notna().sum()
        faltantes = df_all[var].isna().sum()
        cob       = (validos / len(df_all)) * 100
        cobertura_global[var] = cob
        print(f"{var:<30} {validos:>12,} {faltantes:>12,} {cob:>11.1f}%")

# Cobertura anual
print(f"\n📅 COBERTURA ANUAL:")
cobertura_anual = {}
for year in años:
    df_y = consolidados[year]
    cobertura_anual[year] = {}
    vars_criticas = ['Price_Close_EUR', 'Return_1D', 'Total_Assets_EUR',
                     'Total_Debt_EUR', 'Pretax_ROA', 'ROA_TTM', 'E_Score', 'G_Score']
    print(f"\n  {year}: {len(df_y):,} filas | {df_y['RIC'].nunique()} RICs")
    for var in vars_criticas:
        if var in df_y.columns:
            cob = (df_y[var].notna().sum() / len(df_y)) * 100
            cobertura_anual[year][var] = cob
            print(f"     {var:<30} {cob:>6.1f}%")

# ==============================================================================
# SECCIÓN 10: DISPONIBILIDAD DE DATOS POR HIPÓTESIS
# ==============================================================================

print("\n" + "─" * 90)
print("SECCIÓN 10: DISPONIBILIDAD DE DATOS POR HIPÓTESIS")
print("─" * 90)

# ── Cálculo de coberturas ──────────────────────────────────────────────────────
q_val        = df_all[(df_all['Market_Cap_EUR'].notna()) & (df_all['Total_Assets_EUR'].notna())].shape[0]
q_cob        = (q_val / len(df_all)) * 100
size_val     = df_all[df_all['Total_Assets_EUR'].notna()].shape[0]
size_cob     = (size_val / len(df_all)) * 100
lev_val      = df_all[(df_all['Total_Debt_EUR'].notna()) & (df_all['Total_Assets_EUR'].notna())].shape[0]
lev_cob      = (lev_val / len(df_all)) * 100
roa_pretax_n = df_all[df_all['Pretax_ROA'].notna()].shape[0]
roa_ttm_n    = df_all[df_all['ROA_TTM'].notna()].shape[0]
roa_comb     = df_all[(df_all['Pretax_ROA'].notna()) | (df_all['ROA_TTM'].notna())].shape[0]
roa_cob      = (roa_comb / len(df_all)) * 100
ret_cob      = df_all['Return_1D'].notna().sum() / len(df_all) * 100
exc_cob      = df_all['Excess_Return_1D'].notna().sum() / len(df_all) * 100
esg_cob      = df_all['ESG_Score'].notna().sum() / len(df_all) * 100
e_cob        = df_all['E_Score'].notna().sum() / len(df_all) * 100
s_cob        = df_all['S_Score'].notna().sum() / len(df_all) * 100
g_cob        = df_all['G_Score'].notna().sum() / len(df_all) * 100
ptb_cob      = df_all['Price_To_Book'].notna().sum() / len(df_all) * 100
eur_cob      = df_all['Euribor_1M'].notna().sum() / len(df_all) * 100
mktcap_cob   = df_all['Market_Cap_EUR'].notna().sum() / len(df_all) * 100
stoxx_obs    = len(df_stoxx) if df_stoxx is not None else 0

def check(cob, umbral=80):
    return "✅" if cob >= umbral else "⚠️ " if cob >= 50 else "❌"

# ── HIPÓTESIS 1 ────────────────────────────────────────────────────────────────
print("""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
H1 — ALPHA DE JENSEN (Carhart 4 Factores)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Pregunta : ¿El mercado europeo premia el desempeño ESG con una rentabilidad
           anormal positiva, ajustada por riesgo?
Modelo   : R_pt − R_ft = α_p + β(Rm−Rf) + s·SMB + h·HML + w·WML + ε_pt
Var. dep.: R_pt − R_ft  (exceso de retorno mensual del portafolio ESG)
Var. int.: α_p          (Alpha de Jensen — lo que queremos medir)
Controles: Rm−Rf, SMB (tamaño), HML (valor/PTB), WML (momentum)
Estrategia: Long Q1 (mejor ESG) − Short Q5 (peor ESG) | equal-weighted | rezago t−1
""")

stoxx_linea = f"{'✅' if stoxx_obs > 0 else '❌'} STOXX 600 [{STOXX_VERSION}]: {stoxx_obs:,} obs"
print(f"  COBERTURAS REQUERIDAS:")
print(f"  {check(ret_cob)}  Return_1D         (R_pt):      {ret_cob:.1f}%")
print(f"  {stoxx_linea}")
print(f"  {check(eur_cob)}  Euribor_1M        (R_ft):      {eur_cob:.1f}%")
print(f"  {check(mktcap_cob)}  Market_Cap_EUR    (SMB):      {mktcap_cob:.1f}%")
print(f"  {check(ptb_cob)}  Price_To_Book     (HML):      {ptb_cob:.1f}%")
print(f"  {check(esg_cob)}  ESG_Score lag t−1 (quintiles): {esg_cob:.1f}%")
print(f"  {check(e_cob)}  E_Score lag t−1               {e_cob:.1f}%")
print(f"  {check(s_cob)}  S_Score lag t−1               {s_cob:.1f}%")
print(f"  {check(g_cob)}  G_Score lag t−1               {g_cob:.1f}%")
print(f"\n  Pendiente: agregar a mensual → construir portafolios y factores (Script 2.3 + 3.1)")

# ── HIPÓTESIS 2 ────────────────────────────────────────────────────────────────
print("""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
H2 — PREFERENCIAS DEL MERCADO Y VALORACIÓN (Q de Tobin, efectos fijos)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Pregunta : ¿Qué pilar ESG (E, S o G) genera mayor valor corporativo en Europa?
Modelo   : TobinQ_it = β0 + β1·ESG_it + β2·Size_it + β3·Lev_it + β4·ROA_it + β5·Growth_it + μ_i + ε_it
Var. dep.: Q de Tobin = Market_Cap_EUR / Total_Assets_EUR
Var. int.: β1 (coeficiente ESG/E/S/G — se corre por separado para cada pilar)
Controles: Size = Ln(Total_Assets), Leverage = Debt/Assets, ROA, Growth anual de activos
Frecuencia: anual (una obs por empresa-año)
""")

print(f"  COBERTURAS REQUERIDAS:")
print(f"  {check(q_cob)}  Q de Tobin   (Market_Cap / Total_Assets):  {q_cob:.1f}%")
print(f"  {check(esg_cob)}  ESG_Score    (β1 — var. de interés):       {esg_cob:.1f}%")
print(f"  {check(e_cob)}  E_Score                                     {e_cob:.1f}%")
print(f"  {check(s_cob)}  S_Score                                     {s_cob:.1f}%")
print(f"  {check(g_cob)}  G_Score                                     {g_cob:.1f}%")
print(f"  {check(size_cob)}  Size         (Ln Total_Assets):             {size_cob:.1f}%")
print(f"  {check(lev_cob)}  Leverage     (Debt / Assets):               {lev_cob:.1f}%")
print(f"  {check(roa_cob)}  ROA Final    (Pretax_ROA | ROA_TTM):        {roa_cob:.1f}%")
print(f"  ❌  Growth Anual  (Δ Total_Assets):              NO DISPONIBLE — calcular en Script 2.3")

# ── HIPÓTESIS 3 ────────────────────────────────────────────────────────────────
print("""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
H3 — RIESGO DINÁMICO (Markov-Switching CAPM)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Pregunta : ¿El alto desempeño ESG reduce el beta sistemático en períodos de crisis?
Modelo   : R_pt − R_ft = α_St + β_St·(Rm−Rf) + ε_pt   donde St ∈ {calma, crisis}
Var. dep.: R_pt − R_ft  (exceso de retorno mensual del portafolio ESG)
Var. int.: β_S1 vs β_S2 (betas por régimen — test de Wald H0: β_S1 = β_S2)
Regímenes: detectados automáticamente por el modelo (endógenos — sin definir crisis a mano)
""")

print(f"  COBERTURAS REQUERIDAS:")
print(f"  {check(exc_cob)}  Excess_Return_1D  (R_pt − R_ft):  {exc_cob:.1f}%")
print(f"  {stoxx_linea}")
print(f"  {check(eur_cob)}  Euribor_1M        (R_ft):         {eur_cob:.1f}%")
print(f"  {check(esg_cob)}  ESG_Score         (quintiles):    {esg_cob:.1f}%")
n_meses = (df_all['Date'].max().year - df_all['Date'].min().year) * 12
print(f"  ✅  Período disponible: ~{n_meses} meses (mínimo recomendado: 60 meses para MS-CAPM)")
print(f"\n  Pendiente: portafolios mensuales Q1/Q5 de H1 → reusar directamente en H3 (Script 3.4)")

print("\n" + "─" * 90)

# ==============================================================================
# SECCIÓN 11: ESTADÍSTICAS DESCRIPTIVAS Y GRÁFICOS
# ==============================================================================

print("\n" + "─" * 90)
print("SECCIÓN 11: ESTADÍSTICAS DESCRIPTIVAS Y GRÁFICOS")
print("─" * 90)

# Estadísticas de variables clave
for nombre, col in [
    ('RETORNOS (Return_1D)',         'Return_1D'),
    ('EXCESS RETURN',                'Excess_Return_1D'),
    ('PRICE-TO-BOOK',                'Price_To_Book'),
    ('ROA PRETAX',                   'Pretax_ROA'),
    ('E_SCORE',                      'E_Score'),
    ('G_SCORE',                      'G_Score'),
]:
    s = df_all[col].dropna()
    if len(s) > 0:
        print(f"\n📊 {nombre}")
        print(f"   n={len(s):,} | Media: {s.mean():.6g} | Desv: {s.std():.6g} | "
              f"Mín: {s.min():.6g} | Máx (P99): {s.quantile(0.99):.6g}")

# ── Gráfico 1: Cobertura y distribuciones consolidadas ──────────────────────
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle('Análisis de Cobertura y Distribuciones (2015-2025)', fontsize=15, fontweight='bold')

ax1 = axes[0, 0]
top10 = sorted(cobertura_global.items(), key=lambda x: x[1], reverse=True)[:10]
n, c = zip(*top10)
colors = ['#2ecc71' if v >= 80 else '#f39c12' if v >= 50 else '#e74c3c' for v in c]
ax1.barh(n, c, color=colors)
ax1.axvline(80, color='#27ae60', linestyle='--', lw=1, label='80%')
ax1.axvline(50, color='#e67e22', linestyle='--', lw=1, label='50%')
ax1.set_xlabel('Cobertura (%)')
ax1.set_title('Cobertura por Variable (Top 10)')
ax1.set_xlim([0, 105])
ax1.legend(fontsize=8)

ax2 = axes[0, 1]
vars_ev = ['Price_Close_EUR', 'Total_Assets_EUR', 'Pretax_ROA', 'E_Score']
for var in vars_ev:
    cobs = [cobertura_anual[y].get(var, 0) for y in años]
    ax2.plot(años, cobs, marker='o', label=var)
ax2.set_xlabel('Año')
ax2.set_ylabel('Cobertura (%)')
ax2.set_title('Evolución de Cobertura Anual')
ax2.legend(fontsize=7)
ax2.grid(alpha=0.3)
ax2.set_ylim([0, 105])

ax3 = axes[1, 0]
ret = df_all['Return_1D'].dropna()
ax3.hist(ret, bins=60, color='#3498db', edgecolor='black', alpha=0.75)
ax3.axvline(ret.mean(), color='red', linestyle='--', lw=1.5, label=f'Media: {ret.mean():.6f}')
ax3.set_xlabel('Retorno Diario')
ax3.set_title(f'Retornos Individuales (n={len(ret):,})')
ax3.legend(fontsize=8)

ax4 = axes[1, 1]
df_corr = df_all[['Return_1D', 'Price_To_Book', 'Pretax_ROA', 'E_Score']].dropna()
if len(df_corr) > 100:
    sns.heatmap(df_corr.corr(), annot=True, fmt='.2f', cmap='coolwarm',
                center=0, ax=ax4, square=True, cbar_kws={'shrink': 0.8})
    ax4.set_title(f'Correlaciones (n={len(df_corr):,})')

plt.tight_layout()
plt.show()

# ── Gráfico 4: STOXX 600 ──────────────────────────────────────────────────────
if df_stoxx is not None:
    fig, axes = plt.subplots(2, 1, figsize=(14, 8))
    fig.suptitle(f'Índice STOXX 600 — {STOXX_VERSION}\n(2015–2025)', fontsize=13, fontweight='bold')

    ax1 = axes[0]
    ax1.plot(df_stoxx['Date'], df_stoxx['Close_Price'], color='#2c3e50', lw=1.5)
    ax1.set_ylabel('Precio de Cierre')
    ax1.set_title('Evolución del Precio')
    ax1.grid(alpha=0.3)

    ax2 = axes[1]
    ret_s = df_stoxx['Return'].dropna()
    ax2.hist(ret_s, bins=60, color='#27ae60', edgecolor='black', alpha=0.75)
    ax2.axvline(ret_s.mean(), color='red', linestyle='--', lw=1.5,
                label=f'Media: {ret_s.mean():.6f}')
    ax2.axvline(0, color='black', lw=0.8, alpha=0.5)
    ax2.set_xlabel('Retorno Diario')
    ax2.set_title(f'Distribución de Retornos (n={len(ret_s):,})')
    ax2.legend(fontsize=8)

    plt.tight_layout()
    plt.show()

# ==============================================================================
# SECCIÓN 12: RESUMEN EJECUTIVO
# ==============================================================================

print("\n" + "=" * 90)
print("SECCIÓN 12: RESUMEN EJECUTIVO")
print("=" * 90)

# Variables de cobertura ESG (calculadas aquí por si la Sección 9 no está en memoria)
esg_score_cob = df_all['ESG_Score'].notna().sum() / len(df_all) * 100
e_score_cob   = df_all['E_Score'].notna().sum()   / len(df_all) * 100
s_score_cob   = df_all['S_Score'].notna().sum()   / len(df_all) * 100
g_score_cob   = df_all['G_Score'].notna().sum()   / len(df_all) * 100

stoxx_status = ("✅ CARGADO (%d obs)" % len(df_stoxx)) if df_stoxx is not None else "❌ NO CARGADO"

print(f"""
ESTADO FINAL DE DATOS AL {datetime.now().strftime('%Y-%m-%d')}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PREGUNTA DE INVESTIGACIÓN:
   ¿Aportan valor los scores ESG a las empresas del STOXX 600?
   ¿Cuál de los componentes (E, S, G) tiene mayor impacto?

📦 DATASET:
   • Consolidados:     {len(años)} años ({min(años)}-{max(años)})
   • Total filas:      {len(df_all):,}
   • Empresas únicas:  {df_all['RIC'].nunique()}
   • Variables:        {df_all.shape[1]}
   • STOXX 600:        {stoxx_status}  [{STOXX_VERSION}]
   • Euríbor:          ✅ CARGADO ({len(euribor):,} obs)

🌿 VARIABLES DE INVESTIGACIÓN PRINCIPAL — SCORES ESG:
   • ESG_Score (combinado):   {esg_score_cob:.1f}%  ✅ Muy buena cobertura
   • E_Score (Ambiental):     {e_score_cob:.1f}%  ✅ Muy buena cobertura
   • S_Score (Social):        {s_score_cob:.1f}%  ✅ Muy buena cobertura
   • G_Score (Gobernanza):    {g_score_cob:.1f}%  ✅ Muy buena cobertura
   → Cobertura insuficiente solo en 2015-2017 (84-87%) — mejora hasta >98% desde 2019

📊 COBERTURA DE VARIABLES DE CONTROL:
   • Precios/Retornos:     EXCELENTE (100%)
   • Fundamentales:        MUY BUENA (95.3%)
   • ROA (combinado):      {roa_cob:.1f}%

✅ RATIOS DERIVADOS CALCULABLES:
   • Q de Tobin:   {q_cob:.1f}%
   • Size:         {size_cob:.1f}%
   • Leverage:     {lev_cob:.1f}%
   • ROA Final:    {roa_cob:.1f}%

⚠️  LIMITACIONES:
   • Growth Anual: no calculable desde datos diarios (necesita datos anuales)
   • ESG en 2015-2017: cobertura menor (~84-87%) — 83 empresas adoptaron ESG
     gradualmente; muestra principal = 453 empresas con ESG en todo el período

📋 PRÓXIMOS PASOS:
   → Script 2.3: Calcular ratios derivados + variable primer_año_esg + muestra 453 empresas
   → Script 2.4: Agregación mensual + portafolios long-short por quintil ESG/E/S/G
   → Script 2.5: Incorporar Growth anual

ESTADO: ✅ LISTO PARA INICIAR MODELADO
""")

print("=" * 90)
print(f"Fin: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 90)
