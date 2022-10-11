import { apiUrl } from "../config";

export const apiCall = (year, number, type, algo, keywords) => {
  let url = apiUrl + "rising-stars";
  if (type === "local") url += "-local";
  switch (algo) {
    case "basic":
      break;
    case "clusters":
      url += "-clusters";
      break;
    case "pagerank":
      url += "-page-rank";
      break;
    default:
      break;
  }

  url = new URL(url);

  url.searchParams.append("first_year", year);
  url.searchParams.append("number", number);
  if (type === "local") {
    keywords.forEach((keyword) => {
      url.searchParams.append("keyword", keyword);
    });
  }

  return fetch(url.href, {
    headers: { "Content-Type": "application/json" },
    method: "GET",
  });
};
