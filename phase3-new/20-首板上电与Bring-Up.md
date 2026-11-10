# 第 20 章 · 首板上电与 Bring-Up

> **所属阶段**：阶段三 · 单片机与第一块项目板
> **前置课程**：第 19 章 2 层板布局布线实战
> **本课难度**：⭐⭐⭐

## 本章目标

学完本章，你应该能够：

1. 制定首板上电的安全顺序，避免“一上电就冒烟”。
2. 用限流电源、万用表、示波器定位电源/复位/时钟问题。
3. 按“电源→MCU→时钟→调试→外设→通信”的顺序 Bring-Up。
4. 读懂常见现象：不亮、不跑、不认、不通，分别查什么。
5. 用 SWD 读 ID、读寄存器、下载程序，确认芯片活着。
6. 记录 Bring-Up 日志，形成可复现的排障表。
7. 说出至少 8 个首板上电常见坑。

Bring-Up 是硬件工程师的“急诊”。板子第一次上电，最怕“全焊满、直接满压”。正确做法是分步、限流、先测后上电。

## 正文

### 20.1 它解决什么问题：三个真实场景

#### 场景一：一上电就冒烟，LDO 反了

LDO 封装焊反/引脚定义错，12V 直接灌到 3.3V 轨，MCU 烧。上电前先目视/测二极管，限流 100mA，能救回大部分板子。

#### 场景二：电源正常，MCU 不跑

3.3V 正常，但 BOOT0 悬空、NRST 被电容按住、晶振不起振。按“电源→复位→时钟→调试”顺序查，不要一上来刷固件。

#### 场景三：SWD 能连，但下载失败

SWD 能读 ID，下载时提示 Flash 保护/时钟不对。检查 BOOT、复位、电源跌落、SWD 速率。

### 20.2 它是什么：Bring-Up 是分步验证

Bring-Up 顺序：

1. 目视/短路检查（不焊关键芯片）
2. 电源段上电（限流）
3. 焊 MCU，测电流/电压
4. 复位/BOOT/时钟
5. SWD 连接/读 ID
6. 下载/运行最小程序
7. 外设逐个验证
8. 通信/负载/老化

> **术语第一次出现**：限流上电（current-limited power-up）是把电源限流设到预期电流的 1.2～2 倍，短路时电压跌落而不是烧板。

### 20.3 关键参数与工具

| 工具 | 用途 | 设置 |
|---|---|---|
| 可调电源 | 限流上电 | 电压=标称，限流=预期×1.5 |
| 万用表 | 电压/通断/二极管 | 先测阻抗 |
| 示波器 | 复位/时钟/纹波 | 20MHz 带宽 |
| 热像仪 | 找发热 | 上电后扫 |
| SWD 调试器 | 下载/读 ID | 速率先低后高 |

### 20.4 三个典型排障流程

#### 20.4.1 电源不亮

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 340">
  <text x="20" y="30" font-size="16" fill="currentColor">图 20-1：电源不亮排障树</text>
  <rect x="280" y="55" width="160" height="50" rx="6" fill="none" stroke="currentColor" stroke-width="2"/>
  <text x="315" y="85" font-size="13" fill="currentColor">无输出</text>
  <rect x="80" y="140" width="160" height="50" rx="6" fill="none" stroke="currentColor" stroke-width="1.5"/>
  <text x="105" y="170" font-size="12" fill="currentColor">输入有无？</text>
  <rect x="280" y="140" width="160" height="50" rx="6" fill="none" stroke="currentColor" stroke-width="1.5"/>
  <text x="305" y="170" font-size="12" fill="currentColor">短路？</text>
  <rect x="480" y="140" width="170" height="50" rx="6" fill="none" stroke="currentColor" stroke-width="1.5"/>
  <text x="505" y="170" font-size="12" fill="currentColor">使能/反馈？</text>
  <rect x="80" y="235" width="160" height="50" rx="6" fill="none" stroke="currentColor" stroke-width="1.5"/>
  <text x="100" y="265" font-size="11" fill="currentColor">保险/接口/极性</text>
  <rect x="280" y="235" width="160" height="50" rx="6" fill="none" stroke="currentColor" stroke-width="1.5"/>
  <text x="300" y="265" font-size="11" fill="currentColor">测对地阻抗</text>
  <rect x="480" y="235" width="170" height="50" rx="6" fill="none" stroke="currentColor" stroke-width="1.5"/>
  <text x="500" y="265" font-size="11" fill="currentColor">EN/FB/电感/焊点</text>
  <line x1="360" y1="105" x2="360" y2="140" stroke="currentColor" stroke-width="2"/>
  <line x1="240" y1="165" x2="280" y2="165" stroke="currentColor" stroke-width="2"/>
  <line x1="440" y1="165" x2="480" y2="165" stroke="currentColor" stroke-width="2"/>
  <line x1="160" y1="190" x2="160" y2="235" stroke="currentColor" stroke-width="2"/>
  <line x1="360" y1="190" x2="360" y2="235" stroke="currentColor" stroke-width="2"/>
  <line x1="565" y1="190" x2="565" y2="235" stroke="currentColor" stroke-width="2"/>
