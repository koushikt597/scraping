from camoufox.sync_api import Camoufox

with Camoufox() as browser:
    page = browser.new_page()
    page.goto("https://google.com")
    page.goto("https://cekbpom.pom.go.id/produk-obat")
    page.wait_for_timeout(1000)
    