"""Noode Desktop Application - Modern UI/UX

A beautiful, intuitive GTK3 interface designed for both beginners and pros.
Clean, modern aesthetic with smooth animations and thoughtful UX.

Design Philosophy:
- Friendly, approachable colors (not too dark/intimidating)
- Large touch targets and clear typography
- Progressive disclosure (simple for beginners, powerful for pros)
- Smooth micro-interactions
- Card-based layouts with soft shadows
"""

import sys
import asyncio
import threading
from pathlib import Path
from typing import Any, Callable, Optional
from datetime import datetime

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Pango', '1.0')
from gi.repository import Gtk, Gdk, GLib, Pango, GObject

import structlog

logger = structlog.get_logger()

# ============================================
# MODERN COLOR PALETTE - Friendly & Fresh
# ============================================
COLORS = {
    # Primary - Soft indigo/violet (modern, friendly)
    "primary": "#6366F1",
    "primary_light": "#818CF8",
    "primary_dark": "#4F46E5",
    "primary_bg": "#EEF2FF",
    
    # Secondary - Teal (fresh, trustworthy)
    "secondary": "#14B8A6",
    "secondary_light": "#5EEAD4",
    "secondary_dark": "#0D9488",
    
    # Accent - Coral/Orange (warm, energetic)
    "accent": "#F97316",
    "accent_light": "#FB923C",
    
    # Backgrounds
    "bg_main": "#FAFBFC",  # Very light gray
    "bg_card": "#FFFFFF",   # Pure white cards
    "bg_sidebar": "#F1F5F9", # Light blue-gray
    "bg_hover": "#F8FAFC",
    "bg_active": "#EFF6FF",
    
    # Text
    "text_primary": "#1E293B",   # Dark slate
    "text_secondary": "#64748B", # Medium gray
    "text_muted": "#94A3B8",     # Light gray
    "text_inverse": "#FFFFFF",
    
    # Status
    "success": "#22C55E",
    "success_bg": "#DCFCE7",
    "warning": "#F59E0B",
    "warning_bg": "#FEF3C7",
    "error": "#EF4444",
    "error_bg": "#FEE2E2",
    "info": "#3B82F6",
    "info_bg": "#DBEAFE",
    
    # Borders & Dividers
    "border": "#E2E8F0",
    "border_light": "#F1F5F9",
    "shadow": "rgba(0, 0, 0, 0.08)",
}

