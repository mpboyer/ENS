// Imagine++ project
// Project: GraphCutsDisparity
// Author:  Renaud Marlet/Pascal Monasse
// Student: Matthieu Boyer

#include <Imagine/Images.h>
#include <iostream>
#include <iomanip>
#include <algorithm>
#include <string>
#include "maxflow/graph.h"
#include <chrono>
#include <stdexcept>
using namespace Imagine;
using namespace std;

typedef Image<octet> byteImage;
typedef Image<double> doubleImage;

// Default data
const string DEF_im1=srcPath("face0.png"), DEF_im2=srcPath("face1.png");
static int dmin=10, dmax=55; // Min and max disparities

// Parameters of the algorithm
// OPTIMIZATION: to make the program faster, a zoom factor is used to
// down-sample the input images on the fly. You will
// only look at pixels (win+zoom*i,win+zoom*j) with win the radius of patch.
//
// I removed the const keyword for testing of different parameter values
int win = (7-1)/2;  // Correlation patches of size (2n+1)*(2n+1)
float lambdaf = 0.1; // Weight of regularization (smoothing) term
int zoom = 2;     // Zoom factor (to speedup computations)
float sigma = 6/zoom; // Gaussian blur parameter for disparity
// Energy discretization precision (as we build a graph with 'int' weights)
int wcc = std::max(1+int(1/lambdaf),20);
int lambda = lambdaf*wcc; // Regularization term (must be >= 1)

Image<Color> displayDisp(const Image<int>& disp) {
  Image<Color> im(disp.width(), disp.height());
  for(int j=0; j<disp.height(); j++)
    for(int i=0; i<disp.width(); i++) {
      if(disp(i,j)<dmin || disp(i,j)>dmax)
        im(i,j) = CYAN;
      else {
        int g = 255*(disp(i,j)-dmin)/(dmax-dmin);
        im(i,j)= Color(g,g,g);
      }
    }
  return im;
}

#ifdef IMAGINE_OPENGL
void doc() {
  cout << "***** 3D mesh renderings *****" << endl;
  cout << "- Button 1: toggle textured or gray rendering" << endl;
  cout << "- SHIFT+Button 1: rotate" << endl;
  cout << "- SHIFT+Button 3: translate" << endl;
  cout << "- Mouse wheel: zoom" << endl;
  cout << "- SHIFT+a: zoom out" << endl;
  cout << "- SHIFT+z: zoom in" << endl;
  cout << "- SHIFT+r: recenter camera" << endl;
  cout << "- SHIFT+m: toggle solid/wire/points mode" << endl;
  cout << "- Button 3: exit" << endl;
}

// Display 3D mesh renderings
void control3D(const Mesh& Mt, const Mesh& Mg) {
  setActiveWindow( openWindow3D(512, 512, "3D") );
  showMesh(Mt);
  bool textured = true;
  while (true) {
    Event evt;
    getEvent(5, evt);
    // On mouse button 1
    if (evt.type == EVT_BUT_ON && evt.button == 1) {
      // Toggle textured rendering and gray rendering
      if (textured) {
        hideMesh(Mt,false);
        showMesh(Mg,false);
      } else {
        hideMesh(Mg,false);
        showMesh(Mt,false);
      }
      textured = !textured;
    }
    // On mouse button 3
    if (evt.type == EVT_BUT_ON && evt.button == 3)
      break;
  }
}
#endif

