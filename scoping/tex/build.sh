#!/bin/bash
# usage: build.sh input.md output.pdf
set -e
in="$1"; out="$2"
title=$(head -1 "$in" | sed 's/^# //')
tmp=$(mktemp --suffix=.md)
tail -n +2 "$in" | sed -e 's/✔/[V]/g' -e 's/✗/no/g' -e 's/★★★/***/g' -e 's/★★/**/g' -e 's/★/*/g' -e 's/→/->/g' -e 's/–/--/g' > "$tmp"
LC_ALL=C.UTF-8 LANG=C.UTF-8 pandoc "$tmp" -o "$out" --pdf-engine=xelatex -H header.tex --lua-filter=widths.lua \
  -M title="$title" -M date="Scoping JMP · octubre 2026" -M lang=es \
  -V fontsize=11pt -V documentclass=article --columns=100 2>&1 | grep -v "^\[WARNING\] Missing character" | tail -5
rm -f "$tmp"
