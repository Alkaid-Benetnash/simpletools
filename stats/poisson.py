import numpy as np
import matplotlib.pyplot as plt
import pdb

# assuming we want to reason about a poisson process that on average has `rate`
# events happen in a fixed-time interval
rate = 10
NSamples = 100000
Nbins = min(rate, 200)
def plotPoisson(ax):
    poissonSample = np.random.poisson(rate, NSamples)
    ax.hist(poissonSample,Nbins, density=True)

def plotPoissionSimulateInterval(ax, intervals, alpha):
    simulated = []
    accu = 0.0
    cnt = 0
    for interval in intervals:
        accu += interval
        if accu > 1.0:
            simulated.append(cnt)
            accu -= 1.0
            cnt = 1
        else:
            cnt += 1
    ax.hist(simulated, Nbins, density=True, alpha=0.5)

def plotPoissonSimulateExp(ax):
    expSample = np.random.exponential(1/rate, NSamples * rate)
    plotPoissionSimulateInterval(ax, expSample, 0.5)

def plotPoissionSimulateDBBench(ax):
    rand = np.random.rand(NSamples * rate)
    dbBenchSample = -np.log(rand) / rate
    plotPoissionSimulateInterval(ax, dbBenchSample, 0.3)

fig, (ax) = plt.subplots(1, 1, figsize=(5,4))
plotPoisson(ax)
plotPoissonSimulateExp(ax)
plotPoissionSimulateDBBench(ax)
plt.show()
