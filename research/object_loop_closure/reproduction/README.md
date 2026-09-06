# SlideSLAM 재현 준비

상태: 절차 초안. 이 폴더에는 SlideSLAM 소스 복사본이나 재현 성공 로그가 없습니다.

1. [공식 저장소](https://github.com/KumarRobotics/SLIDE_SLAM)의 README와 사용할 revision을 확인합니다. 대화에서 확인한 master는 Ubuntu 20.04/ROS Noetic 기준이며 ROS2 포트와 실험을 혼합하지 않습니다.
2. 사용할 정확한 upstream commit SHA, submodule SHA, Docker image digest를 run manifest에 기록합니다. latest 태그만으로 재현 버전을 고정했다고 보지 않습니다.
3. 공식 안내에 따라 별도 workspace에 clone/build합니다. 이 저장소의 third_party 디렉터리는 로컬 외부 소스용이며 버전 기록 없이 소스를 복사해 넣지 않습니다.
4. 공식 processed-data demo를 먼저 확인하고, 실제 sensor front-end 실행과 구분합니다. 데이터 파일 checksum·sequence·frame 범위·모델 weights 출처를 기록합니다.
5. 원 논문의 SemanticKITTI 05/07 inter-robot 분할을 재현할 때는 V-K의 GT segmentation, SuMa++ 초기 pose, 분할 조건을 확인합니다. 이 절차는 single-robot chronological retrieval 평가와 다릅니다.
6. 정상 실행 명령, 환경, 로그, 산출 object map, 처리 frame 수, 종료 상태, 결과를 연결해야 재현 완료로 기록합니다.

## 소스 추적 지점

- backend/multi_robot_utils_launch: 실행 구성
- backend/sloam/clipper_semantic_object: triangulation descriptor와 CLIPPER 수정본
- backend/sloam/src/core: 핵심 흐름
- backend/sloam/src/factorgraph: 최적화
- backend/sloam/src/objects: 객체 모델
- backend/sloam/params: 설정

이 목록은 대화에서 확인한 디렉터리이며 함수별 call graph 추적 완료를 뜻하지 않습니다.

## 재현 증거

- [ ] 코드 commit, dirty 상태, 변경 patch
- [ ] OS/ROS/compiler/Python, dependency·image digest
- [ ] 실제 실행 명령·launch·yaml과 SHA256
- [ ] 데이터·weights 출처, checksum, split
- [ ] object map의 좌표계·단위·관측 시점·객체 속성 스키마
- [ ] stdout/stderr, 처리 수·실패·runtime
- [ ] 원문 표와 동일 조건인지, 차이가 있다면 원인

[SlideSLAM 원문](https://natanaso.github.io/ref/Liu_SlideSLAM_TRO25.pdf)
