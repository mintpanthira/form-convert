# 🚀 คู่มือ Deploy บน Streamlit Cloud

## ขั้นตอนการ Deploy แบบละเอียด

### 1️⃣ เตรียม Repository บน GitHub

#### 1.1 สร้าง Repository ใหม่บน GitHub

1. ไปที่ https://github.com/new
2. ตั้งชื่อ repository เช่น `mint-excel-converter`
3. เลือก **Public** (จำเป็นสำหรับ Streamlit Cloud ฟรี)
4. **อย่าเพิ่ม** README, .gitignore, license (เพราะมีอยู่แล้ว)
5. กด **Create repository**

#### 1.2 Push Code ขึ้น GitHub

เปิด Terminal และรันคำสั่ง:

```bash
# ไปที่โฟลเดอร์โปรเจค
cd /Users/fastwork/Desktop/form-fastmatch-mint

# Initialize Git (ถ้ายังไม่ได้ทำ)
git init

# เพิ่มไฟล์ทั้งหมด
git add .

# Commit
git commit -m "Initial commit: Mint Excel to JSON Converter"

# เปลี่ยน branch เป็น main
git branch -M main

# เพิ่ม remote (แทนที่ YOUR_USERNAME และ YOUR_REPO)
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git

# Push ขึ้น GitHub
git push -u origin main
```

### 2️⃣ Deploy บน Streamlit Cloud

#### 2.1 ไปที่ Streamlit Cloud

1. เปิดเว็บ: https://streamlit.io/cloud
2. กด **"Sign in with GitHub"**
3. Login ด้วย GitHub account ของคุณ

#### 2.2 สร้าง App ใหม่

1. กด **"New app"** (ปุ่มสีแดง มุมขวาบน)
2. กรอกข้อมูล:
   - **Repository:** เลือก `YOUR_USERNAME/YOUR_REPO`
   - **Branch:** `main`
   - **Main file path:** `mint_excel_to_json_converter.py`
   - **App URL:** เลือก URL ที่ต้องการ (ถ้าว่างจะสุ่มให้)

3. กด **"Deploy!"**

#### 2.3 รอ Deploy เสร็จ

- ใช้เวลา 2-5 นาที
- จะเห็น log การติดตั้ง
- เมื่อเสร็จจะขึ้น **"Your app is live!"** 🎉

### 3️⃣ ใช้งาน App

URL ของคุณจะเป็น: `https://your-app-name.streamlit.app`

## 📋 Checklist ก่อน Deploy

- ✅ มีไฟล์ `requirements.txt` (ครบทุก package)
- ✅ มีไฟล์ `.streamlit/config.toml` (optional แต่แนะนำ)
- ✅ มีไฟล์ `.gitignore` (ไม่ push `venv/` และ `__pycache__/`)
- ✅ ทดสอบรันในเครื่องสำเร็จ (`streamlit run mint_excel_to_json_converter.py`)
- ✅ Repository เป็น **Public** บน GitHub
- ✅ Push code ขึ้น GitHub สำเร็จ

## 🔧 การตั้งค่า Custom Domain (Optional)

Streamlit Cloud รองรับ Custom Domain แต่ต้อง upgrade เป็น:
- **Starter Plan:** $20/month
- **Team Plan:** $250/month

### ใช้ Default Domain (ฟรี)

URL เริ่มต้น: `https://your-app-name.streamlit.app`

## 🔄 อัปเดต App

เมื่อต้องการอัปเดตโค้ด:

```bash
# แก้ไขโค้ด
# ...

# Commit และ Push
git add .
git commit -m "Update: description of changes"
git push

# Streamlit Cloud จะ auto-deploy ใหม่ภายใน 1-2 นาที
```

## 🐛 แก้ปัญหา

### ปัญหา: Deploy ล้มเหลว

**สาเหตุ:** `requirements.txt` ไม่ครบหรือมี package ที่ติดตั้งไม่ได้

**วิธีแก้:**
1. ตรวจสอบ log ใน Streamlit Cloud
2. ตรวจสอบ `requirements.txt` ว่าครบทุก package
3. ลองรันในเครื่องก่อน

### ปัญหา: ไม่พบไฟล์ `mint_excel_to_json_converter.py`

**สาเหตุ:** ใส่ path ไม่ถูก

**วิธีแก้:**
- ตรวจสอบว่าไฟล์อยู่ที่ root ของ repository
- Main file path ต้องเป็น: `mint_excel_to_json_converter.py` (ไม่มี `/` ข้างหน้า)

### ปัญหา: App ช้ามาก

**สาเหตุ:** Free tier มี resource จำกัด

**วิธีแก้:**
- Optimize โค้ด
- ลด caching
- พิจารณา upgrade plan

### ปัญหา: อัปโหลดไฟล์ใหญ่ไม่ได้

**สาเหตุ:** ขนาดไฟล์เกิน limit

**วิธีแก้:**
- ดู `maxUploadSize` ใน `.streamlit/config.toml` (ตอนนี้ตั้งไว้ที่ 200 MB)
- Free tier limit: 200 MB
- Paid tier limit: 400 MB

## 📊 Resource Limits (Free Tier)

- **CPU:** 1 vCPU
- **Memory:** 1 GB RAM
- **Storage:** 1 GB
- **Upload:** 200 MB/file
- **Apps:** 1 app (unlimited viewers)
- **Runtime:** Sleep after 7 days inactive

## 💰 Pricing Plans (ถ้าต้องการ Upgrade)

### Free Plan (Community Cloud)
- ✅ 1 public app
- ✅ 1 GB RAM
- ✅ Unlimited viewers
- ❌ No custom domain
- ❌ No secrets management UI

### Starter Plan - $20/month
- ✅ 3 private apps
- ✅ 2 GB RAM
- ✅ Custom domain
- ✅ Secrets management UI
- ✅ Priority support

### Team Plan - $250/month
- ✅ 10 private apps
- ✅ 4 GB RAM
- ✅ All features
- ✅ SSO support
- ✅ Dedicated support

## 🔒 Secrets Management (สำหรับ API Keys)

ถ้ามี API keys หรือ credentials:

1. ไปที่ App Settings ใน Streamlit Cloud
2. เลือก **Secrets**
3. เพิ่ม secrets ในรูปแบบ TOML:

```toml
[api]
key = "your-api-key"

[database]
host = "your-db-host"
password = "your-password"
```

4. เข้าถึงในโค้ด:

```python
import streamlit as st

api_key = st.secrets["api"]["key"]
```

## 📞 Support

- **Streamlit Docs:** https://docs.streamlit.io/
- **Community Forum:** https://discuss.streamlit.io/
- **GitHub Issues:** https://github.com/streamlit/streamlit/issues

---

**Happy Deploying! 🚀**
