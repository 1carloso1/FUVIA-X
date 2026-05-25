import { generarCurvaAbrams } from '../../utils/curvaAbrams';
import AbramsTooltip from '../tooltips/AbramsTooltip'; 
import { 
  LineChart, Line, XAxis, YAxis, CartesianGrid, ReferenceDot, 
  Tooltip, ResponsiveContainer, Label 
} from 'recharts';

interface AbramsCurveCardProps {
  ratio: number;
  strength: number;
}

export default function AbramsCurveCard({ ratio, strength }: AbramsCurveCardProps) {
  const data = generarCurvaAbrams(ratio, strength);

  // COLORES DEL SISTEMA (Coinciden con tailwind.config.js)
  const colors = {
    brand: '#00357a',      // Tu azul principal
    grid: '#e2e8f0',       // slate-200
    text: '#64748b',       // slate-500
    contrast: '#ef4444',   // red-500 (Para el punto de "Ud. está aquí")
    tooltipLine: '#94a3b8' // slate-400
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border border-slate-100 mt-6 overflow-hidden">
      
      <div className="p-6 pb-4 border-b border-slate-50 flex justify-between items-center">
        <h3 className="text-sm font-bold text-slate-400 uppercase tracking-wide">
          Curva de Abrams
        </h3>
        {/* Badge opcional para mantener el estilo de "etiqueta a la derecha" */}
        <span className="px-2 py-1 rounded-md text-[10px] font-bold border uppercase tracking-wide text-slate-500 bg-slate-100">
          Proyección - Real vs Teórica 
        </span>
      </div>

      <div className="p-6">
        <div className="w-full h-80">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart
              data={data}
              margin={{ top: 20, right: 30, left: 20, bottom: 20 }}
            >
              <CartesianGrid strokeDasharray="3 3" stroke={colors.grid} vertical={false} />

              <XAxis 
                dataKey="ratio" 
                type="number" 
                domain={['dataMin', 'dataMax']} 
                tickCount={8}
                stroke={colors.text}
                tick={{ fontSize: 12, fill: colors.text }}
                tickLine={false}
                axisLine={{ stroke: colors.grid, strokeWidth: 2 }}
              >
                <Label 
                  value="Relación Agua/Cemento" 
                  offset={-15} 
                  position="insideBottom" 
                  style={{ fill: colors.text, fontSize: '12px', fontWeight: 600, textTransform: 'uppercase' }} 
                />
              </XAxis>

              <YAxis 
                stroke={colors.text} 
                tick={{ fontSize: 12, fill: colors.text }}
                tickLine={false}
                axisLine={false}
                label={{ 
                  value: 'Resistencia (MPa)', 
                  angle: -90, 
                  position: 'insideLeft',
                  style: { fill: colors.text, fontSize: '12px', fontWeight: 600, textTransform: 'uppercase', textAnchor: 'middle' } 
                }} 
              />
              
              <Tooltip 
                content={<AbramsTooltip />} 
                cursor={{ stroke: colors.tooltipLine, strokeWidth: 2, strokeDasharray: '4 4' }} 
              />

              <Line 
                type="monotone" 
                dataKey="strength" 
                stroke={colors.brand} 
                strokeWidth={4} 
                dot={false} 
                activeDot={{ r: 8, stroke: colors.brand, strokeWidth: 4, fill: 'white' }} 
                isAnimationActive={true}
              />

              <ReferenceDot 
                x={ratio} 
                y={strength}
                r={6} 
                fill={colors.contrast} 
                stroke="white" 
                strokeWidth={3}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="mt-4 flex justify-center items-center gap-2 opacity-80 hover:opacity-100 transition-opacity">
          <span className="w-3 h-3 rounded-full bg-red-500 border-2 border-white shadow-sm" />
          <p className="text-[10px] uppercase tracking-widest text-slate-400 font-semibold">
            Mezcla Actual
          </p>
        </div>

      </div>
    </div>
  );
}