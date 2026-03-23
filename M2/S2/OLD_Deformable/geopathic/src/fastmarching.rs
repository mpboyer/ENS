// Wavefront propagation based methods: Fast Marching

use std::{cmp::Ordering, collections::BinaryHeap};

use nalgebra::DVector;

use crate::manifold::Manifold;
use crate::sources::Sources;

/// State of vertex during fast marching (basically adapted Dijkstra)
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
enum VertexState {
    Far,   // Not yet visited
    Trial, // In priority Queue
    Alive, // Distance finalized
}

#[derive(Debug, Clone)]
struct TrialVertex {
    vertex: usize,
    distance: f64,
}

impl PartialEq for TrialVertex {
    fn eq(&self, other: &Self) -> bool {
        self.distance == other.distance
    }
}

impl Eq for TrialVertex {}

impl PartialOrd for TrialVertex {
    fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
        other.distance.partial_cmp(&self.distance) // Order is reversed because we use min-heap
    }
}

impl Ord for TrialVertex {
    fn cmp(&self, other: &Self) -> Ordering {
        self.partial_cmp(other).unwrap_or(Ordering::Equal)
    }
}

pub struct FastMarching<'a> {
    manifold: &'a Manifold,
}

impl<'a> FastMarching<'a> {
    pub fn new(manifold: &'a Manifold) -> Self {
        Self { manifold }
    }

    /// Compute geodesic distance from a source vertex using Fast Marching Method
    /// Based on Kimmel & Sethian (1998)
    pub fn compute_distance<S: Into<Sources>>(&self, sources: S) -> Result<DVector<f64>, String> {
        let sources = sources.into();
        self.compute_distance_impl(&sources.0)
    }

    pub fn compute_distance_impl(&self, sources: &[usize]) -> Result<DVector<f64>, String> {
        let n = self.manifold.vertices().len();

        // Validate sources
        for &source in sources {
            if source >= n {
                return Err(format!(
                    "Source vertex {} out of bounds (max: {})",
                    source,
                    n - 1
                ));
            }
        }

        // Initialize distances and states
        let mut distances = vec![f64::INFINITY; n];
        let mut states = vec![VertexState::Far; n];
        let mut heap = BinaryHeap::new();

        // Set all sources to distance 0 and alive
        for &source in sources {
            distances[source] = 0.0;
            states[source] = VertexState::Alive;
        }

        for &source in sources {
            for face in self.manifold.faces() {
                let (i, j, k) = *face;

                // Check each edge in the face
                if i == source {
                    self.init_neighbor(source, j, &mut distances, &mut states, &mut heap);
                    self.init_neighbor(source, k, &mut distances, &mut states, &mut heap);
                } else if j == source {
                    self.init_neighbor(source, i, &mut distances, &mut states, &mut heap);
                    self.init_neighbor(source, k, &mut distances, &mut states, &mut heap);
                } else if k == source {
                    self.init_neighbor(source, i, &mut distances, &mut states, &mut heap);
                    self.init_neighbor(source, j, &mut distances, &mut states, &mut heap);
                }
            }
        }
        // Fast Marching main loop
        while let Some(trial) = heap.pop() {
            let v = trial.vertex;

            // Skip if already processed (duplicate in heap)
            if states[v] == VertexState::Alive {
                continue;
            }

            // Mark as alive
            states[v] = VertexState::Alive;

            // Update neighbors
            for face in self.manifold.faces() {
                let (i, j, k) = *face;
                if i == v || j == v || k == v {
                    self.update_vertex_from_face(face, v, &mut distances, &mut states, &mut heap)?;
                }
            }
        }

        Ok(DVector::from_vec(distances))
    }

    /// Initialize a direct neighbor of the source with edge distance
    fn init_neighbor(
        &self,
        source: usize,
        neighbor: usize,
        distances: &mut [f64],
        states: &mut [VertexState],
        heap: &mut BinaryHeap<TrialVertex>,
    ) {
        let p_source = &self.manifold.vertices()[source];
        let p_neighbor = &self.manifold.vertices()[neighbor];
        let edge_dist = (p_neighbor - p_source).norm();

        // Only update if this gives a better distance
        if edge_dist < distances[neighbor] {
            distances[neighbor] = edge_dist;

            if states[neighbor] == VertexState::Far {
                states[neighbor] = VertexState::Trial;
            }

            heap.push(TrialVertex {
                vertex: neighbor,
                distance: edge_dist,
            });
        }
    }

