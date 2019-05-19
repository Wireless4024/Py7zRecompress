#!/usr/bin/python
# coding=utf-8
import _thread
import os
import platform
import subprocess
import sys
import threading
import time

_7zCompressable = ('.7z', '.xz', '.zip', '.tar', '.rar', '.jar')
_7zCompressArgs = '"{_7z}" a -sdel -mx9 -ssw -mmt3 -myx9 -md{dictsz} -aoa -mfb273 ' \
				  '-ms=on "{dest}" "{src}"'
_xzCompressArgs = '"{_7z}" a -sdel -txz -mx9 -ssw -mmt3 -myx9 -md{dictsz} -aoa -mfb273 ' \
				  '-ms=on "{dest}" "{src}"'
_zipCompressArgs = '"{_7z}" a -sdel -tzip -mx9 -mfb258 -mmt3 -ssw -aoa "{dest}" "{src}"'
_7zExtractArgs = '"{_7z}" x "{src}" "-o{dest}" -y -r'

_default7z = "C:\\Program Files\\7-Zip\\7z.exe" if platform.system() == 'Windows' and os.path.exists(
	"C:\\Program Files\\7-Zip\\7z.exe") else '7z'
_defaultDictSize = '96m'

gb = {}


def compress(_7z = _default7z, source = '', dest = os.getcwd(), dictionary_size = _defaultDictSize, method = '7z'):
	if source == '':
		return False
	if method == 'xz':
		command = _xzCompressArgs.format(_7z = _7z, src = os.path.join(source, '*'), dest = dest,
										 dictsz = dictionary_size)
		execComm(command)
	elif method == 'zip' or method == 'jar':
		command = _zipCompressArgs.format(_7z = _7z, src = os.path.join(source, '*'), dest = dest,
										  dictsz = dictionary_size)
		execComm(command)
	else:
		command = _7zCompressArgs.format(_7z = _7z, src = os.path.join(source, '*'), dest = dest,
										 dictsz = dictionary_size)
		execComm(command)


def extract(_7z = _default7z, source = '', dest = os.path.join(os.getcwd(), 'tmp')):
	if source == '':
		return False
	command = _7zExtractArgs.format(_7z = _7z, src = source, dest = dest)
	execComm(command)


def execComm(command = ''):
	subprocess.Popen(command, shell = True, stdout = subprocess.DEVNULL).wait()


def getType(val = '', sensitive = False):
	if val.endswith('.jar'):
		return 'jar'
	if not sensitive:
		return '7z'
	if val.endswith('.xz'):
		return 'xz'
	elif val.endswith('.zip'):
		return 'zip'
	return '7z'


class File:
	def __init__(self, path, deep, sensitive = False):
		self.name = os.path.basename(path)
		self.deep = deep
		self.type = getType(path, sensitive)
		self.out = os.path.join(os.path.dirname(path), (self.name.split('.', 1)[0] + '.' + self.type))
		self.path = path
		self.status = 'idle'

	def info(self):
		return "name:[{}]|path:[{}]".format(self.name, self.path)

	def backup(self):
		old = os.path.join(os.getcwd(), 'old', str(int(time.time())) + self.name)
		os.rename(self.path, old)
		return old

	def deepCompress(self, folder):
		execComm('"{}" "{}" "{}" "{}" "{}" "{}" "{}" "{}"'.format(sys.executable, sys.argv[0], folder, gb['thread'],
																  gb['deep'], 'yes', gb['dict'], gb['7z'], True))

	def recompress(self):
		print("\rWorking on [{}] path : '{}'".format(self.name, self.path))
		temp = os.path.join(os.getcwd(), 'tmp', str(time.time()) + '-' + self.name.replace('.', '-'))
		self.status = 'creating temp'
		if not os.path.exists(temp):
			os.mkdir(temp)
		self.status = 'backing up'
		backup = self.backup()
		self.status = 'extracting'
		extract(source = backup, dest = temp)
		if self.deep > 1 and deeper(temp):
			self.status = 'waiting deep compress'
			self.deepCompress(temp)
		self.status = 'compressing'
		compress(source = temp, dest = self.out, method = self.type)
		self.status = 'removing temp'
		os.rmdir(temp)
		self.status = 'done'
		Manager.working.remove(self)
		print("\r[ done ] {}".format(self.path))

	def __str__(self):
		return self.path


