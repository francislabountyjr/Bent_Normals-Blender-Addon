# Bent Normals

## About
 Bent Normals is a Blender 3D addon that adds self shadowing to normal maps. The algorithm is based off of this post I found https://www.gamedev.net/forums/topic/557465-self-shadowing-normal-maps/ I rewrote the algorithm to run on CUDA gpus in order to drastically speed up the process. I then wrote a pybind11 wrapper for the code so I could create a module for Blender to call the code from python.

## Features
 - Node group is defined programmatically
 - Adjustable mask strength
 - CUDA module for quick calculations

## Setup
 1. Compile or grab a precompiled release of the CPU or CUDA version of the bent normals .pyd module.
  - CUDA: https://github.com/francislabountyjr/BentNormalsCUDAModule
  - CPU: https://github.com/francislabountyjr/BentNormalsCPUModule

 2. Download the latest release of the addon from the releases page/section.

 3. Install in blender by going to preferences > addons and then select the .zip file.

 4. In the Bent Normals addon settings panel, select the location of the directory where the .pyd module is located.

*Usage is described in the pdf documentation
**Questions/suggestions/bugs - labounty3d@gmail.com
