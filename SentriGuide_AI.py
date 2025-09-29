import os
import tkinter as tk
from tkinter import scrolledtext, messagebox, ttk
import threading
import datetime
import time
import requests
from bs4 import BeautifulSoup
import re

# =============================
# SentriGuide AI Configuration
# =============================
TREND_MICRO_HELP_CENTER = "https://helpcenter.trendmicro.com/en-us/"
SEARCH_KEYWORDS = ["antivirus", "security", "malware", "threat", "protection", "scan", "update", "firewall", "email", "endpoint", "renew", "renewal", "subscription", "activate", "activation", "license", "expire", "expiration", "payment", "billing"]

# =============================
# Responsive UI Scaling System
# =============================
def get_screen_info():
    """Get screen dimensions and calculate scaling factors"""
    # Create temporary root to get screen info
    temp_root = tk.Tk()
    temp_root.withdraw()  # Hide the window

    screen_width = temp_root.winfo_screenwidth()
    screen_height = temp_root.winfo_screenheight()

    temp_root.destroy()

    # Calculate scaling factors based on common resolutions
    # Base resolution: 1920x1080 (scale factor 1.0)
    width_scale = screen_width / 1920.0
    height_scale = screen_height / 1080.0

    # Use the smaller scale to maintain aspect ratio
    scale_factor = min(width_scale, height_scale)

    # Clamp scaling between 0.7 and 2.0 for usability
    scale_factor = max(0.7, min(2.0, scale_factor))

    return {
        'screen_width': screen_width,
        'screen_height': screen_height,
        'scale_factor': scale_factor,
        'width_scale': width_scale,
        'height_scale': height_scale
    }

def calculate_scaled_dimensions(base_width, base_height, scale_info):
    """Calculate scaled dimensions for windows"""
    scale = scale_info['scale_factor']

    # Calculate scaled dimensions
    scaled_width = int(base_width * scale)
    scaled_height = int(base_height * scale)

    # Ensure minimum usable size
    scaled_width = max(800, scaled_width)
    scaled_height = max(600, scaled_height)

    # Ensure doesn't exceed screen size (with padding)
    max_width = int(scale_info['screen_width'] * 0.95)
    max_height = int(scale_info['screen_height'] * 0.9)

    scaled_width = min(scaled_width, max_width)
    scaled_height = min(scaled_height, max_height)

    return scaled_width, scaled_height

def calculate_font_size(base_size, scale_factor):
    """Calculate appropriate font size based on scale factor"""
    scaled_size = int(base_size * scale_factor)
    return max(8, min(16, scaled_size))  # Clamp between 8 and 16

# Get screen information and calculate scaling
SCREEN_INFO = get_screen_info()
SCALE_FACTOR = SCREEN_INFO['scale_factor']

# Modern SentriGuide UI Theme with Dynamic Scaling
SENTRIGUIDE_THEME = {
    # Modern Color Palette - Material Design 3.0 Inspired
    'primary': '#1565C0',        # Modern blue - trust & technology
    'primary_light': '#42A5F5',  # Light blue accent
    'primary_dark': '#0D47A1',   # Dark blue for contrast
    'secondary': '#424242',      # Modern gray - professional
    'secondary_light': '#757575', # Light gray for subtle elements
    'accent': '#E91E63',         # Modern pink - attention & energy
    'accent_light': '#F06292',   # Light pink for hover states
    'success': '#2E7D32',        # Modern green - positive outcomes
    'success_light': '#4CAF50',  # Light green for highlights
    'warning': '#F57C00',        # Modern orange - caution
    'warning_light': '#FF9800',  # Light orange for warnings
    'danger': '#C62828',         # Modern red - urgent attention
    'danger_light': '#F44336',   # Light red for alerts
    'info': '#1976D2',           # Information blue
    'info_light': '#2196F3',     # Light info blue

    # Modern Background Colors
    'bg_primary': '#FAFAFA',     # Pure white background
    'bg_secondary': '#F5F5F5',   # Light gray background
    'bg_surface': '#FFFFFF',     # Card/surface background
    'bg_dark': '#212121',        # Dark theme background
    'bg_gradient_start': '#1565C0',  # Gradient start color
    'bg_gradient_end': '#1976D2',    # Gradient end color

    # Modern Text Colors
    'text_primary': '#212121',   # Primary text - high emphasis
    'text_secondary': '#757575', # Secondary text - medium emphasis
    'text_disabled': '#BDBDBD',  # Disabled text - low emphasis
    'text_inverse': '#FFFFFF',   # Text on dark backgrounds
    'text_accent': '#1565C0',    # Accent text color

    # Modern Typography
    'font_primary': 'Inter, Segoe UI, Arial, sans-serif',  # Modern font stack
    'font_mono': 'JetBrains Mono, Consolas, monospace',   # Monospace font
    'font_size': calculate_font_size(10, SCALE_FACTOR),
    'font_size_small': calculate_font_size(9, SCALE_FACTOR),
    'font_size_medium': calculate_font_size(11, SCALE_FACTOR),
    'font_size_large': calculate_font_size(13, SCALE_FACTOR),
    'font_size_header': calculate_font_size(16, SCALE_FACTOR),
    'font_size_title': calculate_font_size(20, SCALE_FACTOR),
    'font_size_display': calculate_font_size(24, SCALE_FACTOR),

    # Modern Spacing System (8px grid)
    'spacing_xs': max(2, int(4 * SCALE_FACTOR)),    # 4px
    'spacing_sm': max(4, int(8 * SCALE_FACTOR)),    # 8px
    'spacing_md': max(8, int(12 * SCALE_FACTOR)),   # 12px
    'spacing_lg': max(12, int(16 * SCALE_FACTOR)),  # 16px
    'spacing_xl': max(16, int(24 * SCALE_FACTOR)),  # 24px
    'spacing_xxl': max(24, int(32 * SCALE_FACTOR)), # 32px

    # Legacy padding support
    'padding_small': max(4, int(8 * SCALE_FACTOR)),
    'padding_medium': max(8, int(12 * SCALE_FACTOR)),
    'padding_large': max(12, int(16 * SCALE_FACTOR)),

    # Modern UI Elements
    'border_radius': max(4, int(8 * SCALE_FACTOR)),  # Rounded corners
    'border_radius_large': max(8, int(12 * SCALE_FACTOR)),  # Large rounded corners
    'shadow_light': '#E0E0E0',   # Light shadow color
    'shadow_dark': '#BDBDBD',    # Dark shadow color
    'divider': '#E0E0E0',        # Divider line color

    # Status Colors
    'online': '#4CAF50',         # Online status
    'offline': '#9E9E9E',        # Offline status
    'busy': '#FF9800',           # Busy status
    'away': '#FFC107',           # Away status
}

# Global state
conversation_history = []
conversation_summary = ""
customer_sentiment = {"emotion": "neutral", "urgency": "medium", "satisfaction": 70}
resolution_confidence = 0
knowledge_suggestions = []
solution_history = []  # Track past solutions provided to customers
anthropic_client = None
is_processing = False
conversation_ended = False
ended_conversation_display = []

# UI Components
engineer_chat_window = None
customer_simulation_window = None
context_panel = None
sentiment_panel = None
confidence_panel = None
knowledge_panel = None
coaching_panel = None
solution_history_panel = None
solution_history_var = None
solution_history_dropdown = None
status_label = None

# Coaching System
coaching_feedback = ""
performance_metrics = {
    "response_time": "good",
    "empathy_level": "medium",
    "technical_accuracy": "high",
    "communication_clarity": "good",
    "session_progress": "on_track"
}

# Real-time Performance Tracking
session_metrics = {
    "messages_sent": 0,
    "avg_response_length": 0,
    "empathy_score_total": 0,
    "technical_accuracy_total": 0,
    "clarity_score_total": 0,
    "session_start_time": None,
    "last_response_time": None,
    "escalation_warnings": 0,
    "customer_satisfaction_trend": []
}

# =============================
# No Authentication Required - Web-based Mode
# =============================
def setup_system():
    """Setup system without requiring API keys"""
    print("✅ SentriGuide AI initialized (Web-based mode)")
    return True

# =============================
# Trend Micro Help Center Integration
# =============================
def fetch_trend_micro_articles(query="security"):
    """Fetch articles from Trend Micro Help Center"""

    # Special case: return fallback articles directly when requested
    if query == "fallback":
        return get_fallback_articles()

    try:
        # Search URL for official Trend Micro Help Center
        search_url = f"https://helpcenter.trendmicro.com/en-us/search?q={query}"

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        response = requests.get(search_url, headers=headers, timeout=10)

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract article titles and links
            articles = []

            # Look for article structures specific to Trend Micro Help Center
            for article in soup.find_all(['article', 'div', 'a'], class_=re.compile(r'(result|search|article|card)')):
                title_elem = article.find(['h1', 'h2', 'h3', 'h4', 'span', 'a'])
                if title_elem and title_elem.get_text().strip():
                    title = title_elem.get_text().strip()

                    # Get the link
                    link = article.get('href', '')
                    if not link and title_elem.name == 'a':
                        link = title_elem.get('href', '')

                    # Make sure link is complete
                    if link and not link.startswith('http'):
                        link = f"https://helpcenter.trendmicro.com{link}"

                    if len(title) > 10 and len(title) < 200:
                        articles.append({
                            'title': title,
                            'link': link or 'https://helpcenter.trendmicro.com/en-us/',
                            'snippet': title[:150]
                        })

            # Remove duplicates
            seen_titles = set()
            unique_articles = []
            for article in articles:
                if article['title'] not in seen_titles:
                    seen_titles.add(article['title'])
                    unique_articles.append(article)

            if unique_articles:
                return unique_articles[:5]  # Return top 5 results

    except Exception as e:
        print(f"Error fetching Trend Micro articles: {str(e)}")

    # Fallback: return comprehensive Trend Micro help topics from official help center
    return get_fallback_articles()

