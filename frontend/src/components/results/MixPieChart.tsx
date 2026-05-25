import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer } from 'recharts';

interface DataItem {
  name: string;
  value: number;
  fill: string;
}

interface MixCompositionCardProps {
  data: DataItem[];
  age: number | string;
  isPdf?: boolean;
}

interface CustomTooltipProps {
  active?: boolean;
  payload?: {
    name: string;
    value: number;
    payload: DataItem;
  }[];
}

const CustomTooltip = ({ active, payload }: CustomTooltipProps) => {
  if (active && payload && payload.length) {
    const data = payload[0];
    return (
      <div 
        className="bg-white p-3 shadow-xl rounded-lg border-l-4 z-50"
        style={{ borderColor: data.payload.fill }}
      >
        <p className="font-bold text-slate-700 text-xs uppercase tracking-wider mb-1">
          {data.name}
        </p>
        <p className="text-slate-600 text-sm">
          <span className="font-extrabold text-slate-800">{data.value}</span> kg/m³
        </p>
      </div>
    );
  }
  return null;
};

export default function MixCompositionCard({ data, age, isPdf = false }: MixCompositionCardProps) {
  // Calculamos el peso total para sacar los porcentajes de la tabla
  const totalWeight = data.reduce((acc, item) => acc + item.value, 0);

  return (
    <div className="bg-white rounded-xl border border-slate-100 shadow-sm overflow-hidden flex flex-col h-full">
      
      {/* Header */}
      <div className="p-6 pb-4 border-b border-slate-50 flex justify-between items-center">
        <h3 className="text-sm font-bold text-slate-400 uppercase tracking-wide">
          Diseño de Mezcla
        </h3>
        <span className="px-2 py-1 rounded-md text-[10px] font-bold border uppercase tracking-wide text-slate-500 bg-slate-100">
          Dosificación por Peso
        </span>
      </div>

      <div className="p-6">
        {/* GRID SPLIT: Gráfico (Izquierda) - Tabla (Derecha) */}
        <div className={`grid gap-8 items-center ${isPdf ? 'grid-cols-2' : 'grid-cols-1 md:grid-cols-2'}`}>
          
          {/* --- COLUMNA 1: TU GRÁFICO (Sin cambios en configuración) --- */}
          <div className="h-72 w-full relative">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={data}
                  cx="50%"            // Centrado horizontal
                  cy="50%"            // Centrado vertical
                  innerRadius={60}    // Radio interior (Efecto Donut)
                  outerRadius={80}    // Radio exterior
                  paddingAngle={2}    // Espacio blanco entre rebanadas
                  minAngle={3}        // Mínimo 3 grados por rebanada
                  dataKey="value"
                  cornerRadius={4}    // Bordes redondeados en las rebanadas
                >
                  {data.map((entry, index) => (
                    <Cell 
                      key={`cell-${index}`} 
                      fill={entry.fill}
                      stroke="none"
                      className="outline-none focus:outline-none" // Quita el borde azul al hacer click
                    />
                  ))}
                </Pie>

                {/* Se muestra el número de días en el centro del gráfico */}
                <text 
                  x="50%" 
                  y="44%" // El Número: Lo subimos al 44% para tener efecto céntrico
                  textAnchor="middle" 
                  dominantBaseline="middle" 
                  className="text-3xl font-extrabold fill-slate-700"
                  style={{ pointerEvents: 'none' }}
                >
                  {age}
                </text>

                <text 
                  x="50%" 
                  y="52%" // La Etiqueta: La ponemos pelín abajo de la mitad 52%
                  textAnchor="middle" 
                  dominantBaseline="middle" 
                  className="text-[10px] font-bold fill-slate-400 uppercase tracking-widest"
                  style={{ pointerEvents: 'none' }}
                >
                  DÍAS
                </text>
                
                {/* Tooltip personalizado */}
                <Tooltip content={<CustomTooltip />}
                isAnimationActive={false} 
                />
                
                
                {/* Leyenda estilizada */}
                <Legend 
                  verticalAlign="bottom" 
                  height={36} 
                  iconType="circle" 
                  iconSize={8}
                  formatter={(value) => (
                    // Usamos span para aplicar clases de Tailwind al texto de la leyenda
                    <span className="text-slate-500 text-xs font-semibold ml-1">{value}</span>
                  )}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>

          {/* --- COLUMNA 2: TABLA DE DETALLES --- */}
          <div className="border border-slate-100 rounded-lg flex flex-col h-auto">
            <table className="w-full table-fixed border-collapse">
              <thead className="bg-slate-50 border-b border-slate-100">
                <tr>
                  <th className="w-5/12 px-2 py-3 text-center text-[10px] font-bold text-slate-400 uppercase">Material</th>
                  <th className="w-4/12 px-2 py-3 text-center text-[10px] font-bold text-slate-400 uppercase">Kg/m³</th>
                  <th className="w-3/12 px-2 py-3 text-center text-[10px] font-bold text-slate-400 uppercase">%</th>
                </tr>
              </thead>
              <tbody className="bg-white">
                {data.map((item, index) => (
                  <tr key={index} className="border-b border-slate-50">
                    {/* ELIMINAMOS whitespace-nowrap y agregamos py-3 para dar margen */}
                    <td className="px-2 py-3">
                      <div className="flex items-center justify-center gap-2">
                        {/* AGREGAMOS shrink-0 para que el círculo no se aplaste */}
                        <div className="w-2 h-2 shrink-0 rounded-full" style={{ backgroundColor: item.fill }} />
                        {/* ELIMINAMOS truncate y agregamos break-words y whitespace-normal */}
                        <span className="text-xs font-semibold text-slate-600 whitespace-normal break-words">{item.name}</span>
                      </div>
                    </td>
                    {/* ELIMINAMOS whitespace-nowrap de las demás celdas */}
                    <td className="px-2 py-3 text-center text-xs font-bold text-slate-700">
                      {item.value}
                    </td>
                    <td className="px-2 py-3 text-center text-[10px] font-bold text-slate-400">
                      {((item.value / totalWeight) * 100).toFixed(1)}%
                    </td>
                  </tr>
                ))}
                {/* Fila Total */}
                <tr className="bg-slate-50/50">
                  <td className="px-2 py-3 text-center text-[10px] font-bold text-slate-500 uppercase">Peso Total</td>
                  <td className="px-2 py-3 text-center text-xs font-extrabold text-slate-800">{totalWeight}</td>
                  <td className="px-2 py-3 text-center text-[10px] font-bold text-slate-500">100%</td>
                </tr>
              </tbody>
            </table>
          </div>

        </div>
      </div>
    </div>
  );
}