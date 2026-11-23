# 01 原模型、资源和控制接口清单

除明确标记外，本篇各表均为 **[事实]**。以有效 XML 为准，注释中的资源另列。

## 1. 全文件清单及身份

`quadtilt_am` 共 2 个文件；`robotic_arm` 共 11 个文件；额外实际依赖 `quadtilt_new` 共 10 个文件（其中 7 个飞机 Mesh 必需）。未发现这三个目录中的符号链接。STL 无独立纹理/材质文件引用；两个目标目录无其他图片、纹理或 DAE 资源。

| 路径 | 字节 | SHA-256 | 说明 |
|---|---|---|---|
| `models/quadtilt_am/model.config` | 735 | `55f942aa8793127b467ac08a337c65983f87ad5f34dc36bda780617051353568` |  |
| `models/quadtilt_am/model.sdf` | 25724 | `f50fc25a10ae9eaa9f90431d15a0541222c4e78c99d7cf9b55467e1bb4f206ce` |  |
| `models/robotic_arm/CMakeLists.txt` | 306 | `cc3b30d35b7a0cdb84e546efa1882158888c7ea6779acb6d7211cababa8689d5` |  |
| `models/robotic_arm/meshes/base_link.STL` | 631284 | `ab000432c34feae3925b97fc2d4e2d7c0813cd4326dda37f81213160665cf564` | 二进制 STL；12624 三角形；84+50N 长度匹配 |
| `models/robotic_arm/meshes/link_1.STL` | 395384 | `45b5a2db28d758f2faf21e2afc4216b0f05c542466dcd4b85ca8f43419a7232e` | 二进制 STL；7906 三角形；84+50N 长度匹配 |
| `models/robotic_arm/meshes/link_2.STL` | 293084 | `43c62293ac498671cbcb31c9f06824cf9eeb3a5ed4064b339d47f65f5550a74b` | 二进制 STL；5860 三角形；84+50N 长度匹配 |
| `models/robotic_arm/meshes/link_3.STL` | 626884 | `81c637bfc47c7c178321f9d73b2cf7755720c3197eb32f702d83120526556ba9` | 二进制 STL；12536 三角形；84+50N 长度匹配 |
| `models/robotic_arm/meshes/link_4.STL` | 275084 | `0df1b151ce1734d137f055f90595925a674eb68d0b026f0ab076a6d3535582db` | 二进制 STL；5500 三角形；84+50N 长度匹配 |
| `models/robotic_arm/meshes/link_5.STL` | 53184 | `549e0104843f4cb247edabfe89545afc9cbd9f51cd2fca4b6d185d48254601a9` | 二进制 STL；1062 三角形；84+50N 长度匹配 |
| `models/robotic_arm/model.config` | 734 | `6c44da904a0266246f862229107417c4cf660c392c54228bac6e7c304b8f4dd7` |  |
| `models/robotic_arm/model.sdf` | 14321 | `89834b56690b6de8db89b62b11fdcf3c8e8d4c97b397c6e42203cfbd17bab030` |  |
| `models/robotic_arm/model.urdf` | 11880 | `450306f71307d9d5f4729a780ff028843e19c6fde3bf82d77d045417a0e815cc` |  |
| `models/robotic_arm/package.xml` | 527 | `d866c21fe3d58cc2437d41d52b3cec054e5a02afed1e5c73061347b78316e174` |  |
| `models/quadtilt_new/meshes/base_link.STL` | 6554484 | `9543645f10040e8d718e7c511b4a0e0d5fb968abe44ef8fbd7e25bb4d27c6528` | 二进制 STL；131088 三角形；84+50N 长度匹配 |
| `models/quadtilt_new/meshes/properller_0_Link.STL` | 17284 | `9f7f7bd9c87d5f79b639be1b542fc64f3921ce65bea4940bd473ca9069d10307` | 二进制 STL；344 三角形；84+50N 长度匹配 |
| `models/quadtilt_new/meshes/properller_1_Link.STL` | 17284 | `379397162b3baa41b50a202ebed0378c4eaf158e91bcc7406c08ff00316efbe8` | 二进制 STL；344 三角形；84+50N 长度匹配 |
| `models/quadtilt_new/meshes/properller_2_Link.STL` | 17284 | `633e550f88bb9e692dca8279b938e42d3ce688ea7e8278ecd223e4d96a90f372` | 二进制 STL；344 三角形；84+50N 长度匹配 |
| `models/quadtilt_new/meshes/properller_3_Link.STL` | 17284 | `203f2caa226f979a3d2db8e26655a7ab8d5aa601c61e53868fa70d344fe0bc91` | 二进制 STL；344 三角形；84+50N 长度匹配 |
| `models/quadtilt_new/meshes/tilt_0_Link.STL` | 464684 | `06ee5f2af3a48acca266738acd3ade9519e80dd019fa690aa66688de0d4058f1` | 二进制 STL；9292 三角形；84+50N 长度匹配 |
| `models/quadtilt_new/meshes/tilt_1_Link.STL` | 464684 | `7026c9b29b6f527dea75141ec571104c8e8e998a845c5d5f473b333b647959dd` | 二进制 STL；9292 三角形；84+50N 长度匹配 |
| `models/quadtilt_new/model.config` | 735 | `292427ba846b0bcfcc264a524a2a96d2c49f366f5c4b940cfbc1a19344bf3d67` | 额外依赖来源；SDF/URDF/config 作为来源存档，不替换总装配权威 |
| `models/quadtilt_new/model.sdf` | 22191 | `98ce6e8194a91463614a9b31ac8559c29028aa8561353b5e47ff111c0777556f` | 额外依赖来源；SDF/URDF/config 作为来源存档，不替换总装配权威 |
| `models/quadtilt_new/model.urdf` | 8659 | `8c1caa6f9aa331ee075fd897f7099ff1f28dbce802fbfb88e0c79c3e6a2884ca` | 额外依赖来源；SDF/URDF/config 作为来源存档，不替换总装配权威 |

