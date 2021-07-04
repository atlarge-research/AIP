import React, { useMemo } from "react";
import { useHistory } from "react-router-dom";
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from "@material-ui/core";
import { DataGrid } from "@material-ui/data-grid";
import Button from "@material-ui/core/Button";
import routes from "../routes";
import defaultValues from "../VisualQuerying/filterDefaultValues";
import { makeStyles } from "@material-ui/core/styles";

const useStyles = makeStyles(() => ({
  dialog: {
    width: "min(680px, 100vh)",
    maxWidth: "none",
  },
}));

const DetailsDialog = ({
  showDetails,
  setShowDetails,
  author,
  addAuthor,
  data,
  rootNodes,
}) => {
  const classes = useStyles();

  const history = useHistory();

  const searchPublications = () => {
    history.push({
      pathname: routes.visualQuerying,
      state: { filterQuery: { ...defaultValues, author_names: [author] } },
    });
  };

  const descriptions = useMemo(() => {
    if (!data) return null;
    let texts = [];
    texts = [
      ...data.citation_edges
        .filter((cits) => cits[0] === author || cits[1] === author)
        .map((cits, i) => ({
          id: i,
          source: cits[0],
          type: "cited",
          target: cits[1],
          times: cits[2],
        })),
    ];
    texts = [
      ...texts,
      ...data.coauthorship_edges
        .filter((cits) => cits[0] === author || cits[1] === author)
        .map((cits, i) => ({
          id: i + data.citation_edges.length,
          source: cits[0],
          type: "coauthored with",
          target: cits[1],
          times: cits[2],
        })),
    ];
    return texts;
  }, [author, data]);

  return (
    <Dialog
      open={showDetails}
      onClose={() => setShowDetails(false)}
      style={{ maxWidth: "none" }}
      maxWidth="xl"
    >
      <DialogTitle className={classes.dialog}>
        Connections of {author}
      </DialogTitle>
      <DialogContent>
        <div style={{ height: 400, width: "100%" }}>
          {descriptions && (
            <DataGrid
              rows={descriptions}
              columns={[
                { field: "source", headerName: "Source", width: 150 },
                { field: "type", headerName: "Connection", width: 150 },
                { field: "target", headerName: "Target", width: 150 },
                { field: "times", headerName: "Times", width: 150 },
              ]}
            />
          )}
        </div>
      </DialogContent>
      <DialogActions>
        {!rootNodes.includes(author) && (
          <Button
            color="primary"
            onClick={() => {
              addAuthor(author);
              setShowDetails(false);
            }}
          >
            Add author's connections to the graph
          </Button>
        )}
        <Button color="primary" onClick={searchPublications}>
          Show author's publications
        </Button>
        <Button
          color="primary"
          onClick={() => {
            setShowDetails(false);
          }}
        >
          Close
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default DetailsDialog;
