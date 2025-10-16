"""
Internationalization support for permission system
Translations, locale management, and text formatting
"""

import sys
from typing import Dict, List, Optional, Any


class I18nManager:
    """Manages internationalization for permission prompts (Constitution compliant)"""
    
    def __init__(self, enabled: bool = True, default_locale: str = 'en'):
        self._enabled = enabled
        self._current_locale = default_locale
        self._translations = self._load_default_translations()
    
    def _load_default_translations(self) -> Dict[str, Dict[str, str]]:
        """Load default translations (Constitution compliant - memory efficient)"""
        return {
            'en': {
                'permission': 'Permission',
                'cancel': 'Cancel',
                'confirm': 'Confirm',
                'yes': 'Yes',
                'no': 'No',
                'allow': 'Allow',
                'deny': 'Deny',
                'help': 'Help',
                'option': 'Option',
                'of': 'of',
                'press_f1_help': 'Press F1 for help',
                'press_esc_cancel': 'Press ESC to cancel',
                'currently_selected': 'Currently selected',
                'options_available': 'Options available',
                'choices': 'choices',
                'accessibility_help': 'Accessibility Help',
            },
            'es': {
                'permission': 'Permiso',
                'cancel': 'Cancelar',
                'confirm': 'Confirmar',
                'yes': 'Sí',
                'no': 'No',
                'allow': 'Permitir',
                'deny': 'Denegar',
                'help': 'Ayuda',
                'option': 'Opción',
                'of': 'de',
                'press_f1_help': 'Presiona F1 para ayuda',
                'press_esc_cancel': 'Presiona ESC para cancelar',
                'currently_selected': 'Actualmente seleccionado',
                'options_available': 'Opciones disponibles',
                'choices': 'opciones',
                'accessibility_help': 'Ayuda de Accesibilidad',
            },
            'fr': {
                'permission': 'Permission',
                'cancel': 'Annuler',
                'confirm': 'Confirmer',
                'yes': 'Oui',
                'no': 'Non',
                'allow': 'Autoriser',
                'deny': 'Refuser',
                'help': 'Aide',
                'option': 'Option',
                'of': 'de',
                'press_f1_help': 'Appuyez sur F1 pour l\'aide',
                'press_esc_cancel': 'Appuyez sur ESC pour annuler',
                'currently_selected': 'Actuellement sélectionné',
                'options_available': 'Options disponibles',
                'choices': 'choix',
                'accessibility_help': 'Aide d\'Accessibilité',
            },
            'de': {
                'permission': 'Berechtigung',
                'cancel': 'Abbrechen',
                'confirm': 'Bestätigen',
                'yes': 'Ja',
                'no': 'Nein',
                'allow': 'Erlauben',
                'deny': 'Verweigern',
                'help': 'Hilfe',
                'option': 'Option',
                'of': 'von',
                'press_f1_help': 'Drücken Sie F1 für Hilfe',
                'press_esc_cancel': 'Drücken Sie ESC zum Abbrechen',
                'currently_selected': 'Aktuell ausgewählt',
                'options_available': 'Verfügbare Optionen',
                'choices': 'Auswahlmöglichkeiten',
                'accessibility_help': 'Barrierefreiheit-Hilfe',
            }
        }

    def set_locale(self, locale: str) -> bool:
        """Set current locale for internationalization (Constitution compliant)"""
        if not self._enabled:
            return False
            
        if locale in self._translations:
            self._current_locale = locale
            sys.stderr.write(f"[PermissionManager] Locale set to: {locale}\n")
            sys.stderr.flush()
            return True
        
        sys.stderr.write(f"[PermissionManager] Unsupported locale: {locale}\n")
        sys.stderr.flush()
        return False

    def get_translation(self, key: str, fallback: str = None) -> str:
        """Get translated text for current locale (Constitution compliant)"""
        if not self._enabled:
            return fallback or key
            
        locale_translations = self._translations.get(self._current_locale, {})
        translated = locale_translations.get(key)
        
        if translated:
            return translated
        
        # Fallback to English
        en_translations = self._translations.get('en', {})
        english_text = en_translations.get(key)
        
        if english_text:
            return english_text
        
        # Ultimate fallback
        return fallback or key

    def add_custom_translation(self, locale: str, key: str, value: str) -> None:
        """Add custom translation (Constitution compliant)"""
        if locale not in self._translations:
            self._translations[locale] = {}
        
        self._translations[locale][key] = value

    def get_supported_locales(self) -> List[str]:
        """Get list of supported locales (Constitution compliant)"""
        return list(self._translations.keys())
    
    @property
    def enabled(self) -> bool:
        """Check if i18n is enabled"""
        return self._enabled
    
    @property
    def current_locale(self) -> str:
        """Get current locale"""
        return self._current_locale