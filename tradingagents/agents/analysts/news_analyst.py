from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import time
import json
from tradingagents.agents.utils.agent_utils import get_news, get_global_news, get_forex_factory_calendar
from tradingagents.dataflows.config import get_config


def create_news_analyst(llm):
    def news_analyst_node(state):
        current_date = state["trade_date"]
        analysis_time = state.get("analysis_time", "Unknown")
        ticker = state["company_of_interest"]

        tools = [
            get_news,
            get_global_news,
            get_forex_factory_calendar,
        ]

        system_message = (
            "You are a news researcher tasked with analyzing recent news and trends over the past week. Please write a comprehensive report of the current state of the world that is relevant for trading and macroeconomics. Use the available tools: get_news(query, start_date, end_date) for company-specific or targeted news searches, and get_global_news(curr_date, look_back_days, limit) for broader macroeconomic news.\n"
            "If the ticker is a Forex pair (e.g. EURUSD) or a Commodity like GOLD/XAUUSD, you MUST use the get_forex_factory_calendar() tool to fetch major US Economic Calendar events for the week. "
            "CRITICAL: Compare the 'Fetched at' time with the event 'Date (UTC)' to determine if an event is in the past or future. "
            "If 'Status: RELEASED' is shown, the news is ALREADY OUT; analyze the 'Actual' vs 'Forecast' / 'Previous' values and describe the market impact (e.g. 'CPI came in higher than expected, strengthening the USD'). "
            "If 'Status: PAST (WAITING API UPDATE)', the event has recently passed but the official 'Actual' figure is not yet in the feed. Look for price action or other news signals to confirm the outcome. "
            "If 'Status: UPCOMING/PENDING', warn about the upcoming volatility. Do not treat released or past news as upcoming."
            "Do not simply state the trends are mixed, provide detailed and finegrained analysis and insights that may help traders make decisions."
            + """ Make sure to append a Markdown table at the end of the report to organize key points in the report, organized and easy to read."""
        )

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are a helpful AI assistant, collaborating with other assistants."
                    " Use the provided tools to progress towards answering the question."
                    " If you are unable to fully answer, that's OK; another assistant with different tools"
                    " will help where you left off. Execute what you can to make progress."
                    " If you or any other assistant has the FINAL TRANSACTION PROPOSAL: **BUY/HOLD/SELL** or deliverable,"
                    " prefix your response with FINAL TRANSACTION PROPOSAL: **BUY/HOLD/SELL** so the team knows to stop."
                    " You have access to the following tools: {tool_names}.\n{system_message}"
                    "For your reference, the current date is {current_date} and the fetch time is {analysis_time}. We are looking at the company {ticker}",
                ),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )

        prompt = prompt.partial(system_message=system_message)
        prompt = prompt.partial(tool_names=", ".join([tool.name for tool in tools]))
        prompt = prompt.partial(current_date=current_date)
        prompt = prompt.partial(analysis_time=analysis_time)
        prompt = prompt.partial(ticker=ticker)

        chain = prompt | llm.bind_tools(tools)
        result = chain.invoke(state["messages"])

        report = ""

        if len(result.tool_calls) == 0:
            report = result.content

        return {
            "messages": [result],
            "news_report": report,
        }

    return news_analyst_node
