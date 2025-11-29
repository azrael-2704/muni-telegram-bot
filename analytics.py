import pandas as pd
from sheets import get_client, SHEET_NAME
import logging

logger = logging.getLogger(__name__)

def get_all_data():
    """Fetches all data from the Google Sheet and returns a Pandas DataFrame."""
    client = get_client()
    if not client:
        return None
    
    try:
        spreadsheet = client.open(SHEET_NAME)
        # Iterate over all worksheets to gather data
        all_data = []
        for worksheet in spreadsheet.worksheets():
            data = worksheet.get_all_records()
            if data:
                all_data.extend(data)
        
        if not all_data:
            return pd.DataFrame()
            
        df = pd.DataFrame(all_data)
        # Ensure numeric columns are actually numeric
        df['Amount(g)'] = pd.to_numeric(df['Amount(g)'], errors='coerce')
        df['Price(INR)'] = pd.to_numeric(df['Price(INR)'], errors='coerce')
        df['Timestamp'] = pd.to_datetime(df['Timestamp'])
        return df
    except Exception as e:
        logger.error(f"Error fetching data for analytics: {e}")
        return None

def generate_report(period='weekly'):
    """
    Generates a text summary for the given period.
    period: 'daily', 'weekly', 'monthly'
    """
    df = get_all_data()
    if df is None or df.empty:
        return "No data available."

    now = pd.Timestamp.now()
    
    if period == 'daily':
        start_date = now.normalize()
        period_name = "Today"
    elif period == 'weekly':
        start_date = now - pd.to_timedelta(now.dayofweek, unit='d')
        start_date = start_date.normalize()
        period_name = "This Week"
    elif period == 'monthly':
        start_date = now.replace(day=1).normalize()
        period_name = "This Month"
    else:
        return "Invalid period."

    # Filter data
    mask = df['Timestamp'] >= start_date
    period_df = df.loc[mask]

    if period_df.empty:
        return f"No transactions found for {period_name}."

    # Calculate stats
    sales = period_df[period_df['Action'] == 'Sale']
    buys = period_df[period_df['Action'] == 'Buy']

    total_sales_amount = sales['Amount(g)'].sum()
    total_revenue = sales['Price(INR)'].sum()
    
    total_bought_amount = buys['Amount(g)'].sum()
    total_cost = buys['Price(INR)'].sum()
    
    profit = total_revenue - total_cost

    report = f"📊 **Report: {period_name}**\n\n"
    report += f"**Sales:**\n"
    report += f"• Volume: {total_sales_amount}g\n"
    report += f"• Revenue: {total_revenue} INR\n\n"
    
    report += f"**Purchases:**\n"
    report += f"• Volume: {total_bought_amount}g\n"
    report += f"• Cost: {total_cost} INR\n\n"
    
    report += f"💰 **Net Profit:** {profit} INR"
    
    return report

