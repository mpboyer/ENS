// Imagine++ project
// Project:  Panorama
// Author:   Pascal Monasse
// Student: Matthieu Boyer

#include <Imagine/Graphics.h>
#include <Imagine/Graphics/Events.h>
#include <Imagine/Graphics/Types.h>
#include <Imagine/Images.h>
#include <Imagine/LinAlg.h>
#include <sstream>
#include <vector>
using namespace Imagine;
using namespace std;

// Record clicks in two images, until right button click
void getClicks(Window w1, Window w2, vector<IntPoint2> &pts1,
               vector<IntPoint2> &pts2) {
  Window win;
  int subWin;
  int button;
  IntPoint2 p;

  while (true) {
    button = anyGetMouse(p, win, subWin);
    cout << "Button " << button << "clicked on Window " << win << " at " << p
         << endl;
    if (button == 3) { // Break on right click
      break;
    }

    // Points should be clicked in the same order for both windows as
    // the order of clicks will be used for computations.
    if (win == w1) {
      pts1.push_back(p); // Add point based on clicked window
    }
    if (win == w2) {
      pts2.push_back(p); // Add point based on clicked window
    }
  }
}

// Return homography compatible with point matches
Matrix<float> getHomography(const vector<IntPoint2> &pts1,
                            const vector<IntPoint2> &pts2) {
  size_t n = min(pts1.size(), pts2.size());
  if (n < 4) {
    cout << "Not enough correspondences: " << n << endl;
    return Matrix<float>::Identity(3);
  }
  Matrix<double> A(2 * n, 8);
  Vector<double> B(2 * n);

  for (size_t i = 0; i < n; i++) {
    double x1 = pts1[i].x();
    double y1 = pts1[i].y();
    double x2 = pts2[i].x();
    double y2 = pts2[i].y();

    // Equation 1: h00*x1 + h01*y1 + h02 - h20*x1*x2 - h21*y1*x2 = x2
    A(2 * i, 0) = x1;
    A(2 * i, 1) = y1;
    A(2 * i, 2) = 1;
    A(2 * i, 3) = 0;
    A(2 * i, 4) = 0;
    A(2 * i, 5) = 0;
    A(2 * i, 6) = -x1 * x2;
    A(2 * i, 7) = -y1 * x2;
    B[2 * i] = x2;

    // Equation 2: h10*x1 + h11*y1 + h12 - h20*x1*y2 - h21*y1*y2 = y2
    A(2 * i + 1, 0) = 0;
    A(2 * i + 1, 1) = 0;
    A(2 * i + 1, 2) = 0;
    A(2 * i + 1, 3) = x1;
    A(2 * i + 1, 4) = y1;
    A(2 * i + 1, 5) = 1;
    A(2 * i + 1, 6) = -x1 * y2;
    A(2 * i + 1, 7) = -y1 * y2;
    B[2 * i + 1] = y2;
  }

  B = linSolve(A, B);
  Matrix<float> H(3, 3);
  H(0, 0) = B[0];
  H(0, 1) = B[1];
  H(0, 2) = B[2];
  H(1, 0) = B[3];
  H(1, 1) = B[4];
  H(1, 2) = B[5];
  H(2, 0) = B[6];
  H(2, 1) = B[7];
  H(2, 2) = 1;

  // Sanity check
  for (size_t i = 0; i < n; i++) {
    cout << "Sanity check" << i << endl;
    float v1[] = {(float)pts1[i].x(), (float)pts1[i].y(), 1.0f};
    float v2[] = {(float)pts2[i].x(), (float)pts2[i].y(), 1.0f};
    Vector<float> x1(v1, 3);
    Vector<float> x2(v2, 3);
    x1 = H * x1;
    cout << "\t" << x1[1] * x2[2] - x1[2] * x2[1] << ' '
         << x1[2] * x2[0] - x1[0] * x2[2] << ' '
         << x1[0] * x2[1] - x1[1] * x2[0] << endl;
  }
  return H;
}

