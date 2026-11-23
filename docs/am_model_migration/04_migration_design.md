# 04 未来迁移设计与验证流程（未实施）

本篇是 **[设计/待验证]**，不是变更记录。它不授权创建模型，也不表示用户已经确认新结构。旧 `quadtilt_am`、`robotic_arm`、`quadtilt_new` 及已有世界/启动程序全部保留。

## 1. 先冻结不能自动决定的内容

新模型名和顶层目录为 `am`；顶层 `model.sdf` 放飞机 Links、Joints、Sensor、Plugin 和总装配。机械臂继续有独立 SDF，通过 include 和固定连接组装。仅删除旧机械臂 base_link 的具体结构实现，必须在用户确认实际固定根、joint_1 是否存在、安装目标的参考系和零位条件后确定；不能为了得到一棵有效 XML 树而擅自减自由度。

迁移默认保持飞机 Link/Joint 名及其局部 pose、轴、限位、惯性、碰撞启用状态、LiftDrag 和控制数值，机械臂子模型实例名优先保持 `robotic_arm`，从而保留 `robotic_arm::joint_n` 控制前缀。顶层内部名改 `am` 时，IMU 查找参数和外部 Link 名仍需同步设计。

## 2. 建议的完整目录

```text
models/
├── quadtilt_am/                       # 全部保留
├── robotic_arm/                       # 全部保留
├── quadtilt_new/                      # 本轮发现的实际飞机 Mesh 来源，全部保留
└── am/                               # 未来创建；本轮不存在
    ├── model.config                  # 复制旧飞机 config 后更新新副本元数据
    ├── model.sdf                     # 飞机 + include + arm_weld + 飞机插件
    ├── meshes/
    │   ├── base_link.STL              # 来自 quadtilt_new/meshes，7 件全部复制
    │   ├── tilt_0_Link.STL
    │   ├── tilt_1_Link.STL
    │   ├── properller_0_Link.STL
    │   ├── properller_1_Link.STL
    │   ├── properller_2_Link.STL
    │   └── properller_3_Link.STL
    └── robotic_arm/
        ├── model.config              # 新副本与机械臂 SDF 实际版本保持一致
        ├── model.sdf                 # 独立机械臂 SDF，拓扑待用户确认
        ├── model.urdf                # 完整复制；未同步期间明确标为来源版本
        ├── package.xml               # 实际原目录资源，不能遗漏
        ├── CMakeLists.txt            # 实际原目录资源，安装问题需单独处理
        └── meshes/
            ├── base_link.STL         # 即使新 SDF 不引用，也保留完整来源副本
            ├── link_1.STL
            ├── link_2.STL
            ├── link_3.STL
            ├── link_4.STL
            └── link_5.STL
```

该基本方案需要原两个目录的 13 个文件，加上额外来源的 7 个飞机 Mesh，共 **20 个文件**再进行新副本修改；没有发现其他模型专属纹理或素材需要补充。所有来源/摘要见 01。飞机和机械臂同名 STL 分别在各自 meshes 下，不会相互覆盖。

`quadtilt_am` 没有飞机 URDF，不能虚构其存在。`quadtilt_new/model.urdf` 可以按需另外复制到 `am/reference/quadtilt_new/model.urdf` 并记录来源；它不是总装配等价描述，也不是必需运行资源。若要求飞机和机械臂都提供可运行 ROS URDF，必须另行确认范围，增加同步后的飞机/总装配 URDF 及明确的 ROS 资源包方案；不能原样使用这个旁系 URDF 冒充已完成。

### 必须改写的新副本路径

