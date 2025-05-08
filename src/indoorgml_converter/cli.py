# src/indoorgml_converter/cli.py

import argparse, sys, logging
from pathlib import Path
from .converter import convert

def setup_logging(verbose: bool):
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=level,
                        format="%(asctime)s - %(levelname)s - %(message)s")

def main():
    p = argparse.ArgumentParser(
        description="Convert GeoJSON → IndoorGML + floor-by-floor preview"
    )
    p.add_argument("input",  type=Path, help="Path to .geojson input")
    p.add_argument("output", type=Path, help="Path to .gml output")
    p.add_argument("-f","--force",   action="store_true", help="Overwrite output")
    p.add_argument("-v","--verbose", action="store_true", help="Verbose logging")
    p.add_argument("--no-visual",    action="store_true", help="Skip preview")

    args = p.parse_args()
    setup_logging(args.verbose)
    log = logging.getLogger(__name__)

    if not args.input.exists() or not args.input.is_file():
        log.error("Input missing or not a file: %s", args.input)
        sys.exit(1)
    if args.output.exists() and not args.force:
        log.error("Output exists; use -f to overwrite.")
        sys.exit(1)
    args.output.parent.mkdir(parents=True, exist_ok=True)

    ok = convert(
        geojson_path     = args.input,
        output_path      = args.output,
        visualize_output = not args.no_visual
    )
    if not ok:
        log.error("❌ Conversion failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
