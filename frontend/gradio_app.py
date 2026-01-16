"""
Executive Analytics - Gradio Landing Page
Modern SaaS-style landing with embedded auth forms
"""
import os
import gradio as gr
import httpx

# API base URL
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
MAIN_APP_URL = os.getenv("MAIN_APP_URL", "http://localhost:7861")

# =============================================================================
# CUSTOM CSS
# =============================================================================

CUSTOM_CSS = """
/* Global Styles */
* {
    box-sizing: border-box;
}

.gradio-container {
    max-width: 100% !important;
    padding: 0 !important;
    margin: 0 !important;
}

/* Hero Section */
.hero-section {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 80px 20px;
    text-align: center;
    margin: -20px -20px 0 -20px;
}

.hero-title {
    font-size: 3rem;
    font-weight: 700;
    margin-bottom: 20px;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
}

.hero-subtitle {
    font-size: 1.4rem;
    opacity: 0.95;
    max-width: 700px;
    margin: 0 auto 40px auto;
    line-height: 1.6;
}

.hero-cta {
    display: inline-block;
    background: white;
    color: #667eea;
    padding: 15px 40px;
    border-radius: 30px;
    font-weight: 600;
    font-size: 1.1rem;
    text-decoration: none;
    transition: transform 0.3s, box-shadow 0.3s;
    margin: 10px;
}

.hero-cta:hover {
    transform: translateY(-3px);
    box-shadow: 0 10px 30px rgba(0,0,0,0.2);
}

.hero-cta-secondary {
    background: transparent;
    border: 2px solid white;
    color: white;
}

.hero-cta-secondary:hover {
    background: white;
    color: #667eea;
}

/* Section Styles */
.section {
    padding: 80px 20px;
    max-width: 1200px;
    margin: 0 auto;
}

.section-title {
    font-size: 2.2rem;
    font-weight: 700;
    text-align: center;
    margin-bottom: 15px;
    color: #333;
}

.section-subtitle {
    font-size: 1.1rem;
    text-align: center;
    color: #666;
    margin-bottom: 50px;
    max-width: 600px;
    margin-left: auto;
    margin-right: auto;
}

/* Feature Cards */
.features-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 30px;
    padding: 20px 0;
}

.feature-card {
    background: white;
    border-radius: 16px;
    padding: 35px 25px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.08);
    transition: transform 0.3s, box-shadow 0.3s;
    text-align: center;
}

.feature-card:hover {
    transform: translateY(-8px);
    box-shadow: 0 12px 40px rgba(0,0,0,0.15);
}

.feature-icon {
    font-size: 3rem;
    margin-bottom: 20px;
}

.feature-title {
    font-size: 1.3rem;
    font-weight: 600;
    margin-bottom: 12px;
    color: #333;
}

.feature-desc {
    color: #666;
    line-height: 1.6;
    font-size: 0.95rem;
}

/* Demo Section */
.demo-section {
    background: #f8f9fa;
    padding: 80px 20px;
    text-align: center;
}

.demo-placeholder {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 16px;
    padding: 60px;
    color: white;
    max-width: 800px;
    margin: 0 auto;
    box-shadow: 0 20px 60px rgba(102, 126, 234, 0.3);
}

.demo-placeholder h3 {
    font-size: 1.8rem;
    margin-bottom: 15px;
}

.demo-placeholder p {
    opacity: 0.9;
    font-size: 1.1rem;
}

/* Pricing Section */
.pricing-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 30px;
    max-width: 1000px;
    margin: 0 auto;
    padding: 20px;
}

.pricing-card {
    background: white;
    border-radius: 16px;
    padding: 40px 30px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.08);
    text-align: center;
    transition: transform 0.3s;
    position: relative;
}

.pricing-card:hover {
    transform: translateY(-5px);
}

.pricing-card.featured {
    border: 3px solid #667eea;
    transform: scale(1.05);
}

.pricing-card.featured:hover {
    transform: scale(1.08);
}

.pricing-badge {
    position: absolute;
    top: -12px;
    left: 50%;
    transform: translateX(-50%);
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 5px 20px;
    border-radius: 20px;
    font-size: 0.85rem;
    font-weight: 600;
}

.pricing-name {
    font-size: 1.5rem;
    font-weight: 700;
    color: #333;
    margin-bottom: 10px;
}

.pricing-price {
    font-size: 3rem;
    font-weight: 700;
    color: #667eea;
    margin-bottom: 5px;
}

.pricing-period {
    color: #888;
    margin-bottom: 25px;
}

.pricing-features {
    list-style: none;
    padding: 0;
    margin: 0 0 30px 0;
    text-align: left;
}

.pricing-features li {
    padding: 10px 0;
    border-bottom: 1px solid #eee;
    color: #555;
}

.pricing-features li:before {
    content: "\\2713";
    color: #667eea;
    font-weight: bold;
    margin-right: 10px;
}

.pricing-btn {
    display: inline-block;
    width: 100%;
    padding: 15px 30px;
    border-radius: 8px;
    font-weight: 600;
    text-decoration: none;
    transition: all 0.3s;
    cursor: pointer;
    border: none;
    font-size: 1rem;
}

.pricing-btn-primary {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
}

.pricing-btn-primary:hover {
    box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
}

.pricing-btn-secondary {
    background: #f0f0f0;
    color: #333;
}

.pricing-btn-secondary:hover {
    background: #e0e0e0;
}

.pricing-btn-disabled {
    background: #e0e0e0;
    color: #999;
    cursor: not-allowed;
}

/* Auth Section */
.auth-section {
    background: #f8f9fa;
    padding: 60px 20px;
}

.auth-container {
    max-width: 500px;
    margin: 0 auto;
}

/* Footer */
.footer {
    background: #1a1a2e;
    color: #aaa;
    padding: 60px 20px 30px;
    text-align: center;
}

.footer-brand {
    font-size: 1.5rem;
    font-weight: 700;
    color: white;
    margin-bottom: 15px;
}

.footer-links {
    display: flex;
    justify-content: center;
    gap: 30px;
    margin-bottom: 30px;
    flex-wrap: wrap;
}

.footer-links a {
    color: #aaa;
    text-decoration: none;
    transition: color 0.3s;
}

.footer-links a:hover {
    color: #667eea;
}

.footer-copy {
    font-size: 0.9rem;
    border-top: 1px solid #333;
    padding-top: 20px;
}

/* Responsive */
@media (max-width: 768px) {
    .hero-title {
        font-size: 2rem;
    }

    .hero-subtitle {
        font-size: 1.1rem;
    }

    .section-title {
        font-size: 1.8rem;
    }

    .features-grid {
        grid-template-columns: 1fr;
    }

    .pricing-grid {
        grid-template-columns: 1fr;
    }

    .pricing-card.featured {
        transform: none;
    }

    .pricing-card.featured:hover {
        transform: translateY(-5px);
    }

    .hero-cta {
        display: block;
        margin: 10px auto;
        max-width: 250px;
    }
}
"""

