# 실제 CLIPPER 첫 연결 실험 — 2026-09-14

공식 [mit-acl/clipper](https://github.com/mit-acl/clipper/tree/e514dc29c273837ffdfeebbefbdcb2a93d970969) v0.2.4의 C++ 소스를 변경 없이 컴파일하고 CLIPPER::scorePairwiseConsistency → solve → getSelectedAssociations를 호출했다. 후보 생성은 기존 class all-to-all이며 SlideGraph를 연결한 것은 아니다.

## 입력과 평가 구분

기존 seed=42 graph.json의 지도 위치와 후보 인덱스만 C++ 프로그램에 전달한다. 실제 solver 입력은 각 결과 폴더 solver_input.txt에 저장했다. 정답은 C++ 입력에 없으며 선택 완료 뒤 precision/recall과 변환 오차 채점에만 사용한다. 변환 추정은 선택된 대응으로 기존 estimate_transform을 호출한다. 따라서 이번 변환은 oracle이 아닌 자동 선택 결과다.

## 설정

- clean/extra_5/noise_020 × epsilon 0.05/0.20/0.50 m, 지도 seed 42 단일 시행.
- CLIPPER EuclideanDistance의 kernel sigma=0.20 m를 모든 경우에 고정한 첫 연결용 설정. 데이터 잡음 sigma와 다른 파라미터이며 최적화된 값이 아니다.
- 실제 소스는 delta < epsilon에서 exp(-0.5*delta²/sigma²)를 계산하고 affinityeps=1e-4 초과 가중치를 사용한다. 앞선 교육용 그래프의 delta <= epsilon 및 이진 edge와 차이가 있다.
- 기본 Params와 DSD_HEU rounding, mindist=0. 초기 벡터는 모든 원소 1, 기본 rescale_u0=true. 공식 무작위 초기값 대신 명시적으로 주입했으며 정답과 무관하다. 초기값별 성능은 미평가.
- A→B, 위치 m, 오차 각도 deg. macOS 26.6.2 arm64, Apple clang 21.0.0, Python 3.12.14.
- 직접 C++14 -O2 serial 빌드. OpenMP/PMC/SCS/MKL/BLAS/Python binding은 사용하지 않는다. solveAsMaximumClique/SDR가 아닌 공식 solve를 사용한다. 성능 벤치마크용 빌드는 아니다.

## 결과

단일 시행이며 평균 또는 loop closure 성공률이 아니다. 선택 precision은 9조합 모두 100%였다.

| 조건 | epsilon(m) | 후보→선택 | 정답 선택 | 대응 recall | 이동 오차(m) | yaw 오차(°) |
|---|---:|---:|---:|---:|---:|---:|
| clean | 0.05/0.20/0.50 각각 | 34→10 | 10 | 100% | 0 | <1e-9 |
| extra_5 | 0.05/0.20/0.50 각각 | 51→10 | 10 | 100% | 0 | <1e-9 |
| noise_020 | 0.05 | 34→4 | 4 | 40% | 0.274436 | 0.539733 |
| noise_020 | 0.20 | 34→5 | 5 | 50% | 0.285119 | 0.310655 |
| noise_020 | 0.50 | 34→6 | 6 | 60% | 0.249264 | 1.096126 |

잡음 조건에서도 이번 선택에 오답은 없었지만 정답 일부를 놓쳤다. 남은 정답만으로도 변환을 계산할 수 있었다. 선택 수가 늘어도 선택된 물체의 배치와 위치 잡음에 따라 yaw 오차는 증가할 수 있다. 현재 단일 지도 결과로 CLIPPER의 일반적인 강건성이나 새 descriptor 성능을 주장하지 않는다. 별도 정합 성공 threshold도 정하지 않았으므로 성공률은 보고하지 않는다.

## 검증과 결과 파일

독립적인 순서가 섞인 3-4-5 삼각형에서 정답 3쌍 선택 통과. 각 9조건 동일 입력 재호출 시 선택 결과 일치, 후보 부분집합·일대일 대응·선택 집합의 pairwise consistency 검사 통과. 무잡음 정답 10개 및 변환 오차 <1e-9 검사 통과. 반복 호출은 재현성 검사이며 별도 통계 시행으로 세지 않았다. 공식 전체 테스트 스위트는 실행하지 않았다.

- [전체 지표](results_clipper_macos_20260914/metrics.csv)
- [출처·버전·코드/실행파일 SHA256](results_clipper_macos_20260914/manifest.json)
- [입력과 선택 결과](results_clipper_macos_20260914/)
- [Python 실행·평가](clipper_experiment.py), [C++ 입력 어댑터](clipper_driver.cpp), [빌드 스크립트](build_clipper.sh)

## 재현

GitHub 정리일: 2026-09-15. AISL checkout에서는 먼저 `cd research/object_loop_closure`로 이동한다. 아래 작업 루트는 이 디렉터리이며, 로컬 복사 배치에서는 Personal Master Study 루트에 해당한다. 의존성이 없는 새 작업 루트에서 다음과 같이 고정 버전을 확보한다(기존 디렉터리가 있으면 덮어쓰지 않고 버전을 먼저 확인).

```sh
git clone https://github.com/mit-acl/clipper.git third_party/clipper
git -C third_party/clipper checkout --detach e514dc29c273837ffdfeebbefbdcb2a93d970969
git clone --depth 1 --branch 3.4.0 https://gitlab.com/libeigen/eigen.git third_party/eigen
git -C third_party/eigen rev-parse HEAD
```

Eigen HEAD는 3147391d946bb4b6c68edd901f2add6ac1f31f8c인지 확인한다. Python은 해당 컴퓨터에 준비된 Python 3를 사용한다(검증 버전 3.12.14). 아래 절대 Python 경로는 실험 당시 맥북의 경로이며 다른 컴퓨터에서는 `python3` 등 실제 경로로 바꾼다. 빌드에는 clang++가 필요하다. 외부 소스 전체·실행 바이너리는 이번 업로드 대상이 아니며 원본 manifest의 로컬 경로와 해시는 실행 이력으로 보존한다.

작업 루트의 third_party/clipper commit e514dc29c273837ffdfeebbefbdcb2a93d970969 및 Eigen 3.4.0 commit 3147391d946bb4b6c68edd901f2add6ac1f31f8c가 필요하다. 기본 공식 CMake에는 Intel 옵션 -mavx/-mfma와 OpenMP 연결이 있어 이번 ARM 연결은 별도 빌드 스크립트를 사용했다. upstream 소스 tracked diff 없음 확인.

```sh
sh virtual_map/build_clipper.sh
/Users/kxgeon/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -B virtual_map/clipper_experiment.py --output virtual_map/results_clipper_next
```

새 output만 허용한다. 입력은 results_graph_macos_20260911의 9개 graph.json이다. 다른 OS로 이동할 때 실행파일을 복사해 사용하지 말고 동일 소스를 다시 빌드한다.

다음은 선택된 정답이 어떤 객체인지 살펴본 뒤, 설정을 고정하고 여러 지도 seed로 반복 평가하는 것이다. 실제 SlideGraph 연결과 센서 데이터/SLAM 실험은 별도 단계다.
