# 第 09 章 · EDA 与原理图入门

> **所属阶段**：阶段二 · 从原理图到第一块板
> **前置课程**：第 01～08 章
> **本课难度**：⭐⭐

## 本章目标

学完本章，你应该能够：

1. 说清 EDA、原理图、符号、网络、网表、封装之间的关系。
2. 独立新建一个 EDA 工程，设置图框、网格和设计规则。
3. 从器件库调用电阻、电容、二极管，画出无 ERC 错误的 RC 电路。
4. 给每个元件挂上正确封装，导出网表，理解“符号管脚号”和“焊盘编号”的对应。
5. 用 ERC 定位悬空网络、输出冲突、电源短路三类错误。
6. 用版本号和目录规范管理原理图，避免“最终版-真的最终版”。
7. 说出至少 8 个新手在原理图阶段常犯的坑。

EDA 不是“画图软件”，而是把电路意图翻译成工厂能执行的数据。原理图画对了，后面的封装、网表、PCB、Gerber 才有意义；原理图画错了，后面每一步都在放大错误。

## 正文

### 9.1 它解决什么问题：三个真实场景

#### 场景一：手画电路图，改一次就全乱

在纸上画一个 RC 低通，改一个电阻值只要擦掉重写；但加上电源、地、连接器、测试点之后，每改一次都要重新画线，版本无法比较，别人也看不懂。EDA 把“元件”和“连线”变成结构化对象：改一个参数，所有引用同步更新；改一版，可以 diff、可以回退。

#### 场景二：原理图和 PCB 各画一遍，管脚对不上

有人在原理图上把三极管 B/C/E 画成 1/2/3，封装却按 2/1/3 焊盘建。图看起来没错，板子做出来三极管接反。EDA 的网表把“符号管脚号”和“封装焊盘号”绑定，导入 PCB 时就会报 Unknown Pin / Extra Pin，逼你在投板前解决。

#### 场景三：工厂问你要网表，你只有一张截图

打样厂和贴片厂要的是 Gerber、钻孔、坐标、BOM，不是聊天窗口里的截图。EDA 工程能一键导出这些生产数据；没有工程文件，就无法保证“你看到的图”和“工厂做出的板”是同一版。

### 9.2 它是什么：从电路意图到生产数据

**EDA**（Electronic Design Automation，电子设计自动化）是设计电子系统的软件工具集合。对 PCB 方向，最常用的是原理图编辑器和 PCB 编辑器。

一条完整的数据链是：

`原理图（Symbol + Wire + Net）→ 网表（Netlist）→ PCB（Footprint + Net）→ Gerber / 钻孔 / 坐标 / BOM`

几个必须分清的概念：

- **符号（Symbol）**：原理图上的图形，代表器件的电气功能。符号有管脚号和管脚名，但不决定焊盘大小。
- **封装（Footprint）**：PCB 上的焊盘图形，决定器件怎么焊。封装有焊盘编号和尺寸，但不管电气功能。
- **网络（Net）**：同一根导线连接的所有管脚属于同一个网络。网络名是 PCB 布线的依据。
- **网表（Netlist）**：原理图导出的“元件—管脚—网络”清单，是原理图和 PCB 之间的合同。
- **ERC**（Electrical Rules Check，电气规则检查）：检查悬空管脚、输出冲突、电源短路等电气问题，不检查封装对不对。

> **术语第一次出现**：ERC 不是“画图检查”，它只按你设置的电气管脚类型判断。ERC 通过不等于板子一定对，封装、极性、网络名还要人工核对。

### 9.3 关键参数与工程设置

EDA 没有“器件手册”，但有一组工程参数必须设置对。下表是新建工程时的检查清单。

| 设置项 | 推荐做法 | 不设置的后果 |
|---|---|---|
| 图框与纸张 | A4/A3，标题栏写项目名、版本、日期 | 打印/归档时缺版本信息 |
| 网格 | 原理图 1.27mm（50mil）或 2.54mm | 线头对不齐，ERC 报悬空 |
| 管脚间距 | 与符号库一致，常用 2.54mm | 连线看起来接上，实际没连 |
| 设计规则 | 线宽、间距、过孔按板厂能力 | 后面 PCB 无法 DRC |
| 元件库 | 只用已核对过的库，禁止随手搜 | 符号/封装不匹配 |
| 版本命名 | `项目_功能_版本_日期` | 文件无法追溯 |
| 备份 | Git 或每日压缩包 | 硬盘坏了全丢 |

读“工程设置”的 three 个条件：

