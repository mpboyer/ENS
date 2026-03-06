use nalgebra::{DVector, Point3};

use crate::manifold::{Manifold, Path};
use crate::viewer::Viewer;

// Color endpoints: purple #7d1dd3 to yellow #ffe500
const COLOR_START: [f64; 3] = [0xff as f64, 0x00 as f64, 0x00 as f64];
const COLOR_END: [f64; 3] = [0x00 as f64, 0xff as f64, 0x00 as f64];

pub fn random_colormap(manifold: &Manifold) -> Vec<[u8; 4]> {
    (0..manifold.faces().len())
        .map(|i| {
            let r = ((i * 37) % 256) as u8;
            let g = ((i * 59) % 256) as u8;
            let b = ((i * 83) % 256) as u8;
            [r, g, b, 255]
        })
        .collect()
}

/// Create a colormap with a gradient from blue to red depending on the height of the face centroid
pub fn vertical_colormap(manifold: &Manifold) -> Vec<[u8; 4]> {
    let mut colormap = Vec::with_capacity(manifold.faces().len());
    // compute the lowest and highest y among vertices
    let mut min_y = f64::MAX;
    let mut max_y = f64::MIN;
    for vertex in manifold.vertices() {
        if vertex[1] < min_y {
            min_y = vertex[1];
        }
        if vertex[1] > max_y {
            max_y = vertex[1];
        }
    }
    for face in manifold.faces() {
        let v0 = &manifold.vertices()[face.0];
        let v1 = &manifold.vertices()[face.1];
        let v2 = &manifold.vertices()[face.2];
        let centroid_y = (v0[1] + v1[1] + v2[1]) / 3.0;
        let t = (centroid_y - min_y) / (max_y - min_y);
        let r = (t * 255.0) as u8;
        let g = 0;
        let b = ((1.0 - t) * 255.0) as u8;
        colormap.push([r, g, b, 255]);
    }
    colormap
}

/// Create a colormap from distance values, mapping from red to green.
/// The distance value for each face is the mean of its vertex distances.
/// Infinite distances are colored grey if interpolate_infinite is false,
/// otherwise they are interpolated based on the finite distances of adjacent faces.
pub fn distance_colormap(
    manifold: &Manifold,
    distances: &DVector<f64>,
    interpolate_infinite: bool,
) -> Vec<[u8; 4]> {
    let mut colormap = Vec::with_capacity(manifold.faces().len());

    // Only keep finite distances for min/max calculation
    let finite_distances: Vec<f64> = distances
        .iter()
        .cloned()
        .filter(|d| d.is_finite())
        .collect();

    // Find min and max distances for normalization
    let min_dist = finite_distances
        .iter()
        .cloned()
        .fold(f64::INFINITY, f64::min);
    let max_dist = finite_distances
        .iter()
        .cloned()
        .fold(f64::NEG_INFINITY, f64::max);
    let range = max_dist - min_dist;

    for face in manifold.faces() {
        let (i, j, k) = *face;

        // Compute mean distance for this face
        let mean_dist = (distances[i] + distances[j] + distances[k]) / 3.0;

        // Normalize to [0, 1]
        let t = if range > 1e-10 {
            (mean_dist - min_dist) / range
        } else {
            0.0
        };

        if mean_dist.is_infinite() {
            if !interpolate_infinite {
                colormap.push([200, 200, 200, 255]); // Grey for infinite distances
            } else {
                // interpolate colors between only two points
                let mean_dist_1 = (distances[i] + distances[j]) / 2.0;
                let mean_dist_2 = (distances[j] + distances[k]) / 2.0;
                let mean_dist_3 = (distances[k] + distances[i]) / 2.0;
                if mean_dist_1.is_infinite()
                    && mean_dist_2.is_infinite()
                    && mean_dist_3.is_infinite()
                {
                    colormap.push([200, 200, 200, 255]); // Grey for infinite distances
                } else {
                    let mut finite_means = Vec::new();
                    if mean_dist_1.is_finite() {
                        finite_means.push(mean_dist_1);
                    }
                    if mean_dist_2.is_finite() {
                        finite_means.push(mean_dist_2);
                    }
                    if mean_dist_3.is_finite() {
                        finite_means.push(mean_dist_3);
                    }
                    let avg_mean = finite_means.iter().sum::<f64>() / (finite_means.len() as f64);
                    let t_avg = (avg_mean - min_dist) / range;
                    let r = (COLOR_START[0] + t_avg * (COLOR_END[0] - COLOR_START[0])) as u8;
                    let g = (COLOR_START[1] + t_avg * (COLOR_END[1] - COLOR_START[1])) as u8;
                    let b = (COLOR_START[2] + t_avg * (COLOR_END[2] - COLOR_START[2])) as u8;
                    colormap.push([r, g, b, 255]);
                }
            }
        } else {
            // Interpolate colors
            let r = (COLOR_START[0] + t * (COLOR_END[0] - COLOR_START[0])) as u8;
            let g = (COLOR_START[1] + t * (COLOR_END[1] - COLOR_START[1])) as u8;
            let b = (COLOR_START[2] + t * (COLOR_END[2] - COLOR_START[2])) as u8;
            colormap.push([r, g, b, 255]);
        }
    }

    colormap
}

/// Returns a vector of paths based on iso values of the distances vector function
pub fn iso_distances(
    manifold: &Manifold,
    distances: &DVector<f64>,
    tolerance: f64,
) -> Vec<(f64, Path)> {
    let mut paths = Vec::new();

    let min_dist = distances.min();
    let max_dist = distances.max();
    let iters = ((max_dist - min_dist) / (2.0 * tolerance)).ceil() as usize;

    let mut grouped_indices: Vec<(f64, Vec<usize>)> = Vec::new();
    for index in 0..iters {
        grouped_indices.push((index as f64 * 2.0 * tolerance, Vec::new()));
    }

    for (index, &value) in distances.iter().enumerate() {
        let group_index = ((value - min_dist) / (2.0 * tolerance)).floor() as usize;
        grouped_indices[group_index].1.push(index);
    }

    for (dist, indices) in grouped_indices {
        match indices[..] {
            [] => continue,
            _ => {
                paths.push((
                    dist,
                    indices
                        .iter()
                        .map(|&index| manifold.vertices()[index].clone())
                        .collect(),
                ));
            }
        }
    }

    paths
}

impl Viewer {
    pub fn plot_curves(&mut self, paths: Vec<(f64, Path)>) {
        let min_dist = paths
            .iter()
            .cloned()
            .fold(f64::INFINITY, |acc, (v, _)| f64::min(v, acc));
        let max_dist = paths
            .iter()
            .cloned()
            .fold(f64::NEG_INFINITY, |acc, (v, __)| f64::max(acc, v));

        for (dist, path) in paths.iter() {
            let mut plot = path.clone();
            plot.push(path[0].clone());

            let t = (dist - min_dist) / (max_dist - min_dist);
            dbg!(plot.len(), t);
            let r = (COLOR_START[0] + t * (COLOR_END[0] - COLOR_START[0])) as f32;
            let g = (COLOR_START[1] + t * (COLOR_END[1] - COLOR_START[1])) as f32;
            let b = (COLOR_START[2] + t * (COLOR_END[2] - COLOR_START[2])) as f32;

            let color = Some(Point3::from_slice(&[r, g, b]));
            dbg!(color);

            self.draw_path(&plot, Some(1.0), color);
        }
    }
}
