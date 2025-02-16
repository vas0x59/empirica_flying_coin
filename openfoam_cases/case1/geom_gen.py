import gmsh
import math

gmsh.initialize()
gmsh.model.add("Tilted_Coin_3D")

# ------------------------
# 1. Parameters
# ------------------------
coin_radius   = 0.01     # Radius of the "coin"
coin_thickness= 0.002    # Thickness of the "coin"
tilt_angle_deg= 45.0    # Tilt angle (degrees)
tilt_angle_rad= tilt_angle_deg * math.pi / 180.0

# Domain dimensions (flow box)
# For example, a rectangular box of size (Lx x Ly x Lz)
Lx = 0.3
Ly = 0.3
Lz = 0.3

# Mesh size parameters
mesh_size_domain = 0.006
mesh_size_coin   = 0.001

# ------------------------
# 2. Create the coin (cylinder)
# ------------------------
#
# We place a cylinder along the z-axis from z=-coin_thickness/2 
# to z=+coin_thickness/2, then rotate it, and finally translate 
# it so that its lowest point just touches z=0.

# Create cylinder (center at z=0):
# addCylinder(x, y, z, dx, dy, dz, radius)
coin_tag = gmsh.model.occ.addCylinder(
    0, 0, 0,   # start center
    0, 0,  coin_thickness,     # extends in z direction by "coin_thickness"
    coin_radius
)
print(coin_tag)

# Rotate the coin around the X-axis by `tilt_angle_rad` about origin (0,0,0):
gmsh.model.occ.rotate(
    [(3, coin_tag)],           # (3, tag) => volume
    0, 0, 0,                   # center of rotation
    1, 0, 0,                   # axis of rotation (x-axis)
    tilt_angle_rad
)

# After rotation, shift the coin upwards so that its lowest z is at 0
xmin, xmax, ymin, ymax, zmin, zmax = gmsh.model.occ.getBoundingBox(3, coin_tag)
# if zmin < 0:
gmsh.model.occ.translate([(3, coin_tag)], 0, 0, zmin)  # move coin so zmin = 0
gmsh.model.occ.synchronize()

surfaces_coin = gmsh.model.getBoundary([(3, coin_tag)], oriented=False)
surface_tags_coin = set(s[1] for s in surfaces_coin)
# print("Volumes before cut:", gmsh.model.getEntities(3))
# coin_surfs = gmsh.model.getBoundary([(3, coin_tag)], oriented=False)
# coin_surf_tags = list(set([s[1] for s in coin_surfs]))

# ------------------------
# 3. Create the flow domain (a rectangular box)
# ------------------------
#
# For example, from x=-Lx/2..+Lx/2, y=-Ly/2..+Ly/2, z=0..+Lz.

box_x0 = -Lx/2
box_y0 = -Ly/2
box_z0 = 0
box_tag = gmsh.model.occ.addBox(box_x0, box_y0, box_z0, Lx, Ly, Lz)
gmsh.model.occ.synchronize()

# ------------------------
# 4. Boolean difference: subtract coin from the box
# ------------------------
#
# This will produce the flow volume around the coin.
surfaces_box = gmsh.model.getBoundary([(3, box_tag)], oriented=False)
surface_tags_box = set(s[1] for s in surfaces_box)


cut_objects  = [(3, box_tag)]
tool_objects = [(3, coin_tag)]
out_dimtags, _ =gmsh.model.occ.cut(cut_objects, tool_objects)


# flow_domain_tag = out[0][0][1]  # The new volume tag of the subtracted domain
# print("out", out)
# The coin itself remains as a separate volume (unless you remove it),
# but for external flow, you typically only need the "fluid" volume.

# ------------------------
# 5. Synchronize the CAD kernel with the Gmsh model
# ------------------------
gmsh.model.occ.synchronize()

surfaces_cut = gmsh.model.getBoundary(out_dimtags, oriented=False)
surface_tags_cut = set(s[1] for s in surfaces_cut)

# ------------------------
# 6. Define physical groups
# ------------------------
#
# So that boundary conditions can be applied easily.
# Let's make:
#   - The volume of the fluid domain a Physical Group
#   - The box walls / patch surfaces as separate Physical Groups
#   - The coin's surface as a Physical Group (if you need to apply BC there).

# 6a. Fluid domain
gmsh.model.addPhysicalGroup(3, [out_dimtags[0][1]], 1)
gmsh.model.setPhysicalName(3, 1, "Fluid_Domain")


# surfaces = gmsh.model.getBoundary(out[0], oriented=False)
# surface_tags = [s[1] for s in surfaces]
print("Surface Tags of the cut object:", surface_tags_cut)
coin = {2, 10, 9}

# surfaces_remaining_from_box1 = surface_tags_cut & surface_tags_box  # Surfaces that were in box1
# surfaces_newly_created_by_cut = surface_tags_cut - surface_tags_box  # New surfaces from the cut

# print("Surfaces remaining from box1:", surfaces_remaining_from_box1)
# print("Surfaces newly created by the cut:", surfaces_newly_created_by_cut)


# 6b. Identify boundary surfaces of the flow domain
#    We can loop over the surfaces that belong to 'flow_domain_tag'
# flow_domain_surfs = gmsh.model.getBoundary(
#     [(3, flow_domain_tag)], oriented=False
# )
# flow_domain_surf_tags = list(set([s[1] for s in flow_domain_surfs]))
inlet = {4}
plate = {7}
flow_domain_surf_tags = list(surface_tags_cut - coin - inlet - plate)
# Optionally, define each face (inlet, outlet, walls) by bounding box checks
# or by manual selection. For simplicity, group them all as "Walls".
gmsh.model.addPhysicalGroup(2, flow_domain_surf_tags, 2)
gmsh.model.setPhysicalName(2, 2, "outlet")

# 6c. Coin surface
#    The coin volume still exists in the CAD model, but if you want its surface:

gmsh.model.addPhysicalGroup(2, list(coin), 3)
gmsh.model.setPhysicalName(2, 3, "coin")

gmsh.model.addPhysicalGroup(2, list(inlet), 4)
gmsh.model.setPhysicalName(2, 4, "inlet")


gmsh.model.addPhysicalGroup(2, list(plate), 5)
gmsh.model.setPhysicalName(2, 5, "plate")

# ------------------------
# 7. Mesh settings and generation
# ------------------------
#
# You can assign characteristic lengths on certain entities if desired.
# For example, the flow domain surfaces or volume:
# for s in flow_domain_surf_tags:

#     # for e in :
#     gmsh.model.mesh.setSize([(2, s)], mesh_size_domain)

# # And a finer mesh on the coin surface:
# for s in coin:
#     # gmsh.model.mesh.setSize([(2, s)], mesh_size_coin)
#     gmsh.model.mesh.setSize([(2, s)], mesh_size_coin)
gmsh.model.occ.mesh.setSize(gmsh.model.occ.getEntities(0), 0.1)
gmsh.model.occ.synchronize()
gmsh.model.mesh.generate(2)

# ------------------------
# 8. Save and (optional) launch GUI
# ------------------------
# gmsh.write("tilted_coin_3d.msh")
gmsh.option.setNumber('Mesh.StlOneSolidPerSurface', 2)
# gmsh.option.setNumber("Mesh.SaveAll", 1)  # Save all physical groups
gmsh.write("constant/triSurface/output.stl")
# Uncomment to see in Gmsh's GUI
# gmsh.fltk.run()

gmsh.finalize()
