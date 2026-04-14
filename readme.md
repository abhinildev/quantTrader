### Important points ###
1) If the graph is flat : use market making algo. Logic: Price doesn’t move → capture spread safely
2) If the graph is oscillating: use mean reversion. Logic: prices deviates -> comes back
3) Is it going up and down: use momentum/trend following.
4) Is it random/noising ? Zig-zag chaos use market making only.
Some stats tricks:
    1. mean vs price: df["mid_price"].mean()=> if price stays near mean -> use mean reversion
    2. standard deviation: df["mid_price"].std() => low std->stable-> market making High std -> volatite-> directional
    3. rolling mean: df["mid_price"].rolling(20).mean() => compare prices corsses mean often -> mean reversion prices stays above/below-> trend
    4. Differences(Important): df["diff"] = df["mid_price"].diff()Check: df["diff"].mean()
            ≈ 0 → no trend → mean reversion 0 → upward trend  < 0 → downward trend

