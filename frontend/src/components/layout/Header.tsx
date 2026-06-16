export default function Header() {
  return (
    <header className="w-full bg-slate-950 border-b border-slate-800/60">

      {/* Línea de acento superior */}
      <div className="h-[2px] w-full bg-gradient-to-r from-transparent via-blue-500 to-transparent opacity-60" />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">

          {/* MARCA */}
          <div className="flex items-center gap-4">
            {/* Indicador de estado */}
            <div className="flex items-center gap-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-blue-400 animate-pulse" />
            </div>

            {/* Nombre del sistema */}
            <div>
              <span className="text-2xl font-black tracking-[0.25em] text-slate-100 uppercase">
                FUVIA
              </span>
              <span className="text-2xl font-black tracking-[0.25em] text-blue-400 ml-1.5">
                X
              </span>
            </div>

            {/* Divisor */}
            <div className="h-6 w-px bg-slate-700 mx-1" />

            {/* Descripción */}
            <span className="text-[11px] font-medium text-slate-500 tracking-[0.12em] uppercase hidden sm:block">
              Plataforma de Inteligencia para Concreto
            </span>
          </div>

          {/* BADGE RAG */}
          <div className="hidden md:flex items-center gap-2 bg-slate-900 border border-slate-700 rounded-full px-3 py-1.5">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
            <span className="text-[10px] font-semibold text-slate-400 tracking-widest uppercase">
              Análisis normativo · Predicción ML
              
            </span>
          </div>

        </div>
      </div>

    </header>
  );
}