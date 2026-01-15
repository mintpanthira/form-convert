"""
Mint Excel to JSON Converter Library
Version: 2.1.0 - Multi-configuration support
Updated: 2026-01-15 17:30
"""

import streamlit as st
import pandas as pd
import json
import re
from typing import Dict, List, Any, Optional

def create_inline_text(th: str, en: str = "") -> Dict:
    """Create INLINE text structure"""
    return {
        "kind": "INLINE",
        "values": {
            "en": en if en else th,  # Use Thai as fallback if no English
            "th": th
        }
    }

def create_i18n_text(key: str) -> Dict:
    """Create I18N text structure"""
    return {
        "key": key,
        "kind": "I18N"
    }

def parse_configuration_text(config_text: str) -> List[Dict]:
    """
    Parse configuration text like:
    ขนาดพื้นที่
    - 25 - 40 ตร.ม. (2 ชั่วโมง)
    - 40 - 60 ตร.ม. (3 ชั่วโมง) +250 THB
    
    Returns list of items with id, value, and additional_price
    """
    if pd.isna(config_text) or not str(config_text).strip():
        return []
    
    items = []
    lines = str(config_text).split('\n')
    item_id = 1
    
    for line in lines:
        line = line.strip()
        if not line or not line.startswith('-'):
            continue
        
        # Remove leading dash
        line = line.lstrip('- ').strip()
        
        # Extract price if exists (e.g., "+250 THB" or "+1,000 THB")
        price_match = re.search(r'\+([\d,]+)\s*THB', line, re.IGNORECASE)
        additional_price = 0
        if price_match:
            # Remove comma from price string
            price_str = price_match.group(1).replace(',', '')
            additional_price = int(price_str)
            # Remove price from value text
            line = re.sub(r'\+[\d,]+\s*THB', '', line, flags=re.IGNORECASE).strip()
        
        items.append({
            "id": str(item_id),
            "value": line,
            "additional_price": additional_price
        })
        item_id += 1
    
    return items

