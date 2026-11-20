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

#### 9.1.1 场景一：手画电路图，改一次就全乱

在纸上画一个 RC 低通，改一个电阻值只要擦掉重写；但加上电源、地、连接器、测试点之后，每改一次都要重新画线，版本无法比较，别人也看不懂。EDA 把“元件”和“连线”变成结构化对象：改一个参数，所有引用同步更新；改一版，可以 diff、可以回退。

#### 9.1.2 场景二：原理图和 PCB 各画一遍，管脚对不上

有人在原理图上把三极管 B/C/E 画成 1/2/3，封装却按 2/1/3 焊盘建。图看起来没错，板子做出来三极管接反。EDA 的网表把“符号管脚号”和“封装焊盘号”绑定，导入 PCB 时就会报 Unknown Pin / Extra Pin，逼你在投板前解决。

#### 9.1.3 场景三：工厂问你要网表，你只有一张截图

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

#### 9.2.1 四类对象：谁决定什么

| 对象 | 在哪里 | 决定什么 | 错了会怎样 |
|---|---|---|---|
| 符号 Symbol | 原理图库 | 电气功能、管脚名/号 | 连线对不上、ERC 误报 |
| 封装 Footprint | PCB 库 | 焊盘尺寸、间距、极性 | 焊不上、贴反、偏移 |
| 网络 Net | 原理图连线 | 哪些管脚必须连在一起 | 板子开路/短路 |
| 网表 Netlist | 导出文件 | 把前两者绑成合同 | 导入 PCB 报 Unknown Pin |
| ERC | 原理图规则 | 电气连接是否自洽 | 通过但板子仍可能错 |

> **术语第一次出现**：Unknown Pin（未知管脚）指网表里的管脚号在封装里找不到对应焊盘；Extra Pin（多余管脚）指封装有焊盘但网表没给连接。两者都是“符号—封装”不匹配的直接证据。

> **术语第一次出现**：No Connect（不连接）是原理图里对“本来就不接”的管脚做的显式标记。它告诉 ERC“这个脚悬空是有意的”，不是“我忘了连”。

#### 9.2.2 数据链的五个检查点

| 检查点 | 看什么 | 通过标准 |
|---|---|---|
| 符号 | 管脚号与手册一致 | 1/2/3 与封装焊盘一一对应 |
| 连线 | 每根线两端都有电气连接 | 无悬空、无重叠假连 |
| 网络名 | 关键网络有语义名 | `VBAT_SENSE` 而不是 `Net12` |
| 封装 | 焊盘尺寸/间距/极性 | 与器件手册推荐焊盘一致 |
| 导出 | 网表、BOM、PDF 同版本 | 文件名与日期能对上 |


#### 9.2.3 先把“合同”想清楚再画

原理图不是画给自己看的，是画给三个人看的：**画板的人**要知道哪些脚必须连；**贴片的人**要知道每个位号焊什么；**测试的人**要知道去哪里量电压。画之前先问三句话：

1. 这个信号从哪来、到哪去、中间经过谁？
2. 这个器件的第 1 脚在哪，封装丝印能不能对上？
3. 板子回来先量哪个点，测试点有没有留？

三句话答不清，图越画越乱；答清了，ERC 只是最后一道形式检查。

这也是为什么原理图阶段要“慢”：这里改一根线只花一分钟，到了 PCB 可能要重布一片地；到了工厂，就是一批板报废。前期多花十分钟核对，后面少花十天返工。

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

#### 9.3.1 新建工程 12 步

1. **定项目名**：`项目_功能_版本_日期`，如 `relay4_v1_20261110`。
2. **选图框**：A4 横版够用；功能块多就 A3，不要在一张图上挤。
3. **设单位**：原理图用 mm/mil 均可，但全工程统一，不要一会儿 50mil 一会儿 1.27mm。
4. **设网格**：1.27mm（50mil）或 2.54mm（100mil），保证管脚落在格点上。
5. **建图层**：至少“主图/电源/接口/测试点”四页，别把所有东西画一张。
6. **选库**：优先用经过核对的公司库/官方库，禁止“搜到就用”。
7. **放符号**：先放核心器件，再放阻容，最后放连接器/测试点。
8. **连线**：先连电源/地，再连信号；每连完一块立即命名网络。
9. **挂封装**：逐个确认封装名、焊盘号、极性，不批量“默认”。
10. **跑 ERC**：先清零错误，再处理警告；每个警告写原因。
11. **导网表**：导出后搜 3 个关键网络，确认管脚归属。
12. **归档**：PDF、网表、BOM、工程文件同目录，打 tag/日期。

