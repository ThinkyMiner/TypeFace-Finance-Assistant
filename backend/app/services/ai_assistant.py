import google.generativeai as genai
from app.core.config import settings
import json
from datetime import datetime, timedelta

# Configure Gemini
genai.configure(api_key=settings.GEMINI_API_KEY)

SYSTEM_PROMPT = """You are a helpful financial AI assistant. You analyze user transaction data and respond to queries about their finances.

Your responses should ALWAYS be in this JSON format:
{
    "insight": "Your text analysis and insights here",
    "chart": {
        "type": "bar|pie|line|doughnut",
        "title": "Chart title",
        "labels": ["label1", "label2", ...],
        "datasets": [{
            "label": "Dataset name",
            "data": [value1, value2, ...]
        }]
    },
    "recommendations": ["recommendation 1", "recommendation 2", ...]
}

Chart types available:
- bar: For comparisons (e.g., spending by category)
- line: For trends over time
- pie/doughnut: For proportions and distributions

Rules:
1. Always suggest a relevant visualization based on the query
2. Keep insights concise and actionable
3. Provide 2-3 specific recommendations
4. Use real numbers from the transaction data
5. Be encouraging and positive while being honest about spending patterns
"""


def analyze_transactions_with_ai(query: str, transactions: list) -> dict:
    """
    Analyzes transactions using Gemini AI and returns insights with chart configuration
    """
    if not settings.GEMINI_API_KEY:
        return {
            "insight": "AI assistant is not configured. Please add GEMINI_API_KEY to your .env file.",
            "chart": None,
            "recommendations": ["Configure Gemini API to use AI features"]
        }

    # Prepare transaction summary for AI
    transaction_summary = prepare_transaction_summary(transactions)

    # Create the prompt
    user_prompt = f"""
User Query: {query}

Transaction Data Summary:
{transaction_summary}

Analyze this data and respond to the user's query with insights and a recommended visualization.
Remember to respond ONLY with valid JSON in the specified format.
"""

    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content(f"{SYSTEM_PROMPT}\n\n{user_prompt}")

        # Parse the response
        result_text = response.text.strip()

        # Clean up markdown code blocks if present
        if result_text.startswith("```json"):
            result_text = result_text[7:]
        if result_text.startswith("```"):
            result_text = result_text[3:]
        if result_text.endswith("```"):
            result_text = result_text[:-3]

        result = json.loads(result_text.strip())
        return result

    except json.JSONDecodeError as e:
        return {
            "insight": "I analyzed your finances, but had trouble formatting the response. Here's what I found: " + response.text[:200],
            "chart": None,
            "recommendations": ["Try rephrasing your question"]
        }
    except Exception as e:
        return {
            "insight": f"Error analyzing data: {str(e)}",
            "chart": None,
            "recommendations": ["Try again or contact support"]
        }


def prepare_transaction_summary(transactions: list) -> str:
    """
    Prepares a concise summary of transactions for AI analysis
    """
    if not transactions:
        return "No transactions available."

    # Calculate statistics
    total_income = sum(t['amount'] for t in transactions if t['kind'] == 'income')
    total_expense = sum(t['amount'] for t in transactions if t['kind'] == 'expense')
    balance = total_income - total_expense

    # Group by category
    category_spending = {}
    for t in transactions:
        if t['kind'] == 'expense' and t.get('merchant'):
            merchant = t['merchant']
            category_spending[merchant] = category_spending.get(merchant, 0) + t['amount']

    # Get date range
    dates = [t['occurred_on'] for t in transactions]
    date_range = f"from {min(dates)} to {max(dates)}" if dates else "N/A"

    # Build summary
    summary = f"""
Total Transactions: {len(transactions)}
Date Range: {date_range}
Total Income: ${total_income:.2f}
Total Expenses: ${total_expense:.2f}
Balance: ${balance:.2f}

Recent Transactions (last 5):
"""

    for t in transactions[:5]:
        summary += f"- {t['occurred_on']}: {t['kind'].title()} ${t['amount']:.2f}"
        if t.get('merchant'):
            summary += f" at {t['merchant']}"
        summary += "\n"

    if category_spending:
        summary += "\nTop Spending by Merchant:\n"
        sorted_spending = sorted(category_spending.items(), key=lambda x: x[1], reverse=True)[:5]
        for merchant, amount in sorted_spending:
            summary += f"- {merchant}: ${amount:.2f}\n"

    return summary


