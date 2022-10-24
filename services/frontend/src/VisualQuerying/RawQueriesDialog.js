import React from "react";
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Typography,
} from "@mui/material";
import { Light as SyntaxHighlighter } from "react-syntax-highlighter";
import sql from "react-syntax-highlighter/dist/esm/languages/hljs/sql";
import { docco } from "react-syntax-highlighter/dist/esm/styles/hljs";

const RawQueriesDialog = ({
  showRawQueries,
  setShowRawQueries,
  rawQueries,
}) => {
  const codeStyles = docco;
  codeStyles.hljs.overflowX = "hidden";
  SyntaxHighlighter.registerLanguage("sql", sql);

  const db_version = localStorage.getItem("db_version");

  return (
    <Dialog open={showRawQueries} onClose={() => setShowRawQueries(false)}>
      <DialogTitle>SQL Queries executed</DialogTitle>
      <DialogContent>
        {db_version && (
          <Typography variant="body1">
            Database version is {db_version}.
          </Typography>
        )}
        {rawQueries &&
          rawQueries.map((query, i) => (
            <SyntaxHighlighter
              key={i}
              style={codeStyles}
              language="sql"
              wrapLongLines
            >
              {query.sql}
            </SyntaxHighlighter>
          ))}
      </DialogContent>
      <DialogActions>
        <Button
          color="primary"
          onClick={() => {
            setShowRawQueries(false);
          }}
        >
          Close
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default RawQueriesDialog;
