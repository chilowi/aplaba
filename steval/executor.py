#! /usr/bin/env python3
"""
Execute a Python module and save some properties about it
"""

from codemetrics import CodeMetrics

import time, ast, sys, io
from collections import namedtuple

globalvars = globals

class ExecutionResult(object):
	def __init__(self):
		self.executed = False
		self.result = None
		self.exception = None
		self.stdout = None
		self.stderr = None
		self.handled_files = None
		self.time = 0.0
	def _start(self):
		self._start_time = time.process_time()
	def _end(self, result, exception=None, globals=None):
		self.executed = True
		self.time = time.process_time() - self._start_time
		self.result = result
		self.exception = exception
		self.globals = globals
	def __repr__(self):
		return "result={}, exception={}, stdout={}, stderr={}, files={}, time={}".format(self.result, self.exception, self.stdout, self.stderr, self.handled_files, self.time)
		
class ExecutionEnvironment(object):
	def __init__(self, globals=None):
		self.result = ExecutionResult()
		self.globals = globalvars() if globals is None else globals
		# track the handled files
		self._handled_files = set()
		this = self
		def _open(self, filepath, *kargs, **kwargs):
			this._handled_files.add(filepath)
		self.globals["open"] = _open
	def execute_impl(self):
		raise NotImplementedError()
	def execute(self):
		stdout, stderr = (sys.stdout, sys.stderr)
		try:
			sys.stdout, sys.stderr = (io.StringIO(), io.StringIO())
			self.execute_impl()
			self.result.stdout = sys.stdout.getvalue().strip()
			self.result.stderr = sys.stderr.getvalue().strip()
			self.result.handled_files = self._handled_files
		finally:
			sys.stdout, sys.stderr = (stdout, stderr) # restore old stdout and stderr
		
	
		
class CodeExecutionEnvironment(ExecutionEnvironment):
	@classmethod
	def from_file(self, filepath):
		with open(filepath, "r") as f:
			return CodeExecutionEnvironemnt(f.read())
	def __init__(self, code, globals=None):
		super(CodeExecutionEnvironment, self).__init__(globals)
		self.code = code
		self.ast = ast.parse(code)
		self.metrics = CodeMetrics(self.code, self.ast)
	def execute_impl(self):
		g = dict(self.globals)
		self.result._start()
		try:
			exec(self.code, g)
		except Exception as e:
			exception = e
		else:
			exception = None
		self.result._end(None, exception=exception, globals={k: g[k] for k in g if k not in self.globals})
	def execute_function(self, name, *kargs, **kwargs):
		if not self.result.executed:
			self.execute()
		function = self.result.globals.get(name)
		if function is None:
			return None
		env = FunctionExecutionEnvironment(function, *kargs, **kwargs)
		env.execute()
		return env
	
class FunctionExecutionEnvironment(ExecutionEnvironment):
	def __init__(self, function, *kargs, **kwargs):
		 super(FunctionExecutionEnvironment, self).__init__()
		 self.function = function
		 self.kargs, self.kwargs = (kargs, kwargs)
	def execute_impl(self):
		"""Execution the function"""
		self.result._start()
		try:
			result = self.function(*self.kargs, **self.kwargs)
		except Exception as e:
			exception = e
			result = None
		else:
			exception = None
		self.result._end(result, exception)
		
class FunctionTestException(Exception):
	def __init__(self, name, arguments, student_result, teacher_result):
		self.name = name
		self.arguments = arguments
		self.student_result = student_result
		self.teacher_result = teacher_result
	def __repr__(self):
		return """Results of the execution of the function {} shows discrepancies between student and teacher versions:
Arguments: {}
Student result: {}
Teacher result: {}""".format(self.name, self.argument, self.student_result, self.teacher_result)
		
class ExecutionEnvironments(object):
	def __init__(self, student=None, teacher=None):
		self._executed = False
		self.student = CodeExecutionEnvironment.from_file(sys.argv[1]) if student is None else CodeExecutionEnvironment(student)
		self.teacher = CodeExecutionEnvironment.from_file(sys.argv[2]) if teacher is None else CodeExecutionEnvironment(teacher)
	def execute(self):
		self.student.execute()
		self.teacher.execute()
		self._executed = True
	def execute_function(self, name, *kargs, **kwargs):
		StudentTeacherResult = namedtuple("StudentTeacherResult", "student teacher")
		return StudentTeacherResult(*[e.execute_function(name, *kargs, **kwargs) for e in (self.student, self.teacher)])
	def test_results(self, function_name, *argument_sets, result_comparator = lambda x, y: x.result == y.result):
		for arguments in argument_sets:
			r = self.execute_function(function_name, *arguments)
			if not result_comparator(r.student.result, r.teacher.result):
				raise FunctionTestException(function_name, arguments, r.student.result, r.teacher.result)

if __name__ == "__main__":
	test_code = """
import sys
def fib(n):
	return fib(n-1) + fib(n-2) if n > 1 else 1
print("Little message on stdout", file=sys.stdout)
print("Little message on stderr", file=sys.stderr)
"""
	test_code2 = """
def fib(n):
	if n < 2: return 1
	v, w = (1, 1)
	for k in range(2, n+1):
		tmp = w
		w = v + w
		v = tmp
	return w
"""
	cee = CodeExecutionEnvironment(test_code)
	print("Vocabulary: {}".format(cee.metrics.vocabulary))
	print("AST height: {}".format(cee.metrics.height))
	cee.execute()
	print("Result: {}".format(cee.result))
	for a in (1,2,3,4,5, 6, 7, 8, 9, 10):
		print(cee.execute_function("fib", a).result)
	ExecutionEnvironments(test_code, test_code2).test_results("fib", *[ (x,) for x in range(0, 10) ])
	print("The end.")
