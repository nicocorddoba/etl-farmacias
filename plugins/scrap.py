from playwright.sync_api import sync_playwright

def launch_browser(chromium):
    browser = chromium.launch(headless=False, args=[
        "--disable-gpu",
        "--disable-dev-shm-usage",
        "--disable-software-rasterizer",
        # "--no-sandbox",
        "--disable-extensions",
        "--disable-background-networking",
        "--disable-sync",
        "--disable-default-apps",
        "--mute-audio"
        # "--single-process" # Muy importante en instancias con poca RAM # DISCLAIMER: Parece cerrar el navegador
        # "--no-zygote"
    ])
    context = browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 11.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Brave/114.0.0.0",
        viewport={"width": 1280, "height": 800},
        locale="en-US",
        extra_http_headers={
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "es-ES,es;q=0.7",
            "Cache-Control": "max-age=0",
            "Sec-CH-UA": '""',
            "Sec-CH-UA-Mobile": "?0",
            "Sec-CH-UA-Platform": '""',
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-User": "?1",
            "Sec-GPC": "1",
            "Upgrade-Insecure-Requests": "1"
        }
    )
    
    return context, browser

def run(url: str, logger= None):
    with sync_playwright() as playwright:
        logger.info("starting browser")
        chromium = playwright.chromium
        context, browser = launch_browser(chromium=chromium)
        page = context.new_page()
        page.goto(url)
        page.wait_for_load_state("networkidle")
        logger.info(f"Page title: {page.title()}")
        html = page.content()
        with open("/home/ubuntu/debug_facebook.html", "w", encoding="utf-8") as f:
            f.write(html)
            f.close()
        page.wait_for_selector("div[data-pagelet^='TimelineFeedUnit_']")
        image_locator = page.locator("a[href*='https://www.facebook.com/photo/?fbid=']").nth(1)
        # print(h.inner_html())
        src_url = image_locator.locator("img[alt*='May be']").get_attribute('src')
        # print(c)
        logger.info(f"Getting image response from {src_url}")
        response = context.request.get(src_url)
        image_bytes = response.body()
        browser.close()
    return image_bytes
        # for i in range(c.count()):
        #     f = c.nth(i)
        #     print(i)
        #     print(f.get_attribute("alt"))
        