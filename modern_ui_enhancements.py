# Modern UI Enhancement Functions for SentriGuide AI
# This file contains additional UI enhancement functions that can be integrated

import tkinter as tk

# Modern UI Animation and Enhancement Functions
def add_card_shadow_effect(widget):
    """Add modern card shadow effect to widgets"""
    try:
        widget.configure(relief='flat', bd=1,
                        highlightbackground='#E0E0E0',
                        highlightthickness=1)
    except:
        pass  # Fallback if shadow effect not supported

def add_hover_animation(widget, hover_color, original_color):
    """Add modern hover animation to buttons"""
    def on_hover(event):
        widget.config(bg=hover_color)
    def on_leave(event):
        widget.config(bg=original_color)

    widget.bind('<Enter>', on_hover)
    widget.bind('<Leave>', on_leave)

def animate_typing_indicator(label_widget, message="Typing"):
    """Animate typing indicator with dots"""
    dots = [".", "..", "..."]
    current_dot = 0

    def update_dots():
        nonlocal current_dot
        if label_widget and label_widget.winfo_exists():
            label_widget.config(text=f"{message}{dots[current_dot]}")
            current_dot = (current_dot + 1) % len(dots)
            label_widget.after(500, update_dots)

    update_dots()

def create_modern_button(parent, text, command, bg_color, text_color='white', **kwargs):
    """Create a modern styled button with consistent design"""
    button = tk.Button(parent, text=text, command=command,
                      bg=bg_color, fg=text_color,
                      font=('Inter, Segoe UI, Arial, sans-serif', 11, 'bold'),
                      relief='flat', bd=0,
                      padx=16, pady=8,
                      cursor='hand2', **kwargs)

    # Add hover effect
    hover_color = bg_color.replace('C0', 'F5') if 'C0' in bg_color else bg_color  # Simple color lightening
    add_hover_animation(button, hover_color, bg_color)

    return button

def apply_modern_styling(widget, widget_type="frame"):
    """Apply modern styling to widgets"""
    try:
        if widget_type == "frame":
            widget.configure(bg='#FFFFFF', relief='flat')
            add_card_shadow_effect(widget)
        elif widget_type == "text":
            widget.configure(bg='#FFFFFF', fg='#212121',
                           relief='flat', bd=0, highlightthickness=1,
                           highlightcolor='#1565C0',
                           highlightbackground='#E0E0E0')
        elif widget_type == "entry":
            widget.configure(bg='#F5F5F5', fg='#212121',
                           relief='flat', bd=1, highlightthickness=2,
                           highlightcolor='#1565C0',
                           highlightbackground='#E0E0E0')
    except:
        pass  # Fallback if styling fails

def create_gradient_frame(parent, start_color, end_color, height=60):
    """Create a gradient effect frame (simplified version)"""
    frame = tk.Frame(parent, bg=start_color, height=height)
    frame.pack_propagate(False)
    return frame

def add_pulse_animation(widget, color1, color2, duration=1000):
    """Add subtle pulse animation to widgets"""
    def pulse():
        widget.config(bg=color2)
        widget.after(duration//2, lambda: widget.config(bg=color1))
        widget.after(duration, pulse)

    pulse()

# Usage Examples:
"""
# Apply modern styling to a frame
modern_frame = tk.Frame(parent)
apply_modern_styling(modern_frame, "frame")

# Create a modern button
modern_btn = create_modern_button(parent, "Click Me", my_command, "#1565C0")

# Add typing animation to a label
typing_label = tk.Label(parent, text="")
animate_typing_indicator(typing_label, "AI is thinking")

# Add hover effect to existing button
add_hover_animation(my_button, "#42A5F5", "#1565C0")
"""