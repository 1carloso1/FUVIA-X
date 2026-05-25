export interface ConcreteInputData {
// Permitimos number | string para que el input se pueda quedar vacío visualmente
  cement: number | string;
  slag: number | string;
  flyash: number | string;
  water: number | string;
  superplasticizer: number | string;
  coarseaggregate: number | string;
  fineaggregate: number | string;
  age: number | string;
}

export interface PredictionResponse {
  resistencia_estimada: number;
  relacion_agua_cemento: number;
  relacion_grava_arena: number;
  clase_resistencia: string;
  recomendaciones: string[];
  clase_ga: string;
  descripcion_ga: string;
  caracteristicas_ga: string[];
  clase_ac: string;
  descripcion_ac: string;
  caracteristicas_ac: string[];
}