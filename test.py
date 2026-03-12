import requests
from datetime import datetime, timezone

def get_forex_factory_calendar_logic(currency_filter: str = "USD") -> str:
    # This is a copy of the logic in forexfactory_tools.py to avoid dependencies
    url = "https://nfs.faireconomy.media/ff_calendar_thisweek.json"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
    }
    
    try:
        # 1. Fix DeprecationWarning by using timezone-aware UTC datetime
        now_utc = datetime.now(timezone.utc)
        current_time_utc_str = now_utc.strftime("%Y-%m-%d %H:%M:%S UTC")
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        events = []
        for item in data:
            currency = item.get("country", "")
            if currency_filter and currency != currency_filter:
                continue
                
            impact = item.get("impact", "")
            if impact.lower() == "low" or impact.lower() == "holiday":
                continue

            date_str = item.get("date", "")
            event_desc = item.get("title", "")
            actual = item.get("actual", "")
            forecast = item.get("forecast", "")
            previous = item.get("previous", "")
            
            # 2. Timezone-aware comparison to check if event has passed
            try:
                # fromisoformat handles strings like '2026-03-11T08:30:00-04:00' perfectly
                event_time = datetime.fromisoformat(date_str)
                is_past = now_utc > event_time
            except ValueError:
                is_past = False
            
            # 3. Accurate status mapping
            if actual:
                status = "RELEASED"
            elif is_past:
                status = "PAST (WAITING API UPDATE)"
            else:
                status = "UPCOMING/PENDING"
            
            event_str = f"Date: {date_str} | Status: {status} | Impact: {impact.upper()} | Event: {event_desc} | "
            event_str += f"Actual: {actual if actual else '---'} | Forecast: {forecast} | Previous: {previous}"
            events.append(event_str)

        if not events:
            return f"No High or Medium impact events found for {currency_filter} this week. (Checked at {current_time_utc_str})"
            
        header = f"ForexFactory Economic Data (Fetched at {current_time_utc_str}):\n"
        header += "NOTE: Times are shown in their original timezone offset. Status is correctly calculated against current UTC.\n"
        header += "=" * 80 + "\n"
        return header + "\n".join(events)
        
    except Exception as e:
        return f"Failed to fetch ForexFactory data: {str(e)}"

def test_forex_factory():
    print("=" * 80)
    print(" TESTING FOREXFACTORY NEWS DATA (USD) - LOGIC ONLY")
    print(f" Local Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    news_data = get_forex_factory_calendar_logic("USD")
    print(news_data)
    
    print("=" * 80)

if __name__ == "__main__":
    test_forex_factory()