from googlesearch import search
from bs4 import BeautifulSoup
import requests
import json
import praw
import time

# Credentials and access

tmdb_key = "xxxxxxxxxxxxx"

creds = {"client_id": "xxxxxxxxxxxxx",
         "client_secret": "xxxxxxxxxxxxx",
         "password": "xxxxxxxxxxxxx",
         "user_agent": "add links to data",
         "username": "user_name"}

reddit = praw.Reddit(client_id=creds["client_id"],
                     client_secret=creds["client_secret"],
                     password=creds["password"],
                     user_agent=creds["user_agent"],
                     username=creds["username"])

# Lists to store the wiki page, titles, taglines, lists to hold and modify the tables,
# a dictionary to alphabetize titles, and a string to contain the wiki page entry

wiki = reddit.subreddit("name_of_subreddit").wiki["wiki_page_with_the_data"].content_md.split("##")
titles = []
taglines = []
tables = []
tables2 = []
tables3 = []
dict = {}
entry = ""

# From the wiki page, get the category titles, taglines, and tables

for i in wiki:
    titles.append(i.split("|")[0].split("\n")[0])
    if len(i.split("|")[0].split("\n")) > 1:
        taglines.append(i.split("|")[0].split("\n")[1])
    if "---|---|---|---|" in i:
        i = i.replace("\n", "")
        if "\n\n" not in i:
            tables.append(i.split("\n\n\n")[0].split("---|---|---|---|")[1].split("|"))

# For each title do the following...

for i in range(1, len(titles)):

    # One by one, add the titles, tag lines, and tables to a string called entry

    entry = entry + "##" + titles[i] + "  \n" + taglines[i] + "  \n  \n" + titles[i] + "| | | |\n---|---|---|---|\n"

    # If a title starts with A, An, or The, make a copy without it and store them both in a dictionary

    for j in tables[i-1]:
        altered_j = j
        if "An " in j:
            altered_j = j.split("An ")[1]
        elif "A " in j:
            altered_j = j.split("A ")[1]
        elif "The " in j:
            altered_j = j.split("The ")[1]
        else:
            altered_j = j

        dict.update({altered_j: j})

    # Alphabetize the dictionary and store it in another one

    sorted_dict = sorted(dict.items())

    # Analyze the tables, omit errors and formatting, and only include titles in the tables2 list

    for k in sorted_dict:
        catch_words = ["---------------------"]
        if not any(x in k[1] for x in catch_words):
            if k[1] != "\n":
                if k[1] != " ":
                    if k[1] != "":
                        if "#" not in k[1]:
                            tables2.append(k[1])

    # For each title in the list try to get the link

    throttle = 0
    for j in tables2:

        # Limit finding links to first 64 titles in the table to reduce search spam

        if throttle < 64:
            try:

                # Just in case, remove line breaks

                if "\n" in j:
                    j = j.replace("\n", "")

                # Create a search query to find the title id from a website

                query = j + " wesite_database_1"
                search_results = search(query, 4, 'en')
                for search_result in search_results:
                    if "https://www.wesite_database_1.com/title/tt" in search_result:
                        imdb_url = str(search_result)
                        if len(imdb_url) == 37:
                            imdb_id = imdb_url.replace("https://www.wesite_database_1.com/title/", "")
                            imdb_id = imdb_id.replace("/", "")
                            break

                # Use the title id from one website to access the titles data from another website

                info1 = "https://api.wesite_database_2.org/3/movie/" + imdb_id + "?api_key=" + tmdb_key + "&append_to_response=credits"
                info1 = requests.get(info1).text
                info1 = BeautifulSoup(info1, 'lxml')
                info1 = info1.p.text

                # Get the title's year and link

                tmdb_info = json.loads(info1)
                j = "[" + j + " (" + tmdb_info["release_date"].split("-")[0] + ")](https://www.wesite_database_2.org/movie/" + str(tmdb_info["id"]) + ")"

                # Add it to another list, tables3, which holds the title's name, year of release, and link

                tables3.append(j)

                # Take a nap to avoid spamming

                time.sleep(8)

            # If task to find title's link fails, just include the title name without the link

            except:
                tables3.append(j)

        # Using throttle, some titles are not used for adding links

        else:
            tables3.append(j)
        throttle = throttle + 1

    # Convert the list, tables3,  into one long string called table_text

    x = 1
    table_text = ""
    for k in tables3:

        # Add a pipe and a line break to every fourth item

        if x % 4 == 0:
            table_text = table_text + k + "|\n"

        # Just add a pipe to the other items

        else:
            table_text = table_text + k + "|"
        x = x + 1

    # Add table_text to the entry with some white space and a line break

    entry = entry + table_text + "  \n"

    # Reset the  lists and dictionaries

    tables2 = []
    tables3 = []
    dict = {}
    sorted_dict = {}

    # Print each completed table to the console

    print(entry + "\n" + 20*"-")

# Update the wiki page with the entry

reddit.subreddit("name_of_subreddit").wiki.create(name="wiki_page_to_update", content=entry, reason="Make Links")