void show3D(const byteImage& I, const doubleImage& D, int zoom) {
#ifdef IMAGINE_OPENGL
  cout << "Click to compute depth map and 3D mesh renderings... " << flush;
  click();

  // Compute 3D point cloud: magic constants depending on camera pose
  const float f = 750; // Focal
  const float d0 = 100; // Disparity for infinite depth (due to crop)
  const float B = -0.20;// Baseline

  const int nx=D.width(), ny=D.height();
  FMatrix<float,3,3> K(0.0f);
  K(0,0)= -f/zoom; K(0,2)=nx/2;
  K(1,1)= f/zoom; K(1,2)=ny/2;
  K(2,2)=1.0f;
  K = inverse(K);
  K /= K(2,2);
  Array<FloatPoint3> p(nx*ny);
  Array<Color> pcol(nx*ny);
  for(int j=0; j<ny; j++)
    for(int i=0; i<nx; i++) {
      float z = f*B/(d0+D(i,j));
      FloatPoint3 pt((float)i,(float)j,1.0f);
      p[i+nx*j] = K*pt*z;
      pcol[i+nx*j] = Color(I(i*zoom,j*zoom));
    }
  // Create mesh from 3D point cloud
  Array<Triangle> t(2*(nx-1)*(ny-1));
  Array<Color> tcol(2*(nx-1)*(ny-1));
  for(int j=0; j+1<ny; j++)
    for(int i=0; i+1<nx; i++) {
      // Create triangles with next pixels in line/column
      t[2*(i+j*(nx-1))]  = Triangle(i+nx*j,  i+1+nx*j,   i+nx*(j+1));
      t[2*(i+j*(nx-1))+1] = Triangle(i+1+nx*j, i+1+nx*(j+1), i+nx*(j+1));
      tcol[2*(i+j*(nx-1))]  = pcol[i+nx*j];
      tcol[2*(i+j*(nx-1))+1] = pcol[i+nx*j];
    }
  // Mesh with texture from original image
  Mesh Mt(p.data(), nx*ny, t.data(), 2*(nx-1)*(ny-1), 0, 0, FACE_COLOR);
  Mt.setColors(TRIANGLE, tcol.data());
  // Mesh with artificial light
  Mesh Mg(p.data(), nx*ny, t.data(), 2*(nx-1)*(ny-1), 0, 0,
      CONSTANT_COLOR, SMOOTH_SHADING);
  cout << "done" << endl;

  doc();
  control3D(Mt, Mg);
#else
  cout << "No 3D: Imagine++ not built with OpenGL support" << endl;
#endif
}

// Return image of mean intensity value over (2win+1)x(2win+1) patch
doubleImage meanImage(const byteImage& I) {
  int w = I.width(), h = I.height();
  doubleImage IM(w,h);
  double area = (2*win+1)*(2*win+1);
  for(int j=0; j<h; j++)
    for(int i=0; i<w; i++) {
      if (j-win<0 || j+win>=h || i-win<0 ||i+win>=w) {
        IM(i,j)=0;
        continue;
      }
      double sum = 0;
      for(int y=-win; y<=win; y++)
        for(int x=-win; x<=win; x++)
          sum += I(x+i,y+j);
      IM(i,j) = sum / area;
    }
  return IM;
}

// Compute correlation between two pixels in images 1 and 2
double correl(const byteImage& I1,  // Image 1
       const doubleImage& I1M, // Image of mean value over patch
       const byteImage& I2,  // Image2
       const doubleImage& I2M, // Image of mean value over patch
       int u1, int v1,     // Pixel of interest in image 1
       int u2, int v2) {    // Pixel of interest in image 2
  double c=0;
  for(int y=-win; y<=win; y++)
    for(int x=-win; x<=win; x++)
      c += (I1(u1+x,v1+y)-I1M(u1,v1)) * (I2(u2+x,v2+y)-I2M(u2,v2));
  return c / ((2*win+1)*(2*win+1));
}

// Compute ZNCC between two patches in images 1 and 2
double zncc(const byteImage& I1,  // Image 1
      const doubleImage& I1M, // Image of mean intensity value over patch
      const byteImage& I2,  // Image2
      const doubleImage& I2M, // Image of mean intensity value over patch
      int u1, int v1,     // Pixel of interest in image 1
      int u2, int v2) {    // Pixel of interest in image 2
  double var1 = correl(I1, I1M, I1, I1M, u1, v1, u1, v1);
  if(var1 == 0)
    return 0;
  double var2 = correl(I2, I2M, I2, I2M, u2, v2, u2, v2);
  if(var2 == 0)
    return 0;
  return correl(I1, I1M, I2, I2M, u1, v1, u2, v2) / sqrt(var1 * var2);
}

