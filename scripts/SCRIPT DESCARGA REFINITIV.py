"""
=============================================================================
REFINITIV CODEBOOK — STOXX 600
Panel diario 2015-2025 | Modelo Carhart 4 factores + Pilares ESG
=============================================================================
FIXES v5 basados en output real:
  [1] EURIBOR: campo correcto es TR.FIXINGVALUE, no CLOSE.
      Fallback a get_data con TR.EURIBOR1MD= y serie aproximada.
  [2] ESG_Combined / Price_To_Book / ROA / E_Score: Refinitiv NO los
      devuelve cuando van mezclados con TR.TRESGScore en una sola llamada.
      Solución: dos llamadas get_data separadas (ESG | Fundamentales)
      y luego merge por RIC + Report_Date.
  [3] E_Score ('Environmental Pillar Score'): norm_key lo mapea a
      'environmentalpillarscore' pero el mapa tenía 'environmentpillarscore'.
      Corregido en ANNUAL_RENAME.
  [4] Return_1D_pct ausente: DAILY_RENAME agregado 'trtotalreturn1d' y
      variantes sin prefijo TR. que devuelve Refinitiv en algunos lotes.
  [5] print_coverage: guard contra NaN antes de int() para evitar ValueError.
=============================================================================
"""

import refinitiv.data as rd
import pandas as pd
import numpy as np
import time

# =============================================================================
# CONFIGURACIÓN
# =============================================================================
START_YEAR = 2015
END_YEAR   = 2025
BATCH_SIZE = 50
SLEEP_SEC  = 0.35

DAILY_FIELDS = [
    'TR.PriceClose',
    'TR.PriceClose.Currency',
    'TR.TotalReturn1D',
    'TR.CompanyMarketCap',
    'TR.Volume',
]
DAILY_PARAMS = {'CURN': 'EUR'}

# Separamos ESG y fundamentales en dos llamadas distintas
# porque Refinitiv a veces ignora campos cuando hay demasiados mezclados
ESG_FIELDS = [
    'TR.TRESGScore',
    'TR.TRESGScore.Date',
    'TR.ESGCombinedScore',
    'TR.EnvironmentPillarScore',
    'TR.SocialPillarScore',
    'TR.GovernancePillarScore',
]

FUND_FIELDS = [
    'TR.PriceToBookValue',
    'TR.PriceToBookValue.Date',
    'TR.ROA',
    'TR.TotalAssetsReported',
    'TR.TotalDebt',
    'TR.BookValuePerShare',
    'TR.ReportedCurrencyCode',
]

ANNUAL_PARAMS_ESG = {
    'SDate': '2014-01-01', 'EDate': '2025-12-31',
    'Frq': 'FY',
}
ANNUAL_PARAMS_FUND = {
    'SDate': '2014-01-01', 'EDate': '2025-12-31',
    'Frq': 'FY', 'CURN': 'EUR',
}

ANNUAL_COLS_NUM = [
    'ESG_Score', 'ESG_Combined_Score',
    'E_Score', 'S_Score', 'G_Score',
    'Price_To_Book', 'ROA',
    'Total_Assets_EUR', 'Total_Debt_EUR', 'Book_Value_Per_Share_EUR',
]
ANNUAL_COLS_ALL = ANNUAL_COLS_NUM + ['Reporting_Currency']

COL_ORDER = [
    'Date', 'RIC', 'Company_Name', 'Currency_Original', 'Reporting_Currency',
    'Price_Close_EUR', 'Return_1D', 'Rf_daily', 'Excess_Return_1D',
    'Market_Cap_EUR', 'Volume',
    'ESG_Score', 'ESG_Combined_Score',
    'E_Score', 'S_Score', 'G_Score',
    'Price_To_Book', 'ROA',
    'Total_Assets_EUR', 'Total_Debt_EUR', 'Book_Value_Per_Share_EUR',
    'ESG_Report_Date', 'Fundamental_Report_Date',
]