def get_fallback_articles():
    """Return comprehensive fallback Trend Micro help articles"""
    return [
        {
            'title': 'How to Renew Your Trend Micro Product',
            'link': 'https://helpcenter.trendmicro.com/en-us/how-to-renew/',
            'snippet': '''DETAILED RENEWAL GUIDE FOR CUSTOMERS:

📋 PREPARATION (Share with Customer):
• Have your activation code ready
• Ensure stable internet connection
• Have payment method available
• Know your Trend Micro account credentials

🔄 METHOD 1: Using Activation Code
1. Open your Trend Micro product
2. Look for "Renew" or "Enter Activation Code" option
3. Enter your activation code in the designated field
4. Click "Submit" or "Activate"
5. Follow on-screen instructions to complete renewal
6. Confirm subscription details and proceed to payment
7. Wait for confirmation email

🌐 METHOD 2: Through Trend Micro Account Portal
1. Visit https://account.trendmicro.com
2. Sign in with your account credentials
3. Navigate to "Licenses" or "Subscriptions" tab
4. Locate the subscription you want to renew
5. Click "Renew Now" button
6. If you see "Manage Subscription", auto-renewal is already enabled
7. Follow the secure checkout process
8. Complete payment and save confirmation

⚠️ SPECIAL SCENARIOS:
• Best Buy purchases: Direct customer to call 1-888-237-8289
• ISP bundled subscriptions: Contact internet service provider
• Corporate licenses: Refer to IT administrator

🔧 TROUBLESHOOTING STEPS:
• Error messages during renewal: Clear browser cache, try different browser
• Payment issues: Verify card details, try alternative payment method
• Activation code problems: Check for typos, ensure code hasn't expired
• Account access issues: Use password reset option
• Still having issues: Escalate to Trend Micro Support Team

✅ POST-RENEWAL VERIFICATION:
1. Check that subscription shows as "Active" in account portal
2. Verify new expiration date
3. Ensure real-time protection is running
4. Save renewal confirmation for records'''
        },
        {
            'title': 'Installing and Activating Trend Micro Products',
            'link': 'https://helpcenter.trendmicro.com/en-us/installation/',
            'snippet': '''COMPREHENSIVE INSTALLATION GUIDE FOR CUSTOMERS:

📋 PRE-INSTALLATION REQUIREMENTS:
• Windows 10/11 (32-bit or 64-bit) or macOS 10.15+
• Minimum 1.5 GB free disk space
• Stable internet connection for download and activation
• Administrator privileges on the computer
• Valid Trend Micro license or activation code

💻 STEP-BY-STEP INSTALLATION PROCESS:

1️⃣ DOWNLOAD THE INSTALLER:
   • Visit https://account.trendmicro.com
   • Sign in with your Trend Micro account credentials
   • Navigate to the "Downloads" tab
   • Select "Maximum Security" or your product
   • Click "Download to this Device"
   • Save the installer file to your desktop

2️⃣ RUN THE INSTALLATION:
   • Right-click the downloaded installer file
   • Select "Run as Administrator" (Windows) or double-click (Mac)
   • Click "Yes" if prompted by User Account Control
   • Follow the installation wizard prompts
   • Accept the license agreement
   • Choose installation directory (default recommended)

3️⃣ PRODUCT ACTIVATION:
   • Enter your activation code when prompted
   • Or sign in with your Trend Micro account
   • Wait for online activation to complete
   • Restart computer if prompted

4️⃣ INITIAL SETUP:
   • Complete the product setup wizard
   • Configure scan settings (recommended: use defaults)
   • Enable real-time protection
   • Set up automatic updates
   • Create recovery tools if offered

✅ POST-INSTALLATION VERIFICATION:
   • Check that Trend Micro icon appears in system tray
   • Verify "Protection Status: Secured" in main interface
   • Run initial system scan to ensure everything works
   • Confirm automatic updates are enabled

🔧 COMMON INSTALLATION ISSUES & SOLUTIONS:
   • "Installation failed" error: Uninstall competing antivirus first
   • "Activation failed" error: Check internet connection, verify code
   • "Insufficient space" error: Free up disk space, clear temp files
   • Installation freezes: Disable Windows Defender temporarily during install
   • Permission errors: Ensure running installer as Administrator

📱 MOBILE DEVICE INSTALLATION:
   • Android: Download from Google Play Store
   • iOS: Download from Apple App Store
   • Search for "Trend Micro Mobile Security"
   • Sign in with same Trend Micro account for license sync

🆘 IF INSTALLATION CONTINUES TO FAIL:
   • Use Trend Micro Diagnostic Toolkit to clean previous installations
   • Temporarily disable Windows Firewall during installation
   • Contact Trend Micro Support with error codes/screenshots'''
        },
        {
            'title': 'Troubleshooting Common Issues',
            'link': 'https://helpcenter.trendmicro.com/en-us/troubleshooting/',
            'snippet': 'Solutions for common problems including installation errors, scanning issues, and performance problems.'
        },
        {
            'title': 'Configuring Real-time Protection',
            'link': 'https://helpcenter.trendmicro.com/en-us/protection-settings/',
            'snippet': 'Learn how to configure and optimize real-time protection settings for maximum security.'
        },
        {
            'title': 'Managing Quarantined Files',
            'link': 'https://helpcenter.trendmicro.com/en-us/quarantine/',
            'snippet': 'How to review, restore, or permanently delete files in quarantine to manage detected threats.'
        },
        {
            'title': 'Email Security Configuration',
            'link': 'https://helpcenter.trendmicro.com/en-us/email-security/',
            'snippet': 'Configure email protection settings to block spam, phishing, and malicious attachments.'
        },
        {
            'title': 'Web Protection and Browsing Safety',
            'link': 'https://helpcenter.trendmicro.com/en-us/web-protection/',
            'snippet': 'Enable web filtering and safe browsing features to protect against malicious websites.'
        },
        {
            'title': 'Firewall Settings and Network Protection',
            'link': 'https://helpcenter.trendmicro.com/en-us/firewall/',
            'snippet': 'Configure firewall rules and network protection to secure your internet connection.'
        },
        {
            'title': 'Performance Optimization Tips',
            'link': 'https://helpcenter.trendmicro.com/en-us/performance/',
            'snippet': 'Optimize Trend Micro settings to minimize system impact while maintaining security.'
        },
        {
            'title': 'Virus and Malware Removal Guide',
            'link': 'https://helpcenter.trendmicro.com/en-us/malware-removal/',
            'snippet': 'Step-by-step instructions for removing detected threats and cleaning infected systems.'
        },
        {
            'title': 'Scheduled Scan Configuration',
            'link': 'https://helpcenter.trendmicro.com/en-us/scheduled-scans/',
            'snippet': 'Set up automated scans to regularly check your system for threats and vulnerabilities.'
        },
        {
            'title': 'Mobile Device Protection Setup',
            'link': 'https://helpcenter.trendmicro.com/en-us/mobile-security/',
            'snippet': 'Protect your mobile devices with Trend Micro Mobile Security features and settings.'
        },
        {
            'title': 'Password Manager Configuration',
            'link': 'https://helpcenter.trendmicro.com/en-us/password-manager/',
            'snippet': 'Set up and use the built-in password manager to secure your online accounts.'
        },
        {
            'title': 'Privacy and Data Protection',
            'link': 'https://helpcenter.trendmicro.com/en-us/privacy-protection/',
            'snippet': 'Configure privacy settings and data protection features to safeguard personal information.'
        },
        {
            'title': 'Parental Controls Setup',
            'link': 'https://helpcenter.trendmicro.com/en-us/parental-controls/',
            'snippet': 'Configure parental controls to protect children online and manage screen time.'
        },
        {
            'title': 'Backup and Restore Settings',
            'link': 'https://helpcenter.trendmicro.com/en-us/backup-restore/',
            'snippet': 'Backup your Trend Micro settings and restore configurations after reinstallation.'
        },
        {
            'title': 'Enterprise and Business Solutions',
            'link': 'https://helpcenter.trendmicro.com/en-us/business/',
            'snippet': 'Deployment and management guides for Trend Micro business and enterprise products.'
        },
        {
            'title': 'Technical Support Resources',
            'link': 'https://helpcenter.trendmicro.com/en-us/support/',
            'snippet': 'Access diagnostic tools, log collection, and contact information for technical support.'
        },
        {
            'title': 'License Management and Transfer',
            'link': 'https://helpcenter.trendmicro.com/en-us/license-management/',
            'snippet': 'Manage your licenses, transfer them between devices, and resolve activation issues.'
        },
        {
            'title': 'Cloud Security Best Practices',
            'link': 'https://helpcenter.trendmicro.com/en-us/cloud-security/',
            'snippet': 'Secure cloud services and protect data stored in cloud environments with Trend Micro.'
        },
        {
            'title': 'Password Manager Setup and Import Guide',
            'link': 'https://helpcenter.trendmicro.com/en-us/password-manager/',
            'snippet': '''COMPREHENSIVE PASSWORD MANAGER GUIDE:

🔐 SETTING UP PASSWORD MANAGER:
• Open Trend Micro Maximum Security or ID Protection
• Navigate to "Password Manager" section
• Click "Get Started" or "Enable Password Manager"
• Create a master password (remember this - it cannot be recovered!)
• Confirm master password and security questions
• Enable browser extension when prompted

📥 IMPORTING PASSWORDS FROM OTHER MANAGERS:
1️⃣ FROM CHROME/EDGE BROWSER:
   • Open Password Manager → Settings → Import
   • Select "Browser" as source
   • Choose Chrome/Edge from dropdown
   • Click "Import Now" - passwords will sync automatically

2️⃣ FROM OTHER PASSWORD MANAGERS:
   • Export passwords from old manager as CSV file
   • In Trend Micro: Settings → Import → "CSV File"
   • Select exported CSV file
   • Map fields if needed (username, password, website)
   • Click "Import" to transfer all passwords

3️⃣ MANUAL ENTRY:
   • Click "Add New" in Password Manager
   • Enter website URL, username, password
   • Add notes if needed
   • Save entry

🛡️ SECURITY FEATURES:
• Password Generator: Create strong, unique passwords
• Auto-Fill: Automatically fill login forms
• Secure Notes: Store sensitive information safely
• Security Audit: Check for weak/reused passwords
• Dark Web Monitoring: Alert if passwords are compromised

🔧 TROUBLESHOOTING COMMON ISSUES:
• Import failed: Check CSV format, ensure no special characters
• Auto-fill not working: Enable browser extension, check permissions
• Forgot master password: Cannot be recovered - will need to reset (loses all data)
• Sync issues: Sign out and back into Trend Micro account
• Browser extension missing: Reinstall from Trend Micro dashboard'''
        },
        {
            'title': 'ID Protection and Privacy Setup',
            'link': 'https://helpcenter.trendmicro.com/en-us/id-protection/',
            'snippet': '''COMPLETE ID PROTECTION SETUP GUIDE:

🛡️ IDENTITY PROTECTION FEATURES:
• Social Security Number monitoring
• Credit report monitoring
• Dark web monitoring for personal data
• Identity theft insurance coverage
• Personal information cleanup
• Identity restoration services

📋 INITIAL SETUP PROCESS:
1. Open Trend Micro ID Protection
2. Complete identity verification with SSN and personal details
3. Connect bank accounts and credit cards for monitoring
4. Set up alerts for suspicious activity
5. Enable dark web monitoring
6. Configure privacy settings

🔍 MONITORING SERVICES:
• Credit Score Tracking: Monthly updates and alerts
• Bank Account Monitoring: Unusual transaction alerts
• Social Media Scanning: Check for unauthorized use of personal info
• Public Records Monitoring: Track when your info appears online
• Data Breach Notifications: Immediate alerts if your data is found

⚠️ IDENTITY THEFT RESPONSE:
• Immediate notification of suspicious activity
• Step-by-step guidance for reporting theft
• Access to identity restoration specialists
• Help with freezing credit reports
• Assistance with fraud alerts and credit disputes

🔧 PRIVACY TOOLS:
• Personal Data Removal: Remove info from data broker sites
• Social Media Privacy Checkup: Secure your online profiles
• Email Monitoring: Track if email appears in breaches
• Phone Number Protection: Monitor for unauthorized use

💡 BEST PRACTICES:
• Review alerts promptly and take recommended actions
• Keep personal information updated in your profile
• Use strong, unique passwords for all accounts
• Enable two-factor authentication where possible
• Regularly check credit reports and bank statements'''
        },
        {
            'title': 'VPN and Secure Connection Setup',
            'link': 'https://helpcenter.trendmicro.com/en-us/vpn/',
            'snippet': '''TREND MICRO VPN SETUP AND USAGE:

🌐 VPN BENEFITS:
• Hide your IP address and location
• Encrypt internet traffic on public Wi-Fi
• Access geo-restricted content safely
• Protect against online tracking
• Secure browsing on untrusted networks

⚙️ VPN SETUP PROCESS:
1. Open Trend Micro Maximum Security
2. Navigate to "Privacy" or "VPN" section
3. Click "Enable VPN" or "Get Started"
4. Choose server location (or use "Auto-Select")
5. Click "Connect" to establish secure connection
6. Verify connection with green "Connected" status

🗺️ SERVER LOCATIONS:
• United States (multiple cities)
• United Kingdom • Germany • Japan
• Canada • Australia • Netherlands
• Auto-Select: Chooses fastest available server
• Specialized servers for streaming and gaming

📱 MOBILE VPN SETUP:
• Download Trend Micro Mobile Security app
• Sign in with your Trend Micro account
• Tap "VPN" → "Enable VPN"
• Allow VPN configuration when prompted
• Select server location and connect

🔧 TROUBLESHOOTING VPN ISSUES:
• Connection fails: Try different server location
• Slow speeds: Use Auto-Select or nearest server
• Can't access local sites: Disconnect VPN temporarily
• Mobile VPN not working: Check app permissions
• Netflix/streaming blocked: Try different server region

💡 OPTIMAL USAGE TIPS:
• Use VPN on public Wi-Fi networks always
• Disconnect when using banking apps (some block VPN)
• Choose nearest server location for best speed
• Enable "Auto-Connect" for automatic protection
• Monitor data usage on mobile devices'''
        },
        {
            'title': 'Email Security and Anti-Spam Configuration',
            'link': 'https://helpcenter.trendmicro.com/en-us/email-security/',
            'snippet': '''EMAIL SECURITY COMPREHENSIVE SETUP:

📧 EMAIL PROTECTION FEATURES:
• Spam filtering and blocking
• Phishing email detection
• Malicious attachment scanning
• Link protection and URL filtering
• Email encryption capabilities
• Anti-spoofing protection

⚙️ OUTLOOK INTEGRATION SETUP:
1. Install Trend Micro Maximum Security
2. Open Outlook → File → Options → Add-ins
3. Verify "Trend Micro Email Security" is enabled
4. Configure scan settings in Trend Micro main interface
5. Set spam sensitivity level (Low/Medium/High)
6. Enable real-time email scanning

🛡️ ANTI-SPAM CONFIGURATION:
• Spam Sensitivity: Adjust based on false positive rate
• Whitelist: Add trusted senders to never block
• Blacklist: Block specific domains or email addresses
• Quarantine: Review blocked emails before deletion
• Custom Rules: Create advanced filtering criteria

🔍 PHISHING PROTECTION:
• Automatic suspicious link scanning
• Warning messages for potential phishing
• Safe browser redirection for protected links
• Real-time URL reputation checking
• Email header analysis for spoofing detection

📎 ATTACHMENT SCANNING:
• Real-time malware detection in attachments
• Quarantine suspicious files automatically
• Safe file type allowlists
• Password-protected archive scanning
• Cloud-based threat intelligence integration

🔧 TROUBLESHOOTING EMAIL ISSUES:
• Legitimate emails in spam: Add sender to whitelist
• Outlook integration not working: Reinstall Trend Micro
• Email scanning slow: Adjust real-time scan settings
• Missing email toolbar: Enable Trend Micro add-in in Outlook
• False phishing warnings: Report false positive to support'''
        },
        {
            'title': 'Parental Controls and Family Protection',
            'link': 'https://helpcenter.trendmicro.com/en-us/parental-controls/',
            'snippet': '''COMPREHENSIVE PARENTAL CONTROLS SETUP:

👨‍👩‍👧‍👦 FAMILY PROTECTION FEATURES:
• Content filtering by age-appropriate categories
• Screen time management and schedules
• App usage monitoring and restrictions
• Location tracking and geofencing alerts
• Social media activity monitoring
• Cyberbullying detection and alerts

⚙️ INITIAL SETUP PROCESS:
1. Open Trend Micro Family → Create family account
2. Add child profiles with names and ages
3. Install Trend Micro Mobile Security on child devices
4. Configure content filtering levels by age group
5. Set screen time limits and schedules
6. Enable location tracking with child consent

🕐 SCREEN TIME MANAGEMENT:
• Daily time limits for device usage
• Scheduled "bedtime" hours with device lockdown
• App-specific time restrictions
• Homework mode: Block entertainment apps during study time
• Weekend vs weekday different schedules
• Instant pause/resume device access

🌐 CONTENT FILTERING OPTIONS:
• Age-based preset filters (Young Child, Tween, Teen)
• Custom category blocking (Social Media, Gaming, Adult Content)
• Website whitelist/blacklist management
• Safe search enforcement on search engines
• YouTube restricted mode activation
• Social media platform monitoring

📱 MOBILE DEVICE CONTROLS:
• App installation approval requirements
• In-app purchase restrictions
• Contact management and stranger blocking
• Text message monitoring for inappropriate content
• Call log tracking and unknown number alerts
• Emergency contact always-available settings

🔧 TROUBLESHOOTING FAMILY ISSUES:
• Child bypassing controls: Enable strict enforcement mode
• Legitimate sites blocked: Add to whitelist or adjust filter level
• Location not updating: Check GPS permissions on child device
• App blocks not working: Verify Mobile Security is installed and active
• Schedule conflicts: Review overlapping time restrictions'''
        },
        {
            'title': 'Cashback Claims and Refund Requests',
            'link': 'https://helpcenter.trendmicro.com/en-us/billing-refunds/',
            'snippet': '''COMPREHENSIVE BILLING AND REFUND GUIDE:

💰 CASHBACK CLAIM PROCESS:
• Cashback offers are typically promotional and time-limited
• Check original purchase email or promotional materials for cashback terms
• Visit the retailer's cashback portal (Best Buy, Amazon, etc.)
• Submit cashback claim within specified timeframe (usually 30-90 days)
• Provide proof of purchase (receipt, order confirmation)
• Track claim status through retailer's cashback system

📋 REFUND REQUEST PROCESS:
1️⃣ DIRECT TREND MICRO PURCHASES:
   • Visit https://account.trendmicro.com
   • Sign in to your account
   • Go to "Billing" or "Subscriptions" section
   • Click "Request Refund" or "Cancel Subscription"
   • Select refund reason from dropdown
   • Submit refund request with order details

2️⃣ RETAIL STORE PURCHASES:
   • Return to original point of purchase (Best Buy, Amazon, etc.)
   • Bring receipt and activation code/packaging
   • Follow retailer's return policy (usually 15-30 days)
   • Contact retailer customer service for assistance

3️⃣ DIGITAL MARKETPLACE PURCHASES:
   • App Store: Request refund through Apple Support
   • Google Play: Use Google Play refund process
   • Microsoft Store: Contact Microsoft support
   • Steam/Epic: Follow digital platform refund policies

⏰ REFUND TIMEFRAMES:
• Trend Micro Direct: 30-day money-back guarantee
• Retail stores: Varies by retailer (typically 15-30 days)
• Digital platforms: 14-48 hours for digital refunds
• Processing time: 5-10 business days after approval

💳 BILLING DISPUTE RESOLUTION:
• Unauthorized charges: Contact Trend Micro billing support immediately
• Duplicate charges: Provide transaction IDs for investigation
• Auto-renewal disputes: Show cancellation attempts/proof
• Proration requests: Explain downgrade/service change needs

📞 BILLING SUPPORT CONTACTS:
• Trend Micro Billing: 1-855-891-0011 (US/Canada)
• Live Chat: Available 24/7 through account portal
• Email Support: billing@trendmicro.com
• International: Check region-specific contact numbers

🔧 COMMON BILLING ISSUES:
• Can't find purchase: Check email, account history, credit card statements
• Refund not processed: Allow 10 business days, then contact support
• Auto-renewal unexpected: Disable in account settings for future
• Wrong product purchased: Exchange may be possible within 30 days
• Payment method failed: Update card info in account billing section

📝 REQUIRED INFORMATION FOR SUPPORT:
• Order number or transaction ID
• Email address used for purchase
• Last 4 digits of payment method
• Approximate purchase date
• Reason for refund request'''
        },
        {
            'title': 'Billing Account Management and Payment Issues',
            'link': 'https://helpcenter.trendmicro.com/en-us/billing-management/',
            'snippet': '''COMPLETE BILLING ACCOUNT MANAGEMENT:

💳 PAYMENT METHOD MANAGEMENT:
• Update credit card information before expiration
• Add backup payment methods for auto-renewal
• Remove old or expired payment methods
• Set up automatic payment notifications
• Configure billing address and tax information

🔄 SUBSCRIPTION MANAGEMENT:
• View current subscription status and expiration
• Manage auto-renewal settings (enable/disable)
• Upgrade or downgrade subscription plans
• Transfer licenses between devices
• Monitor device usage against license limits

📧 BILLING NOTIFICATIONS:
• Renewal reminders (30, 15, 7 days before expiration)
• Payment confirmation emails
• Failed payment alerts and retry attempts
• Receipt and invoice downloads
• Promotional offer notifications

🛠️ PAYMENT TROUBLESHOOTING:
• "Payment failed" errors: Check card expiration, available balance
• "Invalid payment method": Verify billing address matches bank records
• International payment issues: Contact bank about international transactions
• Declined transactions: Ensure card allows online/international purchases
• Currency conversion problems: Check if card supports foreign transactions

📊 BILLING HISTORY ACCESS:
• Download invoices and receipts from account portal
• View payment history for tax/expense reporting
• Track refunds and credits applied to account
• Monitor subscription changes and modifications
• Export billing data for accounting purposes

🔒 BILLING SECURITY:
• Use secure payment methods (avoid debit cards for subscriptions)
• Monitor credit card statements for Trend Micro charges
• Report unauthorized charges immediately
• Enable two-factor authentication on account
• Never share account credentials or payment information

💡 BILLING BEST PRACTICES:
• Set calendar reminders before auto-renewal dates
• Keep payment methods updated to avoid service interruption
• Review charges monthly for accuracy
• Download receipts immediately after purchase
• Contact support before charges if canceling subscription'''
        },
        {
            'title': 'Subscription Cancellation and Service Management',
            'link': 'https://helpcenter.trendmicro.com/en-us/cancel-subscription/',
            'snippet': '''SUBSCRIPTION CANCELLATION COMPREHENSIVE GUIDE:

❌ CANCELLATION PROCESS:
1. Sign in to https://account.trendmicro.com
2. Navigate to "Subscriptions" or "My Products"
3. Find active subscription to cancel
4. Click "Manage Subscription" or "Cancel"
5. Select cancellation reason (required)
6. Confirm cancellation and save changes
7. Receive cancellation confirmation email

⏰ CANCELLATION TIMING:
• Cancel anytime during subscription period
• Service continues until current period expires
• No prorated refunds for partial months (check specific terms)
• Auto-renewal stops immediately upon cancellation
• Reactivation possible before expiration date

🔄 ALTERNATIVE OPTIONS BEFORE CANCELING:
• Pause subscription: Temporary hold for up to 6 months
• Downgrade plan: Switch to lower-tier service
• Transfer to family member: Change account ownership
• Seasonal suspension: For temporary travel/non-use
• Contact retention team: May offer discounts or incentives

📱 MOBILE SUBSCRIPTION CANCELLATION:
• App Store subscriptions: Cancel through iOS Settings → Subscriptions
• Google Play subscriptions: Cancel through Play Store → Subscriptions
• Direct mobile billing: Use account portal cancellation process

💰 POST-CANCELLATION CONSIDERATIONS:
• Download software installers before expiration
• Export password manager data and settings
• Save important security reports and history
• Note expiration date for potential renewal
• Consider data backup before service ends

🔧 CANCELLATION TROUBLESHOOTING:
• "Cancel" button missing: May be retail/partner subscription - contact seller
• Cancellation not processed: Clear browser cache, try different browser
• Still charged after cancellation: Verify cancellation email, contact billing
• Want to cancel immediately: Request refund separately from cancellation
• Multiple subscriptions: Cancel each subscription individually

🆘 EMERGENCY CANCELLATION:
• Contact billing support for immediate assistance: 1-855-891-0011
• Use live chat for urgent cancellation needs
• Email billing@trendmicro.com with "URGENT CANCELLATION" in subject
• Dispute charges with bank if other methods fail
• Request manager escalation for complex situations

📋 CANCELLATION CHECKLIST:
✓ Export important data (passwords, reports, settings)
✓ Note current subscription expiration date
✓ Save cancellation confirmation email
✓ Remove auto-renewal from payment method if desired
✓ Consider alternative security solution before expiration
✓ Update password manager with new security software plans'''
        },
        {
            'title': 'Installation Error Troubleshooting Guide',
            'link': 'https://helpcenter.trendmicro.com/en-us/installation-errors/',
            'snippet': '''COMPREHENSIVE INSTALLATION ERROR SOLUTIONS:

❌ COMMON INSTALLATION ERRORS:

🔧 ERROR: "Installation Failed" or "Setup Error"
• Close all running programs and antivirus software
• Run installer as Administrator (right-click → "Run as administrator")
• Temporarily disable Windows Defender Real-time protection
• Clear Windows temp files: %temp% and delete all contents
• Download fresh installer from account portal
• Restart computer and try installation again

🔧 ERROR: "Another version already installed"
• Uninstall previous Trend Micro products completely
• Use Trend Micro Diagnostic Toolkit to remove remnants
• Clear registry entries with official uninstaller
• Restart computer before installing new version
• Run Windows Registry cleaner if issues persist

🔧 ERROR: "Insufficient privileges" or "Access denied"
• Right-click installer → "Run as administrator"
• Disable User Account Control temporarily
• Log in with administrator account
• Check folder permissions for installation directory
• Ensure account has administrative rights

🔧 ERROR: "Installation package corrupt" or "Cannot access installer"
• Download installer again from trusted source
• Verify file integrity and size
• Disable antivirus during download
• Try downloading on different network/computer
• Use different browser or clear browser cache

💻 SYSTEM COMPATIBILITY ISSUES:
• Windows version not supported: Check system requirements
• Insufficient disk space: Free up at least 2GB space
• Missing system updates: Install latest Windows updates
• Conflicting software: Uninstall competing antivirus products
• Architecture mismatch: Ensure 32-bit/64-bit compatibility

🌐 NETWORK AND DOWNLOAD ISSUES:
• Slow/interrupted download: Use stable internet connection
• Firewall blocking: Add Trend Micro to firewall exceptions
• Proxy settings: Configure proxy in installer if needed
• VPN interference: Temporarily disconnect VPN during installation
• Corporate network: Contact IT for installation permissions

🔄 POST-INSTALLATION ACTIVATION ERRORS:
• "Activation failed": Check internet connection and try again
• "Invalid activation code": Verify code spelling and expiration
• "Code already used": Contact support for new activation code
• "Server unavailable": Wait and retry, or try different time
• "Region mismatch": Ensure code matches your geographic region

🛠️ ADVANCED TROUBLESHOOTING STEPS:
1. Boot in Safe Mode and attempt installation
2. Create new Windows user account with admin rights
3. Use Windows System File Checker: sfc /scannow
4. Check Windows Event Viewer for detailed error messages
5. Disable startup programs that may interfere
6. Update device drivers, especially network and storage

📞 ESCALATION PROCEDURES:
• Collect installation logs from %temp% folder
• Note exact error messages and error codes
• Document system specifications and OS version
• Contact Trend Micro Technical Support: 1-888-762-8736
• Use remote assistance tools if offered by support team'''
        },
        {
            'title': 'Application Error and Crash Troubleshooting',
            'link': 'https://helpcenter.trendmicro.com/en-us/app-errors/',
            'snippet': '''COMPLETE APPLICATION ERROR RESOLUTION:

💥 APPLICATION CRASHES AND FREEZES:

🔧 ERROR: "Application has stopped working" or Sudden Crashes
• Update Trend Micro to latest version
• Restart Trend Micro services: Services.msc → Trend Micro services → Restart
• Run Windows Memory Diagnostic to check RAM
• Check for corrupted system files: sfc /scannow
• Disable conflicting software (other security tools)
• Reset Trend Micro settings to default

🔧 ERROR: Application Won't Start or "Failed to launch"
• Check if Trend Micro services are running
• Verify product license is active and not expired
• Run Trend Micro as Administrator
• Temporarily disable Windows Firewall
• Check for Windows updates and install
• Reinstall Trend Micro if issues persist

🔧 ERROR: Interface Freezes or Becomes Unresponsive
• Force close Trend Micro: Ctrl+Alt+Del → Task Manager → End Process
• Clear Trend Micro cache and temporary files
• Disable unnecessary Windows visual effects
• Check available system memory and close other programs
• Update graphics drivers
• Restart computer and relaunch application

🌐 WEBSITE AND WEB PROTECTION ERRORS:

🔧 ERROR: "Website blocked incorrectly" or False Positives
• Add website to Web Reputation exceptions
• Adjust Web Reputation sensitivity level
• Clear browser cache and cookies
• Disable Web Reputation temporarily for testing
• Report false positive to Trend Micro support
• Check if website is actually malicious using online scanners

🔧 ERROR: "Cannot access websites" or Connection Issues
• Check if Web Reputation is blocking access
• Verify internet connection without Trend Micro
• Flush DNS cache: ipconfig /flushdns
• Reset browser settings to default
• Disable proxy settings in browser
• Try accessing websites in incognito/private mode

🔧 ERROR: Browser Integration Not Working
• Reinstall browser extensions/add-ons
• Check browser compatibility with Trend Micro version
• Enable browser add-ons if disabled
• Update browser to latest version
• Clear browser cache and restart browser
• Run browser as administrator

📧 EMAIL AND SCANNING ERRORS:

🔧 ERROR: "Scan failed" or "Cannot complete scan"
• Check available disk space (need at least 1GB free)
• Close other resource-intensive programs
• Exclude scanning of very large files temporarily
• Update virus definition files
• Run scan in Safe Mode if persistent
• Check for file system errors: chkdsk /f

🔧 ERROR: Email Integration Problems
• Verify Outlook version compatibility
• Reinstall Trend Micro Email Security add-in
• Check if Outlook is running in administrator mode
• Disable other email security add-ins
• Repair Microsoft Office installation
• Reset Outlook profile if necessary

🔄 UPDATE AND SYNCHRONIZATION ERRORS:

🔧 ERROR: "Update failed" or "Cannot download updates"
• Check internet connection stability
• Verify Windows date and time settings
• Clear Trend Micro update cache
• Temporarily disable firewall during update
• Try manual update download from website
• Contact ISP if persistent connectivity issues

🔧 ERROR: "Sync error" or Cloud Synchronization Issues
• Verify Trend Micro account credentials
• Check account subscription status
• Clear sync cache and restart synchronization
• Ensure stable internet connection
• Try logging out and back into account
• Contact support if account shows as suspended

🆘 CRITICAL ERROR RECOVERY:
• Safe Mode troubleshooting steps
• System restore to point before issues began
• Complete uninstall and fresh installation
• Contact Technical Support with error logs
• Remote assistance session setup if needed'''
        },
        {
            'title': 'Website and Connectivity Technical Issues',
            'link': 'https://helpcenter.trendmicro.com/en-us/connectivity-issues/',
            'snippet': '''WEBSITE AND CONNECTIVITY TROUBLESHOOTING:

🌐 TREND MICRO WEBSITE ACCESS ISSUES:

🔧 ERROR: "Cannot access account.trendmicro.com"
• Clear browser cache and cookies completely
• Try different browser (Chrome, Firefox, Edge)
• Disable browser extensions temporarily
• Check if corporate firewall is blocking access
• Try accessing from different network (mobile hotspot)
• Use incognito/private browsing mode

🔧 ERROR: "Page won't load" or "Connection timeout"
• Check internet connection with other websites
• Flush DNS cache: ipconfig /flushdns (Windows) or sudo dscacheutil -flushcache (Mac)
• Change DNS servers to 8.8.8.8 and 8.8.4.4 (Google DNS)
• Disable VPN if connected
• Try accessing website using IP address instead of domain
• Contact ISP if issues persist across multiple sites

🔧 ERROR: "Login failed" or "Session expired"
• Verify username and password accuracy
• Check Caps Lock and ensure correct keyboard layout
• Clear cookies for trendmicro.com domain
• Disable password manager auto-fill temporarily
• Try password reset if login consistently fails
• Check if account is locked due to multiple failed attempts

🔒 SSL AND SECURITY CERTIFICATE ERRORS:

🔧 ERROR: "Your connection is not private" or SSL Certificate Error
• Check system date and time settings (must be accurate)
• Clear browser SSL state: Settings → Advanced → Clear browsing data
• Add security exception for trendmicro.com if trusted
• Update browser to latest version
• Disable antivirus SSL scanning temporarily
• Try accessing via https:// explicitly

🔧 ERROR: "Certificate has expired" or "Certificate not trusted"
• Update Windows certificates: Windows Update
• Clear certificate cache in browser
• Import Trend Micro root certificates manually
• Check if corporate network has certificate filtering
• Try accessing from personal network instead of corporate

📱 MOBILE APP CONNECTIVITY ISSUES:

🔧 ERROR: Mobile app won't connect or sync
• Check mobile data/WiFi connection
• Force close and restart Trend Micro mobile app
• Clear app cache: Settings → Apps → Trend Micro → Storage → Clear Cache
• Update mobile app to latest version
• Sign out and back into Trend Micro account
• Restart mobile device

🔧 ERROR: "Server unavailable" or "Network error"
• Switch between WiFi and mobile data
• Check if mobile carrier blocks certain connections
• Disable mobile VPN if connected
• Allow Trend Micro through mobile firewall/security apps
• Check mobile date and time settings
• Reinstall mobile app if persistent

🔄 ACCOUNT PORTAL AND WEB INTERFACE ISSUES:

🔧 ERROR: Dashboard not loading or "Internal server error"
• Wait 15-30 minutes and try again (may be temporary server issue)
• Try accessing specific sections directly via bookmarks
• Disable ad blockers and privacy extensions
• Clear all browser data for trendmicro.com
• Try different device or network
• Contact support if error persists over 2 hours

🔧 ERROR: Features missing or "Access denied"
• Verify subscription includes requested features
• Check if account has proper permissions
• Log out completely and log back in
• Clear browser session data
• Try accessing from account owner's login
• Contact billing if features should be available

🛠️ ADVANCED NETWORK TROUBLESHOOTING:

• Network trace: tracert account.trendmicro.com
• DNS lookup test: nslookup account.trendmicro.com
• Port connectivity test: telnet account.trendmicro.com 443
• Disable Windows firewall temporarily for testing
• Check router/modem firewall settings
• Test with ethernet cable instead of WiFi
• Contact network administrator for corporate environments

📞 ESCALATION FOR CONNECTIVITY ISSUES:
• Document specific error messages and codes
• Note time of day when issues occur
• Test from multiple devices and networks
• Collect network diagnostic information
• Contact ISP to verify no service issues
• Report to Trend Micro if widespread connectivity problems'''
        },
        {
            'title': 'Account Portal Access and Login Issues',
            'link': 'https://helpcenter.trendmicro.com/en-us/account-access/',
            'snippet': '''COMPREHENSIVE ACCOUNT PORTAL TROUBLESHOOTING:

🔐 LOGIN AND AUTHENTICATION ISSUES:

🔧 ERROR: "Invalid username or password" or Login Failed
• Verify email address spelling and format
• Check password for correct case sensitivity
• Ensure Caps Lock is OFF and correct keyboard layout
• Try typing password manually (don't copy/paste)
• Clear browser saved passwords and try again
• Use password reset if multiple attempts fail

🔧 ERROR: "Account locked" or "Too many failed attempts"
• Wait 30 minutes before attempting login again
• Use "Forgot Password" to reset and unlock account
• Contact support if lockout persists after reset
• Check for automated login attempts or malware
• Verify account hasn't been compromised

🔧 ERROR: "Account not found" or "Email not recognized"
• Double-check email address spelling
• Try alternative email addresses you may have used
• Check if account was created with phone number instead
• Look for original purchase/activation emails for correct account
• Contact support with proof of purchase if account missing

🔄 PASSWORD RESET AND RECOVERY:

🔧 PASSWORD RESET PROCESS:
1. Visit https://account.trendmicro.com
2. Click "Forgot your password?" link
3. Enter email address associated with account
4. Check email inbox AND spam folder for reset link
5. Click reset link within 24 hours (expires)
6. Create new password meeting requirements
7. Log in with new password immediately

🔧 ERROR: "Password reset email not received"
• Check spam/junk folder thoroughly
• Verify email address spelling when requesting reset
• Wait up to 15 minutes for email delivery
• Add noreply@trendmicro.com to contacts/whitelist
• Try requesting reset from different browser/device
• Contact support if email still not received after 30 minutes

🔧 ERROR: "Reset link expired" or "Invalid reset link"
• Request new password reset (links expire in 24 hours)
• Use link from most recent reset email only
• Don't click link multiple times
• Clear browser cache before clicking reset link
• Try opening link in incognito/private browser window

🌐 ACCOUNT PORTAL NAVIGATION ISSUES:

🔧 ERROR: Dashboard blank or not loading completely
• Clear browser cache and cookies for trendmicro.com
• Disable browser extensions (ad blockers, privacy tools)
• Try different browser (Chrome, Firefox, Edge, Safari)
• Check if JavaScript is enabled in browser settings
• Disable VPN or proxy connections temporarily
• Try accessing from different network

🔧 ERROR: "Session expired" or Frequent logouts
• Enable cookies for trendmicro.com domain
• Clear existing cookies and log in fresh
• Check browser privacy settings aren't too restrictive
• Disable "Clear cookies on exit" browser setting
• Stay active in portal (don't leave idle too long)
• Contact support if sessions expire within minutes

🔧 ERROR: Missing features or "Access denied" messages
• Verify subscription is active and not expired
• Check if account has proper license level for feature
• Log out completely and log back in
• Clear browser session data
• Try accessing feature from main dashboard
• Contact billing to verify subscription includes feature

📱 MOBILE ACCOUNT ACCESS:

🔧 MOBILE BROWSER ISSUES:
• Use mobile browser in desktop mode for full portal
• Clear mobile browser cache and cookies
• Try Trend Micro mobile app instead of browser
• Switch between WiFi and mobile data
• Update mobile browser to latest version
• Use different mobile browser if available

🔧 MOBILE APP ACCOUNT ISSUES:
• Force close and restart Trend Micro mobile app
• Update mobile app to latest version
• Clear app cache and data in device settings
• Sign out and back into account within app
• Reinstall mobile app if persistent issues
• Check mobile device date/time settings

👥 MULTIPLE ACCOUNT ISSUES:

🔧 ERROR: "Multiple accounts found" or Account confusion
• Identify which email was used for original purchase
• Check credit card statements for billing email
• Try all possible email addresses you might have used
• Look for activation emails in old email accounts
• Contact support with proof of purchase to merge accounts
• Use most recent/active account going forward

🔧 FAMILY/SHARED ACCOUNT ACCESS:
• Verify you're using correct family member credentials
• Check if main account holder restricted your access
• Contact primary account holder for permission changes
• Don't share login credentials between family members
• Set up separate accounts if appropriate

🆘 ACCOUNT RECOVERY AND ESCALATION:

📞 WHEN TO CONTACT SUPPORT:
• Account completely inaccessible after all troubleshooting
• Suspicious account activity or potential compromise
• Need to merge multiple accounts with same email
• Billing/subscription shows but can't access features
• Account shows suspended/terminated unexpectedly

📋 INFORMATION TO PROVIDE SUPPORT:
• Email address(es) associated with account
• Approximate account creation date
• Last successful login date/time
• Order number or transaction ID from original purchase
• Last 4 digits of payment method used
• Detailed description of error messages
• Screenshots of error screens if possible

🔒 ACCOUNT SECURITY BEST PRACTICES:
• Use unique, strong password (12+ characters)
• Enable two-factor authentication if available
• Don't share account credentials with others
• Log out when using public/shared computers
• Monitor account activity regularly
• Update password if security breach suspected'''
        },
        {
            'title': 'Account Management and Profile Issues',
            'link': 'https://helpcenter.trendmicro.com/en-us/account-management/',
            'snippet': '''COMPLETE ACCOUNT MANAGEMENT TROUBLESHOOTING:

👤 PROFILE AND PERSONAL INFORMATION:

🔧 ERROR: "Cannot update profile" or Profile changes not saving
• Clear browser cache and cookies completely
• Try updating one field at a time instead of all at once
• Ensure all required fields are filled out correctly
• Check for special characters that might not be accepted
• Use different browser or incognito mode
• Contact support if profile changes critical for service

🔧 ERROR: "Invalid email format" or Email update issues
• Verify new email address is spelled correctly
• Ensure email format includes @ and proper domain
• Check that new email isn't already associated with another account
• Complete email verification process if required
• Use different email provider if format issues persist

🔧 ERROR: "Phone number invalid" or SMS verification problems
• Enter phone number with proper country code format
• Remove dashes, spaces, or special characters
• Verify mobile number can receive SMS messages
• Check if phone number already used on another account
• Try landline number if mobile SMS not working
• Contact support for manual verification if needed

🏠 ADDRESS AND BILLING INFORMATION:

🔧 ERROR: "Billing address mismatch" or Payment failures
• Ensure address exactly matches credit card billing address
• Include apartment/unit numbers in correct fields
• Use same format as on bank/credit card statements
• Verify zip/postal code is correct for country
• Contact bank if address format requirements unclear

🔧 ERROR: "Country/region cannot be changed" or Location restrictions
• Contact support for legitimate country changes (moved residence)
• Some subscription types may be region-locked
• May need to cancel and repurchase if moving countries
• Check if VPN is affecting detected location
• Provide proof of residence change if required

🔐 SECURITY AND PRIVACY SETTINGS:

🔧 TWO-FACTOR AUTHENTICATION ISSUES:
• Verify mobile number can receive SMS codes
• Check if authentication app (Google Authenticator) is synced
• Keep backup codes in secure location
• Contact support immediately if locked out due to 2FA
• Don't disable 2FA unless absolutely necessary

🔧 PRIVACY AND NOTIFICATION SETTINGS:
• Review email notification preferences regularly
• Opt out of marketing emails if desired (won't affect service)
• Check spam folder for important account notifications
• Update communication preferences after email changes
• Set mobile push notification preferences in app

📊 SUBSCRIPTION AND DEVICE MANAGEMENT:

🔧 ERROR: "Device limit exceeded" or Cannot add new device
• Remove old/unused devices from account first
• Check device list for duplicates or renamed devices
• Verify subscription allows additional devices
• Upgrade subscription if more devices needed
• Contact support if device count appears incorrect

🔧 DEVICE MANAGEMENT ISSUES:
• Refresh device list if recently removed devices still showing
• Rename devices with clear, identifiable names
• Remove devices before selling/disposing of hardware
• Transfer licenses between devices if moving to new computer
• Check device status and last sync times regularly

💳 PAYMENT METHOD AND BILLING:

🔧 ERROR: "Payment method declined" or Billing failures
• Verify credit card hasn't expired
• Check available credit limit/account balance
• Ensure billing address matches card exactly
• Try different payment method if primary fails
• Contact bank about international transaction blocks
• Update payment method before auto-renewal date

🔧 RECURRING BILLING MANAGEMENT:
• Review auto-renewal settings before each billing cycle
• Update payment methods proactively before expiration
• Set calendar reminders for subscription renewals
• Monitor credit card statements for Trend Micro charges
• Contact billing support for payment disputes immediately

👨‍👩‍👧‍👦 FAMILY AND SHARED ACCOUNTS:

🔧 FAMILY ACCOUNT SETUP AND MANAGEMENT:
• Designate primary account holder for billing/administration
• Set up individual profiles for each family member
• Configure appropriate permissions for child accounts
• Review family sharing settings and restrictions
• Monitor usage across all family devices regularly

🔧 SHARED ACCOUNT ACCESS ISSUES:
• Don't share login credentials between users
• Set up separate sub-accounts if available
• Use family sharing features instead of credential sharing
• Contact support for guidance on multi-user setups
• Consider individual accounts for business/professional use

🔄 ACCOUNT TRANSFER AND MIGRATION:

🔧 TRANSFERRING ACCOUNT TO NEW EMAIL:
• Update email address in account settings first
• Verify new email address access before changing
• Update email in all Trend Micro products/apps
• Check that old email won't be reused by others
• Keep record of account transfer date/confirmation

🔧 ACCOUNT CLOSURE AND DATA EXPORT:
• Export important data before closing account
• Download password manager data and security reports
• Cancel recurring billing before account closure
• Contact support for complete account deletion
• Allow 30-90 days for complete data removal from systems

🆘 ESCALATION AND ADVANCED SUPPORT:

📞 WHEN TO CONTACT ACCOUNT SUPPORT:
• Critical account access issues affecting service
• Billing disputes or unauthorized charges
• Account compromise or security concerns
• Complex family/business account configurations
• Account transfer between users/organizations

📋 ACCOUNT SUPPORT CONTACT INFORMATION:
• General Account Support: 1-888-762-8736
• Billing Support: 1-855-891-0011
• Live Chat: Available through account portal
• Email Support: accountsupport@trendmicro.com
• Business/Enterprise: Contact dedicated business support team'''
        },
        {
            'title': 'Resolution Guard - Case Closure Quality Control',
            'link': 'https://helpcenter.trendmicro.com/en-us/resolution-guard/',
            'snippet': '''COMPREHENSIVE RESOLUTION GUARD FRAMEWORK:

✅ CASE CLOSURE READINESS ASSESSMENT:

🎯 RESOLUTION CONFIDENCE SCORING (0-100):
• 90-100: HIGH CONFIDENCE - Safe to close
  - Customer explicitly confirms satisfaction
  - All requested actions completed successfully
  - No follow-up questions or concerns raised
  - Clear understanding demonstrated by customer

• 70-89: MEDIUM CONFIDENCE - Requires verification
  - Solution provided but no clear confirmation from customer
  - Customer responded positively but not explicitly satisfied
  - Minor follow-up items may exist
  - Consider proactive follow-up before closure

• 0-69: LOW CONFIDENCE - DO NOT CLOSE
  - Customer has not confirmed resolution
  - Additional questions or concerns raised
  - Solution only partially implemented
  - Customer expressed confusion or frustration

📋 MANDATORY PRE-CLOSURE CHECKLIST:

☑️ CUSTOMER CONFIRMATION REQUIREMENTS:
• Customer explicitly states issue is resolved
• Customer confirms they can successfully perform the action
• Customer indicates no additional assistance needed
• Customer expresses satisfaction with support provided

☑️ TECHNICAL VALIDATION REQUIREMENTS:
• All troubleshooting steps completed successfully
• Customer confirmed successful testing of solution
• No error messages or technical issues remain
• Follow-up verification completed where applicable

☑️ DOCUMENTATION REQUIREMENTS:
• Complete record of troubleshooting steps taken
• Customer responses and confirmations documented
• Final resolution clearly documented for future reference
• Any escalation paths or alternative solutions noted

🚫 PREMATURE CLOSURE PREVENTION:

⚠️ RED FLAGS - NEVER CLOSE WHEN:
• Customer says "I'll try this later" without confirming success
• Customer stops responding mid-conversation
• Multiple solutions provided but none confirmed working
• Customer asks follow-up questions about the solution
• Technical error messages still present
• Customer expresses frustration or dissatisfaction

⚠️ YELLOW FLAGS - VERIFY BEFORE CLOSING:
• Customer says "okay" or "thanks" without specific confirmation
• Solution provided recently without time for testing
• Complex multi-step solution may need verification
• Previous similar cases required follow-up
• Customer is new to technology or product

✅ GREEN SIGNALS - SAFE TO CLOSE:
• "Yes, that fixed it completely"
• "Everything is working perfectly now"
• "Thank you, my issue is resolved"
• "I can now [specific action] without problems"
• Customer demonstrates successful completion

🔄 FOLLOW-UP AND QUALITY ASSURANCE:

📞 PROACTIVE FOLLOW-UP SCENARIOS:
• Complex technical solutions (follow up in 24-48 hours)
• Installation or configuration changes (verify after 1 week)
• Account or billing changes (confirm next billing cycle)
• Security-related fixes (ensure continued protection)
• First-time customers (extra verification for satisfaction)

📊 RESOLUTION QUALITY METRICS:
• Customer satisfaction score confirmation
• Time to resolution tracking
• First contact resolution rate
• Escalation avoidance rate
• Follow-up requirement analysis

💬 CUSTOMER COMMUNICATION BEST PRACTICES:

🎯 CONFIRMATION QUESTIONS TO ASK:
• "Can you confirm that [specific issue] is now working correctly?"
• "Are you able to [specific action] without any errors?"
• "Is there anything else I can help you with regarding this issue?"
• "How would you rate your satisfaction with this resolution?"
• "Do you feel confident using [solution] going forward?"

📝 CLOSURE COMMUNICATION TEMPLATE:
"Before I close this case, I want to confirm:
1. Your [specific issue] has been resolved
2. You can successfully [specific action]
3. You have no additional questions
4. You're satisfied with the support provided

Please confirm each point so I can properly close your case with confidence."

🔧 CASE REOPENING PROCEDURES:

⏰ AUTOMATIC REOPENING TRIGGERS:
• Customer contacts within 48 hours with same issue
• Related error reports detected within 1 week
• Solution verification fails during follow-up
• Customer satisfaction score below threshold

📋 REOPENING REQUIREMENTS:
• Reference original case number and solution provided
• Document what aspect of solution failed or was incomplete
• Identify if issue is continuation or new related problem
• Assign appropriate priority based on business impact

🆘 ESCALATION CRITERIA:

🔺 IMMEDIATE ESCALATION REQUIRED:
• Customer explicitly requests manager/supervisor
• Resolution attempts exceed 3 different approaches
• Technical issue beyond current knowledge/tools
• Customer reports urgent business impact
• Potential security or compliance concerns

📈 QUALITY IMPROVEMENT PROCESS:
• Analyze patterns in premature closures
• Identify training needs for support staff
• Update knowledge base based on resolution gaps
• Monitor customer feedback and satisfaction trends
• Implement process improvements based on metrics'''
        },
        {
            'title': 'Case Closure Confidence Analysis',
            'link': 'https://helpcenter.trendmicro.com/en-us/case-closure-confidence/',
            'snippet': '''ADVANCED CASE CLOSURE CONFIDENCE ASSESSMENT:

🧠 AI-POWERED CONFIDENCE ANALYSIS:

📊 CONVERSATION ANALYSIS FACTORS:
• Customer language sentiment and tone progression
• Frequency and nature of follow-up questions
• Explicit confirmation vs. implicit acceptance
• Time elapsed between solution and response
• Customer expertise level and technical understanding

🔍 CONFIDENCE INDICATORS BY CATEGORY:

💚 HIGH CONFIDENCE INDICATORS (Score: 85-100):
• "Perfect! That solved everything."
• "It's working exactly as expected now."
• "Thank you so much, you've been incredibly helpful."
• Customer provides detailed confirmation of successful testing
• Customer asks about unrelated topics (indicates current issue resolved)

🟡 MEDIUM CONFIDENCE INDICATORS (Score: 60-84):
• "Okay, I'll try that."
• "That seems to have worked."
• "I think that fixed it."
• Brief acknowledgment without detailed confirmation
• Customer responds quickly without testing time

🔴 LOW CONFIDENCE INDICATORS (Score: 0-59):
• "I'll let you know if it doesn't work."
• "I'm still not sure what happened."
• "What if this happens again?"
• Customer asking clarifying questions about the solution
• Silence after solution provided

📈 RESOLUTION TRAJECTORY ANALYSIS:

⬆️ POSITIVE TRAJECTORY SIGNS:
• Customer frustration decreasing over time
• Questions becoming more specific and actionable
• Customer showing understanding of solution steps
• Positive language increasing in recent messages
• Customer taking ownership of solution implementation

⬇️ NEGATIVE TRAJECTORY SIGNS:
• Customer frustration maintaining or increasing
• Repeated questions about same concepts
• Customer expressing doubt about solution viability
• Negative language persisting in conversation
• Customer delegating to others instead of implementing

🎯 CONTEXTUAL CONFIDENCE MODIFIERS:

📞 COMMUNICATION CHANNEL FACTORS:
• Phone: Higher confidence due to real-time verification
• Chat: Medium confidence, good for quick confirmations
• Email: Lower baseline confidence, requires explicit confirmation
• Self-service: Lowest confidence, needs follow-up verification

⏰ TIMING FACTORS:
• Immediate response to solution: Lower confidence (insufficient testing time)
• 15-30 minutes after solution: Optimal confidence window
• Hours later: Higher confidence if positive
• Days later: Highest confidence for complex solutions

👤 CUSTOMER TYPE MODIFIERS:
• Technical users: Higher confidence with technical confirmations
• Business users: Medium confidence, need practical confirmations
• Home users: Lower baseline, need simple language confirmations
• First-time users: Lowest baseline, require extra verification

🔄 DYNAMIC CONFIDENCE SCORING:

📋 REAL-TIME ASSESSMENT ALGORITHM:
1. Baseline confidence: 50 points
2. Add/subtract based on customer language sentiment
3. Modify based on solution complexity and customer expertise
4. Adjust for communication channel and timing
5. Factor in conversation trajectory and resolution pattern

⚡ CONFIDENCE SCORE TRIGGERS:
• Score 85+: Approve for closure with standard follow-up
• Score 70-84: Require additional confirmation before closure
• Score 55-69: Mandatory verification call/email before closure
• Score <55: Do not close, continue troubleshooting or escalate

🛡️ QUALITY SAFEGUARDS:

🔒 AUTOMATED CLOSURE PREVENTION:
• Block closure if confidence score below threshold
• Require supervisor override for low-confidence closures
• Flag cases with declining confidence trajectories
• Alert for unusual closure patterns or timing

📊 CONFIDENCE CALIBRATION:
• Regular review of confidence scores vs. actual outcomes
• Adjustment of scoring algorithms based on reopening rates
• Training data improvement from successful resolutions
• Feedback loop integration from customer satisfaction surveys

🎖️ BEST PRACTICES FOR HIGH-CONFIDENCE CLOSURES:

✅ PROACTIVE VERIFICATION TECHNIQUES:
• Ask specific action-based confirmation questions
• Request customer to demonstrate solution working
• Provide clear success criteria for customer to verify
• Offer specific timeframe for testing before closure
• Set expectations for follow-up communication

📝 DOCUMENTATION EXCELLENCE:
• Record exact customer confirmation language
• Document all verification steps completed
• Note any remaining concerns or follow-up items
• Include confidence score rationale in case notes
• Prepare handoff information for potential reopening

🔮 PREDICTIVE CLOSURE SUCCESS:
• Historical pattern analysis for similar issues
• Customer behavior profiling for closure preferences
• Solution complexity correlation with success rates
• Follow-up requirement prediction based on case characteristics'''
        }
    ]