/// Create graph
/// The graph library works with node numbers. To clarify the setting, create
/// a formula to associate a unique node number to a triplet (x,y,d) of pixel
/// coordinates and disparity.
/// The library assumes an edge consists of a pair of oriented edges, one in
/// each direction. Put correct weights to the edges, such as 0, INF, or
/// an intermediate weight.
void build_graph(Graph<int,int,int>& G,
         const byteImage& I1, const byteImage& I2,
         int nx, int ny, int nd) {
  const int INF=1000000; // "Infinite" value for edge impossible to cut
  // Precompute images of mean intensity value over patch
  doubleImage I1M = meanImage(I1), I2M = meanImage(I2);

  // Number of nodes in total
  const int nbNodes = nx * ny * nd;

  // Helper to map grid coordinates (ix, iy, d) → node index
  auto nodeIndex = [&](int ix, int iy, int d) {
    if (ix < 0 || iy < 0 || ix >= nx || iy >= ny || d < dmin || d > dmax)
      return -1; // invalid
    return (iy * nx + ix) * nd + (d - dmin);
  };

  // Allocate all nodes
  G.add_node(nbNodes);

  // Build unary data terms (ZNCC-based)
  for (int iy = 0; iy < ny; iy++) {
    for (int ix = 0; ix < nx; ix++) {
      // Actual image coordinates, accounting for zoom and patch margin
      int y = win + iy * zoom;
      int x = win + ix * zoom;

      for (int d = dmin; d <= dmax; d++) {
        int n = nodeIndex(ix, iy, d);
        if (n < 0 || n >= nbNodes)
          continue;

        int xr = x - d;

        // Check that patch fits inside both images
        if (xr - win < 0 || xr + win >= I2.width() ||
          x - win < 0 || x + win >= I1.width() ||
          y - win < 0 || y + win >= I1.height()) {
          G.add_tweights(n, 0, INF); // invalid match
          continue;
        }

        double ncc = zncc(I1, I1M, I2, I2M, x, y, xr, y);
        int costData = (int)(wcc * (1.0 - ncc)); // in [0, wcc]

        if (d == dmin)
          G.add_tweights(n, costData, INF);
        else if (d == dmax)
          G.add_tweights(n, INF, costData);
        else
          G.add_tweights(n, costData, costData);

        // Edge linking consecutive disparities (vertical in disparity column)
        if (d < dmax) {
          int n2 = nodeIndex(ix, iy, d + 1);
          if (n2 >= 0 && n2 < nbNodes)
            G.add_edge(n, n2, lambda, lambda);
        }
      }
    }
  }

  // Spatial smoothness edges (4-neighborhood)
  for (int iy = 0; iy < ny; iy++) {
    for (int ix = 0; ix < nx; ix++) {
      for (int d = dmin; d <= dmax; d++) {
        int n = nodeIndex(ix, iy, d);
        if (n < 0 || n >= nbNodes)
          continue;

        // Right neighbor
        int nx_ = nodeIndex(ix + 1, iy, d);
        if (nx_ >= 0 && nx_ < nbNodes)
          G.add_edge(n, nx_, lambda, lambda);

        // Bottom neighbor
        int ny_ = nodeIndex(ix, iy + 1, d);
        if (ny_ >= 0 && ny_ < nbNodes)
          G.add_edge(n, ny_, lambda, lambda);
      }
    }
  }

 // Compute maxflow / mincut
 // int flow = G.maxflow();
 // std::cout << "Maxflow = " << flow << std::endl;
}

/// Extract disparity from minimum cut.
/// w2 is the width of image2, used to detect pixels with no valid patch.
doubleImage decode_graph(Graph<int,int,int>& G, int nx, int ny, int nd, int w2){
 doubleImage D(nx,ny);

 auto nodeIndex = [&](int x, int y, int d) {
  return (y * nx + x) * nd + (d - dmin);
 };

 // Compute disparity for each pixel from cut
 for (int y = 0; y < ny; y++) {
  for (int x = 0; x < nx; x++) {
   int bestD = dmin;
   for (int d = dmin; d <= dmax; d++) {
    int n = nodeIndex(x, y, d);
    if (G.what_segment(n) == Graph<int,int,int>::SOURCE)
      bestD = d;
   }

   // If the corresponding pixel in image2 is invalid, mark disparity 0
   if (x - bestD < 0 || x - bestD >= w2)
    D(x, y) = 0;
   else
    D(x, y) = bestD;
  }
}
  return D;
}

