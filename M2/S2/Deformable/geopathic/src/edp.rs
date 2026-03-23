/// Module computing geodesics based on different PDEs
use core::f64;
use itertools::Itertools;
use nalgebra::{DMatrix, DVector};
use std::collections::HashMap;
use std::fmt::Display;

use crate::manifold::{Manifold, Point};
use crate::sources::Sources;

// Laplace-Beltrami operator based methods

fn compute_cotangent(a: &Point, b: &Point) -> f64 {
    let dot = a.dot(b);
    let cross = a.cross(b);
    let cross_norm = cross.norm();

    if cross_norm > 1e-10 {
        dot / cross_norm
    } else {
        0.0
    }
}

fn solve_linear_system(a: &DMatrix<f64>, b: &DVector<f64>) -> Result<DVector<f64>, String> {
    a.clone()
        .lu()
        .solve(b)
        .ok_or_else(|| "Failed to solve linear system. Matrix may be ill-conditioned.".to_string())
}

impl Manifold {
    fn compute_face_gradient(
        &self,
        face_idx: usize,
        vertex_values: &DVector<f64>,
    ) -> Result<DVector<f64>, String> {
        let (i, j, k) = self.faces[face_idx];

        let v0 = &self.vertices[i];
        let v1 = &self.vertices[j];
        let v2 = &self.vertices[k];

        let u0 = vertex_values[i];
        let u1 = vertex_values[j];
        let u2 = vertex_values[k];

        let e0 = v2 - v1;
        let e1 = v0 - v2;
        let e2 = v1 - v0;

        // Compute face normal
        let edge1 = v1 - v0;
        let edge2 = v2 - v0;
        let normal = edge1.cross(&edge2);
        let double_area = normal.norm();

        if double_area < 1e-10 {
            return Err("Degenerate face encountered".to_string());
        }

        let n = normal / double_area;

        // Gradient using barycentric formula

        let grad =
            ((&n.cross(&e0) * u0) + (&n.cross(&e1) * u1) + (&n.cross(&e2) * u2)) / double_area;

        Ok(grad)
    }

    fn compute_divergence(&self, face_vectors: &[DVector<f64>]) -> Result<DVector<f64>, String> {
        let n = self.vertices.len();
        let mut divergence = DVector::zeros(n);

        for (face_idx, face) in self.faces.iter().enumerate() {
            let (i, j, k) = *face;

            let vi = &self.vertices[i];
            let vj = &self.vertices[j];
            let vk = &self.vertices[k];

            let x = &face_vectors[face_idx];

            // Edge vectors
            let eij = vj - vi;
            let eik = vk - vi;
            let ejk = vk - vj;

            // Cotangent at each vertex
            let cot_k = compute_cotangent(&eik, &(-&ejk));
            let cot_i = compute_cotangent(&(-&eij), &eik);
            let cot_j = compute_cotangent(&eij, &ejk);

            divergence[i] += 0.5 * (cot_k * (eij.dot(x)) + cot_j * (eik.dot(x)));
            divergence[j] += 0.5 * (cot_i * (ejk.dot(x)) + cot_k * ((-&eij).dot(x)));
            divergence[k] += 0.5 * (cot_j * ((-&eik).dot(x)) + cot_i * ((-&ejk).dot(x)));
        }

        Ok(divergence)
    }

    fn compute_time_step(&self) -> f64 {
        let mut value = 0.0;
        let n_edges = 1.5 * self.faces.len() as f64;
        for f in &self.faces {
            let (i, j, k) = f;
            let v0 = &self.vertices[*i];
            let v1 = &self.vertices[*j];
            let v2 = &self.vertices[*k];

            let e0 = v2 - v1;
            let e1 = v0 - v2;
            let e2 = v1 - v0;

            value += 0.5 * (e0.norm() + e1.norm() + e2.norm());
        }
        let h = value / n_edges;
        h * h
    }
}

/// Structure used for computing the laplacian of a manifold, as its matrix
#[derive(Debug, Clone)]
pub struct Laplacian {
    pub laplace_matrix: DMatrix<f64>,
    pub n_vertices: usize,
}

impl Laplacian {
    pub fn new(manifold: &Manifold) -> Self {
        let n_vertices = manifold.vertices().len();
        let mut laplace_matrix = DMatrix::zeros(n_vertices, n_vertices);

        let mut edge_weights: HashMap<(usize, usize), f64> = HashMap::new();

        for face in manifold.faces() {
            let (i, j, k) = *face;

            let vi = &manifold.vertices()[i];
            let vj = &manifold.vertices()[j];
            let vk = &manifold.vertices()[k];

            // Compute cotangent weights for each edge
            Self::add_cotangent_weight(&mut edge_weights, i, j, k, vi, vj, vk);
            Self::add_cotangent_weight(&mut edge_weights, j, k, i, vj, vk, vi);
            Self::add_cotangent_weight(&mut edge_weights, k, i, j, vk, vi, vj);
        }

        for ((i, j), weight) in edge_weights.iter() {
            laplace_matrix[(*i, *j)] = -weight;
            laplace_matrix[(*j, *i)] = -weight;
        }

        // Set diagonal entries (sum of incident edge weights)
        for i in 0..n_vertices {
            let row_sum: f64 = (0..n_vertices)
                .filter(|&j| j != i)
                .map(|j| -laplace_matrix[(i, j)])
                .sum();
            laplace_matrix[(i, i)] = row_sum;
        }

        Self {
            laplace_matrix,
            n_vertices,
        }
    }