# =============================
# Core SentriGuide AI Functions
# =============================
def update_conversation_summary():
    """Challenge 1: Context Management - Summarize long conversations"""
    global conversation_summary, is_processing

    if is_processing or len(conversation_history) < 2:
        return

    is_processing = True
    update_status("Analyzing conversation context...")

    try:
        # Simple rule-based analysis
        total_messages = len(conversation_history)
        customer_messages = [msg for msg in conversation_history if msg['role'] == 'customer']
        engineer_messages = [msg for msg in conversation_history if msg['role'] == 'engineer']

        # Identify main issue from first customer message
        main_issue = "General inquiry"
        if customer_messages:
            first_msg = customer_messages[0]['content'].lower()
            if any(word in first_msg for word in ['virus', 'malware', 'infected']):
                main_issue = "Malware/Virus concern"
            elif any(word in first_msg for word in ['slow', 'performance', 'speed']):
                main_issue = "Performance issue"
            elif any(word in first_msg for word in ['email', 'spam', 'phishing']):
                main_issue = "Email security"
            elif any(word in first_msg for word in ['update', 'install', 'download']):
                main_issue = "Software update/installation"

        # Determine conversation state
        if total_messages > 6:
            state = "Extended conversation - consider escalation"
        elif total_messages > 3:
            state = "Active troubleshooting"
        else:
            state = "Initial contact phase"

        conversation_summary = f"""CONVERSATION SUMMARY:

MAIN ISSUE: {main_issue}
TOTAL MESSAGES: {total_messages} ({len(customer_messages)} customer, {len(engineer_messages)} engineer)
CURRENT STATE: {state}

CUSTOMER PROFILE:
• Communication: {'Detailed' if len(customer_messages) > 0 and len(customer_messages[0]['content']) > 100 else 'Concise'}
• Latest concern: {customer_messages[-1]['content'][:100] if customer_messages else 'None'}...

PROGRESS NOTES:
• Conversation started with: {main_issue}
• Engineer responses provided: {len(engineer_messages)}
• Latest interaction: {conversation_history[-1]['timestamp'] if conversation_history else 'N/A'}

CONTEXT NOTES:
• Monitor for resolution confirmation
• Track customer satisfaction indicators
• Consider escalation if conversation exceeds 8 messages
"""

        update_context_panel()
        update_status("Context updated")

    except Exception as e:
        conversation_summary = f"Summary error: {str(e)}"
        update_status("Context analysis failed")
    finally:
        is_processing = False

def analyze_sentiment_and_tone():
    """Challenge 2: Emotional Alignment - Analyze customer sentiment and suggest tone"""
    global customer_sentiment, is_processing

    if not conversation_history or is_processing:
        return

    latest_customer_msg = ""
    for msg in reversed(conversation_history):
        if msg["role"] == "customer":
            latest_customer_msg = msg["content"]
            break

    if not latest_customer_msg:
        return

    is_processing = True
    update_status("Analyzing customer emotion...")

    try:
        # Enhanced sentiment analysis with contextual patterns
        msg_lower = latest_customer_msg.lower()

        # Emotion detection with weighted scoring
        frustrated_patterns = [
            ('this is ridiculous', 3), ('this is stupid', 3), ('this is terrible', 3),
            ('not working', 2), ('still not', 2), ('keep getting', 2), ('tried everything', 2),
            ('waste of time', 3), ('sick of this', 3), ('fed up', 3), ('had enough', 3),
            ('frustrated', 2), ('annoying', 2), ('horrible', 2), ('awful', 2), ('terrible', 2),
            ('angry', 2), ('mad', 2), ('upset', 2), ('irritated', 2), ('furious', 3),
            ('useless', 2), ('broken', 2), ('garbage', 3), ('worst', 2), ('hate', 3)
        ]

        satisfied_patterns = [
            ('thank you', 2), ('thanks', 2), ('appreciate', 2), ('helpful', 2), ('great', 2),
            ('excellent', 2), ('perfect', 2), ('amazing', 2), ('wonderful', 2), ('fantastic', 2),
            ('works perfectly', 3), ('fixed it', 2), ('solved', 2), ('resolved', 2),
            ('good', 1), ('better', 1), ('working now', 2), ('that worked', 2),
            ('happy', 2), ('pleased', 2), ('satisfied', 2), ('love', 2)
        ]

        urgent_patterns = [
            ('urgent', 2), ('emergency', 3), ('critical', 2), ('asap', 2), ('immediately', 2),
            ('right now', 2), ('can\'t wait', 2), ('need help now', 3), ('broken down', 2),
            ('not working at all', 3), ('completely broken', 3), ('dead', 2), ('crashed', 2),
            ('lost everything', 3), ('virus', 2), ('hacked', 3), ('breach', 3), ('compromised', 3)
        ]

        confused_patterns = [
            ('don\'t understand', 2), ('confused', 2), ('unclear', 2), ('what does', 1),
            ('how do i', 1), ('what is', 1), ('explain', 1), ('not sure', 1), ('help me understand', 2),
            ('i don\'t know', 2), ('what\'s the difference', 1), ('which one', 1), ('where do i', 1),
            ('step by step', 1), ('walk me through', 2), ('show me how', 2)
        ]

        worried_patterns = [
            ('worried', 2), ('concerned', 2), ('afraid', 2), ('scared', 2), ('nervous', 2),
            ('what if', 1), ('might happen', 1), ('could this', 1), ('is this normal', 1),
            ('should i be', 1), ('is it safe', 2), ('will i lose', 2), ('am i protected', 2)
        ]

        impatient_patterns = [
            ('how long', 1), ('still waiting', 2), ('been hours', 2), ('taking forever', 2),
            ('when will', 1), ('how much longer', 2), ('this is slow', 2), ('hurry up', 3),
            ('speed this up', 2), ('taking too long', 2), ('why so slow', 2)
        ]

        # Calculate weighted sentiment scores
        sentiment_score = 0
        emotion_scores = {
            'frustrated': 0,
            'satisfied': 0,
            'urgent': 0,
            'confused': 0,
            'worried': 0,
            'impatient': 0
        }

        # Check for patterns and calculate scores
        for pattern, weight in frustrated_patterns:
            if pattern in msg_lower:
                emotion_scores['frustrated'] += weight
                sentiment_score -= weight

        for pattern, weight in satisfied_patterns:
            if pattern in msg_lower:
                emotion_scores['satisfied'] += weight
                sentiment_score += weight

        for pattern, weight in urgent_patterns:
            if pattern in msg_lower:
                emotion_scores['urgent'] += weight

        for pattern, weight in confused_patterns:
            if pattern in msg_lower:
                emotion_scores['confused'] += weight

        for pattern, weight in worried_patterns:
            if pattern in msg_lower:
                emotion_scores['worried'] += weight

        for pattern, weight in impatient_patterns:
            if pattern in msg_lower:
                emotion_scores['impatient'] += weight
                sentiment_score -= 1  # Impatience is slightly negative

        # Determine primary emotion based on highest score
        max_emotion = max(emotion_scores, key=emotion_scores.get)
        max_score = emotion_scores[max_emotion]

        if max_score >= 2:
            emotion = max_emotion
        elif sentiment_score >= 2:
            emotion = "satisfied"
        elif sentiment_score <= -2:
            emotion = "frustrated"
        else:
            emotion = "neutral"

        # Special case: if urgent score is high, prioritize urgency
        if emotion_scores['urgent'] >= 2:
            emotion = "urgent"

        # Enhanced urgency detection
        urgency_score = emotion_scores['urgent']

        # Additional urgency indicators
        high_urgency_phrases = ['asap', 'emergency', 'critical', 'immediately', 'right now', 'urgent', 'can\'t wait', 'need help now']
        medium_urgency_phrases = ['soon', 'quickly', 'when will', 'how long', 'need this fixed', 'time sensitive']

        for phrase in high_urgency_phrases:
            if phrase in msg_lower:
                urgency_score += 2

        for phrase in medium_urgency_phrases:
            if phrase in msg_lower:
                urgency_score += 1

        # Check for business/work context that increases urgency
        if any(word in msg_lower for word in ['work', 'business', 'office', 'meeting', 'deadline', 'presentation']):
            urgency_score += 1

        # Determine final urgency level
        if urgency_score >= 3 or emotion == "urgent":
            urgency = "high"
        elif urgency_score >= 1 or any(word in msg_lower for word in ['when', 'time', 'soon', 'quick']):
            urgency = "medium"
        else:
            urgency = "low"

        # Calculate satisfaction score with better logic
        if emotion == "satisfied":
            satisfaction = max(75, min(95, 85 + (sentiment_score * 5)))
        elif emotion == "frustrated":
            satisfaction = max(5, min(40, 25 + (sentiment_score * 10)))
        elif emotion == "urgent":
            satisfaction = max(30, min(60, 45 + (sentiment_score * 5)))
        elif emotion == "worried":
            satisfaction = max(20, min(50, 35 + (sentiment_score * 8)))
        elif emotion == "confused":
            satisfaction = max(40, min(70, 55 + (sentiment_score * 5)))
        elif emotion == "impatient":
            satisfaction = max(15, min(45, 30 + (sentiment_score * 8)))
        else:
            satisfaction = max(50, min(80, 65 + (sentiment_score * 10)))

        # Enhanced tone recommendations based on detected emotion
        if emotion == "frustrated":
            tone_rec = "🚨 EMPATHETIC & SOLUTION-FOCUSED: Acknowledge frustration immediately, apologize for the inconvenience, focus on quick resolution"
            empathy = "Say: 'I understand this is frustrating. Let me help resolve this right away.' Validate their experience and show urgency to help"
            approach = "Immediate acknowledgment → Quick apology → Direct solution → Follow-up confirmation"
        elif emotion == "urgent":
            tone_rec = "⚡ DIRECT & EFFICIENT: Skip pleasantries, get straight to solutions, provide clear timelines"
            empathy = "Say: 'I see this is urgent. Let me address this immediately.' Prioritize speed and efficiency over detailed explanations"
            approach = "Immediate action → Clear steps → Timeline expectations → Escalation path if needed"
        elif emotion == "confused":
            tone_rec = "📚 PATIENT & EDUCATIONAL: Use simple language, break down steps, check understanding frequently"
            empathy = "Say: 'Let me walk you through this step-by-step.' Use analogies and confirm understanding at each step"
            approach = "Simple explanation → Step-by-step guidance → Comprehension checks → Alternative explanations if needed"
        elif emotion == "worried":
            tone_rec = "🛡️ REASSURING & INFORMATIVE: Provide reassurance about security, explain safety measures clearly"
            empathy = "Say: 'I understand your concern. Let me explain what's happening and how we'll protect you.' Focus on safety and prevention"
            approach = "Address concerns → Explain safety measures → Provide reassurance → Preventive guidance"
        elif emotion == "satisfied":
            tone_rec = "✅ PROFESSIONAL & THOROUGH: Maintain current positive momentum, ensure nothing is missed"
            empathy = "Say: 'I'm glad that helped! Is there anything else I can assist you with?' Reinforce positive experience"
            approach = "Acknowledge success → Complete any remaining items → Offer additional help → Positive closure"
        elif emotion == "impatient":
            tone_rec = "⏰ EFFICIENT & RESPONSIVE: Move quickly through solutions, provide specific timelines"
            empathy = "Say: 'I'll get this resolved quickly for you.' Focus on speed and provide time estimates for each step"
            approach = "Quick acknowledgment → Fast-track solution → Time estimates → Efficient execution"
        else:
            tone_rec = "🤝 STANDARD PROFESSIONAL: Be helpful, informative, and maintain friendly demeanor"
            empathy = "Maintain standard professional courtesy while being thorough and helpful"
            approach = "Professional greeting → Understand issue → Provide solution → Confirm satisfaction"

        # Generate detailed analysis
        detected_patterns = []
        for pattern, weight in frustrated_patterns + satisfied_patterns + urgent_patterns + confused_patterns + worried_patterns + impatient_patterns:
            if pattern in msg_lower:
                detected_patterns.append(f"'{pattern}' (weight: {weight})")

        analysis = f"""🧠 ENHANCED SENTIMENT ANALYSIS:

😊 EMOTION DETECTED: {emotion.upper()}
⚡ URGENCY LEVEL: {urgency.upper()}
📊 SATISFACTION ESTIMATE: {satisfaction}%
🎯 CONFIDENCE: {max_score}/5 (detection strength)

{tone_rec}

💬 EMPATHY APPROACH:
{empathy}

🔄 RESPONSE WORKFLOW:
{approach}

📋 CONVERSATION CONTEXT:
• Message length: {'Detailed communication' if len(latest_customer_msg) > 100 else 'Concise message'}
• Technical level: {'High-tech user' if any(word in msg_lower for word in ['log', 'error', 'code', 'configuration', 'registry', 'firewall']) else 'General user'}
• Communication style: {'Formal' if any(word in msg_lower for word in ['please', 'kindly', 'would you']) else 'Casual'}
• Response priority: {urgency.upper()}

🔍 DETECTED INDICATORS:
{', '.join(detected_patterns[:5]) if detected_patterns else 'Standard neutral language patterns'}

💡 KEY RECOMMENDATION:
{approach.split(' → ')[0]} - {empathy.split('.')[0]}"""

        customer_sentiment.update({
            "emotion": emotion,
            "urgency": urgency,
            "satisfaction": satisfaction,
            "analysis": analysis
        })

        update_sentiment_panel()
        update_status("Emotion analysis complete")

    except Exception as e:
        customer_sentiment["analysis"] = f"Sentiment analysis error: {str(e)}"
        update_status("Emotion analysis failed")
    finally:
        is_processing = False