| 原引用 | 新引用候选 | 说明 |
|---|---|---|
| `model://quadtilt_new/meshes/X.STL` | `model://am/meshes/X.STL` | 所有飞机有效引用及注释中的旧引用一并审查 |
| `model://robotic_arm/meshes/X.STL` | `model://am/robotic_arm/meshes/X.STL` | Mesh 解析目标是文件，不需要机械臂目录作为顶级模型被发现 |
| include `model://robotic_arm` | 首选候选 `model://am/robotic_arm` | 是否被 include resolver 接受必须按本机版本验证 |
| `imuName=quadtilt_new::imu_link::imu_sensor` | 候选 `am::imu_link::imu_sensor` | 还需结合世界实例覆盖/包装和实际 sensor scoped name 核对 |
| URDF `package://robotic_arm/meshes/X.STL` | 独立 ROS 资源包 URI 或经验证的自包含解析方案 | 只替换 SDF 不会消除 URDF 的旧包依赖 |

Gazebo 系统材质 `file://media/materials/scripts/gazebo.material` 以及插件动态库继续作为显式环境依赖；本仓库没有这些内置资源的模型私有副本。保持系统 Gazebo 依赖与消除旧模型目录依赖是两个不同目标。若需跨机器离线整包交付，再明确运行环境和插件安装清单。

URDF 的 `package://` 不能未经验证直接换成 `model://`：Gazebo、RViz、robot_state_publisher 使用的资源解析机制并不相同。若仍运行 URDF，优先使用一个新的唯一 ROS 描述包来提供 `am` 下资源，避免把复制来的 `package.xml` 以旧包名注册进工作空间。保留来源文件不意味着应将嵌套同名包加入 catkin；原 `install(DIRECTORY urdf ...)` 的无目录问题也需在新包阶段处理。此项为后续选择，不在本轮修复。

## 3. Gazebo Classic 11 / SDFormat 兼容性分析

### 已在本机验证的范围

[事实] Gazebo 11.15.1 / libsdformat 9.10.1；本机安装 schema `/usr/share/sdformat9/1.7/model.sdf:37–60` 允许 model 内 include 和 nested model，`:46–48` 允许 include/name 覆盖实例名。两个旧 config 标注 1.6、实际 SDF 为 1.7；新副本应与其实际采用的 schema 一致，旧配置不改。

[事实] 本轮只读展开旧飞机时：

```xml
<model name='quadtilt_new'>
  <!-- 飞机实体、插件省略 -->
  <frame name='robotic_arm::__model__' attached_to='robotic_arm::base_link'>
    <pose relative_to='__model__'>0 0 -0.04 -3.14159 -0 0</pose>
  </frame>
  <link name='robotic_arm::base_link'>
    <!-- inertial/visual 省略 -->
    <pose relative_to='robotic_arm::__model__'>0 0 0 0 -0 0</pose>
  </link>
  <joint name='robotic_arm::joint_1' type='revolute'>
    <pose relative_to='robotic_arm::base_link'>0 0 0.03 0 -0 0</pose>
    <parent>robotic_arm::base_link</parent>
    <child>robotic_arm::link_1</child>
    <!-- axis 等省略 -->
  </joint>
  <!-- 后续连杆、关节、Frame 省略 -->
  <joint name='arm_weld' type='fixed'>
    <parent>base_link</parent>
    <child>robotic_arm::base_link</child>
  </joint>
</model>
```

这说明本机旧 include 能被解析并带作用域前缀展开，输出并没有保留一个独立 `<model name='robotic_arm'>` 树。不能把磁盘上嵌套目录、源文件 model 嵌套、解析后实体层次和 ROS 实际名字视为同一件事。两份主要 SDF 的维护方式不受展开输出扁平化影响，但必须核对运行时插件的 GetJoint 和传感器匹配。

### 新子目录 URI 的源码依据与验证限制

