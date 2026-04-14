## Trading Strategy Cheat Sheet (Prosperity Round)

### Pattern → Strategy Mapping

**1. Flat Market**

* Signal: price barely moves, tight range
* Strategy: Market Making
* Logic: capture spread repeatedly

**2. Oscillating Market**

* Signal: price moves around a central value
* Strategy: Mean Reversion
* Logic: buy low, sell high around fair price

**3. Trending Market**

* Signal: sustained upward/downward movement
* Strategy: Momentum
* Logic: follow direction, don’t fight it

**4. Noisy / Random Market**

* Signal: erratic zig-zag, no structure
* Strategy: Conservative Market Making
* Logic: avoid prediction, just capture spread

---

### Data-Driven Decision Tools

**1. Mean vs Price**

```python
df["mid_price"].mean()
```

* Price sticks near mean → Mean Reversion
* Price drifts away → Trend

---

**2. Standard Deviation**

```python
df["mid_price"].std()
```

* Low → stable → Market Making
* High → volatile → Directional (MR or Momentum)

---

**3. Rolling Mean**

```python
df["mid_price"].rolling(20).mean()
```

* Frequent crossings → Mean Reversion
* Stays above/below → Trend

---

**4. Differences (Important)**

```python
df["diff"] = df["mid_price"].diff()
df["diff"].mean()
```

* ≈ 0 → Mean Reversion
* > 0 → Uptrend
* < 0 → Downtrend

---

### Advanced Graph Tricks (Real Edge)

**A. Bands (Mean Reversion++)**

* Identify:

  * upper bound
  * mean
  * lower bound

* Rules:

  * touches lower → BUY
  * touches upper → SELL

---

**B. Sticky Levels**

* If price repeatedly returns to a level (e.g., 5000)
* That level = fair price anchor

---

**C. Volatility Zones**

* Pattern: tight → tight → sudden wide swings

* Strategy:

  * tight → market make
  * wide → widen spread / reduce risk

---

**D. Lagging vs Leading**

* Compare:

  * mid price
  * trade price

* If one moves first → use as signal

---

### Quick Decision Checklist

When you see any graph:

1. Is it flat? → Market Making
2. Is it oscillating? → Mean Reversion
3. Is it trending? → Momentum
4. Is it messy/noisy? → Safe Market Making

---

### Key Principle

Edge ≠ more trades
Edge = better trades
