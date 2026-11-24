# 第 24 章 · 存储与 DDR 基础

> **所属阶段**：阶段四 · 多层板与高速设计
> **前置课程**：第 23 章 阶段复盘与设计评审
> **本课难度**：⭐⭐⭐

## 本章目标

学完本章，你应该能够：

1. 区分 NOR/NAND Flash、EEPROM、SRAM、DRAM、DDR 的用途。
2. 说清 DDR 的 bank、row/column、prefetch、burst 基本概念。
3. 看懂 DDR 的电源、时钟、命令/地址、数据组的连接关系。
4. 解释 DDR 布线为什么要求等长、阻抗、参考平面。
5. 给一个 SoC 画 DDR 拓扑（点对点/ fly-by）。
6. 判断 DDR 容量/位宽/速率是否匹配 SoC。
7. 说出至少 8 个 DDR 设计常见坑。

存储是“程序的仓库”，DDR 是“运行时的桌子”。DDR 不像 SPI Flash 那样“接上就能读”，它是高速并行总线，布线/电源/时序都要一起看。

## 正文

### 24.1 它解决什么问题：三个真实场景

#### 24.1.1 场景一：DDR 容量选小，系统跑大程序就崩

SoC 标称支持 2GB，板子只贴 512MB，跑 Linux + 应用后 OOM。DDR 容量/位宽要按系统预算选，不是“能亮就行”。

#### 24.1.2 场景二：DDR 布线不等长，跑一会儿花屏

DDR 数据组内不等长、跨分割，低频能跑，高频误码。DDR 的等长/阻抗/参考平面是硬要求。

#### 24.1.3 场景三：DDR 电源噪声大，随机死机

DDR 的 VREF/VTT/电源去耦不足，读写时电流突变，眼图闭合。DDR 电源要按手册加电容/终端。

### 24.2 它是什么：从存储层次到 DDR

| 类型 | 掉电保留 | 速度 | 用途 |
|---|---|---|---|
| NOR Flash | 是 | 中 | 启动代码/固件 |
| NAND Flash | 是 | 高容量 | 系统/数据存储 |
| EEPROM | 是 | 低 | 参数/校准 |
| SRAM | 否 | 高 | MCU 内部 RAM |
| DRAM | 否 | 高 | 运行内存 |
| DDR | 否 | 很高 | SoC 主内存 |

DDR（Double Data Rate，双倍数据速率）在时钟上下沿都传数据。关键概念：

- **Bank**：内部存储阵列分区，可并行。
- **Row/Column**：行地址/列地址，先激活行再读列。
- **Burst**：一次连续读/写多个数据。
- **Prefetch**：内部预取，提高带宽。
- **DQS**：数据选通，和 DQ 一起传输。

> **术语第一次出现**：Fly-by（飞越式）是 DDR 命令/地址/时钟走线依次经过多颗颗粒的拓扑；数据线点对点。Fly-by 要做终端匹配和长度补偿。

#### 24.2.1 存储层次：为什么需要 DDR

CPU 跑得比存储快得多：寄存器 1 个周期、L1 几个周期、L2 十几个、主存几十到上百个周期、Flash/硬盘上千。为了让 CPU 不“等米下锅”，系统用“缓存+主存”分层：常用数据放 SRAM 缓存，大块数据放 DRAM 主存，掉电不丢的放 Flash/ eMMC。DDR 就是“主存”这一层：容量大（GB 级）、带宽高（GB/s 级）、单位成本低，但掉电即失、需要定期刷新、时序复杂。做硬件时要回答三个问题：容量够不够、带宽够不够、时序/电源能不能稳。任何一个不够，系统就表现为“跑大程序崩/花屏/随机死机”。

**课程**：先分清“哪一层存储”再谈选型；把 eMMC 当内存、把 DDR 当硬盘，都是常见误解。

#### 24.2.2 DRAM 单元与刷新

DRAM 的 1 bit 是一个电容+一个晶体管：电容存电荷表示 0/1，晶体管做开关。电容会漏电，所以必须每隔几十毫秒“读出来再写回去”，叫刷新（refresh）。刷新按行进行，每次刷一行；温度越高漏电越快，高温下刷新频率要加倍（如 85℃ 以上）。刷新会占用总线时间，所以“可用带宽”不是标称带宽的 100%。读操作是“破坏性读出”：读走电荷后要写回，这也是 DRAM 时序里 tRCD/tRAS/tWR 存在的原因。

**课程**：DDR 的“随机死机”有时不是布线，是刷新/温度/电源问题；先看温度再怀疑走线。

#### 24.2.3 SDRAM 的内部结构：bank/row/col

一颗 DDR 内部分成多个 bank（常见 8/16 个），每个 bank 有行（row）和列（col）阵列。访问流程是：先激活某 bank 的某行（ACT），再读/写某列（RD/WR），最后预充电（PRE）关闭该行。同一 bank 连续访问不同行要先 PRE 再 ACT，开销大；不同 bank 可以交错操作，提高效率。这就是为什么“顺序访问/多 bank 并行”快，而“随机跨行”慢。控制器会做调度（bank interleaving）来隐藏这些开销；硬件设计要保证地址/命令/数据走线等长、电源干净，否则控制器再聪明也救不回来。

