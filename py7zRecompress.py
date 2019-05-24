#!/usr/bin/python3
# coding=utf-8
import _thread
import argparse
import os
import platform
import shutil
import subprocess
import sys
import threading
import time
from typing import *

_7zCompressable = ('.7z', '.xz', '.zip', '.tar', '.jar')
_7zCompressArgs = '"{_7z}" a -sdel -mx9 -ssw -mmt{thread} -myx9 -md{dictsz}m -aoa -mfb273 ' \
				  '-ms=on "{dest}" "{src}"'
_xzCompressArgs = '"{_7z}" a -sdel -txz -mx9 -ssw -mmt{thread} -myx9 -md{dictsz}m -aoa -mfb273 ' \
				  '-ms=on "{dest}" "{src}"'
_zipCompressArgs = '"{_7z}" a -sdel -tzip -mx9 -mfb258 -mmt{thread} -ssw -aoa "{dest}" "{src}"'
_7zExtractArgs = '"{_7z}" x "{src}" "-o{dest}" -p"{pw}" -y -r'

_default7z = "C:\\Program Files\\7-Zip\\7z.exe" if platform.system() == 'Windows' and os.path.exists(
	"C:\\Program Files\\7-Zip\\7z.exe") else '7z'

gb = {}  # type:Dict[Union[str,int,list,tuple]]


def terminal_width():
	try:
		term_width, void = os.get_terminal_size()
	except Exception:
		term_width = 80
	return min(max(20, term_width), 120) - 4


def compress(_7z = _default7z, source = '', dest = os.getcwd(), dictionary_size = 96, method = '7z') -> bool:
	if source == '':
		return False
	arg = gb['carguments'] if len(gb['carguments']) > 0 else ''
	if method == 'xz':
		command = _xzCompressArgs.format(_7z = _7z, src = os.path.join(source, '*'), dest = dest,
										 dictsz = dictionary_size, thread = gb['ct']) + arg
		return execommand(command)
	elif method == 'zip' or method == 'jar':
		command = _zipCompressArgs.format(_7z = _7z, src = os.path.join(source, '*'), dest = dest,
										  dictsz = dictionary_size, thread = gb['ct']) + arg
		return execommand(command)
	else:
		command = _7zCompressArgs.format(_7z = _7z, src = os.path.join(source, '*'), dest = dest,
										 dictsz = dictionary_size, thread = gb['ct']) + arg
		return execommand(command)


def extract(_7z = _default7z, source = '', dest = os.path.join(os.getcwd(), 'tmp')) -> bool:
	if source == '':
		return False
	command = _7zExtractArgs.format(_7z = _7z, src = source, dest = dest, pw = gb['password']) + (
		gb['earguments'] if len(gb['earguments']) > 0 else '')
	return execommand(command, gb['timeout'])


def test7z(file, pw = ''):
	return not execommand(r'"%s" t -p"%s" "%s"' % (gb['7z'], pw, file), exitCode = 2)


