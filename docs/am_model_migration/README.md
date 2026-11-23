# am 模型迁移前只读审计

审计日期：2026-11-23（Asia/Shanghai）。本轮已完成源文件审计和文档编写，**没有实施迁移或修复**。`models/am/` 未创建；旧模型、插件、质量和惯量均未修改；没有 Git 提交或推送。

## 证据口径

- **[事实]**：当前磁盘文件、XML 有效元素或本次只读命令的直接结果。
- **[推导]**：根据上述数据及明确的坐标/动力学规则计算得出。
- **[待验证]**：候选实现、运行时兼容性或未完成的环境验证。
- **[用户确认]**：实物结构、安装基准、关节保留与测量数据，不能由旧模型替代决定。

下列源文件行号属于本次快照；XML 注释中的旧配置不计入有效实体。文档内部链接使用仓库相对路径及 `#L` 行号。跨仓库 ROS 证据另标绝对路径，不属于本轮修改范围。

## 基线和文档导航

[事实] 当前分支 `feat/tmech-benchmark-worlds`，HEAD 为 `d5146058be1b5b95a0484674f38084d4d6118ec6`。初始 `git status --short` 为空；没有适用于本仓库的 `AGENTS.md`。本轮未启动 Gazebo、SITL 或控制程序，未操作已有 ROS 进程。

| 文档 | 内容 |
|---|---|
| [01_model_inventory.md](01_model_inventory.md) | 全部原文件、SHA-256、资源 URI、插件和外部名称依赖 |
| [02_frames_and_joints.md](02_frames_and_joints.md) | 全部 Link/Joint/Pose、完整运动链、安装变换及 URDF 差异 |
| [03_dynamics_baseline.md](03_dynamics_baseline.md) | 每个有效 Link 的质量、惯性坐标系及惯量六分量 |
| [04_migration_design.md](04_migration_design.md) | 未来目录、两份 SDF 的组织、解析限制和分级验证流程 |
| [05_questions_for_owner.md](05_questions_for_owner.md) | 按优先级排列的实物和坐标系确认事项 |

## 主要结论

1. [事实] `models/quadtilt_am/model.sdf:2` 实际声明 `<model name='quadtilt_new'>`，不同于目录名及 `model.config:4`。飞机自身有 8 个 Link、7 个 Joint、1 个 IMU、9 个 Plugin；另包含机械臂和 `arm_weld`。
2. [事实] 飞机目录只有 SDF/config，没有自己的 Mesh 或 URDF。7 个飞机 STL 来自 `models/quadtilt_new/meshes/`；机械臂有 6 个 STL。所有有效模型 URI 的本地依赖均存在；13 个二进制 STL 的记录长度检查通过。完整复制两旧目录仍会遗漏飞机 Mesh，必须纳入 `quadtilt_new` 资源。
3. [事实] 机械臂 SDF 有 8 个 Link、5 个转动 Joint、2 个移动指爪 Joint、2 个末端 Frame。旧 `base_link` 有 0.34432 kg 质量和可视 Mesh，且承接飞机固定连接、作为 `joint_1` 的父连杆；不是空坐标系。
4. [推导] `link_1` 在零位时相对机械臂模型原点上移 0.03 m，且由 `joint_1` 绕局部负 Z 轴转动。直接删除根连杆、把 `link_1` 固定安装会改变自由度；是否保留这一级实际转动必须由用户确认。
5. [事实] 通道 0–3 为电机、4–5 为倾转、6–10 为 `joint_1`–`joint_5`，两指爪共用通道 11。插件按关节名查找，查找失败会提前退出；修改模型名也会影响 IMU 后缀匹配及 ROS 完整 Link 名。
6. [推导] 安装目标 `0 0 -0.044 π 0 0` 必须施加到选定的新安装参考系。若仍保留旧模型到 `link_1` 的 30 mm 偏移，单把 include 设为该目标，会把 `link_1` 放在约 -0.074 m；若目标就是旧 `link_1` 零位，补偿后的 include 应为 -0.014 m。后者只作为条件算例。
7. [事实] 机械臂 SDF 与 URDF 已不一致：URDF 没有双指爪，`link_5` 的质量/质心/惯量不同；不能直接把 URDF 当作当前仿真权威。
8. [待验证] 两份 SDF 的分文件维护可沿用旧 include 机制；`model://am/robotic_arm` 有本地目录解析的源码依据，但本轮未创建 `am`，所以没有验证该候选 URI。不能将其写成已加载通过。

## 本轮验证及限制

[事实] 本机 `pkg-config --modversion gazebo sdformat9` 对应 Gazebo **11.15.1**、libsdformat **9.10.1**。lxml 可解析两份 SDF、机械臂 URDF 和配置文件。

```text
gz sdf -k models/robotic_arm/model.sdf
Check complete

gz sdf -k models/quadtilt_am/model.sdf
Warning [parser.cc:833] XML Attribute[version] in element[sdf] not defined in SDF, ignoring.
Check complete
```

[事实] `gz sdf -p models/quadtilt_am/model.sdf` 返回 0，同样带上述警告；输出中机械臂被展开为 `robotic_arm::...` 前缀实体和 `robotic_arm::__model__` Frame，保留 `arm_weld`。展开内容仅在内存中检查，未保存模型副本。警告未被消除，也未将 `Check complete` 解读为运行时控制或碰撞验证通过。

沙箱内首次 `gz sdf --help` 被接口枚举限制阻断：`error in getifaddrs: Unknown error -1`。随后在获准的只读命令范围内查询帮助并执行以上校验。没有使用会原地改写的 `gz sdf -c`。

[事实] 修改前 1866 个 Git 跟踪路径的文件内容聚合 SHA-256：

```text
bcd0e2388dfa8fc2af6ec4eb64180b5cc1eaed64c49944ad3ac6871103fa3b99
```

算法：按路径排序，对每个普通文件追加 `路径UTF-8 + NUL + 文件SHA-256二进制摘要`，最后计算总 SHA-256。源文件逐项摘要见 01。完成后的相同算法复核及 Git 范围检查记录在本文件末尾。

**现阶段停止点：等待用户确认 05 中的关键结构与坐标定义；本轮不会进入模型修改阶段。**

## 完成后的范围复核

[事实] 六份文档的 131 个本地链接及引用行号已检查；Markdown 围栏成对。按相同算法重新计算 1866 个原有 Git 跟踪路径，内容聚合 SHA-256 与上述基线完全相同。`git diff --name-only` 和 `git diff --cached --name-only` 均为空；`git ls-files --others --exclude-standard` 仅列出本目录规定的六份 Markdown。`models/am/` 不存在。没有改动原模型、构建产物、其他文档或 Git 暂存区，也没有自动提交。

本轮验收止于文档、源身份、XML/旧 include 的只读检查；新 URI、模型加载、实际关节控制和实物配置均保留为下一阶段待验证事项。
