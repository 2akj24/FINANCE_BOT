import pandas as pd
from difflib import get_close_matches

# Load data
df = pd.read_csv("Enhanced_Company_Growth_Data.csv")

# Constants
METRICS = ["Total Revenue", "Net Income", "Total Assets", 
          "Total Liabilities", "Cash Flow"]
YEARS = ["2022", "2023", "2024"]
COMPANIES = df['Company'].unique().tolist()

# Context management
_last_company = None

def get_last_company():
    return _last_company

def set_last_company(company):
    global _last_company
    _last_company = company

def get_closest_metric(user_input, valid_metrics):
    """Fuzzy match for metrics"""
    match = get_close_matches(user_input, valid_metrics, n=1, cutoff=0.6)
    return match[0] if match else None

def get_trend(row, metric):
    """Calculate trend for a metric"""
    values = {}
    trend = "stable"
    
    for year in YEARS:
        col = f"{metric} {year}"
        if col in row:
            values[year] = row[col]
    
    if len(values) >= 2:
        years = sorted(values.keys())
        first = values[years[0]]
        last = values[years[-1]]
        if first < last:
            trend = "increasing"
        elif first > last:
            trend = "decreasing"
    
    return values, trend

def generate_summary(company, metric, values, trend):
    """Generate natural language summary"""
    if not values:
        return f"No data available for {metric}"
    
    value_str = ", ".join([f"{year}: ${val:,.2f}" for year, val in values.items()])
    return f"{company}'s {metric} has been {trend} over time ({value_str})"

def export_company_report(company, row):
    """Export data to a text file"""
    filename = f"{company}_report.txt"
    with open(filename, 'w') as f:
        f.write(f"Financial Report for {company}\n")
        f.write("="*40 + "\n")
        f.write(row.to_string())
    print(f"\n✅ Report exported to {filename}")

def compare_companies(df, company1, company2, metric, year):
    """Compare two companies on a metric"""
    col = f"{metric} {year}"
    if col not in df.columns:
        print(f"❌ Metric {col} not found in data")
        return
    
    row1 = df[df['Company'] == company1]
    row2 = df[df['Company'] == company2]
    
    if row1.empty or row2.empty:
        print("❌ One or both companies not found")
        return
    
    val1 = row1.iloc[0][col]
    val2 = row2.iloc[0][col]
    diff = val1 - val2
    pct_diff = (diff / val2) * 100 if val2 != 0 else float('inf')
    
    print(f"\n📊 Comparison: {company1} vs {company2} - {metric} {year}")
    print(f" - {company1}: ${val1:,.2f}")
    print(f" - {company2}: ${val2:,.2f}")
    print(f" - Difference: ${diff:,.2f} ({pct_diff:+.2f}%)")

def parse_question(question):
    """Extract components from user question"""
    q_lower = question.lower()
    components = {
        'companies': [c for c in COMPANIES if c.lower() in q_lower],
        'metrics': [m for m in METRICS if m.lower() in q_lower],
        'years': [y for y in YEARS if y in question],
        'action': None
    }
    
    if "compare" in q_lower:
        components['action'] = 'compare'
    elif "export" in q_lower or "report" in q_lower:
        components['action'] = 'export'
    elif "all data" in q_lower:
        components['action'] = 'show_all'
    elif "growth" in q_lower or "change" in q_lower:
        components['action'] = 'trend'
    
    return components

def display_help():
    """Show help message with examples"""
    print("\n💡 Example Questions You Can Ask:")
    print(" • What is the total revenue of Apple in 2024?")
    print(" • How has net income changed over the last year for Tesla?")
    print(" • Show Microsoft all data")
    print(" • Export report for Apple")
    print(" • Compare Apple and Tesla net income in 2024")
    print(" • What is the cash flow for Microsoft?")
    print(" • Show Tesla revenue (shows all years)")
    print(" • Apple 2023 liabilities")
    print(" • Show me all data for Tesla")
    print(" • help – show this message again")
    print(" • exit – quit the chatbot\n")

def ask_bot():
    print("\n📊 Financial Growth Chatbot")
    print("Ask questions about company financials (Apple, Tesla, Microsoft)")
    print("Type 'help' for examples or 'exit' to quit.\n")

    while True:
        question = input("Ask: ").strip()
        if not question:
            continue
            
        q_lower = question.lower()
        
        if q_lower == "help":
            display_help()
            continue
            
        if q_lower == "exit":
            break

        components = parse_question(question)
        
        # Use last company if none specified
        if not components['companies'] and get_last_company():
            components['companies'] = [get_last_company()]
        
        if not components['companies']:
            print("❌ No company specified. Try like 'Apple revenue 2024'")
            continue
            
        company = components['companies'][0]
        set_last_company(company)
        row = df[df['Company'] == company].iloc[0]
        
        # Handle actions
        if components['action'] == 'export':
            export_company_report(company, df[df['Company'] == company])
            continue
        elif components['action'] == 'show_all':
            print(f"\n📊 Full Data for {company}:")
            print(df[df['Company'] == company].T)
            continue
        elif components['action'] == 'compare':
            if len(components['companies']) >= 2 and components['metrics'] and components['years']:
                compare_companies(df, components['companies'][0], components['companies'][1], 
                                components['metrics'][0], components['years'][0])
            else:
                print("❌ Need two companies, a metric, and a year to compare")
            continue
            
        # Handle metric display
        if not components['metrics']:
            # Try fuzzy matching if no exact metric found
            closest = get_closest_metric(question, METRICS)
            if closest:
                components['metrics'] = [closest]
            else:
                print("❌ No metric specified. Available metrics:")
                print(", ".join(METRICS))
                continue
                
        metric = components['metrics'][0]
        
        # Show specific years or all years
        if components['years']:
            print(f"\n📌 {company} - {metric}:")
            for year in components['years']:
                col = f"{metric} {year}"
                if col in df.columns:
                    print(f" - {year}: ${row[col]:,.2f}")
                else:
                    print(f" - {year}: Data not available")
        else:
            print(f"\n📊 {company} - {metric} (All Years):")
            for year in YEARS:
                col = f"{metric} {year}"
                if col in df.columns:
                    print(f" - {year}: ${row[col]:,.2f}")
                else:
                    print(f" - {year}: Data not available")
        
        # Show trend summary
        values, trend = get_trend(row, metric)
        summary = generate_summary(company, metric, values, trend)
        print(f"\n💬 Summary: {summary}\n")

if __name__ == "__main__":
    ask_bot()
