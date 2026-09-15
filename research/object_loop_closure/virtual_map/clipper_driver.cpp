// Adapter only: official CLIPPER implements scoring and solve(). No GT input.
#include <iostream>
#include <iomanip>
#include <memory>
#include "clipper/clipper.h"
int main() {
  int n,m,h; double epsilon,sigma;
  if (!(std::cin>>n>>m>>h>>epsilon>>sigma) || n<2 || m<2 || h<1 || epsilon<=0 || sigma<=0) return 2;
  Eigen::MatrixXd a(2,n),b(2,m);
  for(int i=0;i<n;++i) std::cin>>a(0,i)>>a(1,i);
  for(int i=0;i<m;++i) std::cin>>b(0,i)>>b(1,i);
  clipper::Association pairs(h,2);
  for(int i=0;i<h;++i) {
    std::cin>>pairs(i,0)>>pairs(i,1);
    if(pairs(i,0)<0 || pairs(i,0)>=n || pairs(i,1)<0 || pairs(i,1)>=m) return 3;
  }
  if(!std::cin) return 4;
  clipper::invariants::EuclideanDistance::Params ip;
  ip.epsilon=epsilon; ip.sigma=sigma; ip.mindist=0;
  auto invariant=std::make_shared<clipper::invariants::EuclideanDistance>(ip);
  clipper::Params params;
  clipper::CLIPPER solver(invariant,params);
  solver.scorePairwiseConsistency(a,b,pairs);
  // Explicit uniform initial vector, independent of truth and reproducible.
  solver.solve(Eigen::VectorXd::Ones(h));
  auto selected=solver.getSelectedAssociations();
  std::cout<<selected.rows()<<"\n";
  for(int i=0;i<selected.rows();++i) std::cout<<selected(i,0)<<" "<<selected(i,1)<<"\n";
}
