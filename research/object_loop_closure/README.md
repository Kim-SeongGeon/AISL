# Object-level Loop Closure Research

정리일: 2026-09-06. 이 폴더는 개인연구의 재현·설정·평가 자료를 관리합니다.

[Notion: 석사 개인 연구](https://app.notion.com/p/388c388e8d7181259571f054730a8512)에서 학습·논문·연구 판단·랩미팅 기록을 관리합니다.

## 현재 상태

- 원 마일스톤: 문헌 조사 완료 기재. SlideSLAM 재현 실행·신규 descriptor·실제 성능 결과는 미확인.
- 이번 정리에서 새로 추가: 재현 절차, 미확정 설정 양식, offline 평가 도구, synthetic 단위 테스트.
- 평가 도구는 모델·ROS·SLAM을 실행하지 않습니다. 예제 결과는 실제 연구 성능이 아닙니다.
- 기존 저장소의 README 및 실습 기록은 기존 위치에 보존했습니다.

## 구성

| 위치 | 용도 |
|---|---|
| reproduction/README.md | 공식 코드 재현 순서·실행 증거 체크리스트 |
| configs/experiment.template.json | 입력·평가·runtime 설정 양식 |
| configs/paper_reproduction.reference.json | 논문 재현 조건과 새 연구 실험 구분 |
| evaluation/evaluate_retrieval.py | Recall@1/5/10, 고정 threshold top-1 precision/recall/F1 |
| evaluation/test_evaluate_retrieval.py | 경계조건 단위 테스트 |
| evaluation/examples/synthetic.json | 합성 검증 fixture |
| experiments/run_manifest.template.json | 실행 명령·SHA·환경·결과 출처 |
| results/README.md | 결과 저장 및 Notion 연결 규칙 |

## 최소 검증

저장소 루트에서 Python 3.10 이상으로 실행합니다. 표준 라이브러리만 사용합니다.

```sh
python -m unittest discover -s research/object_loop_closure/evaluation -p "test_*.py" -v
python research/object_loop_closure/evaluation/evaluate_retrieval.py --input research/object_loop_closure/evaluation/examples/synthetic.json --threshold 0.5 --output research/object_loop_closure/results/local/synthetic-metrics.json
```

출력 파일이 있으면 덮어쓰지 않고 오류로 종료합니다. 새 실행에는 다른 파일명을 사용하세요.

## 평가 입력 계약

JSON은 schema_version=1, protocol_id, synthetic(boolean), queries를 가집니다. 각 query에는 query_id, eligible_ids, positive_ids, candidates가 필요합니다. candidates는 id와 score의 내림차순 배열이며 score는 클수록 유사합니다. 거리라면 제출 전에 부호 변환 등의 규칙을 고정합니다.

eligible_ids에는 시간 제외·self 제외·GT 회색 구간 처리가 이미 반영되어야 합니다. positive_ids는 eligible_ids의 부분집합입니다. GT 생성은 별도 단계이며 이 스크립트는 GT의 정확성을 보증하지 않습니다. 모든 예정 query를 포함하고 실패한 검색은 빈 candidates로 기록합니다. 동점 순서는 입력을 유지하며 생성 측의 결정적 규칙을 명시해야 합니다.

Recall@k의 분모는 positive_ids가 비어 있지 않은 query 수입니다. detection은 고정 threshold에서 top-1만 판정합니다. 양성 query에서 잘못된 장소를 수락하면 FP와 FN에 함께 반영합니다. 따라서 TP+FP+FN+TN이 query 수와 항상 같지는 않습니다. 분모가 0인 precision/recall은 null입니다. 높은 k에서 예측 후보가 k보다 적으면 제출된 후보만 평가합니다.

PR/AP, registration error, ATE/RPE, runtime 측정은 아직 구현되지 않았습니다. 별도 도구로 측정하고 규칙을 기록해야 합니다. threshold를 test 결과로 튜닝하지 않습니다.

## 연구 경계

Global map retrieval과 두 map의 object correspondence matching을 구분합니다. SlideGraph의 내부 후보를 바꾸는 것만으로 과거 장소 DB Top-k 검색을 구현했다고 볼 수 없습니다. Baseline·query 단위·GT·허용 오차는 Notion 판단 기록에서 합의한 뒤 설정에 고정합니다.
