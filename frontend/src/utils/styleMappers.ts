export const getStrengthStyle = (claseBackend: string) => {
  // ESCUDO DE SEGURIDAD
  if (!claseBackend) return { badge: 'bg-slate-50 text-slate-400 border-slate-200', text: 'text-slate-400' };

  // Normalizamos a minúsculas o buscamos coincidencias parciales por seguridad
  const clase = claseBackend.toLowerCase();

  if (clase.includes('baja')) {
    return {
      badge: 'bg-red-50 text-red-700 border-red-200',
      text: 'text-red-600',
    };
  }
  if (clase.includes('estándar') || clase.includes('estandar')) {
    return {
      badge: 'bg-blue-50 text-blue-700 border-blue-200',
      text: 'text-blue-600',
    };
  }

  if (clase.includes('ultra')) {
    return {
      badge: 'bg-violet-50 text-violet-700 border-violet-200',
      text: 'text-violet-600',
    };
  }
  // Default (Alta)
  return {
    badge: 'bg-emerald-50 text-emerald-700 border-emerald-200',
    text: 'text-emerald-600',
  };
};

export const getACStyle = (claseAC: string) => {
  // ESCUDO DE SEGURIDAD
  if (!claseAC) return { color: 'text-slate-400', bg: 'bg-slate-50', border: 'border-slate-100' };

  const clase = claseAC.toLowerCase();

  if (clase.includes('alta')) { // Mucha agua
    return {
      color: 'text-amber-600',
      bg: 'bg-amber-50',
      border: 'border-amber-100'
    };
  }
  if (clase.includes('baja')) { // Poca agua
    return {
      color: 'text-indigo-600',
      bg: 'bg-indigo-50',
      border: 'border-indigo-100'
    };
  }
  // Óptima
  return {
    color: 'text-emerald-600',
    bg: 'bg-emerald-50',
    border: 'border-emerald-100'
  };
};

export const getGAStyle = (claseGA: string) => {
  // ESCUDO DE SEGURIDAD
  if (!claseGA) return { color: 'text-slate-400', bg: 'bg-slate-50', border: 'border-slate-100' };

  const clase = claseGA.toLowerCase();

  if (clase.includes('fina')) { // Mucha arena
    return {
      color: 'text-amber-600',
      bg: 'bg-amber-50',
      border: 'border-amber-100'
    };
  }
  if (clase.includes('áspera') || clase.includes('aspera')) { // Mucha Grava
    return {
      color: 'text-indigo-600',
      bg: 'bg-indigo-50',
      border: 'border-indigo-100'
    };
  }
  // Óptima
  return {
    color: 'text-emerald-600',
    bg: 'bg-emerald-50',
    border: 'border-emerald-100'
  };
};