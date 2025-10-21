Rex spells
Overlay para League of Legends que muestra los hechizos de invocador de los campeones enemigos y permite marcarlos para ver su enfriamiento en tiempo real mediante la API local del cliente.

Vista rápida

![Rex spells muestra 1](https://github.com/user-attachments/assets/766d7521-3383-44a9-b2f1-29d39059d07a)
![Rex spells muestra 2](https://github.com/user-attachments/assets/d009137f-c8d9-42c9-900b-49e96c1a7d0c)
![Rex spells muestra 3](https://github.com/user-attachments/assets/76702698-92aa-4d21-b41a-4e3ca1cc997d)
![Rex spells muestra 4](https://github.com/user-attachments/assets/2be5fedd-3475-4b63-99fb-f58df139f294)

Características
Visualiza a los campeones enemigos con sus dos hechizos de invocador.

Haz clic sobre un hechizo para iniciar o limpiar su temporizador.

Panel flotante siempre visible, con bloqueo de arrastre, colapsar/expandir y ajuste de opacidad.

Icono único en la bandeja del sistema con acciones Mostrar/Ocultar y Salir.

Sondeo adaptativo: rápido durante la partida, lento fuera de partida para consumir menos recursos.

Requisitos
Windows 10/11.

Cliente de League of Legends ejecutándose con la API local liveclientdata disponible en 127.0.0.1:2999.

Para captura fiable del overlay, usar modo ventana o pantalla completa sin bordes en el juego.

Descarga
Ve a la sección Releases del repositorio y descarga el ejecutable más reciente.

No es necesario instalar; se ejecuta como una aplicación de escritorio.

Uso
Ejecuta Rex spells y coloca el panel donde prefieras.

Botones de la barra superior: engranaje (configurar), guion (colapsar), candado (bloquear o permitir arrastre).

Desde el icono de la bandeja puedes mostrar/ocultar rápidamente o salir.

Problemas conocidos y explicación técnica
Modo de pantalla obligatorio: debe usarse en ventana o sin bordes.

Razón: en pantalla completa exclusiva el juego toma control exclusivo de la salida gráfica y no muestra ventanas externas por encima, de modo que un overlay de escritorio no puede dibujarse de forma fiable sin inyección en el proceso del juego.

Decisión: se evita cualquier inyección o hooking por seguridad y para no violar términos del juego, por eso el requisito se mantiene.

Cambio del cursor tras hacer clic en el overlay: el cursor del juego se sustituye por el cursor de Windows hasta pasar el mouse por encima de un objeto del juego (torreta, súbdito, etc.).

Razón: al hacer clic, el overlay recibe el foco y Windows restaura el cursor del sistema; el cliente de LoL vuelve a aplicar su cursor personalizado cuando procesa movimiento sobre elementos de juego. Sin inyectar eventos sintéticos ni hooks globales de bajo nivel (que podrían ser riesgosos), no hay forma limpia de forzar esa restauración inmediata.

Solución actual: mover el mouse sobre cualquier entidad del juego o realizar un alt‑tab breve para que LoL recupere el foco y re‑aplique su cursor.

Estado: se deja así por diseño para priorizar compatibilidad y evitar técnicas intrusivas.

Icono fantasma en bandeja tras cierres anómalos.

Razón: el sistema puede cachear iconos si la aplicación no alcanza a notificar su retirada.

Mitigación: el programa oculta y destruye el icono al salir, pero si el proceso se cierra a la fuerza, el sistema puede tardar en limpiar el icono residual.

Disponibilidad de datos: fuera de partida la API local puede no responder.

Comportamiento: el overlay reduce la frecuencia de sondeo y limpia la UI tras varios intentos sin datos.

Privacidad y seguridad
La aplicación solo lee la API local del cliente en 127.0.0.1; no envía datos a terceros.

No modifica archivos del juego ni inyecta código en el proceso del cliente.

Créditos
Proyecto creado íntegramente con asistencia de IA, con ediciones y pruebas manuales para integración y empaquetado.

Licencia
MIT. Consulta el archivo LICENSE en la raíz del repositorio.
