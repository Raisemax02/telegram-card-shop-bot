"""Italian (it) locale — UI strings."""

from __future__ import annotations

LANG_CODE = "it"
LANG_NAME = "Italiano"
FLAG = "🇮🇹"

# --- Language Selection -------------------------------------------------------
MSG_SELECT_LANGUAGE = "🌍 **Select your language / Seleziona la lingua:**"
MSG_LANGUAGE_CHANGED = "✅ Lingua impostata su Italiano"

# --- Main Menu ----------------------------------------------------------------
MSG_START = (
    "👋 **Benvenuto nel Negozio di Carte Collezionabili!**\n\n"
    "🃏 Sfoglia le nostre categorie per vedere le carte disponibili "
    "e le loro condizioni tramite video.\n\n"
    "Scegli un'opzione qui sotto ⬇️"
)

MSG_CATEGORIES_MENU = "📂 **Categorie**\n\nScegli una categoria per sfogliare le carte:"

# --- Info & Contacts ----------------------------------------------------------
MSG_INFO = (
    "🏢 **Info Negozio**\n\n"
    "📍 Aperti Lun-Sab, 9:00 – 19:00\n"
    "🃏 Carte Yu-Gi-Oh!, Pokémon, Magic e altro\n\n"
    "Usa i tasti qui sotto per navigare ⬇️"
)

MSG_CONTACTS = (
    "📞 **Contatti**\n\n📱 Tel: 0123-456789\n📧 Email: info@negozio.it\n\nUsa i tasti qui sotto per navigare ⬇️"
)

# --- Reviews ------------------------------------------------------------------
MSG_REVIEWS_TITLE = "⭐ **Recensioni Carte**\n\n"
ROW_CARD_REVIEW = "🏷 {title}: ⭐ {average:.1f} ({count} recensioni)\n"
ROW_OVERALL_RATING = "\n📊 **Voto Complessivo:** ⭐ {average:.1f} ({total} recensioni totali)"
NO_REVIEWS = "Nessuna recensione ancora ricevuta."
ERR_REVIEWS_LOAD = "⚠️ Errore nel caricamento delle recensioni."

MSG_START_REVIEW = "⭐ **Recensione per {title}**\n\nScegli un voto da 1 a 5 stelle:"
MSG_WRITE_COMMENT = "⭐ **Voto:** {rating} stelle per {title}\n\nScrivi un commento (opzionale, max 200 caratteri):"
CONFIRM_REVIEW = "✅ Recensione salvata! Grazie per il feedback. ⭐"
MSG_REVIEW_SAVED = "✅ Recensione salvata!"
ERR_SAVE_REVIEW = "⚠️ Errore nel salvataggio della recensione."

# --- Admin Panel --------------------------------------------------------------
MSG_ADMIN_PANEL = "🔐 **Pannello Admin**\n\nScegli la categoria dove operare:"

# --- FSM: Card Upload ---------------------------------------------------------
MSG_WRITE_TITLE = (
    "📝 Aggiungo in **{cat_name}**\n\nScrivi il **NOME/TITOLO** della carta:\n_(massimo {max_len} caratteri)_"
)
MSG_TITLE_OK = "✅ Titolo: **{title}**\n\n🎥 **Ora invia il VIDEO** della carta."
MSG_VIDEO_OK = "✅ Video ricevuto!\n\n📝 **Scrivi ora la Descrizione e il Prezzo**:\n\n_(massimo {max_len} caratteri)_"
MSG_CARD_PUBLISHED = "✅ **Carta pubblicata con successo!**"
MSG_CARD_DELETED = "🗑 Carta eliminata!"

# --- Delete Confirmation ------------------------------------------------------
MSG_CONFIRM_DELETE = (
    "🗑 **Conferma Eliminazione**\n\nVuoi eliminare la carta **{title}**?\n\n⚠️ Questa azione è **irreversibile**."
)

# --- Category -----------------------------------------------------------------
MSG_CATEGORY = "📂 **{cat_name}**"
NO_CARDS = "\n\n📭 Nessuna carta disponibile al momento."

# --- Warnings / Errors --------------------------------------------------------
WARN_SESSION_EXPIRED = "⏰ **Sessione scaduta per inattività.** Riprova dall'inizio."
WARN_TEXT_REQUIRED = "⚠️ Devi scrivere un testo per il titolo, non mandare file."
WARN_TITLE_TOO_LONG = "⚠️ Titolo troppo lungo. Massimo {max} caratteri."
WARN_VIDEO_REQUIRED = "⚠️ Devi inviare un **video**, non un messaggio di testo o altro file."
WARN_VIDEO_TOO_LARGE = "⚠️ Video troppo grande. Massimo {max} MB."
WARN_DESCRIPTION_REQUIRED = "⚠️ Scrivi una descrizione testuale."
WARN_DESCRIPTION_TOO_LONG = "⚠️ Descrizione troppo lunga. Massimo {max} caratteri."
WARN_MISSING_DATA = "⚠️ Errore: dati mancanti. Riprova dall'inizio."
WARN_INVALID_CATEGORY = "⚠️ Categoria non valida."
WARN_ACCESS_DENIED = "⛔️ Accesso negato"
WARN_CARD_NOT_FOUND = "Carta non trovata."
WARN_VIDEO_UNAVAILABLE = "⚠️ Video non disponibile."
WARN_SAVE_ERROR = "⚠️ Errore durante il salvataggio. Riprova."
WARN_DELETE_ERROR = "⚠️ Errore durante la cancellazione"
WARN_COMMENT_TOO_LONG = "Commento troppo lungo. Max 200 caratteri."
WARN_WRITE_COMMENT = "Scrivi un commento o usa il tasto 'Salta commento'."
WARN_SPAM = "⛔️ **Usa solo i tasti del menu!**"
WARN_ALREADY_REVIEWED = "⚠️ Hai già lasciato una recensione per questa carta."
WARN_INVALID_VIDEO_FORMAT = "⚠️ Formato video non valido. Usa: MP4, MOV, AVI, MKV, WebM."
WARN_REVIEW_RATE_LIMIT = "⚠️ Hai raggiunto il limite di recensioni. Riprova tra {minutes} minuti."

