import React, { useState, useEffect } from "react";

import { makeStyles } from "@material-ui/core/styles";

import AppBar from "@material-ui/core/AppBar";
import Toolbar from "@material-ui/core/Toolbar";
import IconButton from "@material-ui/core/IconButton";
import MenuIcon from "@material-ui/icons/Menu";

import Typography from "@material-ui/core/Typography";

import Drawer from "@material-ui/core/Drawer";
import List from "@material-ui/core/List";
import ListItem from "@material-ui/core/ListItem";
import ListItemIcon from "@material-ui/core/ListItemIcon";
import ListItemText from "@material-ui/core/ListItemText";
import Divider from "@material-ui/core/Divider";

import HomeOutlinedIcon from "@material-ui/icons/HomeOutlined";
import SearchOutlinedIcon from "@material-ui/icons/SearchOutlined";
import StarBorderOutlinedIcon from "@material-ui/icons/StarBorderOutlined";
import WhatshotOutlinedIcon from "@material-ui/icons/WhatshotOutlined";
import FavoriteBorderOutlinedIcon from "@material-ui/icons/FavoriteBorderOutlined";
import PeopleIcon from "@material-ui/icons/People";
import Brightness4Icon from "@material-ui/icons/Brightness4";
import Brightness7Icon from "@material-ui/icons/Brightness7";
import GitHubIcon from "@material-ui/icons/GitHub";

import useMediaQuery from "@material-ui/core/useMediaQuery";
import { createMuiTheme, ThemeProvider } from "@material-ui/core/styles";
import CssBaseline from "@material-ui/core/CssBaseline";

import Box from "@material-ui/core/Box";
import Container from "@material-ui/core/Container";

import {
  BrowserRouter as Router,
  Switch,
  Route,
  NavLink,
  Redirect,
} from "react-router-dom";
import routes from "./routes";

import Home from "./Home";
import VisualQuerying from "./VisualQuerying";
import AuthorsExploration from "./AuthorsExploration";
import RisingStars from "./RisingStars";
import HotKeywords from "./HotKeywords";
import FavouriteQueries from "./FavouriteQueries";

import "./App.css";

const useStyles = makeStyles({
  list: {
    width: 250,
  },
  link: {
    textDecoration: "none",
    color: "inherit",
  },
});

const App = () => {
  const [drawerOpened, setDrawerOpened] = useState(false);

  const classes = useStyles();

  const [darkMode, setDarkMode] = useState(
    useMediaQuery("(prefers-color-scheme: dark)")
  );
  const theme = React.useMemo(
    () =>
      createMuiTheme({
        palette: {
          type: darkMode ? "dark" : "light",
        },
      }),
    [darkMode]
  );

  useEffect(() => {
    const themeLS = localStorage.getItem("theme");

    if (themeLS === "dark") setDarkMode(true);
    if (!theme) localStorage.setItem("theme", darkMode ? "dark" : "light");
  }, []);

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <Drawer
          anchor="left"
          open={drawerOpened}
          onClose={() => setDrawerOpened(false)}
        >
          <div
            onClick={() => setDrawerOpened(false)}
            onKeyDown={() => setDrawerOpened(false)}
            className={classes.list}
          >
            <List>
              <ListItem
                button
                component={NavLink}
                to={routes.home}
                className={classes.link}
                activeClassName="Mui-selected"
                exact
              >
                <ListItemIcon>
                  <HomeOutlinedIcon />
                </ListItemIcon>
                <ListItemText primary="Home"></ListItemText>
              </ListItem>
              <Divider />
              <ListItem
                button
                component={NavLink}
                to={routes.visualQuerying}
                className={classes.link}
                activeClassName="Mui-selected"
              >
                <ListItemIcon>
                  <SearchOutlinedIcon />
                </ListItemIcon>
                <ListItemText primary="Visual Quering"></ListItemText>
              </ListItem>
              <ListItem
                button
                component={NavLink}
                to={routes.favouriteQueries}
                className={classes.link}
                activeClassName="Mui-selected"
              >
                <ListItemIcon>
                  <FavoriteBorderOutlinedIcon />
                </ListItemIcon>
                <ListItemText primary="Favourite Queries"></ListItemText>
              </ListItem>
              <ListItem
                button
                component={NavLink}
                to={routes.risingStars}
                className={classes.link}
                activeClassName="Mui-selected"
              >
                <ListItemIcon>
                  <StarBorderOutlinedIcon />
                </ListItemIcon>
                <ListItemText primary="Rising Stars"></ListItemText>
              </ListItem>
              <ListItem
                button
                component={NavLink}
                to={routes.authorsExploration}
                className={classes.link}
                activeClassName="Mui-selected"
              >
                <ListItemIcon>
                  <PeopleIcon />
                </ListItemIcon>
                <ListItemText primary="Authors Exploration"></ListItemText>
              </ListItem>

              <ListItem
                button
                component={NavLink}
                to={routes.hotKeywords}
                className={classes.link}
                activeClassName="Mui-selected"
              >
                <ListItemIcon>
                  <WhatshotOutlinedIcon />
                </ListItemIcon>
                <ListItemText primary="Hot Keywords"></ListItemText>
              </ListItem>
            </List>
          </div>
        </Drawer>
        <AppBar position="fixed" color={darkMode ? "default" : "primary"}>
          <Toolbar>
            <Box
              display="flex"
              justifyContent="space-between"
              alignItems="center"
              style={{ width: "100%" }}
            >
              <Box display="flex" justifyContent="center" alignItems="center">
                <IconButton
                  edge="start"
                  color="inherit"
                  aria-label="open drawer"
                  onClick={() => setDrawerOpened(true)}
                >
                  <MenuIcon />
                </IconButton>
                <Typography variant="h6" noWrap>
                  Article Information Parser
                </Typography>
              </Box>
              <Box>
                <a
                  href="https://github.com/atlarge-research/AIP"
                  target="__blank"
                >
                  <IconButton>
                    <GitHubIcon style={{ color: "white" }} />
                  </IconButton>
                </a>
                <IconButton
                  edge="start"
                  color="inherit"
                  aria-label="open drawer"
                  onClick={() => {
                    localStorage.setItem("theme", !darkMode ? "dark" : "light");
                    setDarkMode(!darkMode);
                  }}
                  style={{ marginLeft: "6px" }}
                >
                  {darkMode ? <Brightness7Icon /> : <Brightness4Icon />}
                </IconButton>
              </Box>
            </Box>
          </Toolbar>
        </AppBar>
        <Box height={64} />
        <Container maxWidth="xl">
          <Switch>
            <Route path={routes.home} component={Home} exact />
            <Route
              path={routes.authorsExploration}
              component={AuthorsExploration}
            />
            <Route path={routes.visualQuerying} component={VisualQuerying} />
            <Route path={routes.risingStars} component={RisingStars} />
            <Route path={routes.hotKeywords} component={HotKeywords} />
            <Route
              path={routes.favouriteQueries}
              component={FavouriteQueries}
            />

            <Route
              path={routes.home}
              component={() => <Redirect to={routes.home} />}
            />
          </Switch>
        </Container>
      </Router>
    </ThemeProvider>
  );
};

export default App;
