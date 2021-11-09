# AIP++

The full documentation of our application can be found at 
https://cutt.ly/Mn78T3f
### Running the application locally using Docker


1. Make sure you have Docker installed and running on your machine.

2. Run 'docker-compose up' command in the root directory of the project.

3. Access the application through your web browser by going to 
'http://localhost:8000/'.
   
### Accessing the application remotely

The most recent version of the application can be accessed at 
https://aip.irqize.dev/

----------------------------------------------------------------------------
#### Useful tips:

Use `docker-compose up --build` to rebuild your project. This is useful, if you
want to update the application after pulling it from git.

If you want to update the database, run docker volume ls' to find the name of
the volume containing the database and delete it using 
'docker volume rm <volume_name>' command.
# AIP
<ins>A</ins>rticle <ins>I</ins>nformation <ins>P</ins>arser is an instrument to parse, unify, and in some cases correct article meta-data. 
AIP creates a PostgreSQL database that allows for easily finding related work.

Developing such a database is tricky, an excerpt of [our article introducing this instrument](https://arxiv.org/abs/2004.10077):
```
Current information sources do not cover the spectrum of the systems community entirely.
For example, DBLP -- which specifically focuses on computer science articles -- lacks certain venues and does not record article abstracts.
Other datasets such as Semantic Scholar and AMiner have similar and other limitations.
Moreover, these datasets also overlap, yet contain important information the others do not offer; they are disjoint.
Our approach is to parse each dataset and filter and unify the information provided.
```

This instrument combines three data sources: [DBLP](https://dblp.uni-trier.de/faq/How+can+I+download+the+whole+dblp+dataset), [Semantic Scholar](https://api.semanticscholar.org/corpus/download/), and [AMiner](https://www.aminer.cn/oag2019), which we filter and store in a PostgreSQL database.
DBLP is a well-known European archive that focuses on computer science and features all the top-level venues (journals and conferences).
Semantic Scholar is an American project created by the Allen Institute for AI.
The project aims to analyze and extract important data from scientific publications.
AMiner is an Asian project that aims to provide a knowledge graph for mining academic social networks.
Both AMiner and Semantic Scholar have incorporated Microsoft's Academic Graph (MAG) in their datasets nowadays.

AIP tackles several non-trivial challenges in unifying these datasets:
1. Data discrepancies between sources. For example, titles in DBLP end with a dot, whereas they do not in the Semantic Scholar and AMiner corpuses, causing exact matching to fail.
2. Titles and abstracts may contain encoded characters leading to mismatching articles that are in fact the same.
3. Despite all data sources having a format specified, we encountered several instances where the format specified is not adhered to, or the data is malformed.
4. Venue strings being different among these sources. Some sources use an abbreviation, some use a BibTeX string, etc. AIP maps all these occurrences to the same abbreviation.
5. Complementing existing entries. For example, DBLP does not offer abstracts whilst Semantic Scholar and AMiner do.