二进制记录长度检查只说明文件结构长度一致，不证明网格封闭、无自交或物理尺寸正确。现有 SDF 的 Mesh scale 均为 `1 1 1`；STL 本身没有单位声明。

## 2. 配置、SDF、URDF 和 ROS 包资源

- 飞机 `model.config:4,6`：`<name>quadtilt_am</name>`、`<sdf version="1.6">model.sdf</sdf>`；实际 SDF `:1–2` 声明 1.7 和 `quadtilt_new`。
- 机械臂 `model.config:4,6`：名称 `robotic_arm`、版本 1.6；实际 SDF `:1` 为 1.7。两份 config 的描述仍为 Iris 历史文本，不能作为结构依据。新副本需统一元数据，不改旧文件。
- `quadtilt_am` 没有 URDF。`quadtilt_new/model.urdf` 是额外可存档的飞机 URDF：7 个 Link、6 个 Joint，不含 IMU、机械臂和 ArduPilot 插件；不是现有总装配的等价 URDF。其 Mesh 为 `package://quadtilt_new/meshes/...`（例如 :29）。
- `robotic_arm/model.urdf` 是实际已有资源，需完整复制但明确未与 SDF 同步；差异见 02、03。
- `robotic_arm/package.xml:3,9–14` 声明名为 `robotic_arm` 的 catkin 包及 ROS 依赖；`CMakeLists.txt:9–10` 安装 `meshes` 和不存在的 `urdf/` 目录，实际 URDF 位于根目录。该安装规则风险仅记录，不修复；复制后也不能假定嵌套 catkin 包能被正确发现。

## 3. 有效 URI 及实际依赖

