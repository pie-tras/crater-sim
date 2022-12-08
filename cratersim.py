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

    # Initilizes a large number of CraterSim specific variables
    def __init__(self, terrainLength, minCraterRadius, maxCraterRadius, surfaceValue, craterValue, occlusionValue, fps=15):
        self.terrainLength = terrainLength
        self.minCraterRadius = minCraterRadius
        self.maxCraterRadius = maxCraterRadius
        self.surfaceValue = surfaceValue
        self.craterValue = craterValue
        self.occlusionValue = occlusionValue
        self.fps = fps

        # Create surface image data with a uniform surface color
        self.data = np.full((terrainLength, terrainLength, 3), [surfaceValue, surfaceValue, surfaceValue], dtype=np.uint8)

    # The main interface to CraterSim: starts simulation
    def generateCraters(self, steps, binning, outlineMode):
        
        # Initilize final items, prep image directory, prep graphics
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
        
        # Run simulation. One step is 1000 yr / 1 impact
        for i in range(steps):
            # Generate a new crater
            xPos = random.uniform(0.0, self.terrainLength)
            yPos = random.uniform(0.0, self.terrainLength)
            radius = math.exp(random.uniform(math.log(self.minCraterRadius), math.log(self.maxCraterRadius)))
            nextCrater =[xPos, yPos, radius]

            # Check if / how many craters it will hide
            hidesOthers = False
            queueRemove = []
            for c in self.visCraterList:
                if not self.__isBVisible(nextCrater, c):
                    hidesOthers = True
                    queueRemove.append(c) # Add the hidden craters to a queue

            # Function of crater removal over time (this is currently unused in the graphics)
            self.removeCount.append(len(queueRemove))

            # Revome any hidden craters from the visible list
            for c in queueRemove:
                self.visCraterList.remove(c)
                
            self.craterList.append(nextCrater) # All crater data
            self.visCraterList.append(nextCrater) # Visible crater data

            # Draw the new crater. If it hides others it will be red.
            sim.__crater(xPos, yPos, radius, hidesOthers, outlineMode)

            self.timeSteps.append(i) # X time axis data
            self.timeCounts.append(i + 1) # Total crater count
            self.visCounts.append(len(self.visCraterList)) # Visible crater count

            # Slopes of visible crater (func of time) line
            slope50 = self.__calcVisSlope(0.5) # For example this is the slope from 50% of the data to the newest data.
            slope75 = self.__calcVisSlope(0.75)
            slope90 = self.__calcVisSlope(0.90)
            slope100 = self.__calcVisSlope(1)
            slopeAvg = (slope50 + slope75 + slope90 + slope100) / 4 # Average of all these slopes: used for saturation detection

            # Keeps track of these slope values so they can be graphed over time
            self.slopes50.append(self.__calcVisSlope(0.5))
            self.slopes75.append(self.__calcVisSlope(0.75))
            self.slopes90.append(self.__calcVisSlope(0.9))
            self.slopes100.append(self.__calcVisSlope(1))
            self.slopesAvg.append(slopeAvg)

            # Used for visualizing the progress to saturation. (Must be between 0 and 1 as it is a percent value)
            satClamp = 1 - slopeAvg
            if satClamp > 1:
                satClamp = 1
            if satClamp < 0:
                satClamp = 0

            self.saturation.append(satClamp) # The saturation list keeps track of this value over time

            # Based on testing in dev a value of ~80% satClamp generally displays saturation behavior.
            # Data below 10 cycles has artificially large satClamp values (we must ignore this)
            # The saturation time is picked once. If it is never picked saturationPoint stays as -1
            if i > 10 and satClamp > 0.8 and self.saturationPoint == -1:
                self.saturationPoint = i

            self.__binCraters(binning) # Calculations for histogram
            self.__drawVisuals(i) # Draws the plots for this cycle

        # Tell us if a saturation time was picked and what it is.
        if self.saturationPoint == -1:
            print('No saturation detected.')
        else:    
            print('Saturation point predicted at time = ' + str(self.saturationPoint) + ' * 10^3 years.')

        self.__selectKeyImages() # Selects images at intervals to saturation point or over entire period
        self.__compileAnimation() # Creates animation from all images

    # Calculates the slope of the visible crater line at a percentage inverval of the data
    def __calcVisSlope(self, chunkPercent):
        visCount = len(self.visCounts)
        interval = int(visCount * chunkPercent) - 1
        if interval <= 0:
            return 0
        v0 = self.visCounts[visCount - 1]
        v1 = self.visCounts[visCount - 1 - interval]
        return (v0 - v1) / interval

    # Determines if crater A (new) hides crater B (old)
    def __isBVisible(self, A, B):
        if A[2] > B[2]: # Only larger new craters are checked
            dis = math.sqrt((B[0] - A[0])**2 + (B[1] - A[1])**2)
            return dis > self.occlusionValue * A[2]
        return True

    # Draws a "crater" on image data (really it just draws a circle)
    # In outline mode it will also fill in the circle (this can be horrendiously slow however)
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
                    if hidesOthers: # if the crater hides others it is red
                        rc = 255
                    if not outlineMode:
                        if r > radius - 4:
                            v = 0
                            rc = 0
                    self.data[xPoint, yPoint] = [rc, v, v] # Here the color is set
            t += step

    # Compute lists needed for histogram / cumulative graph
    def __binCraters(self, binStep):
        self.bins = []
        self.cCounts = []
        self.vCCounts = []

        # Cumulative list generation
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
        
        # Histogram data generation
        self.histCounts = np.histogram(radii, bins=self.bins)[0]
        self.vHistCounts = np.histogram(vRadii, bins=self.bins)[0]

    # Init plot figures
    def __createPlots(self):
        self.fig, self.ax = plt.subplots(2, 3)
        self.fig.tight_layout(pad=3.0)
        self.fig.set_figheight(10.08)
        self.fig.set_figwidth(15.20)
        
        self.fileNames = [] # keeps track of all the images generated

    # Draw all graphs
    def __drawVisuals(self, frameCount):
        self.ax[0, 0].set_title("Cratered Terrain")
        self.ax[0, 0].set_xlabel("X (km)")
        self.ax[0, 0].set_ylabel("Y (km)")
        self.ax[0, 0].imshow(self.data, interpolation='nearest')

        self.ax[0, 1].cla() # Clears graph
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
        self.fileNames.append(fileName) # Append new image name
        plt.savefig(fileName) # Create image

    # Prep image directory for a new run
    def __clearImages(self):
        imageDir = 'images/'
        if os.path.exists(imageDir):
            images = [f for f in listdir(imageDir) if isfile(join(imageDir, f))]
            for i in images:
                os.remove(imageDir + i)
        else:
            os.mkdir(imageDir)

    # Selects images at invervals based on saturationPoint or entire period (no saturationPoint case)
    def __selectKeyImages(self):
        length = self.saturationPoint

        if self.saturationPoint == -1:
            length = len(self.fileNames) - 1

        intv25 = int(0.25 * length) # 25%, 50%, 75% and 100% of interval
        intv50 = int(0.50 * length)
        intv75 = int(0.75 * length)
        intv100 = int(length)
        shutil.copy2(self.fileNames[intv25], 'saturation25.png') # copy these outside of image directory and label
        shutil.copy2(self.fileNames[intv50], 'saturation50.png')
        shutil.copy2(self.fileNames[intv75], 'saturation75.png')
        shutil.copy2(self.fileNames[intv100], 'saturation100.png')

    # Takes all images and creates mp4 at specified fps
    def __compileAnimation(self):
        images = []
        for f in self.fileNames:
            images.append(iio.imread(f))
        iio.imwrite('animation.mp4', images, fps=self.fps)

# User config
sim = CraterSim(terrainLength=500, minCraterRadius=5, maxCraterRadius=50, surfaceValue=185, craterValue=50, occlusionValue=0.6, fps=30)
sim.generateCraters(steps=2500, binning=4, outlineMode=True)