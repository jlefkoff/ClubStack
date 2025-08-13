from modules.nav import SideBarLinks
import streamlit as st
import requests
import logging

logger = logging.getLogger(__name__)

st.set_page_config(layout="wide")
SideBarLinks()

# Define the base URL for the API
BASE_URL = "http://api:4000"

# Initialize cart in session state
if 'cart' not in st.session_state:
    st.session_state.cart = {}

if 'show_cart' not in st.session_state:
    st.session_state.show_cart = False

# Function to fetch merch items from the API
@st.cache_data(ttl=60)  # Cache for 1 minute
def fetch_merch_items():
    try:
        response = requests.get(f"{BASE_URL}/merch")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        st.error("Unable to connect to the API. Please ensure the server is running.")
        return []
    except requests.exceptions.HTTPError as http_err:
        st.error(f"HTTP error occurred: {http_err}")
        return []
    except Exception as err:
        st.error(f"An unexpected error occurred: {err}")
        return []

# Cart functions
def add_to_cart(item_id, item_name, item_price):
    if item_id in st.session_state.cart:
        st.session_state.cart[item_id]['quantity'] += 1
    else:
        st.session_state.cart[item_id] = {
            'name': item_name,
            'price': item_price,
            'quantity': 1
        }
    st.success(f"Added {item_name} to cart!")

def remove_from_cart(item_id):
    if item_id in st.session_state.cart:
        if st.session_state.cart[item_id]['quantity'] > 1:
            st.session_state.cart[item_id]['quantity'] -= 1
        else:
            del st.session_state.cart[item_id]

def get_cart_total():
    total = 0
    for item in st.session_state.cart.values():
        total += float(item['price']) * item['quantity']
    return total

def get_cart_count():
    return sum(item['quantity'] for item in st.session_state.cart.values())

def clear_cart():
    st.session_state.cart = {}

# Header with cart
col1, col2, col3 = st.columns([2, 1, 1])
with col1:
    st.title("🛍️ Club Merch Store")

with col2:
    cart_count = get_cart_count()
    if st.button(f"🛒 Cart ({cart_count})", use_container_width=True, type="secondary"):
        st.session_state.show_cart = not st.session_state.show_cart

with col3:
    if cart_count > 0:
        cart_total = get_cart_total()
        st.metric("Total", f"${cart_total:.2f}")

# Show cart sidebar if toggled
if st.session_state.show_cart:
    with st.sidebar:
        st.header("🛒 Shopping Cart")
        
        if st.session_state.cart:
            for item_id, item in st.session_state.cart.items():
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"**{item['name']}**")
                    st.write(f"${float(item['price']):.2f} x {item['quantity']}")
                with col2:
                    if st.button("➖", key=f"remove_{item_id}", help="Remove one"):
                        remove_from_cart(item_id)
                        st.rerun()
                st.write("---")
            
            st.write(f"**Total: ${get_cart_total():.2f}**")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🗑️ Clear", use_container_width=True):
                    clear_cart()
                    st.rerun()
            with col2:
                if st.button("💳 Checkout", use_container_width=True, type="primary"):
                    st.session_state.checkout_mode = True
                    st.rerun()
        else:
            st.info("Your cart is empty")

# Checkout modal
if st.session_state.get('checkout_mode', False):
    st.header("💳 Checkout")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Order Summary")
        total = 0
        for item_id, item in st.session_state.cart.items():
            item_total = float(item['price']) * item['quantity']
            total += item_total
            st.write(f"{item['name']} x {item['quantity']} = ${item_total:.2f}")
        
        st.write("---")
        st.write(f"**Total: ${total:.2f}**")
    
    with col2:
        st.subheader("Payment Options")
        payment_method = st.radio("Payment Method", ["Cash", "Card"])
        
        if payment_method == "Cash":
            st.info("💵 Pay cash at pickup")
        elif payment_method == "Card":
            st.info("💳 Card payment at pickup")
        
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("Cancel", use_container_width=True):
                st.session_state.checkout_mode = False
                st.rerun()
        
        with col_b:
            if st.button("Place Order", use_container_width=True, type="primary"):
                # Process each item in cart
                success_count = 0
                for item_id, item in st.session_state.cart.items():
                    for _ in range(item['quantity']):
                        try:
                            cash = payment_method == "Cash"
                            response = requests.post(
                                f"{BASE_URL}/merch/merch-sales", 
                                json={"cash": cash, "ID": int(item_id)}
                            )
                            if response.status_code == 200:
                                success_count += 1
                        except:
                            st.error(f"Failed to process {item['name']}")
                
                if success_count == get_cart_count():
                    st.success(f"🎉 Order placed successfully! {success_count} items ordered.")
                    clear_cart()
                    st.session_state.checkout_mode = False
                    st.rerun()
                else:
                    st.error("Some items failed to process. Please try again.")

    st.write("---")

