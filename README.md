# COVID-19: data, charts and interpretations in Europe
I worked on COVID-19 (Coronavirus) to see how it spreads around the world. I built charts and collected data, built dashboards and interpretations...

You can see how the virus spreads in France, Luxembourg, Spain, Belgium, United Kingdom (UK) compared to Italy and China.
# All charts
Confirmed cases of COVID-19
* [PNG](https://raw.githubusercontent.com/rozierguillaume/covid-19/master/images/charts/cases.png) - Confirmed cases over time
••This chart represents the total number of confirmed cases of COVID-19 against time, in days).
* [PNG](https://raw.githubusercontent.com/rozierguillaume/covid-19/master/images/charts/cases_since.png) - Confirmed cases over time [since a treschold]
* [PNG](https://raw.githubusercontent.com/rozierguillaume/covid-19/master/images/charts/cases_per_1m_inhabitant.png) - Confirmed cases for 1 million inhabitants over time
* [PNG](https://raw.githubusercontent.com/rozierguillaume/covid-19/master/images/charts/cases_per_1m_inhabitant_aligned.png) - Confirmed cases for 1 million inhabitants over time [aligned]
* [PNG](https://raw.githubusercontent.com/rozierguillaume/covid-19/master/images/charts/cases_per_1m_inhabitant_since.png) - Confirmed cases for 1 million inhabitants over time [since a treschold]

Deaths caused by COVID-19
* [PNG](https://raw.githubusercontent.com/rozierguillaume/covid-19/master/images/charts/deaths.png) - Deaths over time
* [PNG](https://raw.githubusercontent.com/rozierguillaume/covid-19/master/images/charts/deaths_since.png) -  Deaths over time [since a treschold]
* [PNG](https://raw.githubusercontent.com/rozierguillaume/covid-19/master/images/charts/deaths_per_1m_inhabitant.png) -  Deaths for 1 million inhabitants over time
* [PNG](https://raw.githubusercontent.com/rozierguillaume/covid-19/master/images/charts/deaths_per_1m_inhabitant_aligned.png) -  Deaths for 1 million inhabitants over time [aligned]
* [PNG](https://raw.githubusercontent.com/rozierguillaume/covid-19/master/images/charts/deaths_per_1m_inhabitant_since.png) - Deaths for 1 million inhabitants over time [since a treschold]

# Few Charts
## Confirmed cases
### Total cases
![](./images/charts/cases.png)

### Total cases for 1 million inhabitants
That's simply the total number of cases over time for each countr divided by the total population of the country.
![](./images/charts/cases_per_1m_inhabitant.png)

### Total cases for 1 million inhabitants, aligned
Same chart, but every curve is aligned with Italy. That's an easier way to compare how fast the curves grow.  
![](./images/charts/cases_per_1m_inhabitant_aligned.png)

### Total cases for 1 million inhabitants, since "x cases/mill. hab."
![](./images/charts/cases_per_1m_inhabitant_since.png)

## Deaths
### Total deaths
![](./images/charts/deaths.png)

### Total deaths for 1 million inhabitants
That's simply the total number of deaths over time for each countr divided by the total population of the country.
![](./images/charts/deaths_per_1m_inhabitant.png)

### Total deaths for 1 million inhabitants, aligned
Same chart, but every curve is aligned with Italy. That's an easier way to compare how fast the curves grow.  
![](./images/charts/deaths_per_1m_inhabitant_aligned.png)

### Total deaths for 1 million inhabitants, since "x deaths/mill. hab."
![](./images/charts/deaths_per_1m_inhabitant_since.png)

## Dashboard (deprecated)
I will do a better one soon...
I created a [dashboard](https://plot.ly/dashboard/worldice:14/) where you can find 4 of the charts I generate. It is refreshed every 4 hours.

![](./images/dashboard.png)

## Data
You can find 2 datasets:
- Data downloaded from [CSSE](https://github.com/CSSEGISandData/COVID-19). Data come from WHO (World Health Organization).
- Personal data (added manually).

The two dataset are then merged into a more complete dataset.
