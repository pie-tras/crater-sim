********
`Impact Crater Saturation Simulation`_
********

A simplified cratering simulation to model surface saturation written in Python.

## Background ##

Crater saturation is a phenomenon that occurs on planetary surfaces when the rate at which new craters form is roughly equal to the rate at which old craters are destroyed or erased. This can be identified when the number of craters on a surface remains constant over time, indicating that the surface has reached a state of equilibrium. Once a surface has reached saturation, observations of the rate at which new craters are forming can be used to estimate the time since saturation, providing a relative age for the surface.

## Model Assumptions ##

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

## Analysis ##

## Further Development ##

## Usage ##

Relevant code for running variatons of the simulation:

.. code:: python
    
    sim = CraterSim(terrainLength=500, minCraterRadius=100, maxCraterRadius=300, surfaceValue=185, craterValue=50, occlusionValue=0.5, fps=30)`
    sim.generateCraters(steps=100, binning=4, outlineMode=True)

`terrainLength`: Size of terrain square length (km)

