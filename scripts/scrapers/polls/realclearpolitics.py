from urllib.request import urlopen as uReq
from bs4 import BeautifulSoup as soup
import ssl
import csv
import time
from datetime import datetime
from fuzzywuzzy import fuzz
from fuzzywuzzy import process

# Not checking ssl certification
# RCP has ssl rating of F

ssl._create_default_https_context = ssl._create_unverified_context

my_url = "https://realclearpolitics.com/epolls/latest_polls/"
my_url_2 = "https://realclearpolitics.com/epolls/other/2018_generic_congressional_vote-6185.html#polls"

# opening up connnection, grabbing the page

uClient = uReq(my_url)
uClient_2 = uReq(my_url_2)

# offloads connection content into a variable

page_html = uClient.read()
page_html_2 = uClient_2.read()

# closes connection

uClient.close()
uClient_2.close()

# html parsing

page_soup = soup(page_html, "html.parser")
page_soup_2 = soup(page_html_2, "html.parser")

# grabs each product

poll_races = page_soup.findAll("td", {"class": "lp-race"})
poll_races_count = page_soup.findAll("td", {"class": "lp-race"})
poll_names = page_soup.findAll("td", {"class": "lp-poll"})
poll_results = page_soup.findAll("td", {"class": "lp-results"})
poll_spreads = page_soup.findAll("td", {"class": "lp-spread"})
table_dates = page_soup.findAll("td", {"class": "date"})
poll_tables = page_soup.findAll("table", {"class": "sortable"})

# grabs poll population from seperate Real Clear Politics page

poll_populations = page_soup_2.findAll("td", {"class": "sample"})

# holds size of each poll table
tableLengthList = []

# holds the table index for every poll
tableIndexList = []

# holds date of each table
tableDateList = []

# holds scraped polls
scrapedPollsList = []

# holds polls already in the csv
oldPollsList = []

# holds the dates of the polls currently in the csv
oldDatesList = []

# holds the name pollsters, per 538
pollsterNameList = []

# holds the rating of pollsters, per 538
pollsterRatingList = []

# holds the method
pollsterMethodList = []

# holds the margin of error
pollsterMoEList = []

# store the number of races in each table in tableLengthList
for table in poll_tables:
  polls_in_table = table.findAll('td', {"class": "lp-race"})
  tableLengthList.append(len(polls_in_table))

# number of rows on the RCP website
total_row_num = len(poll_races_count)
# number of tables on the RCP website
table_num = len(tableLengthList)

# calculate table index for every poll
for table_index in range(0, table_num):
  table_row_count = 0
  while table_row_count < tableLengthList[table_index]:
    tableIndexList.append(table_index)
    table_row_count = table_row_count + 1

# store table dates
for date in table_dates:
  tableDateList.append(date.string);


# Takes date format, Example: Wednesday, February 7
# transforms into format: DD/MM/YYYY
def formatDate(str):
  date = ""
  a, b = str.split(',')
  del a
  space, month, day = b.split(' ')
  del space

  if month == "January":
    date = date + "01/"
  if month == "February":
    date = date + "02/"
  if month == "March":
    date = date + "03/"
  if month == "April":
    date = date + "04/"
  if month == "May":
    date = date + "05/"
  if month == "June":
    date = date + "06/"
  if month == "July":
    date = date + "07/"
  if month == "August":
    date = date + "08/"
  if month == "September":
    date = date + "09/"
  if month == "October":
    date = date + "10/"
  if month == "November":
    date = date + "11/"
  if month == "December":
    date = date + "12/"

  date = date + day + "/"
  year = datetime.now().strftime('%Y')
  date = date + year
  return date


# Take as input: Democrats 44, Republicans 39
# Transforms input into a simple decimal value
def formatDem(str):
  Dem, Rep = str.split(',')
  DemName, Dem_percent, RepName, Rep_percent = str.split(' ')
  del DemName
  del RepName
  Dem_percent, comma = Dem_percent.split(',')
  del comma
  Dem_percent = "0." + Dem_percent
  return Dem_percent


def formatRep(str):
  Dem, Rep = str.split(',')
  DemName, Dem_percent, RepName, Rep_percent = str.split(' ')
  del DemName
  del RepName
  Rep_percent = "0." + Rep_percent
  return Rep_percent