// Simple region growing disparity estimation for comparison
doubleImage region_growing_disparity(const byteImage& I1, const byteImage& I2,
                   int nx, int ny) {
  doubleImage D(nx, ny);
  doubleImage I1M = meanImage(I1), I2M = meanImage(I2);

  // Initialize with best ZNCC match per pixel (no smoothing)
  for (int iy = 0; iy < ny; iy++) {
    for (int ix = 0; ix < nx; ix++) {
      int y = win + iy * zoom;
      int x = win + ix * zoom;

      double bestScore = -2.0;
      int bestDisp = dmin;

      for (int d = dmin; d <= dmax; d++) {
        int xr = x - d;
        if (xr - win < 0 || xr + win >= I2.width() ||
          x - win < 0 || x + win >= I1.width() ||
          y - win < 0 || y + win >= I1.height()) {
          continue;
        }

        double score = zncc(I1, I1M, I2, I2M, x, y, xr, y);
        if (score > bestScore) {
          bestScore = score;
          bestDisp = d;
        }
      }
      D(ix, iy) = bestDisp;
    }
  }
  return D;
}

// Compute metrics for evaluation
struct DisparityMetrics {
  double mae;      // Mean Absolute Error (if ground truth available)
  double smoothness;  // Average gradient magnitude
  double validRatio;  // Ratio of valid disparities
  double computeTime;  // Computation time in seconds
};

// Compute smoothness metric (average gradient magnitude)
double compute_smoothness(const doubleImage& D) {
  double totalGrad = 0.0;
  int count = 0;

  for (int y = 0; y < D.height() - 1; y++) {
    for (int x = 0; x < D.width() - 1; x++) {
      if (D(x, y) > 0 && D(x+1, y) > 0 && D(x, y+1) > 0) {
        double gx = abs(D(x+1, y) - D(x, y));
        double gy = abs(D(x, y+1) - D(x, y));
        totalGrad += sqrt(gx*gx + gy*gy);
        count++;
      }
    }
  }
  return count > 0 ? totalGrad / count : 0.0;
}

// Compute valid ratio
double compute_valid_ratio(const doubleImage& D) {
  int valid = 0, total = 0;
  for (int y = 0; y < D.height(); y++) {
    for (int x = 0; x < D.width(); x++) {
      total++;
      if (D(x, y) > 0) valid++;
    }
  }
  return total > 0 ? (double)valid / total : 0.0;
}

// Compute MAE with ground truth (if available)
double compute_mae(const doubleImage& D, const doubleImage& GT) {
  if (D.width() != GT.width() || D.height() != GT.height()) {
    return -1.0; // Invalid comparison
  }

  double totalError = 0.0;
  int count = 0;

  for (int y = 0; y < D.height(); y++) {
    for (int x = 0; x < D.width(); x++) {
      if (D(x, y) > 0 && GT(x, y) > 0) {
        totalError += abs(D(x, y) - GT(x, y));
        count++;
      }
    }
  }
  return count > 0 ? totalError / count : -1.0;
}

