import { useConcretePrediction } from '../../hooks/useConcretePrediction';
import NumberInput from '../ui/NumberInput';
import PredictionResult from '../results/PredictionResult';
import MixCompositionCard from '../results/MixPieChart';
import AbramsCurveCard from '../results/AbramsLineChart';
import ValidationModal from '../ui/ValidationModal';
import html2canvas from 'html2canvas';

export default function FormularioConcreto() {

  // LOGICA
  const { 
      form, resultado, error, loading, isLocked, camposError, resultsRef, pieData,
      isModalOpen, realStrength, openModal, closeModal, handleExperimentalChange, confirmPdfGeneration,
      handleChange, handleSubmit, handleReset, printRef
  } = useConcretePrediction();

  // RENDER
  return (
    <div className="max-w-4xl w-full bg-white shadow-2xl rounded-xl overflow-hidden relative">
      {/* ENCABEZADO DEL FORMULARIO (Instrucciones) */}
      <div className="bg-slate-50 p-6 border-b border-slate-200">
        <div className="flex items-start gap-3">
          {/* Ícono de información opcional, pero le da un toque muy pro */}
          <div className="mt-0.5 text-[#00357a]">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-5 h-5">
              <path fillRule="evenodd" d="M2.25 12c0-5.385 4.365-9.75 9.75-9.75s9.75 4.365 9.75 9.75-4.365 9.75-9.75 9.75S2.25 17.385 2.25 12zm8.706-1.442c1.146-.573 2.437.463 2.126 1.732l-1.178 4.814a1.5 1.5 0 01-2.887.323c-1.146-.573-2.437-.463-2.126-1.732l1.178-4.814a1.5 1.5 0 012.887-.323zM12 9a1.5 1.5 0 100-3 1.5 1.5 0 000 3z" clipRule="evenodd" />
            </svg>
          </div>
          
          <div>
      <h2 className="text-base sm:text-lg font-bold text-[#0a2e5c]">
        Diseño de Mezcla
      </h2>
      <p className="text-slate-600 text-sm mt-1 leading-relaxed">
        Para que el sistema infiera con precisión la resistencia de la mezcla, las cantidades ingresadas deben corresponder a las proporciones de diseño para <span className="font-bold text-[#00357a] bg-blue-50 px-1.5 py-0.5 rounded border border-blue-100">un metro cúbico (1 m³)</span>.
      </p>
    </div>
        </div>
      </div>

      {/* --- FORMULARIO --- */}
      <div className="p-8">
        <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-6">
          <NumberInput 
            label="Cemento (kg/m³)" 
            name="cement" 
            value={form.cement} 
            onChange={handleChange} 
            disabled={isLocked}
            hasError={camposError.includes("cement")}
          />
          <NumberInput 
            label="Escoria de Alto Horno (kg/m³)" 
            name="slag" 
            value={form.slag} 
            onChange={handleChange} 
            disabled={isLocked}
            hasError={camposError.includes("slag")}
          />
          <NumberInput 
            label="Ceniza Volante (kg/m³)" 
            name="flyash" 
            value={form.flyash} 
            onChange={handleChange} 
            disabled={isLocked}
            hasError={camposError.includes("flyash")}
          />
          <NumberInput 
            label="Agua (kg/m³)" 
            name="water" 
            value={form.water} 
            onChange={handleChange} 
            disabled={isLocked}
            hasError={camposError.includes("water")}
          />
          <NumberInput 
            label="Superplastificante (kg/m³)" 
            name="superplasticizer" 
            value={form.superplasticizer} 
            onChange={handleChange} 
            step={0.1} 
            disabled={isLocked}
            hasError={camposError.includes("superplasticizer")}
          />
          <NumberInput 
            label="Agregado Grueso / Grava (kg/m³)" 
            name="coarseaggregate" 
            value={form.coarseaggregate} 
            onChange={handleChange} 
            disabled={isLocked}
            hasError={camposError.includes("coarseaggregate")}
          />
          <NumberInput 
            label="Agregado Fino / Arena (kg/m³)" 
            name="fineaggregate" 
            value={form.fineaggregate} 
            onChange={handleChange} 
            disabled={isLocked}
            hasError={camposError.includes("fineaggregate")}
          />
          <NumberInput 
            label="Edad (días)" 
            name="age" 
            value={form.age} 
            onChange={handleChange} 
            disabled={isLocked}
            hasError={camposError.includes("age")}
          />
          <div className="md:col-span-2 mt-6">
            <button
              type="submit"
              disabled={loading || isLocked}
              className={`w-full bg-brand text-white font-bold py-4 rounded-lg shadow-lg transition transform active:scale-[0.98] text-lg flex justify-center items-center gap-2 ${loading || isLocked ? 'opacity-50 cursor-not-allowed' : 'hover:bg-brand-hover'}`}
            >
              {/* ESTADO CARGANDO: Spinner animado */}
              {loading && (
                <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
              )}
              {/* ESTADO COMPLETADO: Checkmark (Palomita) */}
              {!loading && isLocked && (
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              )}
              {/* ESTADO NORMAL: Rayo (Ejecutar) */}
              {!loading && !isLocked && (
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              )}
              {/* TEXTO DEL BOTÓN */}
              <span>
                {loading ? 'Calculando...' : isLocked ? 'Inferencia Completada' : 'Ejecutar Inferencia'}
              </span>
            </button>
          </div>
        </form>

        {/* CASO DE ERROR */}
        {error && (
          <div className="mt-6 p-4 bg-red-50 border-l-4 border-red-500 text-red-700 rounded-r">
            <p className="font-bold">Error</p>
            <p>{error}</p>
          </div>
        )}

        {/* RESULTADOS */}
        {resultado && (
          <div ref={resultsRef} className="mt-10 animate-fade-in space-y-8 border-t pt-8 border-gray-100">
            <div className="flex flex-col gap-8">
              {/* FILA SUPERIOR: MÉTRICAS */}
              <PredictionResult resultado={resultado} />
              {/* FILA INFERIOR: PIE CHART */}
              <MixCompositionCard data={pieData} age={form.age} />
            </div>
            {/* SECCIÓN INFERIOR: ABRAMS */}   
            <AbramsCurveCard ratio={resultado.relacion_agua_cemento} strength={resultado.resistencia_estimada}/>
            {/* --- BOTONES DE ACCIÓN FINAL (PDF y REINICIO) --- */}
            <div className="mt-12 pt-8 border-t border-slate-100 flex flex-col md:flex-row gap-4">
              {/*  Botón REINICIAR */}
              <button
                onClick={handleReset}
                className="
                  w-full md:w-[40%]
                  bg-brand text-white 
                  font-bold py-4 rounded-lg shadow-lg 
                  transition transform active:scale-[0.98] 
                  text-lg flex justify-center items-center gap-2
                  hover:bg-brand-hover
                "
              >
                <span className="text-xl">↺</span> Nuevo Diseño
              </button>
              {/* 2. Botón PDF */}
              <button
                type="button" 
                onClick={openModal} // <--- AHORA ABRE EL MODAL
                className="w-full md:w-[60%] bg-[#ef4444] text-white font-bold py-4 rounded-lg shadow-lg hover:bg-red-600 transition transform active:scale-[0.98] flex justify-center items-center gap-2"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                Generar Reporte PDF
              </button>
            </div>
          </div>
        )}
      </div>
      {/* --- RENDERIZADO DEL MODAL --- */}
      {/* Se renderiza aquí abajo, flotando sobre todo lo demás */}
      <ValidationModal
        isOpen={isModalOpen}
        onClose={closeModal}
        value={realStrength}
        onChange={handleExperimentalChange}
        predictedValue={resultado?.resistencia_estimada || 0}
        predictionClass={resultado?.clase_resistencia || ''}
        
        // BOTÓN 1: "Confirmar" (Usa el valor que el usuario escribió en el input)
        onConfirm={async () => {
          try {
            if (!printRef.current) return;
            const canvas = await html2canvas(printRef.current, { scale: 2, windowWidth: 1200, width: 800 });
            const base64 = canvas.toDataURL('image/png');
            await confirmPdfGeneration(base64); // No mandamos el 2do parámetro, usa el estado normal
          } catch (err) {
            console.error("Error capturando gráficas:", err);
          }
        }}

        // BOTÓN 2: "Omitir y Generar" (Fuerza el 0 inmediatamente)
        onSkip={async () => {
          try {
            if (!printRef.current) return;
            handleExperimentalChange("0"); // Opcional: actualiza el input visualmente a "0"
            const canvas = await html2canvas(printRef.current, { scale: 2, windowWidth: 1200, width: 800 });
            const base64 = canvas.toDataURL('image/png');
            
            // Aquí le mandamos el "0" explícitamente a tu hook
            await confirmPdfGeneration(base64, "0"); 
          } catch (err) {
            console.error("Error capturando gráficas:", err);
          }
        }}
      />
      {/* =========================================================
          EL SET DE FOTOGRAFÍA (CONTENEDOR OCULTO)
          Se renderiza solo cuando hay un resultado.
          Con w-[800px] fijamos el tamaño perfecto para el PDF,
          sin importar si el usuario está en celular o monitor.
          ========================================================= */}
      {resultado && (
        <div 
          ref={printRef}
          // Volvemos a mandarlo fuera de la pantalla, pero con opacidad normal al 100%
          className="absolute -left-[9999px] w-[800px] bg-white"
        >
           {/* El padding-bottom (pb-8) sigue siendo importante para proteger los bordes */}
           <div>
             <MixCompositionCard data={pieData} age={form.age} isPdf={true}/>
           </div>

           <div>
             <AbramsCurveCard ratio={resultado.relacion_agua_cemento} strength={resultado.resistencia_estimada}/>
           </div>
        </div>
      )}

    </div>
  );
}