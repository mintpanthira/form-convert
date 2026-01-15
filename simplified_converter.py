"""
Simplified JSON Converter
- title, description, placeholder เป็น string ธรรมดา (ภาษาไทย)
- components ใช้ I18N keys
- ถ้าไม่มีใน translation ให้ใช้ค่าจาก Excel
"""

import streamlit as st
import pandas as pd
import json
import re

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
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="main-header">
    <h1>🚀 Excel to JSON Converter (Simplified)</h1>
    <p style="margin: 0;">JSON format แบบง่าย - ใช้ string แทน object</p>
</div>
""", unsafe_allow_html=True)

def parse_configuration_text(config_text: str) -> list:
    """Parse configuration text"""
    if pd.isna(config_text) or not str(config_text).strip():
        return []
    
    items = []
    lines = str(config_text).split('\n')
    item_id = 1
    
    for line in lines:
        line = line.strip()
        if not line or not line.startswith('-'):
            continue
        
        line = line.lstrip('- ').strip()
        
        price_match = re.search(r'\+(\d+)\s*THB', line, re.IGNORECASE)
        additional_price = 0
        if price_match:
            additional_price = int(price_match.group(1))
            line = re.sub(r'\+\d+\s*THB', '', line, flags=re.IGNORECASE).strip()
        
        items.append({
            "id": str(item_id),
            "value": line,
            "additional_price": additional_price
        })
        item_id += 1
    
    return items

def get_placeholder_key(category_slug: str) -> str:
    """Get placeholder key based on category"""
    # Map category slug to placeholder key
    placeholder_map = {
        'cleaning': 'service.placeholder.cleaning',
        'air-cleaning': 'service.placeholder.air-cleaning',
        'massage': 'service.placeholder.technician',
        'technician-electrical': 'service.placeholder.technician',
        'technician-plumbing': 'service.placeholder.technician',
        'technician-repair': 'service.placeholder.technician',
        'technician-cleaning': 'service.placeholder.technician',
        'technician-garden': 'service.placeholder.technician',
        'part-time-ecommerce': 'service.placeholder.part-time',
        'part-time-online': 'service.placeholder.part-time',
        'part-time-general': 'service.placeholder.part-time',
        'part-time-event': 'service.placeholder.part-time',
        'part-time-hospitality': 'service.placeholder.part-time',
        'part-time-stock': 'service.placeholder.part-time',
        'part-time-driver': 'service.placeholder.part-time',
        'photography': 'service.placeholder.photography',
        'horoscope': 'service.placeholder.technician',
        'nail-salon': 'service.placeholder.technician',
        'queue-booking': 'service.placeholder.queue-booking',
        'hair-salon': 'service.placeholder.hair-salon'
    }
    
    return placeholder_map.get(category_slug, 'service.placeholder.technician')

def split_by_category(df):
    """แยก JSON ตาม Category slug"""
    
    headers = df.iloc[0].tolist()
    df_data = df.iloc[1:].copy()
    df_data.columns = headers
    df_data.columns = df_data.columns.str.strip()
    
    categories = df_data[df_data['Category slug'].notna()]['Category slug'].unique()
    
    results = {}
    
    for category_slug in categories:
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
        for _, row in category_data.iterrows():
            if pd.isna(row.get('Package Name')):
                continue
            
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
            
            # Simplified package structure
            package = {
                "id": package_id,
                "note": {
                    "placeholder": str(row.get('other text field - placeholder', 'ระบุข้อมูลเพิ่มเติม'))
                },
                "image": {
                    "cover": "https://example.com/inspection-cover.jpg",
                    "thumbnail": "https://example.com/inspection-thumb.jpg"
                },
                "title": package_name,  # Simple string
                "quantity": {
                    "validation": {
                        "max": int(row.get('max', 10)) if pd.notna(row.get('max')) else 10,
                        "min": int(row.get('min', 1)) if pd.notna(row.get('min')) else 1
                    },
                    "placeholder": str(row.get('quantity.placeholder', 'จำนวน'))  # Simple string
                },
                "base_price": int(row.get('Starting price', 0)) if pd.notna(row.get('Starting price')) else 0,
                "description": str(row.get('Package Description', '')),  # Simple string
                "configurations": []
            }
            
            # Process configurations
            config_type = str(row.get('Configurations.type', 'NONE')).strip().upper()
            
            if config_type not in ['NONE', 'NAN'] and config_type:
                config_text = row.get('Package Detail selection ( Configuration )')
                config_title = row.get('Configurations.title', 'ตัวเลือก')
                config_id = row.get('Configurations.id', 'config-001')
                
                if pd.notna(config_text):
                    items = parse_configuration_text(config_text)
                    
                    if items:
                        config = {
                            "id": str(config_id) if pd.notna(config_id) else "config-001",
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
                        package["configurations"].append(config)
            
            packages.append(package)
        
        # Get placeholder key for this category
        placeholder_key = get_placeholder_key(category_slug)
        
        # Build JSON with I18N keys in components
        category_json = {
            "id": category_slug,
            "title": subcat_thai,  # Simple string
            "packages": packages,
            "cart_limit": cart_limit,
            "components": {
                "banner": {
                    "title": {
                        "key": "service.banner.title",
                        "kind": "I18N"
                    },
                    "button": {
                        "url": "https://www.fastwork.co/join",
                        "text": {
                            "key": "service.banner.button_text",
                            "kind": "I18N"
                        }
                    },
                    "subtitle": {
                        "key": "service.banner.subtitle",
                        "kind": "I18N"
                    }
                },
                "info_badge": [
                    {
                        "icon": "refund_icon",
                        "full_text": {
                            "key": "service.info_badge.refund",
                            "kind": "I18N"
                        },
                        "more_content": None,
                        "highlight_text": {
                            "key": "service.info_badge.refund",
                            "kind": "I18N"
                        }
                    },
                    {
                        "icon": "payment_icon",
                        "full_text": {
                            "key": "service.info_badge.cashback",
                            "kind": "I18N"
                        },
                        "more_content": None,
                        "highlight_text": {
                            "key": "service.info_badge.cashback",
                            "kind": "I18N"
                        }
                    }
                ],
                "location_box": {
                    "text": {
                        "at_pin": {
                            "description": None,
                            "placeholder": {
                                "kind": "I18N",
                                "key": placeholder_key
                            }
                        },
                        "online": {
                            "description": None,
                            "placeholder": None
                        },
                        "at_store": {
                            "description": None,
                            "placeholder": {
                                "kind": "I18N",
                                "key": placeholder_key
                            }
                        }
                    },
                    "visible": True,
                    "service_location_types": service_location_types,
                    "default_service_location_type": service_location_types[0] if service_location_types else "AT_PIN"
                },
                "cashback_section": {
                    "icon": "point_icon",
                    "full_text": {
                        "key": "summary.info_badge.cashback",
                        "kind": "I18N"
                    },
                    "highlight_text": {
                        "key": "summary.info_badge.cashback",
                        "kind": "I18N"
                    }
                },
                "summary_info_badge": [
                    {
                        "icon": "check_icon",
                        "full_text": {
                            "key": "summary.info_badge.payment",
                            "kind": "I18N"
                        },
                        "more_content": None,
                        "highlight_text": {
                            "key": "summary.info_badge.payment",
                            "kind": "I18N"
                        }
                    }
                ],
                "summary_location_box": {
                    "location": {
                        "text": {
                            "at_pin": {
                                "description": None,
                                "placeholder": {
                                    "kind": "I18N",
                                    "key": placeholder_key
                                }
                            },
                            "online": {
                                "description": None,
                                "placeholder": None
                            },
                            "at_store": {
                                "description": None,
                                "placeholder": {
                                    "kind": "I18N",
                                    "key": placeholder_key
                                }
                            }
                        },
                        "visible": True,
                        "service_location_types": service_location_types,
                        "default_service_location_type": service_location_types[0] if service_location_types else "AT_PIN"
                    },
                    "date_time": {
                        "visible": True,
                        "placeholder": "เลือกวันที่และเวลารับบริการ"
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
    "เลือกไฟล์ Excel (รูปแบบ Mint)",
    type=['xlsx', 'xls']
)

if uploaded_file is not None:
    try:
        df = pd.read_excel(uploaded_file)
        
        st.success(f"✅ อ่านไฟล์สำเร็จ! ({df.shape[0]} แถว, {df.shape[1]} คอลัมน์)")
        
        st.markdown("## 🔄 Step 2: แปลงเป็น JSON")
        
        if st.button("🚀 เริ่มแปลง", type="primary"):
            with st.spinner("กำลังแปลง..."):
                results = split_by_category(df)
            
            if results:
                st.session_state['results'] = results
                st.success(f"✅ แปลงสำเร็จ! พบ {len(results)} categories")
            else:
                st.error("❌ ไม่พบข้อมูล categories")
        
        if 'results' in st.session_state:
            results = st.session_state['results']
            
            st.markdown("## 📊 Step 3: เลือก Category")
            
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
                
                col1, col2, col3 = st.columns(3)
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
                
                # Generate JSON with proper line endings
                json_str = json.dumps(category_json, ensure_ascii=False, indent=2)
                json_str = json_str.replace('\r\n', '\n').replace('\r', '\n')
                
                st.markdown("### 🎯 Actions")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.download_button(
                        label="📥 ดาวน์โหลด JSON (แนะนำ)",
                        data=json_str.encode('utf-8'),
                        file_name=f"{selected_slug}.json",
                        mime="application/json",
                        use_container_width=True
                    )
                
                with col2:
                    show_json = st.checkbox("👁️ แสดง JSON Code เพื่อ Copy")
                
                if show_json:
                    st.markdown("### 📋 Copy JSON")
                    st.info("💡 **วิธี Copy:** เลือกทั้งหมด (Ctrl+A / Cmd+A) → Copy (Ctrl+C / Cmd+C)")
                    
                    st.text_area(
                        "JSON Code (LF line endings)",
                        value=json_str,
                        height=400,
                        key=f"json_copy_{selected_slug}"
                    )
                
                # Preview
                st.markdown("### 📦 Preview Packages")
                
                for pkg in category_json['packages']:
                    with st.expander(f"**{pkg['title']}** - ฿{pkg['base_price']:,}"):
                        st.markdown(f"**📝 คำอธิบาย:** {pkg['description']}")
                        st.markdown(f"**🆔 Package ID:** `{pkg['id']}`")
                        st.markdown(f"**📦 จำนวน:** {pkg['quantity']['validation']['min']} - {pkg['quantity']['validation']['max']} {pkg['quantity']['placeholder']}")
                        
                        if pkg['configurations']:
                            st.markdown("**⚙️ Configurations:**")
                            for config in pkg['configurations']:
                                st.markdown(f"- **{config['title']}** ({config['type']})")
                                for item in config['data']['items']:
                                    price_text = f"+฿{item['additional_price']}" if item['additional_price'] > 0 else "ฟรี"
                                    st.markdown(f"  - {item['value']} ({price_text})")
    
    except Exception as e:
        st.error(f"❌ เกิดข้อผิดพลาด: {str(e)}")
        st.exception(e)

else:
    st.info("""
    ### 📋 คำแนะนำ:
    
    **JSON Format แบบใหม่:**
    - `title`, `description`, `placeholder` → string ธรรมดา (ภาษาไทย)
    - `components` → ใช้ I18N keys จาก th.json, en.json
    - หากไม่มี key ในไฟล์ translation → ใช้ค่าจาก Excel
    
    **ตัวอย่าง:**
    ```json
    {
      "title": "บริการทำความสะอาด",  // แทน {kind: "INLINE", values: {...}}
      "placeholder": "จำนวน",        // แทน object
      "components": {
        "banner": {
          "title": {"key": "service.banner.title", "kind": "I18N"}
        }
      }
    }
    ```
    """)

st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666;">
    <p>🚀 Simplified JSON Converter v2.0 | Made with ❤️ for Fastwork</p>
</div>
""", unsafe_allow_html=True)
