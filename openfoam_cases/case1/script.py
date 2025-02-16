from paraview.simple import *
LoadPalette("WhiteBackground")
# Load OpenFOAM case (replace with actual file)
foam_reader = OpenFOAMReader(FileName="case.foam")
foam_reader.CaseType = "Reconstructed Case"  # Adjust to "Decomposed Case" if necessary

# Apply Slice Filter
slice_filter = Slice(Input=foam_reader)
slice_filter.SliceType = 'Plane'
slice_filter.SliceOffsetValues = [0.001]  # Adjust slicing position

# Define slice orientation (XZ-plane: Normal along Y)
slice_filter.SliceType.Normal = [0, 1, 0]  # Normal along Y-axis to get X-Z plane

# Show pressure field on slice
pressure_display = Show(slice_filter)
pressure_display.Representation = "Surface"
pressure_display.ColorArrayName = ["POINTS", "p"]  # "p" = pressure field
pressure_display.LookupTable = GetColorTransferFunction("p")
pressure_display.LookupTable.ApplyPreset("Turbo", True)
pressure_display.LookupTable.RescaleTransferFunction(-10, 10)
# Create a Line Source for StreamTracer in XZ-plane
line_source = Line()
line_source.Point1 = [-0.022, 0, 0.001]  # Start point in XZ-plane
line_source.Point2 = [-0.022, 0, 0.035]    # End point in XZ-plane
line_source.Resolution = 15  # Number of seed points along the line

# Apply StreamTracer with the line source
stream_tracer = StreamTracer(Input=foam_reader, SeedType="Line")
stream_tracer.Vectors = ["POINTS", "U"]  # "U" = velocity field in OpenFOAM
stream_tracer.MaximumStreamlineLength = 1000  # Adjust based on your domain

# Assign the line source to the StreamTracer
stream_tracer.SeedType.Point1 = line_source.Point1
stream_tracer.SeedType.Point2 = line_source.Point2
stream_tracer.SeedType.Resolution = line_source.Resolution

# Show Streamlines
streamline_display = Show(stream_tracer)
streamline_display.Representation = "Surface"
streamline_display.ColorArrayName = "SolidColor"
# streamline_display.LookupTable = None  # Make it solid black
streamline_display.AmbientColor = [0, 0, 0]  # Black color
streamline_display.DiffuseColor = [0, 0, 0]  # Black color
streamline_display.DisableLighting = 0  # Disable lighting
streamline_display.LineWidth = 5
streamline_display.RenderLinesAsTubes=True

renderView = GetActiveView()

# Enable axes grid
renderView.AxesGrid = 'Grid Axes 3D Actor'
renderView.AxesGrid.Visibility = 1  # Show the grid
renderView.AxesGrid.XLabelFontSize = 21
renderView.AxesGrid.YLabelFontSize = 21
renderView.AxesGrid.ZLabelFontSize = 21
renderView.AxesGrid.XTitleFontSize = 24
renderView.AxesGrid.YTitleFontSize = 24
renderView.AxesGrid.ZTitleFontSize = 24
resolution = [600, 400]
renderView.ViewSize = resolution 

# Set up rendering
# Render()

# Adjust camera for 2D XZ view (flip X-axis)
camera = GetActiveCamera()
camera.SetPosition(0.0, -0.09, 0.01)  # Position the camera above Y-axis to look at XZ-plane
camera.SetFocalPoint(0.0, 0, 0.01)  # Focus on the center
camera.SetViewUp(0, 0, 1)  # Ensure Z is upwards
# camera.Yaw(180)  # Flip the X-axis
camera.OrthogonalizeViewUp()  # Enforce a 2D orthographic projection

# Save the rendered visualization as a PNG
SaveScreenshot("openfoam_xz_view.png", ImageResolution=[resolution[0]*2, resolution[1]*2])
# SaveScreenshot("output.pdf", renderView, ImageResolution=[1920, 1080], TransparentBackground=1)
print("PNG image saved as 'openfoam_xz_view.png'")

# Interact()