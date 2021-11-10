import React, { useState, useEffect } from "react";
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Typography,
  Box,
  TextField,
  Slider,
  Paper,
  Chip,
  FormControl,
  OutlinedInput,
  InputAdornment,
  IconButton,
  Switch,
  makeStyles,
} from "@material-ui/core";
import AddIcon from "@material-ui/icons/Add";
import { YEAR_MIN, CITATIONS_MAX } from "../config";

const useStyles = makeStyles((theme) => ({
  form: {
    display: "grid",
    gridTemplateColumns: "1fr 1fr",
    gap: "10px",
  },
  wholeRow: {
    gridColumn: "1 / -1",
  },
  chipList: {
    display: "flex",
    justifyContent: "center",
    flexWrap: "wrap",
    listStyle: "none",
    padding: theme.spacing(0.5),
    margin: 0,
    width: "100%",
    gridColumn: "1 / -1",
  },
  chip: {
    margin: theme.spacing(0.5),
  },
}));

const FiltersDialog = ({
  filtersOpen,
  setFiltersOpen,
  filters,
  setFilters,
}) => {
  const classes = useStyles();

  const onFormChange = (field, value) => {
    const data = { ...formValues };
    data[field] = value;
    setFormValues(data);
  };

  const [formValues, setFormValues] = useState({ ...filters });

  useEffect(() => {
    setFormValues({ ...filters });
  }, [filters]);

  const [newAuthor, setNewAuthor] = useState("");

  const [newKeyword, setNewKeyword] = useState("");

  const [yearActive, setYearActive] = useState(!!formValues.year);

  const [n_citationsActive, setN_citationsActive] = useState(
    !!filters.n_citations
  );

  useEffect(() => {
    if (!filtersOpen && !filters.n_citations) setN_citationsActive(false);
    if (!filtersOpen && !filters.year) setYearActive(false);
  }, [filtersOpen]);

  return (
    <Dialog open={filtersOpen} onClose={() => setFiltersOpen(false)}>
      <DialogTitle>Filter Publications</DialogTitle>
      <DialogContent>
        <form className={classes.form}>
          <TextField
            label="ID"
            value={formValues.id}
            onChange={(e) => onFormChange("id", e.target.value)}
            variant="outlined"
            className={classes.wholeRow}
          />
          <TextField
            label="Title"
            value={formValues.title}
            onChange={(e) => onFormChange("title", e.target.value)}
            variant="outlined"
          />
          <TextField
            label="DOI"
            value={formValues.doi}
            onChange={(e) => onFormChange("doi", e.target.value)}
            variant="outlined"
          />
          <TextField
            label="Venue"
            value={formValues.venue}
            onChange={(e) => onFormChange("venue", e.target.value)}
            variant="outlined"
          />
          <TextField
            label="Volume"
            value={formValues.volume}
            onChange={(e) => onFormChange("volume", e.target.value)}
            variant="outlined"
          />

          <Typography gutterBottom>Names of the Authors</Typography>
          <FormControl variant="outlined" className={classes.wholeRow}>
            <OutlinedInput
              id="new-author"
              value={newAuthor}
              onChange={(e) => setNewAuthor(e.target.value)}
              placeholder="Enter the name of the author"
              onKeyPress={(event) => {
                if (event.key === "Enter" && newAuthor) {
                  if (formValues.author_names.includes(newAuthor))
                    return setNewAuthor("");
                  onFormChange("author_names", [
                    ...formValues.author_names,
                    newAuthor.replace(/,/g, ""),
                  ]);
                  setNewAuthor("");
                }
              }}
              endAdornment={
                <InputAdornment position="end">
                  <IconButton
                    onClick={() => {
                      if (
                        formValues.author_names.includes(newAuthor) ||
                        !newAuthor
                      )
                        return setNewAuthor("");
                      onFormChange("author_names", [
                        ...formValues.author_names,
                        newAuthor.replace(/,/g, ""),
                      ]);
                      setNewAuthor("");
                    }}
                    edge="end"
                  >
                    <AddIcon />
                  </IconButton>
                </InputAdornment>
              }
            />
          </FormControl>
          {formValues.author_names.length > 0 && (
            <Paper component="ul" className={classes.chipList}>
              {formValues.author_names.map((name, i) => (
                <li key={i}>
                  <Chip
                    className={classes.chip}
                    label={name}
                    onDelete={() =>
                      onFormChange(
                        "author_names",
                        formValues.author_names.filter((el) => el !== name)
                      )
                    }
                  />
                </li>
              ))}
            </Paper>
          )}

          <Typography gutterBottom>Keywords</Typography>
          <FormControl variant="outlined" className={classes.wholeRow}>
            <OutlinedInput
              id="new-keyword"
              value={newKeyword}
              onChange={(e) => setNewKeyword(e.target.value)}
              placeholder="Enter the keyword"
              onKeyPress={(event) => {
                if (event.key === "Enter") {
                  if (formValues.abstract_keywords.includes(newAuthor))
                    return setNewKeyword("");
                  onFormChange("abstract_keywords", [
                    ...formValues.abstract_keywords,
                    ...newKeyword
                      .replace(/,/g, "")
                      .split(/[ ,]+/)
                      .filter(
                        (k) => !formValues.abstract_keywords.includes(k) && k
                      ),
                  ]);
                  setNewKeyword("");
                }
              }}
              endAdornment={
                <InputAdornment position="end">
                  <IconButton
                    onClick={() => {
                      if (formValues.abstract_keywords.includes(newAuthor))
                        return setNewKeyword("");
                      onFormChange("abstract_keywords", [
                        ...formValues.abstract_keywords,
                        ...newKeyword
                          .replace(/,/g, "")
                          .split(/[ ,]+/)
                          .filter(
                            (k) =>
                              !formValues.abstract_keywords.includes(k) && k
                          ),
                      ]);
                      setNewKeyword("");
                    }}
                    edge="end"
                  >
                    <AddIcon />
                  </IconButton>
                </InputAdornment>
              }
            />
          </FormControl>
          {formValues.abstract_keywords.length > 0 && (
            <Paper component="ul" className={classes.chipList}>
              {formValues.abstract_keywords.map((name, i) => (
                <li key={i}>
                  <Chip
                    className={classes.chip}
                    label={name}
                    onDelete={() =>
                      onFormChange(
                        "abstract_keywords",
                        formValues.abstract_keywords.filter((el) => el !== name)
                      )
                    }
                  />
                </li>
              ))}
            </Paper>
          )}

          <Box className={classes.wholeRow} mt={1}>
            <Typography id="discrete-slider-custom" gutterBottom>
              <Switch
                onChange={(e) => {
                  if (e.target.checked) {
                    setYearActive(true);
                    onFormChange("year", [YEAR_MIN, new Date().getFullYear()]);
                  } else {
                    setYearActive(false);
                    onFormChange("year", null);
                  }
                }}
                checked={yearActive}
                color="primary"
              />
              Year of Publication
            </Typography>
            {yearActive && (
              <Slider
                valueLabelDisplay="auto"
                aria-labelledby="range-slider"
                min={YEAR_MIN}
                max={new Date().getFullYear()}
                value={formValues.year}
                onChange={(_, d) => onFormChange("year", d)}
              />
            )}
          </Box>
          <Box className={classes.wholeRow} mt={1}>
            <Typography id="discrete-slider-custom" gutterBottom>
              <Switch
                onChange={(e) => {
                  if (e.target.checked) {
                    setN_citationsActive(true);
                    onFormChange("n_citations", [0, CITATIONS_MAX]);
                  } else {
                    setN_citationsActive(false);
                    onFormChange("n_citations", null);
                  }
                }}
                checked={n_citationsActive}
                color="primary"
              />
              Number of Citations
            </Typography>
          </Box>
          {n_citationsActive && formValues.n_citations && (
            <>
              <TextField
                label="Min citations"
                type="number"
                value={formValues.n_citations[0]}
                onChange={(e) => {
                  onFormChange("n_citations", [
                    e.target.value,
                    formValues.n_citations[1],
                  ]);
                }}
                variant="outlined"
                min={0}
                max={formValues.n_citations[1]}
              />
              <TextField
                label="Max citations"
                type="number"
                value={formValues.n_citations[1]}
                onChange={(e) => {
                  onFormChange("n_citations", [
                    formValues.n_citations[0],
                    e.target.value,
                  ]);
                }}
                variant="outlined"
                min={formValues.n_citations[0]}
                max={CITATIONS_MAX}
              />
            </>
          )}
        </form>
      </DialogContent>
      <DialogActions>
        <Button
          onClick={() => {
            setFiltersOpen(false);
            setFormValues({ ...filters });
          }}
          color="primary"
        >
          Cancel
        </Button>
        <Button
          color="primary"
          onClick={() => {
            setFiltersOpen(false);
            setFilters({ ...formValues });
          }}
        >
          Search
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default FiltersDialog;
