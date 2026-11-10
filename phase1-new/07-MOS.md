# 第 07 章 · MOS 管

> **所属阶段**：阶段一 · 基础概念与七大元器件
> **前置课程**：第 01～06 章
> **本课难度**：⭐⭐⭐

> **建议用时：4～5 小时**
>
> 学完本章，你应该能：① 认出 N 沟道/ P 沟道 MOS 的 G、D、S；② 用 `VGS` 判断导通趋势；③ 理解 `VGS(th)` 不等于“完全导通”；④ 会算导通损耗、看 `RDS(on)` 条件；⑤ 能设计低边开关、理解高边驱动和体二极管。

---

## 7.1 它解决什么问题

### 场景一：大电流负载，三极管发热严重

用三极管驱动 12V/2A 的电机，假设 VCE(sat)=0.5V，功耗 `0.5×2=1W`，SOT-23 封装根本扛不住。换成导通电阻 20mΩ 的 NMOS，功耗 `2²×0.02=0.08W`，发热小得多。

这就是 MOS 在大电流开关里取代三极管的核心原因：**导通时压降可以很低**。

### 场景二：PWM 调光、调速

LED 调光、电机调速常用 PWM：开关快速通断，改变占空比。MOS 的开关速度可以很高，栅极驱动简单，适合高频 PWM。但频率越高，栅极充放电和开关损耗越不能忽略。

### 场景三：电源转换（Buck/Boost）

开关电源的功率级几乎都用 MOS 做开关。第 04 章 Buck 电路里的高边开关、低边开关，实际就是 MOS。理解 MOS 的导通电阻、栅极电荷、体二极管，才能看懂电源为什么发热、为什么需要驱动器。

### 本章在课程里的位置

第 06 章三极管是“电流控制”，本章 MOS 是“电压控制”。两者都能做开关，但 MOS 的栅极几乎不耗稳态电流，适合大电流；代价是栅极有电容，开关时要充放电，驱动设计更讲究。

---

## 7.2 它是什么

### 7.2.1 一句话定义

**MOSFET（Metal-Oxide-Semiconductor Field-Effect Transistor，金属-氧化物-半导体场效应晶体管）** 是三个端子的电压控制器件，用栅极-源极电压 `VGS` 控制漏极-源极之间沟道的导通程度。

三个端子：

- **栅极 G（Gate）**：控制端，和沟道之间有一层绝缘氧化层，稳态几乎不耗电流。
- **漏极 D（Drain）**：主电流端子。
- **源极 S（Source）**：主电流端子，通常低边开关接地。

原理图位号常用 **Q**。封装有 SOT-23、SOT-323、SO-8、DFN、TO-252、TO-220 等。**同封装不同型号的 G/D/S 顺序可能不同**，必须查完整料号。

### 7.2.2 N 沟道与 P 沟道

| 类型 | 导通条件（相对 S） | 常见位置 | 符号 |
|---|---|---|---|
| N 沟道 NMOS（增强型） | `VGS = VG − VS > 0`，足够大时导通 | 低边开关 | 箭头指向沟道（向里） |
| P 沟道 PMOS（增强型） | `VGS = VG − VS < 0`，足够负时导通 | 高边开关 | 箭头背离沟道（向外） |

> **术语解释：增强型**
> 增强型 MOS 在 `VGS=0` 时沟道是关断的，必须施加足够的正（NMOS）或负（PMOS）栅源电压才导通。与之相对的“耗尽型”在 0V 时已有沟道，入门阶段先掌握增强型。

**判断导通，永远看 `VGS`，不是看栅极对地电压。** 高边电路中，S 点电压会随负载变化，栅极对地 12V 不一定意味着 `VGS` 合适。

### 7.2.3 `VGS(th)` 不是“导通电压”

手册里的 `VGS(th)`（阈值电压）通常定义为：在规定的很小漏极电流（比如 250μA）下，使沟道开始形成的 `VGS`。它只说明“开始有一点点电流”，**不说明大电流下已经充分导通**。

真正决定导通电阻的是手册在具体 `VGS`、`ID`、温度下给出的 `RDS(on)`。例如某 NMOS 的 `VGS(th)` 最大 2.5V，但 `RDS(on)` 只在 `VGS=10V` 下保证 20mΩ；你用 3.3V 驱动，实际 `RDS(on)` 可能大很多，甚至发热失控。

**结论：3.3V GPIO 驱动 MOS，必须查 `VGS=3.3V`（或 2.5V/4.5V）下的 `RDS(on)`，不能只看阈值。**

### 7.2.4 体二极管

MOS 内部有一个寄生二极管，叫**体二极管**：

