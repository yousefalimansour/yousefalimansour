// Renders arcade-style animations (Pac-Man, ...) of the GitHub contribution graph as SVG.
//
// It drives the pacman-contribution-graph library directly instead of going through
// that project's GitHub Action, because the Action also reports the username and game
// score to its author's server. Here every request that is not to api.github.com is refused.
//
// env: GH_USER, GITHUB_TOKEN, ARCADE_LIB (path to the library bundle),
//      GAMES (comma separated, or "all"), OUT_DIR (default: dist)
import { copyFileSync, mkdirSync, mkdtempSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, resolve } from 'node:path';
import { pathToFileURL } from 'node:url';

const user = process.env.GH_USER;
const token = process.env.GITHUB_TOKEN;
const libPath = process.env.ARCADE_LIB;
const outDir = process.env.OUT_DIR || 'dist';
if (!user || !token || !libPath) {
	console.error('GH_USER, GITHUB_TOKEN and ARCADE_LIB are required');
	process.exit(1);
}

const realFetch = globalThis.fetch;
globalThis.fetch = (input, init) => {
	const url = new URL(typeof input === 'string' ? input : input.url);
	if (url.origin !== 'https://api.github.com') {
		return Promise.reject(new Error(`request to ${url.origin} blocked`));
	}
	return realFetch(input, init);
};

// The bundle is an ES module with a .js extension; load a .mjs copy so Node treats it as one.
const esmCopy = join(mkdtempSync(join(tmpdir(), 'arcade-')), 'arcade-lib.mjs');
copyFileSync(resolve(libPath), esmCopy);
const { ArcadeRenderer, ARCADE_GAMES } = await import(pathToFileURL(esmCopy).href);
console.log(`available games: ${ARCADE_GAMES.join(', ')}`);

const wanted = (process.env.GAMES || 'pacman').split(',').map((g) => g.trim().toLowerCase()).filter(Boolean);
const games = wanted.includes('all') ? [...ARCADE_GAMES] : wanted.filter((g) => ARCADE_GAMES.includes(g));
if (games.length === 0) {
	console.error(`no valid game in "${process.env.GAMES}"`);
	process.exit(1);
}

function render(game, theme) {
	return new Promise((done, fail) => {
		let svg = '';
		const timer = setTimeout(() => fail(new Error(`${game} (${theme}) timed out`)), 240_000);
		const renderer = new ArcadeRenderer({
			game,
			platform: 'github',
			username: user,
			gameTheme: theme,
			playerStyle: 'opportunistic',
			showMonthLabels: true,
			githubSettings: { accessToken: token },
			svgCallback: (s) => { svg = s; },
			gameOverCallback: () => { clearTimeout(timer); done(svg); },
			pointsIncreasedCallback: () => {}
		});
		renderer.start().catch((e) => { clearTimeout(timer); fail(e); });
	});
}

mkdirSync(outDir, { recursive: true });
for (const game of games) {
	for (const [theme, suffix] of [['github', ''], ['github-dark', '-dark']]) {
		const svg = await render(game, theme);
		if (!svg || !svg.includes('<svg')) throw new Error(`${game} (${theme}) produced no SVG`);
		const file = join(outDir, `${game}-contribution-graph${suffix}.svg`);
		writeFileSync(file, svg);
		console.log(`wrote ${file} (${(svg.length / 1024).toFixed(0)} KB)`);
	}
}
process.exit(0);
