use geopathic::ich::*;
use geopathic::loader::load_manifold;
use geopathic::mesh::Mesh;
use rand::Rng;
use std::fs::File;
use std::io::Write;

const RESTARTS: usize = 10;

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
        "fantasy-piece.obj",
        "ferrari.obj",
    ];
    let model_paths: Vec<_> = model_paths
        .into_iter()
        .filter(|path| !skipped.contains(&path.file_name().unwrap().to_str().unwrap()))
        .collect();

    let mut rng = rand::rng();
    let timestamp = chrono::Local::now().format("%m:%d_%H:%M:%S").to_string();
    let mut file = File::create(format!("../benchmarks/csv/ich_benchmark_{}.csv", timestamp)).unwrap();
    writeln!(
        file,
        "model,vertices,faces,source,time,windows_created,windows_propagated"
    )
    .unwrap();

    // warmup run
    println!("Warming up...\n");
    for _ in 0..10 {
        let manifold = load_manifold("../examples/models/teddy.obj").unwrap();
        let mesh = Mesh::from_manifold(&manifold);
        let source = 0;
        let mut ich = ICH::new(mesh, vec![source], vec![], vec![]);
        ich.run();
    }

    for path in model_paths {
        print!("Benchmarking {:?}", path.file_name().unwrap());
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
        let mesh = Mesh::from_manifold(&manifold);
        if mesh.check_topology().is_err() {
            println!(
                "skipping {:?} due to topology check failure.",
                path.file_name().unwrap()
            );
            continue;
        }

        for _ in 0..RESTARTS {
            // pick a random source
            let source = rng.random_range(0..manifold.vertices().len());
            let mesh = mesh.clone();

            // run ICH
            let tick = std::time::Instant::now();
            let mut ich = ICH::new(mesh, vec![source], vec![], vec![]);
            ich.run();
            let time_elapsed = tick.elapsed();
            let stats = ich.stats;

            // log the results to csv
            writeln!(
                file,
                "{},{},{},{},{},{},{}",
                path.file_name().unwrap().to_str().unwrap(),
                manifold.vertices().len(),
                manifold.faces().len(),
                source,
                time_elapsed.as_secs_f64(),
                stats.windows_created,
                stats.windows_propagated,
            )
            .unwrap();
            print!(".");
            std::io::stdout().flush().unwrap();
        }
        println!("done.");
    }
}
