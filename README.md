# HMI Industrial — Robot PAROL6 (6 GDL)

Interfaz Hombre-Máquina (HMI) para la simulación y control cinemático del robot manipulador **PAROL6** de 6 grados de libertad, desarrollada como proyecto académico en la **Universidad Tecnológica de Pereira**.

---

## Descripción

Esta aplicación permite simular, controlar y analizar el robot PAROL6 en tiempo real mediante un entorno gráfico intuitivo. Integra simulación física con PyBullet, visualización 3D con Matplotlib y generación automática de reportes en PDF con análisis cinemático completo.

---

## Características Principales

- **Control Manual Directo**: Sliders por articulación para mover cada uno de los 6 motores en tiempo real (en radianes).
- **Ir a Pose Manual (3 pasos + PDF)**: Define una pose objetivo articular y el robot viaja hasta ella generando automáticamente un reporte PDF con 3 puntos de muestreo.
- **Trayectorias Automáticas Predefinidas**:
  - Trayectoria 1: Pick & Place
  - Trayectoria 2: Inspección
  - Trayectoria 3: Esquivar
- **Cinemática Directa en Tiempo Real**: Visualización de la matriz de transformación homogénea T (4×4) y la matriz de rotación R (3×3) con ángulos de Euler ZYX.
- **Reconstrucción 3D Matricial**: Trayectoria del TCP (Tool Center Point) graficada en el panel derecho.
- **Barras de Protección Mecánica**: Indicadores visuales de límites articulares con alertas de color.
- **Generación de Reportes PDF**: Reportes automáticos con imágenes del simulador, wireframe analítico y matrices cinemáticas por cada trayectoria ejecutada.

---

## Estructura del Proyecto

```
HMI-PAROL6/
├── main.py                    # Punto de entrada principal para ejecutar la HMI
├── utils.py                   # Funciones utilitarias (manejo de recursos, iconos y rutas)
├── PAROL6.urdf                # Archivo de descripción estructural y cinemática del robot
├── README.md                  # Documentación y guía del proyecto para el usuario en GitHub
├── requirements.txt           # Lista de librerías y dependencias necesarias para el entorno
├── HMI_PAROL6.spec            # Especificaciones de empaquetado para generar el ejecutable (.exe)
├── Manual_HMI_PAROL6.pdf      # Manual de usuario oficial enlazado a la nube
├── brazo-robotico.ico         # Icono personalizado de la interfaz de usuario
├── Logo_UTP.png               # Logotipo institucional de la Universidad Tecnológica de Pereira
├── gseea.png                  # Logotipo del grupo de investigación GIGSEEA
│
├── control/
│   ├── __init__.py            # Inicializador del módulo de control
│   └── controller.py          # Controlador de articulaciones en modos Manual y Automático
│
├── meshes/
│   ├── base_link.STL          # Malla tridimensional de la estructura base del robot
│   ├── L1.STL                 # Malla 3D del Eslabón 1 (Eje articular 1)
│   ├── L2.STL                 # Malla 3D del Eslabón 2 (Eje articular 2)
│   ├── L3.STL                 # Malla 3D del Eslabón 3 (Eje articular 3)
│   ├── L4.STL                 # Malla 3D del Eslabón 4 (Eje articular 4)
│   ├── L5.STL                 # Malla 3D del Eslabón 5 (Eje articular 5)
│   └── L6.STL                 # Malla 3D del Eslabón 6 (Eje articular 6 - TCP)
│
├── reports/
│   ├── __init__.py            # Inicializador del módulo de reportes
│   └── pdf_report.py          # Generador de reportes técnicos con datos cinemáticos en PDF
│
├── robot/
│   ├── __init__.py            # Inicializador del módulo del robot
│   ├── kinematics.py          # Algoritmos y transformaciones de cinemática directa e inversa
│   └── simulation.py          # Simulación del entorno físico y visualización con PyBullet
│
├── trajectories/
│   ├── __init__.py            # Inicializador del módulo de trayectorias
│   └── generator.py           # Planificación, cálculo e interpolación de trayectorias
│
├── ui/
│   ├── __init__.py            # Inicializador del módulo de interfaz gráfica
│   ├── left_panel.py          # Panel izquierdo (control articular, sliders y logos)
│   ├── main_window.py         # Ventana principal que acopla todos los componentes de la HMI
│   └── right_panel.py         # Panel derecho (monitoreo de matrices, gráficas y control automático)
│
└── visualization/
    ├── __init__.py            # Inicializador del módulo de visualización
    ├── canvas3d.py            # Lienzo 3D integrado de Matplotlib para rastreo del espacio de trabajo
    ├── visua.py               # Módulo complementario de apoyo para el renderizado visual
    └── wireframe.py           # Renderizado geométrico analítico del esqueleto del manipulador
```

