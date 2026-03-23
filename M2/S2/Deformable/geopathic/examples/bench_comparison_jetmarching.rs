use geopathic::fastmarching::*;
use geopathic::jetmarching::{
    InterpolantRepresentation, JetMarching, MinimizationProblemMethod, SlownessModel,
    StencilUpdateMethod,
};
use geopathic::loader::load_manifold;
use geopathic::manifold::Manifold;
use geopathic::sources::Sources;
use indicatif::{MultiProgress, ProgressBar, ProgressStyle};
use nalgebra::DVector;
use rand::Rng;
use std::fs::File;
use std::io::Write;
use std::sync::Arc;
use std::time::Duration;

const RESTARTS: usize = 10;

const ELL1_THRESHOLDS: &[f64] = &[0.5, 2.0];

// ─── Colour helpers (ANSI) ───────────────────────────────────────────────────
const BOLD: &str = "\x1b[1m";
const DIM: &str = "\x1b[2m";
const CYAN: &str = "\x1b[36m";
const GREEN: &str = "\x1b[32m";
const YELLOW: &str = "\x1b[33m";
const MAGENTA: &str = "\x1b[35m";
const RESET: &str = "\x1b[0m";

fn c(colour: &str, text: &str) -> String {
    format!("{colour}{text}{RESET}")
}

// ─── Slowness field ──────────────────────────────────────────────────────────

#[derive(Clone, Copy, Debug)]
enum SlownessField {
    Constant(f64),
    LinearX,
    Radial,
    PerVertexRandom,
}

impl SlownessField {
    fn label(self) -> String {
        match self {
            Self::Constant(v) => format!("constant_{v}"),
            Self::LinearX => "linear_x".into(),
            Self::Radial => "radial".into(),
            Self::PerVertexRandom => "pervertex_random".into(),
        }
    }
    fn display(self) -> String {
        match self {
            Self::Constant(v) => format!("const({v:.1})"),
            Self::LinearX => "lin-x".into(),
            Self::Radial => "radial".into(),
            Self::PerVertexRandom => "random".into(),
        }
    }
}

// ─── Slowness model impls ────────────────────────────────────────────────────

struct ConstantSlowness(f64);
impl SlownessModel for ConstantSlowness {
    fn at_vertex(&self, _idx: usize, _m: &Manifold) -> f64 {
        self.0
    }
    fn at_point_local(
        &self,
        _p: &DVector<f64>,
        _m: &Manifold,
        _l: &[usize],
        _v: &[Vec<usize>],
    ) -> f64 {
        self.0
    }
}

struct LinearXSlowness;
impl SlownessModel for LinearXSlowness {
    fn at_vertex(&self, idx: usize, m: &Manifold) -> f64 {
        1.0 + m.vertices()[idx][0].abs()
    }
    fn at_point_local(
        &self,
        p: &DVector<f64>,
        _m: &Manifold,
        _l: &[usize],
        _v: &[Vec<usize>],
    ) -> f64 {
        1.0 + p[0].abs()
    }
}

struct RadialSlowness;
impl SlownessModel for RadialSlowness {
    fn at_vertex(&self, idx: usize, m: &Manifold) -> f64 {
        1.0 + m.vertices()[idx].norm()
    }
    fn at_point_local(
        &self,
        p: &DVector<f64>,
        _m: &Manifold,
        _l: &[usize],
        _v: &[Vec<usize>],
    ) -> f64 {
        1.0 + p.norm()
    }
}

// ─── Error metrics ───────────────────────────────────────────────────────────

fn mae(reference: &[f64], candidate: &[f64]) -> f64 {
    let (sum, count) = reference
        .iter()
        .zip(candidate)
        .filter(|(r, c)| r.is_finite() && c.is_finite())
        .fold((0.0f64, 0usize), |(s, n), (&r, &c)| {
            (s + (r - c).abs(), n + 1)
        });
    if count == 0 {
        f64::NAN
    } else {
        sum / count as f64
    }
}