**课程**：DDR 不是“插上就能跑”，它是“模拟+数字+时序”三合一。

#### 24.2.4 DDR 代际：DDR3/4/5 的差别

**电压**：DDR3 1.5V（L 1.35V）、DDR4 1.2V、DDR5 1.1V；电压越低，眼图越小、对电源/阻抗越敏感。

**速率**：DDR3 800～2133MT/s、DDR4 2133～3200、DDR5 4800～6400+；速率越高，时序窗口越窄。

**结构**：DDR4 引入 bank group，DDR5 把 channel 拆成两个子通道、片上 ECC、决策反馈均衡（DFE）。

**电源**：DDR3 需要 VTT 端接电源，DDR4/DDR5 多为 POD 端接，VTT 需求减少但 VREF 更敏感。

**课程**：新手建议从 DDR3/DDR4 点对点学起；DDR5 对阻抗/电源/仿真要求高，不适合第一块板。

#### 24.2.5 位宽、容量与颗粒数量

容量=颗粒容量×颗粒数；位宽=颗粒位宽×颗粒数（并联）。例如 2 颗 16bit 512Mb 颗粒并联成 32bit、1Gb 总容量。控制器位宽常见 16/32/64bit；位宽越宽，带宽越高，但走线越多、等长越难。颗粒数量增加会带来拓扑问题（fly-by/星形）、负载加重、信号质量下降。选型时要先定“位宽/容量/速率”，再定“几颗/什么拓扑”，不要先买颗粒再凑。

**算例**：64bit 总线、1600MT/s，理论带宽=64bit×1600MT/s/8=12.8GB/s；实际可用约 70%～85%，看访问模式。

#### 24.2.6 突发长度与预取

DDR 以“突发（burst）”为单位传输，常见 BL8（连续 8 个数据）。内部预取（prefetch）把多个 bit 并行取出再串行发送：DDR3 8n、DDR4 8n、DDR5 16n。突发长度与位宽共同决定“一次访问搬多少数据”：64bit×8=512bit=64B，正好一个缓存行。硬件设计要保证 DQS/DQ 的相位关系支持这个突发；控制器会做 write leveling/read training，但前提是走线等长、阻抗连续。

**课程**：看到“BL8/预取 8n”不要死记，理解为“内部宽、外部快”。

#### 24.2.7 单端与差分：DQS 为什么是差分

DDR 的数据 DQ 是单端信号，参考 VREF；选通 DQS 是差分（DQS/DQS#），因为它要在高速下准确“框住”数据窗口。DQS 由发送端随数据一起发出（源同步），接收端用 DQS 的边沿采样 DQ。差分 DQS 抗共模噪声、时序抖动小；单端 DQ 则依赖 VREF 和电源质量。设计时要成对走 DQS、等长、同层、参考面连续；DQ 组内等长、组间可不同。把 DQS 当普通单端线走，是 DDR 失败的常见原因。

**课程**：DQS 是“节拍器”，DQ 是“演员”；节拍器乱了，演员再好也没用。

#### 24.2.8 控制器与 PHY 的分工

DDR 控制器（Controller）负责命令调度、地址复用、刷新、时序参数；PHY 负责把数字信号变成模拟波形、做 write leveling/read training、调节 delay/驱动强度。SoC 厂商通常给“PHY 训练固件/配置表”，硬件工程师要做的是：按参考设计布线、选对颗粒、供好电源、留测试点。训练能补偿一部分偏差，但补偿不了“阻抗不连续/等长差太多/电源噪声大”。所以“反正有训练”不是不做等长的理由。

**课程**：训练是“微调”，不是“纠错”；先把物理层做对。

### 24.3 关键参数与手册

| 参数 | 含义 | 设计影响 |
|---|---|---|
| 容量 | 颗粒容量×数量 | 系统内存 |
| 位宽 | x8/x16/x32 | 总线宽度 |
| 速率 | MT/s | 布线/时序 |
| 电压 | 1.5V/1.35V/1.2V | 电源/电平 |
| VREF | 参考电压 | 走线/去耦 |
| ODT | 片上终端 | 匹配 |
| CL/tRCD/tRP | 时序 | SoC 配置 |

#### 24.3.1 速率、时钟与数据率

DDR 标称“1600MT/s”指每秒 1600M 次数据传输；时钟 CK 是 800MHz，因为双沿传输（DDR=Double Data Rate）。所以“1600MT/s”不等于“1600MHz 时钟”，看手册时要分清 tCK（时钟周期，单位 ns）与数据率。tCK=1.25ns 对应 800MHz 时钟/1600MT/s；tCK=0.625ns 对应 3200MT/s。带宽=位宽×数据率/8。写预算时用“数据率”，画时序/算等长时用“tCK”，不要混。

**算例**：32bit、2400MT/s → 32×2400/8=9.6GB/s 理论峰值。

