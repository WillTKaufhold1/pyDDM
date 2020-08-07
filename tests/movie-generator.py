#!/home/wtk23/anaconda3/bin/python

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

#create a big field, with movement based on periodic boundary conditions
#movement from the Langevin equation
#then just focus in on a small square
#to give the illusion of a grand cannonical ensemble. 

class Particle:
    def __init__(self,X,D,dt):
        self.X = np.random.rand(2)*X #random float between 0 and X.
        self.D = D
        self.history = []
        self.dt = dt

    def move(self):
        #undergo Weiner noise, based on diffusion coefficient D, with timestep dt.
        #just in 2d, and not sure this is correct.
        #there may well be a factor missing!
        dx = np.sqrt(self.D)*np.sqrt(self.dt) * np.random.randn(2)
        self.X += dx 

    def get_trajectory(N):
        for i in range(N):
            self.history.append(self.X)
            self.move()

class Universe:
    def __init__(self,X,N_particles,D,dt):
        self.particles = [Particle(X,D,dt) for _ in range(N_particles)]
    def get_trajectory(N):
        for p in self.particles:
            p.get_trajectory(N) 
    def make_image():
        fok
        

N_particles = []