# =============================================================================
# HTML SECTIONS
# =============================================================================

def hero_section() -> str:
    """Hero section with main CTA"""
    return """
    <div class="hero-section">
        <h1 class="hero-title">Executive Analytics</h1>
        <p class="hero-subtitle">
            Transform your data questions into instant SQL insights.
            No coding required. Just ask in plain English.
        </p>
        <div>
            <a href="#auth-section" class="hero-cta">Get Started Free</a>
            <a href="#demo-section" class="hero-cta hero-cta-secondary">See Demo</a>
        </div>
    </div>
    """


def features_section() -> str:
    """Features grid with 4 benefit cards"""
    return """
    <div class="section">
        <h2 class="section-title">Why Choose Executive Analytics?</h2>
        <p class="section-subtitle">
            Powerful features designed for business users who want data insights without the complexity.
        </p>
        <div class="features-grid">
            <div class="feature-card">
                <div class="feature-icon">💬</div>
                <h3 class="feature-title">Natural Language Queries</h3>
                <p class="feature-desc">
                    Ask questions in plain English. Our AI understands your intent
                    and generates accurate SQL automatically.
                </p>
            </div>
            <div class="feature-card">
                <div class="feature-icon">⚡</div>
                <h3 class="feature-title">Instant Results</h3>
                <p class="feature-desc">
                    Get answers in seconds, not hours. No more waiting for
                    technical teams to run your reports.
                </p>
            </div>
            <div class="feature-card">
                <div class="feature-icon">🔒</div>
                <h3 class="feature-title">Secure & Private</h3>
                <p class="feature-desc">
                    Your data stays yours. Enterprise-grade security with
                    role-based access controls.
                </p>
            </div>
            <div class="feature-card">
                <div class="feature-icon">📊</div>
                <h3 class="feature-title">Visual Insights</h3>
                <p class="feature-desc">
                    Beautiful charts and graphs generated automatically.
                    Export to PDF, Excel, or share with your team.
                </p>
            </div>
        </div>
    </div>
    """


