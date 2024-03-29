
from timeit import timeit



def numIterable(n, v): return range(v, n + v)
def bitGen(n):
	while n:
		yield n & 1
		n >>= 1

def powGen(iterSrc):
	return map(
		lambda x: map(
			lambda i: i[1],
			filter(
				lambda i: i[0],
				zip(
					bitGen(x),
					iterSrc
				)
			)
		),
		range(1 << len(iterSrc))
	)

def pinSetCandGen(n, v):
	return map(list, powGen(numIterable(n, v)))

def admPinFilt(P, v):
	for i, p in enumerate(P, 1):
		if p - v < 2 * i: return False
	return True

def admPinGen(n, v):
	return filter(lambda i: admPinFilt(i, v), pinSetCandGen(n, v))



def checkCountsSingle(F, G, n, P, v):
	return F(n, P, v) == G(n, P, v)

def checkCountsPoly(F, G, n, v):
	return all(map(lambda i: checkCountsSingle(F, G, n, i, v), admPinGen(n, v)))

def checkCountsPoly_getFail(F, G, n, v):
	for P in admPinGen(n, v):
		if checkCountsSingle(F, G, n, P, v): continue
		return (n, P, v)
	return None



def checkSg3fcBySg3npgcSingle(n, P, v):
	return sg3fCount(n, P, v) == sg3newPinGenCount(n, P, v)

def checkSg3fcBySg3npgcPoly(n, v):
	return all(map(lambda i: checkSg3fcBySg3npgcSingle(n, i, v), admPinGen(n, v)))

def checkSg3fcBySg3npgcPoly_getFail(n, v):	
	for P in admPinGen(n, v):
		if checkSg3fcBySg3npgcSingle(n, P, v): continue
		return (n, P, v)
	return None

def checkPccBySg3fcSingle(n, P, v):
	return pcCount(n, P, v) == sg3fCount(n, P, v)

def checkPccBySg3fcPoly(n, v):
	return all(map(lambda i: checkPccBySg3fcSingle(n, [*i], v), admPinGen(n, v)))

def checkPccBySg3fcPoly_getFail(n, v):	
	for P in admPinGen(n, v):
		if checkPccBySg3fcSingle(n, P, v): continue
		return (n, P, v)
	return None

def checkPcSg3fcavsgBySg3fcSingle(n, P, v):
	return pcSg3fcavsg(n, P, v) == sg3fCount(n, P, v)

def checkPcSg3fcavsgBySg3fcPoly(n, v):
	return all(map(lambda i: checkPcSg3fcavsgBySg3fcSingle(n, [*i], v), admPinGen(n, v)))

def checkPcSg3fcavsgBySg3fcPoly_getFail(n, v):	
	for P in admPinGen(n, v):
		if checkPcSg3fcavsgBySg3fcSingle(n, P, v): continue
		return (n, P, v)
	return None

def checkOfcBySg3fcSingle(n, P, v):
	return pcOrigFCount(n, P, v) == sg3fCount(n, P, v)

def checkOfcBySg3fcPoly(n, v):
	return all(map(lambda i: checkOfcBySg3fcSingle(n, [*i], v), admPinGen(n, v)))

def checkOfcBySg3fcPoly_getFail(n, v):	
	for P in admPinGen(n, v):
		if checkOfcBySg3fcSingle(n, P, v): continue
		return (n, P, v)
	return None



def timeCounter(func, n, P, v, count = 1):
	return timeit(lambda: func(n, P, v), number = count) / count

def timeOfc(n, P, v, count = 1):
	return timeit(lambda: pc.origFCount(n, P, v), number = count) / count

def timePcCount(n, P, v, count = 1):
	return timeit(lambda: pc.fullCount(n, P, v), number = count) / count

def simpleFactorial(n):
	prod = 1
	for k in range(1, n + 1): prod *= k
	return prod

def totalCountVerif(func, n, v):
	acc = 0
	for P in admPinGen(n, v):
		acc += func(n, P, v)
	return acc == simpleFactorial(n)
































