// server.js
const express = require('express');
const genshindb = require('genshin-db');

const app = express();

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

app.get('/weapon', (req, res) => {
    const { name, level } = req.query;

    const weapon = genshindb.weapons(name);
    const stats = weapon.stats(parseInt(level));

    res.json(stats);
});

app.listen(3000, () => {
    console.log("Server running on port 3000");
});
