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
        <div className="bg-white border-l-4 border-red-500 p-4 shadow-xl rounded-lg">
          <p className="font-bold text-red-600 mb-2 text-xs uppercase tracking-wider">
            Mezcla Actual
          </p>
          <div className="space-y-1">
            <p className="text-sm text-slate-600">
              <span className="font-semibold text-slate-800">A/C:</span> {data.ratio}
            </p>
            <p className="text-sm text-slate-600">
              <span className="font-semibold text-slate-800">Resistencia:</span> {data.strength} MPa
            </p>
          </div>
        </div>
      );
    }

    // CASO 2: LA CURVA (Simulación)
    return (
      <div className="bg-white border-l-4 border-brand p-4 shadow-xl rounded-lg">
        <p className="font-bold text-brand-light mb-2 text-xs uppercase tracking-wider">
          Simulación Teórica
        </p>
        <div className="space-y-1">
          <p className="text-sm text-slate-600">
            <span className="font-semibold text-slate-800">A/C:</span> {data.ratio}
          </p>
          <p className="text-sm text-slate-600">
            <span className="font-semibold text-slate-800">Resistencia:</span> {data.strength} MPa
          </p>
        </div>
      </div>
    );
  }
  return null;
};

export default AbramsGraph;