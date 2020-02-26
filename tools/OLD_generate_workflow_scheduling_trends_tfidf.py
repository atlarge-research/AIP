import sqlite3

from tools.utils import get_top_keywords_for_query, create_df_for_query

conn = sqlite3.connect('../aip.db')
start_year = 2009  # inclusive
end_year = 2018  # inclusive

corpus_query = """
    SELECT * 
    FROM publications 
    WHERE year BETWEEN ? AND ?"""

corpus_df = create_df_for_query(conn, corpus_query, [start_year, end_year])

top_keywords_for_query = get_top_keywords_for_query(conn, corpus_df,
                                                    "SELECT * FROM publications WHERE year between {} and {}".format(
                                                        start_year, end_year), 50)
custom_stopwords_for_query = ["based", "method", "service", "approach", "problem", "computing", "proposed"]

# Generate overall trends across my entire database
print("""\\begin{{table}}[t]
\\caption{{Top-10 keywords in system-venue articles in the past decade.}}
\\label{{tbl:top-10-overall}}
\\vspace{{-0.2cm}}
\\begin{{adjustbox}}{{max width=\\columnwidth}}
\\begin{{tabular}}{{lllllllllll}}
\\toprule
Rank & 1 & 2 & 3 & 4 & 5 & 6 & 7 & 8 & 9 & 10 \\\\ \\midrule
Word & {0} \\\\ \\bottomrule
\\end{{tabular}}
\\end{{adjustbox}}
\\vspace{{-0.3cm}}
\\end{{table}}\n""".format(" & ".join([x for x in top_keywords_for_query if x not in custom_stopwords_for_query][:10])))

corpus_query = """
    SELECT * 
    FROM publications 
    WHERE year BETWEEN ? AND ?
    AND (title like '%workflow%' or abstract like '%workflow%') 
    AND (title like '%schedul%' or abstract like '%schedul%')"""

corpus_df = create_df_for_query(conn, corpus_query, [start_year, end_year])

top_keywords_for_query = get_top_keywords_for_query(conn, corpus_df,
                                                    """SELECT * 
                                                    FROM publications 
                                                    WHERE year between {} and {} 
                                                    and (lower(title) like '%workflow%' or lower(abstract) like '%workflow%') 
                                                    and (lower(title) like '%schedul%' or lower(abstract) like '%schedul%')""".format(
                                                        start_year, end_year),
                                                    40)

print(top_keywords_for_query)
exit()

print("""\\begin{{table}}[t]
\\caption{{Top-10 keywords in scheduling workflow articles in the past decade.}}
\\label{{tbl:top-10-scheduling-workflow-overall}}
\\vspace{{-0.2cm}}
\\begin{{adjustbox}}{{max width=\\columnwidth}}
\\begin{{tabular}}{{lllllllllll}}
\\toprule
Rank & 1 & 2 & 3 & 4 & 5 & 6 & 7 & 8 & 9 & 10 \\\\ \\midrule
Word & {0} \\\\ \\bottomrule
\\end{{tabular}}
\\end{{adjustbox}}
\\vspace{{-0.3cm}}
\\end{{table}}\n""".format(" & ".join([x for x in top_keywords_for_query if x not in custom_stopwords_for_query][:10])))

keywords_per_year = dict()
num_keywords = 10

for year in range(start_year, end_year + 1):
    query = "SELECT * FROM publications WHERE year = ? and (lower(title) like '%workflow%' or lower(abstract) like '%workflow%') and (lower(title) like '%schedul%' or lower(abstract) like '%schedul%')"
    keywords = get_top_keywords_for_query(conn, corpus_df, query, num_keywords, [year])
    keywords_per_year[year] = keywords

print("""
\\begin{table}[t]
\\caption{Top-10 keywords in scheduling workflow articles in the past decade per year.}
\\label{tbl:top-10-scheduling-workflow-per-year}
\\vspace{-0.2cm}
\\begin{adjustbox}{max width=\columnwidth}
\\begin{tabular}{{rllllllllll}}
\\toprule""")
print("Rank & {0} \\\\ \\midrule".format(" & ".join([str(x) for x in range(start_year, end_year + 1)])))

for rank in range(1, num_keywords + 1):
    line = "{0} & ".format(rank)
    for year in range(start_year, end_year + 1):
        line += "{0} & ".format(keywords_per_year[year][rank - 1])

    line = line.rstrip(" & ")
    line += " \\\\"
    if rank == 5:
        line += " \\midrule"

    if rank == num_keywords:
        line += " \\bottomrule"

    print(line)
print("""\end{tabular}
\\end{adjustbox}
\\vspace{-0.3cm}
\\end{table}""")
