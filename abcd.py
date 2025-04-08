import asyncio
from playwright.async_api import async_playwright
from asyncio import Semaphore

Leads = [
    "fashion", "real estate", "education", "ecommerce", "event management", "digital marketing", 
    "coaching", "consulting", "gym", "fitness", "interior design", "wedding planner", "photography", 
    "salon", "spa", "makeup artist", "cafes", "restaurants", 
    "architect", "freelancer", "lawyer", "accountant", "tax consultant", 
    "travel agency", "hr services","technician", "yoga", "meditation", "astrology", "numerology", 
    "branding", "influencer marketing", "ads agency", "social media agency", "video editing", 
    "content creation", "app development", "software", "saas", "b2b", "enterprise solution", 
    "productivity tool", "erp", "crm", "email marketing", "automation", 
    "webinar", "virtual event", "online course", "membership", "community", "startup", 
    "venture","book publisher", "public speaker", "career coach", 
    "life", "homeloan", "insurance", "mutual funds", "stock market", "trading", 
    "crypto", "blockchain", "ai tools", "chatbot", "ai integration", 
    "cybersecurity", "compliance", "legal tech",
    "b2g", "agritech", "edtech", "fintech"
]

from_date = '2025-04-05'
to_date = '2025-04-08'
country = 'IN'
active_status = 'active'
platform = 'facebook'

URL = set()
sema = Semaphore(5)

async def scrape_ads(keyword, page):
    async with sema:
        search_url = (
            f"https://www.facebook.com/ads/library/?"
            f"active_status={active_status}&ad_type=all&country={country}"
            f"&media_type=all&platforms={platform}"
            f"&q={keyword}"
            f"&start_date={from_date}&end_date={to_date}"
            f"&sort_data[direction]=desc&sort_data[mode]=relevancy_monthly_grouped"
        )

        await page.goto(search_url, timeout=60000)
        await page.wait_for_selector('div.x1lliihq', timeout=15000)

        last_height = 0
        retries = 0
        for i in range(2):
            await page.mouse.wheel(0, 10000)
            await asyncio.sleep(2)
            new_height = await page.evaluate("() => document.documentElement.scrollHeight")
            if new_height == last_height:
                retries += 1
            else:
                retries = 0
            last_height = new_height

        anchors = await page.query_selector_all('a[href*="facebook.com/"]')
        for anchor in anchors:
            href = await anchor.get_attribute('href')
            if href and "facebook.com/" in href and not "l.facebook.com" in href:
                cleaned = href.split('?')[0]
                if '/ads/library' not in cleaned and '/ads/' not in cleaned:
                    URL.add(cleaned)

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        tasks = [scrape_ads(keyword, page) for keyword in Leads]
        await asyncio.gather(*tasks)

        await browser.close()

        with open("leads.txt", "w") as f:
            for link in sorted(URL):
                f.write(link + "\n")
    print(f"\n🎯 Total unique profiles found: {len(URL)}\n")

asyncio.run(main())