def generate_detailed_report(period='weekly'):
    """Generates a detailed breakdown by person."""
    df = get_all_data()
    if df is None or df.empty:
        return "No data available."
        
    # Similar filtering logic as above...
    now = pd.Timestamp.now()
    if period == 'daily':
        start_date = now.normalize()
    elif period == 'weekly':
        start_date = now - pd.to_timedelta(now.dayofweek, unit='d')
        start_date = start_date.normalize()
    elif period == 'monthly':
        start_date = now.replace(day=1).normalize()
    else:
        return "Invalid period."

    mask = df['Timestamp'] >= start_date
    period_df = df.loc[mask]
    
    if period_df.empty:
        return "No data."

    # Calculate aggregate stats for the period
    sales = period_df[period_df['Action'] == 'Sale']
    buys = period_df[period_df['Action'] == 'Buy']
    
    total_sales = sales['Price(INR)'].sum()
    total_cost = buys['Price(INR)'].sum()
    profit = total_sales - total_cost
    
    # Volume Stats
    vol_sold = sales['Amount(g)'].sum()
    vol_bought = buys['Amount(g)'].sum()
    
    # Averages
    avg_sale_price = (total_sales / vol_sold) if vol_sold > 0 else 0
    avg_buy_cost = (total_cost / vol_bought) if vol_bought > 0 else 0
    
    # Top Buyer (by Revenue)
    top_buyer = "N/A"
    if not sales.empty:
        top_buyer_stats = sales.groupby('Buyer/Source')['Price(INR)'].sum().sort_values(ascending=False)
        if not top_buyer_stats.empty:
            top_buyer = f"{top_buyer_stats.index[0]} (₹{top_buyer_stats.iloc[0]})"

    report = f"📝 **Detailed Report ({period})**\n\n"
    
    report += f"**💰 Financials:**\n"
    report += f"• Revenue: ₹{total_sales:,.2f}\n"
    report += f"• Cost: ₹{total_cost:,.2f}\n"
    report += f"• Profit: ₹{profit:,.2f}\n\n"
    
    report += f"**📦 Inventory & Volume:**\n"
    report += f"• Sold: {vol_sold}g (Avg: ₹{avg_sale_price:.2f}/g)\n"
    report += f"• Bought: {vol_bought}g (Avg: ₹{avg_buy_cost:.2f}/g)\n"
    report += f"• Txns: {len(sales)} Sales, {len(buys)} Buys\n"
    report += f"• Top Buyer: {top_buyer}\n\n"
    
    report += "**📋 All Transactions:**\n"
    report += "```\n"
    report += f"{'Date':<10} | {'Act':<4} | {'Entity':<10} | {'Amt':<5} | {'Price'}\n"
    report += "-"*50 + "\n"
    
    # Sort by timestamp descending (newest first)
    period_df = period_df.sort_values('Timestamp', ascending=False)
    
    for _, row in period_df.iterrows():
        date_str = row['Timestamp'].strftime('%Y-%m-%d')
        action = "Sale" if row['Action'] == 'Sale' else "Buy"
        action = action[:4] # Truncate
        entity = str(row['Buyer/Source'])[:10]
        amt = str(row['Amount(g)'])
        price = str(row['Price(INR)'])
        
        report += f"{date_str:<10} | {action:<4} | {entity:<10} | {amt:<5} | {price}\n"
        
    report += "```"
    return report

def generate_person_report(person_name):
    """Generates a report for a specific person across all time (or current sheet)."""
    df = get_all_data()
    if df is None or df.empty:
        return "No data available."
        
    # Filter by Seller (case insensitive)
    # df['Seller'] might be mixed case, so we normalize
    mask = df['Seller'].str.lower() == person_name.lower()
    person_df = df.loc[mask]
    
    if person_df.empty:
        return f"No transactions found for '{person_name}'."
        
    sales = person_df[person_df['Action'] == 'Sale']
    buys = person_df[person_df['Action'] == 'Buy']
    
    total_sales_amount = sales['Amount(g)'].sum()
    total_revenue = sales['Price(INR)'].sum()
    
    report = f"👤 **Report for {person_name.title()}**\n\n"
    report += f"**Stats:**\n"
    report += f"• Vol: {total_sales_amount}g\n"
    report += f"• Rev: ₹{total_revenue}\n"
    report += f"• Txns: {len(sales)}\n\n"
    
    if not sales.empty:
        report += "**Recent Sales:**\n"
        report += "```\n"
        report += f"{'Date':<10} | {'Buyer':<10} | {'Amt':<5} | {'Price'}\n"
        report += "-"*42 + "\n"
        
        # Show last 10 sales (increased from 5)
        recent = sales.tail(10)
        for _, row in recent.iterrows():
            date_str = row['Timestamp'].strftime('%Y-%m-%d')
            buyer = str(row['Buyer/Source'])[:10] # Truncate to 10 chars
            amt = str(row['Amount(g)'])
            price = str(row['Price(INR)'])
            
            report += f"{date_str:<10} | {buyer:<10} | {amt:<5} | {price}\n"
        report += "```"

    return report