</svg>
```

#### 20.4.2 MCU 不跑

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 320">
  <text x="20" y="30" font-size="16" fill="currentColor">图 20-2：MCU 不跑排查顺序</text>
  <rect x="40" y="70" width="130" height="60" rx="6" fill="none" stroke="currentColor" stroke-width="1.5"/>
  <text x="60" y="105" font-size="12" fill="currentColor">电源 3.3V</text>
  <rect x="200" y="70" width="130" height="60" rx="6" fill="none" stroke="currentColor" stroke-width="1.5"/>
  <text x="220" y="105" font-size="12" fill="currentColor">复位波形</text>
  <rect x="360" y="70" width="130" height="60" rx="6" fill="none" stroke="currentColor" stroke-width="1.5"/>
  <text x="380" y="105" font-size="12" fill="currentColor">BOOT 电平</text>
  <rect x="520" y="70" width="150" height="60" rx="6" fill="none" stroke="currentColor" stroke-width="1.5"/>
  <text x="540" y="105" font-size="12" fill="currentColor">晶振起振</text>
  <line x1="170" y1="100" x2="200" y2="100" stroke="currentColor" stroke-width="2"/>
  <line x1="330" y1="100" x2="360" y2="100" stroke="currentColor" stroke-width="2"/>
  <line x1="490" y1="100" x2="520" y2="100" stroke="currentColor" stroke-width="2"/>
  <rect x="200" y="200" width="320" height="60" rx="6" fill="none" stroke="currentColor" stroke-width="1.5"/>
  <text x="225" y="235" font-size="12" fill="currentColor">SWD 读 ID / 下载最小程序</text>
  <line x1="595" y1="130" x2="595" y2="230" stroke="currentColor" stroke-width="2"/>
  <line x1="595" y1="230" x2="520" y2="230" stroke="currentColor" stroke-width="2"/>
  <text x="40" y="285" font-size="13" fill="currentColor">顺序不能跳：先电源，再复位/BOOT，再时钟，最后调试。</text>
</svg>
```

#### 20.4.3 通信不通

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 300">
  <text x="20" y="30" font-size="16" fill="currentColor">图 20-3：UART/RS485 不通检查点</text>
  <rect x="40" y="80" width="120" height="60" rx="6" fill="none" stroke="currentColor" stroke-width="1.5"/>
  <text x="60" y="115" font-size="12" fill="currentColor">TX/RX</text>
  <rect x="200" y="80" width="120" height="60" rx="6" fill="none" stroke="currentColor" stroke-width="1.5"/>
  <text x="220" y="115" font-size="12" fill="currentColor">电平/交叉</text>
  <rect x="360" y="80" width="120" height="60" rx="6" fill="none" stroke="currentColor" stroke-width="1.5"/>
  <text x="380" y="115" font-size="12" fill="currentColor">波特率/时钟</text>
  <rect x="520" y="80" width="150" height="60" rx="6" fill="none" stroke="currentColor" stroke-width="1.5"/>
  <text x="540" y="115" font-size="12" fill="currentColor">共地/终端</text>
  <line x1="160" y1="110" x2="200" y2="110" stroke="currentColor" stroke-width="2"/>
  <line x1="320" y1="110" x2="360" y2="110" stroke="currentColor" stroke-width="2"/>
  <line x1="480" y1="110" x2="520" y2="110" stroke="currentColor" stroke-width="2"/>
  <text x="40" y="220" font-size="13" fill="currentColor">先看波形有没有、电平对不对，再看协议/终端，最后怀疑固件。</text>
