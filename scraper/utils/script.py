scrolling_script = """
const delay = ms => new Promise(resolve => setTimeout(resolve, ms));

(async () => {
    let lastHeight = 0;

    while (true) {
        window.scrollTo(0, document.body.scrollHeight);

        await delay(500);

        const newHeight = document.body.scrollHeight;

        if (newHeight === lastHeight) {
            break;
        }

        lastHeight = newHeight;
    }
})();
"""


text_message = """
() => {
    const div = document.createElement('div');
    div.style.cssText = 'position:fixed;top:0;left:0;width:100%;background:red;color:white;padding:20px;font-size:24px;text-align:center;z-index:9999;';
    div.textContent = 'test message';
    document.body.prepend(div);
}
"""