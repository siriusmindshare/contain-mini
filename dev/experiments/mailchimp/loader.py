import cx_Oracle
import os

def insert_data_from_temp_to_main():
    
    # Establish a connection to the Oracle database
    with open('D:\contain-freemium\dev\ds_infra\ds_infra.env') as f:
        for line in f:
            key, value = line.strip().split('=')
            os.environ[key] = value
    user = os.environ.get("USER")
    host = os.environ.get("HOST")
    service = os.environ.get("SERVICE")
    port = os.environ.get("PORT")
    password = os.environ.get("PASSWORD")

    conn = cx_Oracle.connect(
        user=user,
        password=password,
        dsn=f"{host}:{port}/{service}",
    )
    cursor = conn.cursor()
    insert_query = f"""
    INSERT INTO RFM_ORDER_DATA (ACCOUNT_ID, ORDER_ID, CUSTOMER_ID, ORDER_STATUS, ORDER_PURCHASE_TIMESTAMP, ORDER_APPROVED_AT, ORDER_DELIVERED_CARRIER_DATE, ORDER_DELIVERED_CUSTOMER_DATE, ORDER_ESTIMATED_DELIVERY_DATE)
    SELECT ACCOUNT_ID, ORDER_ID, CUSTOMER_ID, ORDER_STATUS, ORDER_PURCHASE_TIMESTAMP, ORDER_APPROVED_AT, ORDER_DELIVERED_CARRIER_DATE, ORDER_DELIVERED_CUSTOMER_DATE, ORDER_ESTIMATED_DELIVERY_DATE
    FROM TEMP_RFM_ORDER_DATA
    """

    cursor.execute(insert_query)
    conn.commit()
    cursor.close()
    conn.close()

    print("Data moved from temporary table to real table.")

if __name__ == "__main__":
    insert_data_from_temp_to_main()