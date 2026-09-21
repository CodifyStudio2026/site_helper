#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🌐 Site Helper — یه اسکریپت تک‌فایلی که به سلامت سایتت کمک می‌کنه.

قابلیت‌ها:
  - چک کردن آنلاین بودن سایت و زمان پاسخ
  - گرفتن عنوان (title) و توضیحات متا (meta description)
  - پیدا کردن لینک‌های خراب (broken links) توی صفحه
  - هشدار برای تصاویر بدون alt و نبود متا دیسکریپشن (چک ساده SEO)

نصب پیش‌نیاز:
    pip install requests beautifulsoup4

استفاده:
    python site_helper.py https://example.com
"""

import sys
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse


def check_site(url: str):
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    print(f"\n🔎 در حال بررسی: {url}\n" + "-" * 40)

    # 1) وضعیت آنلاین بودن
    try:
        resp = requests.get(url, timeout=10, headers={"User-Agent": "SiteHelperBot/1.0"})
        print(f"✅ سایت آنلاینه — کد وضعیت: {resp.status_code}")
        print(f"⏱️ زمان پاسخ: {resp.elapsed.total_seconds():.2f} ثانیه")
    except requests.RequestException as e:
        print(f"❌ سایت در دسترس نیست: {e}")
        return

    soup = BeautifulSoup(resp.text, "html.parser")

    # 2) عنوان و توضیحات متا
    title = soup.title.string.strip() if soup.title and soup.title.string else None
    print(f"\n📄 عنوان صفحه: {title or '⚠️ عنوان پیدا نشد'}")

    meta_desc = soup.find("meta", attrs={"name": "description"})
    if meta_desc and meta_desc.get("content"):
        print(f"📝 توضیحات متا: {meta_desc['content'][:120]}")
    else:
        print("⚠️ توضیحات متا (meta description) تنظیم نشده — برای SEO بد نیست اضافه کنی.")

    # 3) تصاویر بدون alt
    images = soup.find_all("img")
    no_alt = [img for img in images if not img.get("alt")]
    print(f"\n🖼️ تعداد کل تصاویر: {len(images)}")
    if no_alt:
        print(f"⚠️ {len(no_alt)} تصویر بدون alt پیدا شد (بد برای SEO و دسترسی‌پذیری).")
    else:
        print("✅ همه‌ی تصاویر alt دارن.")

    # 4) چک کردن لینک‌های خراب
    links = {urljoin(url, a["href"]) for a in soup.find_all("a", href=True)}
    same_domain_only = [l for l in links if urlparse(l).netloc in ("", urlparse(url).netloc)]
    print(f"\n🔗 تعداد لینک‌های پیدا‌شده: {len(links)} (در حال چک کردن {min(len(links), 20)} تای اول...)")

    broken = []
    for link in list(links)[:20]:  # برای سرعت بیشتر فقط ۲۰ تای اول چک میشه
        try:
            r = requests.head(link, timeout=5, allow_redirects=True, headers={"User-Agent": "SiteHelperBot/1.0"})
            if r.status_code >= 400:
                broken.append((link, r.status_code))
        except requests.RequestException:
            broken.append((link, "بدون پاسخ"))

    if broken:
        print(f"❌ {len(broken)} لینک خراب پیدا شد:")
        for link, status in broken:
            print(f"   - {link} → {status}")
    else:
        print("✅ هیچ لینک خرابی (تو ۲۰ تای بررسی‌شده) پیدا نشد.")

    print("\n" + "-" * 40 + "\n🏁 بررسی تموم شد.\n")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("استفاده: python site_helper.py <آدرس سایت>")
        print("مثال:   python site_helper.py example.com")
        sys.exit(1)
    check_site(sys.argv[1])
