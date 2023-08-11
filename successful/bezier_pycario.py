import cairo

# Set up Pycairo
surface = cairo.ImageSurface(cairo.FORMAT_RGB24, 400, 250)
ctx = cairo.Context(surface)

# Paint the background
ctx.set_source_rgb(0, 0, 0)
ctx.paint()

# Draw the image
ctx.move_to(50, 200)
ctx.curve_to(150, 75, 225, 50, 350, 150)
ctx.set_source_rgb(1, 0, 0)
ctx.set_line_width(1)
ctx.stroke()

# Save the result
surface.write_to_png('bezier_pycario.png')

print("all is well")
