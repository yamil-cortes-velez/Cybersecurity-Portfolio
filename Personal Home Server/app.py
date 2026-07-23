from flask import Flask, render_template, session, redirect, url_for, request, send_from_directory
from database import db, Device
from config import SECRET_KEY, PIN, UPLOAD_FOLDER, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
import os
import telegram

app = Flask(__name__)
app.secret_key = SECRET_KEY
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///devices.db"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

db.init_app(app)

with app.app_context():
    db.create_all()

# check if user is unlocked
def is_unlocked():
    return session.get("unlocked") == True

# home screen
@app.route("/")
def index():
    return render_template("index.html", unlocked=is_unlocked())

# pin check
@app.route("/unlock", methods=["POST"])
def unlock():
    entered_pin = request.form.get("pin")
    if entered_pin == PIN:
        session["unlocked"] = True
    return redirect(url_for("index"))

# lock
@app.route("/lock")
def lock():
    session["unlocked"] = False
    return redirect(url_for("index"))

# files page
@app.route("/files")
def files():
    if not is_unlocked():
        return redirect(url_for("index"))
    file_list = os.listdir(UPLOAD_FOLDER)
    return render_template("files.html", files=file_list)

# upload a file
@app.route("/upload", methods=["POST"])
def upload():
    if not is_unlocked():
        return redirect(url_for("index"))
    file = request.files.get("file")
    if file:
        file.save(os.path.join(UPLOAD_FOLDER, file.filename))
    return redirect(url_for("files"))

# download a file
@app.route("/download/<filename>")
def download(filename):
    return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)

# delete a file
@app.route("/delete/<filename>")
def delete(filename):
    if not is_unlocked():
        return redirect(url_for("index"))
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    if os.path.exists(file_path):
        os.remove(file_path)
    return redirect(url_for("files"))

# photos page
@app.route("/photos")
def photos():
    if not is_unlocked():
        return redirect(url_for("index"))
    photo_list = os.listdir(UPLOAD_FOLDER)
    photos = [f for f in photo_list if f.lower().endswith(('.png','.jpg','.jpeg','.gif','.webp'))]
    return render_template("photos.html", photos=photos)

# upload photo
@app.route("/upload_photo", methods=["POST"])
def upload_photo():
    if not is_unlocked():
        return redirect(url_for("index"))
    file = request.files.get("file")
    if file:
        file.save(os.path.join(UPLOAD_FOLDER, file.filename))
    return redirect(url_for("photos"))

# videos page
@app.route("/videos")
def videos():
    if not is_unlocked():
        return redirect(url_for("index"))
    video_list = os.listdir(UPLOAD_FOLDER)
    videos = [f for f in video_list if f.lower().endswith(('.mp4','.mov','.avi','.mkv'))]
    return render_template("videos.html", videos=videos)

# upload video
@app.route("/upload_video", methods=["POST"])
def upload_video():
    if not is_unlocked():
        return redirect(url_for("index"))
    file = request.files.get("file")
    if file:
        file.save(os.path.join(UPLOAD_FOLDER, file.filename))
    return redirect(url_for("videos"))

# stream a video
@app.route("/stream/<filename>")
def stream(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

# send page
@app.route("/send")
def send():
    if not is_unlocked():
        return redirect(url_for("index"))
    devices = Device.query.all()
    return render_template("send.html", devices=devices)

# send file to device via telegram
@app.route("/send_file", methods=["POST"])
def send_file():
    if not is_unlocked():
        return redirect(url_for("index"))
    filename = request.form.get("filename")
    device_id = request.form.get("device_id")
    device = Device.query.get(device_id)
    if device and filename:
        bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)
        file_url = f"http://{request.host}/download/{filename}"
        bot.send_message(chat_id=device.telegram_id, text=f"File ready: {file_url}")
    return redirect(url_for("send"))

# add device page
@app.route("/add_device", methods=["GET", "POST"])
def add_device():
    if not is_unlocked():
        return redirect(url_for("index"))
    if request.method == "POST":
        name = request.form.get("name")
        ip = request.form.get("wireguard_ip")
        telegram_id = request.form.get("telegram_id")
        new_device = Device(name=name, wireguard_ip=ip, telegram_id=telegram_id)
        db.session.add(new_device)
        db.session.commit()
        return redirect(url_for("send"))
    return render_template("add_device.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
