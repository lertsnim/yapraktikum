import threading
import time
import requests
import os
from datetime import datetime, date
from flask import Flask, render_template, request, jsonify, send_from_directory

app = Flask(__name__)

# Папка frontend лежит в templates — раздаём её по URL /frontend/
FRONTEND_PATH = os.path.join(os.path.dirname(__file__), 'templates', 'frontend')

@app.route("/frontend/<path:filename>")
def serve_frontend(filename):
    """Раздача CSS, JS, изображений из папки templates/frontend."""
    return send_from_directory(FRONTEND_PATH, filename)

def load_config():
    """Загружает конфигурацию из файла config.txt"""
    config = {}
    config_path = os.path.join(os.path.dirname(__file__), 'config.txt')
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    config[key.strip()] = value.strip()
    except FileNotFoundError:
        print(f"Warning: Config file {config_path} not found")
    return config

config = load_config()
API_TOKEN = config.get('API_TOKEN', '')
TEMPLATE = config.get('TEMPLATE', 'index.html')
BASE_URL = config.get('BASE_URL', 'https://dev.blago.ru').rstrip('/')
MARATHON_ID = config.get('MARATHON_ID', '27')
API_MARATHON_URL = f"{BASE_URL}/api/v2/marathons/{MARATHON_ID}"
API_MARATHON_STATS_URL = f"{BASE_URL}/api/v2/marathons/{MARATHON_ID}/stats"
MATCHING_RATIO = config.get('MATCHING_RATIO', '0')

# Глобальное хранилище данных акции
marathon_data = None
participants_data = None
photos_data = None
last_updated = None
partners_data = None
stats_data = None


def fetch_marathon():
    """Запрос данных акции по API."""
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Accept": "application/json",
    }
    resp = requests.get(API_MARATHON_URL, headers=headers, timeout=10)
    resp.raise_for_status()
    return resp.json()

#Запрос статистики акции по API
def fetch_marathon_stats():
    #Запрос данных агреггированой статистикаи акции по API
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Accept": "application/json",
    }
    resp = requests.get(API_MARATHON_STATS_URL, headers=headers, timeout=10)
    resp.raise_for_status()
    return resp.json()



def format_money(value):
    if value is None:
        return "0 ₽"
    return f"{int(value):,} ₽".replace(",", " ")

def updater_loop():
    global marathon_data, participants_data, photos_data, partners_data, stats_data, last_updated
    while True:
        try:
            data = fetch_marathon()
            marathon_data = data
            photos_data = data.get("photos", [])
            partners_data = data.get("partners", [])
            participants_data = data.get("participants", [])
            last_updated = time.strftime("%d.%m.%Y %H:%M:%S")
            #Статистика по акции через отдельный эндпоинт
            #stats_data = fetch_marathon_stats()
        except Exception as e:
            print("Error updating marathon data:", e)
        time.sleep(60)  # 1 минуту

@app.route("/")
def marathon_page():
    if not marathon_data:
        return "Данные акции ещё не загружены. Попробуйте обновить страницу позже.", 503

    total = marathon_data.get("total") or 0
    total_raised = marathon_data.get("total_raised") or 0
    remaining = max(0, int(float(total) - float(total_raised)))  # вычисляем остаток до цели
    try:
        progress_percent = min(100, max(0, int(total_raised / total * 100))) if total else 0
    except Exception:
        progress_percent = 0
    
    fill_percent = 100 - progress_percent

#Метчинг дополнительной поддержки от партнера акции
    if marathon_data.get("matching") != 0:
        matching = marathon_data.get("matching")+int(total_raised)
    else:
        matching = int(total_raised) * int(MATCHING_RATIO)

    
    description = (marathon_data.get("description") or "").strip()
    short_description = description.split("\n")[0][:280]

    # text уже в HTML
    text_html = marathon_data.get("text") or ""

    date_start = (marathon_data.get("date_start") or "")[:10]
    date_end = (marathon_data.get("date_end") or "")[:10]

    # Дней до конца акции (по date_end)
    days_left = None
    if date_end:
        try:
            end = datetime.strptime(date_end, "%Y-%m-%d").date()
            today = date.today()
            days_left = max(0, (end - today).days)
        except (ValueError, TypeError):
            pass

    # Статус акции из API: status_code 0 — действует, 1 — завершена, 2 — сумма собрана
    status = marathon_data.get("status") or ""
    status_code = marathon_data.get("status_code")


    return render_template(TEMPLATE,
        marathon=marathon_data,
        participants = participants_data,
        photos=photos_data,
        partners=partners_data,
        last_updated=last_updated or "",
        total_display=format_money(total),
        total_raised_display=format_money(total_raised),
        progress_percent=progress_percent,
        fill_percent=fill_percent,
        description=description,
        short_description=short_description,
        text_html=text_html,
        date_start=date_start,
        date_end=date_end,
        days_left=days_left,
        status=status,
        status_code=status_code,
        base_url=BASE_URL,
        remaining=remaining,
        matching_display=format_money(matching),
        matching=matching,
        #stats = stats_data,
    )

@app.route("/donate", methods=["POST"])
def donate():
    """Обработка формы пожертвования"""

    try:
        if not marathon_data:
            return jsonify({"error": "Данные марафона не загружены"}), 503
        
        # Получаем данные из запроса
        data = request.get_json()
        if not data:
            return jsonify({"error": "Отсутствуют данные"}), 400
        
        email = data.get("email", "").strip()
        donations = data.get("donations", {})  # {"101": 500, "102": 1000}
        
        if not email:
            return jsonify({"error": "Укажите email"}), 400
        
        # Формируем recipients из donations
        recipients = []
        for participant_id, amount in donations.items():
            amount = float(amount)
            if amount > 0:
                recipients.append({
                    "participant_id": int(participant_id),
                    "amount": amount,
                    "is_monthly": False  # по умолчанию не ежемесячное
                })
        
        if not recipients:
            return jsonify({"error": "Нет пожертвований для отправки"}), 400
        
        # Общая сумма
        total_amount = sum(r["amount"] for r in recipients)
        
        donation_data = {
            "email": email,
            "recipients": recipients,
            "total_amount": total_amount
        }
        
        # Отправляем на API
        api_url = f"{BASE_URL}/api/v2/donations/create"
        headers = {
            "Authorization": f"Bearer {API_TOKEN}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        
        response = requests.post(api_url, json=donation_data, headers=headers, timeout=10)
        response.raise_for_status()
        
        response_data = response.json() if response.text else {}
        payment_url = response_data.get("payment_url")
        
        if payment_url:
            return jsonify({
                "success": True,
                "payment_url": payment_url
            }), 200
        else:
            return jsonify({
                "success": True,
                "message": f"Пожертвование на {len(recipients)} участников успешно отправлено",
                "data": response_data
            }), 200
            
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Ошибка API: {str(e)}"}), 500
    except (ValueError, KeyError) as e:
        return jsonify({"error": f"Некорректные данные: {str(e)}"}), 400
    except Exception as e:
        return jsonify({"error": f"Ошибка сервера: {str(e)}"}), 500

if __name__ == "__main__":
    # фоновый поток обновления данных
    t = threading.Thread(target=updater_loop, daemon=True)
    t.start()
    app.run(host="0.0.0.0", port=80, debug=True)