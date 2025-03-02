import readability

def textstat(*args, **kwargs):
	return readability.getmeasures(*args, **kwargs)

def init_textstat(name):
	try:
		suffix = b'_' + name.encode('ascii')
	except UnicodeEncodeError:
		suffix = b'U_' + name.encode('punycode').replace(b'-',b'_')
	return b'PyInit' + suffix

if __name__ == "__main__":
	print(textstat("thing").dale_chall())