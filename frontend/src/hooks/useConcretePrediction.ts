import { useState, useMemo, useRef, useEffect } from 'react';
import { predecirConcreto, generarReporteAPI } from '../services/predictionService';
import type { ConcreteInputData, PredictionResponse } from '../types/concreteTypes';
import { DEFAULT_STATE, INITIAL_STATE } from '../constants/concreteConstants';



export function useConcretePrediction() {
  
  // 1. ESTADO
  const [form, setForm] = useState<ConcreteInputData>(DEFAULT_STATE);
  
  const [resultado, setResultado] = useState<PredictionResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [camposError, setCamposError] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [isLocked, setIsLocked] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [realStrength, setRealStrength] = useState(""); // Valor experimental

  const resultsRef = useRef<HTMLDivElement>(null);
  const printRef = useRef<HTMLDivElement>(null);

  // 2. EFECTOS
    // 2.1 SCROLL:  Cuando 'resultado' cambia y no es null, hacemos scroll suave hacia él.
  useEffect(() => {
    if (resultado && resultsRef.current) {
      // Un pequeño timeout asegura que el DOM ya se pintó antes de scrollear
      setTimeout(() => {
        resultsRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }, 100);
    }
  }, [resultado]);

  // 3. HANDLERS
    // 3.1. HANDLER INTELIGENTE
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    
    // Si el usuario borra todo (value es ""), guardamos string vacío.
    // Esto permite que el input se vea vacío visualmente.
    if (value === '') {
      setForm({ ...form, [name]: '' });
      return;
    }

    // Detectar si el usuario está escribiendo decimales
    // Si termina en punto (ej: "12.") O si es un decimal intermedio (ej: "12.0")
    // Lo guardamos como TEXTO para que no se borre el caracter.
    if (value.endsWith('.') || (value.includes('.') && value.endsWith('0'))) {
      setForm({ ...form, [name]: value });
      return;
    }

    // Intento de conversión estándar
    const numVal = parseFloat(value);
    
    if (!isNaN(numVal)) {
      // Si es un número válido, lo guardamos.
      setForm({ ...form, [name]: numVal });
    } else {
      // Si no es número (ej: letras), ignoramos o dejamos lo que estaba
      // Opcional: permitir que se escriba pero no guardarlo si solo quieres nums
    }
  };

    // 3.2. SUBMIT SEGURO (Limpia los datos antes de enviar)
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null); // Limpiamos errores previos
    setCamposError([]); // Limpiamos los campos pintados de rojo
    setResultado(null); // Limpiamos resultados previos

      // CONVERTIR A NÚMEROS PUROS:
      // Si algún campo se quedó como string vacío "", lo convertimos a 0 antes de enviar
      const payload = {
        cement: Number(form.cement),
        slag: Number(form.slag),
        flyash: Number(form.flyash),
        water: Number(form.water),
        superplasticizer: Number(form.superplasticizer),
        coarseaggregate: Number(form.coarseaggregate),
        fineaggregate: Number(form.fineaggregate),
        age: Number(form.age)
      };

      // VALIDACIÓN: ¿Hay materiales?
      // Sumamos todo EXCEPTO 'age'. Si la suma es 0, es que el formulario está vacío.
      const totalMateriales = 
        payload.cement + 
        payload.slag + 
        payload.flyash + 
        payload.water + 
        payload.superplasticizer + 
        payload.coarseaggregate + 
        payload.fineaggregate;

      if (totalMateriales <= 0) {
        setError("Sin información que inferir. Por favor agrega materiales a la mezcla.");
        return; // <--- AQUÍ DETENEMOS LA FUNCIÓN. No se hace el fetch.
      }
 
    setLoading(true); // Activamos el estado de carga

    try {
      const data = await predecirConcreto(payload);
      setResultado(data);
      setIsLocked(true);
    } catch (error) {
      console.error("Falla interceptada:", error);
      
      // 1. Definimos la estructura exacta que esperamos sin usar 'any'
      type ExpectedError = {
        response?: {
          data?: {
            detail?: unknown;
          };
        };
        detail?: unknown;
        message?: string;
      };

      // 2. Asertamos el error con nuestro tipo seguro
      const err = error as ExpectedError;
      
      // 3. Extraemos el detalle como 'unknown'
      let errorDetail: unknown = null;
      
      if (err?.response?.data?.detail) {
        errorDetail = err.response.data.detail;
      } else if (err?.detail) {
        errorDetail = err.detail;
      } else if (err?.message) {
        errorDetail = err.message;
      }

      // 4. Validamos el contenido con Type Guards
      if (
        errorDetail && 
        typeof errorDetail === 'object' && 
        'campos' in errorDetail && 
        'mensaje' in errorDetail
      ) {
        // Como ya comprobamos que es un objeto con 'campos' y 'mensaje', 
        // TypeScript nos permite asertarlo con seguridad:
        const detailObj = errorDetail as { campos: string[]; mensaje: string };
        setError(detailObj.mensaje);
        setCamposError(detailObj.campos);
      } 
      else if (typeof errorDetail === 'string') {
        setError(errorDetail);
        setCamposError([]);
      } 
      else {
        setError("Error: No se pudo conectar con el servidor.");
        setCamposError([]);
      }
    } finally {
      setLoading(false);
    }
  };

  // 3.3. FUNCIÓN DE REINICIO
  const handleReset = () => {
    // A. Hacemos scroll hacia arriba PRIMERO para evitar saltos bruscos
    window.scrollTo({
      top: 0,
      behavior: 'smooth'
    });

    // B. Esperamos un poco a que suba y luego limpiamos (opcional, o hacerlo directo)
    setTimeout(() => {
      setResultado(null);       // Borrar gráficas
      setForm(INITIAL_STATE);   // Borrar datos del formulario
      setIsLocked(false);       // Desbloquear inputs
      setError(null);           // Borrar errores si los hubiera
      setCamposError([]);       // Despintar los inputs rojos
    }, 600); // 600ms da tiempo al scroll
  };

  // 3.4. FUNCIÓN DE MODAL
  const openModal = () => setIsModalOpen(true);
  const closeModal = () => setIsModalOpen(false);
  
  const handleExperimentalChange = (val: string) => {
     // Solo permitir números y un punto decimal
     if (/^\d*\.?\d*$/.test(val)) {
        setRealStrength(val);
     }
  };

  const confirmPdfGeneration = async (graficasBase64: string, overrideStrength?: string) => {
    try {
      if (!resultado) return; 
      
      const fuerzaFinal = overrideStrength !== undefined ? overrideStrength : realStrength;
      const pdfBlob = await generarReporteAPI(form, resultado, fuerzaFinal, graficasBase64);
      
      const url = window.URL.createObjectURL(pdfBlob);
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `Reporte_Validacion_${form.age}dias.pdf`);
      document.body.appendChild(link);
      link.click();
      
      link.parentNode?.removeChild(link);
      window.URL.revokeObjectURL(url);
      
      closeModal();
    } catch (error) {
      console.error("Error al generar PDF:", error);
      alert("Hubo un problema al generar el reporte. Intenta nuevamente.");
    }
  };

  // 4. PREPARACIÓN DE DATOS (Optimizada con useMemo)
  const pieData = useMemo(() => {
    // Nota: Recharts necesita códigos HEX directos en el objeto 'fill', 
    // no lee clases de Tailwind automáticamente.
    const datosBrutos = [
      { name: 'Cemento', value: Number(form.cement), fill: '#1e293b' }, // Slate-800
      { name: 'Escoria', value: Number(form.slag), fill: '#64748b' },   // Slate-500
      { name: 'Ceniza', value: Number(form.flyash), fill: '#94a3b8' },  // Slate-400
      { name: 'Agua', value: Number(form.water), fill: '#3b82f6' },     // Blue-500
      { name: 'Aditivo', value: Number(form.superplasticizer), fill: '#8b5cf6' }, // Violet-500
      { name: 'Grava', value: Number(form.coarseaggregate), fill: '#451a03' }, // Amber-900
      { name: 'Arena', value: Number(form.fineaggregate), fill: '#d97706' }    // Amber-600
    ];

    return datosBrutos.filter(item => item.value > 0);
  }, [form]);

  return {
    form,
    resultado,
    error,
    camposError,
    loading,
    isLocked,
    resultsRef,
    pieData, 
    isModalOpen,
    realStrength,
    printRef,
    handleChange,
    handleSubmit,
    handleReset,
    openModal,
    closeModal,
    handleExperimentalChange,
    confirmPdfGeneration,
  };
}