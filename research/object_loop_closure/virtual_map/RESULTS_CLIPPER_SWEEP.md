# CLIPPER 30개 지도 반복 실험 — 2026-09-16

기존 설정을 유지하고 지도 seed 42~71 × 3조건 × epsilon 3개 = 270조합을 실행했다. kernel sigma=0.20m, ones 초기 벡터, 공식 CLIPPER solve/DSD_HEU, A→B 규약을 유지했다. 정답은 평가에만 사용했다. 원본 코드/바이너리 해시는 첫 연결 실험과 일치한다.

모든 조합에서 변환을 계산했다. solver 오류·대응 부족·퇴화로 계산하지 못한 경우는 0개다. 계산 가능은 정합 성공 판정이 아니며 성공 threshold는 아직 없다.

## 조건별 결과

각 행은 30개 seed의 산술평균이다. ±는 표본 표준편차(n−1), precision/recall은 지도별 값의 macro 평균이다.

| 조건 | epsilon(m) | 선택 수 | precision | recall | 이동 오차(m) | yaw 오차(°) | 오답 포함 지도 |
|---|---:|---:|---:|---:|---:|---:|---:|
| clean | 0.05 | 10.000 ± 0.000 | 100.00% | 100.00% | 0.000 ± 0.000 | 0.000 ± 0.000 | 0/30 |
| clean | 0.20 | 10.000 ± 0.000 | 100.00% | 100.00% | 0.000 ± 0.000 | 0.000 ± 0.000 | 0/30 |
| clean | 0.50 | 10.000 ± 0.000 | 100.00% | 100.00% | 0.000 ± 0.000 | 0.000 ± 0.000 | 0/30 |
| extra_5 | 0.05 | 10.000 ± 0.000 | 100.00% | 100.00% | 0.000 ± 0.000 | 0.000 ± 0.000 | 0/30 |
| extra_5 | 0.20 | 10.000 ± 0.000 | 100.00% | 100.00% | 0.000 ± 0.000 | 0.000 ± 0.000 | 0/30 |
| extra_5 | 0.50 | 10.000 ± 0.000 | 100.00% | 100.00% | 0.000 ± 0.000 | 0.000 ± 0.000 | 0/30 |
| noise_020 | 0.05 | 2.467 ± 0.629 | 91.67% | 23.00% | 0.474 ± 1.009 | 11.890 ± 29.045 | 3/30 |
| noise_020 | 0.20 | 4.367 ± 0.669 | 100.00% | 43.67% | 0.151 ± 0.080 | 1.628 ± 1.357 | 0/30 |
| noise_020 | 0.50 | 6.067 ± 0.691 | 100.00% | 60.67% | 0.122 ± 0.066 | 1.303 ± 1.226 | 0/30 |

## 해석

무잡음과 추가 객체 조건의 180조합에서는 모두 정답 10쌍을 선택했고 이동·yaw 오차는 1e-9 미만이었다. 잡음 조건의 epsilon 0.05에서는 3개 지도에서 오답을 선택했다. 따라서 앞선 seed=42의 precision 100%를 일반화할 수 없다. 0.20/0.50에서는 이번 30개 지도에 한해 precision 100%였다.

오대응 사례:

```json
[
  {
    "seed": 47,
    "epsilon_m": 0.05,
    "selected": 2,
    "correct": 0,
    "translation_error_m": 0.9677991674921391,
    "yaw_error_deg": 108.73362415248452
  },
  {
    "seed": 51,
    "epsilon_m": 0.05,
    "selected": 2,
    "correct": 0,
    "translation_error_m": 5.235563284708289,
    "yaw_error_deg": 97.78229992523428
  },
  {
    "seed": 69,
    "epsilon_m": 0.05,
    "selected": 2,
    "correct": 1,
    "translation_error_m": 2.5335922322672992,
    "yaw_error_deg": 83.96365811579427
  }
]
```

epsilon 0.05→0.20에서 선택 수가 늘어난 30개 중 6개, 0.20→0.50에서 늘어난 29개 중 13개에서 yaw 오차가 증가했다. 집계 평균은 감소해도 개별 지도에서는 악화될 수 있다. epsilon을 늘린다고 선택 집합 포함 관계나 오차 감소가 보장되지 않는다.

이 결과만으로 0.50m를 최적 설정으로 확정하지 않는다. 동일 30개 지도에서 관찰한 결과이며 별도 validation/test, 초기값별 평가, 누락/class 오류/비겹침, 실제 데이터는 미평가다.

## 검증·재현

270개 고유 조합, 30행씩 9그룹, 전 결과 pose 재계산과 집계 평균 대조 통과. seed=42의 9결과는 이전 선택 목록·pose와 일치. 선택 부분집합·일대일 및 pairwise consistency 확인. solver 입력은 각 폴더 solver_input.txt로 보존한다.

[전체 CSV](results_clipper_sweep_20260916/metrics.csv) · [평균/표준편차/중앙값/최댓값](results_clipper_sweep_20260916/summary.json) · [검증](results_clipper_sweep_20260916/verification.json) · [실행 출처와 해시](results_clipper_sweep_20260916/manifest.json)

```sh
/Users/kxgeon/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -B virtual_map/clipper_sweep.py --output virtual_map/results_clipper_sweep_next
```

실험은 맥북의 기존 실행파일로 수행했고 추가 설치·재빌드는 하지 않았다. 실행 당시 원격 업로드는 하지 않았으며, 본 보고서는 9월 16일 GitHub 정리용이다. 다음은 오대응한 3개 지도의 선택과 기하 배치를 확인하는 것이다.

### AISL에서 확인·재현할 때

AISL의 작업 루트는 `research/object_loop_closure`이다. 의존성의 고정 버전과 빌드 방법은 [첫 CLIPPER 보고서](RESULTS_CLIPPER.md)를 따른다. 실행 기록의 Python은 3.12.14이고 OS는 manifest의 `macOS-27.0-arm64-arm-64bit`이다. 빌드 정보는 기존 바이너리의 Apple clang 21.0.0, C++14, -O2, serial 설정을 계승했다.

```sh
cd research/object_loop_closure
python3 -B virtual_map/clipper_sweep.py --output virtual_map/results_clipper_sweep_new
```

위 명령은 기존 코드와 바이너리 해시가 일치하는 환경용이다. 현재 스크립트는 첫 실험 manifest의 **바이너리 SHA256까지 엄격하게 검사**한다. 다른 PC에서 재빌드한 실행파일은 같은 소스여도 해시가 달라 실행 전 검사에서 중단될 수 있다. 새 환경에서의 재현에는 별도의 검증된 기준 manifest를 사용하는 이식성 보완이 필요하며, 기존 manifest와 결과를 덮어써서 검사를 통과시키면 안 된다. 바이너리와 third_party 소스 전체는 이 결과 묶음에 포함하지 않는다.
