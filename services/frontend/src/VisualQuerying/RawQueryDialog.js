import React, { useState } from "react";
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Box,
  Alert,
} from "@mui/material";

import { makeStyles } from "@mui/styles";

const useStyles = makeStyles((_) => ({
  input: {
    width: "100%",
  },
}));

const RawQueryDialog = ({ opened, setOpened, onSubmit, error }) => {
  const [rawQuery, setQuery] = useState("");

  const classes = useStyles();

  return (
    <Dialog
      open={opened}
      onClose={() => setOpened(false)}
      className={classes.dialog}
      fullWidth
      maxWidth="lg"
    >
      <DialogTitle>Enter the SQL Query</DialogTitle>
      <DialogContent>
        <TextField
          label="SQL Query"
          value={rawQuery}
          onChange={(e) => setQuery(e.target.value)}
          variant="outlined"
          multiline
          className={classes.input}
        />
        {error && (
          <Box mt={1} mb={1}>
            <Alert elevation={6} variant="filled" severity="error">
              {error}
            </Alert>
          </Box>
        )}
      </DialogContent>
      <DialogActions>
        <Button
          onClick={() => {
            setOpened(false);
          }}
          color="primary"
        >
          Cancel
        </Button>
        <Button
          color="primary"
          onClick={() => {
            onSubmit(rawQuery);
            setOpened(false);
          }}
        >
          Execute
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default RawQueryDialog;
