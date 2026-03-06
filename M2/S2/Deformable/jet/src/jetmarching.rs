// Wavefront propagation based methods: Jet Marching
// This is adapted from the fast marching implementation to work with contents of

#![allow(dead_code, unused_variables)] // FIXME: remove this instruction when fully implremented

use std::{cmp::Ordering, collections::BinaryHeap};

use nalgebra::DVector;

use crate::manifold::{Manifold, Triangle};
use crate::sources::Sources;

fn get_barycentric_if_inside(
    p: &DVector<f64>,
    a: &DVector<f64>,
    b: &DVector<f64>,
    c: &DVector<f64>,
) -> Option<(f64, f64, f64)> {
    let v0 = b - a;
    let v1 = c - a;
    let v2 = p - a;
    let d00 = v0.dot(&v0);
    let d01 = v0.dot(&v1);
    let d11 = v1.dot(&v1);
    let d20 = v2.dot(&v0);
    let d21 = v2.dot(&v1);
    let denom = d00 * d11 - d01 * d01;
    if denom.abs() < 1e-12 {
        return None;
    }
    let v = (d11 * d20 - d01 * d21) / denom;
    let w = (d00 * d21 - d01 * d20) / denom;
    let u = 1.0 - v - w;
    if u >= -1e-6 && v >= -1e-6 && w >= -1e-6 {
        Some((u, v, w))
    } else {
        None
    }
}

/// State of vertex during jet marching (basically adapted Dijkstra)
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
enum VertexState {
    Far,   // Not yet visited
    Trial, // In priority Queue
    Valid, // Distance finalized
}

#[derive(Debug, Clone, Copy, PartialEq, Default)]
enum StencilUpdateMethod {
    #[default]
    Mesh,
    Ell1(f64),
    MeshEll1(f64),
}

impl StencilUpdateMethod {
    pub fn has_mesh(&self) -> bool {
        matches!(self, Self::Mesh | Self::MeshEll1(_))
    }

    pub fn _has_ell(&self) -> bool {
        matches!(self, Self::Ell1(_) | Self::MeshEll1(_))
    }

    pub fn get_thresh(&self) -> Option<f64> {
        match self {
            Self::Mesh => None,
            Self::Ell1(a) | Self::MeshEll1(a) => Some(*a),
        }
    }
}

#[derive(Debug, Clone)]
pub struct CubicCurveParams {
    pub x_v: (usize, Option<usize>), // The two end vertices
    pub lambda: f64,
    pub t_v: DVector<f64>, // unit vectors
    pub t_hat: DVector<f64>,
}

#[derive(Debug, Clone)]
pub struct GraphCurveParams {
    pub x_v: (usize, Option<usize>),
    pub lambda: f64,
    pub b0: DVector<f64>,
    pub b1: DVector<f64>,
}

#[derive(Debug, Clone)]
enum Interpolant {
    Cubic(CubicCurveParams),
    Graph(GraphCurveParams),
}

#[derive(Debug, Clone, Copy, Default)]
enum MinimizationProblemMethod {
    #[default]
    FermatIntegral,
    EikonalEquation,
    CellBasedMarching,
    QuadraticCurve,
}

#[derive(Debug, Clone, Copy, Default)]
enum InterpolantRepresentation {
    #[default]
    Cubic,
    Graph,
}

#[derive(Debug, Default, Clone, Copy)]
struct AlgorithmicParameters {
    stencil_update: StencilUpdateMethod,
    minimization_problem: MinimizationProblemMethod,
    interpolant_representation: InterpolantRepresentation,
}

#[derive(Debug, Clone)]
pub struct Jet {
    pub distance: f64,
    pub amplitude: f64,
    pub gradient: DVector<f64>,
}

#[derive(Debug, Clone)]
struct TrialVertex {
    vertex: usize,
    jet: Jet,
    update_interpolant: Interpolant,
}

impl PartialEq for TrialVertex {
    fn eq(&self, other: &Self) -> bool {
        self.jet.distance == other.jet.distance
    }
}

impl Eq for TrialVertex {}

impl PartialOrd for TrialVertex {
    fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
        other.jet.distance.partial_cmp(&self.jet.distance) // Order is reversed because we use min-heap
    }
}

