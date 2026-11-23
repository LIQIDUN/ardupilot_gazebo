# 06 am 模型迁移实施记录

日期：2026-11-23（Asia/Shanghai）。本轮依据用户明确确认的实物结构实施：拆除机械臂转盘及 joint_1，原 link_1 固定安装，保留四个旋转轴和双指夹爪。**没有进入质量/惯量整定、SITL、ARM、起飞或 PID 调试。**

## 1. 交付状态与必须保留的限制

| 项目 | 结果 |
|---|---|
| `models/am/` | 已创建，20 个文件，13 个 STL 完整复制 |
| 两份 SDF 的 XML / `gz sdf -k` | 通过；飞机检查保留与旧模型相同的 parser 警告 |
| `model://am/robotic_arm` | **已实际解析成功**；strace 证实打开新目录 config/SDF，Gazebo 运行时也加载成功 |
| 新机械臂结构 | 7 Link、6 Joint：4 revolute + 2 prismatic；link_1 为首 Link/默认 canonical link |
| 控制配置 | 12 个有效 control，channel 6 的 joint_1 已删除，7–10 不重排，两项 channel 11 保留 |
| 插件/IMU | 暂停加载时初始化通过，default.log 有 ready 日志，实际 IMU 枚举正确 |
| 安装平移 | 通过：运行时 `(0,0,-0.04400000000000004)` m，无旧 30 mm 偏移 |
| 安装旋转的严格 π 目标 | **未完全满足**：本机 include 展开把 π 量化为 `3.14159`；运行时角误差约 `2.653589793e-6 rad`，详见第 5 节 |
| Mesh 资源 | 12 种活动 STL 的客户端实际打开路径全部在新 am 内；旧机械臂 base STL 未加载 |
| Mesh 显示外观 | **尚未完成图像验收**：客户端加载资源，但三次截图尝试未得到有效图像，不能声称肉眼验证通过 |
| 保护文件 | 三个来源目录 23 个文件、原六份审计文档及 1866 个原有跟踪文件均通过前后哈希复核 |

本报告使用 **[事实]** 标示源文件或本次命令直接证据，**[推导]** 标示计算，**[未验证/待确认]** 标示尚未完成的验收。没有为了通过校验而改动惯量、其他关节或控制参数。严格角度偏差和显示验收缺口保留给用户检查。

## 2. 开始状态、审计文档与复制来源

[事实] 实施前 HEAD 为 `d5146058be1b5b95a0484674f38084d4d6118ec6`；分支 `feat/tmech-benchmark-worlds`。`models/am/` 和本报告均不存在。工作区已有此前六份未跟踪的审计 Markdown；没有跟踪文件修改或暂存变更。

已重读 README 和 01–05，并重新解析实际源 SDF/config、检查插件源码。23 个来源文件的 SHA-256 全部与 01 清单一致，**未发现文档与当前来源文件身份不一致**。用户本次确认解决了历史审计中首轴和根坐标的待确认问题；未修改历史文档。

[事实] 文件复制来源：

- `models/quadtilt_am/model.config`、`model.sdf` → `models/am/`。
- `models/quadtilt_new/meshes/` 的七个指定 STL → `models/am/meshes/`，保留 `properller` 原始拼写与大小写。
- `models/robotic_arm/` 全部 11 个文件及子目录 → `models/am/robotic_arm/`。
- 只修改新副本的两份 SDF 和两份 model.config。其余 **16 个文件逐字节一致**，包括全部 13 个 STL、URDF、package.xml、CMakeLists.txt。

### 最终目录

```text
models/am/
├── model.config
├── model.sdf
├── meshes/
│   ├── base_link.STL
│   ├── tilt_0_Link.STL
│   ├── tilt_1_Link.STL
│   ├── properller_0_Link.STL
│   ├── properller_1_Link.STL
│   ├── properller_2_Link.STL
│   └── properller_3_Link.STL
└── robotic_arm/
    ├── model.config
    ├── model.sdf
    ├── model.urdf
    ├── package.xml
    ├── CMakeLists.txt
    └── meshes/
        ├── base_link.STL       # 完整保留，未被新 SDF 引用
        ├── link_1.STL
        ├── link_2.STL
        ├── link_3.STL
        ├── link_4.STL
        └── link_5.STL
```

### 新文件身份

| 新文件 | 字节 | SHA-256 |
|---|---|---|
| `models/am/meshes/base_link.STL` | 6554484 | `9543645f10040e8d718e7c511b4a0e0d5fb968abe44ef8fbd7e25bb4d27c6528` |
| `models/am/meshes/properller_0_Link.STL` | 17284 | `9f7f7bd9c87d5f79b639be1b542fc64f3921ce65bea4940bd473ca9069d10307` |
| `models/am/meshes/properller_1_Link.STL` | 17284 | `379397162b3baa41b50a202ebed0378c4eaf158e91bcc7406c08ff00316efbe8` |
| `models/am/meshes/properller_2_Link.STL` | 17284 | `633e550f88bb9e692dca8279b938e42d3ce688ea7e8278ecd223e4d96a90f372` |
| `models/am/meshes/properller_3_Link.STL` | 17284 | `203f2caa226f979a3d2db8e26655a7ab8d5aa601c61e53868fa70d344fe0bc91` |
| `models/am/meshes/tilt_0_Link.STL` | 464684 | `06ee5f2af3a48acca266738acd3ade9519e80dd019fa690aa66688de0d4058f1` |
| `models/am/meshes/tilt_1_Link.STL` | 464684 | `7026c9b29b6f527dea75141ec571104c8e8e998a845c5d5f473b333b647959dd` |
| `models/am/model.config` | 726 | `52a43985a8c65b05d8214c78a0c0fc573aa92a01c1e0956b4c8ab5a4a3b24124` |
| `models/am/model.sdf` | 25225 | `8c1d68789271917a0ce07d0d42d25850b96c9db3187634e9769a10163db7aab9` |
| `models/am/robotic_arm/CMakeLists.txt` | 306 | `cc3b30d35b7a0cdb84e546efa1882158888c7ea6779acb6d7211cababa8689d5` |
| `models/am/robotic_arm/meshes/base_link.STL` | 631284 | `ab000432c34feae3925b97fc2d4e2d7c0813cd4326dda37f81213160665cf564` |
| `models/am/robotic_arm/meshes/link_1.STL` | 395384 | `45b5a2db28d758f2faf21e2afc4216b0f05c542466dcd4b85ca8f43419a7232e` |
| `models/am/robotic_arm/meshes/link_2.STL` | 293084 | `43c62293ac498671cbcb31c9f06824cf9eeb3a5ed4064b339d47f65f5550a74b` |
| `models/am/robotic_arm/meshes/link_3.STL` | 626884 | `81c637bfc47c7c178321f9d73b2cf7755720c3197eb32f702d83120526556ba9` |
| `models/am/robotic_arm/meshes/link_4.STL` | 275084 | `0df1b151ce1734d137f055f90595925a674eb68d0b026f0ab076a6d3535582db` |
| `models/am/robotic_arm/meshes/link_5.STL` | 53184 | `549e0104843f4cb247edabfe89545afc9cbd9f51cd2fca4b6d185d48254601a9` |
| `models/am/robotic_arm/model.config` | 734 | `1d3bd12cb74c4f13302b021a715ee4de520140498e4cde6795f92c01529300d1` |
| `models/am/robotic_arm/model.sdf` | 12630 | `402bb8d871f30d889503b7768fa5b020e2b258d361ccfd79ea15152400650c72` |
| `models/am/robotic_arm/model.urdf` | 11880 | `450306f71307d9d5f4729a780ff028843e19c6fde3bf82d77d045417a0e815cc` |
| `models/am/robotic_arm/package.xml` | 527 | `d866c21fe3d58cc2437d41d52b3cec054e5a02afed1e5c73061347b78316e174` |

