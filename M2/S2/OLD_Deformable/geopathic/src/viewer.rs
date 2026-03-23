extern crate kiss3d;
extern crate nalgebra as na;

use kiss3d::camera::ArcBall;
use kiss3d::prelude::Mesh;
use kiss3d::scene::SceneNode;
use kiss3d::window::Window;
use kiss3d::{light::Light, prelude::TextureManager};
use na::{Point2, Vector3};
use nalgebra::{Point3, UnitQuaternion};

use std::cell::RefCell;
use std::rc::Rc;

use image::{DynamicImage, GenericImage};

use crate::manifold::{Manifold, Path, Point};
use crate::sources::Sources;

pub struct Viewer {
    pub window: Window,
    pub nodes: Vec<SceneNode>,
    pub camera: ArcBall,
}

impl Viewer {
    /// Creates a new Viewer instance.
    pub fn new() -> Self {
        let window = Window::new_with_size("Manifold Viewer", 1200, 800);

        // change the default camera position
        let eye = Point3::new(0.0, 3.0, 7.0);
        let at = Point3::new(0.0, 1.0, 0.0);
        let camera = ArcBall::new(eye, at);

        Viewer {
            window,
            nodes: Vec::new(),
            camera,
        }
    }

    pub fn add_manifold(&mut self, manifold: &Manifold, colormap: Option<Vec<[u8; 4]>>) {
        // add the coordinates of the manifold vertices (with respect to the order in the hashmap)
        let mut base_coords: Vec<Point3<f32>> = Vec::with_capacity(manifold.vertices.len());
        for i in 0..manifold.vertices.len() {
            let vertex = &manifold.vertices[i];
            base_coords.push(Point3::new(
                vertex[0] as f32,
                vertex[1] as f32,
                vertex[2] as f32,
            ));
        }

        // add the faces
        let base_faces: Vec<Point3<u16>> = manifold
            .faces
            .iter()
            .map(|f| Point3::new(f.0 as u16, f.1 as u16, f.2 as u16))
            .collect();

        let (mesh, texture) = match colormap {
            Some(colormap) => {
                // create a 1xN texture where each texel = face color
                let face_count = base_faces.len() as u32;
                let mut image = DynamicImage::new_rgba8(face_count, 1);
                for i in 0..face_count {
                    image.put_pixel(i, 0, image::Rgba(colormap[i as usize]));
                }

                // duplicate vertices per face and assign UVs pointing to the right texel
                let mut coords = Vec::new();
                let mut uvs = Vec::new();
                let mut faces = Vec::new();

                for (i, f) in base_faces.iter().enumerate() {
                    let base_u = (i as f32 + 0.5) / (face_count as f32); // center of texel
                    for j in 0..3 {
                        coords.push(base_coords[f[j] as usize]);
                        uvs.push(Point2::new(base_u, 0.5)); // same UV for all 3 vertices
                    }
                    let idx = (i * 3) as u16;
                    faces.push(Point3::new(idx, idx + 1, idx + 2));
                }

                let texture =
                    TextureManager::get_global_manager(|tm| tm.add_image(image.clone(), "colors"));

                (
                    Mesh::new(coords, faces, None, Some(uvs), true),
                    Some(texture),
                )
            }
            None => (Mesh::new(base_coords, base_faces, None, None, true), None),
        };

        // create a mesh and add it to the window
        let mesh = Rc::new(RefCell::new(mesh));
        let mut mesh_node = self.window.add_mesh(mesh, Vector3::new(1.0, 1.0, 1.0));
        mesh_node.enable_backface_culling(false);

        // add the texture (color per face) or set a default color
        match texture {
            Some(tex) => {
                mesh_node.set_texture(tex);
            }
            None => {
                mesh_node.set_color(1.0, 1.0, 1.0);
                // draw the edges
                mesh_node.set_lines_color(Some(Point3::new(1.0, 0.0, 0.0)));
                mesh_node.set_lines_width(1.0);
            }
        }

        // set the lighting
        self.window.set_light(Light::StickToCamera);
        self.nodes.push(mesh_node);
    }

