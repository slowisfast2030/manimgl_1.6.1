# Import the numpy and matplotlib modules
import numpy as np
import matplotlib.pyplot as plt

# Define the parameters of the Möbius strip
resolution = 100 # The number of points along the strip
major_radius = 3 # The distance from the center of the strip to the middle of the edge
minor_radius = 0.5 # The width of the strip
angle = np.pi / 2 # The angle of the half-twist in radians

# Create the parametric equations of the Möbius strip
u = np.linspace(0, 2 * np.pi, resolution) # The angle along the edge
v = np.linspace(-minor_radius, minor_radius, resolution) # The distance from the edge
u, v = np.meshgrid(u, v)

# Calculate the x, y, and z coordinates of each point
x = (major_radius + v * np.cos(angle / 2) * np.sign(u)) * np.cos(u)
y = (major_radius + v * np.cos(angle / 2) * np.sign(u)) * np.sin(u)
z = v/2 * np.sin(u / 2)

# Create a figure and a 3D axis
fig = plt.figure()
ax = fig.add_subplot(projection='3d')

# Plot the surface
ax.plot_surface(x, y, z, color='blue', alpha=0.8)

# Show the plot
plt.show()
