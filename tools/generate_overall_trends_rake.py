import csv
import re
import sqlite3

from rake_nltk import Rake

workflow_venue_set = set()
with open('venues-having-workflow.csv') as csvfile:
    reader = csv.reader(csvfile, delimiter=',', quotechar='"')
    for row in reader:
        workflow_venue_set.add(row[0])

schedul_venue_set = set()
with open('venues-mentioning-schedul.csv') as csvfile:
    reader = csv.reader(csvfile, delimiter=',', quotechar='"')
    for row in reader:
        schedul_venue_set.add(row[0])

# Compute the intersection of the two sets to obtain venues mentioning both
intersection_venue_set = workflow_venue_set.intersection(schedul_venue_set)

conn = sqlite3.connect(
    '/home/lfdversluis/PycharmProjects/parse-semantic-scholar-corpus/dblp_ss'
    '.db')

c = conn.cursor()

r = Rake(min_length=1, max_length=1)

word_ranks = dict()


def remove_string_special_characters(s):
    stripped = re.sub('[^\w\s]', '', s)
    stripped = re.sub('_', '', stripped)

    stripped = re.sub('\s+', ' ', stripped)

    stripped = stripped.strip()

    return stripped


for venue in intersection_venue_set:
    query = "SELECT * FROM publications WHERE venue = ? and year between " \
            "2008 and 2018 "
    res = c.execute(query, [venue])

    for row in res:
        title = remove_string_special_characters(row[4])
        abstract = remove_string_special_characters(row[5])

        title_and_abstract = " ".join([title, abstract])
        r.extract_keywords_from_text(title_and_abstract)
        keywords = r.get_ranked_phrases()

        for keyword in keywords:
            if keyword not in word_ranks:
                word_ranks[keyword] = 0

            word_ranks[keyword] += 1

s = [(k, word_ranks[k]) for k in
     sorted(word_ranks, key=word_ranks.get, reverse=True)]
for k, v in s:
    print(k, v)