# =============================================================================
# FUNCIONES AUXILIARES
# =============================================================================
def make_batches(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

def to_num(s):
    return pd.to_numeric(s, errors='coerce')

def norm_key(s):
    return (str(s).strip().lower()
            .replace('.', '').replace(' ', '').replace('_', '')
            .replace(',', '').replace('(', '').replace(')', ''))

def smart_rename(df, norm_map):
    mapping = {}
    already_mapped = set()
    for col in df.columns:
        k = norm_key(col)
        dest = norm_map.get(k)
        if dest and dest not in already_mapped:
            mapping[col] = dest
            already_mapped.add(dest)
    return df.rename(columns=mapping)

def get_ric_col(df):
    for col in df.columns:
        if norm_key(col) in {'ric', 'instrument', 'trric'}:
            return col
    return None

def flatten_get_history(df_raw):
    if not isinstance(df_raw.columns, pd.MultiIndex):
        return df_raw.reset_index()
    level0 = df_raw.columns.get_level_values(0).unique().tolist()
    l0_has_rics = any('.' in str(v) and not str(v).startswith('TR.') for v in level0)
    temp = df_raw.stack(level=0 if l0_has_rics else 1).reset_index()
    for col in temp.columns:
        if norm_key(col) in {'timestamp', 'date', 'level0', 'index'}:
            temp = temp.rename(columns={col: 'Date'})
            break
    ric_col = get_ric_col(temp)
    if ric_col and ric_col != 'RIC':
        temp = temp.rename(columns={ric_col: 'RIC'})
    elif ric_col is None:
        for col in temp.columns:
            if col == 'Date':
                continue
            sample = temp[col].dropna().astype(str).head(5).tolist()
            if any('.' in v and not v.startswith('TR') for v in sample):
                temp = temp.rename(columns={col: 'RIC'})
                break
    return temp

def download_annual_batches(batches, fields, params, label):
    """Descarga get_data en lotes y devuelve DataFrame concatenado."""
    chunks = []
    for idx, batch in enumerate(batches):
        try:
            df = rd.get_data(universe=batch, fields=fields, parameters=params)
            if df is not None and not df.empty:
                chunks.append(df)
            time.sleep(SLEEP_SEC)
            if (idx + 1) % 5 == 0:
                print(f"    [{label}] Lote {idx+1}/{len(batches)} OK")
        except Exception as e:
            print(f"    [{label}] Lote {idx+1} error: {e}")
    return pd.concat(chunks, ignore_index=True) if chunks else pd.DataFrame()

def print_coverage(panel, year):
    """Imprime cobertura — robusto contra columnas vacías o todo-NaN."""
    cols = [
        'Price_Close_EUR', 'Return_1D', 'Rf_daily', 'Excess_Return_1D',
        'ESG_Score', 'ESG_Combined_Score', 'E_Score', 'S_Score', 'G_Score',
        'Price_To_Book', 'ROA', 'Total_Assets_EUR',
    ]
    print(f"\n    Cobertura — {year}:")
    for col in cols:
        if col not in panel.columns or len(panel) == 0:
            print(f"      {col:<30} [{'?' * 20}]   N/A")
            continue
        pct = panel[col].notna().mean() * 100
        if np.isnan(pct):
            pct = 0.0
        n_x = int(pct / 5)
        bar = 'X' * n_x + '.' * (20 - n_x)
        print(f"      {col:<30} [{bar}] {pct:5.1f}%")

# =============================================================================
# PASO 0 — SESIÓN Y UNIVERSO
# =============================================================================
try:
    rd.open_session()
    print("Sesión Refinitiv abierta")
except Exception as e:
    print(f"  Sesión ya abierta: {e}")

print("\n[0] Obteniendo universo STOXX 600...")
rics_raw = rd.get_data('0#.STOXX', fields=['TR.CommonName'])
print(f"    Columnas devueltas: {rics_raw.columns.tolist()}")

ric_col = get_ric_col(rics_raw)
if ric_col and ric_col != 'RIC':
    rics_raw = rics_raw.rename(columns={ric_col: 'RIC'})
elif ric_col is None:
    rics_raw = rics_raw.rename(columns={rics_raw.columns[0]: 'RIC'})

rics_raw = smart_rename(rics_raw, {
    'commonname': 'Company_Name',
    'trcommonname': 'Company_Name',
    'companycommonname': 'Company_Name',
})
if 'Company_Name' not in rics_raw.columns:
    rics_raw['Company_Name'] = np.nan

rics_raw['RIC'] = rics_raw['RIC'].astype(str).str.strip()
rics_df = (rics_raw[['RIC', 'Company_Name']]
           .loc[lambda d: d['RIC'].str.len() > 1]
           .loc[lambda d: ~d['RIC'].isin(['nan', 'None', ''])]
           .drop_duplicates('RIC').reset_index(drop=True))

rics_list = rics_df['RIC'].tolist()
batches   = list(make_batches(rics_list, BATCH_SIZE))
print(f"    -> {len(rics_list)} tickers | {len(batches)} lotes de {BATCH_SIZE}")

# =============================================================================
# PASO 1 — EURIBOR 1M
# El campo correcto para tasas de interés en Refinitiv es TR.FIXINGVALUE,
# no CLOSE (que es para activos de precio). Se prueban varios RICs y campos.
# =============================================================================
print("\n[1] Descargando EURIBOR 1M...")

rf_master = pd.DataFrame()

# Intento A: get_history con campo TR.FIXINGVALUE (campo correcto para tasas)
euribor_attempts = [
    ('EUR1MD=',      ['TR.FIXINGVALUE']),
    ('EURIBOR1MD=',  ['TR.FIXINGVALUE']),
    ('EUR1MD=',      ['TR.BID']),
    ('EURIBOR1MD=',  ['TR.BID']),
]
for ric_try, fields_try in euribor_attempts:
    try:
        print(f"    Intento get_history {ric_try} / {fields_try}...")
        rf_raw = rd.get_history(
            universe=[ric_try],
            fields=fields_try,
            interval='daily',
            start='2014-12-31',
            end='2025-12-31',
        )
        if rf_raw is not None and not rf_raw.empty:
            rf_raw = rf_raw.reset_index()
            for col in rf_raw.columns:
                if norm_key(col) in {'timestamp', 'date', 'index'}:
                    rf_raw = rf_raw.rename(columns={col: 'Date'})
                    break
            val_col = [c for c in rf_raw.columns if c != 'Date'][0]
            rf_raw['Date']     = pd.to_datetime(rf_raw['Date']).dt.normalize()
            rf_raw['Rf_daily'] = to_num(rf_raw[val_col]) / 100 / 12
            rf_master = (rf_raw[['Date', 'Rf_daily']]
                         .dropna().drop_duplicates('Date')
                         .sort_values('Date').reset_index(drop=True))
            if len(rf_master) > 100:
                print(f"    OK {ric_try}: {len(rf_master):,} días")
                break
            else:
                rf_master = pd.DataFrame()
    except Exception as e:
        print(f"    {ric_try}/{fields_try} falló: {str(e)[:80]}")

# Intento B: get_data mensual con TR.EURIBOR1MD=
if rf_master.empty:
    print("    Intentando get_data mensual...")
    rf_chunks = []
    for yr in range(2014, 2026):
        for s, e in [(f'{yr}-01-01', f'{yr}-06-30'), (f'{yr}-07-01', f'{yr}-12-31')]:
            for ric_try in ['EURIBOR1MD=', 'EUR1MD=']:
                try:
                    df_rf = rd.get_data(
                        universe=[ric_try],
                        fields=['TR.FIXINGVALUE', 'TR.FIXINGVALUE.Date'],
                        parameters={'SDate': s, 'EDate': e, 'Frq': 'M'},
                    )
                    if df_rf is not None and not df_rf.empty:
                        rf_chunks.append(df_rf)
                        break
                    time.sleep(0.15)
                except Exception:
                    pass

    if rf_chunks:
        rf_raw = pd.concat(rf_chunks, ignore_index=True)
        print(f"    Columnas get_data EURIBOR: {rf_raw.columns.tolist()}")
        # Detectar columna de fecha y de valor
        date_c = next((c for c in rf_raw.columns
                       if norm_key(c) in {'date','trfixingvaluedate','fixingvaluedate',
                                          'trfixingvalue date'}), None)
        rate_c = next((c for c in rf_raw.columns
                       if norm_key(c) in {'trfixingvalue','fixingvalue',
                                          'trbid','bid','rate','value'}), None)
        if date_c and rate_c:
            rf_m = rf_raw[[date_c, rate_c]].copy()
            rf_m.columns = ['Date', 'Rate']
            rf_m['Date'] = pd.to_datetime(rf_m['Date'], errors='coerce')
            rf_m['Rate'] = to_num(rf_m['Rate'])
            rf_m = rf_m.dropna().drop_duplicates('Date').sort_values('Date')
            full = pd.DataFrame({'Date': pd.date_range('2014-12-01', '2025-12-31', freq='D')})
            rf_exp = full.merge(rf_m, on='Date', how='left')
            rf_exp['Rate']     = rf_exp['Rate'].ffill().bfill()
            rf_exp['Rf_daily'] = rf_exp['Rate'] / 100 / 12
            rf_master = rf_exp[['Date', 'Rf_daily']].dropna().reset_index(drop=True)
            print(f"    OK get_data mensual ffill: {len(rf_master):,} días")

# Fallback C: serie histórica aproximada con niveles reales del EURIBOR 1M
if rf_master.empty:
    print("    Usando serie histórica aproximada del EURIBOR 1M.")
    dates = pd.date_range('2014-12-01', '2025-12-31', freq='D')
    def euribor_approx(d):
        if   d < pd.Timestamp('2015-03-01'): return  0.05 / 100 / 12
        elif d < pd.Timestamp('2016-04-01'): return -0.10 / 100 / 12
        elif d < pd.Timestamp('2022-07-01'): return -0.50 / 100 / 12
        elif d < pd.Timestamp('2022-09-01'): return -0.10 / 100 / 12
        elif d < pd.Timestamp('2022-12-01'): return  0.50 / 100 / 12
        elif d < pd.Timestamp('2023-03-01'): return  1.50 / 100 / 12
        elif d < pd.Timestamp('2023-06-01'): return  2.50 / 100 / 12
        elif d < pd.Timestamp('2023-09-01'): return  3.40 / 100 / 12
        elif d < pd.Timestamp('2024-06-01'): return  3.86 / 100 / 12
        elif d < pd.Timestamp('2024-10-01'): return  3.65 / 100 / 12
        elif d < pd.Timestamp('2024-12-01'): return  3.40 / 100 / 12
        else:                                return  3.15 / 100 / 12
    rf_master = pd.DataFrame({
        'Date':     dates,
        'Rf_daily': [euribor_approx(d) for d in dates]
    })
    print(f"    Serie aproximada: {len(rf_master):,} días")

rf_master['Date'] = pd.to_datetime(rf_master['Date']).dt.normalize()
print(f"    Rango: {rf_master['Date'].min().date()} → {rf_master['Date'].max().date()}")
print(f"    Media: {rf_master['Rf_daily'].mean()*12*100:.2f}% anual")

# =============================================================================
# PASO 2 — DATOS ANUALES: ESG Y FUNDAMENTALES EN LLAMADAS SEPARADAS
#
# MOTIVO: Refinitiv ignora campos como TR.ESGCombinedScore, TR.ROA y
# TR.PriceToBookValue cuando van en la misma llamada que TR.TRESGScore.
# Solución: dos llamadas get_data independientes, luego merge por RIC+fecha.
# =============================================================================
print("\n[2a] Descargando datos ESG anuales (2014-2025)...")

ESG_RENAME = {
    'trtresgscore':              'ESG_Score',
    'tresgscore':                'ESG_Score',
    'esgscore':                  'ESG_Score',
    'lsegesgscore':              'ESG_Score',
    'trtresgscoredatedate':      'ESG_Report_Date',
    'tresgscoredatedate':        'ESG_Report_Date',
    'esgscoredatedate':          'ESG_Report_Date',
    'tresgcombinedscore':        'ESG_Combined_Score',
    'esgcombinedscore':          'ESG_Combined_Score',
    # E_Score: 'Environmental Pillar Score' → norm_key → 'environmentalpillarscore'
    'trenvironmentalpillarscore': 'E_Score',
    'environmentalpillarscore':   'E_Score',
    'trenvironmentpillarscore':   'E_Score',
    'environmentpillarscore':     'E_Score',
    'trsocialpillarscore':        'S_Score',
    'socialpillarscore':          'S_Score',
    'trgovernancepillarscore':    'G_Score',
    'governancepillarscore':      'G_Score',
}

esg_raw = download_annual_batches(batches, ESG_FIELDS, ANNUAL_PARAMS_ESG, 'ESG')
print(f"    Columnas RAW ESG: {esg_raw.columns.tolist()}")

ric_c = get_ric_col(esg_raw)
if ric_c and ric_c != 'RIC':
    esg_raw = esg_raw.rename(columns={ric_c: 'RIC'})
esg_df = smart_rename(esg_raw, ESG_RENAME)
print(f"    Columnas tras rename ESG: {esg_df.columns.tolist()}")

if 'ESG_Report_Date' not in esg_df.columns and 'Date' in esg_df.columns:
    esg_df = esg_df.rename(columns={'Date': 'ESG_Report_Date'})
esg_df['ESG_Report_Date'] = pd.to_datetime(esg_df.get('ESG_Report_Date'), errors='coerce')
for col in ['ESG_Score', 'ESG_Combined_Score', 'E_Score', 'S_Score', 'G_Score']:
    if col in esg_df.columns:
        esg_df[col] = to_num(esg_df[col])
    else:
        esg_df[col] = np.nan

print(f"\n[2b] Descargando datos fundamentales anuales (2014-2025)...")

FUND_RENAME = {
    'trpricetobookvalue':          'Price_To_Book',
    'pricetobookvalue':            'Price_To_Book',
    'pricetobook':                 'Price_To_Book',
    'pricetobookratio':            'Price_To_Book',
    'trpricetobookvaluedatedate':  'Fundamental_Report_Date',
    'pricetobookvaluedatedate':    'Fundamental_Report_Date',
    'trroa':                       'ROA',
    'roa':                         'ROA',
    'returnonassets':              'ROA',
    'roaactual':                   'ROA',
    'trtotalassetsreported':       'Total_Assets_EUR',
    'totalassetsreported':         'Total_Assets_EUR',
    'totalassets':                 'Total_Assets_EUR',
    'trtotaldebt':                 'Total_Debt_EUR',
    'totaldebt':                   'Total_Debt_EUR',
    'trbookvaluepershare':         'Book_Value_Per_Share_EUR',
    'bookvaluepershare':           'Book_Value_Per_Share_EUR',
    'trreportedcurrencycode':      'Reporting_Currency',
    'reportedcurrencycode':        'Reporting_Currency',
    'currencycode':                'Reporting_Currency',
}

fund_raw = download_annual_batches(batches, FUND_FIELDS, ANNUAL_PARAMS_FUND, 'FUND')
print(f"    Columnas RAW FUND: {fund_raw.columns.tolist()}")

ric_c = get_ric_col(fund_raw)
if ric_c and ric_c != 'RIC':
    fund_raw = fund_raw.rename(columns={ric_c: 'RIC'})
fund_df = smart_rename(fund_raw, FUND_RENAME)
print(f"    Columnas tras rename FUND: {fund_df.columns.tolist()}")

if 'Fundamental_Report_Date' not in fund_df.columns and 'Date' in fund_df.columns:
    fund_df = fund_df.rename(columns={'Date': 'Fundamental_Report_Date'})
fund_df['Fundamental_Report_Date'] = pd.to_datetime(fund_df.get('Fundamental_Report_Date'), errors='coerce')
for col in ['Price_To_Book', 'ROA', 'Total_Assets_EUR', 'Total_Debt_EUR', 'Book_Value_Per_Share_EUR']:
    if col in fund_df.columns:
        fund_df[col] = to_num(fund_df[col])
    else:
        fund_df[col] = np.nan

# ── Merge ESG + Fundamentales ─────────────────────────────────────────────
print("\n[2c] Fusionando ESG y fundamentales...")

esg_df  = esg_df.dropna(subset=['RIC']).sort_values(['RIC', 'ESG_Report_Date'])
fund_df = fund_df.dropna(subset=['RIC']).sort_values(['RIC', 'Fundamental_Report_Date'])

# Merge por RIC: para cada registro ESG, unir el fundamental más cercano hacia atrás
annual_df = pd.merge_asof(
    esg_df.sort_values(['RIC', 'ESG_Report_Date']),
    fund_df[['RIC', 'Fundamental_Report_Date', 'Price_To_Book', 'ROA',
             'Total_Assets_EUR', 'Total_Debt_EUR', 'Book_Value_Per_Share_EUR',
             'Reporting_Currency']].sort_values(['RIC', 'Fundamental_Report_Date']),
    by='RIC',
    left_on='ESG_Report_Date',
    right_on='Fundamental_Report_Date',
    direction='nearest',
    tolerance=pd.Timedelta('400 days'),
)

annual_df['Report_Date'] = annual_df['ESG_Report_Date'].fillna(
    annual_df.get('Fundamental_Report_Date', pd.NaT)
)
annual_df = annual_df.dropna(subset=['RIC']).sort_values(['RIC', 'Report_Date']).reset_index(drop=True)

print(f"    Registros anuales combinados: {len(annual_df):,}")
print(f"    Cobertura:")
for col in ['ESG_Score', 'ESG_Combined_Score', 'E_Score', 'S_Score', 'G_Score',
            'Price_To_Book', 'ROA', 'Total_Assets_EUR']:
    if col in annual_df.columns:
        pct = annual_df[col].notna().mean() * 100
        print(f"      {col:<30}: {pct:.1f}%")
    else:
        print(f"      {col:<30}: AUSENTE")

merge_ann_cols = (
    ['Report_Date'] + ANNUAL_COLS_ALL +
    [c for c in ['ESG_Report_Date', 'Fundamental_Report_Date']
     if c in annual_df.columns]
)

# =============================================================================
# PASO 3 — LOOP ANUAL: DATOS DIARIOS + MERGE + CSV
# =============================================================================
print(f"\n[3] Construyendo panel diario {START_YEAR}-{END_YEAR}...")

# Mapa de rename exhaustivo para los campos diarios
# Incluye variantes con y sin prefijo TR. que Refinitiv devuelve según versión
DAILY_RENAME = {
    # Precio de cierre
    'trpriceclose':          'Price_Close_EUR',
    'priceclose':            'Price_Close_EUR',
    'close':                 'Price_Close_EUR',
    # Moneda original
    'trpriceclosecurrency':  'Currency_Original',
    'priceclosecurrency':    'Currency_Original',
    'currency':              'Currency_Original',
    # Retorno — variantes con y sin prefijo, con y sin '1d'
    'trtotalreturn1d':       'Return_1D_pct',
    'totalreturn1d':         'Return_1D_pct',
    'trtotalreturn':         'Return_1D_pct',
    'totalreturn':           'Return_1D_pct',
    'return1d':              'Return_1D_pct',
    'dailytotalreturn':      'Return_1D_pct',
    # Market Cap
    'trcompanymarketcap':    'Market_Cap_EUR',
    'companymarketcap':      'Market_Cap_EUR',
    'marketcap':             'Market_Cap_EUR',
    # Volumen
    'trvolume':              'Volume',
    'volume':                'Volume',
}

for year in range(START_YEAR, END_YEAR + 1):
    start_date = f'{year}-01-01'
    end_date   = f'{year}-12-31'
    print(f"\n  AÑO {year}  ({start_date} -> {end_date})")
    print(f"  {'=' * 56}")

    # ── 3a. Descarga diaria ────────────────────────────────────────────────
    daily_chunks = []
    for idx, batch in enumerate(batches):
        try:
            df_d = rd.get_history(
                universe=batch,
                fields=DAILY_FIELDS,
                interval='daily',
                start=start_date,
                end=end_date,
                parameters=DAILY_PARAMS,
            )
            if df_d is None or df_d.empty:
                continue
            temp = flatten_get_history(df_d)
            if 'RIC' not in temp.columns:
                print(f"    Lote {idx+1}: RIC no encontrado — cols: {temp.columns.tolist()[:6]}")
                continue
            # Mostrar columnas del primer lote para diagnóstico
            if idx == 0:
                print(f"    Columnas RAW diarias (lote 1): {temp.columns.tolist()}")
            temp = smart_rename(temp, DAILY_RENAME)
            daily_chunks.append(temp)
            time.sleep(SLEEP_SEC)
        except Exception as e:
            print(f"    Lote {idx+1} error: {e}")

    if not daily_chunks:
        print(f"    Sin datos para {year}, saltando.")
        continue

    # ── 3b. Ensamblar y limpiar ────────────────────────────────────────────
    panel = pd.concat(daily_chunks, ignore_index=True)
    panel['Date'] = pd.to_datetime(panel['Date'], errors='coerce').dt.normalize()
    panel = panel[
        (panel['Date'] >= pd.Timestamp(start_date)) &
        (panel['Date'] <= pd.Timestamp(end_date))
    ].copy()

    # Conversión numérica
    for col in ['Price_Close_EUR', 'Return_1D_pct', 'Market_Cap_EUR', 'Volume']:
        if col in panel.columns:
            panel[col] = to_num(panel[col])

    # Return de % a decimal
    if 'Return_1D_pct' in panel.columns:
        panel['Return_1D'] = panel['Return_1D_pct'] / 100
        panel.drop(columns=['Return_1D_pct'], inplace=True)
    else:
        # Diagnóstico: mostrar qué columnas sí llegaron
        print(f"    AVISO: Return_1D_pct no encontrada.")
        print(f"    Columnas disponibles: {[c for c in panel.columns if 'ret' in c.lower() or 'return' in c.lower()]}")
        panel['Return_1D'] = np.nan

    # Redondear a 4 decimales — resuelve 307 vs 307.0 vs 307.0000
    for col in ['Price_Close_EUR', 'Return_1D', 'Market_Cap_EUR']:
        if col in panel.columns:
            panel[col] = panel[col].round(4)

    panel = panel.sort_values(['RIC', 'Date']).reset_index(drop=True)
    print(f"    Filas brutas   : {len(panel):,} | Empresas: {panel['RIC'].nunique()}")

    # ── 3c. Nombre de empresa ──────────────────────────────────────────────
    panel = panel.merge(rics_df[['RIC', 'Company_Name']], on='RIC', how='left')

    # ── 3d. Merge EURIBOR ─────────────────────────────────────────────────
    cal = pd.DataFrame({'Date': pd.date_range(start_date, end_date, freq='D')})
    rf_year = cal.merge(rf_master, on='Date', how='left')
    rf_year['Rf_daily'] = rf_year['Rf_daily'].ffill().bfill()
    panel = panel.merge(rf_year[['Date', 'Rf_daily']], on='Date', how='left')
    panel['Excess_Return_1D'] = panel['Return_1D'] - panel['Rf_daily']

    # ── 3e. Merge datos anuales (merge_asof backward) ─────────────────────
    annual_sub = annual_df[
        annual_df['RIC'].isin(panel['RIC'].unique()) &
        annual_df['Report_Date'].notna()
    ].copy()
    annual_sub['Report_Date'] = pd.to_datetime(annual_sub['Report_Date'])

    merged_list = []
    for ric, grp_d in panel.groupby('RIC', sort=False):
        grp_d = grp_d.sort_values('Date').copy()
        grp_a = annual_sub[annual_sub['RIC'] == ric].sort_values('Report_Date')
        if grp_a.empty:
            for col in ANNUAL_COLS_ALL:
                if col not in grp_d.columns:
                    grp_d[col] = np.nan if col != 'Reporting_Currency' else None
            grp_d['ESG_Report_Date']         = pd.NaT
            grp_d['Fundamental_Report_Date'] = pd.NaT
            merged_list.append(grp_d)
            continue
        cols_disp = [c for c in merge_ann_cols if c in grp_a.columns]
        merged = pd.merge_asof(
            grp_d, grp_a[cols_disp],
            left_on='Date', right_on='Report_Date',
            direction='backward',
        )
        merged_list.append(merged)

    panel = pd.concat(merged_list, ignore_index=True)

    # ── 3f. Eliminar filas sin retorno ─────────────────────────────────────
    panel = panel.dropna(subset=['Return_1D'])
    print(f"    Filas finales  : {len(panel):,}")

    # ── 3g. Cobertura ──────────────────────────────────────────────────────
    print_coverage(panel, year)

    # ── 3h. Timestamp y orden de columnas ──────────────────────────────────
    panel['Date'] = pd.to_datetime(panel['Date']).dt.strftime('%Y-%m-%d')
    panel = panel[[c for c in COL_ORDER if c in panel.columns]]

    # ── 3i. Guardar CSV ────────────────────────────────────────────────────
    # float_format='%.4f' → 307, 307.0, 307.000 → siempre 307.0000
    fname = f'stoxx600_DEFENSA_{year}.csv'
    panel.to_csv(fname, index=False, float_format='%.4f')
    print(f"\n    Guardado: {fname} ({len(panel):,} filas)")

# =============================================================================
# CIERRE
# =============================================================================
rd.close_session()
print("""
DESCARGA COMPLETA
Archivos: stoxx600_DEFENSA_2015.csv ... stoxx600_DEFENSA_2025.csv
""")
