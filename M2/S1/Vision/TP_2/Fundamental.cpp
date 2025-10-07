// Imagine++ project
// Project:  Fundamental
// Author:   Pascal Monasse

#include "./Imagine/Features.h"
#include <Imagine/Common.h>
#include <Imagine/Graphics.h>
#include <Imagine/LinAlg.h>
#include <cstdlib>
#include <ctime>
#include <vector>
using namespace Imagine;
using namespace std;

static const float BETA = 0.01f; // Probability of failure

struct Match {
  float x1, y1, x2, y2;
};

// Display SIFT points and fill vector of point correspondences
void algoSIFT(Image<Color, 2> I1, Image<Color, 2> I2, vector<Match> &matches) {
  // Find interest points
  SIFTDetector D;
  D.setFirstOctave(-1);
  Array<SIFTDetector::Feature> feats1 = D.run(I1);
  drawFeatures(feats1, Coords<2>(0, 0));
  cout << "Im1: " << feats1.size() << flush;
  Array<SIFTDetector::Feature> feats2 = D.run(I2);
  drawFeatures(feats2, Coords<2>(I1.width(), 0));
  cout << " Im2: " << feats2.size() << flush;

  const double MAX_DISTANCE = 100.0 * 100.0;
  for (size_t i = 0; i < feats1.size(); i++) {
    SIFTDetector::Feature f1 = feats1[i];
    for (size_t j = 0; j < feats2.size(); j++) {
      double d = squaredDist(f1.desc, feats2[j].desc);
      if (d < MAX_DISTANCE) {
        Match m;
        m.x1 = f1.pos.x();
        m.y1 = f1.pos.y();
        m.x2 = feats2[j].pos.x();
        m.y2 = feats2[j].pos.y();
        matches.push_back(m);
      }
    }
  }
}

// Auxiliary function running the 8-point algorithm to compute F from 8 matches.
// Matches are in &matches[&indices], and normalization matrices N1 and N2 are
// used.
// Auxiliary function: 8-point algorithm to compute F from 8 matches
// Returns normalized fundamental matrix
FMatrix<float, 3, 3> computeF8Points(const vector<Match> &matches,
                                     const vector<int> &indices,
                                     const FMatrix<float, 3, 3> &N1,
                                     const FMatrix<float, 3, 3> &N2) {
  // Build matrix A for 8-point algorithm with normalized coordinates
  // We use all matches (not just 8) to make it over-determined, or add a 9th
  // point
  FMatrix<float, 9, 9> A;
  A.fill(0);

  for (int i = 0; i < 8; i++) {
    float x1 = matches[indices[i]].x1;
    float y1 = matches[indices[i]].y1;
    float x2 = matches[indices[i]].x2;
    float y2 = matches[indices[i]].y2;

    // Apply normalization
    float x1n = N1(0, 0) * x1 + N1(0, 2);
    float y1n = N1(1, 1) * y1 + N1(1, 2);
    float x2n = N2(0, 0) * x2 + N2(0, 2);
    float y2n = N2(1, 1) * y2 + N2(1, 2);

    A(i, 0) = x2n * x1n;
    A(i, 1) = x2n * y1n;
    A(i, 2) = x2n;
    A(i, 3) = y2n * x1n;
    A(i, 4) = y2n * y1n;
    A(i, 5) = y2n;
    A(i, 6) = x1n;
    A(i, 7) = y1n;
    A(i, 8) = 1;
  }

  // Add a 9th equation: we can use another match or add constraint ||F|| = 1
  // Let's use a 9th random match if available, otherwise use a normalization
  // constraint
  int n = matches.size();
  if (n > 8) {
    // Find a 9th point not in indices
    int idx9 = -1;
    for (int i = 0; i < n; i++) {
      bool found = false;
      for (int j = 0; j < 8; j++) {
        if (indices[j] == i) {
          found = true;
          break;
        }
      }
      if (!found) {
        idx9 = i;
        break;
      }
    }

    if (idx9 >= 0) {
      float x1 = matches[idx9].x1;
      float y1 = matches[idx9].y1;
      float x2 = matches[idx9].x2;
      float y2 = matches[idx9].y2;

      // Apply normalization
      float x1n = N1(0, 0) * x1 + N1(0, 2);
      float y1n = N1(1, 1) * y1 + N1(1, 2);
      float x2n = N2(0, 0) * x2 + N2(0, 2);
      float y2n = N2(1, 1) * y2 + N2(1, 2);

      A(8, 0) = x2n * x1n;
      A(8, 1) = x2n * y1n;
      A(8, 2) = x2n;
      A(8, 3) = y2n * x1n;
      A(8, 4) = y2n * y1n;
      A(8, 5) = y2n;
      A(8, 6) = x1n;
      A(8, 7) = y1n;
      A(8, 8) = 1;
    }
  }

  // Solve using SVD
  FMatrix<float, 9, 9> U;
  FVector<float, 9> S;
  FMatrix<float, 9, 9> Vt;
  svd(A, U, S, Vt);

  // F is last column of V (last row of Vt) - corresponding to smallest singular
  // value
  FMatrix<float, 3, 3> Fn;
  for (int i = 0; i < 9; i++) {
    Fn.data()[i] = Vt(8, i);
  }

  // Enforce rank 2 constraint
  FMatrix<float, 3, 3> Uf;
  FVector<float, 3> Sf;
  FMatrix<float, 3, 3> Vtf;
  svd(Fn, Uf, Sf, Vtf);
  Sf[2] = 0; // Set smallest singular value to 0
  Fn = Uf * Diagonal(Sf) * Vtf;

  // Denormalize: F = N2^T * Fn * N1
  FMatrix<float, 3, 3> F = transpose(N2) * Fn * N1;

  return F;
}

