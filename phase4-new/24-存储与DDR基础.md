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

#### 场景一：DDR 容量选小，系统跑大程序就崩

SoC 标称支持 2GB，板子只贴 512MB，跑 Linux + 应用后 OOM。DDR 容量/位宽要按系统预算选，不是“能亮就行”。

#### 场景二：DDR 布线不等长，跑一会儿花屏

DDR 数据组内不等长、跨分割，低频能跑，高频误码。DDR 的等长/阻抗/参考平面是硬要求。

#### 场景三：DDR 电源噪声大，随机死机

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

### 24.5 选型与降额

| 项目 | 选择 | 注意 |
|---|---|---|
| 容量 | 按系统预算×1.5 | 不选刚好 |
| 位宽 | 匹配 SoC | x16/x32 |
| 速率 | 按 SoC 支持 | 高速布线难 |
| 电压 | 按颗粒 | 1.2/1.35/1.5V |
| 颗粒数量 | 拓扑/布线 | Fly-by |
| 终端 | 按手册 | VTT/ODT |

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

下一章讲**叠层、阻抗与 SI/PI 基础**：DDR 能不能跑，最终取决于叠层和阻抗。
