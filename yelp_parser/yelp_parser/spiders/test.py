import scrapy
import re
import json
import requests
from dotenv import load_dotenv, find_dotenv
import os
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

load_dotenv(find_dotenv())


class YelpSpider(scrapy.Spider):
    name = "yelp"

    def parse(self, response):
        # first of all we gonna extract business id
        # so that get ability of using api data
        business_id = self.parse_id(response)

        # data from yelp api about current business.
        # it's not required to use, but it gives
        # some guarantees of reliability of parsed data.
        api_info = self.get_api_info(response, business_id)

        # following variables include all necessary info to parse
        # there is special def for each field
        business_title = self.parse_title(response, api_info)
        business_url = self.parse_business_url(response, api_info)
        business_image_url = self.parse_image_url(response, api_info)
        phone_number = self.parse_phone_number(response, api_info)
        website = self.parse_website(response, api_info)
        location = self.parse_location(response, api_info)
        rating = self.parse_rating(response, api_info)
        reviews = self.parse_reviews(response, api_info)
        categories = self.parse_categories(response, api_info)
        schedule = self.parse_schedule(response, api_info)
        read_more = self.parse_read_more(response)
        amenities_and_more = self.parse_amenities_and_more(response)

        yield {
            "title": business_title,
            "url": business_url,
            "id": business_id,
            "business_image_url": business_image_url,
            "website": website,
            "phone_number": phone_number,
            "location": location,
            "rating": rating,
            "reviews": reviews,
            "categories": categories,
            "schedule": schedule,
            "read_more": read_more,
            "amenitites_and_more": amenities_and_more,
        }

    def get_api_info(self, response, business_id):
        # getting data from yelp api
        url = "https://api.yelp.com/v3/businesses/" + business_id
        api_key = os.getenv("KEY")
        if api_key is None:
            return None
        headers = {"Authorization": "Bearer %s" % api_key}
        return json.loads(requests.get(url, headers=headers).text)

    def check_api(self, parsed_data, api_data):
        """
            Return data from api if parsed data doesn't match api data,
            otherwise return parsed data
        """
        if parsed_data is not None:
            return parsed_data
        else:
            self.log(
                " \
                Something went wrong with markup. \
                Api's data were returned"
            )
            return api_data

    def parse_id(self, response):
        # there are several specific cases, including business id.
        # all them occurs in expression like /biz/IdIsHere?
        # so we can just extract all those cases and definitely we will be
        # able to extract id from them, unless we got a big changes on the
        # page, after which all cases were lost.
        occurrences = (response.xpath("//*/@href")
                               .re(r"/biz/[a-zA-Z0-9-]*\?"))
        if len(occurrences) == 0:
            self.log("Issue: Current markup does not allow extract id!")

        # take just first occurrence and extract id from regex
        id = re.search(r"/biz/(.*?)\?", occurrences[0]).group(1)
        return id

    def parse_title(self, response, api_info):
        # following xpath is reliable because
        # there is no h1 tags anymore
        business_title = response.xpath(
            '//h1/text()'
        ).get()
        # check match with api_data and return result
        return (
            self.check_api(business_title, api_info["name"])
            if api_info
            else business_title
        )

    def parse_business_url(self, response, api_info):
        # actually data from api will be different anyway
        # cause yelp use special urls for redirecting to the
        # business page. So with api_key or without it, you
        # will get different urls, but both work fine.
        business_url = response.request.url
        # check match with api_data and return result
        return (
            self.check_api(business_url, api_info["url"])
            if api_info
            else business_url
        )

    def parse_image_url(self, response, api_info):
        # take first image
        business_image_url = response.xpath(
            '//a/img/@src'
        ).get()
        # check match with api_data and return result
        return (
            self.check_api(business_image_url, api_info["image_url"])
            if api_info
            else business_image_url
        )

    def parse_phone_number(self, response, api_info):
        # search <p> tag with text 'Phone number',
        # then search number beside it
        phone_number = response.xpath(
            "//p[.='Phone number']/..//p/text()"
        ).getall()
        try:
            phone_number = phone_number[1]
        except IndexError:
            print("Something went wrong")
            phone_number = None
        # check match with api_data and return result
        return (
            self.check_api(phone_number, api_info["display_phone"])
            if api_info
            else phone_number
        )

    def parse_website(self, response, api_info):
        # search <p> tag with text 'Business website',
        # then search url beside it
        website = response.xpath(
            "//p[.='Business website']/..//p/a/@href"
        ).get()
        # check match with api_data and return result
        return (
            self.check_api(website, api_info["url"])
            if api_info
            else website
        )

    def parse_location(self, response, api_info):
        # search addredd tag. it's only on the page
        try:
            location_full = response.xpath("//address/p/span/text()").getall()
            location = {}
            # check all addresses
            for i in location_full[0:-1]:
                location.update({"address" + str(location_full.index(i) + 1): i})
            # and rest info
            city = location_full[-1].split(",")[0]
            location.update({"city": city})
            rest = location_full[-1].split(",")[1].split()
            location.update({"zip_code": rest[1], "state": rest[0]})
        except IndexError:
            print("Something went wrong")
            location = None
        # check match with api_data and return result
        return (
            self.check_api(location, api_info["location"])
            if api_info
            else location
        )

    def parse_rating(self, response, api_info):
        rating = response.xpath(
            '//div[contains(@aria-label, "rating")]/@aria-label'
        ).get()
        # check match with api_data and return result
        return (
            self.check_api(rating, api_info["rating"])
            if api_info
            else rating
        )

    def parse_reviews(self, response, api_info):
        reviews = response.xpath(
            '//p[contains(text(), "reviews")]/text()'
        ).get()
        # check match with api_data and return result
        return (
            self.check_api(reviews, api_info["review_count"])
            if api_info
            else reviews
        )

    def parse_categories(self, response, api_info):
        categories = response.xpath(
            '//a[contains(text(), "Edit")]/../span/span/a/text()'
        ).getall()
        if len(categories) == 0:
            categories = None
        # check match with api_data and return result
        return (
            self.check_api(categories, api_info["categories"])
            if api_info
            else categories
        )

    def parse_schedule(self, response, api_info):
        schedule = {}
        try:
            schedule_full = response.xpath(
                '//div/table/tbody//th/p[contains(text(),"Mon")]/../../../tr//p/text()'
            ).getall()
            schedule = {
                schedule_full[i * 2]: schedule_full[i * 2 + 1] for i in range(7)
            }
        except IndexError:
            print("Something went wrong")
            schedule = None
        # check match with api_data and return result
        return (
            self.check_api(schedule, api_info["hours"])
            if api_info
            else schedule
        )

    # following parsers are a little bit specific
    # because webdriver is required to extract data.
    # it's necessary, cause Scrapy cannot interpret javascript,
    # but for getting info on the site, users are required
    # to click special button
    def parse_read_more(self, response):
        data = {}

        # start driver
        self.driver = webdriver.Chrome(ChromeDriverManager().install())
        self.driver.get(response.request.url)

        # click special button to get info on the page
        self.driver.find_element_by_xpath(
            '//button/div/span[contains(text(), "Read more")]'
        ).click()

        headers = self.driver.find_elements_by_xpath(
            '//h2[contains(text(), "From the business")]/../../..//h5'
        )
        paragraphs_in_div = self.driver.find_elements_by_xpath(
            '//h2[contains(text(), "From the business")]/../..//h5/../..'
        )
        paragraphs = self.driver.find_elements_by_xpath(
            '//h2[contains(text(), "From the business")]/../..//h5/../../p'
        )

        for header in headers:
            data.update({header.text: ""})

        for paragraph in paragraphs:
            for paragraph_in_div in paragraphs_in_div:
                new = (
                    paragraph.text
                    if paragraph.get_attribute("innerHTML")
                    in paragraph_in_div.get_attribute("innerHTML")
                    else ""
                )
                data[
                    list(data.keys())[paragraphs_in_div.index(paragraph_in_div)]
                ] += new

        # close driver
        self.driver.close()
        return data

    def parse_amenities_and_more(self, response):
        data = ""

        # start driver
        self.driver = webdriver.Chrome(ChromeDriverManager().install())
        self.driver.get(response.request.url)

        # click special button to get info on the page
        try:
            self.driver.find_element_by_xpath(
                '//p[contains(text(), "More Attributes")]'
            ).click()
        except NoSuchElementException:
            print("there is no special button")

        try:
            points = self.driver.find_elements_by_xpath(
                '//h4[contains(text(), "Amenities and More")]/../../..//div//span'
            )
            pattern = re.compile(r"[a-zA-Z ]+")
            for point in points:
                if pattern.match(point.text):
                    data += point.text + ", "
        except NoSuchElementException:
            print("There is no such element")

        # close driver
        self.driver.close()
        return data