# Admin section (only for Treasurer)
if st.session_state["role"] == "treasurer" or st.session_state["role"] == "vp" or st.session_state["role"] == "administrator":
    with st.expander("🔧 Admin Panel"):
        st.subheader("Add New Merch Item")
        
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            new_item_name = st.text_input("Item Name", key="admin_name")
        with col2:
            new_item_price = st.number_input("Price", min_value=0.0, format="%.2f", key="admin_price")
        with col3:
            new_item_quantity = st.number_input("Quantity", min_value=0, key="admin_quantity")
        new_item_description = st.text_area("Description", key="admin_description")
        if st.button("Add Item", use_container_width=True):
                if new_item_name and new_item_price >= 0:
                    try:
                        response = requests.post(
                            f"{BASE_URL}/merch/merch-items", 
                            json={"name": new_item_name, "price": new_item_price, "quantity": new_item_quantity, "description": new_item_description}
                        )
                        if response.status_code == 201:
                            st.success(f"Added {new_item_name}!")
                            st.cache_data.clear()  # Clear cache to refresh items
                            st.rerun()
                        else:
                            st.error("Failed to add item")
                    except:
                        st.error("Error adding item")

# Add this after the Admin section and before the Main storefront

# Sales Report section (only for admins)
if st.session_state["role"] in ["treasurer", "vp", "administrator"]:
  with st.expander("📊 Sales Report"):
    st.subheader("Merch Sales Analytics")
    
    try:
      # Fetch sales data
      sales_response = requests.get(f"{BASE_URL}/merch/merch-report")
      if sales_response.status_code == 200:
        sales_data = sales_response.json()
        
        if sales_data:
          # Summary metrics
          total_sales = len(sales_data)
          total_revenue = sum(float(sale.get('TotalSalePrice', 0)) for sale in sales_data)
          cash_sales = sum(1 for sale in sales_data if float(sale['Cash']) > 0)
          card_sales = total_sales - cash_sales
          
          # Display metrics
          col1, col2, col3, col4 = st.columns(4)
          with col1:
            st.metric("Total Sales", total_sales)
          with col2:
            st.metric("Total Revenue", f"${total_revenue:.2f}")
          with col3:
            st.metric("Cash Sales", cash_sales)
          with col4:
            st.metric("Card Sales", card_sales)
          
          st.write("---")
          
          # Filter options
          col_filter1, col_filter2 = st.columns(2)
          with col_filter1:
            # Date filter
            from datetime import datetime, timedelta
            today = datetime.now().date()
            date_filter = st.selectbox(
              "Filter by Date",
              ["All Time", "Today", "This Week", "This Month"],
              key="date_filter"
            )
          
          with col_filter2:
            # Payment method filter
            payment_filter = st.selectbox(
              "Payment Method",
              ["All", "Cash Only", "Card Only"],
              key="payment_filter"
            )
          
          # Apply filters
          filtered_sales = sales_data.copy()
          
          # Date filtering
          if date_filter != "All Time":
            filtered_sales = []
            for sale in sales_data:
              try:
                sale_date = datetime.strptime(sale['SaleDate'], "%a, %d %b %Y %H:%M:%S %Z").date()
                
                if date_filter == "Today" and sale_date == today:
                  filtered_sales.append(sale)
                elif date_filter == "This Week" and sale_date >= today - timedelta(days=7):
                  filtered_sales.append(sale)
                elif date_filter == "This Month" and sale_date >= today - timedelta(days=30):
                  filtered_sales.append(sale)
              except:
                # If date parsing fails, include the sale
                filtered_sales.append(sale)
          
          # Payment method filtering
          if payment_filter == "Cash Only":
            filtered_sales = [sale for sale in filtered_sales if float(sale['Cash']) > 0]
          elif payment_filter == "Card Only":
            filtered_sales = [sale for sale in filtered_sales if float(sale['Cash']) == 0]
          
          # Display filtered results
          if filtered_sales:
            st.write(f"**Showing {len(filtered_sales)} sales:**")
            
            # Sales by item analysis
            from collections import Counter
            items_sold = Counter(sale['ItemsSold'] for sale in filtered_sales)
            
            col_table, col_chart = st.columns([2, 1])
            
            with col_table:
              st.write("**Sales Details:**")
              
              # Create a more detailed table
              for sale in sorted(filtered_sales, key=lambda x: x['SaleDate'], reverse=True):
                try:
                  sale_date = datetime.strptime(sale['SaleDate'], "%a, %d %b %Y %H:%M:%S %Z")
                  formatted_date = sale_date.strftime("%m/%d/%Y %H:%M")
                except:
                  formatted_date = sale['SaleDate']
                
                payment_type = "💵 Cash" if float(sale['Cash']) > 0 else "💳 Card"
                sale_price = float(sale.get('TotalSalePrice', 0))
                
                col_item, col_payment, col_price, col_date = st.columns([2, 1, 1, 2])
                with col_item:
                  st.write(f"**{sale['ItemsSold']}**")
                with col_payment:
                  st.write(f"{payment_type}")
                with col_price:
                  st.write(f"${sale_price:.2f}")
                with col_date:
                  st.write(f"{formatted_date}")
                
                st.write("---")
            
            with col_chart:
              st.write("**Top Items:**")
              for item, count in items_sold.most_common(5):
                st.write(f"**{item}**: {count}")
                # Simple progress bar
                progress = count / max(items_sold.values()) if items_sold.values() else 0
                st.progress(progress)
          else:
            st.info("No sales found for the selected filters")
          
          # Export functionality
          st.write("---")
          col_export1, col_export2 = st.columns(2)
          
          with col_export1:
            if st.button("📥 Download CSV", use_container_width=True):
              import pandas as pd
              import io
              
              # Create DataFrame
              df = pd.DataFrame(filtered_sales)
              
              # Format the data
              for index, row in df.iterrows():
                try:
                  sale_date = datetime.strptime(row['SaleDate'], "%a, %d %b %Y %H:%M:%S %Z")
                  df.at[index, 'SaleDate'] = sale_date.strftime("%Y-%m-%d %H:%M:%S")
                except:
                  pass
                
                df.at[index, 'PaymentMethod'] = "Cash" if float(row['Cash']) > 0 else "Card"
              
              # Convert to CSV
              csv_buffer = io.StringIO()
              df.to_csv(csv_buffer, index=False)
              csv_data = csv_buffer.getvalue()
              
              st.download_button(
                label="Download Sales Report",
                data=csv_data,
                file_name=f"merch_sales_report_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
              )
          
          with col_export2:
            # Quick stats summary
            filtered_revenue = sum(float(sale.get('TotalSalePrice', 0)) for sale in filtered_sales)
            st.metric("Filtered Revenue", f"${filtered_revenue:.2f}")
        
        else:
          st.info("No sales data available")
      else:
        st.error("Failed to load sales report")
        
    except Exception as e:
      st.error(f"Error loading sales report: {str(e)}")

