# 第 12 章 · PCB 布局与布线基础

> **所属阶段**：阶段二 · 从原理图到第一块板
> **前置课程**：第 09～11 章
> **本课难度**：⭐⭐⭐

## 本章目标

学完本章，你应该能够：

1. 说清 PCB 设计九步流程，以及每步的关键产出。
2. 按“先大后小、先核心后外围、信号流向、热分区、接口靠边、测试点可及”六原则完成布局。
3. 用飞线走查法检查布局是否合理，再开始布线。
4. 按电流选线宽，按载流/工艺选过孔，理解直角/锐角的危害。
5. 解释铺铜、接地、回流路径的关系，避免“铺了铜但回流更差”。
6. 完成一块 2 层板的布线、铺铜、DRC 清零。
7. 说出至少 8 个布局布线常见坑。

布局决定 80% 的布线难度。布局错了，布线只能“补锅”；布局对了，布线是水到渠成。

## 正文

### 12.1 它解决什么问题：三个真实场景

#### 场景一：去耦电容放在芯片背面，电源纹波压不下去

芯片电源脚旁边没有放 100nF，电容放在板子另一头。芯片瞬间取电时，电流要跑很长一段走线，寄生电感让电源电压塌陷。不是电容没用，是放错位置。

#### 场景二：晶振走线穿过电源/USB，时钟被干扰

晶振输出走了一条长线，旁边是 USB 差分和 DC-DC 的 SW 节点。时钟上叠了开关噪声，MCU 跑飞。晶振要靠近芯片、包地、远离噪声源。

#### 场景三：USB 差分线一长一短，眼图闭合

USB D+/D− 没有按差分对走，长度差 500mil，参考平面被电源分割。低速还能枚举，高速丢包。差分对要等长、等距、连续参考平面。

### 12.2 它是什么：布局是“摆关系”，布线是“连网络”

PCB 设计九步：

1. 需求与方案
2. 原理图
3. 封装匹配
4. 网表导入
5. 布局
6. 布线
7. 铺铜
8. DRC
9. 生产文件

**布局**解决“器件之间的相对位置”：谁靠近谁、谁远离谁、接口放哪、散热怎么走。
**布线**解决“网络怎么连”：线宽、过孔、层、长度、参考平面。

> **术语第一次出现**：飞线（ratsnest）是 PCB 软件把未布线的网络画成细线，用来提示连接关系。飞线不是电气连接，只是“应该连”。

### 12.3 关键参数与设计规则

| 参数 | 推荐值（2 层普通板） | 依据 |
|---|---|---|
| 最小线宽 | 6～8mil（0.15～0.2mm） | 板厂能力 |
| 电源线宽 | 20～40mil 或按 1A/mm 估算 | 电流/温升 |
| 最小间距 | 6～8mil | 板厂能力 |
| 过孔 | 0.3/0.6mm（钻孔/焊盘） | 载流/工艺 |
| 铜厚 | 1oz（35μm） | 常规板 |
| 晶振包地 | 是 | 抗干扰 |
| 去耦电容 | 每个电源脚 100nF，尽量近 | 瞬态电流 |

线宽估算（经验起点，最终按 IPC/板厂）：

`I ≈ k × ΔT^0.44 × A^0.725`，其中 A 是铜截面积。工程上常用简化：1oz 铜、10℃ 温升，1mm 线宽约 2～3A。实际按板厂/IPC 计算器复核。

### 12.4 三个典型布局

#### 12.4.1 电源入口与保护

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 320">
  <text x="20" y="30" font-size="16" fill="currentColor">图 12-1：电源入口布局：接口→保护→滤波→稳压</text>
  <rect x="30" y="70" width="110" height="70" rx="6" fill="none" stroke="currentColor" stroke-width="1.5"/>
  <text x="55" y="110" font-size="13" fill="currentColor">连接器</text>
  <rect x="180" y="70" width="110" height="70" rx="6" fill="none" stroke="currentColor" stroke-width="1.5"/>
  <text x="205" y="110" font-size="13" fill="currentColor">保险/TVS</text>
  <rect x="330" y="70" width="110" height="70" rx="6" fill="none" stroke="currentColor" stroke-width="1.5"/>
  <text x="355" y="110" font-size="13" fill="currentColor">输入电容</text>
  <rect x="480" y="70" width="110" height="70" rx="6" fill="none" stroke="currentColor" stroke-width="1.5"/>
  <text x="505" y="110" font-size="13" fill="currentColor">稳压器</text>
  <line x1="140" y1="105" x2="180" y2="105" stroke="currentColor" stroke-width="2"/>
  <line x1="290" y1="105" x2="330" y2="105" stroke="currentColor" stroke-width="2"/>
  <line x1="440" y1="105" x2="480" y2="105" stroke="currentColor" stroke-width="2"/>
  <text x="35" y="200" font-size="13" fill="currentColor">原则：保护器件靠近接口；输入电容紧靠稳压器输入脚；</text>
  <text x="35" y="225" font-size="13" fill="currentColor">大电流走线短、粗、少换层；SW 节点远离敏感模拟区。</text>
