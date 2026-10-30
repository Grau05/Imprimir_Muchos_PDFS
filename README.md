# Imprimir_Muchos_PDFS

Aplicacion de escritorio para enviar varios archivos PDF a una impresora en Windows. Permite elegir una carpeta, configurar las opciones de impresion y enviar todos los documentos o solo los seleccionados.

## Requisitos

- Windows.
- Python 3 con Tkinter, incluido normalmente en las instalaciones oficiales de Python para Windows.
- SumatraPDF instalado o `SumatraPDF.exe` ubicado junto a `imprimir.py`.
- Una impresora instalada y configurada en Windows.

El programa busca SumatraPDF junto al script, en `%LOCALAPPDATA%\SumatraPDF` y en las carpetas habituales de `Program Files`. Las impresoras disponibles se obtienen mediante PowerShell (`Get-Printer`).

## Uso

1. Guarda `imprimir.py` en tu equipo.
2. Instala SumatraPDF si aun no esta instalado.
3. Abre una terminal en la carpeta del proyecto y ejecuta:

   ```powershell
   python .\imprimir.py
   ```

4. Pulsa **Carpeta…** y selecciona la carpeta que contiene los PDF.
5. Elige la impresora y configura las opciones necesarias.
6. Pulsa **Imprimir todos** o selecciona uno o mas documentos de la lista y pulsa **Imprimir seleccionados**. La aplicacion pide confirmacion antes de iniciar el trabajo.

## Opciones

- Buscar PDF en la carpeta seleccionada; activa **Incluir subcarpetas** para buscar tambien dentro de sus subcarpetas.
- Seleccionar impresora. Si hay impresoras disponibles, se preselecciona la primera cuyo nombre contiene "HP"; si no, se usa la primera de la lista.
- Definir color (predeterminado, color o blanco y negro), impresion a una o dos caras, papel (Carta, Oficio o A4), orientacion y escala.
- Indicar de 1 a 99 copias y, opcionalmente, un rango de paginas, por ejemplo `1-3,5`.
- Abrir **Preferencias / calidad…** para acceder a las preferencias del controlador de la impresora, donde pueden configurarse opciones como la calidad.

Los valores predeterminados dejan que la impresora determine los ajustes correspondientes. Los PDF se ordenan por nombre y se envian de uno en uno. La ventana muestra el progreso e informa si algun archivo no se pudo enviar.
