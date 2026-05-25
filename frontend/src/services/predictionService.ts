import type { ConcreteInputData, PredictionResponse } from '../types/concreteTypes';
import pkg from '../../package.json';

// 1. Obtenemos la URL base (Ej: https://fuvia.onrender.com)
const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

// 2. Limpiamos la URL para que NUNCA termine en "/" ni en "/api/predecir"
const baseUrl = API_URL.replace(/\/+$/, "").replace(/\/api\/predecir$/, "");

//"Recibo ConcreteInputData y devuelvo una Promesa de PredictionResponse"
export const predecirConcreto = async (formData: ConcreteInputData): Promise<PredictionResponse> => {
  const response = await fetch(`${baseUrl}/api/predecir`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(formData)
  });

  // --- INTERCEPTAMOS ERRORES DEL BACKEND ---
  if (!response.ok) {
    // 1. Tratamos de leer el cuerpo del error que mandó Python
    const errorData = await response.json().catch(() => null);
    
    // arrojamos el objeto COMPLETO directamente hacia el Hook.
    if (errorData) {
      throw errorData;
    } else {
      throw new Error("Error al conectar con el servidor de predicción");
    }
  }

  // --- SI TODO ESTÁ BIEN ---
  return await response.json();

  // --- SI TODO ESTÁ BIEN ---
  return await response.json();
};

// --- NUEVA FUNCIÓN PARA EL PDF ---
export const generarReporteAPI = async (
  formData: ConcreteInputData, 
  resultadoPrediccion: PredictionResponse,
  realStrength: string | number, 
  graficasBase64: string
): Promise<Blob> => {
  
  const payload = {
    inputs: formData,
    prediccion: resultadoPrediccion,
    // Si realStrength es un valor válido mayor a 0, lo mandamos como número. Si no, mandamos null.
    resistencia_real: (realStrength && Number(realStrength) > 0) ? Number(realStrength) : null,
    graficas_base64: graficasBase64,
    version: pkg.version
  };

  const response = await fetch(`${baseUrl}/api/generar-reporte`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });

  if (!response.ok) throw new Error("Error al generar el documento PDF en el servidor.");
  
  return await response.blob(); 
};