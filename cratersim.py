import os
import math
import random
import numpy as np
import imageio.v3 as iio
import shutil

from os import listdir
from os.path import isfile, join
from matplotlib import pyplot as plt

class CraterSim:

    def __init__(self, terrainLength, minCraterRadius, maxCraterRadius, surfaceValue, craterValue, occlusionValue, fps=15):
        self.terrainLength = terrainLength
        self.minCraterRadius = minCraterRadius
        self.maxCraterRadius = maxCraterRadius
        self.surfaceValue = surfaceValue
        self.craterValue = craterValue
        self.occlusionValue = occlusionValue
        self.fps = fps

        self.data = np.full((terrainLength, terrainLength, 3), [surfaceValue, surfaceValue, surfaceValue], dtype=np.uint8)

    def generateCraters(self, steps, binning, outlineMode):
        self.__clearImages()

        self.craterList = []
        self.visCraterList = []

        self.timeSteps = []
        self.timeCounts = []
        self.visCounts = []

        self.removeCount = []

        self.slopes50 = []
        self.slopes75 = []
        self.slopes90 = []
        self.slopes100 = []
        self.slopesAvg = []

        self.saturation = []
        self.saturationPoint = -1

        self.__binCraters(binning)

        sim.__createPlots()
        
        for i in range(steps):
            xPos = random.uniform(0.0, self.terrainLength)
            yPos = random.uniform(0.0, self.terrainLength)
            radius = math.exp(random.uniform(math.log(self.minCraterRadius), math.log(self.maxCraterRadius)))
            nextCrater =[xPos, yPos, radius]
            hidesOthers = False
            queueRemove = []
            for c in self.visCraterList:
                if not self.__isBVisible(nextCrater, c):
                    hidesOthers = True
                    queueRemove.append(c)

            self.removeCount.append(len(queueRemove))

            for c in queueRemove:
                self.visCraterList.remove(c)
                
            self.craterList.append(nextCrater)
            self.visCraterList.append(nextCrater)
            sim.__crater(xPos, yPos, radius, hidesOthers, outlineMode)

            self.timeSteps.append(i)
            self.timeCounts.append(i + 1)
            self.visCounts.append(len(self.visCraterList))

            slope50 = self.__calcVisSlope(0.5)
            slope75 = self.__calcVisSlope(0.75)
            slope90 = self.__calcVisSlope(0.90)
            slope100 = self.__calcVisSlope(1)
            slopeAvg = (slope50 + slope75 + slope90 + slope100) / 4

            self.slopes50.append(self.__calcVisSlope(0.5))
            self.slopes75.append(self.__calcVisSlope(0.75))
            self.slopes90.append(self.__calcVisSlope(0.9))
            self.slopes100.append(self.__calcVisSlope(1))
            self.slopesAvg.append(slopeAvg)

            satClamp = 1 - slopeAvg
            if satClamp > 1:
                satClamp = 1
            if satClamp < 0:
                satClamp = 0

            self.saturation.append(satClamp)

            if i > 10 and satClamp > 0.8 and self.saturationPoint == -1:
                self.saturationPoint = i

            self.__binCraters(binning)
            self.__drawVisuals(i)

        if self.saturationPoint == -1:
            print('No saturation detected.')
        else:    
            print('Saturation point predicted at time = ' + str(self.saturationPoint) + ' * 10^3 years.')

        self.__selectKeyImages()
        self.__compileAnimation()

    def __calcVisSlope(self, chunkPercent):
        visCount = len(self.visCounts)
        interval = int(visCount * chunkPercent) - 1
        if interval <= 0:
            return 0
        v0 = self.visCounts[visCount - 1]
        v1 = self.visCounts[visCount - 1 - interval]
        return (v0 - v1) / interval

    def __isBVisible(self, A, B):
        if A[2] > B[2]:
            dis = math.sqrt((B[0] - A[0])**2 + (B[1] - A[1])**2)
            return dis > self.occlusionValue * A[2]
        return True

    def __crater(self, x, y, radius, hidesOthers, outlineMode=False):
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

    def __binCraters(self, binStep):
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

    def __createPlots(self):
        self.fig, self.ax = plt.subplots(2, 3)
        self.fig.tight_layout(pad=3.0)
        self.fig.set_figheight(10.08)
        self.fig.set_figwidth(15.20)
        
        self.fileNames = []

    def __drawVisuals(self, frameCount):
        self.ax[0, 0].set_title("Cratered Terrain")
        self.ax[0, 0].set_xlabel("X (km)")
        self.ax[0, 0].set_ylabel("Y (km)")
        self.ax[0, 0].imshow(self.data, interpolation='nearest')

        self.ax[0, 1].cla()
        self.ax[0, 1].set_title("Cumulative Crater Counts")
        self.ax[0, 1].set_xlabel("Crater Radii (km)")
        self.ax[0, 1].set_ylabel("Cumulative Crater Count")
        self.ax[0, 1].set_xscale('log')
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

        self.ax[0, 2].cla()
        self.ax[0, 2].set_title("Saturation Predictiors")
        self.ax[0, 2].set_xlabel("Time (10^3 yr)")
        self.ax[0, 2].set_ylabel("Average Slopes of Visible Crater Counts")
        self.ax[0, 2].plot(self.timeSteps, self.slopes50, label="Last 50%")
        self.ax[0, 2].plot(self.timeSteps, self.slopes75, label="Last 75%")
        self.ax[0, 2].plot(self.timeSteps, self.slopes90, label="Last 90%")
        self.ax[0, 2].plot(self.timeSteps, self.slopes100, label="Last 100%")
        self.ax[0, 2].plot(self.timeSteps, self.slopesAvg, label="Average")
        self.ax[0, 2].legend(shadow=True, fancybox=True)

        self.ax[1, 2].cla()
        self.ax[1, 2].set_title("Predicted Saturation Percent")
        self.ax[1, 2].set_xlabel("Time (10^3 yr)")
        self.ax[1, 2].set_ylabel("Saturation Percent")
        self.ax[1, 2].plot(self.timeSteps, self.saturation)

        fileName = 'images/' + str(frameCount) + '.png'
        self.fileNames.append(fileName)
        plt.savefig(fileName)

    def __clearImages(self):
        imageDir = 'images/'
        if os.path.exists(imageDir):
            images = [f for f in listdir(imageDir) if isfile(join(imageDir, f))]
            for i in images:
                os.remove(imageDir + i)
        else:
            os.mkdir(imageDir)

    def __selectKeyImages(self):
        length = self.saturationPoint

        if self.saturationPoint == -1:
            length = len(self.fileNames) - 1

        intv25 = int(0.25 * length)
        intv50 = int(0.50 * length)
        intv75 = int(0.75 * length)
        intv100 = int(length)
        shutil.copy2(self.fileNames[intv25], 'saturation25.png')
        shutil.copy2(self.fileNames[intv50], 'saturation50.png')
        shutil.copy2(self.fileNames[intv75], 'saturation75.png')
        shutil.copy2(self.fileNames[intv100], 'saturation100.png')

    def __compileAnimation(self):
        images = []
        for f in self.fileNames:
            images.append(iio.imread(f))
        iio.imwrite('animation.mp4', images, fps=self.fps)

sim = CraterSim(terrainLength=500, minCraterRadius=100, maxCraterRadius=300, surfaceValue=185, craterValue=50, occlusionValue=0.5, fps=30)
sim.generateCraters(100, 4, True)