</svg>
```

#### 12.4.2 去耦电容与芯片

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 320">
  <text x="20" y="30" font-size="16" fill="currentColor">图 12-2：去耦电容布局：近、短、少过孔</text>
  <rect x="250" y="80" width="180" height="120" rx="8" fill="none" stroke="currentColor" stroke-width="2"/>
  <text x="300" y="145" font-size="14" fill="currentColor">MCU</text>
  <text x="270" y="170" font-size="12" fill="currentColor">VDD / GND</text>
  <rect x="300" y="230" width="80" height="30" fill="none" stroke="currentColor" stroke-width="2"/>
  <text x="315" y="250" font-size="12" fill="currentColor">100nF</text>
  <line x1="340" y1="200" x2="340" y2="230" stroke="currentColor" stroke-width="2"/>
  <line x1="300" y1="245" x2="240" y2="245" stroke="currentColor" stroke-width="2"/>
  <line x1="240" y1="245" x2="240" y2="270" stroke="currentColor" stroke-width="2"/>
  <line x1="220" y1="270" x2="260" y2="270" stroke="currentColor" stroke-width="2"/>
  <text x="180" y="285" font-size="12" fill="currentColor">GND</text>
  <text x="430" y="110" font-size="13" fill="currentColor">正确：电容紧贴电源脚，</text>
  <text x="430" y="135" font-size="13" fill="currentColor">回路短，过孔少。</text>
  <text x="430" y="175" font-size="13" fill="currentColor">错误：电容放远/过孔多，</text>
  <text x="430" y="200" font-size="13" fill="currentColor">寄生电感抵消去耦效果。</text>
</svg>
```

#### 12.4.3 晶振与 USB 差分

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 320">
  <text x="20" y="30" font-size="16" fill="currentColor">图 12-3：晶振包地与 USB 差分对</text>
  <rect x="80" y="80" width="160" height="120" rx="8" fill="none" stroke="currentColor" stroke-width="1.5"/>
  <text x="110" y="110" font-size="14" fill="currentColor">MCU</text>
  <rect x="300" y="100" width="80" height="60" rx="6" fill="none" stroke="currentColor" stroke-width="1.5"/>
  <text x="315" y="135" font-size="12" fill="currentColor">晶振</text>
  <line x1="240" y1="130" x2="300" y2="130" stroke="currentColor" stroke-width="2"/>
  <path d="M295 90 Q260 70 295 50" fill="none" stroke="currentColor" stroke-width="1" stroke-dasharray="3 3"/>
  <text x="290" y="45" font-size="12" fill="currentColor">包地</text>
  <text x="80" y="230" font-size="13" fill="currentColor">晶振靠近芯片，走线短，下面不走高速/电源。</text>
  <line x1="420" y1="120" x2="620" y2="120" stroke="currentColor" stroke-width="2"/>
  <line x1="420" y1="155" x2="620" y2="155" stroke="currentColor" stroke-width="2"/>
  <text x="500" y="105" font-size="12" fill="currentColor">D+</text>
  <text x="500" y="180" font-size="12" fill="currentColor">D−</text>
  <text x="420" y="215" font-size="13" fill="currentColor">USB 差分：等长、等距、同层、连续参考平面。</text>
