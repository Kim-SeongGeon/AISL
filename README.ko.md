# AISL의 여정

[![KR](https://img.shields.io/badge/README-한국어-blue)](./README.ko.md)
[![EN](https://img.shields.io/badge/README-English-red)](./README.md)

<img src="https://capsule-render.vercel.app/api?type=waving&color=413fd9&height=150&section=header&text=내가%20가고%20싶은%20회사에%20취직하는%20날까지!&fontSize=32" />

## 🧠 AISL 프로젝트에 대해서

### 🎯 주요 목표

### 🧰 도구

### 🛠 기술 스택
**Languages**  
![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=Python&logoColor=white)

<p><br></p>

---

## 2026년 7월 14일

### 📝 할 일 (2026-03-18)

- [ ] FAST-LIO 논문 공부

### 📌 메모

- Bayes Filter란?
  - Bayes Filter를 이야기 하기 전 우선 베이즈 정리(Bayes' theorem)가 무엇인지 간단히 알아보자.
  - 확률 시간에 들어볼 법한 베이즈 정리는 이전의 경험과 현재의 증거를 토대로 어떤 사건의 확률을 추론하는 과정을 이야기한다. 이 말을 조금 더 확률에 나오는 용어들을 활용해서 이야기하면 prior와 likelihood를 이용하여 posterior를 구할 수 있다는 의미이다.
  - Bayes Filter는 이러한 Bayes' theorem를 반복적으로 사용하는 Filter로 이해하면 된다.
  <img src="https://github.com/Kim-SeongGeon/AISL/blob/main/Image/State Estimation.png" width="400"/>

  - State Estimation이란 $t$라는 시간에서 로봇의 상태 $x$를 로봇의 관찰값(observation) $z$와, 로봇의 Control command $u$에 의해서 결정하게 되는 것이다.
  - 위 식은 1부터 $t$까지 주어진 observation $z$와 control command $u$를 고려하여 $t$번째 로봇의 상태 $x$를 추정하는 것이다.
  - 여기에 Recursive의 의미를 붙이면 로봇의 상태 $x_{t-1}$를 활용해서 로봇의 상태 $x_t$를 추정하는 것이다.
  - Bayes Filter의 가장 유명한 예제인 Robot의 위치 찾는 것을 예를 들어 알아보자.
  <img src="https://github.com/Kim-SeongGeon/AISL/blob/main/Image/Bayes Filter example_1.png" width="400"/>

  - 로봇은 1차원 공간을 가정하고, Door인지 아닌지 판단할 수 있다. 그리고 Global Environment에 대해 아무것도 모르는 상태라고 해보자. 처음은 아무도 모르는 상태이기 때문에 로봇의 위치를 Uniform distribution으로 나타낼 수 있다.
  - 로봇이 움직이면서 문을 관찰했을 경우, $bel(x)$는 아래와 같이 변한다. (문을 관찰했으므로 문 앞에 로봇에 위치가 있을 확률이 높다고 판단하는 것이다.)
  <img src="https://github.com/Kim-SeongGeon/AISL/blob/main/Image/Bayes Filter example_2.png" width="450"/>

  - 구한 $bel(x)$를 가지고 로봇을 앞으로 조금 움직여보자.
  <img src="https://github.com/Kim-SeongGeon/AISL/blob/main/Image/Bayes Filter example_3.png" width="400"/>

  - 우리가 예측했던 $bel(x)$의 모양은 그대로이지만 로봇이 정확하게 얼마나 움직였는지 불확실성이 존재하기 때문에, 확률 분포가 조금 퍼져있는 형태로 나타내졌다.
  - 그리고 또 다시 한 번 새로운 관찰값을 받아보자.
  <img src="https://github.com/Kim-SeongGeon/AISL/blob/main/Image/Bayes Filter example_4.png" width="400"/>

  - 새로운 관찰값 $p(z|x)$와 기존의 $bel(x)$의 확률 분포를 합쳐 새로운 $bel(x)$를 구할 수 있다.
  - 이처럼 로봇의 이전 $bel(x)$ 값과 observation 값 $(p(z|x))$을 활용해서 현재의 $bel(x)$ 값을 나타내는 것이 Bayes Filter이다.

- Bayes Filter 식 유도
  - 먼저 식 유도를 하기 전 확률에 대한 기본적인 지식을 Remind 해보면,
    1. Bayes' theorem
    2. Markov Property / Assumption
    3. Law of Total Probability
   
  - Bayes' theorem
  - 우리가 지금까지 봤던 베이즈 정리(Bayes' theorem)를 한 장의 슬라이드로 정리하면 아래와 같다.
  

### ✅ 결론

- 

<p><br></p>

---

## 2026년 3월 18일

### 📝 할 일 (2026-03-18)

- [X] VINS 논문 읽기
- [ ] 연구실 프로젝트 구현(초소형 지상로봇 군집운용 통제기술)

### 📌 메모

- 

### ✅ 결론

- 

<p><br></p>

---


## 2026년 3월 17일

### 📝 할 일 (2026-03-17)

- [X] VINS 논문 읽기

### 📌 메모

- 1. Introduction
  - VINS-Mono는 Monocular camera와 IMU를 결합했을 때 단순히 카메라를 썼을 때보다, 여러 장점이 있다고 소개함
    - Scale 값을 얻을 수 있음(Roll, Pitch angle도 얻을 수 있음)
    - 카메라쪽에서 Tracking하기 어려운 환경(Illumination Change, Textureless Area, or Motion Blur)에서도 IMU 센서의 도움을 받아 Tracking을 수행할 수 있음
    - Camera, IMU 모두 저가로 구입할 수 있는 센서
  - 이러한 장점이 있는 반면 큰 Issue들도 존재
    - 초기화 과정이 힘듦
      - : 직접 거리를 측정할 수 있는 센서가 없기 때문에, Visual Structure와 Inertial Measurement의 결합이 어려움
    - VINS(Visual-Inertial Navigation System)은 Non-linear한 System
      - : 대부분의 경우 시스템은 고정 위치에서 시작해야 하며 처음에는 천천히 조심스럽게 움직여야 하므로 실제로 사용이 제한됨
    - VIO(Visual-Inertial Odometry)의 경우, drift 현상이 필연적임
  - 따라서 이런 Issue들을 해결하기 위해 VINS-Mono에서는 다음과 같은 Contribution이 존재함
    - 초기 상태(Initial States)를 모르더라도 초기화할 수 있는 방법을 제안
    - Tightly-Coupled 방식의 Sensor Fusion, Optimization-based Estimation 방법
    - 실시간이 보장된 Relocaization and 4 DOF(Degrees-Of-Freedom) global pse graph optimization
    - pose graph를 저장하고 불러오고 다른 local pose graph와 합칠 수 있음

- 2. Overview
  - VINS-Mono의 전반적인 system은 아래 그림과 같음
  <img src="https://github.com/Kim-SeongGeon/AISL/blob/main/Image/Visual-InertialStateEstimatorDiagram.png" width="450"/>
  
  - VINS-Mono는 우선 Measurement Preprocessing 과정을 거침. 이미지로부터 feature를 뽑아내고, Tracking을 하면서 연속적인 두 이미지 사이에 IMU Measurements를 Preintegrated하는 과정을 거침
  - Measurement Preprocessing 과정이 끝나면 초기화(Initialization) 과정을 거침. 추후 Non-linear Optimization을 할 때 필요한 값들을 모두 구함. 예를 들어, pose, velocity, gravity vector, gyroscope, bias and 3D 특징 점의 위치 등을 구하게 됨
  - 초기화 값으로 구한 값을 가지고 Relocalization Module이 있는 Visual-Inertial Odometry Module은 Pre-integrated된 IMU 측정값과 Feature Observations를 tightly-coupled 방법으로 fusion을 진행함
  - VINS-Mono에서는 Monocular Camera와 IMU 값을 이용하여 초기화하는 방법, Keyframe을 고르는 방법, Tracking을 잘 수행하는 방법등을 제안했으며, Loop Closure와 Pose Graph Reuse 모듈까지 만들어 전체적인 SLAM System을 구축함
  - 이 논문에서는 사용하는 Notation은 다음과 같음:
    - $()^c$ : camera frame
    - $()^w$ : world frame
    - $()^b$ : IMU frame
    - $q$ : 쿼터니언, $R$ : Rotation Matrix
    - $p$ : Translation vector
    - $b_k$ : $k$번째 이미지에서의 IMU(Body) frame
    - $c_k$ : $k$번째 이미지에서의 Camera frame
    - $\otimes$ : 쿼터니언끼리의 곱
    - $\hat{(\cdot)}$ : 추정 값 or noisy measurement
   
- 3. Measurement Preprocessing
  - Visual Measurement와 IMU Measurement의 전처리 과정을 자세하게 살펴보면, Visual Measurement에서는 연속적인 이미지에서의 Tracking을 시도하고, 현재 frame에서 새로운 특징점을 찾음. IMU Measurements에서는 연속적인 두 이미지에서 Pre-integration 과정을 거침
  - Vision Processing Front End
    - 새로운 이미지가 들어오면, KLT Sparse Optical Flow Algorithm을 수행함. Feature를 찾을 때는 GoodFeatureToTrack() 함수를 사용함. 이는 OpenCV()에 있는 함수. 한 이미지당 Feature의 개수는 100~300개 정도를 유지함. Detector는 feature간 너무 붙어 있지 않도록 uniform feature distribution를 적용함
      - KLT Sparse Optical Flow는 VINS-Mono의 시각적 전처리 단계에서 기존에 찾은 특징점들이 다음 프레임에서 어디로 갔는지 쫓아가는(Tracking) 핵심 알고리즘
        - KLT 알고리즘의 3개의 가정
          1. 밝기 불변(Brightness Costancy): 카메라가 아주 짧은 시간동안 움직였을 때, 특정 물체의 밝기나 색상은 변하지 않는다고 가정
          2. 아주 작은 움직임(Small Motion): 시간이 짧으므로, 물체나 픽셀이 아주 조금만 이동했다고 가정함
          3. 공간적 일관성(Spatial Coherence): 이것이 KLT의 가장 핵심적인 아이디어. 하나의 픽셀만 추적하면 노이즈 때문에 실패하기 쉬움. 그래서 '이웃한 픽셀들은 모두 같은 방향, 같은 속도로 움직인다'고 가정함
        - 왜 "Sparse" Optical Flow 인가?
          => 화면 안의 모든 픽셀 200만 개의 움직임을 다 계산하는 것을 'Dense Optical Flow'라고 함. 하지만 이는 계산량이 너무 많아 실시간으로 작동해야 하는 로봇이나 드론에는 쓸 수 없음
        - 그래서 VINS-Mono는 화면에서 추적하기 쉬운 모서리(코너) 같은 뚜렷한 특징점 100~300개 정도만 콕콕 집어서 띄엄띄엄 추적함. 계산량이 획기적으로 줄어들고 속도가 엄청나게 빨라짐. VINS-Mono는 매 프레임 KLT로 기존 특징점들을 빠르게 추적하고, 시야에서 벗어난 개수가 줄어들면 그때 새로운 코너를 찾아서 보충함
      - RANSAC 알고리즘을 이용하여 Outlier 제거를 거친 후, 특징이 추출된 이미지를 unit sphere(단위 구)에 투영을 시킴
        - RANSAC(Random Sample Consensus)은 수많은 데이터 속에 섞여 있는 '가짜 데이터(Outlier)'를 걸러내고 '진짜 데이터(Inlier)'들만 찾아내어 정답을 맞히는 알고리즘
        - 앞서 배운 KLT로 특징점들을 추적하다 보면, 카메라가 움직인게 아니라 실제로 움직이는 자동차를 쫓아가거나, 빛 반사 때문에 엉뚱한 곳을 짚는 경우가 생김. 이런 '거짓말하는 점'들을 무시하고 카메라가 진짜 어떻게 움직였는지 찾아내는 것이 RANSAC의 역할임
          - VINS-Mono에서 RANSAC이 하는 일
          - VINS-Mono는 KLT로 추적된 점들 사이에서 이 과정을 수행
            - 입력: 이전 프레임과 현재 프레임에서 매칭된 수백 개의 특징점 쌍
            - 가설: 무작위로 몇 개의 점만 골라서 "카메라가 이만큼 회전하고 이동했을 거야"라는 모델(Fundamental Matrix 등)을 만듦
            - 검증: 그 모델을 적용했을 때, 나머지 점들이 "맞아, 나도 그 위치쯤에 있어!"라고 동의하는지 확인함
            - 결과: 카메라의 실제 움직임과 맞지 않게 튀는 점들(Outlier)은 이때 가차 없이 삭제됨
          - RANSAC이 좋은 이유
            - 보통의 알고리즘은 모든 데이터를 평균 내어 계산하려고 함. 그래서 데이터 중에 엄청나게 큰 에러(Outlier)가 하나만 섞여 있어도 결과값이 완전히 망가짐
            - 반면, RANSAC은 "어차피 가짜가 섞여 있을 테니, 운 좋게 진짜들만 뽑힐 때까지 여러 번 시도해 보겠다"는 전략을 취함. 그래서 데이터의 절반이 가짜라도 시간만 충분하면 정답을 찾아낼 수 있는 아주 강력하고 끈질긴 알고리즘
      - 이 과정에서 Keyframe 선별도 하게 되는데 두 가지 기준을 가지고 Keyframe을 선별함
        - Last Frame과 Current Frame 간에 특징점들끼리의 픽셀 차이(Parallax)가 일정 threshold 이상일 경우 새로운 Keyframe으로 구분
        - Tracking quality에 따라 구분
      - 특징점끼리의 픽셀 차이를 여기서 Parallax(시차)라고 표현. 이러한 기준을 선정한 이유는 Triangulate를 진행할 때 충분한 Feature 수를 확보하기 위해서이다. 또한 Parallax를 구할 때 Rotation만 일어났을 때만을 대비하여 IMU Measurement에서 측정된 short-term integration of gyroscope measurements를 보상하여 Parallax를 계산함
      - Tracking Quality는 Visual Feature Point의 수로 판단을 할 수가 있는데, Tracking이 되고 있는 Feature Point의 수가 일정 threshold보다 아래로 떨어지면 새로운 feature들이 많이 생기고, 새로운 상황(이미지 및 장면)을 맞이했다고 이해할 수 있음. 따라서 새로운 상황이라고 판단하면 Keyframe을 선별한다고 이해하면 됨

### ✅ 결론

- 계속 읽기...

<p><br></p>

---

## 2026년 3월 16일

### 📝 할 일 (2026-03-16)

- [X] VINS 논문 읽기

### 📌 메모

- OpenVINS의 근원이 VINS의 논문을 찾아서 이 논문을 본격적으로 읽기로 결정
- [VINS-Mono: A Robust and Versatile Monocular Visual-Inertial State Estimator](https://arxiv.org/pdf/1708.03852)
  - 1. VINS-Mono의 핵심 철학: '모든 것을 한 번에 묶어서 푼다(Tightly-Coupled)'
    - : 과거에는 카메라가 계산한 위치 따로, IMU가 예측한 위치 따로 구해서 대충 섞는 방식(Loosely-Coupled)을 썼음. 하지만 VINS-Mono는 카메라가 본 특징점 오차(Vision-Residual)와 IMU가 측정한 가속도/각속도 오차(IMU Residual)를 하나의 거대한 방정식으로 묶어서 동시에 최적화함. 이 방식을 'Tightly-Coupled'라고 부름.
  - 2. 논문의 4단계 파이프라인(흐름도)
    - 1. 측정값 전처리(Measurement Preprocessing)
      - Vision: KLT 알고리즘으로 들어오는 이미지에서 특징점을 추적함
      - IMU Pre-Integration(사전 적분): IMU는 카메라보다 훨씬 빠름. 카메라 프레임 사이사이에 들어오는 수많은 IMU 데이터를 미리 하나로 뭉쳐놓는 기술임. 특히 VINS-Mono는 이때 IMU의 편향(Bias) 오차까지 실시간으로 보정하는 수식을 제안하여 정확도를 끌어올림
    - 2. 초기화(Estimator Initialization)
      - 카메라 한 대(Mono)를 쓰면 실제 거리(Scale)를 알 수 없음
      - VINS-Mono는 정지 상태가 아니라 로봇이 움직이는 와중(on-the-fly)에도 초기화를 성공시키는 강력한 알고리즘을 제안함. 카메라가 대충 그린 뼈대(Vision-Only SfM)와 IMU 데이터를 정렬시켜서 실제 크기(Scale), 중력 방향, 초기 속도, IMU 편향 값을 한 번에 찾아냄
    - 3. 슬라이딩 윈도우 기반 VIO(Local VIO)
      - 최적화 방식은 계산량이 너무 많아진다는 단점이 있음
      - 이를 해결하기 위해 과거의 데이터는 버리고 최근 N개의 핵심 프레임(Key Frame)만 창문(Window)안에 남겨두고 최적화하는 Sliding Window 기법을 사용함
      - 이때 오래된 데이터를 윈도우에서 그냥 삭제하지 않고, Marginalization(주변화)이라는 수학적 기법을 통해 과거 데이터가 품고 있던 정보(Prior)를 압축해서 현재 윈도우에 넘겨줌
    - 4. 4-DOF 글로벌 최적화(Relocalization & Pose Graph Optimization)
      - 아무리 최적화를 잘해도 오래 주행하면 오차가 누적됨
      - DBoW2를 이용해 이미 방문했던 장소를 인식(Loop Detection)하면, 현재 위치를 교정함
      - 가장 멋짐 점은 '4-DOF(x, y, z, yaw)'만 최적화한다는 것임. IMU가 중력을 게속 느끼고 있기 때문에 로봇의 기울어짐(Roll, Pitch)은 이미 절대적으로 정확하게 알고 있으므로, 굳이 계산을 낭비하지 않는 것임
     
### ✅ 결론

- 내 개인 연구 주제에도 연관성이 있는 논문으로 판단되어 계속 읽으면 될듯

<p><br></p>

---

## 2026년 3월 13일

### 📝 할 일 (2026-03-13)

- [X] 오늘 했던 데이터셋 외에 다른 데이터셋으로 테스트하기
- [X] OpenVINS 정확하게 공부하기

### 📌 메모

- OpenVINS에서 제공하는 데이터셋 중 3가지를 골라서 테스트해봄
  - 테스트할 데이터셋이 rosbag은 다운로드가 되지 않아 rosbag2로 다운로드하여 변환 후 rosbag play를 진행함
- OpenVINS는 이름에서 알 수 있듯이 'Open-Source Visual-Inertial Navigation System'의 약자로, 카메라(Visual)와 관성 측정 장치(IMU, Inertial)를 결합하여 로봇의 위치와 자세를 추정하는 플랫폼
  - 1. OpenVINS의 핵심: MSCKF 기반의 필터 방식
    - 가장 큰 특징은 MSCKF(Multi-State Constraint Kalman Filter) 알고리즘을 사용한다는 점
      - => MSCKF는 IMU와 Camera 센서를 사용하여 고정된 Feature에 대해서 measurement update(새로운 노이즈 센서 측정과 이전 예측 상태를 결합하여 개선되고 더 정확한 사후 추정치를 생성함)를 수행하여 odometry(휠 엔코더, IMU, 카메라 등 모션 센서 데이터를 사용하여 시작 위치를 기준으로 로봇이나 차량의 상대적인 위치와 자세 변화를 추정하는 기술)를 제공하는 알고리즘
    - ORB-SLAM과의 차이: ORB-SLAM은 주로 '최적화' 기반으로 전체 지도를 그리며 위치를 잡는다면, OpenVINS는 '필터' 기반임
    - 슬라이딩 윈도우: 모든 과거 데이터를 다 들고 있지 않고, 최근의 카메라 프레임 몇 개만 유지하면서 상태를 업데이트함. 그래서 계산량이 적고 실시간성이 매우 뛰어남
      
  - 2. 왜 OpenVINS를 쓸까?
    - 온라인 캘리브레이션(Online Calibration): 카메라와 IMU 사이의 상대적인 위치(Extrinsics)나 시간 차이(Time Offset)를 로봇이 움직이는 동안 실시간으로 스스로 보정함. 수동으로 값을 맞추는 수고를 덜어줌
    - 확장성: 모듈형 구조라 새로운 센서를 추가하거나 알고리즘 일부를 교체하기가 매우 쉬움
    - 정확도와 속도: EKF(Extended Kalman Filter)기반임에도 불구하고 최적화 기반 알고리즘에 뒤처지지 않는 높은 정밀도를 보여줌. 특히 자원이 제한된 드론이나 소형 로봇에서 강력함
      
  - 3. OpenVINS의 구조
    - Feature Tracking: 카메라 이미지에서 앞서 배운 FAST 같은 코너를 찾아 추적함
    - IMU Preintegration: IMU의 가속도/자이로 데이터를 쌓아서 로봇의 대략적인 움직임을 예측함
    - State Update: 카메라 정보와 IMU 예측치를 합쳐서 로봇의 정확한 위치(x, y, z)와 자세(q)를 확정함

### ✅ 결론

- OpenVINS 감이 완벽히 잡히지 않아 관련 논문 읽기
- ORB-SLAM 구현해보기

<p><br></p>

---

## 2026년 3월 12일

### 📝 할 일 (2026-03-12)

- [X] OpenVINS 플랫폼 테스트

### 📌 메모

- EuRoC에서 제공하는 데이터셋을 사용했는데 현시점 기준으로는 찾을 수 없어서 갖고 있는 KITTI에서 제공하는 public datasets을 기반으로 테스트하였지만, launch 파일 실행하는 터미널에서 지속적으로 보이는 에러와 실질적으로 rviz 화면에서 아무것도 보이지 않았음
  - 문제점의 원인을 알아보니 subscribe.launch 파일을 실행한 터미널에 뜬 내용을 보면 [Init]: failed static init: platform moving too much 로 KITTI 데이터셋에서 초기 동작으로 인해 정적 초기화 조건이 위반되어 오류가 발생한 것으로 보이고, KITTI의 원본 캘리브레이션 값은 OpenVINS가 사용하는 Kalibr 형식과 다름. 단순히 토픽 이름만 바꾼다고 되는 것이 아니라, KITTI용 가속도/자이로 노이즈 모델과 카메라-IMU 간의 변환 행렬(T)을 직접 계산해서 넣어주지 않으면 필터가 즉시 발산(Divergence)하게 됨
- OpenVINS에서 제공하는 튜토리얼을 샅샅이 살펴보던 중 ros2 기준에 데이터(현시점 기준 ros1은 다운로드 불가, https://docs.openvins.com/gs-datasets.html <- 참고)는 zip파일로 다운로드 할 수 있어 다운 후 ros2 파일을 ros1으로 convert 해줄 수 있는 명령어가 있어 변환하고 테스트했더니 정상적으로 성공
  
<img src="https://github.com/Kim-SeongGeon/AISL/blob/main/Image/OpenVINS(KITTI).png" width="250"/>
<img src="https://github.com/Kim-SeongGeon/AISL/blob/main/Image/OpenVINS(EuRoC).png" width="250"/>

### ✅ 결론

- 오늘 했던 데이터셋 외에 다른 데이터셋으로 테스트하기
- OpenVINS 정확하게 공부하기

<p><br></p>

---

## 2026년 3월 11일

### 📝 할 일 (2026-03-11)

- [X] 공용 데이터셋을 기반으로 SLAM 테스트
- [X] 교수님께 받은 논문 읽기

### 📌 메모

- Visual SLAM 기반으로 돌리게 되면 내가 원하는 건 ORB-SLAM 이지만 설치 때 의존성 문제가 많다고 해서 Visual SLAM 기반으로 돌려본 경험이 있는 랩원에게 OpenVINS 플랫폼를 추천받아 우선 이것부터 SLAM 테스트해보기로 결정(https://github.com/rpng/open_vins <- 참고)
  - 중간중간에 메모리 부족 문제를 여러 번 겪어서 많이 힘들었지만, OpenVINS 시뮬레이션을 성공적으로 구동함
  - 구동 완료 후 나온 두 화면은 OpenVINS가 로봇의 움직임(궤적)을 얼마나 정확하게 추정하고 있는지를 보여주는 성능 지표와 시각화 결과임
  - 첫 번째 이미지: 궤적 시각화(로봇이 움직인 경로를 2D 평면에 그린 것), 두 번째 이미지: 추정 정확도(시뮬레이션이 실시간으로 돌아가면서 "내가 계산한 위치가 실제와 얼마나 차이 나는가?"를 숫자로 보여주는 데이터 창)
  - 교수님께 받은 논문은 멀티 로봇 시스템에서 특징 지도 병합의 정확성과 효율성을 크게 향상시키는 비반복적인 VSLs 기반 기술을 제시하며, 이는 실시간 로봇 시스템 구현에 중요한 기여를 하는 내용

<img src="https://github.com/Kim-SeongGeon/AISL/blob/main/Image/Trajectory%20Visualization.jpeg" width="250"/>
<img src="https://github.com/Kim-SeongGeon/AISL/blob/main/Image/Estimation%20Accuracy.png" width="250"/>

### ✅ 결론

- OpenVINS 프로젝트 후에 이어서 할 내용 진행
- VSLs 기반 기술 논문 계속 읽기

<p><br></p>

--- 

## 2026년 3월 10일

### 📝 할 일 (2026-03-10)

- 교수님과 진지한 면담(개인 연구 주제 선택 관련)
- 연구실 내에 공용 데이터셋을 기반으로 SLAM 테스트

### 📌 메모

- 교수님께서도 내가 생각한 주제들을 좋게 봐주시고 2번째는 다른 랩원이 하고 있어서 1번과 3번을 잘 연관지어서 진행하고 관련 조언을 해주심
  - 1번째 주제에서 '통신 제약' 조건은 통신 분야의 지식이 많이 부족하므로 패스 (혹은 약간의 제약으로 변경)
  - 1번째 주제를 주요 주체로 잡아서 3번째 주제까지 확장, 3번째는 석사 논문으로, 그리고 임무 계획은 AI 사용이 아니면 굳이임
  - Sparse(featrue 포함) Map Merging은 상업 분야에서는 굳이, 국방 분야에서는 필요성이 있고 실용적인 연구로 보임
  - 시험은 알고리즘을 중요시로 해서 시뮬레이션(Matlab 등)부터 시작
  - baseline 잘 잡기
  - ICP+VSLs 조합 잘 해보기
  - 기하학적 정보(랜드마크의 위치 정보) + 클래스 정보
- 공용 데이터셋을 기반으로 SLAM 테스트를 시도했지만, 예상치 못한 문제들에 많이 부딪혀 내일 관련 공부를 했던 랩원에게 도움 요청함

### ✅ 결론

- 교수님께서 보내주시고 추천해주신 논문들 꾸준히 읽고 공부하기
- 내일은 공용 데이터셋 기반의 SLAM 테스트 배우고 확실하게 내 것으로 만들기

<p><br></p>

---

## 2026년 3월 09일

### 📝 할 일 (2026-03-09)

- 정확한 개인 연구 주제를 선택하기 위한 연구

### 📌 메모

- 학부 연구생부터 해오던 멀티로봇 관련 프로젝트를 석사과정 1학년에 받게 되어 이쪽 분야 중에 내용으로 개인 연구를 진행해야겠다고 생각       
- 방산 기업 취업이 최종 목표이므로 내가 원하는 방산 기업에서 원하는 SW R&D 인재상이 무엇인지 어떤 주제를 선택해야 그 기업에 들어가서 다재다능하게 해낼 수 있을지 조사
  - 취업을 우선시 생각해보면 C++/Python 기반 알고리즘 구현 능력, '무인/로봇' 관련 실질적인 프로젝트와 논문(특히 방산 및 자율주행 연관)과 다양한 로봇 플랫폼(지상 4족, UGV, USV 등)에 이식 가능한 실전형 SW 아키텍처 이해가 필요
  - 멀티 로봇 SLAM을 방위나 전장에서 사용하게 되면 고려되는 환경 특성은 GNSS 취약(실내, 지하, 재난/전장, 전자전 환경), 통신 지연 및 두절(분산하고 견고한 SLAM 및 군집 필요), 다수 이기종 로봇(4족 보행, UGV, 드론, USV 등) 혼합과 센서 제한이나 부분적으로 가려지는(연막, 먼지, 어두운 환경, 제한된 FoV LiDAR 등) 내용들이 있음
  - 이걸 기준으로, 방산 기업 로봇/무인 체계에 잘 맞고 논문 및 포트폴리오로도 괜찮은 주제를 3개 정도 압축해 봄
  1. 통신 제약을 고려한 분산 멀티 로봇 SLAM : 중앙 서버 없이(또는 최소 의존) 로봇들이 부분 맵과 포즈를 주고받으며, 통신 끊김이나 지연 상황에서도 점진적으로 글로벌 맵을 일치시키는 분산 혹은 준-분산 SLAM
  2. 제한된 센서 및 시야에서의 강인 멀티 로봇 SLAM : 제한된 FoV LiDAR, 노이즈가 심한 IMU, 카메라 가려짐 등 방산 환경에서 흔한 센서 조약 조건에서 협력적으로 인식 성능을 올리는 멀티 SLAM
  3. 멀티 로봇 SLAM 기반 군집 임무 계획(MUM-T 염두) : 멀티 SLAM 결과(공유 맵, 각 로봇의 불확실도)를 직접 군집 경로 계획, 탐색 그리고 감시 임무 할당에 연결하는 연구
  - 이 중에서 석사 2년 안에 논문과 데모 구현을 한다고 하면, '통신·센서 제약 환경을 고려한 분산 멀티 로봇 SLAM 및 정찰 임무 계획'을 하나의 큰 주제로 잡고, 1년 차에는 SLAM 쪽을, 2년 차에는 임무 계획/군집 쪽을 붙이는 구조가 알맞다고 판단
 
- 간단한 석사 1~2년차 로드맵(연구+취업 준비)
  - 1년차: 기반 다지기 + 1편 수준 결과
    - 0-6개월
      - 이론·코드: ORB-SLAM 계열, pose graph SLAM, LAMP/LAMP2.0 같이 검증된 멀티 로봇 SLAM 시스템 분석 및 구현 연습
      - 언어/도구: C++/Python, ROS2, Git, 기본 PCL/OpenCV/로봇 시뮬레이터(Gazebo/Ignition, Isaac Sim 등)
    - 6-12개월
      - 소규모 멀티 로봇(예: 3대 UGV 혹은 1 UGV + 1 드론) 시뮬레이션에서 분산/준-중앙집중식 SLAM 구현
      - 국내 학회에 논문 또는 포스터 한 편 정도를 목표로
  - 2년차: 멀티 로봇 + 군집/임무 계획까지 확장
    - 13-18개월
      - 센서 제약(제한 FoV LiDAR, 카메라 occlusion, 통신 dropout)을 넣은 시뮬레이션 환경 구성
      - 이 환경에서 robust loop closure, 통신량 최소화 전략, 분산 최적화 개선
    - 18-24개월
      - SLAM 결과를 사용해 정찰/감시 임무의 경로 계획·역할 분담 알고리즘 개발
      - 국제 학회 + 석사 논문 완성

### ✅ 결론

- 우선 생각한 3가지 방식을 교수님과 진지한 대화를 해보고 정확한 방향을 잡아야겠음
- 그리고 연구실 내에 쉽게 사용할 수 있는 데이터셋을 가지고 간단한 테스트로 SLAM 감을 잡아야겠음

<p><br></p>

---
