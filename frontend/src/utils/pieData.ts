import type { ConcreteInputData } from '../types/concreteTypes';

export interface PieItem { name: string; value: number; fill: string; }

export function buildPieData(inputs: ConcreteInputData): PieItem[] {
  const datosBrutos: PieItem[] = [
    { name: 'Cement',           value: Number(inputs.cement),          fill: '#8f8f91' },
    { name: 'Slag',             value: Number(inputs.slag),            fill: '#64748b' },
    { name: 'Fly Ash',          value: Number(inputs.flyash),          fill: '#94a3b8' },
    { name: 'Water',            value: Number(inputs.water),           fill: '#3b82f6' },
    { name: 'Superplasticizer', value: Number(inputs.superplasticizer), fill: '#8b5cf6' },
    { name: 'Coarse Aggregate', value: Number(inputs.coarseaggregate), fill: '#451a03' },
    { name: 'Fine Aggregate',   value: Number(inputs.fineaggregate),   fill: '#d97706' },
  ];
  return datosBrutos.filter(item => item.value > 0);
}