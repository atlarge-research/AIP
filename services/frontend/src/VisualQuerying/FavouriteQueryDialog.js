import React, { useState } from "react";
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
} from "@mui/material";

import { makeStyles } from "@mui/styles";

const useStyles = makeStyles(() => ({
  input: {
    width: "100%",
  },
}));

const FavouriteQueryDialog = ({ showFQD, setShowFDQ, onSave }) => {
  const [name, setName] = useState("");
  const classes = useStyles();

  return (
    <Dialog open={showFQD} onClose={() => setShowFDQ(false)}>
      <DialogTitle>Set the name of favourite query</DialogTitle>
      <DialogContent>
        <TextField
          label="Name of the query"
          value={name}
          onChange={(e) => setName(e.target.value)}
          className={classes.input}
        />
      </DialogContent>
      <DialogActions>
        <Button
          color="primary"
          onClick={() => {
            setShowFDQ(false);
          }}
        >
          Close
        </Button>
        <Button
          color="primary"
          onClick={() => {
            setShowFDQ(false);
            onSave(name);
            setName("");
          }}
          disabled={!name}
        >
          Save
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default FavouriteQueryDialog;