#### 24.3.2 关键时序参数：CL/tRCD/tRP/tRAS

**CL（CAS Latency）**：从读命令到数据输出的时钟数；越大越慢，但高频下必须大。

**tRCD**：激活到读/写命令的最小间隔；行选通延迟。

**tRP**：预充电到下一次激活的最小间隔。

**tRAS**：激活到预充电的最小时间；保证行保持足够久。

**tWR**：写恢复到预充电的时间。

**关系**：一次“跨行读”大致要 tRCD+CL+tRP 的等待；控制器会重排命令隐藏。选颗粒时不能只看 CL，要看整套时序在目标速率下是否满足控制器/PHY 能力。

#### 24.3.3 刷新与温度：tREFI 与高温加倍

tREFI 是刷新间隔（常见 7.8μs/3.9μs），tRFC 是刷新占用时间。温度升高漏电加快，标准要求 85℃ 以上刷新频率加倍（tREFI 减半），更高温再加倍。刷新占用带宽：占用率≈tRFC/tREFI。例如 tRFC=350ns、tREFI=7.8μs，占用约 4.5%；高温加倍后约 9%。这就是“高温下带宽下降/更热”的原因之一。设计时要保证高温下电源/散热/刷新配置都到位，不能只按常温调。

**课程**：工业/车载产品必须按最高温度配刷新策略。

#### 24.3.4 端接：ODT、VTT 与 POD

**ODT（On-Die Termination）**：颗粒内部可切换端接电阻，写时开启、读时关闭；控制器通过 MR 寄存器配置。ODT 不匹配会造成反射/过冲。

**VTT**：DDR3 常用 0.75V 端接电源（VDD/2），需要能吸/灌电流的 LDO 或专用 VTT 芯片；VTT 不稳会直接恶化眼图。

**POD（Pseudo Open Drain）**：DDR4/DDR5 端接为“上拉到 VDDQ/下拉到地”的组合，不再需要 VTT；但 VREF 更关键。

**用法**：按颗粒/控制器手册配 ODT；不要“全开/全关”图省事。

#### 24.3.5 VREF：单端信号的“尺子”

DDR3 的 VREF 常为 VDDQ/2（0.75V），由电阻分压或专用 VREF 芯片产生；DDR4 的 VREF 可能由控制器内部生成/外部提供。VREF 不稳或噪声大，DQ 采样就会“高低不分”，表现为随机误码。要求：VREF 走线远离高速/电源开关节点、加去耦、分压电阻精度 1%、靠近控制器/颗粒。很多“跑一会儿花屏”的根因就是 VREF 被电源噪声带动。

**课程**：VREF 是“尺子”，尺子抖，量什么都不准。

#### 24.3.6 电源域与去耦

DDR 电源通常有 VDD（核心）、VDDQ（IO）、VPP（DDR4 字线升压）、VTT/VREF。每路都要有足够去耦：大容量（10μF 级）+ 中容量（1μF/0.1μF）+ 小容量（0.01μF）组合，靠近颗粒/控制器放置。VDDQ 的噪声直接进 DQ 眼图；VPP 不稳会影响激活/写恢复。去耦不是“越多越好”，而是“容值组合+位置+低 ESL”。DDR 颗粒下方尽量放 0.1μF，电源引脚到电容到地过孔路径最短。

**课程**：DDR 电源评审先看“每颗颗粒旁边有没有 0.1μF”。

#### 24.3.7 温度与自刷新

DRAM 有自刷新（Self Refresh）模式：低功耗时由颗粒自己刷新，控制器可休眠。温度升高时自刷新频率也要提高；工业级颗粒支持宽温。做产品时要确认“工作温度范围内自刷新/刷新配置”是否满足，不能只测常温。高温还会加速老化，DDR 周围的热设计（风道/铜箔/散热片）要一起看。

**课程**：温度不是“环境部门的事”，它直接改 DDR 的时序和寿命。

#### 24.3.8 手册怎么读：先看这五页

1. **Features/Ordering**：电压/速率/容量/位宽/温度等级。
2. **Pin Description**：电源/地/DQ/DQS/地址/命令/ODT/ZQ。
3. **Absolute/Recommended Operating**：电压范围、温度范围。
4. **AC/DC 时序表**：tCK/tRCD/tRP/tRAS/CL、建立/保持窗口。
5. **初始化/模式寄存器**：上电序列、MR 配置、ZQ 校准、ODT 设置。

**方法**：把关键参数抄到自己的“选型表”，不要每次翻 200 页手册；抄的时候带页码。

### 24.4 三个典型连接