这 12 步里，最容易被跳过的是第 9 步和第 12 步。第 9 步决定“能不能焊”，第 12 步决定“下次还能不能找回来”。把这两步写进自己的检查表，每次新建工程照着走，比事后返工便宜得多。原理图阶段的每一分钟，都会在 PCB、焊接、调试阶段被放大成十分钟。把图当合同，而不是当草图，是这一章最想让你带走的习惯。合同写清楚，后面每个人才知道自己该做什么；合同写错，后面每个人都在替同一个错误买单。

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

#### 9.4.2 电路二：分压网络（练网络命名与功耗）

12V 电池经 `R1=10kΩ`、`R2=3.3kΩ` 分压，送 ADC。空载输出：

`Vout = 12 × 3.3 / (10 + 3.3) ≈ 2.98V`

先别急着画，做三个核算：

| 核算 | 公式 | 结果 | 判断 |
|---|---|---|---|
| 分压比 | `R2/(R1+R2)` | `3.3/13.3≈0.248` | 12V→2.98V，落在 3.3V ADC 量程内 |
| 分压电流 | $I=\frac{V_{\text{in}}}{R_1+R_2}$ | `12/13.3k≈0.90mA` | 可接受；电池长期在线要算漏电 |
| R1 功耗 | $P=I^{2}R$ | `(0.9m)²×10k≈8.1mW` | 0805 足够 |

如果换成 `R1=100kΩ、R2=33kΩ`，电流降到 90µA，但 ADC 输入漏电/采样电容会影响精度；这时要在分压点加 100nF 电容，并核算 ADC 源阻抗。**分压不是“算对电压就行”，还要算电流、功耗、源阻抗。**

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 280">
  <text x="20" y="30" font-size="16" fill="currentColor">图 9-4：12V 电池分压进 ADC</text>
  <text x="40" y="110" font-size="14" fill="currentColor">VBAT 12V</text>
  <line x1="120" y1="105" x2="180" y2="105" stroke="currentColor" stroke-width="2"/>
  <rect x="180" y="85" width="60" height="40" fill="none" stroke="currentColor" stroke-width="2"/>
  <text x="188" y="78" font-size="13" fill="currentColor">R1 10k</text>
  <line x1="240" y1="105" x2="320" y2="105" stroke="currentColor" stroke-width="2"/>
  <text x="270" y="95" font-size="13" fill="currentColor">VBAT_SENSE</text>
  <line x1="320" y1="105" x2="380" y2="105" stroke="currentColor" stroke-width="2"/>
  <text x="385" y="110" font-size="14" fill="currentColor">ADC</text>
  <line x1="320" y1="105" x2="320" y2="160" stroke="currentColor" stroke-width="2"/>
  <rect x="290" y="160" width="60" height="40" fill="none" stroke="currentColor" stroke-width="2"/>
  <text x="298" y="153" font-size="13" fill="currentColor">R2 3.3k</text>
  <line x1="320" y1="200" x2="320" y2="235" stroke="currentColor" stroke-width="2"/>
  <line x1="300" y1="235" x2="340" y2="235" stroke="currentColor" stroke-width="2"/>
  <line x1="306" y1="242" x2="334" y2="242" stroke="currentColor" stroke-width="2"/>
  <line x1="312" y1="249" x2="328" y2="249" stroke="currentColor" stroke-width="2"/>
  <text x="350" y="245" font-size="13" fill="currentColor">GND</text>
  <text x="400" y="170" font-size="12" fill="currentColor">Vout≈2.98V</text>
  <text x="400" y="190" font-size="12" fill="currentColor">I≈0.9mA</text>
