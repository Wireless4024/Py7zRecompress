#!/usr/bin/python3
# coding=utf-8
import _thread
import argparse
import os
import platform
import subprocess
import sys
import threading
import time

_7zCompressable = ('.7z', '.xz', '.zip', '.tar', '.jar')
_7zCompressArgs = '"{_7z}" a -sdel -mx9 -ssw -mmt{thread} -myx9 -md{dictsz} -aoa -mfb273 ' \
				  '-ms=on "{dest}" "{src}"'
_xzCompressArgs = '"{_7z}" a -sdel -txz -mx9 -ssw -mmt{thread} -myx9 -md{dictsz} -aoa -mfb273 ' \
				  '-ms=on "{dest}" "{src}"'
_zipCompressArgs = '"{_7z}" a -sdel -tzip -mx9 -mfb258 -mmt{thread} -ssw -aoa "{dest}" "{src}"'
_7zExtractArgs = '"{_7z}" x "{src}" "-o{dest}" -y -r'

_default7z = "C:\\Program Files\\7-Zip\\7z.exe" if platform.system() == 'Windows' and os.path.exists(
	"C:\\Program Files\\7-Zip\\7z.exe") else '7z'
_defaultDictSize = '96m'

gb = {}


def terminal_width():
	try:
		term_width, void = os.get_terminal_size()
	except Exception:
		term_width = 80
	return min(max(20, term_width), 120) - 3


def compress(_7z = _default7z, source = '', dest = os.getcwd(), dictionary_size = _defaultDictSize, method = '7z'):
	if source == '':
		return False
	if method == 'xz':
		command = _xzCompressArgs.format(_7z = _7z, src = os.path.join(source, '*'), dest = dest,
										 dictsz = dictionary_size, thread = gb['ct'])
		execommand(command)
	elif method == 'zip' or method == 'jar':
		command = _zipCompressArgs.format(_7z = _7z, src = os.path.join(source, '*'), dest = dest,
										  dictsz = dictionary_size, thread = gb['ct'])
		execommand(command)
	else:
		command = _7zCompressArgs.format(_7z = _7z, src = os.path.join(source, '*'), dest = dest,
										 dictsz = dictionary_size, thread = gb['ct'])
		execommand(command)


def extract(_7z = _default7z, source = '', dest = os.path.join(os.getcwd(), 'tmp')):
	if source == '':
		return False
	command = _7zExtractArgs.format(_7z = _7z, src = source, dest = dest)
	execommand(command)


# noinspection SpellCheckingInspection
def execommand(command = ''):
	subprocess.Popen(command, shell = True, stdout = subprocess.DEVNULL).wait()


def get_extension(val = '', sensitive = False):
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
	def __init__(self, path, sensitive = False):
		self.name = os.path.basename(path)
		self.type = get_extension(path, sensitive)
		# noinspection PyTypeChecker
		self.out = os.path.join(os.path.dirname(path),
								(self.name.rsplit('.', 1)[0] + '.' + self.type) if not sensitive else self.name)
		self.path = path
		self.status = 'idle'

	def backup(self):
		old = os.path.join(os.getcwd(), 'old', str(int(time.time())) + '-' + self.name)
		os.rename(self.path, old)
		return old

	@staticmethod
	def deep_compress(folder):
		execommand('"{}" "{}" "{}" -wt "{}" -ct "{}" -d "{}" -s "{}" -dc "{}" -7z "{}" -_deep "{}"'.format(
			sys.executable, sys.argv[0], folder, gb['wt'], gb['ct'], gb['deep'] - 1, 'yes', gb['dict'], gb['7z'], True))

	# noinspection SpellCheckingInspection
	def recompress(self):
		print("\rWorking on [{}]".format(self))
		temp = os.path.join(os.getcwd(), 'tmp', str(time.time()) + '-' + self.name.replace('.', '-'))
		self.status = 'creating temp'
		if not os.path.exists(temp):
			os.mkdir(temp)
		self.status = 'backing up'
		backup = self.backup()
		self.status = 'extracting'
		extract(source = backup, dest = temp)
		if gb['deep'] > 1 and deeper(temp):
			self.status = 'waiting deep compress'
			self.deep_compress(temp)
		self.status = 'compressing'
		compress(source = temp, dest = self.out, method = self.type)
		self.status = 'removing temp'
		os.rmdir(temp)
		self.status = 'done'
		Manager.working.remove(self)
		print("\r[ done ] {}".format(self, -9))

	def __str__(self):
		return self.path


