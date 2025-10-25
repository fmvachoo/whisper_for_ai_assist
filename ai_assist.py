import warnings
import os
import whisper
import speech_recognition as sr
import pyttsx3
import time
import subprocess
from pathlib import Path

# Отключаем предупреждение о FP16
warnings.filterwarnings("ignore", message="FP16 is not supported on CPU")

class VoiceQASystem:
    def __init__(self, model_size):
        """Инициализация системы"""
        
        self.check_ffmpeg()
        
        print(f"Загрузка модели {model_size}...")
        self.model = whisper.load_model(model_size)
        print("Модель загружена!")
        
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.tts_engine = pyttsx3.init()
        self.tts_engine.setProperty('rate', 150)
        
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
        
        self.dialog_file = "dialog.txt"
        print("Система готова к работе!")
    
    def check_ffmpeg(self):
        """Проверка наличия ffmpeg"""
        try:
            subprocess.run(["ffmpeg", "-version"], 
                         capture_output=True, check=True)
            print("FFmpeg найден")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("FFmpeg не найден!")
            raise
    
    def speak(self, text):
        """Произнесение текста"""
        print(f"Система: {text}")
        self.tts_engine.say(text)
        self.tts_engine.runAndWait()
        time.sleep(0.5)
    
    def listen_and_transcribe(self, timeout=10):
        """
        Прослушивание и транскрипция аудио
        """
        try:
            print("Слушаю...")
            with self.microphone as source:
                audio = self.recognizer.listen(
                    source, 
                    timeout=timeout, 
                    phrase_time_limit=10
                )
            
            # Сохраняем аудио
            audio_file = "temp_audio.wav"
            with open(audio_file, "wb") as f:
                f.write(audio.get_wav_data())
            
            # Транскрибируем
            result = self.model.transcribe(
                audio_file, 
                language="ru",
                fp16=False
            )
            text = result["text"].strip()
            
            # Удаляем временный файл
            if os.path.exists(audio_file):
                os.remove(audio_file)
            
            if text:
                print(f"Распознано: {text}")
                return text
            else:
                print("Пустой ответ")
                return None
            
        except sr.WaitTimeoutError:
            print("Время ожидания истекло")
            return None
        except Exception as e:
            print(f"Ошибка распознавания: {e}")
            # Очищаем временный файл
            if os.path.exists("temp_audio.wav"):
                os.remove("temp_audio.wav")
            return None
    
    def save_dialog(self, question, answer):
        """Сохранение диалога"""
        with open(self.dialog_file, "a", encoding="utf-8") as f:
            f.write(f"{question}@{answer}\n")
        print(f"Сохранено: {question}@{answer}")
    
    def conduct_interview(self, questions):
        """
        Проведение интервью с исправленной логикой
        """
        self.speak("Здравствуйте! Начнём наше интервью.")
        time.sleep(1)
        
        for i, question in enumerate(questions, 1):
            print(f"\n{'='*50}")
            print(f"Вопрос {i}/{len(questions)}: {question}")
            print(f"{'='*50}")
            
            # Задаем вопрос
            self.speak(question)
            time.sleep(1)
            
            answer = None
            for attempt in range(2):
                print(f"Попытка {attempt + 1}...")
                answer = self.listen_and_transcribe(timeout=15)
                
                if answer:
                    self.save_dialog(question, answer)
                    self.speak("Спасибо, ответ записан.")
                    break
                else:
                    # Не распознано
                    if attempt == 0:
                        self.speak("Я не расслышала ответ. Пожалуйста, повторите.")
                    else:
                        self.speak("Переходим к следующему вопросу.")
                        self.save_dialog(question, "НЕТ_ОТВЕТА")
            
            if i < len(questions):
                print("Подготовка к следующему вопросу...")
                time.sleep(2)
        
        # Завершение
        self.speak("Интервью завершено. Спасибо за участие!")
        print(f"\n Все ответы сохранены в файл: {self.dialog_file}")

if __name__ == "__main__":
    try:
        test_questions = [
            "Как вас зовут?",
            "Сколько вам лет?",
            "Какой ваш любимый цвет?",
            "Чем вы увлекаетесь?"
        ]
        
        print(" Запуск системы...")
        
        # Модель можно заменить на tiny, small, medium, large
        system = VoiceQASystem(model_size="base")
        
        print("Система готова!")
        print("Вопросы:", test_questions)
        
        system.conduct_interview(test_questions)
        
    except Exception as e:
        print(f" Ошибка: {e}")
        print("\n Советы по устранению проблем:")
        print("1. Проверьте что микрофон подключен")
        print("2. Дайте разрешение на использование микрофона")
        print("3. Убедитесь что в комнате достаточно тихо")
        print("4. Попробуйте говорить громче и четче")