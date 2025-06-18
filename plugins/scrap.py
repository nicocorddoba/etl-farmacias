from playwright.sync_api import sync_playwright

def launch_browser(chromium):
    browser = chromium.launch(headless=True, args=[
        "--disable-gpu",
        "--disable-dev-shm-usage",
        "--disable-software-rasterizer",
        "--no-sandbox",
        "--disable-extensions",
        "--disable-background-networking",
        "--disable-sync",
        "--disable-default-apps",
        "--mute-audio",
        # "--single-process" # Muy importante en instancias con poca RAM # DISCLAIMER: Parece cerrar el navegador
        "--no-zygote"
    ])
    context = browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 11.0; Win64; x64)...",
        viewport={"width": 1280, "height": 800},
        locale="en-US"
    )
    
    return context, browser

def run(url: str, logger= None):
    with sync_playwright() as playwright:
        logger.info("starting browser")
        chromium = playwright.chromium
        context, browser = launch_browser(chromium=chromium)
        page = context.new_page()
        page.goto(url)
        page.wait_for_selector("div[data-pagelet^='TimelineFeedUnit_']")
        image_locator = page.locator("a[href*='https://www.facebook.com/photo/?fbid=']").nth(1)
        # print(h.inner_html())
        src_url = image_locator.locator("img[alt*='May be']").get_attribute('src')
        # print(c)
        logger.info(f"Getting image response from {src_url}")
        response = context.request.get(src_url)
        image_bytes = response.body()
        playwright.close()
    return image_bytes
        # for i in range(c.count()):
        #     f = c.nth(i)
        #     print(i)
        #     print(f.get_attribute("alt"))
        