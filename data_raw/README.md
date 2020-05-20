# data_raw 
- Raw data without preprocessing goes here. 

### anomaly_periods.csv 
- Contains the anomaly periods detected for each agency, including the start and end date. 

      metadata:
          agency: acronym for the government agency
          start_date: identified starting date of the anomaly period
          end_date: identified ending date of the anomaly period
 Both dates are inclusive. 
 
### article_data.csv 
Contains newspaper articles from several sources, each of which mentions a government agency. 

      metadata:
          id:       id of the article
          source:   newspaper that wrote the article
          date:     date article was published
          title:    title of the article
          byline:   byline of the article
          story:    article text
          agencies: agency/agencies mentioned in the article
