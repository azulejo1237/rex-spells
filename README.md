# Rex Spells

<div align="center">
  
![Rex Spells Logo](https://img.shields.io/badge/Rex%20Spells-v1.0.0-brightgreen)
![Platform](https://img.shields.io/badge/Platform-Windows%2010%2F11-blue)
![License](https://img.shields.io/badge/License-MIT-yellow)

**Overlay para League of Legends que muestra los hechizos de invocador de los campeones enemigos con temporizadores en tiempo real**

[📥 Descargar](#-descarga) • [⚙️ Instalación](#%EF%B8%8F-instalación) • [🎮 Uso](#-uso) • [📋 Requisitos](#-requisitos)

</div>

## 🖼️ Capturas de Pantalla

<div align="center">

### Interfaz Principal
<img src="https://github.com/user-attachments/assets/918a2d92-ce45-401e-8f0b-e608d8e1c58b" alt="Rex spells interfaz principal" width="400"/>

*Vista del overlay en funcionamiento mostrando los hechizos enemigos*

### Funciones Principales

<p align="center">
<img src="https://github.com/user-attachments/assets/5d998fe3-8df5-4370-9c84-e240dedaf8a2" alt="Rex spells panel flotante" width="145"/>
</p>

<p align="center">
<em>Overlay activo con temporizadores</em>
</p>

<p align="center">
<img src="https://github.com/user-attachments/assets/d81b2ebf-e41e-495d-81ee-912441bce328" alt="Rex spells configuración" width="380"/>
</p>

<p align="center">
<em>Panel de configuració</em>
</p>

<p align="center">
<img src="https://github.com/user-attachments/assets/4c204701-e9be-4bf4-93e4-d07898d395e3" alt="Rex spells estados" width="460"/>
</p>

<p align="center">
<em>Diferentes estados del overlay</em>
</p>

</div>

## 📖 Descripción

Rex Spells es una aplicación overlay para League of Legends que te permite rastrear los hechizos de invocador enemigos de forma visual y eficiente. Utilizando la API local del cliente de League of Legends, la aplicación muestra los campeones enemigos con sus dos hechizos de invocador y permite iniciar temporizadores con un simple clic.

## ✨ Características

- 🎯 **Visualización de campeones enemigos** con sus dos hechizos de invocador
- ⏱️ **Sistema de temporizadores** - Haz clic sobre un hechizo para iniciar o limpiar su temporizador
- 🪟 **Panel flotante siempre visible** con funcionalidades de:
  - Bloqueo/desbloqueo de arrastre
  - Colapsar/expandir
  - Ajuste de opacidad
- 🔔 **Icono en bandeja del sistema** con acciones rápidas (Mostrar/Ocultar y Salir)
- 🚀 **Sondeo adaptativo** - Rápido durante la partida, lento fuera de partida para optimizar recursos

## 📋 Requisitos

- **Sistema Operativo**: Windows 10/11
- **League of Legends** ejecutándose con la API local liveclientdata disponible en `127.0.0.1:2999`
- **Modo de visualización**: Para captura fiable del overlay, usar:
  - Modo ventana
  - Pantalla completa sin bordes

> ⚠️ **Nota**: No funciona en modo pantalla completa exclusiva debido a limitaciones de Windows.

## 📥 Descarga

Ve a la sección [**Releases**](https://github.com/azulejo1237/rex-spells/releases) del repositorio y descarga la última versión del ejecutable.

- ✅ **Sin instalación requerida** - Se ejecuta como aplicación de escritorio
- 📦 **Archivo único** - Todo incluido en el ejecutable

## ⚙️ Instalación

1. Descarga el archivo `rex-spells.exe` desde [Releases](https://github.com/azulejo1237/rex-spells/releases)
2. Coloca el archivo en la carpeta de tu preferencia
3. Ejecuta `rex-spells.exe` - ¡Listo para usar!

## 🎮 Uso

### Configuración Inicial
1. Ejecuta Rex Spells
2. Inicia League of Legends
3. Coloca el panel donde prefieras en tu pantalla

### Controles del Panel
- **⚙️ Engranaje**: Abrir configuración
- **➖ Guión**: Colapsar/expandir panel
- **🔒 Candado**: Bloquear/permitir arrastre del panel

### Icono de Bandeja
Desde el icono en la bandeja del sistema puedes:
- 👁️ **Mostrar/Ocultar** rápidamente la aplicación
- ❌ **Salir** de la aplicación

### Funcionamiento
- Los **hechizos aparecen automáticamente** cuando entras en una partida
- **Haz clic** en cualquier hechizo para activar su temporizador de enfriamiento
- El **temporizador se muestra en tiempo real** sobre el hechizo
- **Haz clic nuevamente** para limpiar el temporizador

## ⚠️ Limitaciones Conocidas

### Modo Pantalla Completa
- **Problema**: Debe usarse en modo ventana o sin bordes
- **Razón**: En pantalla completa exclusiva, el juego toma control exclusivo de la salida gráfica
- **Solución**: Usar modo ventana o pantalla completa sin bordes en League of Legends

### Cambio de Cursor
- **Problema**: El cursor del juego se sustituye por el cursor de Windows tras hacer clic
- **Razón**: Al hacer clic, el overlay recibe el foco y Windows restaura el cursor del sistema
- **Solución**: Mover el mouse sobre cualquier entidad del juego o realizar Alt+Tab breve

### Icono Fantasma
- **Problema**: Puede quedar un icono residual en la bandeja tras cierres anómalos
- **Razón**: El sistema cachea iconos si la aplicación no notifica su retirada
- **Mitigación**: El programa limpia automáticamente al salir normal

## 🔒 Privacidad y Seguridad

- ✅ **Solo lectura local**: La aplicación únicamente lee la API local del cliente en `127.0.0.1`
- ✅ **Sin datos externos**: No envía información a terceros
- ✅ **No intrusivo**: No modifica archivos del juego ni inyecta código
- ✅ **Seguro**: Cumple con los términos de servicio de Riot Games

## 🛠️ Tecnologías

- **Python** - Lenguaje principal
- **Tkinter** - Interfaz gráfica
- **Requests** - Comunicación con API
- **Threading** - Procesamiento asíncrono
- **PyInstaller** - Empaquetado de ejecutable

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Haz un Fork del proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Consulta el archivo [LICENSE](LICENSE) para más detalles.

## 🏆 Créditos

Proyecto creado íntegramente con asistencia de IA, con ediciones y pruebas manuales para integración y empaquetado.

---

<div align="center">

**¿Te gustó Rex Spells? ¡Dale una ⭐ al repositorio!**

[🐛 Reportar Bug](https://github.com/azulejo1237/rex-spells/issues) • [💡 Solicitar Feature](https://github.com/azulejo1237/rex-spells/issues)

</div>