[源码事实] Gazebo Classic 11 的 `SystemPaths::FindFileURI` 将 `model://` 后面的完整后缀拼接到已注册模型搜索目录，再检查存在性（上游 [SystemPaths.cc:289–320](https://github.com/gazebosim/gazebo-classic/blob/gazebo11/gazebo/common/SystemPaths.cc#L289)）；从这一层看，后缀包含 `am/robotic_arm` 并非必然非法。

[源码事实] libsdformat 9 分支 include 解析先将 URI 解析为目录，再读取该目录的 `model.config` 来选择 SDF（上游 [parser.cc:690–737,809–846](https://github.com/gazebosim/sdformat/blob/sdf9/src/parser.cc#L690)）。这是目录 URI 和直接指向 `model.sdf` 文件 URI 不能混用的依据。

这些上游分支用于说明机制，不冒充本机 9.10.1 构建的逐行源码身份。[推导/待验证] 当 `${GAZEBO_MODEL_PATH}` 包含 `.../models` 且 `am/robotic_arm/model.config` 存在并正确指向其 SDF 时，`model://am/robotic_arm` 具备可行性依据。但本轮没有新建任何 `am`，故未验证此 URI 的真实解析、GUI 插入列表、插件查找或物理加载；不能宣称“保证支持”。目录在 GUI 中是否被单独列出与 include 是否可读也不等价。

本机 SDF 1.7 include schema 没有较新版本的 `placement_frame` 或 include merge 等选项，本方案不依赖这些新语法。安装应使用 02 的显式模型到根变换。不能仅因新版本在线文档支持某属性就向 Classic 11 模型加入它。

### 候选 URI 不兼容时的替代方案

| 方案 | 实现 | 两份主要 SDF | 代价和验证点 |
|---|---|---|---|
| A，首选验证 | `model://am/robotic_arm`，子目录保留 model.config | 保持 | 只注册外层 models；必须验证实际 resolver |
| B，兼容回退 | 为**隔离的新启动入口**额外加入 `.../models/am` 搜索根，把内部目录改为唯一的 `am_robotic_arm`，include 用 `model://am_robotic_arm` | 保持 | 所有文件仍在 am 内；不覆盖旧目录；增加启动环境要求。include/name 可仍指定 robotic_arm，控制前缀可保持。目录结构与首选不同，需批准后选择 |
| C，诊断或固定部署 | include 指向机械臂**目录**的绝对 `file://` URI，并保留该目录 config | 保持 | 可用于定位 model URI 层故障；不便迁移机器，且 file URI 接受性也须实测，不能作为可移植默认 |
| D，生成装配产物 | 源码仍维护飞机/机械臂两个主要 SDF，离线展开生成一个可加载 SDF | 源码保持，运行产物单文件 | 能绕开部分 include 问题，但需要生成/校验流程，增加第三个产物；偏离用户要求的运行时 include 组成整体，仅作再次确认后的末级回退 |

不推荐把 `models/am` 加入搜索路径后继续使用 `model://robotic_arm`：它可能命中旧顶层同名目录，造成假自包含。也不推荐未经验证使用 `model://am/robotic_arm/model.sdf` 作为 include URI；该版本 include 通路要求目录/config。相对路径 `robotic_arm`、`file://robotic_arm` 对启动工作目录和解析上下文有潜在依赖，也不能未经验证替代 A。

## 4. 需要保留及最小修改的接口

| 类别 | 默认保持 | 必要的新副本改动 |
|---|---|---|
| 飞机结构 | 8 Link、IMU固定 Joint、两倾转和四桨；原数值 | 顶层 model/config 名称改 am，资源 URI 改到 am |
| 气动和电机 | 8 LiftDrag、桨 Joint 名、速度控制、符号和增益 | 路径改写不涉及气动数值；验证所有 link_name 有效 |
| 倾转 | channel 4/5、两个 Joint、轴与限位 | 保留独立通道；验证同输入下运动方向与同步行为 |
| ArduPilot | 一份插件、原通道、端口、坐标转换和增益 | IMU 名与新真实 scope 对齐；必要时保持/核对 arm 关节 scope |
| 机械臂 | 所有仍适用关节及控制语义 | 仅按用户确认的根/首轴结构调整拓扑与安装变换 |
| 安装 | fixed 连接到实际静止根 | include 依据 `T_AN=T_AR inverse(T_NR)`，不得只改 Z 而忽略内部偏移 |
| 惯性 | 未改造刚体的现有物理参数和局部坐标 | 不调 mass/COM/inertia；结构拆除带来的质量删除单独记账，待第二阶段测量 |
| ROS | 旧入口仍使用旧模型 | 单独新入口配置新世界、模型、Link 名、机械臂零位及 TCP；不全局替换历史材料 |

“最小修改”不是忽略当前风险：首轴是否存在决定了能否固定安装到选定根，未确认前不能实施最终根删除。若要先做无结构变化的复制基线，也须下一阶段明确授权，且不能把它算作完成新机械结构。

## 5. 未来分级验证流程及验收条件

以下步骤均**未在本轮执行**，仅保留旧模型的 XML 校验/展开证据。每级失败保留失败输出，不靠删关节、删 control 或调整惯量来使其表面通过。

1. **源身份和复制完整性**：冻结旧文件哈希，按 01 清单复制，逐个核对 13 个 STL、配置和 URDF；确认旧目录哈希不变。仅允许新 `am` 及明确批准的新测试入口变更。
2. **自包含静态审查**：解析所有有效 URI；扫描新模型全部文本（含注释、URDF 和 ROS 包描述）的旧路径。所有实际模型资源应指向 am 内，URDF 若仅存档须标识而不宣称可运行。扫描 abs path、package://、file://、插件和材质，分别列出允许的系统依赖。
3. **真实路径消歧**：在独立搜索环境测试只可见新 am 和必需的系统资源；原文件不重命名、不移动、不删除。因为 Gazebo 默认缓存可能补足旧资源，需核对实际展开及加载日志使用的文件，不能只看退出码；如缓存无法隔离，应在之后获准的临时部署树/容器测试。
4. **SDF 检查/展开**：运行 `gz sdf -k`、`gz sdf -p`，禁止 `-c`。核对 config/schema、include 目标、所有 parent/child/relative_to/attached_to、完整关节和 IMU 名；候选 A URI 只有此时实测成功才升级为已验证。原警告保留对照，新增警告须解释。
5. **坐标与运动链计算**：指定新静止根和 q=0 定义。使用矩阵核对目标 translation `(0,0,-0.044)`、rotation `Rx(π)`；建议验收容差先与用户约定，例如数值层 1e-6 m / 1e-6 rad，实物安装误差另计。采样非零关节配置，验证下游变换、轴和控制符号；目标若属运动根零位，不将其误当全构型恒定关系。
6. **独立无飞控的暂停加载**：使用新验证世界、独立 Gazebo master 和日志目录；不启动 SITL、不发控制，检查 Mesh、固定连接和实体枚举。插件可能等待飞控，不将“进程未退出”作为控制成功。新旧模型不在共享 9002/9003 的同一场景直接竞争。
7. **只读接口核对**：用真实 Gazebo entity/sensor 列表及 ROS model/link states 检查 scoped 名字；对照 `_model->GetJoint` 和 IMU 后缀逻辑。确保加载到的 libArduPilotPlugin.so 身份与当前源码对应，记录库路径/摘要；检测所有 13 个 control 条目和共享通道。
8. **单独获准的隔离 SITL 回归**：沿用一套 SITL/控制桥，新入口配置独立端口。依次验证 IMU、四桨符号、两倾转、所有保留的机械臂关节和共通道指爪；实际关节位置/速度响应是证据，不能只以发出命令为通过。任何旋翼/舵机异常先停止并保留日志。该步骤不等于实机飞行验收，也不默认自动 ARM/起飞。
9. **第二阶段动力学更新**：按测量表更新 mass/COM/惯量及必要碰撞几何，独立审查物理一致性，再重复相关回归。当前无机械臂碰撞等限制始终写进结果；保留原数值迁移不能宣称新实物动力学有效。

## 6. 本轮不实施的事项

没有创建新世界、脚本、模型副本或 `models/am`；没有改插件、ROS、配置、质量、碰撞或关节；没有构建新库、运行 SITL 或启动仿真。下一阶段先取得 05 中 P0 项答案和新的实施指令，再选择相应最小方案。本轮完成文档后停止。
