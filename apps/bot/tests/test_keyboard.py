from bot.main import open_app_keyboard


def test_keyboard_opens_webapp():
    markup = open_app_keyboard("https://example.com")
    button = markup.inline_keyboard[0][0]
    assert button.web_app.url == "https://example.com"
