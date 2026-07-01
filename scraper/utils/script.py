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
