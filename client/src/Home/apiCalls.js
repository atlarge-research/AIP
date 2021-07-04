import { apiUrl } from "../config";

export const apiCall = () => {
  let url = new URL(apiUrl + "statistics");

  return fetch(url.href, {
    headers: { "Content-Type": "application/json" },
    method: "GET",
  });
};

export const apiCallFresh = () => {
  let url = new URL(apiUrl + "is-fresh");

  return fetch(url.href, {
    headers: { "Content-Type": "application/json" },
    method: "GET",
  });
};