def convert_mint_excel_to_json(df: pd.DataFrame, service_id: str = None, 
                                service_title_th: str = None,
                                service_title_en: str = None) -> Dict:
    """
    Convert Mint Excel format to JSON structure
    
    Excel columns (from row 0):
    - Category, Subcat thai, Category slug, Cart limit
    - Package Name, Package Id, Package Description
    - Starting price, min, max, quantity.placeholder
    - Configurations.title, Package Detail selection ( Configuration ), Configurations.id, Configurations.type
    - Configurations.title.2, Package Detail selection ( Configuration ).2, Configurations.id.2, Configurations.type.2
    - Configurations.title.3, Package Detail selection ( Configuration ).3, Configurations.id.3, Configurations.type.3
    - (Support up to 5 configurations per package)
    - other text field - placeholder
    - service_location_types, Location type, marketplace subcategory
    
    Configuration Types:
    - NONE = no configuration (configurations: [])
    - RADIO = radio buttons (single select)
    - CHECKBOX = checkboxes (multiple select)
    - DATE_TIME_RANGE = date/time range picker
    """
    
    # Set headers from first row
    headers = df.iloc[0].tolist()
    df_data = df.iloc[1:].copy()
    df_data.columns = headers
    
    # Clean up column names
    df_data.columns = df_data.columns.str.strip()
    
    # Get service metadata from first package
    first_package = df_data[df_data['Package Name'].notna()].iloc[0]
    cart_limit = int(str(first_package.get('Cart limit', 10)).replace(',', '')) if pd.notna(first_package.get('Cart limit')) and str(first_package.get('Cart limit', 10)).replace(',', '').isdigit() else 10
    category = first_package.get('Category', 'Service')
    subcat_thai = first_package.get('Subcat thai', '')
    
    # Use provided service details or generate from data
    if not service_id:
        service_id = str(first_package.get('Category slug', 'service-001')).strip()
    if not service_title_th:
        service_title_th = subcat_thai if subcat_thai else category
    if not service_title_en:
        service_title_en = category
    
    # Build packages
    packages = []
    current_package = None
    
    for idx, row in df_data.iterrows():
        # Check if this is a new package (has Package Name)
        has_package_name = pd.notna(row.get('Package Name')) and str(row.get('Package Name')).strip()
        
        if has_package_name:
            # Save previous package if exists
            if current_package:
                packages.append(current_package)
            
            # Start new package
            package_name = str(row['Package Name']).strip()
            package_id = str(row['Package Id']).strip()
            
            if not package_name or not package_id:
                continue
        
            # Get service location types
            location_types_str = str(row.get('service_location_types', 'AT_PIN'))
            service_location_types = []
            if pd.notna(location_types_str) and location_types_str != 'nan':
                service_location_types = [loc.strip() for loc in location_types_str.split(',')]
            if not service_location_types:
                service_location_types = ['AT_PIN']
            
            current_package = {
                "id": package_id,
                "note": {
                    "placeholder": str(row.get('other text field - placeholder', 'ระบุข้อมูลเพิ่มเติม'))
                },
                "image": {
                    "cover": "https://example.com/inspection-cover.jpg",
                    "thumbnail": "https://example.com/inspection-thumb.jpg"
                },
                "title": create_inline_text(package_name, package_name),
            "quantity": {
                "validation": {
                    "max": int(str(row.get('max', 10)).replace(',', '')) if pd.notna(row.get('max')) and str(row.get('max', 10)).replace(',', '').replace('.', '').isdigit() else 10,
                    "min": int(str(row.get('min', 1)).replace(',', '')) if pd.notna(row.get('min')) and str(row.get('min', 1)).replace(',', '').replace('.', '').isdigit() else 1
                },
                    "placeholder": create_inline_text(
                        str(row.get('quantity.placeholder', 'จำนวน')),
                        "Quantity"
                    )
                },
                "base_price": int(str(row.get('Starting price', 0)).replace(',', '')) if pd.notna(row.get('Starting price')) and str(row.get('Starting price', 0)).replace(',', '').isdigit() else 0,
                "description": create_inline_text(
                    str(row.get('Package Description', '')),
                    str(row.get('Package Description', ''))
                ),
                "configurations": []
            }
        
        # Process configuration (for both new package and additional config rows)
        if current_package:
            config_type = str(row.get('Configurations.type', 'NONE')).strip().upper()
            
            # Skip if NONE or NAN or empty
            if config_type not in ['NONE', 'NAN', ''] and not pd.isna(row.get('Configurations.type')):
                config_text = row.get('Package Detail selection ( Configuration )')
                config_title = str(row.get('Configurations.title', 'ตัวเลือก')) if pd.notna(row.get('Configurations.title')) else 'ตัวเลือก'
                config_id = str(row.get('Configurations.id', f'config-{len(current_package["configurations"])+1:03d}')) if pd.notna(row.get('Configurations.id')) else f'config-{len(current_package["configurations"])+1:03d}'
                
                # Parse items from config_text
                items = []
                if pd.notna(config_text):
                    items = parse_configuration_text(config_text)
                
                # Create configuration
                config = {
                    "id": config_id,
                    "data": {
                        "items": items
                    },
                    "type": config_type,
                    "title": config_title,
                    "validation": {
                        "required": config_type == "RADIO"
                    },
                    "description": None,
                    "default_value": None
                }
                
                current_package["configurations"].append(config)
    
    # Don't forget to add the last package
    if current_package:
        packages.append(current_package)
    
    # Get service location types from first package
    first_pkg_location = packages[0] if packages else {}
    location_types_str = str(df_data[df_data['Package Name'].notna()].iloc[0].get('service_location_types', 'AT_PIN'))
    service_location_types = []
    if pd.notna(location_types_str) and location_types_str != 'nan':
        service_location_types = [loc.strip() for loc in location_types_str.split(',')]
    if not service_location_types:
        service_location_types = ['AT_PIN']
    
    # Build final JSON structure
    result = {
        "id": service_id,
        "note": {
            "placeholder": create_i18n_text("service_definition.note.placeholder")
        },
        "title": create_inline_text(service_title_th, service_title_en),
        "packages": packages,
        "cart_limit": cart_limit,
        "components": {
            "banner": {
                "title": create_i18n_text("service_definition.components.banner.title"),
                "button": {
                    "url": "https://www.fastwork.co/join",
                    "text": create_i18n_text("service_definition.components.banner.button_text")
                },
                "subtitle": create_i18n_text("service_definition.components.banner.subtitle")
            },
            "info_badge": [
                {
                    "icon": "refund_icon",
                    "full_text": create_i18n_text("service_definition.components.info_badge.refund.full_text"),
                    "more_content": None,
                    "highlight_text": create_i18n_text("service_definition.components.info_badge.refund.highlight_text")
                },
                {
                    "icon": "payment_icon",
                    "full_text": create_i18n_text("service_definition.components.info_badge.payment.full_text"),
                    "more_content": None,
                    "highlight_text": create_i18n_text("service_definition.components.info_badge.payment.highlight_text")
                }
            ],
            "location_box": {
                "text": {
                    "at_pin": {
                        "description": None,
                        "placeholder": create_inline_text(
                            "คุณต้องการให้ช่างไปที่ไหน ?",
                            "Address where the service is needed"
                        )
                    },
                    "online": {
                        "description": None,
                        "placeholder": None
                    },
                    "at_store": {
                        "description": None,
                        "placeholder": create_inline_text(
                            "เราจะช่วยหาร้านที่ว่าง ใกล้หมุดที่คุณปัก",
                            "We'll help find available shops near your location"
                        )
                    }
                },
                "visible": True,
                "service_location_types": service_location_types,
                "default_service_location_type": service_location_types[0] if service_location_types else "AT_PIN"
            },
            "cashback_section": {
                "icon": "point_icon",
                "full_text": create_i18n_text("service_definition.components.cashback_section.full_text"),
                "highlight_text": create_i18n_text("service_definition.components.cashback_section.highlight_text")
            },
            "summary_info_badge": [
                {
                    "icon": "check_icon",
                    "full_text": create_i18n_text("service_definition.summary_info_badge.full_text"),
                    "more_content": None,
                    "highlight_text": create_i18n_text("service_definition.summary_info_badge.highlight_text")
                }
            ],
            "summary_location_box": {
                "location": {
                    "text": {
                        "at_pin": {
                            "description": None,
                            "placeholder": create_inline_text(
                                "คุณต้องการให้ช่างไปที่ไหน ?",
                                "Address where the service is needed"
                            )
                        },
                        "online": {
                            "description": None,
                            "placeholder": None
                        },
                        "at_store": {
                            "description": None,
                            "placeholder": create_inline_text(
                                "เราจะช่วยหาร้านที่ว่าง ใกล้หมุดที่คุณปัก",
                                "We'll help find available shops near your location"
                            )
                        }
                    },
                    "visible": True,
                    "service_location_types": service_location_types,
                    "default_service_location_type": service_location_types[0] if service_location_types else "AT_PIN"
                },
                "date_time": {
                    "visible": True,
                    "placeholder": create_inline_text(
                        "เลือกวันที่และเวลารับบริการ",
                        "Select date and time for service"
                    )
                }
            }
        },
        "cover_image": "https://example.com/service-cover.jpg",
        "service_location_types": service_location_types
    }
    
    return result