    fn add_cotangent_weight(
        edge_weights: &mut HashMap<(usize, usize), f64>,
        i: usize,
        j: usize,
        _k: usize,
        vi: &Point,
        vj: &Point,
        vk: &Point,
    ) {
        let ki = vi - vk;
        let kj = vj - vk;

        let dot = ki.dot(&kj);
        let cross_norm = ki.cross(&kj).norm();

        if cross_norm > 1e-10 {
            let cot = dot / cross_norm;
            let weight = 0.5 * cot;

            *edge_weights.entry((i.min(j), i.max(j))).or_insert(0.0) += weight;
        }
    }

    pub fn apply(&self, u: &DVector<f64>) -> DVector<f64> {
        &self.laplace_matrix * u
    }

    pub fn matrix(&self) -> &DMatrix<f64> {
        &self.laplace_matrix
    }
}

/// Structure to help choose from the different poisson equations.
// J'ai pas pu m'empêcher pour le nom désolé Antoine
#[derive(Debug, Clone, Copy)]
pub enum Poiffon {
    // bool argument is whether to apply Spalding-Tucker transform.
    ScreenedPoiffon(f64, bool), // (\Delta - \frac{1}{arg1^{2}}) = 0 on M, u = 1 on \partial M
    BorderPoiffon(bool),        // \Delta u = -1 on M, u = 0 on \partial M
}

/// Structure to help choose from the different spectral distance
#[derive(Debug, Clone, Copy)]
pub enum SpectralPDE {
    Eigenmap,
    CommuteTime,
    Biharmonic,
    Diffusion,
}

impl Display for SpectralPDE {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        let display_string = match self {
            SpectralPDE::Eigenmap => "Eigenmap".to_string(),
            SpectralPDE::CommuteTime => "CommuteTime".to_string(),
            SpectralPDE::Biharmonic => "Biharmonic".to_string(),
            SpectralPDE::Diffusion => "Diffusion".to_string(),
        };
        write!(f, "{}", display_string)
    }
}

pub struct EDPMethod<'a> {
    manifold: &'a Manifold,
    pub laplace: Laplacian,
    pub time_step: f64,
}
impl<'a> EDPMethod<'a> {
    pub fn new(manifold: &'a Manifold) -> Self {
        Self {
            manifold,
            laplace: Laplacian::new(manifold),
            time_step: manifold.compute_time_step(),
        }
    }

    pub fn compute_distance_heat<S: Into<Sources>>(
        &self,
        sources: S,
    ) -> Result<DVector<f64>, String> {
        let sources = sources.into();
        self.compute_distance_heat_impl(&sources.0)
    }

    fn compute_distance_heat_impl(&self, sources: &[usize]) -> Result<DVector<f64>, String> {
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

        // (I + t*L)u = δ_source
        let identity = DMatrix::identity(n, n);
        let heat_matrix = &identity + &self.laplace.laplace_matrix * self.time_step;

        let mut rhs = DVector::zeros(n);

        for &source in sources {
            rhs[source] = 1.0;
        }

        let u = solve_linear_system(&heat_matrix, &rhs)?;

        // X = -∇u / |∇u|
        let mut face_gradients = Vec::new();

        for face_idx in 0..self.manifold.faces().len() {
            let gradient = self.manifold.compute_face_gradient(face_idx, &u)?;

            let grad_norm = gradient.norm();
            let normalized_grad = if grad_norm > 1e-10 {
                -gradient / grad_norm
            } else {
                DVector::zeros(3)
            };
            face_gradients.push(normalized_grad);
        }

        // Solve Poisson equation L*φ = ∇·X
        let divergence_x = self.manifold.compute_divergence(&face_gradients)?;

        let regularization = 1e-4;
        let regularized_laplacian = &self.laplace.laplace_matrix + &identity * regularization;

        let phi = solve_linear_system(&regularized_laplacian, &divergence_x)?;

        // For multiple sources, sh ggift so that the minimum distance at sources is 0
        let min_phi_at_sources = sources
            .iter()
            .map(|&s| phi[s])
            .min_by(|a, b| a.partial_cmp(b).unwrap_or(std::cmp::Ordering::Equal))
            .unwrap_or(0.0);
        let distances = phi.map(|x| x - min_phi_at_sources);
        // println!("{}", &distances);

        Ok(distances)
    }

