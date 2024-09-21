import logging
import os
import json
from datetime import datetime
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackContext
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Configura il logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Stati della conversazione
(CHOOSING, TYPING_NUMBER, TYPING_DATE, TYPING_DESCRIPTION, CHOOSING_TYPE, CHOOSING_CLASS,
 CONFIRMATION, RESTART_OR_END, CANCEL_CONFIRMATION) = range(9)

# Ottieni il token del bot dalle variabili d'ambiente
BOT_TOKEN = os.environ['BOT_TOKEN']

# Definisci l'ID utente autorizzato
AUTHORIZED_USER_ID = 563155342  # Sostituisci con il tuo ID utente

# Configura le credenziali di Google Sheets
def authorize_google_sheets():
    creds_json = os.environ['CREDS_JSON']
    creds_dict = json.loads(creds_json)
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    sheet = client.open('Budget').sheet1  # Sostituisci con il nome del tuo sheet
    return sheet

sheet = authorize_google_sheets()

# Lista dei tipi aggiornata
type_options = [
    'Abbonamenti Digitali', 'Affitto', 'Assicurazione', 'Autostrada', 'Bar',
    'Beauty', 'Beneficienza', 'Benzina', 'Cane', 'Cibo', 'Delivery', 'Health',
    'Leisure', 'Macchina', 'Parcheggio', 'Regali', 'Ristorante', 'Saving',
    'Shopping', 'Spese Conto', 'Supermercato', 'Tasse', 'Utenze', 'Vacanze',
    'Viaggi', 'Pensione', 'Proventi', 'Rimborsi', 'Stipendio'
]

# Tastiera con il pulsante "Annulla"
cancel_keyboard = ReplyKeyboardMarkup(
    [['Annulla']],
    one_time_keyboard=False,
    resize_keyboard=True
)

# Decorator per controllare l'autorizzazione
def authorized_user(func):
    def wrapper(update: Update, context: CallbackContext, *args, **kwargs):
        user_id = update.effective_user.id
        if user_id != AUTHORIZED_USER_ID:
            update.message.reply_text('Non sei autorizzato ad utilizzare questo bot.')
            return ConversationHandler.END
        return func(update, context, *args, **kwargs)
    return wrapper

# Funzioni della conversazione con il decorator
@authorized_user
def start(update: Update, context: CallbackContext) -> int:
    logging.info("Avviato comando /start")
    reply_keyboard = [['SI', 'NO', 'Annulla']]
    update.message.reply_text(
        'Vuoi inserire un nuovo movimento?',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
    )
    return CHOOSING

@authorized_user
def choosing(update: Update, context: CallbackContext) -> int:
    user_reply = update.message.text.casefold()
    logging.info(f"Stato: CHOOSING, Input utente: {user_reply}")
    if user_reply == 'si':
        update.message.reply_text(
            'Perfetto! Inserisci l\'importo (può essere positivo o negativo, massimo due cifre decimali).',
            reply_markup=cancel_keyboard
        )
        context.user_data['current_state'] = TYPING_NUMBER
        return TYPING_NUMBER
    elif user_reply == 'no':
        update.message.reply_text('Ok, se hai bisogno, scrivimi /start per ricominciare.')
        return ConversationHandler.END
    elif user_reply == 'annulla':
        return cancel_entry(update, context)
    else:
        update.message.reply_text(
            'Per favore, rispondi con SI, NO o Annulla.',
            reply_markup=ReplyKeyboardMarkup([['SI', 'NO', 'Annulla']], one_time_keyboard=True, resize_keyboard=True)
        )
        context.user_data['current_state'] = CHOOSING
        return CHOOSING

@authorized_user
def received_number(update: Update, context: CallbackContext) -> int:
    user_input = update.message.text.replace(',', '.')
    logging.info(f"Stato: TYPING_NUMBER, Input utente: {user_input}")
    if user_input.casefold() == 'annulla':
        return cancel_entry(update, context)
    try:
        amount = float(user_input)
        amount = round(amount, 2)
        context.user_data['amount'] = amount
        update.message.reply_text(
            'Inserisci la data (formato DD/MM/YYYY) o scrivi "oggi" per usare la data odierna.',
            reply_markup=cancel_keyboard
        )
        context.user_data['current_state'] = TYPING_DATE
        return TYPING_DATE
    except ValueError:
        update.message.reply_text(
            'Per favore, inserisci un numero valido (es. 123.45 o -67.89).',
            reply_markup=cancel_keyboard
        )
        context.user_data['current_state'] = TYPING_NUMBER
        return TYPING_NUMBER

