# scrapy-yelp
  This project is an implementation of a small parser written using the [scrapy](https://docs.scrapy.org/en/latest/index.html) module. Experiments were carried out on the [yelp](https://www.yelp.com/) website, in particular, the data was extracted from the business pages. The parser extracts a lot of useful information about businesses.
  In order to use this parser, just clone this repo for yourself, go to the directory 'yelp_parser' and run the command 
> scrapy parse https://www.yelp.com/biz/german-auto-sport-berkeley --spider=yelp -o german_auto_sport.json
