# Raw paper figures

Drop raw figure files into this folder, then run from the repo root:

```
./scripts/process_figures.sh
```

The script rasterizes PDFs, resizes anything wider than 1200px, and writes
web-ready PNGs to `images/research/`.

## Naming

Each file's stem must match the paper ID used in `_pages/research.md`. Examples:

| Paper                                           | Raw filename     |
|-------------------------------------------------|------------------|
| Property Rights Without Transfer Rights         | `land.pdf`       |
| Transportation Networks & Geographic Conc.      | `hwy.pdf`        |
| Bureaucratic Discretion                         | `agents.pdf`     |
| Indigenous Self-Governance                      | `pnp.pdf`        |
| Economic Consequences of Childhood Lead         | `lead.pdf`       |
| Market Integration (Hadachek)                   | `mktint.pdf`     |
| Land Development Along Highway Networks         | `hwyland.pdf`    |
| Allotment Households (Assimilation Era)         | `ppl.pdf`        |
| Colonial Definitions of Indigenous Identity     | `ineq.pdf`       |
| Local vs Central Governance (IRA)               | `ira.pdf`        |
| Native Americans in the Historical Census       | `nadata.pdf`     |

PDF, PNG, JPG, and TIFF inputs are all accepted.

## After running the script

Uncomment the matching `<div class="paper__figure">` line for that paper in
`_pages/research.md`.
