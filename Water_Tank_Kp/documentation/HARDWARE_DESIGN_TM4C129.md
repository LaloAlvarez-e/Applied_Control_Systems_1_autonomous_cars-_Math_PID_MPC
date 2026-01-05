# Water Tank Control System - Hardware Design with TM4C129

## System Overview

This document describes the complete hardware implementation of the water tank control system using the **Texas Instruments TM4C129XNCZAD** microcontroller (ARM Cortex-M4F @ 120 MHz).

### System Block Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                     WATER TANK CONTROL SYSTEM                       │
└─────────────────────────────────────────────────────────────────────┘

                    ┌──────────────────────┐
                    │   TM4C129XNCZAD      │
                    │   Microcontroller    │
                    │   (ARM Cortex-M4F)   │
                    └──────────┬───────────┘
                               │
        ┌──────────────────────┼──────────────────────┐
        │                      │                      │
        ▼                      ▼                      ▼
┌───────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ POWER SUPPLY  │    │   SENSORS        │    │  ACTUATORS      │
│               │    │                  │    │                 │
│ • 5V Reg      │    │ • Level Sensor   │    │ • Pump Driver   │
│ • 3.3V Reg    │    │   (Ultrasonic)   │    │   (Relay/MOSFET)│
│ • 12V Input   │    │ • Flow Sensor    │    │ • Valve Driver  │
└───────────────┘    │   (Hall Effect)  │    │   (Solenoid)    │
                     │ • Temperature    │    └─────────────────┘
                     └──────────────────┘
                               │
                     ┌──────────────────┐
                     │  USER INTERFACE  │
                     │                  │
                     │ • LCD Display    │
                     │   (16x2 or OLED) │
                     │ • Buttons/Keys   │
                     │ • Status LEDs    │
                     └──────────────────┘
                               │
                     ┌──────────────────┐
                     │  COMMUNICATION   │
                     │                  │
                     │ • UART (RS-232)  │
                     │ • USB (Debug)    │
                     │ • Ethernet       │
                     └──────────────────┘
