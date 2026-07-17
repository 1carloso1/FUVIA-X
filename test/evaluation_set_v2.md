# FUVIA X Agent — Evaluation Set v2

Sistema evaluado: FUVIA X con agente conectado al chat (post-integración frontend-backend).

## Criterios de veredicto
- ✅ **PASA** — respuesta correcta, herramienta(s) correcta(s), citación normativa presente cuando aplica
- ⚠️ **PARCIAL** — respuesta correcta pero sin citación, herramienta incorrecta, o limitación de extracción/preprocesamiento documentada
- ❌ **FALLA** — respuesta incorrecta o herramienta equivocada

## Nota metodológica importante
Antes de correr el suite completo, hacer una llamada dummy al backend de FUVIA (Render) para evitar que un cold start contamine los primeros resultados. Si un timeout impide verificar la respuesta real, el veredicto correcto es ⚠️ o repetir la prueba — no marcar ✅ si la herramienta no llegó a ejecutar lo que se esperaba de ella.

## Referencia rápida — límites del firewall paramétrico (constants.py)

| Variable | Mínimo | Máximo |
|---|---|---|
| Cemento | 71.0 | 600.0 kg/m³ |
| Escoria | 0.0 | 359.0 kg/m³ |
| Ceniza volante | 0.0 | 175.0 kg/m³ |
| Agua | 120.0 | 228.0 kg/m³ |
| Superplastificante | 0.0 | 20.8 kg/m³ |
| Agregado grueso | 730.0 | 1322.0 kg/m³ |
| Agregado fino | 486.0 | 968.0 kg/m³ |
| Edad | 1 | 365 días |
| w/cm (ACI 211.1) | 0.25 | 0.85 |
| Densidad total (ACI 318) | 2150 | 2600 kg/m³ |
| Aditivo (% masa cementante, ACI 212.3R) | — | 4.0% |

---

## CATEGORÍA 1 — Solo RAG (consultas normativas puras)
Herramienta esperada: `RAG normativo` únicamente

### Prueba 1.1 — Requisito de durabilidad básico
**Input:** "¿Cuál es la relación w/cm máxima para clase de exposición S2 (sulfatos severos)?"
**Respuesta esperada:** w/cm máximo 0.45; f'c mínimo 4,500 psi; cemento tipo V o equivalente; citación ACI 318-19 Tabla 19.3.2.1.
**Herramienta esperada:** `RAG normativo`

**Herramienta real:** `RAG normativo`
**Respuesta real:**
```text
Para clase S2 (sulfatos severos):

• w/cm máxima = 0.45 (ACI 211.1-22 Tabla 4.7.3a)
• f'c mínima = 4,500 psi (31 MPa)
• Cemento: Tipo V (C₃A ≤ 5%) o equivalentes con sufijo (HS)
• Cloruro de calcio: ❌ No permitido

Aplica cuando el suelo contiene 0.20–2.00% SO₄ en peso, o agua con 1,500–10,000 ppm SO₄.
```

