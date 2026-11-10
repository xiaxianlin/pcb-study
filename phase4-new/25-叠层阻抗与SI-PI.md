# 第 25 章 · 叠层、阻抗与 SI/PI 基础

> **所属阶段**：阶段四 · 多层板与高速设计
> **前置课程**：第 24 章 存储与 DDR 基础
> **本课难度**：⭐⭐⭐⭐

## 本章目标

学完本章，你应该能够：

1. 画出 4 层/6 层/8 层典型叠层，并说清每层作用。
2. 计算微带线/带状线的特征阻抗，理解线宽/介质/参考面关系。
3. 区分 SI（信号完整性）与 PI（电源完整性）。
4. 解释反射、串扰、地弹、回流路径的物理原因。
5. 给 USB/HDMI/DDR 设阻抗目标，并与板厂沟通。
6. 用 TDR/眼图/仿真判断通道好坏。
7. 说出至少 8 个叠层/阻抗设计常见坑。

高速不是“跑得快”，是“波形到接收端还认得出来”。叠层和阻抗，是让波形不变形的物理基础。

## 正文

### 25.1 它解决什么问题：三个真实场景

#### 场景一：4 层板叠层错，USB 阻抗做不出来

板厂按“信号-信号-地-电源”做，USB 差分没有连续参考面，阻抗偏离 90Ω，眼图闭合。叠层要“信号-地-电源-信号”，关键信号有地参考。

#### 场景二：线宽按“经验”设，阻抗差 20%

USB 差分按 6/6mil 画，板厂算出 110Ω。没做阻抗控制，也没给板厂目标，最后靠“能枚举”过关。高速线要按叠层算线宽/间距。

#### 场景三：电源平面谐振，板子某频点噪声大

电源/地平面像一块“板”，在特定频率谐振。去耦电容 placement 不对，谐振点噪声放大。PI 要看平面+电容的阻抗曲线。

### 25.2 它是什么：叠层是“地-信号-电源”的排序

典型叠层：

| 层数 | 叠层 | 特点 |
|---|---|---|
| 2 层 | 信号/地（底层铺铜） | 便宜，参考不完整 |
| 4 层 | 信号-地-电源-信号 | 性价比高，有完整参考 |
| 6 层 | 信号-地-信号-电源-地-信号 | 高速/双参考 |
| 8 层 | 信号-地-信号-电源-地-信号-地-信号 | 高速/多层 |

阻抗：

- **微带线**（microstrip）：外层，一边是空气，一边是介质。
- **带状线**（stripline）：内层，上下都是介质/参考面。

近似公式（微带，粗略）：

`Z0 ≈ 87 / sqrt(εr + 1.41) × ln(5.98h / (0.8w + t))`

其中 h 介质厚度，w 线宽，t 铜厚。工程上用板厂/阻抗计算器，不手算投产。

> **术语第一次出现**：SI（Signal Integrity，信号完整性）关心“信号波形是否失真”；PI（Power Integrity，电源完整性）关心“电源/地是否稳定”。两者通过回流路径耦合在一起。

### 25.3 关键参数与手册

| 参数 | 含义 | 设计影响 |
|---|---|---|
| εr | 介质介电常数 | 阻抗/传播速度 |
| h | 介质厚度 | 阻抗 |
| w/t | 线宽/铜厚 | 阻抗 |
| Z0 | 特征阻抗 | 匹配 |
| 传播延迟 | ps/inch | 等长 |
| 平面电容 | 电源-地 | PI |
| 谐振 | 平面谐振 | EMI |

### 25.4 三个典型叠层与结构

#### 25.4.1 4 层叠层

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 340">
  <text x="20" y="30" font-size="16" fill="currentColor">图 25-1：4 层板典型叠层</text>
  <rect x="100" y="60" width="420" height="40" fill="none" stroke="currentColor" stroke-width="1.5"/>
  <text x="110" y="85" font-size="12" fill="currentColor">L1 信号/器件</text>
  <rect x="100" y="100" width="420" height="40" fill="none" stroke="currentColor" stroke-width="1.5"/>
  <text x="110" y="125" font-size="12" fill="currentColor">L2 地平面</text>
  <rect x="100" y="140" width="420" height="40" fill="none" stroke="currentColor" stroke-width="1.5"/>
  <text x="110" y="165" font-size="12" fill="currentColor">L3 电源平面</text>
  <rect x="100" y="180" width="420" height="40" fill="none" stroke="currentColor" stroke-width="1.5"/>
  <text x="110" y="205" font-size="12" fill="currentColor">L4 信号/地</text>
  <text x="100" y="260" font-size="13" fill="currentColor">关键信号走 L1，参考 L2；L4 走低速/电源。</text>
  <text x="100" y="285" font-size="13" fill="currentColor">L2/L3 完整，避免被过孔/走线切碎。</text>
