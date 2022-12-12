import React, { useState, useEffect } from "react";
import {
  IconButton,
  Typography,
  Box,
  LinearProgress,
  Snackbar,
  Tooltip,
  Alert,
} from "@mui/material";
import { useLocation } from "react-router-dom";
import moment from "moment";
import { addFavouriteQuery } from "../FavouriteQueries/localStorageHelper";

// Icons
import FilterListIcon from "@mui/icons-material/FilterList";
import FavoriteBorderIcon from "@mui/icons-material/FavoriteBorder";
import FavoriteIcon from "@mui/icons-material/Favorite";
import SaveIcon from "@mui/icons-material/Save";

import exportToCsv from "./exportToCsv";
import { apiCallFilter } from "./apiCalls";
import defaultValues from "./filterDefaultValues";
import Table from "./Table";
import AbstractDialog from "./AbstractDialog";
import FiltersDialog from "./FiltersDialog";
import AuthorsDialog from "./AuthorsDialog";
import FavouriteQueryDialog from "./FavouriteQueryDialog";
import SchemaDialog from "./SchemaDialog";

const VisualQuerying = () => {
  const location = useLocation();

  const [filtersOpen, setFiltersOpen] = useState(false);

  const [sort, setSort] = useState(["id", "asc"]);
  const [data, setData] = useState([]);

  const [rawQueries, setRawQueries] = useState(null);
  const [showRawQueries, setShowRawQueries] = useState(false);

  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const [count, setCount] = useState(-1);

  const [loading, setLoading] = useState(false);

  // const [rawQuery, setRawQuery] = useState("");
  // const [rawQueryDialogOpened, setRawQueryDialogOpened] = useState(false);
  // const [rawQueryError, setRawQueryError] = useState("");
  // const [rawQueryExecuted, setRawQueryExecuted] = useState(false);

  const [filters, setFilters] = useState({ ...defaultValues });

  const [currentArticle, setCurrentArticle] = useState({ authors: [] });
  const [showAbstract, setShowAbstract] = useState(false);

  const [showAuthors, setShowAuthors] = useState(false);

  const [alertOpened, setAlertOpened] = useState(false);
  const [alert, setAlert] = useState("");
  const closeAlert = () => setAlertOpened(false);

  const [showFQD, setShowFQD] = useState(false);

  const [showSchema, setShowSchema] = useState(false);

  const [querySaved, setQuerySaved] = useState(false);
  const saveCurrentQuery = (name) => {
    setQuerySaved(true);
    // if (rawQueryExecuted) {
    //   addFavouriteQuery({
    //     type: "sql",
    //     queryName: name,
    //     time: moment(),
    //     query: rawQuery,
    //   });
    // } else {
      const specifiedFilters = {};
      for (let key in defaultValues) {
        if (
          defaultValues.hasOwnProperty(key) &&
          filters[key] !== defaultValues[key]
        ) {
          if (Array.isArray(filters[key]) && filters[key].length === 0)
            continue;
          specifiedFilters[key] = filters[key];
        }
      }
      addFavouriteQuery({
        type: "filters",
        queryName: name,
        time: moment(),
        query: specifiedFilters,
      });
    // }
  };

  // const onRawQuerySubmit = (query) => {
  //   setRawQueryError("");
  //   setRawQuery(query);
  //   setLoading(true);
  //   apiCallRaw(query)
  //     .then((res) => res.json())
  //     .then((data) => {
  //       console.log(data);
  //       setData(data);
  //       setLoading(false);
  //       setRawQueryExecuted(true);
  //       setRawQueries(null);
  //       setQuerySaved(false);

  //       if (initialRawQuery) setInitialRawQuery(null);
  //     })
  //     .catch((e) => {
  //       console.error(e);
  //       setRawQuery(null);
  //       setLoading(false);
  //       setRawQueryDialogOpened(true);
  //       setRawQueryError(
  //         "There was a problem executing your query. Please check your syntax."
  //       );
  //     });
  // };

  // const [initialRawQuery, setInitialRawQuery] = useState(
  //   location && location.state && location.state.rawQuery
  // );

  useState(() => {
    // if (initialRawQuery) onRawQuerySubmit(initialRawQuery);
    if (location && location.state && location.state.filterQuery)
      setFilters(location.state.filterQuery);
  }, []);

  // On every filter change refetch from the api
  useEffect(() => {
    // if (initialRawQuery) return;
    setLoading(true);
    apiCallFilter(page, pageSize, sort, filters)
      .then((res) => res.json())
      .then((data) => {
        setData(data.results);
        setCount(data.count);
        setRawQueries(data.raw_query);
        setLoading(false);
        // setRawQueryExecuted(false);
        setQuerySaved(false);
        // setRawQuery(null);
      })
      .catch((e) => {
        console.error(e);
        setLoading(false);
        setAlert("Problem occured when connecting to the backend.");
      });
    /* eslint-disable-next-line */
  }, [filters, page, sort, pageSize]);

  const filterByAuthor = (name) => {
    const newFilters = { ...defaultValues };
    newFilters.author_names = [name];
    setFilters(newFilters);
  };

  useEffect(() => {
    if (alert) setAlertOpened(true);
  }, [alert]);

  return (
    <div>
      <SchemaDialog showSchema={showSchema} setShowSchema={setShowSchema} />
      <FavouriteQueryDialog
        showFQD={showFQD}
        setShowFDQ={setShowFQD}
        onSave={saveCurrentQuery}
      />
      {/* <RawQueryDialog
        query={rawQuery}
        setRawQuery={setRawQuery}
        opened={rawQueryDialogOpened}
        setOpened={setRawQueryDialogOpened}
        onSubmit={onRawQuerySubmit}
        error={rawQueryError}
      /> */}
      <FiltersDialog
        filters={filters}
        setFilters={setFilters}
        filtersOpen={filtersOpen}
        setFiltersOpen={setFiltersOpen}
      />
      <AuthorsDialog
        showAuthors={showAuthors}
        setShowAuthors={setShowAuthors}
        currentArticle={currentArticle}
        filterByAuthor={filterByAuthor}
      />
      <AbstractDialog
        showAbstract={showAbstract}
        setShowAbstract={setShowAbstract}
        currentArticle={currentArticle}
      />
      {/* <RawQueriesDialog
        showRawQueries={showRawQueries}
        setShowRawQueries={setShowRawQueries}
        rawQueries={rawQueries}
      /> */}
      <Box display="flex" justifyContent="space-between" my={3}>
        <Typography variant="h4">Visual Querying</Typography>
        <Box display="flex" alignItems="center">
          {/* <Tooltip title="Show schema of the database">
            <IconButton
              variant="contained"
              onClick={() => setShowSchema(true)}
              aria-label="show database schema"
              size="large">
              <HelpIcon />
            </IconButton>
          </Tooltip> */}
          {/* {rawQueries && (
            <Tooltip title="Show executed SQL Queries" aria-label="sql">
              <IconButton
                variant="contained"
                onClick={() => setShowRawQueries(true)}
                aria-label="show sql quries"
                size="large">
                <InfoIcon />
              </IconButton>
            </Tooltip>
          )} */}
          <IconButton
            variant="contained"
            onClick={() => setShowFQD(true)}
            disabled={querySaved}
            aria-label="save query"
            size="large">
            {querySaved ? (
              <FavoriteIcon />
            ) : (
              <Tooltip
                title="Add last executed query to Favourite Queries"
                aria-label="sql"
              >
                <FavoriteBorderIcon />
              </Tooltip>
            )}
          </IconButton>
          <Tooltip title="Export current page to a CSV file" aria-label="sql">
            <IconButton
              variant="contained"
              onClick={() => {
                if (data.length && !loading)
                  exportToCsv(data, "");
                  // exportToCsv(data, rawQueryExecuted);
              }}
              aria-label="export csv"
              disabled={!data.length || loading}
              size="large">
              <SaveIcon />
            </IconButton>
          </Tooltip>
          <Box display="inline-flex" ml={3}>
            {/* <Tooltip title="Execute custom SQL query" aria-label="sql">
              <IconButton
                variant="contained"
                onClick={() => setRawQueryDialogOpened(true)}
                aria-label="run sql query"
                size="large">
                <BuildIcon />
              </IconButton>
            </Tooltip> */}
            <Tooltip title="Filter the database" aria-label="filter">
              <IconButton
                variant="contained"
                onClick={() => setFiltersOpen(true)}
                aria-label="filter list"
                size="large">
                <FilterListIcon />
              </IconButton>
            </Tooltip>
          </Box>
        </Box>
      </Box>
      {loading ? (
        <LinearProgress />
      ) : (
        <Table
          data={data}
          // rawQueryExecuted={""}
          sort={sort}
          setSort={setSort}
          page={page}
          setPage={setPage}
          pageSize={pageSize}
          setPageSize={setPageSize}
          count={count}
          setCurrentArticle={setCurrentArticle}
          setShowAbstract={setShowAbstract}
          setShowAuthors={setShowAuthors}
        />
      )}

      <Snackbar open={alertOpened} autoHideDuration={6000} onClose={closeAlert}>
        <Alert
          elevation={6}
          variant="filled"
          onClose={closeAlert}
          severity="error"
          key={alert}
        >
          {alert}
        </Alert>
      </Snackbar>
    </div>
  );
};

export default VisualQuerying;
