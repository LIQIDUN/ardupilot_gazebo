# 02 坐标系、完整运动链和安装变换

## 1. 语义和坐标约定

本篇 pose 顺序均为 `x y z roll pitch yaw`，单位 m/rad。使用列向量，`T_XY` 将 Y 系坐标变换到 X 系；RPY 对应 `Rz(yaw) Ry(pitch) Rx(roll)`。**[事实]** XML 中未声明 `relative_to` 的 Link pose 以所属模型系表达；Joint pose 默认以 child Link 表达；visual/collision/inertial pose 默认以所在 Link 表达；Frame 默认相对 `attached_to`。本机 `/usr/share/sdformat9/1.7/joint.sdf:3,53–63` 明确 Joint 默认参考和轴表达规则；`model.sdf:9–16` 明确 canonical link 默认取首个 Link。模型系附着于 canonical link，不意味着两者原点必然重合。

| 符号 | 含义 | 本模型关系 |
|---|---|---|
| A | 飞机自身 SDF 模型系（当前名 quadtilt_new，未来 am） | 不是世界外层包装模型，也不是机体质心 |
| B | 飞机 `base_link` | 当前没有 Link pose，`T_AB=I`；`inertial/pose` 不是 Link pose |
| M | 旧机械臂 SDF 模型系 | 首 Link 为旧机械臂 base_link，未设 model/link pose |
| O | 旧机械臂 `base_link` | `T_MO=I`，且是固定安装的实体 |
| J1 | 原 `joint_1` 轴/零位关节系 | `T_OJ1=Trans(0,0,0.03)` |
| L1 | 原 `link_1` | XML 零位 `T_J1,L1=I`；运动时绕 J1 的负 Z 轴旋转 |
| N | 未来机械臂模型系 | 新模型尚未创建，不能沿用 M 的含义而不说明 |
| R | 用户确认后的实际新安装根连杆坐标系 | 名称及是否静止必须由机械结构决定，不能擅自命名 link_0/link_1 |

[事实] 飞机 `base_link` 是首 Link，且模型无显式 pose（飞机 SDF :2–3）；IMU Link 与 B 零位重合，但 Sensor 自身 Roll=3.141593（:136–149）。机械臂旧根是首 Link（机械臂 SDF :2–3）。所有以下 pose 均是模型加载的参考配置，不表示任意运行时关节角下仍保持该相对姿态。

## 2. 飞机完整 Link 和 Joint