1. **板厂能力先于个人喜好**：最小线宽/间距、最小孔径、层数，先看目标板厂工艺表。
2. **符号库先于连线速度**：库里的符号管脚号必须和器件手册一致，不能“看起来像”就用。
3. **版本先于“最终版”**：每次投板前打 tag，Gerber 与工程文件同版本归档。

### 9.4 典型电路：从库到原理图

#### 9.4.1 电路一：RC 低通（最小闭环）

目标：输入 0～5V 方波，输出给 ADC，截止频率约 159Hz。选 `R=10kΩ`、`C=100nF`。

计算：

`fc = 1 / (2πRC) = 1 / (2π × 10k × 100n) ≈ 159Hz`

操作顺序：

1. 新建工程，命名 `rc_lpf_v1_20261110`。
2. 从库中放 `R`、`C`、`GND`、`+5V`、输入/输出端口。
3. 连线，给输入网络命名 `SIG_IN`，输出命名 `ADC_IN`。
4. 给 R 挂 0805 封装，给 C 挂 0603 封装。
5. 运行 ERC，确认无悬空管脚、无输出冲突。
6. 导出网表，检查 `R1-1`、`C1-1` 是否在同一网络。

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 300">
  <rect x="20" y="20" width="680" height="260" fill="none" stroke="currentColor" stroke-width="1.5"/>
  <text x="40" y="50" font-size="16" fill="currentColor">图 9-1：EDA 数据链：原理图到生产文件</text>
  <rect x="50" y="90" width="120" height="60" rx="8" fill="none" stroke="currentColor" stroke-width="1.5"/>
  <text x="72" y="125" font-size="14" fill="currentColor">原理图</text>
  <text x="62" y="145" font-size="12" fill="currentColor">Symbol + Net</text>
  <rect x="210" y="90" width="120" height="60" rx="8" fill="none" stroke="currentColor" stroke-width="1.5"/>
  <text x="236" y="125" font-size="14" fill="currentColor">网表</text>
  <text x="222" y="145" font-size="12" fill="currentColor">Netlist</text>
  <rect x="370" y="90" width="120" height="60" rx="8" fill="none" stroke="currentColor" stroke-width="1.5"/>
  <text x="396" y="125" font-size="14" fill="currentColor">PCB</text>
  <text x="382" y="145" font-size="12" fill="currentColor">Footprint + Net</text>
  <rect x="530" y="90" width="140" height="60" rx="8" fill="none" stroke="currentColor" stroke-width="1.5"/>
  <text x="550" y="125" font-size="14" fill="currentColor">生产文件</text>
  <text x="548" y="145" font-size="12" fill="currentColor">Gerber/BOM/坐标</text>
  <line x1="170" y1="120" x2="210" y2="120" stroke="currentColor" stroke-width="2"/>
  <polygon points="210,120 200,115 200,125" fill="currentColor"/>
  <line x1="330" y1="120" x2="370" y2="120" stroke="currentColor" stroke-width="2"/>
  <polygon points="370,120 360,115 360,125" fill="currentColor"/>
  <line x1="490" y1="120" x2="530" y2="120" stroke="currentColor" stroke-width="2"/>
  <polygon points="530,120 520,115 520,125" fill="currentColor"/>
  <text x="55" y="200" font-size="13" fill="currentColor">每一环都必须能追溯到上一环；任何一环靠“口头说明”，工厂都接不住。</text>
