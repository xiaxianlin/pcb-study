# 第 26 章 · EMC/ESD 与防护设计

> **所属阶段**：阶段四 · 多层板与高速设计
> **前置课程**：第 25 章 叠层、阻抗与 SI/PI 基础
> **本课难度**：⭐⭐⭐⭐

## 本章目标

学完本章，你应该能够：

1. 区分 EMI（发射）与 EMS（抗扰），理解 EMC = 两者之和。
2. 说清辐射/传导的常见耦合路径，以及板级抑制手段。
3. 设计接口 ESD、电源浪涌、信号滤波的保护链。
4. 处理屏蔽、接地、电缆、缝隙、共模电流。
5. 做一次 EMC 预测试（近场探头/频谱仪）并定位噪声源。
6. 区分“过认证”和“现场稳定”的差别。
7. 说出至少 8 个 EMC 设计常见坑。

EMC 不是“加个磁珠”，是“从源头减小、从路径阻断、从敏感体加固”。板级 EMC 做不好，认证要整改，现场还会死机。

## 正文

### 26.1 它解决什么问题：三个真实场景

#### 场景一：DC-DC 辐射超标，30～100MHz 包络

Buck 的 SW 节点/输入环路大，辐射发射超标。改布局（输入电容紧靠、SW 短粗）、加 snubber/屏蔽，辐射下降。

#### 场景二：RS485 现场通信，雷击/浪涌打坏收发器

接口只加了普通 TVS，浪涌能量太大，TVS 失效。要加气体放电管/压敏+TVS 两级，配合隔离。

#### 场景三：塑料外壳缝隙漏辐射

板子本身辐射不大，但外壳缝隙像“天线”，特定频率泄漏。屏蔽要连续，缝隙长度小于最高频率波长 1/20。

### 26.2 它是什么：EMC 的三要素

EMC（Electromagnetic Compatibility，电磁兼容）= EMI（发射）+ EMS（抗扰）。

三要素：

- **源**：开关电源、时钟、高速总线、继电器。
- **路径**：传导（线缆/电源）、辐射（空间）、耦合（电容/电感）。
- **敏感体**：MCU、ADC、通信、传感器。

> **术语第一次出现**：共模电流（common-mode current）是两根线/地之间同向流动的电流，是电缆辐射的主因。差模是两根线反向流动。

### 26.3 关键参数与标准

| 项目 | 典型要求 | 说明 |
|---|---|---|
| 辐射发射 | CISPR 32/EN 55032 | 30MHz～1GHz |
| 传导发射 | CISPR 32 | 150kHz～30MHz |
| ESD 抗扰 | IEC 61000-4-2 | ±4/8kV |
| 浪涌 | IEC 61000-4-5 | 1/2kV |
| 群脉冲 | IEC 61000-4-4 | 1/2kV |
| 电压跌落 | IEC 61000-4-11 | 按产品 |

### 26.4 三个典型防护

#### 26.4.1 接口 ESD/浪涌两级

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 320">
  <text x="20" y="30" font-size="16" fill="currentColor">图 26-1：接口两级防护：GDT/压敏 + TVS</text>
  <rect x="40" y="80" width="100" height="70" rx="6" fill="none" stroke="currentColor" stroke-width="1.5"/>
  <text x="55" y="115" font-size="12" fill="currentColor">接口</text>
  <rect x="180" y="80" width="110" height="70" rx="6" fill="none" stroke="currentColor" stroke-width="1.5"/>
  <text x="195" y="110" font-size="11" fill="currentColor">GDT/压敏</text>
  <text x="195" y="130" font-size="10" fill="currentColor">大能量</text>
  <rect x="330" y="80" width="100" height="70" rx="6" fill="none" stroke="currentColor" stroke-width="1.5"/>
  <text x="345" y="110" font-size="11" fill="currentColor">TVS</text>
  <text x="345" y="130" font-size="10" fill="currentColor">钳位</text>
  <rect x="470" y="80" width="100" height="70" rx="6" fill="none" stroke="currentColor" stroke-width="1.5"/>
  <text x="485" y="110" font-size="11" fill="currentColor">滤波</text>
  <rect x="610" y="80" width="80" height="70" rx="6" fill="none" stroke="currentColor" stroke-width="1.5"/>
  <text x="625" y="115" font-size="11" fill="currentColor">芯片</text>
  <line x1="140" y1="115" x2="180" y2="115" stroke="currentColor" stroke-width="2"/>
  <line x1="290" y1="115" x2="330" y2="115" stroke="currentColor" stroke-width="2"/>
  <line x1="430" y1="115" x2="470" y2="115" stroke="currentColor" stroke-width="2"/>
  <line x1="570" y1="115" x2="610" y2="115" stroke="currentColor" stroke-width="2"/>
  <text x="40" y="220" font-size="13" fill="currentColor">大能量先泄放，再钳位，再滤波；器件越靠接口越好。</text>
