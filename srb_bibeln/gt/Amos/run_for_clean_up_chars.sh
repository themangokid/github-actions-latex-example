for file in *.txt; do
  perl -pi -e 's/\d+\s|\*//g' "$file"
done
