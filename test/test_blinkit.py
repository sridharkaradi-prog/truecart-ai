from playwright.sync_api import Page


def test_blinkit_inspect(page: Page) -> None:
    page.goto(
        "https://blinkit.com/",
        wait_until="domcontentloaded",
        timeout=30_000,
    )

    page.wait_for_timeout(5_000)

    print("\nPAGE TITLE:", page.title())
    print("PAGE URL:", page.url)

    print("\nINPUTS:")
    inputs = page.locator("input")

    for i in range(inputs.count()):
        element = inputs.nth(i)

        print(
            f"[{i}] placeholder=",
            element.get_attribute("placeholder"),
            "| aria-label=",
            element.get_attribute("aria-label"),
            "| type=",
            element.get_attribute("type"),
        )

    print("\nBUTTONS:")
    buttons = page.locator("button")

    for i in range(min(buttons.count(), 20)):
        element = buttons.nth(i)

        print(
            f"[{i}] text=",
            element.inner_text()[:100],
            "| aria-label=",
            element.get_attribute("aria-label"),
        )

    print("\nBODY TEXT:")
    print(page.locator("body").inner_text()[:3000])