    pub fn draw_path(&mut self, path: &Path, scale: Option<f32>, color: Option<Point3<f32>>) {
        if path.len() <= 2 && (path[0] == path[path.len() - 1]) {
            return self.draw_point(path[0].clone(), scale, color);
        }

        let scale = scale.unwrap_or(1.0);
        let mut source = self.window.add_sphere(0.02 * scale);
        source.set_color(1.0, 0.0, 0.0); // red marker
        source.append_translation(&na::Translation3::new(
            path[0][0] as f32,
            path[0][1] as f32,
            path[0][2] as f32,
        ));

        let mut target = self.window.add_sphere(0.02 * scale);
        target.set_color(0.0, 1.0, 0.0); // green marker
        target.append_translation(&na::Translation3::new(
            path[path.len() - 1][0] as f32,
            path[path.len() - 1][1] as f32,
            path[path.len() - 1][2] as f32,
        ));

        // add nodes to the viewer to handle rotation
        self.nodes.push(source);
        self.nodes.push(target);

        // set the color (argument of default)
        let (r, g, b) = match color {
            Some(c) => (c[0], c[1], c[2]),
            None => (0.0, 0.0, 1.0),
        };

        for i in 0..path.len() - 1 {
            // extract start and end points of the segment
            let p0 = &path[i];
            let p1 = &path[i + 1];

            // add a thin cylinder between p0 and p1
            let dir = Vector3::new(
                (p1[0] - p0[0]) as f32,
                (p1[1] - p0[1]) as f32,
                (p1[2] - p0[2]) as f32,
            );
            let mut line = self.window.add_cylinder(0.005 * scale, dir.norm());
            line.set_color(r, g, b);

            // set the position and orientation
            line.set_local_translation(na::Translation3::new(
                p0[0] as f32 + dir[0] / 2.0,
                p0[1] as f32 + dir[1] / 2.0,
                p0[2] as f32 + dir[2] / 2.0,
            ));
            let rotation = UnitQuaternion::rotation_between(&Vector3::<f32>::y(), &dir.normalize())
                .unwrap_or(UnitQuaternion::identity());
            line.set_local_rotation(rotation);

            // add to the viewer nodes to handle rotation
            self.nodes.push(line);
        }
    }

    pub fn draw_point(&mut self, point: Point, scale: Option<f32>, color: Option<Point3<f32>>) {
        // set the color (argument of default)
        let (r, g, b) = match color {
            Some(c) => (c[0], c[1], c[2]),
            None => (0.0, 0.0, 1.0),
        };
        let scale = scale.unwrap_or(1.0);
        let mut source = self.window.add_sphere(0.02 * scale);
        source.set_color(r, g, b); // red marker
        source.append_translation(&na::Translation3::new(
            point[0] as f32,
            point[1] as f32,
            point[2] as f32,
        ));

        self.nodes.push(source);
    }

    pub fn plot_sources<S: Into<Sources>>(
        &mut self,
        manifold: &Manifold,
        sources: S,
        scale: Option<f32>,
        color: Option<Point3<f32>>,
    ) {
        let source_scale = match scale {
            None => Some(10.0),
            _ => scale,
        };

        let true_sources: Sources = sources.into();
        let source_color = match color {
            None => Some(Point3::from_slice(&[0.0, 0.0, 1.0])),
            _ => color,
        };

        for &s in true_sources.iter() {
            self.draw_point(manifold.vertices()[s].clone(), source_scale, source_color);
        }
    }
    /// Launches the render loop.
    pub fn render(&mut self, rotate: bool) {
        // rotate the object a bit each frame
        while self.window.render_with_camera(&mut self.camera) {
            if rotate {
                let rotation = UnitQuaternion::from_axis_angle(&Vector3::y_axis(), 0.005);
                for segment in &mut self.nodes {
                    segment.append_rotation(&rotation);
                }
            }
        }
    }

    pub fn white_background(&mut self) {
        self.window.set_background_color(1.0, 1.0, 1.0);
    }
}

impl Default for Viewer {
    fn default() -> Self {
        Self::new()
    }
}