```

## Component Selection

### Microcontroller: TM4C129XNCZAD

**Specifications:**
- **Core**: ARM Cortex-M4F with FPU
- **Clock**: 120 MHz
- **Flash**: 1024 KB
- **RAM**: 256 KB
- **Package**: 212-pin NFBGA
- **ADC**: 2x 12-bit, 2 MSPS
- **PWM**: 16 channels
- **GPIO**: ~90 pins
- **Timers**: 8x 32-bit
- **Communication**: UART, SPI, I2C, CAN, USB, Ethernet

**Why TM4C129?**
- Hardware FPU for fast PID calculations
- Multiple ADC channels for sensors
- PWM for pump speed control
- Ethernet for remote monitoring
- Industrial temperature range available

### Sensors

#### 1. Water Level Sensor: **JSN-SR04T** (Waterproof Ultrasonic)

**Specifications:**
- Range: 25-450 cm
- Resolution: 2 mm
- Power: 5V DC
- Current: 8 mA
- Output: TTL digital (Echo pulse)
- Waterproof: IP67

**Connection:**
- VCC → 5V
- Trigger → TM4C129 GPIO (3.3V compatible)
- Echo → TM4C129 Timer Input Capture
- GND → GND

**Alternative**: **MPX5700AP** (Pressure Sensor)
- Range: 0-700 kPa
- Output: Analog 0.2V - 4.7V
- Better for submerged applications

#### 2. Flow Sensor: **YF-S201** (Hall Effect)

**Specifications:**
- Flow range: 1-30 L/min
- Power: 5V DC
- Output: Digital pulse (frequency proportional to flow)
- Material: Food-grade plastic

**Connection:**
- Red → 5V
- Yellow → TM4C129 Timer Input (frequency counter)
- Black → GND

**Calibration:**
- Frequency (Hz) = 7.5 × Flow rate (L/min)
- Pulses per liter ≈ 450

#### 3. Temperature Sensor: **DS18B20** (Optional)

**Specifications:**
- Range: -55°C to +125°C
- Accuracy: ±0.5°C
- Interface: 1-Wire digital
- Waterproof version available

**Connection:**
- VDD → 3.3V or 5V
- Data → TM4C129 GPIO (with 4.7kΩ pull-up)
- GND → GND

### Actuators

#### 1. Water Pump: **12V DC Submersible Pump**

**Specifications:**
- Voltage: 12V DC
- Current: 1-3A (depending on model)
- Flow rate: 2-5 L/min (adjustable with PWM)
- Head: 2-3 meters

**Driver Circuit**: See schematic below (MOSFET-based)

#### 2. Solenoid Valve: **12V DC 1/2" Electric Solenoid**

**Specifications:**
- Voltage: 12V DC
- Current: 0.5-1A
- Port size: 1/2" NPT
- Normally closed (NC) or normally open (NO)

**Driver Circuit**: See schematic below (Relay or MOSFET with flyback diode)

### User Interface

#### 1. Display: **16x2 LCD with I2C Backpack** or **SSD1306 OLED**

**Option A: HD44780 16x2 LCD**
- Interface: I2C (PCF8574)
- Power: 5V
- Displays: Level %, setpoint, controller type

**Option B: SSD1306 128x64 OLED**
- Interface: I2C or SPI
- Power: 3.3V
- Better graphics capability

#### 2. User Input

- **4 Push Buttons**: Up, Down, Select, Mode
- **Rotary Encoder** (optional): For easier setpoint adjustment
- **3 Status LEDs**: Power, Error, Running

## Detailed Schematic

### 1. Power Supply Circuit

```
12V DC Input (from wall adapter or battery)
    │
    ├──────────────────────────────────► To Pump/Valve Drivers (12V)
    │
    ├────[C1 470µF]─── GND
    │
    ├────[7805 Regulator]────► 5V Rail (for sensors, LCD)
    │        │
    │        └──[C2 100µF]─── GND
    │        │
    │        └──[C3 0.1µF]─── GND
    │
    └────[AMS1117-3.3 Regulator]────► 3.3V Rail (for TM4C129)
             │
             ├──[C4 10µF]─── GND
             └──[C5 0.1µF]─── GND

Components:
- C1: 470µF/25V electrolytic (input filter)
- C2: 100µF/10V electrolytic (5V output)
- C3: 0.1µF ceramic (5V bypass)
- C4: 10µF tantalum (3.3V output)
- C5: 0.1µF ceramic (3.3V bypass)
- 7805: 5V 1A linear regulator (TO-220)
- AMS1117-3.3: 3.3V 1A LDO regulator (SOT-223)
```

**Notes:**
- Add heatsinks to regulators if current > 500mA
- Use switching regulators (LM2596, MP1584) for better efficiency
- Power consumption estimate: 200-300mA @ 12V

### 2. TM4C129 Core Circuit

```
┌─────────────────────────────────────────────────────────────────┐
│                    TM4C129XNCZAD (212-pin NFBGA)                │
│                                                                  │
│  VDD (multiple pins) ────[0.1µF]─── GND (each VDD pin)          │
│  VDDA ────[10µF + 0.1µF]─── GND                                 │
│  VDDC ────[10µF + 0.1µF]─── GND (internal regulator output)    │
│                                                                  │
│  OSC0 ────[25MHz Crystal]────┬─── OSC1                          │
│                              │                                  │
│                         [18pF][18pF]                            │
│                              │  │                               │
│                             GND GND                             │
│                                                                  │
│  RESET ────[10kΩ pull-up]─── VDD                                │
│        └───[Button]─── GND                                      │
│                                                                  │
│  DEBUG (JTAG/SWD):                                              │
│    TCK/SWCLK ────► Pin for debugger                             │
│    TMS/SWDIO ────► Pin for debugger                             │
│    TDO/SWO ───────► Pin for debugger                            │
│    TDI ───────────► Pin for debugger (optional)                 │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘

Decoupling Capacitors:
- Place 0.1µF ceramic capacitor near EACH VDD pin (critical!)
- Place 10µF tantalum near power entry points
- Keep traces short and wide
```

### 3. Level Sensor Interface (JSN-SR04T Ultrasonic)

```
JSN-SR04T Module                 TM4C129XNCZAD
┌─────────────┐                  ┌──────────────┐
│    VCC      │ ◄────── 5V       │              │
│    Trig     │ ◄────── PB4 ─────┤ GPIO Output  │
│    Echo     │ ─────────────────┤ Timer Input  │ (PE4 - Timer 3A)
│    GND      │ ◄────── GND      │  Capture     │
└─────────────┘                  └──────────────┘
             │
             └──[1kΩ + 2kΩ voltage divider]──► Echo signal (if 5V)
                    (Optional - JSN-SR04T is usually 3.3V compatible)

Timing:
1. Send 10µs pulse to Trigger
2. Measure Echo pulse width (50µs - 25ms)
3. Distance (cm) = Echo width (µs) / 58
4. Level (m) = Tank height - Distance

Interrupt Configuration:
- Use Timer 3A in edge-time capture mode
- Capture both rising and falling edges
- Calculate pulse width in ISR
```

### 4. Flow Sensor Interface (YF-S201)

```
YF-S201 Module                   TM4C129XNCZAD
┌─────────────┐                  ┌──────────────┐
│  Red (VCC)  │ ◄────── 5V       │              │
│ Yellow (Sig)│ ─────────────────┤ Timer Input  │ (PF0 - Timer 0A)
│ Black (GND) │ ◄────── GND      │  Counter     │
└─────────────┘                  └──────────────┘
             │
             └──[1kΩ resistor + 0.1µF cap to GND] (debounce)

Frequency Measurement:
- Use Timer 0A in edge count mode
- Count pulses over 1 second intervals
- Flow rate (L/min) = Pulse count / (7.5 × 60)
- Or use Input Capture for period measurement

ISR:
- Increment counter on each rising edge
- Main loop reads counter every 1s and calculates flow
```

### 5. Pump Driver Circuit (PWM Control)

```
                              +12V
                               │
                               │
                          ┌────┴────┐
                          │ PUMP    │  (12V DC, 1-3A)
                          │ Motor   │
                          └────┬────┘
                               │
                             Drain
                          ┌────┴────┐
                          │ MOSFET  │  IRF540N (N-channel)
                          │         │  (Vds=100V, Id=33A, Rds=44mΩ)
                          └────┬────┘
                             Source  │
                          ┌────┴────┐│
                          │ Flyback ││
                          │ Diode   ││ 1N4007 (or Schottky for faster switching)
                          └────┬────┘│
                               │     │
                              GND ◄──┘

         TM4C129 PWM
         (PF2 - M0PWM2)
              │
              ├───[1kΩ]─────┬─── Gate
              │             │
              │          [10kΩ]
              │             │
              │            GND
              │
         [Optional: Gate driver IC for faster switching]
         [Use TC4427 or similar for >1kHz PWM]

PWM Configuration:
- Frequency: 1-20 kHz (10 kHz recommended)
- Duty cycle: 0-100%
- Dead time: Not needed (single switch)
- Current sense: Optional 0.1Ω shunt resistor in series with source