def execommand(command = '', timeout = 2147483647, exitCode = 0) -> True | False:
	"""
	Execute following command \n
	:param exitCode: return true if exit-code equals this parameter
	:param command: a command <br>
	:param timeout: max running time <br>
	:return: True if process finished properly or False if reached timeout or exit code it not zero
	"""
	try:
		return exitCode == subprocess.call(command, shell = True,
										   stdout = subprocess.DEVNULL,
										   stderr = sys.stdout,
										   timeout = timeout)
	except subprocess.TimeoutExpired:
		return False


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

		self.old = os.path.join(os.getcwd(), 'old', str(int(time.time())) + '-' + self.name)
		self.path = path
		self.status = 'idle'

	def backup(self):
		try:
			os.rename(self.path, self.old)
		except OSError:
			shutil.move(self.path, self.old)
		return self.old

	@staticmethod
	def deep_compress(folder):
		return execommand('"%s" "%s" "%s" -wt %s -ct %s -d %s -s %s -dc %s -7z "%s" -n yes -_deep %s' % (
			sys.executable, sys.argv[0], folder, gb['wt'], gb['ct'], gb['deep'] - 1, 'yes', gb['dict'], gb['7z'],
			True))

	def undo(self):
		try:
			os.rename(self.old, self.path)
		except OSError:
			shutil.move(self.old, self.path)

	# noinspection SpellCheckingInspection
	def recompress(self):
		if not test7z(self.path) and gb['skip']:
			print('[Skip] %s cause Locked' % self.path)
			return None
		try:
			cll()
			print("\rWorking on [%s]" % self)
			temp = os.path.join(os.getcwd(), 'tmp', str(int(time.time())) + '-' + self.name.replace('.', '-'))
			self.status = 'creating temp'
			if not os.path.exists(temp):
				os.mkdir(temp)
			self.status = 'backing up'
			backup = self.backup()
			self.status = 'extracting'
			if not extract(source = backup, dest = temp):
				cll()
				raise Error.ExtractError("\r[Error] when extract archive %s\n" % self)
			cll()
			stats = DirStats(temp)
			print("\rFound [%s] files | [%s] directories | size %0.6f Mbytes in [%s]" % (
				stats.stats['file'], stats.stats['folder'], (stats.stats['size'] / 1024.0) / 1024.0, temp))
			if gb['deep'] > 1 and deeper(temp):
				self.status = 'waiting deep compress'
				if not self.deep_compress(temp):
					cll()
					sys.stderr.write("\r[Error] when digging in archive %s\n" % self)

			self.status = 'compressing'
			if not compress(source = temp, dictionary_size = gb['dict'], dest = self.out, method = self.type):
				raise Error.CompressError("\r[Error] when compressing %s\n" % self)
			self.status = 'removing temp'
			try:
				os.rmdir(temp)
			except OSError:
				shutil.rmtree(temp)
			self.status = 'done'
			Manager.working.remove(self)
			if not gb['no_keep']:
				saveInfo(self.path, self.old)
			else:
				os.remove(self.old)
			cll()
			print("\r[done] %s" % self)
		except Exception as e:
			sys.stderr.write("\r[Error] %s | [Cause] %s\n" % (self, e.args[0]))
			self.undo()
			sys.stderr.write("\r[Info] %s undo successfully!\n" % self)

	def __str__(self):
		return self.path


class Error:
	class ExtractError(IOError):
		def __init__(self, msg = ''):
			self.msg = msg

		def __str__(self):
			return self.msg

	class CompressError(IOError):
		def __init__(self, msg = ''):
			self.msg = msg

		def __str__(self):
			return self.msg


class Manager:
	files = []  # type: List[File,...]
	working = []  # type: List[File,...]
	total = 0

	def __init__(self, locations, sensitive = False, threads = 1):
		self.run(threads)
		if len(gb['only']) < 1:
			file_types = _7zCompressable if sensitive else (*_7zCompressable, '.rar', '.gz')
			if len(gb['exclude']) > 0:
				file_types = (x for x in (*file_types, *gb['include']) if not x.endswith((*gb['exclude'],)))
		else:
			file_types = (*gb['only'],)
		for location in locations:
			print("Scanning directory '%s'" % location)
			temp = [File(os.path.join(root, f), sensitive)
					for root, dirs, files in os.walk(location) for f
					in files if f.endswith((*file_types,))]
			Manager.total += len(temp)
			Manager.files.extend(temp)
		print("Found %s files!" % Manager.total)
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


class DirStats:
	def __init__(self, directory):
		self.dir = directory
		self.stats = {'size': 0, 'folder': 0, 'file': 0}  # type: Dict[str:int]
		self.walk()

	def walk(self, path = None):
		if path is None:
			path = self.dir
		for f in os.listdir(path):
			f = os.path.join(path, f)
			if os.path.isdir(f):
				self.stats['folder'] += 1
				self.walk(f)
			elif os.path.isfile(f):
				self.stats['size'] += os.stat(f).st_size
				self.stats['file'] += 1

	def __str__(self):
		return "%s folder | %s files | size %s MBytes" % (
			self.stats['folder'], self.stats['file'], ((self.stats['size'] / 1024.0) / 1024.0))


# clear line
def cll():
	print('\r', ' ' * (terminal_width() + 3), end = '', sep = '')


def saveInfo(path, old):
	file = open('info.txt', 'a+')
	file.write('[OLD] %s -> [ORIGINAL] %s' % (old, path))
	file.newlines()
	file.close()


