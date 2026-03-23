use geopathic::edp::*;
use geopathic::loader::load_manifold;
use geopathic::sources::Sources;
use itertools::Itertools;
use nalgebra::{DMatrix, DVector};
use rand::Rng;
use std::fs::File;
use std::io::Write;

const METHODS: [SpectralPDE; 4] = [
    SpectralPDE::Eigenmap,
    SpectralPDE::CommuteTime,
    SpectralPDE::Diffusion,
    SpectralPDE::Biharmonic,
];

fn compute_eigen_embedding(laplace_matrix: &DMatrix<f64>, n: usize) -> (Vec<f64>, DMatrix<f64>) {
    let squared_eigens = (laplace_matrix * &laplace_matrix.transpose()).symmetric_eigen();

    let eigenvectors = squared_eigens.eigenvectors;
    let eigenvalues = squared_eigens.eigenvalues;

    // Sort eigenvalues and get corresponding eigenvectors (skip first, take n-1)
    let sorted_eigens: Vec<(usize, f64)> = eigenvalues
        .iter()
        .enumerate()
        .sorted_by(|(_, u), (_, v)| u.partial_cmp(v).unwrap_or(std::cmp::Ordering::Less))
        .skip(1)
        .take(n - 1)
        .map(|(i, v)| (i, *v))
        .collect();

    let eigenvalues_sorted: Vec<f64> = sorted_eigens.iter().map(|(_, v)| *v).collect();

    // Build embedding matrix: rows are vertices, columns are eigenvectors
    let mut eigen_embedding = DMatrix::zeros(n, n - 1);
    for (j, (eigen_idx, _)) in sorted_eigens.iter().enumerate() {
        for i in 0..n {
            eigen_embedding[(i, j)] = eigenvectors[(*eigen_idx, i)];
        }
    }

    (eigenvalues_sorted, eigen_embedding)
}

fn compute_distance_with_k_eigenvectors(
    eigen_embedding: &DMatrix<f64>,
    eigenvalues: &[f64],
    sources: &[usize],
    n: usize,
    k: usize,
    equation: SpectralPDE,
    time_step: f64,
) -> DVector<f64> {
    fn eigenvalue_transformation(equation: &SpectralPDE, l: f64, time_step: f64) -> f64 {
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

    let mut distance_vec = DVector::zeros(n);

    for x_idx in 0..n {
        let mut min_dist = f64::INFINITY;

        for &y_idx in sources {
            let mut dist = 0.0;
            for i in 0..k {
                let point_dist = eigen_embedding[(x_idx, i)] - eigen_embedding[(y_idx, i)];
                let lambda_transform =
                    eigenvalue_transformation(&equation, eigenvalues[i], time_step);
                dist += lambda_transform * point_dist.powi(2);
            }
            min_dist = min_dist.min(dist);
        }

        distance_vec[x_idx] = min_dist;
    }

    distance_vec
}

fn compute_relative_l2_error(dist_k: &DVector<f64>, dist_full: &DVector<f64>) -> (f64, f64) {
    let diff = dist_k - dist_full;
    let error_norm = diff.norm();
    let full_norm = dist_full.norm();

    if full_norm > 1e-10 {
        (error_norm, error_norm / full_norm)
    } else {
        (0.0, 0.0)
    }
}

fn main() {
    // List all files in ../examples/models/
    let model_paths: Vec<_> = std::fs::read_dir("../examples/models/")
        .unwrap()
        .filter_map(|entry| {
            let path = entry.unwrap().path();
            if path.extension()?.to_str()? == "obj" {
                Some(path)
            } else {
                None
            }
        })
        .collect();

    let skipped = [
        // non-manifold meshes
        "nonmanifold_edge.obj",
        "suzanne.obj",
        "teapot.obj",
        // weird propagation
        "cow-nonormals.obj",
        // too big
        // "xwings.obj",
        "screw.obj",
        "dragon.obj",
        "rabbit-head.obj",
        // "fantasy-piece.obj",
        // "ferrari.obj",
    ];
    let model_paths: Vec<_> = model_paths
        .into_iter()
        .filter(|path| !skipped.contains(&path.file_name().unwrap().to_str().unwrap()))
        .collect();

    let mut rng = rand::rng();
    let timestamp = chrono::Local::now().format("%m:%d_%H:%M:%S").to_string();
    let mut file = File::create(format!(
        "../benchmarks/csv/accuracy_spectral_methods_{}.csv",
        timestamp
    ))
    .unwrap();
    writeln!(
        file,
        "model,vertices,faces,method,dimension,embedding size,relative embedding size,error,relative error"
    )
    .unwrap();

    for path in model_paths {
        print!("Computing {:?}", path.file_name().unwrap());
        std::io::stdout().flush().unwrap();
        // load the manifold
        let manifold = load_manifold(path.to_str().unwrap());
        if manifold.is_err() {
            println!(
                "skipping {:?} due to load failure.",
                path.file_name().unwrap()
            );
            continue;
        }
        let manifold = manifold.unwrap();
        let n = manifold.vertices().len();

        // Choose a random source
        let source = rng.random_range(0..n);
        let sources = vec![source];

        let edp = EDPMethod::new(&manifold);
        let time_step = edp.time_step;

        // Compute eigendecomposition once
        let (eigenvalues, eigen_embedding) =
            compute_eigen_embedding(&edp.laplace.laplace_matrix, n);

        // For each method, compute distances for all k values
        for spectral_method in METHODS {
            // Compute full distance (with n-1 eigenvectors)
            let dist_full = compute_distance_with_k_eigenvectors(
                &eigen_embedding,
                &eigenvalues,
                &sources,
                n,
                n - 1,
                spectral_method,
                time_step,
            );

            for k in 1..n {
                let dist_k = compute_distance_with_k_eigenvectors(
                    &eigen_embedding,
                    &eigenvalues,
                    &sources,
                    n,
                    k,
                    spectral_method,
                    time_step,
                );

                let (error, relative_error) = compute_relative_l2_error(&dist_k, &dist_full);

                // Log to CSV
                writeln!(
                    file,
                    "{},{},{},{},{},{},{:.6},{:.10},{:.10}",
                    path.file_name().unwrap().to_str().unwrap(),
                    n,
                    manifold.faces().len(),
                    spectral_method,
                    source,
                    k,
                    k as f64 / n as f64,
                    error,
                    relative_error,
                )
                .unwrap();
            }

            std::io::stdout().flush().unwrap();
            println!("\t{} done.", spectral_method);
        }
    }
}
