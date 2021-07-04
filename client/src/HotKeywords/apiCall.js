import { apiUrl } from "../config";

export const apiCall = (
  year,
  p_rate,
  c_rate,
  r_adjustment,
  number_of_features,
  r_min,
  dt
) => {
  let url = new URL(apiUrl + "hot-keywords");
  url.searchParams.append("year", year);
  if (p_rate) url.searchParams.append("p_rate", p_rate);
  if (c_rate) url.searchParams.append("c_rate", c_rate);
  if (typeof r_adjustment === "boolean")
    url.searchParams.append("r_adjustment", r_adjustment);
  if (number_of_features)
    url.searchParams.append("number_of_features", number_of_features);
  if (r_min) url.searchParams.append("r_min", r_min);
  if (dt) url.searchParams.append("dt", dt);

  return fetch(url.href, {
    headers: { "Content-Type": "application/json" },
    method: "GET",
  });
};
