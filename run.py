import sys
import subprocess
import os

def read_filter(file):
	with open(file, 'r') as fd:
		data = fd.read()
	filter_empty = lambda arr : list(filter(lambda x: len(x) > 0, arr))
	return filter_empty( \
		list(map(lambda x: filter_empty(x.split('\n')), \
		filter_empty(data.split('\n\n')))))

def match_any(conds, s):
	for i in range(0, len(conds)):
		cond = conds[i]
		b = True
		for c in cond:
			if s.find(c) < 0:
				b = False
				break
		if b:
			return i
	return None

def exec_cmd(cmd, sample):
	cmd = list(cmd)
	idx = cmd.index("@@") if "@@" in cmd else -1
	if idx == 0:
		print("Error: @@ cannot be program path", file=sys.stderr)
		exit(1)
	elif idx > 0:
		cmd[idx] = sample
		r = subprocess.run(cmd, capture_output=True)
	else:
		with open(sample, 'rb') as fd:
			data = fd.read()
		r = subprocess.run(cmd, input=data, capture_output=True)
	return sample, r.stdout, r.stderr

if __name__ == '__main__':
	if len(sys.argv) < 4:
		print("Usage: python3 run.py filter.txt directory program [args]",
			file=sys.stderr)
		exit(1)

	cmd = sys.argv[3:]
	conds = read_filter(sys.argv[1])
	with os.scandir(sys.argv[2]) as it:
		for entry in it:
			if entry.is_file() and entry.name != "README.txt":
				sample, _, err = exec_cmd(cmd, entry.path)
				err = err.decode()
				r = match_any(conds, err)
				if r is None:
					print("New Error Msg: \n%s\n%s" % (sample, err),
						file=sys.stderr)
				else:
					print("Old Error Msg: \n%s = %u" % (sample, r))