</svg>
```

### 12.5 选型与降额：层数、铜厚、过孔

| 项目 | 2 层板 | 4 层板 | 说明 |
|---|---|---|---|
| 层数 | 顶层/底层 | 信号-地-电源-信号 | 4 层有完整参考平面 |
| 铜厚 | 1oz | 1～2oz | 大电流加铜 |
| 过孔 | 0.3/0.6mm | 0.2/0.45mm | 按板厂 |
| 线宽 | 6～8mil | 4～6mil | 高速/密集 |
| 阻抗控制 | 一般不做 | 需要时做 | USB/HDMI/DDR |

降额：

- 电源线按计算值再留 50% 余量。
- 过孔载流按 1A/0.3mm 钻孔估算，再留余量。
- 连接器/铜箔边缘留 0.5mm 以上。

### 12.6 测量与仿真：飞线走查与 DRC

#### 12.6.1 飞线走查

1. 布局完成，先不布线，看飞线。
2. 飞线是否“顺”？有没有长距离来回交叉？
3. 关键网络（电源、晶振、差分、复位）是否短？
4. 接口是否靠板边？测试点是否可及？
5. 调整布局，直到飞线“顺”再布线。

#### 12.6.2 DRC

- 间距、线宽、过孔、阻焊、丝印全部清零；
- 未布线网络为 0；
- 检查孤岛铜、天线铜、锐角。

#### 12.6.3 CircuitJS 观察开关环路

```circuitjs
power-buck
```

观察 SW 节点电流环路。PCB 上这条环路要最短，输入电容紧靠开关管和地。

#### 12.6.4 动手任务

- 给一块 2 层 LED 板做布局，用飞线走查法自检。
- 按 1A 电流算一条电源线宽。
- 完成布线、铺铜、DRC 清零，截图记录。

### 12.7 常见坑

1. **先布线后布局**：布线绕远、交叉，最后返工。
2. **去耦电容放远**：电源纹波压不下去。
3. **晶振不包地/走长线**：时钟被干扰。
4. **差分对不等长**：USB/HDMI 丢包。
5. **电源线太细**：大电流发热/掉压。
6. **过孔太多/太小**：载流不够、工艺做不出。
7. **铺铜不接 GND 或孤岛**：形成天线。
8. **直角/锐角走线**：高速/高压下尖端放电/阻抗突变。
9. **丝印压焊盘**：上锡不良。
10. **不留测试点**：调试时无法下探针。

### 12.8 本章复盘

#### 12.8.1 公式与规则表

| 公式/规则 | 用途 | 条件与注意 |
|---|---|---|
| 九步流程 | 设计顺序 | 布局前先想清楚 |
| 1oz 铜、10℃ 温升，1mm≈2～3A | 线宽估算 | 按 IPC/板厂复核 |
| 去耦电容紧靠电源脚 | 瞬态电流 | 回路短、过孔少 |
| 差分对等长/等距/同层 | 高速 | 长度差按协议要求 |
| 晶振包地、靠近芯片 | 时钟 | 下方不走高速 |

#### 12.8.2 术语表

| 术语 | 英文 | 一句话解释 |
|---|---|---|
| 布局 | placement | 摆器件位置 |
| 布线 | routing | 把网络连成铜线 |
| 飞线 | ratsnest | 未布线的连接提示 |
| 过孔 | via | 连接不同层的孔 |
| 铺铜 | copper pour | 大面积铜箔 |
| 回流 | return current | 电流返回源头的路径 |
| DRC | design rule check | 设计规则检查 |

#### 12.8.3 自测 10 题

1. PCB 九步流程是什么？
2. 布局六原则有哪些？
3. 飞线走查法看什么？
4. 1oz 铜、1mm 线宽大概能走多少电流？
5. 去耦电容为什么必须靠近电源脚？
6. 晶振布局要注意什么？
7. USB 差分对的三条基本要求？
8. 铺铜为什么要接 GND？
9. 直角走线有什么问题？
10. DRC 清零前还要检查什么？

#### 12.8.4 能力清单

- [ ] 能完成 2 层板布局并用飞线走查。
- [ ] 能按电流选线宽/过孔。
- [ ] 能处理去耦、晶振、差分三条关键规则。
- [ ] 能铺铜、DRC 清零。
- [ ] 能说出布局布线常见坑。

#### 12.8.5 下一章

下一章讲**电源模块与电源树**：板子上所有器件都要供电，电源布局是 PCB 布局里最不能妥协的一块。你会看到 LDO、Buck、Boost、电源树和热设计。