</svg>
```

#### 25.4.2 微带/带状线

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 320">
  <text x="20" y="30" font-size="16" fill="currentColor">图 25-2：微带线与带状线</text>
  <rect x="60" y="70" width="240" height="40" fill="none" stroke="currentColor" stroke-width="1.5"/>
  <text x="75" y="95" font-size="12" fill="currentColor">微带线：线在表面</text>
  <line x1="80" y1="130" x2="280" y2="130" stroke="currentColor" stroke-width="6"/>
  <rect x="60" y="150" width="240" height="30" fill="none" stroke="currentColor" stroke-width="1.5"/>
  <text x="75" y="170" font-size="11" fill="currentColor">介质</text>
  <rect x="60" y="180" width="240" height="25" fill="none" stroke="currentColor" stroke-width="1.5"/>
  <text x="75" y="197" font-size="11" fill="currentColor">参考地</text>
  <rect x="400" y="70" width="260" height="30" fill="none" stroke="currentColor" stroke-width="1.5"/>
  <text x="415" y="90" font-size="11" fill="currentColor">参考地</text>
  <rect x="400" y="100" width="260" height="35" fill="none" stroke="currentColor" stroke-width="1.5"/>
  <text x="415" y="122" font-size="11" fill="currentColor">介质</text>
  <line x1="420" y1="150" x2="640" y2="150" stroke="currentColor" stroke-width="6"/>
  <rect x="400" y="160" width="260" height="35" fill="none" stroke="currentColor" stroke-width="1.5"/>
  <text x="415" y="182" font-size="11" fill="currentColor">介质</text>
  <rect x="400" y="195" width="260" height="25" fill="none" stroke="currentColor" stroke-width="1.5"/>
  <text x="415" y="212" font-size="11" fill="currentColor">参考地</text>
  <text x="60" y="270" font-size="13" fill="currentColor">微带：一边空气；带状：上下介质，阻抗更稳。</text>
</svg>
```

#### 25.4.3 回流路径

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 300">
  <text x="20" y="30" font-size="16" fill="currentColor">图 25-3：信号回流路径</text>
  <rect x="60" y="70" width="580" height="30" fill="none" stroke="currentColor" stroke-width="1.5"/>
  <text x="75" y="90" font-size="11" fill="currentColor">信号线</text>
  <rect x="60" y="170" width="580" height="30" fill="none" stroke="currentColor" stroke-width="1.5"/>
  <text x="75" y="190" font-size="11" fill="currentColor">地平面</text>
  <line x1="120" y1="100" x2="120" y2="170" stroke="currentColor" stroke-width="2"/>
  <line x1="120" y1="170" x2="120" y2="200" stroke="currentColor" stroke-width="2"/>
  <line x1="580" y1="100" x2="580" y2="170" stroke="currentColor" stroke-width="2"/>
  <line x1="580" y1="170" x2="580" y2="200" stroke="currentColor" stroke-width="2"/>
  <text x="60" y="245" font-size="13" fill="currentColor">回流走最近的地平面；跨分割时回流绕远，形成环路/辐射。</text>
</svg>
```

### 25.5 选型与降额

| 项目 | 目标 | 说明 |
|---|---|---|
| USB2.0 | 90Ω 差分 | 板厂阻抗控制 |
| HDMI | 100Ω 差分 | 4 对 |
| DDR | 按手册 | 单端/差分 |
| 叠层 | 4/6/8 层 | 按速率/成本 |
| 介质 | FR-4/高速材料 | 按损耗 |
| 铜厚 | 1oz/0.5oz | 细线用 0.5oz |

### 25.6 测量与仿真

#### 25.6.1 阻抗验证

1. 给板厂叠层+阻抗目标。
2. 板厂回传阻抗报告。
3. 用 TDR 测样板（有条件）。
4. 眼图/误码测试。

#### 25.6.2 CircuitJS

```circuitjs
rc-lowpass-159
```

用 RC 低通理解“上升沿变慢/带宽限制”。

#### 25.6.3 动手任务

- 画一个 4 层叠层，标出参考面。
- 用阻抗计算器算 90Ω 差分线宽/间距。
- 找一条跨分割的线，改布局。
- 读一份板厂阻抗报告。

### 25.7 常见坑

1. **叠层没有完整参考面**：阻抗不稳。
2. **线宽凭经验**：阻抗偏。
3. **差分线不按叠层算**：90Ω 变 110Ω。
4. **参考面被切碎**：回流绕远。
5. **过孔 stub 太长**：高速反射。
6. **介质厚度不均**：阻抗批次差异。
7. **电源平面谐振**：PI 噪声。
8. **不做 TDR/眼图**：问题到现场。
9. **板厂没做阻抗控制**：报告对不上。

### 25.8 本章复盘

#### 25.8.1 公式与规则表

| 公式/规则 | 用途 | 条件与注意 |
|---|---|---|
| 微带 Z0 近似 | 估算 | 最终用板厂 |
| 差分 90/100Ω | USB/HDMI | 按叠层 |
| 参考面连续 | 回流 | 不跨分割 |
| 4 层：信号-地-电源-信号 | 性价比 | 关键信号参考地 |
| 阻抗报告 | 验证 | 板厂回传 |

#### 25.8.2 术语表

| 术语 | 英文 | 一句话解释 |
|---|---|---|
| SI | signal integrity | 信号完整性 |
| PI | power integrity | 电源完整性 |
| 微带 | microstrip | 表面线 |
| 带状 | stripline | 内层线 |
| TDR | time domain reflectometry | 时域反射 |
| 眼图 | eye diagram | 信号质量图 |

#### 25.8.3 自测 10 题

1. 4 层典型叠层？
2. 微带和带状线区别？
3. 特征阻抗由什么决定？
4. SI 和 PI 分别关心什么？
5. 回流为什么走最近地？
6. 跨分割有什么后果？
7. USB 差分阻抗多少？
8. 阻抗报告怎么用？
9. 过孔 stub 有什么影响？
10. 4/6/8 层怎么选？

#### 25.8.4 能力清单

- [ ] 能画 4/6/8 层叠层。
- [ ] 能算/查微带/带状阻抗。
- [ ] 能解释反射/串扰/回流。
- [ ] 能给板厂阻抗目标并读报告。
- [ ] 能用 TDR/眼图验证。

#### 25.8.5 下一章

下一章讲**EMC/ESD 与防护设计**：高速板不仅要“自己跑得稳”，还要“不干扰别人、不被别人干扰”。
