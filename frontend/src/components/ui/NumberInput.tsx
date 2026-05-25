import React from 'react';

interface NumberInputProps {
  label: string;
  name: string;
  //Aceptamos string para permitir inputs vacíos al borrar
  value: number | string; 
  onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  step?: number | string;
  disabled?: boolean;
  hasError?: boolean; // Prop para activar el color rojo
}

export default function NumberInput({ label, name, value, onChange, step = "any", disabled = false, hasError = false }: NumberInputProps) {
  return (
    <div className="flex flex-col">
      {/*
         - text-slate-500: Color neutro para no pelear con el input.
      */}
      <label className={`text-xs font-bold uppercase tracking-wider mb-2 ml-1 transition-colors ${
        hasError ? 'text-red-500' : 'text-slate-500'
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
        /*Estilos conectados a tu Sistema de Diseño
           - focus:border-brand -> Borde azul de tu marca al enfocar.
           - focus:ring-brand/20 -> Anillo exterior suave (con opacidad) al enfocar.
           - transition-all -> Suaviza el cambio de color.
        */
        className={`
          w-full 
          p-3 
          border 
          rounded-lg 
          font-medium 
          outline-none 
          transition-all 
          duration-200 
          
          ${disabled 
            // 1. ESTILOS BLOQUEADO (Gris, sin cursor)
            ? 'bg-slate-100 text-slate-400 border-slate-200 cursor-not-allowed' 
            
            // Si no está bloqueado, verificamos si hay error:
            : hasError
              // 2. ESTILOS DE ERROR 🔴 (Fondo rojizo, texto oscuro, borde rojo)
              ? 'bg-red-50 text-red-900 border-red-500 placeholder:text-red-300 focus:bg-white focus:border-red-600 focus:ring-4 focus:ring-red-500/20'
              
              // 3. ESTILOS NORMALES 🔵 (Tu diseño original)
              : 'bg-slate-50 text-slate-800 border-slate-200 placeholder:text-slate-300 focus:bg-white focus:border-brand focus:ring-4 focus:ring-brand/10' 
          }
        `}
      />
    </div>
  );
}