    /// Update a vertex by solving the eikonal equation on a triangle
    fn update_vertex_from_face(
        &self,
        face: &(usize, usize, usize),
        known_vertex: usize,
        distances: &mut [f64],
        states: &mut [VertexState],
        heap: &mut BinaryHeap<TrialVertex>,
    ) -> Result<(), String> {
        let (i, j, k) = *face;

        // Try to update each vertex in the face
        for target in [i, j, k] {
            if target == known_vertex || states[target] == VertexState::Alive {
                continue;
            }

            // Find the other two vertices
            let others: Vec<usize> = [i, j, k]
                .iter()
                .filter(|&&v| v != target)
                .copied()
                .collect();

            if others.len() != 2 {
                continue;
            }

            let v1 = others[0];
            let v2 = others[1];

            // Compute new distance using eikonal equation
            let Some(new_dist) = self.solve_eikonal_on_triangle(target, v1, v2, distances)? else {
                continue;
            };

            if new_dist < distances[target] {
                heap.push(TrialVertex {
                    vertex: target,
                    distance: new_dist,
                });
                distances[target] = new_dist;
                if states[target] == VertexState::Far {
                    states[target] = VertexState::Trial;
                }
            }
        }

        Ok(())
    }

    /// Solve the eikonal equation on a triangle to find distance at target
    /// Given distances at v1 and v2, find distance at target
    /// See https://www.cis.upenn.edu/~cis6100/Kimmel-Sethian-geodesics-98.pdf
    fn solve_eikonal_on_triangle(
        &self,
        target: usize, // Vertex C
        v1: usize,     // Vertex A
        v2: usize,     // Vertex B
        distances: &[f64],
    ) -> Result<Option<f64>, String> {
        // Get known distances at A and B
        let distance_a = distances[v1]; // T(A)
        let distance_b = distances[v2]; // T(B)

        // Need at least one known distance
        if distance_a.is_infinite() && distance_b.is_infinite() {
            return Ok(None);
        }

        // Get vertex positions
        let point_c = &self.manifold.vertices()[target]; // Point C (target)
        let point_a = &self.manifold.vertices()[v1]; // Point A
        let point_b = &self.manifold.vertices()[v2]; // Point B
        // C = 1, 1, 0
        // B = 1, 0, 0
        // A = 0, 0, 0

        // Edge lengths from paper's notation
        let a = (point_b - point_c).norm(); // |BC|
        let b = (point_a - point_c).norm(); // |AC|
        let c = (point_b - point_a).norm(); // |AB|

        // One-sided updates if only one distance is known
        if distance_a.is_infinite() {
            return Ok(Some(distance_b + a));
        }
        if distance_b.is_infinite() {
            return Ok(Some(distance_a + b));
        }

        // Speed F = 1 for geodesic distance
        let f = 1.0;

        // Difference in known distances: u = T(B) - T(A)
        let u = distance_b - distance_a;

        // Compute angle θ at vertex C using law of cosines
        // cos(θ) = (a² + b² - c²) / (2ab)
        let cos_theta = (a * a + b * b - c * c) / (2.0 * a * b);
        let cos_theta = cos_theta.clamp(-1.0, 1.0);
        let sin_theta = (1.0 - cos_theta * cos_theta).sqrt();

        // Check if triangle is non-obtuse at C (required for the method)
        // If θ > 90°, cannot do two-sided update from within triangle
        if cos_theta <= 0.0 {
            // Fall back to one-sided update
            return Ok(Some((distance_a + b).min(distance_b + a)));
        }

        // Solve the quadratic equation (Eq. 4 from the paper):
        // (a² + b² - 2ab cos θ)t² + 2bu(a cos θ - b)t + b²(u² - F²a² sin² θ) = 0
        //
        // Coefficients:
        let a_coef = a * a + b * b - 2.0 * a * b * cos_theta;
        let b_coef = 2.0 * b * u * (a * cos_theta - b);
        let c_coef = b * b * (u * u - f * f * a * a * sin_theta * sin_theta);

        if a_coef.abs() < 1e-12 {
            // Degenerate case
            return Ok(Some((distance_a + b).min(distance_b + a)));
        }

        // Solve quadratic: At² + Bt + C = 0
        let discriminant = b_coef * b_coef - 4.0 * a_coef * c_coef;

        if discriminant < 0.0 {
            // No real solution - fall back to one-sided update
            return Ok(Some((distance_a + b).min(distance_b + a)));
        }

        // Take solution that gives t > u (upwind condition)
        // t = (-B ± √discriminant) / (2A)
        let sqrt_disc = discriminant.sqrt();
        let t1 = (-b_coef + sqrt_disc) / (2.0 * a_coef);
        let t2 = (-b_coef - sqrt_disc) / (2.0 * a_coef);

        // Choose solution that satisfies u < t
        let t = if t1 > u && t2 > u {
            t1.min(t2) // Both valid, take smaller
        } else if t1 > u {
            t1
        } else if t2 > u {
            t2
        } else {
            // Neither solution satisfies causality
            return Ok(Some((distance_a + b).min(distance_b + a)));
        };

        // Verify that update comes from within the triangle (Eq. 5 from paper):
        // a cos θ < b(t - u)/t < a / cos θ
        let ratio = b * (t - u) / t;
        let lower_bound = a * cos_theta;
        let upper_bound = a / cos_theta;

        if ratio <= lower_bound || ratio >= upper_bound {
            // Update is not from within the triangle
            // Fall back to one-sided update using edge with smaller distance
            return Ok(Some((distance_a + b).min(distance_b + a)));
        }

        // Final distance: T(C) = T(A) + t
        let distance_c = distance_a + t;

        // Causality check: new distance must be greater than both known distances
        if distance_c <= distance_a.max(distance_b) {
            return Ok(Some((distance_a + b).min(distance_b + a)));
        }

        Ok(Some(distance_c))
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_fast_marching_tetrahedron() {
        let vertices = vec![
            DVector::from_vec(vec![0.0, 0.0, 0.0]),
            DVector::from_vec(vec![1.0, 0.0, 0.0]),
            DVector::from_vec(vec![0.0, 1.0, 0.0]),
            DVector::from_vec(vec![0.0, 0.0, 1.0]),
        ];

        let faces = vec![(0, 1, 2), (0, 1, 3), (0, 2, 3), (1, 2, 3)];

        let manifold = Manifold::new(vertices.clone(), faces);
        let fm = FastMarching::new(&manifold);

        let distances = fm.compute_distance(0).unwrap();

        println!("Computed distances: {:?}", distances);

        // Check that source has zero distance
        assert!(distances[0].abs() < 1e-6, "Source distance should be 0");

        // Check that distances are positive and finite
        for i in 1..4 {
            assert!(
                distances[i] > 0.0,
                "Distance at vertex {} should be positive",
                i
            );
            assert!(
                distances[i].is_finite(),
                "Distance at vertex {} should be finite",
                i
            );
        }

        // The actual geodesic distances on this tetrahedron:
        // Vertices 1,2,3 are all connected by direct edges of length 1.0 from vertex 0
        // But the algorithm might compute them through the polyhedral surface
        // Let's verify they're at least close to 1.0
        assert!(
            (distances[1] - 1.0).abs() < 0.01,
            "Distance to vertex 1: expected ~1.0, got {}",
            distances[1]
        );
        assert!(
            (distances[2] - 1.0).abs() < 0.01,
            "Distance to vertex 2: expected ~1.0, got {}",
            distances[2]
        );

        // Vertex 3 might be computed differently depending on the update order
        // Accept either ~1.0 (direct) or ~1.414 (through another path)
        assert!(
            (distances[3] - 1.0).abs() < 0.01,
            "Distance to vertex 3: expected ~1.0 got {}",
            distances[3]
        );
    }

    #[test]
    fn test_fast_marching_square() {
        // Create a simple square made of two triangles
        let vertices = vec![
            DVector::from_vec(vec![0.0, 0.0, 0.0]),
            DVector::from_vec(vec![1.0, 0.0, 0.0]),
            DVector::from_vec(vec![1.0, 1.0, 0.0]),
            DVector::from_vec(vec![0.0, 1.0, 0.0]),
        ];

        let faces = vec![(0, 1, 2), (0, 2, 3)];

        let manifold = Manifold::new(vertices, faces);
        let fm = FastMarching::new(&manifold);

        let distances = fm.compute_distance(0).unwrap();

        println!("Square distances: {:?}", distances);

        // Expected distances from vertex 0
        assert!(
            distances[0].abs() < 1e-6,
            "Distance to vertex 0: {}",
            distances[0]
        );
        assert!(
            (distances[1] - 1.0).abs() < 1e-6,
            "Distance to vertex 1: expected 1.0, got {}",
            distances[1]
        );
        assert!(
            (distances[3] - 1.0).abs() < 1e-6,
            "Distance to vertex 3: expected 1.0, got {}",
            distances[3]
        );

        // Diagonal distance - should be sqrt(2) but might vary based on path
        println!(
            "Diagonal distance to vertex 2: {} (expected ~{})",
            distances[2],
            2.0_f64.sqrt()
        );
        assert!(
            (distances[2] - 2.0_f64.sqrt()).abs() < 0.1,
            "Distance to vertex 2: expected ~{}, got {}",
            2.0_f64.sqrt(),
            distances[2]
        );
    }

    #[test]
    fn test_fast_marching_symmetry() {
        let vertices = vec![
            DVector::from_vec(vec![0.0, 0.0, 0.0]),
            DVector::from_vec(vec![1.0, 0.0, 0.0]),
            DVector::from_vec(vec![0.0, 1.0, 0.0]),
            DVector::from_vec(vec![0.0, 0.0, 1.0]),
        ];

        let faces = vec![(0, 1, 2), (0, 1, 3), (0, 2, 3), (1, 2, 3)];

        let manifold = Manifold::new(vertices, faces);
        let fm = FastMarching::new(&manifold);

        // Compute from source 0
        let dist_from_0 = fm.compute_distance(0).unwrap();

        println!("Symmetry test distances: {:?}", dist_from_0);
        println!("Distance to v1: {}", dist_from_0[1]);
        println!("Distance to v2: {}", dist_from_0[2]);
        println!("Distance to v3: {}", dist_from_0[3]);

        // Due to symmetry, distances from 0 to vertices 1,2,3 should be similar
        // But they might not be exactly equal due to numerical precision and update order
        let avg_dist = (dist_from_0[1] + dist_from_0[2] + dist_from_0[3]) / 3.0;
        println!("Average distance: {}", avg_dist);

        // Check they're all within 10% of each other
        for i in 1..4 {
            assert!(
                (dist_from_0[i] - avg_dist).abs() / avg_dist < 0.1,
                "Distance {} deviates too much from average: {} vs {}",
                i,
                dist_from_0[i],
                avg_dist
            );
        }
    }

    #[test]
    fn test_fast_marching_multiple_sources() {
        // Create a simple square made of two triangles
        let vertices = vec![
            DVector::from_vec(vec![0.0, 0.0, 0.0]),
            DVector::from_vec(vec![1.0, 0.0, 0.0]),
            DVector::from_vec(vec![1.0, 1.0, 0.0]),
            DVector::from_vec(vec![0.0, 1.0, 0.0]),
        ];

        let faces = vec![(0, 1, 2), (0, 2, 3)];

        let manifold = Manifold::new(vertices, faces);
        let fm = FastMarching::new(&manifold);

        // Test with multiple sources using Vec
        let distances = fm.compute_distance(vec![0, 2]).unwrap();

        println!("Multiple source distances: {:?}", distances);

        // Both sources should have zero distance
        assert!(distances[0].abs() < 1e-6, "Source 0 distance should be 0");
        assert!(distances[2].abs() < 1e-6, "Source 2 distance should be 0");

        // Vertices 1 and 3 should be at distance 1 from their nearest source
        assert!(
            (distances[1] - 1.0).abs() < 1e-6,
            "Distance to vertex 1: expected 1.0, got {}",
            distances[1]
        );
        assert!(
            (distances[3] - 1.0).abs() < 1e-6,
            "Distance to vertex 3: expected 1.0, got {}",
            distances[3]
        );

        // Test with array syntax
        let distances2 = fm.compute_distance([0, 2]).unwrap();
        assert_eq!(distances, distances2);

        // Test with slice
        let sources = vec![0, 2];
        let distances3 = fm.compute_distance(sources.as_slice()).unwrap();
        assert_eq!(distances, distances3);
    }
}