def demo_section() -> str:
    """Demo placeholder section"""
    return """
    <div class="demo-section" id="demo-section">
        <h2 class="section-title">See It In Action</h2>
        <p class="section-subtitle">
            Watch how easy it is to get insights from your data.
        </p>
        <div class="demo-placeholder">
            <h3>🎬 Demo Coming Soon</h3>
            <p>We're preparing an interactive demo to show you the magic in action.</p>
        </div>
    </div>
    """


def pricing_section() -> str:
    """Pricing tiers: Free, Pro, Enterprise"""
    return """
    <div class="section">
        <h2 class="section-title">Simple, Transparent Pricing</h2>
        <p class="section-subtitle">
            Start free, upgrade when you're ready.
        </p>
        <div class="pricing-grid">
            <div class="pricing-card">
                <h3 class="pricing-name">Free</h3>
                <div class="pricing-price">$0</div>
                <div class="pricing-period">forever</div>
                <ul class="pricing-features">
                    <li>50 queries per month</li>
                    <li>1 database connection</li>
                    <li>Basic visualizations</li>
                    <li>Community support</li>
                </ul>
                <a href="#auth-section" class="pricing-btn pricing-btn-primary">Get Started</a>
            </div>
            <div class="pricing-card featured">
                <span class="pricing-badge">Coming Soon</span>
                <h3 class="pricing-name">Pro</h3>
                <div class="pricing-price">$29</div>
                <div class="pricing-period">per month</div>
                <ul class="pricing-features">
                    <li>Unlimited queries</li>
                    <li>10 database connections</li>
                    <li>Advanced visualizations</li>
                    <li>Priority support</li>
                    <li>Export to PDF/Excel</li>
                </ul>
                <button class="pricing-btn pricing-btn-disabled" disabled>Coming Soon</button>
            </div>
            <div class="pricing-card">
                <h3 class="pricing-name">Enterprise</h3>
                <div class="pricing-price">Custom</div>
                <div class="pricing-period">contact us</div>
                <ul class="pricing-features">
                    <li>Everything in Pro</li>
                    <li>Unlimited connections</li>
                    <li>SSO integration</li>
                    <li>Dedicated support</li>
                    <li>Custom features</li>
                </ul>
                <a href="mailto:e.gzlzmesones@gmail.com" class="pricing-btn pricing-btn-secondary">Contact Us</a>
            </div>
        </div>
    </div>
    """


def footer_section() -> str:
    """Footer with links"""
    return """
    <div class="footer">
        <div class="footer-brand">Executive Analytics</div>
        <div class="footer-links">
            <a href="#features">Features</a>
            <a href="#demo-section">Demo</a>
            <a href="#pricing">Pricing</a>
            <a href="mailto:e.gzlzmesones@gmail.com">Contact</a>
        </div>
        <div class="footer-copy">
            &copy; 2024 Executive Analytics. All rights reserved.
        </div>
    </div>
    """


