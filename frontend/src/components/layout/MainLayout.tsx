import { useEffect, useMemo, useState } from 'react';
import MixSelector from '../results/MixSelector';
import { useActiveMix } from '../../hooks/useActiveMix';
import { buildPieData } from '../../utils/pieData';
import PredictionResultDark from '../results/PredictionResultDark';
import MixCompositionCardDark from '../results/MixPieChartDark';
import AbramsCurveCardDark from '../results/AbramsLineChartDark';
import SHAPContributionCardDark from '../results/SHAPContributionCardDark';
import SHAPContributionCard from '../results/SHAPContributionCard';
import MixCompositionCard from '../results/MixPieChart';
import AbramsCurveCard from '../results/AbramsLineChart';
import CopilotChat from '../chat/CopilotChat';
import { useConcretePrediction } from '../../hooks/useConcretePrediction';
import { useAgentChat } from '../../hooks/useAgentChat';
import ValidationModal from '../ui/ValidationModal';
import NumberInputDark from '../ui/NumberInputDark';
import html2canvas from 'html2canvas';

// ----------------------------------------------------------------
// TABS DEL CARRUSEL
// ----------------------------------------------------------------

type Tab = 'formulario' | 'resultados';

// ----------------------------------------------------------------
// COMPONENTE PRINCIPAL
// ----------------------------------------------------------------

