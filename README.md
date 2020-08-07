# Python DDM

## Introduction

Implementation of Dynamic Differential Microscopy (DDM) in Python. 

## Features

1. Fourier transform GPU acceleration
2. Clever memory management
3. Fitting arbitrary models of particles, including multiple particles and polydispersity
4. Automated structure function fitting

## Requirements

1. Python 3.6
2. Numpy, ...
3. CUDA capable GPU

## Description of the algorithm

Fitting of a model using DDM requires as an input a map of $\tau$, a frame lag time, to a function mapping between $q$, wavevector length, to the mean Fourier power intensity at $q$ taken of images separted by $\tau$ frames.

We take a stack of 2d square images with one channel (i.e. grayscale images), such that the total number is N. For each value of $\tau$ in the range 1, floor(N/2), we take the pointwise mean of the 2D Fourier transforms of frames separated by $\tau$ frames. Here by the ensemble of 2D Fourier transforms over which the mean is carried out between frame index $A$, and index $A + \tau$, and averaged out over all possible $A$.  

Subsequently each averaged 2D Fourier transform image is radially averaged, collapsing the 2 dimensional Fourier image into a one dimensional function. The image ought to be isotropic, but is not due to finite sampling length and stochastic noise. It may also be non-isotropic because the transport properties of the sample are non-isotropic: i.e. if there's a leak in the sample chamber, liquid may leak north to south, so that $\vec{q}$ vectors which point north or south will demonstrate ballistic relaxation, while those which point east or west will demonstrate Brownian relaxation. We store the standard error over the Fourier intensities between positions in the Fourier image with the same q, (but rotated $\vec{q}$) as a measure of uncertainty in the power spectrum. This later ensures that fitting of a model is more robust. 

The one dimensional map (the raw image structure function), its uncertainty, and the movie framerate is stored in a dictionary and serialized, while the original image stack and related data is discarded. Such a proceedure is necessary as typically each framestack will be several gigabytes in size, and there may be thousands of framestacks to process. Decoupling image structure acquisition and model fitting is therefore essential. For a one thousand frame stack, with each frame being of width 1024 pixels, acquisition of the image structure function takes around a minute using GPU accelerated Fourier transforms.

The serialized data is then read back into Python. In general, transport properties are calculated by fitting a theoretically motivated model to the image structure function. Typical models are given here

1. A set of monodisperse particles undergoing Brownian motion: $I(q) = A(q) (1-e^{-t D/\tau^2}) + B(q)$.
2. A set of monodisperse particles undergoing Ballistic motion: $I(q) = A(q) (1-e^{-t v / \tau}) + B(q)$.
3. A more general model where particles are (all) undergoing some process on the continuum between anomylous subdiffusion and superdiffusive motion: $I(q) = A(q) (1-e^{-t D' / \tau^\alpha}) + B(q)$. Here $\alpha$ varies between $1$ (indicating superdiffusive motion), to $2$ (diffusion), to values above two (indicating anomylous subdiffusion).
4. A mixture of monodisperse particles undergoing different kinds of transport:  $I(q) = B(q) + \sum_i A_i(q) (1-e^{1-t D / \tau_i^{\alpha_i}})$.
5. A polydisperse population of particles, 

The statistically optimal method of fitting 




















