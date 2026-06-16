import React from 'react';

interface NumberInputDarkProps {
  label:    string;
  name:     string;
  value:    number | string;
  onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  step?:    number | string;
  disabled?: boolean;
  hasError?: boolean;
}

/**
 * Versión oscura de NumberInput para el layout de FUVIA X.
 * Misma lógica y props que NumberInput.tsx — solo cambian los colores
 * para ser compatibles con el fondo slate-900/950.
 */
export default function NumberInputDark({
  label, name, value, onChange,
  step = 'any', disabled = false, hasError = false
}: NumberInputDarkProps) {
  return (
    <div className="flex flex-col">
      <label className={`text-[10px] font-bold uppercase tracking-wider mb-1.5 ml-0.5 transition-colors ${
        hasError ? 'text-red-400' : 'text-slate-500'
      }`}>
        {label}
      </label>

      <input
        type="number"
        name={name}
        value={value}
        onChange={onChange}
        step={step}
        min="0"
        disabled={disabled}
        placeholder="0.0"
        className={`
          w-full px-3 py-2 border rounded-lg text-[12px] font-medium
          outline-none transition-all duration-200
          ${disabled
            ? 'bg-slate-800 text-slate-600 border-slate-700 cursor-not-allowed'
            : hasError
              ? 'bg-red-950 text-red-300 border-red-700 placeholder:text-red-800 focus:border-red-500 focus:ring-2 focus:ring-red-500/20'
              : 'bg-slate-800 text-slate-200 border-slate-600 placeholder:text-slate-600 focus:bg-slate-750 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20'
          }
        `}
      />
    </div>
  );
}