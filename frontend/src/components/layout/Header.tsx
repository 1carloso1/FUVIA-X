export default function Header() {
  return (
    <header className="w-full bg-white border-b-4 border-[#00357a] shadow-md">
      {/* Barra superior delgada (opcional para un toque más pro) */}
      <div className="w-full h-1 bg-[#D4AF37]"></div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center py-4 md:py-6">
          
          {/* LADO IZQUIERDO: Logos */}
          <div className="hidden sm:flex items-center gap-4 md:gap-8">
            {/* Logo Universidad */}
            <div className="h-12 md:h-16 w-auto flex items-center">
              <img 
                src="/logo-universidad.png" 
                alt="Logo Universidad" 
                className="h-full object-contain"
              />
            </div>
            
            {/* Divisor vertical */}
            <div className="h-16 w-[1px] bg-slate-200 hidden md:block"></div>
            
            {/* Logo Laboratorio */}
            <div className="h-8 md:h-16 w-auto flex items-center">
              <img 
                src="/logo-laboratorio.png" 
                alt="Logo Laboratorio" 
                className="h-full object-contain"
              />
            </div>
          </div>

            {/* LADO DERECHO: Título y Badge */}
            <div className="w-full sm:w-auto text-center sm:text-right">
            
            <h1 className="text-xl md:text-2xl font-black text-[#0a2e5c] tracking-[0.4em] uppercase">
                FUVIA
            </h1>
            
            <div className="flex justify-center sm:justify-end items-center gap-2 mt-1">
                <span className="h-2 w-2 rounded-full bg-green-500 animate-pulse"></span>
                <p className="text-[10px] md:text-xs font-bold text-slate-500 uppercase tracking-[0.1em]">
                Evaluación Predictiva de Diseños de Mezcla
                </p>
            </div>
            
            </div>

        </div>
      </div>
    </header>
  );
}