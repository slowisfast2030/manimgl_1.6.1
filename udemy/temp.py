import pyglet

# Create a window
window = pyglet.window.Window()

# Create a label to display text
label = pyglet.text.Label('Hello, World', font_name='Times New Roman', font_size=36, x=window.width//2, y=window.height//2, anchor_x='center', anchor_y='center')

# Override the on_draw method of the window to display the label
@window.event
def on_draw():
    window.clear()
    label.draw()

# Run the Pyglet application
pyglet.app.run()