# Comparison: Python Reference vs Our C Implementation

## Python Implementation (calculus_sim_waterTanks_Kp_controller.py)

### Key Characteristics:
1. **Controller Output**: Direct mass flow rate
   ```python
   m_dot1[i] = Kp1 * error1[i-1]  # kg/s
   ```

2. **No Outflow Dynamics**: Pure accumulation model
   - No Torricelli's law
   - No level-dependent outflow
   - Controller has perfect control over volume

3. **Integration (Trapezoidal Rule)**:
   ```python
   volume_Tank1[i] = volume_Tank1[i-1] + (m_dot1[i-1] + m_dot1[i])/(2*density_water)*(dt)
   ```
   - Averages mass flows: `(ṁ[i-1] + ṁ[i])/2`
   - Converts to volume: `/density`
   - Multiplies by time step: `*dt`

## Our C Implementation

### Model 1: Realistic Tank with Torricelli's Law
**Functions**: `tankModel`, `tankModelTrapezoidal`

1. **Controller Output**: Volumetric inflow rate (m³/s)
2. **Physics**: Outflow depends on water level
   - Torricelli's law: `outflow = coeff * sqrt(level)`
   - Net flow = inflow - outflow
3. **More realistic** but different from Python reference

### Model 2: Simplified (Matches Python)
**Functions**: `tankModelTrapezoidalSimplified`, `calculateTankNetFlowSimplified`

1. **Controller Output**: Volumetric flow rate converted to mass flow
2. **No Outflow**: Pure accumulation (matches Python)
3. **Integration**: Identical to Python
   ```c
   massFlow_avg = (previousNetFlow + massFlow_current) / 2.0;
   volumeChange = (massFlow_avg / density) * dt;
   level += volumeChange / area;
   ```

## Key Differences

| Aspect | Python Reference | Our C (Realistic) | Our C (Simplified) |
|--------|------------------|-------------------|-------------------|
| Outflow | None | Torricelli's law | None |
| Control | Direct mass flow | Volumetric inflow | Direct (like Python) |
| Physics | Ideal accumulation | Realistic drainage | Ideal accumulation |
| Matching | - | ❌ | ✅ |

## Usage Recommendations

- **Use Simplified Model** when comparing with Python reference or when you want ideal response
- **Use Realistic Model** for actual water tank systems with drainage
