from integrations.square.square_client import SquareClient


LOCATION_ID = "LCQJDMZ076NK1"
CATALOG_OBJECT_ID = "CHI74NB3HRW3WABQQJ2RUX42"

NUMBER_OF_SALES = 10
AMOUNT_PER_UNIT = 350


def main():
    client = SquareClient()

    print("=" * 60)
    print("SMARTSTOCK AI - SANDBOX SALES GENERATOR")
    print("=" * 60)

    successful = 0

    for i in range(1, NUMBER_OF_SALES + 1):
        print(f"\nCreating Sandbox Sale {i}/{NUMBER_OF_SALES}")

        try:
            # 1. Create order
            order = client.create_order(
                location_id=LOCATION_ID,
                catalog_object_id=CATALOG_OBJECT_ID,
                quantity=1
            )

            if not order:
                print("Order creation failed.")
                continue

            order_id = order.get("id")

            print("Order ID:", order_id)

            # 2. Create payment
            payment = client.create_payment(
                order_id=order_id,
                amount=AMOUNT_PER_UNIT
            )

            if not payment:
                print("Payment creation failed.")
                continue

            payment_id = payment.get("id")

            print("Payment ID:", payment_id)

            # 3. Pay/complete the order
            result = client.pay_order(
                order_id=order_id,
                payment_id=payment_id
            )

            if result:
                print("SALE CREATED SUCCESSFULLY")
                successful += 1
            else:
                print("Could not complete the order.")

        except Exception as error:
            print("ERROR:", error)

    print("\n" + "=" * 60)
    print("RESULT")
    print("=" * 60)
    print("Successful Sandbox Sales:", successful)
    print("Requested Sales:", NUMBER_OF_SALES)


if __name__ == "__main__":
    main()