Protection:
- Flyback diode (1N4007 or 1N5819 Schottky)
- Optional: Fuse (3A fast-blow)
- Optional: Overcurrent detection via op-amp comparator
```

### 6. Solenoid Valve Driver (Relay or MOSFET)

**Option A: Relay Driver (Simpler, Click noise)**

```
         TM4C129 GPIO                    +12V
         (PG0)                            │
              │                      ┌────┴────┐
              ├───[1kΩ]─────┬─── Base   │ SOLENOID │  (12V, 0.5-1A)
              │             │    │   │  VALVE   │
              │          [NPN]   │   └────┬─────┘
              │        2N2222    │        │
              │             │ Emitter    │
              │             └─── GND     │
              │                  │       │
              │              ┌───┴───────┤
              │              │  Relay    │
              │              │  Coil     │
              │              │ (12V)     │
              │              └───┬───────┘
              │                  │
              │              [Flyback]
              │              [Diode  ]
              │              [1N4007 ]
              │                  │
              │                 GND

Relay: SPDT 10A/250VAC (e.g., Omron G5LE-1-12VDC)
```

**Option B: MOSFET Driver (Silent, Faster)**

```
         TM4C129 GPIO                    +12V
         (PG0)                            │
              │                      ┌────┴────┐
              ├───[1kΩ]─────┬─── Gate  │ SOLENOID │
              │             │    │   │  VALVE   │
              │          [MOSFET]  │   └────┬─────┘
              │          IRF540N   │        │
              │             │ Source   [Flyback]
              │             └─── GND  [Diode  ]
              │                  │    [1N4007 ]
             [10kΩ]              │        │
              │                  └────────┴───► GND
             GND

Flyback diode essential for inductive load!
```

### 7. User Interface Connections

#### LCD Display (16x2 with I2C Backpack)

```
LCD with PCF8574                 TM4C129XNCZAD
┌─────────────┐                  ┌──────────────┐
│    VCC      │ ◄────── 5V       │              │
│    SDA      │ ◄──────[330Ω]────┤ PB3 (I2C0)   │
│    SCL      │ ◄──────[330Ω]────┤ PB2 (I2C0)   │
│    GND      │ ◄────── GND      │  SDA/SCL     │
└─────────────┘                  └──────────────┘
         │
    [4.7kΩ pull-ups on SDA and SCL to 5V]

I2C Configuration:
- Speed: 100 kHz (standard) or 400 kHz (fast)
- Address: 0x27 or 0x3F (check your module)
- Series resistors protect 3.3V GPIO from 5V I2C bus
```

#### Push Buttons

```
         TM4C129 GPIO
         (PD0-PD3)                 +3.3V
              │                      │
         [PD0]├───[Button]───┬──[10kΩ]  (UP)
              │              │
         [PD1]├───[Button]───┼──[10kΩ]  (DOWN)
              │              │
         [PD2]├───[Button]───┼──[10kΩ]  (SELECT)
              │              │
         [PD3]├───[Button]───┴──[10kΩ]  (MODE)
              │
             GND

Configuration:
- Internal pull-ups can be used instead of external resistors
- Add 0.1µF capacitor across each button for debouncing
- Or use software debouncing (20-50ms delay)
```

#### Status LEDs

```
         TM4C129 GPIO              +3.3V
         (PN0-PN2)                   │
              │                  [470Ω]
         [PN0]├────[470Ω]─────[LED Green]─── GND  (Power/Running)
              │                  [470Ω]
         [PN1]├────[470Ω]─────[LED Yellow]── GND  (Warning)
              │                  [470Ω]
         [PN2]├────[470Ω]─────[LED Red]───── GND  (Error)

LED Current: ~5mA each (safe for GPIO direct drive)
```

### 8. Communication Interfaces

#### UART (RS-232)

```
TM4C129 UART0                MAX3232 (RS-232 Transceiver)              DB9 Connector
┌──────────────┐             ┌───────────────────┐                    ┌─────────┐
│ PA0 (U0RX)   │ ────────────┤ T1IN          T1OUT├────────────────────│ Pin 2   │ RX
│ PA1 (U0TX)   │ ────────────┤ R1OUT         R1IN ├────────────────────│ Pin 3   │ TX
└──────────────┘             │                    │                    │ Pin 5   │ GND
                             │ VCC = 3.3V         │                    └─────────┘
                             │ C1+ C1- C2+ C2-    │
                             │ [0.1µF caps]       │
                             └────────────────────┘

