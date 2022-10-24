import React, { useState, useEffect, useMemo } from "react";
import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";
import Accordion from "@mui/material/Accordion";
import AccordionSummary from "@mui/material/AccordionSummary";
import AccordionDetails from "@mui/material/AccordionDetails";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import Button from "@mui/material/Button";
import useTheme from "@mui/material/styles/useTheme";
import Tooltip from "@mui/material/Tooltip";
import IconButton from "@mui/material/IconButton";
import TextField from "@mui/material/TextField";
import makeStyles from "@mui/styles/makeStyles";

import { Light as SyntaxHighlighter } from "react-syntax-highlighter";
import { useHistory } from "react-router-dom";
import sql from "react-syntax-highlighter/dist/esm/languages/hljs/sql";
import json from "react-syntax-highlighter/dist/esm/languages/hljs/json";
import { docco } from "react-syntax-highlighter/dist/esm/styles/hljs";
import moment from "moment";

import PublishIcon from "@mui/icons-material/Publish";
import GetAppIcon from "@mui/icons-material/GetApp";

import { exportToJson } from "./jsonFunctions";

import defaultValues from "../VisualQuerying/filterDefaultValues";
import routes from "../routes";
import {
  getFavouriteQueries,
  updateFavouriteQueries,
} from "./localStorageHelper";
import ImportDialog from "./ImportDialog";

const codeStyles = docco;
codeStyles.hljs.overflowX = "hidden";
SyntaxHighlighter.registerLanguage("sql", sql);
SyntaxHighlighter.registerLanguage("json", json);

const useStyles = makeStyles(() => ({
  accordion: {
    display: "block",
  },
  cancel: {
    marginRight: "10px",
  },
}));

const FavouriteQueries = () => {
  const classes = useStyles();
  const history = useHistory();
  const theme = useTheme();

  const [queries, setQueries] = useState([]);
  const [showID, setShowID] = useState(false);
  const [filter, setFilter] = useState("");

  useEffect(() => {
    setQueries(getFavouriteQueries());
  }, []);

  const removeFavouriteQuery = (query) => {
    const newQueries = queries.filter((q) => q !== query);
    setQueries(newQueries);
    updateFavouriteQueries(newQueries);
  };

  const importQueries = (newQueries) => {
    const queryArray = [...queries, ...newQueries];
    updateFavouriteQueries(queryArray);
    setQueries(queryArray);
  };

  // const queries = [
  //   {
  //     type: "sql",
  //     queryName: name,
  //     time: moment(),
  //     query:
  //       'SELECT "publications"."id", "publications"."venue", "publications"."year" FROM "publications" ORDER BY "publications"."id" ASC LIMIT 10',
  //   },
  //   {
  //     type: "filters",
  //     queryName: name,
  //     time: moment(),
  //     query: {
  //       venue: "",
  //       volume: "",
  //       year: [2001, 2009],
  //       title: "",
  //       doi: "",
  //       n_citations: [10000, 25000],
  //       author_names: [],
  //       abstract_keywords: [],
  //     },
  //   },
  // ];

  const executeRawQuery = (query) => {
    history.push({
      pathname: routes.visualQuerying,
      state: { rawQuery: query },
    });
  };

  const executeFilterQuery = (query) => {
    history.push({
      pathname: routes.visualQuerying,
      state: { filterQuery: { ...defaultValues, ...query } },
    });
  };

  const generateQueryItem = (query, key) => {
    switch (query.type) {
      case "sql":
        return (
          <Accordion key={key}>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Typography>
                [SQL Query saved on{" "}
                {moment(query.time).format("DD.MM.YYYY HH:mm")}]{" "}
                {query.queryName}
              </Typography>
            </AccordionSummary>
            <AccordionDetails className={classes.accordion}>
              <SyntaxHighlighter
                style={codeStyles}
                language="sql"
                wrapLongLines
              >
                {query.query}
              </SyntaxHighlighter>
              <Box display="flex" justifyContent="flex-end">
                <Button
                  variant="contained"
                  color="secondary"
                  onClick={() => removeFavouriteQuery(query)}
                  className={classes.cancel}
                >
                  Remove
                </Button>
                <Button
                  variant="contained"
                  color={theme.palette.mode === "light" ? "primary" : "default"}
                  onClick={() => executeRawQuery(query.query)}
                >
                  Execute
                </Button>
              </Box>
            </AccordionDetails>
          </Accordion>
        );
      case "filters":
        return (
          <Accordion key={key}>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Typography>
                [Filter Query saved on{" "}
                {moment(query.time).format("DD.MM.YYYY HH:mm")}]{" "}
                {query.queryName}
              </Typography>
            </AccordionSummary>
            <AccordionDetails className={classes.accordion}>
              <SyntaxHighlighter
                style={codeStyles}
                language="json"
                wrapLongLines
              >
                {JSON.stringify(query.query, null, 2)}
              </SyntaxHighlighter>
              <Box display="flex" justifyContent="flex-end">
                <Button
                  variant="contained"
                  color="secondary"
                  onClick={() => removeFavouriteQuery(query)}
                  className={classes.cancel}
                >
                  Remove
                </Button>
                <Button
                  variant="contained"
                  color={theme.palette.mode === "light" ? "primary" : "default"}
                  onClick={() => executeFilterQuery(query.query)}
                >
                  Execute
                </Button>
              </Box>
            </AccordionDetails>
          </Accordion>
        );
      default:
        return null;
    }
  };

  const queriesAccordions = useMemo(
    () =>
      queries
        .filter((query) =>
          query.queryName.toLowerCase().includes(filter.toLowerCase())
        )
        .map((query, key) => generateQueryItem(query, key)),
    [queries, filter]
  );

  return (
    <div>
      <ImportDialog
        showID={showID}
        setShowID={setShowID}
        onSave={importQueries}
      />
      <Box my={3} display="flex" justifyContent="space-between" flexWrap="wrap">
        <Typography variant="h4">Favourite Queries</Typography>
        <TextField
          variant="outlined"
          size="medium"
          label="Filter queries by name"
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
        />
        <Box>
          <Tooltip
            title="Export favourite queries to JSON file"
            aria-label="export queries"
          >
            <IconButton
              variant="contained"
              onClick={() => exportToJson(queries)}
              disabled={!queries.length}
              aria-label="show sql quries"
              size="large">
              <GetAppIcon />
            </IconButton>
          </Tooltip>
          <Tooltip
            title="Import favourite queries by uploading JSON file"
            aria-label="import queries"
          >
            <IconButton
              variant="contained"
              onClick={() => setShowID(true)}
              aria-label="show sql quries"
              size="large">
              <PublishIcon />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>
      {!Boolean(queries.length) && (
        <Typography variant="h6">No queries were saved yet.</Typography>
      )}
      {queriesAccordions}
    </div>
  );
};

export default FavouriteQueries;