impl Ord for TrialVertex {
    fn cmp(&self, other: &Self) -> Ordering {
        self.partial_cmp(other).unwrap_or(Ordering::Equal)
    }
}

pub struct JetMarching<'a, S: SlownessModel> {
    manifold: &'a Manifold,
    slowness: S,
    vertex_to_faces: Vec<Vec<usize>>, // adjacency map at runtime for faces
    params: AlgorithmicParameters,
}

impl Manifold {
    fn ell1(&self, x1_idx: usize, x2_idx: usize) -> f64 {
        let x1 = &self.vertices()[x1_idx];
        let x2 = &self.vertices()[x2_idx];
        (x2 - x1).abs().sum()
    }
}

pub trait SlownessModel {
    fn at_vertex(&self, idx: usize, manifold: &Manifold) -> f64;

    fn at_point_local(
        &self,
        p: &DVector<f64>,
        manifold: &Manifold,
        local_indices: &[usize],
        vertex_to_faces: &[Vec<usize>],
    ) -> f64;
}

impl SlownessModel for Vec<f64> {
    fn at_vertex(&self, idx: usize, manifold: &Manifold) -> f64 {
        self[idx]
    }

    fn at_point_local(
        &self,
        p: &DVector<f64>,
        manifold: &Manifold,
        local_indices: &[usize],
        vertex_to_faces: &[Vec<usize>],
    ) -> f64 {
        let mut candidates = Vec::with_capacity(12);
        for &v_idx in local_indices {
            for &f_idx in &vertex_to_faces[v_idx] {
                if !candidates.contains(&f_idx) {
                    candidates.push(f_idx);
                }
            }
        }

        for f_idx in candidates {
            let (i, j, k) = manifold.faces()[f_idx];
            let p0 = &manifold.vertices()[i];
            let p1 = &manifold.vertices()[j];
            let p2 = &manifold.vertices()[k];

            if let Some((u, v, w)) = get_barycentric_if_inside(p, p0, p1, p2) {
                return u * self[i] + v * self[j] + w * self[k];
            }
        }

        if local_indices.len() >= 2 {
            let p1 = &manifold.vertices()[local_indices[0]];
            let p2 = &manifold.vertices()[local_indices[1]];
            let d1 = (p - p1).norm();
            let d2 = (p - p2).norm();
            if d1 + d2 < 1e-12 {
                return self[local_indices[0]];
            }
            return (d2 * self[local_indices[0]] + d1 * self[local_indices[1]]) / (d1 + d2);
        }
        self[local_indices[0]]
    }
}

impl<F> SlownessModel for F
where
    F: Fn(&DVector<f64>) -> f64,
{
    fn at_vertex(&self, idx: usize, manifold: &Manifold) -> f64 {
        self(&manifold.vertices()[idx])
    }

    fn at_point_local(
        &self,
        p: &DVector<f64>,
        manifold: &Manifold,
        local_indices: &[usize],
        vertex_to_faces: &[Vec<usize>],
    ) -> f64 {
        self(p)
    }
}

impl<'a, Sl: SlownessModel> JetMarching<'a, Sl> {
    pub fn new(manifold: &'a Manifold, slowness: Sl) -> Self {
        let n_vertices = manifold.vertices().len();
        let mut vertex_to_faces = vec![Vec::new(); n_vertices];

        for (face_idx, &(i, j, k)) in manifold.faces().iter().enumerate() {
            vertex_to_faces[i].push(face_idx);
            vertex_to_faces[j].push(face_idx);
            vertex_to_faces[k].push(face_idx);
        }

        Self {
            manifold,
            slowness,
            vertex_to_faces,
            params: AlgorithmicParameters::default(),
        }
    }

    fn get_incident_faces(&self, v_idx: usize) -> Vec<Triangle> {
        self.vertex_to_faces[v_idx]
            .iter()
            .map(|&f_idx| self.manifold.faces[f_idx])
            .collect()
    }

