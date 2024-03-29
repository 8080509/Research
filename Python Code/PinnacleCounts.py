
import itertools as it

"""

We are going to count the number of permutations with a given pinnacle set according to our count.

As a reminder, the count follows:

count = 2^{n - |P| - 1} sum_{V in VV(P)} prod_{p in P} binom{N_{PV}(p)}2 prod_{k in [n] \ (P cup V)} N_{PV}

VV(P) being the set of admissible vale sets

"""

# Pinnacle Set Format [p1, p2, p3,..., p_ell]

def dualBoundWeakCompGenSub(ub, lb, rem, storage, acc = 0, ind = 0):
	"""
	Generates weak compositions, subject to an upper bound (ub) on each item and a lower bound (lb) for the running total.
	Results are placed in 'storage'.
	*Caution, the generator only yields references to 'storage'!
	
	ub - list of upper bounds per item
	lb - list of lower bounds for the running total
	rem - remaing value to place in the composition
	storage - list to store the results
	
	acc - running total for this stage of the recursion
		should be zero if called by user
	ind - index of ub, lb, and storage for this layer of the recursion to use
		should be zero if called by user
	
	Requirements:
		Expects rem + acc == lb[-1]
			Will trigger an IndexError if rem + acc > lb[-1]
			If rem + acc < lb[-1], the condition will always fail and will thus yield no values, but not except
		ub, lb, and storage should all have the same length
	
	Generator return value - Once exhausted, the generator returns a boolean to indicate if it yielded anything
		Mainly for internal use
	"""
	if not rem: # if nothing left to store, set remaining entries to zero and return
		for i in range(ind, len(storage)): storage[i] = 0
		yield storage
		return True
	u = min(ub[ind], rem) # we may store no more than the upper bound, or the remaining quantity
	l = max(lb[ind] - acc, 0) - 1 # we may store no less than what is missing to meet the lower bound
	nInd = ind + 1
	for i in range(u, l, -1):
		storage[ind] = i
		if not (yield from dualBoundWeakCompGenSub(ub, lb, rem - i, storage, acc + i, nInd)):
			# if the next layer could not meet the restrictions, we are done in this layer.
			return i != u
	return u != l

def primaryWeakCompGen(bounds, ell, storage):
	"""
	Generates weak compositions as requested in the paper
	
	bounds - list of upper bounds per item
	ell - number to partition
	storage - place to store the result
	
	Requirements:
		Expects ell == len(bounds) == len(storage)
	"""
	return dualBoundWeakCompGenSub(bounds, range(1, ell + 1), ell, storage)

def gapCards(P, v):
	"""
	Produces the list of the cardinalities of the gap sets derived from pinnacle set P, and minimum value v.
	
	Returns g, a list gap cardinalities.
	"""
	
	ell = len(P)
	g = [None] * ell
	
	prev = v
	for i in range(ell):
		p = P[i]
		g[i] = p - prev - 1
		prev = p
	
	return g

def gapSets(P, v):
	"""
	Produces the list of gap sets and the list of corresponding cardinalities derived from pinnacle set P and minimum value v.
	
	Returns (G, g), where G is the list of gap sets, and g is the corresponding cardinalities.
	"""
	ell = len(P)
	G = [None] * ell
	g = [None] * ell
	prev = v
	for i in range(ell):
		p = P[i]
		G[i] = range(prev + 1, p)
		g[i] = p - prev - 1
		prev = p
	return G, g

# def NPVPGen(P, t):
	# N = 2
	# for p, ti in zip(P, t):
		# N += ti - 1
		# yield N

factorialMemo = [1]
def factorialMemoBuild(N):
	"Internal use"
	k = len(factorialMemo)
	prev = factorialMemo[k - 1]
	while k <= N:
		prev *= k
		factorialMemo.append(prev) #fM[k] = prev = fM[k-1] * k
		k += 1
	return prev

def factorial(n):
	"""
	Memoized factorial function
	Do not use for large factorials, as it will store all intermediate results.
	"""
	if n < len(factorialMemo): return factorialMemo[n]
	return factorialMemoBuild(n)

def binom(n, k): return factorial(n) // (factorial(k) * factorial(n - k))
def binom2(n): return (n * (n - 1)) >> 1

def intPow(b, e):
	out = 1
	while e:
		if e & 1: out *= b
		b *= b
		e >>= 1
	return out

def neg1Pow(e):
	return 1 - ((e & 1) << 1)

