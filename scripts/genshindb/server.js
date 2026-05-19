// server.js
const express = require('express');
const genshindb = require('genshin-db');
// genshindb.setOptions({ v4Props: true });

const app = express();

// HEALTH ENDPOINT

app.get("/health", (_, res) => {
    res.status(200).json({
        status: "ok"
    });
});

// LIST ENDPOINTS

app.get('/artifact/list', (_, res) => {
    const artifacts = genshindb.artifacts('names', { matchCategories: true });
    res.json(artifacts);
});

app.get('/character/list', (_, res) => {
    const characters = genshindb.characters('names', { matchCategories: true });
    res.json(characters);
});

app.get('/weapon/list', (_, res) => {
    const weapons = genshindb.weapons('names', { matchCategories: true });
    res.json(weapons);
});

// QUERY ENDPOINTS

app.get('/character', (req, res) => {
    const { name } = req.query;

    if (!name) {
        return res.status(400).json({
            status: "failed",
            message: "name query parameter required"
        });
    }

    const character = genshindb.characters(name);
    if (!character) {
        return res.status(404).json({
            status: "failed"
        });
    }

    res.json(character);
});

app.get('/talents', (req, res) => {
    const { name } = req.query;

    if (!name) {
        return res.status(400).json({
            status: "failed",
            message: "name query parameter required"
        });
    }

    const talents = genshindb.talents(name);
    if (!talents) {
        return res.status(404).json({
            status: "failed"
        });
    }

    res.json(talents);
});

app.get('/artifact', (req, res) => {
    const { name } = req.query;

    if (!name) {
        return res.status(400).json({
            status: "failed",
            message: "name query parameter required"
        });
    }

    const artifact = genshindb.artifacts(name);
    if (!artifact) {
        return res.status(404).json({
            status: "failed"
        });
    }

    res.json(artifact);
});

app.get('/weapon', (req, res) => {
    const { name } = req.query;

    if (!name) {
        return res.status(400).json({
            status: "failed",
            message: "name query parameter required"
        });
    }

    weapon = genshindb.weapons(name);

    res.json(weapon);
});

app.get('/weapon/stats', (req, res) => {
    const { name, level } = req.query;

    let weapon;
    try {
        weapon = genshindb.weapons(name);
    } catch (err) {
        return res.status(404).json({ status: "failed" });
    }
    if (!weapon) {
        return res.status(404).json({ status: "failed" });
    }
    const stats = weapon.stats(parseInt(level));

    res.json(stats);
});

app.listen(3000, () => {
    console.log("Server running on port 3000");
});
