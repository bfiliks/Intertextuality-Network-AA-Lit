# Intertextual Influence Network in African American Literature

This repository contains a **timeline–network visualization** and supporting materials for exploring **intertextual influence** among key works in African American literature (1830s–present). It demonstrates a *weighted influence* approach (direct reuse, thematic echoes, stylistic resonance).


## What's Inside
- `assets/interactive.html` — Interactive Plotly graph with **theme filters**.
- `assets/book_level_network.png` — Static image of the book-level network.
- `assets/book_level_network.svg` — Vector version for print.
- `assets/book_level_poster.pdf` — Print-ready poster with legend.
- `assets/book_level_presentation.pptx` — Slide deck with embedded graph and QR code.
- `assets/interactive_qr.png` — QR code linking to the interactive graph (local path by default).

## Quick Start
1. **View interactive (local):**
   - Download this repo and open `assets/interactive.html` in your browser.
2. **View static poster:**
   - Open `assets/book_level_poster.pdf`.
3. **Present:** 
   - Use `assets/book_level_presentation.pptx` in talks or classes.

## Methods (Summary)
- **Influence levels:** 
  - 3 = direct reuse / strong thematic recurrence
  - 2 = thematic echo / semantic similarity
  - 1 = stylistic resonance
- **Network construction:**
  - Nodes = books (or authors); Edges = intertextual connections.
  - Edge weight encodes degree of influence.
  - Node size ~ degree centrality.
- **Themes:** freedom/abolition, veil/double-consciousness, Harlem Renaissance poetics, vernacular/folk, epistolary/moral urgency, memory/haunting/witness.

> Note: The book-level pairs here are a **curated demo**. For HTRC-scale research (thousands of volumes), integrate with HTRC Extracted Features and text reuse/semantic similarity pipelines (e.g., `passim`, embedding similarity).

## Reproduce / Extend
- Replace or augment the curated edges in the Python notebook/script to include:
  - Additional authors/titles
  - Work-to-work connections
  - Theme tags
- Re-export `interactive.html` and overwrite the file in `assets/`.

## Publish to the Web (GitHub Pages)
1. Create a public GitHub repo named e.g., `Intertextuality-Network-AA-Lit`.
2. Commit this folder's contents.
3. In **Settings → Pages**, set:
   - **Source:** `main` branch
   - **Root:** `/` (or `/docs` if you move files there)
4. Access it at: `https://bfiliks.github.io/Intertextuality-Network-AA-Lit/assets/interactive.html`

## Alternative Hosting
- **Hugging Face Spaces:** host `interactive.html` as a static demo (`Static` Space).
- **Netlify/Vercel:** deploy the repo; set `assets/interactive.html` as the landing page or create an `index.html` redirect.

## License
- Add a license of your choice (e.g., MIT) in `LICENSE`. The included works/authors are cited for **scholarly demonstration**; verify rights if distributing full texts or excerpts.

## Citation
If you use or adapt this repository, please cite as:
> Oke, Felix B. *Intertextual Influence Network in African American Literature.* 2025. 

---

**Contact:** bfiliks4xt@gmail.com/website. Contributions welcome via pull requests.

## Build From CSV (CLI)

You can regenerate the interactive network from a CSV (`edges.csv`) using the included script:

```bash
python build_network.py
```

- Edit `edges.csv` to add or modify connections (columns: `source_title,source_year,target_title,target_year,weight,themes,note` where `themes` are semicolon-separated).
- The script writes a fresh `assets/interactive.html` each run.