Baud Rate: 115200 bps (configurable)
Data: 8 bits, No parity, 1 stop bit
```

#### USB (Device Mode - Virtual COM Port)

```
TM4C129 USB0                 USB Micro-B Connector
┌──────────────┐             ┌──────────────┐
│ PD4 (USB0DM) │ ────────────┤ D-           │
│ PD5 (USB0DP) │ ────────────┤ D+           │
│              │             │ VCC (5V)     │ ─► Can power board
│              │             │ GND          │
└──────────────┘             └──────────────┘

Components:
- No external USB PHY needed (built-in)
- Add ESD protection diodes (optional but recommended)
- Ferrite bead on USB VCC for noise filtering
```

#### Ethernet (For remote monitoring)

```
TM4C129 Ethernet             DP83848 PHY                RJ45 with Magnetics
┌──────────────┐             ┌──────────────┐           ┌──────────────┐
│ PF1 (EN0LED0)│ ────────────│ Link LED     │           │              │
│ PF0 (EN0LED1)│ ────────────│ Activity LED │           │   Ethernet   │
│              │             │              │           │   Jack       │
│ RMII Bus     │◄───────────►│ RMII         │◄─────────►│   with       │
│ (Multiple    │             │ Interface    │           │   Magnetics  │
│  pins)       │             │              │           │              │
└──────────────┘             └──────────────┘           └──────────────┘

