# 📊 Mint Excel to JSON Converter

เครื่องมือแปลงไฟล์ Excel เป็น JSON สำหรับ Service Definition ของ Fastwork

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://your-app.streamlit.app)

## 🚀 Features

- ✅ แปลง Excel เป็น JSON รูปแบบ Service Definition
- ✅ รองรับ Configuration แบบ RADIO และ CHECKBOX
- ✅ คำนวณราคาเพิ่มเติมอัตโนมัติ
- ✅ Preview ข้อมูลก่อนแปลง
- ✅ ดาวน์โหลด JSON ทันที
- ✅ UI สวยงาม ใช้งานง่าย

## 🎯 วิธีใช้งาน

### 1. เข้าใช้งาน Web App

เปิดเว็บเบราว์เซอร์แล้วเข้า: **https://your-app.streamlit.app**

### 2. อัปโหลดไฟล์ Excel

อัปโหลดไฟล์ Excel ที่มีรูปแบบตาม `Mint test form.xlsx`

### 3. แปลงเป็น JSON

กดปุ่ม "แปลงเป็น JSON" และดาวน์โหลดไฟล์ที่ได้

## 📋 รูปแบบไฟล์ Excel

### Headers (Row 0)

ไฟล์ Excel ต้องมี Headers ดังนี้:

- `Category` - หมวดหมู่บริการ
- `Subcat thai` - หมวดหมู่ย่อย (ภาษาไทย)
- `Category slug` - Service ID
- `Cart limit` - จำนวนสูงสุดในตะกร้า
- `Package Name` - ชื่อแพ็คเกจ
- `Package Id` - รหัสแพ็คเกจ
- `Package Description` - รายละเอียดแพ็คเกจ
- `Starting price` - ราคาเริ่มต้น
- `min` - จำนวนขั้นต่ำ
- `max` - จำนวนสูงสุด
- `quantity.placeholder` - placeholder สำหรับจำนวน
- `Configurations.title` - ชื่อ Configuration
- `Package Detail selection ( Configuration )` - ตัวเลือก Configuration
- `Configurations.id` - รหัส Configuration
- `Configurations.type` - ประเภท Configuration (RADIO, CHECKBOX, NONE)
- `other text field - placeholder` - placeholder สำหรับหมายเหตุ
- `service_location_types` - ประเภทสถานที่ (AT_PIN, AT_STORE, ONLINE)

### รูปแบบ Configuration

ในคอลัมน์ `Package Detail selection ( Configuration )` ใช้รูปแบบ:

```
ขนาดพื้นที่
- 25 - 40 ตร.ม. (2 ชั่วโมง)
- 40 - 60 ตร.ม. (3 ชั่วโมง) +250 THB
- 60 - 80 ตร.ม. (4 ชั่วโมง) +500 THB
```

**หมายเหตุ:**
- ขึ้นต้นด้วย `- ` ทุกตัวเลือก
- ราคาเพิ่มใช้รูปแบบ: `+จำนวน THB`
- ถ้าไม่ระบุราคา = ราคาเพิ่ม 0

### Configuration Types

- `NONE` - ไม่มี configuration (`configurations: []`)
- `RADIO` - เลือกได้ 1 อย่าง (single select)
- `CHECKBOX` - เลือกได้หลายอย่าง (multiple select)
- `DATE_TIME_RANGE` - เลือกช่วงวันที่และเวลา

### Multiple Configurations

**1 package สามารถมีหลาย configurations ได้** (สูงสุด 5 configurations)

ใช้ suffix `.2`, `.3`, `.4`, `.5` สำหรับ configuration เพิ่มเติม:

**Configuration 1:**
- `Configurations.title`
- `Configurations.type`
- `Configurations.id`
- `Package Detail selection ( Configuration )`

**Configuration 2:**
- `Configurations.title.2`
- `Configurations.type.2`
- `Configurations.id.2`
- `Package Detail selection ( Configuration ).2`

**ตัวอย่าง:** Package "นวดคอบ่าไหล่" มี 2 configurations:
1. **ขนาดพื้นที่** (RADIO) - เลือก 1 จาก 5 ตัวเลือก
2. **คำขอพิเศษ** (CHECKBOX) - เลือกได้หลายอย่าง

