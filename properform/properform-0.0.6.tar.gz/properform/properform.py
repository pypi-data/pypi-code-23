# -*- coding: utf-8 -*-
# Copyright 2017 ibelie, Chen Jie, Joungtao. All rights reserved.
# Use of this source code is governed by The MIT License
# that can be found in the LICENSE file.

import grpc
import marshal
from properform_pb2 import Void, Profile, PullRequest
from properform_pb2_grpc import ProperformStub

def Touch(addr):
	try:
		stub = ProperformStub(grpc.insecure_channel(addr))
		response = stub.Touch(Void())
		print('OK')
		return response is not None
	except:
		return False

def Push(addr, ID, filename):
	stats = marshal.load(open(filename, 'rb'))
	stub = ProperformStub(grpc.insecure_channel(addr))
	profile = Profile(ID = ID)
	for (f, l, n), (pc, rc, it, ct, callers) in stats.iteritems():
		callee = profile.Python.Stats.add()
		callee.Function.File = f
		callee.Function.Line = l
		callee.Function.Name = n
		callee.Stat.PrimitiveCalls = pc
		callee.Stat.RecursiveCalls = rc
		callee.Stat.InternalTime = it
		callee.Stat.CumulativeTime = ct
		for (f, l, n), (pc, rc, it, ct) in callers.iteritems():
			caller = callee.Callers.add()
			caller.Function.File = f
			caller.Function.Line = l
			caller.Function.Name = n
			caller.Stat.PrimitiveCalls = pc
			caller.Stat.RecursiveCalls = rc
			caller.Stat.InternalTime = it
			caller.Stat.CumulativeTime = ct
	response = stub.Push(profile)
	print('[Properform] Push %s' % (response.Success, ))

def Pull(addr, ID, filename):
	stub = ProperformStub(grpc.insecure_channel(addr))
	profile = stub.Pull(PullRequest(ID = ID))
	stats = {(callee.Function.File, callee.Function.Line, callee.Function.Name):
		(callee.Stat.PrimitiveCalls, callee.Stat.RecursiveCalls,
		callee.Stat.InternalTime, callee.Stat.CumulativeTime, {
			(caller.Function.File, caller.Function.Line, caller.Function.Name):
			(callee.Stat.PrimitiveCalls, callee.Stat.RecursiveCalls,
			callee.Stat.InternalTime, callee.Stat.CumulativeTime)
			for caller in callee.Callers}) for callee in profile.Python.Stats}
	f = file(filename, 'wb')
	try:
		marshal.dump(stats, f)
	finally:
		f.close()
