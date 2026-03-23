//! Defines a Mesh structure, extending Manifold by precomputing some data.

use nalgebra::{Point2, Point3};

use crate::manifold;

/// Vertex of a mesh
#[derive(Debug, Clone, PartialEq)]
pub struct Vertex {
    /// Position of the vertex
    pub(crate) position: Point3<f64>,
    /// List of the indices of adjacent edges
    pub(crate) edges: Vec<usize>,
}

/// Edge of a mesh
#[derive(Debug, Clone, PartialEq)]
pub struct Edge {
    /// Index of the start vertex
    pub(crate) start: usize,
    /// Index of the end vertex
    pub(crate) end: usize,
    /// Index of the next edge around the face
    pub(crate) next_edge: usize,
    /// Index of the opposite twin edge
    pub(crate) twin_edge: Option<usize>,
    /// Length of the edge
    pub(crate) length: f64,
    /// Face associated with the edge
    pub(crate) face: usize,
}

/// Face of a mesh
#[derive(Debug, Clone, PartialEq)]
pub struct Face {
    /// Indices of the vertices forming the face
    pub(crate) vertices: [usize; 3],
    /// Indices of the edges forming the face
    pub(crate) edges: [usize; 3],
}

/// Mesh, containing vertices, edge and faces
#[derive(Debug, Clone, PartialEq)]
pub struct Mesh {
    pub(crate) vertices: Vec<Vertex>,
    pub(crate) edges: Vec<Edge>,
    /// List of faces, each defined by a triplet of vertex indices
    pub(crate) faces: Vec<Face>,
    /// Precomputed sum of angles of each vertex
    pub(crate) angles: Vec<f64>,
}

impl Mesh {
    /// Create a Mesh from a Manifold, precomputing necessary data.
    pub fn from_manifold(manifold: &manifold::Manifold) -> Self {
        let mut vertices = Vec::new();
        let mut edges: Vec<Edge> = Vec::new();
        let mut faces: Vec<Face> = Vec::new();
        let mut angles = vec![0.0; manifold.faces().len()];

        // Iterate over the vertices in the manifold
        for v in &manifold.vertices {
            let position = Point3::new(v[0], v[1], v[2]);
            vertices.push(Vertex {
                position,
                edges: Vec::new(),
            });
        }

        // Iterate over the faces in the manifold
        for f in &manifold.faces {
            faces.push(Face {
                vertices: [f.0, f.1, f.2],
                edges: [0; 3],
            });
        }

        // Compute the edges
        for (face_id, face) in faces.iter().enumerate() {
            let v0 = &vertices[face.vertices[0]].position;
            let v1 = &vertices[face.vertices[1]].position;
            let v2 = &vertices[face.vertices[2]].position;

            let edge_lengths = [(v1 - v0).norm(), (v2 - v1).norm(), (v0 - v2).norm()];

            // Create edges
            let edge_indices = [edges.len(), edges.len() + 1, edges.len() + 2];

            for i in 0..3 {
                let start = face.vertices[i];
                let end = face.vertices[(i + 1) % 3];
                let next_edge = edge_indices[(i + 1) % 3];

                edges.push(Edge {
                    start,
                    end,
                    next_edge,
                    twin_edge: None,
                    length: edge_lengths[i],
                    face: face_id,
                });

                vertices[start].edges.push(edge_indices[i]);
            }
        }

        // Compute the twin edges
        for i in 0..edges.len() {
            for j in 0..edges.len() {
                if edges[i].start == edges[j].end && edges[i].end == edges[j].start {
                    edges[i].twin_edge = Some(j);
                }
            }
        }

        // Compute the faces' edge indices
        let mut edge_offset = 0;
        for face in &mut faces {
            for j in 0..3 {
                face.edges[j] = edge_offset;
                edge_offset += 1;
            }
        }

        // Compute angles at each vertex (see code above)
        for face in &faces {
            for j in 0..3 {
                let cur_vert = face.vertices[j];

                let edge0 = edges[face.edges[j]].length;
                let edge1 = edges[face.edges[(j + 2) % 3]].length;

                // let vec0 = vertices[cur_vert].position;
                let vec1 = vertices[face.vertices[(j + 1) % 3]].position;
                let vec2 = vertices[face.vertices[(j + 2) % 3]].position;

                let edge2 = (vec1 - vec2).norm();

                let cur_angle = ((edge0.powi(2) + edge1.powi(2) - edge2.powi(2))
                    / (2.0 * edge0 * edge1))
                    .acos();
                // TODO: handle concave angles properly if necessary
                angles[cur_vert] += cur_angle;
            }
        }

        Mesh {
            vertices,
            edges,
            faces,
            angles,
        }
    }

    pub fn edges_of_vertex(&self, vertex_index: usize) -> Vec<&Edge> {
        let vertex = &self.vertices[vertex_index];
        vertex
            .edges
            .iter()
            .map(|&edge_index| &self.edges[edge_index])
            .collect()
    }

    pub fn point_on_edge(&self, edge_index: usize, t: f64) -> Point3<f64> {
        let edge = &self.edges[edge_index];
        let v_start = &self.vertices[edge.start].position;
        let v_end = &self.vertices[edge.end].position;
        v_start + (v_end - v_start) * t / edge.length
    }

