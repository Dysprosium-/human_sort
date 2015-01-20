#!python3
# -*- coding: utf-8 -*-

import pickle, sys, time, traceback

"""
Sort a list using human comparison.
"""

# We use the built-in Python sorting algorithm (Timsort) but replace the
# comparison operator by a special one which ask the user what is
# better between two compared elements.
#
# This doesn't affect the complexity, but affects the overall time of
# execution since the user might take several seconds to decide the result
# of each comparison.
#
# As a partial solution to this problem, we register all the human comparisons
# into a dictionary which associates pairs of elements to -1 or 1 and
# store this dictionary in a log file when the program stops. This allows the
# user to stop the sorting process and resume it later by loading the log file.
#
# When launching the program again with a log file, the sorting process start
# again from the beginning, but all already-answered comparisons are known, so
# the algorithm reach the point where it was before (where it needs new human
# comparisons) really fast, assuming little-sized inputs.
#
# The storing of equality in this dicationary is a little bit more complicated.
# The problem is that the sorting algorithm doesn't know transitivity. That is,
# if a == b and b == c and the algorithm wants to compare a and c, it will just
# fire the comparison function again, which will be frustating for the user.
#
# The solution is that the dictionary contains a special key 'EQSETS' which is
# associated to a list of sets. Each set represents an equality group. That is,
# every element of one set are equal, and one element can't be in more than one
# set.
#
# Since users usually want to know the palmares, we output the result in the
# reverse order: from the best to the worst. As an option, the output can also
# have blank lines which seperates groups of equal elements. We do this with
# a second pass on the sorted list. This second pass is linear and uses the
# comparisons log fabricated during the sorting process.


ERROR = """YOU BROKE THE PROGRAM! WHAT HAVE YOU DONE?!!\n"""

USAGE = """Usage:

	-i <input filename> -o <output filename> [-e] [-l <logfile>] [--nolog]

	<input filename>
	A text file where you want to sort lines

	<ouput filename>
	A text file where sorted lines will be written (will overwrite an already existing file)

	-e
	Put a blank line between groups of equal elements.

	-l <logfile>
	Load a comparisons log file. Comparisons stored in the log won't be asked again to the user.

	--nolog
	Doesn't save a log file at the end. Use with caution. You really want a log file.
"""


def my_fucking_print(fucking_string):
	""" Seems like there is no easy fucking solution not to fuck up
		an executing program which is going to try to print some
		weird character that the console cannot write so I have
		to write the motherfucking print function myself.
	"""
	for fucking_character in fucking_string:
		try:
			print(fucking_character, end='')
		except UnicodeEncodeError:
			print('?', end='')
	print()

def my_cmp_to_key(mycmp, stuff):
    """Convert a cmp= function into a key= function.
       This is from the functools module, I just added a stuff argument which
       is stuff to be passed to the custom comparison function.
    """
    class K(object):
        def __init__(self, obj, *args):
            self.obj = obj
        def __lt__(self, other):
            return mycmp(self.obj, other.obj, stuff) < 0
        def __gt__(self, other):
            return mycmp(self.obj, other.obj, stuff) > 0
        def __eq__(self, other):
            return mycmp(self.obj, other.obj, stuff) == 0
        def __le__(self, other):
            return mycmp(self.obj, other.obj, stuff) <= 0
        def __ge__(self, other):
            return mycmp(self.obj, other.obj, stuff) >= 0
        def __ne__(self, other):
            return mycmp(self.obj, other.obj, stuff) != 0
    return K

def human_compare(a, b, known={'EQSETS':[]}):
	""" Custom comparator. Check in known to see if the comparison of a and b
		is already known, and if it's not the case, ask the user what he thinks
		about it. In this case, the user's answers is stored in known.
	"""
	if frozenset((a,b)) in known:
		return known[frozenset((a,b))]
	for eqset in known['EQSETS']:
		if a in eqset and b in eqset:
			return 0
	template = "\nWhat is the better:\n(a) {}\n(b) {}\n(c) can't decide!"
	my_fucking_print(template.format(a, b))
	ans = input('> ')
	if ans == 'a':
		known[frozenset((a,b))] = 1
		return 1
	elif ans == 'b':
		known[frozenset((a,b))] = -1
		return -1
	elif ans == 'c':
		for eqset in known['EQSETS']:
			if a in eqset:
				eqset.add(b)
				break
			elif b in eqset:
				eqset.add(a)
				break
		else:
			known['EQSETS'].append({a,b})
		return 0
	else:
		print('\n/!\ Accepted input: a, b or c')
		return human_compare(a, b, known)

def get_eq_groups(sl, known_comp={'EQSETS':[]}):
	""" Takes a sorted list and returns a list of lists where each sublist
		contains the largest sequence of equal elements in their original
		list's order.
	"""
	ln = len(sl)
	result = []
	k = 0
	while k < ln:
		row = [sl[k]]
		while k+1 < ln and human_compare(sl[k], sl[k+1], known_comp) == 0:
			k += 1
			row.append(sl[k])
		k += 1
		result.append(row)
	return result

def human_sort(li, known_comp={'EQSETS':[]}, eq_groups=False):
	""" Sort a list using human comparison."""
	raw_sorted = sorted(li, key=my_cmp_to_key(human_compare, known_comp))
	if eq_groups:
		return get_eq_groups(raw_sorted, known_comp)
	else:
		return raw_sorted

def io_human_sort(infilename, outfilename, known_comp={'EQSETS':[]}, eq_groups=False, log=True):
	""" Sort the lines of the file infilename using human comparison and output
		the result to outfilename.
	"""
	with open(infilename, 'r') as infile:
		in_list = [a[:-1] for a in infile.readlines() if a[-1] == '\n']
	try:
		sorted_list = human_sort(in_list, known_comp, eq_groups)
		sorted_list.reverse()
	except:
		print()
		print(traceback.format_exc())
		print(ERROR)
	else:
		print('\nWriting sort result to', outfilename)
		with open(outfilename, 'w') as outfile:
			if eq_groups:
				for eqset in sorted_list:
					for item in eqset:
						outfile.write(str(item)+'\n')
					outfile.write('\n')
			else:
				for item in sorted_list:
					outfile.write(str(item)+'\n')
		print('Done.')
	finally:
		if log:
			logname = 'human_sort_log_' + time.strftime('%Y-%m-%dT%H-%M-%S')
			print('\nSaving comparisons log to', logname)
			with open(logname, 'wb') as new_logfile:
				pickle.dump(known_comp, new_logfile)
			print('Log saved.')

def main():
	known_comp = {'EQSETS':[]}
	eq_groups = False
	log = True
	infilename, output = None, None
	if sys.argv[1] in ('--help', '-h', 'help', '-help', 'heeeeeeelp me'):
		print(USAGE)
		return
	for index, arg in enumerate(sys.argv):
		if arg == '-l':
			with open(sys.argv[index+1], 'rb') as file:
				known_comp = pickle.load(file)
		if arg == '-o':
			output = sys.argv[index+1]
		if arg == '-e':
			eq_groups = True
		if arg == '--nolog':
			log = False
		if arg == '-i':
			infilename = sys.argv[index+1]
	if not (infilename and output):
		print(USAGE)
		return
	io_human_sort(infilename, output, known_comp, eq_groups, log)


if __name__ == '__main__':
	main()