</svg>
```

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 320">
  <text x="20" y="30" font-size="16" fill="currentColor">图 9-2：符号、封装、网络三者的对应关系</text>
  <rect x="30" y="60" width="200" height="110" rx="8" fill="none" stroke="currentColor" stroke-width="1.5"/>
  <text x="50" y="85" font-size="14" fill="currentColor">符号（原理图）</text>
  <text x="50" y="110" font-size="13" fill="currentColor">R1  管脚 1 / 2</text>
  <text x="50" y="132" font-size="13" fill="currentColor">管脚名：1、2</text>
  <text x="50" y="154" font-size="13" fill="currentColor">只表达电气功能</text>
  <rect x="260" y="60" width="200" height="110" rx="8" fill="none" stroke="currentColor" stroke-width="1.5"/>
  <text x="280" y="85" font-size="14" fill="currentColor">封装（PCB）</text>
  <text x="280" y="110" font-size="13" fill="currentColor">0805  焊盘 1 / 2</text>
  <text x="280" y="132" font-size="13" fill="currentColor">焊盘尺寸/间距</text>
  <text x="280" y="154" font-size="13" fill="currentColor">只表达怎么焊</text>
  <rect x="490" y="60" width="190" height="110" rx="8" fill="none" stroke="currentColor" stroke-width="1.5"/>
  <text x="510" y="85" font-size="14" fill="currentColor">网络（Net）</text>
  <text x="510" y="110" font-size="13" fill="currentColor">SIG_IN / ADC_IN</text>
  <text x="510" y="132" font-size="13" fill="currentColor">同一网络 = 同一根线</text>
  <text x="510" y="154" font-size="13" fill="currentColor">PCB 布线的依据</text>
  <line x1="230" y1="115" x2="260" y2="115" stroke="currentColor" stroke-width="2"/>
  <polygon points="260,115 250,110 250,120" fill="currentColor"/>
  <line x1="460" y1="115" x2="490" y2="115" stroke="currentColor" stroke-width="2"/>
  <polygon points="490,115 480,110 480,120" fill="currentColor"/>
  <text x="30" y="230" font-size="13" fill="currentColor">网表把三者绑在一起：元件位号 + 符号管脚号 + 封装焊盘号 + 网络名。</text>
  <text x="30" y="255" font-size="13" fill="currentColor">任何一项对不上，PCB 导入就会报 Unknown Pin / Extra Pin。</text>
</svg>
```

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 260">
  <text x="20" y="30" font-size="16" fill="currentColor">图 9-3：RC 低通原理图</text>
  <text x="40" y="120" font-size="14" fill="currentColor">SIG_IN</text>
  <line x1="95" y1="115" x2="150" y2="115" stroke="currentColor" stroke-width="2"/>
  <rect x="150" y="100" width="60" height="30" fill="none" stroke="currentColor" stroke-width="2"/>
  <text x="160" y="95" font-size="13" fill="currentColor">R1 10k</text>
  <line x1="210" y1="115" x2="270" y2="115" stroke="currentColor" stroke-width="2"/>
  <text x="245" y="105" font-size="13" fill="currentColor">ADC_IN</text>
  <line x1="270" y1="115" x2="270" y2="180" stroke="currentColor" stroke-width="2"/>
  <line x1="250" y1="180" x2="290" y2="180" stroke="currentColor" stroke-width="2"/>
  <line x1="260" y1="190" x2="280" y2="190" stroke="currentColor" stroke-width="2"/>
  <line x1="270" y1="180" x2="270" y2="200" stroke="currentColor" stroke-width="2"/>
  <text x="300" y="185" font-size="13" fill="currentColor">C1 100n</text>
  <line x1="270" y1="200" x2="270" y2="225" stroke="currentColor" stroke-width="2"/>
  <line x1="255" y1="225" x2="285" y2="225" stroke="currentColor" stroke-width="2"/>
  <line x1="260" y1="232" x2="280" y2="232" stroke="currentColor" stroke-width="2"/>
  <line x1="265" y1="239" x2="275" y2="239" stroke="currentColor" stroke-width="2"/>
  <text x="295" y="232" font-size="13" fill="currentColor">GND</text>
  <text x="40" y="220" font-size="13" fill="currentColor">fc = 1/(2πRC) ≈ 159Hz</text>
