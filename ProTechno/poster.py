import requests
import time

ACCESS_TOKEN = "vk1.a.QhPc8KVE4BUXd7vGk5YCOY240aLsuJEK7HADb6OyOBiUbhvP8bN6RIMkdTGiLOC4x1l17HyZJVO_zJm8yC7YgChAe92wRGqjGrxyBt1ZMUatdJej2Nu_3LOoCbUlnhcip2tyi3A6eQbPa-wViKWbVy81fzLpJtoMGct7suNQc-jO4b_lBhVNJuhzK6iMQS2CfHoumAAhUjxLQoiXZzKU1Q"

GROUP_ID = 238056064
API_VERSION = "5.199"
API_URL = "https://api.vk.com/method/wall.post"


def create_post(message, attachments=None, from_group=True):
    """
    Публикует пост на стену сообщества.

    :param message: Текст поста
    :param attachments: Вложения (фото, видео и т.д.) в формате VK, например "photo123_456"
    :param from_group: True — пост от имени сообщества, False — от имени пользователя
    :return: ID опубликованного поста или None при ошибке
    """
    params = {
        "owner_id": -GROUP_ID,
        "from_group": int(from_group),
        "message": message,
        "v": API_VERSION,
        "access_token": ACCESS_TOKEN,
    }

    if attachments:
        params["attachments"] = attachments

    for attempt in range(5):
        try:
            resp = requests.post(API_URL, data=params, timeout=15)
            data = resp.json()
            break
        except (requests.exceptions.RequestException, ValueError) as e:
            print(f"  Ошибка сети (попытка {attempt + 1}/5): {e}")
            time.sleep(2)
    else:
        print("Не удалось выполнить запрос после 5 попыток.")
        return None

    if "error" in data:
        print(f"Ошибка VK API: {data['error']['error_msg']}")
        return None

    post_id = data["response"]["post_id"]
    print(f"Пост опубликован! ID: {post_id}")
    print(f"Ссылка: https://vk.com/wall-{GROUP_ID}_{post_id}")
    return post_id


def main():
    message = input("Введите текст поста: ").strip()
    if not message:
        print("Текст поста не может быть пустым.")
        return

    attachments = input("Вложения (оставьте пустым, если нет): ").strip() or None

    create_post(message, attachments=attachments)


if __name__ == "__main__":
    main()