// Run comprehensive tests
void run_tests(const byteImage& I1, const byteImage& I2,
               const vector<float>& lambda_values,
               const vector<int>& window_sizes) {

    int w1=I1.width(), h=I1.height();

    ofstream tableFile("disparity_tables.tex");
    if (!tableFile.is_open()) {
        cerr << "Error: Could not open output file" << endl;
        return;
    }
    
    ofstream analysisFile("disparity_analysis.tex");
    if (!analysisFile.is_open()) {
        cerr << "Error: Could not open output file" << endl;
        return;
    }


    int nd = dmax - dmin;

    // Start main table
    tableFile << "\\begin{table*}[h]\n\\centering\n";
    tableFile << "\\caption{Comparison of disparity estimation methods. "
            << "Smoothness is measured as average gradient magnitude (lower is smoother). "
            << "MAE shows mean absolute error between Graph Cuts and Region Growing results.}\n";
    tableFile << "\\label{tab:disparity_results}\n\n\\hline";

    for (float lambda_value : lambda_values) {
        for (int win_value : window_sizes) {

            // Update parameters
            lambdaf = lambda_value;
            win = win_value;
            wcc = std::max(1 + int(1 / lambdaf), 20);
            lambda = lambdaf * wcc;

            int nx = (w1 - 2 * win) / zoom;
            int ny = (h - 2 * win) / zoom;

            cout << "→ Running λ=" << lambdaf
                 << ", win=" << win << endl;

            // Begin subtable
            tableFile << "\\begin{subtable}{0.4\\textwidth}\n";
            tableFile << "\\centering\n";
            tableFile << "\\begin{tabular}{lcccc}\n\\hline\n";
            tableFile << "Method & Time (s) & Smooth. & Valid & MAE \\\\\n\\hline\n";

            // Graph Cuts
            auto startGC = chrono::high_resolution_clock::now();
            Graph<int,int,int> G(nx*ny*nd, 2*nx*ny*nd);
            build_graph(G, I1, I2, nx, ny, nd);
            G.maxflow();
            doubleImage D_gc = decode_graph(G, nx, ny, nd, I2.width());
            auto endGC = chrono::high_resolution_clock::now();
            double timeGC = chrono::duration<double>(endGC - startGC).count();
            double smoothGC = compute_smoothness(D_gc);
            double validGC  = compute_valid_ratio(D_gc);

            // Region Growing
            auto startRG = chrono::high_resolution_clock::now();
            doubleImage D_rg = region_growing_disparity(I1, I2, nx, ny);
            auto endRG = chrono::high_resolution_clock::now();
            double timeRG = chrono::duration<double>(endRG - startRG).count();
            double smoothRG = compute_smoothness(D_rg);
            double validRG  = compute_valid_ratio(D_rg);

            // Cross-method MAE
            double mae = compute_mae(D_gc, D_rg);

            // Write rows
            tableFile << "GC & " << fixed << setprecision(3)
                    << timeGC << " & " << smoothGC << " & " << validGC << " & -- \\\\\n";
            tableFile << "RG & " << fixed << setprecision(3)
                    << timeRG << " & " << smoothRG << " & " << validRG << " & "
                    << mae << " \\\\\n\\hline\n";
            tableFile << "\\end{tabular}\n\\\\\n";
            // Subtable caption
            tableFile << "\\caption{$\\lambda = " << lambdaf
                    << "$, window radius = " << win
                    << " (patch " << 2*win+1 << "×" << 2*win+1 << ")}\n";

            tableFile << "\\end{subtable}\\hline\n";

            analysisFile << "\\item Pour: $\\lambda = " << lambdaf
                    << "$, window radius = " << win
                    << " (patch " << 2*win+1 << "×" << 2*win+1 << "):\n";

            analysisFile << "\\begin{itemize}\n";
            analysisFile << "\\item \\textbf{Temps de calcul:} ";
            if (timeGC < timeRG) {
              analysisFile << "Graph Cuts est " << fixed << setprecision(2)
                      << (timeRG/timeGC) << "$\\times$ plus rapide que Region Growing.\n";
            } else {
              analysisFile << "Region Growing is " << fixed << setprecision(2)
                      << (timeGC/timeRG) << "$\\times$ plus rapide Graph Cuts.\n";
            }

            analysisFile << "\\item \\textbf{Caractère lisse:} ";
            if (smoothGC < smoothRG) {
              analysisFile << "Graph Cuts produit des cartes " << fixed << setprecision(1)
                      << ((smoothRG - smoothGC) / smoothRG * 100)
                      << "\\% plus lisses.\n";
            } else {
              analysisFile << "Region Growing produit des cartes plus lisses dans ce cas.\n";
            }

            analysisFile << "\\item \\textbf{Précision:} ";
            analysisFile << "Graph Cuts atteint " << fixed << setprecision(1) << (validGC*100)
                    << "\\% de disparités valides, tandis que Region Growing atteint"
                    << fixed << setprecision(1) << (validRG*100) << "\\%.\n";
            analysisFile << "\\end{itemize}\n";
        }
    }

    // End main table
    tableFile << "\\end{table*}\n";
    tableFile.close();
}


