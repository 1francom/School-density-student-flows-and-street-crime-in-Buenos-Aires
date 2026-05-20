# Micro-Place: School Density, Student Flows, and Street Crime in Buenos Aires

Repository for Franco Medero's Bachelor Thesis at Ludwig-Maximilians-Universitat Munchen, Applied Economics Group.

## Overview

This project studies whether daily student flows around schools help predict the micro-spatial distribution of street crime in the City of Buenos Aires (CABA), and whether targeted guardianship can reduce that crime.

The thesis combines open data on crime, schools, public transport, police stations, land use, and census characteristics with a spatial grid covering CABA. The main unit of analysis is a 500 x 500 meter grid cell, with robustness checks using a finer 300 x 300 meter grid. The empirical strategy estimates Poisson fixed-effects models with grid and date fixed effects, exploiting within-day variation around school entry and dismissal windows. The analysis is complemented by a Sun-Abraham event study evaluating the Senderos Escolares program.

The central question is whether schools act as routine-activity anchors that change crime risk at specific times of the day. The conceptual framework separates three mechanisms: incapacitation, because students are inside school during instructional hours; opportunity, because school entry and dismissal concentrate potential targets along pedestrian corridors; and guardianship, because adults, prevention agents, and informal supervision may reduce criminal opportunities.

## Main Findings

- During school entry hours, grid cells close to schools record lower robbery counts than cells farther away, consistent with a guardianship mechanism.
- Around midday dismissal, the gradient reverses: areas close to schools record higher crime, consistent with target concentration and pedestrian congestion.
- Aggregate school density within a grid cell has weak effects; proximity to the nearest school appears more relevant than the total number of schools.
- The Senderos Escolares program is associated with post-treatment crime reductions concentrated in the first year of implementation, mainly linked to prevention agents.
- Night-hour placebo tests and displacement exercises provide little evidence of spurious effects or systematic crime displacement to adjacent areas.

## Repository Structure

- `Data preparation _oficial.R`: data cleaning and spatial preparation, including grid construction and variables for schools, crime, transport, police presence, land use, and census characteristics.
- `Regressions_2016.R`: main 2016 models, spatial gradients, time-slot specifications, and control variables.
- `Event_study.R`: Senderos Escolares event study using a Sun-Abraham estimator, treatment cohorts, time slots, and guardianship intensity.
- `graphs and plots.R`: spatial maps and visualizations.
- `Summary statistics.R`: descriptive statistics and summary tables.
- `tables/`: LaTeX tables generated for the thesis.
- `plots/`: exported figures in PDF and PNG format.
- `output_latex/`: figures and tables prepared for LaTeX integration.
- `*.csv`, `*.rds`, `*.shp`, `*.shx`, `*.xlsx`: raw, intermediate, and processed data used by the scripts.
- `BA definitivo.pdf`: final version of the Bachelor Thesis.

## Data Sources

The data mainly come from Buenos Aires Data and official sources from the City of Buenos Aires. The repository includes inputs and processed objects used to reproduce the analysis:

- Mapa del Delito for georeferenced robberies, thefts, and other crimes.
- Educational establishments with coordinates, sector, and school level.
- Senderos Escolares routes and prevention corridors.
- Bus stops, police stations, and police district divisions.
- Land use, census tracts, neighborhoods, communes, and the CABA boundary.

## Requirements

The analysis is written in R. The main packages used are:

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

## Reproducibility

The original scripts use local absolute paths through `setwd()`. To run the project on another machine, update those paths to the directory where the repository is cloned.

Suggested order:

1. Run `Data preparation _oficial.R` to generate the spatial objects and base panels.
2. Run `Regressions_2016.R` to estimate the main models.
3. Run `Event_study.R` to reproduce the Senderos Escolares analysis.
4. Run `graphs and plots.R` and `Summary statistics.R` to regenerate figures and tables.

## Large Files

This repository is configured for Git LFS because several data files exceed GitHub's standard file-size limits. Before cloning or pushing changes involving large data files, install Git LFS and run:

```bash
git lfs install
```

## Suggested Citation

Medero, Franco. 2026. "Micro-Place: School Density, Student Flows, and Street Crime in Buenos Aires." Bachelor Thesis, Ludwig-Maximilians-Universitat Munchen.
