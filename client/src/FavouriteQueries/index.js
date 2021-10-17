import React, { useState, useEffect, useMemo } from "react";
import Box from "@material-ui/core/Box";
import Typography from "@material-ui/core/Typography";
import Accordion from "@material-ui/core/Accordion";
import AccordionSummary from "@material-ui/core/AccordionSummary";
import AccordionDetails from "@material-ui/core/AccordionDetails";
import ExpandMoreIcon from "@material-ui/icons/ExpandMore";
import Button from "@material-ui/core/Button";
import useTheme from "@material-ui/core/styles/useTheme";
import Tooltip from "@material-ui/core/Tooltip";
import IconButton from "@material-ui/core/IconButton";
import TextField from "@material-ui/core/TextField";
import makeStyles from "@material-ui/core/styles/makeStyles";

import { Light as SyntaxHighlighter } from "react-syntax-highlighter";
import { useHistory } from "react-router-dom";
import sql from "react-syntax-highlighter/dist/esm/languages/hljs/sql";
import json from "react-syntax-highlighter/dist/esm/languages/hljs/json";
import { docco } from "react-syntax-highlighter/dist/esm/styles/hljs";
import moment from "moment";

import PublishIcon from "@material-ui/icons/Publish";
import GetAppIcon from "@material-ui/icons/GetApp";

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
                  color={theme.palette.type === "light" ? "primary" : "default"}
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
                  color={theme.palette.type === "light" ? "primary" : "default"}
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
            >
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
            >
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