## 3. SDF/config 的全部授权修改与差异审查

### 机械臂

- 从新 SDF 完整删除旧 `base_link` Link（其 inertial/visual/Mesh 引用一并删除）及 revolute `joint_1`。飞机自身 base_link 完整保留。
- 原 link_1 成为首个 Link；其 pose 从 `relative_to='joint_1'` 的单位位姿改为以模型系表达的单位位姿，不保留 +30 mm。没有额外插入根 Link 或 Frame，没有改 link_1 的局部 Mesh、visual、inertial。
- 所有机械臂 Mesh URI，包括注释中旧 link_5 的 URI，改为 `model://am/robotic_arm/meshes/...`。
- joint_2–joint_5、两个指爪 Joint、其他所有保留 Link、两个末端 Frame 的参数保持原值。机械臂 SDF 内不再出现 base_link 或 joint_1 的实体/参考，也不再引用 base_link.STL。

### 飞机总装配

- 仅将顶层 `<model name='quadtilt_new'>` 改为 `am`，并将飞机 Mesh URI（含注释）重定向到 `model://am/meshes/...`。
- include URI 改为 `model://am/robotic_arm`，实例名仍为 robotic_arm，pose 精确写入用户给出的六元组。原“重心下方”注释改为实际安装基准说明。
- arm_weld 的 child 改为 `robotic_arm::link_1`；parent 仍为 base_link；不添加 arm_weld pose。
- 删除指向 `robotic_arm::joint_1` 的有效 channel 6 control；其余 control 不改。
- `<imuName>` 改为 `am::imu_link::imu_sensor`；IMU Link、Sensor、imu_joint 及所有传感器参数不变。
- 两个新 config 的 sdf 版本从历史 1.6 更新为实际 SDF 1.7；顶层 config/name 改为 am，机械臂 config/name 仍为 robotic_arm。没有改作者或其他历史元数据。

[事实] 差异审查使用“由原 XML 仅施加上述允许变更，再与新 XML 完整树比较”的方式，比较所有有效元素、属性和文本，忽略排版空白/注释。两个完整树比较均通过。对 15 个保留 Link 的 `<inertial>` 另作字节级比较，全部一致；保留 Joint/Plugin 的所有有效内容也被完整树比较覆盖。统一 diff 保存在临时证据目录。

[事实] 8 个飞机 Link、7 个飞机自身 Joint，加装配 arm_weld 共 8 个顶层 Joint，8 个 LiftDrag + 1 个 ArduPilot 插件均保留，名称无意外变化。文件中历史注释里的 channel 6/7 → tilt_2/tilt_3 原样保留，**它们不属于有效 control**；有效 channel 6 已不存在。

[事实] 按用户要求，复制的 URDF/package.xml/CMakeLists.txt 完全不修改、不参与验收；因此 URDF 仍包含旧 base_link/joint_1 与 package://robotic_arm 路径。这是明确保留的来源版本，不是新版仿真的模型依赖或等价运动学描述。

## 4. 最终机械臂清单和连接