    fn get_neighbours(&self, v_idx: usize) -> Vec<usize> {
        let mut neighbours = Vec::new();
        for &f_idx in &self.vertex_to_faces[v_idx] {
            let (i, j, k) = self.manifold.faces()[f_idx];
            if i != v_idx {
                neighbours.push(i);
            }
            if j != v_idx {
                neighbours.push(j);
            }
            if k != v_idx {
                neighbours.push(k);
            }
        }
        neighbours.sort_unstable();
        neighbours.dedup();
        neighbours
    }

    /// Compute geodesic distance from a source vertex using Jet Marching Method
    pub fn compute_distance<S: Into<Sources>>(
        &self,
        sources: S,
    ) -> Result<(DVector<f64>, DVector<f64>), String> {
        let sources = sources.into();
        self.compute_distance_impl(&sources.0)
    }

    pub fn compute_distance_impl(
        &self,
        sources: &[usize],
    ) -> Result<(DVector<f64>, DVector<f64>), String> {
        let n = self.manifold.vertices().len();
        let dim = 3;

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
        let mut jets = vec![Jet {
            distance: f64::INFINITY,
            amplitude: 0.0,
            gradient: DVector::from_element(dim, 0.0),
        }];
        let mut states = vec![VertexState::Far; n];
        let mut heap = BinaryHeap::new();

        // Set all sources to distance 0, gradient 0 (local minima) and alive
        for &source in sources {
            jets[source] = Jet {
                distance: 0.0,
                amplitude: 1.0,
                gradient: DVector::from_element(dim, 0.0),
            };
            states[source] = VertexState::Valid;
        }

        for &source in sources {
            for &f_idx in &self.vertex_to_faces[source] {
                let (i, j, k) = self.manifold.faces()[f_idx];
                for &neighbour in &[i, j, k] {
                    if neighbour != source && states[neighbour] != VertexState::Valid {
                        self.init_neighbour(source, neighbour, &mut jets, &mut states, &mut heap);
                    }
                }
            }
        }
        // Fast Marching main loop
        while let Some(trial) = heap.pop() {
            let v = trial.vertex;

            // Skip if already processed (duplicate in heap)
            if states[v] == VertexState::Valid {
                continue;
            }

            states[v] = VertexState::Valid;
            // TODO: March amplitude

            // Update neighbours
            for &n_idx in &self.get_neighbours(v) {
                if states[n_idx] != VertexState::Valid {
                    self.update_vertex(n_idx, &mut jets, &mut states, &mut heap)?;
                }
            }
        }

        let distances = DVector::from_vec(jets.iter().map(|j| j.distance).collect());

        let amplitudes = DVector::from_vec(jets.iter().map(|j| j.amplitude).collect());

        Ok((distances, amplitudes))
    }

    /// Initialize a direct neighbour of the source with edge distance
    fn init_neighbour(
        &self,
        source: usize,
        neighbour: usize,
        jets: &mut [Jet],
        states: &mut [VertexState],
        heap: &mut BinaryHeap<TrialVertex>,
    ) {
        let p_source = &self.manifold.vertices()[source];
        let p_neighbour = &self.manifold.vertices()[neighbour];
        let edge_vec = p_neighbour - p_source;
        let edge_dist = edge_vec.norm();
        let tau_hat =
            jets[source].distance + edge_dist * self.slowness.at_vertex(neighbour, self.manifold);

        if tau_hat < jets[neighbour].distance {
            let t_hat = edge_vec.normalize();
            let new_jet = Jet {
                distance: tau_hat,
                amplitude: jets[source].amplitude,
                gradient: t_hat.clone() * self.slowness.at_vertex(neighbour, self.manifold),
            };

            let interpolant = match self.params.interpolant_representation {
                InterpolantRepresentation::Cubic => Interpolant::Cubic(CubicCurveParams {
                    x_v: (source, None), // We are in d=1
                    lambda: 0.0,
                    t_v: t_hat.clone(), // In 1d, t_v = t_hat
                    t_hat,
                }),
                InterpolantRepresentation::Graph => Interpolant::Graph(GraphCurveParams {
                    x_v: (source, None),
                    lambda: 0.0,
                    b0: DVector::from_element(3, 0.0),
                    b1: DVector::from_element(3, 0.0),
                }),
            };

            states[neighbour] = VertexState::Trial;
            jets[neighbour] = new_jet.clone();

            heap.push(TrialVertex {
                vertex: neighbour,
                jet: new_jet,
                update_interpolant: interpolant,
            });
        }
    }

