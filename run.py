from selenium import webdriver
import selenium
import time
import json
import shutil
import requests
import re

CRAWLED_LINKS = 'links.txt'
PEOPLE_DATA = 'people.txt'
CANDIDATES = set([])

def login(driver):
	driver.get("some login link")
	ele_key = driver.find_element_by_name("session_key")
	ele_pwd = driver.find_element_by_name("session_password")

	# ele_key.send_keys("sanmateorenting@gmail.com")
	# ele_pwd.send_keys("linkedintony")

	ele_key.send_keys("test@test.com")
	ele_pwd.send_keys("password")
	ele_signin = driver.find_element_by_name("signin")
	ele_signin.submit()		
	time.sleep(15)

def load_urls():
	# read the potenial un crawled links
	with open(CRAWLED_LINKS, 'r') as f:
		for line in f:
			CANDIDATES.add(line)

	# remove if any link has been crawled
	with open(PEOPLE_DATA, 'r') as f:
		for line in f:
			url = json.loads(line)['url']
			CANDIDATES.discard(url)


def fetch_a_link():
	# will throw a KeyError if the set is empty
	return CANDIDATES.pop()

def extract_url(uu):
	return re.search("(?P<url>https?://[^\s]+)", uu).group("url")[:-3]


def append_to_the_file(person_url):
	CANDIDATES.add(person_url)
	with open(CRAWLED_LINKS, 'a') as f:
		f.write(person_url)
		f.write('\n')


def dump(data):
	with open(PEOPLE_DATA, 'a') as outfile:
		json.dump(data, outfile)
		outfile.write('\n')

def download_img(url, ts):
	response = requests.get(url, stream=True)
	with open('images/' + ts, 'wb') as f:
		shutil.copyfileobj(response.raw, f)
	del response


####################################################################################
# scraping process
driver = webdriver.Firefox()
login(driver)
load_urls()

counter = 0

while True:

	if counter > 10:
		break

	# grab a link 
	data = {}
	data['url'] = fetch_a_link() # if no more data, will throw exceptions

	driver.get(data['url'])
	
	#timestamp
	data['ts'] = str(int(time.time()))

	time.sleep(10)
	
	#### scape the info

	#picture address
	try:
		profile_div = driver.find_element_by_xpath("//div[contains(@style, 'background-image')]")
	except selenium.common.exceptions.NoSuchElementException:
		counter += 1
		continue

	image_url = profile_div.get_attribute("style")
	print("url:" + image_url)
	
	if not image_url:
		continue

	data['image_url'] = extract_url(image_url)
	download_img(data['image_url'], data['ts'])

	#name
	try:
		name_span = driver.find_element_by_xpath("//div[contains(@style, 'background-image')]/child::span")
	except selenium.common.exceptions.NoSuchElementException:
		counter += 1
		continue
	name = name_span.text
	data['name'] = name
	print("name:" + name)

	dump(data)

	#links to other people
	try:
		people_a = driver.find_elements_by_xpath("//a[contains(@class, 'section__member')]")
	except selenium.common.exceptions.NoSuchElementException:
		counter += 1
		continue

	for person in people_a:
		person_url = person.get_attribute("href")
		append_to_the_file(person_url)
		print(person_url)

	counter = 0

driver.close()
