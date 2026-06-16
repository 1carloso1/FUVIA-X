// ================================================================
// VARIANTES ORIGINALES (tema claro — FormularioConcreto original)
// ================================================================

export const getStrengthStyle = (claseBackend: string) => {
  if (!claseBackend) return { badge: 'bg-slate-50 text-slate-400 border-slate-200', text: 'text-slate-400' };
  const clase = claseBackend.toLowerCase();
  if (clase.includes('baja'))
    return { badge: 'bg-red-50 text-red-700 border-red-200',       text: 'text-red-600' };
  if (clase.includes('estándar') || clase.includes('estandar'))
    return { badge: 'bg-blue-50 text-blue-700 border-blue-200',    text: 'text-blue-600' };
  if (clase.includes('ultra'))
    return { badge: 'bg-violet-50 text-violet-700 border-violet-200', text: 'text-violet-600' };
  return   { badge: 'bg-emerald-50 text-emerald-700 border-emerald-200', text: 'text-emerald-600' };
};

export const getACStyle = (claseAC: string) => {
  if (!claseAC) return { color: 'text-slate-400', bg: 'bg-slate-50', border: 'border-slate-100' };
  const clase = claseAC.toLowerCase();
  if (clase.includes('alta'))  return { color: 'text-amber-600',   bg: 'bg-amber-50',   border: 'border-amber-100' };
  if (clase.includes('baja'))  return { color: 'text-indigo-600',  bg: 'bg-indigo-50',  border: 'border-indigo-100' };
  return                              { color: 'text-emerald-600', bg: 'bg-emerald-50', border: 'border-emerald-100' };
};

export const getGAStyle = (claseGA: string) => {
  if (!claseGA) return { color: 'text-slate-400', bg: 'bg-slate-50', border: 'border-slate-100' };
  const clase = claseGA.toLowerCase();
  if (clase.includes('fina'))                              return { color: 'text-amber-600',   bg: 'bg-amber-50',   border: 'border-amber-100' };
  if (clase.includes('áspera') || clase.includes('aspera')) return { color: 'text-indigo-600',  bg: 'bg-indigo-50',  border: 'border-indigo-100' };
  return                                                          { color: 'text-emerald-600', bg: 'bg-emerald-50', border: 'border-emerald-100' };
};


// ================================================================
// VARIANTES DARK (tema oscuro — MainLayout / FUVIA X)
// ================================================================

export const getStrengthStyleDark = (claseBackend: string) => {
  if (!claseBackend) return { badge: 'bg-slate-800 text-slate-400 border-slate-700' };
  const clase = claseBackend.toLowerCase();
  if (clase.includes('baja'))
    return { badge: 'bg-red-950 text-red-400 border-red-800' };
  if (clase.includes('estándar') || clase.includes('estandar'))
    return { badge: 'bg-blue-950 text-blue-400 border-blue-800' };
  if (clase.includes('ultra'))
    return { badge: 'bg-violet-950 text-violet-400 border-violet-800' };
  return   { badge: 'bg-emerald-950 text-emerald-400 border-emerald-800' };
};

export const getACStyleDark = (claseAC: string) => {
  if (!claseAC) return { badge: 'bg-slate-800 text-slate-400 border-slate-700' };
  const clase = claseAC.toLowerCase();
  if (clase.includes('alta'))  return { badge: 'bg-amber-950 text-amber-400 border-amber-800' };
  if (clase.includes('baja'))  return { badge: 'bg-indigo-950 text-indigo-400 border-indigo-800' };
  return                              { badge: 'bg-emerald-950 text-emerald-400 border-emerald-800' };
};

export const getGAStyleDark = (claseGA: string) => {
  if (!claseGA) return { badge: 'bg-slate-800 text-slate-400 border-slate-700' };
  const clase = claseGA.toLowerCase();
  if (clase.includes('fina'))                                return { badge: 'bg-amber-950 text-amber-400 border-amber-800' };
  if (clase.includes('áspera') || clase.includes('aspera'))  return { badge: 'bg-indigo-950 text-indigo-400 border-indigo-800' };
  return                                                            { badge: 'bg-emerald-950 text-emerald-400 border-emerald-800' };
};