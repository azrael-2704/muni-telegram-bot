import re

def parse_sales_message(message_text):
    """
    Parses a message string to extract sales or purchase details.
    
    Formats:
    1. Sale: "I Sold <amount> gram to <buyer> for <price> rupees"
    2. Buy:  "I Bought <amount> gram from <seller> for <price> rupees"
    
    Returns a dict with 'type', 'amount', 'entity', 'price' if matched, else None.
    """
    # Regex patterns
    # Flexible: "I Sold" or just "Sold", "gram" or "grams"
    # (?i) flag for case insensitive is handled by re.IGNORECASE
    
    # Pattern: (I )?Sold <amount> gram(s)? to <buyer> for <price> rupees
    sale_pattern = r"(?:I\s+)?Sold\s+(\d+(?:\.\d+)?)\s+grams?\s+to\s+(.+)\s+for\s+(\d+(?:\.\d+)?)\s+rupees"
    
    # Pattern: (I )?Bought <amount> gram(s)? from <seller> for <price> rupees
    buy_pattern = r"(?:I\s+)?Bought\s+(\d+(?:\.\d+)?)\s+grams?\s+from\s+(.+)\s+for\s+(\d+(?:\.\d+)?)\s+rupees"
    
    # Check for Sale
    sale_match = re.search(sale_pattern, message_text, re.IGNORECASE)
    if sale_match:
        return {
            "type": "Sale",
            "amount": float(sale_match.group(1)),
            "entity": sale_match.group(2).strip(), # Buyer
            "price": float(sale_match.group(3))
        }

    # Check for Buy
    buy_match = re.search(buy_pattern, message_text, re.IGNORECASE)
    if buy_match:
        return {
            "type": "Buy",
            "amount": float(buy_match.group(1)),
            "entity": buy_match.group(2).strip(), # Seller/Source
            "price": float(buy_match.group(3))
        }

    # Check for CSV format (Sale or Buy)
    # Pattern: [Buy] <amount>, <optional_name>, <price>
    try:
        # Check for explicit "buy" prefix
        text_to_parse = message_text
        transaction_type = "Sale"
        
        # Check if starts with "buy" (case insensitive)
        # We look for "buy" followed by space or comma
        if re.match(r'^buy[\s,]+', message_text, re.IGNORECASE):
            transaction_type = "Buy"
            # Remove the "buy" prefix and any following delimiters
            text_to_parse = re.sub(r'^buy[\s,]+', '', message_text, flags=re.IGNORECASE)

        parts = [p.strip() for p in text_to_parse.split(',')]
        if len(parts) >= 2:
            # Check if first part is a number
            amount = float(parts[0])
            
            if len(parts) == 2:
                # <amount>, <price>
                price = float(parts[1])
                entity = "Unknown"
                return {"type": transaction_type, "amount": amount, "entity": entity, "price": price}
            
            elif len(parts) == 3:
                # <amount>, <name>, <price>
                # Check if 3rd part is number
                price = float(parts[2])
                entity = parts[1]
                return {"type": transaction_type, "amount": amount, "entity": entity, "price": price}
                
    except ValueError:
        pass # Not a CSV number format
        
    return None
        
    return None