@authorized_user
def received_date(update: Update, context: CallbackContext) -> int:
    user_input = update.message.text.casefold()
    logging.info(f"Stato: TYPING_DATE, Input utente: {user_input}")
    if user_input == 'annulla':
        return cancel_entry(update, context)
    if user_input == 'oggi':
        date = datetime.now().strftime('%d/%m/%Y')
    else:
        try:
            date_obj = datetime.strptime(user_input, '%d/%m/%Y')
            date = date_obj.strftime('%d/%m/%Y')
        except ValueError:
            update.message.reply_text(
                'Per favore, inserisci la data nel formato DD/MM/YYYY o scrivi "oggi".',
                reply_markup=cancel_keyboard
            )
            context.user_data['current_state'] = TYPING_DATE
            return TYPING_DATE
    context.user_data['date'] = date
    update.message.reply_text(
        'Inserisci una descrizione per il movimento.',
        reply_markup=cancel_keyboard
    )
    context.user_data['current_state'] = TYPING_DESCRIPTION
    return TYPING_DESCRIPTION

@authorized_user
def received_description(update: Update, context: CallbackContext) -> int:
    user_input = update.message.text
    logging.info(f"Stato: TYPING_DESCRIPTION, Input utente: {user_input}")
    if user_input.casefold() == 'annulla':
        return cancel_entry(update, context)
    description = user_input
    context.user_data['description'] = description

    # Creiamo la lista numerata dei tipi
    type_list = ''
    for idx, tipo in enumerate(type_options, start=1):
        type_list += f"{idx}. {tipo}\n"

    update.message.reply_text(
        'Seleziona il tipo inserendo il numero corrispondente:\n\n' + type_list,
        reply_markup=cancel_keyboard
    )
    context.user_data['current_state'] = CHOOSING_TYPE
    return CHOOSING_TYPE

@authorized_user
def received_type(update: Update, context: CallbackContext) -> int:
    user_input = update.message.text
    logging.info(f"Stato: CHOOSING_TYPE, Input utente: {user_input}")
    if user_input.casefold() == 'annulla':
        return cancel_entry(update, context)
    try:
        selected_index = int(user_input)
        if 1 <= selected_index <= len(type_options):
            selected_type = type_options[selected_index - 1]
            context.user_data['type'] = selected_type
            # Passiamo alla scelta della classe
            class_options = ['L', 'N', 'S', 'E', 'Annulla']
            reply_keyboard = [class_options]
            update.message.reply_text(
                'Seleziona la classe (L, N, S, E):',
                reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
            )
            context.user_data['current_state'] = CHOOSING_CLASS
            return CHOOSING_CLASS
        else:
            update.message.reply_text(
                f'Per favore, inserisci un numero valido tra 1 e {len(type_options)}.',
                reply_markup=cancel_keyboard
            )
            context.user_data['current_state'] = CHOOSING_TYPE
            return CHOOSING_TYPE
    except ValueError:
        update.message.reply_text(
            'Per favore, inserisci un numero valido.',
            reply_markup=cancel_keyboard
        )
        context.user_data['current_state'] = CHOOSING_TYPE
        return CHOOSING_TYPE

@authorized_user
def received_class(update: Update, context: CallbackContext) -> int:
    selected_class = update.message.text.upper()
    logging.info(f"Stato: CHOOSING_CLASS, Input utente: {selected_class}")
    if selected_class.casefold() == 'annulla':
        return cancel_entry(update, context)
    if selected_class in ['L', 'N', 'S', 'E']:
        context.user_data['class'] = selected_class
        amount = context.user_data['amount']
        date = context.user_data['date']
        description = context.user_data['description']
        selected_type = context.user_data['type']
        reply_keyboard = [['SI', 'NO', 'Annulla']]
        update.message.reply_text(
            f"Confermi di voler inserire:\n"
            f"Importo: {amount}\n"
            f"Data: {date}\n"
            f"Descrizione: {description}\n"
            f"Tipo: {selected_type}\n"
            f"Classe: {selected_class}\n"
            f"Rispondi con SI per confermare o NO per annullare.",
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
        )
        context.user_data['current_state'] = CONFIRMATION
        return CONFIRMATION
    else:
        update.message.reply_text(
            'Per favore, seleziona una classe valida (L, N, S, E).',
            reply_markup=cancel_keyboard
        )
        context.user_data['current_state'] = CHOOSING_CLASS
        return CHOOSING_CLASS

