import { getStrengthStyle } from '../../utils/styleMappers';

interface ValidationModalProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => void;
  onSkip: () => void;
  predictedValue: number;
  predictionClass: string;
  value: string;
  onChange: (val: string) => void;
}

export default function ValidationModal({ 
  isOpen, onClose, onConfirm, onSkip, predictedValue, predictionClass, value, onChange 
}: ValidationModalProps) {
  
  if (!isOpen) return null;
  const styleIA = getStrengthStyle(predictionClass);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      {/* 1. BACKDROP (Fondo oscuro desenfocado) */}
      <div 
        className="absolute inset-0 bg-slate-900/60 backdrop-blur-sm transition-opacity"
        onClick={onClose}
      ></div>

      {/* 2. CARD DEL MODAL */}
      <div className="relative bg-white rounded-2xl shadow-2xl w-full max-w-md overflow-hidden animate-fade-in-up">
        
        {/* Encabezado */}
        <div className="bg-slate-50 px-6 py-4 border-b border-slate-100 flex justify-between items-center">
          <h3 className="text-lg font-bold text-slate-800 flex items-center gap-2">
            {/* Icono de Probeta */}
            <svg className="w-5 h-5 text-brand" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
            </svg>
            Validación Experimental
          </h3>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-600">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" /></svg>
          </button>
        </div>

        {/* Cuerpo */}
        <div className="p-6">
          <p className="text-sm text-slate-500 mb-6">
            Ingresa el valor real obtenido en laboratorio.
          </p>

          {/* Comparación Visual */}
          <div className="flex items-center gap-4 mb-6">
            <div className={`flex-1 p-3 rounded-lg border text-center ${styleIA.badge}`}>
              <span className={`block text-xs font-bold uppercase tracking-wider opacity-80 ${styleIA.text}`}>Inferencia de IA</span>
              <span className="text-xl font-bold text-slate-700">{predictedValue} <span className="text-xs">MPa</span></span>
            </div>
            <div className="text-slate-400 font-bold">VS</div>
            <div className="flex-1 bg-slate-50 p-3 rounded-lg border border-slate-200 text-center">
               <span className="block text-xs font-bold text-slate-400 uppercase tracking-wider">Real</span>
               {value ? (
                 <span className="text-xl font-bold text-slate-700">{value} <span className="text-xs">MPa</span></span>
               ) : (
                 <span className="text-xl font-bold text-slate-300">---</span>
               )}
            </div>
          </div>

          {/* Input */}
          <div className="relative">
            <label className="block text-xs font-bold text-slate-700 mb-1">Resistencia Real (MPa)</label>
            <input
              type="text"
              value={value}
              onChange={(e) => onChange(e.target.value)}
              placeholder="0.0"
              className="w-full p-3 border rounded-lg font-medium outline-none transition-all duration-200 bg-slate-50 text-slate-800 border-slate-200 placeholder:text-slate-300 focus:bg-white focus:border-brand focus:ring-4 focus:ring-brand/10"
              autoFocus
            />
          </div>
        </div>

        {/* Footer Acciones */}
        <div className="px-6 py-4 bg-slate-50 border-t border-slate-100 flex justify-end gap-3">
          <button 
            onClick={onSkip}
            className="text-slate-500 hover:text-slate-700 font-medium text-sm px-4 py-2"
          >
            Omitir y Generar
          </button>
          <button
            onClick={onConfirm}
            className="bg-brand hover:bg-brand-hover text-white font-bold py-2 px-6 rounded-lg shadow-md transform active:scale-95 transition"
          >
            Confirmar
          </button>
        </div>

      </div>
    </div>
  );
}