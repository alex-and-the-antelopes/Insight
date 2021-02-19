from parlpy.bills.bill_list_fetcher import BillsOverview

bills_this_session = BillsOverview()
bills_this_session.update_all_bills_in_session()

print(bills_this_session.bills_overview_data)

