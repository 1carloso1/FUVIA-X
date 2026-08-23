/**
 * SHAPContributionCard.tsx
 * ────────────────────────
 * Visualiza las contribuciones SHAP de cada insumo al f'c predicho.
 * Barras horizontales prominentes con etiquetas inline — sin eje X.
 */

import {
  BarChart, Bar, XAxis, YAxis, ReferenceLine,
  Cell, Tooltip, LabelList, ResponsiveContainer,
} from 'recharts';
import type { SHAPContribution } from '../../types/concreteTypes';

const COLOR_POSITIVE = '#1D9E75';
const COLOR_NEGATIVE = '#D85A30';

interface TooltipProps {
  active?:  boolean;
  payload?: { value: number; payload: SHAPContribution }[];
}

const CustomTooltip = ({ active, payload }: TooltipProps) => {
  if (!active || !payload?.length) return null;
  const { feature, value } = payload[0].payload;
  const sign  = value >= 0 ? '+' : '';
  const color = value >= 0 ? COLOR_POSITIVE : COLOR_NEGATIVE;
  return (
    <div
      className="bg-slate-800 p-2.5 shadow-xl rounded-lg border-l-4 z-50"
      style={{ borderColor: color }}
    >
      <p className="font-bold text-slate-300 text-[10px] uppercase tracking-wider mb-1">
        {feature}
      </p>
      <p className="text-[11px]" style={{ color }}>
        {sign}{value.toFixed(3)} MPa
      </p>
    </div>
  );
};

const renderLabel = (props: {
  x?: number; y?: number; width?: number; height?: number; value?: number;
}) => {
  const { x = 0, y = 0, width = 0, height = 0, value = 0 } = props;
  const sign   = value >= 0 ? '+' : '';
  const color  = value >= 0 ? COLOR_POSITIVE : COLOR_NEGATIVE;
  const xPos   = value >= 0 ? x + width + 5 : x + width - 5;
  const anchor = value >= 0 ? 'start' : 'end';
  return (
    <text
      x={xPos}
      y={y + height / 2}
      textAnchor={anchor}
      dominantBaseline="central"
      fontSize={10}
      fontWeight={700}
      fill={color}
    >
      {sign}{value.toFixed(2)}
    </text>
  );
};

interface SHAPContributionCardProps {
  shap_base_value:    number;
  shap_contributions: SHAPContribution[];
  isPdf?:             boolean;
}

export default function SHAPContributionCard({
  shap_base_value,
  shap_contributions,
  isPdf = false,
}: SHAPContributionCardProps) {
  const SHORT_NAMES: Record<string, string> = {
  'Cement':             'Cemento',
  'Blast Furnace Slag': 'Escoria',
  'Fly Ash':            'Ceniza',
  'Water':              'Agua',
  'Superplasticizer':   'Aditivo',
  'Coarse Aggregate':   'Grava',
  'Fine Aggregate':     'Arena',
  'Age':                'Edad',
};

  const chartData = shap_contributions.map(c => ({
    ...c,
    shortName: SHORT_NAMES[c.feature] ?? c.feature,
  }));

  const maxAbs = Math.max(...shap_contributions.map(c => Math.abs(c.value)), 1);
  const domain: [number, number] = [-maxAbs * 1.35, maxAbs * 1.35];

  return (
    <div className="bg-slate-800 rounded-xl border border-slate-700 overflow-hidden flex flex-col">

      {/* Header */}
      <div className="px-4 py-3 border-b border-slate-700 flex justify-between items-center">
        <h3 className="text-[11px] font-bold text-slate-400 uppercase tracking-widest">
          Contribución SHAP al f'c
        </h3>
        <span className="px-2 py-0.5 rounded-md text-[10px] font-bold border uppercase tracking-wide text-slate-500 bg-slate-900 border-slate-700">
          Explicabilidad XAI
        </span>
      </div>

      {/* Valor base */}
      <div className="px-4 pt-3 pb-1 flex items-center gap-2">
        <span className="text-[10px] text-slate-500 uppercase tracking-wider">
          Valor base del modelo
        </span>
        <span className="text-[12px] font-bold text-slate-300 ml-auto">
          {shap_base_value.toFixed(2)} MPa
        </span>
      </div>

      {/* Gráfico */}
      <div className="px-2 pb-3">
        <div className={isPdf ? 'h-80' : 'h-80 md:h-96'}>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={chartData}
              layout="vertical"
              barCategoryGap="5%"
              margin={{ top: 4, right: 52, left: 72, bottom: 4 }}
            >
              <XAxis
                type="number"
                domain={domain}
                hide={true}
              />
              <YAxis
                type="category"
                dataKey="shortName"
                width={68}
                tick={{ fontSize: 10, fill: '#94a3b8' }}
                tickLine={false}
                axisLine={false}
              />

              <ReferenceLine
                x={0}
                stroke="#ef4444"
                strokeWidth={1.5}
                strokeDasharray="4 3"
              />

              <Tooltip
                content={<CustomTooltip />}
                cursor={{ fill: 'rgba(255,255,255,0.03)' }}
                isAnimationActive={false}
              />

              <Bar
                dataKey="value"
                radius={[0, 4, 4, 0]}
                barSize={40}
                isAnimationActive={false}
              >
                <LabelList dataKey="value" content={renderLabel} />
                {chartData.map((entry, index) => (
                  <Cell
                    key={`cell-${index}`}
                    fill={entry.value >= 0 ? COLOR_POSITIVE : COLOR_NEGATIVE}
                    fillOpacity={0.9}
                  />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Leyenda */}
      <div className="flex justify-center gap-4 pb-3">
        <div className="flex items-center gap-1.5">
          <span className="w-2.5 h-2.5 rounded-sm" style={{ background: COLOR_POSITIVE }} />
          <span className="text-[10px] text-slate-500">Aumenta f'c</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="w-2.5 h-2.5 rounded-sm" style={{ background: COLOR_NEGATIVE }} />
          <span className="text-[10px] text-slate-500">Reduce f'c</span>
        </div>
      </div>

    </div>
  );
}