#### 24.4.1 DDR 点对点

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 320">
  <text x="20" y="30" font-size="16" fill="currentColor">图 24-1：SoC 与 DDR 点对点连接</text>
  <rect x="80" y="80" width="160" height="140" rx="8" fill="none" stroke="currentColor" stroke-width="2"/>
  <text x="120" y="115" font-size="13" fill="currentColor">SoC</text>
  <text x="100" y="145" font-size="11" fill="currentColor">DDR 控制器</text>
  <text x="100" y="170" font-size="11" fill="currentColor">DQ/DQS/CA</text>
  <rect x="460" y="80" width="160" height="140" rx="8" fill="none" stroke="currentColor" stroke-width="2"/>
  <text x="500" y="115" font-size="13" fill="currentColor">DDR 颗粒</text>
  <text x="480" y="145" font-size="11" fill="currentColor">DQ/DQS/CA</text>
  <text x="480" y="170" font-size="11" fill="currentColor">VREF/VTT</text>
  <line x1="240" y1="120" x2="460" y2="120" stroke="currentColor" stroke-width="2"/>
  <line x1="240" y1="150" x2="460" y2="150" stroke="currentColor" stroke-width="2"/>
  <line x1="240" y1="180" x2="460" y2="180" stroke="currentColor" stroke-width="2"/>
  <text x="300" y="110" font-size="10" fill="currentColor">DQ</text>
  <text x="300" y="145" font-size="10" fill="currentColor">DQS</text>
  <text x="300" y="175" font-size="10" fill="currentColor">CA</text>
  <text x="80" y="265" font-size="13" fill="currentColor">数据组内等长；CA/CLK 按拓扑；参考平面连续。</text>
</svg>
```

#### 24.4.2 Fly-by 多颗粒

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 280">
  <text x="20" y="30" font-size="16" fill="currentColor">图 24-2：Fly-by：CA/CLK 依次经过颗粒</text>
  <rect x="40" y="90" width="120" height="90" rx="6" fill="none" stroke="currentColor" stroke-width="2"/>
  <text x="60" y="125" font-size="13" fill="currentColor">SoC</text>
  <rect x="230" y="90" width="100" height="90" rx="6" fill="none" stroke="currentColor" stroke-width="1.5"/>
  <text x="250" y="125" font-size="12" fill="currentColor">DDR1</text>
  <rect x="380" y="90" width="100" height="90" rx="6" fill="none" stroke="currentColor" stroke-width="1.5"/>
  <text x="400" y="125" font-size="12" fill="currentColor">DDR2</text>
  <rect x="530" y="90" width="100" height="90" rx="6" fill="none" stroke="currentColor" stroke-width="1.5"/>
  <text x="550" y="125" font-size="12" fill="currentColor">DDR3</text>
  <line x1="160" y1="120" x2="230" y2="120" stroke="currentColor" stroke-width="2"/>
  <line x1="330" y1="120" x2="380" y2="120" stroke="currentColor" stroke-width="2"/>
  <line x1="480" y1="120" x2="530" y2="120" stroke="currentColor" stroke-width="2"/>
  <line x1="630" y1="120" x2="680" y2="120" stroke="currentColor" stroke-width="2"/>
  <text x="650" y="110" font-size="10" fill="currentColor">终端</text>
  <text x="40" y="230" font-size="13" fill="currentColor">数据线仍点对点；CA/CLK 长度补偿/终端按手册。</text>
</svg>
```

#### 24.4.3 DDR 电源

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 300">
  <text x="20" y="30" font-size="16" fill="currentColor">图 24-3：DDR 电源与去耦</text>
  <text x="40" y="95" font-size="13" fill="currentColor">1.2V/1.5V</text>
  <line x1="120" y1="90" x2="220" y2="90" stroke="currentColor" stroke-width="2"/>
  <rect x="220" y="70" width="120" height="90" rx="6" fill="none" stroke="currentColor" stroke-width="2"/>
  <text x="245" y="105" font-size="12" fill="currentColor">DDR 电源</text>
  <text x="235" y="130" font-size="11" fill="currentColor">VDD/VDDQ</text>
  <line x1="340" y1="90" x2="440" y2="90" stroke="currentColor" stroke-width="2"/>
  <rect x="440" y="70" width="140" height="90" rx="6" fill="none" stroke="currentColor" stroke-width="1.5"/>
  <text x="465" y="105" font-size="12" fill="currentColor">VREF/VTT</text>
  <text x="460" y="130" font-size="11" fill="currentColor">分压/终端</text>
  <text x="40" y="210" font-size="13" fill="currentColor">每个电源脚 100nF；大电容 10μF；VREF 单独滤波，远离开关电源。</text>