---

## Requisitos

- Python 3.9 – 3.11 (recomendado 3.11)
- Sistema Operativo: Windows 10/11 (64 bits)
- Procesador: Intel Core i3 @ 2.3GHz (o equivalente)
- Memoria RAM: 8 GB mínimo
- Espacio libre en disco: 500 MB
- Tarjeta gráfica con soporte OpenGL para PyBullet por hardware
- Visor de archivos PDF

### Dependencias

```
PyQt5>=5.15.0
numpy>=1.21.0
pybullet>=3.2.5
matplotlib>=3.5.0
```

---

## Instalación y Ejecución

### 1. Clonar o descargar el repositorio

```bash
git clone <url-del-repositorio>
cd ACOFI
```

### 2. Crear entorno virtual (recomendado)

```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Ejecutar la aplicación

```bash
python main.py
```

---

## Uso del Ejecutable (.exe)

Si dispone del archivo `HMI_PAROL6.exe`, simplemente ejecútelo con doble clic. No requiere instalación de Python ni librerías adicionales.

> **Nota**: El ejecutable debe estar en la misma carpeta que los archivos `PAROL6.urdf`, `Logo_UTP.png`, `gseea.png` y la carpeta `meshes/`.

---

## Ejemplos de Uso

### Control Manual
1. Mueva los sliders del panel izquierdo para posicionar cada articulación.
2. Observe la posición del robot en el visor central y las matrices en el panel derecho.

### Trayectoria Automática con Reporte
1. Haga clic en uno de los botones de trayectoria del panel derecho.
2. El robot ejecutará la trayectoria en 3 poses de muestreo.
3. Al finalizar, se generará automáticamente un archivo PDF en el directorio de trabajo.

### Pose Manual con PDF
1. Ingrese los valores articulares deseados (en radianes) en los campos del panel izquierdo.
2. Haga clic en **"VIAJAR A ESTA POSE (PDF)"**.
3. El robot viajará en 3 etapas y generará el reporte PDF.

---

## Autores

| Nombre | Rol |
|--------|-----|
| Elias Escobar Pereira | Desarrollo principal |
| Kevin David Ortega Quiñones | Colaborador |
| Daniela Buitrago Largo | Colaboradora |
| Mauricio Holguín Londoño | Colaborador |
| German Andres Holguín Londoño | Colaborador |

---

## Institución

**Universidad Tecnológica de Pereira**  
Facultad de Ingenierías
Ingenieria Eléctrica  
Grupo de Investigación: **GIGSEEA** — Grupo de Investigación en Gestión de Sistemas Eléctricos, Electrónicos y Automáticos

---

## Licencia

Proyecto académico — Universidad Tecnológica de Pereira.

Este proyecto es un trabajo derivado que utiliza como base el repositorio oficial del brazo robótico **[PAROL6](https://github.com/PCrnjak/PAROL6-Desktop-robot-arm)**, creado por Petar Crnjak.

En cumplimiento con los términos de la licencia original del autor, este software y sus modificaciones se distribuyen bajo la licencia de código abierto **GNU General Public License v3 (GPLv3)**. 

* © 2026 Autores del proyecto académico (Universidad Tecnológica de Pereira). Algunos derechos reservados bajo los términos copyleft de la GPLv3.
* Puedes consultar los términos legales completos en el archivo `LICENSE` adjunto en este repositorio directamente en el [Aviso de Licencia original de PAROL6](https://github.com/PCrnjak/PAROL6-Desktop-robot-arm/blob/main/LICENSE).
