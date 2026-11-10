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

#### 20.2.1 上电前的静态检查

首板最大的风险不是“设计错”，是“焊错/短路”。上电前用 10 分钟做静态检查，能救回大部分板子。

**目视**：连锡/虚焊/立碑/极性/器件方向；连接器/座子是否焊反；BGA/QFN 是否偏移。

**对地阻抗**：万用表电阻档/二极管档测 12V/5V/3.3V 对 GND；正常是几百 Ω 到几 kΩ（有电容充电会跳）；接近 0Ω 就是短路，不能上电。

**二极管档**：测 LDO 输入输出、MOS 体二极管、TVS 方向；能看出“反了/短路”。

**电源轨隔离**：先不焊 MCU/大电流负载，只焊电源段；测电压正常再焊负载。

**保险/限流**：输入串自恢复保险/限流电阻；限流电源设到预期电流 1.2～2 倍。

**静电/台面**：防静电台垫/腕带；金属台面短路；板子下垫绝缘。

**记录**：静态检查结果写进 Bring-Up 日志；哪一步没过，就停在哪一步。

#### 20.2.2 限流上电与电流判读

限流上电是“用电源保护板子”，不是“正常供电”。

**设置**：电压=标称（比如 12V），限流=预期电流×1.5；预期不知道就先 50～100mA。空板/轻载电流很小，限流低能立刻发现短路。

**现象判读**：

- 电压正常、电流很小：正常/负载没接；
- 电压被拉低、电流到限流值：短路/反接/器件坏；
- 电流逐渐上升：电容充电/器件发热；
- 电流跳动：接触不良/振荡。

**逐步加压**：12V 系统可先 5V/9V 试，再 12V；3.3V 轨先 1.8V/2.5V 试（注意欠压不复位）。

**限流不是保险**：限流电源反应慢，短路瞬间仍可能损坏；保险/ TVS 是第二层保护。

**记录**：空板/半载/满载电流都记；后面比较“是否异常”。

**常见错误**：限流设太大（等于没限）、限流设太小（正常启动被误判）、上电顺序错（先功率后控制）。

#### 20.2.3 首板电流预算：先算“应该多少”

不知道“正常电流”，就无法判断“异常电流”。

**静态电流**：MCU 睡眠 + LDO 静态 + 上拉/指示 LED；通常几 mA 到几十 mA。

**运行电流**：MCU 72MHz + 外设 + LED + 通信；几十 mA 到几百 mA。

**峰值电流**：继电器/电机/无线发射；可能是平均的几倍；电源/限流要按峰值。

**算法**：`I_total=ΣI_device + 余量(30%)`；每路电源分别算；DCDC/LDO 效率影响输入电流。

**算例**：3.3V 轨 MCU 30mA + LED 4×5mA + 传感器 5mA + 串口 5mA ≈ 60mA；5V 输入经 LDO，`I_in≈60mA×3.3/5/0.9≈44mA`（LDO 输入电流≈输出）。

**判读**：实测电流比预算大很多→短路/器件错/短路保护；小很多→没跑起来/外设没使能。

**记录**：空板/运行/峰值都写进日志；后面对比“是否漂移”。

#### 20.2.4 焊接顺序：先低后高、先小后大

同一块板，焊接顺序影响返修难度。

**先电源后负载**：电源段焊完测电压，再焊 MCU/外设；避免“电源错烧一片”。

**先小后大**：0402/0603 小阻容→QFN/QFP→连接器/大电容；大器件挡住小焊点。

**先低后高**：矮器件先焊，高器件后焊；避免热风/烙铁碰倒。

**先贴片后插件**：贴片回流/热风，插件最后手工焊；插件挡贴片。

**关键器件最后**：MCU/BGA/贵器件最后焊，减少返修次数。

**焊接参数**：烙铁 330～360℃（无铅）、热风 260～300℃、预热台 100～150℃；按锡膏/器件。

**保护**：ESD/防静电；连接器/屏排线最后插；焊接后清洗助焊剂。

#### 20.2.5 首板预算与“预期值”表

| 项目 | 预期 | 实测 | 偏差原因 |
|---|---|---|---|
| 12V 空载电流 | <10mA |  |  |
| 5V 空载 | <20mA |  |  |
| 3.3V 空载 | <30mA |  |  |
| 3.3V 运行 | 40～80mA |  |  |
| 5V 运行 | 50～100mA |  |  |
| LDO 温升 | <30℃ |  |  |
| MCU 温升 | <20℃ |  |  |

