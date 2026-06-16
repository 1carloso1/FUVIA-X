import Header from './components/layout/Header';
import MainLayout from './components/layout/MainLayout';
import WarmupScreen from './components/layout/WarmupScreen';
import { useSystemWarmup } from './hooks/useSystemWarmup';
import pkg from '../package.json';

function App() {
  const warmup = useSystemWarmup();

  // Mostrar pantalla de carga mientras los servidores despiertan
  if (!warmup.ready) {
    return <WarmupScreen state={warmup} />;
  }

  return (
    <div className="min-h-screen w-full bg-slate-950 flex flex-col">

      <Header />

      <main className="flex-grow">
        <MainLayout />
      </main>

      <footer className="py-4 text-slate-600 text-[11px] text-center border-t border-slate-800">
        &copy; {new Date().getFullYear()} Civiltrónica · LIAI · v{pkg.version}
      </footer>

    </div>
  );
}

export default App;