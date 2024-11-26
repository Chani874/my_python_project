import subprocess
import math
import tkinter as tk
import threading
import time
import winsound  # מודול להשמעת צלילים

# פונקציה להמרת עוצמת אות (באחוזים) ל-RSSI
def signal_strength_to_rssi(signal_strength):
    return (signal_strength / 2) - 100

# פונקציה לחישוב מרחק על בסיס RSSI
def calculate_distance_from_rssi(rssi, tx_power=-59):
    if rssi == 0:
        return -1  # אין מידע
    ratio = rssi / tx_power
    if ratio < 1.0:
        return math.pow(ratio, 10)
    else:
        return (0.89976 * math.pow(ratio, 7.7095)) + 0.111

# פונקציה לסריקת עוצמת האות
def get_signal_strength():
    try:
        result = subprocess.run(
            ["netsh", "wlan", "show", "interfaces"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        output = result.stdout
        for line in output.split("\n"):
            if "Signal" in line and "%" in line:
                signal_strength = int(line.split(":")[1].strip().replace("%", ""))
                return signal_strength
    except Exception as e:
        print(f"שגיאה באיסוף עוצמת האות: {e}")
    return 0

# פונקציה להשמעת צליל אזהרה
def play_warning_sound():
    if not is_warning_playing[0]:  # למנוע השמעת צלילים בו זמנית
        is_warning_playing[0] = True
        winsound.Beep(1000, 500)  # צפצוף בתדר 1000Hz למשך 500ms
        is_warning_playing[0] = False

# פונקציה שרצה ברקע לעדכון הנתונים
def background_update():
    global current_distance
    while True:
        signal_strength = get_signal_strength()
        if signal_strength != 0:
            rssi = signal_strength_to_rssi(signal_strength)
            current_distance = calculate_distance_from_rssi(rssi)
        else:
            current_distance = -1
        time.sleep(0.02)  # בדיקה כל 20ms

# פונקציה לעדכון הממשק
def update_circle():
    if current_distance == -1:
        canvas.itemconfig(circle_outer, outline="gray", width=6)
        canvas.itemconfig(circle_inner, fill="white")
        canvas.itemconfig(text, text="")
        label.config(text="")  # לא להציג טקסט מתחת לעיגול
    else:
        canvas.itemconfig(text, text=f"{current_distance:.2f}", font=("Helvetica", 48, "bold"), fill="white")
        if current_distance < 0.5:
            # עיגול כחול
            canvas.itemconfig(circle_outer, outline="#4449CC", width=45)  # כחול בהיר למסגרת, עובי פי 3
            canvas.itemconfig(circle_inner, fill="#1A1E85")  # כחול כהה בפנים
            label.config(text="")  # לא להציג טקסט מתחת לעיגול
        elif 0.5 <= current_distance <= 1:
            # עיגול כתום
            canvas.itemconfig(circle_outer, outline="#FF8B59", width=45)  # כתום בהיר למסגרת, עובי פי 3
            canvas.itemconfig(circle_inner, fill="#EA641C")  # כתום כהה בפנים
            label.config(text="זוהה מרחק אסיר מחוץ לטווח השטח", fg="blue", font=("Helvetica", 10))  # טקסט כתום
        else:
            # עיגול אדום
            canvas.itemconfig(circle_outer, outline="#F64949", width=45)  # אדום בהיר למסגרת, עובי פי 3
            canvas.itemconfig(circle_inner, fill="#AA0000")  # אדום כהה בפנים
            label.config(text="זוהה מרחק אסיר מחוץ לטווח השטח", fg="blue", font=("Helvetica", 10))  # טקסט אדום
            play_warning_sound()  # השמעת צליל אם המרחק גדול מדי

    root.after(20, update_circle)  # עדכון כל 20ms

# משתנים גלובליים
current_distance = -1
is_warning_playing = [False]  # משתנה לבקרת צלילים

# יצירת הממשק
root = tk.Tk()
root.title("מדידת מרחק עם Wi-Fi")

canvas = tk.Canvas(root, width=400, height=400, bg="white")
canvas.pack()

# עיגול חיצוני (מסגרת) ועיגול פנימי
circle_outer = canvas.create_oval(50, 50, 350, 350, outline="gray", width=6)
circle_inner = canvas.create_oval(60, 60, 340, 340, fill="white", outline="")

# טקסט בתוך המסגרת
text = canvas.create_text(200, 200, text="", font=("Helvetica", 48, "bold"), fill="white")

# טקסט מתחת לעיגול
label = tk.Label(root, text="", font=("Helvetica", 10))
label.pack()

# הפעלת הליך ברקע
thread = threading.Thread(target=background_update, daemon=True)
thread.start()

# התחלת העדכון
update_circle()

root.mainloop()