</svg>
```

#### 9.4.2 电路二：分压网络（练网络命名）

12V 电池经 `R1=10kΩ`、`R2=3.3kΩ` 分压，送 ADC。空载输出：

`Vout = 12 × 3.3 / (10 + 3.3) ≈ 2.98V`

在原理图里给分压点命名 `VBAT_SENSE`，不要用默认 `Net1`。默认网络名一多，PCB 里根本找不到。

#### 9.4.3 电路三：按键输入（练端口与上拉）

按键一端接 `GPIO_IN`，另一端接 GND；`GPIO_IN` 通过 `R1=10kΩ` 上拉到 3.3V。按下读 0，松开读 1。原理图要画出去耦电容 `C1=100nF`，否则长按抖动会在 ERC 之外的场景里咬你。

### 9.5 选型与降额：软件与工程规范

| 软件 | 适合谁 | 优点 | 注意 |
|---|---|---|---|
| 立创 EDA | 零基础、快速打样 | 中文、库全、与嘉立创打通 | 库封装要自己复核 |
| KiCad | 免费、开源、长期项目 | 跨平台、脚本强、社区大 | 学习曲线比立创陡 |
| Altium Designer | 企业、多层板、高速 | 规则强、生态成熟 | 授权贵、上手慢 |
| Allegro / PADS | 大厂、高速/通信 | 约束管理强 | 学习成本高，按岗位需要学 |

选型三条：

1. 先能独立走完“原理图→PCB→Gerber”，再谈软件高级功能。
2. 团队协作用什么，你就学什么；个人练习优先免费/低成本。
3. 不要同时学三套软件；一套用到能投板，再迁移。

工程“降额”指给后续修改留余地：

- 图框留 20% 空白，方便加测试点。
- 网络名统一前缀（`PWR_`、`ADC_`、`GPIO_`），不要 `Net1`。
- 每个功能块单独一页，别把所有东西塞一张图。
- 投板前打 tag，保留 Gerber 与工程文件同版本。

### 9.6 测量与仿真：ERC、网表、前仿真

#### 9.6.1 ERC 检查

1. 运行 ERC。
2. 看三类错误：悬空管脚、输出冲突、电源/地短路。
3. 悬空管脚：要么接网络，要么标记“不连接”（No Connect）。
4. 输出冲突：两个输出直接并联，必须加电阻/二极管隔离。
5. 电源短路：`+5V` 与 `GND` 同名或误连，必须改网络名。

#### 9.6.2 网表核对

导出网表后，搜 `R1`，确认：
- `R1-1` 接 `SIG_IN`；
- `R1-2` 接 `ADC_IN`；
- `C1-1` 与 `R1-2` 同网络；
- `C1-2` 接 `GND`。

#### 9.6.3 CircuitJS 前仿真

```circuitjs
rc-lowpass-159
```

观察：输入方波，输出被“磨圆”；频率越高，输出幅度越小。前仿真只验证拓扑，不验证 PCB 布局。

#### 9.6.4 动手任务

- 画一个 `12V→3.3V` 分压电路，命名为 `VBAT_SENSE`。
- 给 R/C 挂 0805/0603 封装，导出网表。
- 故意把 `+5V` 与 `GND` 短接，运行 ERC，截图记录报错。
- 修复后导出 PDF 原理图，按 `项目_功能_v1_日期` 命名归档。

### 9.7 常见坑

1. **符号管脚号和封装焊盘号不一致**：三极管、MOS、USB-C 最容易错。
2. **用默认网络名**：`Net1`、`Net2` 一多，PCB 里无法定位。
3. **隐藏电源管脚**：芯片电源脚被隐藏，ERC 不报，板子没电。
4. **输出直接并联**：两个 LDO 输出接一起，轻则倒灌，重则烧。
5. **No Connect 乱用**：把该接的管脚标 NC，ERC 通过，功能没有。
6. **图框版本不写**：三版图混在一个文件夹，投错版。
7. **库封装不核对**：库里的 QFN 焊盘和实际器件差 0.2mm，焊接偏移。
8. **原理图当草稿**：边画边改网络名，最后网表和 PCB 对不上。

### 9.8 本章复盘

#### 9.8.1 公式与规则表

| 公式/规则 | 用途 | 条件与注意 |
|---|---|---|
| `fc = 1/(2πRC)` | RC 低通截止频率 | R 单位 Ω，C 单位 F |
| `Vout = Vin × R2/(R1+R2)` | 分压 | 输出端几乎不取电流 |
| 符号管脚号 = 封装焊盘号 | 网表绑定 | 必须逐个核对 |
| ERC 通过 ≠ 板子正确 | 电气规则检查 | 封装/极性/网络仍要人工核对 |
| 网络名统一前缀 | 可读性 | 禁止 `Net1` 满天飞 |

#### 9.8.2 术语表

| 术语 | 英文 | 一句话解释 |
|---|---|---|
| EDA | Electronic Design Automation | 电子设计自动化工具 |
| 符号 | symbol | 原理图上的器件图形 |
| 封装 | footprint | PCB 上的焊盘图形 |
| 网络 | net | 同一根导线连接的所有管脚 |
| 网表 | netlist | 元件—管脚—网络清单 |
| ERC | electrical rules check | 电气规则检查 |
| 网表导入 | netlist import | 把原理图连接同步到 PCB |

#### 9.8.3 自测 10 题

1. 符号和封装分别决定什么？
2. 网表里 `R1-1` 代表什么？
3. ERC 报“悬空管脚”怎么处理？
4. 为什么不能把两个输出直接并联？
5. 默认网络名有什么问题？
6. 原理图版本怎么命名？
7. 立创 EDA 和 KiCad 各自适合什么场景？
8. 隐藏电源管脚为什么危险？
9. No Connect 什么情况下可以用？
10. 投板前要归档哪些文件？

#### 9.8.4 能力清单

- [ ] 能新建工程并设置图框、网格、规则。
- [ ] 能画 RC 低通、分压、按键三个原理图。
- [ ] 能给元件挂封装并导出网表。
- [ ] 能用 ERC 定位三类错误。
- [ ] 能按版本规范归档工程。

#### 9.8.5 下一章

下一章讲**焊接与返修基础**：原理图画完、板子打样回来，第一件事是把它焊出来。你会看到工具、温度、焊锡、助焊剂，以及虚焊、连锡、冷焊怎么识别。
