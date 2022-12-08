********
`Impact Crater Saturation Simulation`_
********

A simplified cratering simulation to model surface saturation written in Python.

Background
==========

Crater saturation is a phenomenon that occurs on planetary surfaces when the rate at which new craters form is roughly equal to the rate at which old craters are destroyed or erased. This can be identified when the number of craters on a surface remains constant over time, indicating that the surface has reached a state of equilibrium. Once a surface has reached saturation, observations of the rate at which new craters are forming can be used to estimate the time since saturation, providing a relative age for the surface.

Model Assumptions
=================

Consider a 500 km x 500 km planetary surface under the following assumptions:

* The rate of impacts is 1 every 1000 years.
* The minimum measurable crater size has a diameter of 10 km.
* A old crater is considered no longer visable when:
  * The new crater has a larger radius than the old crater.
  * The distance between the center of both craters is less than 30% of the the radius of the new crater.
* Effects such as erosion and secondary craters are ignored.
* All craters are simple craters.
* Crater radii are random under this distribution (weights smaller craters):
  
  `math.exp(random.uniform(math.log(self.minCraterRadius), math.log(self.maxCraterRadius)))`

Notes on Graphics
=================

There are six figures that display data about each time-step of the simulation.

From right to left, top to bottom:

**Cratered Terrain:**

    Displays a visualization of the surface. The circles are crater rims. Red circles are craters that have hidden others.

**Cumulative Crater Counts:**

    Displays a radii binned graph of cumulative crater counts. One line displays all craters. One line displays Visible craters.
    
**Saturation Predictors:**

    Graphs average slopes at intervals of visible craters line (next plot)
    
**Crater Count as a Function of Time:**

    Graphs all craters as a function of time and visiable craters as a function of time.
    
**Crater Size Distribution:**

    Histogram of crater radii and the current counts (visible and all)
    
**Predicted Saturation Percent:**

    The perdicted saturation percent as a function of time.
    
**Example Graphic:**

Analysis
========

**Run 1**

Conditions

**Run 2**

Conditions

Further Development
===================

A logical next step would be to rework the crater removal mechanics. Rather than computing (a rather abitrary) collision value, it would be significantly better to determine visible craters by measuring how many craters are detictable in the image of the surface. Methods of doing this could range from circle detection algorithms to a simple machine-learning image processing implementation. 

Additionally if the images of the surface are relativly comparable to real surfaces: real images of planetary surfaces could be fed in to this to count craters. Since real surfaces do not have cratering rates that are anywhere near the timescales run on the simulation it would be more intersting data-wise to try and estimate the ages of these surfaces (which would likely need more information besides crater numbers).

The collision detection that currently detects if craters are hidden likely could be improved via a quadtree datastructure. Another optimization would be changing how (especially filled) craters are drawn. When outlineMode is disabled drawing craters can cause significant computation time.

Usage
=====

Relevant code for running variatons of the simulation:

.. code:: python
    
    sim = CraterSim(terrainLength=500, minCraterRadius=100, maxCraterRadius=300, 
                    surfaceValue=185, craterValue=50, occlusionValue=0.5, fps=30)
    sim.generateCraters(steps=100, binning=4, outlineMode=True)
    
    
The above code uses the following parameters to initialize the simulation:


+------------------+-------------------------------------+
| Parameter        | Purpose                             |
+------------------+-------------------------------------+
| terrainLength    | Size of terrain square length (km). |
+------------------+-------------------------------------+
| minCraterRadius  | Minimum crater radius (km).         |
+------------------+-------------------------------------+
| maxCraterRadius  | Maximum crater radius (km).         |
+------------------+-------------------------------------+
| surfaceValue     | 0-255 color value for surface.      |
+------------------+-------------------------------------+
| craterValue      | 0-255 color value for craters.      |
+------------------+-------------------------------------+
| occlusionValue   | If the distance between a larger    |
|                  | new crater and a smaller old        |
|                  | crater is less than the new craters |
|                  | radius * this value: the old crater |
|                  | will be hidden.                     |
+------------------+-------------------------------------+
| fps              | Framerate of animation.             |
+------------------+-------------------------------------+
| steps            | Numer of 1000 years to simmulate.   |
|                  | This will also be the total number  |
|                  | of craters generated.               |
+------------------+-------------------------------------+
| binning          | Bin size for histogram.             |
+------------------+-------------------------------------+
| outlineMode      | When enabled draws filled in        |
|                  | craters. This is slower.            |
+------------------+-------------------------------------+



