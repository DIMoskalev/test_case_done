import pytest

from app.models import Post


@pytest.fixture()
async def upload_test_data(test_sessionmaker):
    async with test_sessionmaker() as session:
        posts = [
            Post(
                category="Электроника",
                content="В данной статье речь пойдет об  ruspberrypie (портативном компьютере для домашнего использования размером с модем). Слово",
            ),
            Post(
                category="Спорт",
                content="Чемпионат мира по настольному теннису недавно завершился и Китай снова занял первые места в индивидуальном зачете среди мужчин и женщин",
            ),
            Post(
                category="Хобби",
                content="Настольный теннис - это отличное хобби, которое помогает держать себя в тонусе, развивает мышление и стратегию",
            ),
            Post(
                category="Тесты",
                content="Проверка проверка, сколько раз раз, встретиться слово слово слово 'слово'? Слово 'слово' должно встретиться в этой статье 6 раз.",
            ),
        ]
    session.add_all(posts)
    await session.commit()


async def test_fetch_all_posts(ac, upload_test_data):
    response = await ac.get("/posts/")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 4
    assert len(data["items"]) == 4


async def test_filter_by_category(ac, upload_test_data):
    response = await ac.get("/posts/", params={"category": "Тесты"})
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    for item in data["items"]:
        assert item["category"] == "Тесты"
        assert item["id"] == 4
        assert item["word_freq"] == {
            "6": 1,
            "проверка": 2,
            "сколько": 1,
            "раз": 3,
            "встретиться": 2,
            "слово": 6,
            "должно": 1,
            "в": 1,
            "этой": 1,
            "статье": 1,
        }


async def test_filter_by_keywords(ac, upload_test_data):
    response = await ac.get("/posts/", params=[("keywords", "слово")])
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert all("слово" in item["word_freq"] for item in data["items"])


async def test_combined_filters(ac, upload_test_data):
    response = await ac.get(
        "/posts/", params=[("category", "Хобби"), ("keywords", "теннис")]
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["id"] == 3


async def test_pagination_limit_offset(ac, upload_test_data):
    response = await ac.get("/posts/", params={"limit": 2, "offset": 1})
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 4
    assert len(data["items"]) == 2
