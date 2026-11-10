# 第 27 章 · DFM、拼板与生产成本

> **所属阶段**：阶段四 · 多层板与高速设计
> **前置课程**：第 26 章 EMC/ESD 与防护设计
> **本课难度**：⭐⭐⭐

## 本章目标

学完本章，你应该能够：

1. 说清 DFM（可制造性设计）检查的 8 个维度。
2. 设计拼板：V-cut/邮票孔/间距/工艺边。
3. 估算 PCB 成本：面积、层数、工艺、数量。
4. 处理阻焊/丝印/孔径/线宽等板厂工艺边界。
5. 做一份可被板厂直接生产的 Gerber/钻孔/坐标包。
6. 理解“设计降本”不等于“偷工减料”。
7. 说出至少 8 个 DFM/拼板常见坑。

设计出来的板子必须能制造。DFM 不是“板厂的事”，是设计阶段就要避免的坑；拼板/工艺边/成本，直接影响打样和量产。

## 正文

### 27.1 它解决什么问题：三个真实场景

#### 场景一：拼板没有工艺边，贴片机夹不住

板子拼在一起，边缘没有 5mm 工艺边/定位孔，贴片机轨道夹不住，只能手贴。拼板要留工艺边和 Mark 点。

#### 场景二：V-cut 太靠边，板子掰裂

V-cut 线离器件/焊盘太近，掰板时应力把焊盘拉裂。V-cut 要留安全距离，邮票孔要按孔径/间距。

#### 场景三：孔太小/线太细，板厂加价或做不出

0.2mm 孔、4mil 线，普通板厂做不了/良率低，价格翻倍。设计前先看板厂工艺能力表。

### 27.2 它是什么：DFM 是“设计迁就工艺”

DFM（Design for Manufacturability，可制造性设计）检查：

1. 最小线宽/间距
2. 最小孔径/环宽
3. 阻焊/丝印
4. 焊盘/钢网
5. 拼板/工艺边
6. 阻抗/叠层
7. 测试点/定位
8. 文件完整性

> **术语第一次出现**：工艺边（process edge）是拼板边缘留出的 5～10mm 区域，给贴片机轨道/定位孔用，不放器件。

### 27.3 关键参数与工艺

| 项目 | 普通板厂 | 高密度 | 说明 |
|---|---|---|---|
| 最小线宽 | 6mil | 4mil | 越细越贵 |
| 最小间距 | 6mil | 4mil | 同上 |
| 最小孔 | 0.3mm | 0.2mm | 钻孔/环宽 |
| 环宽 | 0.15mm | 0.1mm | 孔到铜 |
| 板厚 | 1.6mm | 0.8～2.0 | 按叠层 |
| 阻焊 | 绿/黑/白 | — | 黑油难检查 |
| 拼板 | V-cut/邮票孔 | — | 按形状 |
| 工艺边 | 5～10mm | — | 贴片 |

### 27.4 三个典型拼板

#### 27.4.1 V-cut 拼板

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 320">
  <text x="20" y="30" font-size="16" fill="currentColor">图 27-1：V-cut 拼板与工艺边</text>
  <rect x="40" y="60" width="640" height="220" fill="none" stroke="currentColor" stroke-width="2"/>
  <rect x="60" y="80" width="180" height="180" fill="none" stroke="currentColor" stroke-width="1.5"/>
  <rect x="270" y="80" width="180" height="180" fill="none" stroke="currentColor" stroke-width="1.5"/>
  <rect x="480" y="80" width="180" height="180" fill="none" stroke="currentColor" stroke-width="1.5"/>
  <line x1="240" y1="80" x2="240" y2="260" stroke="currentColor" stroke-width="3" stroke-dasharray="6 4"/>
  <line x1="450" y1="80" x2="450" y2="260" stroke="currentColor" stroke-width="3" stroke-dasharray="6 4"/>
  <text x="200" y="295" font-size="11" fill="currentColor">V-cut</text>
  <text x="60" y="55" font-size="11" fill="currentColor">工艺边 5～10mm</text>
</svg>
```

#### 27.4.2 邮票孔拼板

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 300">
  <text x="20" y="30" font-size="16" fill="currentColor">图 27-2：邮票孔拼板</text>
  <rect x="80" y="70" width="240" height="160" fill="none" stroke="currentColor" stroke-width="2"/>
  <rect x="360" y="70" width="240" height="160" fill="none" stroke="currentColor" stroke-width="2"/>
  <line x1="320" y1="80" x2="320" y2="220" stroke="currentColor" stroke-width="1" stroke-dasharray="2 6"/>
  <text x="330" y="255" font-size="12" fill="currentColor">邮票孔：孔径 0.5～1.0mm，孔间距 1.5～2.5mm</text>
</svg>
```