PHY Configuration:
- RMII mode (fewer pins than MII)
- 50MHz clock from TM4C129
- PHY address: 0x01 (default)
- Use module like ENC28J60 or built-in Ethernet PHY
```

## Pin Assignment Table

| Pin Name | TM4C129 Pin | Function | Connected To |
|----------|-------------|----------|--------------|
| **Sensors** | | | |
| LEVEL_TRIG | PB4 | GPIO Output | Ultrasonic Trigger |
| LEVEL_ECHO | PE4 | Timer 3A Input | Ultrasonic Echo |
| FLOW_IN | PF0 | Timer 0A Counter | Flow Sensor Pulse |
| TEMP_DATA | PB5 | 1-Wire GPIO | DS18B20 Data |
| **Actuators** | | | |
| PUMP_PWM | PF2 | PWM (M0PWM2) | Pump MOSFET Gate |
| VALVE_CTRL | PG0 | GPIO Output | Solenoid Driver |
| **User Interface** | | | |
| LCD_SDA | PB3 | I2C0 SDA | LCD I2C Data |
| LCD_SCL | PB2 | I2C0 SCL | LCD I2C Clock |
| BTN_UP | PD0 | GPIO Input | Button Up |
| BTN_DOWN | PD1 | GPIO Input | Button Down |
| BTN_SELECT | PD2 | GPIO Input | Button Select |
| BTN_MODE | PD3 | GPIO Input | Button Mode |
| LED_RUN | PN0 | GPIO Output | Green LED |
| LED_WARN | PN1 | GPIO Output | Yellow LED |
| LED_ERROR | PN2 | GPIO Output | Red LED |
| **Communication** | | | |
| UART_RX | PA0 | UART0 RX | RS-232 RX |
| UART_TX | PA1 | UART0 TX | RS-232 TX |
| USB_DM | PD4 | USB0 D- | USB Data - |
| USB_DP | PD5 | USB0 D+ | USB Data + |
| **Debug** | | | |
| SWCLK | PC0 | JTAG/SWD | Debugger Clock |
| SWDIO | PC1 | JTAG/SWD | Debugger Data |

## PCB Layout Considerations

### Layer Stack (Recommended 4-layer)

```
Layer 1: Top - Signal, Components
Layer 2: Ground Plane (continuous)
Layer 3: Power Plane (3.3V, 5V regions)
Layer 4: Bottom - Signal, Components
```

### Design Guidelines

1. **Power Distribution**
   - Keep 3.3V and 5V separate
   - Use copper pours for power planes
   - Decouple every IC with 0.1µF ceramic capacitor (close to VCC pin)

2. **High-Speed Signals**
   - Keep RMII/USB traces short and equal length
   - Use differential pair routing for USB D+/D-
   - Avoid routing high-speed signals over splits in ground plane

3. **Analog Signals**
   - Keep ADC traces short and away from digital switching signals
   - Use ground guard rings around analog sections
   - Separate AGND and DGND, connect at single point

4. **Power Traces**
   - Use wide traces for 12V pump power (≥50 mil)
   - Use Kelvin connection for current sensing
   - Add test points for voltage rails

5. **Connector Placement**
   - Group by function (sensors, power, communication)
   - Use screw terminals for high-current connections
   - Add mounting holes (M3 or #4-40)

## Bill of Materials (BOM)

### Microcontroller & Core Components

| Qty | Part Number | Description | Package | Supplier |
|-----|-------------|-------------|---------|----------|
| 1 | TM4C129XNCZAD | MCU ARM Cortex-M4F 120MHz | 212-NFBGA | Digi-Key, Mouser |
| 1 | 25MHz | Crystal oscillator | HC-49 | Any |
| 2 | 18pF | Ceramic capacitor | 0805 | Any |
| 10 | 0.1µF | Ceramic capacitor (decoupling) | 0805 | Any |
| 5 | 10µF | Tantalum capacitor | 1206 | Any |

### Power Supply

| Qty | Part Number | Description | Package | Supplier |
|-----|-------------|-------------|---------|----------|
| 1 | 7805 | 5V 1A Linear Regulator | TO-220 | Any |
| 1 | AMS1117-3.3 | 3.3V 1A LDO Regulator | SOT-223 | Any |
| 1 | 470µF/25V | Electrolytic capacitor | Radial | Any |
| 2 | 100µF/10V | Electrolytic capacitor | Radial | Any |
| 1 | 12V 3A | Wall adapter | Barrel jack | Any |

### Sensors

| Qty | Part Number | Description | Supplier |
|-----|-------------|-------------|----------|
| 1 | JSN-SR04T | Waterproof ultrasonic sensor | AliExpress, Amazon |
| 1 | YF-S201 | Hall effect flow sensor | AliExpress, Amazon |
| 1 | DS18B20 | Waterproof temp sensor (optional) | Digi-Key, Mouser |

### Actuators & Drivers

| Qty | Part Number | Description | Package | Supplier |
|-----|-------------|-------------|---------|----------|
| 1 | 12V DC Pump | Submersible water pump 2-5 L/min | - | Amazon |
| 1 | 12V Solenoid | 1/2" electric valve NC | - | Amazon |
| 2 | IRF540N | N-Channel MOSFET 100V 33A | TO-220 | Digi-Key, Mouser |
| 2 | 1N4007 | Flyback diode 1A 1000V | DO-41 | Any |
| 1 | 2N2222 | NPN Transistor (relay driver) | TO-92 | Any |

### User Interface

| Qty | Part Number | Description | Supplier |
|-----|-------------|-------------|----------|
| 1 | 1602 LCD + I2C | 16x2 character LCD with I2C backpack | Amazon |
| 4 | Tactile Switch | 6mm push button | Any |
| 3 | LED 3mm | Red, Yellow, Green | Any |
| 7 | 10kΩ | Resistor (pull-up) | 0805 | Any |
| 3 | 470Ω | Resistor (LED current limit) | 0805 | Any |

### Communication

| Qty | Part Number | Description | Package | Supplier |
|-----|-------------|-------------|---------|----------|
| 1 | MAX3232 | RS-232 transceiver | SOIC-16 | Digi-Key, Mouser |
| 5 | 0.1µF | Capacitor for MAX3232 | 0805 | Any |
| 1 | DB9 Female | RS-232 connector | - | Any |
| 1 | USB Micro-B | USB connector | SMD | Any |

### Miscellaneous

| Qty | Description | Notes |
|-----|-------------|-------|
| 1 | PCB | 4-layer, ~100x100mm |
| 1 | Enclosure | IP54 rated for industrial use |
| 4 | M3 Standoffs | PCB mounting |
| 1 | Heatsink | For 7805 if needed |
| - | Screw terminals | For sensor/actuator connections |
| - | Wire | 18-22 AWG for power, 24-28 AWG for signals |

**Total estimated cost**: ~$80-120 USD (excluding PCB fabrication)

## Software Integration

### TivaWare Library Usage

```c
// Initialize system clock to 120MHz
SysCtlClockFreqSet((SYSCTL_XTAL_25MHZ | SYSCTL_OSC_MAIN |
                    SYSCTL_USE_PLL | SYSCTL_CFG_VCO_480), 120000000);

