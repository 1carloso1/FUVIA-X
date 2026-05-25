/**
 * Genera un conjunto de coordenadas (x, y) para visualizar la Curva de Abrams.
 * * Esta función calibra la ecuación de Abrams basándose en el punto de predicción actual
 * para proyectar cómo cambiaría la resistencia si se variara la relación agua/cemento.
 * * **Modelo Matemático:**
 * La Ley de Abrams establece: f'c = A/(B^{a/c})$
 * - Se asume B = 14 (Constante estándar para Cemento Portland).
 * - Se despeja A usando los valores de entrada.
 * * @param {number} ratioActual - Relación agua/cemento (a/c) de la mezcla actual (Eje X).
 * @param {number} resistenciaActual - Resistencia a la compresión estimada en MPa (Eje Y).
 * @returns {Array<{ratio: number, strength: number, esReal: boolean}>} 
 * Retorna un array ordenado de objetos, donde cada uno representa un punto en la gráfica.
 * La propiedad `esReal` distingue la predicción actual de la proyección matemática.
 */

export const generarCurvaAbrams = (ratioActual: number, resistenciaActual: number) => {
  // 1. VALIDACIÓN: Evitamos cálculos con valores nulos o negativos que rompan la gráfica.
  if (!ratioActual || ratioActual <= 0) return [];

  const puntos = [];
  // 2. CALIBRACIÓN DEL MODELO:
  // Despejamos la constante 'A' usando el punto conocido (la predicción de la IA).
  // Fórmula despejada: A = Resistencia * (14 ^ ratio)
  const A = resistenciaActual * Math.pow(14, ratioActual);
  
  // 3. DEFINICIÓN DEL DOMINIO (Rango del Eje X):
  // Calculamos un rango dinámico visualmente agradable: +/- 0.2 alrededor del punto real.
  // Math.max(0.20, ...) asegura que la gráfica nunca empiece por debajo de a/c = 0.20.
  const start = Math.max(0.20, Math.floor((ratioActual - 0.2) * 10) / 10);
  const end = Math.max(0.80, Math.ceil((ratioActual + 0.2) * 10) / 10);

  // 4. GENERACIÓN DE LA CURVA (Iteración):
  // Creamos puntos simulados cada 0.02 unidades de a/c para suavizar la línea.
  for (let r = start; r <= end; r += 0.02) {
    // FILTRO DE SUPERPOSICIÓN:
    // Si un punto simulado está demasiado cerca (< 0.01) del punto real, 
    // lo saltamos para evitar que se encimen visualmente en la gráfica.
    if (Math.abs(r - ratioActual) < 0.01) continue;

    // Aplicamos la fórmula de Abrams con la 'A' calibrada: f'c = A / (14 ^ r)
    const resistencia = A / Math.pow(14, r);
    puntos.push({
      ratio: parseFloat(r.toFixed(2)),  // Redondeo a 2 decimales para limpieza visual
      strength: parseFloat(resistencia.toFixed(2)),
      esReal: false,  // BANDERA: Indica que es un punto matemático (proyección)
    });
  }
  
  // 5. INYECCIÓN DEL PUNTO CRÍTICO:
  // Insertamos el punto exacto que predijo la IA.
  puntos.push({
      ratio: parseFloat(ratioActual.toFixed(3)), // Mayor precisión (3 decimales) para el punto real
      strength: parseFloat(resistenciaActual.toFixed(2)),
      esReal: true, // BANDERA: Indica que este es el resultado del usuario (Punto Rojo)
  });
  
  // 6. ORDENAMIENTO FINAL:
  // Las librerías de gráficas (como Recharts) necesitan los datos ordenados por el Eje X
  // para dibujar la línea secuencialmente sin "saltos" extraños.
  return puntos.sort((a, b) => a.ratio - b.ratio);
};