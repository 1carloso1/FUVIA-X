import type { ActiveMix } from '../../hooks/useActiveMix';

interface MixSelectorProps {
  mixes:    ActiveMix[];
  activeId: string;
  onSelect: (id: string) => void;
}

export default function MixSelector({ mixes, activeId, onSelect }: MixSelectorProps) {
  const current = mixes.find(m => m.id === activeId);
  const title = current?.origin === 'copilot'
    ? `Propuesta del copiloto ${current.label}`
    : 'Mezcla del formulario';

  return (
    <div className="space-y-2">
      <p className="text-[11px] font-bold text-slate-300 uppercase tracking-widest">{title}</p>
      {mixes.length > 1 && (
        <div className="flex flex-wrap gap-1.5">
          {mixes.map(m => (
            <button
              key={m.id}
              onClick={() => onSelect(m.id)}
              className={`px-2.5 py-1 rounded-md text-[10px] font-semibold border transition-colors ${
                m.id === activeId
                  ? 'bg-slate-700 text-slate-100 border-slate-500'
                  : 'bg-slate-900 text-slate-500 border-slate-700 hover:text-slate-300'
              }`}
            >
              {m.origin === 'form' ? 'Formulario' : `Copiloto ${m.label}`}
              {' · '}{m.result.resistencia_estimada.toFixed(1)} MPa
            </button>
          ))}
        </div>
      )}
    </div>
  );
}