# ============================================
# MODERN CSS STYLES
# ============================================
CSS = f"""
/* ============================================
   GLOBAL RESET & BASE
   ============================================ */
* {{
    font-family: "Inter", "SF Pro Display", "Segoe UI", "Cantarell", sans-serif;
    -gtk-icon-style: symbolic;
}}

window {{
    background-color: {COLORS["bg_main"]};
}}

/* ============================================
   GLASSMORPHISM HEADER
   ============================================ */
.glass-header {{
    background: linear-gradient(135deg, 
        rgba(99, 102, 241, 0.95) 0%, 
        rgba(79, 70, 229, 0.95) 100%);
    padding: 20px 32px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}}

.glass-header-title {{
    font-size: 28px;
    font-weight: 800;
    color: {COLORS["text_inverse"]};
    letter-spacing: -0.5px;
}}

.glass-header-subtitle {{
    font-size: 14px;
    color: rgba(255, 255, 255, 0.8);
    margin-top: 4px;
}}

/* ============================================
   MODERN SIDEBAR - Clean & Minimal
   ============================================ */
.sidebar {{
    background-color: {COLORS["bg_sidebar"]};
    padding: 16px 12px;
    border-right: 1px solid {COLORS["border"]};
}}

.sidebar-logo {{
    font-size: 24px;
    font-weight: 800;
    color: {COLORS["primary"]};
    padding: 16px;
    margin-bottom: 8px;
}}

.sidebar-section {{
    font-size: 11px;
    font-weight: 600;
    /* Note: text-transform not supported in GTK3 CSS */
    letter-spacing: 0.5px;
    color: {COLORS["text_muted"]};
    padding: 16px 16px 8px 16px;
}}

.sidebar-item {{
    padding: 12px 16px;
    border-radius: 10px;
    margin: 2px 8px;
    color: {COLORS["text_secondary"]};
    background: transparent;
    border: none;
    font-size: 14px;
    font-weight: 500;
    transition: all 150ms ease;
}}

.sidebar-item:hover {{
    background-color: {COLORS["bg_hover"]};
    color: {COLORS["text_primary"]};
}}

.sidebar-item-active {{
    background-color: {COLORS["bg_active"]};
    color: {COLORS["primary"]};
    font-weight: 600;
}}

.sidebar-item-active:hover {{
    background-color: {COLORS["bg_active"]};
}}

/* ============================================
   MODERN CARDS - Soft & Inviting
   ============================================ */
.card {{
    background-color: {COLORS["bg_card"]};
    border-radius: 16px;
    padding: 24px;
    margin: 8px 0;
    border: 1px solid {COLORS["border"]};
    box-shadow: 0 1px 3px {COLORS["shadow"]};
    transition: all 200ms ease;
}}

.card:hover {{
    box-shadow: 0 4px 12px {COLORS["shadow"]};
}}

.card-title {{
    font-size: 18px;
    font-weight: 700;
    color: {COLORS["text_primary"]};
    margin-bottom: 4px;
}}

.card-subtitle {{
    font-size: 13px;
    color: {COLORS["text_muted"]};
}}

/* ============================================
   PRIMARY BUTTON - Bold & Inviting
   ============================================ */
.button-primary {{
    background: linear-gradient(135deg, {COLORS["primary"]} 0%, {COLORS["primary_dark"]} 100%);
    color: {COLORS["text_inverse"]};
    padding: 12px 24px;
    border-radius: 10px;
    font-size: 14px;
    font-weight: 600;
    border: none;
    box-shadow: 0 2px 8px rgba(99, 102, 241, 0.3);
    transition: all 150ms ease;
}}

.button-primary:hover {{
    background: linear-gradient(135deg, {COLORS["primary_light"]} 0%, {COLORS["primary"]} 100%);
    box-shadow: 0 4px 12px rgba(99, 102, 241, 0.4);
}}

.button-primary:active {{
    box-shadow: 0 1px 4px rgba(99, 102, 241, 0.3);
}}

/* ============================================
   SECONDARY BUTTON - Subtle
   ============================================ */
.button-secondary {{
    background-color: {COLORS["bg_card"]};
    color: {COLORS["text_primary"]};
    padding: 12px 24px;
    border-radius: 10px;
    font-size: 14px;
    font-weight: 600;
    border: 1px solid {COLORS["border"]};
    transition: all 150ms ease;
}}

.button-secondary:hover {{
    background-color: {COLORS["bg_hover"]};
    border-color: {COLORS["primary"]};
}}

/* ============================================
   GHOST BUTTON - Minimal
   ============================================ */
.button-ghost {{
    background-color: transparent;
    color: {COLORS["primary"]};
    padding: 8px 16px;
    border-radius: 8px;
    font-size: 14px;
    font-weight: 500;
    border: none;
}}

.button-ghost:hover {{
    background-color: {COLORS["primary_bg"]};
}}

/* ============================================
   INPUT FIELDS - Clean & Modern
   ============================================ */
.input-field {{
    background-color: {COLORS["bg_card"]};
    border: 2px solid {COLORS["border"]};
    border-radius: 10px;
    padding: 12px 16px;
    font-size: 14px;
    color: {COLORS["text_primary"]};
    transition: all 150ms ease;
}}

.input-field:focus {{
    border-color: {COLORS["primary"]};
    box-shadow: 0 0 0 3px {COLORS["primary_bg"]};
}}

/* ============================================
   STATUS BADGES - Clear & Colorful
   ============================================ */
.badge {{
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
}}

.badge-success {{
    background-color: {COLORS["success_bg"]};
    color: {COLORS["success"]};
}}

.badge-warning {{
    background-color: {COLORS["warning_bg"]};
    color: {COLORS["warning"]};
}}

.badge-error {{
    background-color: {COLORS["error_bg"]};
    color: {COLORS["error"]};
}}

.badge-info {{
    background-color: {COLORS["info_bg"]};
    color: {COLORS["info"]};
}}

/* ============================================
   CONTENT AREAS
   ============================================ */
.content-area {{
    background-color: {COLORS["bg_main"]};
    padding: 32px;
}}

.page-title {{
    font-size: 32px;
    font-weight: 800;
    color: {COLORS["text_primary"]};
    margin-bottom: 8px;
    letter-spacing: -0.5px;
}}

.page-subtitle {{
    font-size: 16px;
    color: {COLORS["text_secondary"]};
    margin-bottom: 32px;
}}

/* ============================================
   QUICK ACTIONS GRID
   ============================================ */
.quick-action {{
    background-color: {COLORS["bg_card"]};
    border-radius: 16px;
    padding: 24px;
    border: 2px solid transparent;
    transition: all 200ms ease;
}}

.quick-action:hover {{
    border-color: {COLORS["primary"]};
    box-shadow: 0 4px 16px {COLORS["shadow"]};
}}

.quick-action-icon {{
    font-size: 32px;
    margin-bottom: 12px;
}}

.quick-action-title {{
    font-size: 16px;
    font-weight: 700;
    color: {COLORS["text_primary"]};
    margin-bottom: 4px;
}}

.quick-action-desc {{
    font-size: 13px;
    color: {COLORS["text_muted"]};
}}

/* ============================================
   CHAT/CONVERSATION BUBBLES
   ============================================ */
.chat-bubble {{
    padding: 16px 20px;
    border-radius: 18px;
    font-size: 14px;
}}

.chat-bubble-user {{
    background-color: {COLORS["primary"]};
    color: {COLORS["text_inverse"]};
    border-bottom-right-radius: 4px;
}}

.chat-bubble-ai {{
    background-color: {COLORS["bg_card"]};
    color: {COLORS["text_primary"]};
    border: 1px solid {COLORS["border"]};
    border-bottom-left-radius: 4px;
}}

/* ============================================
   AGENT AVATARS
   ============================================ */
.agent-avatar {{
    border-radius: 50%;
    font-weight: 700;
    font-size: 18px;
}}

.avatar-research {{
    background: linear-gradient(135deg, #8B5CF6 0%, #7C3AED 100%);
    color: white;
}}

.avatar-frontend {{
    background: linear-gradient(135deg, #06B6D4 0%, #0891B2 100%);
    color: white;
}}

.avatar-backend {{
    background: linear-gradient(135deg, #10B981 0%, #059669 100%);
    color: white;
}}

.avatar-security {{
    background: linear-gradient(135deg, #EF4444 0%, #DC2626 100%);
    color: white;
}}

.avatar-orchestrator {{
    background: linear-gradient(135deg, #F59E0B 0%, #D97706 100%);
    color: white;
}}

/* ============================================
   TOOLTIP - Modern
   ============================================ */
tooltip {{
    background-color: {COLORS["text_primary"]};
    color: {COLORS["text_inverse"]};
    padding: 8px 12px;
    border-radius: 8px;
    font-size: 12px;
    font-weight: 500;
}}

/* ============================================
   SCROLLBAR - Minimal
   ============================================ */
scrollbar slider {{
    background-color: {COLORS["border"]};
    border-radius: 8px;
}}

scrollbar slider:hover {{
    background-color: {COLORS["text_muted"]};
}}
"""