// Load two rectified images.
// Compute the disparity of image 2 w.r.t. image 1.
// Display disparity map.
// Display 3D mesh of corresponding depth map.
int main(int argc, char* argv[]) {
  string im1 = DEF_im1, im2 = DEF_im2;

  // Valid invocations:
  //   ./binary                -> defaults
  //   ./binary im1 im2 dmin dmax
  //   ./binary test
  if (argc == 1) {
    // defaults already set
  } else if (argc == 2 && string(argv[1]) == "test") {
    // test mode; we'll load images using defaults below
  } else if (argc == 5) {
    im1 = argv[1];
    im2 = argv[2];
    dmin = stoi(argv[3]);
    dmax = stoi(argv[4]);
  } else {
    cerr << "Usage:\n"
         << "  " << argv[0] << "               # Normal mode using defaults\n"
         << "  " << argv[0] << " im1 im2 dmin dmax  # Normal mode with parameters\n"
         << "  " << argv[0] << " test          # Run evaluation tests\n";
    return 1;
  }

  cout << "Loading images... " << flush;
  byteImage I1, I2;
  if (!load(I1, im1) || !load(I2, im2)) {
    cerr << "Error loading image files" << endl;
    return 1;
  }
  cout << "done" << endl;

  // If test mode requested
  if (argc == 2 && string(argv[1]) == "test") {
    cout << "\n========================================" << endl;
    cout << "Running Comparative Evaluation " << endl;
    cout << "========================================\n" << endl;

    std::vector<float> lambda_values = {0.05f, 0.1f, 0.2f, 0.5f};
    std::vector<int> window_sizes = {1, 2, 3, 4}; // radii -> patch sizes 3x3..9x9

    run_tests(I1, I2, lambda_values, window_sizes);

    cout << "\n==================================================" << endl;
    cout << "Analysis results written to: disparity_results.tex" << endl;
    cout << "==================================================\n" << endl;

    return 0;
  }

  // Normal GUI workflow
  int w1 = I1.width(), w2 = I2.width(), h = I1.height();
  cout << "Parameters: " << "d=" << dmin << "..." << dmax
       << ", win=" << win << ", lambda=" << lambdaf << ", sigma=" << sigma
       << ", zoom=" << zoom << endl;

  cout << "Displaying images... " << flush;
  openWindow(w1 + w2, h);
  display(I1); display(I2, w1, 0);
  cout << "done" << endl;

  // Zoomed image dim, disregarding borders (strips of width the patch radius)
  const int nx = (w1 - 2*win) / zoom;
  const int ny = (h - 2*win) / zoom;
  const int nd = dmax - dmin; // Disparity range

  if (nx <= 0 || ny <= 0 || nd <= 0) {
    cerr << "Invalid nx/ny/nd computed. Aborting.\n";
    return 1;
  }

  cout << "Constructing graph (be patient)... " << flush;
  Graph<int,int,int> G(nx*ny*nd, 2*nx*ny*nd);
  build_graph(G, I1, I2, nx, ny, nd);
  cout << "done" << endl;

  cout << "Computing minimum cut... " << flush;
  int f = G.maxflow();
  cout << "done" << endl << " max flow = " << f << endl;

  cout << "Extracting disparity map from minimum cut... " << flush;
  doubleImage D = decode_graph(G, nx, ny, nd, I2.width());
  cout << "done" << endl;

  cout << "Displaying disparity map... " << flush;
  fillRect(0,0,w1,h,CYAN);
  display(enlarge(displayDisp(D),zoom),win,win);
  cout << "done" << endl;
  cout << "Click to compute and display blurred disparity map... " << flush;
  click();
  D = blur(D,sigma);
  display(enlarge(displayDisp(D),zoom),win,win);
  cout << "done" << endl;

  show3D(I1.getSubImage(win,win,w1-2*win,h-2*win), D, zoom);
  endGraphics();
  return 0;
}
