import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from 'recharts';

interface DataItem {
  name:  string;
  value: number;
  fill:  string;
}

interface MixCompositionCardDarkProps {
  data:   DataItem[];
  age:    number | string;
  isPdf?: boolean;
}

interface CustomTooltipProps {
  active?:  boolean;
  payload?: { name: string; value: number; payload: DataItem }[];
}

const CustomTooltip = ({ active, payload }: CustomTooltipProps) => {
  if (active && payload && payload.length) {
    const item = payload[0];
    return (
      <div
        className="bg-slate-800 p-2.5 shadow-xl rounded-lg border-l-4 z-50"
        style={{ borderColor: item.payload.fill }}
      >
        <p className="font-bold text-slate-300 text-[10px] uppercase tracking-wider mb-1">
          {item.name}
        </p>
        <p className="text-slate-400 text-[11px]">
          <span className="font-extrabold text-slate-200">{item.value}</span> kg/m³
        </p>
      </div>
    );
  }
  return null;
};

export default function MixCompositionCardDark({ data, age, isPdf = false }: MixCompositionCardDarkProps) {
  const totalWeight = data.reduce((acc, item) => acc + item.value, 0);

  return (
    <div className="bg-slate-800 rounded-xl border border-slate-700 overflow-hidden flex flex-col">

      {/* Header */}
      <div className="px-4 py-3 border-b border-slate-700 flex justify-between items-center">
        <h3 className="text-[11px] font-bold text-slate-400 uppercase tracking-widest">
          Composición de la mezcla
        </h3>
        <span className="px-2 py-0.5 rounded-md text-[10px] font-bold border uppercase tracking-wide text-slate-500 bg-slate-900 border-slate-700">
          Dosificación por peso
        </span>
      </div>

      <div className="p-4">
        <div className={`grid gap-4 items-start ${isPdf ? 'grid-cols-2' : 'grid-cols-1 md:grid-cols-2'}`}>

          {/* Pie chart — sin Legend interna */}
          <div className="flex flex-col items-center">
            <div className="w-full h-44">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart margin={{ top: 0, right: 0, bottom: 0, left: 0 }}>
                  <Pie
                    data={data}
                    cx="50%" cy="50%"
                    innerRadius={48} outerRadius={68}
                    paddingAngle={2} minAngle={3}
                    dataKey="value"
                    cornerRadius={4}
                  >
                    {data.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.fill} stroke="none" />
                    ))}
                  </Pie>

                  {/* Días en el centro */}
                  <text x="50%" y="44%" textAnchor="middle" dominantBaseline="middle"
                    style={{ fontSize: '20px', fontWeight: 700, fill: '#e2e8f0', pointerEvents: 'none' }}>
                    {age}
                  </text>
                  <text x="50%" y="55%" textAnchor="middle" dominantBaseline="middle"
                    style={{ fontSize: '8px', fontWeight: 700, fill: '#64748b', textTransform: 'uppercase', letterSpacing: '0.1em', pointerEvents: 'none' }}>
                    DÍAS
                  </text>

                  <Tooltip content={<CustomTooltip />} isAnimationActive={false} />
                </PieChart>
              </ResponsiveContainer>
            </div>

            {/* Leyenda manual — fuera del ResponsiveContainer para evitar espacio en blanco */}
            <div className="flex flex-wrap justify-center gap-x-3 gap-y-1 mt-1">
              {data.map((item) => (
                <div key={item.name} className="flex items-center gap-1">
                  <span className="w-2 h-2 rounded-full flex-shrink-0" style={{ backgroundColor: item.fill }} />
                  <span className="text-[10px] text-slate-500 font-medium">{item.name}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Tabla */}
          <div className="border border-slate-700 rounded-lg overflow-hidden">
            <table className="w-full table-fixed border-collapse">
              <thead className="bg-slate-900 border-b border-slate-700">
                <tr>
                  <th className="w-5/12 px-2 py-2 text-center text-[10px] font-bold text-slate-500 uppercase">Material</th>
                  <th className="w-4/12 px-2 py-2 text-center text-[10px] font-bold text-slate-500 uppercase">kg/m³</th>
                  <th className="w-3/12 px-2 py-2 text-center text-[10px] font-bold text-slate-500 uppercase">%</th>
                </tr>
              </thead>
              <tbody>
                {data.map((item, index) => (
                  <tr key={index} className="border-b border-slate-700/50">
                    <td className="px-2 py-2">
                      <div className="flex items-center justify-center gap-1.5">
                        <div className="w-2 h-2 shrink-0 rounded-full" style={{ backgroundColor: item.fill }} />
                        <span className="text-[10px] font-semibold text-slate-400 whitespace-normal break-words">{item.name}</span>
                      </div>
                    </td>
                    <td className="px-2 py-2 text-center text-[11px] font-bold text-slate-300">{item.value}</td>
                    <td className="px-2 py-2 text-center text-[10px] font-bold text-slate-500">
                      {((item.value / totalWeight) * 100).toFixed(1)}%
                    </td>
                  </tr>
                ))}
                <tr className="bg-slate-900/50">
                  <td className="px-2 py-2 text-center text-[10px] font-bold text-slate-500 uppercase">Total</td>
                  <td className="px-2 py-2 text-center text-[11px] font-extrabold text-slate-200">{totalWeight}</td>
                  <td className="px-2 py-2 text-center text-[10px] font-bold text-slate-500">100%</td>
                </tr>
              </tbody>
            </table>
          </div>

        </div>
      </div>
    </div>
  );
}