- N 沟道：二极管从 S 指向 D（阳极 S，阴极 D）。
- P 沟道：二极管从 D 指向 S（阳极 D，阴极 S）。

它平时反偏，不影响导通；但当 D-S 电压反向时，它会导通。所以 MOS 关断**不一定能阻断反向电流**。防反接、电池切换、同步 Buck 等电路必须考虑体二极管的方向和压降。

### 7.2.5 符号

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 620 260" role="img" aria-label="N沟道与P沟道增强型MOS符号，标注栅极G、漏极D、源极S">
<g fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round">
  <path d="M40 120 H95"/><path d="M95 78 V162"/>
  <path d="M122 78 V104 M122 112 V128 M122 136 V162"/>
  <path d="M122 92 H170 V48"/><path d="M122 148 H170 V192"/>
  <path d="M145 148 L127 148 L135 138" fill="currentColor"/>
  <path d="M300 120 H355"/><path d="M355 78 V162"/>
  <path d="M382 78 V104 M382 112 V128 M382 136 V162"/>
  <path d="M382 92 H430 V48"/><path d="M382 148 H430 V192"/>
  <path d="M407 148 L389 138 L389 158 Z" fill="currentColor"/>
</g>
<g fill="currentColor" font-family="sans-serif" font-size="16">
  <text x="28" y="108">G</text><text x="178" y="44">D</text><text x="178" y="212">S</text>
  <text x="288" y="108">G</text><text x="438" y="44">D</text><text x="438" y="212">S</text>
  <text x="86" y="240">N 沟道：箭头向里</text><text x="330" y="240">P 沟道：箭头向外</text>
