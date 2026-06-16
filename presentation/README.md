# Presentación del TFM

Archivos de presentación y materiales visuales.

## 📊 Archivos

### `Infografía TFM - Impacto ESG en Alpha y Beta.pdf`
- **Formato:** PDF (270 KB)
- **Contenido:** Infografía visual de hallazgos principales
- **Uso:** Presentación en defensa, redes sociales, comunicación

**Secciones:**
1. Resumen ejecutivo (3 hipótesis)
2. Metodología resumida
3. Resultados principales con visualizaciones
4. Interpretación económica

---

### `infografia_linkedin.html`
- **Formato:** HTML interactivo
- **Contenido:** Versión web responsive de la infografía
- **Ventajas:** Se abre en cualquier navegador, sin dependencias

**Cómo abrir:**
```bash
# En Linux/Mac
open infografia_linkedin.html

# O cualquier navegador
firefox infografia_linkedin.html
```

---

## 🎯 Contenido Visual

### H1: Green Premium
- Gráfico de alphas por quintil ESG
- Serie temporal del spread L-S
- Factor loadings Fama-French

### H2: Valuación (Tobin Q)
- Forest plot: β1 por especificación
- Scatter: relación Q vs. ESG
- Evolución temporal por terciles

### H3: Beta en Crisis
- Regímenes de mercado (Calma vs. Crisis)
- Betas condicionales
- Spread L-S por régimen

---

## 📄 Formato Recomendado para Defensa

1. **Portadas:** Carátula + objetivos (1 min)
2. **Contexto:** ESG, Green Premium, motivación (3 min)
3. **Metodología:** Datasets, modelos, especificaciones (4 min)
4. **Resultados:** H1 → H2 → H3 (10 min)
   - Enfatizar la convergencia de evidencia
   - Explicar la "paradoja" del Green Premium
5. **Conclusiones:** Implicaciones prácticas (2 min)
6. **Preguntas:** 5 min

**Total estimado:** 25 minutos

---

## 💡 Narrativa para la Defensa

### Apertura
> "Este TFM examina una paradoja: ¿por qué las empresas con mejor desempeño ESG generan retornos más bajos? Analizamos 598 empresas del STOXX 600 durante 2015-2025."

### Desarrollo H1
> "Encontramos que el quintil de mejor ESG (Q1) genera alpha de +0.34%/mes, mientras que el peor quintil (Q5) genera +0.94%/mes. El spread es negativo y significativo: −0.60%/mes con un t-stat de −5.2. Esto confirma el 'Green Premium': los inversores pagan un precio más alto por empresas con mejor ESG."

### Desarrollo H2
> "¿Afecta este premium a la valuación? Analizamos la Tobin Q con modelos de panel dinámico. El resultado principal es que no hay efecto robusto, pero sí hay sensibilidad en especificaciones alternativas. Esto sugiere que el premium ESG no se refleja completamente en la valuación contable."

### Desarrollo H3
> "Finalmente, estudiamos si el ESG protege en momentos de estrés. Usamos Markov-Switching para identificar regímenes de mercado. Encontramos un hallazgo especular: mientras que Q1 mantiene beta estable (~1.05), el quintil Q5 amplifica su beta en crisis (+0.21 puntos). El ESG proporciona protección relativa."

### Cierre
> "Estos tres hallazgos convergen en una interpretación: el ESG es un factor de riesgo no capturado por modelos estándar. El 'Green Premium' no es solo una preferencia de inversores, sino un ajuste real por el riesgo 'brown' que se materializa en estrés de mercado."

---

## 🎨 Recomendaciones Visuales

### Colores sugeridos
- Verde: ESG alto (Q1)
- Rojo: ESG bajo (Q5)
- Neutral: Gris para mercado general

### Fuentes
- Títulos: Sans-serif bold (Arial, Helvetica)
- Cuerpo: Sans-serif regular (12-14pt)
- Datos: Monospace para números (Courier New)

### Elementos visuales
- Usar iconos para cada hipótesis
- Gráficos con leyendas claras
- Tablas con alternancia de color

---

## 📱 Compartir en LinkedIn

**Sugerencia de post:**

```
"Hoy he presentado mi TFM sobre impacto del ESG en retornos y riesgo 
de empresas del STOXX 600. 🌱📊

Hallazgo principal: Existe un 'Green Premium' donde inversores pagan 
un precio más alto por mejor ESG, lo que resulta en retornos más bajos. 
Pero en tiempos de estrés, el ESG proporciona protección relativa.

Análisis de 598 empresas (2015-2025) usando:
✓ Carhart 4 Factores
✓ Panel Dinámico (Tobin Q)
✓ Markov-Switching CAPM

Links a resultados + código: [repo GitHub]

#ESG #FinanzasSostenibles #Investigación #STOXX600"
```

---

## 🔗 Recursos Complementarios

- Notebook Colab: `notebooks/`
- Scripts de análisis: `scripts/`
- Dataset consolidado: `data/processed/`

---

**Última actualización:** 16 de junio de 2026
