def get_search_result(carrier, featur):
    """Get search result from database"""
    # Connect to database
    conn = connect_db()
    cur = conn.cursor()
    # Get search result
    cur.execute("SELECT * FROM search_result WHERE carrier = %s AND feature = %s", (carrier, feature))
    result = cur.fetchall()
    # Close connection
    cur.close()
    conn.close()
    print(result)
    return result