</svg>
```

#### 24.4.4 拓扑选择：点对点、fly-by、星形

**点对点**：控制器→1 颗颗粒，走线最短、信号最好，常见于 MCU/低端 SoC。

**Fly-by**：地址/命令/时钟沿一条线依次经过多颗颗粒，末端端接；数据线各自点对点。DDR3/DDR4 多颗粒常用，优点是地址/命令负载可控，缺点是末端颗粒时序偏后，需要 write leveling/读训练补偿。

**星形**：所有颗粒到同一节点等长，适合少量颗粒/低速；高速多颗粒时分支反射严重。

**选择**：1～2 颗优先点对点/短 fly-by；4 颗以上按控制器手册推荐拓扑；不要自创“随便连”。

#### 24.4.5 Fly-by 的等长与端接细节

Fly-by 要求：地址/命令/时钟走线连续、分支短（最好无分支）、末端端接电阻靠近最后一颗颗粒；每颗颗粒的 DQS/DQ 与控制器点对点，组内等长。时钟与地址/命令之间的偏斜要靠 write leveling 补偿，但前提是“同一拓扑、阻抗连续”。末端端接（常见 39～56Ω 到 VTT 或 VDDQ）不能省；省了会看到振铃/过冲。走线要避免跨分割、避免过孔 stub 过长。

**课程**：fly-by 不是“把线拉直”，是“让每颗颗粒看到同样的波形”。

#### 24.4.6 星形的适用与风险

星形拓扑把所有颗粒的地址/命令连到一个中心点，理论上等长最好；但中心点分支多，阻抗不连续，高速下反射明显。它适合 2～4 颗、速率不高、控制器驱动强的场景。做星形时要：中心节点加端接、分支尽量短、每支等长；数据线仍按组点对点。速率 >1600MT/s 时优先 fly-by/点对点，不要硬上星形。

**课程**：拓扑没有“最好”，只有“和速率/颗粒数匹配”。

#### 24.4.7 DDR 电源的三种方案

**LDO 方案**：VDDQ/VTT 用 LDO，简单、噪声低，但效率低、发热大；适合小电流/低速率。

**Buck 方案**：VDDQ 用 Buck，效率高，但开关噪声要滤；适合大电流/高速。

**专用 PMIC**：DDR4/DDR5 常用多路 PMIC（VDD/VDDQ/VPP），配时序/监控；省空间但贵。

**选择**：按电流/效率/噪声/成本；VTT 要能吸灌电流（DDR3），VPP 要干净（DDR4）。

#### 24.4.8 ZQ 校准电阻

颗粒的 ZQ 引脚要接精密电阻（常见 240Ω/1%）到地，用于输出阻抗校准；控制器也有 ZQ 校准。电阻精度/走线短/远离噪声是关键。ZQ 校不准会导致驱动强度/端接偏差，眼图变差。评审时看“ZQ 电阻值/精度/位置”，不要漏。

**课程**：一颗 1% 电阻，可能决定 DDR 能不能跑满速。

#### 24.4.9 DDR 测试点与调试

留测试点：CK/CK#、DQS/DQ（至少一组）、VDDQ/VREF、ZQ、复位。测试点要短、不破坏阻抗、可探。调试顺序：电源→时钟→复位→初始化→训练→读写测试→压力测试。没有测试点，只能“换颗粒/换板”猜。

**课程**：DDR 调试最贵的是“看不见波形”。

#### 24.4.10 点对点与 fly-by 的走线差别

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 320">
  <text x="20" y="28" font-size="16" fill="currentColor">图 24-4：点对点 vs fly-by</text>
  <rect x="60" y="60" width="90" height="50" fill="none" stroke="currentColor" stroke-width="1.5"/>
  <text x="82" y="90" font-size="12" fill="currentColor">控制器</text>
  <rect x="380" y="60" width="90" height="50" fill="none" stroke="currentColor" stroke-width="1.5"/>
  <text x="405" y="90" font-size="12" fill="currentColor">颗粒</text>
  <line x1="150" y1="85" x2="380" y2="85" stroke="currentColor" stroke-width="2"/>
  <text x="200" y="75" font-size="10" fill="currentColor">DQ/DQS/CK/ADDR</text>
  <text x="60" y="145" font-size="12" fill="currentColor">点对点：一颗一颗走，最短</text>
  <rect x="60" y="180" width="90" height="45" fill="none" stroke="currentColor" stroke-width="1.5"/>
  <text x="76" y="207" font-size="11" fill="currentColor">控制器</text>
  <rect x="230" y="180" width="60" height="45" fill="none" stroke="currentColor" stroke-width="1.5"/>
  <text x="245" y="207" font-size="10" fill="currentColor">颗粒1</text>
  <rect x="350" y="180" width="60" height="45" fill="none" stroke="currentColor" stroke-width="1.5"/>
  <text x="365" y="207" font-size="10" fill="currentColor">颗粒2</text>
  <rect x="470" y="180" width="60" height="45" fill="none" stroke="currentColor" stroke-width="1.5"/>
  <text x="485" y="207" font-size="10" fill="currentColor">颗粒3</text>
  <line x1="150" y1="202" x2="230" y2="202" stroke="currentColor" stroke-width="2"/>
  <line x1="290" y1="202" x2="350" y2="202" stroke="currentColor" stroke-width="2"/>
  <line x1="410" y1="202" x2="470" y2="202" stroke="currentColor" stroke-width="2"/>
  <line x1="530" y1="202" x2="560" y2="202" stroke="currentColor" stroke-width="1.5"/>
  <rect x="560" y="190" width="22" height="22" fill="none" stroke="currentColor" stroke-width="1.5"/>
  <text x="560" y="235" font-size="10" fill="currentColor">末端端接</text>
  <text x="60" y="265" font-size="12" fill="currentColor">fly-by：地址/命令一条线串下去，末端端接；DQ 各自点对点</text>
  <text x="40" y="300" font-size="11" fill="currentColor">末端颗粒时序最晚，需要 write leveling/读训练补偿。</text>
</svg>
```

