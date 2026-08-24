import {
  BarChart, Bar, XAxis, YAxis, ReferenceLine,
  Cell, LabelList, ResponsiveContainer,
} from 'recharts';
import type { SHAPContribution } from '../../types/concreteTypes';

// ── Paleta tema claro ─────────────────────────────────────────────────────────
const COLOR_POSITIVE = '#15803d';  // green-700
const COLOR_NEGATIVE = '#b91c1c';  // red-700

// ── Renderizador de etiqueta inline ──────────────────────────────────────────
const renderLabel = (props: {
  x?: number | string; y?: number | string; width?: number | string; height?: number | string; value?: number | string;
}) => {
  const { x = 0, y = 0, width = 0, height = 0, value = 0 } = props;
  // Convertir a número para las operaciones matemáticas
  const nx = Number(x); const ny = Number(y);
  const nw = Number(width); const nh = Number(height); const nv = Number(value);
  const sign   = nv >= 0 ? '+' : '';
  const color  = nv >= 0 ? COLOR_POSITIVE : COLOR_NEGATIVE;
  const xPos   = nv >= 0 ? nx + nw + 5 : nx + nw - 5;
  const anchor = nv >= 0 ? 'start' : 'end';
  return (
    <text
      x={xPos}
      y={ny + nh / 2}
      textAnchor={anchor}
      dominantBaseline="central"
      fontSize={9}
      fontWeight={700}
      fill={color}
    >
      {sign}{nv.toFixed(2)}
    </text>
  );
};

// ── Nombres en español ────────────────────────────────────────────────────────
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

// ── Props ─────────────────────────────────────────────────────────────────────
interface SHAPContributionCardLightProps {
  shap_base_value:    number;
  shap_contributions: SHAPContribution[];
}

export default function SHAPContributionCardLight({
  shap_base_value,
  shap_contributions,
}: SHAPContributionCardLightProps) {
  const chartData = shap_contributions.map(c => ({
    ...c,
    shortName: SHORT_NAMES[c.feature] ?? c.feature,
  }));

  const maxAbs = Math.max(...shap_contributions.map(c => Math.abs(c.value)), 1);
  const domain: [number, number] = [-maxAbs * 1.35, maxAbs * 1.35];

  return (
    <div className="bg-white rounded-xl shadow-sm border border-slate-100 mt-6 overflow-hidden">

      {/* Header — mismo patrón que AbramsLineChart y MixPieChart */}
      <div className="p-6 pb-4 border-b border-slate-50 flex justify-between items-center">
        <h3 className="text-sm font-bold text-slate-400 uppercase tracking-wide">
          Contribución SHAP al f'c
        </h3>
        <span className="px-2 py-1 rounded-md text-[10px] font-bold border uppercase tracking-wide text-slate-500 bg-slate-100">
          Explicabilidad XAI
        </span>
      </div>

      <div className="px-6 pt-3 pb-1 flex items-center gap-2">
        <span className="text-[10px] text-slate-400 uppercase tracking-wider font-semibold">
          Valor base del modelo
        </span>
        <span className="text-[12px] font-bold text-slate-700 ml-auto">
          {shap_base_value.toFixed(2)} MPa
        </span>
      </div>

      <div className="px-4 pb-6">
        <div className="w-full h-72">
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
                tick={{ fontSize: 11, fill: '#64748b' }}
                tickLine={false}
                axisLine={false}
              />

              {/* Línea central roja punteada */}
              <ReferenceLine
                x={0}
                stroke="#ef4444"
                strokeWidth={1.5}
                strokeDasharray="4 3"
              />

              <Bar
                dataKey="value"
                radius={[0, 4, 4, 0]}
                barSize={18}
                isAnimationActive={false}
              >
                <LabelList dataKey="value" content={renderLabel} />
                {chartData.map((entry, index) => (
                  <Cell
                    key={`cell-${index}`}
                    fill={entry.value >= 0 ? COLOR_POSITIVE : COLOR_NEGATIVE}
                    fillOpacity={0.85}
                  />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Leyenda */}
        <div className="flex justify-center gap-6 mt-2">
          <div className="flex items-center gap-1.5">
            <span className="w-3 h-3 rounded-sm" style={{ background: COLOR_POSITIVE }} />
            <span className="text-[10px] text-slate-400 font-semibold uppercase tracking-wide">Aumenta f'c</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-1 h-4 rounded-sm" style={{ background: '#ef4444' }} />
            <span className="text-[10px] text-slate-400 font-semibold uppercase tracking-wide">Punto neutro</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-3 h-3 rounded-sm" style={{ background: COLOR_NEGATIVE }} />
            <span className="text-[10px] text-slate-400 font-semibold uppercase tracking-wide">Reduce f'c</span>
          </div>
        </div>
      </div>
    </div>
  );
}
