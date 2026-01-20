import logging
import asyncio
from playwright.async_api import async_playwright, Page, Browser
import time
from app.domain.interfaces.IBrowserService import IBrowserService
from datetime import datetime

class BrowserService(IBrowserService):

    logger = logging.getLogger(__name__)

    UA = "Opera/70.0 (Windows NT 6.0) Presto/2.12.388 Version/12.14"

    def __init__(self):
        self.url = "https://portalrestituciondetierras.ramajudicial.gov.co/#/busqueda/reporteEstados"

    # ==========================================================
    # 🚀 MÉTODO PRINCIPAL
    # ==========================================================
    async def scrapper_screenshots_notifications( self,city: str, court_office: str,current_year: str,litigando_court_id: int):
        browser = None

        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(
                    headless=True,
                    args=["--no-sandbox", "--disable-dev-shm-usage"]
                )

                screenshot_path= await self.screenshots_notifications(browser, city,court_office, current_year, litigando_court_id)
              
                return screenshot_path
            
        except asyncio.CancelledError:
            self.logger.warning("⚠️ Tarea de scrapper cancelada.")
            return

        except Exception as e:
            self.logger.exception(f"❌ Error general en scrapper: {e}")
            return

        finally:
            if browser:
                try:
                    await browser.close()
                except Exception as e:
                    self.logger.warning(f"⚠️ Error cerrando navegador: {e}")

    # ==========================================================
    # 🌐 NAVEGACIÓN + SELECCIÓN
    # ==========================================================
    async def screenshots_notifications( self,  browser: Browser, city: str,  court_office: str, current_year: str,  litigando_court_id: int ) -> None:

        try:
            context = await browser.new_context(
                user_agent=self.UA,
                accept_downloads=True,
                viewport={"width": 1400, "height": 1080},
            )

            page: Page = await context.new_page()
            page.set_default_navigation_timeout(0)

            self.logger.info(f"🌐 Navegando a {self.url}")
            await page.goto(self.url, wait_until="domcontentloaded")

            # 🏙️ Seleccionar ciudad
            selected_city= await self.select_city(page, city)


            # 🏛️ Seleccionar despacho judicial
            if selected_city:
                court_office_selec= await self.select_court_office(page, court_office)

                if court_office_selec:


                    time.sleep(4)

                    fecha_hora_fmt = datetime.now().strftime("%d_%m_%Y_%H_%M_%S")

                    screenshot_path = (
                        f"/app/output/img/estados/"
                        f"{fecha_hora_fmt}_{litigando_court_id}_{court_office}.png"
                    )
                    await page.screenshot(path=screenshot_path)
                    self.logger.info( f"📸 Captura guardada correctamente | despacho_id={litigando_court_id} | despacho='{court_office}' | ruta={screenshot_path}")
                    return screenshot_path
                else:
                    self.logger.error("No se logro seleccionar el despacho  ")
                    return None
                    
            else:
                self.logger.error("No se logro seleccionar la ciudad ")
                return None
                
            
            
        except Exception as e:
            self.logger.exception(f"❌ Error en screenshots_notifications: {e}")
            return None


  # ==========================================================
    # 🏙️ SELECCIÓN DE CIUDAD POR INPUT (PRIMENG)
    # ==========================================================
    async def select_city(self, page: Page, city: str):
        """
        Selecciona ciudad en p-dropdown PrimeNG usando texto visible (robusto)
        """
        city = city.strip().upper()
        self.logger.info(f"🏙️ Buscando ciudad por input: {city}")

        try:
            # 1️⃣ Abrir dropdown (PRIMER p-dropdown)
            dropdown = page.locator("p-dropdown").first
            await dropdown.click()

            # 2️⃣ Esperar input de búsqueda
            filter_input = page.locator("input.p-dropdown-filter")
            await filter_input.wait_for(state="visible", timeout=10000)

            # 3️⃣ Escribir ciudad
            await filter_input.fill("")
            await filter_input.type(city, delay=30)

            # 4️⃣ Esperar render de opciones
            await asyncio.sleep(0.6)

            # 5️⃣ Buscar opción por TEXTO VISIBLE (NO aria-label)
            option = page.locator(
                "li[role='option']",
                has_text=city
            ).first

            await option.wait_for(state="visible", timeout=5000)
            await option.click()

            self.logger.info(f"✅ Ciudad seleccionada: {city}")
            return city

        except Exception as e:
            self.logger.exception(f"❌ Error seleccionando ciudad {city}: {e}")
            return None

    # ==========================================================
    # 🏛️ SELECCIÓN DE DESPACHO JUDICIAL (PrimeNG + Virtual Scroll)
    # ==========================================================
    async def select_court_office(self, page: Page, court_office: str):
        """
        Selecciona el despacho judicial en un p-dropdown PrimeNG
        usando scroll virtual (cdk-virtual-scroll)
        """

        court_office = court_office.strip()
        self.logger.info(f"🏛️ Seleccionando despacho judicial: {court_office}")

        try:
            # 1️⃣ Abrir el dropdown del despacho (SEGUNDO p-dropdown)
            dropdowns = page.locator("p-dropdown")
            await dropdowns.nth(1).click()

            # 2️⃣ Esperar el PANEL del dropdown (NO el viewport global)
            panel = page.locator("div.p-dropdown-panel").last
            await panel.wait_for(state="visible", timeout=5000)

            # 3️⃣ Obtener el viewport SOLO de este panel
            viewport = panel.locator("cdk-virtual-scroll-viewport")
            await viewport.wait_for(state="visible", timeout=5000)

            option_selector = f"li[role='option'][aria-label='{court_office}']"
            option = panel.locator(option_selector)

            found = False

            # 4️⃣ Scroll controlado
            for _ in range(20):
                if await option.count() > 0:
                    found = True
                    break

                await viewport.evaluate("(el) => el.scrollBy(0, 200)")
                await asyncio.sleep(0.15)

            if not found:
                self.logger.error(f"❌ Despacho NO encontrado: {court_office}")
                return None

            # 5️⃣ Click final
            await option.first.click()
            self.logger.info(f"✅ Despacho seleccionado: {court_office}")

            await asyncio.sleep(1.5)

            return court_office

            

        except Exception as e:
            self.logger.exception(
                f"❌ Error seleccionando despacho judicial {court_office}: {e}"
            )
            return None