</svg>
```

### 20.5 选型与降额

| 工具/设置 | 建议 | 注意 |
|---|---|---|
| 限流 | 预期×1.5 | 太小会误判 |
| 示波器探头 | 10× | 地线短 |
| SWD 速率 | 先 1MHz | 稳定后再升 |
| 热像仪 | 上电扫 | 找异常发热 |

### 20.6 测量与仿真

#### 20.6.1 上电记录表

| 步骤 | 测点 | 期望 | 实测 | 结论 |
|---|---|---|---|---|
| 1 | Vin | 12V | | |
| 2 | 5V | 5±0.25V | | |
| 3 | 3.3V | 3.3±0.1V | | |
| 4 | NRST | 高 | | |
| 5 | BOOT0 | 低 | | |
| 6 | SWD ID | 可读 | | |

#### 20.6.2 CircuitJS

```circuitjs
rc-charge
```

观察复位 RC 上电波形。

```circuitjs
power-buck
```

观察电源软启动/纹波。

#### 20.6.3 动手任务

- 给一块新板做限流上电，记录电压/电流。
- 测 NRST/BOOT0/晶振。
- 用 SWD 读 ID，下载 blink。
- 写一页 Bring-Up 日志。

### 20.7 常见坑

1. **满压直接上电**：短路烧一片。
2. **不测对地阻抗**：电源短路不知道。
3. **先焊 MCU 再测电源**：电源错烧 MCU。
4. **复位电容太大**：MCU 不启动。
5. **BOOT0 悬空**：启动模式随机。
6. **晶振不起振**：时钟错，串口波特率偏。
7. **SWD 地不可靠**：连不上/下载失败。
8. **通信不共地**：波形有但通信不通。
9. **不记录**：同样问题再犯。

### 20.8 本章复盘

#### 20.8.1 公式与规则表

| 公式/规则 | 用途 | 条件与注意 |
|---|---|---|
| 限流 = 预期×1.5 | 上电保护 | 太小误判 |
| 先电源后负载 | Bring-Up | 分步焊 |
| NRST 高/BOOT0 低 | 启动 | 按手册 |
| SWD 先低速 | 连接 | 稳定后升 |
| 共地 | 通信 | 差分/单端都需 |

#### 20.8.2 术语表

| 术语 | 英文 | 一句话解释 |
|---|---|---|
| Bring-Up | bring-up | 新板首次上电调试 |
| 限流 | current limit | 限制短路电流 |
| 读 ID | read ID | 确认芯片活着 |
| 冷焊 | cold joint | 未润湿的焊点 |
| 热像 | thermal image | 找发热点 |

#### 20.8.3 自测 10 题

1. 首板上电第一步做什么？
2. 限流设多少？
3. 电源不亮先查什么？
4. MCU 不跑的四步顺序？
5. BOOT0 正常是什么电平？
6. 晶振不起振怎么查？
7. SWD 能连但下载失败查什么？
8. 通信不通先看什么？
9. 为什么要记录 Bring-Up 日志？
10. 热像仪怎么用？

#### 20.8.4 能力清单

- [ ] 能制定限流上电顺序。
- [ ] 能按电源→MCU→时钟→调试排障。
- [ ] 能用 SWD 读 ID/下载。
- [ ] 能测复位/BOOT/晶振/通信。
- [ ] 能写 Bring-Up 记录。

#### 20.8.5 下一章

下一章讲**硬件测试与可靠性**：板子能跑只是开始，还要验证它在高低温、振动、EMC、寿命下的表现。
