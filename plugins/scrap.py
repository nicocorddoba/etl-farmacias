from playwright.sync_api import sync_playwright, Page
import os
import time

def ig_login(page: Page, context, logger):
    page.goto("https://www.instagram.com/accounts/login/")

    # 2. Esperar a que cargue el formulario
    page.wait_for_selector('input[name="username"]')

    # 3. Completar los campos
    page.fill('input[name="username"]', USERNAME)
    page.fill('input[name="password"]', PASSWORD)

    # 4. Hacer clic en "Iniciar sesión"
    page.click('button[type="submit"]')
    

    # 5. Esperar a que se redirija (perfil, feed, etc.)
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(10000)
    logger.info("Waiting for Instagram to load after login")
    time.sleep(4)  # Esperar un poco para que la página cargue después del login
    # Esperar a que cargue algo del perfil
    # page.wait_for_selector('[role="navigation"]', timeout=10000)

    # Guardar sesión para usar después
    context.storage_state(path="./instagram.json")
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
        locale="en-US"
    )
    
    return context, browser

def run(url: str, logger) -> bytes:
    with sync_playwright() as playwright:
        logger.info("starting browser")
        chromium = playwright.chromium
        context, browser = launch_browser(chromium=chromium)
        page = context.new_page()
        context = ig_login(page=page, context=context, logger= logger)
        page.goto(url)
        page.wait_for_load_state("networkidle")
        feed = page.locator("div._aagu") # Select the feed
        image_locator = feed.locator("img[alt*='Photo by Farmacia Martina']").nth(0).get_attribute('src') # Link to the first image publication
        logger.info(f"Getting image response from {image_locator}")
        # # context = fb_login(page=page, context=context, logger= logger)
        # page.goto(image_locator)
        # page.wait_for_load_state("networkidle")
        # src_url = page.locator("img[alt*='May be an image of text that says']").get_attribute('src') # Link to the first image
        # print(c)
        logger.info(f"Getting image response from {image_locator}")
        response = context.request.get(image_locator)
        image_bytes = response.body()
        browser.close()
    return image_bytes
        # for i in range(c.count()):
        #     f = c.nth(i)
        #     print(i)
        #     print(f.get_attribute("alt"))
        