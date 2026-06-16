# Bibliografía y Referencias

Documentación de referencia utilizada en el TFM.

## 📚 Guías Metodológicas

### `GUIA_BIBLIOGRAFIA_TFM.pdf`
- Bibliografía completa citada en el TFM
- Formato APA 7ª edición
- Clasificación por tema

### `MUFIB 25 26 - guia metodologica TFM.pdf`
- Guía metodológica del Master en Finanzas (UPF)
- Estructura de TFM
- Requerimientos de investigación

### `GUIA_ESTUDIO_DEFENSA_v2.pdf`
- Preparación para defensa del TFM
- Recomendaciones de presentación
- Preguntas frecuentes de evaluadores

---

## 🌱 ESG y Sostenibilidad

### `lseg-esg-scores-methodology.pdf`
- **Fuente:** LSEG/Refinitiv (London Stock Exchange Group)
- **Contenido:** Metodología oficial de cálculo de scores ESG
- **Relevancia:** Define cómo se construyen los scores E/S/G utilizados en el análisis
- **Temas:** 
  - Definición de pilares ESG
  - Indicadores por sector
  - Fórmulas de agregación
  - Validación y auditoría

### `2026-desafios-inversion-sostenible-dark-green-2a-ed.pdf`
- **Título:** Desafíos de la Inversión Sostenible (Dark Green, 2ª edición)
- **Contenido:** Marco conceptual de inversión ESG
- **Temas:**
  - Green washing y greenwashing
  - Riesgos de transición
  - Regulación (Taxonomía EU, CSRD)
  - Integración ESG en portafolios

### `ESG_datasolutions_internaldoc.pdf`
- **Fuente:** Documento interno de ESG Data Solutions
- **Contenido:** Análisis de coverage y quality de datos ESG
- **Relevancia:** Explica limitaciones y gaps en cobertura de datos ESG
- **Temas:**
  - Metodología de validación de datos
  - Cobertura por sector geográfico
  - Evolución temporal de la data ESG

---

## 📏 Normas de Referencia

### `Guia-Normas-APA-7ma-edicion.pdf`
- Guía completa de formato APA 7ª edición
- Usada para todas las citas y referencias en el TFM
- Incluye:
  - Formato de citas
  - Bibliografía
  - Tablas y figuras
  - Ejemplos de diferentes fuentes

---

## 🔗 Referencias Teóricas Clave

Las siguientes referencias académicas están citadas en el TFM (ver `GUIA_BIBLIOGRAFIA_TFM.pdf` para detalles):

### Teoría Moderna de Portafolios
- **Markowitz (1952):** Portfolio Selection
- **Sharpe (1964):** Capital Asset Pricing Model (CAPM)
- **Fama & French (1993):** Common Risk Factors in the Returns on Stocks and Bonds

### Factor Models
- **Carhart (1997):** On Persistence in Mutual Fund Performance
  - Añade factor momentum (WML) a Fama-French
  - Base del modelo de H1

### Panel Methods & Time Series
- **Newey & West (1987):** Heteroskedasticity and Autocorrelation Consistent Covariance Matrix
  - Métodos robustos para datos autocorrelacionados
  - Usado en H1 (Carhart 4F)

- **Driscoll & Kraay (1998):** Consistent Covariance Matrix Estimation with Spatially Dependent Panel Data
  - Métodos para panel dinámico con correlación espacial-temporal
  - Usado en H2 (Tobin Q)

- **Hamilton (1989):** A New Approach to the Economic Analysis of Nonstationary Time Series
  - Markov-Switching models
  - Base de H3

### Régimen Switching
- **Hamilton & Susmel (1994):** Autoregressive Conditional Heteroskedasticity and Changes in Regime
  - ARCH-GARCH con cambios de régimen

### ESG y Riesgo de Inversión
- **Pástor, Stambaugh & Taylor (2021):** Sustainable Investing in Equilibrium
  - "Green Premium": por qué ESG genera menores retornos
  - Marco teórico de H1

- **Bolton & Kacperczyk (2021):** Do Investors Care About Carbon Risk?
  - Riesgo "brown" (transición energética)
  - Explicación de amplificación de beta en crisis (H3)

- **Friede, Busch & Bassen (2015):** ESG and financial performance: aggregated evidence
  - Meta-análisis de relación ESG-retornos
  - Contexto de la paradoja del Green Premium

---

## 📖 Cómo Citar Este TFM

```bibtex
@mastersthesis{bergero2026esg,
  author = {Bergero, Leandro},
  title = {Impacto del desempeño ESG en Alpha y Beta de empresas del STOXX 600},
  school = {Universitat Autònoma de Barcelona, Master en Finanzas (MUFIB)},
  year = {2026},
  note = {Disponible en: https://github.com/leabergero/tfm-esg-alpha-beta-stoxx600}
}
```

---

## 📝 Referencias por Hipótesis

### H1: Green Premium (Carhart 4F)
- Carhart (1997)
- Pástor, Stambaugh & Taylor (2021)
- Fama & French (1993)
- Newey & West (1987)

### H2: Valuación (Panel Tobin Q)
- Driscoll & Kraay (1998)
- Bolton & Kacperczyk (2021)

### H3: Beta en Crisis (Markov-Switching)
- Hamilton (1989)
- Hamilton & Susmel (1994)
- Bolton & Kacperczyk (2021)

---

## 📊 Metodología ESG

Para entender cómo se construyen los scores ESG:
1. Lee `lseg-esg-scores-methodology.pdf` (definiciones)
2. Consulta `ESG_datasolutions_internaldoc.pdf` (cobertura y validez)
3. Ver sección 4 del `scripts/2. Carga Consolidacion y Analisis.py` para implementación

---

## 🔍 Búsqueda de Literatura Adicional

### Bases de datos recomendadas
- **Google Scholar:** https://scholar.google.com
- **SSRN:** https://ssrn.com (finance research)
- **JStor:** https://www.jstor.org (mediante acceso institucional UPF)
- **ScienceDirect:** https://www.sciencedirect.com

### Palabras clave para búsquedas
- ESG performance anomaly
- Green premium investing
- Fama-French factors
- Markov-switching CAPM
- Sustainable investing returns
- Brown risk financial markets

---

## 📅 Última Actualización
16 de junio de 2026
