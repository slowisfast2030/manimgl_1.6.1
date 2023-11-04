import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Step 1: Define the parameters for the Möbius strip
theta = np.linspace(0, 2 * np.pi, 100)  # Define the range of angles
w = np.linspace(-1, 1, 50)              # Width of the strip
theta, w = np.meshgrid(theta, w)        # Create a 2D grid of points

# Step 2: Define the parametric equations of the Möbius strip
# We use half-angle for theta/2 to get one full twist
r = 1 + w/2 * np.cos(theta/2)
x = r * np.cos(theta)
y = r * np.sin(theta)
z = w/2 * np.sin(theta/2)

# Step 3: Plot the Möbius strip
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

# Create a surface plot using the x, y, z coordinates
ax.plot_surface(x, y, z, rstride=1, cstride=1, color='c', edgecolor='none', alpha=0.75)

# Set plot display parameters for better visualization
ax.set_xlim([-1.5, 1.5])
ax.set_ylim([-1.5, 1.5])
ax.set_zlim([-1.5, 1.5])
ax.set_xlabel('X axis')
ax.set_ylabel('Y axis')
ax.set_zlabel('Z axis')

# Display the plot
plt.show()