fn max_abs_err(reference: &[f64], candidate: &[f64]) -> f64 {
    reference
        .iter()
        .zip(candidate)
        .filter(|(r, c)| r.is_finite() && c.is_finite())
        .map(|(&r, &c)| (r - c).abs())
        .fold(f64::NEG_INFINITY, f64::max)
}

fn dist_max(d: &[f64]) -> f64 {
    d.iter()
        .copied()
        .filter(|v| v.is_finite())
        .fold(f64::NEG_INFINITY, f64::max)
}

// ─── Parameter sets ──────────────────────────────────────────────────────────

#[derive(Debug, Clone, Copy)]
struct ParamSet {
    stencil: StencilUpdateMethod,
    minimization: MinimizationProblemMethod,
    interpolant: InterpolantRepresentation,
}

impl ParamSet {
    fn stencil_label(self) -> String {
        match self.stencil {
            StencilUpdateMethod::Mesh => "Mesh".into(),
            StencilUpdateMethod::Ell1(t) => format!("Ell1({t})"),
            StencilUpdateMethod::MeshEll1(t) => format!("MeshEll1({t})"),
        }
    }
    fn minimization_label(self) -> &'static str {
        match self.minimization {
            MinimizationProblemMethod::FermatIntegral => "FermatIntegral",
            MinimizationProblemMethod::EikonalEquation => "EikonalEquation",
            MinimizationProblemMethod::CellBasedMarching => "CellBasedMarching",
            MinimizationProblemMethod::QuadraticCurve => "QuadraticCurve",
        }
    }
    fn interpolant_label(self) -> &'static str {
        match self.interpolant {
            InterpolantRepresentation::Cubic => "Cubic",
            InterpolantRepresentation::Graph => "Graph",
        }
    }
    /// Short human-readable summary for the progress bar message
    fn short(self) -> String {
        let stencil = match self.stencil {
            StencilUpdateMethod::Mesh => "Mesh".into(),
            StencilUpdateMethod::Ell1(t) => format!("ℓ₁({t:.1})"),
            StencilUpdateMethod::MeshEll1(t) => format!("M+ℓ₁({t:.1})"),
        };
        let min = match self.minimization {
            MinimizationProblemMethod::FermatIntegral => "Fermat",
            MinimizationProblemMethod::EikonalEquation => "Eikonal",
            MinimizationProblemMethod::CellBasedMarching => "Cell",
            MinimizationProblemMethod::QuadraticCurve => "Quad",
        };
        let interp = match self.interpolant {
            InterpolantRepresentation::Cubic => "Cubic",
            InterpolantRepresentation::Graph => "Graph",
        };
        format!("{stencil}/{min}/{interp}")
    }
}

fn all_param_sets() -> Vec<ParamSet> {
    let mut stencils = vec![StencilUpdateMethod::Mesh];
    for &t in ELL1_THRESHOLDS {
        stencils.push(StencilUpdateMethod::Ell1(t));
        stencils.push(StencilUpdateMethod::MeshEll1(t));
    }
    let minimizations = [
        MinimizationProblemMethod::FermatIntegral,
        MinimizationProblemMethod::EikonalEquation,
        MinimizationProblemMethod::CellBasedMarching,
        MinimizationProblemMethod::QuadraticCurve,
    ];
    let interpolants = [
        InterpolantRepresentation::Cubic,
        InterpolantRepresentation::Graph,
    ];

    let mut sets = Vec::new();
    for &stencil in &stencils {
        for &minimization in &minimizations {
            for &interpolant in &interpolants {
                sets.push(ParamSet {
                    stencil,
                    minimization,
                    interpolant,
                });
            }
        }
    }
    sets
}

// ─── JM runner ───────────────────────────────────────────────────────────────