def print_status():
	while len(Manager.files) < 1 and not gb['finished']:
		time.sleep(1)
	while len(Manager.working) > 0 or len(Manager.files) > 0:
		for work in Manager.working:
			cll()
			print("\r[%s] %s" % (work.status, wrap(work, -(len(work.status) + 3))), end = '')
			time.sleep(2)
		cll()
		print("\rRunning [%s] task | Remaining [%s] files" % (len(Manager.working), len(Manager.files)), end = '')
		time.sleep(2)
		print(gen_prog(terminal_width()), end = '')
		time.sleep(2)
	cll()
	print('\rDone!? | %s file has been re-compressed' % Manager.total)
	exit(0)


def gen_prog(leng):
	total = Manager.total
	remaining = len(Manager.files)
	working = len(Manager.working)
	done = total - remaining - working
	str_rem = str(done) + '/' + str(total) + ' '
	leng -= len(str_rem)
	return "\r%s[%s%s%s]" % (str_rem, '|' * int((done / total) * leng),
							 ':' * int((working / total) * leng),
							 '-' * int((remaining / total) * leng))


def wrap(msg, length = 0):
	if length < 0:
		length += terminal_width()
	if length == 0:
		length = terminal_width()
	msg = str(msg)
	return ('...' + msg[len(msg) - length:].strip(' \r\n\t')) if len(msg) > length else msg


def deeper(path = ''):
	for root, dirs, files in os.walk(path):
		for f in files:
			if f.endswith(_7zCompressable):
				return True
	return False


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
	args.add_argument('-e', '--exclude', default = '', dest = 'exclude', type = str,
					  help = 'excluded file extension separator is ; like "-e 7z;xz"')
	args.add_argument('-i', '--include', default = '', dest = 'include', type = str,
					  help = 'include file extension separator is ; like "-i iso;wim"')
	args.add_argument('-o', '--only', default = '', dest = 'only', type = str,
					  help = 're-compress only file extension separator is ; like "-o zip"')
	args.add_argument('-n', '--no-keep', default = 'no', dest = 'no_keep', type = str,
					  choices = ('y', 'yes', 'n', 'no'),  help = 'if yes will keep old file')
	args.add_argument('-t', '--timeout', default = 900, dest = 'timeout', type = int,
					  help = 'timeout in second if extract time is longer than the specified time program will abort this file')
	args.add_argument('-p', '--password', default = '', dest = 'password', type = str,
					  help = 'password to extract archive file')
	args.add_argument('-ca', '--compress-arguments', default = '', dest = 'compress_arguments', type = str,
					  help = 'additional argument when compress for 7zip')
	args.add_argument('-ea', '--extract-arguments', default = '', dest = 'extract_arguments', type = str,
					  help = 'additional argument when extract for 7zip')
	args.add_argument('-skip', '--skip-locked', default = '', dest = 'skip', type = str,
					  choices = ('y', 'yes', 'n', 'no'), help = 'skip locked file')
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
	gb['dict'] = arg.dictionary_size
	# noinspection PyProtectedMember
	gb['7z'] = arg._7z_path
	# noinspection PyProtectedMember
	gb['deepcall'] = arg._deep
	gb['finished'] = False
	gb['exclude'] = arg.exclude.split(';')
	gb['include'] = arg.include.split(';')
	gb['only'] = arg.only.split(';')
	gb['no_keep'] = arg.no_keep.startswith('y')
	gb['timeout'] = arg.timeout
	gb['carguments'] = arg.compress_arguments
	gb['earguments'] = arg.extract_arguments
	gb['password'] = arg.password
	gb['skip'] = arg.password == '' or arg.skip.startswith('y')
	if len(gb['include'][0]) < 1:
		gb['include'] = []
	if len(gb['exclude'][0]) < 1:
		gb['exclude'] = []
	if len(gb['only'][0]) < 1:
		gb['only'] = []

	gb['include'] = ['.' + i if not i.startswith('.') else i for i in gb['include']]
	gb['only'] = ['.' + i if not i.startswith('.') else i for i in gb['only']]
	if not os.path.exists('tmp'):
		os.mkdir('tmp')
	if not os.path.exists('old'):
		os.mkdir('old')
	_thread.start_new_thread(print_status, ())
	Manager(gb['path'], gb['sensitive'], gb['wt'])