def get_preset_insights(transactions: list, preset_type: str) -> dict:
    """
    Returns pre-configured insights for common queries
    """
    if preset_type == "overview":
        return generate_overview_insight(transactions)
    elif preset_type == "spending":
        return generate_spending_insight(transactions)
    elif preset_type == "trends":
        return generate_trends_insight(transactions)
    else:
        return analyze_transactions_with_ai(preset_type, transactions)


def generate_overview_insight(transactions: list) -> dict:
    """
    Generates financial overview
    """
    total_income = sum(t['amount'] for t in transactions if t['kind'] == 'income')
    total_expense = sum(t['amount'] for t in transactions if t['kind'] == 'expense')
    balance = total_income - total_expense

    return {
        "insight": f"Your financial overview: You've earned ${total_income:.2f} and spent ${total_expense:.2f}, leaving you with a balance of ${balance:.2f}. {'Great job staying positive!' if balance > 0 else 'Consider ways to reduce expenses or increase income.'}",
        "chart": {
            "type": "doughnut",
            "title": "Income vs Expenses",
            "labels": ["Income", "Expenses"],
            "datasets": [{
                "label": "Amount",
                "data": [total_income, total_expense]
            }]
        },
        "recommendations": [
            "Track all transactions consistently",
            f"{'Keep up the good work!' if balance > 0 else 'Look for areas to cut back'}",
            "Set monthly budgets for different categories"
        ]
    }


def generate_spending_insight(transactions: list) -> dict:
    """
    Analyzes spending by merchant
    """
    category_spending = {}
    for t in transactions:
        if t['kind'] == 'expense':
            merchant = t.get('merchant', 'Other')
            category_spending[merchant] = category_spending.get(merchant, 0) + t['amount']

    sorted_spending = sorted(category_spending.items(), key=lambda x: x[1], reverse=True)[:5]
    labels = [item[0] for item in sorted_spending]
    data = [item[1] for item in sorted_spending]

    top_merchant = sorted_spending[0][0] if sorted_spending else "N/A"
    top_amount = sorted_spending[0][1] if sorted_spending else 0

    return {
        "insight": f"Your top spending category is {top_merchant} with ${top_amount:.2f}. This represents a significant portion of your expenses.",
        "chart": {
            "type": "bar",
            "title": "Top 5 Spending Categories",
            "labels": labels,
            "datasets": [{
                "label": "Amount Spent",
                "data": data
            }]
        },
        "recommendations": [
            f"Review your {top_merchant} spending for potential savings",
            "Set category-specific budgets",
            "Track recurring expenses carefully"
        ]
    }


def generate_trends_insight(transactions: list) -> dict:
    """
    Analyzes spending trends over time
    """
    # Group by date
    daily_spending = {}
    for t in transactions:
        if t['kind'] == 'expense':
            date = t['occurred_on']
            daily_spending[date] = daily_spending.get(date, 0) + t['amount']

    sorted_dates = sorted(daily_spending.items())
    labels = [item[0] for item in sorted_dates]
    data = [item[1] for item in sorted_dates]

    avg_daily = sum(data) / len(data) if data else 0

    return {
        "insight": f"Your average daily spending is ${avg_daily:.2f}. {'Your spending has been relatively consistent.' if len(set(data)) < len(data) * 0.3 else 'Your spending varies significantly day to day.'}",
        "chart": {
            "type": "line",
            "title": "Spending Trend Over Time",
            "labels": labels,
            "datasets": [{
                "label": "Daily Spending",
                "data": data
            }]
        },
        "recommendations": [
            "Monitor daily spending to stay on track",
            "Look for patterns in high-spending days",
            "Consider setting daily spending limits"
        ]
    }
