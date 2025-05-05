import requests
import streamlit as st


def get_shopify_data():
    # Credentials for store
    shop_handle = st.secrets["SHOPIFY"]["SHOP_NAME"]
    access_token = st.secrets["SHOPIFY"]["ACCESS_TOKEN"]
    api_version  = st.secrets["SHOPIFY"]["API_VERSION"]

    url = f"https://{shop_handle}.myshopify.com/admin/api/{api_version}/graphql.json"

    query = """
    {
      products(first: 10) {
        edges {
          node {
            id
            title
            descriptionHtml
          }
        }
      }
    }
    """

    headers = {
        "Content-Type": "application/json",
        "X-Shopify-Access-Token": access_token
    }

    try:
        response = requests.post(url, json={"query": query}, headers=headers)
        response.raise_for_status()  # CHANGE: Raises an exception on 4xx/5xx
    except requests.HTTPError as err:
        print(f"HTTP error: {err}")
        print(f"→ Check that '{shop_handle}.myshopify.com' is correct and the store is active.")
        return None
    except requests.RequestException as err:
        print(f"Request failed: {err}")
        return None

    data = response.json()
    # CHANGE: Handle GraphQL-level errors explicitly
    if "errors" in data:
        print("GraphQL errors:", data["errors"])
        return None
    raw_list = data["data"]["products"]["edges"]
    product_list = []
    for bottle in raw_list:
        product_list.append(bottle['node']['title'])

    return product_list

products = get_shopify_data()
print(products)