fn run_jm(
    manifold: &Manifold,
    params: ParamSet,
    slowness: SlownessField,
    source: usize,
    rng: &mut impl Rng,
) -> Option<(Vec<f64>, Vec<f64>, Duration)> {
    macro_rules! timed {
        ($s:expr) => {{
            let tick = std::time::Instant::now();
            let res = JetMarching::new(manifold, $s)
                .with_stencil(params.stencil)
                .with_minimization(params.minimization)
                .with_interpolant(params.interpolant)
                .compute_distance(source);
            let elapsed = tick.elapsed();
            res.ok().map(|(d, a)| {
                (
                    d.iter().copied().collect::<Vec<_>>(),
                    a.iter().copied().collect::<Vec<_>>(),
                    elapsed,
                )
            })
        }};
    }
    match slowness {
        SlownessField::Constant(s) => timed!(ConstantSlowness(s)),
        SlownessField::LinearX => timed!(LinearXSlowness),
        SlownessField::Radial => timed!(RadialSlowness),
        SlownessField::PerVertexRandom => {
            let pv: Vec<f64> = (0..manifold.vertices().len())
                .map(|_| rng.random_range(0.5_f64..2.0))
                .collect();
            timed!(pv)
        }
    }
}

// ─── Formatting helpers ───────────────────────────────────────────────────────

fn fmt_duration(d: Duration) -> String {
    let s = d.as_secs();
    if s < 60 {
        return format!("{s}s");
    }
    let m = s / 60;
    let s = s % 60;
    if m < 60 {
        return format!("{m}m{s:02}s");
    }
    let h = m / 60;
    let m = m % 60;
    format!("{h}h{m:02}m{s:02}s")
}

// ─── main ─────────────────────────────────────────────────────────────────────

