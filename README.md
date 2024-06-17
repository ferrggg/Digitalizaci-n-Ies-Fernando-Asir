El presente documento detalla el diseño y desarrollo de una aplicación web des-
tinada a mejorar la gestión y comunicación dentro de una institución escolar, especı́fi-
camente el instituto IES Fernando Asir. La aplicación aborda necesidades como la
comunicación entre profesores y alumnos, la gestión de incidencias, el control de inven-
tario de recursos hardware, y la difusión de información relevante a través de un tablón
de anuncios. Se empleará tecnologı́a web moderna, incluyendo frameworks como Odoo
o Django, bases de datos PostgreSQL, y servicios en la nube de Amazon Web Services
(AWS).
Actualmente, la comunicación dentro del instituto presenta deficiencias, lo que
dificulta la resolución rápida de incidencias y la difusión de información relevante. Los
profesores enfrentan dificultades para reportar y resolver problemas, y la interacción
entre profesores y alumnos podrı́a mejorarse significativamente.
En este proyecto se enseñará a manejar un aplicativo web fusionado con un ERP
, gestión de usuarios , tickets , correos electrónico (smtp y imap) , gestión de eventos ,
gestión de DNS locales y gestionar un servidor web mediante Apache2.
Vamos a hacer del centro escolar algo mucho mas amigable y ameno para todos!

Los objetivos principales de este proyecto son:
  Mejorar la comunicación dentro de la institución escolar : Facilitando
  la interacción entre profesores, alumnos y personal técnico.
  Optimización: Optimizar la gestión de incidencias y el soporte técnico mediante
  un sistema centralizado de tickets.
  Control y gestión: Controlar y gestionar el inventario de recursos hardware de
  manera eficiente.
  Difusión : Facilitar la difusión de información relevante mediante un tablón de
  anuncios accesible para toda la comunidad escolar.

Las principales funciones de la aplicación incluyen:
  • Chat para profesores.
  • Gestión de incidencias para alumnos, profesores y departamento TIC.
  • Gestión de inventario para el personal técnico.
  • Tablón de anuncios para la publicación de información relevante.
Los requisitos técnicos incluyen:
  • Uso de PostgreSQL como gestor de base de datos.
  • LDAP para la gestión de usuarios.
  • Odoo o Django como frameworks de desarrollo web.
  • GLPI como gestor de tickets.
  • Un servidor de correos para poder recibir y enviar correos dentro de la
  organización.
  ◦ Usaremos el servidor de correos interno llamado Postfix.
  ◦ Un webmail para acceder a los correos llamado Roundcube.
