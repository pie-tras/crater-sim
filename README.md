# Impact Crater Saturation Simulation

Consider a 500 km x 500 km planetary surface under the following assumptions:

* The rate of impacts is 1 every 1000 years.
* The minimum measurable crater size has a diameter of 10 km.
* A old crater is considered no longer visable when:
  * The new crater has a larger radius than the old crater.
  * The distance between the center of both craters is less than 30% of the the radius of the new crater.
* Effects such as erosion and secondary craters are ignored.
* All craters are simple craters.
* Crater radii are random under this distribution (weights smaller craters): `math.exp(random.uniform(math.log(self.minCraterRadius), math.log(self.maxCraterRadius)))`
