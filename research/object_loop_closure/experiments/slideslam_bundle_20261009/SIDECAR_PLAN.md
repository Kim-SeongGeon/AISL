# 원래 class ID 보존 sidecar: 지점 결정과 검증 계획

상태: **설계와 시각·frame 감사 완료, 새 sidecar 수집·객체별 공간 연결 미실행** (2026-10-12). 범위는 지상 단일 robot0의 객체 지도 입력 인터페이스다. 정답 ID는 매칭에 사용하지 않는다.

## 왜 별도 기록이 필요한가

KITTI 입력 `/semantic_point_cloud`의 `intensity`에는 class ID가 들어 있다. `process_cloud_node_outdoor.py`는 이를 읽고 KITTI class YAML의 ground 40, car 10, tree 71, lightpole 80을 사용한다. 그러나 후단의 `merge_synced_measurements.py`는 cuboid를 `-2`로 만들고 다중 측정 병합 시 cylinder를 `-1`로 만든다. 기록된 `PoseMstBundle.map_of_labelXYZ` 20개에도 이 음수값만 있다. 최종 7D에서 양수 class를 추정해 채우는 방법은 채택하지 않는다.

## sidecar 생성 위치

**관측 객체를 만드는 frontend에서, 형상과 class가 함께 존재하고 동기화 노드가 label을 대체하기 전**에 별도 sidecar를 만든다. 기존 SLAM 메시지나 7D 출력의 의미를 바꾸지 않는다.

- **Cuboid:** `frontend/scan2shape/script/cuboid_utils_outdoor.py`의 `publish_cuboid_markers()` 직전/직후. `process_cloud_node_outdoor.py`는 class별 점군을 분리하고 `ObjectTrack.class_label`을 유지한다. 최종 cuboid는 `class_name`을 갖고, body marker의 `ns`는 `<class_name>_body`, `id`는 해당 발행 배열의 index, header는 원본 scan stamp와 `body` frame이다. YAML의 `class_name→id`를 함께 저장한다. `(stamp, ns, marker.id)`는 **한 발행 메시지 내 관측 키**이며 영속 객체 ID가 아니다.
- **Cylinder:** `frontend/object_modeller/script/cylinder_plane_modeller.py`가 `ROSCylinderArray`를 발행하기 전. 그 입력 `tree_cloud`에는 cylinder 후보 점의 intensity class가 남지만 tree(71)와 lightpole(80)가 한 cloud에 들어갈 수 있다. 현재 코드가 발행하는 cylinder의 `id=temp_id`는 callback마다 0부터 다시 시작하고 semantic label은 채우지 않는다. 각 cylinder에 사용된 점들의 원래 class를 보존하려면 fitter의 인lier/point-support와 intensity를 연결해 class histogram 또는 명시적 `class_id`를 **별도 관측 기록**에 적어야 한다. 이 점 연결 구현·검증 전에는 cylinder별 class를 단정하지 않는다.

sidecar의 최소 필드: `run_id`, `robot_id`, `source_topic`, `scan_header_stamp_ns`, `source_frame`, `observation_kind`, `observation_index`, `class_id_raw`, `class_name`, `class_yaml_sha256`, `geometry`, `geometry_frame`, `association_provenance`. class가 불확실하면 `class_id_raw=null`과 이유를 기록한다. ROS bag 수신 시각은 별도 필드로 두고 scan header 시각 대신 쓰지 않는다. 원본 bag·코드 HEAD·수정 diff·실행 설정·출력 SHA-256을 manifest에 넣는다.

## 단계별 검증

1. **기존 bag의 시간축·frame 감사 — 완료.** `evidence/time_frame_audit.json`에서 점군 `body` 1,001개, odometry `camera_init→body` 1,001개, 같은 순번 헤더 시각 차이 0.01초 이하 1,000쌍을 확인했다. 나머지 첫 쌍은 약 0.1초다. 20개 bundle은 첫 scan 이후 약 5초부터 발행된다. 순번 비교가 각 scan의 실제 처리/발행을 입증하지는 않는다.
2. **새 replay의 계측 bag — 미실행.** 기존 입력·결과를 보존하고 새 output dir에서 recorder를 bag 재생 전에 연결한다. 현재 ROS 그래프에서 실제 토픽명을 확인한 뒤 원본 점군·odometry, class가 남는 frontend 결과(`car_cuboids_body`, `tree_cloud`), `cylinder_measurements`, `semantic_meas_sync_odom_raw`, `semantic_meas_sync_odom`, SLAM map pose/TF와 7D bundle을 기록한다. 구독/메시지 수·각 header stamp/frame·marker namespace와 class YAML 해시를 검증한다. 토픽명·타입은 현재 실행에서 재확인한다.
3. **관측 연결 — 미실행.** Cuboid는 scan stamp·body marker의 `(ns,id)`와 동기화 cuboid의 순서·body geometry를 대조한다. Cylinder는 source point-support 없이 class를 부여하지 않는다. 중복 stamp, 누락, 역순, geometry 불일치는 보류로 남긴다. 샘플마다 candidate 수와 잔차를 저장한다.
4. **지도 연결 — 미실행.** `quadrotor/map`의 누적 7D와 `body` 관측을 직접 좌표 비교하지 않는다. 같은 시각의 TF·SLAM map pose를 이용해 `body→map` 변환 방향과 단위를 확인하고, 해당 관측 이후에 나타난 지도 항목에 한해 거리·형상 잔차와 유일성을 검사한다. bundle 자체에는 항목별 stamp·ID가 없고 기존 객체 위치가 최적화로 변할 수 있어, 근접만으로 정답 대응을 선언하지 않는다. 변환 또는 유일성이 확인되지 않으면 `unresolved`로 남긴다.

첫 실험의 통과 기준은 (a) 새 sidecar의 모든 class가 실제 원본 intensity/YAML 또는 명시적 frontend class 값에서 왔다는 출처가 있고, (b) scan→관측 시각·frame이 대조되며, (c) 지도 연결은 변환·잔차·충돌 검사 결과와 미해결 비율을 함께 보고하는 것이다. 자동 대응 성능이나 loop closure 수치는 이 단계의 결과로 보고하지 않는다.

## 근거 코드와 설정 (SlideSLAM HEAD `63c78b9995b1e068dc0f185b3550e837b524833c`)

- `frontend/scan2shape/script/process_cloud_node_outdoor.py`: 입력 intensity 해석, class별 cuboid/cylinder 점군 처리, `body`·`odom` frame 설정.
- `frontend/scan2shape/script/cuboid_utils_outdoor.py`: cuboid class 이름, 원본 시각·body marker의 `ns`·`id`.
- `frontend/scan2shape/scan2shape_launch/config/process_cloud_node_outdoor_kitti_class_info.yaml`: KITTI class ID와 형상 모델.
- `frontend/object_modeller/script/cylinder_plane_modeller.py`: tree cloud→cylinder 피팅, callback별 임시 ID, 입력 cloud header 복사.
- `frontend/object_modeller/script/merge_synced_measurements.py`: cuboid `-2`, cylinder `-1` 대입.
- `backend/sloam/src/core/sloamNode.cpp`, `databaseManager.cpp`, `backend/sloam/params/sloam.yaml`: 지도 업데이트/7D 직렬화와 `quadrotor/map` 설정. 실행 당시 실제 TF 관계와 최종 지도 frame은 다음 replay에서 확인한다.
