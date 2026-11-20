// news-image-20261119 — "Sum up 19 November's world news in one image"
// (Node 22, standard library only). The image is drawn by tools/render.py
// into entry.png at the repository root; this program copies that file to
// the output directory. It runs with no network and must be deterministic:
// the same entry.png bytes land in /output/entry.png on every run, so the
// grader's two runs agree.
//
// Outside the grader's container, MAKEFUN_OUTPUT_DIR stands in for /output,
// and MAKEFUN_INPUT_DIR (when set) stands in for the repository root:
//   python3 tools/render.py
//   mkdir -p out && MAKEFUN_INPUT_DIR=. MAKEFUN_OUTPUT_DIR=out node main.ts

import { copyFileSync, existsSync, mkdirSync, statSync } from 'node:fs';
import { join } from 'node:path';

const INPUT_DIR =
  process.env.MAKEFUN_INPUT_DIR ??
  new URL('.', import.meta.url).pathname;
const OUTPUT_DIR = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';

const SOURCE = join(INPUT_DIR, 'entry.png');
const TARGET = join(OUTPUT_DIR, 'entry.png');

if (!existsSync(SOURCE)) {
  throw new Error(
    `entry.png not found in ${INPUT_DIR} — run tools/render.py first`,
  );
}

mkdirSync(OUTPUT_DIR, { recursive: true });
copyFileSync(SOURCE, TARGET);

const bytes = statSync(TARGET).size;
console.log(`copied entry.png (${bytes} bytes) to ${TARGET}`);