export default function MainLayout() {

  const [activeTab, setActiveTab] = useState<Tab>('formulario');

  const {
    form, resultado, error, loading, isLocked, camposError,
    resultsRef, isModalOpen, realStrength, printRef, shapRef,
    submittedInputs,
    handleChange, handleSubmit, handleReset,
    openModal, closeModal, handleExperimentalChange, confirmPdfGeneration,
  } = useConcretePrediction();

  const { mixes, active: shown, selectMix, addCopilotMixes, notice, dismissNotice } =
    useActiveMix(submittedInputs, resultado);
  const shownPie = useMemo(() => (shown ? buildPieData(shown.inputs) : []), [shown]);

  const {
    messages, input, setInput, isLoading: agentLoading,
    lastReport, bottomRef, sendUserMessage, stopGeneration,
    confirmAnalysis, declineAnalysis, handleKeyDown, privacy
  } = useAgentChat(resultado, form, shown, addCopilotMixes);

  // Cambiar automáticamente a tab de resultados cuando llega la predicción
  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    if (resultado) setActiveTab('resultados');
  }, [resultado]);

  const handleFormSubmit = async (e: React.FormEvent) => {
    await handleSubmit(e);
  };

  const handleFormReset = () => {
    handleReset();
    setActiveTab('formulario');
  };

  return (
    <div className="w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 h-[calc(100vh-120px)] min-h-[600px]">

        {/* ====================================================
            COLUMNA IZQUIERDA — Carrusel (Formulario | Resultados)
            ==================================================== */}
        <div className="flex flex-col bg-slate-900 rounded-xl border border-slate-700 overflow-hidden">

          {/* Tab switcher */}
          <div className="flex gap-1 p-2 bg-slate-950 flex-shrink-0 border-b border-slate-700">
            <button
              onClick={() => setActiveTab('formulario')}
              className={`flex-1 py-2 px-3 rounded-lg text-[11px] font-semibold uppercase tracking-wider transition-colors ${
                activeTab === 'formulario'
                  ? 'bg-slate-800 text-slate-100 border border-slate-600'
                  : 'text-slate-500 hover:text-slate-300'
              }`}
            >
              Formulario
            </button>
            <button
              onClick={() => setActiveTab('resultados')}
              disabled={!shown}
              className={`flex-1 py-2 px-3 rounded-lg text-[11px] font-semibold uppercase tracking-wider transition-colors ${
                activeTab === 'resultados' && shown
                  ? 'bg-slate-800 text-slate-100 border border-slate-600'
                  : !shown
                  ? 'text-slate-700 cursor-not-allowed'
                  : 'text-slate-500 hover:text-slate-300'
              }`}
            >
              Resultados y Gráficas
              {shown && (
                <span className="ml-1.5 w-1.5 h-1.5 rounded-full bg-blue-400 inline-block" />
              )}
            </button>
          </div>

          {notice && (
            <div className="flex items-center gap-2 px-3 py-2 bg-blue-950 border-b border-blue-900 text-[11px] text-blue-300 flex-shrink-0">
              <span className="flex-1">{notice}</span>
              {activeTab === 'formulario' && (
                <button onClick={() => setActiveTab('resultados')} className="underline hover:text-blue-100">Ver</button>
              )}
              <button onClick={dismissNotice} aria-label="Cerrar aviso" className="hover:text-blue-100">✕</button>
            </div>
          )}          

          {/* Contenido del carrusel */}
          <div className="flex-1 overflow-y-auto">

            {/* TAB: FORMULARIO */}
            {activeTab === 'formulario' && (
              <div className="p-4">
                {/* Instrucciones */}
                <div className="flex items-start gap-2 bg-slate-800 border border-slate-700 rounded-lg p-3 mb-4">
                  <svg className="w-4 h-4 text-blue-400 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 24 24">
                    <path fillRule="evenodd" d="M2.25 12c0-5.385 4.365-9.75 9.75-9.75s9.75 4.365 9.75 9.75-4.365 9.75-9.75 9.75S2.25 17.385 2.25 12zm8.706-1.442c1.146-.573 2.437.463 2.126 1.732l-1.178 4.814a1.5 1.5 0 01-2.887.323c-1.146-.573-2.437-.463-2.126-1.732l1.178-4.814a1.5 1.5 0 012.887-.323zM12 9a1.5 1.5 0 100-3 1.5 1.5 0 000 3z" clipRule="evenodd" />
                  </svg>
                  <div>
                    <p className="text-[11px] font-semibold text-slate-300">Diseño de Mezcla</p>
                    <p className="text-[11px] text-slate-500 mt-0.5 leading-relaxed">
                      Para que el sistema infiera con precisión la resistencia de la mezcla, las cantidades ingresadas deben corresponder a las proporciones de diseño para{' '}
                      <span className="text-blue-400 font-medium">un metro cúbico (1 m³)</span> de concreto.
                    </p>
                  </div>
                </div>

                {/* Grid de inputs */}
                <form onSubmit={handleFormSubmit} className="grid grid-cols-2 gap-3">
                  <NumberInputDark label="Cemento (kg/m³)"           name="cement"           value={form.cement}          onChange={handleChange} disabled={isLocked} hasError={camposError.includes('cement')} />
                  <NumberInputDark label="Escoria (kg/m³)"            name="slag"             value={form.slag}            onChange={handleChange} disabled={isLocked} hasError={camposError.includes('slag')} />
                  <NumberInputDark label="Ceniza Volante (kg/m³)"     name="flyash"           value={form.flyash}          onChange={handleChange} disabled={isLocked} hasError={camposError.includes('flyash')} />
                  <NumberInputDark label="Agua (kg/m³)"               name="water"            value={form.water}           onChange={handleChange} disabled={isLocked} hasError={camposError.includes('water')} />
                  <NumberInputDark label="Superplastificante (kg/m³)" name="superplasticizer" value={form.superplasticizer} onChange={handleChange} disabled={isLocked} hasError={camposError.includes('superplasticizer')} step={0.1} />
                  <NumberInputDark label="Ag. Grueso (kg/m³)"         name="coarseaggregate"  value={form.coarseaggregate} onChange={handleChange} disabled={isLocked} hasError={camposError.includes('coarseaggregate')} />
                  <NumberInputDark label="Ag. Fino (kg/m³)"           name="fineaggregate"    value={form.fineaggregate}   onChange={handleChange} disabled={isLocked} hasError={camposError.includes('fineaggregate')} />
                  <NumberInputDark label="Edad (días)"                name="age"              value={form.age}             onChange={handleChange} disabled={isLocked} hasError={camposError.includes('age')} />

                  <div className="col-span-2 mt-2">
                    <button
                      type="submit"
                      disabled={loading || isLocked}
                      className="w-full bg-blue-600 hover:bg-blue-500 disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold py-3 rounded-lg transition-colors flex items-center justify-center gap-2 text-[13px]"
                    >
                      {loading ? (
                        <>
                          <svg className="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/>
                            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
                          </svg>
                          Calculando...
                        </>
                      ) : isLocked ? (
                        <>
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7"/>
                          </svg>
                          Inferencia completada
                        </>
                      ) : (
                        <>
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z"/>
                          </svg>
                          Ejecutar Inferencia
                        </>
                      )}
                    </button>
                  </div>
                </form>

                {/* Error */}
                {error && (
                  <div className="mt-3 p-3 bg-red-950 border border-red-800 text-red-400 rounded-lg text-[11px]">
                    <p className="font-semibold">Error</p>
                    <p className="mt-0.5">{error}</p>
                  </div>
                )}
              </div>
            )}

            {/* TAB: RESULTADOS + GRÁFICAS */}
            {activeTab === 'resultados' && shown && (
              <div ref={resultsRef} className="p-4 space-y-4">
                <MixSelector mixes={mixes} activeId={shown.id} onSelect={selectMix} />
                <PredictionResultDark resultado={shown.result} />
                <MixCompositionCardDark data={shownPie} age={Number(shown.inputs.age)} />
                <AbramsCurveCardDark
                  ratio={shown.result.relacion_agua_cemento}
                  strength={shown.result.resistencia_estimada}
                />
                {shown.result.shap_contributions?.length > 0 && (
                  <SHAPContributionCardDark
                    shap_base_value={shown.result.shap_base_value}
                    shap_contributions={shown.result.shap_contributions}
                  />
                )}
                {/* Botones de acción */}
                <div className="flex gap-3 pt-2">
                  <button
                    onClick={handleFormReset}
                    className="flex-1 bg-slate-700 hover:bg-slate-600 text-slate-200 font-semibold py-3 rounded-lg transition-colors text-[12px] flex items-center justify-center gap-2"
                  >
                    <span>↺</span> Nuevo Diseño
                  </button>
                  <button
                    onClick={openModal}
                    className="flex-1 bg-red-600 hover:bg-red-500 text-white font-semibold py-3 rounded-lg transition-colors text-[12px] flex items-center justify-center gap-2"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
                    </svg>
                    Reporte PDF
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* ====================================================
            COLUMNA DERECHA — Copiloto IA
            ==================================================== */}
        <CopilotChat
          messages={messages}
          input={input}
          setInput={setInput}
          isLoading={agentLoading}
          lastReport={lastReport}
          bottomRef={bottomRef}
          sendUserMessage={sendUserMessage}
          stopGeneration={stopGeneration}
          confirmAnalysis={confirmAnalysis}
          declineAnalysis={declineAnalysis}
          handleKeyDown={handleKeyDown}
          privacy={privacy}
        />

      </div>

      {/* Modal de validación — fuera del grid para que flote correctamente */}
      <ValidationModal
        isOpen={isModalOpen}
        onClose={closeModal}
        value={realStrength}
        onChange={handleExperimentalChange}
        predictedValue={shown?.result.resistencia_estimada || 0}
        predictionClass={shown?.result.clase_resistencia || ''}
        onConfirm={async () => {
          try {
            if (!printRef.current) return;
            const canvas = await html2canvas(printRef.current, { scale: 2, windowWidth: 1200, width: 800 });
            
            let shapBase64: string | undefined;
            if (shapRef.current) {
              const shapCanvas = await html2canvas(shapRef.current, { scale: 2, windowWidth: 1200, width: 800 });
              shapBase64 = shapCanvas.toDataURL('image/png');
            }
            await confirmPdfGeneration(canvas.toDataURL('image/png'), undefined, shapBase64, shown ?? undefined);   // onConfirm
            await confirmPdfGeneration(canvas.toDataURL('image/png'), '0', shapBase64, shown ?? undefined);          // onSkip
          } catch (err) { console.error('Error capturando gráficas:', err); }
        }}
        onSkip={async () => {
          try {
            if (!printRef.current) return;
            handleExperimentalChange('0');
            const canvas = await html2canvas(printRef.current, { scale: 2, windowWidth: 1200, width: 800 });
            
            // Capturar SHAP igual que en onConfirm
            let shapBase64: string | undefined;
            if (shapRef.current) {
              const shapCanvas = await html2canvas(shapRef.current, { scale: 2, windowWidth: 1200, width: 800 });
              shapBase64 = shapCanvas.toDataURL('image/png');
            }
            await confirmPdfGeneration(canvas.toDataURL('image/png'), '0', shapBase64);
          } catch (err) { console.error('Error capturando gráficas:', err); }
        }}
      />

      {/* Contenedor oculto para captura PDF */}
      {shown && (
        <>
          <div ref={printRef} className="absolute -left-[9999px] w-[800px] bg-white">
            <MixCompositionCard data={shownPie} age={Number(shown.inputs.age)} isPdf={true} />
            <AbramsCurveCard ratio={shown.result.relacion_agua_cemento} strength={shown.result.resistencia_estimada} />
          </div>
          {shown.result.shap_contributions?.length > 0 && (
            <div ref={shapRef} className="absolute -left-[9999px] w-[800px] bg-white p-8">
              <SHAPContributionCard
                shap_base_value={shown.result.shap_base_value}
                shap_contributions={shown.result.shap_contributions}
              />
            </div>
          )}
        </>
      )}
    </div>
  );
}