class AnimatedWidget:
    """Mixin for widgets with smooth animations."""
    
    def animate_property(self, widget: Gtk.Widget, property_name: str, 
                        start_value: float, end_value: float, 
                        duration_ms: int = 200) -> None:
        """Animate a widget property smoothly."""
        import time
        
        start_time = time.time()
        duration_sec = duration_ms / 1000.0
        
        def update_animation():
            elapsed = time.time() - start_time
            progress = min(elapsed / duration_sec, 1.0)
            
            # Easing function (ease-out-cubic)
            eased = 1 - pow(1 - progress, 3)
            
            current = start_value + (end_value - start_value) * eased
            
            if property_name == "opacity":
                widget.set_opacity(current)
            
            if progress < 1.0:
                GLib.timeout_add(16, update_animation)  # ~60fps
            
            return False
        
        GLib.timeout_add(16, update_animation)


class ModernButton(Gtk.Button):
    """Modern styled button with icon support."""
    
    def __init__(self, label: str = "", icon: str = "", 
                 style: str = "primary", **kwargs):
        super().__init__(**kwargs)
        
        self.style = style
        
        # Create container
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        box.set_halign(Gtk.Align.CENTER)
        
        if icon:
            icon_widget = Gtk.Image.new_from_icon_name(
                icon, Gtk.IconSize.BUTTON
            )
            box.pack_start(icon_widget, False, False, 0)
        
        if label:
            label_widget = Gtk.Label(label=label)
            box.pack_start(label_widget, False, False, 0)
        
        self.add(box)
        
        # Apply style class
        style_map = {
            "primary": "button-primary",
            "secondary": "button-secondary",
            "ghost": "button-ghost",
        }
        self.get_style_context().add_class(style_map.get(style, "button-primary"))
        
        # Cursor pointer on hover
        self.connect("enter-notify-event", self._on_enter)
        self.connect("leave-notify-event", self._on_leave)
    
    def _on_enter(self, widget, event):
        display = Gdk.Display.get_default()
        cursor = Gdk.Cursor.new_from_name(display, "pointer")
        self.get_window().set_cursor(cursor)
    
    def _on_leave(self, widget, event):
        self.get_window().set_cursor(None)