先写“预期”，再测“实测”；偏差大就查，不凭感觉。
### 20.3 关键参数与工具

| 工具 | 用途 | 设置 |
|---|---|---|
| 可调电源 | 限流上电 | 电压=标称，限流=预期×1.5 |
| 万用表 | 电压/通断/二极管 | 先测阻抗 |
| 示波器 | 复位/时钟/纹波 | 20MHz 带宽 |
| 热像仪 | 找发热 | 上电后扫 |
| SWD 调试器 | 下载/读 ID | 速率先低后高 |

#### 20.3.1 工具设置：示波器、万用表、热像仪

**示波器**：探头 10×，带宽限制 20MHz（测电源纹波），耦合 DC（看电平）/AC（看纹波）；地线短（弹簧地），避免长地线引入噪声；触发用边沿/单次抓上电。

**万用表**：电阻/通断/二极管/电压/电流档；测对地阻抗先断电、放电；通断档有阈值（<50Ω 响），不要当精密电阻用。

**热像仪**：上电前调发射率/量程；上电后扫 LDO/MCU/驱动/MOS；异常发热点先断电查；小器件可贴黑胶带提高发射率。

**SWD 调试器**：先 1MHz，稳定后升；接线短/地可靠；目标板供电/调试器供电不要冲突。

**可调电源**：限流/电压/电流显示；带输出开关；最好有远端补偿（长线）。

**工具不是越多越好**：万用表+示波器+限流电源，三件套能覆盖 80% 首板问题。

#### 20.3.2 万用表的四个关键测法

**对地阻抗**：断电/放电，红笔接测试点、黑笔接 GND；电阻档；有电容会缓慢上升，等稳定读数；<10Ω 重点查短路。

**通断**：断电测焊点/连接器；<50Ω 响；不要带电测。

**二极管档**：测 LDO 输入输出、MOS 体二极管、TVS；正向 0.5～0.7V，反向 OL；反了/短路能看出。

**电压/电流**：电压并联、电流串联；电流档不要并联到电源（会短路）；测电流用限流电源显示更方便。

**技巧**：表笔尖细/钩子；测 QFN 用针；地参考选干净点；读数跳动查接触/干扰。

**误区**：通断响≠焊好（可能是旁边短路）；电压正常≠能带载；二极管档测在路会受并联影响。
#### 20.3.3 示波器抓上电的单次设置

**时基**：先 100ms/div 看全程，再放大到 1ms/div 看细节；上电过程几十 ms。

**触发**：边沿触发、上升沿、电平在 1～2V；单次（Single）抓第一次上电。

**通道**：CH1 电源、CH2 NRST/BOOT0；两通道对比时序。

**探头**：10×、短地；测纹波用弹簧地；高压/浮地用差分探头。

**保存**：截图/存波形；记录时间/条件；和后面批次对比。

**常见错误**：时基太快看不到全程、触发没设好抓不到、地线长引入噪声。

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

#### 20.4.4 电源纹波、负载瞬态与软启动

电源“有电压”不等于“能带负载”。

**纹波**：示波器 AC 耦合、20MHz 带宽、探头地弹簧；测 3.3V/5V 输出；纹波大查电容/布局/开关频率。

**负载瞬态**：电子负载/继电器切负载，看电压跌落/恢复；跌落大查反馈/输出电容/布线。

**软启动**：DCDC 的 SS 脚/内部软启动，限制上电浪涌；软启动太长会“上电慢”，太短会过流。

**上电时序**：多路电源按顺序（core→IO→模拟）；用示波器多通道抓；时序错会锁死/大电流。

**效率/发热**：满载测输入功率/输出功率，算效率；发热点用热像仪；效率低查电感/开关/死区。

**记录**：纹波峰峰值、瞬态跌落、效率、温度；这些是“电源能不能交付”的判据。

#### 20.4.5 焊接返修与冷焊：Bring-Up 的一半是焊

首板问题里，焊接占很大比例。

**冷焊**：焊点未润湿/发暗/成球；看似焊上，实际电阻大/时通时断。返修：加助焊剂/补焊。

**连锡**：QFP/QFN 引脚间短路；用吸锡带/助焊剂清理；显微镜检查。

**立碑/偏移**：小电容/电阻一端翘起；返修：热风+镊子复位。

**虚焊**：BGA/QFN EP 底部空洞；X-Ray 才能看出；返修：重新植球/回流。

