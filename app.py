import streamlit as st
import sqlite3
from datetime import datetime
import pandas as pd

# 데이터베이스 초기화
def init_db():
    conn = sqlite3.connect('board.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            author TEXT NOT NULL,
            created_at TIMESTAMP NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# 데이터베이스 연결
def get_db_connection():
    conn = sqlite3.connect('board.db')
    conn.row_factory = sqlite3.Row
    return conn

# 페이지 설정
st.set_page_config(
    page_title="게시판",
    page_icon="📝",
    layout="centered"
)

# 데이터베이스 초기화
init_db()

# 사이드바 - 메뉴 선택
st.sidebar.title("메뉴")
menu = st.sidebar.radio(
    "선택하세요",
    ["글 목록", "글 작성", "글 수정/삭제"]
)

# 글 목록 보기
if menu == "글 목록":
    st.title("게시글 목록")
    
    conn = get_db_connection()
    posts = conn.execute('SELECT * FROM posts ORDER BY created_at DESC').fetchall()
    conn.close()
    
    if not posts:
        st.info("등록된 게시글이 없습니다.")
    else:
        for post in posts:
            with st.expander(f"{post['title']} - {post['author']} ({post['created_at']})"):
                st.write(f"내용: {post['content']}")
                st.write(f"작성일: {post['created_at']}")

# 글 작성
elif menu == "글 작성":
    st.title("게시글 작성")
    
    with st.form("write_form"):
        title = st.text_input("제목")
        content = st.text_area("내용")
        author = st.text_input("작성자")
        submit = st.form_submit_button("작성")
        
        if submit:
            if not title or not content or not author:
                st.error("모든 필드를 입력해주세요.")
            else:
                conn = get_db_connection()
                conn.execute(
                    'INSERT INTO posts (title, content, author, created_at) VALUES (?, ?, ?, ?)',
                    (title, content, author, datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                )
                conn.commit()
                conn.close()
                st.success("게시글이 작성되었습니다.")
                st.rerun()

# 글 수정/삭제
else:
    st.title("게시글 수정/삭제")
    
    conn = get_db_connection()
    posts = conn.execute('SELECT * FROM posts ORDER BY created_at DESC').fetchall()
    conn.close()
    
    if not posts:
        st.info("수정/삭제할 게시글이 없습니다.")
    else:
        # 게시글 선택
        post_titles = [f"{post['title']} - {post['author']} ({post['created_at']})" for post in posts]
        selected_post = st.selectbox("수정/삭제할 게시글을 선택하세요", post_titles)
        
        if selected_post:
            # 선택된 게시글 정보 가져오기
            selected_index = post_titles.index(selected_post)
            selected_post_data = posts[selected_index]
            
            # 수정 폼
            with st.form("edit_form"):
                st.write("### 게시글 수정")
                new_title = st.text_input("제목", value=selected_post_data['title'])
                new_content = st.text_area("내용", value=selected_post_data['content'])
                new_author = st.text_input("작성자", value=selected_post_data['author'])
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.form_submit_button("수정"):
                        if not new_title or not new_content or not new_author:
                            st.error("모든 필드를 입력해주세요.")
                        else:
                            conn = get_db_connection()
                            conn.execute(
                                'UPDATE posts SET title = ?, content = ?, author = ? WHERE id = ?',
                                (new_title, new_content, new_author, selected_post_data['id'])
                            )
                            conn.commit()
                            conn.close()
                            st.success("게시글이 수정되었습니다.")
                            st.rerun()
                
                with col2:
                    if st.form_submit_button("삭제"):
                        conn = get_db_connection()
                        conn.execute('DELETE FROM posts WHERE id = ?', (selected_post_data['id'],))
                        conn.commit()
                        conn.close()
                        st.success("게시글이 삭제되었습니다.")
                        st.rerun() 
