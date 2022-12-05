import os

import numpy as np
import trimesh
from PyQt5.QtWidgets import QApplication, QLabel, QSlider, QHBoxLayout, QWidget
from PyQt5.QtCore import Qt
from PyIGL_viewer import Viewer


script_folder = os.path.dirname(__file__)
path_to_obj_file = r"D:\work\wrist40-right-watertight.obj"
# Path to your OBJ file stored in path_to_obj_file
mesh = trimesh.load(path_to_obj_file)
vertices, faces = mesh.vertices, mesh.faces

bbox_min = np.min(vertices, axis=0)
bbox_max = np.max(vertices, axis=0)
scaling_factor = 1.0 / np.max(bbox_max - bbox_min)
center = np.mean(vertices, axis=0)
vertices -= center
vertices *= scaling_factor


# Create Qt application and our viewer window
viewer_app = QApplication(["IGL viewer"])
viewer = Viewer()
viewer.show()
viewer.set_column_stretch(0, 1)

# Add a viewer widget to visualize 3D meshes to our viewer window
viewer_widget, _ = viewer.add_viewer_widget(0, 0)
viewer_widget.show()
viewer_widget.link_light_to_camera()

# Arrange layouts.
menu = viewer.current_menu_layout
view_distance_label = QLabel(viewer)
view_distance_label.setText("Maximum indexing distance")


hbox = QHBoxLayout()
view_distance_slider_label = QLabel(viewer)
view_distance_slider_label.setText(f"{0:.02f}")


def view_distance_slider_update(value):
    if value <= 80:
        value = 0
    view_distance_slider_label.setText(f"{value / 100:.02f}")
    viewer_widget.set_draw_indices_distance(value / 100)
    viewer_widget.update()


view_distance_slider = QSlider(Qt.Horizontal, viewer)
view_distance_slider.setRange(80, 100)
view_distance_slider.setPageStep(1)
view_distance_slider.setSliderPosition(0)
view_distance_slider.sliderMoved.connect(view_distance_slider_update)
hbox.addWidget(view_distance_slider)
hbox.addSpacing(15)
hbox.addWidget(view_distance_slider_label)
hbox_widget = QWidget()
hbox_widget.setLayout(hbox)


menu.addWidget(view_distance_label)
menu.addWidget(hbox_widget)


# Add a mesh to our viewer widget
# This requires three steps:
# - Adding the mesh vertices and faces
# - Adding a mesh prefab that contains shader attributes and uniform values
# - Adding an instance of our prefab whose position is defined by a model matrix

# Here, we use the lambert shader.
# This shader requires two things:
# - A uniform value called 'albedo' for the color of the mesh.
# - An attribute called 'normal' for the mesh normals.
uniforms = {}
vertex_attributes = {}
face_attributes = {}

uniforms["albedo"] = np.array([0.8, 0.8, 0.8])

# If we want flat shading with normals defined per face.
# face_normals = igl.per_face_normals(vertices, faces, np.array([1.0, 1.0, 1.0])).astype(
#     np.float32
# )
face_normals = mesh.face_normals.astype(np.float32)
face_attributes["normal"] = face_normals

# If we want smooth shading with normals defined per vertex.
# vertex_normals = igl.per_vertex_normals(vertices, faces, igl.PER_VERTEX_NORMALS_WEIGHTING_TYPE_AREA).astype(np.float32)
# vertex_attributes['normal'] = vertex_normals

mesh_index = viewer_widget.add_mesh(vertices, faces)
mesh_prefab_index = viewer_widget.add_mesh_prefab(
    mesh_index,
    "lambert",
    vertex_attributes=vertex_attributes,
    face_attributes=face_attributes,
    uniforms=uniforms,
)
instance_index = viewer_widget.add_mesh_instance(
    mesh_prefab_index, np.eye(4, dtype="f")
)

# Add the wireframe for our mesh
viewer_widget.add_wireframe(instance_index, line_color=np.array([0.1, 0.1, 0.1]))

# Launch the Qt application
viewer_app.exec()
