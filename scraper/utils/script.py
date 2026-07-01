scrolling_script = """
const numScrolls = -1
let scrollCount = 0

// scroll down and then wait for 0.5s
const scrollInterval = setInterval(() => {
    window.scrollTo(0, document.body.scrollHeight)
    scrollCount++

    if (scrollCount === numScrolls) {
    clearInterval(scrollInterval)
    }
}, 500)
"""