class Manager:
	files = []
	working = []

	def __init__(self, locations, sensitive = False, threads = 1):
		self.run(threads)
		length = 0
		fileTypes = _7zCompressable if sensitive else (*_7zCompressable, '.rar', '.gz')
		for location in locations:
			print("scanning directory '{}'".format(location))
			temp = [File(os.path.join(root, f), sensitive)
					for root, dirs, files in os.walk(location) for f
					in files if f.endswith(fileTypes)]
			length += len(temp)
			Manager.files.extend(temp)
		print("Found {} files!".format(len(Manager.files)))
		gb['finished'] = True

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
		while len(Manager.files) < 1 and not gb['finished']:
			time.sleep(1)
		while 1:
			if len(Manager.files) < 1:
				break
			Manager.pop().recompress()


def print_status():
	while len(Manager.files) < 1 and not gb['finished']:
		time.sleep(1)
	while len(Manager.working) > 0:
		for work in Manager.working:
			print("\r[ {} ] {}".format(work.status, wrap(work, -len(work.status))), end = '')
			time.sleep(1)
		print("running [{}] task | remaining [{}] files".format(len(Manager.working), len(Manager.files)), end = '')
		time.sleep(2)


def wrap(msg, length = 0):
	if length < 0:
		length += terminal_width()
	if length == 0:
		length = terminal_width()
	msg = str(msg)
	return ('..' + msg[len(msg) - length:].strip(' \r\n\t')) if len(msg) > length else msg


def deeper(path = ''):
	for root, dirs, files in os.walk(path):
		for f in files:
			if f.endswith(_7zCompressable):
				return True
	return False


# noinspection SpellCheckingInspection
def argstr(arr):
	base = ' '
	for i in arr:
		base += '"{}" '.format(i)
	return base


if __name__ == '__main__':
	args = argparse.ArgumentParser(description = 'Py7zReCompress help')
	args.add_argument(dest = 'directory', help = 'directory that contains archive files')
	args.add_argument('-wt', '--work_thread', default = 1, dest = 'work_thread', type = int,
					  help = 'number of working thread(s)')
	args.add_argument('-ct', '--compress_thread', default = 3, dest = 'compress_thread', type = int,
					  help = 'number of thread used by 7zip')
	args.add_argument('-d', '--deep', default = 2, dest = 'deep_count', type = int,
					  help = 'number to dig into archive file')
	args.add_argument('-s', '--sensitive', default = 'no', dest = 's', type = str,
					  help = 'use compress algorithm same with file extension', choices = ('yes', 'y', 'no', 'n'))
	args.add_argument('-dc', '--dictionary', default = 96, dest = 'dictionary_size', type = int,
					  help = 'dictionary size (megabytes)')
	args.add_argument('-7z', '--executable', default = _default7z, dest = '_7z_path', type = str,
					  help = '7zip executable path')
	args.add_argument('-_deep', default = False, dest = '_deep', type = bool,
					  help = 'deep call from itself (internal use)')
	arg = args.parse_args()

	gb['path'] = arg.directory if not isinstance(arg.directory, str) else [arg.directory]
	for d in gb['path']:
		if not os.path.exists(d):
			print("'{}' doesn't exist".format(d))
			exit(-1)
		if not os.path.isdir(d):
			print("'{}' is not a directory".format(d))
			exit(-1)

	gb['wt'] = arg.work_thread
	gb['ct'] = arg.compress_thread
	gb['deep'] = 2147483647 if arg.deep_count < 0 else arg.deep_count
	gb['sensitive'] = arg.s.startswith('y')
	gb['dict'] = "{}m".format(arg.dictionary_size)
	# noinspection PyProtectedMember
	gb['7z'] = arg._7z_path
	# noinspection PyProtectedMember
	gb['deepcall'] = arg._deep
	gb['finished'] = False
	if not os.path.exists('tmp'):
		os.mkdir('tmp')
	if not os.path.exists('old'):
		os.mkdir('old')

	_thread.start_new_thread(print_status, ())
	Manager(gb['path'], gb['sensitive'], gb['wt'])
