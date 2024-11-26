if __name__ == "__main__":
    coupon_example = Coupon(code="SAVE20", discount=20.0, expiry_date=datetime(2024, 12, 31))
    print(coupon_example.model_dump_json())  # Serialize to JSON

    transaction_example = Transaction(user_id="user_123", amount=50.75, status="completed")
    print(transaction_example.model_dump_json())  # Serialize to JSON

    payment_example = Payment(user_id="user_456", amount=100.0, currency="USD", status="pending")
    print(payment_example.model_dump_json())  # Serialize to JSON

    match_example = Match(home_team="Team A", away_team="Team B", start_time="2024-10-20T15:00:00", sport="Soccer", league="Premier League", odds={"Team A": 1.5, "Team B": 2.5})
    print(match_example.model_dump_json())  # Serialize to JSON