**焊盘脱落**：过热/拉拽；飞线/补焊盘；改设计加泪滴。

**返修工具**：烙铁/热风/预热台/显微镜/助焊剂/吸锡带；温度按锡膏/器件。

**返修后**：重新测对地阻抗/上电电流；不要“焊完直接满压”。

**记录**：返修位置/原因/结果；同一位置反复返修说明设计/工艺有问题。

#### 20.4.6 复位与时钟波形怎么判读

**NRST**：上电应从低到高；一直低→复位按键/电容/短路；一直高但不起振→时钟/BOOT；抖动→干扰/按键。

**BOOT0**：上电时必须低（Flash）；高→进 ISP；跳变→接触不良。

**晶振**：正弦/近似方波，频率 8MHz；幅度小/不起→负载电容/焊接；探头电容会让它停振，测时用 10×/短地。

**SWDCLK/SWDIO**：连接时有波形；无波形→调试器/接线/目标未上电。

**电源纹波**：AC 耦合，20MHz 带宽；峰峰值大→电容/布局；上电过冲→软启动/电容。

**判读原则**：先看“有没有”，再看“电平对不对”，最后看“时序对不对”。

#### 20.4.7 发热排查：热像仪怎么用

**发射率**：金属/亮面反射，测温不准；贴黑胶带/喷哑光漆，发射率设 0.95。

**量程**：先大量程扫，再缩小；避免“满量程饱和”。

**扫描顺序**：LDO/DCDC→MCU→驱动/MOS→连接器→电感/电阻；异常热点优先。

**判据**：`Tj=Ta+P×RθJA`；手摸烫（>60℃）要查；器件结温留 20℃ 余量。

**常见热点**：LDO 压差大、MOS 导通电阻大、电感饱和、电阻功率不够、短路。

**处理**：降电流/换封装/加铜/加散热；不要“烫但能用”就放过。

**记录**：热点位置/温度/负载条件；老化前后对比。

#### 20.4.8 多路电源的上电时序

多电源系统，时序错会“锁死/大电流/器件损坏”。

**顺序原则**：core（内核）→IO→模拟/射频；或按芯片手册；DCDC 的 PG（Power Good）级联 EN。

**时序参数**：上升时间/延时/单调性；用示波器多通道抓；非单调上升可能锁死。

**常见错误**：3.3V 早于 5V、VDDA 早于 VDD、IO 有电 core 没电→漏电/锁死。

**实现**：EN 分压/RC 延时、PG 级联、电源排序芯片；软件也可控制（但硬件要先安全）。

**验证**：反复上电/断电，抓时序；异常时加负载/温度。

**记录**：每路上升时间/延时/过冲；和手册比。
#### 20.4.9 静电与台面：别在最后一步毁板

**静电来源**：人体/衣服/塑料/地毯；MOS/BGA/连接器最怕。

**防护**：防静电台垫/腕带（1MΩ 限流）、接地烙铁、离子风机；板子放防静电袋。

**台面**：金属台面/工具短路；板子下垫绝缘；不要带电插拔。

**操作**：拿板边/连接器外壳，不摸金手指/引脚；插拔先断电；连接器对齐再插。

**已损坏表现**：IO 漏电/ADC 漂/通信不稳/上电电流大；可能“时好时坏”。

**课程**：至少做到“洗手/摸接地金属/拿板边”；条件允许用腕带。

### 20.5 选型与降额

| 工具/设置 | 建议 | 注意 |
|---|---|---|
| 限流 | 预期×1.5 | 太小会误判 |
| 示波器探头 | 10× | 地线短 |
| SWD 速率 | 先 1MHz | 稳定后再升 |
| 热像仪 | 上电扫 | 找异常发热 |

#### 20.5.1 首板上电顺序表（可打印）

| 步 | 操作 | 判据 | 不通过怎么办 |
|---|---|---|---|
| 1 | 目视/短路 | 无连锡，阻抗>100Ω | 返修/查短路 |
| 2 | 只焊电源段 | 12V/5V/3.3V 正常 | 查输入/EN/FB |
| 3 | 焊 MCU | 3.3V 不跌，电流<50mA | 查短路/焊接 |
| 4 | 测复位/BOOT | NRST 高，BOOT0 低 | 查 RC/下拉 |
| 5 | 测晶振 | 8MHz 起振 | 查电容/焊接 |
| 6 | SWD 读 ID | ID 正确 | 查地/复位/时钟 |
| 7 | 下载 blink | LED 闪 | 查 BOOT/Flash |
| 8 | 逐个外设 | 每个功能正常 | 查对应电路 |
| 9 | 通信/负载 | 不丢包/不跌压 | 查终端/电源 |
| 10 | 老化 | 温度/电流稳定 | 查热/余量 |

