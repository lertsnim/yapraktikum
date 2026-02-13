import threading
import time
import requests
import os
import json
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
ACTION_ID = config.get('ACTION_ID', '439')
API_ACTION_URL = f"{BASE_URL}/api/v2/actions/{ACTION_ID}"
API_ACTION_STATS_URL = f"{BASE_URL}/api/v2/actions/{ACTION_ID}/stats"
API_ACTION_DONAT_URL = f"{BASE_URL}/api/v2/actions/{ACTION_ID}/donations"
MATCHING_RATIO = config.get('MATCHING_RATIO', '0')

# Глобальное хранилище данных акции
action_data = None
company_data = None
photos_data = None
last_updated = None
partners_data = None
stats_data = None
donat_data = None


def fetch_action():
    """Запрос данных акции по API."""
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Accept": "application/json",
    }
    resp = requests.get(API_ACTION_URL, headers=headers, timeout=10)
    resp.raise_for_status()
    return resp.json()

#Запрос статистики акции по API
def fetch_action_stats():
    #Запрос данных агреггированой статистикаи акции по API
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Accept": "application/json",
    }
    resp = requests.get(API_ACTION_STATS_URL, headers=headers, timeout=10)
    resp.raise_for_status()
    return resp.json()


#Запрос статистики акции по API
def fetch_donations():
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    payload = {
        "sort": "amount desc",
        "limit": 3,
        "offset": 0
    }

    resp = requests.get(
        API_ACTION_DONAT_URL,
        headers=headers,
        data=json.dumps(payload),
        timeout=10
    )

    resp.raise_for_status()
    return resp.json()


def format_money(value):
    if value is None:
        return "0 ₽"
    return f"{int(value):,} ₽".replace(",", " ")

def updater_loop():
    global action_data, company_data, photos_data, partners_data, stats_data, donat_data, last_updated
    while True:
        try:
            data = fetch_action()
            action_data = data
            company_data = data.get("company", {})
            photos_data = data.get("photos", [])
            partners_data = data.get("partners", []) 
            last_updated = time.strftime("%d.%m.%Y %H:%M:%S")
            #Статистика по акции через отдельный эндпоинт
            stats_data = fetch_action_stats()
            donat_data = fetch_donations()
        except Exception as e:
            print("Error updating action data:", e)
        time.sleep(60)  # 1 минуту

@app.route("/")
def action_page():
    if not action_data:
        return "Данные акции ещё не загружены. Попробуйте обновить страницу позже.", 503

    total = action_data.get("total") or 0
    total_raised = action_data.get("total_raised") or 0
    remaining = max(0, int(float(total) - float(total_raised)))  # вычисляем остаток до цели
    try:
        progress_percent = min(100, max(0, int(total_raised / total * 100))) if total else 0
    except Exception:
        progress_percent = 0
    
    fill_percent = 100 - progress_percent

    #Метчинг дополнительной поддержки от партнера акции
    if action_data.get("matching") != 0:
        matching = action_data.get("matching")+int(total_raised)
    else:
        matching = int(total_raised) * int(MATCHING_RATIO)

    #Вычисление заполнения строки суммы акци с учетом метчинга
    matching_percent = matching*100/total


    description = (action_data.get("description") or "").strip()
    short_description = description.split("\n")[0][:280]

    # text уже в HTML
    text_html = action_data.get("text") or ""

    date_start = (action_data.get("date_start") or "")[:10]
    date_end = (action_data.get("date_end") or "")[:10]

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
    status = action_data.get("status") or ""
    status_code = action_data.get("status_code")

    # Фиксированные суммы из API (amounts: amount, description, ord) — чем больше ord, тем выше в списке
    amounts_raw = action_data.get("amounts") or []
    amounts = sorted(amounts_raw, key=lambda x: x.get("ord", 0), reverse=True)

    
    


    return render_template(TEMPLATE,
        action=action_data,
        company=company_data,
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
        amounts=amounts,
        remaining=remaining,
        matching=matching,
        matching_display=format_money(matching),
        matching_percent = matching_percent,
        stats = stats_data,
        donations = donat_data,
    )

@app.route("/donate", methods=["POST"])
def donate():
    """Обработка формы пожертвования"""
    try:
        if not action_data:
            return jsonify({"error": "Данные акции не загружены"}), 503
        
        # Получаем данные из запроса
        data = request.get_json()
        if not data:
            return jsonify({"error": "Отсутствуют данные"}), 400
        
        email = data.get("email", "").strip()
        action_amount = float(data.get("action_amount", 0) or 0)
        company_amount = float(data.get("company_amount", 0) or 0)
        
        # Валидация
        if not email:
            return jsonify({"error": "Email обязателен"}), 400
        
        if action_amount < 0 or company_amount < 0:
            return jsonify({"error": "Суммы не могут быть отрицательными"}), 400
        
        if action_amount == 0 and company_amount == 0:
            return jsonify({"error": "Укажите хотя бы одну сумму пожертвования"}), 400
        
        # Получаем ID акции и компании
        action_id = action_data.get("id")
        company_id = action_data.get("company_id")
        
        if not action_id:
            return jsonify({"error": "ID акции не найден"}), 500
        
        if not company_id:
            return jsonify({"error": "ID компании не найден"}), 500
        
        # Формируем JSON для отправки
        total_amount = action_amount + company_amount
        
        recipients = []
        if action_amount > 0:
            recipients.append({
                "action_id": action_id,
                "amount": action_amount,
                "is_monthly": False
            })
        
        if company_amount > 0:
            recipients.append({
                "company_id": company_id,
                "amount": company_amount,
                "is_monthly": True
            })
        
        donation_data = {
            "email": email,
            "recipients": recipients,
            "total_amount": total_amount
        }
        
        # Отправляем на API (URL собирается из BASE_URL из конфига)
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
                "message": "Пожертвование успешно отправлено",
                "data": response_data
            }), 200
        
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Ошибка при отправке на API: {str(e)}"}), 500
    except ValueError as e:
        return jsonify({"error": f"Некорректные данные: {str(e)}"}), 400
    except Exception as e:
        return jsonify({"error": f"Внутренняя ошибка: {str(e)}"}), 500

if __name__ == "__main__":
    # фоновый поток обновления данных
    t = threading.Thread(target=updater_loop, daemon=True)
    t.start()
    app.run(host="0.0.0.0", port=80, debug=True)