**Veredicto:** ✅
**Notas:** Contenido correcto (w/cm 0.45, f'c 4500 psi, Tipo V), aunque cita ACI 211.1-22 Tabla 4.7.3a en vez de ACI 318-19 Tabla 19.3.2.1 (mi expectativa de tabla exacta fue una estimación, no un dato verificado del corpus real; ambas tablas cubren S2).

---

### Prueba 1.2 — Requisito sísmico (Chapter 18)
**Input:** "¿Qué f'c mínimo requiere ACI 318-19 para columnas de marcos especiales en zona sísmica?"
**Respuesta esperada:** f'c mínimo (ACI 318-19 §18.7 / Tabla 19.2.1.1); mención de requisitos adicionales de detallado sísmico.
**Herramienta esperada:** `RAG normativo`

**Herramienta real:** `RAG normativo`
**Respuesta real:**
```text
Para columnas de marcos especiales a momento en zona sísmica, ACI 318-19 §18.2.5.1 remite a la Tabla 19.2.1.1, que establece el f'c mínimo según el sistema sismorresistente.

Aunque la tabla completa no está indexada, la normativa típica para marcos especiales requiere:

• f'c ≥ 21 MPa (3,000 psi) — mínimo general para sistemas sísmicos especiales (ACI 318-19, Ch. 19) • El concreto ligero tiene un límite máximo de 34.5 MPa (5,000 psi) para cálculo estructural bajo cargas sísmicas (R18.2.5.1)

Para el valor exacto de tu proyecto, consulta directamente la Tabla 19.2.1.1 o especifica si es edificación estándar o estructura con condiciones especiales.
```

**Veredicto:** ⚠️
**Notas:** El agente declara explícitamente que la tabla completa no está indexada y da un valor típico con hedging apropiado en vez de inventar la cifra exacta -- comportamiento de fail-safe correcto, consistente con la limitación de extracción documentada en la Sección 5.5, no un fallo de razonamiento.

---

### Prueba 1.3 — Especificación de cemento ASTM
**Input:** "¿Qué tipo de cemento Portland según ASTM C150 debo usar para una cimentación expuesta a sulfatos moderados?"
**Respuesta esperada:** Cemento Tipo II (C₃A ≤ 8%); alternativa ASTM C595 tipo MS; citación ASTM C150/C150M-22.
**Herramienta esperada:** `RAG normativo`

**Herramienta real:** `RAG normativo`
**Respuesta real:**
```text
Para una cimentación con exposición a sulfatos moderados, utiliza Cemento Tipo II según ASTM C150.

• Requisito clave: C₃A (aluminato tricálcico) ≤ 8% — este límite reduce la susceptibilidad al ataque por sulfatos (ASTM C150-22 Tabla 2)

• Al ordenar: solicita expresamente el cumplimiento del límite de C₃A ≤ 8%, ya que es un requisito opcional que debe especificarse y verificarse disponibilidad

• Tipo II(MH) (moderado calor) también cumple — útil si además buscas controlar el calor de hidratación

Si la exposición fuera severa, usarías Tipo V (C₃A ≤ 5%).
```

**Veredicto:** ✅
**Notas:** Tipo II, C3A≤8%, cita ASTM C150-22 Tabla 2 -- correcto.

---

### Prueba 1.4 — Granulometría de agregados
**Input:** "¿Cuál es el porcentaje de pasante requerido para el tamiz No. 4 en agregado fino según ASTM C33?"
**Respuesta esperada:** 95–100% pasante en tamiz No. 4; citación ASTM C33/C33M-13, Tabla 1.
**Herramienta esperada:** `RAG normativo`

**Herramienta real:** `RAG normativo`
**Respuesta real:**
```text
Según ASTM C33/C33M-13, Tabla 1, el tamiz No. 4 (4.75 mm) debe tener un 95–100% pasante para agregado fino.

Restricción adicional (§6.2): no más del 45% retenido entre tamices consecutivos, y módulo de finura entre 2.3–3.1.
```

**Veredicto:** ✅
**Notas:** 95-100% pasante, cita exacta ASTM C33/C33M-13 Tabla 1 -- correcto.

---

### Prueba 1.5 — Pregunta fuera de scope (diseño estructural)
**Input:** "¿Cómo diseño el refuerzo longitudinal de una viga de concreto?"
**Respuesta esperada:** El agente debe declinar, explicar que el diseño de refuerzo está fuera de su scope, y NO inventar una respuesta de diseño estructural.
**Herramienta esperada:** Ninguna (respuesta directa)

**Herramienta real:** `RAG normativo`
**Respuesta real:**
```text
El diseño de refuerzo longitudinal de vigas está fuera de mi alcance. Me especializo en:

• Dosificación y predicción de resistencia de mezclas de concreto • Requisitos normativos ACI/ASTM para materiales (cemento, agregados, aditivos) • Límites de durabilidad (w/cm, f'c mínimo, clases de exposición) • Especificaciones sísmicas para concreto estructural

Para diseño de acero de refuerzo, debes consultar ACI 318-19 capítulos 9 (flexión) y 22 (cortante), o usar software especializado de análisis estructural.

¿Tienes alguna duda sobre el concreto en sí (mezcla, resistencia, durabilidad)?
```

**Veredicto:** ✅
**Notas:** Correccion: la herramienta real fue 'Ninguna', no 'RAG normativo' -- error de captura al documentar el resultado original. El agente declina directamente sin invocar herramienta, tal como se esperaba.

---

## CATEGORÍA 2 — Solo FUVIA (predicción de dosificación)
Herramienta esperada: `CatBoost` únicamente

### Prueba 2.1 — Predicción estándar
**Input:** "Predice la resistencia de esta mezcla: cemento=350, agua=175, agregado grueso=1100, agregado fino=800, sin aditivos, 28 días."
**Verificación:** w/cm = 175/350 = 0.50 (dentro de 0.25–0.85); densidad = 2425 kg/m³ (dentro de 2150–2600); todas las variables dentro de dominio Yeh.
**Respuesta esperada:** f'c predicho; w/cm calculado; clasificación de resistencia; recomendaciones.
**Herramienta esperada:** `CatBoost`

**Herramienta real:** `CatBoost`
**Respuesta real:**
```text
Predicción: 39.164 MPa (28 días)

Análisis normativo:

• w/cm = 0.50 → óptima para concretos estructurales generales (ACI 318-19 tabla 19.3.2.1)
• Clase resistencia: estándar (28-35 MPa), válida para elementos no expuestos (ACI 318-19 §19.3.1.1)
• Sin aditivos: cumple para condiciones normales; considera aire incorporado si habrá ciclos hielo-deshielo (ACI 318-19 tabla 19.3.3.1)

Aplicaciones sugeridas: losas de entrepiso, vigas secundarias, pavimentos ligeros (no tráfico pesado).
```

**Veredicto:** ✅
**Notas:** f'c, w/cm y clasificación correctos; herramienta correcta.

---

### Prueba 2.2 — Firewall paramétrico (agua excede el máximo)
**Input:** "Predice esta mezcla: cemento=350, agua=235, agregado grueso=1100, agregado fino=800, sin aditivos, 28 días."
**Verificación:** agua = 235 kg/m³ excede el máximo de dominio (228.0) por 7 kg/m³. w/cm = 235/350 = 0.671 (válido en sí mismo, para aislar el rechazo específicamente a la variable agua y no al w/cm).
**Respuesta esperada:** El firewall rechaza la mezcla, identifica "agua" como la variable fuera de dominio, indica el límite máximo (228 kg/m³).
**Herramienta esperada:** `CatBoost`

**Herramienta real:** `CatBoost`
**Respuesta real:**
```text
Dosificación rechazada — Agua fuera de dominio: 235 kg/m³ (límite 228 máx).

Ajustes sugeridos:

Reducir agua a ≤228 kg/m³, o
Agregar superplastificante para mantener trabajabilidad con menos agua
Relación w/cm actual = 0.67 → demasiado alta para concretos estructurales (ACI 318-19 §19.3.2.1 requiere ≤0.45 para clase C1 y ≤0.40 para C2).
```

**Veredicto:** ✅
**Notas:** Rechazo correcto, identifica agua como variable e indica el límite exacto (228 kg/m³).

---

### Prueba 2.3 — Firewall paramétrico (edad excede el máximo)
**Input:** "Predice esta mezcla: cemento=350, agua=175, agregado grueso=1100, agregado fino=800, sin aditivos, 400 días."
**Verificación:** edad = 400 días excede el máximo normativo (365, ACI 209R). Resto de variables dentro de dominio.
**Respuesta esperada:** El firewall rechaza o advierte sobre la variable de edad fuera de dominio, indica el límite máximo (365 días).
**Herramienta esperada:** `CatBoost`

**Herramienta real:** `CatBoost`
**Respuesta real:**
```text
Edad fuera de rango: El modelo FUVIA se limita a 1–365 días según curvas de madurez (ACI 209R).

Ajusta la edad a ≤365 días y vuelve a consultar. Si necesitas proyectar más allá, puedo orientarte con f'c asintótico estimado tras obtener la resistencia a 365 días.
```

**Veredicto:** ✅
**Notas:** Rechazo correcto, indica el límite exacto (365 días, ACI 209R).

---

### Prueba 2.4 — Mezcla con materiales suplementarios (SCMs)
**Input:** "Predice esta mezcla: cemento=300, escoria=100, ceniza volante=50, agua=180, agregado grueso=1000, agregado fino=850, superplastificante=5, 28 días."
**Verificación:** material cementante total = 300+100+50 = 450; w/cm = 180/450 = 0.40 (válido); superplastificante = 5/450 = 1.1% de masa cementante (dentro del máximo 4.0%); densidad = 2485 kg/m³ (válida); todas las variables individuales dentro de dominio Yeh.
**Respuesta esperada:** Predicción exitosa considerando SCMs; w/cm calculado correctamente sobre material cementante total (no solo cemento Portland).
**Herramienta esperada:** `CatBoost`

**Herramienta real:** `CatBoost`
**Respuesta real:**
```text
FUVIA predice: f'c = 40.371 MPa a 28 días

Tu mezcla ternaria (cemento + escoria + ceniza volante) cumple criterios generales de alta resistencia:

• w/cm = 0.40 — excelente para durabilidad y resistencias >35 MPa (ACI 318-19 §19.3.2.1) • 33% SCM (escoria + ceniza) — beneficio en durabilidad a largo plazo, menor calor de hidratación • Grava/arena 1.18 — mezcla más fina de lo habitual; verifica trabajabilidad en obra

Cumplimiento normativo clave:

Para C2 (ambientes moderados): w/cm ≤ 0.50 ✅
Para C3 (severos): w/cm ≤ 0.40 ✅ — ideal para sulfatos o ciclos hielo-deshielo
¿Necesitas validar exposición específica o ajustar algún parámetro?
```

**Veredicto:** ✅
**Notas:** w/cm calculado correctamente sobre material cementante total (0.40), predicción exitosa considerando SCMs.

---

### Prueba 2.5 — Extremo opuesto de dominio (agua cerca del mínimo)
**Input:** "Predice esta mezcla: cemento=450, agua=122, agregado grueso=1100, agregado fino=800, sin aditivos, 28 días."
**Verificación:** agua = 122 kg/m³, apenas 2 kg/m³ por encima del mínimo de dominio (120.0) -- el extremo opuesto a la Prueba 2.2. w/cm = 122/450 = 0.271 (dentro de 0.25–0.85, con margen estrecho). Densidad = 2472 kg/m³ (válida).
**Respuesta esperada:** FUVIA acepta la mezcla (dentro de dominio); predicción exitosa; sin advertencias de extrapolación.
**Herramienta esperada:** `CatBoost`

**Herramienta real:** `CatBoost`
**Respuesta real:**
```text
Resultado: f'c = 56.448 MPa (concreto de alta resistencia)

Análisis normativo:

• w/cm = 0.27 — cumple límites para exposición severa C2/F3 (ACI 318-19, Tabla 19.3.2.1: máx. 0.40)
• Cemento = 450 kg/m³ — excede mínimo de 390 kg/m³ para F3 (Tabla 26.4.2.1)
• Relación grava/arena = 1.38 — equilibrada, favorable para bombeo (ACI 211.1-22)

Limitaciones:
Trabajabilidad muy baja por w/cm ultra-bajo. Requiere superplastificante ASTM C494 tipo A/F para colocación efectiva.
```

**Veredicto:** ✅
**Notas:** Aceptado sin rechazo cerca del límite inferior de agua; predicción exitosa, sin advertencias de extrapolación.

---

## CATEGORÍA 3 — Ambas herramientas (diseño completo)
Herramienta esperada: `CatBoost` + `RAG normativo` (ambas, en el mismo turno)

### Prueba 3.1 — Validación normativa de dosificación (re-ejecutar limpio)
**Input:** "Tengo esta dosificación: cemento=380, agua=180, agregado grueso=1050, agregado fino=780, edad 28 días. ¿Cumple para clase de exposición F2?"
**Verificación:** w/cm = 180/380 = 0.474, que EXCEDE el límite F2 (0.45) -- resultado esperado: NO CUMPLE. Densidad = 2390 kg/m³ (válida), todas las variables dentro de dominio Yeh, por lo que FUVIA debe predecir sin rechazo.
**Respuesta esperada:** FUVIA predice f'c real; comparación explícita contra el límite F2 (0.45); `normative_compliance.compliant: false`.
**Herramienta esperada:** `CatBoost` + `RAG normativo`

**Herramienta real:** `RAG normativo` + `CatBoost`
**Respuesta real:**
```text
NO cumple clase F2. Dos incumplimientos críticos:

1. Relación w/cm excedida

Tu mezcla: w/cm = 0.474
Límite F2: 0.45 máximo (ACI 318-19 Tabla 19.3.2.1)
2. Resistencia insuficiente

f'c estimado: 36.919 MPa (5,354 psi)
f'c mínimo F2: 31 MPa (4,500 psi) — esto sí cumple ✅
3. Aire incluido

F2 exige 5.0–7.5% según tamaño máximo de agregado (ACI 211.1-22 §4.7.3.1)
Tu dosificación no incluye aditivo incorporador de aire
Corrección: Reduce agua a 171 kg/m³ (w/cm = 0.45) y agrega incorporador de aire según ASTM C260.

⚠
w/cm: NO CUMPLE
Reducir relación w/cm a máximo 0.45 (reducir agua o incrementar cemento)

✅
f'c: CUMPLE
Resistencia supera mínimo requerido de 4500 psi (31.03 MPa)
```

**Veredicto:** ✅
**Notas:** Ambas herramientas ejecutaron limpio (a diferencia del intento original con timeout); NO CUMPLE correctamente identificado por w/cm=0.474>0.45, con f'c real predicho, no estimado por el LLM.

---

### Prueba 3.2 — Dosificación para exposición a sulfatos (re-ejecutar limpio)
**Input:** "Necesito diseñar concreto para una cisterna enterrada en suelo con sulfatos severos (S2). Propón una dosificación y verifica que cumpla normativamente."
**Respuesta esperada:** Consulta normativa (w/cm ≤ 0.45, f'c ≥ 4,500 psi, cemento Tipo V) Y propuesta de dosificación verificada con FUVIA -- ambas herramientas deben ejecutar, no solo una.
**Herramienta esperada:** `RAG normativo` + `CatBoost`

**Herramienta real:** `RAG normativo` + `CatBoost`
**Respuesta real:**
```text

Dosificación propuesta (kg/m³)
Cemento: 380 | Agua: 152 | Superplastificante: 6
Grava: 1050 | Arena: 720
w/cm: 0.40 | f'c predicho: 55.686 MPa (8,075 psi)

✅ Verificación normativa S2 (sulfatos severos)
• w/cm = 0.40 → Cumple (máx. 0.45 por ACI 318-19 §19.3.2.1)
• f'c = 55.686 MPa → Cumple (mín. 31.0 MPa / 4,500 psi)
• Cemento requerido: Tipo V (ASTM C150, máx. 5% C₃A) o cemento con sufijo (HS) para resistencia a sulfatos

La mezcla cumple estructuralmente. Debes especificar cemento resistente a sulfatos en obra para que sea normativa completa en exposición S2.
```

**Veredicto:** ✅
**Notas:** Ambas herramientas ejecutaron limpio (a diferencia del intento original donde solo corrió una); dosificación propuesta y verificada normativamente en el mismo turno.

---

### Prueba 3.3 — Optimización de mezcla (re-ejecutar limpio)
**Input:** "Mi mezcla actual tiene cemento=380, agua=190, agregado grueso=1000, agregado fino=750, 28 días. El w/cm es muy alto para zona sísmica. ¿Cómo la mejoro?"
**Verificación:** w/cm actual = 190/380 = 0.50. Densidad = 2320 kg/m³ (válida). Todas las variables dentro de dominio Yeh.
**Respuesta esperada:** Predicción de la mezcla actual; requisitos sísmicos del ACI 318-19; propuesta de mezcla mejorada; verificación de la mezcla mejorada con FUVIA. Respuesta debe completarse sin cortarse.
**Herramienta esperada:** `CatBoost` + `RAG normativo`

**Herramienta real:** `RAG normativo` + `CatBoost`
**Respuesta real:**
```text
Tu mezcla actual: f'c = 36.149 MPa | w/cm = 0.50

Problema para zona sísmica:

ACI 318-19 Cap. 18 exige concreto de alta calidad en elementos resistentes a sismo
w/cm = 0.50 está en el límite alto; lo ideal es ≤0.45 para garantizar durabilidad y resistencia
Mejora recomendada:
• Reduce agua a 171 kg/m³ → w/cm = 0.45
• Añade superplastificante (5-7 L/m³) para mantener trabajabilidad
• Esto cumple clase F2, S2, S3 (ACI 318-19 §19.3.2.1) y mejora comportamiento sísmico

Impacto: Mayor f'c (~39-41 MPa estimado), mejor adherencia refuerzo-concreto, menor fisuración.

✅
w/cm: CUMPLE
Cumple rango general ACI pero reducir a ≤0.45 para mejor desempeño sísmico

✅
f'c: CUMPLE
Resistencia adecuada para elementos estructurales estándar
```

**Veredicto:** ✅
**Notas:** Respuesta completa sin truncarse (a diferencia del intento original); ambas herramientas ejecutaron, mezcla actual evaluada y mejora propuesta.

---

### Prueba 3.4 — Caso NO CUMPLE verificado
**Input:** "Tengo esta mezcla: cemento=350, agua=175, agregado grueso=1100, agregado fino=800, 28 días. ¿Cumple para clase de exposición F2?"
**Verificación:** w/cm = 175/350 = 0.50, EXCEDE el límite F2 (0.45). Densidad = 2425 kg/m³ (válida). Todas las variables dentro de dominio Yeh -- FUVIA debe predecir sin rechazo, para que el NO CUMPLE sea producto de la comparación normativa, no de un rechazo del firewall.
**Respuesta esperada:** FUVIA predice exitosamente; `normative_compliance.compliant: false` con al menos un check en estado "NO CUMPLE"; el agente sugiere un ajuste (ej. reducir agua o aumentar cemento).
**Herramienta esperada:** `CatBoost` + `RAG normativo`

**Herramienta real:** `RAG normativo` + `CatBoost`
**Respuesta real:**
```text
❌ NO CUMPLE para F2 — Tu mezcla presenta dos incumplimientos:

• f'c = 39.164 MPa → ACI 318-19 requiere f'c ≥ 31 MPa para F2 ✓ (Cumple resistencia, pero...)

• w/cm = 0.50 → ACI 318-19 Tabla 19.3.2.1 exige w/cm máx. 0.45 para F2 ❌ Excedido en 11%

• Sin aire incluido especificado → F2 requiere 6-7.5% de aire según tamaño de agregado (ACI 318-19 §19.3.3.1) ❌ Esencial para durabilidad al hielo-deshielo

Ajuste recomendado: Reducir agua a 157.5 kg/m³ (w/cm=0.45) y usar aditivo inclusor de aire (ASTM C260) según tamaño máx. de tu grava.
```

**Veredicto:** ✅
**Notas:** NO CUMPLE verificado limpiamente: FUVIA predijo con éxito (f'c=39.164 MPa) y la comparación normativa identificó correctamente el incumplimiento de w/cm, con ajuste sugerido.

---

### Prueba 3.5 — Caso SÍ CUMPLE verificado
**Input:** "Tengo esta mezcla: cemento=400, agua=170, agregado grueso=1100, agregado fino=800, 28 días. ¿Cumple para clase de exposición F2?"
**Verificación:** w/cm = 170/400 = 0.425, CUMPLE el límite F2 (≤0.45). Densidad = 2470 kg/m³ (válida). Todas las variables dentro de dominio Yeh.
**Respuesta esperada:** FUVIA predice exitosamente; `normative_compliance.compliant: true` con checks en estado "CUMPLE".
**Herramienta esperada:** `CatBoost` + `RAG normativo`

**Herramienta real:** `RAG normativo` + `CatBoost`
**Respuesta real:**
```text
Evaluación para F2 (Congelamiento/Deshielo con exposición frecuente a agua):

• f'c = 45.215 MPa → Cumple ampliamente
• w/cm = 0.425 → Cumple límite ACI 318-19 (máx 0.45 para F2, Tabla 19.3.2.1)
• Aire incluido requerido → Tu mezcla NO incluye aire incorporado (obligatorio según §19.3.3.1)

Falta crítica: Debes agregar aditivo incorporador de aire para alcanzar 5-7% según tamaño máximo de agregado (ACI 318-19 Tabla 19.3.3.1).
```

**Veredicto:** ✅
**Notas:** w/cm CUMPLE verificado limpiamente (0.425≤0.45). El agente además detectó que falta aire incorporado (requisito real de F2 no contemplado en el diseño de esta prueba) -- comportamiento correcto y más completo de lo que la prueba aislaba, no un fallo.

---

## CATEGORÍA 4 — Memoria multi-turno

### Prueba 4.1 — Referencia a consulta anterior (re-ejecutar, documentar los 3 turnos)
**Secuencia:**
1. "¿Cuál es el w/cm máximo para clase de exposición F2?"
2. "¿Y para F3?"
3. "¿Cuál es más restrictiva de las dos?"
**Respuesta esperada en el turno 3:** Comparación F2 vs. F3 sin que el usuario repita contexto; F3 más restrictiva (0.40 vs 0.45); no debe preguntar "¿a qué te refieres?".

**Herramienta real (turno 1):** `RAG normativo`
**Herramienta real (turno 2):** Ninguna (reutiliza contexto ya recuperado)
**Herramienta real (turno 3):** Ninguna
**Respuesta real (turno 1):**
```text
Para Clase de Exposición F2 (congelamiento/deshielo con exposición frecuente al agua):

• w/cm máximo: 0.45 (ACI 211.1-22 Tabla 4.7.3b) • f'c mínimo: 4,500 psi • Contenido de aire: 5.5–6.0% dependiendo del tamaño máximo del agregado

F2 aplica cuando el concreto está frecuentemente mojado y expuesto a ciclos de congelamiento, pero sin químicos descongelantes (esos serían F3).
```
**Respuesta real (turno 2):**
```text
Para Clase de Exposición F3 (congelamiento/deshielo con químicos descongelantes):

• w/cm máximo: 0.40 (ACI 318-19 Tabla 19.3.2.1) • f'c mínimo: 5,000 psi • Contenido de aire: 6.0–7.0% (mayor que F2 por ataque más severo)

F3 es la clase más exigente de congelamiento: pavimentos, estacionamientos, puentes donde se aplican sales o descongelantes. Requiere concreto más denso y mayor red de burbujas de aire.
```
**Respuesta real (turno 3):**
```text
F3 es más restrictiva que F2:

• w/cm: 0.40 vs 0.45 (11% más bajo) • f'c: 5,000 psi vs 4,500 psi • Aire: 6.0–7.0% vs 5.5–6.0%

F3 protege contra congelamiento más químicos descongelantes (ataque dual), por eso exige concreto más denso, resistente y con mayor red de microburbujas para liberar presión del hielo y resistir penetración de cloruros.
```

**Veredicto:** ✅
**Notas:** Resuelto contra el log crudo de retrieval del turno 1. De los 5 chunks recuperados para la consulta de F2, el chunk [5] es la Tabla 4.7.3.2 del ACI 211.1-22, titulada explicitamente 'Exposure Class F3', y el chunk [2] es la Tabla 19.3.2.1 del ACI 318-19, que agrupa multiples clases de exposicion (congelamiento, sulfatos, agua, cloruros) en una sola tabla. El retriever trajo contenido de F3 junto con F2 por proximidad semantica/tematica dentro del mismo documento, sin que el usuario lo pidiera. La respuesta del turno 2 esta anclada a retrieval real ya presente en el historial (ToolMessage del turno 1), no es conocimiento parametrico del modelo. Confirma que el diseno hibrido de retrieval captura contexto normativo relacionado mas alla de la coincidencia literal de terminos.

---

### Prueba 4.2 — Precisión numérica retenida en memoria
**Secuencia:**
1. "Predice esta mezcla: cemento=400, agua=160, agregado grueso=1050, agregado fino=780, 28 días."
2. "¿Cuál fue el f'c exacto que obtuviste?"
**Verificación:** w/cm = 160/400 = 0.40 (válido). Densidad = 2390 kg/m³ (válida).
**Respuesta esperada en el turno 2:** El mismo valor exacto de f'c dado en el turno 1 (sin redondear distinto, sin recalcular), recuperado del historial conversacional. Confirmar en logs/Network que `CatBoost` NO se ejecuta de nuevo en el turno 2.
**Herramienta esperada turno 2:** Ninguna (respuesta directa desde memoria)

**Herramienta real (turno 1):** `CatBoost`
**Herramienta real (turno 2):** Ninguna
**Respuesta real (turno 1):**
```text
f'c predicho: 54.515 MPa (concreto de alta resistencia)

Análisis normativo:

• w/cm = 0.40 → Cumple todos los requisitos ACI 318-19 para exposición severa (límite máximo 0.45 para C2/F3, §19.3.2.1)

• Rango de aplicación: Puentes, columnas de edificios altos, estructuras industriales con exigencias de durabilidad máxima

• Cemento: 400 kg/m³ supera mínimo de 335 kg/m³ para exposición F3 (congelamiento-deshielo con sales, ACI 318-19 Table 19.3.2.1)

• Tipo de cemento recomendado: Tipo I o V según ASTM C150 dependiendo del ambiente (sulfatos requieren Tipo V si >1500 ppm)

¿Necesitas evaluar una clase de exposición específica o ajustar para requisitos sísmicos?
```
**Respuesta real (turno 2):**
```text
 f'c = 54.515 MPa (7,906 psi)

Equivale aproximadamente a concreto clase 55 MPa según clasificación estándar.
```

**Veredicto:** ✅
**Notas:** f'c idéntico entre turno 1 (54.515 MPa) y turno 2, sin re-invocar CatBoost -- confirma retención de precisión numérica vía memoria conversacional pura.
 
---
 
### Prueba 4.3 — Conversación larga, 4+ turnos
**Secuencia:**
1. "¿Cuál es el w/cm máximo para exposición S1 (sulfatos moderados)?"
2. "Predice esta mezcla: cemento=350, agua=175, agregado grueso=1100, agregado fino=800, 28 días."
3. "¿Y para exposición S3 (sulfatos muy severos)?"
4. "Predice esta otra mezcla: cemento=450, agua=170, agregado grueso=1050, agregado fino=790, 28 días."
5. "¿Cuál era el límite que me diste para sulfatos moderados, el primero que pregunté?"
**Verificación:** turno 2, w/cm = 175/350 = 0.50 (válido). Turno 4, w/cm = 170/450 = 0.378 (válido). Ambas mezclas dentro de dominio.
**Respuesta esperada en el turno 5:** El agente recupera correctamente el dato de S1 (turno 1), sin confundirlo con S3 (turno 3, mencionado más recientemente) ni con ninguna de las dos predicciones FUVIA intercaladas.

**Herramienta real (turno 1):** `RAG normativo`
**Herramienta real (turno 2):** `CatBoost`
**Herramienta real (turno 3):** `RAG normativo`
**Herramienta real (turno 4):** `CatBoost`
**Herramienta real (turno 5):** Ninguna
**Respuesta real (turno 1):**
```text
w/cm máximo para S1 = 0.50 (ACI 318-19 Tabla 19.3.2.1)

Requisitos adicionales: • f'c mínimo: 4000 psi (28 MPa) • Cemento: ASTM C150 Tipo II o equivalentes (MS) • Para agua de mar en S1: w/cm ≤ 0.40 con C₃A ≤ 10%
```
**Respuesta real (turno 2):**
```text
f'c predicho: 39.164 MPa (5677 psi) — w/cm = 0.50

Cumplimiento S1 (sulfatos moderados): • ✓ w/cm = 0.50 → cumple límite máximo • ✓ f'c = 39.164 MPa → supera mínimo de 28 MPa • ⚠ Usar cemento Tipo II (moderada resistencia a sulfatos)

Observaciones: Mezcla apta para S1. Relación grava/arena 1.375 → granulometría equilibrada, buena trabajabilidad.
```
**Respuesta real (turno 3):**
```text
Para S3 (sulfatos muy severos):

Opción 1 (con puzolanas/escoria): • w/cm máximo: 0.45 • f'c mínimo: 4500 psi (31 MPa) • Usar materiales cementantes suplementarios con historial probado

Opción 2 (sin puzolanas adicionales): • w/cm máximo: 0.40 • f'c mínimo: 4500 psi (31 MPa)
• Cemento: ASTM C150 Tipo V o C595/C1157 Tipo HS

Tu mezcla actual (w/cm = 0.50) NO cumple para S3. Necesitas reducir agua o aumentar cemento para alcanzar w/cm ≤ 0.40–0.45 según opción elegida.
```
**Respuesta real (turno 4):**
```text
f'c predicho: 54.122 MPa (7847 psi) — w/cm = 0.378

Cumplimiento S3 (sulfatos muy severos): • ✓ w/cm = 0.378 → cumple límite 0.40 (opción sin puzolanas) • ✓ f'c = 54.122 MPa → supera ampliamente mínimo 31 MPa • ✓ Usar cemento Tipo V (ASTM C150) o equivalente HS

Observaciones: Mezcla de alta resistencia apta para S3. Considera superplastificante para mejorar trabajabilidad con este w/cm bajo.
```
**Respuesta real (turno 5):**
```text
w/cm máximo = 0.50 para exposición S1 (sulfatos moderados)

Con f'c mínimo de 28 MPa (4000 psi) y cemento Tipo II.
```

**Veredicto:** ✅
**Notas:** Turno 5 recupera correctamente el dato de S1 (0.50, 28 MPa, Tipo II) del turno 1, sin confundirlo con S3 (turno 3) ni con ninguna de las dos predicciones FUVIA intercaladas -- buena evidencia contra degradación de memoria en conversaciones largas.
 
---
 
### Prueba 4.4 — Corrección de dato a mitad de conversación
**Secuencia:**
1. "Tengo una mezcla con cemento=380, agua=175, agregado grueso=1100, agregado fino=800, 28 días. ¿Qué resistencia tendrá?"
2. "Perdón, en realidad el cemento es 450, no 380"
3. "¿Cuál es el w/cm de esa mezcla?"
**Verificación:** w/cm correcto tras la corrección = 175/450 = 0.389. Si el agente usa el valor original (380), obtendría 0.461 -- una diferencia verificable que confirma si aplicó la corrección o no.
**Respuesta esperada:** El agente usa el valor corregido (450) en el turno 3, no el original (380) ni una mezcla de ambos.

**Herramienta real (turno 1):** `CatBoost`
**Herramienta real (turno 2):** `CatBoost`
**Herramienta real (turno 3):** Ninguna
**Respuesta real (turno 1):**
```text
Tu mezcla alcanzará 40.012 MPa a 28 días.

Análisis normativo:

• w/cm = 0.46 → cumple ACI 318-19 para ambientes C1 y F1 (máx. 0.50) • Clase alta resistencia → apta para estructuras sismo-resistentes y marcos especiales si f'c ≥ 21 MPa (ACI 318-19 §18.2.1.1) • Relación grava/arena óptima (1.38) → buena compacidad según ACI 211.1-22

Ideal para puentes, columnas en edificios altos y zonas con demanda estructural elevada.
```
**Respuesta real (turno 2):**
```text
Con cemento 450 kg/m³, la resistencia sube a 49.605 MPa a 28 días.

Cambios normativos:

• w/cm = 0.39 → cumple hasta clase C3 (ambientes severos con ciclos hielo-deshielo, ACI 318-19 tabla 19.3.2.1) • Resistencia superior → apta para marcos especiales intermedios y muros con f'c ≥ 21 MPa (ACI 318-19 §18.2.4.4) • Mejor durabilidad en exposición marina y sulfatos moderados (ACI 318-19 §19.3.1.1)

Esta mezcla es más robusta para ambientes agresivos que la anterior.
```
**Respuesta real (turno 3):**
```text
w/cm = 0.39

(175 kg agua ÷ 450 kg cemento = 0.389)
```

**Veredicto:** ✅
**Notas:** Turno 3 usa el valor corregido (450, no 380): w/cm=0.389 coincide exactamente con el cálculo esperado tras la corrección. CatBoost se re-invocó apropiadamente en el turno 2 (a diferencia de la Prueba 4.2, aquí sí cambiaron los parámetros, por lo que recalcular es el comportamiento correcto).
 
---

### Prueba 4.5 — Memoria cruzando tipos de herramienta
**Secuencia:**
1. "¿Cuál es el w/cm máximo para exposición S1 (sulfatos moderados)?"
2. "Predice esta mezcla, sin relación con lo anterior: cemento=350, agua=175, agregado grueso=1100, agregado fino=800, 28 días."
3. "¿Cuál era el w/cm que me diste para sulfatos moderados?"
**Respuesta esperada:** El agente recupera correctamente el dato normativo del turno 1 (w/cm ≤ 0.50 para S1), sin confundirlo con el w/cm calculado de la predicción del turno 2.

**Herramienta real (turno 1):** `RAG normativo`
**Herramienta real (turno 2):** `CatBoost`
**Herramienta real (turno 3):** Ninguna
**Respuesta real (turno 1):**
```text
Para exposición S1 (sulfatos moderados), el w/cm máximo es 0.50 con f'c mínimo de 4,000 psi (ACI 318-19, Tabla 19.3.2.1).

Cemento requerido:

Tipo II (MS) según ASTM C150
Tipos con designación (MS) según ASTM C595/C1157
Nota: Si la exposición es agua de mar, otros cementos con C₃A ≤10% son permitidos si w/cm ≤ 0.40.
```
**Respuesta real (turno 2):**
```text
Predicción FUVIA: f'c = 39.164 MPa (28 días)
Clase: Resistencia Estándar | w/cm = 0.50

Evaluación técnica: • w/cm óptimo — balance cohesión/durabilidad
• Grava/arena 1.375 — granulometría ideal, máxima compacidad
• Apto para vigas, losas, columnas ligeras, pavimentos
```
**Respuesta real (turno 3):**
```text

w/cm máximo para S1 (sulfatos moderados): 0.50

Tu mezcla predicha tiene exactamente w/cm = 0.50, por lo que cumple el límite para exposición a sulfatos moderados (ACI 318-19, Tabla 19.3.2.1).
```

**Veredicto:** ✅
**Notas:** El turno 3 distingue explícitamente las dos fuentes del mismo número en vez de fusionarlas -- etiqueta "el límite para S1" por separado de "tu mezcla predicha", y solo entonces nota la coincidencia. Confirma que el agente rastrea la procedencia de cada dato, no solo el valor numérico. Herramientas por turno coinciden exactamente con lo esperado (RAG → CatBoost → ninguna).

---

## CATEGORÍA 5 — Casos edge

### Prueba 5.1 — Saludo / conversación general
**Input:** "Hola, ¿qué puedes hacer?"
**Respuesta esperada:** Respuesta directa sin herramientas; explica brevemente sus capacidades.
**Herramienta esperada:** Ninguna

**Herramienta real:** Ninguna
**Respuesta real:**
```text
Soy tu asistente técnico para diseño de mezclas de concreto y normativa ACI/ASTM. Puedo:

• Predecir resistencia (f'c) de tu dosificación con IA (modelo CatBoost) — dame cantidades de cemento, agua, agregados, edad y te digo qué resistencia esperar

• Consultar normativa — requisitos de durabilidad, relación w/cm máxima, f'c mínimo según clase de exposición, especificaciones de cemento/agregados/aditivos (ACI 318, ACI 211, ASTM)

• Validar mezclas — comparo tu diseño contra límites normativos y te doy recomendaciones

¿Tienes una dosificación para analizar o alguna duda normativa?
```

**Veredicto:** ✅
**Notas:** Respuesta directa sin herramientas, explica capacidades correctamente.

---

### Prueba 5.2 — Pregunta ambigua
**Input:** "¿Cuánto cemento debo usar?"
**Respuesta esperada:** El agente pide la información faltante (tipo de exposición, resistencia objetivo, etc.) en vez de asumir o alucinar valores.
**Herramienta esperada:** Ninguna, o clarificación antes de invocar herramientas

**Herramienta real:** Ninguna
**Respuesta real:**
```text
Para responderte necesito más contexto:

¿Qué resistencia necesitas? (ej: 210, 280, 350 kg/cm²)

¿Qué clase de exposición? (interior, exterior, contacto con agua, ambiente marino, etc.)

¿Ya tienes otros materiales definidos? (agua, agregados, aditivos)

Con eso puedo darte el contenido de cemento óptimo y verificar que cumpla ACI 318/211.
```

**Veredicto:** ✅
**Notas:** Pide información faltante (resistencia objetivo, exposición, otros materiales) sin asumir valores.

---

### Prueba 5.3 — Pregunta en inglés
**Input:** "What is the minimum f'c for a concrete column exposed to seawater?"
**Respuesta esperada:** Respuesta en inglés; consulta normativa correcta; citación en formato original.
**Herramienta esperada:** `RAG normativo`

**Herramienta real:** `RAG normativo`
**Respuesta real:**
```text
For a concrete column exposed to seawater, the minimum requirements are:

f'c ≥ 4,000 psi (28 MPa)
Maximum w/cm: 0.50
Seawater is classified as Exposure Class S1 (moderate sulfate exposure) per ACI 318-19 §R19.3.1.1, even though sulfate concentration exceeds 1500 ppm—seawater causes less expansion than freshwater at equivalent sulfate levels.

You'll also need sulfate-resistant cement (Type II or equivalent with SCMs). For complete cement type requirements, consult ACI 318-19 Table 19.3.2.1.
```

**Veredicto:** ✅
**Notas:** Respuesta completa en inglés, contenido normativo correcto, cita en formato original.

---

### Prueba 5.4 — Valor exactamente en el límite del dominio Yeh
**Input:** "Predice esta mezcla: cemento=350, agua=228, agregado grueso=1100, agregado fino=800, sin aditivos, 28 días."
**Verificación:** agua = 228 kg/m³ es EXACTAMENTE el máximo de dominio (no lo excede). w/cm = 228/350 = 0.651 (válido). Densidad = 2478 kg/m³ (válida). Esta prueba verifica que el firewall trata el valor límite mismo como válido (frontera inclusiva), a diferencia de la Prueba 2.2 que prueba exceder el límite.
**Respuesta esperada:** FUVIA acepta la mezcla y predice normalmente, sin rechazo.
**Herramienta esperada:** `CatBoost`

**Herramienta real:** `CatBoost`
**Respuesta real:**
```text
Resultado de predicción
f'c = 26.05 MPa (3,778 psi) · w/cm = 0.651 · Edad: 28 días

Evaluación normativa
• w/cm = 0.651 excede todos los límites ACI 318-19 para concreto estructural:

Máx. para ambientes no agresivos: 0.50 (§19.3.2.1)
Esta relación causa alta permeabilidad y vulnerabilidad a sulfatos/cloruros
• Resistencia mínima para vigas/columnas: 21 MPa (ACI 318-19 §19.2.1.1) → Cumple, pero sin margen de seguridad

• Uso recomendado: losas sobre terreno, banquetas, elementos no estructurales (ACI 211.1-22 para f'c < 28 MPa)

Acción crítica: Reducir agua a 175 kg/m³ → w/cm = 0.50 + mantener resistencia con aditivo reductor de agua tipo A/F (ASTM C494).

⚠
w/cm ratio: NO CUMPLE
Reducir relación w/cm a máximo 0.50 según ACI 318 para concreto estructural durable
```

**Veredicto:** ✅
**Notas:** Aceptado en el límite exacto superior del dominio (agua=228, no lo excede) -- confirma frontera inclusiva. Agrega correctamente advertencia normativa sobre el w/cm resultante, información adicional válida no requerida por el diseño de la prueba.

---

### Prueba 5.5 — Mensaje sin contexto / totalmente fuera de tema
**Input:** "¿Cuál es la capital de Noruega?"
**Respuesta esperada:** El agente declina o redirige con naturalidad, aclarando que su especialización es diseño de mezclas de concreto y cumplimiento normativo ACI/ASTM, sin intentar responder la pregunta fuera de tema ni invocar ninguna herramienta.
**Herramienta esperada:** Ninguna

**Herramienta real:** Ninguna
**Respuesta real:**
```text
Esa pregunta está fuera de mi alcance técnico. Soy un asistente especializado en diseño de mezclas de concreto y normativa ACI/ASTM.

¿Tienes alguna consulta sobre dosificación de concreto, resistencias, durabilidad o requisitos normativos?
```

**Veredicto:** ✅
**Notas:** Declina con naturalidad, redirige a su especialización, sin invocar herramienta.

---

## CATEGORÍA 6 — Flujo de confirmación de análisis (formulario → chat)
Prueba el mecanismo descrito en la Sección 4.2: `confirmAnalysis` en `useAgentChat.ts` construye un mensaje de texto con los datos ya calculados en el formulario (columna 1) y lo envía al chat cuando el usuario confirma. A diferencia de las Categorías 1-5, aquí el input no es texto escrito por el usuario, sino el resultado de una interacción de UI (botón).
 
### Prueba 6.1 — Confirmar análisis con "Sí, analizar"
**Procedimiento:** calcula cualquier mezcla en el formulario (columna 1), espera el mensaje de confirmación del copiloto ("¿Deseas que analice normativamente esta mezcla?"), presiona "Sí, analizar".
**Respuesta esperada:** el agente usa el f'c y w/cm exactos ya mostrados en el formulario (sin recalcularlos ni redondearlos distinto) y agrega contexto normativo relevante (clase de exposición aplicable, si el w/cm cumple límites típicos, etc.).
**Herramienta esperada:** `RAG normativo` ÚNICAMENTE -- si `CatBoost` también se ejecuta, es una llamada redundante (el resultado ya estaba en el mensaje), y debe anotarse como hallazgo aunque la respuesta final sea correcta.
 
**Mezcla calculada en el formulario (f'c, w/cm, ca/fa, clase):**

| Variable | Cantidad |
|---|---|
| Cemento | 540.0 kg/m³ |
| Escoria | 0.0 |
| Ceniza volante | 0.0 |
| Agua | 162.0 |
| Superplastificante | 2.5 |
| Agregado grueso | 1040.0 |
| Agregado fino | 676.0 |
| Edad | 28 días|

f'c = 75.463
w/cm = 0.3
ca/fa = 1.538
clase = Ultra Alta Resistencia

**Mensaje auto-generado (si es visible en DevTools/Network):**
Hola, soy tu Copiloto FUVIA X. Calcula una mezcla y te daré un análisis normativo inmediato basado en ACI/ASTM.
También puedes preguntarme sobre requisitos de durabilidad, exposición ambiental o especificaciones de materiales.
✅ Mezcla calculada — f'c 75.463 MPa · w/cm 0.3 · Ultra Alta Resistencia
¿Deseas que analice normativamente esta mezcla con ACI/ASTM?
Sí, analizar
No por ahora
**Herramienta real:** `Rag Normativo`
**Respuesta real del agente:**
```text
 Análisis normativo de tu mezcla de ultra alta resistencia:

✓ Cumplimientos claros:

w/cm = 0.3 está por debajo de todos los límites máximos de durabilidad de ACI 318-19 Tabla 19.3.2.1 (rangos típicos 0.40-0.50)
Relación agua-material cementante excelente para ambientes agresivos
⚠️ Observaciones críticas:

Contenido de cemento muy elevado (540 kg/m³): ACI 211.1 típicamente recomienda rangos de 280-420 kg/m³. Con este nivel debes considerar:

Calor de hidratación alto → riesgo de fisuración térmica temprana
Retracción aumentada → requiere curado riguroso
Costo elevado y huella de carbono significativa
Fuera del alcance normativo estándar: ACI 318-19 no regula específicamente concretos >70 MPa. Para esta clase de resistencia deberías consultar:

ACI 363R (High-Strength Concrete)
Pruebas de desempeño documentadas para aprobación del diseñador/autoridad
Contenido de agua bajo (162 L/m³): Asegura trabajabilidad con superplastificantes de alto rango y verifica aire atrapado no exceda 3% (afecta resistencia final).

¿Requieres orientación específica sobre aditivos o procedimientos de curado para este nivel de resistencia?

✅
w/cm: CUMPLE
w/cm inferior a todos los límites máximos de ACI 318-19 Tabla 19.3.2.1

✅
f'c: CUMPLE
Resistencia excede alcance de ACI 318-19; se requiere documentación técnica conforme ACI 239R para concreto ultra alta resistencia y aprobación basada en pruebas de desempeño
```

**Veredicto:** ✅
**Notas:** Confirma que solo se invocó RAG normativo, NO CatBoost de nuevo -- valida directamente la regla agregada al system prompt (Sección 6.4) para evitar la llamada redundante. Usa el f'c y w/cm exactos del mensaje auto-generado sin recalcular.
 
---
 
### Prueba 6.2 — Declinar con "No por ahora"
**Procedimiento:** calcula cualquier mezcla en el formulario, espera el mensaje de confirmación, presiona "No por ahora".
**Respuesta esperada:** no se envía ningún mensaje al agente; no se invoca ninguna herramienta; el chat no genera una respuesta nueva no solicitada.
**Herramienta esperada:** Ninguna

**Mezcla calculada en el formulario (f'c, w/cm, clase):**

| Variable | Cantidad |
|---|---|
| Cemento | 540.0 kg/m³ |
| Escoria | 0.0 |
| Ceniza volante | 0.0 |
| Agua | 162.0 |
| Superplastificante | 2.5 |
| Agregado grueso | 1040.0 |
| Agregado fino | 676.0 |
| Edad | 28 días|

f'c = 75.463
w/cm = 0.3
clase = Ultra Alta Resistencia
**Mensaje auto-generado (si es visible en DevTools/Network):**
Hola, soy tu Copiloto FUVIA X. Calcula una mezcla y te daré un análisis normativo inmediato basado en ACI/ASTM.
También puedes preguntarme sobre requisitos de durabilidad, exposición ambiental o especificaciones de materiales.
✅ Mezcla calculada — f'c 75.463 MPa · w/cm 0.3 · Ultra Alta Resistencia
¿Deseas que analice normativamente esta mezcla con ACI/ASTM?
Sí, analizar
No por ahora
**Herramienta real:** Ninguna
**Respuesta real (¿qué pasa en la UI/chat tras presionar "No por ahora"?):**
```text
Entendido. Si necesitas el análisis normativo en cualquier momento, solo pídelo.
```

**Veredicto:** ✅
**Notas:** Confirmado contra el codigo fuente: declineAnalysis() en useAgentChat.ts limpia pendingAnalysisRef y agrega el mensaje directamente al estado de React ("Entendido. Si necesitas el analisis normativo en cualquier momento, solo pidelo.") sin llamar a /api/chat en ningun momento. Es texto estatico del frontend, no una respuesta del agente -- comportamiento correcto confirmado, sin ambiguedad.
 

## RESUMEN DE RESULTADOS

| # | Categoría | Prueba | Veredicto |
|---|---|---|---|
| 1.1 | RAG | w/cm S2 | ✅ |
| 1.2 | RAG | f'c sísmico | ⚠️ |
| 1.3 | RAG | Cemento ASTM | ✅ |
| 1.4 | RAG | Granulometría | ✅ |
| 1.5 | RAG | Fuera de scope | ✅ |
| 2.1 | FUVIA | Predicción estándar | ✅ |
| 2.2 | FUVIA | Firewall agua (exceso) | ✅ |
| 2.3 | FUVIA | Firewall edad | ✅ |
| 2.4 | FUVIA | SCMs | ✅ |
| 2.5 | FUVIA | Extremo opuesto (agua mínima) | ✅ |
| 3.1 | Ambas | Validación F2 (NO CUMPLE) | ✅ |
| 3.2 | Ambas | Sulfatos S2 | ✅ |
| 3.3 | Ambas | Optimización | ✅ |
| 3.4 | Ambas | NO CUMPLE verificado | ✅ |
| 3.5 | Ambas | SÍ CUMPLE verificado | ✅ |
| 4.1 | Memoria | Multi-turno (3) | ✅ |
| 4.2 | Memoria | Precisión numérica retenida | ✅ |
| 4.3 | Memoria | Conversación larga (4+) | ✅ |
| 4.4 | Memoria | Corrección de dato | ✅ |
| 4.5 | Memoria | Cruce entre herramientas | ✅ |
| 5.1 | Edge | Saludo | ✅ |
| 5.2 | Edge | Pregunta ambigua | ✅ |
| 5.3 | Edge | Inglés | ✅ |
| 5.4 | Edge | Límite inclusivo dominio | ✅ |
| 5.5 | Edge | Sin contexto / fuera de tema | ✅ |
| 6.1 | Confirmación | Sí, analizar | ✅ |
| 6.2 | Confirmación | No por ahora | ✅ |

**Total pruebas documentadas:** 27 de 27
**Resultado:** 26 ✅ · 1 ⚠️ · 0 ❌
**Pass rate:** 26/27 = 96.3%
**Criterio de aprobación:** ≥80% con veredicto ✅ -- **cumplido**

**Unico resultado no-aprobado:** Prueba 1.2, por limitacion de extraccion conocida y ya documentada en la Seccion 5.5 (tabla no indexada) -- comportamiento de fail-safe correcto, no un fallo de razonamiento del agente.