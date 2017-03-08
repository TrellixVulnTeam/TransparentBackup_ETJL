# Converts the aggregation of the previous state of the backup set and the updated files, rooted in the current directory, to the final new state
# Copies duplicated updated files to all destinations
cp --no-dereference --preserve=all "./Created File.txt" "./New Moved Subdirectory/Created File.txt"