# --- Labels -------------------------------------------------------------------
LBL_RATING = "Voto"
LBL_REVIEWS = "recensioni"

# --- Button Labels ------------------------------------------------------------
BTN_MENU_CARDS = "📂  Menu Carte"
BTN_REVIEWS = "⭐  Recensioni"
BTN_INFO = "ℹ️ Info"
BTN_CONTACTS = "📞 Contatti"
BTN_BACK = "🔙 Indietro"
BTN_CANCEL = "❌ Annulla"
BTN_ADD_CARD = "AGGIUNGI CARTA"
BTN_SKIP_COMMENT = "Salta commento"
BTN_DELETE = "🗑"
BTN_YES_DELETE = "Sì, elimina"
BTN_LEAVE_REVIEW = "Lascia Recensione"
BTN_LANGUAGE = "🌍 Lingua"
BTN_CATEGORIES_MENU = "Menu Categorie"
BTN_BACK_TO_CAT = "Torna a {cat_name}"

# --- Pagination ---------------------------------------------------------------
BTN_PREVIOUS = "◀️ Indietro"
BTN_NEXT = "Avanti ▶️"
LBL_PAGE = "Pagina"

# --- Admin: Update Video ------------------------------------------------------
MSG_UPDATE_VIDEO = (
    "📹 **Aggiorna Video**\n\n"
    "🏷 **Carta:** {title}\n\n"
    "Invia il nuovo video per questa carta.\n\n"
    "⚠️ Il video precedente sarà sostituito."
)
MSG_VIDEO_UPDATED = (
    "✅ **Video aggiornato con successo!**\n\nIl nuovo video è stato salvato e il file YAML è stato aggiornato."
)
WARN_VIDEO_UPDATE_ERROR = "❌ Errore durante l'aggiornamento del video. Riprova più tardi."

# --- Admin: Update Title ------------------------------------------------------
MSG_UPDATE_TITLE = (
    "✏️ **Modifica Titolo**\n\n"
    "📝 **Titolo Attuale:** {title}\n\n"
    "Invia il nuovo titolo per questa carta.\n\n"
    "⚠️ Max {max_len} caratteri."
)
MSG_TITLE_UPDATED = "✅ **Titolo aggiornato con successo!**\n\n📝 **Nuovo Titolo:** {title}"
WARN_TITLE_UPDATE_ERROR = "❌ Errore durante l'aggiornamento del titolo. Riprova più tardi."
WARN_TITLE_EMPTY = "⚠️ Il titolo non può essere vuoto."
WARN_TITLE_UPDATE_TOO_LONG = (
    "⚠️ Titolo troppo lungo. Max {max_len} caratteri.\n\nLunghezza attuale: {current_len} caratteri."
)

# --- Admin: Update Description ------------------------------------------------
MSG_UPDATE_DESCRIPTION = (
    "📝 **Modifica Descrizione**\n\n"
    "🏷 **Carta:** {title}\n\n"
    "📄 **Descrizione Attuale:**\n{description}\n\n"
    "Invia la nuova descrizione per questa carta.\n\n"
    "⚠️ Max {max_len} caratteri."
)
MSG_DESCRIPTION_UPDATED = "✅ **Descrizione aggiornata con successo!**\n\nLa nuova descrizione è stata salvata e il file YAML è stato aggiornato."
WARN_DESCRIPTION_UPDATE_ERROR = "❌ Errore durante l'aggiornamento della descrizione. Riprova più tardi."
WARN_DESCRIPTION_EMPTY = "⚠️ La descrizione non può essere vuota."
WARN_DESCRIPTION_UPDATE_TOO_LONG = (
    "⚠️ Descrizione troppo lunga. Max {max_len} caratteri.\n\nLunghezza attuale: {current_len} caratteri."
)

# --- Admin: Card View Buttons -------------------------------------------------
BTN_EDIT_TITLE = "✏️ Titolo"
BTN_EDIT_DESCRIPTION = "📝 Descrizione"
BTN_UPDATE_VIDEO = "📹 Aggiorna Video"
BTN_BACK_TO_CATEGORY = "🔙 Torna alla Categoria"
BTN_VIEW_CARD = "👁️ Visualizza Carta"
