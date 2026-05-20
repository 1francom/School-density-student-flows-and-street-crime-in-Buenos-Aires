# Micro-Place: School Density, Student Flows, and Street Crime in Buenos Aires

Repositorio de la Bachelor Thesis de Franco Medero para la Ludwig-Maximilians-Universitat Munchen, Applied Economics Group.

## Descripcion

Este proyecto estudia si los flujos diarios de estudiantes alrededor de las escuelas ayudan a predecir la distribucion micro-espacial del crimen callejero en la Ciudad Autonoma de Buenos Aires (CABA), y si una intervencion de guardiania dirigida puede reducir ese crimen.

La tesis combina datos abiertos de crimen, escuelas, transporte, comisarias, uso del suelo y caracteristicas censales con una grilla espacial de CABA. La unidad principal de analisis es una celda de 500 x 500 metros, con ejercicios de robustez en grillas de 300 x 300 metros. El trabajo estima modelos Poisson con efectos fijos de grilla y fecha para explotar variacion dentro del dia en horarios escolares, y complementa el analisis con un event study tipo Sun-Abraham para evaluar el programa Senderos Escolares.

La pregunta central es si las escuelas funcionan como anclas de actividad que modifican el riesgo de crimen en horarios especificos. El marco conceptual distingue tres canales: incapacitation, porque los estudiantes estan dentro de la escuela durante las horas de clase; opportunity, porque la entrada y salida concentran potenciales victimas en corredores peatonales; y guardianship, porque adultos, agentes y supervision informal pueden reducir oportunidades delictivas.

## Principales hallazgos

- En horarios de entrada, las celdas ubicadas cerca de escuelas muestran menores robos respecto de zonas mas alejadas, consistente con un canal de guardiania.
- En la salida del mediodia, el gradiente se revierte y las zonas cercanas a escuelas registran mas crimen, consistente con concentracion de objetivos y congestion peatonal.
- La densidad agregada de escuelas dentro de una celda tiene efectos debiles; la proximidad a la escuela mas cercana parece ser mas importante que el numero total de escuelas.
- El programa Senderos Escolares muestra reducciones de crimen post-tratamiento concentradas en el primer ano de implementacion, principalmente asociadas a agentes de prevencion.
- Los tests placebo nocturnos y los ejercicios de desplazamiento no muestran evidencia fuerte de efectos espurios o desplazamiento sistematico a zonas adyacentes.

## Estructura del repositorio

- `Data preparation _oficial.R`: limpieza y preparacion de datos espaciales, construccion de grillas, variables de escuelas, crimen, transporte, policia, uso del suelo y censo.
- `Regressions_2016.R`: modelos principales para 2016, gradientes espaciales, especificaciones por franja horaria y controles.
- `Event_study.R`: event study para Senderos Escolares con estimador Sun-Abraham, cohortes de tratamiento, slots horarios e intensidad de guardiania.
- `graphs and plots.R`: mapas y visualizaciones espaciales.
- `Summary statistics.R`: estadisticas descriptivas y tablas de resumen.
- `tables/`: tablas LaTeX generadas para la tesis.
- `plots/`: figuras exportadas en PDF y PNG.
- `output_latex/`: tablas y figuras listas para integracion en LaTeX.
- `*.csv`, `*.rds`, `*.shp`, `*.shx`, `*.xlsx`: datos crudos, intermedios y procesados usados por los scripts.
- `BA definitivo.pdf`: version final de la Bachelor Thesis.

## Datos y fuentes

Los datos provienen principalmente de Buenos Aires Data y fuentes oficiales de la Ciudad de Buenos Aires. El repositorio incluye insumos y objetos procesados para facilitar la reproduccion del analisis:

- Mapa del Delito para robos, hurtos y otros crimenes georreferenciados.
- Establecimientos educativos con coordenadas, sector y nivel.
- Senderos Escolares y rutas de prevencion.
- Paradas de colectivo, comisarias y divisiones policiales.
- Uso del suelo, radios censales, barrios, comunas y perimetro de CABA.

## Requisitos

El analisis esta escrito en R. Los paquetes principales utilizados son:

- `dplyr`
- `tidyverse`
- `sf`
- `fixest`
- `ggplot2`
- `lubridate`
- `readr`
- `readxl`
- `writexl`
- `broom`
- `knitr`
- `units`

## Reproduccion

Los scripts originales usan rutas absolutas locales mediante `setwd()`. Para correr el proyecto en otra maquina, ajustar esas rutas al directorio donde se clone el repositorio.

Orden sugerido:

1. Ejecutar `Data preparation _oficial.R` para generar los objetos espaciales y paneles base.
2. Ejecutar `Regressions_2016.R` para estimar los modelos principales.
3. Ejecutar `Event_study.R` para reproducir el analisis de Senderos Escolares.
4. Ejecutar `graphs and plots.R` y `Summary statistics.R` para regenerar figuras y tablas.

## Archivos grandes

El repositorio esta preparado para Git LFS porque algunos datos superan el limite normal de GitHub para archivos grandes. Antes de clonar o empujar cambios con datos pesados, instalar Git LFS y ejecutar:

```bash
git lfs install
```

## Cita sugerida

Medero, Franco. 2026. "Micro-Place: School Density, Student Flows, and Street Crime in Buenos Aires." Bachelor Thesis, Ludwig-Maximilians-Universitat Munchen.
