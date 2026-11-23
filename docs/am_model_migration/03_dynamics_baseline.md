# 03 动力学参数基线（只读）

## 1. 单位和参考系

全部表格是当前有效 `<link><inertial>` 的 **[事实]**，不含 XML 注释中的旧 link_5。质量单位 kg，pose 平移单位 m、角度 rad，惯量单位 kg·m²。pose 顺序为 x/y/z/roll/pitch/yaw，默认相对所属 Link；惯量六分量以 inertial 坐标轴表达，原点位于其 COM。

本模型全部有效 inertial pose 的旋转为零（含 -0），但其 Link 各自的空间朝向不同。下面的飞机 base_link 惯量仅属于该刚体，不是整机等效惯量；机械臂 base_link 也只是一个刚体。

## 飞机自身（不含机械臂）

| Link | mass | inertial pose（相对本 Link） | ixx | iyy | izz | ixy | ixz | iyz | 证据 |
|---|---|---|---|---|---|---|---|---|---|
| base_link | 2.3411 | 0.0 -0.000647 0.024368 0 -0 0 | 0.0013622 | 0.011253 | 0.011215 | 1.2109e-05 | 2.1278e-05 | 1.003e-06 | [`models/quadtilt_am/model.sdf:4`](../../models/quadtilt_am/model.sdf#L4) |
| imu_link | 0.015 | 0 0 0 0 0 0 | 0.00001 | 0.00002 | 0.00002 | 0 | 0 | 0 | [`models/quadtilt_am/model.sdf:138`](../../models/quadtilt_am/model.sdf#L138) |
| tilt_0_Link | 0.94736 | 0.028311 -0 -0 0 -0 0 | 0.0033591 | 0.0032937 | 0.0001883 | -3.2015e-12 | 5.825e-11 | 6.3798e-10 | [`models/quadtilt_am/model.sdf:182`](../../models/quadtilt_am/model.sdf#L182) |
| properller_0_Link | 0.025 | 0 0 0.005 0 -0 0 | 0.00005 | 0.00005 | 0.0003 | 0 | 0 | 0 | [`models/quadtilt_am/model.sdf:234`](../../models/quadtilt_am/model.sdf#L234) |
| properller_2_Link | 0.025 | -0 -0 0.005 0 -0 0 | 0.00005 | 0.00005 | 0.0003 | 0 | 0 | 0 | [`models/quadtilt_am/model.sdf:286`](../../models/quadtilt_am/model.sdf#L286) |
| tilt_1_Link | 0.94736 | 0.028311 -0 -0 0 -0 0 | 0.0033591 | 0.0032937 | 0.0001883 | -3.2015e-12 | 5.825e-11 | 6.3798e-10 | [`models/quadtilt_am/model.sdf:338`](../../models/quadtilt_am/model.sdf#L338) |
| properller_1_Link | 0.025 | -0 -0 0.005 0 -0 0 | 0.00005 | 0.00005 | 0.0003 | 0 | 0 | 0 | [`models/quadtilt_am/model.sdf:390`](../../models/quadtilt_am/model.sdf#L390) |
| properller_3_Link | 0.025 | 0 0 0.005 0 -0 0 | 0.00005 | 0.00005 | 0.0003 | 0 | 0 | 0 | [`models/quadtilt_am/model.sdf:442`](../../models/quadtilt_am/model.sdf#L442) |

## 机械臂（包含当前夹爪）

| Link | mass | inertial pose（相对本 Link） | ixx | iyy | izz | ixy | ixz | iyz | 证据 |
|---|---|---|---|---|---|---|---|---|---|
| base_link | 0.34432 | -0.000805 -3.1e-05 0.015733 0 -0 0 | 0.00026968 | 0.00027222 | 0.00052932 | -2.6656e-10 | -8.0892e-08 | -9.1152e-11 | [`models/robotic_arm/model.sdf:4`](../../models/robotic_arm/model.sdf#L4) |
| link_1 | 0.057604 | -2.1e-05 0.000147 0.016563 0 -0 0 | 1.8263e-05 | 1.3985e-05 | 2.307e-05 | -3.807e-10 | -1.4763e-10 | -2.922e-08 | [`models/robotic_arm/model.sdf:64`](../../models/robotic_arm/model.sdf#L64) |
| link_2 | 0.039095 | 0.056726 -0 -0.000271 0 -0 0 | 1.0114e-05 | 1.4176e-05 | 7.7479e-06 | 7.2762e-21 | 2.0973e-19 | 3.677e-21 | [`models/robotic_arm/model.sdf:124`](../../models/robotic_arm/model.sdf#L124) |
| link_3 | 0.075843 | 0.043581 -0.000872 -0.000243 0 -0 0 | 1.4302e-05 | 2.3711e-05 | 1.4547e-05 | 2.9527e-10 | -1.407e-12 | -4.2397e-20 | [`models/robotic_arm/model.sdf:184`](../../models/robotic_arm/model.sdf#L184) |
| link_4 | 0.038113 | 0.044666 0.009062 0.000129 0 -0 0 | 7.4825e-06 | 1.0505e-05 | 1.2542e-05 | -5.112e-07 | 3.807e-10 | -1.4763e-10 | [`models/robotic_arm/model.sdf:244`](../../models/robotic_arm/model.sdf#L244) |
| link_5 | 0.02 | 0 0 0.01 0 -0 0 | 1e-05 | 1e-05 | 1e-05 | 0 | 0 | 0 | [`models/robotic_arm/model.sdf:336`](../../models/robotic_arm/model.sdf#L336) |
| left_finger | 0.005 | 省略 → 0 0 0 0 0 0 | 1e-05 | 1e-05 | 1e-05 | 0 | 0 | 0 | [`models/robotic_arm/model.sdf:406`](../../models/robotic_arm/model.sdf#L406) |
| right_finger | 0.005 | 省略 → 0 0 0 0 0 0 | 1e-05 | 1e-05 | 1e-05 | 0 | 0 | 0 | [`models/robotic_arm/model.sdf:449`](../../models/robotic_arm/model.sdf#L449) |

## 2. 可计算的标量质量和不能直接相加的惯量

[推导] 对有效 Link mass 作十进制标量求和：

| 范围 | 质量 kg | 解释 |
|---|---|---|
| 飞机自身 8 Link | 4.350820 | 含 IMU、两倾转体、四桨，不含机械臂 |
| 当前机械臂 8 Link | 0.584975 | 含旧根、五级连杆和两指 |
| 当前总装配 16 Link | 4.935795 | 不含任何世界其他模型 |
| 仅删旧机械臂根、其他 mass 不变的算术值 | 4.591475 | 条件算例，减少 0.344320 kg；不是新实物质量预测 |

没有计算或声称当前整机 COM/等效惯量。固定安装的机械臂并不意味着内部关节刚性；整机等效惯量依赖关节构型 q。若以后在统一参考点 O 求和，必须先旋转到统一坐标，再使用平行轴定理：

```text
I_O(q) = Σ [ R_OIi(q) I_Ci R_OIi(q)^T
             + m_i ((r_i(q)^T r_i(q)) I_3 - r_i(q) r_i(q)^T) ]
c_total(q) = Σ m_i c_i(q) / Σ m_i
```

其中 `r_i` 是 O 到各 COM 的向量，`R_OIi` 是每个 inertial 系到 O 的旋转。不能把表中不同 Link 下的 3×3 矩阵直接相加。

## 3. 已有参数的审计观察（不修复）

1. [事实/推导] 四个桨的当前对角惯量都是 `(0.00005,0.00005,0.0003)`，交叉项为零；主惯量满足正值，但 `0.0003 > 0.00005+0.00005`，不满足物理刚体主惯量三角不等式。数值特征值检查也确认四者相同。本轮保持原值；SDF 语法校验通过不能替代物理惯量一致性。
2. [事实] SDF `link_5` 的注释说明合并了夹爪基座质量并人为提高惯量（机械臂 :337–343）；这里只记录源码，不把注释的“安全/彻底解决”当成已验证物理结论。
3. [事实] 当前两指各 0.005 kg、对角惯量 1e-5，inertial pose 省略。没有测量证据证明这些参数与 42 mm 指爪实物相符。
4. [事实] 两份 SDF 中全部有效惯量矩阵对称组装后特征值为正；除了四桨主惯量三角关系外，没有由该代数检查发现其他非正定项。这仍不能证明数值与实物一致。
5. [事实] 当前飞机只有三处起落架球体 collision（半径 0.03 m）和两倾转体 Mesh collision；机身和四桨 Mesh collision 被注释。机械臂没有任何有效 collision。因此可视几何、惯性实体和实际参与碰撞的几何不等同，不能用“没发生碰撞”作为完整模型正确的证据。

## 4. URDF 中共有连杆的动力学对照

除 link_5 外，URDF 与 SDF 共有连杆的 mass 和惯量六分量数值一致，COM 有小数精度差异。以下保留 URDF 原值供后续同步时对照；URDF tool0 没有 inertial，不能当作已测得零质量实体。

| URDF Link | mass | origin xyz / rpy | ixx | iyy | izz | ixy | ixz | iyz | 证据 |
|---|---|---|---|---|---|---|---|---|---|
| base_link | 0.34432 | -0.00080493 -3.0749E-05 0.015733 / 0 0 0 | 0.00026968 | 0.00027222 | 0.00052932 | -2.6656E-10 | -8.0892E-08 | -9.1152E-11 | [`models/robotic_arm/model.urdf:17`](../../models/robotic_arm/model.urdf#L17) |
| link_1 | 0.057604 | -2.0847E-05 0.00014678 0.016563 / 0 0 0 | 1.8263E-05 | 1.3985E-05 | 2.307E-05 | -3.807E-10 | -1.4763E-10 | -2.922E-08 | [`models/robotic_arm/model.urdf:57`](../../models/robotic_arm/model.urdf#L57) |
| link_2 | 0.039095 | 0.056726 -3.9302E-14 -0.00027136 / 0 0 0 | 1.0114E-05 | 1.4176E-05 | 7.7479E-06 | 7.2762E-21 | 2.0973E-19 | 3.677E-21 | [`models/robotic_arm/model.urdf:116`](../../models/robotic_arm/model.urdf#L116) |
| link_3 | 0.075843 | 0.043581 -0.00087218 -0.00024348 / 0 0 0 | 1.4302E-05 | 2.3711E-05 | 1.4547E-05 | 2.9527E-10 | -1.407E-12 | -4.2397E-20 | [`models/robotic_arm/model.urdf:175`](../../models/robotic_arm/model.urdf#L175) |
| link_4 | 0.038113 | 0.044666 0.0090624 0.00012944 / 0 0 0 | 7.4825E-06 | 1.0505E-05 | 1.2542E-05 | -5.112E-07 | 3.807E-10 | -1.4763E-10 | [`models/robotic_arm/model.urdf:234`](../../models/robotic_arm/model.urdf#L234) |
| link_5 | 0.01 | -8.2823E-14 0 -0.0014527 / 0 0 0 | 1.9014E-08 | 1.9014E-08 | 3.6585E-08 | -9.2928E-25 | 3.0708E-24 | 1.5073E-23 | [`models/robotic_arm/model.urdf:293`](../../models/robotic_arm/model.urdf#L293) |

## 5. 第二阶段测量与更新清单

以下全部为 **[用户确认/后续测量]**，本轮不填入猜测值：

- 实际拆除的旧基座、首轴定子/转子、安装支架、线缆和紧固件分别归入哪个刚体；删除 Link 不等于把其质量自动并入飞机。
- 实际新根和每个改造 Link 的质量、局部 COM、惯量六分量及其坐标基准；如 CAD 给出主轴惯量，提供主轴相对 Link 的旋转。
- 新安装点和装配姿态实测值；该变换负责全局放置，不应被重复写进每个 Link 的 inertial pose。
- link_5 的法兰、夹爪基座和两指质量边界；TCP/抓取物质量是否单独建模。
- 飞机侧受安装件/线缆影响的 base_link 质量/COM/惯量，及倾转体、电机/桨惯量复核，避免一个部件在多个 Link 重复计入。
- 相同确认数据同步到仍在使用的 URDF 和控制/规划动力学模型；检查构型相关的总质量、COM、等效惯量，以及物理惯量可实现性。

推荐先保留现有数值并逐项记录结构变化，待测量齐备后集中更新。若改变 Link 自身参考系，COM/惯量的坐标表达必须同步变换，即使该刚体物理参数没改变；这应单独审查，不能当作普通模型移动悄悄实施。
