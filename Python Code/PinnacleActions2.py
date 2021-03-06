from itertools import chain
from SymmetricGroups1 import compose, inverse, subDescGen, desc, fSActionX

# def shiftFac(n, k):
	# return [*range(k-1), *range(k+1, n), k-1, k]

def nPV(P, V, x):
	return len([*filter(lambda i: i < x, V)]) - len([*filter(lambda i: i < x, P)])

def getPV(x):
	edge = float('inf')
	x = x.copy()
	x.append(edge)
	P = set()
	V = set()
	preV = x.pop(0)
	preD = True
	for j in x:
		newD = preV > j
		if (not preD) and newD:
			P.add(preV)
		elif preD and (not newD):
			V.add(preV)
		preV = j
		preD = newD
	return P, V

def shiftFac(n, k):
	return [k-1, k, *range(k-1), *range(k+1, n)]

def shiftFacInv(n, k):
	return [*range(2, k+1), 0, 1, *range(k+1, n)]

def uLFac(pi, x):
	U = [[]]
	L = []
	piIter = iter(pi)
	val = next(piIter)
	try:
		while True:
			while val >= x:
				U[-1].append(val)
				val = next(piIter)
			U.append([])
			L.append([])
			while val < x:
				L[-1].append(val)
				val = next(piIter)
	except StopIteration:
		pass
	except: raise
	return U, L

def uLFacPlus(pi, x):
	res = [] # res includes (Max Pin, Min Vale, body)
	P = set()
	V = set()
	mP = mV = None
	prev = True
	asc = False
	pVal = float('inf')
	body = []
	for val in pi:
		if asc:
			if pVal >= val:
				P.add(pVal)
				if mP is None: mP = pVal
				mP = max(mP, pVal)
				asc = False
		else:
			if pVal <= val:
				V.add(pVal)
				if mV is None: mV = pVal
				mV = min(mV, pVal)
				asc = True
		pVal = val
		new = (val >= x)
		if prev != new:
			prev = new
			res.append((mP, mV, body))
			mP = mV = None
			body = []
		body.append(val)
	if not asc:
		V.add(pVal)
		if mV is None: mV = pVal
		mV = min(mV, pVal)
	res.append((mP, mV, body))
	if not prev:
		res.append((None, None, []))
	return res, P, V

def ascShift(pi, x, n):
	U, L = uLFac(pi, x + 1)
	(k, Lk), = filter(lambda i: i[1][0] == x or i[1][-1] == x, enumerate(L))
	s = Lk[0] == x
	if s:
		Lk.pop(0)
	else:
		Lk.pop(-1)
	k = (k + n) % len(L)
	if s:
		L[k].insert(0, x)
	else:
		L[k].append(x)
	L.append([])
	return sum(chain.from_iterable(zip(U, L)), [])

def fMax(ops):
	return lambda i: max(filter(ops.__contains__, i))

#0 <= a < b <= ell - 2 = len(L) - 2
def valShift(pi, x, a, b):
	P, V = getPV(pi)
	assert 0 <= a
	assert a <  b
	U, L0 = uLFac(pi, x)
	ell = len(L0)
	k = U.index([x])
	L1 = [*map(tuple, L0)]
	assert b < ell
	tau = shiftFac(ell, k)
	L2 = compose(L1, tau)
	sigma = [0] * len(L1)
	origPos = {val: i for i, val in enumerate(L2)}
	lL = L2[:2]
	rL = L2[2:]
	lL.sort(key = max)
	rL.sort(key = max)
	L3 = lL + rL
	sigma = [origPos[val] for val in L3] # L3 = compose(L2, sigma)
	Lk = L3.pop(a)
	LK = L3.pop(b-1)
	L3.sort(key = max)
	L4 = sorted([Lk, LK], key = fMax(P.union(V))) + L3
	L5 = compose(compose(L4, inverse(sigma)), inverse(tau))
	L5.append([])
	return sum(chain.from_iterable(zip(U, map(list, L5))), [])

def uLPlotDataI(x, k):
	edge = max(x) + 2
	pts = []
	alt = []
	prev = (0, edge)
	k += 1
	for i, j in enumerate((j + 1 for j in x), 1):
		pt = (i, j)
		if prev[1] < k and k < j:
			alt.append(((k - prev[1])*(i - prev[0])/(j - prev[1])+prev[0], k))
		elif k == j:
			alt.append(pt)
		pts.append(pt)
		prev = pt
	return pts, alt, edge

def uLPlotDataD(x, k):
	edge = max(x) + 2
	pts = []
	alt = []
	prev = (0, edge)
	k += 1
	for i, j in enumerate((j + 1 for j in x), 1):
		pt = (i, j)
		if prev[1] > k and k > j:
			alt.append(((k - prev[1])*(i - prev[0])/(j - prev[1])+prev[0], k))
		elif k == j:
			alt.append(pt)
		pts.append(pt)
		prev = pt
	return pts, alt, edge