    fn update_vertex(
        &self,
        x_hat_idx: usize,
        jets: &mut [Jet],
        states: &mut [VertexState],
        heap: &mut BinaryHeap<TrialVertex>,
    ) -> Result<(), String> {
        let neighbours = self.get_neighbours(x_hat_idx);
        let valid_neighbours: Vec<usize> = neighbours
            .into_iter()
            .filter(|&n| states[n] == VertexState::Valid)
            .collect();

        if valid_neighbours.is_empty() {
            return Ok(());
        }

        let mut best_jet: Option<Jet> = None;

        // We use the OLIM hierchical update strategy with at most triangles as we are on
        // 2-manifolds embedded in \mathbb{R}^{3}
        let mut best_x1: Option<usize> = None;
        let mut best_interp: Option<Interpolant> = None;

        // Line updates with \hat{x} fixed
        for &x1 in &valid_neighbours {
            if let Some((candidate, interpolant)) = self.solve_line_update(x_hat_idx, x1, jets)?
                && (best_jet.is_none() || candidate.distance < best_jet.as_ref().unwrap().distance)
            {
                best_jet = Some(candidate);
                best_x1 = Some(x1);
                best_interp = Some(interpolant);
            }
        }

        // Triangle updates with \hat{x} and x_{1} fixed, only if \hat{x}x_{1}x_{2} \in \mathcal{F}
        // Default mesh based updates
        if let Some(x1_idx) = best_x1
            && self.params.stencil_update.has_mesh()
        {
            for &f_idx in &self.vertex_to_faces[x_hat_idx] {
                let (i, j, k) = self.manifold.faces()[f_idx];

                let x2 = if (i == x_hat_idx && j == x1_idx) || (j == x_hat_idx && i == x1_idx) {
                    Some(k)
                } else if (i == x_hat_idx && k == x1_idx) || (k == x_hat_idx && i == x1_idx) {
                    Some(j)
                } else if (j == x_hat_idx && k == x1_idx) || (k == x_hat_idx && j == x1_idx) {
                    Some(i)
                } else {
                    None
                };

                if let Some(x2_idx) = x2
                    && x1_idx != x2_idx
                    && states[x2_idx] == VertexState::Valid
                    && let Some((candidate, interpolant)) =
                        self.solve_triangle_update(x_hat_idx, x1_idx, x2_idx, jets)?
                    && (candidate.distance < best_jet.as_ref().unwrap().distance)
                {
                    best_jet = Some(candidate);
                    best_interp = Some(interpolant);
                }
            }
        }

        // If we also use \ell^{1} based updates:
        if let Some(x1_idx) = best_x1
            && let Some(thresh) = self.params.stencil_update.get_thresh()
        {
            for &x2_idx in &valid_neighbours {
                if x2_idx != x1_idx
                    && self.manifold.ell1(x1_idx, x2_idx) < thresh
                    && let Some((candidate, interpolant)) =
                        self.solve_triangle_update(x_hat_idx, x1_idx, x2_idx, jets)?
                    && (candidate.distance < best_jet.as_ref().unwrap().distance)
                {
                    best_jet = Some(candidate);
                    best_interp = Some(interpolant);
                }
            }
        }

        if let Some(jet) = best_jet
            && jet.distance < jets[x_hat_idx].distance
            && let Some(interp) = best_interp
        {
            jets[x_hat_idx] = jet.clone();
            states[x_hat_idx] = VertexState::Trial;
            heap.push(TrialVertex {
                vertex: x_hat_idx,
                jet,
                update_interpolant: interp,
            });
        }

        Ok(())
    }

