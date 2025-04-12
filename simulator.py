import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Settings
initial_equity = 2000
risk_pct = 0.25
rr_ratio = 2
win_rate = 0.75
commission_pct = 0.0003

def simulate_trades():
    equity = initial_equity
    equity_high = equity
    equity_low = equity
    drawdowns = []
    equity_curve = [equity]
    trades = []
    max_dd = 0
    max_equity = equity
    min_equity = equity

    total_profit = 0
    wins = 0
    losses = 0
    win_streak = 0
    max_win_streak = 0
    loss_streak = 0
    max_loss_streak = 0
    consecutive_wins = 0
    consecutive_losses = 0

    current_risk_pct = risk_pct
    base_risk_pct = risk_pct
    reduced_risk_streak = 0

    while equity < 1_000_000:
        trade_outcome = np.random.rand() < win_rate
        risk_amount = equity * current_risk_pct
        gross_profit = risk_amount * rr_ratio if trade_outcome else -risk_amount
        net_profit = gross_profit - (abs(risk_amount) + abs(gross_profit)) * commission_pct
        percent_return = net_profit / equity

        equity += net_profit
        equity_curve.append(equity)
        equity_high = max(equity_high, equity)
        equity_low = min(equity_low, equity)

        # DD tracking
        drawdown = (equity_high - equity) / equity_high
        drawdowns.append(drawdown)

        # Update stats
        if trade_outcome:
            wins += 1
            consecutive_wins += 1
            consecutive_losses = 0
            reduced_risk_streak = 0
            current_risk_pct = base_risk_pct
        else:
            losses += 1
            consecutive_losses += 1
            consecutive_wins = 0
            if reduced_risk_streak == 0:
                current_risk_pct /= 2
            elif reduced_risk_streak >= 2:
                current_risk_pct = min(current_risk_pct, 0.075)
            reduced_risk_streak += 1

        max_win_streak = max(max_win_streak, consecutive_wins)
        max_loss_streak = max(max_loss_streak, consecutive_losses)

        trades.append({
            'Trade': len(trades) + 1,
            'Result': 'Win' if trade_outcome else 'Loss',
            'Risk ($)': f"${risk_amount:.2f}",
            'Risk (%)': f"{current_risk_pct*100:.2f}%",
            'Net P/L ($)': f"${net_profit:.2f}",
            'Gain/Loss (%)': f"{percent_return*100:.2f}%",
            'Equity ($)': f"${equity:.2f}"
        })

        if equity <= 0:
            break

    trade_df = pd.DataFrame(trades)
    
    stats = {
        'Total Net Profit': f"${equity - initial_equity:,.0f}",
        'Wins': f"{wins} ({(wins / len(trades)) * 100:.1f}%)",
        'Losses': f"{losses} ({(losses / len(trades)) * 100:.1f}%)",
        'Average profit': f"${(sum(float(t['Net P/L ($)'].replace('$','')) for t in trades if t['Result']=='Win') / max(wins,1)):.0f}",
        'Average loss': f"${(sum(float(t['Net P/L ($)'].replace('$','')) for t in trades if t['Result']=='Loss') / max(losses,1)):.0f}",
        'Expectancy': f"${(equity - initial_equity) / len(trades):.2f}",
        'Max consecutive wins': f"{max_win_streak}",
        'Max consecutive losses': f"{max_loss_streak}",
        'Equity high value': f"${max(equity_curve):,.0f}",
        'Equity low value': f"${min(equity_curve):,.0f}",
        'Ending Equity': f"${equity:,.0f}",
        'Maximum Draw Down Dollars': f"${max([(max(equity_curve[:i+1]) - e) for i, e in enumerate(equity_curve)]):,.0f}",
        'Maximum Draw Down Percent': f"{max(drawdowns)*100:.1f}%",
        'Max Draw Down/Average Profit': f"{(max(drawdowns)*equity) / max((sum(float(t['Net P/L ($)'].replace('$','')) for t in trades if t['Result']=='Win') / max(wins,1)), 1):.2f}",
        'Profit Factor': f"{(sum(float(t['Net P/L ($)'].replace('$','')) for t in trades if t['Result']=='Win') / abs(sum(float(t['Net P/L ($)'].replace('$','')) for t in trades if t['Result']=='Loss'))):.2f}",
        'Probability of Ruin': f"{100 - (wins / len(trades))*100:.5f}%"
    }

    return equity_curve, trade_df, stats

# Streamlit UI
st.set_page_config(layout="wide")
st.title("Forex Equity Simulator 🚀")

if st.button("Run New Simulation"):
    equity_curve, trade_df, stats = simulate_trades()

    # Equity Curve
    fig, ax = plt.subplots(figsize=(14, 5))
    ax.plot(equity_curve, color='green')
    ax.set_title("Equity Curve")
    ax.set_xlabel("Trade #")
    ax.set_ylabel("Equity ($)")
    st.pyplot(fig)

    # Trade Table
    st.subheader("Trade Log")
    st.dataframe(trade_df, use_container_width=True)

    # Stats
    st.subheader("Trade Performance Summary")
    stats_df = pd.DataFrame(stats.items(), columns=["Metric", "Value"])
    st.table(stats_df)