顺序不能跳；每一步都有“判据/不通过怎么办”，新手也能照着走。

#### 20.5.2 保险、TVS 与限流电阻怎么选

**保险**：额定电流≥最大工作电流 1.5 倍；自恢复保险有保持/跳闸电流/时间；慢启动负载选耐浪涌。

**TVS**：工作电压>正常电压，钳位<后级耐压；双向/单向按信号；结电容按速率（USB 低电容）。

**限流电阻**：`R=(Vin−Vout)/I`；功耗 `P=I²R`；只适合小电流/低成本，大电流用保险/PMOS。

**反接保护**：串联肖特基（压降/发热）或 PMOS（低损耗）；TVS 只能钳位不能防反接。

**过压保护**：TVS + 保险/OVP 芯片；雷击/浪涌用压敏/GDT。

**选型错误**：保险太大（不起作用）、TVS 钳位太高（后级先坏）、限流电阻功率不够（烧）。

**验证**：限流上电 + 短路测试（小心）；确认保护动作后能恢复。
#### 20.5.3 电源保护链的顺序

保护器件不是“随便加”，顺序决定谁先承受能量。

**典型链**：输入连接器→保险/自恢复→TVS/压敏→共模/滤波→DCDC/LDO→负载。

**原则**：保险在最前（切断持续过流）、TVS 在保险后（钳位瞬态）、滤波在 TVS 后（去残压）；ESD 靠近接口。

**反接**：PMOS/理想二极管在输入；TVS 不能防反接。

**过压**：OVP 芯片/钳位；雷击/浪涌用 GDT/压敏。

**选型**：保险 I²t/电压；TVS 钳位/峰值脉冲；电容耐压/纹波。

**验证**：限流上电、短路、反接（小心）；保护后能恢复/更换。

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

#### 20.6.4 四个“不”的故障树

**不亮**（电源灯不亮）：输入→保险→LDO EN→输出→LED 极性。先测电压，再测 LED 电流。

**不跑**（MCU 不运行）：3.3V→NRST→BOOT0→晶振→SWD ID。按顺序，不要一上来刷固件。

**不认**（SWD/下载器识别不到）：GND→SWDIO/SWCLK→NRST→BOOT→时钟→调试器速率。地最先查。

**不通**（通信不通）：TX/RX 交叉→电平→共地→波特率→终端→协议。先看波形有无，再看数据。

**共同原则**：从“能量/电平”查到“协议/固件”；先用万用表/示波器，再怀疑芯片/固件。

#### 20.6.5 Bring-Up 日志模板

| 时间 | 步骤 | 现象 | 测量值 | 判断/动作 | 结果 |
|---|---|---|---|---|---|
| 10:00 | 目视 | 无连锡 | 3.3V 对地 1.2kΩ | 正常 | 通过 |
| 10:10 | 上电 5V | 电流 0.02A | 5.01V | 正常 | 通过 |
| 10:20 | 焊 MCU | 电流 0.05A | 3.30V | 正常 | 通过 |
| 10:30 | SWD | 读 ID 失败 | SWCLK 无波形 | 接线松 | 重接 |
| 10:40 | 重试 | 读 ID 成功 | 0x1BA01477 | 正常 | 通过 |

**写法**：时间/步骤/现象/测量值/判断/结果；不写“好像正常”，写数值。

**用途**：复盘/交接/量产对照；同一块板二次调试能快速定位。

**注意**：失败记录也要留；失败比成功更有信息量。

#### 20.6.6 小批试产与首板差异

首板过了，不等于小批能过。

**物料**：替代料/批次差异；连接器/晶振/电容公差；BOM 核对。

**工艺**：贴片偏移/连锡/虚焊；回流曲线；钢网开口。

**测试**：治具/测试点；ICT/FCT；限流/老化。

**一致性**：多块板对比电流/波形/温度；偏差大查物料/工艺。

**文档**：测试记录/不良分析/返修记录；小批问题反馈到设计。

**课程**：没有小批条件，也要知道“首板≠量产”；设计要为测试/生产留余量。

#### 20.6.7 测试点、治具与可测性

板子难测，往往不是“技术问题”，是“没留测试点”。

