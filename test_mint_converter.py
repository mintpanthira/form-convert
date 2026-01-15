"""
Test script to verify Mint Excel to JSON converter
"""

import pandas as pd
import json
from mint_excel_to_json_converter import convert_mint_excel_to_json

def test_mint_conversion():
    print("🧪 Testing Mint Excel to JSON Converter\n")
    print("=" * 70)
    
    # Read the Mint test file
    print("\n1️⃣  Reading Mint test form.xlsx...")
    try:
        df = pd.read_excel('Mint test form.xlsx')
        print(f"   ✅ Successfully read Excel file")
        print(f"   📊 Data: {df.shape[0]} rows, {df.shape[1]} columns")
        
        # Count packages
        headers = df.iloc[0].tolist()
        df_data = df.iloc[1:].copy()
        df_data.columns = headers
        df_data.columns = df_data.columns.str.strip()
        
        packages_count = len(df_data[df_data['Package Name'].notna()])
        print(f"   📦 Found {packages_count} packages")
        
    except Exception as e:
        print(f"   ❌ Error reading Excel: {e}")
        return False
    
    # Convert to JSON
    print("\n2️⃣  Converting to JSON...")
    try:
        result_json = convert_mint_excel_to_json(df)
        print("   ✅ Successfully converted to JSON")
        
        # Validate structure
        print("\n3️⃣  Validating JSON structure...")
        assert 'id' in result_json, "Missing 'id' field"
        assert 'title' in result_json, "Missing 'title' field"
        assert 'packages' in result_json, "Missing 'packages' field"
        assert 'components' in result_json, "Missing 'components' field"
        
        print(f"   ✅ JSON structure is valid")
        
        # Check packages
        print(f"\n   📦 Packages converted: {len(result_json['packages'])}")
        
        # Show first 10 packages
        for i, pkg in enumerate(result_json['packages'][:10]):
            title_th = pkg['title']['values']['th']
            price = pkg['base_price']
            config_count = len(pkg['configurations'])
            
            print(f"      {i+1}. {pkg['id']}")
            print(f"         ├─ Title: {title_th}")
            print(f"         ├─ Price: ฿{price}")
            print(f"         └─ Configs: {config_count}")
            
            if pkg['configurations']:
                for config in pkg['configurations']:
                    print(f"            └─ {config['title']} ({config['type']}): {len(config['data']['items'])} items")
        
        if len(result_json['packages']) > 10:
            print(f"      ... และอีก {len(result_json['packages']) - 10} packages")
        
        # Statistics
        total_configs = sum(len(p['configurations']) for p in result_json['packages'])
        packages_with_config = sum(1 for p in result_json['packages'] if p['configurations'])
        
        print(f"\n   📊 Statistics:")
        print(f"      - Total packages: {len(result_json['packages'])}")
        print(f"      - Packages with configurations: {packages_with_config}")
        print(f"      - Total configurations: {total_configs}")
        
        # Save to file
        print("\n4️⃣  Saving to mint_output.json...")
        json_str = json.dumps(result_json, ensure_ascii=False, indent=2)
        with open('mint_output.json', 'w', encoding='utf-8') as f:
            f.write(json_str)
        print("   ✅ Saved successfully")
        
        # Show sample
        print("\n5️⃣  Sample JSON output (first package):")
        print("   " + "=" * 66)
        first_package = json.dumps(result_json['packages'][0], ensure_ascii=False, indent=2)
        for line in first_package.split('\n')[:30]:
            print(f"   {line}")
        print("   ...")
        print("   " + "=" * 66)
        
        print("\n" + "=" * 70)
        print("✅ All tests passed!")
        print("=" * 70)
        print(f"\n📁 Output file: mint_output.json")
        print(f"📏 JSON size: {len(json_str):,} bytes")
        print(f"📦 Total packages: {len(result_json['packages'])}")
        print(f"🎯 Service ID: {result_json['id']}")
        print(f"🏷️  Service Title: {result_json['title']['values']['th']}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error during conversion: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_mint_conversion()
    exit(0 if success else 1)