// Configure PWM for pump control
PWMGenConfigure(PWM0_BASE, PWM_GEN_1, PWM_GEN_MODE_DOWN);
PWMGenPeriodSet(PWM0_BASE, PWM_GEN_1, period);
PWMGenEnable(PWM0_BASE, PWM_GEN_1);

// Configure Timer for ultrasonic measurement
TimerConfigure(TIMER3_BASE, TIMER_CFG_SPLIT_PAIR | TIMER_CFG_A_CAP_TIME_UP);
TimerIntEnable(TIMER3_BASE, TIMER_CAPA_EVENT);

// Configure I2C for LCD
I2CMasterInitExpClk(I2C0_BASE, SysCtlClockGet(), false);
```

### Real-time Control Loop

```c
void ControlTask(void) {
    static uint32_t lastTime = 0;
    uint32_t currentTime = xTaskGetTickCount();
    
    if (currentTime - lastTime >= pdMS_TO_TICKS(40)) {  // 40ms = 25Hz
        lastTime = currentTime;
        
        // Read sensors
        float currentLevel = ReadLevelSensor();  // Returns 0-100%
        float flowRate = ReadFlowSensor();       // Returns L/min
        
        // PID calculation (reuse existing controller.c functions)
        float error = setpoint - currentLevel;
        float controlOutput = pidController(&controller, error, 0.04);
        
        // Apply control signal
        SetPumpPWM(controlOutput);  // 0-100% PWM duty cycle
        
        // Update display
        UpdateLCD(currentLevel, setpoint, flowRate);
        
        // Send data via UART/Ethernet
        SendTelemetry(currentLevel, setpoint, controlOutput);
    }
}
```

## Testing & Calibration

### 1. Power-On Test
- Verify all voltage rails: 12V, 5V, 3.3V
- Check for excessive current draw
- Verify LED indicators

### 2. Sensor Calibration

**Level Sensor:**
```c
// Empty tank: measure distance to bottom
float emptyDistance = 450.0;  // cm
// Full tank: measure distance to full level
float fullDistance = 50.0;    // cm
// Calculate percentage
float level_percent = 100.0 * (emptyDistance - currentDistance) / 
                              (emptyDistance - fullDistance);
```

**Flow Sensor:**
```c
// Collect known volume (e.g., 1 liter) and count pulses
// Adjust calibration factor
float calibrationFactor = pulsesPerLiter / 450.0;
float flowRate_Lmin = (pulseCount / calibrationFactor) / 60.0;
```

### 3. Controller Tuning

Start with conservative gains:
```c
// Initial PID gains (from simulation)
Kp = 0.35;
Ki = 0.08;
Kd = 0.50;