**看图**：点对点没有分支反射，fly-by 有末端端接但各颗粒到达时间不同；拓扑由颗粒数和速率决定。

### 24.5 选型与降额

| 项目 | 选择 | 注意 |
|---|---|---|
| 容量 | 按系统预算×1.5 | 不选刚好 |
| 位宽 | 匹配 SoC | x16/x32 |
| 速率 | 按 SoC 支持 | 高速布线难 |
| 电压 | 按颗粒 | 1.2/1.35/1.5V |
| 颗粒数量 | 拓扑/布线 | Fly-by |
| 终端 | 按手册 | VTT/ODT |

#### 24.5.1 容量预算：别按“能跑就行”

容量预算要列：操作系统/文件系统、应用、缓存/缓冲、日志、升级余量。经验：预留 30%～50% 余量，否则“跑大程序/升级”就崩。eMMC/NAND 还要算“预留空间/磨损均衡”；DDR 容量不够会频繁换页，性能骤降。评审时问“最大同时运行什么/未来一年加什么”，不要只看 demo。

**课程**：容量是“需求”，不是“成本项”；省 1GB 可能省出一年后的返工。

#### 24.5.2 带宽预算：峰值不等于可用

带宽=位宽×速率/8×效率。效率受刷新、跨行、命令开销、访问模式影响，通常 70%～85%。预算要按“最坏并发”算：屏幕刷新+DDR 读写+网络 DMA+CPU 缓存未命中。若峰值接近理论值 80%，就要升位宽/升速率/加缓存/优化访问。不要用“理论带宽”做设计余量。

**算例**：64bit/2400MT/s=19.2GB/s 理论；按 75% 可用≈14.4GB/s；系统峰值 12GB/s，余量约 20%。

#### 24.5.3 颗粒选型：先看“能不能买到/能不能跑”

选型顺序：控制器支持列表（QVL）→ 电压/速率/容量/位宽 → 温度等级 → 封装/高度 → 供货/价格/替代。优先选“参考设计用过/厂商验证过”的颗粒；新颗粒要打样验证。注意“同型号不同批次”的时序差异，量产要锁定批次/供应商。

**课程**：DDR 颗粒不是“参数对就行”，互通性/批次一致性很关键。

#### 24.5.4 降额：速率/温度/电压

降额思路：标称 3200MT/s 的颗粒在四层板/普通阻抗下可能只能跑 2400；工业温度下时序余量更小。设计时按“降一档”选型（如目标 2400 选 3200 颗粒），留时序/眼图余量。电压/端接/驱动强度按手册推荐，不要“超频”当常规。降额不是“保守”，是“给批次/温度/生产波动留空间”。

**课程**：能跑 demo 不等于能量产；降额是量产思维。

#### 24.5.5 BOM 与替代

BOM 要写清：厂商/型号/速度等级/温度/封装/批次要求；替代料要同电压/同速率/同时序/同封装，且验证过。DDR 替代不能只看“容量一样”，bank 结构/时序/ODT 可能不同。建议关键物料双源，但替代料必须打样验证，不能“直接换”。

**课程**：DDR 是“最不该随便替代”的器件之一。

#### 24.5.6 成本与层数

DDR 布线层数影响成本：2 层很难做好阻抗/等长；4 层可做但余量小；6 层以上更容易。速率越高、颗粒越多，层数/阻抗/电源要求越高。选型时把“层数/阻抗/电源/测试”成本一起算，不要只看颗粒单价。

**课程**：省 layer 的钱，常在调试/返工里加倍还回去。

### 24.6 测量与仿真

#### 24.6.1 DDR 检查

1. 电源电压/纹波。
2. VREF 电压。
3. 时钟/CA/DQ 波形。
4. 眼图/误码（有条件）。
5. 内存测试（memtest）。

#### 24.6.2 CircuitJS

```circuitjs
rc-lowpass-159
```

观察高速线上的 RC 效应，理解等长/阻抗为什么重要。

#### 24.6.3 动手任务

- 查一颗 DDR 颗粒手册，列容量/位宽/电压/速率。
- 画 SoC 与 DDR 的连接框图。
- 列 DDR 电源去耦清单。
- 跑一次内存测试，记录速率/误码。

#### 24.6.4 眼图与模板

DDR 眼图看“张开度”：水平（时间）和垂直（电压）。用示波器+差分探头测 DQS/DQ，触发用 CK 或 DQS；看最差组合（高温/低压/满载）。眼图闭合的常见原因：阻抗不连续、等长差、VREF 噪声、端接错、电源跌落。测试要记录“条件/速率/温度”，不能只截一张漂亮图。

**课程**：眼图是“结果”，布线/电源/端接是“原因”；先查原因再调 PHY。

#### 24.6.5 时序测量：建立/保持窗口

用示波器测 DQ 相对 DQS 的建立/保持时间；与颗粒/控制器手册的窗口比较。注意探头带宽/接地方式（短地弹簧），否则测到的是“探头振铃”。多测几组 DQ（最差位），不要只看一组。结果偏小先查等长/阻抗，再查 PHY delay 配置。