fn main() {
    let skipped = [
        "nonmanifold_edge.obj",
        "suzanne.obj",
        "teapot.obj",
        "cow-nonormals.obj",
        "dragon.obj",
        // "alligator.obj",
        // "screw.obj",
        // "rabbit-head.obj",
    ];
    let mut model_paths: Vec<_> = std::fs::read_dir("../examples/models/")
        .expect("Could not read models directory")
        .filter_map(|e| {
            let p = e.unwrap().path();
            if p.extension()?.to_str()? == "obj" {
                Some(p)
            } else {
                None
            }
        })
        .filter(|p| !skipped.contains(&p.file_name().unwrap().to_str().unwrap()))
        .collect();
    model_paths.sort();

    let param_sets = all_param_sets();
    let slowness_fields = [
        SlownessField::Constant(1.0),
        SlownessField::Constant(2.0),
        SlownessField::LinearX,
        SlownessField::Radial,
        SlownessField::PerVertexRandom,
    ];

    let n_models = model_paths.len();
    let n_params = param_sets.len();
    let n_slow = slowness_fields.len();
    let total_jm = n_params * n_slow * n_models * RESTARTS;

    // ── Banner ──────────────────────────────────────────────────────────────
    println!();
    println!(
        "{}",
        c(BOLD, "╔══════════════════════════════════════════════════╗")
    );
    println!(
        "{}",
        c(BOLD, "║      Geopathic Jet-Marching Benchmark Suite      ║")
    );
    println!(
        "{}",
        c(BOLD, "╚══════════════════════════════════════════════════╝")
    );
    println!();
    println!(
        "  {}  {} param combos",
        c(CYAN, "⬡"),
        c(BOLD, &n_params.to_string())
    );
    println!(
        "  {}  {} slowness fields",
        c(CYAN, "⬡"),
        c(BOLD, &n_slow.to_string())
    );
    println!(
        "  {}  {} models",
        c(CYAN, "⬡"),
        c(BOLD, &n_models.to_string())
    );
    println!(
        "  {}  {} restarts each",
        c(CYAN, "⬡"),
        c(BOLD, &RESTARTS.to_string())
    );
    println!(
        "  {}  {} total JM runs",
        c(YELLOW, "▶"),
        c(BOLD, &total_jm.to_string())
    );
    println!();

    let mut rng = rand::rng();
    let timestamp = chrono::Local::now().format("%m:%d_%H:%M:%S").to_string();
    let mut file = File::create(format!(
        "../benchmarks/csv/comparison_benchmark_{timestamp}.csv"
    ))
    .expect("Cannot create output CSV");
    writeln!(
        file,
        "model,vertices,faces,source,stencil,minimization,interpolant,slowness,\
         time_s,dist_max,mae_vs_fm,max_err_vs_fm"
    )
    .unwrap();

    // ── Warm-up ──────────────────────────────────────────────────────────────
    {
        let wb = ProgressBar::new(5);
        wb.set_style(
            ProgressStyle::with_template(
                "  {spinner:.cyan} {msg} [{bar:30.yellow/dim}] {pos}/{len}",
            )
            .unwrap()
            .tick_chars("⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏ "),
        );
        wb.set_message(c(DIM, "Warming up JIT caches…"));
        wb.enable_steady_tick(Duration::from_millis(80));
        let m = load_manifold("../examples/models/teddy.obj").unwrap();
        for _ in 0..5 {
            let _ = FastMarching::new(&m).compute_distance(Sources::from(0));
            let ps = ParamSet {
                stencil: StencilUpdateMethod::Mesh,
                minimization: MinimizationProblemMethod::FermatIntegral,
                interpolant: InterpolantRepresentation::Cubic,
            };
            let _ = run_jm(&m, ps, SlownessField::Constant(1.0), 0, &mut rng);
            wb.inc(1);
        }
        wb.finish_with_message(format!("{} Warm-up complete.", c(GREEN, "✔")));
    }
    println!();

    // ── Multi-bar setup ───────────────────────────────────────────────────────
    let mp = Arc::new(MultiProgress::new());

    // Overall bar (one tick = one JM run)
    let overall = mp.add(ProgressBar::new(total_jm as u64));
    overall.set_style(
        ProgressStyle::with_template(
            "{spinner:.green} {msg}\n  \
             [{bar:50.cyan/blue}] {pos:>6}/{len} runs  \
             {percent:>3}%  elapsed {elapsed_precise}  ETA {eta_precise}",
        )
        .unwrap()
        .tick_chars("⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏ ")
        .progress_chars("█▉▊▋▌▍▎▏ "),
    );
    overall.enable_steady_tick(Duration::from_millis(100));

    // Model bar
    let model_bar = mp.add(ProgressBar::new(n_models as u64));
    model_bar.set_style(
        ProgressStyle::with_template(
            "  {spinner:.magenta} {msg:<44} [{bar:30.magenta/dim}] {pos}/{len} models",
        )
        .unwrap()
        .tick_chars("⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏ ")
        .progress_chars("█▉▊▋▌▍▎▏ "),
    );
    model_bar.enable_steady_tick(Duration::from_millis(120));

    // Inner (param × slowness) bar — reset per restart
    let inner_bar = mp.add(ProgressBar::new((n_params * n_slow) as u64));
    inner_bar.set_style(
        ProgressStyle::with_template(
            "    {spinner:.yellow} {msg:<44} [{bar:26.yellow/dim}] {pos}/{len}",
        )
        .unwrap()
        .tick_chars("⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏ ")
        .progress_chars("▪▫ "),
    );
    inner_bar.enable_steady_tick(Duration::from_millis(80));

    let bench_start = std::time::Instant::now();

    for (model_idx, path) in model_paths.iter().enumerate() {
        let model_name = path.file_name().unwrap().to_str().unwrap();
        let short_name = model_name.trim_end_matches(".obj");

        model_bar.set_message(format!("{}  {}", c(BOLD, short_name), c(DIM, "loading…")));
        overall.set_message(format!(
            "{} model {}/{}: {}",
            c(CYAN, "▶"),
            model_idx + 1,
            n_models,
            c(BOLD, short_name),
        ));

        let manifold = match load_manifold(path.to_str().unwrap()) {
            Ok(m) => m,
            Err(e) => {
                model_bar.println(format!(
                    "  {} {short_name}: load failed — {e:#?}",
                    c(YELLOW, "⚠")
                ));
                model_bar.inc(1);
                continue;
            }
        };
        let n_v = manifold.vertices().len();
        let n_f = manifold.faces().len();

        model_bar.set_message(format!(
            "{} {}",
            c(BOLD, short_name),
            c(DIM, &format!("({n_v}v {n_f}f)")),
        ));

        for restart in 0..RESTARTS {
            let source: usize = rng.random_range(0..n_v);

            let fm_distances: Vec<f64> = match FastMarching::new(&manifold).compute_distance(source)
            {
                Ok(d) => d.iter().copied().collect(),
                Err(e) => {
                    overall.println(format!(
                        "  {} FM error on {short_name}: {e}",
                        c(YELLOW, "⚠")
                    ));
                    continue;
                }
            };

            inner_bar.set_position(0);
            inner_bar.reset_eta();

            for &params in param_sets.iter() {
                for &slowness in &slowness_fields {
                    inner_bar.set_message(format!(
                        "{} · {}",
                        c(MAGENTA, &params.short()),
                        c(DIM, &slowness.display()),
                    ));

                    match run_jm(&manifold, params, slowness, source, &mut rng) {
                        None => {
                            overall.println(format!(
                                "  {} JM failed: {short_name} src={source} {}  {}",
                                c(YELLOW, "⚠"),
                                params.short(),
                                slowness.display(),
                            ));
                        }
                        Some((distances, _amplitudes, elapsed)) => {
                            let dmax = dist_max(&distances);
                            let mae_v = mae(&fm_distances, &distances);
                            let merr = max_abs_err(&fm_distances, &distances);
                            writeln!(
                                file,
                                "{model_name},{n_v},{n_f},{source},\
                                 {stencil},{min},{interp},{slow},\
                                 {t:.9},{dmax:.6},{mae:.6},{merr:.6}",
                                stencil = params.stencil_label(),
                                min = params.minimization_label(),
                                interp = params.interpolant_label(),
                                slow = slowness.label(),
                                t = elapsed.as_secs_f64(),
                                dmax = dmax,
                                mae = mae_v,
                                merr = merr,
                            )
                            .unwrap();
                        }
                    }

                    inner_bar.inc(1);
                    overall.inc(1);
                }
            }

            // Status line after each restart
            let elapsed_total = bench_start.elapsed();
            let done = overall.position() as f64;
            let rate = done / elapsed_total.as_secs_f64();
            let remaining_runs = total_jm as f64 - done;
            let eta_secs = if rate > 0.0 {
                Duration::from_secs_f64(remaining_runs / rate)
            } else {
                Duration::MAX
            };
            overall.set_message(format!(
                "{} {short_name} restart {}/{RESTARTS}  {}  ETA {}",
                c(CYAN, "▶"),
                restart + 1,
                c(DIM, &format!("{:.1} runs/s", rate)),
                c(YELLOW, &fmt_duration(eta_secs)),
            ));
        }

        model_bar.inc(1);
        overall.println(format!(
            "  {} {}{} — {} verts, {} faces",
            c(GREEN, "✔"),
            c(BOLD, short_name),
            c(DIM, ".obj"),
            n_v,
            n_f,
        ));
    }

    inner_bar.finish_and_clear();
    model_bar.finish_with_message(format!("{} All models complete.", c(GREEN, "✔")));
    overall.finish_with_message(format!(
        "{} Benchmark finished in {}.",
        c(GREEN, "✔"),
        c(BOLD, &fmt_duration(bench_start.elapsed())),
    ));

    println!();
    println!(
        "{}",
        c(
            GREEN,
            "╔══════════════════════════════════════════════════╗"
        )
    );
    println!(
        "{}",
        c(
            GREEN,
            &format!("║  Results → benchmarks/csv/comparison_benchmark_{timestamp}.csv  ║")
        )
    );
    println!(
        "{}",
        c(
            GREEN,
            "╚══════════════════════════════════════════════════╝"
        )
    );
    println!();
}
