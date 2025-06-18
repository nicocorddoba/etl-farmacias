from playwright.sync_api import sync_playwright

def launch_browser(chromium):
    browser = chromium.launch(headless=True, args=[
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

        page.wait_for_selector("div._aagv")
        image_locator = page.locator("img[alt*='Photo by Farmacia']").nth(0)
        # print(c)
        src_url = image_locator.get_attribute('src')
        logger.info(f"Getting image response from {src_url}")
        response = context.request.get(src_url)
        image_bytes = response.body()
        browser.close()
    return image_bytes
        # for i in range(c.count()):
        #     f = c.nth(i)
        #     print(i)
        #     print(f.get_attribute("alt"))
        