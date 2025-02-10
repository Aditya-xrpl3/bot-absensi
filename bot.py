from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, CommandHandler, ContextTypes
from datetime import datetime

# Data absensi
absensi = {}
tanggal_terakhir = None  # Untuk menyimpan tanggal terakhir absensi
GROUP_CHAT_ID = -1002454995237  # Ganti dengan ID grup Anda
MESSAGE_ID = None  # Menyimpan ID pesan daftar absensi


# Fungsi untuk membuat tombol absensi
def buat_tombol_absen():
    keyboard = [
        [InlineKeyboardButton("Absen Sekarang", callback_data="absen")]
    ]
    return InlineKeyboardMarkup(keyboard)


# Fungsi untuk menangani perintah /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.message.from_user
    await update.message.reply_text(
        text="Halo! Selamat datang di bot absensi sederhana. Tekan tombol di bawah untuk melakukan absensi.",
        reply_markup=buat_tombol_absen(),
    )


# Callback untuk tombol absen
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global absensi, tanggal_terakhir

    query = update.callback_query
    await query.answer()  # Respon agar tombol tidak terlihat "loading"

    user = query.from_user
    now = datetime.now()
    today_date = now.strftime("%Y-%m-%d")  # Format tanggal saat ini (YYYY-MM-DD)
    time = now.strftime("%Y-%m-%d %H:%M:%S")

    # Reset data absensi jika hari berganti
    if tanggal_terakhir != today_date:
        absensi = {}  # Bersihkan data absensi
        tanggal_terakhir = today_date  # Perbarui tanggal terakhir

    # Cek apakah user sudah absen
    if user.id not in absensi:
        absensi[user.id] = {"name": user.full_name, "time": time}
        await query.edit_message_text(
            text=f"Terima kasih, {user.full_name}! Anda telah absen pada {time}."
        )

        # Kirim atau perbarui laporan absensi di grup
        await kirim_laporan_ke_grup(context)
    else:
        await query.edit_message_text(
            text=f"Halo, {user.full_name}! Anda sudah absen sebelumnya pada {absensi[user.id]['time']}."
        )


# Fungsi untuk mengirim atau memperbarui laporan absensi ke grup
async def kirim_laporan_ke_grup(context: ContextTypes.DEFAULT_TYPE) -> None:
    global MESSAGE_ID
    if absensi:
        response = "📋 *Daftar Absensi:*\n\n"
        for i, (user_id, data) in enumerate(absensi.items(), start=1):
            response += f"{i}. {data['name']} pada {data['time']}\n"

        if MESSAGE_ID is None:  # Jika pesan belum pernah dikirim
            sent_message = await context.bot.send_message(
                chat_id=GROUP_CHAT_ID, text=response, parse_mode="Markdown"
            )
            MESSAGE_ID = sent_message.message_id
        else:  # Jika pesan sudah ada, perbarui pesan tersebut
            await context.bot.edit_message_text(
                chat_id=GROUP_CHAT_ID,
                message_id=MESSAGE_ID,
                text=response,
                parse_mode="Markdown",
            )
    else:
        # Tidak ada yang absen
        if MESSAGE_ID is not None:
            await context.bot.edit_message_text(
                chat_id=GROUP_CHAT_ID,
                message_id=MESSAGE_ID,
                text="Belum ada yang absen hari ini.",
                parse_mode="Markdown",
            )


# Fungsi utama
def main():
    # Masukkan API Token Anda di sini
    API_TOKEN = "8026635161:AAEJ_Spgp6zMTGmr3LW2H7iNcqdJ572Shsg"

    # Bangun aplikasi bot
    application = ApplicationBuilder().token(API_TOKEN).build()

    # Daftarkan handler
    application.add_handler(CommandHandler("start", start))  # Menangani perintah /start
    application.add_handler(CallbackQueryHandler(button_handler))  # Menangani klik tombol

    # Jalankan bot
    application.run_polling()


if __name__ == '__main__':
    main()