</svg>
```

给分压点命名 `VBAT_SENSE`，不要用默认 `Net1`。命名规则建议：

- 电源：`PWR_12V`、`PWR_5V`、`PWR_3V3`
- 模拟：`ADC_xxx`、`VBAT_SENSE`
- 数字：`GPIO_xxx`、`UART_TX`
- 差分：`USB_DP/DM`、`ETH_TXP/TXN`

默认网络名一多，PCB 里根本找不到；改一处分压比，也不知道影响哪些页。

#### 9.4.3 电路三：按键输入（练端口、上拉与去抖）

按键一端接 `GPIO_IN`，另一端接 GND；`GPIO_IN` 通过 `R1=10kΩ` 上拉到 3.3V。按下读 0，松开读 1。先算三个值：

| 项目 | 公式 | 结果 | 说明 |
|---|---|---|---|
| 按下电流 | `I=3.3V/10kΩ` | 0.33mA | 触点电流偏小，潮湿环境可降到 1k～4.7k |
| 上拉功耗 | `P=3.3V²/10kΩ` | ≈1.1mW | 0805 足够 |
| RC 去抖时间 | $\tau=RC$ | 10k×100n≈1ms | 机械抖动通常 0.1～10ms，按按键选 |

去抖电容 `C1=100nF` 与上拉构成低通，`τ≈1ms`；如果按键抖动重，增大到 1µF（`τ≈10ms`），但响应会变慢。**去抖不是越大约好，要在“不误触”和“响应快”之间选。**

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 300">
  <text x="20" y="30" font-size="16" fill="currentColor">图 9-5：按键上拉、去抖与端口命名</text>
  <text x="40" y="80" font-size="13" fill="currentColor">3.3V</text>
  <line x1="90" y1="75" x2="90" y2="120" stroke="currentColor" stroke-width="2"/>
  <rect x="70" y="120" width="40" height="60" fill="none" stroke="currentColor" stroke-width="2"/>
  <text x="118" y="150" font-size="13" fill="currentColor">R1 10k</text>
  <line x1="90" y1="180" x2="90" y2="210" stroke="currentColor" stroke-width="2"/>
  <line x1="90" y1="210" x2="170" y2="210" stroke="currentColor" stroke-width="2"/>
  <text x="120" y="200" font-size="13" fill="currentColor">GPIO_IN</text>
  <line x1="170" y1="210" x2="240" y2="210" stroke="currentColor" stroke-width="2"/>
  <line x1="240" y1="195" x2="240" y2="225" stroke="currentColor" stroke-width="2"/>
  <line x1="225" y1="195" x2="255" y2="195" stroke="currentColor" stroke-width="2"/>
  <line x1="225" y1="225" x2="255" y2="225" stroke="currentColor" stroke-width="2"/>
  <text x="262" y="215" font-size="13" fill="currentColor">按键</text>
  <line x1="240" y1="225" x2="240" y2="255" stroke="currentColor" stroke-width="2"/>
  <line x1="220" y1="255" x2="260" y2="255" stroke="currentColor" stroke-width="2"/>
  <line x1="226" y1="262" x2="254" y2="262" stroke="currentColor" stroke-width="2"/>
  <line x1="232" y1="269" x2="248" y2="269" stroke="currentColor" stroke-width="2"/>
  <text x="270" y="265" font-size="13" fill="currentColor">GND</text>
  <line x1="90" y1="210" x2="90" y2="245" stroke="currentColor" stroke-width="2"/>
  <line x1="60" y1="245" x2="100" y2="245" stroke="currentColor" stroke-width="2"/>
  <line x1="66" y1="252" x2="94" y2="252" stroke="currentColor" stroke-width="2"/>
  <line x1="72" y1="259" x2="88" y2="259" stroke="currentColor" stroke-width="2"/>
  <text x="20" y="280" font-size="12" fill="currentColor">C1 100nF 与 R1 构成 τ≈1ms 低通；按键按下读 0，松开读 1。</text>
</svg>
```

原理图阶段还要注意：按键是“人接触”的接口，量产板建议加 ESD 器件（如双向 TVS 或 RC+TVS），并在结构上做间隙；这些在原理图上就要留位，不要等 PCB 才想起。

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

#### 9.5.1 库里没有的器件怎么办

新手最常见的卡点不是“不会画”，而是“库里没有”。处理顺序：

1. **先查官方库**：芯片官网/开发板资料常提供符号与封装，优先用原厂。
2. **再查社区库**：立创/KiCad 官方库有大量器件，但要核对管脚号与焊盘。
3. **最后自己建**：按手册画符号（管脚名/号/类型）和封装（焊盘尺寸/间距/丝印）。
4. **建完必须复核**：打印 1:1 封装图，拿实物或游标卡尺对比；符号用“管脚号—功能”表逐脚核对。
5. **入库命名**：`厂商_型号_封装`，写数据手册链接和日期，避免下次又找不到。