    /// For a given possible 1-update, compute the associated parametrization of \phi and the
    /// jet.
    fn solve_line_update(
        &self,
        x_hat: usize,
        x_1: usize,
        jets: &[Jet],
    ) -> Result<Option<(Jet, Interpolant)>, String> {
        let p1 = &self.manifold.vertices()[x_1];
        let p_hat = &self.manifold.vertices()[x_hat];

        let jet1 = &jets[x_1];

        let edge_vec = p_hat - p1;
        let h = edge_vec.norm();
        if h < f64::EPSILON {
            return Ok(None);
        }
        let s1 = self.slowness.at_vertex(x_1, self.manifold);
        let s_hat = self.slowness.at_vertex(x_hat, self.manifold);

        let grad_lambda = if jet1.distance == 0.0 {
            edge_vec.normalize() * s1
        } else {
            jet1.gradient.clone()
        };
        let grad_hat = edge_vec.normalize() * s_hat;

        let (f_lambda, f_mid, f_hat) = match self.params.interpolant_representation {
            InterpolantRepresentation::Cubic => {
                let t_lambda = grad_lambda.normalize();
                let t_hat = grad_hat.normalize();

                let phi_prime_mid = 1.5 * edge_vec - h * 0.25 * (&t_lambda + &t_hat);
                let norm_phi_mid = phi_prime_mid.norm();

                let p_mid = 0.5 * (p1 + p_hat) + (h / 8.) * (&t_lambda - &t_hat);
                let s_mid = self.slowness.at_point_local(
                    &p_mid,
                    self.manifold,
                    &[x_1, x_hat],
                    &self.vertex_to_faces,
                );

                (s1 * h, s_mid * norm_phi_mid, s_hat * h)
            }
            InterpolantRepresentation::Graph => {
                let p_mid = 0.5 * (p1 + p_hat);
                let s_mid = self.slowness.at_point_local(
                    &p_mid,
                    self.manifold,
                    &[x_1, x_hat],
                    &self.vertex_to_faces,
                );

                (s1 * h, s_mid * h, s_hat * h)
            }
        };

        let new_dist = jet1.distance + (h / 6.0) * (f_lambda + 4.0 * f_mid + f_hat); // Eq 3.3 in 3.1

        let new_jet = Jet {
            distance: new_dist,
            gradient: grad_hat.clone(),
            amplitude: jet1.amplitude,
        };

        let interpolant = match self.params.interpolant_representation {
            InterpolantRepresentation::Cubic => Interpolant::Cubic(CubicCurveParams {
                x_v: (x_1, None),
                lambda: 0.0,
                t_v: grad_lambda.normalize(),
                t_hat: grad_hat.normalize(),
            }),
            InterpolantRepresentation::Graph => Interpolant::Graph(GraphCurveParams {
                x_v: (x_1, None),
                lambda: 0.0,
                b0: DVector::from_element(3, 0.0),
                b1: DVector::from_element(3, 0.0),
            }),
        };

        Ok(Some((new_jet, interpolant)))
    }

    /// For a given possible 2-update (x_hat, x_1, x_2), solve the minimization problem verified by
    /// t_\lambda and compute a parametrization of \phi. Compute the associated jet and update
    /// path, and return them.
    fn solve_triangle_update(
        &self,
        x_hat: usize,
        x_1: usize,
        x_2: usize,
        jets: &[Jet],
    ) -> Result<Option<(Jet, Interpolant)>, String> {
        match self.params.minimization_problem {
            MinimizationProblemMethod::FermatIntegral => {
                match self.params.interpolant_representation {
                    InterpolantRepresentation::Cubic => todo!(),
                    InterpolantRepresentation::Graph => todo!(),
                }
            }
            MinimizationProblemMethod::EikonalEquation => {
                match self.params.interpolant_representation {
                    InterpolantRepresentation::Cubic => todo!(),
                    InterpolantRepresentation::Graph => todo!(),
                }
            }
            MinimizationProblemMethod::CellBasedMarching => {
                match self.params.interpolant_representation {
                    InterpolantRepresentation::Cubic => todo!(),
                    InterpolantRepresentation::Graph => todo!(),
                }
            }
            MinimizationProblemMethod::QuadraticCurve => {
                match self.params.interpolant_representation {
                    InterpolantRepresentation::Cubic => todo!(),
                    InterpolantRepresentation::Graph => todo!(),
                }
            }
        }
    }
}

#[cfg(test)]
mod geometry_tests {
    use super::*;
    use nalgebra::DVector;

