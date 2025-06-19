from playwright.sync_api import sync_playwright, Page
import os
import time

def fb_login(page: Page, context, logger):
    page.goto("https://www.facebook.com/login")
    FB_EMAIL = os.getenv("FB_EMAIL")
    FB_PASSWORD = os.getenv("FB_PASSWORD")
    logger.info("Logging in to Facebook")
    page.fill('input[name="email"]', FB_EMAIL)
    page.fill('input[name="pass"]', FB_PASSWORD)
    page.click('button[name="login"]')
    logger.info("Waiting for Facebook to load after login")
    time.sleep(4)  # Esperar un poco para que la página cargue después del login
    # Esperar a que cargue algo del perfil
    # page.wait_for_selector('[role="navigation"]', timeout=10000)

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
        storage_state=os.getenv("FB_STORAGE_STATE")
    )
    
    return context, browser

def run(url: str, logger) -> bytes:
    with sync_playwright() as playwright:
        logger.info("starting browser")
        chromium = playwright.chromium
        context, browser = launch_browser(chromium=chromium)
        page = context.new_page()
        # context = fb_login(page=page, context=context, logger= logger)
        page.goto(url)
        page.wait_for_load_state("networkidle")
        feed = page.locator("div[data-pagelet^='TimelineFeedUnit_']") # Select the feed
        image_locator = feed.locator("a[href*='https://www.facebook.com/photo/?fbid=']").nth(0).get_attribute('href') # Link to the first image publication
        logger.info(f"Getting image response from {image_locator}")
        # context = fb_login(page=page, context=context, logger= logger)
        page.goto(image_locator)
        page.wait_for_load_state("networkidle")
        src_url = page.locator("img[alt*='May be an image of text that says']").get_attribute('src') # Link to the first image
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
        