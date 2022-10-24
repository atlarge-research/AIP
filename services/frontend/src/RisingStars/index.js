import React, { useState } from "react";
import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";
import { LinearProgress } from "@mui/material";
import { DataGrid } from "@mui/x-data-grid";
import TextField from "@mui/material/TextField";
import Button from "@mui/material/Button";
import InputLabel from "@mui/material/InputLabel";
import MenuItem from "@mui/material/MenuItem";
import FormControl from "@mui/material/FormControl";
import Select from "@mui/material/Select";
import {
  OutlinedInput,
  InputAdornment,
  IconButton,
  Paper,
  Chip,
} from "@mui/material";
import { makeStyles } from "@mui/styles";
import AddIcon from "@mui/icons-material/Add";

import { apiCall } from "./apiCall";

const columns = [
  { field: "id", headerName: "Ranking", width: 130 },
  { field: "author_id", headerName: "ID" },
  { field: "author_name", headerName: "Name", width: 200 },
  { field: "z_score", headerName: "z-score", type: "number", width: 150 },
  {
    field: "first_publication",
    headerName: "Year of the first publication",
    width: 300,
  },
];

const useStyles = makeStyles((theme) => ({
  chip: {
    margin: theme.spacing(0.5),
  },
  chipList: {
    display: "flex",
    justifyContent: "center",
    flexWrap: "wrap",
    listStyle: "none",
    padding: 0,
    margin: 0,
    width: "100%",
    gridColumn: "1 / -1",
    marginLeft: "12px",
  },
}));

const RisingStars = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [number, setNumber] = useState(100);
  const [type, setType] = useState("");
  const [algo, setAlgo] = useState("");
  const [year, setYear] = useState(new Date().getFullYear());
  const [newKeyword, setNewKeyword] = useState("");
  const [keywords, setKeywords] = useState([]);

  const [error, setError] = useState(null);

  const classes = useStyles();

  const getStars = () => {
    setLoading(true);
    apiCall(year, number, type, algo, keywords)
      .then((res) => res.json())
      .then((d) => {
        setLoading(false);
        setData(d.map((row, i) => ({ ...row, id: i + 1 })));
      })
      .catch((e) => {
        setLoading(false);
        setError(e);
      });
  };

  const addKeyword = (keyword) => {
    if (keywords.includes(keyword) && !keyword) return setNewKeyword("");
    setKeywords([
      ...keywords,
      ...newKeyword
        .replace(/,/g, "")
        .split(/[ ,]+/)
        .filter((k) => !keywords.includes(k) && k),
    ]);
    setNewKeyword("");
  };

  return (
    <div>
      <Box my={3}>
        <Typography variant="h4">Rising Stars</Typography>
      </Box>

      <Box mb={2}>
        <FormControl size="small" variant="outlined">
          <InputLabel id="demo-simple-select-outlined-label">
            Algorithm Type
          </InputLabel>
          <Select
            value={type}
            onChange={(e) => {
              setType(e.target.value);
            }}
            label="Algorithm Type"
            size="small"
            style={{ width: "158px" }}
          >
            <MenuItem value="global">Global</MenuItem>
            <MenuItem value="local">Local</MenuItem>
          </Select>
        </FormControl>
        <FormControl
          size="small"
          variant="outlined"
          style={{ marginLeft: 12, width: "188px" }}
        >
          <InputLabel id="demo-simple-select-outlined-label">
            Algorithm Selection
          </InputLabel>
          <Select
            labelId="demo-simple-select-outlined-label"
            id="demo-simple-select-outlined"
            value={algo}
            onChange={(e) => setAlgo(e.target.value)}
            label="Algorithm Selection"
            size="small"
            disabled={!type}
          >
            <MenuItem value="basic">Basic</MenuItem>
            <MenuItem value="clusters">Clustering</MenuItem>
            <MenuItem value="pagerank">Page rank</MenuItem>
          </Select>
        </FormControl>
        <TextField
          label="From year"
          value={year}
          onChange={(e) => setYear(e.target.value)}
          variant="outlined"
          style={{ marginLeft: 12 }}
          size="small"
          disabled={!algo}
        />
        <TextField
          label="Number of results"
          value={number}
          onChange={(e) => setNumber(e.target.value)}
          variant="outlined"
          size="small"
          style={{ marginLeft: 12 }}
          disabled={!algo}
        />
        <Button
          color="primary"
          onClick={() => getStars()}
          variant="contained"
          style={{ height: 40, marginLeft: 12 }}
          disabled={!algo || (type === "local" && !keywords.length)}
        >
          Search
        </Button>
      </Box>
      {type === "local" && algo && (
        <Box display="flex" alignItems="center" mb={2}>
          <FormControl variant="outlined" size="small">
            <OutlinedInput
              id="new-keyword"
              value={newKeyword}
              onChange={(e) => setNewKeyword(e.target.value)}
              placeholder="Enter the keyword"
              onKeyPress={(event) => {
                if (event.key === "Enter") addKeyword();
              }}
              endAdornment={
                <InputAdornment position="end">
                  <IconButton onClick={() => addKeyword()} edge="end" size="large">
                    <AddIcon />
                  </IconButton>
                </InputAdornment>
              }
            />
          </FormControl>
          {keywords.length > 0 && (
            <Paper component="ul" className={classes.chipList}>
              {keywords.map((name, i) => (
                <li key={i}>
                  <Chip
                    className={classes.chip}
                    label={name}
                    onDelete={() =>
                      setKeywords([...keywords.filter((k) => k !== name)])
                    }
                  />
                </li>
              ))}
            </Paper>
          )}
        </Box>
      )}
      {loading && <LinearProgress />}
      {!loading && data ? (
        <div
          style={{ height: "max(400px, calc(100vh - 250px))", width: "100%" }}
        >
          <DataGrid hideFooterPagination columns={columns} rows={data} />
        </div>
      ) : null}
      {error && <Typography>{error}</Typography>}
    </div>
  );
};

export default RisingStars;

// http://localhost:8000/api/rising-stars?first_year=2019
