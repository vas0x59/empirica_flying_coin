import gmsh
import math
import sys
import os
import argparse
import argparse

# Create an ArgumentParser object
parser = argparse.ArgumentParser()

# Add named arguments with default values
parser.add_argument("--x", type=float, default=0.0)
parser.add_argument("--y", type=float, default=0.0)
parser.add_argument("--z", type=float, default=float('nan'))
parser.add_argument("--phi", type=float, default=30 * math.pi / 180.0)
parser.add_argument("--R", type=float, default=0.01)
parser.add_argument("--t", type=float, default=0.002)

# Parse the arguments
args = parser.parse_args()

# Print the values
print(f"x: {args.x}, y: {args.y}, z: {args.z}, phi: {args.phi}")
x, y, z = args.x, args.y, args.z
tilt_angle_rad = args.phi
# ------------------------
# 1. Parameters
# ------------------------
coin_radius   = args.R    # Radius of the "coin"
coin_thickness= args.t    # Thickness of the "coin"

if z == float('nan'):
   z = coin_radius*math.sin(abs(tilt_angle_rad))-coin_thickness/4

gmsh.initialize()
gmsh.model.add("Tilted_Coin_3D")


# Domain dimensions (flow box)
# For example, a rectangular box of size (Lx x Ly x Lz)
Lx = 0.3
Ly = 0.3
Lz = 0.3



coin_tag = gmsh.model.occ.addCylinder(
    0, 0, -coin_thickness/2,   # start center
    0, 0,  coin_thickness,     # extends in z direction by "coin_thickness"
    coin_radius
)
print(coin_tag)

# Rotate the coin around the X-axis by `tilt_angle_rad` about origin (0,0,0):
gmsh.model.occ.rotate(
    [(3, coin_tag)],           # (3, tag) => volume
    0, 0, 0,                   # center of rotation
    0, math.copysign(1, tilt_angle_rad), 0,                   # axis of rotation (x-axis)
    abs(tilt_angle_rad)
)

# After rotation, shift the coin upwards so that its lowest z is at 0
xmin, xmax, ymin, ymax, zmin, zmax = gmsh.model.occ.getBoundingBox(3, coin_tag)
# if zmin < 0:
# gmsh.model.occ.translate([(3, coin_tag)], 0, 0, coin_radius*math.sin(tilt_angle_rad)*2-coin_thickness/2)  # move coin so zmin = 0

gmsh.model.occ.translate([(3, coin_tag)], x, y, z)  # move coin so zmin = 0


gmsh.model.occ.synchronize()

gmsh.model.addPhysicalGroup(2, [i for _, i in gmsh.model.occ.getEntities(2)], 5)
gmsh.model.setPhysicalName(2, 5, "coin")


gmsh.model.occ.mesh.setSize(gmsh.model.occ.getEntities(0), 0.001)
gmsh.model.occ.synchronize()
gmsh.model.mesh.generate(2)

# ------------------------
# 8. Save and (optional) launch GUI
# ------------------------
# gmsh.write("tilted_coin_3d.msh")
gmsh.option.setNumber('Mesh.StlOneSolidPerSurface', 2)
# gmsh.option.setNumber("Mesh.SaveAll", 1)  # Save all physical groups
gmsh.write("constant/triSurface/coin.stl")
# Uncomment to see in Gmsh's GUI
# gmsh.fltk.run()

gmsh.finalize()
