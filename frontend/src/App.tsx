import FormularioConcreto from './components/forms/FormularioConcreto';
import Header from './components/layout/Header'; // <-- 1. IMPORTA TU NUEVO ENCABEZADO
import pkg from '../package.json';

function App() {
  return (
    // CONTENEDOR PRINCIPAL
    // Cambiamos el fondo a bg-slate-900 (gris muy oscuro) para que combine elegante con tu Header blanco
    // Quitamos los paddings de aquí para que el Header toque los bordes de la pantalla
    <div className="min-h-screen w-full bg-slate-900 flex flex-col">
      
      {/* 2. TU NUEVO ENCABEZADO ESTRELLA */}
      {/* Como está directo en el contenedor principal, abarcará el 100% del ancho arriba */}
      <Header />

      {/* CONTENEDOR DEL FORMULARIO Y FOOTER */}
      {/* flex-grow hace que este contenedor ocupe todo el espacio que sobra debajo del Header */}
      {/* Aquí volvemos a poner los paddings (py-12 px-4) para centrar el formulario */}
      <div className="flex-grow flex flex-col items-center py-12 px-4 sm:px-6 lg:px-8">
        
        {/* AQUÍ VA TU COMPONENTE ESTRELLA */}
        <main className="w-full max-w-4xl">
          <FormularioConcreto />
        </main>

        {/* FOOTER */}
        <footer className="mt-12 text-slate-400 text-xs text-center">
          <p>&copy; {new Date().getFullYear()} Civiltrónica • LIAI. v.{pkg.version}</p>
        </footer>

      </div>

    </div>
  );
}

export default App;