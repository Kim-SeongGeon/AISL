# SlideSLAM 단일 로봇 7D 지도 추출·검증 (2026-10-09)

KITTI 05 일부 구간의 robot0 실행에서 기록한 PoseMstBundle.map_of_labelXYZ를 값 변경 없이 20개의 누적 지도 snapshot으로 추출했다. 첫 지도는 12개, 마지막 지도는 111개 객체이며, 전체 CSV는 1,302행이다. 같은 객체가 여러 snapshot에 반복되므로 1,302행은 고유 객체 수가 아니다.

입력 기록 bag SHA-256: a9a68425de6a0ef7fee26476f15de9b07c269635fd357f6188ec305f594957d4. SlideSLAM source HEAD: 63c78b9995b1e068dc0f185b3550e837b524833c. 연구실 ROS Noetic에서 원본 bag·source HEAD·JSON/CSV·출력 해시를 대조했고, Mac 복사본에서도 출력 해시와 행별 대조를 통과했다. 전체 label은 -1이 712행, -2가 590행이다.

원본 입력 점군의 intensity에는 KITTI class ID가 있다(ground 40, car 10, tree 71, lightpole 80). 그러나 후단 cuboid와 cylinder 경로는 label을 각각 -2와 -1로 대체한다. 따라서 현재 7D를 class-aware 객체 대응 입력으로 사용하지 않는다. 7D 항목에는 개별 객체 ID·시각·frame이 없다.

재현 스크립트, manifest와 시간/frame 감사 결과를 이 폴더에 보존한다. 원본 bag과 snapshots.json/objects.csv는 저장소의 data/ 제외 규칙에 따라 연구실·Mac의 별도 출력에 보존한다. 검증 예: python3 verify_sloam_bundle.py <로컬 출력 폴더> --offline. 예상 결과는 snapshots=20, object_rows=1302, labels=[(-2.0,590),(-1.0,712)]이다.

시각 감사에서 원본 점군과 odometry는 각각 1,001개이고 같은 순번의 header stamp 차이가 1,000쌍에서 0.01초 이하다. 점군 frame은 body, odometry는 camera_init→body다. 20개 bundle은 첫 점군 header보다 약 5.101초 뒤부터 발행됐다. 이것만으로 개별 점군 객체와 7D 지도 객체의 대응을 증명할 수 없다. 다음 검증 계획은 SIDECAR_PLAN.md를 참조한다. 이번 결과는 데이터 인터페이스 검증이며 SlideGraph·CLIPPER나 loop closure 성능 결과가 아니다.