def main():
    st.set_page_config(page_title="Mint Excel to JSON Converter", page_icon="📊", layout="wide")
    
    st.title("📊 Mint Excel to JSON Converter")
    st.markdown("### แปลงไฟล์ Excel (รูปแบบ Mint) เป็น JSON สำหรับ Service Definition")
    
    st.markdown("""
    ---
    **รูปแบบไฟล์ที่รองรับ:**
    
    Excel ที่มีโครงสร้างแบบ "Mint test form.xlsx":
    - Row 0: Headers (Category, Package Name, Package Id, Starting price, etc.)
    - Row 1-N: Package data (แต่ละแถว = 1 package)
    - Configurations อยู่ในคอลัมน์ "Package Detail selection"
    
    **คอลัมน์ที่สำคัญ:**
    - Package Name, Package Id, Package Description
    - Starting price, min, max, quantity.placeholder
    - Configurations.title, Package Detail selection, Configurations.id, Configurations.type
    - other text field - placeholder
    - service_location_types
    ---
    """)
    
    # File upload
    uploaded_file = st.file_uploader("อัปโหลดไฟล์ Excel", type=['xlsx', 'xls'])
    
    if uploaded_file is not None:
        try:
            # Read Excel file
            df = pd.read_excel(uploaded_file)
            
            st.success(f"✅ อ่านไฟล์สำเร็จ! พบ {df.shape[0]} แถว, {df.shape[1]} คอลัมน์")
            
            # Show preview
            with st.expander("🔍 ดูข้อมูลต้นฉบับ"):
                st.dataframe(df.head(10))
            
            # Service metadata input
            st.markdown("### ⚙️ ตั้งค่า Service (optional)")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                service_id = st.text_input("Service ID", value="", placeholder="ใช้ค่าจาก Excel ถ้าไม่กรอก")
            
            with col2:
                service_title_th = st.text_input("Service Title (TH)", value="", placeholder="ใช้ค่าจาก Excel ถ้าไม่กรอก")
            
            with col3:
                service_title_en = st.text_input("Service Title (EN)", value="", placeholder="ใช้ค่าจาก Excel ถ้าไม่กรอก")
            
            # Convert button
            if st.button("🔄 แปลงเป็น JSON", type="primary"):
                try:
                    result_json = convert_mint_excel_to_json(
                        df,
                        service_id=service_id if service_id else None,
                        service_title_th=service_title_th if service_title_th else None,
                        service_title_en=service_title_en if service_title_en else None
                    )
                    
                    # Display JSON
                    st.success("✅ แปลงสำเร็จ!")
                    
                    # Show summary
                    st.markdown("### 📊 สรุปข้อมูล")
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Total Packages", len(result_json['packages']))
                    col2.metric("Cart Limit", result_json['cart_limit'])
                    
                    packages_with_config = sum(1 for p in result_json['packages'] if p['configurations'])
                    col3.metric("Packages with Configs", packages_with_config)
                    
                    # Package details
                    with st.expander("📦 Package Details"):
                        for pkg in result_json['packages']:
                            st.markdown(f"**{pkg['id']}** - {pkg['title']['values']['th']}")
                            st.write(f"  - ราคา: ฿{pkg['base_price']}")
                            st.write(f"  - Configurations: {len(pkg['configurations'])}")
                            if pkg['configurations']:
                                for config in pkg['configurations']:
                                    st.write(f"    - {config['title']} ({config['type']}): {len(config['data']['items'])} options")
                    
                    # Format JSON with indentation
                    json_str = json.dumps(result_json, ensure_ascii=False, indent=2)
                    
                    # Show JSON
                    st.json(result_json)
                    
                    # Download button
                    st.download_button(
                        label="📥 ดาวน์โหลด JSON",
                        data=json_str,
                        file_name="service_definition.json",
                        mime="application/json"
                    )
                    
                    # Copy to clipboard section
                    st.text_area(
                        "JSON Output (คัดลอกได้)",
                        value=json_str,
                        height=400
                    )
                    
                except Exception as e:
                    st.error(f"❌ เกิดข้อผิดพลาดในการแปลง: {str(e)}")
                    st.exception(e)
        
        except Exception as e:
            st.error(f"❌ เกิดข้อผิดพลาดในการอ่านไฟล์: {str(e)}")
            st.exception(e)
    
    else:
        st.info("📝 รอการอัปโหลดไฟล์...")
        
        st.markdown("### 📋 ตัวอย่างรูปแบบข้อมูล")
        st.markdown("""
        **Configuration Format:**
        ```
        ขนาดพื้นที่
        - 25 - 40 ตร.ม. (2 ชั่วโมง)
        - 40 - 60 ตร.ม. (3 ชั่วโมง) +250 THB
        - 60 - 80 ตร.ม. (4 ชั่วโมง) +500 THB
        ```
        
        **Configuration Types:**
        - `RADIO` = เลือกได้ 1 อย่าง
        - `CHECKBOX` = เลือกได้หลายอย่าง
        - `NONE` = ไม่มี configuration
        
        **Price Format:**
        - ระบุราคาเพิ่มด้วย `+จำนวน THB` เช่น `+250 THB`
        - ถ้าไม่ระบุ = ราคาเพิ่ม 0
        """)

if __name__ == "__main__":
    main()
