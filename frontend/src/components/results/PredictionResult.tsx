// Importamos el mapeador de estilos
import { getStrengthStyle, getACStyle, getGAStyle } from '../../utils/styleMappers';

interface PredictionResultProps {
  resultado: {
    resistencia_estimada: number;
    relacion_agua_cemento: number;
    relacion_grava_arena: number;
    
    clase_resistencia: string;
    recomendaciones: string[];
    
    clase_ga: string;
    descripcion_ga: string;
    caracteristicas_ga: string[];

    clase_ac: string;
    descripcion_ac: string;
    caracteristicas_ac: string[];
  };
}

export default function PredictionResult({ resultado }: PredictionResultProps) {
  // Solo pedimos estilos basándonos en las etiquetas de texto del backend
  const strengthStyle = getStrengthStyle(resultado.clase_resistencia);
  const acStyle = getACStyle(resultado.clase_ac);
  const gaStyle = getGAStyle(resultado.clase_ga); 

  return (
    // Definimos 2 columnas en pantallas medianas (md:grid-cols-2)
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6 h-full">
      
      {/* --- TARJETA 1: RESISTENCIA --- */}
      <div className="md:col-span-2 bg-white rounded-xl shadow-sm border border-slate-100 flex flex-col justify-between overflow-hidden transition-all">
        
        {/* 1. HEADER NUEVO (Con la línea sutil abajo) */}
        <div className="px-6 py-4 border-b border-slate-50 flex justify-between items-start">
             <h4 className="text-sm font-bold text-slate-400 uppercase tracking-wide">
               Resistencia
             </h4>
             <span className={`px-2 py-1 rounded-md text-[10px] font-bold border uppercase tracking-wide ${strengthStyle.badge}`}>
               {resultado.clase_resistencia}
             </span>
        </div>

        {/* 2. BODY NUEVO (El número centrado en el espacio restante) */}
        <div className="px-6 pb-6 pt-10 flex-1 flex flex-col items-center justify-center">
          <div className="flex items-baseline gap-2">
            <span className="text-7xl font-bold text-slate-800 tracking-tight">
              {resultado.resistencia_estimada}
            </span>
            <span className="text-xl font-medium text-slate-400">MPa</span>
          </div>
        </div>
        
        {/* Footer */}
        <div className="bg-slate-50 px-6 pt-4 pb-4 border-t border-slate-100 flex flex-col items-center shrink-0">
          <p className="text-[10px] font-bold text-slate-400 uppercase tracking-wide mb-3 text-center">
            Aplicaciones Sugeridas
          </p>
          <div className="flex flex-wrap gap-2 justify-center w-full">
            {(resultado.recomendaciones || []).map((uso, index) => (
              <span key={index} className="px-3 py-1 bg-white text-slate-600 text-[11px] font-semibold rounded-full border border-slate-200 shadow-sm">
                {uso}
              </span>
            ))}
          </div>
        </div>
      </div>

      {/* --- TARJETA 2: RELACIÓN A/C --- */}
      <div className={`md:col-span-1 bg-white rounded-xl shadow-sm border border-slate-100 flex flex-col justify-between overflow-hidden transition-all`}>
        
        {/* 1. HEADER NUEVO (Igual que arriba) */}
        <div className="px-6 py-4 border-b border-slate-50 flex justify-between items-start">
            <p className="text-sm font-bold text-slate-400 uppercase tracking-wide">Relación AGUA/CEMENTO</p>
            
            <div className={`px-2 py-1 rounded-md border uppercase tracking-wide flex flex-col items-end ${acStyle.bg} ${acStyle.border}`}>
              <span className={`text-[10px] font-bold ${acStyle.color}`}>
                {resultado.clase_ac}
              </span>
            </div>
        </div>

        {/* 2. BODY NUEVO (Centrado vertical perfecto) */}
        <div className="px-6 pb-6 pt-10 flex-1 flex flex-col items-center justify-center">
            <span className="text-6xl font-bold text-slate-800 tracking-tight">
              {resultado.relacion_agua_cemento}
            </span>
        </div>

        {/* Footer */}
        <div className="bg-slate-50 px-6 pt-4 pb-4 border-t border-slate-100 flex flex-col items-center shrink-0">
          <p className="text-[10px] font-bold text-slate-400 uppercase tracking-wide mb-3 text-center">
            Comportamiento de la Mezcla
          </p>
          <div className="flex flex-wrap gap-2 justify-center w-full">
            {(resultado.caracteristicas_ac || []).map((caracteristica, index) => (
              <span key={index} className="px-3 py-1 bg-white text-slate-600 text-[11px] font-medium rounded-full border border-slate-200 shadow-sm flex items-center gap-1.5">
                <span className={`w-1.5 h-1.5 rounded-full ${acStyle.bg.replace('bg-', 'bg-').replace('-50', '-400')}`}></span>
                {caracteristica}
              </span>
            ))}
          </div>
        </div>
      </div>

      {/* --- TARJETA 3: RELACIÓN GRAVA/ARENA --- */}
      <div className={`md:col-span-1 bg-white rounded-xl shadow-sm border border-slate-100 flex flex-col justify-between overflow-hidden transition-all`}>
        
        {/* 1. HEADER NUEVO (Igual que arriba) */}
        <div className="px-6 py-4 border-b border-slate-50 flex justify-between items-start">
            <p className="text-sm font-bold text-slate-400 uppercase tracking-wide">Relación GRAVA/ARENA</p>
            
            <div className={`px-2 py-1 rounded-md border uppercase tracking-wide flex flex-col items-end ${gaStyle.bg} ${gaStyle.border}`}>
              <span className={`text-[10px] font-bold ${gaStyle.color}`}>
                {resultado.clase_ga}
              </span>
            </div>
        </div>

        {/* 2. BODY NUEVO (Centrado vertical perfecto) */}
        <div className="px-6 pb-6 pt-10 flex-1 flex flex-col items-center justify-center">
            <span className="text-6xl font-bold text-slate-800 tracking-tight">
              {resultado.relacion_grava_arena}
            </span>
        </div>

        {/* Footer */}
        <div className="bg-slate-50 px-6 pt-4 pb-4 border-t border-slate-100 flex flex-col items-center shrink-0">
          <p className="text-[10px] font-bold text-slate-400 uppercase tracking-wide mb-3 text-center">
            Comportamiento de la Mezcla
          </p>
          <div className="flex flex-wrap gap-2 justify-center w-full">
            {(resultado.caracteristicas_ga || []).map((caracteristica, index) => (
              <span key={index} className="px-3 py-1 bg-white text-slate-600 text-[11px] font-medium rounded-full border border-slate-200 shadow-sm flex items-center gap-1.5">
                <span className={`w-1.5 h-1.5 rounded-full ${gaStyle.bg.replace('bg-', 'bg-').replace('-50', '-400')}`}></span>
                {caracteristica}
              </span>
            ))}
          </div>
        </div>
      </div>

    </div>
  );
}