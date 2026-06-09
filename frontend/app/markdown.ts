/** Fix LLM tables — rebuild rows by column count from separator (no cell shuffling). */
export function normalizeMarkdown(text: string): string {
  const lines = text.split("\n");
  const output: string[] = [];
  let tableParts: string[] = [];
  let proseParts: string[] = [];

  function flushTable() {
    if (tableParts.length > 0) {
      output.push(rebuildTable(tableParts));
      tableParts = [];
    }
  }

  function flushProse() {
    if (proseParts.length > 0) {
      output.push(proseParts.join("\n"));
      proseParts = [];
    }
  }

  for (const raw of lines) {
    const line = raw.trim();
    if (!line) continue;

    if (line.includes("|")) {
      flushProse();
      tableParts.push(line);
    } else {
      flushTable();
      proseParts.push(line);
    }
  }

  flushTable();
  flushProse();

  return output.join("\n\n");
}

function parseCells(row: string): string[] {
  return row
    .split("|")
    .map((c) => c.trim())
    .filter((c) => c.length > 0);
}

function isDashCell(cell: string): boolean {
  return /^[-‑–:\s]+$/.test(cell);
}

function isSeparatorCell(cell: string): boolean {
  return isDashCell(cell) && cell.replace(/[-‑–:\s]/g, "").length === 0 && cell.length >= 3;
}

function splitInlineRows(line: string): string {
  let text = line.trim();
  text = text.replace(/(\|[-| :‑–]+\|)\s+\|/g, "$1\n|");
  text = text.replace(/ \| \| /g, " |\n| ");
  return text;
}

function rebuildTable(lines: string[]): string {
  const flat = lines.map((l) => splitInlineRows(l)).join(" ");
  const cells = parseCells(flat);

  if (cells.length < 2) {
    return flat;
  }

  // Find separator: longest run of dash-only cells (table divider row)
  let sepStart = -1;
  let numCols = 0;

  for (let i = 0; i < cells.length; i++) {
    if (!isSeparatorCell(cells[i])) continue;

    let cols = 0;
    while (i + cols < cells.length && isSeparatorCell(cells[i + cols])) {
      cols++;
    }
    if (cols >= 2) {
      sepStart = i;
      numCols = cols;
      break;
    }
  }

  // Single-column code list: one ------ separator
  if (sepStart < 0) {
    for (let i = 0; i < cells.length; i++) {
      if (isSeparatorCell(cells[i])) {
        sepStart = i;
        numCols = 1;
        break;
      }
    }
  }

  if (sepStart < 0) {
    return flat.replace(/ \| \| /g, " |\n| ");
  }

  let headerCells = cells.slice(0, sepStart);
  const sepCells = cells.slice(sepStart, sepStart + numCols);
  const dataCells = cells.slice(sepStart + numCols);

  // Align header width to separator column count
  if (numCols >= 2) {
    if (headerCells.length > numCols) {
      headerCells = headerCells.slice(0, numCols);
    } else if (headerCells.length < numCols && headerCells.length > 0) {
      // Header split across lines — take exactly numCols from start
      while (headerCells.length < numCols && headerCells.length < sepStart) {
        break;
      }
    }
  }

  const rows: string[] = [];

  if (headerCells.length > 0) {
    rows.push("| " + headerCells.join(" | ") + " |");
  }

  rows.push("| " + sepCells.map(() => "---").join(" | ") + " |");

  for (let i = 0; i < dataCells.length; i += numCols) {
    const row = dataCells.slice(i, i + numCols);
    if (row.length === numCols) {
      rows.push("| " + row.join(" | ") + " |");
    }
  }

  return rows.join("\n");
}
