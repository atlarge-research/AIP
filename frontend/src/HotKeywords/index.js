import React, { useState } from "react";
import { apiCall } from "./apiCall";
import {
  IconButton,
  Typography,
  Box,
  LinearProgress,
  TextField,
  Button,
  Tooltip,
} from "@material-ui/core";
import InfoIcon from "@material-ui/icons/Info";

import FormControlLabel from "@material-ui/core/FormControlLabel";
import Checkbox from "@material-ui/core/Checkbox";
import routes from "../routes";
import { useHistory } from "react-router-dom";
import defaultValues from "../VisualQuerying/filterDefaultValues";
import Table from "@material-ui/core/Table";
import TableBody from "@material-ui/core/TableBody";
import TableCell from "@material-ui/core/TableCell";
import TableContainer from "@material-ui/core/TableContainer";
import TableHead from "@material-ui/core/TableHead";
import TableRow from "@material-ui/core/TableRow";
import Paper from "@material-ui/core/Paper";

import InfoDialog from "./InfoDialog";

const HotKeywords = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);

  const [year, setYear] = useState(new Date().getFullYear());

  const [p_rate, setP_rate] = useState("0.01");
  const [c_rate, setC_rate] = useState("0.05");
  const [r_adjustment, setR_adjustment] = useState(true);
  const [number_of_features, setNumber_of_features] = useState("10");
  const [r_min, setR_min] = useState("5");
  const [dt, setDt] = useState("5");

  const [showAdvanced, setShowAdvanced] = useState(false);

  const [showInfo, setShowInfo] = useState(false);

  const history = useHistory();

  const getKeywords = () => {
    if (!year) return;
    setLoading(true);

    (showAdvanced
      ? apiCall(
          year,
          p_rate,
          c_rate,
          r_adjustment,
          number_of_features,
          r_min,
          dt
        )
      : apiCall(year)
    )
      .then((res) => res.json())
      .then((d) => {
        setLoading(false);
        setData(d);
      })
      .catch((e) => {
        setLoading(false);
        console.error(e);
      });
  };

  const goToKeyword = (keyword) => {
    history.push({
      pathname: routes.visualQuerying,
      state: {
        filterQuery: { ...defaultValues, abstract_keywords: [keyword] },
      },
    });
  };

  return (
    <div>
      <InfoDialog showInfo={showInfo} setShowInfo={setShowInfo} />
      <Box my={3} justifyContent="space-between" display="flex">
        <Typography variant="h4">Hot Keywords</Typography>
        <Tooltip title="Show algorithm description" aria-label="info">
          <IconButton
            variant="contained"
            onClick={() => setShowInfo(true)}
            aria-label="show sql quries"
          >
            <InfoIcon />
          </IconButton>
        </Tooltip>
      </Box>
      <Box mb={2}>
        <TextField
          label="Year"
          value={year}
          onChange={(e) => setYear(e.target.value)}
          variant="outlined"
          type="number"
          size="small"
        />
        <Button
          color="primary"
          onClick={() => getKeywords()}
          variant="contained"
          style={{ height: 40, marginLeft: 12 }}
        >
          Search
        </Button>
        <Box ml={2} display="inline-block">
          <FormControlLabel
            control={
              <Checkbox
                color="primary"
                checked={showAdvanced}
                onChange={(e) => setShowAdvanced(e.target.checked)}
              />
            }
            label="Show advanced options"
          />
        </Box>
      </Box>
      {showAdvanced && (
        <Box
          mb={2}
          display="flex"
          justifyContent="space-between"
          flexWrap="wrap"
          style={{ gap: "5px" }}
        >
          <Box ml={2} display="inline-block">
            <FormControlLabel
              control={
                <Checkbox
                  color="primary"
                  checked={r_adjustment}
                  onChange={(e) => setR_adjustment(e.target.checked)}
                />
              }
              label="r_adjustment"
            />
          </Box>
          <TextField
            label="p_rate"
            value={p_rate}
            onChange={(e) => setP_rate(e.target.value)}
            variant="outlined"
            type="number"
            size="small"
            max="1"
            min="0"
          />
          <TextField
            label="c_rate"
            value={c_rate}
            onChange={(e) => setC_rate(e.target.value)}
            variant="outlined"
            type="number"
            size="small"
          />
          <TextField
            label="number_of_features"
            value={number_of_features}
            onChange={(e) => setNumber_of_features(e.target.value)}
            variant="outlined"
            type="number"
            size="small"
          />
          <TextField
            label="r_min"
            value={r_min}
            onChange={(e) => setR_min(e.target.value)}
            variant="outlined"
            type="number"
            size="small"
          />
          <TextField
            label="dt"
            value={dt}
            onChange={(e) => setDt(e.target.value)}
            variant="outlined"
            type="number"
            size="small"
          />
        </Box>
      )}
      {loading && <LinearProgress />}
      {data && !loading && (
        <TableContainer component={Paper} style={{ marginBottom: "12px" }}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Keyword</TableCell>
                <TableCell>Publications</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {data.map((keyword, i) => (
                <TableRow key={i}>
                  <TableCell>{keyword}</TableCell>
                  <TableCell>
                    <Button
                      variant="outlined"
                      color="primary"
                      onClick={() => goToKeyword(keyword)}
                    >
                      Show publications
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}
    </div>
  );
};

export default HotKeywords;
