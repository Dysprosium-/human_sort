# Human sort

Sort a list using the Python built-in sorting algorithm (Timsort), but ask a human what is better between two elements at each comparison.

## Usage

The script works on Python 3 with the standard library. To sort items you need to write them on a text file (one item per line) and then run the script:

	python3 human_sort.py -i input_filename -o output_filename

## Complete usage guide:

	-i <input filename> -o <output filename> [-e] [-l <logfile>] [--nolog]

	-e
	Put a blank line between groups of equal elements.

	-l <logfile>
	Load a comparisons log file. Comparisons stored in the log won't be asked again to the user.

	--nolog
	Doesn't save a log file. Use with caution. You really want a log file.

## Author

Dysprosium