</g></svg>
```

图 7-1 N 沟道与 P 沟道增强型 MOS 符号

符号里：G 是单独的栅极竖线；D 和 S 之间有三段沟道线；箭头表示沟道类型。实际器件的引脚号、体二极管方向、封装散热焊盘，都要查手册。

### 7.2.6 封装与散热

| 封装 | 常见功率 | 注意 |
|---|---|---|
| SOT-23 | 小信号、几百 mA | 散热能力很有限 |
| SOT-323 | 更小 | 功耗更低 |
| SO-8 | 中功率、双 MOS | 多引脚并联散热 |
| DFN 2×2 / 3×3 | 中功率、低高度 | 底部散热焊盘必须焊好 |
| TO-252 (DPAK) | 中功率 | 散热焊盘面积 |
| TO-220 | 较大功率 | 背板可能和 D 相连 |

**ID 额定值通常有测试条件**（如 `TC=25℃`、无限大散热面）。实际 PCB 上能连续跑多少电流，取决于铜皮面积、环境温度、封装热阻。不能只看“ID=10A”就以为能跑 10A。

---

## 7.3 关键参数与手册

### 7.3.1 一张表看懂 MOS 手册

| 参数 | 符号 | 含义 | 为什么重要 |
|---|---|---|---|
| 漏源耐压 | VDS | D-S 允许电压 | 电源、感性尖峰 |
| 栅源耐压 | VGS(max) | G-S 允许电压 | 驱动过压、静电 |
| 阈值电压 | VGS(th) | 开始导通的阈值 | 只作参考，不等于充分导通 |
| 导通电阻 | RDS(on) | 导通时 D-S 电阻 | 损耗、发热 |
| 漏极电流 | ID | 允许持续电流 | 负载、散热 |
| 脉冲电流 | IDM | 短时允许 | 启动、浪涌 |
| 栅极电荷 | Qg | 栅极充放电电荷 | 驱动电流、开关速度 |
| 输入电容 | Ciss | 栅极等效电容 | 驱动、振荡 |
| 输出电容 | Coss | D-S 电容 | 开关损耗、谐振 |
| 反向恢复电荷 | Qrr | 体二极管恢复 | 同步 Buck、桥式 |
| 安全工作区 | SOA | 允许 V-I 组合 | 线性/短路保护 |
| 热阻 | RθJA/RθJC | 散热能力 | 温升计算 |

### 7.3.2 读手册的四个关键点

**第一，RDS(on) 一定带 VGS 和 ID。** 手册可能给多行：`VGS=10V, ID=10A`、`VGS=4.5V, ID=5A`。你实际用 3.3V，就要找 3.3V 附近的数据或曲线；没有的话，不能保证。

**第二，RDS(on) 随温度升高。** 硅 MOS 的导通电阻通常是正温度系数，结温从 25℃ 升到 100℃，RDS(on) 可能增大 30%～50%。热设计要按热态算，不能按 25℃ 算。

**第三，Qg 决定驱动电流。** 开关频率 f、栅极电荷 Qg，驱动电流近似 `Ig = Qg × f`。比如 Qg=10nC、f=100kHz，`Ig=1mA`；如果 f=1MHz，`Ig=10mA`。驱动太弱，开关变慢，损耗增大。

**第四，SOA 不是“任何电压电流都能扛”。** 线性区同时有大电压和大电流，发热集中，容易热失控。开关应用要看开关损耗和热，不能拿 ID 额定值硬套。

### 7.3.3 MOS 的损耗构成

| 损耗 | 公式（近似） | 说明 |
|---|---|---|
| 导通损耗 | `Pcond = Irms² × RDS(on)` | 热态电阻 |
| 开关损耗 | `Psw ≈ 0.5 × VDS × ID × (tr+tf) × f` | 频率越高越大 |
| 栅极驱动损耗 | `Pgate = Qg × VGS × f` | 驱动电路承担 |
| 体二极管损耗 | `Pdiode = VF × IF × (1−D)` | 死区/续流 |
| 静态损耗 | 漏电 | 通常很小 |

**算例**：VDS=12V、ID=2A、RDS(on)=20mΩ（热态 30mΩ）、f=100kHz、tr+tf=100ns。

- 导通：`2²×0.03=0.12W`；
- 开关：`0.5×12×2×100e-9×100e3=0.12W`；
- 合计约 0.24W，SOT-23 可能勉强，SO-8 更稳。

如果 RDS(on) 按 25℃ 的 20mΩ 算，导通损耗只有 0.08W，会低估发热。**热态电阻是关键。**

---

## 7.4 五个典型电路

### 7.4.1 电路一：NMOS 低边开关

```svg
<svg role="img" aria-label="NMOS高边或低边开关电路，LED和限流电阻构成负载" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" xml:lang="en" height="276.34pt" width="244.10299999999998pt" viewBox="-67.375 -277.49999999999994 244.10299999999998 276.34"><polygon points="117,-175.5 108,-162.9 99,-175.5 " style="stroke:currentColor;fill:none;stroke-width:2.0;stroke-dasharray:-;stroke-linecap:round;stroke-linejoin:round;" /><path d="M 108.0,-54.0 L 108,-69 L 84,-69 L 84,-93 L 108,-93 L 108,-108" style="stroke:currentColor;fill:none;stroke-width:2.0;stroke-dasharray:-;stroke-linecap:round;stroke-linejoin:round;" /><path d="M 78.00000000000001,-69.0 L 78,-93" style="stroke:currentColor;fill:none;stroke-width:2.0;stroke-dasharray:-;stroke-linecap:round;stroke-linejoin:round;" /><path d="M 58.8,-81.0 L 78,-81" style="stroke:currentColor;fill:none;stroke-width:2.0;stroke-dasharray:-;stroke-linecap:round;stroke-linejoin:round;" /><path d="M 108.0,-108.0 L 108,-126 L 108,-144" style="stroke:currentColor;fill:none;stroke-width:2.0;stroke-dasharray:-;stroke-linecap:round;stroke-linejoin:round;" /><path d="M 108.0,-144.0 L 108,-162.9 M 117,-162.9 L 99,-162.9 M 108,-175.5 L 108,-194.4" style="stroke:currentColor;fill:none;stroke-width:2.0;stroke-dasharray:-;stroke-linecap:round;stroke-linejoin:round;" /><path d="M 85.0013506232961,-161.07220035616922 L 94.5,-166.5" style="stroke:currentColor;fill:none;stroke-width:2.0;stroke-dasharray:-;stroke-linecap:round;stroke-linejoin:round;" /><path d="M 80.486 -158.492 L 83.572 -163.573 L 86.43 -158.572 Z" style="stroke:currentColor;fill:currentColor;stroke-linecap:butt;stroke-linejoin:miter;" /><path d="M 85.0013506232961,-169.1722003561692 L 94.5,-174.6" style="stroke:currentColor;fill:none;stroke-width:2.0;stroke-dasharray:-;stroke-linecap:round;stroke-linejoin:round;" /><path d="M 80.486 -166.592 L 83.572 -171.673 L 86.43 -166.672 Z" style="stroke:currentColor;fill:currentColor;stroke-linecap:butt;stroke-linejoin:miter;" /><path d="M 108.0,-194.4 L 108,-205.2 L 99,-205.2 L 99,-241.2 L 117,-241.2 L 117,-205.2 L 108,-205.2 M 108,-241.2 L 108,-252" style="stroke:currentColor;fill:none;stroke-width:2.0;stroke-dasharray:-;stroke-linecap:round;stroke-linejoin:round;" /><path d="M 108.0,-54.0 L 108,-41.4 L 108,-28.8" style="stroke:currentColor;fill:none;stroke-width:2.0;stroke-dasharray:-;stroke-linecap:round;stroke-linejoin:round;" /><path d="M 108.0,-28.8 L 108,-14.4 L 99,-14.4 L 117,-14.4 M 101.7,-10.08 L 114.3,-10.08 M 106.2,-5.76 L 109.8,-5.76" style="stroke:currentColor;fill:none;stroke-width:2.0;stroke-dasharray:-;stroke-linecap:round;stroke-linejoin:round;" /><path d="M 58.8,-81.0 L 43.8,-81 L 28.8,-81" style="stroke:currentColor;fill:none;stroke-width:2.0;stroke-dasharray:-;stroke-linecap:round;stroke-linejoin:round;" /><path d="M 28.8,-81.0 L 18,-81 L 18,-72 L -18,-72 L -18,-90 L 18,-90 L 18,-81 M -18,-81 L -28.8,-81" style="stroke:currentColor;fill:none;stroke-width:2.0;stroke-dasharray:-;stroke-linecap:round;stroke-linejoin:round;" /><path d="M 28.8,-81.0 L 28.8,-72.9 L 37.8,-72.9 L 37.8,-36.9 L 19.8,-36.9 L 19.8,-72.9 L 28.8,-72.9 M 28.8,-36.9 L 28.8,-28.8" style="stroke:currentColor;fill:none;stroke-width:2.0;stroke-dasharray:-;stroke-linecap:round;stroke-linejoin:round;" /><path d="M 28.8,-28.8 L 28.8,-14.4 L 19.8,-14.4 L 37.8,-14.4 M 22.5,-10.08 L 35.1,-10.08 M 27,-5.76 L 30.6,-5.76" style="stroke:currentColor;fill:none;stroke-width:2.0;stroke-dasharray:-;stroke-linecap:round;stroke-linejoin:round;" /><text x="111.60000000000001" y="-94.0" dominant-baseline="central" fill="black" font-size="13" font-family="sans" text-anchor="start"><tspan x="111.60000000000001" dy="13">Q1 NMOS</tspan></text><text x="147.6" y="-135.39999999999998" dominant-baseline="central" fill="black" font-size="13" font-family="sans" text-anchor="middle"><tspan x="147.6" dy="13">D</tspan></text><text x="147.6" y="-59.800000000000004" dominant-baseline="central" fill="black" font-size="13" font-family="sans" text-anchor="middle"><tspan x="147.6" dy="13">S</tspan></text><text x="120.60000000000001" y="-182.20000000000002" dominant-baseline="central" fill="black" font-size="13" font-family="sans" text-anchor="start"><tspan x="120.60000000000001" dy="13">LED</tspan></text><text x="95.39999999999999" y="-236.20000000000002" dominant-baseline="central" fill="black" font-size="13" font-family="sans" text-anchor="end"><tspan x="95.39999999999999" dy="13">RLED</tspan></text><text x="104.39999999999999" y="-279.4" dominant-baseline="central" fill="black" font-size="13" font-family="sans" text-anchor="middle"><tspan x="104.39999999999999" dy="13">5V</tspan></text><text x="0.0" y="-106.60000000000001" dominant-baseline="ideographic" fill="black" font-size="13" font-family="sans" text-anchor="middle"><tspan x="0.0" dy="13">RG</tspan></text><text x="-54.0" y="-90.39999999999999" dominant-baseline="central" fill="black" font-size="13" font-family="sans" text-anchor="middle"><tspan x="-54.0" dy="13">控制端</tspan></text><text x="16.200000000000003" y="-67.9" dominant-baseline="central" fill="black" font-size="13" font-family="sans" text-anchor="end"><tspan x="16.200000000000003" dy="13">栅源下拉</tspan></text><circle cx="58.8" cy="-81" r="2.7" style="stroke:currentColor;fill:currentColor;stroke-width:2.0;stroke-dasharray:-;" /><text x="58.8" y="-87.7" dominant-baseline="hanging" fill="black" font-size="13" font-family="sans" text-anchor="middle"><tspan x="58.8" dy="13">G</tspan></text><circle cx="28.8" cy="-81" r="2.7" style="stroke:currentColor;fill:currentColor;stroke-width:2.0;stroke-dasharray:-;" /></svg>
```

图 7-2 NMOS 低边开关驱动负载

```text
5V ── 负载 ── D  Q1  S ── GND
GPIO ── RG ── G
               │
             RGS（下拉）
               │
              GND