</svg>
```

#### 26.4.2 屏蔽与缝隙

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 280">
  <text x="20" y="30" font-size="16" fill="currentColor">图 26-2：外壳缝隙与波长</text>
  <rect x="80" y="70" width="260" height="120" fill="none" stroke="currentColor" stroke-width="2"/>
  <line x1="200" y1="70" x2="200" y2="190" stroke="currentColor" stroke-width="6"/>
  <text x="100" y="215" font-size="12" fill="currentColor">缝隙长度 &lt; λ/20</text>
  <text x="400" y="100" font-size="13" fill="currentColor">缝隙像天线，长度接近 λ/2 时辐射最强；</text>
  <text x="400" y="125" font-size="13" fill="currentColor">用弹片/导电泡棉/多点螺钉缩短缝隙。</text>
</svg>
```

#### 26.4.3 共模与滤波

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 300">
  <text x="20" y="30" font-size="16" fill="currentColor">图 26-3：共模电感与 Y 电容</text>
  <text x="40" y="95" font-size="13" fill="currentColor">线缆</text>
  <line x1="100" y1="90" x2="220" y2="90" stroke="currentColor" stroke-width="2"/>
  <line x1="100" y1="120" x2="220" y2="120" stroke="currentColor" stroke-width="2"/>
  <rect x="220" y="70" width="100" height="70" fill="none" stroke="currentColor" stroke-width="2"/>
  <text x="235" y="100" font-size="11" fill="currentColor">共模</text>
  <text x="235" y="120" font-size="11" fill="currentColor">电感</text>
  <line x1="320" y1="90" x2="440" y2="90" stroke="currentColor" stroke-width="2"/>
  <line x1="320" y1="120" x2="440" y2="120" stroke="currentColor" stroke-width="2"/>
  <line x1="380" y1="105" x2="380" y2="160" stroke="currentColor" stroke-width="2"/>
  <line x1="360" y1="160" x2="400" y2="160" stroke="currentColor" stroke-width="2"/>
  <text x="410" y="165" font-size="11" fill="currentColor">Y 电容</text>
  <text x="440" y="100" font-size="12" fill="currentColor">到板内</text>
  <text x="40" y="220" font-size="13" fill="currentColor">共模电感抑制同向电流；Y 电容给共模电流提供回流。</text>
</svg>
```

### 26.5 选型与降额

| 场景 | 方案 | 注意 |
|---|---|---|
| 电源入口 | 压敏+TVS+共模+滤波 | 两级配合 |
| 高速接口 | 低电容 ESD | 不影响信号 |
| 继电器/电机 | 续流+RC/压敏 | 触点/线圈 |
| 电缆 | 屏蔽/双绞/共模 | 接地 |
| 外壳 | 导电涂层/弹片 | 缝隙 |

### 26.6 测量与仿真

#### 26.6.1 预测试

1. 近场探头扫板子，找噪声源。
2. 频谱仪看辐射包络。
3. 拔线/加磁环，判断传导/辐射。
4. 改布局/加滤波，复测。

#### 26.6.2 CircuitJS

```circuitjs
inductkick-snub
```

观察续流/吸收对开关反峰的影响。

#### 26.6.3 动手任务

- 用近场探头扫一块 Buck 板，找最强点。
- 给 RS485 画两级防护。
- 给电源入口画共模+Y 电容。
- 写一页 EMC 整改记录。

### 26.7 常见坑

1. **只加 TVS 不分级**：大能量打坏。
2. **ESD 器件放远**：保护不到芯片。
3. **高速线用大电容**：信号失真。
4. **屏蔽缝隙太长**：泄漏。
5. **共模电感方向错**：无效。
6. **Y 电容位置错**：共模无回流。
7. **继电器无续流**：触点/驱动损坏。
8. **只在实验室过认证**：现场线缆/接地不同。
9. **忽略电缆辐射**：板子好，整机不过。

### 26.8 本章复盘

#### 26.8.1 公式与规则表

| 公式/规则 | 用途 | 条件与注意 |
|---|---|---|
| EMC=EMI+EMS | 概念 | 发射+抗扰 |
| 缝隙 &lt; λ/20 | 屏蔽 | 最高频率 |
| 两级防护 | 浪涌 | 大能量+钳位 |
| 共模电感+Y 电容 | 电缆 | 共模回流 |
| 近场探头 | 定位 | 噪声源 |

#### 26.8.2 术语表

| 术语 | 英文 | 一句话解释 |
|---|---|---|
| EMC | electromagnetic compatibility | 电磁兼容 |
| EMI | electromagnetic interference | 电磁发射 |
| EMS | electromagnetic susceptibility | 电磁抗扰 |
| 共模 | common mode | 同向电流 |
| GDT | gas discharge tube | 气体放电管 |
| Y 电容 | Y-capacitor | 跨接地的安规电容 |

#### 26.8.3 自测 10 题

1. EMC/EMI/EMS 关系？
2. EMC 三要素？
3. 共模和差模区别？
4. 两级防护怎么配？
5. 缝隙为什么用 λ/20？
6. 共模电感作用？
7. Y 电容作用？
8. 近场探头怎么用？
9. 为什么实验室过认证现场还死机？
10. 继电器为什么要续流？

#### 26.8.4 能力清单

- [ ] 能解释 EMC 三要素。
- [ ] 能设计接口两级防护。
- [ ] 能处理屏蔽/缝隙/共模。
- [ ] 能用近场探头定位噪声。
- [ ] 能写整改记录。

#### 26.8.5 下一章

下一章讲**DFM、拼板与生产成本**：设计要能做得出来、做得便宜。
