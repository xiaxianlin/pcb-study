# 第 31 章 · 消费电子维修与 BGA 返修（选学）

> **所属阶段**：阶段五 · 维修、就业与持续进阶
> **前置课程**：第 10 章 焊接与返修基础、第 20 章 首板上电与 Bring-Up
> **本课难度**：⭐⭐⭐⭐（选学）

## 本章目标

学完本章，你应该能够：

1. 按“观察→测阻→测压→分段”的顺序排查一块不亮的消费电子板。
2. 用万用表/示波器/热像仪定位短路、开路、虚焊、器件失效。
3. 认识 BGA 返修的设备与流程：预热、拆焊、植球、回流。
4. 判断“值得修/不值得修”，避免把板子修废。
5. 处理维修中的安全边界：电池、电容、静电、高温。
6. 写维修记录，形成故障库。
7. 说出至少 8 个维修/BGA 返修常见坑。

维修不是“换件”，是“用证据缩小范围”。BGA 返修不是“吹下来再吹上去”，是“控制温度曲线和应力”。

## 正文

### 31.1 它解决什么问题：三个真实场景

#### 场景一：手机不亮，先换屏还是先测电？

换屏成本高，可能只是电池/排线/电源 IC。先测电池电压、开机电流、主供电，再决定换什么。

#### 场景二：笔记本短路，一上电就大电流

用可调电源限流，测对地阻抗，热像仪找发热点；拆电容/换 IC，不要盲目加焊。

#### 场景三：BGA 虚焊，吹下来植球失败

温度不够/助焊剂不足/植球错位，BGA 报废。BGA 返修要预热台+热风+植球台，按曲线。

### 31.2 它是什么：维修四步与 BGA 五步

维修四步：

1. **观察**：外观、烧痕、电容鼓包、进液、焊点。
2. **测阻**：断电测关键点对地阻抗，找短路。
3. **测压**：限流上电，测各级电压。
4. **分段**：断开负载/飞线，缩小故障范围。

BGA 五步：

1. 预热（板底 100～150℃）
2. 拆焊（热风 220～250℃，按锡膏）
3. 清焊盘/植球
4. 贴装/对位
5. 回流（按曲线）

> **术语第一次出现**：植球（reballing）是给 BGA 重新做焊球。需要钢网/植球台，球径/间距按封装。

### 31.3 关键参数与工具

| 工具 | 用途 | 参数 |
|---|---|---|
| 可调电源 | 限流上电 | 电压/限流 |
| 万用表 | 阻/压/通断 | 二极管档 |
| 热像仪 | 找发热 | — |
| 热风枪 | 拆焊 | 300～380℃ |
| 预热台 | BGA 底部加热 | 100～150℃ |
| 植球台/钢网 | BGA 植球 | 球径/间距 |
| 放大镜/显微镜 | 检查 | 5～20× |

### 31.4 三个典型维修流程

#### 31.4.1 不亮排查

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 340">
  <text x="20" y="30" font-size="16" fill="currentColor">图 31-1：不亮排查顺序</text>
  <rect x="280" y="55" width="160" height="50" rx="6" fill="none" stroke="currentColor" stroke-width="2"/>
  <text x="315" y="85" font-size="13" fill="currentColor">不亮</text>
  <rect x="60" y="140" width="150" height="50" rx="6" fill="none" stroke="currentColor" stroke-width="1.5"/>
  <text x="80" y="170" font-size="12" fill="currentColor">外观/进液</text>
  <rect x="270" y="140" width="150" height="50" rx="6" fill="none" stroke="currentColor" stroke-width="1.5"/>
  <text x="290" y="170" font-size="12" fill="currentColor">电池/输入</text>
  <rect x="480" y="140" width="180" height="50" rx="6" fill="none" stroke="currentColor" stroke-width="1.5"/>
  <text x="505" y="170" font-size="12" fill="currentColor">主供电/短路</text>
  <rect x="60" y="235" width="150" height="50" rx="6" fill="none" stroke="currentColor" stroke-width="1.5"/>
  <text x="80" y="265" font-size="11" fill="currentColor">排线/屏/开关</text>
  <rect x="270" y="235" width="150" height="50" rx="6" fill="none" stroke="currentColor" stroke-width="1.5"/>
  <text x="290" y="265" font-size="11" fill="currentColor">电源 IC/时序</text>
  <rect x="480" y="235" width="180" height="50" rx="6" fill="none" stroke="currentColor" stroke-width="1.5"/>
  <text x="505" y="265" font-size="11" fill="currentColor">CPU/字库/虚焊</text>
  <line x1="360" y1="105" x2="360" y2="140" stroke="currentColor" stroke-width="2"/>
  <line x1="210" y1="165" x2="270" y2="165" stroke="currentColor" stroke-width="2"/>
  <line x1="420" y1="165" x2="480" y2="165" stroke="currentColor" stroke-width="2"/>
</svg>
```

#### 31.4.2 短路定位

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 300">
  <text x="20" y="30" font-size="16" fill="currentColor">图 31-2：限流+热像定位短路</text>
  <rect x="80" y="80" width="160" height="80" rx="6" fill="none" stroke="currentColor" stroke-width="2"/>
  <text x="100" y="115" font-size="12" fill="currentColor">可调电源</text>
  <text x="100" y="140" font-size="11" fill="currentColor">1V/限流 100mA</text>
  <rect x="300" y="80" width="160" height="80" rx="6" fill="none" stroke="currentColor" stroke-width="2"/>
  <text x="320" y="115" font-size="12" fill="currentColor">板子</text>
  <text x="320" y="140" font-size="11" fill="currentColor">对地短路</text>
  <rect x="520" y="80" width="150" height="80" rx="6" fill="none" stroke="currentColor" stroke-width="2"/>
  <text x="545" y="115" font-size="12" fill="currentColor">热像仪</text>
  <text x="545" y="140" font-size="11" fill="currentColor">找热点</text>
  <line x1="240" y1="120" x2="300" y2="120" stroke="currentColor" stroke-width="2"/>
  <line x1="460" y1="120" x2="520" y2="120" stroke="currentColor" stroke-width="2"/>
  <text x="80" y="220" font-size="13" fill="currentColor">先限流，再看热点；拆/换发热器件，不要满压硬扛。</text>
</svg>
```