```

**工作原理**：

- GPIO 低（0V）：`VGS=0−0=0V`，NMOS 关断，负载不工作。
- GPIO 高（3.3V）：`VGS=3.3V`，如果该器件在 3.3V 下 `RDS(on)` 足够低，NMOS 导通，负载得电。

**RG 的作用**：限制栅极充电峰值电流、抑制振荡；**RGS 的作用**：GPIO 高阻/复位时把栅极拉到 0V，保证关断。RG 太大会让开关变慢，增加开关损耗；RGS 一般 10kΩ～100kΩ，具体看速度要求。

**算例**：负载 1A、RDS(on)=30mΩ（热态），导通损耗 `1²×0.03=0.03W`；如果 RDS(on)=300mΩ（驱动不足），损耗 `0.3W`，发热明显。**同样的管子，驱动电压不够，RDS(on) 会大一个数量级。**

```circuitjs
nmos-switch
```

### 7.4.2 电路二：PMOS 高边开关

```svg
<svg role="img" aria-label="PMOS高边或低边开关电路，LED和限流电阻构成负载" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" xml:lang="en" height="287.14pt" width="244.10299999999998pt" viewBox="-67.375 -223.49999999999994 244.10299999999998 287.14"><circle cx="73.8" cy="-81" r="4.2" style="stroke:currentColor;fill:none;stroke-width:2.0;stroke-dasharray:-;" /><polygon points="117,2.7 108,15.3 99,2.7 " style="stroke:currentColor;fill:none;stroke-width:2.0;stroke-dasharray:-;stroke-linecap:round;stroke-linejoin:round;" /><path d="M 108.0,-54.0 L 108,-69 L 84,-69 L 84,-93 L 108,-93 L 108,-108" style="stroke:currentColor;fill:none;stroke-width:2.0;stroke-dasharray:-;stroke-linecap:round;stroke-linejoin:round;" /><path d="M 78.00000000000001,-69.0 L 78,-93" style="stroke:currentColor;fill:none;stroke-width:2.0;stroke-dasharray:-;stroke-linecap:round;stroke-linejoin:round;" /><path d="M 58.8,-81.0 L 69.6,-81" style="stroke:currentColor;fill:none;stroke-width:2.0;stroke-dasharray:-;stroke-linecap:round;stroke-linejoin:round;" /><path d="M 108.0,-108.0 L 108,-153 L 108,-198" style="stroke:currentColor;fill:none;stroke-width:2.0;stroke-dasharray:-;stroke-linecap:round;stroke-linejoin:round;" /><path d="M 108.0,-54.0 L 108,-63 L 108,-72" style="stroke:currentColor;fill:none;stroke-width:2.0;stroke-dasharray:-;stroke-linecap:round;stroke-linejoin:round;" /><path d="M 108.0,-72.0 L 108,-63 L 117,-63 L 117,-27 L 99,-27 L 99,-63 L 108,-63 M 108,-27 L 108,-18" style="stroke:currentColor;fill:none;stroke-width:2.0;stroke-dasharray:-;stroke-linecap:round;stroke-linejoin:round;" /><path d="M 108.0,-18.0 L 108,2.7 M 117,15.3 L 99,15.3 M 108,15.3 L 108,36" style="stroke:currentColor;fill:none;stroke-width:2.0;stroke-dasharray:-;stroke-linecap:round;stroke-linejoin:round;" /><path d="M 121.5,11.7 L 130.999,17.128" style="stroke:currentColor;fill:none;stroke-width:2.0;stroke-dasharray:-;stroke-linecap:round;stroke-linejoin:round;" /><path d="M 135.514 19.708 L 129.57 19.628 L 132.428 14.627 Z" style="stroke:currentColor;fill:currentColor;stroke-linecap:butt;stroke-linejoin:miter;" /><path d="M 121.5,3.599999999999999 L 130.999,9.028" style="stroke:currentColor;fill:none;stroke-width:2.0;stroke-dasharray:-;stroke-linecap:round;stroke-linejoin:round;" /><path d="M 135.514 11.608 L 129.57 11.528 L 132.428 6.527 Z" style="stroke:currentColor;fill:currentColor;stroke-linecap:butt;stroke-linejoin:miter;" /><path d="M 108.0,36.0 L 108,50.4 L 99,50.4 L 117,50.4 M 101.7,54.72 L 114.3,54.72 M 106.2,59.04 L 109.8,59.04" style="stroke:currentColor;fill:none;stroke-width:2.0;stroke-dasharray:-;stroke-linecap:round;stroke-linejoin:round;" /><path d="M 58.8,-81.0 L 43.8,-81 L 28.8,-81" style="stroke:currentColor;fill:none;stroke-width:2.0;stroke-dasharray:-;stroke-linecap:round;stroke-linejoin:round;" /><path d="M 28.8,-81.0 L 18,-81 L 18,-72 L -18,-72 L -18,-90 L 18,-90 L 18,-81 M -18,-81 L -28.8,-81" style="stroke:currentColor;fill:none;stroke-width:2.0;stroke-dasharray:-;stroke-linecap:round;stroke-linejoin:round;" /><path d="M 28.8,-81.0 L 28.8,-121.5 L 19.8,-121.5 L 19.8,-157.5 L 37.8,-157.5 L 37.8,-121.5 L 28.8,-121.5 M 28.8,-157.5 L 28.8,-198" style="stroke:currentColor;fill:none;stroke-width:2.0;stroke-dasharray:-;stroke-linecap:round;stroke-linejoin:round;" /><path d="M 28.8,-198.0 L 68.4,-198 L 108,-198" style="stroke:currentColor;fill:none;stroke-width:2.0;stroke-dasharray:-;stroke-linecap:round;stroke-linejoin:round;" /><text x="111.60000000000001" y="-94.0" dominant-baseline="central" fill="black" font-size="13" font-family="sans" text-anchor="start"><tspan x="111.60000000000001" dy="13">Q1 PMOS</tspan></text><text x="147.6" y="-135.39999999999998" dominant-baseline="central" fill="black" font-size="13" font-family="sans" text-anchor="middle"><tspan x="147.6" dy="13">S</tspan></text><text x="147.6" y="-59.800000000000004" dominant-baseline="central" fill="black" font-size="13" font-family="sans" text-anchor="middle"><tspan x="147.6" dy="13">D</tspan></text><text x="104.39999999999999" y="-225.39999999999998" dominant-baseline="central" fill="black" font-size="13" font-family="sans" text-anchor="middle"><tspan x="104.39999999999999" dy="13">5V</tspan></text><text x="95.39999999999999" y="-58.0" dominant-baseline="central" fill="black" font-size="13" font-family="sans" text-anchor="end"><tspan x="95.39999999999999" dy="13">RLED</tspan></text><text x="146.60999999999999" y="-4.0000000000000036" dominant-baseline="central" fill="black" font-size="13" font-family="sans" text-anchor="start"><tspan x="146.60999999999999" dy="13">LED</tspan></text><text x="0.0" y="-106.60000000000001" dominant-baseline="ideographic" fill="black" font-size="13" font-family="sans" text-anchor="middle"><tspan x="0.0" dy="13">RG</tspan></text><text x="-54.0" y="-90.39999999999999" dominant-baseline="central" fill="black" font-size="13" font-family="sans" text-anchor="middle"><tspan x="-54.0" dy="13">控制端</tspan></text><text x="16.200000000000006" y="-152.5" dominant-baseline="central" fill="black" font-size="13" font-family="sans" text-anchor="end"><tspan x="16.200000000000006" dy="13">栅源上拉</tspan></text><circle cx="58.8" cy="-81" r="2.7" style="stroke:currentColor;fill:currentColor;stroke-width:2.0;stroke-dasharray:-;" /><text x="58.8" y="-87.7" dominant-baseline="hanging" fill="black" font-size="13" font-family="sans" text-anchor="middle"><tspan x="58.8" dy="13">G</tspan></text><circle cx="28.8" cy="-81" r="2.7" style="stroke:currentColor;fill:currentColor;stroke-width:2.0;stroke-dasharray:-;" /></svg>
```

图 7-3 PMOS 高边开关驱动负载

```text
5V ── S  Q2  D ── 负载 ── GND
       G ── RG ── 控制/驱动
       │
      RGS（上拉）
       │
      5V
