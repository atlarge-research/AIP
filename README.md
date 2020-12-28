# AIP
<ins>A</ins>rticle <ins>I</ins>nformation <ins>P</ins>arser is an instrument to parse, unify, and in some cases correct article meta-data. 
AIP creates a SQLite database that allows for easily finding related work.

Developing such a database is tricky, an excerpt of [our article introducing this instrument](https://arxiv.org/abs/2004.10077):
```
Current information sources do not cover the spectrum of the systems community entirely.
For example, DBLP -- which specifically focuses on computer science articles -- lacks certain venues and does not record article abstracts.
Other datasets such as Semantic Scholar and AMiner have similar and other limitations.
Moreover, these datasets also overlap, yet contain important information the others do not offer; they are disjoint.
Our approach is to parse each dataset and filter and unify the information provided.
```

This instrument combines three data sources: [DBLP](https://dblp.uni-trier.de/faq/How+can+I+download+the+whole+dblp+dataset), [Semantic Scholar](https://api.semanticscholar.org/corpus/download/), and [AMiner](https://www.aminer.cn/oag2019), which we filter and store in a SQLite database.
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

## How to run AIP

We developed two useful scripts to run AIP and generate the database using raw datasources:
1. [A script to renew the data on a local (single) machine](https://github.com/atlarge-research/AIP/blob/master/renew_data_locally.py)
2. [A script to renew the data on a distributed system having a SLURM scheduler (managed by Dask)](https://github.com/atlarge-research/AIP/blob/master/renew_data_dask.py)

The steps to run AIP are as followed:
1. Clone this repository.
2. Run either one of the two scripts mentioned earlier or run separately [parse_dblp.py](https://github.com/atlarge-research/AIP/blob/master/parse_dblp.py), [parse_semantic_scholar.py](https://github.com/atlarge-research/AIP/blob/master/parse_semantic_scholar.py), or [parse_aminer.py](https://github.com/atlarge-research/AIP/blob/master/parse_aminer.py) using as argument to root of the data.

Have a look at which argument each script accepts (such as an alternative database name) for more options.

# AIP database structure

The `aip.db` (default) database file contains the following tables:

__publications__
| Column name | Explanation                                                                        |
|-------------|------------------------------------------------------------------------------------|
| id          | A unique id for the paper, usually the ID assigned by DBLP.                        |
| venue       | The abbreviation of the venue the article was accepted at.                         |
| year        | The publishing year.                                                               |
| volume      | (Optional) the volume of the journal the article it was included in.               |
| title       | The title of the article.                                                          |
| doi         | The DOI of the article, in case there are multiple, the first one is usually used. |
| abstract    | The abstract of the article (if present in one of the datasets).                   |
| n_citations | The number of times this article has been cited.                                   |

__authors__
| Column name | Explanation                                                  |
|-------------|--------------------------------------------------------------|
| id          | A unique identifier per author, this is the id used by DBLP. |
| name        | The full name of the author.                                 |
| orcid       | The ORCID of the author if known.                            |

__author_paper_pairs__ this is a table to make a link between authors and publications. We are aware of the use of `paper` rather than `article` (legacy).
| Column name | Explanation                                    |
|-------------|------------------------------------------------|
| author_id   | A id of an author.                             |
| paper_id    | The id of an article the author (co-)authored. |

__cites__ is currently not used, this table will contain in the future two article ids: which paper cited which.

__properties__
| Column name       | Explanation                                                                                                                                  |
|-------------------|----------------------------------------------------------------------------------------------------------------------------------------------|
| last_modified     | The data when the contents of the database were last altered.                                                                                |
| version           | The version of the database content, whenever a script modifies the database, after being done, this counter should be incremented.          |
| db_schema_version | The version of the database schema. We use this to incrementally alter the database (adding indices, modifying/deleting/adding tables, etc.) |