#### 31.4.3 BGA 返修

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 300">
  <text x="20" y="30" font-size="16" fill="currentColor">图 31-3：BGA 返修五步</text>
  <rect x="30" y="80" width="120" height="60" rx="6" fill="none" stroke="currentColor" stroke-width="1.5"/>
  <text x="50" y="115" font-size="11" fill="currentColor">预热</text>
  <rect x="170" y="80" width="120" height="60" rx="6" fill="none" stroke="currentColor" stroke-width="1.5"/>
  <text x="190" y="115" font-size="11" fill="currentColor">拆焊</text>
  <rect x="310" y="80" width="120" height="60" rx="6" fill="none" stroke="currentColor" stroke-width="1.5"/>
  <text x="330" y="115" font-size="11" fill="currentColor">清焊盘/植球</text>
  <rect x="450" y="80" width="120" height="60" rx="6" fill="none" stroke="currentColor" stroke-width="1.5"/>
  <text x="470" y="115" font-size="11" fill="currentColor">贴装</text>
  <rect x="590" y="80" width="100" height="60" rx="6" fill="none" stroke="currentColor" stroke-width="1.5"/>
  <text x="605" y="115" font-size="11" fill="currentColor">回流</text>
  <line x1="150" y1="110" x2="170" y2="110" stroke="currentColor" stroke-width="2"/>
  <line x1="290" y1="110" x2="310" y2="110" stroke="currentColor" stroke-width="2"/>
  <line x1="430" y1="110" x2="450" y2="110" stroke="currentColor" stroke-width="2"/>
  <line x1="570" y1="110" x2="590" y2="110" stroke="currentColor" stroke-width="2"/>
  <text x="30" y="210" font-size="13" fill="currentColor">预热减应力；拆焊温度按锡膏；植球对位；回流按曲线。</text>
</svg>
```

### 31.5 选型与降额

| 场景 | 方案 | 注意 |
|---|---|---|
| 手机/平板 | 先测电/排线 | 不盲目换屏 |
| 笔记本 | 限流+热像 | 主板短路 |
| BGA | 预热台+热风 | 温度曲线 |
| 进液板 | 清洗/超声 | 腐蚀/漏电 |
| 电池 | 防爆/绝缘 | 安全 |

### 31.6 测量与仿真

#### 31.6.1 维修记录

| 板号 | 现象 | 测点 | 结论 | 处理 | 结果 |
|---|---|---|---|---|---|
| 001 | 不亮 | 电池 0V | 电池饿死 | 激活/换 | 亮 |
| 002 | 大电流 | 3.3V 对地 5Ω | 电容短路 | 拆电容 | 正常 |

#### 31.6.2 CircuitJS

```circuitjs
diode-forward
```

观察二极管档测结压降，理解万用表判好坏。

#### 31.6.3 动手任务

- 找一块废板，练测阻/测压。
- 用限流电源+热像找短路（有条件）。
- 记录 5 条维修案例。
- 看一次 BGA 返修视频/实操。

### 31.7 常见坑

1. **不测阻直接上电**：短路扩大。
2. **满压硬扛**：烧更多器件。
3. **盲目换件**：成本高/问题没找到。
4. **BGA 不预热**：板子变形/焊盘脱落。
5. **植球错位/球径错**：返修失败。
6. **温度过高**：芯片/PCB 损坏。
7. **静电**：修好又坏。
8. **电池/电容未放电**：触电/短路。
9. **不记录**：经验不积累。

### 31.8 本章复盘

#### 31.8.1 公式与规则表

| 公式/规则 | 用途 | 条件与注意 |
|---|---|---|
| 观察→测阻→测压→分段 | 维修 | 先断电 |
| 限流 100mA | 短路 | 1V 起步 |
| BGA 预热 100～150℃ | 返修 | 减应力 |
| 拆焊 220～250℃ | BGA | 按锡膏 |
| 记录故障库 | 经验 | 可复用 |

#### 31.8.2 术语表

| 术语 | 英文 | 一句话解释 |
|---|---|---|
| 植球 | reballing | 给 BGA 重做焊球 |
| 虚焊 | cold joint | 未润湿焊点 |
| 限流 | current limit | 限制短路电流 |
| 热像 | thermal image | 找发热点 |
| 进液 | liquid damage | 液体腐蚀 |

#### 31.8.3 自测 10 题

1. 维修四步是什么？
2. 不亮先查什么？
3. 短路怎么定位？
4. BGA 返修五步？
5. 为什么要预热？
6. 植球注意什么？
7. 电池/电容安全边界？
8. 什么时候不值得修？
9. 维修记录写什么？
10. 静电怎么防？

#### 31.8.4 能力清单

- [ ] 能按四步排查不亮/短路。
- [ ] 能用限流+热像定位。
- [ ] 了解 BGA 返修流程。
- [ ] 能判断维修价值。
- [ ] 能写维修记录。

#### 31.8.5 下一章

下一章讲**硬件工程师职业路径与简历**：从“会修/会画”走向“能求职/能成长”。