@authorized_user
def confirm(update: Update, context: CallbackContext) -> int:
    user_reply = update.message.text.casefold()
    logging.info(f"Stato: CONFIRMATION, Input utente: {user_reply}")
    if user_reply == 'si':
        data = [
            context.user_data['amount'],
            context.user_data['date'],
            context.user_data['description'],
            context.user_data['type'],
            context.user_data['class']
        ]
        try:
            sheet.append_row(data)
            update.message.reply_text('Movimento inserito con successo!', reply_markup=cancel_keyboard)
        except Exception as e:
            logging.error(f"Errore durante l'inserimento dei dati: {e}")
            update.message.reply_text('Si è verificato un errore durante l\'inserimento dei dati.', reply_markup=cancel_keyboard)
        finally:
            context.user_data.clear()

        # Chiedi se l'utente vuole inserire un altro movimento
        reply_keyboard = [['SI', 'NO', 'Annulla']]
        update.message.reply_text(
            'Vuoi inserire un altro movimento?',
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
        )
        context.user_data['current_state'] = RESTART_OR_END
        return RESTART_OR_END
    elif user_reply == 'no':
        update.message.reply_text('Inserimento annullato.', reply_markup=cancel_keyboard)
        context.user_data.clear()
        # Chiedi se l'utente vuole inserire un nuovo movimento
        reply_keyboard = [['SI', 'NO', 'Annulla']]
        update.message.reply_text(
            'Vuoi inserire un nuovo movimento?',
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
        )
        context.user_data['current_state'] = CHOOSING
        return CHOOSING
    elif user_reply == 'annulla':
        return cancel_entry(update, context)
    else:
        update.message.reply_text(
            'Per favore, rispondi con SI, NO o Annulla.',
            reply_markup=ReplyKeyboardMarkup([['SI', 'NO', 'Annulla']], one_time_keyboard=True, resize_keyboard=True)
        )
        context.user_data['current_state'] = CONFIRMATION
        return CONFIRMATION

@authorized_user
def restart_or_end(update: Update, context: CallbackContext) -> int:
    user_reply = update.message.text.casefold()
    logging.info(f"Stato: RESTART_OR_END, Input utente: {user_reply}")
    if user_reply == 'si':
        update.message.reply_text(
            'Perfetto! Inserisci l\'importo (può essere positivo o negativo, massimo due cifre decimali).',
            reply_markup=cancel_keyboard
        )
        context.user_data['current_state'] = TYPING_NUMBER
        return TYPING_NUMBER
    elif user_reply == 'no':
        update.message.reply_text('Grazie per aver utilizzato il bot. Alla prossima!')
        return ConversationHandler.END
    elif user_reply == 'annulla':
        return cancel_entry(update, context)
    else:
        update.message.reply_text(
            'Per favore, rispondi con SI, NO o Annulla.',
            reply_markup=ReplyKeyboardMarkup([['SI', 'NO', 'Annulla']], one_time_keyboard=True, resize_keyboard=True)
        )
        context.user_data['current_state'] = RESTART_OR_END
        return RESTART_OR_END

@authorized_user
def cancel_entry(update: Update, context: CallbackContext) -> int:
    # Salviamo lo stato corrente
    context.user_data['previous_state'] = context.user_data.get('current_state')
    reply_keyboard = [['SI', 'NO']]
    update.message.reply_text(
        'Sei sicuro di voler annullare l\'inserimento?',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
    )
    return CANCEL_CONFIRMATION

@authorized_user
def confirm_cancel_entry(update: Update, context: CallbackContext) -> int:
    user_reply = update.message.text.casefold()
    logging.info(f"Stato: CANCEL_CONFIRMATION, Input utente: {user_reply}")
    if user_reply == 'si':
        context.user_data.clear()
        reply_keyboard = [['SI', 'NO', 'Annulla']]
        update.message.reply_text(
            'Inserimento annullato. Vuoi inserire un nuovo movimento?',
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
        )
        context.user_data['current_state'] = CHOOSING
        return CHOOSING
    elif user_reply == 'no':
        update.message.reply_text(
            'Ok, continuiamo con l\'inserimento.',
            reply_markup=cancel_keyboard
        )
        # Torniamo allo stato precedente salvato
        previous_state = context.user_data.get('previous_state', CHOOSING)
        context.user_data['current_state'] = previous_state
        return previous_state
    else:
        update.message.reply_text(
            'Per favore, rispondi con SI o NO.',
            reply_markup=ReplyKeyboardMarkup([['SI', 'NO']], one_time_keyboard=True, resize_keyboard=True)
        )
        return CANCEL_CONFIRMATION

def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CHOOSING: [MessageHandler(Filters.text & ~Filters.command, choosing)],
            TYPING_NUMBER: [MessageHandler(Filters.text & ~Filters.command, received_number)],
            TYPING_DATE: [MessageHandler(Filters.text & ~Filters.command, received_date)],
            TYPING_DESCRIPTION: [MessageHandler(Filters.text & ~Filters.command, received_description)],
            CHOOSING_TYPE: [MessageHandler(Filters.text & ~Filters.command, received_type)],
            CHOOSING_CLASS: [MessageHandler(Filters.text & ~Filters.command, received_class)],
            CONFIRMATION: [MessageHandler(Filters.text & ~Filters.command, confirm)],
            RESTART_OR_END: [MessageHandler(Filters.text & ~Filters.command, restart_or_end)],
            CANCEL_CONFIRMATION: [MessageHandler(Filters.text & ~Filters.command, confirm_cancel_entry)],
        },
        fallbacks=[CommandHandler('cancel', cancel_entry)],
    )
    dp.add_handler(conv_handler)

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
