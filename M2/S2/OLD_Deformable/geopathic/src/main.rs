use std::io::Write;

use geopathic::colormaps::{distance_colormap, iso_distances};
use geopathic::edp::{EDPMethod, Poiffon, SpectralPDE};
use geopathic::fastmarching::FastMarching;
use geopathic::ich::ICH;
use geopathic::loader::load_manifold;
use geopathic::mesh::Mesh;
use geopathic::viewer::Viewer;
use kiss3d::camera::ArcBall;
use nalgebra::{DVector, Point3};

fn main() {
    // heat_method();
    // fast_marching();
    // spectral_method();
    poiffon_method();
    // ich();
}

#[allow(dead_code)]
fn heat_method() {
    let manifold = load_manifold("../examples/models/teddy.obj").unwrap();
    let heat_method = EDPMethod::new(&manifold);

    let sources = [0, 431];
    let distances = match heat_method.compute_distance_heat(sources) {
        Ok(it) => it,
        Err(err) => panic!("{}", err),
    };
    let colormap = distance_colormap(&manifold, &distances, false);

    let mut viewer = Viewer::new();
    viewer.add_manifold(&manifold, Some(colormap));
    viewer.plot_curves(iso_distances(&manifold, &distances, 1e-6));

    for s in sources {
        viewer.draw_point(
            manifold.vertices()[s].clone(),
            Some(10.0),
            Some(Point3::from_slice(&[0.0, 0.0, 1.0])),
        );
    }

    viewer.camera = ArcBall::new(Point3::new(0.0, 10.0, 65.0), Point3::new(0.0, 0.0, 0.0));
    viewer.render(true);
}

#[allow(dead_code)]
fn fast_marching() {
    let manifold = load_manifold("../examples/models/screw.obj").unwrap();
    let fastmarching = FastMarching::new(&manifold);
    let sources = [0, 256];
    let distances = match fastmarching.compute_distance(sources) {
        Ok(it) => it,
        Err(err) => panic!("{}", err),
    };
    let colormap = None; // Some(distance_colormap(&manifold, &distances));

    let mut viewer = Viewer::new();
    viewer.add_manifold(&manifold, colormap);
    viewer.plot_curves(iso_distances(&manifold, &distances, 1.0));

    viewer.plot_sources(&manifold, sources, None, None);
    viewer.render(true);
}

#[allow(dead_code)]
fn spectral_method() {
    let manifold = load_manifold("../examples/models/teddy.obj").unwrap();
    let edpmethod = EDPMethod::new(&manifold);

    let sources = [0, 431];
    let spectral_methods = [
        SpectralPDE::Eigenmap,    // lambda
        SpectralPDE::CommuteTime, // 1/lambda
        SpectralPDE::Biharmonic,  // 1/lambda**2
        SpectralPDE::Diffusion,   // exp(-2lambda)
    ];

    let spectral_distances = Vec::from_iter(spectral_methods.iter().map(|spectral_method| {
        let distances = match edpmethod.compute_distance_spectral(sources, *spectral_method, 7) {
            Ok(it) => it,
            Err(err) => panic!("{}", err),
        };
        let colormap = distance_colormap(&manifold, &distances, false);

        (distances, colormap)
    }));

    let mut viewer = Viewer::new();
    for s in sources {
        viewer.draw_point(
            manifold.vertices()[s].clone(),
            Some(10.0),
            Some(Point3::from_slice(&[0.0, 0.0, 1.0])),
        );
    }

    let (distances, colormap) = spectral_distances[0].clone();
    viewer.add_manifold(&manifold, Some(colormap));
    viewer.plot_curves(iso_distances(&manifold, &distances, 1e-6));

    viewer.camera = ArcBall::new(Point3::new(0.0, 10.0, 65.0), Point3::new(0.0, 0.0, 0.0));
    viewer.render(true);
}

#[allow(dead_code)]
fn poiffon_method() {
    let manifold = load_manifold("../examples/models/teddy.obj").unwrap();
    let edpmethod = EDPMethod::new(&manifold);

    let sources = [0, 431];
    let poiffon_methods = [
        // Poiffon::ScreenedPoiffon(1.0, true),
        // Poiffon::ScreenedPoiffon(3.0, false),
        Poiffon::ScreenedPoiffon(34530.4, true), // rho value for universal gravitation potential
                                                 // Poiffon::BorderPoiffon(true),
    ];

    let poiffon_distances = Vec::from_iter(poiffon_methods.iter().map(|poiffon_method| {
        let distances = match edpmethod.compute_distance_poisson(sources, *poiffon_method) {
            Ok(it) => it,
            Err(err) => panic!("{}", err),
        };
        let colormap = distance_colormap(&manifold, &distances, false);

        (distances, colormap)
    }));

    let mut viewer = Viewer::new();
    for s in sources {
        viewer.draw_point(
            manifold.vertices()[s].clone(),
            Some(10.0),
            Some(Point3::from_slice(&[0.0, 0.0, 1.0])),
        );
    }

    let (distances, colormap) = poiffon_distances[0].clone();
    viewer.add_manifold(&manifold, Some(colormap));
    viewer.plot_curves(iso_distances(&manifold, &distances, 1e-6));

    viewer.camera = ArcBall::new(Point3::new(0.0, 10.0, 65.0), Point3::new(0.0, 0.0, 0.0));
    viewer.render(true);
}

#[allow(dead_code)]
fn ich() {
    let manifold = load_manifold("../examples/models/star.obj").unwrap();
    print!("Converting to mesh...");
    std::io::stdout().flush().unwrap();
    let mesh = Mesh::from_manifold(&manifold);
    mesh.check_topology().unwrap();
    println!("done.");

    print!("Running ICH...");
    std::io::stdout().flush().unwrap();
    let mut ich = ICH::new(mesh, vec![0], vec![], vec![]);
    ich.run();
    println!("done.");
    ich.print_stats();

    let distances = ich.distances_to_vertices();
    let colormap = distance_colormap(&manifold, &DVector::from_vec(distances.clone()), true);

    let mut viewer = Viewer::new();
    viewer.white_background();
    viewer.add_manifold(&manifold, Some(colormap));

    #[allow(clippy::needless_range_loop)]
    for dest in 1..manifold.vertices().len() {
        if distances[dest].is_infinite() {
            continue;
        }
        let path: Vec<DVector<f64>> = ich
            .path_to_vertex(dest)
            .iter()
            .map(|p| DVector::from_vec(vec![p.x, p.y, p.z]))
            .collect();
        viewer.draw_path(&path, Some(20.0), None);
    }

    println!("Rendering...");
    viewer.render(false);
}
