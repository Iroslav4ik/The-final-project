import cv2
import mediapipe as mp
import random
import time
import threading
import tkinter as tk


class GestureRecognizer:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            max_num_hands=1,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.results = None

    def process_frame(self, frame):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(rgb_frame)
        return frame

    def get_gesture(self):
        if not self.results or not self.results.multi_hand_landmarks:
            return None

        landmarks = self.results.multi_hand_landmarks[0].landmark
        finger_tips = [
            landmarks[self.mp_hands.HandLandmark.INDEX_FINGER_TIP],
            landmarks[self.mp_hands.HandLandmark.MIDDLE_FINGER_TIP],
            landmarks[self.mp_hands.HandLandmark.RING_FINGER_TIP],
            landmarks[self.mp_hands.HandLandmark.PINKY_TIP]
        ]
        mcp_joints = [
            landmarks[self.mp_hands.HandLandmark.INDEX_FINGER_MCP],
            landmarks[self.mp_hands.HandLandmark.MIDDLE_FINGER_MCP],
            landmarks[self.mp_hands.HandLandmark.RING_FINGER_MCP],
            landmarks[self.mp_hands.HandLandmark.PINKY_MCP]
        ]

        fingers_up = [1 if tip.y < mcp.y else 0 for tip, mcp in zip(finger_tips, mcp_joints)]

        if fingers_up == [1, 1, 0, 0]:
            return "scissors"
        elif all(f == 0 for f in fingers_up):
            return "rock"
        elif all(f == 1 for f in fingers_up):
            return "paper"
        return None


class Game:
    GESTURES = ["rock", "paper", "scissors"]
    WIN_CONDITIONS = {
        "rock": "scissors",
        "scissors": "paper",
        "paper": "rock"
    }

    def __init__(self):
        self.recognizer = GestureRecognizer()
        self.player_gesture = None
        self.computer_gesture = None

    def get_computer_choice(self):
        self.computer_gesture = random.choice(self.GESTURES)
        return self.computer_gesture

    def determine_winner(self):
        if self.player_gesture == self.computer_gesture:
            return "draw"
        elif self.WIN_CONDITIONS[self.player_gesture] == self.computer_gesture:
            return "player"
        else:
            return "computer"

    def play(self):
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            return "📷 Ошибка: Камера не найдена!"

        time.sleep(3)
        ret, frame = cap.read()
        if not ret:
            cap.release()
            return "❌ Ошибка: Не удалось получить изображение с камеры"

        self.recognizer.process_frame(frame)
        self.player_gesture = self.recognizer.get_gesture()
        cap.release()

        if not self.player_gesture:
            return "🤔 Жест не распознан. Попробуйте снова."

        self.get_computer_choice()
        result = self.determine_winner()
        return self.format_result(result)

    def format_result(self, result):
        gesture_names = {
            "rock": "Камень ✊",
            "paper": "Бумага ✋",
            "scissors": "Ножницы ✌️"
        }

        player = gesture_names.get(self.player_gesture, "Неизвестно")
        computer = gesture_names.get(self.computer_gesture, "Неизвестно")

        if result == "player":
            outcome = "ПОБЕДА 🎉"
        elif result == "computer":
            outcome = "ВЫ ПРОИГРАЛИ 😭"
        else:
            outcome = "НИЧЬЯ 😐"

        return f"Вы: {player}\nКомпьютер: {computer}\n\n {outcome}"


# === Интерфейс ===
def run_game():
    play_button.config(state="disabled")
    result_label.config(text="⏳ Подождите, игра начинается...")

    def task():
        game = Game()
        result = game.play()
        result_label.config(text=result)
        play_button.config(state="normal")

    threading.Thread(target=task).start()


# Главное окно
root = tk.Tk()
root.title("Игра: Камень, ножницы, бумага ✋✌️✊")
root.geometry("400x300")
root.configure(bg="#66CDAA")  # Голубой фон

# Заголовок
title_label = tk.Label(
    root,
    text="КАМЕНЬ НОЖНИЦЫ БУМАГА",
    font=("Arial", 22, "bold"),
    bg="#66CDAA"
)
title_label.pack(pady=20)

# Кнопка "Играть"
play_button = tk.Button(
    root,
    text="Играть!",
    font=("Arial", 18, "bold"),
    bg="#66CDAA",
    fg="black",
    padx=20,
    pady=10,
    command=run_game
)
play_button.pack(pady=15)

# Результаты игры
result_label = tk.Label(
    root,
    text="",
    font=("Arial", 16),
    bg="#66CDAA",
    wraplength=450,
    justify="center"
)
result_label.pack(pady=20)

root.mainloop()
