import { apiUrl } from "../config";

export const apiCallFilter = (
  page,
  pageSize,
  sort,
  {
    venue,
    volume,
    year,
    title,
    doi,
    n_citations,
    author_names,
    id,
    // orcid,
    abstract_keywords,
    academic_age,
  }
) => {
  let url = new URL(apiUrl + "publications/");
  url.searchParams.append("page", page);
  url.searchParams.append("page_size", pageSize);
  if (venue) url.searchParams.append("venue__contains", venue);
  if (volume) url.searchParams.append("volume__contains", volume);
  if (year) url.searchParams.append("year__gte", year[0]);
  if (year) url.searchParams.append("year__lte", year[1]);
  if (title) url.searchParams.append("title__icontains", title);
  if (doi) url.searchParams.append("doi__contains", doi);
  if (n_citations) url.searchParams.append("n_citations__gte", n_citations[0]);
  if (n_citations) url.searchParams.append("n_citations__lte", n_citations[1]);
  if (author_names.length > 0)
    url.searchParams.append("authors", author_names.join(","));
  if (abstract_keywords.length > 0)
    url.searchParams.append("abstract", abstract_keywords.join(","));

  url.searchParams.append("ordering", (sort[1] === "asc" ? "" : "-") + sort[0]);

  return fetch(url.href, {
    headers: { "Content-Type": "application/json" },
    method: "GET",
  });
};

export const apiCallRaw = (query) => {
  let url = new URL(apiUrl + "raw-query");
  url.searchParams.append("sql", query);

  return fetch(url.href, {
    headers: { "Content-Type": "application/json" },
    method: "GET",
  });
};
