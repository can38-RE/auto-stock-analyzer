import baostock as bs

bs.login()

# Check what financial data baostock provides
print("=" * 60)
print("BaoStock Financial Data Fields")
print("=" * 60)

# Test profit data
rs = bs.query_profit_data(code='sh.600519', year=2024, quarter=4)
print("\nProfit Data Fields:")
print(rs.fields)
print("\nSample Data:")
while rs.next():
    print(rs.get_row_data())

# Test operation data
rs = bs.query_operation_data(code='sh.600519', year=2024, quarter=4)
print("\nOperation Data Fields:")
print(rs.fields)

# Test growth data
rs = bs.query_growth_data(code='sh.600519', year=2024, quarter=4)
print("\nGrowth Data Fields:")
print(rs.fields)

# Test balance data
rs = bs.query_balance_data(code='sh.600519', year=2024, quarter=4)
print("\nBalance Data Fields:")
print(rs.fields)

bs.logout()
