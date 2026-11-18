import time
from playwright.sync_api import sync_playwright

def main():
    user_data_dir = "/home/hamilcar/Antigravity/playwright_user_data"
    with sync_playwright() as p:
        print("Launching browser. Please wait...")
        context = p.chromium.launch_persistent_context(user_data_dir, headless=False)
        
        print("Waiting to detect #Questao_Nome in any active page...")
        print("Please ensure you have opened the editor modal in the browser.")
        
        while True:
            try:
                for idx, page in enumerate(context.pages):
                    try:
                        url = page.url
                        exists = page.evaluate("() => document.getElementById('Questao_Nome') !== null")
                        if exists:
                            info = page.evaluate("""() => {
                                const el = document.getElementById('Questao_Nome');
                                const list = [];
                                let current = el;
                                while (current) {
                                    const style = window.getComputedStyle(current);
                                    list.push({
                                        tag: current.tagName,
                                        id: current.id,
                                        className: current.className,
                                        display: style.display,
                                        visibility: style.visibility,
                                        opacity: style.opacity,
                                        rect: current.getBoundingClientRect()
                                    });
                                    current = current.parentElement;
                                }
                                return list;
                            }""")
                            print(f"\\n=== [Tab {idx}] FOUND #Questao_Nome on {url} ===")
                            for p_idx, p_info in enumerate(info):
                                rect = p_info['rect']
                                print(f"[{p_idx}] Tag: {p_info['tag']}, ID: {p_info['id']}, Class: {p_info['className']}")
                                print(f"    Style -> Display: {p_info['display']}, Vis: {p_info['visibility']}, Opacity: {p_info['opacity']}")
                                print(f"    Rect  -> x={rect['x']:.1f}, y={rect['y']:.1f}, w={rect['width']:.1f}, h={rect['height']:.1f}")
                    except Exception as e:
                        # Print page errors if any
                        pass
            except Exception as e:
                print(f"Error checking pages: {e}")
            time.sleep(2)

if __name__ == "__main__":
    main()
