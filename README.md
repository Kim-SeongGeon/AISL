# AISL's journey

## Master's individual research

[Reproduction, experiment configurations, and evaluation scripts](./research/object_loop_closure/) · [Learning, papers, research decisions, and lab meetings (Notion)](https://app.notion.com/p/388c388e8d7181259571f054730a8512)

Added 2026-09-06. The research folder contains preparation materials and a tested offline metric utility; no SlideSLAM reproduction or new-descriptor benchmark is claimed. Existing study records remain below.

[![KR](https://img.shields.io/badge/README-한국어-blue)](./README.ko.md)
[![EN](https://img.shields.io/badge/README-English-red)](./README.md)

<img src="https://capsule-render.vercel.app/api?type=waving&color=413fd9&height=150&section=header&text=Until%20the%20day%20I%20get%20a%20job%20at%20the%20company%20I%20want%20to%20go%20to!&fontSize=32" />

## 🧠 About AISL PROJECT

### 🎯 Main Objectives

### 🧰 Tools

### 🛠 Tech Stack
**Languages**  
![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=Python&logoColor=white)

<p><br></p>

---

## July 21, 2026

### 📝 To-Do List (2026-07-21)

* [x] Complete FAST-LIO practice

### 📌 Notes

* Based on the results obtained from the FAST-LIO practice conducted so far, the following points were confirmed.

  * Both LiDAR and IMU are required for FAST-LIO to initialize and operate normally
  * The relationship among the number of processed points, CPU usage, and map detail according to changes in filter_size_surf
  * The relationship between ikd-Tree size and registration stability according to changes in filter_size_map
  * Real-time processing without message loss at up to 8x playback speed, corresponding to approximately 80 Hz input
  * The need to verify the closed-loop condition and GT (Ground Truth) before evaluating return-to-start error
  * The limitation that FAST-LIO is an Odometry system that does not include Loop Closure
* **Overall Conclusion of FAST-LIO Practice**

  * In this practice, FAST-LIO was built in an Ubuntu 20.04 and ROS Noetic environment, and LiDAR-Inertial Odometry and 3D map generation were verified using a publicly available Livox Avia rosbag. Rather than simply executing the system, changes according to sensor input conditions, current scan downsampling, global map downsampling, and rosbag playback speed were compared.
  * Normal initialization and Odometry estimation were possible only when both LiDAR and IMU data were provided. Through this, the roles of the IMU in state prediction and motion compensation and the LiDAR in scan-to-map correction were confirmed. As filter_size_surf increased, the number of points processed in each frame decreased, but excessive downsampling caused the loss of detailed structures such as walls and columns.
  * As filter_size_map increased, the number of ikd-Tree points decreased. However, CPU usage did not decrease in proportion to the number of map points, and at 1.0 m, `No Effective Points!` warnings and reduced registration stability were observed. In this environment, the default value of 0.5 m provided the best balance between map size and structural preservation.
  * In the rosbag playback speed experiment, 487 Odometry messages and identical pose estimation results were generated under all conditions from 0.5x to 8x playback speed. CPU usage increased, but memory usage remained constant at approximately 174–175 MiB, and no noticeable post-completion delay occurred. Therefore, under the experimental environment, FAST-LIO was considered capable of processing LiDAR input at a rate of at least approximately 80 Hz.
  * Long-duration data were analyzed to measure return-to-start error, but the dataset could not be used for drift evaluation because the ending position and orientation did not return to the starting state. This confirmed that accumulated error should not be determined solely from the start-to-end distance of Odometry and that a closed-loop trajectory or Ground Truth must be available beforehand.
  * FAST-LIO is a computationally efficient LiDAR-Inertial Odometry system, but it does not include place recognition or Pose Graph Optimization. Therefore, to globally correct accumulated errors generated during long-distance travel, FAST-LIO must be combined with Scan Context, Loop Closure, or a separate SLAM backend.

### ✅ Conclusion

* Through this practice, the following points were learned.

  * Parameters cannot be interpreted using the simple relationship that smaller values are always more precise and larger values are always faster.
  * A reduction in the number of map points does not necessarily lead to a reduction in overall CPU usage.
  * An environment-specific trade-off is required between computational efficiency and map quality.
  * Real-time performance should not be evaluated solely based on the number of output messages.
  * Drift evaluation requires either a closed-loop condition or Ground Truth.
  * The strength of FAST-LIO is fast local Odometry, while global consistency correction is a separate problem.


<p><br></p>

---

## July 20, 2026

### 📝 To-Do List (2026-07-20)

* [x] Conduct FAST-LIO experiments

### 📌 Notes

### FAST-LIO Practice

* Experiment 4: Measurement of Return-to-Start Error and Data Validity Verification

  1. Experimental Objective

  * Verify the accumulated positional error that occurs when FAST-LIO returns to the starting point after traveling along a long trajectory.
  * Calculate the difference between the starting and ending positions and analyze the drift ratio relative to the total traveled distance.
  * However, calculating the return-to-start error requires that the sensor actually return to the same position and orientation as the starting state.

  2. Dataset

  ```
  HKU_MB_2020-09-20-13-34-51.bag
  ```

  * A dataset with a longer execution time than the **2020-09-16-quick-shack.bag** used in the previous experiment was selected.
  * The dataset contains the following topics.

  ```
  /livox/lidar
  /livox/imu
  ```

  * After playing the bag file, the /Odometry topic published by FAST-LIO was saved in CSV format.

  ```
  rostopic echo -p /Odometry > hku_mb_odom.csv
  ```

<img src="https://github.com/Kim-SeongGeon/AISL/blob/main/Image/HKU_MB_2020-09-20-13-34-51bag_rviz.png" width="400"/>

3. FAST-LIO Configuration

* To reduce unnecessary memory usage when processing a long-duration dataset, the PCD saving function was disabled.

```
pcd_save:
  pcd_save_en: false
  interval: -1
```

* The default values were used for the downsampling parameters.

```
<param name="filter_size_surf" type="double" value="0.5" />
<param name="filter_size_map" type="double" value="0.5" />
```

4. Analysis Method

* The first Odometry position was defined as the starting position $\mathbf{p}_0$, and the last position was defined as the ending position $\mathbf{p}_f$.

**XY Start-to-End Distance**

$$ E_{xy} = \sqrt{(x_f - x_0)^2 + (y_f - y_0)^2} $$

**3D Start-to-End Distance**

$$ E_{3D} = \sqrt{(x_f - x_0)^2 + (y_f - y_0)^2 + (z_f - z_0)^2} $$

**Odometry-Based Accumulated Travel Distance**

$$ L = \sum_{i=1}^{N-1} \sqrt{(x_{i+1} - x_i)^2 + (y_{i+1} - y_i)^2 + (z_{i+1} - z_i)^2} $$

If the dataset is confirmed to return to the starting point, the drift ratio can be calculated using the following equation.

$$ D = \frac{E_{3D}}{L} \times 100 $$

However, if the actual trajectory does not return to the starting point, $E_{3D}$ includes both the positional difference caused by the actual motion and the accumulated FAST-LIO error. Therefore, the drift ratio cannot be calculated.

5. CSV Data Verification

| Item                             | Result                |
| -------------------------------- | --------------------- |
| Number of Odometry messages      | 2,602 messages        |
| Recording duration               | 260.10 seconds        |
| Average publishing frequency     | Approximately 10 Hz   |
| Maximum inter-frame displacement | Approximately 0.102 m |
| Abnormal positional jumps        | Not detected          |

* A total of 2,602 Odometry messages were recorded continuously, and no abnormally large positional changes were detected between frames. Therefore, the CSV recording and FAST-LIO processing were considered to have been performed normally.

6. Starting and Ending Positions

| Category          | X(m)     | Y(m)     | Z(m)    |
| ----------------- | -------- | -------- | ------- |
| Starting position | -0.0052  | 0.0014   | 0.0122  |
| Ending position   | 59.2596  | 22.9559  | 2.2246  |
| Change            | +59.2648 | +22.9545 | +2.2123 |

* The ending position was approximately 63.55 m away from the starting position in the XY plane. In addition, the elevation at the ending point was approximately 2.21 m higher than at the starting point.

7. Position and Travel Distance Analysis

| Metric                         | Measured Value | Interpretation                           |
| ------------------------------ | -------------- | ---------------------------------------- |
| Accumulated XY travel distance | 96.1665 m      | Odometry-based estimate                  |
| Accumulated 3D travel distance | 98.7626 m      | Odometry-based estimate                  |
| XY start-to-end distance       | 63.5548 m      | Cannot be used as return-to-start error  |
| 3D start-to-end distance       | 63.5933 m      | Cannot be used as return-to-start error  |
| Elevation change               | +2.2123 m      | Did not return to the starting elevation |

* The accumulated travel distance is not GT (Ground Truth), but the sum of the distances between consecutive positions estimated by FAST-LIO.

8. Comparison of Starting and Ending Orientations

| Orientation | Start    | End        | Change                 |
| ----------- | -------- | ---------- | ---------------------- |
| Roll        | -0.0146° | -14.0471°  | Approximately -14.03°  |
| Pitch       | 0.0465°  | 2.3240°    | Approximately +2.28°   |
| Yaw         | -0.0039° | -155.1641° | Approximately -155.16° |

* The total rotational difference between the starting and ending orientations, calculated using quaternions, was as follows.

$$ E_R = 155.0646° $$

* Because the ending orientation differed from the starting orientation by approximately 155°, the sensor did not return to its initial state in either position or orientation.

9. Feasibility of Drift Calculation

* Simply substituting the measured values produces the following result.

$$ \frac{63.5933}{98.7626} \times 100 = 64.3901% $$

* However, this value is not the drift ratio of FAST-LIO.
* Because the actual sensor did not return to the starting point, the 63.5933 m distance contains the following two components.

$$ Start-to-end distance = Actual trajectory displacement + FAST-LIO accumulated error $$

* Without GT, these two components cannot be separated. Therefore, `64.3901%` was not used as the FAST-LIO drift value.

### ✅ Conclusion

* A total of 2,602 Odometry samples were successfully obtained from HKU_MB_2020-09-20-13-34-51.bag. The Odometry-based accumulated 3D travel distance was 98.7626 m, while the distance between the starting and ending positions was 63.5933 m. The elevation changed by 2.2123 m, and a rotational difference of approximately 155.0646° existed between the starting and ending orientations. These results confirmed that the dataset was not a closed-loop trajectory returning to the original position and orientation. Therefore, the start-to-end distance cannot be interpreted as the accumulated FAST-LIO error or used to calculate the drift ratio. This experiment was not summarized as a return-to-start error measurement, but rather as a preliminary data validation experiment demonstrating that the closed-loop condition of a rosbag must be verified before evaluating accumulated error.


<p><br></p>

---

## July 19, 2026

### 📝 To-Do List (2026-07-19)

* [x] Conduct FAST-LIO experiments

### 📌 Notes

### FAST-LIO Practice

* Experiment 3: Real-Time Processing Limit of FAST-LIO According to rosbag Playback Speed

  * The rosbag was played at 0.5x, 1x, 2x, 4x, and 8x speeds to determine when FAST-LIO could no longer keep up with the input data in real time.
  * Since this experiment was intended to evaluate the computational performance of FAST-LIO, RViz visualization and PCD saving were disabled during execution.

| Playback Speed | Actual Processing Time | Number of Odometry Messages | Retention Rate | Average CPU Usage | Maximum RSS              | Post-Completion Delay | Warnings                      |
| -------------- | ---------------------- | --------------------------- | -------------- | ----------------- | ------------------------ | --------------------- | ----------------------------- |
| 0.5x           | Approximately 97s      | 487 messages                | 100%           | 30.97%            | 179,469 KiB / 175.25MiB  | Within 0–1s           | ROS warning logs not measured |
| 1.0x           | Approximately 49s      | 487 messages                | 100%           | 52.43%            | 179,560 KiB / 175.35MiB  | Within 0–1s           | ROS warning logs not measured |
| 2.0x           | Approximately 25s      | 487 messages                | 100%           | 85.20%            | 178,332 KiB / 174.15MiB  | Within 0–1s           | ROS warning logs not measured |
| 4.0x           | Approximately 13s      | 487 messages                | 100%           | 104.23%           | 178,716 KiB / 174.53 MiB | Within 0–1s           | ROS warning logs not measured |
| 8.0x           | Approximately 7s       | 487 messages                | 100%           | 154.71%           | 178,860 KiB / 174.67 MiB | Within 0–1s           | ROS warning logs not measured |

### ✅ Conclusion

* As the rosbag playback speed increased from 0.5x to 8x, the average CPU usage increased from 30.97% to 154.71%. In contrast, the maximum RSS remained nearly constant at approximately 174–175 MiB. Under all conditions, 487 Odometry messages were generated, and the overall pose estimation results were identical. In addition, no noticeable processing delay was observed after the bag playback ended. Therefore, under the current hardware and configuration, FAST-LIO is considered capable of real-time processing for input rates up to 8x playback speed, corresponding to approximately 80 Hz. However, because no processing failure occurred even at 8x playback speed, the actual processing limit of FAST-LIO is higher than the range evaluated in this experiment. Additional experiments at 16x playback speed or higher are required to determine the precise processing limit.


<p><br></p>

---

## July 16, 2026

### 📝 To-Do List (2026-07-16)

* [x] Conduct FAST-LIO experiments

### 📌 Notes

### FAST-LIO Practice

* Experiment 2: Effect of Downsampling Size on Processing Speed and Map Quality

  * Experiment 2-A: Current Scan Downsampling
  * 1. Parameter Definitions
  * filter_size_surf: Downsamples newly received LiDAR scans on a voxel basis
  * filter_size_map: Downsamples the accumulated global map
  * For example, if filter_size_surf is set to 0.5, a representative point is used within each voxel of approximately 0.5 m in size.

| Setting | Expected Result                                                       |
| ------- | --------------------------------------------------------------------- |
| 0.2 m   | More points, higher detail, increased computational load              |
| 0.5 m   | Default setting                                                       |
| 1.0 m   | Fewer points, faster processing, possible structural information loss |

* Actual Results

* filter_size_surf = 0.2

  <img src="https://github.com/Kim-SeongGeon/AISL/blob/main/Image/0.2m_rviz.png" width="400"/>

* filter_size_surf = 0.5

  <img src="https://github.com/Kim-SeongGeon/AISL/blob/main/Image/0.5m_rviz.png" width="400"/>

* filter_size_surf = 1.0

  <img src="https://github.com/Kim-SeongGeon/AISL/blob/main/Image/1.0m_rviz.png" width="400"/>

| filter_size_surf | Average Number of Points | Average CPU Usage | Map Detail | Wall and Column Shapes                                                                                          | Processing Issues                                                                                                                                                                                     |
| ---------------- | ------------------------ | ----------------- | ---------- | --------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 0.2 m            | 947.1 points             | 62.09%            | High       | The outlines of walls and columns were the most continuous, and detailed structures were clearly represented    | Normal. Some wall surfaces appeared thick or overlapped, but this may have been caused by the accumulated display of dense point clouds or minor registration errors, so further analysis is required |
| 0.5 m            | 332.3 points             | 51.80%            | Medium     | Major wall surfaces and column shapes could be distinguished, and their outlines were relatively well preserved | Normal. The balance between information quantity and computational load was the best                                                                                                                  |
| 1.0 m            | 122.3 points             | 51.40%            | Low        | The outlines of walls and columns became discontinuous, and many small structures were lost                     | The system operated normally, but excessive downsampling caused significant structural information loss                                                                                               |

* Experiment 2-B: Global Map Downsampling

  * Difference from Experiment 2-A

| Parameter        | Applied Target      | Directly Affected Value                          |
| ---------------- | ------------------- | ------------------------------------------------ |
| filter_size_surf | New LiDAR scan      | Number of processed points per frame             |
| filter_size_map  | ikd-Tree global map | Number of map points and nearest-neighbor search |

* Actual Results

* filter_size_map = 0.2

  <img src="https://github.com/Kim-SeongGeon/AISL/blob/main/Image/map02_rviz.png" width="400"/>

* filter_size_map = 0.5

  <img src="https://github.com/Kim-SeongGeon/AISL/blob/main/Image/map05_rviz.png" width="400"/>

* filter_size_map = 1.0

  <img src="https://github.com/Kim-SeongGeon/AISL/blob/main/Image/map10_rviz.png" width="400"/>

| filter_size_map | Final map_valid | Final Number of ikd-Tree Points | Average CPU Usage | Estimated Trajectory                                                                                           | Wall and Column Registration                                                                         | Processing Status                             |
| --------------- | --------------- | ------------------------------- | ----------------- | -------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------- | --------------------------------------------- |
| 0.2 m           | 35,913          | 38,287                          | 80.22%            | Trajectory estimation was normal, but a difference existed between the baseline setting and the final position | The structures were the densest and most continuous, but some surfaces appeared thick and overlapped | Normal                                        |
| 0.5 m           | 4,400           | 5,485                           | 81.10%            | Stable trajectory estimation and structural registration were maintained                                       | The outlines of walls and columns were maintained relatively stably                                  | Normal, with the best overall balance         |
| 1.0 m           | 1,432           | 1,751                           | 75.40%            | Registration stability decreased along with warnings about insufficient valid points                           | Detailed structures were reduced, and local registration stability decreased                         | Repeated occurrence of `No Effective Points!` |

### ✅ Conclusion

* As **filter_size_surf** increased, the average number of output points decreased significantly from 947.1 to 122.3. CPU usage was the highest at 0.2 m, but there was almost no difference between 0.5 m and 1.0 m. Therefore, in this dataset and computing environment, increasing the voxel size beyond 0.5 m provided only a limited additional reduction in CPU usage, while the loss of map structure increased.
* When **filter_size_map** was increased from 0.2 m to 1.0 m, the final number of ikd-Tree points decreased by approximately 95.4%, from 38,287 to 1,751. However, CPU usage did not decrease in proportion to the number of map points, and the values at 0.2 m and 0.5 m were nearly identical. The 0.2 m setting preserved more detailed structures but significantly increased the map size, while the 1.0 m setting caused detailed structural information loss and repeated `No Effective Points!` warnings, reducing registration stability. In this experimental environment, 0.5 m provided the best balance between map size and registration stability.


<p><br></p>

---

## July 15, 2026

### 📝 To-Do List (2026-07-15)

* [x] Study Kalman Filter theory
* [x] Conduct FAST-LIO experiments

### 📌 Notes

### Kalman Filter Theory

* What is a Kalman Filter?

  * To understand the Kalman Filter, it is first necessary to understand the Bayes Filter.

  * The Kalman Filter is a type of Bayes Filter that can be used when all distributions are Gaussian probability distributions and the model is a linear system. Like the Bayes Filter, it is a recursive filter that uses the previous estimate to calculate the current estimate. As with the Bayes Filter, it is divided into two stages: the Prediction Step and the Correction Step.

  * The Kalman Filter was originally proposed as an algorithm for trajectory estimation. It has since been extended and is now used in various fields, including control and navigation.

  * For example, to understand the Kalman Filter, suppose that a ship is currently located at the black point shown in the figure below, and the objective is to estimate where it will move next.

    <img src="https://github.com/Kim-SeongGeon/AISL/blob/main/Image/Kalman Filter example_1.png" width="400"/>

  * Through the Prediction process, it is estimated that the ship will move to the location marked with the black (X).

    <img src="https://github.com/Kim-SeongGeon/AISL/blob/main/Image/Kalman Filter example_2.png" width="400"/>

  * At this point, an observation is performed using the lighthouse. As a result of the Correction process, the distance represented by the green line is observed, and the ship determines that its position is the location marked with the green (X), as shown below. The Kalman Filter algorithm can then calculate the weighted sum of the green (X) and black (X), resulting in the estimated position marked with the red (X).

    <img src="https://github.com/Kim-SeongGeon/AISL/blob/main/Image/Kalman Filter example_3.png" width="400"/>

  * In summary, the assumptions are as follows.

    1. All probability distributions are Gaussian distributions.
    2. The model is linear.

  * The Kalman Filter is a type of Bayes Filter that is used when these two assumptions are satisfied.

  * Its overall framework is similar to that of the Bayes Filter.

* Proof and Explanation of the Kalman Filter Assumptions

  * As explained earlier, the Kalman Filter is based on two assumptions.

    1. All probability distributions are Gaussian distributions.
    2. The model is linear.

  * A linear model is a model that can be represented using linear functions.

  * If the input follows a Gaussian distribution, the output of a linear model also follows a Gaussian distribution.

    <img src="https://github.com/Kim-SeongGeon/AISL/blob/main/Image/Kalman Filter Proof of Assumptions_1.png" width="400"/>

  * The equations in the image above represent the Kalman Filter in mathematical form. To examine their meanings in greater detail,

    <img src="https://github.com/Kim-SeongGeon/AISL/blob/main/Image/Kalman Filter Proof of Assumptions_2.png" width="400"/>

  * In the equations shown above, $n$ represents the dimension of the state vector.

  * $l$ represents the dimension of the control command ($u$).

  * The Gaussian distribution is expanded mathematically, and the following formula must be understood to interpret it.

    <img src="https://github.com/Kim-SeongGeon/AISL/blob/main/Image/Kalman Filter Proof of Assumptions_3.png" width="400"/>

  * By understanding the equation above and substituting the Kalman Filter equations into it, the following two equations can be obtained.

    <img src="https://github.com/Kim-SeongGeon/AISL/blob/main/Image/Kalman Filter Proof of Assumptions_4.png" width="400"/>

  * Based on the two images above, it is confirmed that $[p(x_t|u_t, x_{t-1}), p(z_t|x_t)]$ follows a Gaussian distribution.

  * Then, does the $bel$ function also follow a Gaussian distribution?

  * As shown in the image below, because we assume that the $\bar{\mathrm{bel}}$ function follows a Gaussian distribution, the $bel$ function can also be said to follow a Gaussian distribution. This is because the product of Gaussian distributions is also a Gaussian distribution.

    <img src="https://github.com/Kim-SeongGeon/AISL/blob/main/Image/Kalman Filter Proof of Assumptions_5.png" width="400"/>

  * Then, does the $\bar{\mathrm{bel}}$ function follow a Gaussian distribution?

  * As shown in the image below, the $\bar{\mathrm{bel}}$ function is also defined as the product of Gaussian distributions, so it can be said to follow a Gaussian distribution. However, for this statement to hold, it must first be demonstrated that the initial $bel$ function also follows a Gaussian distribution.

    <img src="https://github.com/Kim-SeongGeon/AISL/blob/main/Image/Kalman Filter Proof of Assumptions_6.png" width="400"/>

  * All components follow Gaussian distributions!

    <img src="https://github.com/Kim-SeongGeon/AISL/blob/main/Image/Kalman Filter Proof of Assumptions_7.png" width="400"/>

  * A Gaussian distribution is represented by two parameters.

  * These parameters are the mean ($μ$) and the covariance matrix ($Σ$).

  * Therefore, the part represented by the $bel$ function in the Bayes Filter can be expressed using only two parameters: $μ,Σ$.

  * Summary

  * Based on all the information above, the properties used to derive the Kalman Filter are as follows.

    * The product of two Gaussian probability distributions is also a Gaussian probability distribution.
    * In a linear system, if the input follows a Gaussian probability distribution, the output also follows a Gaussian probability distribution.
    * The marginal and conditional distributions of a Gaussian distribution are also Gaussian distributions.
    * A Gaussian distribution can be fully represented using only its mean and covariance matrix.
    * Properties related to inverse matrix operations are also used.

  * Therefore, the pseudocode of the Kalman Filter can be written as follows.

    <img src="https://github.com/Kim-SeongGeon/AISL/blob/main/Image/Kalman Filter Proof of Assumptions_8.png" width="400"/>

  * The inputs are the mean at time t-1, the covariance matrix at time t-1, the control command ($u_t$), and the observation ($z_t$).

  * Lines 2 and 3 represent the Prediction Step, while Lines 4 through 6 represent the Correction Step.

  * As defined earlier, $A_t$ is a matrix that represents the relationship between the states at $[t-1, t]$, excluding control and noise.

  * $B_t$ is a matrix that represents the relationship between the control input $u_t$ and the state vector.

  * In the Prediction Step, the current mean and covariance matrix are predicted.

  * In the Correction Step, the observation is used to update the mean and covariance matrix predicted in the Prediction Step.

  * $K_t$ is the Kalman Gain, which is defined in Line 4, and $C_t$ is the matrix that represents the relationship between the state vector and the observation, as defined earlier.

  * The Kalman Gain calculated in Line 4 is used to update the mean and covariance matrix obtained in the Prediction Step to the current mean and covariance matrix.

  * Line 5 calculates the mean. The current observation $z_t$, the previously calculated mean, and $C_t$ are used to update the mean of the current state.

  * Line 6 updates the covariance matrix in a direction that reduces uncertainty based on the observation.

* What is an EKF?

  * The Kalman Filter is used when the model is linear and all probability distributions are Gaussian probability distributions. Therefore, if these assumptions are violated, the Kalman Filter does not operate properly.

  * However, real-world systems frequently fail to satisfy these assumptions. For example, even when considering localization on a 2D plane, an orientation value must be added to the state vector. Because sine and cosine values are introduced, the model becomes nonlinear.

  * Therefore, the EKF extends the Kalman Filter so that it can also be used in nonlinear situations.

  * EKF stands for Extended Kalman Filter.

  * As its name suggests, the EKF is an extended version of the Kalman Filter. Although the model is defined as nonlinear, the overall algorithmic flow is similar to that of the Kalman Filter.

  * First, a nonlinear model can be defined as shown in the image below.

    <img src="https://github.com/Kim-SeongGeon/AISL/blob/main/Image/EKF_1.png" width="400"/>

  * The problem with these nonlinear functions is that when an input with a Gaussian probability distribution is passed through the model, the resulting output does not follow a Gaussian probability distribution.

  * To resolve this problem, a process called Local Linearization is performed.

  * Linearization is performed using a first-order Taylor expansion.

  * Like the Kalman Filter, the EKF consists of a Prediction Step and a Correction Step. The values required for these steps are defined as shown in the image below. Jacobian matrices are also used.

    <img src="https://github.com/Kim-SeongGeon/AISL/blob/main/Image/EKF_2.png" width="400"/>

  * Two main factors affect Local Linearization.

    * The difference between the value linearized using the first-order Taylor expansion and the actual nonlinear model
    * Input uncertainty (= Covariance Matrix)

  * When the input uncertainty is small, the standard deviation is also small. Therefore, the probability distribution becomes narrow, reducing the difference between the model linearized using the Taylor expansion and the actual nonlinear model.

  * Examining the EKF equations in greater detail,

  * As with the Kalman Filter,

  * $[p(x_t|u_t, x_{t-1}), p(z_t|x_t)]$

  * When these two probability distributions are calculated, it can be seen that they result in Gaussian probability distributions because the model has been linearized, as shown in the image below.

    <img src="https://github.com/Kim-SeongGeon/AISL/blob/main/Image/EKF_3.png" width="400"/>

  * The pseudocode of the EKF is shown below.

    <img src="https://github.com/Kim-SeongGeon/AISL/blob/main/Image/EKF_4.png" width="400"/>

  * It is very similar to the original Kalman Filter, but note that $A_t$ and $C_t$ have been replaced by the Jacobian matrices $G_t$ and $H_t$!

  * What happens if the observation model (sensor) has no noise?

  * As can be determined by calculating Lines 4 and 5, $μ_t = ({H_t}^T)^{-1} * z_t$.

  * This means that the current mean is updated using only the current observation vector.

  * Conversely, what happens if the observation model (sensor) contains an extremely large amount of noise?

  * The matrix $Q_t$, which represents noise, approaches infinity. This means that the Kalman Gain ($K_t$) becomes 0.

  * Therefore, the mean predicted in the previous Prediction Step is used as the current updated mean.

  * The EKF can be applied in various situations. For example, it can be used for localization as follows.

    <img src="https://github.com/Kim-SeongGeon/AISL/blob/main/Image/EKF_5.png" width="400"/>

  * Finally, the EKF can be summarized as follows.

    * It is an extended version of the Kalman Filter.
    * It performs Local Linearization of nonlinear models using a first-order Taylor expansion.
    * If the uncertainty of the input sensor increases, the linearized values may become inaccurate.

### FAST-LIO Practice

* Experiments to conduct while practicing FAST-LIO

  * The respective roles of LiDAR and IMU in FAST-LIO
  * The effect of downsampling size on processing speed and map quality
  * The rosbag playback speed at which the real-time processing limit is exceeded
  * The accumulated error that occurs when returning to the starting point
  * Drift caused by the absence of Loop Closure in FAST-LIO

* Experiment 1: Identifying the Roles of LiDAR and IMU

  * Experiment 1-A: Measuring the Baseline with Normal Inputs

    * FAST-LIO initialized normally
    * Average Odometry publishing frequency: 9.988 Hz
    * Average Odometry period: approximately 100.1 ms
    * The Path and accumulated map were generated normally in RViz
  * Experiment 1-B: LiDAR Input Only

    * The /livox/lidar topic was published normally
    * FAST-LIO initialization failed because IMU data was unavailable
    * /Odometry was not published
    * Accumulated map generation failed because the system could not estimate orientation or displacement
  * Experiment 1-C: IMU Input Only

    * The /livox/imu topic was published normally
    * Average IMU publishing frequency: approximately 202.913 Hz
    * Average IMU publishing period: approximately 4.93 ms
    * Initial IMU measurements were received, but the geometric structure of the surrounding environment could not be observed
    * Position correction and map generation were impossible because no LiDAR feature points were available
    * /Odometry and the accumulated map were not generated

  ### Functional Comparison by Input Condition

| Input Condition | Orientation and Motion Change Estimation | Point Cloud Motion Distortion Compensation | LiDAR Map Registration                      | Normal Map/Odometry |
| --------------- | ---------------------------------------- | ------------------------------------------ | ------------------------------------------- | ------------------- |
| LiDAR + IMU     | Possible                                 | Possible                                   | Possible                                    | Possible            |
| LiDAR Only      | Impossible                               | Impossible                                 | Cannot proceed because initialization fails | Impossible          |
| IMU Only        | Inertial measurements can be received    | No point cloud available for compensation  | Impossible                                  | Impossible          |

### ✅ Conclusion

* The **IMU** measures acceleration and angular velocity at a high frequency to estimate the robot's orientation and motion changes and compensate for motion distortion in the LiDAR point cloud.
* The **LiDAR** provides geometric features of the surrounding environment to correct positional errors and perform map registration.
* When only LiDAR data is provided, IMU-based initialization and point cloud motion distortion compensation are impossible. When only IMU data is provided, no environmental information is available for position correction, so a map and Odometry cannot be generated.
* Therefore, **both LiDAR and IMU are required** for normal localization and map generation in FAST-LIO.


<p><br></p>

---

## July 14, 2026

### 📝 To-Do (2026-07-14)

- [X] Study Bayes Filter theory

### 📌 Notes

- What is Bayes Filter?
  - Before discussing the Bayes Filter, let's first briefly understand what Bayes' theorem is.
  - Bayes' theorem, which you might hear about in probability class, refers to the process of inferring the probability of an event based on previous experience and current evidence. Let me explai[...]
  - Bayes Filter can be understood as a filter that repeatedly uses Bayes' theorem.
  <img src="https://github.com/Kim-SeongGeon/AISL/blob/main/Image/State Estimation.png" width="400"/>

  - State estimation refers to determining the robot's state $x$ at time $t$ based on the robot's observations $z$ and the robot's control commands $u$.
  - The above equation estimates the robot's state $x$ at time $t$ considering the given observations $z$ and control commands $u$ from 1 to $t$.
  - Adding the meaning of recursive means estimating the robot's state $x_t$ using the robot's previous state $x_{t-1}$.
  - Let's use the most famous example of Bayes Filter - finding the robot's location - to understand it.
  <img src="https://github.com/Kim-SeongGeon/AISL/blob/main/Image/Bayes Filter example_1.png" width="400"/>

  - Let's assume the robot is in a 1D space and can determine whether it's a door or not. And let's say the robot knows nothing about the global environment. Initially, the robot is equally likely[...]
  - When the robot moves and observes a door, $bel(x)$ changes as follows. (Since a door was observed, the probability of the robot being in front of a door is judged to be high[...]
  <img src="https://github.com/Kim-SeongGeon/AISL/blob/main/Image/Bayes Filter example_2.png" width="450"/>

  - Let's move the robot forward a bit using the calculated $bel(x)$.
  <img src="https://github.com/Kim-SeongGeon/AISL/blob/main/Image/Bayes Filter example_3.png" width="400"/>

  - The shape of $bel(x)$ we predicted remains the same, but since there is uncertainty about exactly how far the robot moved, the probability distribution is somewhat spread out[...]
  - And let's receive a new observation value once more.
  <img src="https://github.com/Kim-SeongGeon/AISL/blob/main/Image/Bayes Filter example_4.png" width="400"/>

  - We can obtain a new $bel(x)$ by combining the new observation value $p(z|x)$ and the existing $bel(x)$ probability distribution.
  - In this way, using the robot's previous $bel(x)$ value and observation value $(p(z|x))$, representing the current $bel(x)$ value is what Bayes Filter is.

- Deriving Bayes Filter Equation
  - Before deriving the equation, reminding basic knowledge about probability:
    1. Bayes' theorem
    2. Markov Property / Assumption
    3. Law of Total Probability
   
  - Bayes' theorem
    - When we summarize Bayes' theorem that we've seen so far on one slide, it looks like this:
    <img src="https://github.com/Kim-SeongGeon/AISL/blob/main/Image/Bayes' theorem.png" width="400"/>

  - Markov Property / Assumption
    - What is Markov Property / Assumption then?
    - In a nutshell, when predicting a future state, it is only affected by the current state and is not affected by all previous past states[...]

  - Law of Total Probability
    - Summarizing the Law of Total Probability on one slide looks like this:
    - A law used to derive the total probability $(p(x))$ without conditions from the conditional probability $(p(x|y))$.
    - Marginalization is similar to the Law of Total Probability, with the only difference being that it uses joint probability instead of conditional probability.
    <img src="https://github.com/Kim-SeongGeon/AISL/blob/main/Image/Law of Total Probability.png" width="400"/>

  - Now let's examine the Bayes Filter mathematically in detail.
  - First, defining $bel(x_t)$ at time $t$ looks like this:
  <img src="https://github.com/Kim-SeongGeon/AISL/blob/main/Image/Bayes Filter Equation_1.png" width="400"/>

  - Applying Bayes' Rule, it can be changed to:
  - Applying $p(x,y) = p(y|x)p(x)$.
  <img src="https://github.com/Kim-SeongGeon/AISL/blob/main/Image/Bayes Filter Equation_2.png" width="400"/>

  - In the above equation, the first part can be simplified by applying Markov Assumption.
  - The assumption that previous values $(z_{1:t-1}, u_{1:t}$ are not considered to find $z_t$, and $u_t$ is the current value but doesn't affect finding $z_t$.
  <img src="https://github.com/Kim-SeongGeon/AISL/blob/main/Image/Bayes Filter Equation_3.png" width="400"/>

  - The equation in the second block can also be transformed using the Law of Total Probability.
  <img src="https://github.com/Kim-SeongGeon/AISL/blob/main/Image/Bayes Filter Equation_4.png" width="400"/>

  - In the above equation, applying Markov Assumption once more simplifies the equation.
  - The assumption that previous values $(z_{1:t-1}, u_{1:t-1})$ are not considered to find $x_t$.
  <img src="https://github.com/Kim-SeongGeon/AISL/blob/main/Image/Bayes Filter Equation_5.png" width="400"/>

  - In the above equation, when calculating $p(x_{t-1})$ in the last block, $u_t$ doesn't need to be considered, so it is removed.
  <img src="https://github.com/Kim-SeongGeon/AISL/blob/main/Image/Bayes Filter Equation_6.png" width="400"/>

  - Using the previously defined $bel(x_{t-1})$, writing the equation in recursive form looks like this:
  <img src="https://github.com/Kim-SeongGeon/AISL/blob/main/Image/Bayes Filter Equation_7.png" width="400"/>

### ✅ Conclusion

- 

<p><br></p>

---

## March 17, 2026

### 📝 To-Do (2026-03-17)

- [X] Read VINS paper

### 📌 Notes

- 1. Introduction
  - VINS-Mono combines monocular camera and IMU and has several advantages compared to using just a camera
    - Can obtain scale values (and also obtain roll, pitch angles)
    - Can perform tracking with the help of IMU sensors in environments where camera tracking is difficult (illumination change, textureless area, or motion blur)
    - Both camera and IMU are low-cost sensors that can be purchased inexpensively
  - While these advantages exist, there are also major issues
    - Initialization process is challenging
      - Since there is no sensor that can directly measure distance, combining visual structure and inertial measurement is difficult
    - VINS (Visual-Inertial Navigation System) is a non-linear system
      - In most cases, the system must start from a fixed location and initially move slowly and carefully, so practical use is limited
    - VIO (Visual-Inertial Odometry) inevitably experiences drift phenomena
  - Therefore, to address these issues, VINS-Mono has the following contributions
    - Proposes a method for initialization even without knowing initial states
    - Tightly-coupled sensor fusion and optimization-based estimation method
    - Real-time guaranteed relocalization and 4 DOF (degrees-of-freedom) global pose graph optimization
    - Can save, load, and merge pose graphs with other local pose graphs

- 2. Overview
  - The overall system of VINS-Mono is shown in the figure below
  <img src="https://github.com/Kim-SeongGeon/AISL/blob/main/Image/Visual-InertialStateEstimatorDiagram.png" width="450"/>
  
  - VINS-Mono first goes through a Measurement Preprocessing process. Features are extracted from images, and while tracking, IMU measurements are preintegrated between two consecutive images
  - After the Measurement Preprocessing process, it undergoes an initialization process. It calculates all the values needed for subsequent non-linear optimization. For example, pose, velocity, e[...]
  - With the initialized values, the Visual-Inertial Odometry Module with the Relocalization Module uses pre-integrated IMU measurements and feature observations using a tightly-coupled approach
  - VINS-Mono proposes methods for initializing with monocular camera and IMU values, methods for selecting keyframes, methods for performing good tracking, and includes loop closure and pose gra[...]
  - The notation used in this paper is as follows:
    - $()^c$ : camera frame
    - $()^w$ : world frame
    - $()^b$ : IMU frame
    - $q$ : quaternion, $R$ : Rotation Matrix
    - $p$ : Translation vector
    - $b_k$ : IMU (Body) frame in the k-th image
    - $c_k$ : Camera frame in the k-th image
    - $\otimes$ : Quaternion multiplication
    - $\hat{(\cdot)}$ : estimated value or noisy measurement
   
- 3. Measurement Preprocessing
  - Looking in detail at the preprocessing process of visual and IMU measurements, visual measurement involves attempting tracking in consecutive images and extracting new features in the current[...]
  - Vision Processing Front End
    - When a new image arrives, KLT Sparse Optical Flow Algorithm is performed. To find features, the GoodFeatureToTrack() function from OpenCV is used. This function can efficiently track about [...]
      - KLT Sparse Optical Flow is the core algorithm in VINS-Mono's visual preprocessing stage that tracks where previously found feature points go in the next frame
        - 3 assumptions of the KLT algorithm
          1. Brightness Constancy: When the camera moves over a very short time, the brightness or color of a specific object does not change
          2. Small Motion: Since the time is short, objects and pixels are assumed to move only slightly
          3. Spatial Coherence: This is the most core idea of KLT. Tracking a single pixel alone is prone to failure due to noise. So neighboring pixels are considered together to maintain spatia[...]
        - Why "Sparse" Optical Flow?
          => Computing the motion of all 2 million pixels in the screen is called 'Dense Optical Flow'. However, this requires too much computation to operate in real-time
        - So VINS-Mono selects only about 100-300 distinct feature points like corners that are easy to track on the screen. The computational load is dramatically reduced
      - RANSAC algorithm is used to remove outliers, and the extracted image features are projected onto a unit sphere
        - RANSAC (Random Sample Consensus) is a method that filters out 'fake data (outliers)' mixed in numerous data and finds only 'real data (inliers)' to obtain the correct answer
        - While tracking feature points with KLT, the camera may follow a moving car instead of moving itself, or incorrectly track due to light reflection
          - What RANSAC does in VINS-Mono
          - VINS-Mono performs this process among KLT-tracked points
            - Input: hundreds of matched feature point pairs between previous and current frames
            - Hypothesis: randomly select a few points to create a model (like Fundamental Matrix) that says "the camera probably rotated and moved like this"
            - Verification: when the model is applied, check if the remaining points agree by saying "yes, I'm around that position too!"
            - Result: feature points that don't match the actual camera motion (outliers) are ruthlessly removed at this point
          - Why RANSAC is good
            - Most algorithms try to average all data to calculate. So if there's even one huge error (outlier) in the data, the result is affected
            - On the other hand, RANSAC takes the strategy of "there will inevitably be fakes mixed in, so let's try several times until we're lucky enough to pick only real ones". So even if hal[...]
      - During this process, keyframes are also selected using two criteria
        - If the parallax (pixel difference in features) between Last Frame and Current Frame exceeds a certain threshold, it is distinguished as a new keyframe
        - Distinguished by tracking quality
      - The pixel difference between features is expressed as parallax here. The reason for selecting this criterion is to secure a sufficient number of features when triangulation is performed
      - Tracking quality can be judged by the number of visual feature points. If the number of tracking feature points falls below a certain threshold, new features are extracted

### ✅ Conclusion

- Continue reading...

<p><br></p>

---

## March 16, 2026

### 📝 To-Do (2026-03-16)

- [X] Read VINS paper

### 📌 Notes

- Found and decided to seriously read the VINS paper that is the origin of OpenVINS
- [VINS-Mono: A Robust and Versatile Monocular Visual-Inertial State Estimator](https://arxiv.org/pdf/1708.03852)
  - 1. Core philosophy of VINS-Mono: 'Solve everything together (Tightly-Coupled)'
    - In the past, loosely-coupled approaches were used where position calculated by camera and position predicted by IMU were computed separately and then roughly combined. However, VINS-Mono co[...]
  - 2. The paper's 4-stage pipeline (flowchart)
    - 1. Measurement Preprocessing
      - Vision: uses KLT algorithm to track feature points in incoming images
      - IMU Pre-Integration: IMU is much faster than camera. The technique of accumulating numerous IMU data between camera frames into one unified value beforehand. This is the key to real-time [...]
    - 2. Initialization
      - Using only one monocular camera, actual distance (scale) cannot be known
      - VINS-Mono proposes a powerful algorithm that succeeds in initialization even while the robot is moving on-the-fly, not just at rest. It combines the rough skeleton drawn by the camera wit[...]
    - 3. Sliding Window-based Local VIO
      - Optimization-based approaches have the disadvantage of requiring too much computation
      - To solve this, it discards old data and uses the Sliding Window technique of keeping only the recent N critical frames (Key Frames) in the window and optimizing
      - When discarding old data from the window, mathematical technique called Marginalization preserves the information contained in past data as Prior
    - 4. 4-DOF Global Optimization (Relocalization & Pose Graph Optimization)
      - No matter how well optimized, error accumulates over long distances
      - When already-visited places are recognized using DBoW2 (Loop Detection), the current location is corrected
      - The most impressive part is that only '4-DOF (x, y, z, yaw)' is optimized. Since the IMU continuously feels gravity, the robot's tilt (roll, pitch) is already absolutely accurate without [...]
      
### ✅ Conclusion

- This paper is judged to have relevance to my personal research topic, so continuing to read should be beneficial

<p><br></p>

---

## March 13, 2026

### 📝 To-Do (03/13/2026)

- [X] Test with a dataset other than the one we did today
- [X] Study OpenVINS accurately

### 📌 Notes

- Selected and tested 3 datasets from those provided by OpenVINS
  - The rosbag for the test dataset was not downloading, so I converted it to rosbag2 after downloading and then performed rosbag play
- OpenVINS, as the name suggests, is an acronym for 'Open-Source Visual-Inertial Navigation System', which combines a camera (visual) and an inertial measurement device (IMU, inertial) to estimat[...]
  - 1. OpenVINS Core: MSCKF-based filter method
    - The biggest feature is using the MSCKF (Multi-State Constraint Kalman Filter) algorithm
      - => MSCKF uses IMU and camera sensors to perform measurement updates on fixed features (combining new noisy sensor measurements with previous prediction states to improve and refine the st[...]
    - Difference from ORB-SLAM: ORB-SLAM primarily uses 'optimization' based approach to draw the entire map and determine position, while OpenVINS is 'filter' based
    - Sliding Window: Instead of keeping all historical data, maintains only a few recent camera frames while updating the state. So computational load is low and is suitable for real-time system[...]
      
  - 2. Why use OpenVINS?
    - Online Calibration: extrinsics (relative position between camera and IMU) or time offsets are updated in real-time while the robot is moving
    - Extensibility: modular structure makes it very easy to add new sensors or replace parts of algorithms
    - Accuracy and Speed: despite being EKF (Extended Kalman Filter) based, shows high precision comparable to optimization-based algorithms. Especially for drones and robots with limited resourc[...]
      
  - 3. OpenVINS Architecture
    - Feature Tracking: finds and tracks corners like FAST mentioned earlier from camera images
    - IMU Preintegration: accumulates accelerometer/gyro data from IMU to predict the robot's rough movement
    - State Update: combines camera information and IMU prediction to finalize the robot's accurate position (x, y, z) and attitude (q)

### ✅ Conclusion

- The sense of OpenVINS was not completely grasped, so reading related papers
- Implement ORB-SLAM

<p><br></p>

---

## March 12, 2026

### 📝 To-Do (03/12/2026)

- [X] Test the OpenVINS platform

### 📌 Notes

- I used the dataset provided by EuRoC, but I couldn't find it at this point, so I tested it based on the public data provided by KITTI, but I couldn't see anything on the rviz screen and encount[...]
  - When I investigated the cause of the problem, the terminal running the subscribe.launch file showed [Init]: failed static init: platform moving too much, which means initial state estimation [...]
- While thoroughly examining the tutorials provided by OpenVINS, I found that data (ros1 cannot be downloaded at this point, https://docs.openvins.com/gs-datasets.html <- reference) can be downlo[...]
  
<img src="https://github.com/Kim-SeongGeon/AISL/blob/main/Image/OpenVINS(KITTI).png" width="250"/>
<img src="https://github.com/Kim-SeongGeon/AISL/blob/main/Image/OpenVINS(EuRoC).png" width="250"/>

### ✅ Conclusion

- Test with a dataset other than the one we did today
- Study OpenVINS accurately

<p><br></p>

---

## March 11, 2026

### 📝 To-Do (03/11/2026)

- [X] SLAM testing based on public datasets
- [X] Reading the papers I received from the professor

### 📌 Notes

- If I switch to Visual SLAM based, what I want is ORB-SLAM, but I decided to test this first by recommending the OpenVINS project to a lab member who has experience in switching to Visual SLAM b[...]
  - It was very difficult because I experienced several out-of-memory problems in the middle, but I successfully ran OpenVINS simulation
  - The two screens after completion of the drive are performance indicators and visualization results showing how accurately OpenVINS estimates the robot's movement (trajectory)
  - First Image: Trajectory visualization (a drawing of the robot's path on a 2D plane)
  - Second Image: estimation accuracy (a data window that numerically shows "how different is the position I calculated from the real thing?" as the simulation runs in real-time)

<img src="https://github.com/Kim-SeongGeon/AISL/blob/main/Image/Trajectory%20Visualization.jpeg" width="250"/>
<img src="https://github.com/Kim-SeongGeon/AISL/blob/main/Image/Estimation%20Accuracy.png" width="250"/>

- The paper received from the professor presents a non-repetitive VSLs-based technique that significantly improves the accuracy and efficiency of feature map merging in multi-robot systems

### ✅ Conclusion

- Proceed with what to do after the OpenVINS project
- Continue reading VSLs-based technical papers

<p><br></p>

--- 

## March 10, 2026

### 📝 To-Do (03/10/2026)

- [X] A serious interview with the professor (regarding the selection of personal research topics)
- [X] SLAM testing based on public datasets

### 📌 Notes

- The professor also liked the topics I thought of and gave advice since another lab member is working on the second one, so I will proceed by connecting the 1st and 3rd topics well
  - In the first topic, the 'communication constraint' condition is passed due to insufficient knowledge in the communication field (or changed to some constraints)
  - Take the first topic as the main subject and expand it to the third topic; the third is the master's thesis, and the mission plan doesn't necessarily need to use AI
  - Sparse (including feature) map merging appears to be a necessary and practical study in both commercial and defense sectors
  - Tests start with simulation (Matlab, etc.) with algorithms as the focus
  - Establish baselines well
  - Try the ICP+VSLs combination well
  - Geometric information (location information of landmarks) + class information
- I tried SLAM testing based on public datasets, but encountered many unexpected problems and asked for help from a lab member who had studied it

### ✅ Conclusion

- Read and study the papers that the professor sent and recommended
- Tomorrow, learn SLAM testing based on public datasets and make it my own

<p><br></p>

---

## March 09, 2026

### 📝 To-Do (03/09/2026)

- [X] Research to choose an accurate personal research topic

### 📌 Notes

- I have been working on multi-robot projects since I was an undergraduate research student, and in my first year of the master's program, I decided I should conduct personal research in this fie[...]
- Since employment in a defense company is my ultimate goal, I investigated what kind of SW R&D talent the defense companies I want to join are looking for, and what topics I should choose to do [...]
  - If I prioritize employment, I need C++/Python-based algorithm implementation ability, practical projects and papers related to 'unmanned/robotics', and diverse robot/system architecture under[...]
  - Environmental characteristics considered when using multi-robot SLAM in defense or battlefield include GNSS vulnerability (indoor, underground, disaster/warfare zones, electronic warfare), co[...]
  - Based on this, I narrowed down to about 3 topics that fit well with defense company robots/unmanned systems and are suitable for papers and portfolios
  1. Distributed Multi-Robot SLAM considering communication constraints: robots share partial maps and poses without a central server (or with minimal dependence), and can reliably perform collab[...]
  2. Robust Multi-Robot SLAM with limited sensors and fields of view: cooperation and robust loop closure in defense environments with common sensor compromises (limited FoV LiDAR, noisy IMU, cam[...]
  3. Multi-Robot SLAM-based swarm mission planning (with MUM-T in mind): directly utilize multi-SLAM results (shared maps, uncertainty of each robot) for swarm path planning, exploration, and sur[...]
  - Among these, if thesis and demo implementation are to be done within 2 years of master's degree, 'Distributed Multi-Robot SLAM and Reconnaissance Mission Planning Considering Communication an[...]
 
- Brief Master's 1st-2nd Year Roadmap (Research + Job Preparation)
  - Year 1: Building foundation + 1 paper-level results
    - 0-6 Months
      - Theory/Code: Analyze and practice implementing verified multi-robot SLAM systems like ORB-SLAM series, pose graph SLAM, LAMP/LAMP2.0
      - Language/Tools: C++/Python, ROS2, Git, basic PCL/OpenCV/robot simulator (Gazebo/Ignition, Isaac Sim, etc.)
    - 6-12 Months
      - Distributed/semi-centralized SLAM implementation in small multi-robot (e.g., 3 UGVs or 1 UGV + 1 drone) simulations
      - Target: present paper or poster at a domestic academic conference
  - Year 2: Expanding to Multi-Robot + Swarm/Mission Planning
    - 13-18 Months
      - Configure simulation environment with sensor constraints (limited FoV LiDAR, camera occlusion, communication dropout)
      - Improve robust loop closure, communication minimization strategies, and distributed optimization in this environment
    - 18-24 Months
      - Develop route planning and role allocation algorithms for reconnaissance/surveillance missions using SLAM results
      - International conference + Master's thesis completion

### ✅ Conclusion

- First, I will have a serious conversation with the professor about the three approaches I thought of and establish the exact direction
- And with datasets easily available in the lab, I need to get a feel for SLAM with simple testing

<p><br></p>

---