    #[test]
    fn test_barycentric_inside() {
        let a = DVector::from_vec(vec![0.0, 0.0, 0.0]);
        let b = DVector::from_vec(vec![1.0, 0.0, 0.0]);
        let c = DVector::from_vec(vec![0.0, 1.0, 0.0]);

        // Point au centre du triangle
        let p = DVector::from_vec(vec![0.25, 0.25, 0.0]);
        let result = get_barycentric_if_inside(&p, &a, &b, &c);

        assert!(result.is_some());
        let (u, v, w) = result.unwrap();
        // u*a + v*b + w*c = p => 0.5*a + 0.25*b + 0.25*c
        assert!((u - 0.5).abs() < 1e-12);
        assert!((v - 0.25).abs() < 1e-12);
        assert!((w - 0.25).abs() < 1e-12);
    }

    #[test]
    fn test_barycentric_outside() {
        let a = DVector::from_vec(vec![0.0, 0.0, 0.0]);
        let b = DVector::from_vec(vec![1.0, 0.0, 0.0]);
        let c = DVector::from_vec(vec![0.0, 1.0, 0.0]);

        let p = DVector::from_vec(vec![1.0, 1.0, 0.0]); // Clairement dehors
        let result = get_barycentric_if_inside(&p, &a, &b, &c);
        assert!(result.is_none());
    }

    #[test]
    fn test_slowness_interpolation_vec() {
        // Mock manifold simple : un seul triangle
        let vertices = vec![
            DVector::from_vec(vec![0.0, 0.0, 0.0]),
            DVector::from_vec(vec![2.0, 0.0, 0.0]),
            DVector::from_vec(vec![0.0, 2.0, 0.0]),
        ];
        let faces = vec![(0, 1, 2)];
        let manifold = Manifold::new(vertices, faces);

        // Slowness différente à chaque sommet
        let slowness_values = vec![10.0, 20.0, 30.0];

        // Table d'adjacence simplifiée
        let mut v2f = vec![vec![0], vec![0], vec![0]];

        // Point milieu : (0.5, 0.5, 0)
        let p_mid = DVector::from_vec(vec![0.5, 0.5, 0.0]);

        // Les coordonnées barycentriques pour (0.5, 0.5) dans (0,0)-(2,0)-(0,2) sont:
        // p = u*(0,0) + v*(2,0) + w*(0,2) => v=0.25, w=0.25, u=0.5
        // s = 0.5*10 + 0.25*20 + 0.25*30 = 5 + 5 + 7.5 = 17.5

        let s_interp = slowness_values.at_point_local(
            &p_mid,
            &manifold,
            &[0, 1], // Stencil sur l'arête 0-1
            &v2f,
        );

        assert!(
            (s_interp - 17.5).abs() < 1e-12,
            "L'interpolation barycentrique a échoué: obtenu {}",
            s_interp
        );
    }

    #[test]
    fn test_slowness_fallback_edge() {
        // Test quand le point est sur l'arête mais aucune face n'est trouvée (cas limite)
        let vertices = vec![
            DVector::from_vec(vec![0.0, 0.0, 0.0]),
            DVector::from_vec(vec![1.0, 0.0, 0.0]),
        ];
        let manifold = Manifold::new(vertices, vec![]); // Pas de faces
        let slowness = vec![1.0, 2.0];
        let v2f = vec![vec![], vec![]];

        let p_mid = DVector::from_vec(vec![0.75, 0.0, 0.0]);
        let s_interp = slowness.at_point_local(&p_mid, &manifold, &[0, 1], &v2f);

        // 75% du chemin vers le sommet 1 (s=2.0)
        assert!((s_interp - 1.75).abs() < 1e-12);
    }

    // --- Tests pour la distance L1 ---