| Link | Link pose | 相对参考 | 新源文件 |
|---|---|---|---|
| link_1 | 0 0 0 0 -0 0 | __model__ | [`models/am/robotic_arm/model.sdf:3`](../../models/am/robotic_arm/model.sdf#L3) |
| link_2 | 0 0 0 0 -0 0 | joint_2 | [`models/am/robotic_arm/model.sdf:63`](../../models/am/robotic_arm/model.sdf#L63) |
| link_3 | 0 0 0 0 -0 0 | joint_3 | [`models/am/robotic_arm/model.sdf:123`](../../models/am/robotic_arm/model.sdf#L123) |
| link_4 | 0 0 0 0 -0 0 | joint_4 | [`models/am/robotic_arm/model.sdf:183`](../../models/am/robotic_arm/model.sdf#L183) |
| link_5 | 0 0 0 0 -0 0 | joint_5 | [`models/am/robotic_arm/model.sdf:275`](../../models/am/robotic_arm/model.sdf#L275) |
| left_finger | 0 0 0.021 0 0 0 | left_finger_joint | [`models/am/robotic_arm/model.sdf:344`](../../models/am/robotic_arm/model.sdf#L344) |
| right_finger | 0 0 0.021 0 0 0 | right_finger_joint | [`models/am/robotic_arm/model.sdf:388`](../../models/am/robotic_arm/model.sdf#L388) |

| Joint | 类型 | parent → child | 原始局部 pose（保持） | axis | 新源文件 |
|---|---|---|---|---|---|
| joint_2 | revolute | link_1 → link_2 | 0.000113 0 0.038401 -1.57079 -1.57079 -3.14159 | 0 0 1 | [`models/am/robotic_arm/model.sdf:33`](../../models/am/robotic_arm/model.sdf#L33) |
| joint_3 | revolute | link_2 → link_3 | 0.10507 0 0 0 -0 0 | 0 0 1 | [`models/am/robotic_arm/model.sdf:93`](../../models/am/robotic_arm/model.sdf#L93) |
| joint_4 | revolute | link_3 → link_4 | 0.087162 -0.000311 -0.000271 0 -0 0 | 0 0 1 | [`models/am/robotic_arm/model.sdf:153`](../../models/am/robotic_arm/model.sdf#L153) |
| joint_5 | revolute | link_4 → link_5 | 0.073 0 0 -1.5708 -0 -1.5708 | 0 0 -1 | [`models/am/robotic_arm/model.sdf:213`](../../models/am/robotic_arm/model.sdf#L213) |
| left_finger_joint | prismatic | link_5 → left_finger | 0 0.005 0.04 0 0 0 | 0 1 0 | [`models/am/robotic_arm/model.sdf:321`](../../models/am/robotic_arm/model.sdf#L321) |
| right_finger_joint | prismatic | link_5 → right_finger | 0 -0.005 0.04 0 0 0 | 0 -1 0 | [`models/am/robotic_arm/model.sdf:366`](../../models/am/robotic_arm/model.sdf#L366) |

两个末端 Frame `flange_to_tool0`、`tool0` 保留；双指原始几何、轴方向、限位、阻尼、摩擦不变。机械臂独立 SDF 的第一个 Link 是 link_1，使用 SDFormat 1.7 默认 canonical link 规则；没有添加版本相关扩展属性。libsdformat 直接加载该机械臂时，首 Link 确认为 link_1，模型到该 Link 的解析变换为严格单位矩阵。

展开及运行时装配链为：

```text
am::base_link
└─ am::arm_weld [FIXED]
   └─ am::robotic_arm::link_1
      └─ joint_2 → link_2
         └─ joint_3 → link_3
            └─ joint_4 → link_4
               └─ joint_5 → link_5
                  ├─ left_finger_joint → left_finger
                  └─ right_finger_joint → right_finger
```

[事实] 新飞机展开后有 15 Link、14 Joint（含 IMU fixed Joint 和 arm_weld），不存在 `robotic_arm::base_link` 或 `robotic_arm::joint_1`。检查了展开树的全部 joint parent/child，以及 29 条显式 relative_to/attached_to 参考，未发现悬空引用。12 项 control 的 jointName 全部能在实际运行时关节枚举中找到。

## 5. 安装变换：源配置正确，实际展开存在 π 精度限制

### 源 SDF 与根定义

[`models/am/model.sdf:606`](../../models/am/model.sdf#L606)：

```xml
<include>
  <uri>model://am/robotic_arm</uri>
  <name>robotic_arm</name>
  <pose>0 0 -0.044 3.141592653589793 0 0</pose>
</include>
<joint name="arm_weld" type="fixed">
  <parent>base_link</parent>
  <child>robotic_arm::link_1</child>
</joint>
```

[事实] 新机械臂 link_1 的模型局部 pose 为 `0 0 0 0 -0 0`，没有 relative_to；arm_weld 没有 pose。因此安装变换只在 include 施加一次，旧 30 mm 偏移没有残留。源文件中的目标矩阵为：

```text
[1  0  0   0     ]
[0 -1  0   0     ]
[0  0 -1  -0.044 ]
[0  0  0   1     ]
```

### 实际展开和 libsdformat SemanticPose 复核

[事实] `gz sdf -p` 的关键展开内容：

```xml
<frame name='robotic_arm::__model__' attached_to='robotic_arm::link_1'>
  <pose relative_to='__model__'>0 0 -0.044 3.14159 -0 0</pose>
</frame>
<link name='robotic_arm::link_1'>
  <pose relative_to='robotic_arm::__model__'>0 0 0 0 -0 0</pose>
  <!-- 原局部 inertial/visual 保留 -->
</link>
```

不能把 `3.14159` 只解释为终端显示格式。本轮用临时 C++ 诊断工具直接链接本机 libsdformat9，**直接读取新飞机原始 SDF**，通过 `Link::SemanticPose().Resolve(..., "base_link")` 在内存中解析（没有重新读取终端截断后的 expanded.sdf），以 17 位精度得到：

```text
load_error_count 10
model=am first_link=base_link link_count=15 joint_count=14
position 0 0 -0.043999999999999997
quaternion_wxyz 1.3267948966775328e-06 0.99999999999911982 0 0
1 0 0 0
0 -0.99999999999647926 -2.65358979335273e-06 0
0 2.65358979335273e-06 -0.99999999999647926 -0.043999999999999997
0 0 0 1
rotation_max_abs_error 2.65358979335273e-06
```

[事实] 额外的严格旋转目标检查阈值为 1e-12，诊断返回 **exit=5**，因此严格旋转验证没有通过，不能以源 XML 有 π 就声明安装全部满足。独立机械臂根的单位位姿解析通过（load_error_count=0）；对应原飞机的对照解析也出现同类 include 角度量化。

### Gazebo 实际运行时复核

`gz model -m am -w am_migration_paused -i` 的 protobuf 模型信息显示，机械臂 link_1 相对飞机模型的 pose 为：

```text
{
  "position": {
    "x": 0.0,
    "y": 0.0,
    "z": -0.04400000000000004
  },
  "orientation": {
    "x": 0.9999999999991198,
    "y": 0.0,
    "z": 0.0,
    "w": 1.3267948966775328e-06
  }
}
```

[推导] 平移误差 `4.163336342344337e-17` m；相对 Rx(π) 的旋转角误差 `2.6535897933558441e-06` rad（约 `0.00015203949571828212`°）。该结果与直接 libsdformat 解析一致，排除了只是终端打印舍入的解释。

**结论：−44 mm 安装位置和删除旧偏移已验证；严格 π 朝向仍受本机 include 精度损失限制。** 本轮没有修改 joint_2、link_1 根 pose 或 arm_weld pose 来补偿，没有改变库、插件或模型结构。是否接受该误差、或在后续另行处理解析器精度，留待用户决定。不能把这项标为严格变换 PASS。

## 6. ArduPilot 最终控制映射与 IMU

| channel（0基） | jointName | type | multiplier | offset | P/I/D | cmd_min/max | 新源文件 |
|---|---|---|---|---|---|---|---|
| 0 | properller_0_joint | VELOCITY | 800 | 0 | 0.20/0/0 | -2.5/2.5 | [`models/am/model.sdf:507`](../../models/am/model.sdf#L507) |
| 1 | properller_1_joint | VELOCITY | 800 | 0 | 0.20/0/0 | -2.5/2.5 | [`models/am/model.sdf:508`](../../models/am/model.sdf#L508) |
| 2 | properller_2_joint | VELOCITY | -800 | 0 | 0.20/0/0 | -2.5/2.5 | [`models/am/model.sdf:509`](../../models/am/model.sdf#L509) |
| 3 | properller_3_joint | VELOCITY | -800 | 0 | 0.20/0/0 | -2.5/2.5 | [`models/am/model.sdf:510`](../../models/am/model.sdf#L510) |
| 4 | tilt_0_joint | POSITION | 1.495 | -0.85 | 40.0/0/0.5 | -2.0/2.0 | [`models/am/model.sdf:514`](../../models/am/model.sdf#L514) |
| 5 | tilt_1_joint | POSITION | 1.495 | -0.85 | 40.0/0/0.5 | -2.0/2.0 | [`models/am/model.sdf:515`](../../models/am/model.sdf#L515) |
| 7 | robotic_arm::joint_2 | POSITION | 4.7124 | -0.5 | 20.0/0/0.05 | -2.0/2.0 | [`models/am/model.sdf:518`](../../models/am/model.sdf#L518) |
| 8 | robotic_arm::joint_3 | POSITION | 4.7124 | -0.5 | 20.0/0/0.05 | -2.0/2.0 | [`models/am/model.sdf:531`](../../models/am/model.sdf#L531) |
| 9 | robotic_arm::joint_4 | POSITION | 4.7124 | -0.5 | 20.0/0/0.05 | -2.0/2.0 | [`models/am/model.sdf:544`](../../models/am/model.sdf#L544) |
| 10 | robotic_arm::joint_5 | POSITION | 4.7124 | -0.5 | 10.0/0/0 | -2.0/2.0 | [`models/am/model.sdf:557`](../../models/am/model.sdf#L557) |
| 11 | robotic_arm::left_finger_joint | POSITION | 0.025 | 0 | 0.5/0/0.01 | -1.0/1.0 | [`models/am/model.sdf:572`](../../models/am/model.sdf#L572) |
| 11 | robotic_arm::right_finger_joint | POSITION | 0.025 | 0 | 0.5/0/0.01 | -1.0/1.0 | [`models/am/model.sdf:590`](../../models/am/model.sdf#L590) |

4 电机 + 2 倾转 + 4 机械臂转动 + 2 指爪 = 12 项 control。channel 7–10 保持原编号；channel 11 两项共享输入保留；没有有效 channel 6。FDM 127.0.0.1、9002/9003、超时 5、坐标转换、增益和其他字段与来源一致。

[事实] runtime 模型为直接 include 的 `am`，IMU Link 为 `am::imu_link`，Sensor 为 imu_sensor；实际话题为：

```text
/gazebo/am_migration_paused/am/imu_link/imu_sensor/imu
```

`imuName=am::imu_link::imu_sensor` 与该作用域相符。源码 `src/ArduPilotPlugin.cc:83–106` 使用完整 Sensor 名称的后缀匹配，`:535–554` 通过 GetJoint 查找 control 对象，`:697–757` 查找 IMU，`:891–908` 在这些检查之后初始化 sockets 并记录 ready 日志。实际 default.log 出现：

```text
[am] ArduPilot ready to fly. The force will be with you
```

该字符串是插件初始化日志，**不代表已经起飞、可飞或控制回归通过**。还核对了 `/proc/<gzserver PID>/maps`，实际加载的是本仓库 `build/libArduPilotPlugin.so`；运行时 UDP 9002 绑定由该 gzserver 持有。未出现“Couldn't find specified joint”“imu_sensor not found”“aborting plugin”类错误。没有向任何控制输入发送数据。

## 7. 动力学保护结果

[事实] 对全部 15 个保留 Link 的 `<inertial>` 作字节级比较，mass、inertial pose、惯量六分量全部与对应原 SDF 一致。完整树比较还覆盖 joint_2–5/双指的 pose、axis、lower/upper、effort/velocity、damping/friction 及其他物理参数。没有做惯量平移、合并或转移。

| 范围 | 迁移前 kg | 迁移后 kg | 变化 |
|---|---|---|---|
| 飞机自身 | 4.350820 | 4.350820 | 0 |
| 机械臂 | 0.584975 | 0.240655 | 仅删旧根 0.344320 |
| 总装配 | 4.935795 | 4.591475 | −0.344320 |

以上是质量标量求和，不是整机惯量求和，也不是实测新整机参数。旧四桨非物理主惯量三角关系、机械臂无有效 collision、旧 link_5 人工惯量等审计限制均保持原状，没有为通过检查而整定。

## 8. 静态检查与路径解析的实际输出

临时证据目录：`/tmp/am_migration_20261123_pxm9xbhn`。临时脚本、world、展开结果、strace 和日志均不加入模型目录或 Git。日志为本机临时证据，可能被系统清理；关键输出和已知限制同时嵌入本报告。

### 机械臂 `gz sdf -k`（exit=0）

```text
Check complete
```

### 飞机总装配 `gz sdf -k`（exit=0）

```text
Check complete
Warning [parser.cc:833] XML Attribute[version] in element[sdf] not defined in SDF, ignoring.
```

### `gz sdf -p models/am/model.sdf`（exit=0）

输出保存为 `expanded.sdf`；stderr 与飞机 -k 相同：

```text
Warning [parser.cc:833] XML Attribute[version] in element[sdf] not defined in SDF, ignoring.
```

strace 确认 include 实际打开下列新文件：

```text
3995198 openat(AT_FDCWD, "/home/liqidun/github/ardupilot_gazebo/models/am/robotic_arm/model.config", O_RDONLY) = 31
3995198 openat(AT_FDCWD, "/home/liqidun/github/ardupilot_gazebo/models/am/robotic_arm/model.sdf", O_RDONLY) = 31
```

本轮没有改变嵌套目录、没有加入 models/am 为新搜索根、没有回退旧 URI。所有有效新 SDF 模型专属 URI 都是 `model://am/...`；注释中的旧 Mesh URI 也已重定向。系统 Gazebo 材质 URI 保持不变。

### 较严格 DOM 检查的继承性错误

额外 C++ Root::Load 检查报告 10 条错误：六条已有 material/script 缺 uri、四条已有桨惯量无效。对原飞机运行相同诊断，错误列表逐条相同。它们未阻止 Gazebo Classic 实际暂停加载，但不能把 `gz sdf -k` 通过扩大为“所有 DOM/物理检查均通过”。新机械臂独立 Root::Load 无错误。

```text
Error Code 8 Msg: A <script> element is missing a child <uri> element, or the <uri> element is empty.
Error Code 8 Msg: A <script> element is missing a child <uri> element, or the <uri> element is empty.
Error Code 17 Msg: A link named properller_0_Link has invalid inertia.
Error Code 8 Msg: A <script> element is missing a child <uri> element, or the <uri> element is empty.
Error Code 17 Msg: A link named properller_2_Link has invalid inertia.
Error Code 8 Msg: A <script> element is missing a child <uri> element, or the <uri> element is empty.
Error Code 8 Msg: A <script> element is missing a child <uri> element, or the <uri> element is empty.
Error Code 17 Msg: A link named properller_1_Link has invalid inertia.
Error Code 8 Msg: A <script> element is missing a child <uri> element, or the <uri> element is empty.
Error Code 17 Msg: A link named properller_3_Link has invalid inertia.
```

C++ 临时诊断最初使用了不属于本版本的 Root::Model 接口而编译失败，改为本机头文件的 ModelByIndex(0) 后编译通过；编译失败与重试日志均保留。随后读取到上述继承性 DOM 错误，再完成几何诊断，最终严格旋转检查仍为 exit=5。没有将失败运行覆盖成 PASS。

## 9. Gazebo 暂停加载、资源访问和日志

### 隔离与不发控制的证据

实施前没有 Gazebo/SITL 进程，9002/9003 空闲。测试使用临时 `paused.world`，仅含内联灯光、新 am 的 include 和 GUI 初始相机，不修改原有 world；am 放在世界 Z=1 m 便于观察，其相对安装变换不受此世界放置影响。

```text
GAZEBO_MASTER_URI=http://127.0.0.1:11496
GAZEBO_MODEL_PATH=/home/liqidun/github/ardupilot_gazebo/models
GAZEBO_PLUGIN_PATH=/home/liqidun/github/ardupilot_gazebo/build:/usr/lib/x86_64-linux-gnu/gazebo-11/plugins
GAZEBO_RESOURCE_PATH=/usr/share/gazebo-11
GAZEBO_MODEL_DATABASE_URI=
gzserver --verbose --pause /tmp/am_migration_20261123_pxm9xbhn/paused.world
```

[事实] 读取 world_stats 的所有样本均为：

```text
sim_time { sec: 0 nsec: 0 }
paused: true
iterations: 0
```

实际模型信息枚举 15 Link、14 Joint，arm_weld type=FIXED，parent=`am::base_link`，child=`am::robotic_arm::link_1`。该结果证明实体和固定连接的初始化存在；因为全程暂停，本轮未测试受力后的固定连接稳定性或任何关节的动态响应。

没有启动 SITL、MAVROS、ROS 控制桥，没有 ARM、步进、解暂停或发送关节/电机控制。只读取 model info、topic list 和 world_stats。启动器为本次专用进程组，结束时只向本次组发 SIGINT；server 返回 0，所有测试 client 已关闭，9002/11496 已释放。未终止用户已有进程。

### 实际 Mesh 打开路径

[事实] 服务端打开两倾转 collision STL；客户端成功打开以下 12 种活动 STL，文件追踪没有打开旧模型的运行时 SDF/Mesh。GUI 的模型目录列表扫描读取了旧目录的 model.config，这不是新模型使用旧资源；完整追踪中旧来源目录的额外打开仅为 config 浏览。

```text
/home/liqidun/github/ardupilot_gazebo/models/am/meshes/base_link.STL
/home/liqidun/github/ardupilot_gazebo/models/am/meshes/properller_0_Link.STL
/home/liqidun/github/ardupilot_gazebo/models/am/meshes/properller_1_Link.STL
/home/liqidun/github/ardupilot_gazebo/models/am/meshes/properller_2_Link.STL
/home/liqidun/github/ardupilot_gazebo/models/am/meshes/properller_3_Link.STL
/home/liqidun/github/ardupilot_gazebo/models/am/meshes/tilt_0_Link.STL
/home/liqidun/github/ardupilot_gazebo/models/am/meshes/tilt_1_Link.STL
/home/liqidun/github/ardupilot_gazebo/models/am/robotic_arm/meshes/link_1.STL
/home/liqidun/github/ardupilot_gazebo/models/am/robotic_arm/meshes/link_2.STL
/home/liqidun/github/ardupilot_gazebo/models/am/robotic_arm/meshes/link_3.STL
/home/liqidun/github/ardupilot_gazebo/models/am/robotic_arm/meshes/link_4.STL
/home/liqidun/github/ardupilot_gazebo/models/am/robotic_arm/meshes/link_5.STL
```

机械臂旧 base_link.STL 完整复制但未被 SDF/客户端引用。没有看到 Mesh 不存在或找不到材质的加载错误。服务端有意移除 DISPLAY 进行 headless 加载，因此出现 rendering disabled；另以 DISPLAY=:1 启动客户端检查资源访问。客户端连接到同一个隔离 master，没有启动其他 world。

### 显示验收未完成

初次使用 ImageMagick import 抓取本次窗口，10 秒超时。后续两次 xwd 捕获均得到 BadWindow（窗口生命周期/抓取目标问题的具体原因尚未证实），没有有效截图。保留失败日志，**不声称 Mesh 的屏幕外观已经验证通过**；当前证据仅支持资源被实际打开、运行时实体存在，外观仍需用户检查。

第二、三次捕获错误原文：

```text
X Error of failed request:  BadWindow (invalid Window parameter)
  Major opcode of failed request:  3 (X_GetWindowAttributes)
  Resource id in failed request:  0x9a0000e
  Serial number of failed request:  7
  Current serial number in output stream:  8

X Error of failed request:  BadWindow (invalid Window parameter)
  Major opcode of failed request:  3 (X_GetWindowAttributes)
  Resource id in failed request:  0x980000e
  Serial number of failed request:  7
  Current serial number in output stream:  8
```

### 服务端完整 stdout/stderr（仅移除 ANSI 颜色码）

```text
Gazebo multi-robot simulator, version 11.15.1
Copyright (C) 2012 Open Source Robotics Foundation.
Released under the Apache 2 License.
http://gazebosim.org


#     # ####### ####### ###  #####  #######
##    # #     #    #     #  #     # #
# #   # #     #    #     #  #       #
#  #  # #     #    #     #  #       #####
#   # # #     #    #     #  #       #
#    ## #     #    #     #  #     # #
#     # #######    #    ###  #####  #######

This version of Gazebo, now called Gazebo classic, reaches end-of-life
in January 2025. Users are highly encouraged to migrate to the new Gazebo
using our migration guides (https://gazebosim.org/docs/latest/gazebo_classic_migration/)


[Msg] Waiting for master.
[Msg] Connected to gazebo master @ http://127.0.0.1:11496
[Msg] Publicized address: 169.254.128.31
[Err] [RenderEngine.cc:749] Can't open display: 
[Wrn] [RenderEngine.cc:89] Unable to create X window. Rendering will be disabled
[Wrn] [RenderEngine.cc:292] Cannot initialize render engine since render path type is NONE. Ignore this warning if rendering has been turned off on purpose.
Warning [parser.cc:833] XML Attribute[version] in element[sdf] not defined in SDF, ignoring.
[Msg] Loading world file [/tmp/am_migration_20261123_pxm9xbhn/paused.world]
[Msg] [ArduPilotPlugin] Model :am
[Msg] [ArduPilotPlugin] Model :  base_link
[Msg] [ArduPilotPlugin] Model :    landing_gear_front_collision
[Msg] [ArduPilotPlugin] Model :      
[Msg] [ArduPilotPlugin] Model :    landing_gear_left_collision
[Msg] [ArduPilotPlugin] Model :      
[Msg] [ArduPilotPlugin] Model :    landing_gear_right_collision
[Msg] [ArduPilotPlugin] Model :      
[Msg] [ArduPilotPlugin] Model :  imu_link
[Msg] [ArduPilotPlugin] Model :  tilt_0_Link
[Msg] [ArduPilotPlugin] Model :    tilt_0_Link_collision
[Msg] [ArduPilotPlugin] Model :      
[Msg] [ArduPilotPlugin] Model :  properller_0_Link
[Msg] [ArduPilotPlugin] Model :  properller_2_Link
[Msg] [ArduPilotPlugin] Model :  tilt_1_Link
[Msg] [ArduPilotPlugin] Model :    tilt_1_Link_collision
[Msg] [ArduPilotPlugin] Model :      
[Msg] [ArduPilotPlugin] Model :  properller_1_Link
[Msg] [ArduPilotPlugin] Model :  properller_3_Link
[Msg] [ArduPilotPlugin] Model :  robotic_arm::link_1
[Msg] [ArduPilotPlugin] Model :  robotic_arm::link_2
[Msg] [ArduPilotPlugin] Model :  robotic_arm::link_3
[Msg] [ArduPilotPlugin] Model :  robotic_arm::link_4
[Msg] [ArduPilotPlugin] Model :  robotic_arm::link_5
[Msg] [ArduPilotPlugin] Model :  robotic_arm::left_finger
[Msg] [ArduPilotPlugin] Model :  robotic_arm::right_finger
[Msg] [ArduPilotPlugin] Model :  imu_joint
[Msg] [ArduPilotPlugin] Model :  tilt_0_joint
[Msg] [ArduPilotPlugin] Model :  properller_0_joint
[Msg] [ArduPilotPlugin] Model :  properller_2_joint
[Msg] [ArduPilotPlugin] Model :  tilt_1_joint
[Msg] [ArduPilotPlugin] Model :  properller_1_joint
[Msg] [ArduPilotPlugin] Model :  properller_3_joint
[Msg] [ArduPilotPlugin] Model :  robotic_arm::joint_2
[Msg] [ArduPilotPlugin] Model :  robotic_arm::joint_3
[Msg] [ArduPilotPlugin] Model :  robotic_arm::joint_4
[Msg] [ArduPilotPlugin] Model :  robotic_arm::joint_5
[Msg] [ArduPilotPlugin] Model :  robotic_arm::left_finger_joint
[Msg] [ArduPilotPlugin] Model :  robotic_arm::right_finger_joint
[Msg] [ArduPilotPlugin] Model :  arm_weld
```

### 插件 ready 证据所在日志

Gazebo 的 `gzlog` 不写入上述 stdout。启动器最初只看 stdout 的 ready 标志为 false，随后读取实际默认日志确认初始化成功：

```text
(1795433525 916683732) [am] ArduPilot ready to fly. The force will be with you
```

客户端另有模型目录下历史非模型文件的目录扫描提示、关闭在线模型数据库后的本地模型提示及无 spacenav daemon 提示，未据此删除任何旧文件或改模型结构。

### 验证进程的仓库外运行副作用

[事实] 虽设置了 GAZEBO_LOG_PATH 到 /tmp，Classic Console 仍默认写入 `~/.gazebo/server-11496/` 和 `~/.gazebo/client-11496/`，libsdformat 写入 `~/.sdformat/sdformat.log`；GUI 还访问系统 dconf 和 NVIDIA/临时 shader 缓存。关键默认日志已复制到临时证据目录。没有把这些运行日志/缓存计入“模型源文件未修改”的声明，也没有清理或改写用户的原有配置。仓库内写入范围仍仅为 models/am 和本报告。

## 10. 源文件最终哈希、Git 范围与停止状态

以下 23 个来源文件均重新计算，与实施前逐文件相同：

| 原始文件 | 实施前/实施后 SHA-256（相同） | 结果 |
|---|---|---|
| `models/quadtilt_am/model.config` | `55f942aa8793127b467ac08a337c65983f87ad5f34dc36bda780617051353568` | 一致 |
| `models/quadtilt_am/model.sdf` | `f50fc25a10ae9eaa9f90431d15a0541222c4e78c99d7cf9b55467e1bb4f206ce` | 一致 |
| `models/robotic_arm/CMakeLists.txt` | `cc3b30d35b7a0cdb84e546efa1882158888c7ea6779acb6d7211cababa8689d5` | 一致 |
| `models/robotic_arm/meshes/base_link.STL` | `ab000432c34feae3925b97fc2d4e2d7c0813cd4326dda37f81213160665cf564` | 一致 |
| `models/robotic_arm/meshes/link_1.STL` | `45b5a2db28d758f2faf21e2afc4216b0f05c542466dcd4b85ca8f43419a7232e` | 一致 |
| `models/robotic_arm/meshes/link_2.STL` | `43c62293ac498671cbcb31c9f06824cf9eeb3a5ed4064b339d47f65f5550a74b` | 一致 |
| `models/robotic_arm/meshes/link_3.STL` | `81c637bfc47c7c178321f9d73b2cf7755720c3197eb32f702d83120526556ba9` | 一致 |
| `models/robotic_arm/meshes/link_4.STL` | `0df1b151ce1734d137f055f90595925a674eb68d0b026f0ab076a6d3535582db` | 一致 |
| `models/robotic_arm/meshes/link_5.STL` | `549e0104843f4cb247edabfe89545afc9cbd9f51cd2fca4b6d185d48254601a9` | 一致 |
| `models/robotic_arm/model.config` | `6c44da904a0266246f862229107417c4cf660c392c54228bac6e7c304b8f4dd7` | 一致 |
| `models/robotic_arm/model.sdf` | `89834b56690b6de8db89b62b11fdcf3c8e8d4c97b397c6e42203cfbd17bab030` | 一致 |
| `models/robotic_arm/model.urdf` | `450306f71307d9d5f4729a780ff028843e19c6fde3bf82d77d045417a0e815cc` | 一致 |
| `models/robotic_arm/package.xml` | `d866c21fe3d58cc2437d41d52b3cec054e5a02afed1e5c73061347b78316e174` | 一致 |
| `models/quadtilt_new/meshes/base_link.STL` | `9543645f10040e8d718e7c511b4a0e0d5fb968abe44ef8fbd7e25bb4d27c6528` | 一致 |
| `models/quadtilt_new/meshes/properller_0_Link.STL` | `9f7f7bd9c87d5f79b639be1b542fc64f3921ce65bea4940bd473ca9069d10307` | 一致 |
| `models/quadtilt_new/meshes/properller_1_Link.STL` | `379397162b3baa41b50a202ebed0378c4eaf158e91bcc7406c08ff00316efbe8` | 一致 |
| `models/quadtilt_new/meshes/properller_2_Link.STL` | `633e550f88bb9e692dca8279b938e42d3ce688ea7e8278ecd223e4d96a90f372` | 一致 |
| `models/quadtilt_new/meshes/properller_3_Link.STL` | `203f2caa226f979a3d2db8e26655a7ab8d5aa601c61e53868fa70d344fe0bc91` | 一致 |
| `models/quadtilt_new/meshes/tilt_0_Link.STL` | `06ee5f2af3a48acca266738acd3ade9519e80dd019fa690aa66688de0d4058f1` | 一致 |
| `models/quadtilt_new/meshes/tilt_1_Link.STL` | `7026c9b29b6f527dea75141ec571104c8e8e998a845c5d5f473b333b647959dd` | 一致 |
| `models/quadtilt_new/model.config` | `292427ba846b0bcfcc264a524a2a96d2c49f366f5c4b940cfbc1a19344bf3d67` | 一致 |
| `models/quadtilt_new/model.sdf` | `98ce6e8194a91463614a9b31ac8559c29028aa8561353b5e47ff111c0777556f` | 一致 |
| `models/quadtilt_new/model.urdf` | `8c1caa6f9aa331ee075fd897f7099ff1f28dbce802fbfb88e0c79c3e6a2884ca` | 一致 |

| 目录 | 实施前聚合 SHA-256 | 实施后聚合 SHA-256 |
|---|---|---|
| models/quadtilt_am | 52cca6a7049406c0994942951dcfe62c1f452ce3aad7fdaebc0039ee0f1702ed | 52cca6a7049406c0994942951dcfe62c1f452ce3aad7fdaebc0039ee0f1702ed |
| models/robotic_arm | b7f60659ff74ca88cc98cf8c0edb0784ccf7fe6bb682c6a3a32a0873cfa0abe6 | b7f60659ff74ca88cc98cf8c0edb0784ccf7fe6bb682c6a3a32a0873cfa0abe6 |
| models/quadtilt_new | da563ca05058ea8fe12b8320e3667fa2e1cc959eedfba744f77708d7b7e0fd6b | da563ca05058ea8fe12b8320e3667fa2e1cc959eedfba744f77708d7b7e0fd6b |

目录聚合算法：按相对目录的文件名排序，逐项追加 `相对路径 UTF-8 + NUL + 文件 SHA-256 二进制摘要` 后计算 SHA-256；同时检查文件集合不增减。

[事实] 六份原审计文档逐字节不变；1866 个原有跟踪文件的逐项哈希不变；Git 已跟踪文件 diff 和暂存区 diff 为空。没有提交或推送。预期 Git 未跟踪变化为：

- 实施前已有的六份审计 Markdown（原样保留）；
- 本轮新增 `models/am/` 的 20 个文件；
- 本轮新增这一份 `06_implementation_report.md`。

### 临时证据身份

| 证据文件（相对临时目录） | 字节 | SHA-256 |
|---|---|---|
| baseline.json | 237337 | 9aea9cbdecf655d32d114ea7ab4bd17f55c98bcb7433b215c8a02102474d55a0 |
| static_review.json | 2706 | 53f87e2845d4623713fd1d7f407313c2b9ddb56357dc8394044ca26ccc40515f |
| aircraft.diff | 6947 | d093b2836f9d591558c8b6060ad4e3db45e689541d74b635ed3fdc46f185fd17 |
| arm.diff | 11969 | 9aab593382ef00fda7f6bb634102ad06c52d097bf1b3d935015c155246d2b91a |
| arm_check.stdout | 15 | bcfcc9e69fb54703a533ec0f43063e5e481562057f7205b7f071930e77f68c84 |
| arm_check.stderr | 0 | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 |
| aircraft_check.stdout | 15 | bcfcc9e69fb54703a533ec0f43063e5e481562057f7205b7f071930e77f68c84 |
| aircraft_check.stderr | 104 | d63a7d92cfd525b9e38ab1847ca300154c0c45433b2353fdc8d9e214e18c2aaf |
| expanded.sdf | 33440 | b87e96c76756ab1a32667ace113d314c62becc964812199afed7f6ad422258ac |
| expand.stderr | 104 | d63a7d92cfd525b9e38ab1847ca300154c0c45433b2353fdc8d9e214e18c2aaf |
| expand.trace | 554669 | e9dc30b98af83d7f35f4622ed1c65be6c553024713f9989e9179674cc74020ff |
| semantic_pose_final.stdout | 350 | 5c40039e292b4cedda34e93ea259e4671b0d455fa599116788b31c0197e8eff2 |
| semantic_pose_final.stderr | 1000 | 1f34ae1d213e99718cd22eafe628ebff4c6c3ff74dbbed4a374a8f3b5033d745 |
| arm_root_pose.stdout | 178 | f240588501029f3106b7fe7ef3cb0d9d45c40e739c4966da9f07f378f8041f3a |
| old_model_dom.stderr | 1000 | 1f34ae1d213e99718cd22eafe628ebff4c6c3ff74dbbed4a374a8f3b5033d745 |
| paused.world | 505 | ec350d6c9ae6a7526b05fa5829f6c5b7ca34639ad9401659162bf73eaee3d904 |
| runtime_env.json | 394 | cedd980fac9064a884204b834faa4a23859bee9be6b32efcf173d0c0ab789d52 |
| gzserver.log | 5434 | 0d0dc6caa10b4d50903841ed8517f84c50de90be541cce5b007593e458c98419 |
| server_default.log | 4013 | 2deb8b53183eb00a70856b86813adff9adb2f0296bedb5e15bb3fcf272fabc46 |
| gzserver.trace | 560128 | d4c39fcebdd137c5f01f7091b9f95e8c340cb6d17907fef0184a34d6a313449b |
| model_info.stdout | 55632 | 87d6c93ecd0a6a2f738464423d8a72d98f0b8d31758e5eb836ae3daf6cf3d8fd |
| runtime_model_review.json | 5067 | 78ad576d7bc280afc5e49e7f87a765f53c93d564ce5fb98d3bf5a8e7b87851ff |
| world_stats.stdout | 1358 | b2d612cc729b4255489537465402f43d51f9dab3c987306da317f33a370f7311 |
| mesh_access_review.json | 3741 | 8ffb69641817e91a209fd53e3a2da11e8f4f4dd8d4d498df39b84277fb7cd285 |
| gzclient.log | 1196 | 9c437f1dda9f4404872705960e7dd991ceb214a11972233c8e60f5f7e22c9953 |
| gzclient_retry.log | 1196 | 9c437f1dda9f4404872705960e7dd991ceb214a11972233c8e60f5f7e22c9953 |
| gzclient_final.log | 1196 | 9c437f1dda9f4404872705960e7dd991ceb214a11972233c8e60f5f7e22c9953 |
| gzclient.trace | 1461845 | 712f7e4cc70aec9b3c710c35992461ac6045426350982a36accd661d4995f572 |
| gzclient_retry.trace | 1465784 | 98c5538a927c40b1c4052281c3b8ce2cc5b26d50c24206dd75636f1e9c979f42 |
| gzclient_final.trace | 1471419 | 936348c59208e3ee04393ae7f99d18ed75767c285ee4403317440da4b9b04591 |
| screenshot_retry.log | 253 | 5a8be0c9ca65bd6996d03ce55987ff20ddc27a51c62844a0da2633ede0226c55 |
| screenshot_final.log | 253 | 24a9e4e65721da7bf272e802d0931f984064ba4053f6d72cd9a82db7a306037e |
| runtime_ports.txt | 12236 | 9957a82c34b24a680a02619235056590ac4b712f039904a0ba1305c9ae1e4c2b |
| postflight_ports.txt | 7406 | fc75bd0add0f6563e158125789e519e1034a9b594799b6e944eb98f1445073f9 |
| server_exit.json | 65 | 0f525f0a3f6fc5c57676ccb00bbe35b4d96cdd38fdb57b0652bab2c8720b9cb0 |
| final_validation.json | 538 | 47b2f45a2f55e4277e0ab2ed2a7869b7b9ee295eeded9c86081d161a0d4b2e6b |

## 11. 未完成事项和停止点

1. 严格 Rx(π) 的运行时精度目标未通过：当前环境 include 路径实际产生约 2.65e-6 rad 偏差。模型源六元组保持用户要求，未擅自添加补偿或改库；是否接受此精度，或另行授权处理解析器，等待用户检查决定。
2. Mesh 外观未获有效截图，仍需用户人工检查；资源路径/实体加载已有证据。
3. 本轮只证明暂停加载与插件初始化。没有验证电机、倾转、四轴或夹爪的动态控制、固定连接受力稳定性，更没有实机/飞行证据。
4. URDF 是用户要求保留的原样来源文件；与四轴新 SDF 不一致，不纳入本轮验收。现有桨惯量及 material/script 的较严格 DOM 错误保持原状，不做修复。

**本轮到此停止，等待用户检查新模型；不自动进入动力学更新、SITL 或 PID 整定。**

## 12. 安装高度修正：以 joint_2 轴心下置 82.5 mm 为设计基准

本节为后续安装高度修正记录，替代前文 −44 mm 的当前高度设置；前文其他结构、控制及验证限制保持原结论。本轮只改 `models/am/model.sdf:609` 的机械臂 include/pose 中 Z 值，未重建 include 块，并将本节追加到报告。

### 修改前后

```xml
<!-- 修改前 -->
<pose>0 0 -0.044 3.141592653589793 0 0</pose>
<!-- 修改后 -->
<pose>0 0 -0.0441 3.141592653589793 0 0</pose>
```

新设计基准为 joint_2 轴心位于飞机 base_link 原点下方约 82.5 mm。用户明确采用工程取整的 link_1 安装高度 −44.1 mm，保持原 joint_2 相对 link_1 的局部位置 `(0.000113, 0, 0.038401)` m 和安装 Roll=π：

```text
z_joint2 = -0.0441 - 0.038401 = -0.082501 m = -82.501 mm
设计目标 = -82.500 mm
差值     = -0.001 mm（比目标向下多 0.001 mm，按用户要求保留，不补偿）
```

源文件 Roll 仍为 `3.141592653589793`，Pitch/Yaw 均为 0，没有角度补偿。机械臂根单位位姿及 arm_weld 配置不变，安装高度仅在 include 中施加一次。

### 本轮实际验证

- `gz sdf -k models/am/model.sdf`：exit=0，输出 `Check complete`。
- `gz sdf -p models/am/model.sdf`：exit=0，机械臂正常展开，仍有 15 Link、14 Joint；`robotic_arm::__model__` 相对飞机模型的 pose 为 `0 0 -0.0441 3.14159 -0 0`，link_1 相对该 Frame 仍为单位位姿。
- 根据实际展开树的 relative_to 关系复合齐次变换，求 `inverse(T_model,base_link) × T_model,joint_2`，joint_2 的飞机系坐标为 `[0.000113, -1.0190050165453818e-07, -0.0825009999998648]` m，即 Z≈−0.082501 m。
- 展开角度的有限精度带来 Z 与理想 π 计算值约 `1.3521128661153625e-13` m 的数值差异，不影响本次约 −82.501 mm 的高度核对。已知 include 旋转精度限制沿用前文记录，不声称该限制得到修复，也不添加补偿。

两个 gz 命令均保留原有警告，原文如下；没有为消除警告而改其他配置：

```text
Warning [parser.cc:833] XML Attribute[version] in element[sdf] not defined in SDF, ignoring.
```

临时证据保存于 `/tmp/am_height_correction_6d_tsxmw`：`check.stdout`、`check.stderr`、`expanded.sdf`、`expand.stderr`、`transform_check.json`、`model_pose.diff`。本轮没有启动 Gazebo server/client、SITL 或电机，没有发送控制命令。

### 差异与保护范围

实施前对 1893 个当前 Git 跟踪/未跟踪普通文件记录 SHA-256。模型文件的新字节内容严格等于实施前快照仅替换上述唯一 pose 字符串；报告只追加本节，已有内容逐字节保留。其余 1891 个快照文件哈希不变，包含独立机械臂 SDF、所有 Mesh/惯量/关节/控制定义、三个原模型目录及其余审计文档。

`git diff --no-index` 对模型实施前快照与当前文件的比较只有一行 Z 值变化。当前 am 和报告沿用此前未跟踪状态，普通 `git diff` 不展示它们；本轮使用内容快照差异和全量哈希补充检查，未新增或删除 Git 路径，未暂存、提交或推送。

本轮内容变化仅为 `models/am/model.sdf` 的一个安装 Z 值及本报告的本节追加。到此停止，不开展其他工作。
