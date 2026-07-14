# H3 — Robustez del modelo calma/crisis (respuesta a la observación del tribunal)

**Fecha:** 2026-07-06
**Estado:** scripts listos para ejecutar en Colab (no modifican nada del pipeline original)

---

## 1. La observación

En la defensa del Hito 4 el tribunal señaló que el Markov-Switching de la H3 está
**desbalanceado**: el MS(2) sobre retornos diarios clasifica **18 de 120 meses (15%)**
como crisis (453 de 2.567 días). El δ del CAPM condicional se estima, por tanto, con
pocas observaciones en el régimen de crisis. Sugerencia recibida: probar otro modelo
matemático para el esquema calma/crisis.

**Objetivo de esta carpeta:** obtener *prueba suficiente* de si la elección del
modelo de régimen afecta al resultado de la H3, para decidir con evidencia si hay
que cambiar el modelo o basta con documentar la robustez.

## 2. Los dos modelos alternativos propuestos

| | Modelo | Por qué responde a la crítica |
|---|---|---|
| **A2** | **GARCH(1,1)-t + umbral de cuantil** sobre la volatilidad condicional del mercado (crisis = mes en el cuartil superior, P75) | El **balance queda fijado por diseño** (25% de meses en crisis, ≥30 obs por régimen). No estima mezclas → sin riesgo de régimen degenerado. Modelo canónico de volatilidad (Bollerslev 1986; clasificación tipo Schwert 1989). Sensibilidad P70–P85 en A4. |
| **A3** | **CAPM de transición suave (LSTAR)** — la beta transita continuamente con la volatilidad realizada mensual del mercado: β(s_t) = β + δ·G(s_t), G logística (Teräsvirta 1994; Lin & Teräsvirta 1994) | **Elimina la clasificación binaria**: no existe dummy, luego la crítica de desbalance **no aplica por construcción** — todos los meses aportan información ponderada por su grado de estrés. La variable de transición (vol. realizada) es libre de modelo → independiente de A2. Incluye test de linealidad LM que justifica la especificación. |

Los δ de ambos modelos miden lo mismo que el δ del MS-CAPM (Δβ entre calma y
crisis extremas) → comparación directa.

**Descartados y por qué** (argumentos para la defensa):
- **MS de 3 regímenes:** agrava el problema — más parámetros de mezcla con los mismos 120 meses.
- **MS-GARCH:** ya explorado (jun-2026); sigue siendo una mezcla markoviana, no responde a la crítica de desbalance.
- **Fechas de crisis exógenas (COVID, Ucrania…):** pierde la detección endógena, introduce arbitrariedad del investigador.

## 3. Batería de pruebas estadísticas (Script A4)

1. **Concordancia de clasificaciones:** kappa de Cohen entre las tres dummies,
   Spearman entre las medidas continuas de estrés (P(crisis) MS, σ GARCH, G LSTAR),
   y **RCM de Ang & Bekaert (2002)** — si el RCM del MS es bajo, la clasificación es
   nítida aunque desbalanceada.
2. **Tabla comparativa de δ** (4 scores × Q1/Q5/L-S × 3 modelos) con la misma Etapa 2
   (OLS + Newey-West) + concordancia de la decisión cualitativa.
3. **Bootstrap pareado por bloques móviles** (B=2.000, bloques de 6 meses): IC 95% y
   p-valor de (δ_alternativo − δ_MS). Es el test formal de "¿afecta el modelo al resultado?".
4. **AIC/BIC** de las tres especificaciones de Etapa 2 (misma Y, misma n → comparables).
5. **Sensibilidad al balance** (ESG Q5, hallazgo central): δ al variar el corte de
   P(crisis) del MS (0.30–0.70) y el cuantil GARCH (P70–P85) → responde directamente
   a la crítica, mostrando si δ depende del grado de balance.
6. **Veredicto automático** con criterio de decisión pre-especificado (sección 5).

## 4. Cómo ejecutar en Colab

Pegar cada archivo `.txt` como celda nueva **al final** del notebook principal,
en este orden (requieren variables en memoria del pipeline):