def uLPlotData(x, k):
	edge = max(x) + 2
	pts = []
	alt = []
	prev = (0, edge)
	k += 1
	for i, j in enumerate((j + 1 for j in x), 1):
		pt = (i, j)
		if (prev[1] < k and k < j) or (prev[1] > k and k > j):
			alt.append(((k - prev[1])*(i - prev[0])/(j - prev[1])+prev[0], k))
		elif k == j:
			alt.append(pt)
		pts.append(pt)
		prev = pt
	return pts, alt, edge

def mainGraphPlot(pts, mark = 'square', color = 'blue', mSize = None):
	out = '\\addplot[color=' + color + ',mark=' + mark
	if mSize is not None:
		out += ',mark size=' + str(mSize) + 'pt'
	out += ']coordinates{'
	out += ''.join(map(str, pts))
	out += '};\n'
	return out

def plotEdges(pts, xMax, xLen, color = 'blue'):
	edge = xMax + 2
	out  = mainGraphPlot(((0, edge), pts[0]), 'none', color)
	out += mainGraphPlot((pts[-1], (xLen + 1, edge)), 'none', color)
	return out

def stdTitle(x):
	out = '$_=('
	out += ', '.join(map(str, (i + 1 for i in x)))
	out += ')$'
	return out

def plotWrapper(plot, xMax, xLen, title = '_'):
	out = '\\begin{tikzpicture}\n\\begin{axis}[\n    height=\\axisdefaultheight*0.8,\n    width=\\textwidth*0.55,\n    title={'
	out += title
	out += '},\n    xtick={'
	out += ', '.join(map(str, range(1, xLen + 1)))
	out += '},\n    ytick={'
	out += ', '.join(map(str, range(1, xMax + 2)))
	out += '},\n    ymajorgrids=true,\n    grid style=dashed,\n    xmin = 0,\n    xmax = ' + str(xLen+1) + ',\n    ymin = 0,\n    ymax = ' + str(xMax + 2) + '\n]\n'
	out += plot
	out += '\\end{axis}\n\\end{tikzpicture}'
	return out

def ascShiftPlot(x, k):
	pts, alt, edge = uLPlotDataI(x, k)
	xMax = max(x)
	xLen = len(x)
	plot = mainGraphPlot(pts)
	plot += plotEdges(pts, xMax, xLen)
	for pt in alt:
		plot += mainGraphPlot((pt,), 'x', 'black', 3)
	plot += '\\addplot[color=black, domain=0:' + str(xLen + 1) + ']{' + str(k+1) + '};\n'
	return plotWrapper(plot, xMax, xLen, stdTitle(x))

def descShiftPlot(x, k):
	pts, alt, edge = uLPlotDataD(x, k)
	xMax = max(x)
	xLen = len(x)
	plot = mainGraphPlot(pts)
	plot += plotEdges(pts, xMax, xLen)
	for pt in alt:
		plot += mainGraphPlot((pt,), 'x', 'black', 3)
	plot += '\\addplot[color=black, domain=0:' + str(xLen + 1) + ']{' + str(k+1) + '};\n'
	return plotWrapper(plot, xMax, xLen, stdTitle(x))

def valShiftPlot(x, p):
	pts, alt, edge = uLPlotData(x, p)
	xMax = max(x)
	xLen = len(x)
	plot = mainGraphPlot(pts)
	for pt in alt:
		if pt[0] < 1 or pt[0] > xLen:
			continue
		plot += mainGraphPlot(((pt[0], 0), (pt[0], edge)), 'none', 'black')
	return plotWrapper(plot, xMax, xLen, stdTitle(x))

def rootGenSub(k, upperFixed, pinLst):
	if not k:
		yield []
		return
	pinLst = pinLst.copy()
	for j in range(2 * k - 1, min(upperFixed, pinLst.pop())):
		for val in rootGenSub(k-1, j - 1, pinLst):
			yield val + [j]

def rootGen(n, P):
	# if not P:
		# yield [*range(n)]
		# return
	P = sorted(P)
	ops = [i for i in range(n) if i not in set(P)]
	unset = [i for i in range(n) if i not in set(P)]
	for posLst in rootGenSub(len(P), n, P):
		out = []
		j = 0
		unSetLst = [*unset]
		pLst = P.copy()
		for i in posLst:
			while j < i:
				out.append(unSetLst.pop(0))
				j += 1
			out.append(pLst.pop(0))
			j += 1
		out.extend(unSetLst)
		yield out

def ActionBasedGen(n, P):
	perms = [*rootGen(n, P)]
	nPerms = []
	for p in P:
		for pi in perms:
			for b in range(2, nPV(*getPV(pi), p)):
				for a in range(0, b):
					nPerms.append(valShift(pi, p, a, b))
		perms.extend(nPerms)
		nPerms.clear()
	for x in range(n):
		for pi in perms:
			P, V = getPV(pi)
			if x in V or x in P:
				continue
			ell = nPV(P, V, x)
			for k in range(1, ell):
				nPerms.append(ascShift(pi, x, k))
		perms.extend(nPerms)
		nPerms.clear()
	for x in range(n):
		for pi in perms:
			_, V = getPV(pi)
			if x in V: continue
			nPerms.append(fSActionX(pi, x))
		perms.extend(nPerms)
		nPerms.clear()
	return perms


