// Scale for hardware response
// May need adjustment based on pump/valve characteristics
```

### 4. Safety Tests

- Emergency stop button
- Overflow detection
- Pump dry-run protection
- Power supply brownout handling

## Safety & Protection Features

### Hardware Protection

1. **Overcurrent Protection**
   - 3A fuse on 12V input
   - Current sense resistor (0.1Ω) for pump
   - Software current limit

2. **Reverse Polarity Protection**
   - Schottky diode (3A) on 12V input
   - Or use P-channel MOSFET circuit

3. **ESD Protection**
   - TVS diodes on all external connections
   - Especially critical for sensors and USB

4. **Thermal Protection**
   - Temperature sensor monitoring
   - Automatic shutdown if overheating
   - Thermal fuse on power regulators

### Software Protection

```c
// Maximum run time without flow detection
#define MAX_DRY_RUN_TIME_MS 5000

// Overflow level (95%)
#define OVERFLOW_THRESHOLD 95.0

// Safety monitoring in main loop
if (currentLevel > OVERFLOW_THRESHOLD) {
    StopPump();
    ActivateAlarm();
}

if (pumpRunning && flowRate < 0.1 && runTime > MAX_DRY_RUN_TIME_MS) {
    StopPump();  // Prevent pump damage
    SetErrorCode(ERROR_PUMP_DRY_RUN);
}
```

## Enclosure & Mechanical Design

### Recommended Enclosure

- **Type**: Plastic IP54 rated enclosure
- **Size**: 150mm x 100mm x 60mm (WxHxD)
- **Material**: ABS or polycarbonate
- **Mounting**: DIN rail or wall mount brackets

### Panel Cutouts

- LCD display window: 71mm x 25mm
- 4 push buttons: 6mm holes
- 3 status LEDs: 3mm holes
- DB9 connector: D-sub cutout
- USB connector: Micro-B cutout
- Cable glands: M12 or PG7 for sensor cables
- Power jack: 8mm hole

### Cable Management

- Use IP67 cable glands for sensor connections
- Separate low-voltage signal cables from 12V power cables
- Use shielded cable for long sensor runs (>2m)
- Label all cables clearly

## Firmware Development

### Development Tools

- **IDE**: Code Composer Studio (CCS) or Keil MDK
- **Debugger**: Tiva C Series LaunchPad (as debugger/programmer)
- **Library**: TivaWare Peripheral Driver Library
- **RTOS**: FreeRTOS (optional but recommended)

### Project Structure

```
firmware/
├── src/
│   ├── main.c              # Main application
│   ├── controller.c        # PID controller (reuse from simulation)
│   ├── sensors.c           # Sensor interface drivers
│   ├── actuators.c         # Pump/valve drivers
│   ├── display.c           # LCD/UI handling
│   ├── communication.c     # UART/USB/Ethernet
│   └── safety.c            # Safety monitoring
├── inc/
│   └── [header files]
├── TivaWare/              # TI peripheral library
└── startup/
    └── startup_TM4C129.c   # Vector table & startup code
```

### Memory Usage Estimate

- **Flash**: ~50-100 KB (with TivaWare)
- **RAM**: ~10-20 KB (buffers, stacks, data)
- **Plenty of headroom** (1 MB Flash, 256 KB RAM available)

## Conclusion

This hardware design provides a complete, production-ready solution for implementing the water tank control system on the TM4C129 microcontroller. The modular design allows for easy testing and debugging of individual components.

### Next Steps

1. **PCB Design**: Create schematic and layout in KiCad/Altium/Eagle
2. **Prototype**: Order PCB and components, hand-assemble first prototype
3. **Firmware Development**: Port C simulation code to embedded platform
4. **Testing**: Bench test with dummy loads before connecting real tank
5. **Calibration**: Fine-tune sensor readings and controller gains
6. **Deployment**: Install in actual water tank system

### Additional Resources

- **TM4C129 Datasheet**: [TI Website](https://www.ti.com/product/TM4C129XNCZAD)
- **TivaWare User's Guide**: TI documentation
- **Application Notes**: TI provides many AN's for sensor interfacing
- **Community**: TI E2E forums, EEVblog forums

---

**Document Version**: 1.0  
**Last Updated**: January 4, 2026  
**Author**: Applied Control Systems Course - Hardware Implementation