    pub fn compute_distance_poisson<S: Into<Sources>>(
        &self,
        sources: S,
        equation: Poiffon,
    ) -> Result<DVector<f64>, String> {
        let sources = sources.into();
        self.compute_distance_poisson_impl(&sources.0, equation)
    }

    fn compute_distance_poisson_impl(
        &self,
        sources: &[usize],
        equation: Poiffon,
    ) -> Result<DVector<f64>, String> {
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
        let identity = DMatrix::identity(n, n);

        // Equation depending on the source. No time step here, only spatial derivatives
        let regularization = 1e-8;
        let poisson_matrix = match equation {
            Poiffon::ScreenedPoiffon(rho, _) => {
                &self.laplace.laplace_matrix - rho.powi(-2) * &identity
            }
            Poiffon::BorderPoiffon(_) => &self.laplace.laplace_matrix + &identity * regularization,
        };

        let mut rhs = match equation {
            Poiffon::ScreenedPoiffon(_, _) => DVector::zeros(n),
            Poiffon::BorderPoiffon(_) => DVector::from_element(n, -1.0),
        };

        for &source in sources {
            // PERF: Je ne sais pas si je ne devrais pas inverser les deux
            // (mais c'est cheum)
            rhs[source] = match equation {
                Poiffon::ScreenedPoiffon(_, _) => 1.0,
                Poiffon::BorderPoiffon(_) => 0.0,
            };
        }
        let u = solve_linear_system(&poisson_matrix, &rhs)?;

        // For multiple sources, sh ggift so that the minimum distance at sources is 0
        let min_phi_at_sources = sources
            .iter()
            .map(|&s| u[s])
            .min_by(|a, b| a.partial_cmp(b).unwrap_or(std::cmp::Ordering::Equal))
            .unwrap_or(0.0);

        let u0 = u.map(|x| (x - min_phi_at_sources).max(0.0));

        let distances = if matches!(
            equation,
            Poiffon::ScreenedPoiffon(_, true) | Poiffon::BorderPoiffon(true)
        ) {
            self.apply_spalding_tucker(&u0)?
        } else {
            // Standard normalization for other methods
            u0
        };

        Ok(distances)
    }

    fn apply_spalding_tucker(&self, u: &DVector<f64>) -> Result<DVector<f64>, String> {
        let n = self.manifold.vertices().len();
        let mut transformed: DVector<f64> = DVector::zeros(n);

        let mut vertex_grad_norms: DVector<f64> = DVector::zeros(n);
        let mut vertex_counts: DVector<f64> = DVector::zeros(n);

        for face_idx in 0..self.manifold.faces().len() {
            let (i, j, k) = self.manifold.faces()[face_idx];

            let gradient = self.manifold.compute_face_gradient(face_idx, u)?;
            let grad_norm = gradient.norm();

            // Accumulate gradient norm to each vertex of the face
            // (transform face gradient to vertex gradient)
            vertex_grad_norms[i] += grad_norm;
            vertex_grad_norms[j] += grad_norm;
            vertex_grad_norms[k] += grad_norm;

            vertex_counts[i] += 1.0;
            vertex_counts[j] += 1.0;
            vertex_counts[k] += 1.0;
        }
        for i in 0..n {
            if vertex_counts[i] > 0.0 {
                vertex_grad_norms[i] /= vertex_counts[i];
            }
        }

        // Apply Spalding-Tucker transform: sqrt(|nabla u|² + 2u - |nabla u|)
        for i in 0..n {
            let grad_norm = vertex_grad_norms[i];
            let u_val = u[i];

            let argument: f64 = grad_norm * grad_norm + 2.0 * u_val - grad_norm;

            // Ensure numerical stability - argument should be non-negative
            transformed[i] = if argument > 0.0 { argument.sqrt() } else { 0.0 };
        }

        Ok(transformed)
    }

    /// Compute the spectral distance passed as argument. Note that the equation is valid for all
    /// $x, y$ so we compute the distances to each of the sources and take the minimum.
    pub fn compute_distance_spectral<S: Into<Sources>>(
        &self,
        sources: S,
        equation: SpectralPDE,
        embedding_size: usize,
    ) -> Result<DVector<f64>, String> {
        let sources = sources.into();
        self.compute_distance_spectral_impl(&sources.0, equation, embedding_size)
    }