**测试点**：每路电源、GND、NRST、BOOT0、UART TX/RX、SWD、关键信号；直径≥1mm，间距≥2.54mm。

**位置**：板边/空旷区，探头能碰；不要被高器件/连接器挡住；双面测试点错开。

**丝印**：测试点标网络名/电压；极性与参考。

**治具**：量产用针床/夹具；测试点要能受力；定位孔/边距。

**ICT/FCT**：ICT 测开路/短路/元件值；FCT 测功能；设计要留测试模式/自检。

**可测性设计**：可调/可断开（0Ω/跳线）、可注入（测试点）、可观察（LED/串口）。

**课程**：首板至少留 3.3V/5V/GND/NRST/UART 测试点；调试少拆焊。
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

#### 20.7.1 三个首板案例

**案例一：12V 反接，TVS 烧短路**。现象：上电限流立即到顶。排查：输入 TVS 反接/选错，钳位后短路。整改：换双向 TVS/加反接 MOS，限流上电。

**案例二：MCU 焊反，3.3V 对地 0Ω**。现象：焊完 MCU 阻抗近 0。排查：LQFP 方向错，VDD/VSS 反。整改：返修/换芯片，目视 1 脚标记。

**案例三：SWD 能读 ID，下载失败**。现象：读 ID 成功，Flash 编程报错。排查：BOOT0 高/低不对、Flash 保护、电源跌落。整改：BOOT0 下拉、解除保护、加电容。

**共同点**：都能在“静态检查/限流/顺序”里提前发现；跳过步骤就要用返修来补。

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 320">
  <text x="20" y="28" font-size="16" fill="currentColor">图 20-4：限流上电的电流—电压关系</text>
  <line x1="80" y1="60" x2="80" y2="240" stroke="currentColor" stroke-width="1.5"/>
  <line x1="80" y1="240" x2="660" y2="240" stroke="currentColor" stroke-width="1.5"/>
  <text x="40" y="70" font-size="11" fill="currentColor">电压</text>
  <text x="620" y="265" font-size="11" fill="currentColor">电流</text>
  <path d="M80 210 L200 210 L220 90 L660 90" fill="none" stroke="currentColor" stroke-width="2"/>
  <text x="230" y="82" font-size="10" fill="currentColor">正常：恒压</text>
  <path d="M80 210 L200 210 L220 180 L660 180" fill="none" stroke="currentColor" stroke-width="2" stroke-dasharray="4 3"/>
  <text x="230" y="172" font-size="10" fill="currentColor">短路：限流</text>
  <line x1="200" y1="60" x2="200" y2="240" stroke="currentColor" stroke-width="1" stroke-dasharray="3 3"/>
  <text x="205" y="255" font-size="10" fill="currentColor">开始带载</text>
  <text x="40" y="295" font-size="12" fill="currentColor">限流=预期×1.5；电压被拉低、电流到顶 = 短路/反接，立即断电。</text>
