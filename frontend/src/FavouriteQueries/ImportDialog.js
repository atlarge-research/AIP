import React, { useState } from "react";
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Box,
} from "@material-ui/core";

const ImportDialog = ({ showID, setShowID, onSave }) => {
  const [selectedFile, setSelectedFile] = useState("");
  const [error, setError] = useState(null);

  const processFile = () => {
    selectedFile
      .text()
      .then((d) => {
        onSave(JSON.parse(d).queries);
        setSelectedFile("");
        setError(null);
        setShowID(false);
      })
      .catch((e) => setError(e));
  };

  return (
    <Dialog open={showID} onClose={() => setShowID(false)}>
      <DialogTitle>Import </DialogTitle>
      <DialogContent>
        {error && <Box>{error}</Box>}
        <Button variant="contained" component="label">
          Upload File
          <input
            type="file"
            hidden
            accept=".json"
            onChange={(e) => {
              console.log(e.target.files);
              setSelectedFile(e.target.files[0]);
            }}
          />
        </Button>
      </DialogContent>
      <DialogActions>
        <Button color="primary" onClick={() => setShowID(false)}>
          Close
        </Button>
        <Button
          color="primary"
          onClick={() => processFile()}
          disabled={!selectedFile}
        >
          Save
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default ImportDialog;