FMatrix<float, 3, 3> computeNormalizationMatrix(const vector<Match> &matches,
                                                bool useImage1) {
  int n = matches.size();

  // Compute mean
  float mean_x = 0, mean_y = 0;
  for (int i = 0; i < n; i++) {
    if (useImage1) {
      mean_x += matches[i].x1;
      mean_y += matches[i].y1;
    } else {
      mean_x += matches[i].x2;
      mean_y += matches[i].y2;
    }
  }
  mean_x /= n;
  mean_y /= n;

  // Compute standard deviation/scale
  // (mean distance to origin should be sqrt(2))
  float scale = 0;
  for (int i = 0; i < n; i++) {
    float x = useImage1 ? matches[i].x1 : matches[i].x2;
    float y = useImage1 ? matches[i].y1 : matches[i].y2;
    float dx = x - mean_x;
    float dy = y - mean_y;
    scale += sqrt(dx * dx + dy * dy);
  }
  scale = sqrt(2.0f) * n / scale;

  // Build normalization matrix
  FMatrix<float, 3, 3> N;
  N.fill(0);
  N(0, 0) = scale;
  N(1, 1) = scale;
  N(0, 2) = -scale * mean_x;
  N(1, 2) = -scale * mean_y;
  N(2, 2) = 1;

  return N;
}

// RANSAC algorithm to compute F from point matches (8-point algorithm)
// Parameter matches is filtered to keep only inliers as output.
FMatrix<float, 3, 3> computeF(vector<Match> &matches) {
  const float distMax = 1.5f; // Pixel error for inlier/outlier discrimination
  int Niter = 100000;         // Adjusted dynamically
  FMatrix<float, 3, 3> bestF;
  vector<int> bestInliers;

  int n = matches.size();
  if (n < 8) {
    cerr << "Not enough matches for F computation" << endl;
    return bestF;
  }

  // Compute normalization matrix for each image
  FMatrix<float, 3, 3> N1 = computeNormalizationMatrix(matches, true);
  FMatrix<float, 3, 3> N2 = computeNormalizationMatrix(matches, false);

  // RANSAC loop
  for (int iter = 0; iter < Niter; iter++) {

    // Select 8 points at random
    vector<int> indices;
    for (int i = 0; i < 8; i++) {
      int idx;
      bool unique;
      do {
        unique = true;
        idx = rand() % n;
        for (int j = 0; j < i; j++) {
          if (indices[j] == idx) {
            unique = false;
            break;
          }
        }
      } while (!unique);
      indices.push_back(idx);
    }

    // Compute Fundamental matrix using 8-point
    FMatrix<float, 3, 3> F = computeF8Points(matches, indices, N1, N2);

    vector<int> inliers;
    for (int i = 0; i < n; i++) {
      FVector<float, 3> p1(matches[i].x1, matches[i].y1, 1);
      FVector<float, 3> p2(matches[i].x2, matches[i].y2, 1);
      FVector<float, 3> line = F * p1;

      // Compute distance from point to line
      float dist = abs(line[0] * p2[0] + line[1] * p2[1] + line[2]) /
                   sqrt(line[0] * line[0] + line[1] * line[1]);

      if (dist < distMax) {
        inliers.push_back(i);
      }
    }

    // Update best model and number of iterations:
    if (inliers.size() > bestInliers.size()) {
      bestInliers = inliers;
      bestF = F;

      float prob = 1.0f - (float)inliers.size() / n;
      float logbet = log(BETA);
      float logprob = log(1.0f - pow(1.0f - prob, 8));
      if (logprob < -1e-10) {
        Niter = min((int)(logbet / logprob), Niter);
      }
    }
  }

  // Updating matches with inliers only
  vector<Match> all = matches;
  matches.clear();
  for (size_t i = 0; i < bestInliers.size(); i++)
    matches.push_back(all[bestInliers[i]]);
  return bestF;
}