```

**工作原理**：S 接 5V，G 被拉到 0V 时 `VGS=−5V`，PMOS 导通；G 被上拉到 5V 时 `VGS=0V`，PMOS 关断。

**3.3V GPIO 直接控制 5V 高边 PMOS 的问题**：

- GPIO 高 3.3V：`VGS=3.3−5=−1.7V`，可能仍导通，关不死；
- GPIO 低 0V：`VGS=−5V`，导通，但栅极电流/电压要核；
- GPIO 引脚可能承受 5V。

所以 3.3V 控制 5V 高边 PMOS，通常需要 NPN/ NMOS 电平转换或专用高边驱动。不能直接连。

```circuitjs
pmos-switch
```

### 7.4.3 电路三：NMOS 高边开关（需要自举/驱动）

N 沟道 MOS 的导通电阻通常比 P 沟道低，但高边使用时 S 点电压接近电源，要 `VGS > VGS(th)` 就必须让 G 比 S 更高，甚至高于电源。这就需要**自举电路**或专用高边驱动芯片。

零基础阶段先理解：**NMOS 低边好用，高边难驱动；PMOS 高边好驱动，但 RDS(on) 通常较大、成本较高。** 实际选型要权衡。

### 7.4.4 电路四：MOS 作为负载开关

```text
VBUS ── S  Q1  D ── 负载
EN ── RG ── G
             │
           RGS ── GND