class ModernCard(Gtk.Box):
    """Modern card widget with hover effects."""
    
    def __init__(self, title: str = "", subtitle: str = "", 
                 icon: str = "", **kwargs):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=0, **kwargs)
        
        self.get_style_context().add_class("card")
        self.set_margin_bottom(8)
        
        # Header
        header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        
        if icon:
            icon_img = Gtk.Image.new_from_icon_name(icon, Gtk.IconSize.DND)
            icon_img.set_pixel_size(32)
            header.pack_start(icon_img, False, False, 0)
        
        text_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        
        if title:
            title_label = Gtk.Label(label=title)
            title_label.get_style_context().add_class("card-title")
            title_label.set_halign(Gtk.Align.START)
            text_box.pack_start(title_label, False, False, 0)
        
        if subtitle:
            subtitle_label = Gtk.Label(label=subtitle)
            subtitle_label.get_style_context().add_class("card-subtitle")
            subtitle_label.set_halign(Gtk.Align.START)
            text_box.pack_start(subtitle_label, False, False, 0)
        
        header.pack_start(text_box, True, True, 0)
        
        self.pack_start(header, False, False, 0)
        
        # Content area
        self.content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        self.content.set_margin_top(16)
        self.pack_start(self.content, True, True, 0)


class QuickAction(Gtk.Button):
    """Quick action tile with icon and description."""
    
    def __init__(self, title: str, description: str, icon: str,
                 callback: Optional[Callable] = None):
        super().__init__()
        
        self.get_style_context().add_class("quick-action")
        self.set_size_request(200, 140)
        
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        box.set_halign(Gtk.Align.CENTER)
        box.set_valign(Gtk.Align.CENTER)
        
        # Icon
        icon_label = Gtk.Label(label=icon)
        icon_label.get_style_context().add_class("quick-action-icon")
        box.pack_start(icon_label, False, False, 0)
        
        # Title
        title_label = Gtk.Label(label=title)
        title_label.get_style_context().add_class("quick-action-title")
        box.pack_start(title_label, False, False, 0)
        
        # Description
        desc_label = Gtk.Label(label=description)
        desc_label.get_style_context().add_class("quick-action-desc")
        box.pack_start(desc_label, False, False, 0)
        
        self.add(box)
        
        if callback:
            self.connect("clicked", callback)


class AgentAvatar(Gtk.Box):
    """Circular avatar for agents with initials."""
    
    def __init__(self, name: str, agent_type: str = "orchestrator"):
        super().__init__()
        
        self.get_style_context().add_class(f"agent-avatar avatar-{agent_type}")
        self.set_size_request(48, 48)
        
        # Get initials
        initials = "".join([n[0].upper() for n in name.split()[:2]])
        
        label = Gtk.Label(label=initials)
        label.set_halign(Gtk.Align.CENTER)
        label.set_valign(Gtk.Align.CENTER)
        
        self.add(label)


class ModernEntry(Gtk.Box):
    """Modern input field with label and icon."""
    
    def __init__(self, placeholder: str = "", label: str = "",
                 icon: str = "", password: bool = False):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        
        if label:
            lbl = Gtk.Label()
            lbl.set_markup(f'<span font_weight="600" color="{COLORS["text_primary"]}">{label}</span>')
            lbl.set_halign(Gtk.Align.START)
            self.pack_start(lbl, False, False, 0)
        
        # Input container
        container = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        container.get_style_context().add_class("input-field")
        
        if icon:
            icon_img = Gtk.Image.new_from_icon_name(icon, Gtk.IconSize.BUTTON)
            container.pack_start(icon_img, False, False, 0)
        
        self.entry = Gtk.Entry()
        self.entry.set_placeholder_text(placeholder)
        self.entry.set_has_frame(False)
        self.entry.set_hexpand(True)
        
        if password:
            self.entry.set_visibility(False)
        
        container.pack_start(self.entry, True, True, 0)
        self.pack_start(container, False, False, 0)
    
    def get_text(self) -> str:
        return self.entry.get_text()
    
    def set_text(self, text: str):
        self.entry.set_text(text)
    
    def connect_changed(self, callback):
        self.entry.connect("changed", callback)


class StatusBadge(Gtk.Label):
    """Colored status badge."""
    
    def __init__(self, text: str, status: str = "info"):
        super().__init__(label=text)
        
        self.get_style_context().add_class(f"badge badge-{status}")
        self.set_halign(Gtk.Align.CENTER)
        self.set_valign(Gtk.Align.CENTER)