**课程**：量时序时，探头地线太长会把好板测成坏板。

#### 24.6.6 读写压力测试

初始化通过不等于稳定。要做：全地址写读比对、March 测试、长时间老化、温度循环、满带宽压力。观察误码/重启/花屏。压力测试暴露的是“时序/电源/温度余量”，不是“功能”。记录误码位置/温度/电压，便于定位。

**课程**：DDR 问题常是“概率性”的，跑 10 分钟不算测过。

#### 24.6.7 电源噪声测量

测 VDDQ/VREF/VPP 的纹波/瞬态：用 AC 耦合、20MHz 带宽、短地。最坏情况是“DDR 满负荷+CPU 满负荷+屏幕刷新”。纹波超标先查去耦/电源环路/地。VREF 噪声要单独看，它直接进眼图。

**课程**：DDR 电源不是“直流对就行”，瞬态才是杀手。

#### 24.6.8 仿真：IBIS 与拓扑

高速 DDR 建议做 IBIS 仿真：看振铃/过冲/眼图/串扰。模型用厂商 IBIS，叠层/阻抗/端接按实际。仿真不能替代实测，但能在打样前发现“拓扑/端接/等长”问题。仿真报告要写“条件/模型/结论”，不要只放一张图。

**课程**：仿真和实测是“互相验证”，不是“二选一”。

#### 24.6.9 调试顺序：从电源到压力

1. 静态阻抗/短路。
2. 电源电压/纹波（VDD/VDDQ/VPP/VREF）。
3. 时钟频率/幅度。
4. 复位/初始化。
5. PHY 训练（write leveling/read training）。
6. 单地址读写。
7. 全地址/压力/温度。
8. 眼图/时序余量。

**课程**：跳过前面直接跑压力，等于在坏地基上盖楼。

#### 24.6.10 眼图要看什么

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 300">
  <text x="20" y="28" font-size="16" fill="currentColor">图 24-5：DDR 眼图示意（时间×电压）</text>
  <line x1="90" y1="60" x2="90" y2="230" stroke="currentColor" stroke-width="1.5"/>
  <line x1="90" y1="230" x2="640" y2="230" stroke="currentColor" stroke-width="1.5"/>
  <text x="40" y="70" font-size="11" fill="currentColor">电压</text>
  <text x="600" y="255" font-size="11" fill="currentColor">时间</text>
  <path d="M110 100 L250 100 L270 140 L290 100 L430 100 L450 140 L470 100 L610 100" fill="none" stroke="currentColor" stroke-width="1.5"/>
  <path d="M110 180 L250 180 L270 140 L290 180 L430 180 L450 140 L470 180 L610 180" fill="none" stroke="currentColor" stroke-width="1.5"/>
  <line x1="270" y1="100" x2="270" y2="180" stroke="currentColor" stroke-width="1" stroke-dasharray="3 3"/>
  <line x1="450" y1="100" x2="450" y2="180" stroke="currentColor" stroke-width="1" stroke-dasharray="3 3"/>
  <text x="255" y="95" font-size="10" fill="currentColor">采样点</text>
  <text x="300" y="150" font-size="10" fill="currentColor">眼高</text>
  <text x="420" y="208" font-size="10" fill="currentColor">眼宽</text>
  <text x="40" y="280" font-size="12" fill="currentColor">眼高=电压余量，眼宽=时间余量；闭合先查阻抗/等长/电源。</text>