```

这是低边控制的负载开关：EN 高时导通，负载得电；EN 低时关断。要加**软启动**（栅极电容、RC 缓升）限制开机浪涌，否则大电容负载会让 MOS 承受很大冲击。

### 7.4.5 电路五：同步 Buck 的低边 MOS

第 04 章 Buck 电路里，续流二极管可以用 MOS 代替，叫**同步整流**。低边 MOS 在死区时靠体二极管续流，死区结束后沟道导通，压降更小、效率更高。

**注意**：同步 Buck 要设计死区时间，防止高边和低边同时导通（直通）；还要考虑体二极管反向恢复、开关节点振铃。零基础阶段理解概念即可，实际设计用控制器手册的参考电路。

---

## 7.5 选型与降额

### 7.5.1 按用途选类型

| 用途 | 首选 | 备选 | 避免 |
|---|---|---|---|
| 低边小电流开关 | NMOS（AO3400 等） | NPN | PMOS（低边不方便） |
| 低边大电流 | NMOS，低 RDS(on) | 多管并联 | 小封装 |
| 高边小电流 | PMOS | 专用高边开关 | NMOS（驱动复杂） |
| 高边大电流 | NMOS + 高边驱动 | 专用智能开关 | PMOS（RDS(on) 大） |
| 电源入口防反接 | PMOS 低边/理想二极管 | NMOS + 电荷泵 | 普通二极管（压降大） |
| 高频开关 | 低 Qg、低 Coss | — | 大 Qg 功率管 |
| 线性/恒流 | 查 SOA | — | 开关管硬套 |

### 7.5.2 降额参考

| 参数 | 建议 | 说明 |
|---|---|---|
| VDS | 实际 ≤80% 额定 | 感性尖峰单独核 |
| VGS | 不超过 ±20V 常见上限 | 具体看手册，有些更低 |
| ID | 实际 ≤70～80% 额定（按温度） | 散热条件 |
| RDS(on) | 按热态、实际 VGS | 不能按 25℃ |
| Qg | 驱动能力足够 | 频率高时重点 |
| Tj | 留 20～30℃ | 热阻、铜皮 |
| SOA | 线性/短路要核 | 开关应用也看瞬态 |

### 7.5.3 选型 9 步

1. 定拓扑：低边/高边/半桥/负载开关。
2. 定 VDS：电源电压 + 尖峰余量。
3. 定电流：平均、峰值、浪涌。
4. 定驱动电压：3.3V/5V/10V，查对应 RDS(on)。
5. 算导通损耗，查热阻和温升。
6. 算开关损耗，查 Qg、tr/tf。
7. 查体二极管方向、Qrr。
8. 查封装、散热焊盘、引脚。
9. 写完整料号，核对供货、温度等级。

---

## 7.6 测量与仿真

### 7.6.1 万用表测 MOS

断电、放电后：

- 测 G-S、G-D、D-S 之间是否短路；
- 体二极管可能让 D-S 单向有读数，不能据此判断坏；
- 栅极电容会让读数缓慢变化；
- 在板测量受并联器件影响。

**静电**：MOS 栅极氧化层很薄，手摸可能击穿。拿器件先接地，焊接时用防静电烙铁/手环。

### 7.6.2 测开关状态

上电后测：

- `VGS`：导通时应明显大于 `VGS(th)`，具体看驱动设计；
- `VDS`：导通时应接近 `I×RDS(on)`，如果很大，说明驱动不足或没导通；
- 栅极波形：用示波器看上升/下降时间、振铃、米勒平台。

**注意**：示波器探头地线夹可能短路，测高边栅极要用差分探头或隔离。

### 7.6.3 仿真记录表

| 仿真 | 改什么 | 预期 | 实际 |
|---|---|---|---|
| nmos-switch | 改栅极电压 | VDS 变 | |
| pmos-switch | 改控制电平 | 是否关断 | |

### 7.6.4 动手任务

1. 用 AO3400 驱动 5V 小电机，测 `VGS`、`VDS`，算导通损耗。
2. 把栅极电阻从 100Ω 改成 10kΩ，观察开关波形变慢。
3. 用 PMOS 做 5V 高边开关，用 3.3V GPIO 直接驱动，测关断时输出是否还有电压，解释原因。
4. 查一只 MOS 的 `RDS(on)` 在 3.3V 和 10V 下的差别。

---

## 7.7 常见坑

### 坑 1：只看 VGS(th)，不看 RDS(on)

`VGS(th)=2V` 不代表 3.3V 就能充分导通。必须查实际 `VGS` 下的 `RDS(on)`。

### 坑 2：栅极悬空

GPIO 高阻、复位、上电瞬间，栅极可能被干扰，MOS 误导通。加 `RGS` 下拉/上拉，保证默认关断。

### 坑 3：高边 NMOS 直接用 GPIO

NMOS 高边需要 `VGS` 高于源极，GPIO 3.3V 根本不够，必须自举/高边驱动。

### 坑 4：忽略体二极管

MOS 关断不阻断反向电流，防反接、电池切换可能倒灌。要查体二极管方向。

### 坑 5：ID 额定值当实际能力

ID 是在特定散热条件下测的，SOT-23 实际可能只能跑 1A 左右。按热阻算。

### 坑 6：栅极电阻太大/太小

太大：开关慢、损耗大、可能振荡；太小：驱动峰值电流大、振铃。按 Qg 和频率选。

### 坑 7：忘记散热焊盘

DFN/SO-8 的散热焊盘不焊，热阻大幅上升，实际电流能力骤降。

### 坑 8：静电损坏

手摸栅极可能击穿氧化层。防静电措施不能省。

### 坑 9：同步 Buck 直通

高边/低边同时导通，电源短路，瞬间大电流。死区时间必须由控制器保证。

---

## 7.8 本章复盘

### 7.8.1 公式表

| 公式 | 用途 | 条件 |
|---|---|---|
| `VGS = VG − VS` | 判断导通 | 永远相对 S |
| `Pcond = Irms² × RDS(on)` | 导通损耗 | 热态电阻 |
| `Psw ≈ 0.5 × VDS × ID × (tr+tf) × f` | 开关损耗 | 近似 |
| `Ig ≈ Qg × f` | 平均驱动电流 | 开关频率 |
| `Tj ≈ Ta + P × RθJA` | 结温 | 热阻 |
| `RDS(on)@Tj ≈ RDS(on)@25 × (1+α(Tj−25))` | 热态电阻 | α 查曲线 |

### 7.8.2 术语表

| 术语 | 解释 |
|---|---|
| MOSFET | 金属-氧化物-半导体场效应管 |
| G/D/S | 栅极/漏极/源极 |
| NMOS | N 沟道，正 VGS 导通 |
| PMOS | P 沟道，负 VGS 导通 |
| VGS(th) | 阈值电压，开始导通 |
| RDS(on) | 导通电阻 |
| Qg | 栅极电荷 |
| Ciss | 输入电容 |
| 体二极管 | 内部寄生二极管 |
| SOA | 安全工作区 |
| 同步整流 | 用 MOS 代替续流二极管 |

### 7.8.3 自测 10 题

1. NMOS 的导通条件是什么？
2. PMOS 的导通条件是什么？
3. `VGS(th)=2V` 是否说明 3.3V 就能充分导通？
4. RDS(on)=20mΩ、2A，导通损耗多少？
5. 为什么高边 NMOS 难驱动？
6. 体二极管的方向是什么？
7. 栅极下拉电阻的作用？
8. Qg=20nC、f=200kHz，平均驱动电流约多少？
9. 为什么 ID 额定值不能直接当实际电流？
10. 同步 Buck 的死区时间有什么用？

<details>
<summary>参考答案</summary>

1. `VGS > 0` 且足够大（增强型）。
2. `VGS < 0` 且足够负。
3. 不一定，必须查 3.3V 下的 RDS(on)。
4. `2²×0.02=0.08W`。
5. S 点接近电源，需要 G 比 S 更高，要自举/高边驱动。
6. NMOS：S→D；PMOS：D→S。
7. 保证 GPIO 高阻/复位时关断。
8. `20nC×200kHz=4mA`。
9. ID 有散热/温度测试条件，实际受封装和铜皮限制。
10. 防止高边/低边同时导通直通。

</details>

### 7.8.4 能力清单

- [ ] 能分清 NMOS/PMOS 和 G/D/S。
- [ ] 能用 VGS 判断导通趋势。
- [ ] 知道 VGS(th) 和 RDS(on) 的区别。
- [ ] 会算导通损耗和温升。
- [ ] 能设计低边开关，理解高边驱动。
- [ ] 知道体二极管、Qg、SOA 的影响。

### 7.8.5 下一章

下一章讲**运算放大器**：它是模拟电路的核心，能把微弱信号放大、缓冲、滤波、比较。你会看到“虚短”“虚断”这两个看似神奇的分析方法，以及它们成立的条件。

---

<!-- 第 07 章完 -->
