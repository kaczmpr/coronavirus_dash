# Coronavirus dashboard

This project uses data about coronavirus pandemic from two sources to create a dashboard 
for data analysis

## Sources

* https://restcountries.eu/rest/v2/all
* https://en.wikipedia.org/wiki/2020_coronavirus_pandemic_in_Poland

## Demo
![Coronavirus dashboard - Animated gif demo](demo/demo.gif)
## Run Project Locally

To run the project locally:
* Clone or fork this repository
* Install docker on your machine
* Go to repository directory and build image: `docker build -t username/imagename`
* Run docker image: `docker run -p 8050:8050 username/imagename`

## Comments

Unfortunately wikipedia html source sometimes changing data structure and if `extractor.py` return 
errors then you should check function `get_poland_data()` especially following lines:
* `df_total = pd.read_html(URL_POLAND, header=0)[9]`
* `df_cases = pd.read_html(URL_POLAND, header=0)[10]`
* `df_deaths = pd.read_html(URL_POLAND, header=0)[11]`
