// Imagine++ project
// Project:  Fundamental
// Author:   Pascal Monasse

#include "./Imagine/Features.h"
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

// RANSAC algorithm to compute F from point matches (8-point algorithm)
// Parameter matches is filtered to keep only inliers as output.
FMatrix<float, 3, 3> computeF(vector<Match> &matches) {
  const float distMax = 1.5f; // Pixel error for inlier/outlier discrimination
  int Niter = 100000;         // Adjusted dynamically
  FMatrix<float, 3, 3> bestF;
  vector<int> bestInliers;
  // --------------- TODO ------------
  // DO NOT FORGET NORMALIZATION OF POINTS

  // Updating matches with inliers only
  vector<Match> all = matches;
  matches.clear();
  for (size_t i = 0; i < bestInliers.size(); i++)
    matches.push_back(all[bestInliers[i]]);
  return bestF;
}

// Expects clicks in one image and show corresponding line in other image.
// Stop at right-click.
void displayEpipolar(Image<Color> I1, Image<Color> I2,
                     const FMatrix<float, 3, 3> &F) {
  while (true) {
    int x, y;
    if (getMouse(x, y) == 3)
      break;
    // --------------- TODO ------------
  }
}

int main(int argc, char *argv[]) {
  srand((unsigned int)time(0));

  const char *s1 = argc > 1 ? argv[1] : srcPath("im1.jpg");
  const char *s2 = argc > 2 ? argv[2] : srcPath("im2.jpg");

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