## 🛠️ ติดตั้งและรันในเครื่อง

### Requirements

- Python 3.8+
- pip

### การติดตั้ง

```bash
# Clone repository
git clone <your-repo-url>
cd form-fastmatch-mint

# สร้าง virtual environment
python -m venv venv

# Activate virtual environment
# macOS/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# ติดตั้ง dependencies
pip install -r requirements.txt
```

### รัน Web App

```bash
streamlit run mint_excel_to_json_converter.py
```

เปิดเว็บเบราว์เซอร์ที่: http://localhost:8501

## 📦 Deploy บน Streamlit Cloud

### ขั้นตอนการ Deploy

1. **Push code ขึ้น GitHub**

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin <your-github-repo-url>
git push -u origin main
```

2. **ไปที่ Streamlit Cloud**

เข้า: https://streamlit.io/cloud

3. **เข้าสู่ระบบด้วย GitHub**

4. **กด "New app"**

5. **กรอกข้อมูล:**
   - Repository: เลือก repository ของคุณ
   - Branch: `main`
   - Main file path: `mint_excel_to_json_converter.py`

6. **กด "Deploy!"**

เสร็จแล้ว! จะได้ URL เป็น: `https://your-app.streamlit.app`

## 📁 โครงสร้างโปรเจค

```
form-fastmatch-mint/
├── mint_excel_to_json_converter.py  # Web App หลัก
├── all_in_one_converter.py          # Converter แบบ all-in-one
├── simplified_converter.py          # Converter แบบง่าย
├── split_by_category.py             # แยกไฟล์ตาม category
├── test_mint_converter.py           # Test script
├── Mint test form.xlsx              # ไฟล์ตัวอย่าง
├── requirements.txt                 # Python dependencies
├── .streamlit/
│   └── config.toml                  # Streamlit configuration
├── json_output/                     # Output directory
├── HOW_TO_USE.txt                   # คู่มือใช้งานสั้น
├── USAGE_GUIDE.txt                  # คู่มือโดยละเอียด
└── README.md                        # ไฟล์นี้
```

## 🧪 ทดสอบด้วย Command Line

```bash
# Activate virtual environment
source venv/bin/activate

# รัน test script
python test_mint_converter.py

# ได้ไฟล์: mint_output.json
```

## 📚 ไฟล์ที่เกี่ยวข้อง

- `mint_excel_to_json_converter.py` - Streamlit Web App (แนะนำ)
- `all_in_one_converter.py` - แปลงทุกแถวเป็นไฟล์เดียว
- `simplified_converter.py` - แปลงแบบง่าย
- `split_by_category.py` - แยกไฟล์ตาม category
- `test_mint_converter.py` - ทดสอบการแปลง

## 🎨 Customization

### เปลี่ยนธีม

แก้ไขไฟล์ `.streamlit/config.toml`:

```toml
[theme]
primaryColor = "#FF4B4B"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"
```

### เพิ่มขนาดไฟล์สูงสุด

แก้ไขใน `.streamlit/config.toml`:

```toml
[server]
maxUploadSize = 200  # MB
```

## 🐛 Troubleshooting

### ปัญหา: ไม่สามารถอ่านไฟล์ Excel

**วิธีแก้:** ตรวจสอบว่าไฟล์เป็น `.xlsx` หรือ `.xls` และมี Headers ครบถ้วน

### ปัญหา: Configuration ไม่แสดง

**วิธีแก้:** ตรวจสอบว่า:
- `Configurations.type` ไม่ใช่ `NONE`
- มีข้อมูลใน `Package Detail selection ( Configuration )`
- ขึ้นต้นด้วย `- ` ทุกบรรทัด

### ปัญหา: ราคาเพิ่มไม่ถูกต้อง

**วิธีแก้:** ใช้รูปแบบ `+จำนวน THB` เช่น `+250 THB`, `+500 THB`

## 📄 License

MIT License - ใช้ได้อย่างอิสระ

## 👨‍💻 Author

Fastwork Team

## 🙏 Credits

- Built with [Streamlit](https://streamlit.io/)
- Excel parsing with [Pandas](https://pandas.pydata.org/)
- Excel reading with [OpenPyXL](https://openpyxl.readthedocs.io/)

---

**Happy Converting! 🎉**
