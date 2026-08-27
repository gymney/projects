import os
import shutil
import threading

from flask import Flask, request, redirect, url_for, send_file, render_template, flash

import config
import db
from processor import process_file
from watcher import start_watcher_thread

app = Flask(__name__)
app.secret_key = "dev-only-not-secret"  # local tool, not exposed to the internet


@app.route("/")
def review_queue():
    pending = db.list_clips(status="pending")
    return render_template("review.html", clips=pending, categories=config.CATEGORIES,
                            incoming_dir=config.INCOMING_DIR)


@app.route("/history")
def history():
    approved = db.list_clips(status="approved")
    rejected = db.list_clips(status="rejected")
    return render_template("history.html", approved=approved, rejected=rejected)


@app.route("/upload", methods=["POST"])
def upload():
    file = request.files.get("file")
    if not file or file.filename == "":
        flash("No file selected.")
        return redirect(url_for("review_queue"))

    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in config.VIDEO_EXTENSIONS:
        flash(f"Unsupported file type: {ext}")
        return redirect(url_for("review_queue"))

    dest_path = os.path.join(config.INCOMING_DIR, file.filename)
    file.save(dest_path)

    # Uploaded via the browser means the file is already fully written
    # (unlike a folder being watched during live recording), so we can
    # process it immediately instead of waiting through the watcher's
    # stability check.
    def run():
        try:
            process_file(dest_path)
        except Exception as e:
            print(f"[upload] error processing {dest_path}: {e}")

    threading.Thread(target=run, daemon=True).start()
    flash(f"Uploaded {file.filename} -- processing in the background, refresh in a bit.")
    return redirect(url_for("review_queue"))


@app.route("/media/<int:clip_id>")
def media(clip_id):
    clip = db.get_clip(clip_id)
    if clip is None:
        return "Not found", 404
    return send_file(clip["clip_path"])


@app.route("/clip/<int:clip_id>/approve", methods=["POST"])
def approve(clip_id):
    clip = db.get_clip(clip_id)
    if clip is None:
        return "Not found", 404
    category = request.form.get("category") or "other"
    dest_dir = os.path.join(config.APPROVED_DIR, category)
    os.makedirs(dest_dir, exist_ok=True)
    dest_path = os.path.join(dest_dir, os.path.basename(clip["clip_path"]))
    shutil.move(clip["clip_path"], dest_path)
    db.update_status(clip_id, "approved", category)
    # keep the clip's db row pointing at its new location
    with db.get_conn() as conn:
        conn.execute("UPDATE clips SET clip_path = ? WHERE id = ?", (dest_path, clip_id))
        conn.commit()
    return redirect(url_for("review_queue"))


@app.route("/clip/<int:clip_id>/reject", methods=["POST"])
def reject(clip_id):
    clip = db.get_clip(clip_id)
    if clip is None:
        return "Not found", 404
    dest_path = os.path.join(config.REJECTED_DIR, os.path.basename(clip["clip_path"]))
    if os.path.exists(clip["clip_path"]):
        shutil.move(clip["clip_path"], dest_path)
    db.update_status(clip_id, "rejected")
    with db.get_conn() as conn:
        conn.execute("UPDATE clips SET clip_path = ? WHERE id = ?", (dest_path, clip_id))
        conn.commit()
    return redirect(url_for("review_queue"))


if __name__ == "__main__":
    db.init_db()
    start_watcher_thread()
    print(f"[app] drop files in {config.INCOMING_DIR} or upload via the web page")
    app.run(host="127.0.0.1", port=5000, debug=False)