    #[test]
    fn test_manifold_ell1_distance() {
        let vertices = vec![
            DVector::from_vec(vec![0.0, 0.0, 0.0]),
            DVector::from_vec(vec![1.0, 2.0, -1.0]),
        ];
        let manifold = Manifold::new(vertices, vec![]);

        // L1 = |1-0| + |2-0| + |-1-0| = 1 + 2 + 1 = 4
        let dist = manifold.ell1(0, 1);
        assert!((dist - 4.0).abs() < 1e-12);
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_jet_marching_tetrahedron() {
        let vertices = vec![
            DVector::from_vec(vec![0.0, 0.0, 0.0]),
            DVector::from_vec(vec![1.0, 0.0, 0.0]),
            DVector::from_vec(vec![0.0, 1.0, 0.0]),
            DVector::from_vec(vec![0.0, 0.0, 1.0]),
        ];
        let faces = vec![(0, 1, 2), (0, 1, 3), (0, 2, 3), (1, 2, 3)];

        // Initialisation de la slowness à 1.0 pour chaque sommet
        let slowness = vec![1.0; vertices.len()];

        let manifold = Manifold::new(vertices, faces);
        let fm = JetMarching::new(&manifold, slowness);

        let (distances, _amplitudes) = fm.compute_distance(0).unwrap();

        assert!(distances[0].abs() < 1e-6, "Source distance should be 0");

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

        // Vérification des distances directes (arêtes de longueur 1.0)
        assert!((distances[1] - 1.0).abs() < 0.01);
        assert!((distances[2] - 1.0).abs() < 0.01);
        assert!((distances[3] - 1.0).abs() < 0.01);
    }

    #[test]
    fn test_jet_marching_square() {
        let vertices = vec![
            DVector::from_vec(vec![0.0, 0.0, 0.0]),
            DVector::from_vec(vec![1.0, 0.0, 0.0]),
            DVector::from_vec(vec![1.0, 1.0, 0.0]),
            DVector::from_vec(vec![0.0, 1.0, 0.0]),
        ];
        let faces = vec![(0, 1, 2), (0, 2, 3)];
        let slowness = vec![1.0; vertices.len()];

        let manifold = Manifold::new(vertices, faces);
        let fm = JetMarching::new(&manifold, slowness);

        let (distances, _amplitudes) = fm.compute_distance(0).unwrap();

        assert!(distances[0].abs() < 1e-6);
        assert!((distances[1] - 1.0).abs() < 1e-6);
        assert!((distances[3] - 1.0).abs() < 1e-6);

        // La distance diagonale (0 -> 2)
        assert!((distances[2] - 2.0_f64.sqrt()).abs() < 0.1);
    }

    #[test]
    fn test_jet_marching_symmetry() {
        let vertices = vec![
            DVector::from_vec(vec![0.0, 0.0, 0.0]),
            DVector::from_vec(vec![1.0, 0.0, 0.0]),
            DVector::from_vec(vec![0.0, 1.0, 0.0]),
            DVector::from_vec(vec![0.0, 0.0, 1.0]),
        ];
        let faces = vec![(0, 1, 2), (0, 1, 3), (0, 2, 3), (1, 2, 3)];
        let slowness = vec![1.0; vertices.len()];

        let manifold = Manifold::new(vertices, faces);
        let fm = JetMarching::new(&manifold, slowness);

        let (dist_from_0, _amplitudes) = fm.compute_distance(0).unwrap();
        let avg_dist = (dist_from_0[1] + dist_from_0[2] + dist_from_0[3]) / 3.0;

        for i in 1..4 {
            assert!((dist_from_0[i] - avg_dist).abs() / avg_dist < 0.1);
        }
    }

    #[test]
    fn test_jet_marching_multiple_sources() {
        let vertices = vec![
            DVector::from_vec(vec![0.0, 0.0, 0.0]),
            DVector::from_vec(vec![1.0, 0.0, 0.0]),
            DVector::from_vec(vec![1.0, 1.0, 0.0]),
            DVector::from_vec(vec![0.0, 1.0, 0.0]),
        ];
        let faces = vec![(0, 1, 2), (0, 2, 3)];
        let slowness = vec![1.0; vertices.len()];

        let manifold = Manifold::new(vertices, faces);
        let fm = JetMarching::new(&manifold, slowness);

        let (distances, _amplitudes) = fm.compute_distance(0).unwrap();

        assert!(distances[0].abs() < 1e-6);
        assert!(distances[2].abs() < 1e-6);
        assert!((distances[1] - 1.0).abs() < 1e-6);
        assert!((distances[3] - 1.0).abs() < 1e-6);

        // Vérification des syntaxes d'entrée (Into<Sources>)
        let (distances2, _amplitudes) = fm.compute_distance(0).unwrap();
        assert_eq!(distances, distances2);
    }
}
