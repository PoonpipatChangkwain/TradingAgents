import functools
import time
import json


def create_trader(llm, memory):
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

        context = {
            "role": "user",
            "content": f"Based on a comprehensive analysis by a team of analysts, here is an investment plan tailored for {company_name}. This plan incorporates insights from current technical market trends, macroeconomic indicators, and social media sentiment. Use this plan as a foundation for evaluating your next trading decision.\n\nProposed Investment Plan: {investment_plan}\n\nLeverage these insights to make an informed and strategic decision.",
        }

        messages = [
            {
                "role": "system",
                "content": f"""You are a trading agent analyzing market data to make intraday investment decisions.
Based on the comprehensive Top-Down analysis, you MUST provide a specific recommendation to **BUY** or **SELL**.
You are **NOT ALLOWED to output HOLD**. Every single analysis must result in an actionable entry.

If the current market price is not optimal for immediate entry, you MUST formulate a **LIMIT ORDER** (BUY LIMIT or SELL LIMIT) or **STOP ORDER** (BUY STOP or SELL STOP) at a better precise Entry price.

CRITICAL INSTRUCTION: You MUST output precise price points with EXACTLY a 1:2 Risk/Reward ratio.
Also, you MUST state the VALIDITY of your setup (e.g., "Valid for 3 days", "Valid for 12 hours").

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

Example for BUY LIMIT: ENTRY: 100, SL: 95 (Risk=5), TP: 110 (Reward=10). Risk/Reward = 5/10 = 1:2. VALIDITY: Valid for 2 days.

Do not forget to utilize lessons from past decisions to learn from your mistakes. Here are some reflections from similar situations you traded in and the lessons learned: {past_memory_str}""",
            },
            context,
        ]

        result = llm.invoke(messages)

        return {
            "messages": [result],
            "trader_investment_plan": result.content,
            "sender": name,
        }

    return functools.partial(trader_node, name="Trader")
