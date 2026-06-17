interface AbramsGraphProps {
  active?: boolean;
  payload?: Array<{
    payload: {
      ratio: number;
      strength: number;
      esReal?: boolean; // Hacemos opcional para evitar errores si falta
    };
  }>;
}

const AbramsGraph = ({ active, payload }: AbramsGraphProps) => {
  if (active && payload && payload.length) {
    const data = payload[0].payload;

    // CASO 1: TU MEZCLA (El punto rojo)
    if (data.esReal) {
  return (
    <div className="bg-slate-800 border-l-4 border-red-500 p-3 shadow-xl rounded-lg">
      <p className="font-bold text-red-400 mb-1 text-[10px] uppercase tracking-wider">Mezcla Actual</p>
      <p className="text-[11px] text-slate-400"><span className="text-slate-200 font-semibold">A/C:</span> {data.ratio}</p>
      <p className="text-[11px] text-slate-400"><span className="text-slate-200 font-semibold">f'c:</span> {data.strength} MPa</p>
    </div>
  );
}

    // CASO 2: LA CURVA (Simulación)
    return (
  <div className="bg-slate-800 border-l-4 border-blue-500 p-3 shadow-xl rounded-lg">
    <p className="font-bold text-blue-400 mb-1 text-[10px] uppercase tracking-wider">Simulación Teórica</p>
    <p className="text-[11px] text-slate-400"><span className="text-slate-200 font-semibold">A/C:</span> {data.ratio}</p>
    <p className="text-[11px] text-slate-400"><span className="text-slate-200 font-semibold">f'c:</span> {data.strength} MPa</p>
  </div>
);
  }
  return null;
};

export default AbramsGraph;