自己建库的三条红线：

- 不能凭“看起来差不多”画焊盘；QFN/BGA 差 0.2mm 就会偏移。
- 不能把多个器件的管脚号“约定俗成”地混用；三极管 B/C/E 与 1/2/3 必须按手册。
- 不能把符号的电源脚全部隐藏；至少要能在原理图上查到供电连接。

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

#### 9.6.3 前仿真：RC 低通与分压

```circuitjs
rc-lowpass-159
```

观察：输入方波，输出被“磨圆”；频率越高，输出幅度越小。前仿真只验证拓扑，不验证 PCB 布局。

```circuitjs
voltdivide
```

把 12V/10k/3.3k 填进去，观察分压点电压和电流。再改 R2，看输出怎么变；这一步比在纸上算更能建立“分压比—负载—功耗”的直觉。

#### 9.6.4 ERC 三类错误对照

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 300">
  <text x="20" y="30" font-size="16" fill="currentColor">图 9-6：ERC 三类常见错误</text>
  <rect x="30" y="60" width="200" height="80" rx="6" fill="none" stroke="currentColor" stroke-width="1.5"/>
  <text x="45" y="85" font-size="13" fill="currentColor">① 悬空管脚</text>
  <text x="45" y="108" font-size="11" fill="currentColor">管脚没有网络</text>
  <text x="45" y="126" font-size="11" fill="currentColor">处理：接网络或标 NC</text>
  <rect x="260" y="60" width="200" height="80" rx="6" fill="none" stroke="currentColor" stroke-width="1.5"/>
  <text x="275" y="85" font-size="13" fill="currentColor">② 输出冲突</text>
  <text x="275" y="108" font-size="11" fill="currentColor">两个输出直接并联</text>
  <text x="275" y="126" font-size="11" fill="currentColor">处理：串电阻/二极管</text>
  <rect x="490" y="60" width="200" height="80" rx="6" fill="none" stroke="currentColor" stroke-width="1.5"/>
  <text x="505" y="85" font-size="13" fill="currentColor">③ 电源/地短路</text>
  <text x="505" y="108" font-size="11" fill="currentColor">+5V 与 GND 同名/误连</text>
  <text x="505" y="126" font-size="11" fill="currentColor">处理：改网络名/查电源脚</text>
  <text x="30" y="200" font-size="13" fill="currentColor">ERC 只查“电气自洽”，不查封装、极性、器件选型。</text>
  <text x="30" y="225" font-size="13" fill="currentColor">ERC 通过后，仍要人工核对：封装、极性、电源管脚、NC 是否合理。</text>