| 飞机 Link | Link pose | relative_to / 默认参考 | 证据 |
|---|---|---|---|
| base_link | 省略 → 0 0 0 0 0 0 | 所属模型系 | [`models/quadtilt_am/model.sdf:3`](../../models/quadtilt_am/model.sdf#L3) |
| imu_link | 0 0 0 0 0 0 | 所属模型系 | [`models/quadtilt_am/model.sdf:136`](../../models/quadtilt_am/model.sdf#L136) |
| tilt_0_Link | 0 0 0 0 -0 0 | tilt_0_joint | [`models/quadtilt_am/model.sdf:180`](../../models/quadtilt_am/model.sdf#L180) |
| properller_0_Link | 0 0 0 0 -0 0 | properller_0_joint | [`models/quadtilt_am/model.sdf:232`](../../models/quadtilt_am/model.sdf#L232) |
| properller_2_Link | 0 0 0 0 -0 0 | properller_2_joint | [`models/quadtilt_am/model.sdf:284`](../../models/quadtilt_am/model.sdf#L284) |
| tilt_1_Link | 0 0 0 0 -0 0 | tilt_1_joint | [`models/quadtilt_am/model.sdf:336`](../../models/quadtilt_am/model.sdf#L336) |
| properller_1_Link | 0 0 0 0 -0 0 | properller_1_joint | [`models/quadtilt_am/model.sdf:388`](../../models/quadtilt_am/model.sdf#L388) |
| properller_3_Link | 0 0 0 0 -0 0 | properller_3_joint | [`models/quadtilt_am/model.sdf:440`](../../models/quadtilt_am/model.sdf#L440) |

| 飞机 Joint / 类型 | 父 → 子 | Joint pose | relative_to / 默认参考 | axis（Joint 系） | 限位（rad/m, N·m/N, rad/s/m/s） | 证据 |
|---|---|---|---|---|---|---|
| imu_joint / fixed | base_link → imu_link | 省略 → 恒等 | child Link | — | 无轴/限位 | [`models/quadtilt_am/model.sdf:152`](../../models/quadtilt_am/model.sdf#L152) |
| tilt_0_joint / revolute | base_link → tilt_0_Link | 0.255 0 0 -1.5708 -1.5708 -3.14159 | base_link | 0 0 1 | lower=-1.57, upper=1.57, effort=10, velocity=2 | [`models/quadtilt_am/model.sdf:162`](../../models/quadtilt_am/model.sdf#L162) |
| properller_0_joint / revolute | tilt_0_Link → properller_0_Link | 0.05075 0 0.255 -1.5708 -0 -1.5708 | tilt_0_Link | 0 0 1 | lower=-1e+16, upper=1e+16, effort=未显式, velocity=未显式 | [`models/quadtilt_am/model.sdf:214`](../../models/quadtilt_am/model.sdf#L214) |
| properller_2_joint / revolute | tilt_0_Link → properller_2_Link | 0.05075 0 -0.255 -1.5708 -0 -1.5708 | tilt_0_Link | 0 0 1 | lower=-1e+16, upper=1e+16, effort=未显式, velocity=未显式 | [`models/quadtilt_am/model.sdf:266`](../../models/quadtilt_am/model.sdf#L266) |
| tilt_1_joint / revolute | base_link → tilt_1_Link | -0.255 0 0 -1.5708 -1.5708 -3.14159 | base_link | 0 0 1 | lower=-1.57, upper=1.57, effort=10, velocity=2 | [`models/quadtilt_am/model.sdf:318`](../../models/quadtilt_am/model.sdf#L318) |
| properller_1_joint / revolute | tilt_1_Link → properller_1_Link | 0.05075 0 -0.255 -1.5708 -0 -1.5708 | tilt_1_Link | 0 0 1 | lower=-1e+16, upper=1e+16, effort=未显式, velocity=未显式 | [`models/quadtilt_am/model.sdf:370`](../../models/quadtilt_am/model.sdf#L370) |
| properller_3_joint / revolute | tilt_1_Link → properller_3_Link | 0.05075 0 0.255 -1.5708 -0 -1.5708 | tilt_1_Link | 0 0 1 | lower=-1e+16, upper=1e+16, effort=未显式, velocity=未显式 | [`models/quadtilt_am/model.sdf:422`](../../models/quadtilt_am/model.sdf#L422) |
| arm_weld / fixed | base_link → robotic_arm::base_link | 省略 → 恒等 | child Link | — | 无轴/限位 | [`models/quadtilt_am/model.sdf:625`](../../models/quadtilt_am/model.sdf#L625) |

飞机运动分支：`base_link → tilt_0_joint → tilt_0_Link → properller_0/2_joint → properller_0/2_Link`；另一侧是 `tilt_1` 与 `properller_1/3`。IMU 经 imu_joint 固定。四桨不是四个倾转 Joint。各运动 Link 的 pose 相对自身关节为恒等。

`arm_weld` 属于飞机总装配 SDF；其无 pose，默认关节系在机械臂 child 根 Link 上；实际安装位置仍由 include 和 Link 初始 pose 决定。仅写一个 fixed Joint 不会自动把模型搬到目标位姿。

## 3. 机械臂全部 Link、Joint 和 Frame

**[事实]** 完整运动树如下；夹爪不是刚性末端单实体：

```text
飞机 base_link
└─ arm_weld [fixed] → robotic_arm::base_link (O)
   └─ joint_1 [revolute, -Z] → link_1
      └─ joint_2 [revolute, +Z] → link_2
         └─ joint_3 [revolute, +Z] → link_3
            └─ joint_4 [revolute, +Z] → link_4
               └─ joint_5 [revolute, -Z] → link_5
                  ├─ left_finger_joint  [prismatic, +Y] → left_finger
                  ├─ right_finger_joint [prismatic, -Y] → right_finger
                  └─ flange_to_tool0 [Frame] → tool0 [Frame]
```

5 个转动自由度加 2 个手指移动自由度；两个手指共用一个输入，因此机械臂有 7 个运动学自由度、6 路独立输入。没有 mimic 或传动约束证明两个手指始终严格等位移。`tool0` 在当前 SDF 中是 Frame，不是夹爪接触尖点。

| 机械臂 Link | Link pose | relative_to / 默认参考 | 证据 |
|---|---|---|---|
| base_link | 省略 → 0 0 0 0 0 0 | 所属模型系 | [`models/robotic_arm/model.sdf:3`](../../models/robotic_arm/model.sdf#L3) |
| link_1 | 0 0 0 0 -0 0 | joint_1 | [`models/robotic_arm/model.sdf:62`](../../models/robotic_arm/model.sdf#L62) |
| link_2 | 0 0 0 0 -0 0 | joint_2 | [`models/robotic_arm/model.sdf:122`](../../models/robotic_arm/model.sdf#L122) |
| link_3 | 0 0 0 0 -0 0 | joint_3 | [`models/robotic_arm/model.sdf:182`](../../models/robotic_arm/model.sdf#L182) |
| link_4 | 0 0 0 0 -0 0 | joint_4 | [`models/robotic_arm/model.sdf:242`](../../models/robotic_arm/model.sdf#L242) |
| link_5 | 0 0 0 0 -0 0 | joint_5 | [`models/robotic_arm/model.sdf:334`](../../models/robotic_arm/model.sdf#L334) |
| left_finger | 0 0 0.021 0 0 0 | left_finger_joint | [`models/robotic_arm/model.sdf:403`](../../models/robotic_arm/model.sdf#L403) |
| right_finger | 0 0 0.021 0 0 0 | right_finger_joint | [`models/robotic_arm/model.sdf:447`](../../models/robotic_arm/model.sdf#L447) |

| 机械臂 Joint / 类型 | 父 → 子 | Joint pose | relative_to / 默认参考 | axis（Joint 系） | 限位（rad/m, N·m/N, rad/s/m/s） | 证据 |
|---|---|---|---|---|---|---|
| joint_1 / revolute | base_link → link_1 | 0 0 0.03 0 -0 0 | base_link | 0 0 -1 | lower=-2.36, upper=2.36, effort=10, velocity=1.5 | [`models/robotic_arm/model.sdf:32`](../../models/robotic_arm/model.sdf#L32) |
| joint_2 / revolute | link_1 → link_2 | 0.000113 0 0.038401 -1.57079 -1.57079 -3.14159 | link_1 | 0 0 1 | lower=-2.36, upper=2.36, effort=10, velocity=1.5 | [`models/robotic_arm/model.sdf:92`](../../models/robotic_arm/model.sdf#L92) |
| joint_3 / revolute | link_2 → link_3 | 0.10507 0 0 0 -0 0 | link_2 | 0 0 1 | lower=-2.36, upper=2.36, effort=10, velocity=1.5 | [`models/robotic_arm/model.sdf:152`](../../models/robotic_arm/model.sdf#L152) |
| joint_4 / revolute | link_3 → link_4 | 0.087162 -0.000311 -0.000271 0 -0 0 | link_3 | 0 0 1 | lower=-2.36, upper=2.36, effort=10, velocity=1.5 | [`models/robotic_arm/model.sdf:212`](../../models/robotic_arm/model.sdf#L212) |
| joint_5 / revolute | link_4 → link_5 | 0.073 0 0 -1.5708 -0 -1.5708 | link_4 | 0 0 -1 | lower=-2.36, upper=2.36, effort=10, velocity=1.5 | [`models/robotic_arm/model.sdf:272`](../../models/robotic_arm/model.sdf#L272) |
| left_finger_joint / prismatic | link_5 → left_finger | 0 0.005 0.04 0 0 0 | link_5 | 0 1 0 | lower=0, upper=0.03, effort=1.0, velocity=0.2 | [`models/robotic_arm/model.sdf:380`](../../models/robotic_arm/model.sdf#L380) |
| right_finger_joint / prismatic | link_5 → right_finger | 0 -0.005 0.04 0 0 0 | link_5 | 0 -1 0 | lower=0, upper=0.03, effort=1.0, velocity=0.2 | [`models/robotic_arm/model.sdf:425`](../../models/robotic_arm/model.sdf#L425) |

| Frame | attached_to | pose（默认以 attached_to 为参考） | 证据 |
|---|---|---|---|
| flange_to_tool0 | link_5 | 0 0 0 0 -0 0 | [`models/robotic_arm/model.sdf:468`](../../models/robotic_arm/model.sdf#L468) |
| tool0 | flange_to_tool0 | 省略 → 恒等 | [`models/robotic_arm/model.sdf:471`](../../models/robotic_arm/model.sdf#L471) |

### 全部局部几何与惯性 pose

以下表补齐每个 Link 内的 visual/collision/inertial pose；全部均未指定 `relative_to`，以所在 Link 为参考。没有 Mesh 独立坐标变换元素；Mesh 通过父 visual/collision 的 pose 和 scale 定位。inertial 的具体参数见 03。

| 模型 | Link | 元素 | 局部 pose | 证据 |
|---|---|---|---|---|
| 飞机 | base_link | inertial | 0.0 -0.000647 0.024368 0 -0 0 | [`models/quadtilt_am/model.sdf:4`](../../models/quadtilt_am/model.sdf#L4) |
| 飞机 | base_link | collision landing_gear_front_collision | -0.3 0 -0.18 0 0 0 | [`models/quadtilt_am/model.sdf:43`](../../models/quadtilt_am/model.sdf#L43) |
| 飞机 | base_link | collision landing_gear_left_collision | 0.3 0.2 -0.18 0 0 0 | [`models/quadtilt_am/model.sdf:68`](../../models/quadtilt_am/model.sdf#L68) |
| 飞机 | base_link | collision landing_gear_right_collision | 0.3 -0.2 -0.18 0 0 0 | [`models/quadtilt_am/model.sdf:93`](../../models/quadtilt_am/model.sdf#L93) |
| 飞机 | base_link | visual base_link_visual | 0 0 0 0 -0 0 | [`models/quadtilt_am/model.sdf:118`](../../models/quadtilt_am/model.sdf#L118) |
| 飞机 | imu_link | inertial | 0 0 0 0 0 0 | [`models/quadtilt_am/model.sdf:138`](../../models/quadtilt_am/model.sdf#L138) |
| 飞机 | tilt_0_Link | inertial | 0.028311 -0 -0 0 -0 0 | [`models/quadtilt_am/model.sdf:182`](../../models/quadtilt_am/model.sdf#L182) |
| 飞机 | tilt_0_Link | collision tilt_0_Link_collision | 0 0 0 0 -0 0 | [`models/quadtilt_am/model.sdf:194`](../../models/quadtilt_am/model.sdf#L194) |
| 飞机 | tilt_0_Link | visual tilt_0_Link_visual | 0 0 0 0 -0 0 | [`models/quadtilt_am/model.sdf:203`](../../models/quadtilt_am/model.sdf#L203) |
| 飞机 | properller_0_Link | inertial | 0 0 0.005 0 -0 0 | [`models/quadtilt_am/model.sdf:234`](../../models/quadtilt_am/model.sdf#L234) |
| 飞机 | properller_0_Link | visual properller_0_Link_visual | 0 0 0 0 -0 0 | [`models/quadtilt_am/model.sdf:255`](../../models/quadtilt_am/model.sdf#L255) |
| 飞机 | properller_2_Link | inertial | -0 -0 0.005 0 -0 0 | [`models/quadtilt_am/model.sdf:286`](../../models/quadtilt_am/model.sdf#L286) |
| 飞机 | properller_2_Link | visual properller_2_Link_visual | 0 0 0 0 -0 0 | [`models/quadtilt_am/model.sdf:307`](../../models/quadtilt_am/model.sdf#L307) |
| 飞机 | tilt_1_Link | inertial | 0.028311 -0 -0 0 -0 0 | [`models/quadtilt_am/model.sdf:338`](../../models/quadtilt_am/model.sdf#L338) |
| 飞机 | tilt_1_Link | collision tilt_1_Link_collision | 0 0 0 0 -0 0 | [`models/quadtilt_am/model.sdf:350`](../../models/quadtilt_am/model.sdf#L350) |
| 飞机 | tilt_1_Link | visual tilt_1_Link_visual | 0 0 0 0 -0 0 | [`models/quadtilt_am/model.sdf:359`](../../models/quadtilt_am/model.sdf#L359) |
| 飞机 | properller_1_Link | inertial | -0 -0 0.005 0 -0 0 | [`models/quadtilt_am/model.sdf:390`](../../models/quadtilt_am/model.sdf#L390) |
| 飞机 | properller_1_Link | visual properller_1_Link_visual | 0 0 0 0 -0 0 | [`models/quadtilt_am/model.sdf:411`](../../models/quadtilt_am/model.sdf#L411) |
| 飞机 | properller_3_Link | inertial | 0 0 0.005 0 -0 0 | [`models/quadtilt_am/model.sdf:442`](../../models/quadtilt_am/model.sdf#L442) |
| 飞机 | properller_3_Link | visual properller_3_Link_visual | 0 0 0 0 -0 0 | [`models/quadtilt_am/model.sdf:463`](../../models/quadtilt_am/model.sdf#L463) |
| 机械臂 | base_link | inertial | -0.000805 -3.1e-05 0.015733 0 -0 0 | [`models/robotic_arm/model.sdf:4`](../../models/robotic_arm/model.sdf#L4) |
| 机械臂 | base_link | visual base_link_visual | 0 0 0 0 -0 0 | [`models/robotic_arm/model.sdf:16`](../../models/robotic_arm/model.sdf#L16) |
| 机械臂 | link_1 | inertial | -2.1e-05 0.000147 0.016563 0 -0 0 | [`models/robotic_arm/model.sdf:64`](../../models/robotic_arm/model.sdf#L64) |
| 机械臂 | link_1 | visual link_1_visual | 0 0 0 0 -0 0 | [`models/robotic_arm/model.sdf:76`](../../models/robotic_arm/model.sdf#L76) |
| 机械臂 | link_2 | inertial | 0.056726 -0 -0.000271 0 -0 0 | [`models/robotic_arm/model.sdf:124`](../../models/robotic_arm/model.sdf#L124) |
| 机械臂 | link_2 | visual link_2_visual | 0 0 0 0 -0 0 | [`models/robotic_arm/model.sdf:136`](../../models/robotic_arm/model.sdf#L136) |
| 机械臂 | link_3 | inertial | 0.043581 -0.000872 -0.000243 0 -0 0 | [`models/robotic_arm/model.sdf:184`](../../models/robotic_arm/model.sdf#L184) |
| 机械臂 | link_3 | visual link_3_visual | 0 0 0 0 -0 0 | [`models/robotic_arm/model.sdf:196`](../../models/robotic_arm/model.sdf#L196) |
| 机械臂 | link_4 | inertial | 0.044666 0.009062 0.000129 0 -0 0 | [`models/robotic_arm/model.sdf:244`](../../models/robotic_arm/model.sdf#L244) |
| 机械臂 | link_4 | visual link_4_visual | 0 0 0 0 -0 0 | [`models/robotic_arm/model.sdf:256`](../../models/robotic_arm/model.sdf#L256) |
| 机械臂 | link_5 | inertial | 0 0 0.01 0 -0 0 | [`models/robotic_arm/model.sdf:336`](../../models/robotic_arm/model.sdf#L336) |
| 机械臂 | link_5 | visual link_5_visual | 0 0 0 0 -0 0 | [`models/robotic_arm/model.sdf:348`](../../models/robotic_arm/model.sdf#L348) |
| 机械臂 | link_5 | visual gripper_base_visual | 0 0 0.02 0 0 0 | [`models/robotic_arm/model.sdf:366`](../../models/robotic_arm/model.sdf#L366) |
| 机械臂 | left_finger | inertial | 省略 → 恒等 | [`models/robotic_arm/model.sdf:406`](../../models/robotic_arm/model.sdf#L406) |
| 机械臂 | left_finger | visual left_finger_visual | 省略 → 恒等 | [`models/robotic_arm/model.sdf:413`](../../models/robotic_arm/model.sdf#L413) |
| 机械臂 | right_finger | inertial | 省略 → 恒等 | [`models/robotic_arm/model.sdf:449`](../../models/robotic_arm/model.sdf#L449) |
| 机械臂 | right_finger | visual right_finger_visual | 省略 → 恒等 | [`models/robotic_arm/model.sdf:456`](../../models/robotic_arm/model.sdf#L456) |

### joint_1 和旧基座的真实作用

[事实] 旧 `base_link` 有独立质量、惯量和 Mesh visual（机械臂 SDF :3–30），没有有效 collision。它同时是 `arm_weld` child（飞机 SDF :625–628）、`joint_1/parent` 和 `joint_1/pose relative_to`（机械臂 SDF :32–35）。`joint_1` 是单自由度 revolute、轴 `0 0 -1`，限位 ±2.36 rad、effort=10、velocity=1.5；damping=0.05、friction=0.01，并有 ODE implicit_spring_damper/cfm_damping（:36–60）。

[推导] `link_1` 原点在零位与 J1 重合，位于旧根 +Z 30 mm，不是旧根原点；其 X/Y 轴在零位与旧根相同。运动时 `T_M,L1(q1)=Trans(0,0,0.03) Rot(axis=-Z,q1)`，原点沿此纯旋转不变，朝向随 q1 改变。旧模型无法证明实物改造后哪个连杆应当作为固定安装根。

## 4. 删除旧 base_link 的失效面

| 有效引用/数据 | 直接删除后的结果 | 后续必须处理 |
|---|---|---|
| 机械臂 joint_1/parent 和 pose relative_to | 父实体/参考系不存在 | 依实际结构确定新的固定承载体及关节，不删除自由度来掩盖引用错误 |
| link_1/pose relative_to=joint_1 | 若顺手删除 joint_1，该 pose 也悬空 | 保留轴时重建有效关节和参考图；取消轴必须用户确认 |
| 飞机 arm_weld/child=robotic_arm::base_link | 固定连接 child 不存在 | 改为确认后的静止安装根，不能与转动轴并联固定同一对刚体 |
| canonical link 默认首 Link | 改由 link_1 等首个剩余 Link 承担 | 明确新模型系及 canonical link 的附着含义；运动中模型系可能随其转动 |
| base_link 的 visual、惯量 | 被整体移除；总质量少 0.34432 kg | 记录这是结构删除的质量变化，不能假定质量自动转移至新根 |
| base_link Mesh URI | 随 Link 删除不再是活动引用 | 文件仍完整复制并归档；不能因此删源文件 |
| 飞机 control channel 6 → robotic_arm::joint_1 | 若 joint_1 不存在，插件查找失败 | 保留有效映射；只有确认该轴取消后才取消对应 control，后续通道不自动重排 |
| URDF joint_1、gazebo reference=base_link | URDF 同样悬空或与 SDF 分叉 | 同步更新拓扑、frame、资源路径及使用 URDF 的消费者 |

link_2 至 link_5 的 `pose relative_to=joint_n` 没有直接引用旧根；只要上游拓扑和轴正确，它们的局部参数可保持。两个 tool Frame 只依赖 link_5，根删除本身不使这些名称消失，但它们相对飞机的变换会变化。

[用户确认] 若实物真的取消 joint_1，影响的是当前 channel 6（常规对应输出序号 7 的解释仍需飞控配置核对），并减少一个转动自由度。当前 channel 7–10 仍分别对应 joint_2–5，channel 11 为夹爪；不能擅自向前平移编号。如果实物保留第一轴，就必须给它保留一个实际静止父刚体或重建等效装配结构。用无质量虚构 Link 代替实物也不是本轮可决定的修复。

## 5. 安装目标的严格变换

目标定义为 `T_AR = Trans(0,0,-0.044) Rx(π)`：

```text
T_AR = [ 1  0  0   0     ]
       [ 0 -1  0   0     ]
       [ 0  0 -1  -0.044 ]
       [ 0  0  0   1     ]
```

[用户确认] 此处 A 暂按飞机 SDF 模型系解释；当前与 B 重合。若用户实际指 B 的质心系、CAD 基准或飞控 FRD 系，则目标变换需要重新定义。飞机当前质心相对 B 为 `(0,-0.000647,0.024368)`，不在 B 原点；ArduPilot 的 X-forward/Z-down 转换也不是机械安装变换。

对于任意未来机械臂模型 N 和新根 R，正确装配关系为：

```text
T_AR(q) = T_AN · T_NR(q)
T_AN    = T_AR,target · inverse(T_NR)       # R 为静止根时
T_BN    = inverse(T_AB) · T_AR,target · inverse(T_NR)
```

include/pose 决定 N 相对 A 的变换，不直接决定 R。仅当 `T_NR=I` 时，include 直接写目标六元组才足够。fixed Joint 应与这些已算好的初始坐标一致，并连到同一个确认后的根。

### 用旧模型说明 30 mm 误差（条件推导，不是修改建议）

旧 include（飞机 SDF :619–623）为 `(0,0,-0.04,3.1416,0,0)`；零位 `T_M,L1=Trans(0,0,0.03)`。以精确 π 近似，旧 L1 位于 A 的 Z=-0.070 m；用源码 3.1416 计算，Y≈+2.204e-7 m，Z≈-0.069999999999 m。

若只把 include 改成 `(0,0,-0.044,π,0,0)`，保留旧内部偏移，则零位 L1 的 Z=-0.074 m，比目标多向下 30 mm。若目标确实是**旧 L1 的 q1=0 坐标系**，在不改内部结构的条件算例中，应取 `T_AM=T_A,L1,target · inverse(Trans(0,0,0.03))`，得 include `(0,0,-0.014,π,0,0)`。

此补偿不实现“删除 base_link”，也不使转动的 L1 在所有 q1 下保持恒定朝向。不能把 -0.014 m 当成新结构最终安装值；新结构的 `T_NR` 必须按实际坐标重新测定。RPY 中的 π/-π 是等价朝向，验证宜使用旋转矩阵/四元数误差，不按字符串判断。

### 不破坏运动学的实现条件

1. [设计/待确认] 先确定 R 是哪个实际刚体的固定坐标系，以及 joint_1 是否真实保留。如果把原运动 link_1 当成固定根，其朝向恒定和原 joint_1 的运动含义无法同时保持；若目标只在 q1=0 成立，应明确零位条件。
2. [设计] 对确认后的静止根重新表达机械臂：可令 N 与 R 重合，或保持非零 `T_NR` 并用上式补偿。新根的 pose 不能继续引用已删的 joint/base。
3. [设计] 若只是统一重设模型坐标，给所有以旧模型系表达的根级数据左乘同一变换；保留仍有效的 child→joint、joint→parent 局部变换、轴、限位及 link 内 Mesh/惯量坐标。不要把安装偏移重复加到每个下游 Joint。
4. [设计] 若重定义了某个 **Link 自身** 的坐标系，必须同时变换该 Link 的 visual、collision、COM、惯性表达以及相邻 Joint/axis；这已超出单纯 include 移位。为遵守本阶段冻结惯量的要求，优先保留现有 Link 局部坐标，把新安装基准作为明确的装配参考；具体实现须等待用户确认。
5. [设计] 用多组 q（包括非零 q1）比较新旧局部运动链与安装目标；目标为静止根时在所有 q 下验证，目标为运动 Link 零位时分别验证零位目标和运动规律。

## 6. SDF 与 URDF 一致性

**[事实]** 两者前五轴的名称、父子链、轴和主要限位一致，但并非完全一致模型。

| 项目 | 当前 SDF | 当前 URDF | 影响 |
|---|---|---|---|
| 根和前四个活动 Link | base_link、link_1–4 | 同名 | 多处 COM/位移精度有舍入差异，不能宣称逐数值相同 |
| joint_2 origin | `0.000113 0 0.038401 -1.57079 -1.57079 -3.14159`（:93） | xyz=`0.00011279 0 0.038401`，rpy=`1.5708 -1.5708 0`（:156–161） | 接近 pitch=-π/2 的欧拉奇异位姿，不能只按 RPY 字符串判定差 π；需矩阵比较数值误差 |
| joint_4 origin | `0.087162 -0.000311 -0.000271`（:213） | `0.087162 -0.00031113 -0.00027136`（:274–279） | 小数舍入差异 |
| link_5 质量、COM、惯量 | 0.02 kg，Z=0.01，主对角 1e-5（:334–344） | 0.01 kg，Z=-0.0014527，主对角约 1.9e-8/3.66e-8（:292–306） | 动力学明显不一致 |
| 夹爪 | link_5 额外箱体 visual + 两指 Link 和 prismatic Joint（:366–465） | 无 | URDF 无当前夹爪自由度/几何 |
| tool0 | 两个 `<frame>`（:468–471） | `<link name="tool0"/>` + fixed Joint（:351–358） | 终端参考命名类型不同；都不是本轮测定的 TCP |
| 碰撞/控制 | 无机械臂有效 collision；控制在飞机插件 | 无有效 collision；ros_control/transmission 注释 | 不可假定 URDF 自带正在工作的 ROS 控制 |
| Mesh 路径 | model://robotic_arm | package://robotic_arm | 复制目录后 URDF 仍可能解析到旧 ROS 包 |

[设计] 新模型以 SDF 为仿真权威；如继续用 URDF 做 TF/IK/可视化，应同步维护确认后的拓扑、零位变换、轴、末端、质量和新路径。完整复制旧 URDF 可作为来源存档，但必须标明未同步，不能自动转换覆盖已添加夹爪的 SDF。若不再使用 URDF，也需明确其仅存档状态，避免消费者误用。
