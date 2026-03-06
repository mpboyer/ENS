//! File containing struct definitions for a memory representation of MANIFolds

use nalgebra::DVector;

/// Generic struct for N-D points.
pub type Point = DVector<f64>;

/// Triangle
pub type Triangle = (usize, usize, usize);

#[derive(Clone, Debug, PartialEq)]
/// Abstract representation of a manifold.
pub struct Manifold {
    pub(crate) vertices: Vec<Point>,
    pub(crate) faces: Vec<Triangle>,
}

impl Manifold {
    pub fn new(vertices: Vec<Point>, faces: Vec<Triangle>) -> Self {
        Manifold { vertices, faces }
    }

    pub fn vertices(&self) -> &[Point] {
        &self.vertices
    }

    pub fn faces(&self) -> &[Triangle] {
        &self.faces
    }
}

pub type Path = Vec<Point>;
