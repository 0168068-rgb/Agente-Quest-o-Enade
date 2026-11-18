import time
from playwright.sync_api import sync_playwright
from automate_questions_v3 import get_active_page

def main():
    user_data_dir = "/home/hamilcar/Antigravity/playwright_user_data"
    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(user_data_dir, headless=False)
        page = get_active_page(context)
        if not page:
            print("No active page found.")
            return
            
        print(f"URL: {page.url}")
        
        # We assume the editor modal is open
        page.wait_for_timeout(2000)
        
        # Let's try to click "Salvar questão" and watch the DOM for error alerts
        print("Clicking 'Salvar questão'...")
        page.evaluate("""() => {
            const btn = document.getElementById('submitFormQuestao');
            if (btn) btn.click();
        }""")
        
        # Wait 5 seconds
        time.sleep(5)
        
        # Capture screenshot and check for error messages
        page.screenshot(path="/home/hamilcar/Antigravity/save_attempt.png")
        print("Screenshot saved to /home/hamilcar/Antigravity/save_attempt.png")
        
        errors = page.evaluate("""() => {
            const errs = [];
            // Check for sweet alert
            const swal = document.querySelector('.sweet-alert, .swal2-container');
            if (swal) errs.push("Swal text: " + swal.innerText);
            
            // Check for standard validation messages
            const valErrs = Array.from(document.querySelectorAll('.field-validation-error, .text-danger, .error-message, .invalid-feedback'));
            valErrs.forEach(el => {
                if (el.offsetWidth > 0) errs.push("Validation error: " + el.innerText);
            });
            
            // Check bootstrap alert
            const alerts = Array.from(document.querySelectorAll('.alert-danger, .alert-warning'));
            alerts.forEach(el => {
                if (el.offsetWidth > 0) errs.push("Alert error: " + el.innerText);
            });
            
            return errs;
        }""")
        
        print("Errors found on screen:")
        for err in errors:
            print(f" - {err}")
            
        context.close()

if __name__ == "__main__":
    main()
