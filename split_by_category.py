"""
Split Mint Excel to multiple JSON files by Category slug
แยกไฟล์ JSON ตาม Category slug
"""

import pandas as pd
import json
import os
from mint_excel_to_json_converter import convert_mint_excel_to_json

def split_by_category(excel_file='Mint test form.xlsx', output_dir='json_output'):
    """
    แยก JSON ตาม Category slug
    
    Output:
    - cleaning.json
    - air-cleaning.json
    - massage.json
    - hair-salon.json
    - etc.
    """
    
    print("🔄 กำลังอ่านไฟล์ Excel...")
    df = pd.read_excel(excel_file)
    
    # Set headers
    headers = df.iloc[0].tolist()
    df_data = df.iloc[1:].copy()
    df_data.columns = headers
    df_data.columns = df_data.columns.str.strip()
    
    # Get unique categories
    categories = df_data[df_data['Category slug'].notna()]['Category slug'].unique()
    
    print(f"\n📊 พบ {len(categories)} categories:")
    for cat in categories:
        print(f"   - {cat}")
    
    # Create output directory
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Split by category
    results = {}
    
    for category_slug in categories:
        print(f"\n🔄 กำลังแปลง category: {category_slug}")
        
        # Filter data for this category
        category_data = df_data[
            (df_data['Category slug'] == category_slug) | 
            (df_data['Package Id'].str.startswith(category_slug, na=False))
        ]
        
        if category_data.empty:
            continue
        
        # Get category info from first row
        category_rows = category_data[category_data['Category'].notna()]
        if len(category_rows) > 0:
            first_row = category_rows.iloc[0]
            category_name = first_row.get('Category', category_slug)
            
            # Try different column name variations
            subcat_thai = None
            for col in df_data.columns:
                if 'subcat' in col.lower() and 'thai' in col.lower():
                    subcat_thai = first_row.get(col, '')
                    break
            if not subcat_thai:
                subcat_thai = category_name
                
            cart_limit = int(first_row.get('Cart limit', 30)) if pd.notna(first_row.get('Cart limit')) else 30
        else:
            # Fallback if no Category column
            first_row = category_data.iloc[0]
            category_name = category_slug.replace('-', ' ').title()
            subcat_thai = category_name
            cart_limit = 30
        
        # Build packages for this category
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
            
            from mint_excel_to_json_converter import create_inline_text, parse_configuration_text
            
            package = {
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
        
        # Build JSON for this category
        from mint_excel_to_json_converter import create_i18n_text, create_inline_text
        
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
        
        # Save to file
        output_file = f"{output_dir}/{category_slug}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(category_json, f, ensure_ascii=False, indent=2)
        
        print(f"   ✅ บันทึก: {output_file}")
        print(f"      - Packages: {len(packages)}")
        print(f"      - Size: {len(json.dumps(category_json)):,} bytes")
        
        results[category_slug] = {
            'file': output_file,
            'packages': len(packages),
            'category_name': category_name,
            'subcat_thai': subcat_thai
        }
    
    # Create index file
    index_file = f"{output_dir}/index.json"
    with open(index_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ เสร็จสมบูรณ์!")
    print(f"📁 ไฟล์ทั้งหมดอยู่ใน: {output_dir}/")
    print(f"📋 Index file: {index_file}")
    
    return results

if __name__ == "__main__":
    results = split_by_category()
    
    print("\n" + "=" * 70)
    print("📊 สรุป:")
    print("=" * 70)
    
    for slug, info in results.items():
        print(f"\n📦 {slug}")
        print(f"   Category: {info['category_name']}")
        print(f"   Thai: {info['subcat_thai']}")
        print(f"   Packages: {info['packages']}")
        print(f"   File: {info['file']}")
