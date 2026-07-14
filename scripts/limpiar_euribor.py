"""
Limpia el archivo de tasas euribor eliminando:
  - Sábados y domingos
  - Festivos bursátiles europeos de CIERRE TOTAL

Mantiene 24-dic y 31-dic (CIERRE PARCIAL: el mercado opera hasta las 14h),
siempre que sean días laborables.

El archivo FESTIVOS.MD solo contiene el calendario 2026, pero los datos cubren
2014-2025, por lo que el calendario se genera por año con el conjunto estándar de
cierres totales comunes a las bolsas europeas (Euronext, BME, Borsa Italiana, LSE):
  - 01/01  Año Nuevo
  - Viernes Santo (Pascua - 2 días)
  - Lunes de Pascua (Pascua + 1 día)
  - 01/05  Día del Trabajador
  - 25/12  Navidad
  - 26/12  Boxing Day / San Esteban
"""
import datetime as dt
import pandas as pd

ENTRADA = "euribor_tasas_diarias_2014_2025.csv"
SALIDA = "euribor_tasas_diarias_2014_2025_corregido.csv"


def domingo_pascua(anio: int) -> dt.date:
    """Algoritmo de Gauss/Meeus (Gregoriano) para el Domingo de Pascua."""
    a = anio % 19
    b = anio // 100
    c = anio % 100
    d = b // 4
    e = b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i = c // 4
    k = c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    mes = (h + l - 7 * m + 114) // 31
    dia = ((h + l - 7 * m + 114) % 31) + 1
    return dt.date(anio, mes, dia)


def festivos_anio(anio: int) -> set:
    pascua = domingo_pascua(anio)
    return {
        dt.date(anio, 1, 1),                 # Año Nuevo
        pascua - dt.timedelta(days=2),       # Viernes Santo
        pascua + dt.timedelta(days=1),       # Lunes de Pascua
        dt.date(anio, 5, 1),                 # Día del Trabajador
        dt.date(anio, 12, 25),               # Navidad
        dt.date(anio, 12, 26),               # Boxing Day / San Esteban
    }


df = pd.read_csv(ENTRADA, parse_dates=["Date"])
df["Date"] = df["Date"].dt.date

anios = range(df["Date"].min().year, df["Date"].max().year + 1)
festivos = set().union(*(festivos_anio(a) for a in anios))

es_finde = df["Date"].apply(lambda d: d.weekday() >= 5)   # 5=sáb, 6=dom
es_festivo = df["Date"].apply(lambda d: d in festivos)
eliminar = es_finde | es_festivo

n_total = len(df)
df_limpio = df.loc[~eliminar].copy()

df_limpio.to_csv(SALIDA, index=False)

print(f"Filas originales : {n_total}")
print(f"  - fines de semana eliminados : {int(es_finde.sum())}")
print(f"  - festivos eliminados        : {int(es_festivo.sum())}")
print(f"  - solapados (festivo en finde): {int((es_finde & es_festivo).sum())}")
print(f"Filas eliminadas : {int(eliminar.sum())}")
print(f"Filas resultantes: {len(df_limpio)}")
print(f"Archivo generado : {SALIDA}")

# Verificación: 24 y 31 de diciembre deben permanecer si son laborables
dic_parcial = [d for d in df_limpio["Date"]
               if d.month == 12 and d.day in (24, 31)]
print(f"24/31-dic conservados (laborables): {len(dic_parcial)}")