    fn compute_distance_spectral_impl(
        &self,
        sources: &[usize],
        equation: SpectralPDE,
        embedding_size: usize,
    ) -> Result<DVector<f64>, String> {
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

        let squared_eigens = (&self.laplace.laplace_matrix
            * &self.laplace.laplace_matrix.transpose())
            .symmetric_eigen();

        let eigenvectors = squared_eigens.eigenvectors;
        let eigenvalues = squared_eigens.eigenvalues;

        let embedding_eigenvalues = Vec::from_iter(
            eigenvalues
                .iter()
                .enumerate()
                .sorted_by(|(_, u), (_, v)| u.partial_cmp(v).unwrap_or(std::cmp::Ordering::Less))
                .skip(1)
                .take(embedding_size),
        );

        let embedding_eigenvectors = Vec::from_iter(
            embedding_eigenvalues
                .iter()
                .map(|(i, _)| eigenvectors.column(*i)),
        );

        // FIXME: je sais pas faire plus joli
        let mut eigen_embedding = DMatrix::zeros(n, embedding_size);

        (0..n).for_each(|i| {
            embedding_eigenvectors
                .iter()
                .enumerate()
                .for_each(|(j, v)| eigen_embedding[(i, j)] = v[i]);
        });

        fn eigenvalue_transformation(equation: &SpectralPDE, l: &f64, time_step: &f64) -> f64 {
            match equation {
                SpectralPDE::Eigenmap => 1.0,
                SpectralPDE::CommuteTime => 1.0 / l,
                SpectralPDE::Biharmonic => {
                    let invl = 1.0 / l;
                    invl * invl
                }
                SpectralPDE::Diffusion => {
                    let exponent = -2.0 * l * time_step;
                    exponent.exp()
                }
            }
        }

        let mut distance_map = DMatrix::zeros(n, embedding_size);
        self.manifold
            .vertices
            .iter()
            .enumerate()
            .for_each(|(x_idx, _)| {
                sources.iter().enumerate().for_each(|(idx, &y_idx)| {
                    let mut dist = 0.0;
                    embedding_eigenvalues
                        .iter()
                        .enumerate()
                        .for_each(|(i, (_, v))| {
                            let point_dist =
                                eigen_embedding[(x_idx, i)] - eigen_embedding[(y_idx, i)];
                            let lambda_i_transform =
                                eigenvalue_transformation(&equation, v, &self.time_step);
                            dist += lambda_i_transform * point_dist.powi(2);
                        });
                    distance_map[(x_idx, idx)] = dist;
                });
            });

        let mut distance_vec = DVector::zeros(n);
        (0..n).for_each(|i| {
            let distances = distance_map.row(i);
            let max_dist = distances.fold(f64::MIN, |acc, u| if acc <= u { u } else { acc });
            distance_vec[i] = max_dist;
        });

        Ok(distance_vec)
    }

    pub fn test_accuracy_spectral(&self) {}
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_laplacian_construction() {
        let vertices = [
            DVector::from_vec(vec![0.0, 0.0, 0.0]),
            DVector::from_vec(vec![1.0, 0.0, 0.0]),
            DVector::from_vec(vec![0.0, 1.0, 0.0]),
            DVector::from_vec(vec![0.0, 0.0, 1.0]),
        ];

        let faces = [(0, 1, 2), (0, 1, 3), (0, 2, 3), (1, 2, 3)];

        let manifold = Manifold::new(vertices.to_vec(), faces.to_vec());
        let laplace = Laplacian::new(&manifold);

        assert_eq!(laplace.matrix().nrows(), 4);
        assert_eq!(laplace.matrix().ncols(), 4);

        for i in 0..4 {
            let row_sum: f64 = (0..4).map(|j| laplace.matrix()[(i, j)]).sum();
            assert!(row_sum.abs() < 1e-5, "Row {} sum: {}", i, row_sum);
        }
    }

    #[test]
    fn test_heat_method_multiple_sources() {
        let vertices = vec![
            DVector::from_vec(vec![0.0, 0.0, 0.0]),
            DVector::from_vec(vec![1.0, 0.0, 0.0]),
            DVector::from_vec(vec![1.0, 1.0, 0.0]),
            DVector::from_vec(vec![0.0, 1.0, 0.0]),
        ];

        let faces = vec![(0, 1, 2), (0, 2, 3)];

        let manifold = Manifold::new(vertices, faces);
        let heat = EDPMethod::new(&manifold);

        // Test with multiple sources
        let distances = heat.compute_distance_heat(vec![0, 2]).unwrap();

        println!("Multiple source distances (heat method): {:?}", distances);

        // Both sources should have zero or near-zero distance
        assert!(distances[0].abs() < 1e-2, "Source 0 distance should be ~0");
        assert!(distances[2].abs() < 1e-2, "Source 2 distance should be ~0");

        // Test with array syntax
        let distances2 = heat.compute_distance_heat([0, 2]).unwrap();

        // Distances should be similar (may not be exact due to numerical methods)
        for i in 0..4 {
            assert!((distances[i] - distances2[i]).abs() < 1e-6);
        }
    }
}
