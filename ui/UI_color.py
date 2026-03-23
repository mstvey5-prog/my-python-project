# UI_colors.py

DARK_THEME = {
    "name": "dark",
    "label": "🌙 Тёмная",
    "bg_dark":    "#1a1a2e",
    "bg_medium":  "#16213e",
    "bg_light":   "#0f3460",
    "bg_card":    "#1f2940",
    "bg_input":   "#2a3a5c",
    "accent":         "#e94560",
    "accent_hover":   "#ff6b81",
    "success":        "#00b894",
    "success_hover":  "#00d2a0",
    "warning":        "#fdcb6e",
    "danger":         "#d63031",
    "danger_hover":   "#e17055",
    "highlight":      "#6c5ce7",
    "highlight_hover":"#a29bfe",
    "text_primary":   "#ffffff",
    "text_secondary": "#a0aec0",
    "text_accent":    "#74b9ff",
    "text_muted":     "#636e72",
    "border":     "#2d3748",
    "rest_day":   "#2d3436",
    "train_day":  "#0f3460",
    "sunday":     "#2d1f3d",
}

LIGHT_THEME = {
    "name": "light",
    "label": "☀️ Светлая",
    "bg_dark":    "#f0f4f8",
    "bg_medium":  "#dce6f0",
    "bg_light":   "#b0c4de",
    "bg_card":    "#ffffff",
    "bg_input":   "#eaf0f8",
    "accent":         "#e53e3e",
    "accent_hover":   "#fc8181",
    "success":        "#38a169",
    "success_hover":  "#48bb78",
    "warning":        "#d69e2e",
    "danger":         "#c53030",
    "danger_hover":   "#e53e3e",
    "highlight":      "#553c9a",
    "highlight_hover":"#805ad5",
    "text_primary":   "#1a202c",
    "text_secondary": "#4a5568",
    "text_accent":    "#2b6cb0",
    "text_muted":     "#a0aec0",
    "border":     "#cbd5e0",
    "rest_day":   "#e2e8f0",
    "train_day":  "#bee3f8",
    "sunday":     "#e9d8fd",
}

THEMES = {"dark": DARK_THEME, "light": LIGHT_THEME}

def get_theme(name: str) -> dict:
    return THEMES.get(name, DARK_THEME)