def calculate_resolution_confidence():
    """Challenge 3: Premature Resolution Prevention - Score resolution confidence"""
    global resolution_confidence, is_processing, resolution_analysis

    if not conversation_history or is_processing:
        return

    is_processing = True
    update_status("Calculating resolution confidence...")

    try:
        conv_text = ""
        for msg in conversation_history[-6:]:  # Last 6 messages
            role = "CUSTOMER" if msg["role"] == "customer" else "ENGINEER"
            conv_text += f"{role}: {msg['content']}\n"

        response = anthropic_client.messages.create(
            model=ANTHROPIC_MODEL,
            max_tokens=300,
            messages=[{
                "role": "user",
                "content": f"""Analyze this support conversation and determine if the issue is truly resolved. Prevent premature case closure.

RECENT CONVERSATION:
{conv_text}

CUSTOMER SENTIMENT: {customer_sentiment.get('emotion', 'unknown')}

Evaluate these factors:
1. Has the root cause been identified and addressed?
2. Has the customer confirmed the solution works?
3. Are there any remaining concerns or questions?
4. Is the customer satisfied with the resolution?
5. Are there potential follow-up issues?

Provide:
CONFIDENCE_SCORE: [0-100] (100 = definitely resolved, 0 = not resolved)
RESOLUTION_STATUS: [RESOLVED/PARTIALLY_RESOLVED/NOT_RESOLVED/NEEDS_FOLLOW_UP]
RISK_FACTORS: [What could cause this to be a repeat contact]
RECOMMENDATION: [Should case be closed or what needs to happen first]"""
            }]
        )

        analysis = response.content[0].text

        # Extract confidence score
        lines = analysis.split('\n')
        for line in lines:
            if 'CONFIDENCE_SCORE:' in line:
                try:
                    score = int(''.join(filter(str.isdigit, line)))
                    resolution_confidence = score
                    break
                except:
                    resolution_confidence = 50

        resolution_analysis = analysis
        update_confidence_panel()
        update_status("Resolution confidence calculated")

    except Exception as e:
        resolution_analysis = f"Confidence calculation error: {str(e)}"
        resolution_confidence = 50
        update_status("Confidence calculation failed")
    finally:
        is_processing = False

def get_solution_bullets(url, title):
    """Extract and format solution as simplified bullet points"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')

            bullets = []

            # Try multiple methods to extract content
            # Method 1: Look for ordered/unordered lists
            for ul_ol in soup.find_all(['ol', 'ul']):
                for li in ul_ol.find_all('li'):
                    text = li.get_text().strip()
                    if text and 10 < len(text) < 200:
                        text = re.sub(r'^[\d\.\)\-\s]+', '', text)
                        text = re.sub(r'\s+', ' ', text)
                        bullets.append(text)

            # Method 2: Look for step-by-step content
            if not bullets:
                for element in soup.find_all(['div', 'section', 'article']):
                    if any(keyword in str(element.get('class', [])).lower() for keyword in ['step', 'procedure', 'instruction']):
                        for item in element.find_all(['p', 'div']):
                            text = item.get_text().strip()
                            if 15 < len(text) < 200 and ('step' in text.lower() or any(word in text.lower() for word in ['click', 'open', 'select', 'install', 'download'])):
                                text = re.sub(r'^[\d\.\)\-\s]+', '', text)
                                bullets.append(text)

            # Method 3: Extract from paragraphs if still no content
            if not bullets:
                paragraphs = soup.find_all('p')
                for p in paragraphs[:8]:
                    text = p.get_text().strip()
                    if 20 < len(text) < 300:
                        # Split into sentences and take meaningful ones
                        sentences = [s.strip() for s in text.split('.') if s.strip()]
                        for sentence in sentences[:2]:
                            if len(sentence) > 15 and any(action in sentence.lower() for action in ['click', 'open', 'go to', 'select', 'install', 'download', 'update', 'scan', 'check']):
                                bullets.append(sentence)

            return bullets[:6] if bullets else []

    except Exception as e:
        print(f"Error fetching solution bullets: {str(e)}")

    return []

def get_default_solution_bullets(title, query=""):
    """Provide default solution bullets based on title and query when web scraping fails"""
    title_lower = title.lower()

    if 'renew' in title_lower:
        return [
            "Visit the Trend Micro customer portal and log into your account",
            "Navigate to 'My Account' and select 'Subscriptions'",
            "Click 'Renew' next to your expiring product",
            "Choose renewal period and complete payment",
            "Download and enter new activation code in your product"
        ]
    elif 'install' in title_lower or 'activation' in title_lower:
        return [
            "Download installer from official Trend Micro website",
            "Run installer as administrator with antivirus temporarily disabled",
            "Follow setup wizard and enter activation code when prompted",
            "Configure initial protection settings and exclusions",
            "Restart computer and verify protection is active"
        ]
    elif 'troubleshoot' in title_lower or 'problem' in title_lower:
        return [
            "Check if Trend Micro services are running in Task Manager",
            "Update to latest version and restart the application",
            "Run Trend Micro diagnostic tool to identify issues",
            "Temporarily disable conflicting security software",
            "Contact support if issue persists with diagnostic logs"
        ]
    elif 'quarantine' in title_lower:
        return [
            "Open Trend Micro main console and go to quarantine section",
            "Review quarantined files and verify if they are false positives",
            "Restore legitimate files or delete confirmed threats",
            "Add restored files to exclusion list if needed",
            "Update virus definitions to prevent future false positives"
        ]
    elif 'protection' in title_lower or 'real-time' in title_lower:
        return [
            "Open Trend Micro main console and go to settings",
            "Navigate to real-time protection configuration",
            "Enable all protection modules including web and email",
            "Configure scan sensitivity and exclusions as needed",
            "Test protection by downloading EICAR test file"
        ]
    else:
        # Generic solution based on common issues
        return [
            "Open Trend Micro main console from system tray",
            "Check product status and update if available",
            "Run quick scan to ensure system is protected",
            "Review settings and adjust as needed",
            "Contact Trend Micro support for specific assistance"
        ]

def analyze_coaching_performance():
    """Challenge 5: Performance Coaching - Analyze engineer performance and provide coaching"""
    global coaching_feedback, performance_metrics, is_processing

    if not conversation_history or is_processing:
        return

    is_processing = True
    update_status("Analyzing performance metrics...")

    try:
        # Get recent engineer responses for analysis
        engineer_messages = [msg for msg in conversation_history if msg['role'] == 'engineer']
        customer_messages = [msg for msg in conversation_history if msg['role'] == 'customer']

        if not engineer_messages:
            return

        latest_engineer_msg = engineer_messages[-1]['content'] if engineer_messages else ""
        latest_customer_msg = customer_messages[-1]['content'] if customer_messages else ""

        # Analyze response time (simulated based on conversation flow)
        response_time_score = "excellent"
        if len(conversation_history) > 8:
            response_time_score = "needs_improvement"
        elif len(conversation_history) > 5:
            response_time_score = "good"

        # Analyze empathy level based on engineer responses
        empathy_score = analyze_empathy_level(latest_engineer_msg, customer_sentiment.get('emotion', 'neutral'))

        # Analyze technical accuracy based on content
        technical_score = analyze_technical_accuracy(latest_engineer_msg)

        # Analyze communication clarity
        clarity_score = analyze_communication_clarity(latest_engineer_msg)

        # Analyze session progress
        progress_score = analyze_session_progress()

        # Update performance metrics
        performance_metrics.update({
            "response_time": response_time_score,
            "empathy_level": empathy_score,
            "technical_accuracy": technical_score,
            "communication_clarity": clarity_score,
            "session_progress": progress_score
        })

        # Generate coaching feedback
        coaching_feedback = generate_coaching_feedback()

        update_coaching_panel()
        update_status("Performance analysis complete")

    except Exception as e:
        coaching_feedback = f"Performance analysis error: {str(e)}"
        update_status("Performance analysis failed")
    finally:
        is_processing = False

def analyze_empathy_level(engineer_msg, customer_emotion):
    """Analyze empathy level in engineer's response"""
    msg_lower = engineer_msg.lower()

    # Check for empathy indicators
    empathy_phrases = [
        "i understand", "i can see", "that must be", "i'm sorry", "i apologize",
        "frustrating", "concerning", "i hear you", "absolutely", "definitely",
        "let me help", "i'll take care", "no worries", "completely understand"
    ]

    empathy_count = sum(1 for phrase in empathy_phrases if phrase in msg_lower)

    # Adjust based on customer emotion
    if customer_emotion in ['frustrated', 'urgent', 'worried']:
        if empathy_count >= 2:
            return "excellent"
        elif empathy_count >= 1:
            return "good"
        else:
            return "needs_improvement"
    else:
        if empathy_count >= 1:
            return "excellent"
        elif len(engineer_msg) > 50:
            return "good"
        else:
            return "needs_improvement"

def analyze_technical_accuracy(engineer_msg):
    """Analyze technical accuracy of the response"""
    msg_lower = engineer_msg.lower()

    # Check for technical terms and accuracy indicators
    technical_terms = [
        "trend micro", "antivirus", "security", "scan", "quarantine", "firewall",
        "real-time", "protection", "malware", "virus", "update", "activation",
        "subscription", "license", "account", "portal", "installation", "configuration"
    ]

    accuracy_indicators = [
        "step by step", "first", "then", "next", "finally", "follow these",
        "navigate to", "click on", "select", "install", "download", "configure"
    ]

    technical_count = sum(1 for term in technical_terms if term in msg_lower)
    accuracy_count = sum(1 for indicator in accuracy_indicators if indicator in msg_lower)

    if technical_count >= 3 and accuracy_count >= 2:
        return "excellent"
    elif technical_count >= 2 or accuracy_count >= 1:
        return "good"
    elif technical_count >= 1:
        return "needs_improvement"
    else:
        return "poor"

def analyze_communication_clarity(engineer_msg):
    """Analyze clarity of communication"""
    if len(engineer_msg) < 20:
        return "poor"

    # Check for clarity indicators
    clarity_indicators = [
        "let me", "here's how", "you can", "simply", "just", "easy",
        "step 1", "step 2", "first", "second", "then", "next", "finally"
    ]

    # Check for jargon overuse
    jargon_terms = [
        "configuration", "implementation", "infrastructure", "methodology",
        "optimization", "parameters", "specifications", "protocols"
    ]

    msg_lower = engineer_msg.lower()
    clarity_count = sum(1 for indicator in clarity_indicators if indicator in msg_lower)
    jargon_count = sum(1 for term in jargon_terms if term in msg_lower)

    # Calculate score
    if clarity_count >= 2 and jargon_count <= 1:
        return "excellent"
    elif clarity_count >= 1 and jargon_count <= 2:
        return "good"
    elif jargon_count <= 3:
        return "needs_improvement"
    else:
        return "poor"

def analyze_session_progress():
    """Analyze overall session progress"""
    total_messages = len(conversation_history)
    engineer_messages = [msg for msg in conversation_history if msg['role'] == 'engineer']
    customer_messages = [msg for msg in conversation_history if msg['role'] == 'customer']

    # Simple progress analysis
    if resolution_confidence >= 80:
        return "excellent"
    elif resolution_confidence >= 60:
        return "good"
    elif total_messages <= 4:
        return "on_track"
    elif total_messages <= 8:
        return "needs_improvement"
    else:
        return "poor"

def generate_coaching_feedback():
    """Generate comprehensive coaching feedback"""
    metrics = performance_metrics

    feedback = "🎯 PERFORMANCE COACHING ANALYSIS\n\n"

    # Overall Performance Summary
    scores = list(metrics.values())
    excellent_count = scores.count("excellent")
    good_count = scores.count("good")
    needs_improvement_count = scores.count("needs_improvement")
    poor_count = scores.count("poor")

    if excellent_count >= 3:
        overall = "🌟 OUTSTANDING PERFORMANCE"
        overall_tag = "excellent"
    elif excellent_count + good_count >= 3:
        overall = "✅ STRONG PERFORMANCE"
        overall_tag = "good"
    elif needs_improvement_count <= 2:
        overall = "⚠️ ROOM FOR IMPROVEMENT"
        overall_tag = "needs_improvement"
    else:
        overall = "🚨 REQUIRES ATTENTION"
        overall_tag = "poor"

    feedback += f"{overall}\n\n"

    # Detailed Metrics
    feedback += "📊 PERFORMANCE METRICS:\n\n"

    metric_labels = {
        "response_time": "⏱️ Response Time",
        "empathy_level": "💝 Empathy Level",
        "technical_accuracy": "🔧 Technical Accuracy",
        "communication_clarity": "💬 Communication Clarity",
        "session_progress": "📈 Session Progress"
    }

    for metric, score in metrics.items():
        label = metric_labels.get(metric, metric)
        feedback += f"{label}: {score.upper()}\n"

    feedback += "\n"

    # Specific Coaching Tips
    feedback += "💡 COACHING RECOMMENDATIONS:\n\n"

    if metrics["empathy_level"] in ["needs_improvement", "poor"]:
        customer_emotion = customer_sentiment.get('emotion', 'neutral')
        if customer_emotion == 'frustrated':
            feedback += "🔸 EMPATHY: Customer is frustrated. Use phrases like 'I understand this is frustrating' and 'Let me help resolve this quickly'\n"
        elif customer_emotion == 'urgent':
            feedback += "🔸 EMPATHY: Customer has urgent needs. Acknowledge urgency: 'I see this is urgent, let me prioritize this'\n"
        elif customer_emotion == 'worried':
            feedback += "🔸 EMPATHY: Customer is worried. Provide reassurance: 'I understand your concern, let me explain what's happening'\n"
        else:
            feedback += "🔸 EMPATHY: Show more understanding. Use phrases like 'I understand', 'That makes sense', 'I can help with that'\n"

    if metrics["technical_accuracy"] in ["needs_improvement", "poor"]:
        feedback += "🔸 TECHNICAL: Include more specific Trend Micro terminology and step-by-step instructions\n"
        feedback += "🔸 TECHNICAL: Reference specific features like 'Real-time Protection', 'Quarantine Manager', 'Account Portal'\n"

    if metrics["communication_clarity"] in ["needs_improvement", "poor"]:
        feedback += "🔸 CLARITY: Break down complex instructions into numbered steps\n"
        feedback += "🔸 CLARITY: Use simpler language and avoid technical jargon when possible\n"
        feedback += "🔸 CLARITY: Use transition words like 'First', 'Next', 'Then', 'Finally'\n"

    if metrics["session_progress"] in ["needs_improvement", "poor"]:
        feedback += "🔸 PROGRESS: Consider escalating if conversation exceeds 8 messages without resolution\n"
        feedback += "🔸 PROGRESS: Ask specific confirmation questions to verify customer understanding\n"
        feedback += "🔸 PROGRESS: Focus on one issue at a time to avoid confusion\n"

    if metrics["response_time"] in ["needs_improvement", "poor"]:
        feedback += "🔸 EFFICIENCY: Provide quicker responses to maintain customer engagement\n"
        feedback += "🔸 EFFICIENCY: Use SentriGuide's knowledge suggestions to speed up solution finding\n"

    # Best Practices
    feedback += "\n🏆 BEST PRACTICES TO MAINTAIN:\n\n"

    if metrics["empathy_level"] == "excellent":
        feedback += "✅ Excellent empathy - continue acknowledging customer emotions\n"
    if metrics["technical_accuracy"] == "excellent":
        feedback += "✅ Strong technical knowledge - keep using specific Trend Micro terms\n"
    if metrics["communication_clarity"] == "excellent":
        feedback += "✅ Clear communication - maintain structured responses\n"
    if metrics["session_progress"] == "excellent":
        feedback += "✅ Great session management - customer is progressing well\n"

    # Next Steps
    feedback += "\n🎯 IMMEDIATE ACTION ITEMS:\n\n"

    if customer_sentiment.get('emotion') == 'frustrated':
        feedback += "1. Acknowledge frustration and apologize for inconvenience\n"
        feedback += "2. Provide immediate next step to show progress\n"
        feedback += "3. Ask if customer needs anything else urgent\n"
    elif customer_sentiment.get('urgency') == 'high':
        feedback += "1. Prioritize speed over detailed explanations\n"
        feedback += "2. Provide timeline for resolution\n"
        feedback += "3. Offer escalation if needed\n"
    elif resolution_confidence < 60:
        feedback += "1. Gather more information about the specific issue\n"
        feedback += "2. Provide step-by-step troubleshooting\n"
        feedback += "3. Confirm customer can follow instructions\n"
    else:
        feedback += "1. Continue current approach\n"
        feedback += "2. Verify customer satisfaction\n"
        feedback += "3. Prepare for case closure if appropriate\n"

    return feedback

def update_coaching_panel():
    """Update coaching analysis panel"""
    if coaching_panel:
        coaching_panel.config(state=tk.NORMAL)
        coaching_panel.delete(1.0, tk.END)

        if coaching_feedback and conversation_history:
            # Show both real-time metrics and coaching analysis
            real_time_feedback = get_real_time_performance_feedback()

            # Insert real-time metrics first
            real_time_lines = real_time_feedback.split('\n')
            for line in real_time_lines:
                if '✅' in line:
                    coaching_panel.insert(tk.END, line + '\n', "excellent")
                elif '⚠️' in line:
                    coaching_panel.insert(tk.END, line + '\n', "needs_improvement")
                elif '🚨' in line:
                    coaching_panel.insert(tk.END, line + '\n', "poor")
                elif '📈' in line or '😊' in line:
                    coaching_panel.insert(tk.END, line + '\n', "good")
                elif '📉' in line or '😞' in line:
                    coaching_panel.insert(tk.END, line + '\n', "poor")
                elif line.startswith('•'):
                    coaching_panel.insert(tk.END, line + '\n', "metric")
                else:
                    coaching_panel.insert(tk.END, line + '\n', "header")

            coaching_panel.insert(tk.END, "\n" + "="*60 + "\n\n", "header")

            # Then show coaching analysis
            lines = coaching_feedback.split('\n')
            for line in lines:
                if line.startswith('🌟 OUTSTANDING'):
                    coaching_panel.insert(tk.END, line + '\n', "excellent")
                elif line.startswith('✅ STRONG'):
                    coaching_panel.insert(tk.END, line + '\n', "good")
                elif line.startswith('⚠️ ROOM'):
                    coaching_panel.insert(tk.END, line + '\n', "needs_improvement")
                elif line.startswith('🚨 REQUIRES'):
                    coaching_panel.insert(tk.END, line + '\n', "poor")
                elif line.startswith('🔸'):
                    coaching_panel.insert(tk.END, line + '\n', "coaching_tip")
                elif 'EXCELLENT' in line or 'excellent' in line:
                    coaching_panel.insert(tk.END, line + '\n', "excellent")
                elif 'GOOD' in line or 'good' in line:
                    coaching_panel.insert(tk.END, line + '\n', "good")
                elif 'NEEDS_IMPROVEMENT' in line or 'needs_improvement' in line:
                    coaching_panel.insert(tk.END, line + '\n', "needs_improvement")
                elif 'POOR' in line or 'poor' in line:
                    coaching_panel.insert(tk.END, line + '\n', "poor")
                else:
                    coaching_panel.insert(tk.END, line + '\n', "metric")
        else:
            # Display coaching guide
            coaching_panel.insert(tk.END, "🎯 PERFORMANCE COACHING ASSISTANT\n\n", "header")
            coaching_panel.insert(tk.END, "💡 WHAT THIS DOES:\n")
            coaching_panel.insert(tk.END, "• Analyzes your support conversation performance in real-time\n")
            coaching_panel.insert(tk.END, "• Provides specific coaching recommendations for improvement\n")
            coaching_panel.insert(tk.END, "• Tracks key performance metrics across all interactions\n")
            coaching_panel.insert(tk.END, "• Offers immediate action items for current conversation\n\n")

            coaching_panel.insert(tk.END, "📊 REAL-TIME METRICS TRACKED:\n", "header")
            coaching_panel.insert(tk.END, "• ⏱️ Response Rate: Messages per minute and efficiency\n", "excellent")
            coaching_panel.insert(tk.END, "• 💬 Message Quality: Length optimization and clarity\n", "good")
            coaching_panel.insert(tk.END, "• 📈 Satisfaction Trends: Customer satisfaction over time\n", "good")
            coaching_panel.insert(tk.END, "• 🚨 Performance Alerts: Real-time warnings and recommendations\n", "needs_improvement")
            coaching_panel.insert(tk.END, "• 🎯 Goal Tracking: Performance objectives and progress\n", "good")

            coaching_panel.insert(tk.END, "\n📊 PERFORMANCE ANALYSIS:\n", "header")
            coaching_panel.insert(tk.END, "• 💝 Empathy Level: Emotional alignment with customer needs\n", "good")
            coaching_panel.insert(tk.END, "• 🔧 Technical Accuracy: Use of correct Trend Micro terminology\n", "good")
            coaching_panel.insert(tk.END, "• 💬 Communication Clarity: Clear, structured communication\n", "good")
            coaching_panel.insert(tk.END, "• 📈 Session Progress: Overall conversation effectiveness\n", "good")

            coaching_panel.insert(tk.END, "\n🏆 COACHING FEATURES:\n", "header")
            coaching_panel.insert(tk.END, "• Real-time performance dashboard with live metrics\n")
            coaching_panel.insert(tk.END, "• Performance scoring with color-coded feedback\n")
            coaching_panel.insert(tk.END, "• Immediate alerts for potential issues\n")
            coaching_panel.insert(tk.END, "• Specific improvement suggestions based on customer emotion\n")
            coaching_panel.insert(tk.END, "• Best practices reinforcement for strong performance areas\n")
            coaching_panel.insert(tk.END, "• Goal-oriented recommendations for skill development\n\n")

            coaching_panel.insert(tk.END, "🧠 Start a customer conversation to receive real-time performance coaching, live metrics, and improvement recommendations.", "coaching_tip")

        coaching_panel.config(state=tk.DISABLED)