// Expects clicks in one image and show corresponding line in other image.
// Stop at right-click.
// Expects clicks in one image and show corresponding line in other image.
// Stop at right-click.
void displayEpipolar(Image<Color> I1, Image<Color> I2,
                     const FMatrix<float, 3, 3> &F) {
  while (true) {
    int x, y;
    if (getMouse(x, y) == 3)
      break;

    int w = I1.width();

    // Check which image was clicked
    if (x < w) {
      // Clicked in image 1, display epipolar line in image 2
      FVector<float, 3> p1(x, y, 1);
      FVector<float, 3> line = F * p1; // line in image 2: ax + by + c = 0

      // Draw the point in image 1
      fillCircle(x, y, 3, RED);

      // Draw epipolar line in image 2
      float a = line[0], b = line[1], c = line[2];

      // Find two points on the line within image 2 bounds
      if (abs(b) > abs(a)) {
        // Line is more horizontal, use x bounds
        int x1 = w;
        int y1 = (int)(-(a * x1 + c) / b);
        int x2 = 2 * w - 1;
        int y2 = (int)(-(a * x2 + c) / b);
        drawLine(x1, y1, x2, y2, RED);
      } else {
        // Line is more vertical, use y bounds
        int y1 = 0;
        int x1 = (int)(-(b * y1 + c) / a);
        int y2 = I2.height() - 1;
        int x2 = (int)(-(b * y2 + c) / a);
        drawLine(x1, y1, x2, y2, RED);
      }
    } else {
      // Clicked in image 2, display epipolar line in image 1
      FVector<float, 3> p2(x - w, y, 1);
      FVector<float, 3> line =
          transpose(F) * p2; // line in image 1: ax + by + c = 0

      // Draw the point in image 2
      fillCircle(x, y, 3, BLUE);

      // Draw epipolar line in image 1
      float a = line[0], b = line[1], c = line[2];

      // Find two points on the line within image 1 bounds
      if (abs(b) > abs(a)) {
        // Line is more horizontal, use x bounds
        int x1 = 0;
        int y1 = (int)(-(a * x1 + c) / b);
        int x2 = w - 1;
        int y2 = (int)(-(a * x2 + c) / b);
        drawLine(x1, y1, x2, y2, BLUE);
      } else {
        // Line is more vertical, use y bounds
        int y1 = 0;
        int x1 = (int)(-(b * y1 + c) / a);
        int y2 = I1.height() - 1;
        int x2 = (int)(-(b * y2 + c) / a);
        drawLine(x1, y1, x2, y2, BLUE);
      }
    }
  }
}

int main(int argc, char *argv[]) {
  srand((unsigned int)time(0));

  std::string path1 = argc > 1 ? argv[1] : srcPath("im1.jpg");
  std::string path2 = argc > 2 ? argv[2] : srcPath("im2.jpg");
  const char *s1 = path1.c_str();
  const char *s2 = path2.c_str();

  // Load and display images
  Image<Color, 2> I1, I2;
  if (!load(I1, s1) || !load(I2, s2)) {
    cerr << "Unable to load images" << endl;
    return 1;
  }
  int w = I1.width();
  openWindow(2 * w, I1.height());
  display(I1, 0, 0);
  display(I2, w, 0);

  vector<Match> matches;
  algoSIFT(I1, I2, matches);
  const int n = (int)matches.size();
  cout << " matches: " << n << endl;
  drawString(100, 20, std::to_string(n) + " matches", RED);
  click();

  FMatrix<float, 3, 3> F = computeF(matches);
  cout << "F=" << endl << F;

  // Redisplay with matches
  display(I1, 0, 0);
  display(I2, w, 0);
  for (size_t i = 0; i < matches.size(); i++) {
    Color c(rand() % 256, rand() % 256, rand() % 256);
    fillCircle(matches[i].x1 + 0, matches[i].y1, 2, c);
    fillCircle(matches[i].x2 + w, matches[i].y2, 2, c);
  }
  drawString(100, 20,
             to_string(matches.size()) + "/" + to_string(n) + " inliers", RED);
  click();

  // Redisplay without SIFT points
  display(I1, 0, 0);
  display(I2, w, 0);
  displayEpipolar(I1, I2, F);

  endGraphics();
  return 0;
}
