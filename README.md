# scrapy-yelp
  This project is an implementation of a small parser written using the [scrapy](https://docs.scrapy.org/en/latest/index.html) module. Experiments were carried out on the [yelp](https://www.yelp.com/) website, in particular, the data was extracted from the business pages. The parser extracts a lot of useful information about businesses.
  In order to use this parser, just clone this repo for yourself, go to the directory 'yelp_parser' and run the command 
  
`scrapy parse https://www.yelp.com/biz/german-auto-sport-berkeley --spider=yelp -o german_auto_sport.json`

(don't forget to download required modules from requirements to your environment)

Instead of test web page, you can pick desirable one. But notice, that this parser is able only work with businesses pages, so links gonna look like preceding one. You can pick your own file name as well.

  Actually, this parser has some feature. It works not only with businesses pages, but also with yelp api to get some info about businesses. To allow parser working with api, you have to get key from yelp website(more info [here](https://www.yelp.com/developers/documentation/v3/authentication)), and put it into .env file in following format 
  
  `KEY = 'yourkeyhere'`
  
  (don't forget that using api is not required, parser can work without it. Just don't create .env file if you want)
  
  As the main idea of this project is parsing, using scrapy, the programm doesn't use api as the main source of information, it just compare data from api and data from page and take first one only in case, when site got big changes in the markup, so that there's no ability to parse something. But actually xpaths to elements were chosen consciously. Because of tags almost don't have any ids, most of elements are chosen by special key words on the site. Some of information is not available for scrapy, because it's not able to interpret javascript, so in some cases selenium webdriver was used(btw, to work with it, you should to have chrome web browser on your machine). You can check examples of data, extracted with the parser, in json_files directory.