def update_session_metrics(engineer_message):
    """Update real-time session metrics"""
    global session_metrics
    import datetime

    current_time = datetime.datetime.now()

    # Initialize session if first message
    if session_metrics["session_start_time"] is None:
        session_metrics["session_start_time"] = current_time

    # Update message count
    session_metrics["messages_sent"] += 1

    # Update average response length
    current_avg = session_metrics["avg_response_length"]
    message_count = session_metrics["messages_sent"]
    session_metrics["avg_response_length"] = ((current_avg * (message_count - 1)) + len(engineer_message)) / message_count

    # Calculate response time (simulated)
    if session_metrics["last_response_time"]:
        response_time_seconds = (current_time - session_metrics["last_response_time"]).total_seconds()
        if response_time_seconds > 300:  # 5 minutes
            session_metrics["escalation_warnings"] += 1

    session_metrics["last_response_time"] = current_time

    # Track customer satisfaction trend
    satisfaction = customer_sentiment.get('satisfaction', 70)
    session_metrics["customer_satisfaction_trend"].append(satisfaction)

    # Keep only last 10 satisfaction scores
    if len(session_metrics["customer_satisfaction_trend"]) > 10:
        session_metrics["customer_satisfaction_trend"].pop(0)

def get_real_time_performance_feedback():
    """Generate real-time performance feedback"""
    import datetime

    if not session_metrics["session_start_time"]:
        return "📊 REAL-TIME PERFORMANCE TRACKING\n\nNo active session data available. Start a conversation to begin tracking performance metrics."

    current_time = datetime.datetime.now()
    session_duration = (current_time - session_metrics["session_start_time"]).total_seconds() / 60  # in minutes

    feedback = "📊 REAL-TIME PERFORMANCE DASHBOARD\n\n"

    # Session Overview
    feedback += "🕒 SESSION OVERVIEW:\n"
    feedback += f"• Duration: {session_duration:.1f} minutes\n"
    feedback += f"• Messages Sent: {session_metrics['messages_sent']}\n"
    feedback += f"• Avg Response Length: {session_metrics['avg_response_length']:.0f} characters\n"
    feedback += f"• Escalation Warnings: {session_metrics['escalation_warnings']}\n\n"

    # Performance Trends
    feedback += "📈 PERFORMANCE TRENDS:\n"

    # Response efficiency
    if session_duration > 0:
        messages_per_minute = session_metrics['messages_sent'] / session_duration
        if messages_per_minute > 1.5:
            feedback += "• ✅ Response Rate: EXCELLENT (>1.5 msg/min)\n"
        elif messages_per_minute > 1.0:
            feedback += "• ✅ Response Rate: GOOD (>1.0 msg/min)\n"
        elif messages_per_minute > 0.5:
            feedback += "• ⚠️ Response Rate: NEEDS IMPROVEMENT (>0.5 msg/min)\n"
        else:
            feedback += "• 🚨 Response Rate: TOO SLOW (<0.5 msg/min)\n"

    # Message quality
    avg_length = session_metrics['avg_response_length']
    if 50 <= avg_length <= 200:
        feedback += "• ✅ Message Length: OPTIMAL (50-200 chars)\n"
    elif avg_length > 200:
        feedback += "• ⚠️ Message Length: TOO VERBOSE (>200 chars)\n"
    else:
        feedback += "• ⚠️ Message Length: TOO BRIEF (<50 chars)\n"

    # Customer satisfaction trend
    if session_metrics["customer_satisfaction_trend"]:
        recent_scores = session_metrics["customer_satisfaction_trend"][-3:]
        if len(recent_scores) >= 2:
            trend = recent_scores[-1] - recent_scores[0]
            if trend > 10:
                feedback += "• 📈 Satisfaction Trend: IMPROVING (+{:.0f}%)\n".format(trend)
            elif trend < -10:
                feedback += "• 📉 Satisfaction Trend: DECLINING ({:.0f}%)\n".format(trend)
            else:
                feedback += "• ➡️ Satisfaction Trend: STABLE\n"

        current_satisfaction = recent_scores[-1]
        if current_satisfaction >= 80:
            feedback += "• 😊 Current Satisfaction: HIGH ({:.0f}%)\n".format(current_satisfaction)
        elif current_satisfaction >= 60:
            feedback += "• 😐 Current Satisfaction: MEDIUM ({:.0f}%)\n".format(current_satisfaction)
        else:
            feedback += "• 😞 Current Satisfaction: LOW ({:.0f}%)\n".format(current_satisfaction)

    # Real-time alerts
    feedback += "\n🚨 REAL-TIME ALERTS:\n"

    alerts_added = False
    if session_metrics["escalation_warnings"] > 0:
        feedback += f"• Slow response detected {session_metrics['escalation_warnings']} time(s)\n"
        alerts_added = True

    if len(conversation_history) > 8:
        feedback += "• Long conversation detected - consider escalation\n"
        alerts_added = True

    if customer_sentiment.get('emotion') == 'frustrated' and session_metrics['messages_sent'] > 3:
        feedback += "• Customer frustration persisting - prioritize empathy\n"
        alerts_added = True

    if resolution_confidence < 50 and session_metrics['messages_sent'] > 4:
        feedback += "• Low resolution confidence - gather more information\n"
        alerts_added = True

    if not alerts_added:
        feedback += "• No alerts - performance on track ✅\n"

    # Immediate recommendations
    feedback += "\n💡 IMMEDIATE RECOMMENDATIONS:\n"

    if session_metrics['messages_sent'] >= 5:
        if performance_metrics.get("empathy_level") in ["needs_improvement", "poor"]:
            feedback += "• Increase empathy expressions in next response\n"
        if performance_metrics.get("technical_accuracy") in ["needs_improvement", "poor"]:
            feedback += "• Include specific Trend Micro terminology\n"
        if performance_metrics.get("communication_clarity") in ["needs_improvement", "poor"]:
            feedback += "• Structure response with clear steps\n"
    else:
        feedback += "• Continue current approach\n"
        feedback += "• Monitor customer sentiment closely\n"

    # Next performance goal
    feedback += "\n🎯 NEXT PERFORMANCE GOAL:\n"

    if resolution_confidence < 70:
        feedback += "• Increase resolution confidence to 70%+\n"
    elif customer_sentiment.get('satisfaction', 70) < 80:
        feedback += "• Improve customer satisfaction to 80%+\n"
    elif session_metrics['messages_sent'] > 6:
        feedback += "• Work toward case closure with high confidence\n"
    else:
        feedback += "• Maintain current excellent performance\n"

    return feedback

def reset_session_metrics():
    """Reset session metrics for new conversation"""
    global session_metrics
    session_metrics = {
        "messages_sent": 0,
        "avg_response_length": 0,
        "empathy_score_total": 0,
        "technical_accuracy_total": 0,
        "clarity_score_total": 0,
        "session_start_time": None,
        "last_response_time": None,
        "escalation_warnings": 0,
        "customer_satisfaction_trend": []
    }

def surface_dynamic_knowledge():
    """Challenge 4: Knowledge Efficiency - Surface Trend Micro Help Center knowledge automatically"""
    global knowledge_suggestions, is_processing

    if not conversation_history or is_processing:
        return

    is_processing = True
    update_status("Searching Trend Micro Help Center...")

    try:
        # Get latest customer message
        latest_customer_msg = ""
        for msg in reversed(conversation_history):
            if msg["role"] == "customer":
                latest_customer_msg = msg["content"]
                break

        if not latest_customer_msg:
            return

        # Extract search query from customer message with priority for renewal terms
        query_words = []
        msg_lower = latest_customer_msg.lower()

        # Check for renewal-related terms first (high priority)
        renewal_terms = ["renew", "renewal", "subscription", "activate", "activation", "license", "expire", "expiration", "payment", "billing"]
        renewal_found = []
        for term in renewal_terms:
            if term in msg_lower:
                renewal_found.append(term)

        # Check for installation-related terms (high priority)
        installation_terms = ["install", "installation", "download", "setup", "maximum security", "antivirus plus", "internet security"]
        installation_found = []
        for term in installation_terms:
            if term in msg_lower:
                installation_found.append(term)

        # Check for ID Protection and Password Manager terms (high priority)
        id_protection_terms = ["id protection", "password manager", "password", "import password", "identity", "personal data", "privacy", "data breach"]
        id_protection_found = []
        for term in id_protection_terms:
            if term in msg_lower:
                id_protection_found.append(term)

        # Check for VPN and Web Protection terms (high priority)
        web_protection_terms = ["vpn", "web protection", "safe browsing", "website", "phishing", "block site", "parental control"]
        web_protection_found = []
        for term in web_protection_terms:
            if term in msg_lower:
                web_protection_found.append(term)

        # Check for billing and refund terms (high priority)
        billing_terms = ["cashback", "refund", "billing", "payment", "charge", "cancel subscription", "money back", "claim cashback", "return", "invoice"]
        billing_found = []
        for term in billing_terms:
            if term in msg_lower:
                billing_found.append(term)

        # Check for technical issues and errors (high priority)
        technical_error_terms = ["error", "not working", "won't start", "crashes", "freezes", "installation failed", "can't install", "setup error", "connection error", "website error", "app error", "loading error", "login error", "sync error", "update failed", "scan failed", "won't open", "blank screen", "stuck", "hangs"]
        technical_error_found = []
        for term in technical_error_terms:
            if term in msg_lower:
                technical_error_found.append(term)

        # Check for account website and portal issues (high priority)
        account_website_terms = ["account portal", "can't login", "forgot password", "account locked", "website down", "portal not working", "account access", "login failed", "password reset", "account issues", "portal error", "dashboard not loading", "account.trendmicro.com", "my account", "sign in problem", "authentication failed", "session expired", "account suspended", "profile issues"]
        account_website_found = []
        for term in account_website_terms:
            if term in msg_lower:
                account_website_found.append(term)

        # Check for resolution guard and case closure terms (high priority)
        resolution_guard_terms = ["case closed", "ticket resolved", "issue resolved", "problem solved", "case complete", "close ticket", "resolution confirmed", "mark resolved", "case closure", "support complete", "issue fixed", "problem fixed", "ready to close", "case status", "resolution quality", "customer satisfied", "follow up needed", "escalate case", "reopen case"]
        resolution_guard_found = []
        for term in resolution_guard_terms:
            if term in msg_lower:
                resolution_guard_found.append(term)

        # Prioritize specific query types
        if resolution_guard_found:
            query_words = resolution_guard_found[:2]  # Use top 2 resolution guard terms (highest priority)
        elif account_website_found:
            query_words = account_website_found[:2]  # Use top 2 account website terms
        elif technical_error_found:
            query_words = technical_error_found[:2]  # Use top 2 technical error terms
        elif renewal_found:
            query_words = renewal_found[:2]  # Use top 2 renewal terms
        elif installation_found:
            query_words = installation_found[:2]  # Use top 2 installation terms
        elif id_protection_found:
            query_words = id_protection_found[:2]  # Use top 2 ID protection terms
        elif web_protection_found:
            query_words = web_protection_found[:2]  # Use top 2 web protection terms
        elif billing_found:
            query_words = billing_found[:2]  # Use top 2 billing terms
        else:
            # Otherwise use general keywords
            for keyword in SEARCH_KEYWORDS:
                if keyword in msg_lower:
                    query_words.append(keyword)

        query = " ".join(set(query_words[:3])) if query_words else "security"

        # Search Trend Micro Help Center
        articles = fetch_trend_micro_articles(query)

        # Special handling for resolution guard and case closure (highest priority)
        if resolution_guard_found:
            knowledge_data = f"💡 RESOLUTION GUARD - CASE CLOSURE ANALYSIS\nIssue: {latest_customer_msg[:80]}...\n\n"

            # Get resolution guard guides from fallback articles
            fallback_articles = get_fallback_articles()
            resolution_guides = []
            for article in fallback_articles:
                if any(term in article['title'].lower() for term in ['resolution', 'case closure', 'quality', 'confidence']):
                    resolution_guides.append(article)

            if resolution_guides:
                for i, article in enumerate(resolution_guides[:3], 1):
                    knowledge_data += f"📋 {i}. {article['title']}\n"
                    knowledge_data += f"{article['snippet']}\n\n"

        # Special handling for account website and portal issues
        elif account_website_found:
            knowledge_data = f"💡 TREND MICRO ACCOUNT PORTAL SOLUTIONS\nIssue: {latest_customer_msg[:80]}...\n\n"

            # Get account portal troubleshooting guides from fallback articles
            fallback_articles = get_fallback_articles()
            account_guides = []
            for article in fallback_articles:
                if any(term in article['title'].lower() for term in ['account', 'portal', 'login', 'website', 'access']):
                    account_guides.append(article)

            if account_guides:
                for i, article in enumerate(account_guides[:3], 1):
                    knowledge_data += f"📋 {i}. {article['title']}\n"
                    knowledge_data += f"{article['snippet']}\n\n"

        # Special handling for technical errors and troubleshooting
        elif technical_error_found:
            knowledge_data = f"💡 TREND MICRO TECHNICAL TROUBLESHOOTING\nIssue: {latest_customer_msg[:80]}...\n\n"

            # Get technical troubleshooting guides from fallback articles
            fallback_articles = get_fallback_articles()
            technical_guides = []
            for article in fallback_articles:
                if any(term in article['title'].lower() for term in ['error', 'troubleshooting', 'installation', 'technical']):
                    technical_guides.append(article)

            if technical_guides:
                for i, article in enumerate(technical_guides[:3], 1):
                    knowledge_data += f"📋 {i}. {article['title']}\n"
                    knowledge_data += f"{article['snippet']}\n\n"

        # Special handling for renewal queries - prioritize detailed renewal guide
        elif renewal_found:
            knowledge_data = f"💡 TREND MICRO RENEWAL SOLUTIONS\nIssue: {latest_customer_msg[:80]}...\n\n"

            # Get the detailed renewal guide from our fallback articles
            fallback_articles = get_fallback_articles()
            renewal_guide = None
            for article in fallback_articles:
                if "renew" in article['title'].lower():
                    renewal_guide = article
                    break

            if renewal_guide:
                knowledge_data += f"📋 1. {renewal_guide['title']}\n"
                knowledge_data += f"{renewal_guide['snippet']}\n\n"

            # Add a few additional relevant articles from fallback for renewal context
            additional_count = 2
            for article in fallback_articles[:3]:  # Get first 3 other articles
                if renewal_guide and article['title'] != renewal_guide['title']:
                    knowledge_data += f"📋 {additional_count}. {article['title']}\n"
                    knowledge_data += f"   • {article['snippet'][:100]}...\n"
                    knowledge_data += f"   🔗 {article['link']}\n\n"
                    additional_count += 1
                    if additional_count > 3:  # Limit to 3 total articles
                        break

        # Special handling for installation queries - prioritize detailed installation guide
        elif installation_found:
            knowledge_data = f"💡 TREND MICRO INSTALLATION SOLUTIONS\nIssue: {latest_customer_msg[:80]}...\n\n"

            # Get the detailed installation guide from our fallback articles
            fallback_articles = get_fallback_articles()
            installation_guide = None
            for article in fallback_articles:
                if "install" in article['title'].lower():
                    installation_guide = article
                    break

            if installation_guide:
                knowledge_data += f"📋 1. {installation_guide['title']}\n"
                knowledge_data += f"{installation_guide['snippet']}\n\n"

            # Add a few additional relevant articles from fallback for installation context
            additional_count = 2
            for article in fallback_articles[:3]:  # Get first 3 other articles
                if installation_guide and article['title'] != installation_guide['title']:
                    knowledge_data += f"📋 {additional_count}. {article['title']}\n"
                    knowledge_data += f"   • {article['snippet'][:100]}...\n"
                    knowledge_data += f"   🔗 {article['link']}\n\n"
                    additional_count += 1
                    if additional_count > 3:  # Limit to 3 total articles
                        break

        # Special handling for ID Protection and Password Manager queries
        elif id_protection_found:
            knowledge_data = f"💡 TREND MICRO ID PROTECTION SOLUTIONS\nIssue: {latest_customer_msg[:80]}...\n\n"

            # Get ID Protection guides from fallback articles
            fallback_articles = get_fallback_articles()
            id_protection_guides = []
            for article in fallback_articles:
                if any(term in article['title'].lower() for term in ['password', 'privacy', 'identity', 'data']):
                    id_protection_guides.append(article)

            if id_protection_guides:
                for i, article in enumerate(id_protection_guides[:3], 1):
                    knowledge_data += f"📋 {i}. {article['title']}\n"
                    knowledge_data += f"{article['snippet']}\n\n"

        # Special handling for VPN and Web Protection queries
        elif web_protection_found:
            knowledge_data = f"💡 TREND MICRO WEB PROTECTION SOLUTIONS\nIssue: {latest_customer_msg[:80]}...\n\n"

            # Get Web Protection guides from fallback articles
            fallback_articles = get_fallback_articles()
            web_protection_guides = []
            for article in fallback_articles:
                if any(term in article['title'].lower() for term in ['web', 'firewall', 'protection', 'parental']):
                    web_protection_guides.append(article)

            if web_protection_guides:
                for i, article in enumerate(web_protection_guides[:3], 1):
                    knowledge_data += f"📋 {i}. {article['title']}\n"
                    knowledge_data += f"{article['snippet']}\n\n"

        # Special handling for billing and refund queries
        elif billing_found:
            knowledge_data = f"💡 TREND MICRO BILLING & REFUND SOLUTIONS\nIssue: {latest_customer_msg[:80]}...\n\n"

            # Get billing guides from fallback articles
            fallback_articles = get_fallback_articles()
            billing_guides = []
            for article in fallback_articles:
                if any(term in article['title'].lower() for term in ['billing', 'refund', 'cashback', 'payment', 'cancel']):
                    billing_guides.append(article)

            if billing_guides:
                for i, article in enumerate(billing_guides[:3], 1):
                    knowledge_data += f"📋 {i}. {article['title']}\n"
                    knowledge_data += f"{article['snippet']}\n\n"

        else:
            knowledge_data = f"💡 TREND MICRO SOLUTIONS\nIssue: {latest_customer_msg[:80]}...\n\n"

            # Process general articles normally
            for i, article in enumerate(articles, 1):
                knowledge_data += f"📋 {i}. {article['title']}\n"

                # Get solution bullets from the article
                bullets = []
                if article['link'] and 'helpcenter.trendmicro.com' in article['link']:
                    bullets = get_solution_bullets(article['link'], article['title'])

                # If no bullets from web scraping, use default solutions
                if not bullets:
                    bullets = get_default_solution_bullets(article['title'], query)

                # If still no bullets, use snippet
                if bullets:
                    for bullet in bullets:
                        knowledge_data += f"   • {bullet}\n"
                else:
                    knowledge_data += f"   • {article['snippet']}\n"

                # Add quick action based on issue type
                if any(word in latest_customer_msg.lower() for word in ['virus', 'malware', 'infected']):
                    knowledge_data += f"   ⚡ Quick: Run full scan, check quarantine\n"
                elif any(word in latest_customer_msg.lower() for word in ['slow', 'performance']):
                    knowledge_data += f"   ⚡ Quick: Check resources, optimize settings\n"
                elif any(word in latest_customer_msg.lower() for word in ['email', 'spam']):
                    knowledge_data += f"   ⚡ Quick: Configure email security\n"

                knowledge_data += f"   🔗 {article['link']}\n\n"

            if not articles:
                knowledge_data += "📚 GENERAL TREND MICRO SOLUTIONS:\n\n"
                knowledge_data += "🛡️ SECURITY BEST PRACTICES:\n"
                knowledge_data += "• Keep Trend Micro products updated to latest version\n"
                knowledge_data += "• Run full system scans weekly\n"
                knowledge_data += "• Enable real-time protection and web reputation\n"
                knowledge_data += "• Configure firewall settings appropriately\n"
                knowledge_data += "• Review quarantine regularly for false positives\n\n"

                knowledge_data += "🔧 COMMON TROUBLESHOOTING STEPS:\n"
                knowledge_data += "• Restart Trend Micro services if performance issues occur\n"
                knowledge_data += "• Check for conflicting security software\n"
                knowledge_data += "• Verify system requirements are met\n"
                knowledge_data += "• Update Windows and system drivers\n"
                knowledge_data += "• Contact support if issues persist\n\n"

        knowledge_suggestions = knowledge_data
        update_knowledge_panel()
        update_status("Trend Micro solutions found")

        # Track this solution in history
        add_to_solution_history(latest_customer_msg, knowledge_data)

    except Exception as e:
        knowledge_suggestions = f"❌ Error accessing Trend Micro Help Center: {str(e)}\n\n🆘 MANUAL SUPPORT OPTIONS:\n• Visit https://helpcenter.trendmicro.com/en-us/\n• Contact Trend Micro technical support\n• Check product documentation\n• Search community forums for solutions"
        update_knowledge_panel()
        update_status("Help Center search failed")
    finally:
        is_processing = False

def add_to_solution_history(customer_query, solution_provided):
    """Add a solution to the history tracking"""
    global solution_history

    import datetime

    # Create solution entry
    solution_entry = {
        'timestamp': datetime.datetime.now(),
        'customer_query': customer_query[:100] + "..." if len(customer_query) > 100 else customer_query,
        'solution_type': get_solution_type(solution_provided),
        'solution_summary': get_solution_summary(solution_provided),
        'full_solution': solution_provided
    }

    # Add to history (keep last 10 solutions)
    solution_history.append(solution_entry)
    if len(solution_history) > 10:
        solution_history.pop(0)  # Remove oldest entry

    # Update solution history dropdown
    update_solution_history_dropdown()

def get_solution_type(solution_text):
    """Determine the type of solution provided"""
    if "RENEWAL SOLUTIONS" in solution_text:
        return "🔄 Renewal Guide"
    elif "INSTALLATION SOLUTIONS" in solution_text:
        return "💻 Installation Guide"
    elif "virus" in solution_text.lower() or "malware" in solution_text.lower():
        return "🛡️ Security Issue"
    elif "scan" in solution_text.lower():
        return "🔍 Scanning Help"
    elif "performance" in solution_text.lower() or "slow" in solution_text.lower():
        return "⚡ Performance Issue"
    else:
        return "📋 General Support"

def get_solution_summary(solution_text):
    """Extract a brief summary of the solution"""
    lines = solution_text.split('\n')

    # Look for specific key information based on solution type
    if "RENEWAL SOLUTIONS" in solution_text:
        # Extract key renewal methods
        if "METHOD 1: Using Activation Code" in solution_text:
            return "Activation code renewal + online portal method with troubleshooting"
        else:
            return "Account portal renewal with step-by-step activation process"

    elif "INSTALLATION SOLUTIONS" in solution_text:
        # Extract key installation steps
        if "DOWNLOAD THE INSTALLER" in solution_text:
            return "Complete download → install → activate → verify process with troubleshooting"
        else:
            return "Full installation guide with system requirements and activation"

    elif "virus" in solution_text.lower() or "malware" in solution_text.lower():
        return "Malware removal steps, full scan procedures, and quarantine management"

    elif "scan" in solution_text.lower():
        return "Scanning configuration, scheduled scans, and scan result interpretation"

    elif "performance" in solution_text.lower() or "slow" in solution_text.lower():
        return "Performance optimization settings and system resource management"

    else:
        # Extract first meaningful bullet point or instruction
        for line in lines:
            line = line.strip()
            if line.startswith('•') and len(line) > 20:
                summary = line[1:].strip()  # Remove bullet point
                if len(summary) > 70:
                    summary = summary[:70] + "..."
                return summary
            elif line.startswith('1.') and len(line) > 20:
                summary = line[2:].strip()  # Remove numbering
                if len(summary) > 70:
                    summary = summary[:70] + "..."
                return summary

        # Final fallback
        return "Trend Micro help center solutions and troubleshooting guidance"

def update_solution_history_dropdown():
    """Update the solution history dropdown with available solutions"""
    if solution_history_dropdown:
        # Clear current options
        solution_history_dropdown['values'] = ()

        if solution_history:
            # Create dropdown options
            dropdown_options = []
            for i, entry in enumerate(reversed(solution_history), 1):
                timestamp_str = entry['timestamp'].strftime("%m/%d %H:%M")
                option_text = f"#{len(solution_history) - i + 1} [{timestamp_str}] {entry['solution_type']} - {entry['customer_query'][:50]}..."
                dropdown_options.append(option_text)

            solution_history_dropdown['values'] = dropdown_options

            # Set default text
            if solution_history_var:
                solution_history_var.set(f"📜 {len(solution_history)} solution(s) available - Select to view details")
        else:
            # No history available
            if solution_history_var:
                solution_history_var.set("📜 No solution history yet - Solutions will appear here automatically")

        # Clear the details panel initially
        if solution_history_panel:
            solution_history_panel.config(state=tk.NORMAL)
            solution_history_panel.delete(1.0, tk.END)
            solution_history_panel.insert(tk.END, "Select a solution from the dropdown above to view details...")
            solution_history_panel.config(state=tk.DISABLED)

