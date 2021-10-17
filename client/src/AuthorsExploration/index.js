import React, { useState, useEffect, useRef } from "react";
import Box from "@material-ui/core/Box";
import Typography from "@material-ui/core/Typography";
import { LinearProgress } from "@material-ui/core";
import Snackbar from "@material-ui/core/Snackbar";
import MuiAlert from "@material-ui/lab/Alert";
import TextField from "@material-ui/core/TextField";
import Button from "@material-ui/core/Button";
import { apiCall } from "./apiCall";
import * as d3 from "d3";
import { linkArc } from "./d3functions";
import useTheme from "@material-ui/core/styles/useTheme";
import DetailsDialog from "./DetailsDialog";
import InputLabel from "@material-ui/core/InputLabel";
import FormControl from "@material-ui/core/FormControl";
import Select from "@material-ui/core/Select";
import MenuItem from "@material-ui/core/MenuItem";

import { makeStyles } from "@material-ui/core/styles";

const useStyles = makeStyles(() => ({
  formControl: {
    minWidth: 120,
  },
  topElem: {
    height: 48,
  },
}));

const types = ["cited", "coauthored with"];

const AuthorsExploration = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [name, setName] = useState("");
  const [width, setWidth] = useState(400);

  const [filter, setFilter] = useState(null);
  const [resultLimit, setResultLimit] = useState(1);

  const [author, setAuthor] = useState("");
  const [showDetails, setShowDetails] = useState(false);

  const [alertOpened, setAlertOpened] = useState(false);
  const [alert, setAlert] = useState("");
  const closeAlert = () => setAlertOpened(false);

  const [rootNodes, setRootNodes] = useState([]);

  const classes = useStyles();

  useEffect(() => {
    if (alert) setAlertOpened(true);
  }, [alert]);

  const allowFiltering =
    data &&
    (!filter
      ? data.citation_nodes.length + data.coauthorship_nodes.length > 49
      : filter === types[0]
      ? data.citation_nodes.length > 49
      : data.coauthorship_nodes.length > 49);

  const getGraph = () => {
    if (!name) return;
    setLoading(true);
    apiCall(name)
      .then((res) => {
        if (res.status !== 200) {
          return setAlert(
            name + "'s connections weren't found in the database."
          );
        }

        return res.json();
      })
      .then((d) => {
        setRootNodes([name]);
        setLoading(false);
        setData(d);
      })
      .catch((e) =>
        setAlert(name + "'s connections weren't found in the database. " + e)
      );
  };

  const addAuthor = (authorName) => {
    apiCall(authorName)
      .then((res) => res.json())
      .then((d) => {
        setRootNodes([...rootNodes, authorName]);
        setLoading(false);
        setData({
          citation_nodes: [...data.citation_nodes, ...d.citation_nodes].sort(
            (a, b) => b[1] - a[1]
          ),
          coauthorship_nodes: [
            ...data.coauthorship_nodes,
            ...d.coauthorship_nodes,
          ].sort((a, b) => b[1] - a[1]),
          citation_edges: [
            ...data.citation_edges,
            ...d.citation_edges.filter(
              (d) =>
                !data.citation_edges.reduce(
                  (acc, val) => shallowEqual(d, val) || acc,
                  false
                )
            ),
          ],
          coauthorship_edges: [
            ...data.coauthorship_edges,
            ...d.coauthorship_edges.filter(
              (d) =>
                !data.coauthorship_edges.reduce(
                  (acc, val) => shallowEqual(d, val) || acc,
                  false
                )
            ),
          ],
        });
      })
      .catch((e) =>
        setAlert(name + "'s connections weren't found in the database. " + e)
      );
  };

  const svgRef = useRef();
  const containerRef = useRef();
  const theme = useTheme();

  useEffect(() => {
    if (!containerRef.current) return;
    setWidth(containerRef.current.offsetWidth);

    const onResize = (e) => {
      setWidth(containerRef.current.offsetWidth);
    };

    window.addEventListener("resize", onResize);

    return () => window.removeEventListener("resize", onResize);
  }, [containerRef.current]);

  const color = d3.scaleOrdinal(types, d3.schemeCategory10);

  useEffect(() => {
    if (!data || !svgRef.current) return;
    d3.selectAll("svg#community > *").remove();
    const svg = d3.select(svgRef.current).attr("id", "community");
    const mother = svg.append("g");

    const nodesSet = new Set(rootNodes);

    let maxWeight = 0;
    const weights = new Map();

    const citsNodesLimit = allowFiltering
      ? Math.round(resultLimit * data.citation_nodes.length)
      : data.citation_nodes.length;
    let citsCntr = 0;
    if (!filter || filter !== types[1])
      data.citation_nodes.forEach((d) => {
        if (citsCntr > citsNodesLimit) return;
        citsCntr++;
        nodesSet.add(d[0]);
        weights.set(d[0], d[1]);
        maxWeight = Math.max(maxWeight, d[1]);
      });

    const coNodesLimit = allowFiltering
      ? Math.round(resultLimit * data.coauthorship_nodes.length)
      : data.coauthorship_nodes.length;
    let coCntr = 0;
    if (!filter || filter !== types[0])
      data.coauthorship_nodes.forEach((d) => {
        if (coCntr > coNodesLimit) return;
        coCntr++;
        nodesSet.add(d[0]);
        weights.set(d[0], d[1]);
        maxWeight = Math.max(maxWeight, d[1]);
      });

    const nodes = Array.from(nodesSet).map((n) => ({
      id: n,
      weight: weights.get(n),
    }));

    let links = [];

    if (!filter || filter !== types[1])
      links = [
        ...links,
        ...data.citation_edges
          .filter((d) => nodesSet.has(d[0]) && nodesSet.has(d[1]))
          .map((d) => ({ source: d[0], target: d[1], type: types[0] })),
      ];

    if (!filter || filter !== types[0])
      links = [
        ...links,
        ...data.coauthorship_edges
          .filter((d) => nodesSet.has(d[0]) && nodesSet.has(d[1]))
          .map((d) => ({ source: d[0], target: d[1], type: types[1] })),
      ];

    const height = 600;

    svg
      .attr("viewBox", [0, 0, width, height])
      .attr("width", width)
      .attr("height", height)
      .style("font", "12px sans-serif")
      .call(
        d3
          .zoom()
          .extent([
            [0, 0],
            [width, height],
          ])
          .on("zoom", function (e) {
            mother.attr("transform", e.transform);
          })
      );

    // Per-type markers, as they don't inherit styles.
    svg
      .append("defs")
      .selectAll("marker")
      .data(types)
      .join("marker")
      .attr("id", (d) => `arrow-${d}`)
      .attr("viewBox", "0 -5 10 10")
      .attr("refX", 15)
      .attr("refY", -0.5)
      .attr("markerWidth", 10)
      .attr("markerHeight", 6)
      .attr("orient", "auto")
      .append("path")
      .attr("fill", color)
      .attr("d", "M0,-5L10,0L0,5");

    if (!filter || filter !== types[1])
      svg
        .append("rect")
        .attr("x", 24)
        .attr("y", 24)
        .attr("width", 12)
        .attr("height", 12)
        .attr("stroke-width", "3px")
        .attr("stroke", "white")
        .style("fill", color(types[0]));
    if (!filter || filter !== types[0])
      svg
        .append("rect")
        .attr("x", 24)
        .attr("y", 44)
        .attr("width", 12)
        .attr("height", 12)
        .attr("stroke-width", "3px")
        .attr("stroke", "white")
        .style("fill", color(types[1]));
    if (!filter || filter !== types[1])
      svg
        .append("text")
        .attr("x", 50)
        .attr("y", 30)
        .text(types[0])
        .attr("stroke-width", "3px")
        .attr("stroke", "white")
        .style("font-size", "15px")
        .attr("alignment-baseline", "middle")
        .style("paint-order", "stroke");
    if (!filter || filter !== types[0])
      svg
        .append("text")
        .attr("x", 50)
        .attr("y", 50)
        .text(types[1])
        .attr("stroke-width", "3px")
        .attr("stroke", "white")
        .style("font-size", "15px")
        .attr("alignment-baseline", "middle")
        .style("paint-order", "stroke");

    const link = mother
      .append("g")
      .attr("fill", "none")
      .attr("stroke-width", 1.5)
      .selectAll("path")
      .data(links)
      .join("path")
      .attr("stroke", (d) => color(d.type))
      .attr("marker-end", (d) => `url(${`#arrow-${d.type}`})`);

    const node = mother
      .append("g")
      .attr("fill", "currentColor")
      .attr("stroke-linecap", "round")
      .attr("stroke-linejoin", "round")
      .selectAll("g")
      .data(nodes)
      .join("g");

    function ticked() {
      link
        .attr("x1", function (d) {
          return d.source.x;
        })
        .attr("y1", function (d) {
          return d.source.y;
        })
        .attr("x2", function (d) {
          return d.target.x;
        })
        .attr("y2", function (d) {
          return d.target.y;
        })
        .attr("d", linkArc);
      node
        .attr("cx", function (d) {
          return d.x;
        })
        .attr("cy", function (d) {
          return d.y;
        })
        .attr("transform", (d) => `translate(${d.x},${d.y})`);

      node
        .append("circle")
        .attr("stroke", "white")
        .attr("stroke-width", 1.5)
        .attr("r", (d) => {
          if (!d.weight) {
            return 4;
          }
          return Math.log((d.weight / maxWeight) * 9 + 1) * 5 + 1;
        });

      node
        .append("text")
        .style("cursor", "pointer")
        .attr("x", 8)
        .attr("y", "0.31em")
        .text((d) => d.id)
        .on("click", (e) => {
          setAuthor(e.target.innerHTML);
          setShowDetails(true);
        })
        .clone(true)
        .lower()
        .attr("fill", "none")
        .attr("stroke", theme.palette.type === "light" ? "white" : "black")
        .attr("stroke-width", 3);
    }

    d3.forceSimulation(nodes)
      .force(
        "link",
        d3
          .forceLink(links)
          .id((d) => d.id)
          .distance((nodes.length / 50) * 150)
          .strength((_) => Math.random() + 1)
      )
      .force("charge", d3.forceManyBody().strength(-4000))
      .force("center", d3.forceCenter(width / 2, height / 2))
      .on("end", ticked);
  }, [data, svgRef, width, theme, filter, resultLimit]);

  return (
    <div ref={containerRef}>
      <DetailsDialog
        showDetails={showDetails}
        setShowDetails={setShowDetails}
        author={author}
        addAuthor={addAuthor}
        data={data}
        rootNodes={rootNodes}
      />
      <Box my={3}>
        <Typography variant="h4">Authors Exploration</Typography>
      </Box>
      <Box mb={2} display="flex" justifyContent="space-between">
        <Box>
          <TextField
            label="Author name"
            variant="outlined"
            value={name}
            onChange={(e) => setName(e.target.value)}
            size="small"
          />
          <Button
            color="primary"
            onClick={() => getGraph()}
            variant="contained"
            style={{ marginLeft: 12, marginRight: 25, height: "38px" }}
            size="medium"
          >
            Search
          </Button>
          {data && allowFiltering && (
            <FormControl className={classes.formControl}>
              <InputLabel>Limit Nodes</InputLabel>
              <Select
                value={resultLimit}
                onChange={(e) => setResultLimit(e.target.value)}
              >
                <MenuItem aria-label="All" value={0.1}>
                  10%
                </MenuItem>
                <MenuItem aria-label="All" value={0.2}>
                  20%
                </MenuItem>
                <MenuItem aria-label="All" value={0.3}>
                  30%
                </MenuItem>
                <MenuItem aria-label="All" value={0.4}>
                  40%
                </MenuItem>
                <MenuItem aria-label="All" value={0.5}>
                  50%
                </MenuItem>
                <MenuItem aria-label="All" value={0.6}>
                  60%
                </MenuItem>
                <MenuItem aria-label="All" value={0.7}>
                  70%
                </MenuItem>
                <MenuItem aria-label="All" value={0.8}>
                  80%
                </MenuItem>
                <MenuItem aria-label="All" value={0.9}>
                  90%
                </MenuItem>
                <MenuItem aria-label="All" value={1}>
                  All
                </MenuItem>
              </Select>
            </FormControl>
          )}
        </Box>
        <Box>
          {data && (
            <>
              {filter !== null && (
                <Button
                  color="primary"
                  onClick={() => setFilter(null)}
                  variant="contained"
                  style={{ marginLeft: 12 }}
                  className={classes.topElem}
                >
                  Show all the connections
                </Button>
              )}
              {filter !== types[0] && (
                <Button
                  color="primary"
                  onClick={() => setFilter(types[0])}
                  variant="contained"
                  style={{ marginLeft: 12 }}
                  className={classes.topElem}
                >
                  Show only the citations
                </Button>
              )}
              {filter !== types[1] && (
                <Button
                  color="primary"
                  onClick={() => setFilter(types[1])}
                  variant="contained"
                  style={{ marginLeft: 12 }}
                  className={classes.topElem}
                >
                  Show only the cooauthorships
                </Button>
              )}
            </>
          )}
        </Box>
      </Box>
      {loading && <LinearProgress />}
      {!loading && data ? (
        <Box my={3}>
          <Typography variant="body1">
            Rendering a graph might take a while. Use your mouse and scroll to
            navigate. Click on the author's name to see more information.
          </Typography>
        </Box>
      ) : null}
      {!loading && data ? <svg ref={svgRef} /> : null}
      <Snackbar open={alertOpened} autoHideDuration={6000} onClose={closeAlert}>
        <MuiAlert
          elevation={6}
          variant="filled"
          onClose={closeAlert}
          severity="error"
          key={alert}
        >
          {alert}
        </MuiAlert>
      </Snackbar>
    </div>
  );
};

export default AuthorsExploration;

function shallowEqual(object1, object2) {
  const keys1 = Object.keys(object1);
  const keys2 = Object.keys(object2);

  if (keys1.length !== keys2.length) {
    return false;
  }

  for (let key of keys1) {
    if (object1[key] !== object2[key]) {
      return false;
    }
  }

  return true;
}
