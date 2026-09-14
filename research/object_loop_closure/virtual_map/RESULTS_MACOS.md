# macOS 연구 재개 결과 — 2026-09-11

출처: [Notion 석사 개인 연구의 26.09.11 실습](https://app.notion.com/p/388c388e8d7181259571f054730a8512), 현재 로컬 코드와 아래 결과 파일.

## 기존 실험 재현

Python 3.12.14, macOS 26.6.2 arm64. 기존 experiment.py를 변경하지 않고 seed 42~71, 7조건 × 30회 실행했다. 원본 results/는 보존했다.

- [새 CSV](results_recheck_macos/metrics.csv): 210행, 조건별 30행.
- 후보 수·정답 후보 수·precision·recall은 이전 CSV와 모두 일치한다.
- oracle 오차 최대 차이: 이동 3.6603e-15 m, yaw 1.2723e-14 deg. 비교 허용오차 1e-12 통과.
- [검증 기록](results_recheck_macos/verification.json): 명령, 환경, 원본 코드 SHA256, 수치 비교 및 작은 독립 예제 검사.
- 무잡음 oracle 복원은 계산 검증이며 자동 정합 성능이 아니다.

## Consistency graph 실습

입력은 기존 생성기의 지도 A·B와 class all-to-all 후보다. 후보 하나가 노드이며, 같은 객체를 중복 사용하는 후보끼리는 연결하지 않는다. 두 지도에서 객체 간 거리 차이가 epsilon 이하일 때 연결한다. 출력은 후보 노드와 무방향 edge다. 정답은 그래프 생성 뒤 채점과 색상에만 쓰인다.

아래는 **seed=42 단일 시행**이며 평균이 아니다. 정답 후보는 10개, 가능한 정답–정답 연결은 45개다. 후보 수는 clean/noise_020 34개, extra_5 51개로 그대로 유지된다.

| 조건 | epsilon (m) | 정답–정답 /45 | 정답–오답 | 오답–오답 |
|---|---:|---:|---:|---:|
| clean | 0.05 | 45 | 4 | 12 |
| clean | 0.20 | 45 | 12 | 16 |
| clean | 0.50 | 45 | 32 | 34 |
| extra_5 | 0.05 | 45 | 5 | 12 |
| extra_5 | 0.20 | 45 | 21 | 30 |
| extra_5 | 0.50 | 45 | 48 | 75 |
| noise_020 | 0.05 | 10 | 3 | 5 |
| noise_020 | 0.20 | 27 | 11 | 10 |
| noise_020 | 0.50 | 38 | 27 | 35 |

허용오차를 늘리면 잡음으로 끊어진 정답 연결이 회복되지만 오답이 포함된 연결도 늘어난다. 무잡음에서도 오답끼리의 거리 일관성이 생길 수 있다. 연결 수만으로 정답을 확정할 수 없으며 이번에는 후보를 제거하거나 pose를 계산하지 않았다. 실제 CLIPPER와 SlideGraph는 여전히 미연결이다.

시각화는 정답 후보 초록색, 오답 후보 회색이다. 각 노드 번호의 A/B 대응은 같은 폴더 graph.json에서 확인한다. 동일 조건의 원형 배치는 epsilon에 따라 바뀌지 않는다.

- [무잡음 그래프, epsilon 0.05](results_graph_macos_20260911/clean_eps_0.05/graph.svg)
- [잡음 그래프, epsilon 0.05](results_graph_macos_20260911/noise_020_eps_0.05/graph.svg)
- [잡음 그래프, epsilon 0.50](results_graph_macos_20260911/noise_020_eps_0.50/graph.svg)
- [9조합 CSV](results_graph_macos_20260911/metrics.csv), [실행 출처·설정·코드 SHA256](results_graph_macos_20260911/manifest.json)

검증: 무잡음 정답 연결 45개, epsilon 증가에 따른 edge 포함 관계, 자기 연결/중복 edge/객체 중복 사용 차단 통과. 독립적인 3-4-5 삼각형, 경계 epsilon 포함, 잘못된 epsilon 거부도 검사했다. JSON 및 SVG XML 파싱 통과. 그림의 실제 렌더링 배치는 별도 시각 검수하지 않았다.

## 이어서 실행하기

작업 루트에서 아래 명령을 사용한다. 이미 있는 output은 덮어쓰지 않고 오류로 중단하므로 새 output 이름을 지정한다.

```sh
/Users/kxgeon/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -B virtual_map/consistency_graph.py --seed 42 --output virtual_map/results_graph_next
```

다음 학습 작업은 noise_020의 epsilon 0.05와 0.50 그림을 비교해 어떤 연결이 회복되고 어떤 오답 연결이 생기는지 보는 것이다. 이후 실제 CLIPPER의 공식 입출력·지원 환경을 확인한다. 실제 데이터와 전체 ROS/SLAM 실험은 연구실 데스크탑 자원·환경을 확인한 뒤 결정한다. 현재 소규모 graph 실습에는 추가 설치나 데스크탑 전환이 필요하지 않았다.