def on_history_selection_changed(event=None):
    """Handle selection change in history dropdown"""
    if not solution_history_dropdown or not solution_history_panel:
        return

    selection_index = solution_history_dropdown.current()
    if selection_index >= 0 and selection_index < len(solution_history):
        # Get the selected solution entry (reversed order)
        entry = list(reversed(solution_history))[selection_index]

        # Display detailed information
        solution_history_panel.config(state=tk.NORMAL)
        solution_history_panel.delete(1.0, tk.END)

        # Header
        timestamp_str = entry['timestamp'].strftime("%m/%d/%Y %H:%M:%S")
        solution_history_panel.insert(tk.END, f"📜 SOLUTION DETAILS - {entry['solution_type']}\n")
        solution_history_panel.insert(tk.END, f"🕒 Timestamp: {timestamp_str}\n")
        solution_history_panel.insert(tk.END, "=" * 60 + "\n\n")

        # Customer query
        solution_history_panel.insert(tk.END, f"❓ CUSTOMER QUERY:\n{entry['customer_query']}\n\n")

        # Solution summary
        solution_history_panel.insert(tk.END, f"✅ SOLUTION PROVIDED:\n{entry['solution_summary']}\n\n")

        # Key actions for quick reference
        solution_history_panel.insert(tk.END, "🔑 QUICK ACTIONS FOR CUSTOMER:\n")
        if "renewal" in entry['customer_query'].lower():
            solution_history_panel.insert(tk.END, "• Visit account.trendmicro.com\n• Go to Licenses tab\n• Click Renew Now\n• Complete payment process\n")
        elif "install" in entry['customer_query'].lower():
            solution_history_panel.insert(tk.END, "• Download installer from account portal\n• Run as Administrator\n• Follow installation wizard\n• Activate with license key\n")
        elif "virus" in entry['customer_query'].lower() or "malware" in entry['customer_query'].lower():
            solution_history_panel.insert(tk.END, "• Run full system scan\n• Check quarantine for threats\n• Update virus definitions\n• Restart if required\n")
        else:
            solution_history_panel.insert(tk.END, "• Follow the detailed solution provided above\n• Contact support if issues persist\n")

        solution_history_panel.insert(tk.END, f"\n💡 TIP: Click '📄 Details' button to view the complete solution text.")

        solution_history_panel.config(state=tk.DISABLED)

def view_solution_details():
    """Show detailed view of selected solution"""
    if not solution_history:
        messagebox.showinfo("No History", "No solution history available to view.")
        return

    # Create a selection dialog
    detail_window = tk.Toplevel()
    detail_window.title("Solution History Details")
    detail_window.geometry("800x600")
    detail_window.configure(bg=SENTRIGUIDE_THEME['bg_primary'])

    # Header
    tk.Label(detail_window, text="📜 Solution History Details",
            bg=SENTRIGUIDE_THEME['bg_primary'], fg=SENTRIGUIDE_THEME['text_primary'],
            font=(SENTRIGUIDE_THEME['font_primary'], 14, 'bold')).pack(pady=10)

    # Selection frame
    selection_frame = tk.Frame(detail_window, bg=SENTRIGUIDE_THEME['bg_primary'])
    selection_frame.pack(fill='x', padx=20, pady=(0, 10))

    tk.Label(selection_frame, text="Select solution to view:",
            bg=SENTRIGUIDE_THEME['bg_primary'], fg=SENTRIGUIDE_THEME['text_primary'],
            font=(SENTRIGUIDE_THEME['font_primary'], 10)).pack(anchor='w')

    # Dropdown for solution selection
    solution_var = tk.StringVar()
    solution_options = []
    for i, entry in enumerate(reversed(solution_history), 1):
        timestamp_str = entry['timestamp'].strftime("%m/%d %H:%M")
        option_text = f"#{len(solution_history) - i + 1} [{timestamp_str}] {entry['solution_type']} - {entry['customer_query'][:50]}..."
        solution_options.append(option_text)

    solution_dropdown = ttk.Combobox(selection_frame, textvariable=solution_var,
                                   values=solution_options, width=80, state="readonly")
    solution_dropdown.pack(fill='x', pady=5)
    if solution_options:
        solution_dropdown.set(solution_options[0])  # Select first (most recent)

    # Detail display
    detail_text = scrolledtext.ScrolledText(detail_window, height=25, width=90,
                                           bg='white', fg=SENTRIGUIDE_THEME['text_primary'],
                                           font=(SENTRIGUIDE_THEME['font_primary'], 9))
    detail_text.pack(fill='both', expand=True, padx=20, pady=(0, 10))

    def update_detail_view():
        selected_index = solution_dropdown.current()
        if selected_index >= 0:
            entry = list(reversed(solution_history))[selected_index]
            detail_text.config(state=tk.NORMAL)
            detail_text.delete(1.0, tk.END)

            detail_text.insert(tk.END, f"🕒 TIMESTAMP: {entry['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}\n")
            detail_text.insert(tk.END, f"🏷️ SOLUTION TYPE: {entry['solution_type']}\n")
            detail_text.insert(tk.END, f"❓ CUSTOMER QUERY: {entry['customer_query']}\n")
            detail_text.insert(tk.END, f"💡 SOLUTION SUMMARY: {entry['solution_summary']}\n")
            detail_text.insert(tk.END, "=" * 80 + "\n\n")
            detail_text.insert(tk.END, "📋 FULL SOLUTION PROVIDED:\n\n")
            detail_text.insert(tk.END, entry['full_solution'])

            detail_text.config(state=tk.DISABLED)

    solution_dropdown.bind('<<ComboboxSelected>>', lambda e: update_detail_view())
    update_detail_view()  # Initial load

    # Close button
    tk.Button(detail_window, text="Close", command=detail_window.destroy,
             bg=SENTRIGUIDE_THEME['secondary'], fg='white',
             font=(SENTRIGUIDE_THEME['font_primary'], 10)).pack(pady=10)

def clear_solution_history():
    """Clear all solution history"""
    global solution_history

    if not solution_history:
        messagebox.showinfo("No History", "Solution history is already empty.")
        return

    result = messagebox.askyesno("Clear History",
                               f"Are you sure you want to clear all {len(solution_history)} solution history entries?\n\nThis action cannot be undone.")

    if result:
        solution_history.clear()
        update_solution_history_dropdown()
        messagebox.showinfo("History Cleared", "Solution history has been cleared successfully.")

def run_sentriguide_analysis():
    """Run all SentriGuide AI analyses"""
    if is_processing:
        return

    def run_analysis():
        update_conversation_summary()
        time.sleep(0.5)  # Prevent API rate limiting
        analyze_sentiment_and_tone()
        time.sleep(0.5)
        calculate_resolution_confidence()
        time.sleep(0.5)
        surface_dynamic_knowledge()
        time.sleep(0.5)
        analyze_coaching_performance()

    # Run in background thread
    threading.Thread(target=run_analysis, daemon=True).start()

# =============================
# UI Update Functions
# =============================
def update_status(message):
    """Update modern status bar with animations"""
    if status_label:
        # Add status indicator based on message type
        if "error" in message.lower() or "failed" in message.lower():
            status_icon = "❌"
        elif "complete" in message.lower() or "success" in message.lower():
            status_icon = "✅"
        elif "processing" in message.lower() or "analyzing" in message.lower():
            status_icon = "⏳"
        else:
            status_icon = "🧠"

        status_label.config(text=f"{status_icon} SentriGuide: {message}")

        # Add subtle animation effect by briefly changing background
        original_bg = status_label.cget('bg')
        try:
            status_label.config(bg=SENTRIGUIDE_THEME['primary_light'])
            status_label.after(200, lambda: status_label.config(bg=original_bg))
        except:
            pass  # Fallback if animation fails

    print(f"🧠 SentriGuide: {message}")

def update_context_panel():
    """Update conversation context panel"""
    if context_panel:
        context_panel.config(state=tk.NORMAL)
        context_panel.delete(1.0, tk.END)

        if conversation_summary:
            context_panel.insert(tk.END, conversation_summary)
        else:
            # Display helpful context management guide
            context_panel.insert(tk.END, "🎯 CONTEXT MANAGER - CONVERSATION TRACKING\n\n")
            context_panel.insert(tk.END, "💡 WHAT THIS DOES:\n")
            context_panel.insert(tk.END, "• Summarizes long conversations to prevent context loss\n")
            context_panel.insert(tk.END, "• Identifies main customer issues and conversation state\n")
            context_panel.insert(tk.END, "• Tracks conversation progress and escalation needs\n")
            context_panel.insert(tk.END, "• Provides customer communication profile analysis\n\n")

            context_panel.insert(tk.END, "📋 CONVERSATION ANALYSIS INCLUDES:\n")
            context_panel.insert(tk.END, "• Main issue identification (virus, performance, email, etc.)\n")
            context_panel.insert(tk.END, "• Total message count and conversation state\n")
            context_panel.insert(tk.END, "• Customer communication style assessment\n")
            context_panel.insert(tk.END, "• Latest customer concerns and progress notes\n")
            context_panel.insert(tk.END, "• Escalation recommendations for long conversations\n\n")

            context_panel.insert(tk.END, "🧠 Start a conversation with a customer to see automatic context analysis and conversation summarization.")

        context_panel.config(state=tk.DISABLED)

def update_sentiment_panel():
    """Update sentiment analysis panel"""
    if sentiment_panel:
        sentiment_panel.config(state=tk.NORMAL)
        sentiment_panel.delete(1.0, tk.END)

        if conversation_history and customer_sentiment.get('analysis'):
            # Sentiment summary
            emotion = customer_sentiment.get('emotion', 'unknown')
            urgency = customer_sentiment.get('urgency', 'medium')
            satisfaction = customer_sentiment.get('satisfaction', 70)

            sentiment_panel.insert(tk.END, f"😊 EMOTION: {emotion.upper()}\n", "emotion")
            sentiment_panel.insert(tk.END, f"⚡ URGENCY: {urgency.upper()}\n", "urgency")
            sentiment_panel.insert(tk.END, f"📊 SATISFACTION: {satisfaction}%\n\n", "satisfaction")

            # Full analysis
            analysis = customer_sentiment.get('analysis', 'No analysis yet')
            sentiment_panel.insert(tk.END, analysis, "analysis")
        else:
            # Display emotion alignment guide
            sentiment_panel.insert(tk.END, "💝 EMOTION ALIGNMENT - CUSTOMER SENTIMENT ANALYSIS\n\n", "emotion")
            sentiment_panel.insert(tk.END, "💡 WHAT THIS DOES:\n")
            sentiment_panel.insert(tk.END, "• Analyzes customer emotion and satisfaction levels\n")
            sentiment_panel.insert(tk.END, "• Provides tone recommendations for your responses\n")
            sentiment_panel.insert(tk.END, "• Identifies urgency levels and empathy triggers\n")
            sentiment_panel.insert(tk.END, "• Suggests response approaches based on customer mood\n\n")

            sentiment_panel.insert(tk.END, "😊 EMOTION DETECTION:\n", "emotion")
            sentiment_panel.insert(tk.END, "• Frustrated: Use empathetic language, acknowledge concerns\n")
            sentiment_panel.insert(tk.END, "• Urgent: Prioritize quick response, be direct\n")
            sentiment_panel.insert(tk.END, "• Confused: Use clear, simple language, be patient\n")
            sentiment_panel.insert(tk.END, "• Satisfied: Maintain professional tone, ensure completeness\n\n")

            sentiment_panel.insert(tk.END, "⚡ URGENCY LEVELS:\n", "urgency")
            sentiment_panel.insert(tk.END, "• High: Emergency/critical issues, immediate action needed\n")
            sentiment_panel.insert(tk.END, "• Medium: Standard timeline expectations\n")
            sentiment_panel.insert(tk.END, "• Low: No time pressure, thorough response preferred\n\n")

            sentiment_panel.insert(tk.END, "🧠 Start chatting with customers to see real-time sentiment analysis and tone recommendations.", "analysis")

        sentiment_panel.config(state=tk.DISABLED)

def update_confidence_panel():
    """Update resolution confidence panel"""
    if confidence_panel:
        confidence_panel.config(state=tk.NORMAL)
        confidence_panel.delete(1.0, tk.END)

        if not conversation_history:
            # Display default Resolution Guard guidance when no conversation
            confidence_panel.insert(tk.END, "🛡️ RESOLUTION GUARD - CASE CLOSURE QUALITY CONTROL\n\n", "header")
            confidence_panel.insert(tk.END, "💡 READY TO CLOSE A CASE? USE THIS GUIDE:\n\n", "header")

            confidence_panel.insert(tk.END, "✅ CONFIDENCE SCORE GUIDE:\n", "high")
            confidence_panel.insert(tk.END, "• 90-100%: SAFE TO CLOSE - Customer confirmed satisfaction\n")
            confidence_panel.insert(tk.END, "• 70-89%: REQUIRES VERIFICATION - Get explicit confirmation\n")
            confidence_panel.insert(tk.END, "• 0-69%: DO NOT CLOSE - Continue troubleshooting\n\n")

            confidence_panel.insert(tk.END, "🚫 RED FLAGS - NEVER CLOSE WHEN:\n", "low")
            confidence_panel.insert(tk.END, "• Customer says 'I'll try this later' without testing\n")
            confidence_panel.insert(tk.END, "• Customer stops responding mid-conversation\n")
            confidence_panel.insert(tk.END, "• Multiple solutions provided but none confirmed working\n")
            confidence_panel.insert(tk.END, "• Customer asks follow-up questions about solution\n")
            confidence_panel.insert(tk.END, "• Customer expresses frustration or dissatisfaction\n\n")

            confidence_panel.insert(tk.END, "✅ GREEN SIGNALS - SAFE TO CLOSE:\n", "high")
            confidence_panel.insert(tk.END, "• 'Yes, that fixed it completely'\n")
            confidence_panel.insert(tk.END, "• 'Everything is working perfectly now'\n")
            confidence_panel.insert(tk.END, "• 'Thank you, my issue is resolved'\n")
            confidence_panel.insert(tk.END, "• Customer demonstrates successful completion\n\n")

            confidence_panel.insert(tk.END, "💬 CONFIRMATION QUESTIONS TO ASK:\n", "medium")
            confidence_panel.insert(tk.END, "• 'Can you confirm that [issue] is now working correctly?'\n")
            confidence_panel.insert(tk.END, "• 'Are you able to [action] without any errors?'\n")
            confidence_panel.insert(tk.END, "• 'Is there anything else I can help you with?'\n")
            confidence_panel.insert(tk.END, "• 'How would you rate your satisfaction with this resolution?'\n\n")

            confidence_panel.insert(tk.END, "🧠 SentriGuide will analyze your conversation and provide resolution confidence scoring once you start chatting with customers.", "analysis")
        else:
            # Display actual confidence analysis when conversation exists
            color = "high" if resolution_confidence >= 80 else "medium" if resolution_confidence >= 60 else "low"

            confidence_panel.insert(tk.END, f"🎯 RESOLUTION CONFIDENCE\n", "header")
            confidence_panel.insert(tk.END, f"{resolution_confidence}%\n\n", color)

            # Analysis
            analysis = globals().get('resolution_analysis', 'No analysis yet')
            confidence_panel.insert(tk.END, analysis, "analysis")

        confidence_panel.config(state=tk.DISABLED)

def update_knowledge_panel():
    """Update knowledge suggestions panel"""
    if knowledge_panel:
        knowledge_panel.config(state=tk.NORMAL)
        knowledge_panel.delete(1.0, tk.END)

        if knowledge_suggestions:
            knowledge_panel.insert(tk.END, knowledge_suggestions)
        else:
            # Display knowledge efficiency guide
            knowledge_panel.insert(tk.END, "📚 TREND MICRO HELP CENTER - KNOWLEDGE EFFICIENCY\n\n")
            knowledge_panel.insert(tk.END, "💡 WHAT THIS DOES:\n")
            knowledge_panel.insert(tk.END, "• Automatically searches Trend Micro Help Center based on customer queries\n")
            knowledge_panel.insert(tk.END, "• Provides detailed, actionable solutions instead of generic links\n")
            knowledge_panel.insert(tk.END, "• Prioritizes specific issue types (renewal, installation, billing, etc.)\n")
            knowledge_panel.insert(tk.END, "• Tracks solution history for reference and consistency\n\n")

            knowledge_panel.insert(tk.END, "🎯 PRIORITY DETECTION FOR:\n")
            knowledge_panel.insert(tk.END, "• 🔄 Renewal & Subscription Issues - Step-by-step renewal guides\n")
            knowledge_panel.insert(tk.END, "• 💻 Installation & Activation - Complete setup procedures\n")
            knowledge_panel.insert(tk.END, "• 🛡️ ID Protection & Password Manager - Security feature setup\n")
            knowledge_panel.insert(tk.END, "• 🌐 VPN & Web Protection - Network security configuration\n")
            knowledge_panel.insert(tk.END, "• 💳 Billing & Refunds - Payment and refund procedures\n")
            knowledge_panel.insert(tk.END, "• ⚠️ Technical Errors - Troubleshooting and error resolution\n")
            knowledge_panel.insert(tk.END, "• 🔐 Account Portal Issues - Login and account access problems\n")
            knowledge_panel.insert(tk.END, "• ✅ Resolution Guard - Case closure and quality control\n\n")

            knowledge_panel.insert(tk.END, "📋 COMPREHENSIVE SOLUTIONS INCLUDE:\n")
            knowledge_panel.insert(tk.END, "• Detailed step-by-step instructions\n")
            knowledge_panel.insert(tk.END, "• Common troubleshooting scenarios\n")
            knowledge_panel.insert(tk.END, "• Error resolution procedures\n")
            knowledge_panel.insert(tk.END, "• Contact information for escalation\n")
            knowledge_panel.insert(tk.END, "• Best practices and preventive measures\n\n")

            knowledge_panel.insert(tk.END, "🧠 Start a customer conversation to see automatic knowledge surfacing and solution recommendations.")

        knowledge_panel.config(state=tk.DISABLED)

# =============================
# Conversation Management
# =============================
def end_conversation():
    """End current conversation and reset all analysis"""
    global conversation_history, conversation_summary, customer_sentiment, resolution_confidence, knowledge_suggestions, is_processing, conversation_ended

    if not conversation_history:
        messagebox.showinfo("No Conversation", "There is no active conversation to end.")
        return

    # Ask for confirmation
    total_messages = len(conversation_history)
    result = messagebox.askyesno("End Conversation",
                               f"Are you sure you want to end this conversation?\n\n"
                               f"• Total messages: {total_messages}\n"
                               f"• This will clear all current analysis\n"
                               f"• Solution history will be preserved\n\n"
                               f"This action cannot be undone.")

    if result:
        # Add conversation end message to history
        timestamp = datetime.datetime.now().strftime("%H:%M")

        # Add end message to conversation history before clearing
        conversation_history.append({"role": "system", "content": "═══ CONVERSATION ENDED ═══", "timestamp": timestamp})

        # Store the final conversation state for display
        final_conversation = conversation_history.copy()

        # Update both chat windows with the final state
        if engineer_chat_window:
            engineer_chat_window.config(state=tk.NORMAL)
            engineer_chat_window.delete(1.0, tk.END)

            for msg in final_conversation:
                msg_timestamp = msg.get('timestamp', datetime.datetime.now().strftime("%H:%M"))
                if msg["role"] == "customer":
                    engineer_chat_window.insert(tk.END, f"[{msg_timestamp}] Customer: {msg['content']}\n", "customer")
                elif msg["role"] == "engineer":
                    engineer_chat_window.insert(tk.END, f"[{msg_timestamp}] You: {msg['content']}\n", "engineer")
                elif msg["role"] == "system":
                    engineer_chat_window.insert(tk.END, f"\n[{msg_timestamp}] {msg['content']}\n\n", "system")

            engineer_chat_window.config(state=tk.DISABLED)
            engineer_chat_window.see(tk.END)

        if customer_simulation_window:
            customer_simulation_window.config(state=tk.NORMAL)
            customer_simulation_window.delete(1.0, tk.END)

            for msg in final_conversation:
                msg_timestamp = msg.get('timestamp', datetime.datetime.now().strftime("%H:%M"))
                if msg["role"] == "customer":
                    customer_simulation_window.insert(tk.END, f"[{msg_timestamp}] Customer: {msg['content']}\n", "customer")
                elif msg["role"] == "engineer":
                    customer_simulation_window.insert(tk.END, f"[{msg_timestamp}] Support: {msg['content']}\n", "engineer")
                elif msg["role"] == "system":
                    customer_simulation_window.insert(tk.END, f"\n[{msg_timestamp}] {msg['content']}\n\n", "system")

            customer_simulation_window.config(state=tk.DISABLED)
            customer_simulation_window.see(tk.END)

        # Clear all analysis data
        conversation_history.clear()
        conversation_summary = ""
        customer_sentiment = {"emotion": "neutral", "urgency": "medium", "satisfaction": 70}
        resolution_confidence = 0
        knowledge_suggestions = ""
        is_processing = False

        # Set flag to indicate conversation has ended (prevent auto-refresh from clearing)
        globals()['conversation_ended'] = True
        globals()['ended_conversation_display'] = final_conversation

        # Update all panels to show default content
        update_context_panel()
        update_sentiment_panel()
        update_confidence_panel()
        update_knowledge_panel()

        # Update status
        update_status("Conversation ended - Ready for new customer")

        messagebox.showinfo("Conversation Ended",
                          f"Conversation with {total_messages} messages has been ended.\n\n"
                          f"All analysis has been reset.\n"
                          f"SentriGuide is ready for the next customer.")

def new_conversation():
    """Start a new conversation (alias for end_conversation)"""
    end_conversation()

