# ==============================================================================
# ANÁLISIS: RICs SIN ESG_Score EN NINGÚN AÑO DEL PERÍODO (2015-2025)
# ==============================================================================
# Pegar en una celda de Colab después de ejecutar el Script 2 principal.
# Requiere que el dict `consolidados` ya esté cargado en memoria.
# ==============================================================================

print("=" * 70)
print("ANÁLISIS: RICs SIN ESG EN NINGÚN AÑO (2015-2025)")
print("=" * 70)

YEARS = range(2015, 2026)

# Universo completo de RICs en todo el período
todos_rics = set()
for year in YEARS:
    todos_rics.update(consolidados[year]['RIC'].unique())

print(f"\nUniverso total de RICs (2015-2025): {len(todos_rics)}")

# Identificar cuáles nunca tuvieron ESG_Score en ningún año
rics_nunca_esg = []
for ric in sorted(todos_rics):
    tiene_esg = False
    for year in YEARS:
        df_y = consolidados[year]
        filas = df_y[df_y['RIC'] == ric]['ESG_Score']
        if len(filas) > 0 and filas.notna().any():
            tiene_esg = True
            break
    if not tiene_esg:
        rics_nunca_esg.append(ric)

print(f"RICs sin ESG_Score en ningún año: {len(rics_nunca_esg)}")
print()

# Detalle por RIC: en qué años aparecen y con qué cobertura
print(f"{'RIC':<20} {'Años en índice':<18} {'Nota'}")
print("-" * 65)

for ric in rics_nunca_esg:
    años_presentes = []
    for year in YEARS:
        df_y = consolidados[year]
        if ric in df_y['RIC'].values:
            años_presentes.append(year)

    if len(años_presentes) == 0:
        rango = "nunca"
    elif años_presentes == list(range(min(años_presentes), max(años_presentes)+1)):
        rango = f"{min(años_presentes)}-{max(años_presentes)}"
    else:
        rango = ", ".join(str(y) for y in años_presentes)

    if len(años_presentes) == 11:
        nota = "⚠️  en índice todo el período, Refinitiv nunca la puntuó"
    elif len(años_presentes) >= 6:
        nota = f"⚠️  {len(años_presentes)} años en índice, Refinitiv nunca la puntuó"
    else:
        nota = f"entrada tardía al índice ({len(años_presentes)} años), sin ESG"
    print(f"{ric:<20} {rango:<18} {nota}")

print()
print(f"→ Estas {len(rics_nunca_esg)} empresas se excluyen en cualquier muestra de análisis.")
print(f"  Refinitiv no las puntuó en ningún momento del período 2015-2025.")
