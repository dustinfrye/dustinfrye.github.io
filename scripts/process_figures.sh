#!/usr/bin/env bash
#
# process_figures.sh
#
# Converts raw paper figures into web-ready PNGs for the research page.
#
# Usage:
#   1. Drop raw figures (PDF, PNG, JPG, TIFF) into  images/research/raw/
#      Name each file after its paper ID (e.g. land.pdf, hwy.png, mktint.pdf).
#      See the filename-to-paper mapping in _pages/research.md.
#   2. Run this script from the repo root:
#        ./scripts/process_figures.sh
#   3. Output PNGs are written to images/research/ (overwriting any existing files).
#
# Requirements (both ship with macOS or can be installed via Homebrew):
#   - pdftoppm  (brew install poppler)  — for PDF -> PNG conversion
#   - sips                              — built into macOS, for resizing
#
# Behavior:
#   - PDFs are rasterized at 200 DPI, first page only
#   - Anything wider than MAX_WIDTH px is resized down preserving aspect ratio
#   - Small images are left at their original size (no upscaling)

set -euo pipefail

# Config
MAX_WIDTH=1200          # px — matches the CSS max-width container
PDF_DPI=200             # dpi for PDF rasterization (200 is a good balance)

# Resolve repo root regardless of where the script is called from
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
RAW_DIR="${REPO_ROOT}/images/research/raw"
OUT_DIR="${REPO_ROOT}/images/research"

# Sanity checks
if ! command -v pdftoppm >/dev/null 2>&1; then
  echo "error: pdftoppm not found. Install with:  brew install poppler" >&2
  exit 1
fi
if ! command -v sips >/dev/null 2>&1; then
  echo "error: sips not found (should be built-in on macOS)" >&2
  exit 1
fi
if [ ! -d "${RAW_DIR}" ]; then
  echo "error: raw directory does not exist: ${RAW_DIR}" >&2
  exit 1
fi

echo "Reading raw figures from:  ${RAW_DIR}"
echo "Writing processed PNGs to: ${OUT_DIR}"
echo

shopt -s nullglob nocaseglob
raw_files=( "${RAW_DIR}"/*.{pdf,png,jpg,jpeg,tif,tiff} )
shopt -u nullglob nocaseglob

if [ ${#raw_files[@]} -eq 0 ]; then
  echo "No raw figures found. Drop PDFs or images into:"
  echo "  ${RAW_DIR}"
  exit 0
fi

processed=0
for src in "${raw_files[@]}"; do
  filename="$(basename "${src}")"
  stem="${filename%.*}"
  ext_lower="$(echo "${filename##*.}" | tr '[:upper:]' '[:lower:]')"
  out="${OUT_DIR}/${stem}.png"

  case "${ext_lower}" in
    pdf)
      echo "→ ${filename}  (PDF, rasterizing at ${PDF_DPI} dpi)"
      # pdftoppm adds "-1" suffix for page 1; write to a temp stem then move
      tmp_prefix="${OUT_DIR}/.${stem}_tmp"
      pdftoppm -png -r "${PDF_DPI}" -f 1 -l 1 "${src}" "${tmp_prefix}"
      mv "${tmp_prefix}-1.png" "${out}"
      ;;
    png|jpg|jpeg|tif|tiff)
      echo "→ ${filename}  (copying to ${stem}.png)"
      # sips can read most raster formats; use it to normalize to PNG
      sips -s format png "${src}" --out "${out}" >/dev/null
      ;;
  esac

  # Resize down if wider than MAX_WIDTH (sips -Z does nothing to smaller images)
  width=$(sips -g pixelWidth "${out}" | awk '/pixelWidth:/ {print $2}')
  if [ -n "${width}" ] && [ "${width}" -gt "${MAX_WIDTH}" ]; then
    sips -Z "${MAX_WIDTH}" "${out}" >/dev/null
    new_width=$(sips -g pixelWidth "${out}" | awk '/pixelWidth:/ {print $2}')
    echo "    resized ${width}px -> ${new_width}px"
  fi

  size_kb=$(( $(stat -f%z "${out}") / 1024 ))
  echo "    wrote ${out#${REPO_ROOT}/}  (${size_kb} KB)"
  processed=$(( processed + 1 ))
done

echo
echo "Done. Processed ${processed} figure(s)."
echo "Remember to uncomment the matching <div class=\"paper__figure\"> line in _pages/research.md"