# Takes split input like "Economist/YouGov"
# returns poll source
def formatSource(str):
  slash_index = str.find('/')
  slash_count = str.count('/')
  slash_index_two = str.find('/', slash_index + 1)

  poll_sponsor = ""
  poll_source = ""

  if slash_count >= 2:
    poll_sponsor = str[:slash_index_two];
    poll_source = str[slash_index_two + 1:len(str)]
  else:
    if slash_index > 0:
      poll_sponsor, poll_source = str.split('/')
    else:
      poll_source = str

  return poll_source


# Takes split input like "Economist/YouGov"
# returns poll sponsor
def formatSponsor(str):
  slash_count = str.count('/')
  slash_index = str.find('/')
  slash_index_two = str.find('/', slash_index + 1)

  poll_sponsor = ""
  poll_source = ""

  if slash_count >= 2:
    poll_sponsor = str[:slash_index_two];
    poll_source = str[slash_index_two + 1:len(str)]
  else:
    if slash_index > 0:
      poll_sponsor, poll_source = str.split('/')
    else:
      poll_sponsor = ""

  return poll_sponsor


# Takes poll population input like "1246 RV"
# transforms to Registered voters
def formatPopulation(str):
  space_index = str.find(' ')

  pop_size = ""
  pop_type = ""

  if space_index > 0:
    pop_size, pop_type = str.split(' ')
  else:
    pop_type = str

  if pop_type == "RV":
    return "Registered Voters"
  if pop_type == "A":
    return "Adults"
  if pop_type == "LV":
    return "Likely Voters"


def findPollsterIndex(str):
  name_count = 0
  max_ratio_count = 0

  match_ratio = 0
  max_ratio = 0

  for name in pollsterNameList:
    match_ratio = fuzz.partial_ratio(str, name)
    if match_ratio > max_ratio:
      max_ratio = match_ratio
      max_ratio_count = name_count

    name_count = name_count + 1

  return max_ratio_count


# holds highest index in file
highest_index = 0
# store dates of polls currently in the csv
with open("conrace.csv", "r", encoding="utf8") as fp:
  reader = csv.reader(fp)
  for row in reader:
    if (len(row) > 0):
      oldDatesList.append(row[1])
      highest_index = row[0]

# find the most recent date in the current csv
most_recent_date = oldDatesList[-1]

# store the name and rating of polls, per 538
with open("pollster-ratings.csv", "r") as fn:
  reader = csv.reader(fn)
  for row in reader:
    pollsterNameList.append(row[1])
    pollsterRatingList.append(row[11])
    pollsterMoEList.append(row[7])

    pollster_method = ""

    if row[3] == "yes":
      pollster_method = "Live Phone"

    if row[4] == "yes":
      if len(pollster_method) > 0:
        pollster_method = pollster_method + "/Internet"
      else:
        pollster_method = "Internet"

    pollsterMethodList.append(pollster_method)

highest_index = int(highest_index)

for count in range(0, total_row_num):

  raceName = poll_races[count].a.string
  pollName = poll_names[count].a.string
  pollSpread = poll_spreads[count].span.string
  pollResult = poll_results[count].a.string

  pollSponsor = formatSponsor(pollName)
  pollSource = formatSource(pollName)

  pollDate = tableDateList[tableIndexList[count]]
  pollDate = formatDate(pollDate)

  pollPopulation = poll_populations[count + 1].string
  pollPopulation = formatPopulation(pollPopulation)

  pollster_index = findPollsterIndex(pollSource)
  pollRating = pollsterRatingList[pollster_index]
  pollMethod = pollsterMethodList[pollster_index]
  pollError = pollsterMoEList[pollster_index]

  pollError = pollError[0:3]

  if raceName == "2018 Generic Congressional Vote":
    RepScore = formatRep(pollResult)
    DemScore = formatDem(pollResult)

    pollInstance = [pollDate, DemScore, RepScore, pollMethod, pollRating, pollPopulation, pollError, pollSponsor,
                    pollSource]
    scrapedPollsList.append(pollInstance)

# reverse so that the data gets input with oldest at bottom and newest at top
scrapedPollsList.reverse()

poll_index = highest_index + 1

for poll in scrapedPollsList:
  poll.insert(0, poll_index)
  poll_index = poll_index + 1

# write new polls to the csv
with open("conrace.csv", "a", newline='') as f:
  writer = csv.writer(f, delimiter=',')
  for poll in scrapedPollsList:
    poll_date_formatted = time.strptime(poll[1], "%m/%d/%Y")
    most_recent_date_formatted = time.strptime(most_recent_date, "%m/%d/%Y")
    if poll_date_formatted > most_recent_date_formatted:
      writer.writerow(poll)