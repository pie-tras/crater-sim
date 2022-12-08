import os
import math
import random
import numpy as np
import imageio.v3 as iio

from matplotlib import pyplot as plt

class CraterSim:

    def __init__(self, terrainLength, minCraterRadius, maxCraterRadius, surfaceValue, craterValue):
        self.terrainLength = terrainLength
        self.minCraterRadius = minCraterRadius
        self.maxCraterRadius = maxCraterRadius
        self.surfaceValue = surfaceValue
        self.craterValue = craterValue

        self.data = np.full((terrainLength, terrainLength, 3), [surfaceValue, surfaceValue, surfaceValue], dtype=np.uint8)

    def crater(self, x, y, radius, hidesOthers, outlineMode=False):
        step = math.acos(1 - 1/radius)
        t = 0.0
        while t < 360.0:
            target = range(int(radius))
            if outlineMode:
                target = range(int(radius) - 4, int(radius))
            for r in target:
                xPoint = int(x + (r * math.cos(math.radians(t))))
                yPoint = int(y + (r * math.sin(math.radians(t))))
                if xPoint > -1 and xPoint < self.terrainLength and yPoint > -1 and yPoint < self.terrainLength:
                    # percent = r/radius
                    v = self.craterValue
                    rc = v

                    if hidesOthers:
                        rc = 255

                    if not outlineMode:
                        if r > radius - 4:
                            v = 0
                            rc = 0

                    self.data[xPoint, yPoint] = [rc, v, v]
            t += step

    def isBVisible(self, A, B):
        if A[2] > B[2]:
            dis = math.sqrt((B[0] - A[0])**2 + (B[1] - A[1])**2)
            return dis > (1 - 0.7) * A[2]

        return True

    def generateCraters(self, steps):
        self.craterList = []
        self.visCraterList = []

        self.timeSteps = []
        self.timeCounts = []
        self.visCounts = []

        self.binCraters(4)

        sim.createPlots()
        
        for i in range(steps):
            xPos = random.uniform(0.0, self.terrainLength)
            yPos = random.uniform(0.0, self.terrainLength)
            radius = math.exp(random.uniform(math.log(self.minCraterRadius), math.log(self.maxCraterRadius)))
            nextCrater =[xPos, yPos, radius]
            hidesOthers = False
            queueRemove = []
            for c in self.visCraterList:
                if not self.isBVisible(nextCrater, c):
                    hidesOthers = True
                    queueRemove.append(c)

            for c in queueRemove:
                self.visCraterList.remove(c)
                
            self.craterList.append(nextCrater)
            self.visCraterList.append(nextCrater)
            sim.crater(xPos, yPos, radius, hidesOthers, outlineMode=True)

            self.timeSteps.append(i)
            self.timeCounts.append(i + 1)
            self.visCounts.append(len(self.visCraterList))

            self.binCraters(4)
            self.drawVisuals(i)

    def binCraters(self, binStep):
        self.bins = []
        self.cCounts = []
        self.vCCounts = []

        size = self.minCraterRadius
        binIndex = 0
        while size < self.maxCraterRadius:
            self.bins.append(size)
            self.cCounts.append(0)
            self.vCCounts.append(0)

            for c in self.craterList:
                if c[2] <= size:
                    self.cCounts[binIndex] += 1
            
            for c in self.visCraterList:
                if c[2] <= size:
                    self.vCCounts[binIndex] += 1
            
            size += binStep
            binIndex += 1

        radii = []
        for c in self.craterList:
            radii.append(c[2])

        vRadii = []
        for c in self.visCraterList:
            vRadii.append(c[2])
        
        self.histCounts = np.histogram(radii, bins=self.bins)[0]
        self.vHistCounts = np.histogram(vRadii, bins=self.bins)[0]

    def createPlots(self):
        self.fig, self.ax = plt.subplots(2, 2)
        self.fig.tight_layout(pad=3.0)
        self.fileNames = []

    def drawVisuals(self, frameCount):
        self.ax[0, 0].set_title("Cratered Terrain")
        self.ax[0, 0].set_xlabel("X (km)")
        self.ax[0, 0].set_ylabel("Y (km)")
        self.ax[0, 0].imshow(self.data, interpolation='nearest')

        self.ax[0, 1].cla()
        self.ax[0, 1].set_title("Cumulative Crater Counts")
        self.ax[0, 1].set_xlabel("Crater Radii (km)")
        self.ax[0, 1].set_ylabel("Cumulative Crater Count")
        self.ax[0, 1].set_xscale('log')
        self.ax[0, 1].invert_xaxis()
        self.ax[0, 1].plot(self.bins[1:], self.cCounts[1:], label="All Craters")
        self.ax[0, 1].plot(self.bins[1:], self.vCCounts[1:], label="Visible Craters")
        self.ax[0, 1].legend(shadow=True, fancybox=True)

        self.ax[1, 0].cla()
        self.ax[1, 0].set_title("Crater Count as a Function of Time")
        self.ax[1, 0].set_xlabel("Time (10^3 years)")
        self.ax[1, 0].set_ylabel("Crater Count")
        self.ax[1, 0].plot(self.timeSteps, self.timeCounts, label="All Craters")
        self.ax[1, 0].plot(self.timeSteps, self.visCounts, label="Visible Craters")
        self.ax[1, 0].legend(shadow=True, fancybox=True)

        self.ax[1, 1].cla()
        self.ax[1, 1].set_title("Crater Size Distribution")
        self.ax[1, 1].set_xlabel("Crater Radii (km)")
        self.ax[1, 1].set_ylabel("Crater Count")
        self.ax[1, 1].hist(self.bins[:-1], self.bins, weights=self.histCounts, label="All Craters")
        self.ax[1, 1].hist(self.bins[:-1], self.bins, weights=self.vHistCounts, label="Visible Craters")
        self.ax[1, 1].legend(shadow=True, fancybox=True)

        fileName = 'images/' + str(frameCount) + '.png'
        self.fileNames.append(fileName)
        plt.savefig(fileName)

sim = CraterSim(terrainLength=500, minCraterRadius=5, maxCraterRadius=50, surfaceValue=185, craterValue=50)
sim.generateCraters(200)

images = []
for f in sim.fileNames:
    images.append(iio.imread(f))
iio.imwrite('animation.mp4', images, fps=15)