# =============================================================================
# AUTH FUNCTIONS
# =============================================================================

def register_user(email: str, password: str, confirm_password: str) -> str:
    """Register a new user via API"""
    if not email or not password:
        return "❌ Please fill in all fields"

    if password != confirm_password:
        return "❌ Passwords do not match"

    if len(password) < 8:
        return "❌ Password must be at least 8 characters"

    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.post(
                f"{API_BASE_URL}/api/auth/register",
                json={"email": email, "password": password}
            )

            if response.status_code == 201:
                return "✅ Registration successful! Check your email to verify your account."
            elif response.status_code == 400:
                data = response.json()
                return f"❌ {data.get('detail', 'Registration failed')}"
            else:
                return f"❌ Registration failed (status {response.status_code})"

    except httpx.ConnectError:
        return "❌ Cannot connect to API. Is the server running?"
    except Exception as e:
        return f"❌ Error: {str(e)}"


def login_user(email: str, password: str) -> str:
    """Login user via API and redirect to main app on success"""
    if not email or not password:
        return "❌ Please fill in all fields"

    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.post(
                f"{API_BASE_URL}/api/auth/login",
                json={"email": email, "password": password}
            )

            if response.status_code == 200:
                # Return JavaScript redirect to main app
                return f"""
                <div style="text-align: center; padding: 20px;">
                    <p style="color: #4ade80; font-size: 1.2rem;">✅ Login successful!</p>
                    <p>Redirecting to app...</p>
                    <script>
                        setTimeout(function() {{
                            window.location.href = '{MAIN_APP_URL}';
                        }}, 1500);
                    </script>
                </div>
                """
            elif response.status_code == 401:
                return "❌ Invalid email or password"
            elif response.status_code == 403:
                return "❌ Please verify your email first"
            elif response.status_code == 423:
                return "❌ Account locked. Try again later."
            else:
                return f"❌ Login failed (status {response.status_code})"

    except httpx.ConnectError:
        return "❌ Cannot connect to API. Is the server running?"
    except Exception as e:
        return f"❌ Error: {str(e)}"


# =============================================================================
# MAIN APP
# =============================================================================

def create_app() -> gr.Blocks:
    """Create the Gradio landing page app"""
    with gr.Blocks(title="Executive Analytics") as app:
        # Hero Section
        gr.HTML(hero_section())

        # Features Section
        gr.HTML(features_section())

        # Demo Section
        gr.HTML(demo_section())

        # Pricing Section
        gr.HTML(pricing_section())

        # Auth Section
        gr.HTML('<div id="auth-section"></div>')
        gr.HTML('<div class="auth-section"><div class="auth-container">')
        gr.Markdown("## Get Started")

        with gr.Tabs():
            with gr.TabItem("Register"):
                reg_email = gr.Textbox(label="Email", placeholder="you@example.com")
                reg_password = gr.Textbox(label="Password", type="password", placeholder="Min 8 characters")
                reg_confirm = gr.Textbox(label="Confirm Password", type="password", placeholder="Repeat password")
                reg_btn = gr.Button("Create Account", variant="primary")
                reg_result = gr.Markdown()

                reg_btn.click(
                    fn=register_user,
                    inputs=[reg_email, reg_password, reg_confirm],
                    outputs=reg_result
                )

            with gr.TabItem("Login"):
                login_email = gr.Textbox(label="Email", placeholder="you@example.com")
                login_password = gr.Textbox(label="Password", type="password", placeholder="Your password")
                login_btn = gr.Button("Sign In", variant="primary")
                login_result = gr.Markdown()

                login_btn.click(
                    fn=login_user,
                    inputs=[login_email, login_password],
                    outputs=login_result
                )

        gr.HTML('</div></div>')

        # Footer
        gr.HTML(footer_section())

    return app


# =============================================================================
# STANDALONE EXECUTION
# =============================================================================

if __name__ == "__main__":
    app = create_app()
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        css=CUSTOM_CSS,
        theme=gr.themes.Soft()
    )
