const ls_name = "favourite_queries";

export const getFavouriteQueries = () => {
  let fq = localStorage.getItem(ls_name);
  if (fq) return JSON.parse(fq);
  else return [];
};

export const addFavouriteQuery = (query) => {
  const favouriteQueries = localStorage.getItem(ls_name);
  if (favouriteQueries)
    localStorage.setItem(
      ls_name,
      JSON.stringify([query, ...JSON.parse(favouriteQueries)])
    );
  else localStorage.setItem(ls_name, JSON.stringify([query]));
};

export const updateFavouriteQueries = (queries) => {
  console.log(queries);
  localStorage.setItem(ls_name, JSON.stringify(queries));
};