// Grow rectangle of corners (x0,y0) and (x1,y1) to include (x,y)
void growTo(float &x0, float &y0, float &x1, float &y1, float x, float y) {
  if (x < x0)
    x0 = x;
  if (x > x1)
    x1 = x;
  if (y < y0)
    y0 = y;
  if (y > y1)
    y1 = y;
}

// Panorama construction
void panorama(const Image<Color, 2> &I1, const Image<Color, 2> &I2,
              Matrix<float> H) {
  Vector<float> v(3);
  float x0 = 0, y0 = 0, x1 = I2.width(), y1 = I2.height();

  // Find bounding box by transforming I1 corners into I2 coordinates
  for (int i = 0; i < 2; i++)
    for (int j = 0; j < 2; j++) {
      v[0] = j * I1.width();
      v[1] = i * I1.height();
      v[2] = 1;
      v = H * v;
      v /= v[2];
      growTo(x0, y0, x1, y1, v[0], v[1]);
    }
  cout << "Rectangle of mosaic in I2 coordinates:" << endl;
  cout << "x0 x1 y0 y1=" << x0 << ' ' << x1 << ' ' << y0 << ' ' << y1 << endl;

  Image<Color> I(int(x1 - x0), int(y1 - y0));
  setActiveWindow(openWindow(I.width(), I.height(), "Panorama"));
  I.fill(WHITE);

  // Compute inverse homography to pull pixels from I2 coordinates to I1
  // coordinates
  Matrix<float> Hinv = inverse(H);

  // Iterate through all pixels in the panorama
  for (int y = 0; y < I.height(); y++) {
    for (int x = 0; x < I.width(); x++) {
      float x2 = x + x0;
      float y2 = y + y0;

      // Check if this pixel is within I2's bounds
      bool inI2 = (x2 >= 0 && x2 < I2.width() && y2 >= 0 && y2 < I2.height());

      // Pull back to I1 coordinates using inverse homography
      v[0] = x2;
      v[1] = y2;
      v[2] = 1;
      v = Hinv * v;
      v /= v[2];
      float x1 = v[0];
      float y1 = v[1];

      // Check if this pixel is within I1's bounds
      bool inI1 = (x1 >= 0 && x1 < I1.width() && y1 >= 0 && y1 < I1.height());

      // Assign color based on which image(s) contain this pixel
      if (inI1 && inI2) {
        // Overlap region: blend or average the two images
        Color c1 = I1.interpolate(x1, y1);
        Color c2 = I2.interpolate(x2, y2);
        I(x, y) = (c1 + c2) / 2;
      } else if (inI1) {
        I(x, y) = I1.interpolate(x1, y1);
      } else if (inI2) {
        I(x, y) = I2.interpolate(x2, y2);
      }
    }
  }

  display(I, 0, 0);
}
// Main function
int main(int argc, char *argv[]) {
  string s1 = argc > 2 ? argv[1] : srcPath("image0006.jpg");
  string s2 = argc > 2 ? argv[2] : srcPath("image0007.jpg");

  // Load and display images
  Image<Color> I1, I2;
  if (!load(I1, s1) || !load(I2, s2)) {
    cerr << "Unable to load the images" << endl;
    return 1;
  }
  Window w1 = openWindow(I1.width(), I1.height(), s1);
  display(I1, 0, 0);
  Window w2 = openWindow(I2.width(), I2.height(), s2);
  setActiveWindow(w2);
  display(I2, 0, 0);

  // Get user's clicks in images
  vector<IntPoint2> pts1, pts2;
  getClicks(w1, w2, pts1, pts2);

  vector<IntPoint2>::const_iterator it;
  cout << "pts1=" << endl;
  for (it = pts1.begin(); it != pts1.end(); it++)
    cout << *it << endl;
  cout << "pts2=" << endl;
  for (it = pts2.begin(); it != pts2.end(); it++)
    cout << *it << endl;

  // Compute homography
  Matrix<float> H = getHomography(pts1, pts2);
  cout << "H=" << H / H(2, 2);

  // Apply homography
  panorama(I1, I2, H);

  endGraphics();
  return 0;
}