class Manager:
	files = []
	working = []

	def __init__(self, location = os.getcwd(), deep = 1, sensitive = False):
		print("scanning directory '{}'".format(location))
		Manager.files = [File(os.path.join(root, f), deep, sensitive) for root, dirs, files in os.walk(location) for f
						 in files if f.endswith(_7zCompressable)]
		print("Found {} files!".format(len(Manager.files)))

	@staticmethod
	def run(threads = 1):
		for i in range(threads):
			Work().start()

	@staticmethod
	def pop():
		temp = Manager.files.pop()
		Manager.working.append(temp)
		return temp


class Work(threading.Thread):
	def run(self):
		while 1:
			if len(Manager.files) < 1:
				break
			Manager.pop().recompress()


def printStatus():
	while len(Manager.working) > 0:
		for work in Manager.working:
			print("\r[ {} ] {}".format(work.status, work), end = '')
			time.sleep(2)


def deeper(path = ''):
	for root, dirs, files in os.walk(path):
		for f in files:
			if f.endswith(_7zCompressable):
				return True
	return False


def argsStr(arr):
	base = ' '
	for i in arr:
		base += '"{}" '.format(i)
	return base


if __name__ == '__main__':
	# File('H:\\Files\\Software\\Downloads\\ChkFlsh.zip').backup()
	if len(sys.argv) < 2:
		print('''py7zrecompress.py <folder> [threads (1)] [deep=1] [extension sensitive=(no|yes)] [dictionary_size (96m)] [7z path (7z)] [deepcall]
folder 	: folder that contain [ .7z , .xz , .zip , .tar , .rar ]
threads : number of working thread (higher number required more memory) 
deep    : scan deep  useful when you have zip inside zip
		 (required more memory when threads > 1)
         1 just it self
         2 will call this program again in extract folder
         3 will call this program again in extract folder 2 times
        -1 will call this program again and again until it doesn't have compressable file at most at 2147483647 times!
extension sensitive : yes - output will same as extension
                      no  - will compress into .7z
dictionary_size : size of dictionary
    memory required (per thread)
deep call = reclusive call when deep > 1 (internal use)
[dictionary size] [memory usage]
      96m           1   GByte
      128m          1.4 GBytes
      192m          2   GBytes 
      256m          2.7 GBytes
      384m          4   GBytes
      512m          5.4 GBytes
      768m          8.3 GBytes
      1024m         10.7 GBytes
      1536m         16.7 GBytes
**Note
<> mean required
[] mean optional
if file is locked will produce empty .7z file and old file are in old folder''')
		exit(-1)
	# exit(-1)
	if not os.path.exists(sys.argv[1]):
		print("'{}' doesn't exist".format(sys.argv[1]))
		exit(-1)
	if not os.path.isdir(sys.argv[1]):
		print("'{}' is not a directory".format(sys.argv[1]))
		exit(-1)

	gb['path'] = path = sys.argv[1]
	gb['thread'] = thread = int(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[2].isdigit() else 1
	deep = int(sys.argv[3]) if len(sys.argv) > 3 else 2
	gb['deep'] = deep = 2147483647 if deep < 0 else deep
	gb['sensitive'] = sensitive = True if len(sys.argv) > 4 and sys.argv[4].lower() == 'yes' else False
	gb['dict'] = _defaultDictSize
	if len(sys.argv) > 5:
		gb['dict'] = _defaultDictSize = sys.argv[5]
	gb['7z'] = _7z = sys.argv[6] if len(sys.argv) > 6 else _default7z
	gb['deepcall'] = True if len(sys.argv) > 7 and sys.argv[7].lower() == 'True' else False

	if not os.path.exists('tmp'):
		os.mkdir('tmp')
	if not os.path.exists('old'):
		os.mkdir('old')
	Manager(path, deep, sensitive).run(thread)
	_thread.start_new_thread(printStatus, ())