#### 27.4.3 成本构成

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 300">
  <text x="20" y="30" font-size="16" fill="currentColor">图 27-3：PCB 成本构成</text>
  <rect x="80" y="200" width="70" height="60" fill="none" stroke="currentColor" stroke-width="1.5"/>
  <rect x="180" y="160" width="70" height="100" fill="none" stroke="currentColor" stroke-width="1.5"/>
  <rect x="280" y="120" width="70" height="140" fill="none" stroke="currentColor" stroke-width="1.5"/>
  <rect x="380" y="90" width="70" height="170" fill="none" stroke="currentColor" stroke-width="1.5"/>
  <rect x="480" y="60" width="70" height="200" fill="none" stroke="currentColor" stroke-width="1.5"/>
  <text x="90" y="285" font-size="11" fill="currentColor">面积</text>
  <text x="190" y="285" font-size="11" fill="currentColor">层数</text>
  <text x="290" y="285" font-size="11" fill="currentColor">工艺</text>
  <text x="390" y="285" font-size="11" fill="currentColor">数量</text>
  <text x="490" y="285" font-size="11" fill="currentColor">交期</text>
</svg>
```

### 27.5 选型与降额

| 决策 | 低成本 | 高性能 | 建议 |
|---|---|---|---|
| 层数 | 2/4 层 | 6/8 层 | 按信号 |
| 线宽 | 6mil | 4mil | 不盲目细 |
| 孔 | 0.3mm | 0.2mm | 按板厂 |
| 拼板 | V-cut | 邮票孔 | 按形状 |
| 表面处理 | HASL | ENIG | 按焊接 |
| 数量 | 多拼 | 单板 | 摊薄 |

### 27.6 测量与仿真

#### 27.6.1 出板前检查

1. Gerber 逐层对照。
2. 钻孔表/孔径。
3. 阻焊/丝印不压焊盘。
4. 拼板/工艺边/Mark。
5. 板厂工艺能力核对。
6. 阻抗/叠层确认。

#### 27.6.2 CircuitJS

```circuitjs
rc-lowpass-159
```

用 RC 理解“工艺/走线寄生”对信号的影响，避免为省成本牺牲关键线。

#### 27.6.3 动手任务

- 给自己的板做一次拼板（3×2）。
- 加 5mm 工艺边和 3 个 Mark。
- 查板厂工艺表，核对最小线宽/孔。
- 估算 10 片/100 片成本。

### 27.7 常见坑

1. **无工艺边**：贴片夹不住。
2. **V-cut 靠器件太近**：掰裂。
3. **邮票孔太少/太大**：掰不断/应力大。
4. **Mark 点被阻焊盖**：贴片机识别不到。
5. **孔太小**：板厂加价/良率低。
6. **线太细**：断线/良率低。
7. **黑油阻焊**：检查困难。
8. **Gerber 缺层/镜像**：做错。
9. **拼板不对称**：应力/变形。

### 27.8 本章复盘

#### 27.8.1 公式与规则表

| 公式/规则 | 用途 | 条件与注意 |
|---|---|---|
| 工艺边 5～10mm | 贴片 | 不放器件 |
| V-cut 留安全距离 | 掰板 | 按板厂 |
| 邮票孔 0.5～1.0mm | 拼板 | 孔距 1.5～2.5mm |
| Mark 3 个 | 贴片 | 不被阻焊盖 |
| 成本≈面积×层数×工艺×数量 | 估算 | 交期也影响 |

#### 27.8.2 术语表

| 术语 | 英文 | 一句话解释 |
|---|---|---|
| DFM | design for manufacturability | 可制造性设计 |
| 拼板 | panelization | 多板拼在一起 |
| V-cut | V-score | V 形切割线 |
| 邮票孔 | mouse bite | 小孔连接拼板 |
| 工艺边 | process edge | 贴片机用的边缘 |
| Mark 点 | fiducial | 贴片定位标记 |

#### 27.8.3 自测 10 题

1. DFM 检查哪些维度？
2. 工艺边多宽？
3. V-cut 和邮票孔区别？
4. Mark 点作用？
5. 孔太小有什么问题？
6. 成本由哪些因素决定？
7. 黑油阻焊为什么难？
8. 拼板不对称有什么后果？
9. Gerber 要检查哪些层？
10. 设计降本不能牺牲什么？

#### 27.8.4 能力清单

- [ ] 能做 DFM 检查。
- [ ] 能设计 V-cut/邮票孔拼板。
- [ ] 能加工艺边/Mark。
- [ ] 能估算成本。
- [ ] 能出完整生产包。

#### 27.8.5 下一章

下一章讲**4 层板·H3 机顶盒**：把叠层、DDR、EMC、DFM 用到一块真实项目板。