# =============================
# Customer Simulation Window
# =============================
def create_customer_simulation():
    """Create modern customer chat simulation for testing"""
    global customer_simulation_window

    sim_window = tk.Toplevel()
    sim_window.title("Customer Chat Simulation - SentriGuide AI")

    # Calculate responsive dimensions
    base_width, base_height = 650, 550
    scaled_width, scaled_height = calculate_scaled_dimensions(base_width, base_height, SCREEN_INFO)
    sim_window.geometry(f"{scaled_width}x{scaled_height}")
    sim_window.configure(bg=SENTRIGUIDE_THEME['bg_primary'])

    # Make window resizable with modern constraints
    sim_window.resizable(True, True)
    sim_window.minsize(int(500 * SCALE_FACTOR), int(450 * SCALE_FACTOR))

    # Modern window styling
    try:
        sim_window.wm_attributes('-alpha', 0.98)  # Slight transparency for modern look
    except:
        pass  # Fallback for systems that don't support transparency

    # Modern Header with Gradient Effect
    header = tk.Frame(sim_window, bg=SENTRIGUIDE_THEME['primary'], height=int(60 * SCALE_FACTOR))
    header.pack(fill='x')
    header.pack_propagate(False)

    # Header content with modern styling
    header_content = tk.Frame(header, bg=SENTRIGUIDE_THEME['primary'])
    header_content.pack(expand=True, fill='both', padx=SENTRIGUIDE_THEME['spacing_lg'], pady=SENTRIGUIDE_THEME['spacing_md'])

    # Modern title with icon and status
    title_frame = tk.Frame(header_content, bg=SENTRIGUIDE_THEME['primary'])
    title_frame.pack(side='left', fill='y')

    tk.Label(title_frame, text="👤 Customer Simulation",
            bg=SENTRIGUIDE_THEME['primary'], fg=SENTRIGUIDE_THEME['text_inverse'],
            font=(SENTRIGUIDE_THEME['font_primary'], SENTRIGUIDE_THEME['font_size_header'], 'bold')).pack(anchor='w')

    tk.Label(title_frame, text="● Live Chat Session",
            bg=SENTRIGUIDE_THEME['primary'], fg=SENTRIGUIDE_THEME['success_light'],
            font=(SENTRIGUIDE_THEME['font_primary'], SENTRIGUIDE_THEME['font_size_small'])).pack(anchor='w')

    # Status indicator
    status_frame = tk.Frame(header_content, bg=SENTRIGUIDE_THEME['primary'])
    status_frame.pack(side='right', fill='y')

    tk.Label(status_frame, text="🟢 Online",
            bg=SENTRIGUIDE_THEME['primary'], fg=SENTRIGUIDE_THEME['text_inverse'],
            font=(SENTRIGUIDE_THEME['font_primary'], SENTRIGUIDE_THEME['font_size_small'])).pack(anchor='e')

    # Modern Main Content Area
    main_frame = tk.Frame(sim_window, bg=SENTRIGUIDE_THEME['bg_primary'])
    main_frame.pack(fill='both', expand=True, padx=SENTRIGUIDE_THEME['spacing_lg'], pady=SENTRIGUIDE_THEME['spacing_lg'])

    # Chat container with modern card design
    chat_container = tk.Frame(main_frame, bg=SENTRIGUIDE_THEME['bg_surface'], relief='flat', bd=0)
    chat_container.pack(fill='both', expand=True)

    # Add subtle shadow effect with border
    try:
        chat_container.configure(highlightbackground=SENTRIGUIDE_THEME['divider'], highlightthickness=1)
    except:
        pass

    # Modern chat header
    chat_header = tk.Frame(chat_container, bg=SENTRIGUIDE_THEME['bg_surface'], height=int(40 * SCALE_FACTOR))
    chat_header.pack(fill='x', padx=SENTRIGUIDE_THEME['spacing_lg'], pady=(SENTRIGUIDE_THEME['spacing_md'], 0))
    chat_header.pack_propagate(False)

    tk.Label(chat_header, text="💬 Live Conversation",
            bg=SENTRIGUIDE_THEME['bg_surface'], fg=SENTRIGUIDE_THEME['text_primary'],
            font=(SENTRIGUIDE_THEME['font_primary'], SENTRIGUIDE_THEME['font_size_large'], 'bold')).pack(side='left', anchor='w')

    # Chat timestamp
    import datetime
    current_time = datetime.datetime.now().strftime("%H:%M")
    tk.Label(chat_header, text=f"Started at {current_time}",
            bg=SENTRIGUIDE_THEME['bg_surface'], fg=SENTRIGUIDE_THEME['text_secondary'],
            font=(SENTRIGUIDE_THEME['font_primary'], SENTRIGUIDE_THEME['font_size_small'])).pack(side='right', anchor='e')

    # Modern chat display with better spacing
    chat_height = max(18, int(22 * SCALE_FACTOR))
    chat_width = max(55, int(75 * SCALE_FACTOR))

    chat_display = scrolledtext.ScrolledText(chat_container, height=chat_height, width=chat_width,
                                            bg=SENTRIGUIDE_THEME['bg_surface'], fg=SENTRIGUIDE_THEME['text_primary'],
                                            font=(SENTRIGUIDE_THEME['font_primary'], SENTRIGUIDE_THEME['font_size_medium']),
                                            relief='flat', bd=0, wrap='word', padx=SENTRIGUIDE_THEME['spacing_md'], pady=SENTRIGUIDE_THEME['spacing_sm'])
    chat_display.pack(fill='both', expand=True, padx=SENTRIGUIDE_THEME['spacing_lg'], pady=(SENTRIGUIDE_THEME['spacing_sm'], SENTRIGUIDE_THEME['spacing_md']))
    chat_display.config(state=tk.DISABLED)

    customer_simulation_window = chat_display

    # Modern Input Area with Card Design
    input_container = tk.Frame(chat_container, bg=SENTRIGUIDE_THEME['bg_surface'])
    input_container.pack(fill='x', padx=SENTRIGUIDE_THEME['spacing_lg'], pady=(0, SENTRIGUIDE_THEME['spacing_lg']))

    # Input header with modern styling
    input_header = tk.Frame(input_container, bg=SENTRIGUIDE_THEME['bg_surface'])
    input_header.pack(fill='x', pady=(0, SENTRIGUIDE_THEME['spacing_sm']))

    tk.Label(input_header, text="✏️ Type as Customer",
            bg=SENTRIGUIDE_THEME['bg_surface'], fg=SENTRIGUIDE_THEME['text_primary'],
            font=(SENTRIGUIDE_THEME['font_primary'], SENTRIGUIDE_THEME['font_size_medium'], 'bold')).pack(side='left')

    # Typing indicator
    typing_label = tk.Label(input_header, text="",
            bg=SENTRIGUIDE_THEME['bg_surface'], fg=SENTRIGUIDE_THEME['text_secondary'],
            font=(SENTRIGUIDE_THEME['font_primary'], SENTRIGUIDE_THEME['font_size_small'], 'italic'))
    typing_label.pack(side='right')

    # Modern input field with enhanced styling
    entry_frame = tk.Frame(input_container, bg=SENTRIGUIDE_THEME['bg_surface'])
    entry_frame.pack(fill='x', pady=(0, SENTRIGUIDE_THEME['spacing_sm']))

    # Modern entry field with better styling
    customer_entry = tk.Entry(entry_frame,
                             font=(SENTRIGUIDE_THEME['font_primary'], SENTRIGUIDE_THEME['font_size_medium']),
                             bg=SENTRIGUIDE_THEME['bg_secondary'], fg=SENTRIGUIDE_THEME['text_primary'],
                             relief='flat', bd=1, highlightthickness=2,
                             highlightcolor=SENTRIGUIDE_THEME['primary'],
                             highlightbackground=SENTRIGUIDE_THEME['divider'])
    customer_entry.pack(side='left', fill='x', expand=True, padx=(0, SENTRIGUIDE_THEME['spacing_md']), ipady=SENTRIGUIDE_THEME['spacing_sm'])

    def send_customer_message():
        global conversation_ended, ended_conversation_display
        message = customer_entry.get().strip()
        if message:
            # Show typing indicator briefly
            typing_label.config(text="✍️ Sending...")
            sim_window.update()

            # Reset conversation ended state when new message is sent
            if conversation_ended:
                conversation_ended = False
                ended_conversation_display = []

            timestamp = datetime.datetime.now().strftime("%H:%M")
            conversation_history.append({"role": "customer", "content": message, "timestamp": timestamp})

            # Update chat display with modern message styling
            chat_display.config(state=tk.NORMAL)
            chat_display.insert(tk.END, f"\n[{timestamp}] ", "timestamp")
            chat_display.insert(tk.END, "Customer", "customer_name")
            chat_display.insert(tk.END, f": {message}\n", "customer_message")
            chat_display.config(state=tk.DISABLED)
            chat_display.see(tk.END)

            customer_entry.delete(0, tk.END)
            typing_label.config(text="")

            # Trigger SentriGuide analysis
            run_sentriguide_analysis()

    # Modern button container
    button_container = tk.Frame(entry_frame, bg=SENTRIGUIDE_THEME['bg_surface'])
    button_container.pack(side='right')

    # Modern send button with hover effect
    send_btn = tk.Button(button_container, text="➤ Send", command=send_customer_message,
                        bg=SENTRIGUIDE_THEME['primary'], fg=SENTRIGUIDE_THEME['text_inverse'],
                        font=(SENTRIGUIDE_THEME['font_primary'], SENTRIGUIDE_THEME['font_size_medium'], 'bold'),
                        relief='flat', bd=0, padx=SENTRIGUIDE_THEME['spacing_lg'], pady=SENTRIGUIDE_THEME['spacing_sm'],
                        cursor='hand2')
    send_btn.pack(side='right', padx=(0, SENTRIGUIDE_THEME['spacing_sm']))

    # Modern end conversation button
    end_btn = tk.Button(button_container, text="⏹️ End", command=end_conversation,
                       bg=SENTRIGUIDE_THEME['danger'], fg=SENTRIGUIDE_THEME['text_inverse'],
                       font=(SENTRIGUIDE_THEME['font_primary'], SENTRIGUIDE_THEME['font_size_medium'], 'bold'),
                       relief='flat', bd=0, padx=SENTRIGUIDE_THEME['spacing_lg'], pady=SENTRIGUIDE_THEME['spacing_sm'],
                       cursor='hand2')
    end_btn.pack(side='right')

    # Add button hover effects
    def on_send_hover(event):
        send_btn.config(bg=SENTRIGUIDE_THEME['primary_light'])
    def on_send_leave(event):
        send_btn.config(bg=SENTRIGUIDE_THEME['primary'])
    def on_end_hover(event):
        end_btn.config(bg=SENTRIGUIDE_THEME['danger_light'])
    def on_end_leave(event):
        end_btn.config(bg=SENTRIGUIDE_THEME['danger'])

    send_btn.bind('<Enter>', on_send_hover)
    send_btn.bind('<Leave>', on_send_leave)
    end_btn.bind('<Enter>', on_end_hover)
    end_btn.bind('<Leave>', on_end_leave)

    customer_entry.bind('<Return>', lambda e: send_customer_message())
    customer_entry.focus()

    # Configure modern text tags with better styling
    chat_display.tag_config("timestamp", foreground=SENTRIGUIDE_THEME['text_secondary'], font=(SENTRIGUIDE_THEME['font_primary'], SENTRIGUIDE_THEME['font_size_small']))
    chat_display.tag_config("customer_name", foreground=SENTRIGUIDE_THEME['primary'], font=(SENTRIGUIDE_THEME['font_primary'], SENTRIGUIDE_THEME['font_size_medium'], 'bold'))
    chat_display.tag_config("customer_message", foreground=SENTRIGUIDE_THEME['text_primary'], font=(SENTRIGUIDE_THEME['font_primary'], SENTRIGUIDE_THEME['font_size_medium']))
    chat_display.tag_config("engineer_name", foreground=SENTRIGUIDE_THEME['success'], font=(SENTRIGUIDE_THEME['font_primary'], SENTRIGUIDE_THEME['font_size_medium'], 'bold'))
    chat_display.tag_config("engineer_message", foreground=SENTRIGUIDE_THEME['text_primary'], font=(SENTRIGUIDE_THEME['font_primary'], SENTRIGUIDE_THEME['font_size_medium']))
    chat_display.tag_config("system", foreground=SENTRIGUIDE_THEME['warning'], font=(SENTRIGUIDE_THEME['font_primary'], SENTRIGUIDE_THEME['font_size_medium'], 'bold'), justify='center')

    # Legacy tags for backward compatibility
    chat_display.tag_config("customer", foreground=SENTRIGUIDE_THEME['primary'], font=(SENTRIGUIDE_THEME['font_primary'], SENTRIGUIDE_THEME['font_size_medium'], 'bold'))
    chat_display.tag_config("engineer", foreground=SENTRIGUIDE_THEME['success'], font=(SENTRIGUIDE_THEME['font_primary'], SENTRIGUIDE_THEME['font_size_medium'], 'bold'))

    return sim_window

# =============================
# AI Analysis Popup Window
# =============================
def create_ai_analysis_popup(parent_window):
    """Create popup window with AI analysis tabs"""
    global context_panel, sentiment_panel, confidence_panel, knowledge_panel, coaching_panel
    global solution_history_panel, solution_history_var, solution_history_dropdown

    # Create popup window
    popup = tk.Toplevel(parent_window)
    popup.title("SentriGuide AI Analysis Dashboard")
    popup.geometry("1000x700")
    popup.configure(bg=SENTRIGUIDE_THEME['bg_primary'])
    popup.resizable(True, True)
    popup.minsize(800, 600)

    # Center the popup on screen
    popup.update_idletasks()
    x = (popup.winfo_screenwidth() - popup.winfo_reqwidth()) // 2
    y = (popup.winfo_screenheight() - popup.winfo_reqheight()) // 2
    popup.geometry(f"+{x}+{y}")

    # Header
    header_frame = tk.Frame(popup, bg=SENTRIGUIDE_THEME['primary'], height=60)
    header_frame.pack(fill='x')
    header_frame.pack_propagate(False)

    header_content = tk.Frame(header_frame, bg=SENTRIGUIDE_THEME['primary'])
    header_content.pack(expand=True, fill='both', padx=20, pady=15)

    tk.Label(header_content, text="🧠 AI Analysis Dashboard",
            bg=SENTRIGUIDE_THEME['primary'], fg=SENTRIGUIDE_THEME['text_inverse'],
            font=(SENTRIGUIDE_THEME['font_primary'], 16, 'bold')).pack(side='left')

    close_btn = tk.Button(header_content, text="✕ Close", command=popup.destroy,
                         bg=SENTRIGUIDE_THEME['danger'], fg=SENTRIGUIDE_THEME['text_inverse'],
                         font=(SENTRIGUIDE_THEME['font_primary'], 10, 'bold'),
                         relief='flat', cursor='hand2')
    close_btn.pack(side='right')

    # Main content with notebook
    content_frame = tk.Frame(popup, bg=SENTRIGUIDE_THEME['bg_primary'])
    content_frame.pack(fill='both', expand=True, padx=20, pady=20)

    # Modern notebook for AI panels with custom styling
    style = ttk.Style()
    try:
        style.theme_use('clam')
        style.configure('TNotebook', background=SENTRIGUIDE_THEME['bg_surface'])
        style.configure('TNotebook.Tab', padding=(SENTRIGUIDE_THEME['spacing_md'], SENTRIGUIDE_THEME['spacing_sm']))
        style.configure('TNotebook.Tab', font=(SENTRIGUIDE_THEME['font_primary'], SENTRIGUIDE_THEME['font_size_medium'], 'bold'))
    except:
        pass

    notebook = ttk.Notebook(content_frame)
    notebook.pack(fill='both', expand=True)

    # Create all the analysis panels in the popup
    create_analysis_panels(notebook, popup)

    # Initialize panels with current data
    update_all_panels()

    return popup

def create_analysis_notebook(container):
    """Create notebook with analysis panels inline in the main window"""
    global context_panel, sentiment_panel, confidence_panel, knowledge_panel, coaching_panel
    global solution_history_panel, solution_history_var, solution_history_dropdown

    # Modern notebook for AI panels with custom styling
    style = ttk.Style()
    try:
        style.theme_use('clam')
        style.configure('TNotebook', background=SENTRIGUIDE_THEME['bg_surface'])
        style.configure('TNotebook.Tab', padding=(SENTRIGUIDE_THEME['spacing_md'], SENTRIGUIDE_THEME['spacing_sm']))
        style.configure('TNotebook.Tab', font=(SENTRIGUIDE_THEME['font_primary'], SENTRIGUIDE_THEME['font_size_medium'], 'bold'))
    except:
        pass

    notebook = ttk.Notebook(container)
    notebook.pack(fill='both', expand=True)

    # Create all the analysis panels in the notebook
    create_analysis_panels(notebook, container)

    # Initialize panels with current data
    update_all_panels()

    return notebook

def create_analysis_panels(notebook, parent_window):
    """Create all analysis panels in the notebook"""
    global context_panel, sentiment_panel, confidence_panel, knowledge_panel, coaching_panel
    global solution_history_panel, solution_history_var, solution_history_dropdown

    # Calculate responsive dimensions for analysis panels
    panel_height = max(20, int(25 * SCALE_FACTOR))
    panel_width = max(60, int(70 * SCALE_FACTOR))

    # Modern Context Panel (Challenge 1)
    context_tab = tk.Frame(notebook, bg=SENTRIGUIDE_THEME['bg_surface'])
    notebook.add(context_tab, text="🎯 Context Manager")

    context_header = tk.Frame(context_tab, bg=SENTRIGUIDE_THEME['bg_surface'])
    context_header.pack(fill='x', padx=SENTRIGUIDE_THEME['spacing_lg'], pady=(SENTRIGUIDE_THEME['spacing_lg'], SENTRIGUIDE_THEME['spacing_sm']))

    tk.Label(context_header, text="Conversation Context & Summary",
            bg=SENTRIGUIDE_THEME['bg_surface'], fg=SENTRIGUIDE_THEME['text_primary'],
            font=(SENTRIGUIDE_THEME['font_primary'], SENTRIGUIDE_THEME['font_size_header'], 'bold')).pack(side='left')

    tk.Label(context_header, text="📊 Active Analysis",
            bg=SENTRIGUIDE_THEME['bg_surface'], fg=SENTRIGUIDE_THEME['info'],
            font=(SENTRIGUIDE_THEME['font_primary'], SENTRIGUIDE_THEME['font_size_small'])).pack(side='right')

    context_panel = scrolledtext.ScrolledText(context_tab, height=panel_height, width=panel_width,
                                             bg=SENTRIGUIDE_THEME['bg_secondary'], fg=SENTRIGUIDE_THEME['text_primary'],
                                             font=(SENTRIGUIDE_THEME['font_primary'], SENTRIGUIDE_THEME['font_size_small']))
    context_panel.pack(fill='both', expand=True, padx=SENTRIGUIDE_THEME['padding_medium'], pady=(0, SENTRIGUIDE_THEME['padding_medium']))
    context_panel.config(state=tk.DISABLED)

    # Sentiment Panel (Challenge 2)
    sentiment_tab = tk.Frame(notebook, bg=SENTRIGUIDE_THEME['bg_primary'])
    notebook.add(sentiment_tab, text="💝 Emotion Alignment")

    tk.Label(sentiment_tab, text="Customer Sentiment & Tone Guidance",
            bg=SENTRIGUIDE_THEME['bg_primary'], fg=SENTRIGUIDE_THEME['text_primary'],
            font=(SENTRIGUIDE_THEME['font_primary'], 11, 'bold')).pack(pady=(10, 5))

    sentiment_panel = scrolledtext.ScrolledText(sentiment_tab, height=25, width=70,
                                               bg='#fff3e0', fg=SENTRIGUIDE_THEME['text_primary'],
                                               font=(SENTRIGUIDE_THEME['font_primary'], 9))
    sentiment_panel.pack(fill='both', expand=True, padx=10, pady=(0, 10))
    sentiment_panel.config(state=tk.DISABLED)

    # Configure sentiment tags
    sentiment_panel.tag_config("emotion", foreground=SENTRIGUIDE_THEME['primary'], font=(SENTRIGUIDE_THEME['font_primary'], 10, 'bold'))
    sentiment_panel.tag_config("urgency", foreground=SENTRIGUIDE_THEME['warning'], font=(SENTRIGUIDE_THEME['font_primary'], 10, 'bold'))
    sentiment_panel.tag_config("satisfaction", foreground=SENTRIGUIDE_THEME['success'], font=(SENTRIGUIDE_THEME['font_primary'], 10, 'bold'))
    sentiment_panel.tag_config("analysis", foreground=SENTRIGUIDE_THEME['text_primary'])

    # Confidence Panel (Challenge 3)
    confidence_tab = tk.Frame(notebook, bg=SENTRIGUIDE_THEME['bg_primary'])
    notebook.add(confidence_tab, text="✅ Resolution Guard")

    tk.Label(confidence_tab, text="Resolution Confidence & Case Closure Prevention",
            bg=SENTRIGUIDE_THEME['bg_primary'], fg=SENTRIGUIDE_THEME['text_primary'],
            font=(SENTRIGUIDE_THEME['font_primary'], 11, 'bold')).pack(pady=(10, 5))

    confidence_panel = scrolledtext.ScrolledText(confidence_tab, height=25, width=70,
                                                bg='#e8f5e8', fg=SENTRIGUIDE_THEME['text_primary'],
                                                font=(SENTRIGUIDE_THEME['font_primary'], 9))
    confidence_panel.pack(fill='both', expand=True, padx=10, pady=(0, 10))
    confidence_panel.config(state=tk.DISABLED)

    # Configure confidence tags
    confidence_panel.tag_config("header", foreground=SENTRIGUIDE_THEME['text_primary'], font=(SENTRIGUIDE_THEME['font_primary'], 10, 'bold'))
    confidence_panel.tag_config("high", foreground=SENTRIGUIDE_THEME['success'], font=(SENTRIGUIDE_THEME['font_primary'], 14, 'bold'))
    confidence_panel.tag_config("medium", foreground=SENTRIGUIDE_THEME['warning'], font=(SENTRIGUIDE_THEME['font_primary'], 14, 'bold'))
    confidence_panel.tag_config("low", foreground=SENTRIGUIDE_THEME['danger'], font=(SENTRIGUIDE_THEME['font_primary'], 14, 'bold'))
    confidence_panel.tag_config("analysis", foreground=SENTRIGUIDE_THEME['text_primary'])

    # Coaching Panel (Challenge 5)
    coaching_tab = tk.Frame(notebook, bg=SENTRIGUIDE_THEME['bg_primary'])
    notebook.add(coaching_tab, text="🎯 Coaching Assistant")

    tk.Label(coaching_tab, text="Performance Analysis & Real-Time Coaching",
            bg=SENTRIGUIDE_THEME['bg_primary'], fg=SENTRIGUIDE_THEME['text_primary'],
            font=(SENTRIGUIDE_THEME['font_primary'], 11, 'bold')).pack(pady=(10, 5))

    coaching_panel = scrolledtext.ScrolledText(coaching_tab, height=25, width=70,
                                              bg='#fff3e0', fg=SENTRIGUIDE_THEME['text_primary'],
                                              font=(SENTRIGUIDE_THEME['font_primary'], 9))
    coaching_panel.pack(fill='both', expand=True, padx=10, pady=(0, 10))
    coaching_panel.config(state=tk.DISABLED)

    # Configure coaching tags
    coaching_panel.tag_config("header", foreground=SENTRIGUIDE_THEME['text_primary'], font=(SENTRIGUIDE_THEME['font_primary'], 10, 'bold'))
    coaching_panel.tag_config("excellent", foreground=SENTRIGUIDE_THEME['success'], font=(SENTRIGUIDE_THEME['font_primary'], 10, 'bold'))
    coaching_panel.tag_config("good", foreground='#4CAF50', font=(SENTRIGUIDE_THEME['font_primary'], 10, 'bold'))
    coaching_panel.tag_config("needs_improvement", foreground=SENTRIGUIDE_THEME['warning'], font=(SENTRIGUIDE_THEME['font_primary'], 10, 'bold'))
    coaching_panel.tag_config("poor", foreground=SENTRIGUIDE_THEME['danger'], font=(SENTRIGUIDE_THEME['font_primary'], 10, 'bold'))
    coaching_panel.tag_config("coaching_tip", foreground=SENTRIGUIDE_THEME['primary'], font=(SENTRIGUIDE_THEME['font_primary'], 9, 'italic'))
    coaching_panel.tag_config("metric", foreground=SENTRIGUIDE_THEME['text_primary'])

    # Knowledge Panel (Challenge 4)
    knowledge_tab = tk.Frame(notebook, bg=SENTRIGUIDE_THEME['bg_primary'])
    notebook.add(knowledge_tab, text="📚 Trend Micro Help")

    tk.Label(knowledge_tab, text="Trend Micro Help Center & Knowledge Base",
            bg=SENTRIGUIDE_THEME['bg_primary'], fg=SENTRIGUIDE_THEME['text_primary'],
            font=(SENTRIGUIDE_THEME['font_primary'], 11, 'bold')).pack(pady=(10, 5))

    # Solution History Dropdown (at top)
    history_frame = tk.Frame(knowledge_tab, bg=SENTRIGUIDE_THEME['bg_primary'])
    history_frame.pack(fill='x', padx=10, pady=(0, 10))

    # History header and controls
    history_header_frame = tk.Frame(history_frame, bg=SENTRIGUIDE_THEME['bg_primary'])
    history_header_frame.pack(fill='x', pady=(0, 5))

    tk.Label(history_header_frame, text="📜 Solution History:",
            bg=SENTRIGUIDE_THEME['bg_primary'], fg=SENTRIGUIDE_THEME['text_primary'],
            font=(SENTRIGUIDE_THEME['font_primary'], 10, 'bold')).pack(side='left')

    # History controls on the right
    history_controls_frame = tk.Frame(history_header_frame, bg=SENTRIGUIDE_THEME['bg_primary'])
    history_controls_frame.pack(side='right')

    tk.Button(history_controls_frame, text="📄 Details",
             command=view_solution_details,
             bg=SENTRIGUIDE_THEME['primary'], fg='white',
             font=(SENTRIGUIDE_THEME['font_primary'], 8)).pack(side='right', padx=(5, 0))

    tk.Button(history_controls_frame, text="🗑️ Clear",
             command=clear_solution_history,
             bg=SENTRIGUIDE_THEME['danger'], fg='white',
             font=(SENTRIGUIDE_THEME['font_primary'], 8)).pack(side='right')

    # History dropdown selection
    solution_history_var = tk.StringVar()
    solution_history_dropdown = ttk.Combobox(history_frame, textvariable=solution_history_var,
                                           width=80, state="readonly",
                                           font=(SENTRIGUIDE_THEME['font_primary'], 9))
    solution_history_dropdown.pack(fill='x', pady=(0, 5))
    solution_history_dropdown.bind('<<ComboboxSelected>>', on_history_selection_changed)

    # History details display (collapsible)
    solution_history_panel = scrolledtext.ScrolledText(history_frame, height=8, width=80,
                                                      bg='#fff8e1', fg=SENTRIGUIDE_THEME['text_primary'],
                                                      font=(SENTRIGUIDE_THEME['font_primary'], 9))
    solution_history_panel.pack(fill='x', pady=(0, 10))
    solution_history_panel.config(state=tk.DISABLED)

    # Current Solutions (main panel)
    tk.Label(knowledge_tab, text="💡 Current Trend Micro Solutions",
            bg=SENTRIGUIDE_THEME['bg_primary'], fg=SENTRIGUIDE_THEME['text_primary'],
            font=(SENTRIGUIDE_THEME['font_primary'], 11, 'bold')).pack(pady=(0, 5))

    knowledge_panel = scrolledtext.ScrolledText(knowledge_tab, height=18, width=80,
                                               bg='#f3e5f5', fg=SENTRIGUIDE_THEME['text_primary'],
                                               font=(SENTRIGUIDE_THEME['font_primary'], 9))
    knowledge_panel.pack(fill='both', expand=True, padx=10, pady=(0, 10))
    knowledge_panel.config(state=tk.DISABLED)

def update_all_panels():
    """Update all analysis panels with current data"""
    update_context_panel()
    update_sentiment_panel()
    update_confidence_panel()
    update_knowledge_panel()
    update_coaching_panel()
    update_solution_history_dropdown()