源文件：[`models/quadtilt_am/model.sdf:1`](../../models/quadtilt_am/model.sdf#L1)；元素为 `<geometry><mesh><uri>`、`<material><script><uri>` 或 `<include><uri>`。

| URI | 行号（全部有效引用） | 解析目标 |
|---|---|---|
| `model://quadtilt_new/meshes/base_link.STL` | 123 | `models/quadtilt_new/meshes/base_link.STL`；存在 |
| `file://media/materials/scripts/gazebo.material` | 129 | Gazebo 安装资源 `/usr/share/gazebo-11/media/materials/scripts/gazebo.material`；存在 |
| `model://quadtilt_new/meshes/tilt_0_Link.STL` | 199, 208 | `models/quadtilt_new/meshes/tilt_0_Link.STL`；存在 |
| `model://quadtilt_new/meshes/properller_0_Link.STL` | 260 | `models/quadtilt_new/meshes/properller_0_Link.STL`；存在 |
| `model://quadtilt_new/meshes/properller_2_Link.STL` | 312 | `models/quadtilt_new/meshes/properller_2_Link.STL`；存在 |
| `model://quadtilt_new/meshes/tilt_1_Link.STL` | 355, 364 | `models/quadtilt_new/meshes/tilt_1_Link.STL`；存在 |
| `model://quadtilt_new/meshes/properller_1_Link.STL` | 416 | `models/quadtilt_new/meshes/properller_1_Link.STL`；存在 |
| `model://quadtilt_new/meshes/properller_3_Link.STL` | 468 | `models/quadtilt_new/meshes/properller_3_Link.STL`；存在 |
| `model://robotic_arm` | 620 | `models/robotic_arm`；存在 |

源文件：[`models/robotic_arm/model.sdf:1`](../../models/robotic_arm/model.sdf#L1)；元素为 `<geometry><mesh><uri>`、`<material><script><uri>` 或 `<include><uri>`。

| URI | 行号（全部有效引用） | 解析目标 |
|---|---|---|
| `model://robotic_arm/meshes/base_link.STL` | 21 | `models/robotic_arm/meshes/base_link.STL`；存在 |
| `file://media/materials/scripts/gazebo.material` | 27, 87, 147, 207, 267, 359, 372, 418, 461 | Gazebo 安装资源 `/usr/share/gazebo-11/media/materials/scripts/gazebo.material`；存在 |
| `model://robotic_arm/meshes/link_1.STL` | 81 | `models/robotic_arm/meshes/link_1.STL`；存在 |
| `model://robotic_arm/meshes/link_2.STL` | 141 | `models/robotic_arm/meshes/link_2.STL`；存在 |
| `model://robotic_arm/meshes/link_3.STL` | 201 | `models/robotic_arm/meshes/link_3.STL`；存在 |
| `model://robotic_arm/meshes/link_4.STL` | 261 | `models/robotic_arm/meshes/link_4.STL`；存在 |
| `model://robotic_arm/meshes/link_5.STL` | 353 | `models/robotic_arm/meshes/link_5.STL`；存在 |

[推导] 所有模型专属有效 URI 均能落到本仓库的普通文件/模型目录；本次环境中每个 URI 在 `GAZEBO_MODEL_PATH` 非空条目中只有一个匹配目标。没有发现还需复制其他旧模型 Mesh 的有效依赖。飞机 Mesh 的碰撞/视觉重复引用不增加复制文件数。

[事实] 注释中另有飞机 base Mesh collision（SDF :16–41）及四个桨 collision（:246–254 等）；机械臂旧 `link_5`（:302–331）。它们不是有效实体，但原样复制注释时也应一并重写其中旧 URI，避免将来启用时重新依赖旧目录。机械臂 6 个 STL 即使新结构删除旧基座，也应先完整保留副本，再由确认后的方案决定是否引用。

[事实] 当前搜索路径为：

```text
/home/liqidun/github/ardupilot_gazebo/models_gazebo
/home/liqidun/github/ardupilot_gazebo/models
/usr/share/gazebo-11/models
```

`model://` 的解析身份是搜索路径下的目录，不是 SDF 内部 `<model name>`。`models_gazebo` 中未发现同名 `quadtilt_new`、`robotic_arm` 或 `am` 目录；用户目录缓存的完整遮蔽情况未做运行时验证。

## 4. 全部 Sensor 和 Plugin

| Sensor | 类型 | Link | 局部 pose | Hz | 证据 |
|---|---|---|---|---|---|
| imu_sensor | imu | imu_link | 0 0 0 3.141593 0 0 | 1000.0 | [`models/quadtilt_am/model.sdf:146`](../../models/quadtilt_am/model.sdf#L146) |

IMU `<always_on>` 为 1（飞机 SDF :148）。IMU 模型局部路径：`quadtilt_new::imu_link::imu_sensor`；SDF `:503` 的 `<imuName>` 与之相同。典型 `quadtilt_am_indoor.world` 使用外层 `<model name="quadtilt_am">` 后，其预期世界完整作用域为 `<world>::quadtilt_am::quadtilt_new::imu_link::imu_sensor`。这是由 include 层次推导的路径，不是本轮运行时传感器枚举结果；若世界直接 include 并覆盖 `<name>`，作用域将不同。

| Plugin name | 动态库 | 名称依赖 | 证据 |
|---|---|---|---|
| rotor_0_blade_1 | libLiftDragPlugin.so | properller_0_Link | [`models/quadtilt_am/model.sdf:482`](../../models/quadtilt_am/model.sdf#L482) |
| rotor_0_blade_2 | libLiftDragPlugin.so | properller_0_Link | [`models/quadtilt_am/model.sdf:483`](../../models/quadtilt_am/model.sdf#L483) |
| rotor_1_blade_1 | libLiftDragPlugin.so | properller_1_Link | [`models/quadtilt_am/model.sdf:486`](../../models/quadtilt_am/model.sdf#L486) |
| rotor_1_blade_2 | libLiftDragPlugin.so | properller_1_Link | [`models/quadtilt_am/model.sdf:487`](../../models/quadtilt_am/model.sdf#L487) |
| rotor_2_blade_1 | libLiftDragPlugin.so | properller_2_Link | [`models/quadtilt_am/model.sdf:490`](../../models/quadtilt_am/model.sdf#L490) |
| rotor_2_blade_2 | libLiftDragPlugin.so | properller_2_Link | [`models/quadtilt_am/model.sdf:491`](../../models/quadtilt_am/model.sdf#L491) |
| rotor_3_blade_1 | libLiftDragPlugin.so | properller_3_Link | [`models/quadtilt_am/model.sdf:494`](../../models/quadtilt_am/model.sdf#L494) |
| rotor_3_blade_2 | libLiftDragPlugin.so | properller_3_Link | [`models/quadtilt_am/model.sdf:495`](../../models/quadtilt_am/model.sdf#L495) |
| ardupilot_plugin | libArduPilotPlugin.so | IMU + 13 个 control（含共享 channel） | [`models/quadtilt_am/model.sdf:498`](../../models/quadtilt_am/model.sdf#L498) |

8 个 LiftDrag 插件每桨两叶：`area=0.0045`、`air_density=1.2041`，`cp=±0.13 0 0`；0/1 号与 2/3 号的 forward 方向不同。必须保留全部插件及 `link_name`，不能仅复制电机关节。

机械臂 SDF 没有独立 Sensor/Plugin；URDF 内的 transmission 和 `libgazebo_ros_control.so` 块是注释（:361–417），不能当作正在生效的控制器。当前适用控制由飞机 ArduPilot 插件承担。

[事实] 本机存在 `build/libArduPilotPlugin.so` 和系统 `.../gazebo-11/plugins/libLiftDragPlugin.so`。`CMakeLists.txt:50–51,63` 构建并安装前者。库存在不证明运行时加载的是这个构建产物；`GAZEBO_PLUGIN_PATH`、系统安装副本及 ABI 需后续验证。Gazebo 内置材质和运行库是显式环境依赖，不是旧模型目录依赖。模型复制不等于复制完整 Gazebo/ROS 安装。

## 5. ArduPilot 全部有效控制映射

通道编号是 XML 和输入数组的 **0 基索引**，不可直接与实机 `SERVOx_FUNCTION` 等同。表中 `properller` 是源文件的实际拼写，迁移时保持。

| channel | jointName | type | multiplier | offset | P/I/D | cmd min/max | 证据 |
|---|---|---|---|---|---|---|---|
| 0 | properller_0_joint | VELOCITY | 800 | 0 | 0.20/0/0 | [-2.5, 2.5] | [`models/quadtilt_am/model.sdf:507`](../../models/quadtilt_am/model.sdf#L507) |
| 1 | properller_1_joint | VELOCITY | 800 | 0 | 0.20/0/0 | [-2.5, 2.5] | [`models/quadtilt_am/model.sdf:508`](../../models/quadtilt_am/model.sdf#L508) |
| 2 | properller_2_joint | VELOCITY | -800 | 0 | 0.20/0/0 | [-2.5, 2.5] | [`models/quadtilt_am/model.sdf:509`](../../models/quadtilt_am/model.sdf#L509) |
| 3 | properller_3_joint | VELOCITY | -800 | 0 | 0.20/0/0 | [-2.5, 2.5] | [`models/quadtilt_am/model.sdf:510`](../../models/quadtilt_am/model.sdf#L510) |
| 4 | tilt_0_joint | POSITION | 1.495 | -0.85 | 40.0/0/0.5 | [-2.0, 2.0] | [`models/quadtilt_am/model.sdf:514`](../../models/quadtilt_am/model.sdf#L514) |
| 5 | tilt_1_joint | POSITION | 1.495 | -0.85 | 40.0/0/0.5 | [-2.0, 2.0] | [`models/quadtilt_am/model.sdf:515`](../../models/quadtilt_am/model.sdf#L515) |
| 6 | robotic_arm::joint_1 | POSITION | 4.7124 | -0.5 | 20.0/0/0 | [-2.0, 2.0] | [`models/quadtilt_am/model.sdf:518`](../../models/quadtilt_am/model.sdf#L518) |
| 7 | robotic_arm::joint_2 | POSITION | 4.7124 | -0.5 | 20.0/0/0.05 | [-2.0, 2.0] | [`models/quadtilt_am/model.sdf:531`](../../models/quadtilt_am/model.sdf#L531) |
| 8 | robotic_arm::joint_3 | POSITION | 4.7124 | -0.5 | 20.0/0/0.05 | [-2.0, 2.0] | [`models/quadtilt_am/model.sdf:544`](../../models/quadtilt_am/model.sdf#L544) |
| 9 | robotic_arm::joint_4 | POSITION | 4.7124 | -0.5 | 20.0/0/0.05 | [-2.0, 2.0] | [`models/quadtilt_am/model.sdf:557`](../../models/quadtilt_am/model.sdf#L557) |
| 10 | robotic_arm::joint_5 | POSITION | 4.7124 | -0.5 | 10.0/0/0 | [-2.0, 2.0] | [`models/quadtilt_am/model.sdf:570`](../../models/quadtilt_am/model.sdf#L570) |
| 11 | robotic_arm::left_finger_joint | POSITION | 0.025 | 0 | 0.5/0/0.01 | [-1.0, 1.0] | [`models/quadtilt_am/model.sdf:585`](../../models/quadtilt_am/model.sdf#L585) |
| 11 | robotic_arm::right_finger_joint | POSITION | 0.025 | 0 | 0.5/0/0.01 | [-1.0, 1.0] | [`models/quadtilt_am/model.sdf:603`](../../models/quadtilt_am/model.sdf#L603) |

所有 control 的 `i_max/i_min=0/0`；没有显式 `useForce`，源码默认 true（`src/ArduPilotPlugin.cc:191,530–532`）。POSITION 使用 PID 计算力/力矩后 `SetForce`（:998–1012），不是把关节直接锁定到目标；桨为速度 PID（:986–995）。SDF 表内 `cmd_min/max` 是 PID 输出限值，不能把它们误当关节位置限位。

源码 `src/ArduPilotPlugin.cc:1147–1158` 对每个 control 分别取 `pkt.motorSpeed[channel]`，输入钳制到 [-1,1]，再计算 `multiplier*(cmd+offset)`。两个 channel=11 条目均被保留（:692 push_back），分别驱动相反轴的指爪，是共享输入，不是后者覆盖前者。不能因为编号重复而自动删掉一个。

倾转两 Joint 独立受控且映射参数相同，SDF 没有机械同步或 mimic 约束；所谓双侧同步还依赖飞控给两路一致命令。注释中的 channel 6/7 → tilt_2/tilt_3 无效，实际 channel 6/7 是机械臂。

其他插件参数：SDF :499–504 为 `fdm_addr=127.0.0.1`、端口 9002/9003、`modelXYZToAirplaneXForwardZDown=0 0 0 3.141593 0 0`、IMU 名称、超时计数 5。改名不直接要求改端口或坐标转换；新旧实例同时加载需独立处理端口冲突。

**失效路径**：`src/ArduPilotPlugin.cc:535–554` 通过 `_model->GetJoint(jointName)` 查找，缺失就 return；:83–106 通过 Sensor 完整名字的后缀匹配，:697–757 查 IMU 失败同样 return。删 `joint_1` 而保留 channel 6 不只是损失一轴，也可能使整个插件初始化中止。

## 6. 世界、启动脚本和 ROS 名称依赖

以下世界引用来自 XML 有效 `<include><uri>`，不计注释：

| 世界及行号 | URI | include/name | 父容器名称 |
|---|---|---|---|
| [`worlds/old_quadtilt_am_indoor.world:765`](../../worlds/old_quadtilt_am_indoor.world#L765) | model://quadtilt_am | 无覆盖 | quadtilt_am |
| [`worlds/quadtilt_am_indoor.world:102`](../../worlds/quadtilt_am_indoor.world#L102) | model://quadtilt_am | 无覆盖 | quadtilt_am |
| [`worlds/quadtilt_am_selicon.world:102`](../../worlds/quadtilt_am_selicon.world#L102) | model://quadtilt_am | 无覆盖 | quadtilt_am |
| [`worlds/quadtilt_new_indoor.world:765`](../../worlds/quadtilt_new_indoor.world#L765) | model://quadtilt_new | 无覆盖 | quadtilt_new |
| [`worlds/robotic_arm_test.world:127`](../../worlds/robotic_arm_test.world#L127) | model://robotic_arm | 无覆盖 | robotic_arm |
| [`worlds/tmech_benchmark/p60_ros/shelf.world:2`](../../worlds/tmech_benchmark/p60_ros/shelf.world#L2) | model://quadtilt_am | p60_quadtilt | tmech_shelf |
| [`worlds/tmech_benchmark/p60_ros/shelf_v2.world:2`](../../worlds/tmech_benchmark/p60_ros/shelf_v2.world#L2) | model://quadtilt_am | 无覆盖 | p60_quadtilt |
| [`worlds/tmech_benchmark/p60_ros/solar.world:2`](../../worlds/tmech_benchmark/p60_ros/solar.world#L2) | model://quadtilt_am | p60_quadtilt | tmech_solar |
| [`worlds/tmech_benchmark/p60_ros/solar_v2.world:2`](../../worlds/tmech_benchmark/p60_ros/solar_v2.world#L2) | model://quadtilt_am | 无覆盖 | p60_quadtilt |

典型世界 `worlds/quadtilt_am_indoor.world:99–104` 的外层 `quadtilt_am` 包含内部 `quadtilt_new`；不能把目录名、内部名、世界实例名混为一谈。本仓库 `tools/`、`src/`、`include/` 的脚本/程序未搜到直接写死这三个模型名称；这是限定路径搜索结果，不是所有外部程序都兼容的证明。

只读补充检查了相邻 ROS 仓库的当前文件，以下依赖已确认（均以 `/home/liqidun/github/ros_quadtilt/src/aerial_manipulator/` 为前缀）：

| 文件与行号 | 有效依赖/影响 |
|---|---|
| `trajectory_planner/test/start_quadtilt_am_ros.sh:47` | 启动 `quadtilt_am_selicon.world` |
| `trajectory_planner/test/start_quadtilt_am_comp_ros.sh:47` | 启动 `quadtilt_am_indoor.world` |
| `trajectory_planner/scripts/planner_main_node.py:41` | `WorldObserver(drone_name='quadtilt_am')` |
| `arm_control/scripts/arm_mavlink_node.py:40` | 同样实例化旧名字的 WorldObserver |
| `trajectory_planner/scripts/modules/world_observer.py:17,39–47,58–61,82–84` | 拼接 `quadtilt_am::quadtilt_new::robotic_arm::link_5`，订阅 model/link states；末端另加局部 `[0,0,0.082]` 偏移 |
| `trajectory_planner/scripts/modules/simulation_execution_ros.py:28–29,214` | 固定旧世界路径、旧 SDF 路径，以及 `name == 'quadtilt_am'` 过滤 |

[推导] 新内部名 `am` 即使保留外层实例名，也会使旧完整 Link 名匹配失败；若连外层实例名也改，ModelStates 过滤也会失败。新机械结构还会使旧 82 mm 末端偏移失效。后续应使用单独新入口/可配置名称进行验证，旧入口保留。本轮未修改 ROS 文件，也未审计或确认全部 ROS 运动学、实机 PWM 配置和飞控参数。
