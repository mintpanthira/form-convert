"""
All-in-One Converter: Upload Excel → Split by Category → Copy JSON → Preview

Flow:
1. Upload Excel file
2. แปลงเป็น JSON แยกตาม category slug
3. Preview packages
4. Copy/Download JSON
"""

import streamlit as st
import pandas as pd
import json

# Force cache invalidation - v2.1 - 2026-01-15 17:30
import importlib
import sys
if 'mint_excel_to_json_converter_lib' in sys.modules:
    importlib.reload(sys.modules['mint_excel_to_json_converter_lib'])

from mint_excel_to_json_converter_lib import (
    convert_mint_excel_to_json,
    create_inline_text,
    create_i18n_text,
    parse_configuration_text
)

st.set_page_config(
    page_title="Excel to JSON Converter",
    page_icon="🚀",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 2rem;
    }
    .category-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        border: 2px solid #e0e0e0;
        margin-bottom: 1rem;
    }
    .category-card:hover {
        border-color: #667eea;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.15);
    }
    .package-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border-left: 4px solid #667eea;
    }
    .json-code {
        background: #f8f9fa;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 1rem;
        font-family: 'Monaco', 'Menlo', monospace;
        font-size: 12px;
        max-height: 400px;
        overflow-y: auto;
    }
    .stButton > button {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="main-header">
    <h1>🚀 Excel to JSON Converter</h1>
    <p style="margin: 0;">Upload Excel → แปลงตาม Category → Copy JSON → Preview Packages</p>
</div>
""", unsafe_allow_html=True)

def split_by_category(df):
    """แยก JSON ตาม Category slug"""
    
    # Set headers
    headers = df.iloc[0].tolist()
    df_data = df.iloc[1:].copy()
    df_data.columns = headers
    df_data.columns = df_data.columns.str.strip()
    
    # Get unique categories
    categories = df_data[df_data['Category slug'].notna()]['Category slug'].unique()
    
    results = {}
    
    for category_slug in categories:
        # Filter data for this category
        category_data = df_data[
            (df_data['Category slug'] == category_slug) | 
            (df_data['Package Id'].str.startswith(category_slug, na=False))
        ]
        
        if category_data.empty:
            continue
        
        # Get category info
        category_rows = category_data[category_data['Category'].notna()]
        if len(category_rows) > 0:
            first_row = category_rows.iloc[0]
            category_name = first_row.get('Category', category_slug)
            
            subcat_thai = None
            for col in df_data.columns:
                if 'subcat' in col.lower() and 'thai' in col.lower():
                    subcat_thai = first_row.get(col, '')
                    break
            if not subcat_thai:
                subcat_thai = category_name
                
            cart_limit = int(first_row.get('Cart limit', 30)) if pd.notna(first_row.get('Cart limit')) else 30
        else:
            first_row = category_data.iloc[0]
            category_name = category_slug.replace('-', ' ').title()
            subcat_thai = category_name
            cart_limit = 30
        
        # Build packages
        packages = []
        current_package = None
        
        for _, row in category_data.iterrows():
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
            
                # Get location types
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
                            "max": int(row.get('max', 10)) if pd.notna(row.get('max')) else 10,
                            "min": int(row.get('min', 1)) if pd.notna(row.get('min')) else 1
                        },
                        "placeholder": create_inline_text(
                            str(row.get('quantity.placeholder', 'จำนวน')),
                            "Quantity"
                        )
                    },
                    "base_price": int(row.get('Starting price', 0)) if pd.notna(row.get('Starting price')) else 0,
                    "description": create_inline_text(
                        str(row.get('Package Description', '')),
                        str(row.get('Package Description', ''))
                    ),
                    "configurations": []
                }
            
            # Process configuration (for both new package and additional config rows)
            if current_package:
                config_type = str(row.get('Configurations.type', 'NONE')).strip().upper()
                
                if config_type not in ['NONE', 'NAN', ''] and not pd.isna(row.get('Configurations.type')):
                    config_text = row.get('Package Detail selection ( Configuration )')
                    config_title = row.get('Configurations.title', 'ตัวเลือก')
                    config_id = row.get('Configurations.id', f'config-{len(current_package["configurations"])+1:03d}')
                    
                    if pd.notna(config_text):
                        items = parse_configuration_text(config_text)
                        
                        if items:
                            config = {
                                "id": str(config_id) if pd.notna(config_id) else f'config-{len(current_package["configurations"])+1:03d}',
                                "data": {
                                    "items": items
                                },
                                "type": config_type,
                                "title": str(config_title) if pd.notna(config_title) else "ตัวเลือก",
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
        
        # Build JSON for this category
        category_json = {
            "id": category_slug,
            "title": create_inline_text(subcat_thai if subcat_thai else category_name, category_name),
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
        
        results[category_slug] = {
            'json': category_json,
            'category_name': category_name,
            'subcat_thai': subcat_thai,
            'packages_count': len(packages)
        }
    
    return results

# Step 1: Upload Excel
st.markdown("## 📤 Step 1: Upload Excel File")

uploaded_file = st.file_uploader(
    "เลือกไฟล์ Excel หรือ CSV (รูปแบบ Mint)",
    type=['xlsx', 'xls', 'csv'],
    help="อัปโหลดไฟล์ Excel หรือ CSV ที่มีโครงสร้างแบบ Mint test form"
)

if uploaded_file is not None:
    try:
        # Read file (Excel or CSV)
        file_extension = uploaded_file.name.split('.')[-1].lower()
        if file_extension == 'csv':
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        
        st.success(f"✅ อ่านไฟล์สำเร็จ! ({df.shape[0]} แถว, {df.shape[1]} คอลัมน์)")
        
        # Step 2: Convert
        st.markdown("## 🔄 Step 2: แปลงเป็น JSON")
        
        if st.button("🚀 เริ่มแปลง", type="primary"):
            with st.spinner("กำลังแปลง..."):
                results = split_by_category(df)
            
            if results:
                st.session_state['results'] = results
                st.success(f"✅ แปลงสำเร็จ! พบ {len(results)} categories")
            else:
                st.error("❌ ไม่พบข้อมูล categories")
        
        # Step 3: Show Results
        if 'results' in st.session_state:
            results = st.session_state['results']
            
            st.markdown("## 📊 Step 3: เลือก Category")
            
            # Category selector
            category_options = {
                slug: f"{data['subcat_thai']} ({data['packages_count']} packages)"
                for slug, data in results.items()
            }
            
            selected_slug = st.selectbox(
                "เลือก Category:",
                options=list(category_options.keys()),
                format_func=lambda x: category_options[x]
            )
            
            if selected_slug:
                category_data = results[selected_slug]
                category_json = category_data['json']
                
                # Show stats
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total Packages", category_data['packages_count'])
                with col2:
                    packages_with_configs = sum(
                        1 for pkg in category_json['packages'] 
                        if pkg['configurations']
                    )
                    st.metric("With Configurations", packages_with_configs)
                with col3:
                    st.metric("Cart Limit", category_json['cart_limit'])
                with col4:
                    json_size = len(json.dumps(category_json))
                    st.metric("JSON Size", f"{json_size:,} bytes")
                
                # Generate JSON with proper line endings (LF only)
                json_str = json.dumps(category_json, ensure_ascii=False, indent=2)
                # Ensure LF line endings (Unix style)
                json_str = json_str.replace('\r\n', '\n').replace('\r', '\n')
                
                # Action buttons
                st.markdown("### 🎯 Actions")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.download_button(
                        label="📥 ดาวน์โหลด JSON (แนะนำ)",
                        data=json_str.encode('utf-8'),
                        file_name=f"{selected_slug}.json",
                        mime="application/json",
                        use_container_width=True,
                        help="ใช้วิธีนี้เพื่อหลีกเลี่ยงปัญหา line endings ใน IDE"
                    )
                
                with col2:
                    show_json = st.checkbox("👁️ แสดง JSON Code เพื่อ Copy", help="แสดง JSON ในรูปแบบ text area สำหรับ copy")
                
                # Show JSON for copying
                if show_json:
                    st.markdown("### 📋 Copy JSON")
                    st.info("💡 **วิธี Copy:** เลือกทั้งหมด (Ctrl+A / Cmd+A) → Copy (Ctrl+C / Cmd+C) → Paste ใน IDE")
                    
                    # Use text_area for better copying
                    st.text_area(
                        "JSON Code (LF line endings)",
                        value=json_str,
                        height=400,
                        key=f"json_copy_{selected_slug}",
                        help="JSON นี้ใช้ LF line endings แล้ว ไม่น่าจะมีปัญหาใน IDE"
                    )
                
                # Additional JSON viewer (for reference only)
                show_code = st.checkbox("🔍 แสดง JSON Code (Syntax Highlighting)", help="สำหรับดูเท่านั้น ไม่แนะนำให้ copy จากที่นี่")
                
                if show_code:
                    st.markdown("### 📄 JSON Code Preview")
                    st.warning("⚠️ **หมายเหตุ:** หากต้องการ copy JSON กรุณาใช้ปุ่ม '👁️ แสดง JSON Code เพื่อ Copy' ด้านบน เพื่อหลีกเลี่ยงปัญหา line endings")
                    st.code(json_str, language='json', line_numbers=True)
                
                # Preview packages - Mobile Mockup
                st.markdown("### 📱 Preview Packages (Mobile Demo)")
                
                # Create mobile frame container
                col_left, col_mobile, col_right = st.columns([1, 2, 1])
                
                with col_mobile:
                    # Show all packages (scrollable)
                    demo_packages = category_json['packages']
                    
                    # Build complete HTML
                    mobile_html = '<div style="max-width: 400px; margin: 0 auto; background: #1a1a1a; border-radius: 36px; padding: 12px; box-shadow: 0 20px 60px rgba(0,0,0,0.3);">'
                    mobile_html += '<div style="background: white; border-radius: 28px 28px 0 0; padding: 12px 24px 8px 24px; display: flex; justify-content: space-between; align-items: center; font-size: 12px;"><div style="font-weight: 600;">9:41</div><div style="display: flex; gap: 4px;"><span>📶</span><span>📡</span><span>🔋</span></div></div>'
                    mobile_html += '<div style="background: #f5f5f5; height: 700px; overflow-y: scroll; padding: 16px; -webkit-overflow-scrolling: touch;">'
                    
                    for idx, pkg in enumerate(demo_packages):
                        # Package Card
                        desc_short = pkg['description']['values']['th'][:80] + ('...' if len(pkg['description']['values']['th']) > 80 else '')
                        mobile_html += f'<div style="background: white; border-radius: 12px; padding: 16px; margin: 12px 0; box-shadow: 0 2px 8px rgba(0,0,0,0.06);"><div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;"><div style="font-weight: 600; color: #1a1a1a; font-size: 15px;">{pkg["title"]["values"]["th"]}</div><div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 6px 12px; border-radius: 8px; font-weight: bold; font-size: 14px;">฿{pkg["base_price"]:,}</div></div><p style="color: #666; margin: 6px 0; line-height: 1.4; font-size: 13px;">{desc_short}</p><div style="background: #f8f9fa; padding: 8px; border-radius: 6px; margin-top: 8px; font-size: 12px;"><span style="color: #666;">📦 {pkg["quantity"]["validation"]["min"]}-{pkg["quantity"]["validation"]["max"]} {pkg["quantity"]["placeholder"]["values"]["th"]}</span></div></div>'
                        
                        # Configurations
                        if pkg['configurations']:
                            for config in pkg['configurations']:
                                mobile_html += f'<div style="margin: 10px 0;"><div style="color: #333; font-weight: 600; font-size: 13px; margin-bottom: 8px;">⚙️ {config["title"]}</div></div>'
                                
                                for item in config['data']['items'][:3]:
                                    price_text = f"+฿{item['additional_price']}" if item['additional_price'] > 0 else ""
                                    icon = "○" if config['type'] == "RADIO" else "☐"
                                    item_value = item['value'][:30] + ('...' if len(item['value']) > 30 else '')
                                    price_html = f'<div style="color: #667eea; font-weight: 600; font-size: 12px;">{price_text}</div>' if price_text else ''
                                    mobile_html += f'<div style="background: white; border: 1.5px solid #e0e0e0; border-radius: 8px; padding: 10px 12px; margin: 6px 0; display: flex; justify-content: space-between; align-items: center; font-size: 13px;"><div style="display: flex; align-items: center; gap: 8px;"><span style="font-size: 14px;">{icon}</span><span style="color: #333;">{item_value}</span></div>{price_html}</div>'
                        
                        # Quantity & Order Button
                        mobile_html += f'<div style="background: white; border-radius: 8px; padding: 12px; margin: 12px 0; display: flex; justify-content: space-between; align-items: center; font-size: 13px;"><span style="color: #333; font-weight: 500;">จำนวน</span><div style="display: flex; align-items: center; gap: 12px;"><button style="width: 28px; height: 28px; border-radius: 50%; border: 1.5px solid #e0e0e0; background: white; color: #999; font-size: 16px;">−</button><span style="font-size: 15px; font-weight: 600; min-width: 24px; text-align: center;">1</span><button style="width: 28px; height: 28px; border-radius: 50%; border: none; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; font-size: 16px;">+</button></div></div>'
                        mobile_html += f'<div style="margin: 12px 0;"><button style="width: 100%; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border: none; border-radius: 10px; padding: 12px; font-size: 14px; font-weight: 600; box-shadow: 0 3px 10px rgba(102, 126, 234, 0.3);">🛒 สั่งซื้อ ฿{pkg["base_price"]:,}</button></div>'
                        
                        if idx < len(demo_packages) - 1:
                            mobile_html += '<hr style="margin: 16px 0; border: none; border-top: 1px solid #e0e0e0;">'
                    
                    # Close frame
                    mobile_html += '</div><div style="background: white; border-radius: 0 0 28px 28px; padding: 12px; display: flex; justify-content: center;"><div style="width: 140px; height: 4px; background: #ddd; border-radius: 2px;"></div></div></div>'
                    mobile_html += f'<div style="text-align: center; margin-top: 16px; color: #666; font-size: 13px;">📱 แสดงทั้งหมด {len(category_json["packages"])} packages (เลื่อนดูได้)</div>'
                    
                    # Render once
                    st.markdown(mobile_html, unsafe_allow_html=True)
    
    except Exception as e:
        st.error(f"❌ เกิดข้อผิดพลาด: {str(e)}")
        st.exception(e)

else:
    # Instructions
    st.info("""
    ### 📋 คำแนะนำ:
    
    1. **อัปโหลดไฟล์ Excel** ที่มีโครงสร้างแบบ Mint test form
    2. **กดปุ่มแปลง** เพื่อแยก JSON ตาม category
    3. **เลือก Category** ที่ต้องการ
    4. **ดาวน์โหลดหรือ Copy JSON** ไปใช้งาน
    5. **ดู Preview** packages ได้เลย
    
    ---
    
    **โครงสร้างไฟล์ Excel ที่รองรับ:**
    - Row 0: Headers
    - Row 1-N: Package data (1 row = 1 package)
    - แต่ละ package มี Category slug, Package ID, Price, Configurations, etc.
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666;">
    <p>🚀 Excel to JSON Converter v2.0 | Made with ❤️ for Fastwork</p>
</div>
""", unsafe_allow_html=True)