</svg>
```

**读法**：眼图张开越大，余量越大；温度/低压/满载下再看一次，才是“最坏眼图”。

#### 24.6.11 仿真：VREF 分压与噪声

VREF 常用两颗等值电阻从 VDDQ 分压得到（如 1kΩ/1kΩ 得 VDDQ/2），再并联 0.1μF。问题在于：分压电阻本身有容差，电源纹波会按比例传到 VREF；如果 VREF 走线又长、又没有去耦，DQ 采样阈值就跟着抖。用分压电路仿真可以看到“输入纹波→VREF 纹波”的关系，从而理解为什么评审要求 1% 电阻、近端去耦、远离开关电源。

```circuitjs
voltdivide
```

**判据**：VREF 直流偏差 <±1%；VREF 上的 AC 纹波 < DQ 眼高的 5%；分压电阻精度 1%。

**课程**：VREF 不是“随便分一下”，它是 DDR 的模拟基准。

### 24.7 常见坑

1. **容量/位宽不匹配**：系统不稳/OOM。
2. **DQ 组内不等长**：高频误码。
3. **CA/CLK 拓扑错**：Fly-by 没终端。
4. **参考平面跨分割**：眼图闭合。
5. **VREF 噪声大**：采样错误。
6. **电源去耦不足**：随机死机。
7. **ODT/终端配置错**：反射。
8. **颗粒批次混用**：时序不同。
9. **不跑内存测试**：问题到客户才暴露。

#### 24.7.1 只做“组内等长”，忘了参考面

DQ 组内等长做了，但走线跨了电源/地分割，回流路径断，眼图照样差。评审要看“参考面是否连续、跨分割有没有桥接电容/改层”。等长是“长度”，参考面是“阻抗”；两者缺一不可。

**课程**：等长不等于“信号好”。

#### 24.7.2 把 DQS 当普通线走

DQS 差分对没成对走、没等长、被其他信号穿插，采样窗口直接乱。要求：DQS/DQS# 同层、紧耦合、等长、两侧包地、参考面连续。

**课程**：DQS 是“时钟”，不是“数据”。

#### 24.7.3 去耦电容放太远

0.1μF 放在颗粒另一侧/板边，等于没有。要求：电容靠近电源引脚、地过孔就近、回路最短。DDR 颗粒下方/背面是常用位置。

**课程**：去耦看“回路”，不是看“数量”。

#### 24.7.4 VREF 分压电阻精度不够/噪声大

5% 电阻分压，VREF 偏 0.1V，DQ 采样阈值偏移；加上电源噪声，误码率上升。要求 1% 电阻、加 0.1μF、远离开关电源。

**课程**：VREF 是“模拟基准”，按模拟电路对待。

#### 24.7.5 忽略 ZQ/ODT 配置

ZQ 电阻漏贴/错值，ODT 全关/全开，驱动强度不对，眼图过冲/欠冲。按手册配 MR/ODT，量驱动强度。

**课程**：DDR 初始化不是“跑通就行”，配置错了会“能跑但不可靠”。

#### 24.7.6 电源上电时序错

VDD/VDDQ/VPP 上电顺序不对，颗粒进入异常状态；DDR4 的 VPP 要先于 VDDQ 或按手册。评审看“电源时序图/PMIC 配置”。

**课程**：DDR 也讲“上电礼仪”。

#### 24.7.7 一上来就跑高频

标称 3200 直接跑 3200，失败就换颗粒；其实降频 2400 能稳，说明布线余量不足。正确做法：从低速起，逐步升频，记录失败点，再优化。

**课程**：调试是“二分”，不是“硬顶”。

#### 24.7.8 忽略温度/批次

常温通过，高温误码；这批通过，下批失败。要求高温/低温/电压拉偏测试，锁定批次，量产抽测。

**课程**：DDR 的“稳定性”是温度/电压/批次的函数。

### 24.8 本章复盘

#### 24.8.1 公式与规则表

| 公式/规则 | 用途 | 条件与注意 |
|---|---|---|
| 容量×1.5 | 系统预算 | 不选刚好 |
| DQ 组内等长 | 数据 | 按手册公差 |
| Fly-by + 终端 | CA/CLK | 按拓扑 |
| 参考平面连续 | 阻抗 | 不跨分割 |
| VREF 单独滤波 | 采样 | 远离开关 |

#### 24.8.2 术语表

| 术语 | 英文 | 一句话解释 |
|---|---|---|
| DDR | double data rate | 双倍速率内存 |
| Bank | bank | 内部阵列分区 |
| DQS | data strobe | 数据选通 |
| Fly-by | fly-by | CA/CLK 依次经过颗粒 |
| ODT | on-die termination | 片内终端 |
| VREF | reference voltage | 参考电压 |

#### 24.8.3 自测 10 题

1. NOR/NAND/DRAM 区别？
2. DDR 为什么叫双倍速率？
3. Bank/Row/Column 是什么？
4. DQS 作用？
5. Fly-by 拓扑是什么？
6. DQ 为什么组内等长？
7. VREF 为什么要滤波？
8. ODT 作用？
9. DDR 容量怎么选？
10. 内存测试怎么做？

#### 24.8.4 能力清单

- [ ] 能区分存储类型。
- [ ] 能解释 DDR 基本概念。
- [ ] 能画 DDR 连接拓扑。
- [ ] 能列 DDR 电源/去耦要求。
- [ ] 能跑内存测试。

#### 24.8.5 下一章

下一章讲“叠层阻抗与 SI/PI”：把这一章的 DDR 走线，放到“层叠/阻抗/参考面/电源完整性”的框架里。DDR 是 SI/PI 最苛刻的场景之一；学完下一章再回头看 24 章，会更清楚“为什么要等长、为什么要连续参考面、为什么要去耦”。

**衔接**：本章的眼图/时序问题，下一章用阻抗/回流/PDN 解释；先去把叠层阻抗的算例做一遍，再回来调 DDR，会少走很多弯路，也能看懂 DDR 为什么对“连续参考面”这么敏感，也能解释为什么“等长做了、眼图还是差”；这两件事在叠层/阻抗那一章会彻底讲清。

**练习**：拿一块现成 DDR 板，量一颗颗粒的 VDDQ 纹波和 DQS 眼图，记录温度/负载；再对照本章的“电源/端接/参考面”逐条查，你会发现问题往往不在“跑多快”，而在“供电和回流”；把这两项做对，再谈速率。

#### 24.8.6 下一章

下一章讲**叠层、阻抗与 SI/PI 基础**：DDR 能不能跑，最终取决于叠层和阻抗。