# =============================
# Main SentriGuide Interface
# =============================
def create_sentriguide_interface():
    """Create the modern SentriGuide AI interface"""
    global engineer_chat_window, context_panel, sentiment_panel, confidence_panel, knowledge_panel, coaching_panel, solution_history_panel, solution_history_var, solution_history_dropdown, status_label

    main_window = tk.Tk()
    main_window.title("SentriGuide AI - Support Engineer Conscience")

    # Calculate responsive dimensions for main window
    base_width, base_height = 1500, 950
    scaled_width, scaled_height = calculate_scaled_dimensions(base_width, base_height, SCREEN_INFO)
    main_window.geometry(f"{scaled_width}x{scaled_height}")
    main_window.configure(bg=SENTRIGUIDE_THEME['bg_primary'])

    # Modern window styling
    try:
        main_window.wm_attributes('-alpha', 0.98)  # Slight transparency
    except:
        pass  # Fallback for systems that don't support transparency

    # Make window resizable with minimum size
    main_window.resizable(True, True)
    main_window.minsize(int(1000 * SCALE_FACTOR), int(700 * SCALE_FACTOR))

    # Center window on screen
    x = (SCREEN_INFO['screen_width'] - scaled_width) // 2
    y = (SCREEN_INFO['screen_height'] - scaled_height) // 2
    main_window.geometry(f"{scaled_width}x{scaled_height}+{x}+{y}")

    # Modern Header with Gradient Design
    header_frame = tk.Frame(main_window, bg=SENTRIGUIDE_THEME['primary'], height=int(80 * SCALE_FACTOR))
    header_frame.pack(fill='x')
    header_frame.pack_propagate(False)

    # Header container with better layout
    header_container = tk.Frame(header_frame, bg=SENTRIGUIDE_THEME['primary'])
    header_container.pack(fill='both', expand=True, padx=SENTRIGUIDE_THEME['spacing_xl'], pady=SENTRIGUIDE_THEME['spacing_lg'])

    # Left side - Title and subtitle
    title_section = tk.Frame(header_container, bg=SENTRIGUIDE_THEME['primary'])
    title_section.pack(side='left', fill='y')

    tk.Label(title_section, text="🧠 SentriGuide AI",
            bg=SENTRIGUIDE_THEME['primary'], fg=SENTRIGUIDE_THEME['text_inverse'],
            font=(SENTRIGUIDE_THEME['font_primary'], SENTRIGUIDE_THEME['font_size_display'], 'bold')).pack(anchor='w')

    tk.Label(title_section, text="AI-Powered Conscience for Support Engineers",
            bg=SENTRIGUIDE_THEME['primary'], fg=SENTRIGUIDE_THEME['primary_light'],
            font=(SENTRIGUIDE_THEME['font_primary'], SENTRIGUIDE_THEME['font_size_medium'])).pack(anchor='w')

    # Right side - Status indicators
    status_section = tk.Frame(header_container, bg=SENTRIGUIDE_THEME['primary'])
    status_section.pack(side='right', fill='y')

    # AI Status indicator
    ai_status = tk.Frame(status_section, bg=SENTRIGUIDE_THEME['primary'])
    ai_status.pack(anchor='e', pady=(0, SENTRIGUIDE_THEME['spacing_xs']))

    tk.Label(ai_status, text="🟢 AI Status: Active",
            bg=SENTRIGUIDE_THEME['primary'], fg=SENTRIGUIDE_THEME['text_inverse'],
            font=(SENTRIGUIDE_THEME['font_primary'], SENTRIGUIDE_THEME['font_size_small'])).pack(side='right')

    # System Status
    system_status = tk.Frame(status_section, bg=SENTRIGUIDE_THEME['primary'])
    system_status.pack(anchor='e')

    tk.Label(system_status, text="⚙️ System: Ready",
            bg=SENTRIGUIDE_THEME['primary'], fg=SENTRIGUIDE_THEME['text_inverse'],
            font=(SENTRIGUIDE_THEME['font_primary'], SENTRIGUIDE_THEME['font_size_small'])).pack(side='right')

    # Modern Main Content Area with Card Design
    content_frame = tk.Frame(main_window, bg=SENTRIGUIDE_THEME['bg_primary'])
    content_frame.pack(fill='both', expand=True, padx=SENTRIGUIDE_THEME['spacing_xl'], pady=SENTRIGUIDE_THEME['spacing_lg'])

    # Modern layout with card-based design
    paned_window = tk.PanedWindow(content_frame, orient=tk.HORIZONTAL, bg=SENTRIGUIDE_THEME['bg_primary'],
                                 sashwidth=6, sashrelief='flat', bd=0)
    paned_window.pack(fill='both', expand=True)

    # Left panel - Engineer chat interface with modern card design
    left_panel = tk.Frame(paned_window, bg=SENTRIGUIDE_THEME['bg_surface'], relief='flat', bd=1,
                         highlightbackground=SENTRIGUIDE_THEME['divider'], highlightthickness=1)
    paned_window.add(left_panel, width=int(650 * SCALE_FACTOR), padx=SENTRIGUIDE_THEME['spacing_sm'])

    # Modern left panel header
    left_header = tk.Frame(left_panel, bg=SENTRIGUIDE_THEME['bg_surface'])
    left_header.pack(fill='x', padx=SENTRIGUIDE_THEME['spacing_lg'], pady=(SENTRIGUIDE_THEME['spacing_lg'], SENTRIGUIDE_THEME['spacing_md']))

    tk.Label(left_header, text="💬 Engineer Chat Interface",
            bg=SENTRIGUIDE_THEME['bg_surface'], fg=SENTRIGUIDE_THEME['text_primary'],
            font=(SENTRIGUIDE_THEME['font_primary'], SENTRIGUIDE_THEME['font_size_header'], 'bold')).pack(side='left')

    # Chat status indicator
    tk.Label(left_header, text="🟢 Active",
            bg=SENTRIGUIDE_THEME['bg_surface'], fg=SENTRIGUIDE_THEME['success'],
            font=(SENTRIGUIDE_THEME['font_primary'], SENTRIGUIDE_THEME['font_size_small'])).pack(side='right')

    # Modern engineer chat window with enhanced styling
    engineer_height = max(22, int(28 * SCALE_FACTOR))
    engineer_width = max(55, int(70 * SCALE_FACTOR))

    engineer_chat_window = scrolledtext.ScrolledText(left_panel, height=engineer_height, width=engineer_width,
                                                    bg=SENTRIGUIDE_THEME['bg_surface'], fg=SENTRIGUIDE_THEME['text_primary'],
                                                    font=(SENTRIGUIDE_THEME['font_primary'], SENTRIGUIDE_THEME['font_size_medium']),
                                                    relief='flat', bd=0, wrap='word',
                                                    padx=SENTRIGUIDE_THEME['spacing_md'], pady=SENTRIGUIDE_THEME['spacing_sm'],
                                                    highlightthickness=1, highlightcolor=SENTRIGUIDE_THEME['primary'],
                                                    highlightbackground=SENTRIGUIDE_THEME['divider'])
    engineer_chat_window.pack(fill='both', expand=True, padx=SENTRIGUIDE_THEME['spacing_lg'], pady=(0, SENTRIGUIDE_THEME['spacing_md']))
    engineer_chat_window.config(state=tk.DISABLED)

    # Modern engineer input section
    engineer_input_frame = tk.Frame(left_panel, bg=SENTRIGUIDE_THEME['bg_surface'])
    engineer_input_frame.pack(fill='x', padx=SENTRIGUIDE_THEME['spacing_lg'], pady=(0, SENTRIGUIDE_THEME['spacing_lg']))

    # Input header with modern styling
    input_header = tk.Frame(engineer_input_frame, bg=SENTRIGUIDE_THEME['bg_surface'])
    input_header.pack(fill='x', pady=(0, SENTRIGUIDE_THEME['spacing_sm']))

    tk.Label(input_header, text="⚙️ Your Support Response",
            bg=SENTRIGUIDE_THEME['bg_surface'], fg=SENTRIGUIDE_THEME['text_primary'],
            font=(SENTRIGUIDE_THEME['font_primary'], SENTRIGUIDE_THEME['font_size_medium'], 'bold')).pack(side='left')

    # Response status indicator
    response_status = tk.Label(input_header, text="",
            bg=SENTRIGUIDE_THEME['bg_surface'], fg=SENTRIGUIDE_THEME['text_secondary'],
            font=(SENTRIGUIDE_THEME['font_primary'], SENTRIGUIDE_THEME['font_size_small'], 'italic'))
    response_status.pack(side='right')

    engineer_entry_frame = tk.Frame(engineer_input_frame, bg=SENTRIGUIDE_THEME['bg_surface'])
    engineer_entry_frame.pack(fill='x')

    # Modern engineer entry field
    engineer_entry = tk.Entry(engineer_entry_frame,
                             font=(SENTRIGUIDE_THEME['font_primary'], SENTRIGUIDE_THEME['font_size_medium']),
                             bg=SENTRIGUIDE_THEME['bg_secondary'], fg=SENTRIGUIDE_THEME['text_primary'],
                             relief='flat', bd=1, highlightthickness=2,
                             highlightcolor=SENTRIGUIDE_THEME['success'],
                             highlightbackground=SENTRIGUIDE_THEME['divider'])
    engineer_entry.pack(side='left', fill='x', expand=True, padx=(0, SENTRIGUIDE_THEME['spacing_md']), ipady=SENTRIGUIDE_THEME['spacing_sm'])

    def send_engineer_response():
        global conversation_ended, ended_conversation_display
        message = engineer_entry.get().strip()
        if message:
            # Show sending status
            response_status.config(text="➤ Sending response...")
            main_window.update()

            # Reset conversation ended state when new message is sent
            if conversation_ended:
                conversation_ended = False
                ended_conversation_display = []

            timestamp = datetime.datetime.now().strftime("%H:%M")
            conversation_history.append({"role": "engineer", "content": message, "timestamp": timestamp})

            # Update both chat windows with modern styling
            engineer_chat_window.config(state=tk.NORMAL)
            engineer_chat_window.insert(tk.END, f"\n[{timestamp}] ", "timestamp")
            engineer_chat_window.insert(tk.END, "You", "engineer_name")
            engineer_chat_window.insert(tk.END, f": {message}\n", "engineer_message")
            engineer_chat_window.config(state=tk.DISABLED)
            engineer_chat_window.see(tk.END)

            if customer_simulation_window:
                customer_simulation_window.config(state=tk.NORMAL)
                customer_simulation_window.insert(tk.END, f"\n[{timestamp}] ", "timestamp")
                customer_simulation_window.insert(tk.END, "Support", "engineer_name")
                customer_simulation_window.insert(tk.END, f": {message}\n", "engineer_message")
                customer_simulation_window.config(state=tk.DISABLED)
                customer_simulation_window.see(tk.END)

            engineer_entry.delete(0, tk.END)
            response_status.config(text="")

            # Update session metrics
            update_session_metrics(message)

            # Trigger analysis
            run_sentriguide_analysis()

    # Modern button frame with enhanced styling
    button_frame = tk.Frame(engineer_entry_frame, bg=SENTRIGUIDE_THEME['bg_surface'])
    button_frame.pack(side='right')

    # Modern send response button
    send_response_btn = tk.Button(button_frame, text="➤ Send Response", command=send_engineer_response,
                                 bg=SENTRIGUIDE_THEME['success'], fg=SENTRIGUIDE_THEME['text_inverse'],
                                 font=(SENTRIGUIDE_THEME['font_primary'], SENTRIGUIDE_THEME['font_size_medium'], 'bold'),
                                 relief='flat', bd=0, padx=SENTRIGUIDE_THEME['spacing_lg'], pady=SENTRIGUIDE_THEME['spacing_sm'],
                                 cursor='hand2')
    send_response_btn.pack(side='left', padx=(0, SENTRIGUIDE_THEME['spacing_sm']))

    # Modern end conversation button
    end_conversation_btn = tk.Button(button_frame, text="⏹️ End Conversation", command=end_conversation,
                                    bg=SENTRIGUIDE_THEME['danger'], fg=SENTRIGUIDE_THEME['text_inverse'],
                                    font=(SENTRIGUIDE_THEME['font_primary'], SENTRIGUIDE_THEME['font_size_medium'], 'bold'),
                                    relief='flat', bd=0, padx=SENTRIGUIDE_THEME['spacing_lg'], pady=SENTRIGUIDE_THEME['spacing_sm'],
                                    cursor='hand2')
    end_conversation_btn.pack(side='left')

    # Add modern hover effects
    def on_send_response_hover(event):
        send_response_btn.config(bg=SENTRIGUIDE_THEME['success_light'])
    def on_send_response_leave(event):
        send_response_btn.config(bg=SENTRIGUIDE_THEME['success'])
    def on_end_conversation_hover(event):
        end_conversation_btn.config(bg=SENTRIGUIDE_THEME['danger_light'])
    def on_end_conversation_leave(event):
        end_conversation_btn.config(bg=SENTRIGUIDE_THEME['danger'])

    send_response_btn.bind('<Enter>', on_send_response_hover)
    send_response_btn.bind('<Leave>', on_send_response_leave)
    end_conversation_btn.bind('<Enter>', on_end_conversation_hover)
    end_conversation_btn.bind('<Leave>', on_end_conversation_leave)

    engineer_entry.bind('<Return>', lambda e: send_engineer_response())

    # Right panel - SentriGuide AI panels with modern design
    right_panel = tk.Frame(paned_window, bg=SENTRIGUIDE_THEME['bg_surface'], relief='flat', bd=1,
                          highlightbackground=SENTRIGUIDE_THEME['divider'], highlightthickness=1)
    paned_window.add(right_panel, width=int(800 * SCALE_FACTOR), padx=SENTRIGUIDE_THEME['spacing_sm'])

    # Button to toggle AI Analysis section
    toggle_button_frame = tk.Frame(right_panel, bg=SENTRIGUIDE_THEME['bg_surface'])
    toggle_button_frame.pack(fill='x', padx=SENTRIGUIDE_THEME['spacing_lg'], pady=SENTRIGUIDE_THEME['spacing_lg'])

    # Variable to track if analysis section is expanded
    analysis_expanded = tk.BooleanVar(value=False)

    ai_analysis_btn = tk.Button(toggle_button_frame, text="▶ Show AI Analysis Dashboard",
                               bg=SENTRIGUIDE_THEME['primary'], fg=SENTRIGUIDE_THEME['text_inverse'],
                               font=(SENTRIGUIDE_THEME['font_primary'], SENTRIGUIDE_THEME['font_size_header'], 'bold'),
                               relief='flat', bd=0, padx=SENTRIGUIDE_THEME['spacing_xl'],
                               pady=SENTRIGUIDE_THEME['spacing_lg'], cursor='hand2')
    ai_analysis_btn.pack(fill='x', pady=SENTRIGUIDE_THEME['spacing_md'])

    # Create expandable frame for AI Analysis (initially hidden)
    analysis_container = tk.Frame(right_panel, bg=SENTRIGUIDE_THEME['bg_surface'])

    # Function to toggle the analysis section
    def toggle_analysis_section():
        if analysis_expanded.get():
            # Hide the analysis section
            analysis_container.pack_forget()
            ai_analysis_btn.config(text="▶ Show AI Analysis Dashboard")
            analysis_expanded.set(False)
            # Show info text again
            info_frame.pack(fill='x', padx=SENTRIGUIDE_THEME['spacing_lg'], pady=SENTRIGUIDE_THEME['spacing_md'])
        else:
            # Hide info text
            info_frame.pack_forget()
            # Show the analysis section
            analysis_container.pack(fill='both', expand=True, padx=SENTRIGUIDE_THEME['spacing_md'], pady=(0, SENTRIGUIDE_THEME['spacing_md']))
            ai_analysis_btn.config(text="▼ Hide AI Analysis Dashboard")
            analysis_expanded.set(True)
            # Create the notebook if it doesn't exist
            if not hasattr(analysis_container, 'notebook_created'):
                create_analysis_notebook(analysis_container)
                analysis_container.notebook_created = True

    ai_analysis_btn.config(command=toggle_analysis_section)

    # Add hover effects for the button
    def on_analysis_hover(event):
        ai_analysis_btn.config(bg=SENTRIGUIDE_THEME['primary_light'])
    def on_analysis_leave(event):
        ai_analysis_btn.config(bg=SENTRIGUIDE_THEME['primary'])

    ai_analysis_btn.bind('<Enter>', on_analysis_hover)
    ai_analysis_btn.bind('<Leave>', on_analysis_leave)

    # Info text about the AI Analysis (only shown when collapsed)
    info_frame = tk.Frame(right_panel, bg=SENTRIGUIDE_THEME['bg_surface'])
    info_frame.pack(fill='x', padx=SENTRIGUIDE_THEME['spacing_lg'], pady=SENTRIGUIDE_THEME['spacing_md'])

    info_text = tk.Label(info_frame,
                        text="💡 Click the button above to access:\n\n"
                             "🎯 Context Manager - Conversation tracking\n"
                             "💝 Emotion Alignment - Customer sentiment analysis\n"
                             "✅ Resolution Guard - Case closure prevention\n"
                             "🎯 Coaching Assistant - Performance feedback\n"
                             "📚 Trend Micro Help - Knowledge base integration",
                        bg=SENTRIGUIDE_THEME['bg_surface'], fg=SENTRIGUIDE_THEME['text_secondary'],
                        font=(SENTRIGUIDE_THEME['font_primary'], SENTRIGUIDE_THEME['font_size_medium']),
                        justify='left')
    info_text.pack()

    # Function to hide/show info text based on expansion state
    def update_info_visibility():
        if analysis_expanded.get():
            info_frame.pack_forget()
        else:
            info_frame.pack(fill='x', padx=SENTRIGUIDE_THEME['spacing_lg'], pady=SENTRIGUIDE_THEME['spacing_md'])

    # Store reference for later use
    right_panel.update_info_visibility = update_info_visibility

    # Initialize global panel variables to None (they will be created when expanded)
    context_panel = None
    sentiment_panel = None
    confidence_panel = None
    knowledge_panel = None
    coaching_panel = None
    solution_history_panel = None
    solution_history_var = None
    solution_history_dropdown = None

    # Modern Status bar with enhanced information
    status_frame = tk.Frame(main_window, bg=SENTRIGUIDE_THEME['secondary'], height=int(35 * SCALE_FACTOR))
    status_frame.pack(side='bottom', fill='x')
    status_frame.pack_propagate(False)

    # Status container with better layout
    status_container = tk.Frame(status_frame, bg=SENTRIGUIDE_THEME['secondary'])
    status_container.pack(fill='both', expand=True, padx=SENTRIGUIDE_THEME['spacing_lg'], pady=SENTRIGUIDE_THEME['spacing_sm'])

    # Main status label
    status_label = tk.Label(status_container, text="🧠 SentriGuide AI Ready",
                           bg=SENTRIGUIDE_THEME['secondary'], fg=SENTRIGUIDE_THEME['text_inverse'],
                           font=(SENTRIGUIDE_THEME['font_primary'], SENTRIGUIDE_THEME['font_size_medium']))
    status_label.pack(side='left')

    # Additional status information
    version_label = tk.Label(status_container, text="v2.0 | Modern UI",
                            bg=SENTRIGUIDE_THEME['secondary'], fg=SENTRIGUIDE_THEME['secondary_light'],
                            font=(SENTRIGUIDE_THEME['font_primary'], SENTRIGUIDE_THEME['font_size_small']))
    version_label.pack(side='right')

    # System status indicators
    import datetime
    current_time = datetime.datetime.now().strftime("%H:%M")
    time_label = tk.Label(status_container, text=f"🕰️ {current_time}",
                         bg=SENTRIGUIDE_THEME['secondary'], fg=SENTRIGUIDE_THEME['secondary_light'],
                         font=(SENTRIGUIDE_THEME['font_primary'], SENTRIGUIDE_THEME['font_size_small']))
    time_label.pack(side='right', padx=(0, SENTRIGUIDE_THEME['spacing_lg']))

    # Configure modern chat window tags
    engineer_chat_window.tag_config("timestamp", foreground=SENTRIGUIDE_THEME['text_secondary'], font=(SENTRIGUIDE_THEME['font_primary'], SENTRIGUIDE_THEME['font_size_small']))
    engineer_chat_window.tag_config("customer_name", foreground=SENTRIGUIDE_THEME['primary'], font=(SENTRIGUIDE_THEME['font_primary'], SENTRIGUIDE_THEME['font_size_medium'], 'bold'))
    engineer_chat_window.tag_config("customer_message", foreground=SENTRIGUIDE_THEME['text_primary'], font=(SENTRIGUIDE_THEME['font_primary'], SENTRIGUIDE_THEME['font_size_medium']))
    engineer_chat_window.tag_config("engineer_name", foreground=SENTRIGUIDE_THEME['success'], font=(SENTRIGUIDE_THEME['font_primary'], SENTRIGUIDE_THEME['font_size_medium'], 'bold'))
    engineer_chat_window.tag_config("engineer_message", foreground=SENTRIGUIDE_THEME['text_primary'], font=(SENTRIGUIDE_THEME['font_primary'], SENTRIGUIDE_THEME['font_size_medium']))
    engineer_chat_window.tag_config("system", foreground=SENTRIGUIDE_THEME['warning'], font=(SENTRIGUIDE_THEME['font_primary'], SENTRIGUIDE_THEME['font_size_medium'], 'bold'), justify='center')

    # Legacy tags for backward compatibility
    engineer_chat_window.tag_config("customer", foreground=SENTRIGUIDE_THEME['primary'], font=(SENTRIGUIDE_THEME['font_primary'], SENTRIGUIDE_THEME['font_size_medium'], 'bold'))
    engineer_chat_window.tag_config("engineer", foreground=SENTRIGUIDE_THEME['success'], font=(SENTRIGUIDE_THEME['font_primary'], SENTRIGUIDE_THEME['font_size_medium'], 'bold'))

    # Auto-refresh conversation display
    def refresh_conversation():
        global conversation_ended, ended_conversation_display

        # Skip refresh if conversation has ended (display is already set)
        if conversation_ended:
            main_window.after(2000, refresh_conversation)
            return

        engineer_chat_window.config(state=tk.NORMAL)
        engineer_chat_window.delete(1.0, tk.END)

        for msg in conversation_history:
            timestamp = msg.get('timestamp', datetime.datetime.now().strftime("%H:%M"))
            if msg["role"] == "customer":
                engineer_chat_window.insert(tk.END, f"\n[{timestamp}] ", "timestamp")
                engineer_chat_window.insert(tk.END, "Customer", "customer_name")
                engineer_chat_window.insert(tk.END, f": {msg['content']}\n", "customer_message")
            elif msg["role"] == "engineer":
                engineer_chat_window.insert(tk.END, f"\n[{timestamp}] ", "timestamp")
                engineer_chat_window.insert(tk.END, "You", "engineer_name")
                engineer_chat_window.insert(tk.END, f": {msg['content']}\n", "engineer_message")
            elif msg["role"] == "system":
                engineer_chat_window.insert(tk.END, f"\n[{timestamp}] {msg['content']}\n\n", "system")

        engineer_chat_window.config(state=tk.DISABLED)
        engineer_chat_window.see(tk.END)

        main_window.after(2000, refresh_conversation)

    refresh_conversation()

    return main_window

# =============================
# Main Application
# =============================
def main():
    """Main SentriGuide application with modern Trend Micro Help Center integration"""
    print("🚀 Starting SentriGuide AI v2.0 - Modern Support Engineer Conscience")
    print("🎨 Modern UI Features:")
    print("   • Material Design 3.0 inspired color palette")
    print("   • Enhanced typography with Inter font stack")
    print("   • Responsive card-based layout design")
    print("   • Modern hover effects and smooth animations")
    print("   • Improved accessibility and contrast ratios")
    print("📋 Addressing 5 major chat operation challenges:")
    print("   1. Context loss in long conversations")
    print("   2. Emotional misalignment with customers")
    print("   3. Premature case resolution")
    print("   4. Inefficient Trend Micro knowledge searching")
    print("   5. Performance coaching and real-time feedback")
    print(f"📱 Responsive UI scaling: {SCALE_FACTOR:.2f}x ({SCREEN_INFO['screen_width']}x{SCREEN_INFO['screen_height']})")
    print(f"🎨 Modern design system with 8px grid and improved spacing")

    # Setup system (no API required)
    if not setup_system():
        print("❌ Failed to setup system")
        return

    try:
        # Create main interface
        main_window = create_sentriguide_interface()

        # Automatically create customer simulation window
        main_window.after(500, create_customer_simulation)

        print("✅ SentriGuide AI v2.0 is ready with modern UI!")
        print("💡 Use the modern customer simulation to test the AI conscience")
        print("🧠 SentriGuide will analyze every interaction and provide:")
        print("   • Smart context summaries for long conversations")
        print("   • Advanced sentiment analysis and tone recommendations")
        print("   • AI-powered resolution confidence scoring")
        print("   • Dynamic Trend Micro Help Center knowledge surfacing")
        print("   • Real-time performance coaching and feedback")
        print("   • Modern, responsive UI with enhanced user experience")
        print("🎨 Modern Design Features:")
        print("   • Card-based layout with subtle shadows")
        print("   • Modern color palette and typography")
        print("   • Enhanced button interactions and hover effects")
        print("   • Improved accessibility and readability")

        # Start the application
        main_window.mainloop()

    except Exception as e:
        print(f"❌ Application error: {str(e)}")
        messagebox.showerror("SentriGuide Error", f"Application error: {str(e)}")

if __name__ == "__main__":
    main()