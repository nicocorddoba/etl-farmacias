from playwright.sync_api import sync_playwright, Page

def fb_login(page: Page, context, FB_EMAIL: str, FB_PASSWORD: str):
    page.goto("https://www.facebook.com/login")
    
    page.fill('input[name="email"]', FB_EMAIL)
    page.fill('input[name="pass"]', FB_PASSWORD)
    page.click('button[name="login"]')

    # Esperar a que cargue algo del perfil
    page.wait_for_selector('[role="navigation"]', timeout=10000)

    # Guardar sesión para usar después
    context.storage_state(path="facebook_state.json")
    return context


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

def run(url: str, logger, FB_EMAIL: str, FB_PASSWORD: str) -> bytes:
    with sync_playwright() as playwright:
        logger.info("starting browser")
        chromium = playwright.chromium
        context, browser = launch_browser(chromium=chromium)
        page = context.new_page()
        context = fb_login(page=page, context=context, FB_EMAIL=FB_EMAIL, FB_PASSWORD=FB_PASSWORD)
        page.goto(url)
        page.wait_for_load_state("networkidle")
        # html = page.content()
        # with open("/home/ubuntu/debug_facebook.html", "w", encoding="utf-8") as f:
        #     f.write(html)
        #     f.close()
        page.wait_for_selector("div[data-pagelet^='TimelineFeedUnit_']")
        image_locator = page.locator("img[alt*='May be']").nth(0)
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
        