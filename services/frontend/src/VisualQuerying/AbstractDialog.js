import React from "react";
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
} from "@material-ui/core";

const AbstractDialog = ({ showAbstract, setShowAbstract, currentArticle }) => {
  return (
    <Dialog open={showAbstract} onClose={() => setShowAbstract(false)}>
      <DialogTitle>
        {currentArticle &&
          `Abstract of ${currentArticle.title} (${currentArticle.year}) ${
            currentArticle.name ? "by " + currentArticle.name : ""
          }`}
      </DialogTitle>
      <DialogContent>{currentArticle && currentArticle.abstract}</DialogContent>
      <DialogActions>
        <Button
          color="primary"
          onClick={() => {
            setShowAbstract(false);
          }}
        >
          Close
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default AbstractDialog;
