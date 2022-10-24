import React from "react";
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
} from "@mui/material";
import schemaIMG from "./db_schema_client.png";

const SchemaDialog = ({ showSchema, setShowSchema }) => {
  return (
    <Dialog
      open={showSchema}
      fullWidth
      maxWidth="md"
      onClose={() => setShowSchema(false)}
    >
      <DialogTitle>Schema of the database</DialogTitle>
      <DialogContent>
        <img src={schemaIMG} alt="Schema" style={{ width: "100%" }} />
      </DialogContent>
      <DialogActions>
        <Button
          color="primary"
          onClick={() => {
            setShowSchema(false);
          }}
        >
          Close
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default SchemaDialog;