def compCount(ell, g, t):
	"""
	Counts the number of permutations that would ultimately be generated by the given weak composition.
	
	ell - Cardinality of the pinnacle set
	g - list of gap set cardinalities
		See gapCards
	t - composition
		See primaryWeakCompGen
	
	Requirements:
		g and t should both be of length ell
		t[i] <= g[i]
		i <= sum(t[:i])
	"""
	N = 1
	prod = 1
	for i in range(ell):
		ti = t[i]
		acc = 0
		for k in range(ti+1):
			acc += binom(ti, k) * neg1Pow(k) * (N ** g[i])# intPow(N, g[i])
			N += 1
		# N' = N + ti + 1
		N -= 1
		acc //= factorial(ti)
		prod *= binom2(N) * neg1Pow(ti) * acc
		N -= 1
	return prod

def fullCount(n, P, v):
	"""
	Counts the number of permutations in Sn with pinnacle set P.
	
	n - n
	P - pinnacle set, as a list sorted in increasing order
	v - minimum value
		Will generally be either 0 or 1, depending on convention.
	
	Requirements:
		P should be a strictly increasing list or range
		v < P[0]
		P[-1] < n + v
	"""
	ell = len(P)
	g = gapCards(P, v)
	t = [0] * ell
	acc = 0
	for _ in primaryWeakCompGen(g, ell, t):
		acc += compCount(ell, g, t)
	return acc << (n - ell - 1)

def valeSetGen(P, v):
	"""
	Generates vale sets following the method described in the paper.
	
	P - pinnacle set as a sorted list
	v - minimum value (will always be a vale)
	"""
	ell = len(P)
	G, g = gapSets(P, v)
	t = [0] * ell
	base = {v}
	return it.chain.from_iterable(
		map(
			lambda i: it.starmap(
				base.union,
				it.product(*map(it.combinations, G, i))
			),
			primaryWeakCompGen(g, ell, t)
		)
	)

def pvCount(P, V, v):
	"""
	Counts the number of permutations which may be generated from a given pinnacle set P, vale set V, and minimum vale v.
	
	P - pinnacle set as an increasing list
	V - vale set (preferably as a set or equivalent)
	v - minimum vale
		must be min(V)
	"""
	prod = 1
	N = 1
	prev = v
	for p in P:
		for k in range(prev + 1, p):
			if k in V: N += 1; continue
			prod *= N
		prod *= N
		N -= 1
		prod *= N
		prod >>= 1
		prev = p
	return prod

def origFCount(n, P, v):
	"""
	See fullCount
	
	Returns the exact same values.
	This is just an alternative implementation for efficiency comparison.
	Follows the original description of the counting algorithm, by iterating over all admissible vale sets.
	"""
	acc = 0
	for V in valeSetGen(P, v):
		acc += pvCount(P, V, v)
	return acc << (n - len(P) - 1)

def nonNegWalkGenSub(ell, ind, acc, storage):
	"INCOMPLETE"
	if ind == ell:
		yield (acc, storage)
		return
	nInd = ind + 1
	if acc:
		storage[ind] = -1
		yield from nonNegWalkGenSub(ell, nInd, acc - 1, storage)
	storage[ind] = 0
	yield from nonNegWalkGenSub(ell, nInd, acc, storage)
	storage[ind] = 1
	yield from nonNegWalkGenSub(ell, nInd, acc + 1, storage)

def nonNegWalkGen(storage):
	"INCOMPLETE"
	return nonNegWalkGenSub(len(storage), 0, 0, storage)

def binomList(n):
	"INCOMPLETE"
	out = [0] * (n + 1)
	for i in range(n + 1):
		out[i] = binom(n, i)
	return out

def slopeCount(n, P, v):
	"INCOMPLETE"
	acc = 0
	ell = len(P)
	t = [0] * ell
	binom2k = binomList(2)
	for T, _ in nonNegWalkGen(t):
		prod = neg1Pow(T + ell)
		prev = v
		Tk = T + 1
		for (tk, pk) in zip(reversed(t), P):
			prod *= binom2k[tk + 1] * (Tk ** (pk - prev))
			prev = pk
		acc += prod
	return acc << (n - (2 * ell) - 1)

def slopeCount2(n, P, v):
	"INCOMPLETE"
	acc = 0
	ell = len(P)
	t = [0] * ell
	binom2k = binomList(2)
	pInd = lambda i: P[i] if i >= 0 else v
	for T, _ in nonNegWalkGen(t):
		prod = neg1Pow(T + ell)
		prev = v
		for k in range(ell):
			prod *= binom2k[t[k] + 1] * (sum(t[:k+1], 1) ** (pInd[ell - k] - pInd[ell - k - 1]))
		acc += prod
	return acc << (n - (2 * ell) - 1)













































