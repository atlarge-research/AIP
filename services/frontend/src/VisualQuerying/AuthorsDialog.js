import React from "react";
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Table,
  TableContainer,
  TableHead,
  TableBody,
  TableRow,
  TableCell,
  Paper,
  Link
} from "@mui/material";

const AuthorsDialog = ({
  showAuthors,
  setShowAuthors,
  currentArticle,
  filterByAuthor,
}) => {
  return (
    <Dialog open={showAuthors} onClose={() => setShowAuthors(false)}>
      <DialogTitle>
        {currentArticle &&
          `Authors of ${currentArticle.title} (${currentArticle.year})`}
      </DialogTitle>
      <DialogContent>
        <TableContainer component={Paper}>
          <Table size="small" aria-label="a dense table">
            <TableHead>
              <TableRow>
                <TableCell>Name</TableCell>
                <TableCell>ORCID</TableCell>
                <TableCell>Year of the first publication</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {currentArticle.authors.map((row, id) => (
                <TableRow key={id} style={{ cursor: "pointer" }}>
                  <TableCell
                    onClick={() => {
                      setShowAuthors(false);
                      filterByAuthor(row.name);
                    }}
                  >
                    {row.name ? row.name : "-"}
                  </TableCell>
                  <TableCell style={{ width: "200px" }}>
                    {row.orcid ? (
                      <Link
                        href={"https://orcid.org/" + row.orcid}
                        target="__blank"
                      >
                        {row.orcid}
                      </Link>
                    ) : (
                      "-"
                    )}
                  </TableCell>
                  <TableCell>
                    {row.first_publication_year
                      ? row.first_publication_year
                      : "-"}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </DialogContent>
      <DialogActions>
        <Button
          color="primary"
          onClick={() => {
            setShowAuthors(false);
          }}
        >
          Close
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default AuthorsDialog;
