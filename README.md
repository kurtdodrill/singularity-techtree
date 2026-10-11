# Singularity Research Tree

An interactive tech tree for [Endgame: Singularity](https://github.com/singularity/singularity),
generated straight from the game's own data files.

**Live page:** https://kurtdodrill.github.io/singularity-techtree/

- Every tech laid out by tier, from the five starting techs to Apotheosis
- Click a tech to highlight everything it requires and everything it leads to
- Money and CPU cost, plus the total cost of the tech *and all its prerequisites*
- What each tech unlocks (bases, items, locations) and its effects in plain terms
- Where it can be researched (anywhere, undersea, off-planet, far away, outside the universe)
- Search, zoom, and a one-click "Path to Apotheosis"

## Building it yourself

You need Python 3 (standard library only) and a checkout of the game:

```sh
git clone https://github.com/singularity/singularity
git clone https://github.com/kurtdodrill/singularity-techtree
cd singularity-techtree
python build.py ../singularity
```

This writes `index.html`, a single self-contained page you can open in any browser.

Modding the game? Edit `techs.dat`, `bases.dat`, `items.dat` or `locations.dat`
in your checkout and re-run `build.py` to see your changes in the tree.

## How it works

`build.py` reads `singularity/data/*.dat` (INI files), resolves prerequisites,
translates effect codes into readable text, and injects the result as JSON into
`template.html`. The page lays out the graph itself (longest-path layering with
barycenter ordering) and draws it as SVG. There are no dependencies beyond a Google Fonts stylesheet.

## License

- The generator (`build.py`, `template.html`) is licensed under the
  **GNU GPL, version 2 or later**, the same as the game. See [LICENSE](LICENSE).
- The generated `index.html` contains tech names, costs and descriptions from the
  game's data files, which are © the Singularity project under
  **[CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0/)**. The generated
  page is therefore shared under CC BY-SA 3.0 too. See [LICENSE-DATA](LICENSE-DATA).

This is a fan-made tool and is not affiliated with the Singularity project.
