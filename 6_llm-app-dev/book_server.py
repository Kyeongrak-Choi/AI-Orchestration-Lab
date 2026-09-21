import os
import sqlite3
from pathlib import Path

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Book")

# `book_server.py`를 어느 폴더에서 실행해도 같은 DB를 사용하도록 합니다.
# 필요하면 BOOK_DATABASE_PATH 환경 변수로 경로를 바꿀 수 있습니다.
DATABASE_PATH = Path(
    os.getenv("BOOK_DATABASE_PATH", Path(__file__).resolve().with_name("my_database.db"))
)

# DB가 비어 있을 때 사용할 실습용 기본 데이터입니다.
# 실제 books 테이블에 데이터가 있으면 이 데이터는 추가하지 않습니다.
DEFAULT_BOOKS = [
    (1, "교사를 지키는 단단한 생활지도 : 상황별 실전 사례 100", "이종혁 저", 18000),
    (2, "세네카, 오늘을 빼앗기고 있는 당신에게", "루키우스 안나이우스 세네카 저/ 하와이 대저택 편역", 16200),
    (3, "흔한남매 23", "흔한남매 원저/ 백난도 글/ 유난희 그림/ 흔한컴퍼니 감수", 15120),
    (4, "우정과 허기를 버무린 우리들의 시간", "파뿌리 저", 17100),
    (5, "싯다르타", "헤르만 헤세 저/ 박병덕 역", 7200),
    (6, "멜로우TV 팀 나빠 추리 탐정단 1", "멜로우 TV, 팀 나빠 원저/ 김정욱 글/ 김기수 그림", 15120),
    (7, "그랬다고 적었다", "김애란 저", 15300),
    (8, "마음의 어휘력", "조아란, 권희, 이정윤 저", 15120),
    (9, "니체의 초월자", "프리드리히 니체 저/ 김철 편역", 15210),
]


def _connect_database() -> sqlite3.Connection:
    """DB와 연결하고, 처음 실행하는 경우 책 테이블과 기본 데이터를 준비합니다."""
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DATABASE_PATH)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS books (
            book_rank INTEGER NOT NULL,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            price INTEGER NOT NULL
        )
        """
    )

    book_count = conn.execute("SELECT COUNT(*) FROM books").fetchone()[0]
    if book_count == 0:
        conn.executemany(
            """
            INSERT INTO books (book_rank, title, author, price)
            VALUES (?, ?, ?, ?)
            """,
            DEFAULT_BOOKS,
        )

    conn.commit()
    return conn


def _format_price(price: int) -> str:
    """DB의 가격 값을 사용자에게 보여줄 형식으로 변환합니다."""
    try:
        return f"{int(price):,}"
    except (TypeError, ValueError):
        return str(price)


# 도구 정의
@mcp.tool()
def get_book_by_rank(rank: int) -> str:
    """
    베스트셀러 순위로 책 정보를 조회합니다.
    """

    sql = """
        SELECT book_rank, title, author, price
          FROM books
         WHERE book_rank = ?
    """

    conn = None
    try:
        conn = _connect_database()
        row = conn.execute(sql, (rank,)).fetchone()

        if row is None:
            return f"{rank}위에 해당하는 책 정보를 찾을 수 없습니다."

        book_rank, title, author, price = row
        return f"{book_rank}위: {title} / {author} / {_format_price(price)}원"
    except (sqlite3.Error, OSError) as exc:
        return f"도서 정보 조회 중 오류가 발생했습니다: {exc}"
    finally:
        if conn is not None:
            conn.close()


@mcp.tool()
def search_book(keyword: str) -> str:
    """
    제목이나 저자에 키워드가 포함된 책 정보를 조회합니다.
    """

    sql = """
        SELECT book_rank, title, author, price
          FROM books
         WHERE title LIKE ? OR author LIKE ?
         ORDER BY book_rank
    """

    keyword = keyword.strip()
    if not keyword:
        return "검색어를 입력해 주세요."

    pattern = f"%{keyword}%"
    conn = None
    try:
        conn = _connect_database()
        rows = conn.execute(sql, (pattern, pattern)).fetchall()

        if not rows:
            return f"'{keyword}'가 포함된 책 정보를 찾을 수 없습니다."

        return "\n".join(
            f"{book_rank}위 / {title} / {author} / {_format_price(price)}원"
            for book_rank, title, author, price in rows
        )
    except (sqlite3.Error, OSError) as exc:
        return f"도서 정보 검색 중 오류가 발생했습니다: {exc}"
    finally:
        if conn is not None:
            conn.close()


if __name__ == "__main__":
    mcp.run(transport="stdio")  # 로컬 stdio로 대기
