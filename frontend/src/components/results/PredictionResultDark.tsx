import { getStrengthStyleDark, getACStyleDark, getGAStyleDark } from '../../utils/styleMappers';

interface PredictionResultProps {
  resultado: {
    resistencia_estimada:  number;
    relacion_agua_cemento: number;
    relacion_grava_arena:  number;
    clase_resistencia:     string;
    recomendaciones:       string[];
    clase_ga:              string;
    descripcion_ga:        string;
    caracteristicas_ga:    string[];
    clase_ac:              string;
    descripcion_ac:        string;
    caracteristicas_ac:    string[];
  };
}

export default function PredictionResultDark({ resultado }: PredictionResultProps) {
  const strengthStyle = getStrengthStyleDark(resultado.clase_resistencia);
  const acStyle       = getACStyleDark(resultado.clase_ac);
  const gaStyle       = getGAStyleDark(resultado.clase_ga);

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 h-full">

      {/* TARJETA 1: RESISTENCIA */}
      <div className="md:col-span-2 bg-slate-800 rounded-xl border border-slate-700 flex flex-col overflow-hidden">
        <div className="px-4 py-3 border-b border-slate-700 flex justify-between items-center">
          <h4 className="text-[11px] font-bold text-slate-400 uppercase tracking-widest">
            Resistencia estimada
          </h4>
          <span className={`px-2 py-0.5 rounded-md text-[10px] font-bold border uppercase tracking-wide ${strengthStyle.badge}`}>
            {resultado.clase_resistencia}
          </span>
        </div>
        <div className="px-4 py-6 flex-1 flex flex-col items-center justify-center">
          <div className="flex items-baseline gap-2">
            <span className="text-6xl font-bold text-slate-100 tracking-tight">
              {resultado.resistencia_estimada}
            </span>
            <span className="text-lg font-medium text-slate-500">MPa</span>
          </div>
        </div>
        <div className="bg-slate-900 px-4 py-3 border-t border-slate-700">
          <p className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-2 text-center">
            Aplicaciones sugeridas
          </p>
          <div className="flex flex-wrap gap-1.5 justify-center">
            {(resultado.recomendaciones || []).map((uso, i) => (
              <span key={i} className="px-2 py-1 bg-slate-800 text-slate-400 text-[10px] font-semibold rounded-full border border-slate-700">
                {uso}
              </span>
            ))}
          </div>
        </div>
      </div>

      {/* TARJETA 2: RELACIÓN A/C */}
      <div className="bg-slate-800 rounded-xl border border-slate-700 flex flex-col overflow-hidden">
        <div className="px-4 py-3 border-b border-slate-700 flex justify-between items-center">
          <p className="text-[11px] font-bold text-slate-400 uppercase tracking-widest">Agua / Cemento</p>
          <span className={`px-2 py-0.5 rounded-md text-[10px] font-bold border uppercase tracking-wide ${acStyle.badge}`}>
            {resultado.clase_ac}
          </span>
        </div>
        <div className="px-4 py-6 flex-1 flex flex-col items-center justify-center">
          <span className="text-5xl font-bold text-slate-100 tracking-tight">
            {resultado.relacion_agua_cemento}
          </span>
        </div>
        <div className="bg-slate-900 px-4 py-3 border-t border-slate-700">
          <div className="flex flex-wrap gap-1.5 justify-center">
            {(resultado.caracteristicas_ac || []).map((c, i) => (
              <span key={i} className="px-2 py-1 bg-slate-800 text-slate-400 text-[10px] font-medium rounded-full border border-slate-700">
                {c}
              </span>
            ))}
          </div>
        </div>
      </div>

      {/* TARJETA 3: RELACIÓN GRAVA/ARENA */}
      <div className="bg-slate-800 rounded-xl border border-slate-700 flex flex-col overflow-hidden">
        <div className="px-4 py-3 border-b border-slate-700 flex justify-between items-center">
          <p className="text-[11px] font-bold text-slate-400 uppercase tracking-widest">Grava / Arena</p>
          <span className={`px-2 py-0.5 rounded-md text-[10px] font-bold border uppercase tracking-wide ${gaStyle.badge}`}>
            {resultado.clase_ga}
          </span>
        </div>
        <div className="px-4 py-6 flex-1 flex flex-col items-center justify-center">
          <span className="text-5xl font-bold text-slate-100 tracking-tight">
            {resultado.relacion_grava_arena}
          </span>
        </div>
        <div className="bg-slate-900 px-4 py-3 border-t border-slate-700">
          <div className="flex flex-wrap gap-1.5 justify-center">
            {(resultado.caracteristicas_ga || []).map((c, i) => (
              <span key={i} className="px-2 py-1 bg-slate-800 text-slate-400 text-[10px] font-medium rounded-full border border-slate-700">
                {c}
              </span>
            ))}
          </div>
        </div>
      </div>

    </div>
  );
}