import { generarCurvaAbrams } from '../../utils/curvaAbrams';
import AbramsTooltip from '../tooltips/AbramsTooltip';
import { LineChart, Line, XAxis, YAxis, CartesianGrid,
  ReferenceDot, ReferenceLine, Tooltip, ResponsiveContainer, Label
} from 'recharts';

interface AbramsCurveCardDarkProps {
  ratio:    number;
  strength: number;
}

export default function AbramsCurveCardDark({ ratio, strength }: AbramsCurveCardDarkProps) {
  const data = generarCurvaAbrams(ratio, strength);

  const colors = {
    brand:       '#378ADD',   // Azul FUVIA X
    grid:        '#334155',  // slate-700 en lugar de slate-800
    text:        '#64748b',   // slate-500
    contrast:    '#ef4444',   // red-500
    tooltipLine: '#475569',   // slate-600
  };

  return (
    <div className="bg-slate-800 rounded-xl border border-slate-700 overflow-hidden">

      <div className="px-4 py-3 border-b border-slate-700 flex justify-between items-center">
        <h3 className="text-[11px] font-bold text-slate-400 uppercase tracking-widest">
          Curva de Abrams
        </h3>
        <span className="px-2 py-0.5 rounded-md text-[10px] font-bold border uppercase tracking-wide text-slate-500 bg-slate-900 border-slate-700">
          Real vs Teórica
        </span>
      </div>

      <div className="p-4">
        <div className="w-full h-56">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={data} margin={{ top: 16, right: 24, left: 16, bottom: 20 }}>
              <CartesianGrid strokeDasharray="3 3" stroke={colors.grid} vertical={false}/>

              <XAxis
                dataKey="ratio"
                type="number"
                domain={['dataMin', 'dataMax']}
                tickCount={8}
                stroke={colors.text}
                tick={{ fontSize: 10, fill: colors.text }}
                tickLine={false}
                axisLine={{ stroke: colors.grid, strokeWidth: 1 }}
              >
                <Label
                  value="Relación Agua/Cemento"
                  offset={-14}
                  position="insideBottom"
                  style={{ fill: colors.text, fontSize: '10px', fontWeight: 600, textTransform: 'uppercase' }}
                />
              </XAxis>

              <YAxis
                stroke={colors.text}
                tick={{ fontSize: 10, fill: colors.text }}
                tickLine={false}
                axisLine={false}
                label={{
                  value: 'f\'c (MPa)',
                  angle: -90,
                  position: 'insideLeft',
                  style: { fill: colors.text, fontSize: '10px', fontWeight: 600, textAnchor: 'middle' }
                }}
              />

              <Tooltip
                content={<AbramsTooltip />}
                cursor={{ stroke: colors.tooltipLine, strokeWidth: 1.5, strokeDasharray: '4 4' }}
                isAnimationActive={false}
              />

              <Line
                type="monotone"
                dataKey="strength"
                stroke={colors.brand}
                strokeWidth={3}
                dot={false}
                activeDot={{ r: 6, stroke: colors.brand, strokeWidth: 3, fill: '#0f172a' }}
                isAnimationActive={true}
              />

              <ReferenceDot
                x={ratio}
                y={strength}
                r={5}
                fill={colors.contrast}
                stroke="#0f172a"
                strokeWidth={2}
              />

              <ReferenceLine
                y={strength}
                stroke={colors.contrast}
                strokeDasharray="4 3"
                strokeWidth={1}
                strokeOpacity={0.6}
              />
              <ReferenceLine
                x={ratio}
                stroke={colors.contrast}
                strokeDasharray="4 3"
                strokeWidth={1}
                strokeOpacity={0.6}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="mt-2 flex justify-center items-center gap-2 opacity-70">
          <span className="w-2.5 h-2.5 rounded-full bg-red-500 border border-slate-900" />
          <p className="text-[10px] uppercase tracking-widest text-slate-500 font-semibold">
            Mezcla actual
          </p>
        </div>
      </div>
    </div>
  );
}