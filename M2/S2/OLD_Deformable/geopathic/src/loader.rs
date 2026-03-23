use crate::manifold::Manifold;
use crate::manifold::Point;
use crate::manifold::Triangle;

use obj::Obj;

#[derive(Debug)]
/// Errors that can occur while loading a manifold.
pub enum LoadError {
    ObjError(obj::ObjError),
    NonTriangularFace(usize),
}

/// Loads a manifold from an OBJ file.
pub fn load_manifold(file_path: &str) -> Result<Manifold, LoadError> {
    let object = Obj::load(file_path).map_err(LoadError::ObjError)?;

    let mut vertices: Vec<Point> = Vec::new();
    let mut faces: Vec<Triangle> = Vec::new();

    for vertex in object.data.position.iter() {
        // Hardcoded 3 dimensions
        vertices.push(Point::from_iterator(3, vertex.iter().map(|&x| x as f64)));
    }

    for sub_obj in object.data.objects {
        for group in sub_obj.groups {
            for poly in group.polys {
                let indices: Vec<usize> = poly.0.iter().map(|v| v.0).collect();
                match indices.len() {
                    3 => faces.push((indices[0], indices[1], indices[2])),
                    _ => return Err(LoadError::NonTriangularFace(indices.len())),
                }
            }
        }
    }

    Ok(Manifold::new(vertices, faces))
}

#[cfg(test)]
mod tests {

    use super::*;

    #[test]
    fn test_load_manifold_teapot() {
        let result = load_manifold("../examples/models/teapot.obj");
        let manifold = result.unwrap();
        dbg!(manifold.vertices.len());
        dbg!(manifold.faces.len());
    }

    #[test]
    fn test_load_manifold_cow() {
        let result = load_manifold("../examples/models/cow-nonormals.obj");
        let manifold = result.unwrap();
        dbg!(manifold.vertices.len());
        dbg!(manifold.faces.len());
    }

    #[test]
    fn test_load_manifold_teddy() {
        let result = load_manifold("../examples/models/teddy.obj");
        let manifold = result.unwrap();
        dbg!(manifold.vertices.len());
        dbg!(manifold.faces.len());
    }
}