</svg>
```

| 错误 | 典型原因 | 处理 |
|---|---|---|
| 悬空管脚 | 忘了连线/管脚隐藏 | 接网络、上拉/下拉、或标 NC |
| 输出冲突 | 两个 LDO/两个 IO 输出并联 | 加隔离电阻/二极管/换开漏 |
| 电源短路 | 网络名相同、电源脚误连 | 改网络名、逐个查电源脚 |
| 单端网络 | 连接器只连了一端 | 补线或删除多余管脚 |

#### 9.6.5 动手任务：一张图走完整个数据链

任务目标：在一块 A4 原理图里放“12V 分压 + 按键 + RC 低通”三个小电路，导出网表并留下检查记录。

步骤：

1. 新建工程 `eda_lab_v1_20261110`，图框写项目名、日期、姓名缩写。
2. 放三个功能块：`VBAT_SENSE`、`KEY_IN`、`ADC_FILTER`，块之间留 10mm 以上空白。
3. 给每个电阻/电容挂封装：R 用 0805，C 用 0603；连接器用 2.54mm 排针。
4. 给关键网络命名：`PWR_12V`、`VBAT_SENSE`、`GPIO_KEY`、`ADC_IN`。
5. 运行 ERC，记录每一条错误/警告，逐条写“原因 + 处理”。
6. 导出网表，搜 `R1`、`C1`、`J1`，确认管脚号与网络名。
7. 故意制造一个错误：把 `PWR_12V` 与 `GND` 短接，再跑 ERC，截图。
8. 修复后导出 PDF，和网表、工程文件放同一目录，命名带版本与日期。

验收标准：

- [ ] ERC 零错误；每条警告都有原因说明。
- [ ] 网表里三个关键网络都能搜到，管脚归属正确。
- [ ] 三个功能块的网络名不重复、不冲突。
- [ ] PDF 图框有项目名/版本/日期。
- [ ] 目录里能一眼看出“工程、网表、PDF”是同一版。

### 9.7 常见坑

| 坑 | 现象 | 根因 | 正确做法 |
|---|---|---|---|
| 符号/封装管脚号不一致 | 导入 PCB 报 Unknown Pin | 符号按 1/2/3，封装按 2/1/3 | 建库时逐脚对照手册 |
| 默认网络名 | PCB 里找不到 `Net37` | 没有命名习惯 | 关键网络统一前缀命名 |
| 隐藏电源管脚 | ERC 不报，板子没电 | 符号把 VDD/GND 隐藏 | 显式画出电源脚或确认库定义 |
| 输出直接并联 | 轻则倒灌，重则烧 | 以为“并联加大电流” | 加隔离/均流/换方案 |
| No Connect 乱用 | ERC 通过但功能没有 | 把该接的脚标 NC | NC 只用于“确实不接”的脚 |
| 图框不写版本 | 三版图混一起，投错版 | 文件名随手起 | `项目_功能_v1_日期` |
| 库封装不核对 | QFN 偏移 0.2mm | 直接调用库，不看手册 | 按手册推荐焊盘复核 |
| 原理图当草稿 | 网表和 PCB 对不上 | 边画边改网络名 | 每完成一块立即定名/复查 |
| 只跑 ERC 不看封装 | 板子焊不上 | 把 ERC 当万能检查 | ERC+封装+极性+网表四查 |
| 多张图网络重名 | 电源/地跨页冲突 | 分页后没统一命名 | 全局网络表/电源符号统一 |
| 连接器定义反了 | 插上就反/不通 | 公母/正反没对照 | 按实物/手册画 pin1 标记 |
| 忘记测试点 | 上电没法测 | 原理图没留测试点 | 关键电源/信号留测试点 |



### 9.8 本章复盘

#### 9.8.1 公式与规则表

| 公式/规则 | 用途 | 条件与注意 |
|---|---|---|
| $f_c=\frac{1}{2\pi RC}$ | RC 低通截止频率 | R 单位 Ω，C 单位 F |
| $V_{\text{out}}=V_{\text{in}}\frac{R_2}{R_1+R_2}$ | 分压 | 输出端几乎不取电流 |
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

**自测参考答案（先自己做，再对照）：**

1. 符号决定电气功能与管脚号；封装决定焊盘尺寸、间距和极性。
2. `R1-1` 是位号 R1 的第 1 号管脚；在网表里它属于某个网络。
3. 先判断该脚是否确实不用：不用则标 NC，要用则接网络/上拉/下拉。
4. 两个输出并联会互相倒灌，轻则电压拉偏，重则烧器件；需要隔离或均流。
5. 默认网络名不可读、不可搜，改一处不知道影响哪页，PCB 里也无法定位。
6. `项目_功能_版本_日期`，投板前打 tag，Gerber 与工程同版本归档。
7. 立创 EDA 适合零基础快速打样；KiCad 适合免费、长期、跨平台项目。
8. 隐藏电源脚会让 ERC 看不到供电连接，板子可能根本没电。
9. 只在“该脚确实不接”时用，并写原因；不能用来掩盖漏连。
10. 工程文件、PDF 原理图、网表、BOM、Gerber、钻孔、坐标、版本说明。

#### 9.8.4 能力清单

- [ ] 能新建工程并设置图框、网格、规则。
- [ ] 能画 RC 低通、分压、按键三个原理图。
- [ ] 能给元件挂封装并导出网表。
- [ ] 能用 ERC 定位三类错误。
- [ ] 能按版本规范归档工程。

#### 9.8.5 下一章

下一章讲**焊接与返修基础**：原理图画完、板子打样回来，第一件事是把它焊出来。你会看到工具、温度、焊锡、助焊剂，以及虚焊、连锡、冷焊怎么识别。

用别人的库，也要用自己的眼睛再核对一遍。核对完再投板，别把别人的错误焊到自己的板上。

**本章收束**：原理图的价值不在“画得整齐”，而在“能被机器读懂”——网络名、封装映射、DRC 规则三者一致，网表才可信。每次改图后，至少核对一次“符号引脚—封装焊盘—BOM 型号”这条链；链断了，板子就一定错。把这条链当成习惯，比记住任何快捷键都有用。