    pub fn check_topology(&self) -> Result<(), String> {
        // every non-boundary edge has exactly one twin and twin.twin == e
        for (e, edge) in self.edges.iter().enumerate() {
            if let Some(t) = edge.twin_edge {
                if t >= self.edges.len() {
                    return Err(format!("twin index out of range for edge {}", e));
                }
                let t2 = self.edges[t].twin_edge.expect("twin.twin missing");
                if t2 != e {
                    return Err(format!("twin.twin != self at edge {}", e));
                }
            }
        }

        // every face must have a 3-cycle: next_edge^3 returns starting edge
        for (f, face) in self.faces.iter().enumerate() {
            for &start_edge in &face.edges {
                let e1 = self.edges[start_edge].next_edge;
                let e2 = self.edges[e1].next_edge;
                let e3 = self.edges[e2].next_edge;
                if e3 != start_edge {
                    return Err(format!(
                        "face {} has broken next_edge cycle at edge {}",
                        f, start_edge
                    ));
                }
            }
        }

        Ok(())
    }
}

/// Compute the Euclidean distance between two 3D points
pub fn dist(p1: &Point3<f64>, p2: &Point3<f64>) -> f64 {
    (p1 - p2).norm()
}

/// Checks whether `p` is on the left of the line formed by `a` and `b`
pub fn is_left(p: &Point2<f64>, a: &Point2<f64>, b: &Point2<f64>) -> bool {
    let ab = b - a;
    let ab = ab.normalize();
    let ap = p - a;
    let ap = ap.normalize();
    (ab.x * ap.y - ab.y * ap.x) > 0.0
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::loader::load_manifold;
    use approx::assert_abs_diff_eq;

    #[test]
    fn manifold_to_mesh_pyramid() {
        let manifold = load_manifold("../examples/models/pyramid.obj").unwrap();
        let mesh = Mesh::from_manifold(&manifold);

        let expected_mesh = Mesh {
            vertices: vec![
                Vertex {
                    position: Point3::new(0.0, 0.0, 0.0),
                    edges: vec![0, 3, 6],
                },
                Vertex {
                    position: Point3::new(1.0, 0.0, 0.0),
                    edges: vec![1, 8, 9],
                },
                Vertex {
                    position: Point3::new(0.0, 1.0, 0.0),
                    edges: vec![2, 4, 11],
                },
                Vertex {
                    position: Point3::new(0.0, 0.0, 1.0),
                    edges: vec![5, 7, 10],
                },
            ],
            edges: vec![
                Edge {
                    start: 0,
                    end: 1,
                    next_edge: 1,
                    twin_edge: Some(8),
                    length: 1.0,
                    face: 0,
                },
                Edge {
                    start: 1,
                    end: 2,
                    next_edge: 2,
                    twin_edge: Some(11),
                    length: f64::sqrt(2.0),
                    face: 0,
                },
                Edge {
                    start: 2,
                    end: 0,
                    next_edge: 0,
                    twin_edge: Some(3),
                    length: 1.0,
                    face: 0,
                },
                Edge {
                    start: 0,
                    end: 2,
                    next_edge: 4,
                    twin_edge: Some(2),
                    length: 1.0,
                    face: 1,
                },
                Edge {
                    start: 2,
                    end: 3,
                    next_edge: 5,
                    twin_edge: Some(10),
                    length: f64::sqrt(2.0),
                    face: 1,
                },
                Edge {
                    start: 3,
                    end: 0,
                    next_edge: 3,
                    twin_edge: Some(6),
                    length: 1.0,
                    face: 1,
                },
                Edge {
                    start: 0,
                    end: 3,
                    next_edge: 7,
                    twin_edge: Some(5),
                    length: 1.0,
                    face: 2,
                },
                Edge {
                    start: 3,
                    end: 1,
                    next_edge: 8,
                    twin_edge: Some(9),
                    length: f64::sqrt(2.0),
                    face: 2,
                },
                Edge {
                    start: 1,
                    end: 0,
                    next_edge: 6,
                    twin_edge: Some(0),
                    length: 1.0,
                    face: 2,
                },
                Edge {
                    start: 1,
                    end: 3,
                    next_edge: 10,
                    twin_edge: Some(7),
                    length: f64::sqrt(2.0),
                    face: 3,
                },
                Edge {
                    start: 3,
                    end: 2,
                    next_edge: 11,
                    twin_edge: Some(4),
                    length: f64::sqrt(2.0),
                    face: 3,
                },
                Edge {
                    start: 2,
                    end: 1,
                    next_edge: 9,
                    twin_edge: Some(1),
                    length: f64::sqrt(2.0),
                    face: 3,
                },
            ],
            faces: vec![
                Face {
                    vertices: [0, 1, 2],
                    edges: [0, 1, 2],
                },
                Face {
                    vertices: [0, 2, 3],
                    edges: [3, 4, 5],
                },
                Face {
                    vertices: [0, 3, 1],
                    edges: [6, 7, 8],
                },
                Face {
                    vertices: [1, 3, 2],
                    edges: [9, 10, 11],
                },
            ],
            angles: vec![4.71238898, 2.617993878, 2.617993878, 2.617993878],
        };

        assert_eq!(mesh.vertices, expected_mesh.vertices);
        assert_eq!(mesh.edges, expected_mesh.edges);
        assert_eq!(mesh.faces, expected_mesh.faces);
        for (a, b) in mesh.angles.iter().zip(expected_mesh.angles.iter()) {
            assert_abs_diff_eq!(a, b, epsilon = 1e-5);
        }
    }

    #[test]
    fn manifold_to_mesh_teddy() {
        let manifold = load_manifold("../examples/models/teddy.obj").unwrap();
        let _ = Mesh::from_manifold(&manifold);
    }
}
