import { apiUrl } from "../config";

export const apiCall = (name) => {
  let url = new URL(apiUrl + "authors-graph-psql");
  url.searchParams.append("author_name", name);

  return fetch(url.href, {
    headers: { "Content-Type": "application/json" },
    method: "GET",
  });
};
