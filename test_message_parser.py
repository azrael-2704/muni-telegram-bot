import unittest
from message_parser import parse_sales_message

class TestParser(unittest.TestCase):
    def test_valid_sale(self):
        text = "Sold 5 grams to Alice for 500 rupees"
        result = parse_sales_message(text)
        self.assertIsNotNone(result)
        self.assertEqual(result['type'], "Sale")
        self.assertEqual(result['amount'], 5.0)
        self.assertEqual(result['entity'], "Alice")
        self.assertEqual(result['price'], 500.0)

    def test_valid_buy(self):
        text = "Bought 10 grams from Supplier for 800 rupees"
        result = parse_sales_message(text)
        self.assertIsNotNone(result)
        self.assertEqual(result['type'], "Buy")
        self.assertEqual(result['amount'], 10.0)
        self.assertEqual(result['entity'], "Supplier")
        self.assertEqual(result['price'], 800.0)

    def test_with_i_prefix(self):
        text = "I Sold 2.5 gram to Bob for 250.50 rupees"
        result = parse_sales_message(text)
        self.assertIsNotNone(result)
        self.assertEqual(result['amount'], 2.5)

    def test_csv_format_simple(self):
        text = "100, 500"
        result = parse_sales_message(text)
        self.assertIsNotNone(result)
        self.assertEqual(result['type'], "Sale")
        self.assertEqual(result['amount'], 100.0)
        self.assertEqual(result['entity'], "Unknown")
        self.assertEqual(result['price'], 500.0)

    def test_csv_format_with_name(self):
        text = "100, Alice, 500"
        result = parse_sales_message(text)
        self.assertIsNotNone(result)
        self.assertEqual(result['type'], "Sale")
        self.assertEqual(result['amount'], 100.0)
        self.assertEqual(result['entity'], "Alice")
        self.assertEqual(result['price'], 500.0)

    def test_csv_buy_simple(self):
        text = "buy 100, 500"
        result = parse_sales_message(text)
        self.assertIsNotNone(result)
        self.assertEqual(result['type'], "Buy")
        self.assertEqual(result['amount'], 100.0)
        self.assertEqual(result['entity'], "Unknown")
        self.assertEqual(result['price'], 500.0)

    def test_csv_buy_with_name(self):
        text = "Buy, 100, Supplier, 500"
        result = parse_sales_message(text)
        self.assertIsNotNone(result)
        self.assertEqual(result['type'], "Buy")
        self.assertEqual(result['amount'], 100.0)
        self.assertEqual(result['entity'], "Supplier")
        self.assertEqual(result['price'], 500.0)

    def test_invalid_message(self):
        text = "Hello world"
        result = parse_sales_message(text)
        self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main()