</svg>
```

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 330">
  <text x="20" y="28" font-size="16" fill="currentColor">图 20-5：首板 Bring-Up 十步流程</text>
  <rect x="40" y="55" width="120" height="45" rx="5" fill="none" stroke="currentColor" stroke-width="1.5"/>
  <text x="55" y="82" font-size="10" fill="currentColor">1 目视/阻抗</text>
  <rect x="190" y="55" width="120" height="45" rx="5" fill="none" stroke="currentColor" stroke-width="1.5"/>
  <text x="205" y="82" font-size="10" fill="currentColor">2 电源段</text>
  <rect x="340" y="55" width="120" height="45" rx="5" fill="none" stroke="currentColor" stroke-width="1.5"/>
  <text x="355" y="82" font-size="10" fill="currentColor">3 焊 MCU</text>
  <rect x="490" y="55" width="140" height="45" rx="5" fill="none" stroke="currentColor" stroke-width="1.5"/>
  <text x="505" y="82" font-size="10" fill="currentColor">4 复位/BOOT</text>
  <rect x="490" y="135" width="140" height="45" rx="5" fill="none" stroke="currentColor" stroke-width="1.5"/>
  <text x="505" y="162" font-size="10" fill="currentColor">5 晶振</text>
  <rect x="340" y="135" width="120" height="45" rx="5" fill="none" stroke="currentColor" stroke-width="1.5"/>
  <text x="355" y="162" font-size="10" fill="currentColor">6 SWD ID</text>
  <rect x="190" y="135" width="120" height="45" rx="5" fill="none" stroke="currentColor" stroke-width="1.5"/>
  <text x="205" y="162" font-size="10" fill="currentColor">7 下载 blink</text>
  <rect x="40" y="135" width="120" height="45" rx="5" fill="none" stroke="currentColor" stroke-width="1.5"/>
  <text x="55" y="162" font-size="10" fill="currentColor">8 外设</text>
  <rect x="40" y="215" width="120" height="45" rx="5" fill="none" stroke="currentColor" stroke-width="1.5"/>
  <text x="55" y="242" font-size="10" fill="currentColor">9 通信/负载</text>
  <rect x="190" y="215" width="120" height="45" rx="5" fill="none" stroke="currentColor" stroke-width="1.5"/>
  <text x="205" y="242" font-size="10" fill="currentColor">10 老化</text>
  <line x1="160" y1="77" x2="190" y2="77" stroke="currentColor" stroke-width="1.5"/>
  <line x1="310" y1="77" x2="340" y2="77" stroke="currentColor" stroke-width="1.5"/>
  <line x1="460" y1="77" x2="490" y2="77" stroke="currentColor" stroke-width="1.5"/>
  <line x1="560" y1="100" x2="560" y2="135" stroke="currentColor" stroke-width="1.5"/>
  <line x1="490" y1="157" x2="460" y2="157" stroke="currentColor" stroke-width="1.5"/>
  <line x1="340" y1="157" x2="310" y2="157" stroke="currentColor" stroke-width="1.5"/>
  <line x1="190" y1="157" x2="160" y2="157" stroke="currentColor" stroke-width="1.5"/>
  <line x1="100" y1="180" x2="100" y2="215" stroke="currentColor" stroke-width="1.5"/>
  <line x1="160" y1="237" x2="190" y2="237" stroke="currentColor" stroke-width="1.5"/>
  <text x="40" y="300" font-size="12" fill="currentColor">顺序不能跳；每步有判据，不通过就停在那一步。</text>
</svg>
```

#### 20.7.2 首板上电 12 条红线

1. 不测阻抗就上电。
2. 满压/不限流上电。
3. 先焊 MCU 再测电源。
4. 电源反接/极性错。
5. 复位电容太大/一直拉低。
6. BOOT0 悬空。
7. 晶振负载电容错/不起振。
8. SWD 少地/长线。
9. 限流设太大/太小。
10. 通信不共地/不交叉。
11. 发热不查继续跑。
12. 不记录，问题重复出现。

红线不是“建议”，是“踩了就大概率烧板/返修”。
#### 20.7.3 “时好时坏”的三种典型原因

**接触不良**：连接器/排线/焊点；振动/温度变化就复现；查插拔/补焊。

**电源余量不足**：负载峰值/温度升高时跌压；查纹波/瞬态/线损。

**时序/复位临界**：复位 RC 太大、电源上升慢；冷启动/热启动不同；查波形。

**排查方法**：反复上电/轻敲/冷热；记录“什么条件下坏”；不要只测一次。

**共同点**：不是“芯片玄学”，是接触/余量/时序的边界问题。

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

#### 20.8.5 首板 Bring-Up 复盘清单

1. 上电前测阻抗了吗？
2. 限流设对了吗？
3. 电源段先焊先测了吗？
4. 电流在预算内吗？
5. 复位/BOOT 电平对吗？
6. 晶振起振了吗？
7. SWD 能读 ID 吗？
8. 下载/运行正常吗？
9. 外设逐个验证了吗？
10. 通信共地/交叉/终端对吗？
11. 发热点查了吗？
12. 日志写了吗？
13. 失败原因归档了吗？
14. 下一块板要改什么？

14 条都过，首板才算真的“Bring-Up 完成”；有一条没过，就先别急着加功能；Bring-Up 的耐心，决定了后面返修的次数；慢就是快，尤其是在首板上；先把每一步测明白，再谈功能和进度；这条顺序反过来，代价往往是一次返修，甚至是一块板报废，这些本来都可以避免，只要按顺序、做记录、不跳步，绝大多数事故都不会发生，剩下的那部分也有记录可查，不至于重头再来，也不会把同一个坑再踩一遍，这就是记录的价值。

#### 20.8.6 下一章

下一章讲**硬件测试与可靠性**：板子能跑只是开始，还要验证它在高低温、振动、EMC、寿命下的表现，把“能工作”变成“能交付”。

