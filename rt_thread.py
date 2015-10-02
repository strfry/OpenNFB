from ctypes import cdll, Structure, c_uint, c_int, c_bool, c_voidp, sizeof, byref
import sys

class thread_time_constraint_policy(Structure):
	_fields_ = [
		('period', c_uint),
		('computation', c_uint),
		('constraint', c_uint),
		('preemptible', c_bool),
	]

class thread_precedence_policy(Structure):
	_fields_ = [('importante', c_int)]

THREAD_TIME_CONSTRAINT_POLICY = c_uint(2)
THREAD_TIME_CONSTRAINT_POLICY_COUNT = c_uint(sizeof(thread_time_constraint_policy) // sizeof(c_uint))

THREAD_PRECEDENCE_POLICY = c_uint(3)
THREAD_PRECEDENCE_POLICY_COUNT = c_uint(sizeof(thread_precedence_policy) // sizeof(c_uint))

lib = None

def set_realtime(period, computation, constraint):
	if sys.platform != 'darwin':
		print ('Warning: set_realtime not implemented on this platform')

	global lib
	lib = cdll.LoadLibrary('libSystem.B.dylib')
	lib.pthread_self.restype = c_voidp

	pthread_id = lib.pthread_self()
	thread_id = lib.pthread_mach_thread_np(c_voidp(pthread_id))

	print (pthread_id, thread_id)
	# TODO: conversion from float seconds to mach absolute time values (nanoseconds)


	ttcpolicy = thread_time_constraint_policy(period, computation, constraint, False)
	result = lib.thread_policy_set(c_uint(thread_id), THREAD_TIME_CONSTRAINT_POLICY,
		byref(ttcpolicy), THREAD_TIME_CONSTRAINT_POLICY_COUNT)

	assert result == 0

	tcpolicy = thread_precedence_policy(63)
	#result = lib.thread_policy_set(c_uint(thread_id), THREAD_PRECEDENCE_POLICY,
	#	byref(tcpolicy), THREAD_PRECEDENCE_POLICY_COUNT)

	assert result == 0
	import gc
	gc.disable()
	

def thread_yield():
	lib.thread_switch(0, 0, 0)