# Main storefront
if not st.session_state.get('checkout_mode', False):
    st.write("---")
    
    # Fetch merch items
    merch_items = fetch_merch_items()
    
    if merch_items:
        # Create product grid (4 columns)
        cols_per_row = 4
        for i in range(0, len(merch_items), cols_per_row):
            cols = st.columns(cols_per_row)
            
            for j, item in enumerate(merch_items[i:i+cols_per_row]):
                with cols[j]:
                    # Product card
                    with st.container():
                        # Product image placeholder
                        st.image("https://placehold.co/400", 
                                use_container_width=True)
                        
                        st.write(f"**{item['Name']}**")
                        st.write(f"**${float(item['Price']):.2f}**")
                        
                        # Button row
                        col_cart, col_admin = st.columns([3, 1])
                        
                        with col_cart:
                            if st.button(
                                "🛒 Add to Cart", 
                                key=f"add_{item['ID']}", 
                                use_container_width=True,
                                type="primary"
                            ):
                                add_to_cart(item['ID'], item['Name'], item['Price'])
                                st.rerun()
                        
                        # Admin delete button
                        if st.session_state.get("first_name") == "Jacob":
                            with col_admin:
                                if st.button("🗑️", key=f"delete_{item['ID']}", help="Delete item"):
                                    try:
                                        response = requests.delete(f"{BASE_URL}/merch/{item['ID']}")
                                        if response.status_code == 200:
                                            st.success("Deleted!")
                                            st.cache_data.clear()
                                            st.rerun()
                                        else:
                                            st.error("Delete failed")
                                    except:
                                        st.error("Error deleting")
                        
                        st.write("---")
    else:
        st.info("No merch items available")

# Footer
st.write("")
st.info("💡 **Tip**: Items will be available for pickup at the next club meeting!")