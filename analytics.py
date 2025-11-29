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

    # Group by Seller
    report = f"📝 **Detailed Report ({period})**\n"
    
    sellers = period_df['Seller'].unique()
    for seller in sellers:
        seller_df = period_df[period_df['Seller'] == seller]
        sales = seller_df[seller_df['Action'] == 'Sale']
        
        if not sales.empty:
            report += f"\n👤 **{seller}**:\n"
            for _, row in sales.iterrows():
                report += f"  - Sold {row['Amount(g)']}g to {row['Buyer/Source']} for {row['Price(INR)']}\n"
                
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