class NoodeWindow(Gtk.ApplicationWindow):
    """Main application window with modern UI."""
    
    def __init__(self, application: Gtk.Application):
        super().__init__(application=application)
        
        self.set_default_size(1400, 900)
        self.set_title("Noode - AI Development Platform")
        
        # Apply CSS
        self._apply_css()
        
        # Main layout
        self.main_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.add(self.main_box)
        
        # Build UI
        self._build_sidebar()
        self._build_content()
        
        # Show welcome screen
        self._show_welcome_screen()
    
    def _apply_css(self):
        """Apply CSS styles."""
        provider = Gtk.CssProvider()
        provider.load_from_data(CSS.encode())
        
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )
    
    def _build_sidebar(self):
        """Build modern sidebar."""
        sidebar = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        sidebar.get_style_context().add_class("sidebar")
        sidebar.set_size_request(260, -1)
        
        # Logo
        logo = Gtk.Label(label="Noode")
        logo.get_style_context().add_class("sidebar-logo")
        sidebar.pack_start(logo, False, False, 0)
        
        # Main section
        section_main = Gtk.Label(label="Hauptmenü")
        section_main.get_style_context().add_class("sidebar-section")
        sidebar.pack_start(section_main, False, False, 0)
        
        self.nav_buttons = {}
        
        nav_items = [
            ("🏠", "Dashboard", "dashboard"),
            ("💬", "Neues Projekt", "new_project"),
            ("📁", "Meine Projekte", "projects"),
        ]
        
        for icon, label, page_id in nav_items:
            btn = Gtk.Button(label=f"  {icon}  {label}")
            btn.get_style_context().add_class("sidebar-item")
            btn.set_relief(Gtk.ReliefStyle.NONE)
            btn.connect("clicked", self._on_nav_clicked, page_id)
            sidebar.pack_start(btn, False, False, 0)
            self.nav_buttons[page_id] = btn
        
        # Separator
        sidebar.pack_start(Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL), 
                          False, False, 16)
        
        # Tools section
        section_tools = Gtk.Label(label="Werkzeuge")
        section_tools.get_style_context().add_class("sidebar-section")
        sidebar.pack_start(section_tools, False, False, 0)
        
        tool_items = [
            ("🔍", "Research", "research"),
            ("🎨", "Design", "design"),
            ("⚡", "Code Review", "review"),
            ("🔒", "Security", "security"),
        ]
        
        for icon, label, page_id in tool_items:
            btn = Gtk.Button(label=f"  {icon}  {label}")
            btn.get_style_context().add_class("sidebar-item")
            btn.set_relief(Gtk.ReliefStyle.NONE)
            btn.connect("clicked", self._on_nav_clicked, page_id)
            sidebar.pack_start(btn, False, False, 0)
            self.nav_buttons[page_id] = btn
        
        # Spacer
        sidebar.pack_start(Gtk.Box(), True, True, 0)
        
        # Settings at bottom
        btn_settings = Gtk.Button(label="  ⚙️  Einstellungen")
        btn_settings.get_style_context().add_class("sidebar-item")
        btn_settings.set_relief(Gtk.ReliefStyle.NONE)
        btn_settings.connect("clicked", self._on_nav_clicked, "settings")
        sidebar.pack_start(btn_settings, False, False, 0)
        self.nav_buttons["settings"] = btn_settings
        
        self.main_box.pack_start(sidebar, False, False, 0)
    
    def _build_content(self):
        """Build main content area."""
        self.content_stack = Gtk.Stack()
        self.content_stack.set_transition_type(
            Gtk.StackTransitionType.SLIDE_LEFT_RIGHT
        )
        self.content_stack.set_transition_duration(300)
        
        self.main_box.pack_start(self.content_stack, True, True, 0)
    
    def _on_nav_clicked(self, button, page_id: str):
        """Handle navigation click."""
        # Update active state
        for bid, btn in self.nav_buttons.items():
            if bid == page_id:
                btn.get_style_context().add_class("sidebar-item-active")
            else:
                btn.get_style_context().remove_class("sidebar-item-active")
        
        # Show page
        if page_id == "dashboard":
            self._show_welcome_screen()
        elif page_id == "new_project":
            self._show_new_project_screen()
        elif page_id == "projects":
            self._show_projects_screen()
        else:
            # TODO: Implement other screens
            self._show_placeholder_screen(page_id)
    
    def _show_welcome_screen(self):
        """Show beautiful welcome/dashboard screen."""
        if self.content_stack.get_child_by_name("welcome"):
            self.content_stack.set_visible_child_name("welcome")
            return
        
        page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        page.get_style_context().add_class("content-area")
        
        # Header with glass effect
        header = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        header.get_style_context().add_class("glass-header")
        
        title = Gtk.Label(label="Willkommen bei Noode")
        title.get_style_context().add_class("glass-header-title")
        header.pack_start(title, False, False, 0)
        
        subtitle = Gtk.Label(label="Was möchtest du heute entwickeln?")
        subtitle.get_style_context().add_class("glass-header-subtitle")
        header.pack_start(subtitle, False, False, 0)
        
        page.pack_start(header, False, False, 0)
        
        # Scrollable content
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        
        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=24)
        content.set_margin_top(32)
        content.set_margin_start(32)
        content.set_margin_end(32)
        content.set_margin_bottom(32)
        
        # Quick actions grid
        actions_label = Gtk.Label()
        actions_label.set_markup(
            f'<span font_size="large" font_weight="bold" color="{COLORS["text_primary"]}">Schnellstart</span>'
        )
        actions_label.set_halign(Gtk.Align.START)
        content.pack_start(actions_label, False, False, 0)
        
        actions_grid = Gtk.FlowBox()
        actions_grid.set_selection_mode(Gtk.SelectionMode.NONE)
        actions_grid.set_column_spacing(16)
        actions_grid.set_row_spacing(16)
        actions_grid.set_homogeneous(True)
        actions_grid.set_max_children_per_line(3)
        
        actions = [
            ("🚀", "Web App", "Webanwendung erstellen", self._on_webapp_clicked),
            ("📱", "Mobile App", "Mobile Anwendung", self._on_mobile_clicked),
            ("🔌", "API", "REST API erstellen", self._on_api_clicked),
            ("🤖", "Chatbot", "KI-Assistent bauen", self._on_chatbot_clicked),
            ("📊", "Dashboard", "Daten-Dashboard", self._on_dashboard_clicked),
            ("🎮", "Spiel", "Browsergame erstellen", self._on_game_clicked),
        ]
        
        for icon, title, desc, callback in actions:
            action = QuickAction(title, desc, icon, callback)
            actions_grid.add(action)
        
        content.pack_start(actions_grid, False, False, 0)
        
        # Recent projects section
        content.pack_start(Gtk.Separator(), False, False, 16)
        
        recent_label = Gtk.Label()
        recent_label.set_markup(
            f'<span font_size="large" font_weight="bold" color="{COLORS["text_primary"]}">Letzte Projekte</span>'
        )
        recent_label.set_halign(Gtk.Align.START)
        content.pack_start(recent_label, False, False, 0)
        
        # Example project cards
        projects_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        
        for i in range(3):
            card = ModernCard(
                title=f"Projekt {i+1}",
                subtitle="Zuletzt bearbeitet: Heute",
                icon="folder-symbolic"
            )
            
            # Add status badge
            status_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
            status_box.set_halign(Gtk.Align.END)
            
            statuses = [("Aktiv", "success"), ("In Entwicklung", "info"), ("Review", "warning")]
            text, status = statuses[i]
            badge = StatusBadge(text, status)
            status_box.pack_start(badge, False, False, 0)
            
            card.content.pack_start(status_box, False, False, 0)
            projects_box.pack_start(card, False, False, 0)
        
        content.pack_start(projects_box, False, False, 0)
        
        scroll.add(content)
        page.pack_start(scroll, True, True, 0)
        
        self.content_stack.add_named(page, "welcome")
        self.content_stack.set_visible_child_name("welcome")
    
    def _show_new_project_screen(self):
        """Show new project creation screen."""
        if self.content_stack.get_child_by_name("new_project"):
            self.content_stack.set_visible_child_name("new_project")
            return
        
        page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        page.get_style_context().add_class("content-area")
        
        # Header
        header_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        header_box.set_margin_bottom(32)
        
        title = Gtk.Label(label="Neues Projekt erstellen")
        title.get_style_context().add_class("page-title")
        title.set_halign(Gtk.Align.START)
        header_box.pack_start(title, False, False, 0)
        
        subtitle = Gtk.Label(
            label="Beschreibe dein Projekt in eigenen Worten. "
                  "Unsere AI-Agents kümmern sich um den Rest."
        )
        subtitle.get_style_context().add_class("page-subtitle")
        subtitle.set_halign(Gtk.Align.START)
        header_box.pack_start(subtitle, False, False, 0)
        
        page.pack_start(header_box, False, False, 0)
        
        # Scrollable content
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        
        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=24)
        content.set_margin_start(32)
        content.set_margin_end(32)
        content.set_margin_bottom(32)
        
        # Project name input
        name_input = ModernEntry(
            placeholder="z.B. Meine Webapp",
            label="Projektname",
            icon="text-x-generic-symbolic"
        )
        content.pack_start(name_input, False, False, 0)
        
        # Description text area
        desc_label = Gtk.Label()
        desc_label.set_markup(
            f'<span font_weight="600" color="{COLORS["text_primary"]}">Beschreibung</span>'
        )
        desc_label.set_halign(Gtk.Align.START)
        content.pack_start(desc_label, False, False, 0)
        
        desc_scroll = Gtk.ScrolledWindow()
        desc_scroll.set_size_request(-1, 150)
        
        desc_view = Gtk.TextView()
        desc_view.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        desc_view.get_buffer().set_text(
            "Ich möchte eine Webanwendung die..."
        )
        desc_view.get_style_context().add_class("input-field")
        
        desc_scroll.add(desc_view)
        content.pack_start(desc_scroll, False, False, 0)
        
        # Template selection
        template_label = Gtk.Label()
        template_label.set_markup(
            f'<span font_weight="600" color="{COLORS["text_primary"]}">Vorlage</span>'
        )
        template_label.set_halign(Gtk.Align.START)
        template_label.set_margin_top(16)
        content.pack_start(template_label, False, False, 0)
        
        templates_grid = Gtk.FlowBox()
        templates_grid.set_selection_mode(Gtk.SelectionMode.SINGLE)
        templates_grid.set_column_spacing(12)
        templates_grid.set_row_spacing(12)
        templates_grid.set_homogeneous(True)
        templates_grid.set_max_children_per_line(3)
        
        templates = [
            ("🌐", "Web App", "Fullstack Webanwendung"),
            ("📱", "Mobile", "React Native / PWA"),
            ("🔌", "API", "REST API Backend"),
            ("🤖", "Chatbot", "KI-Assistent"),
            ("📊", "Dashboard", "Analytics Dashboard"),
            ("🎮", "Spiel", "Browsergame"),
        ]
        
        for icon, title, desc in templates:
            card = ModernCard(title=title, subtitle=desc, icon="applications-other")
            templates_grid.add(card)
        
        content.pack_start(templates_grid, False, False, 0)
        
        # Action buttons
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        button_box.set_halign(Gtk.Align.END)
        button_box.set_margin_top(32)
        
        cancel_btn = ModernButton("Abbrechen", style="secondary")
        cancel_btn.connect("clicked", lambda x: self._show_welcome_screen())
        button_box.pack_start(cancel_btn, False, False, 0)
        
        create_btn = ModernButton("Projekt erstellen", "document-new", "primary")
        create_btn.connect("clicked", self._on_create_project)
        button_box.pack_start(create_btn, False, False, 0)
        
        content.pack_start(button_box, False, False, 0)
        
        scroll.add(content)
        page.pack_start(scroll, True, True, 0)
        
        self.content_stack.add_named(page, "new_project")
        self.content_stack.set_visible_child_name("new_project")
    
    def _show_projects_screen(self):
        """Show projects list screen."""
        if self.content_stack.get_child_by_name("projects"):
            self.content_stack.set_visible_child_name("projects")
            return
        
        page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        page.get_style_context().add_class("content-area")
        
        # Header
        header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=16)
        
        title_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        
        title = Gtk.Label(label="Meine Projekte")
        title.get_style_context().add_class("page-title")
        title.set_halign(Gtk.Align.START)
        title_box.pack_start(title, False, False, 0)
        
        subtitle = Gtk.Label(label="Alle deine Projekte auf einen Blick")
        subtitle.get_style_context().add_class("page-subtitle")
        subtitle.set_halign(Gtk.Align.START)
        title_box.pack_start(subtitle, False, False, 0)
        
        header_box.pack_start(title_box, True, True, 0)
        
        # New project button
        new_btn = ModernButton("Neues Projekt", "list-add", "primary")
        new_btn.connect("clicked", lambda x: self._show_new_project_screen())
        new_btn.set_valign(Gtk.Align.CENTER)
        header_box.pack_start(new_btn, False, False, 0)
        
        page.pack_start(header_box, False, False, 0)
        
        # Scrollable content
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroll.set_margin_top(32)
        scroll.set_margin_start(32)
        scroll.set_margin_end(32)
        scroll.set_margin_bottom(32)
        
        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        
        # Filter bar
        filter_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        filter_box.set_margin_bottom(16)
        
        search_input = ModernEntry(placeholder="Projekte durchsuchen...", icon="system-search-symbolic")
        filter_box.pack_start(search_input, True, True, 0)
        
        content.pack_start(filter_box, False, False, 0)
        
        # Projects list
        for i in range(5):
            card = ModernCard(
                title=f"Projekt {i+1}",
                subtitle="Eine tolle Webanwendung mit moderner UI",
                icon="folder-symbolic"
            )
            
            # Add metadata row
            meta_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=16)
            meta_box.set_margin_top(8)
            
            # Status
            statuses = [("Aktiv", "success"), ("In Entwicklung", "info"), 
                       ("Review", "warning"), ("Aktiv", "success"), ("Pausiert", "error")]
            text, status = statuses[i]
            badge = StatusBadge(text, status)
            meta_box.pack_start(badge, False, False, 0)
            
            # Date
            date_label = Gtk.Label(label=f"Erstellt: {i+1}.02.2026")
            date_label.get_style_context().add_class("card-subtitle")
            meta_box.pack_start(date_label, False, False, 0)
            
            # Spacer
            meta_box.pack_start(Gtk.Box(), True, True, 0)
            
            # Actions
            open_btn = ModernButton("Öffnen", style="ghost")
            meta_box.pack_start(open_btn, False, False, 0)
            
            card.content.pack_start(meta_box, False, False, 0)
            content.pack_start(card, False, False, 0)
        
        scroll.add(content)
        page.pack_start(scroll, True, True, 0)
        
        self.content_stack.add_named(page, "projects")
        self.content_stack.set_visible_child_name("projects")
    
    def _show_placeholder_screen(self, page_id: str):
        """Show placeholder for unimplemented screens."""
        name = f"placeholder_{page_id}"
        if self.content_stack.get_child_by_name(name):
            self.content_stack.set_visible_child_name(name)
            return
        
        page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=24)
        page.get_style_context().add_class("content-area")
        page.set_valign(Gtk.Align.CENTER)
        page.set_halign(Gtk.Align.CENTER)
        
        icon = Gtk.Label(label="🚧")
        icon.set_markup('<span font_size="xx-large">🚧</span>')
        page.pack_start(icon, False, False, 0)
        
        title = Gtk.Label(label=page_id.title())
        title.get_style_context().add_class("page-title")
        page.pack_start(title, False, False, 0)
        
        subtitle = Gtk.Label(label="Diese Funktion wird bald verfügbar sein!")
        subtitle.get_style_context().add_class("page-subtitle")
        page.pack_start(subtitle, False, False, 0)
        
        back_btn = ModernButton("Zurück zum Dashboard", "go-previous", "primary")
        back_btn.connect("clicked", lambda x: self._show_welcome_screen())
        back_btn.set_halign(Gtk.Align.CENTER)
        page.pack_start(back_btn, False, False, 0)
        
        self.content_stack.add_named(page, name)
        self.content_stack.set_visible_child_name(name)
    
    # Event handlers
    def _on_webapp_clicked(self, button):
        """Handle web app quick action."""
        logger.info("quick_action_clicked", action="webapp")
        self._show_new_project_screen()
    
    def _on_mobile_clicked(self, button):
        """Handle mobile app quick action."""
        logger.info("quick_action_clicked", action="mobile")
        self._show_new_project_screen()
    
    def _on_api_clicked(self, button):
        """Handle API quick action."""
        logger.info("quick_action_clicked", action="api")
        self._show_new_project_screen()
    
    def _on_chatbot_clicked(self, button):
        """Handle chatbot quick action."""
        logger.info("quick_action_clicked", action="chatbot")
        self._show_new_project_screen()
    
    def _on_dashboard_clicked(self, button):
        """Handle dashboard quick action."""
        logger.info("quick_action_clicked", action="dashboard")
        self._show_new_project_screen()
    
    def _on_game_clicked(self, button):
        """Handle game quick action."""
        logger.info("quick_action_clicked", action="game")
        self._show_new_project_screen()
    
    def _on_create_project(self, button):
        """Handle project creation."""
        logger.info("create_project_clicked")
        # TODO: Implement project creation
        self._show_placeholder_screen("creating")


class NoodeDesktopApp(Gtk.Application):
    """Main GTK Application."""
    
    def __init__(self):
        super().__init__(application_id="dev.noode.desktop")
        
        self.window: Optional[NoodeWindow] = None
    
    def do_activate(self):
        """Activate the application."""
        if not self.window:
            self.window = NoodeWindow(application=self)
        
        self.window.show_all()
        self.window.present()
    
    def do_startup(self):
        """Startup the application."""
        Gtk.Application.do_startup(self)


def main():
    """Entry point."""
    # Enable asyncio integration
    import asyncio
    
    app = NoodeDesktopApp()
    return app.run(sys.argv)


if __name__ == "__main__":
    sys.exit(main())
