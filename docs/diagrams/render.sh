#!/usr/bin/env bash
set -euo pipefail

diagrams_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
sources=(
  "$diagrams_dir/database.puml"
  "$diagrams_dir/domain-classes.puml"
  "$diagrams_dir/application-classes.puml"
)

if [[ -n "${PLANTUML_JAR:-}" ]]; then
  command=(java -Djava.awt.headless=true -jar "$PLANTUML_JAR")
elif command -v plantuml >/dev/null 2>&1; then
  command=(plantuml)
else
  printf '%s\n' 'Set PLANTUML_JAR to your PlantUML JAR, or install the plantuml command.' >&2
  exit 1
fi

# Validate every source before replacing committed previews.
"${command[@]}" -charset UTF-8 -checkonly -failfast2 "${sources[@]}"
"${command[@]}" -charset UTF-8 -tsvg -nometadata -failfast2 "${sources[@]}"
printf '%s\n' "SVG previews generated in $diagrams_dir"
