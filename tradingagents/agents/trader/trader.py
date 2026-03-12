import functools
import time
import json
from tradingagents.agents.utils.history_tracker import HistoryTracker


def create_trader(llm, memory, history_tracker=None):
    """
    Create a trader node for the trading graph.
    
    Args:
        llm: Language model for generating trading signals
        memory: Memory system for storing past decisions
        history_tracker: Optional HistoryTracker instance for tracking signals
    """
    # Initialize history tracker if not provided
    if history_tracker is None:
        history_tracker = HistoryTracker()
    
    def trader_node(state, name):
        company_name = state["company_of_interest"]
        investment_plan = state["investment_plan"]
        market_research_report = state["market_report"]
        sentiment_report = state["sentiment_report"]
        news_report = state["news_report"]
        fundamentals_report = state["fundamentals_report"]

        curr_situation = f"{market_research_report}\n\n{sentiment_report}\n\n{news_report}\n\n{fundamentals_report}"
        past_memories = memory.get_memories(curr_situation, n_matches=2)

        past_memory_str = ""
        if past_memories:
            for i, rec in enumerate(past_memories, 1):
                past_memory_str += rec["recommendation"] + "\n\n"
        else:
            past_memory_str = "No past memories found."

        # Read recent trading history for the AI to learn from (Last 3 trades as requested)
        recent_history = history_tracker.read_recent_history(n_records=3)
        history_str = history_tracker.format_history_for_ai(recent_history)

        context = {
            "role": "user",
            "content": f"Based on a comprehensive analysis by a team of analysts, here is an investment plan tailored for {company_name}. This plan incorporates insights from current technical market trends, macroeconomic indicators, and social media sentiment. Use this plan as a foundation for evaluating your next trading decision.\n\nProposed Investment Plan: {investment_plan}\n\nLeverage these insights to make an informed and strategic decision.",
        }

        messages = [
            {
                "role": "system",
                "content": f"""You are a Day Trading agent analyzing market data to make INTRADAY investment decisions to secure daily cash flow.
Based on the comprehensive Top-Down analysis, you MUST find the absolute best setup for today and provide a specific recommendation to **BUY** or **SELL**.
You are **NOT ALLOWED to output HOLD**. Every single analysis must result in an actionable entry for today.

If the current market price is not optimal for immediate entry, you MUST formulate a **LIMIT ORDER** (BUY LIMIT or SELL LIMIT) or **STOP ORDER** (BUY STOP or SELL STOP) at a better precise Entry price.

CRITICAL INSTRUCTION FOR STOP LOSS (SL) DISTANCE: 
The absolute distance between your ENTRY price and your SL price MUST be strictly between 5 and 10 units (dollars/points).
- Example 1: ENTRY BUY 5000. SL must be between 4990 and 4995. (e.g. 4992 -> distance is 8. VALID)
- Example 2: ENTRY SELL 4500. SL must be between 4505 and 4510. (e.g. 4507 -> distance is 7. VALID)
- You MUST NEVER set an SL that is more than 10 points away from the entry, nor less than 5 points away.

CRITICAL INSTRUCTION FOR TAKE PROFIT (TP):
You MUST output precise price points with EXACTLY a 1:2 Risk/Reward ratio. NO EXCEPTIONS. (RR ต้อง 1:2 เท่านั้น)
Since your SL distance is 5 to 10 units, your TP distance MUST be EXACTLY DOUBLE your SL distance (10 to 20 units). 

Also, you MUST state the VALIDITY of your setup (e.g., "Valid for 6 hours", "Valid for 12 hours" - keep it intraday).

Your response MUST end with the following exact format:

FINAL TRANSACTION PROPOSAL: **[ORDER TYPE]**
ENTRY: [Exact Price]
SL: [Exact Stop Loss Price]
TP: [Exact Take Profit Price]
VALIDITY: [Timeframe]

Explanation conventions for [ORDER TYPE]:
- **BUY** or **SELL** (Execute at Current Market Price)
- **BUY LIMIT** (Buy lower than current price)
- **SELL LIMIT** (Sell higher than current price)
- **BUY STOP** (Buy higher than current price on breakout)
- **SELL STOP** (Sell lower than current price on breakdown)

Example for BUY LIMIT: ENTRY: 100, SL: 92 (Distance=8), TP: 116 (Distance=16). Risk/Reward = 8/16 = 1:2. VALIDITY: Valid for 6 hours.

Do not forget to utilize lessons from past decisions to learn from your mistakes. Here are some reflections from similar situations you traded in and the lessons learned: {past_memory_str}

---

{history_str}

---

Now provide your best intraday trading signal based on all this analysis to secure today's profit. Use the historical review above to avoid repeating previous failures.""",
            },
            context,
        ]

        result = llm.invoke(messages)

        return {
            "messages": [result],
            "trader_investment_plan": result.content,
            "sender": name,
            "history_tracker": history_tracker,  # Pass tracker to next node
        }

    return functools.partial(trader_node, name="Trader")