```
Pipeline habitual:  Script 2 → 2.3 → 3.1 → 3.2 → 3.3 → 3.4
Después añadir:     A2_H3_Alt1_GARCH_Umbral.txt      (instala 'arch' si falta)
                    A3_H3_Alt2_LSTAR.txt
                    A4_H3_Contraste_Modelos.txt
                    A5_H3_Direccional_Bajista.txt    (tras el resultado del A4)
```

Outputs en Drive: `TFM_STOXX600/HITO4/H3_ROBUSTEZ/` — 3 figuras
(`a2_garch_regimen.png`, `a3_lstar_transicion.png`, `a4_contraste_modelos.png`)
y 4 CSV con las tablas del contraste.

## 5. Criterio de decisión (pre-especificado)

**MANTENER el MS-CAPM** como modelo principal (añadiendo esta carpeta como anexo de
robustez) si se cumplen los tres criterios sobre el hallazgo central (ESG Q1 y Q5):

- **(i)** la decisión cualitativa (refugio / amplifica / sin cambio) coincide en los 3 modelos;
- **(ii)** los IC bootstrap de (δ_alt − δ_MS) contienen el 0;
- **(iii)** el δ de Q5 conserva signo y significancia al variar el grado de balance.

**CAMBIAR de modelo** si falla (i) o (ii) → adoptar el de mejor AIC/BIC como principal.
Si solo falla (iii) → preferir GARCH-umbral (balance por diseño) o LSTAR (sin dummy).

## 6. Qué escribir en el TFM según el resultado (sin reescribir nada aún)

- **Si el veredicto es MANTENER:** párrafo en la sección metodológica de la H3 +
  anexo con la tabla comparativa de δ, el bootstrap y la figura de sensibilidad.
  Argumento: *el desbalance refleja que las crisis son escasas por naturaleza en
  2016–2025; el hallazgo es invariante al modelo de detección (mezcla markoviana,
  umbral GARCH, transición suave) y al grado de balance*.
- **Si el veredicto es CAMBIAR:** el modelo ganador por AIC/BIC pasa a ser la
  especificación principal de la H3 y el MS-CAPM queda como análisis inicial;
  habría que actualizar tablas y conclusión de la H3 (decisión a tomar en ese momento).

## 7. Resultado del A4 (corrida Colab 2026-07-06) y script A5

La corrida real del A4 dio **resultado mixto**: los tres modelos coinciden en rechazar
H3 (el ESG no es refugio bajo ninguna especificación) y el bootstrap no detecta
diferencias de δ (23/24 IC contienen el 0), **pero el hallazgo especular se invierte**:
bajo GARCH-umbral y LSTAR la amplificación significativa aparece en Q1 (no en Q5).
Diagnóstico: el MS (media cambiante, μ_crisis<0) detecta regímenes *bajistas*, mientras
GARCH/LSTAR clasifican solo por *volatilidad* e incluyen rebotes (jul/ago/nov-2020) y
sustos sin caída (feb-2018, ago-2019, mar-2023).

**`A5_H3_Direccional_Bajista.txt`** contrasta esa explicación: (1) verifica que los
meses discordantes son rebotes (Rm>0); (2) reestima las alternativas con dirección —
GARCH-direccional (σ>P75 ∧ Rm<0) y LSTAR sobre **semivolatilidad negativa** RV⁻
(Markowitz 1959; Ang, Chen & Xing 2006); (3) veredicto: si reproducen el patrón del MS,
el hallazgo especular queda rescatado como fenómeno de **mercados bajistas**; si no,
se degrada a evidencia sugestiva (guía de redacción impresa en cada escenario).

## 8. Referencias para citar

- Bollerslev (1986) — GARCH. · Schwert (1989) — regímenes de volatilidad por umbral.
- Teräsvirta (1994); Lin & Teräsvirta (1994) — modelos STR/LSTAR y test LM de linealidad.
- Ang & Bekaert (2002) — Regime Classification Measure (RCM).
- Landis & Koch (1977) — interpretación de kappa. · Künsch (1989) — block bootstrap.
- Burnham & Anderson (2002) — comparación por AIC.
