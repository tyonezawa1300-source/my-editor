import streamlit as st
import dropbox

# --- 1. Dropbox設定 ---
TOKEN = st.secrets["DROPBOX_TOKEN"]
dbx = dropbox.Dropbox(TOKEN)
FILE_PATH = "/note.txt"

st.set_page_config(page_title="iPhone Editor Pro", layout="centered")
st.title("📝 Dropbox Editor")

# ファイル読み書き関数
def load_file():
    try:
        _, res = dbx.files_download(FILE_PATH)
        return res.content.decode("utf-8")
    except:
        return ""

def save_file(content):
    dbx.files_upload(content.encode("utf-8"), FILE_PATH, mode=dropbox.files.WriteMode.overwrite)
    st.success("Dropboxに保存しました！")

# --- 2. 履歴管理の初期化 ---
if "history" not in st.session_state:
    initial_text = load_file()
    st.session_state.history = [initial_text]  # 過去の履歴リスト
    st.session_state.redo_stack = []           # やり直し用リスト
    st.session_state.current_text = initial_text

# --- 3. 編集エリア ---
# 入力欄（文字が変更されたら履歴に追加する）
temp_text = st.text_area("内容を編集", value=st.session_state.current_text, height=300)

# 文字が手入力で変わった場合、履歴に保存
if temp_text != st.session_state.current_text:
    st.session_state.history.append(temp_text)
    st.session_state.current_text = temp_text
    st.session_state.redo_stack = [] # 新しく書いたらやり直しスタックはクリア

# --- 4. 操作ボタン（元に戻す・やり直し） ---
col1, col2, col3 = st.columns(3)

with col1:
    # 元に戻す (Undo)
    if st.button("⬅️ 元に戻す", use_container_width=True):
        if len(st.session_state.history) > 1:
            # 現在の状態をやり直し用に保存して、一つ前の履歴に戻す
            last_state = st.session_state.history.pop()
            st.session_state.redo_stack.append(last_state)
            st.session_state.current_text = st.session_state.history[-1]
            st.rerun()

with col2:
    # やり直し (Redo)
    if st.button("➡️ やり直す", use_container_width=True):
        if st.session_state.redo_stack:
            next_state = st.session_state.redo_stack.pop()
            st.session_state.history.append(next_state)
            st.session_state.current_text = next_state
            st.rerun()

with col3:
    if st.button("💾 保存", use_container_width=True):
        save_file(temp_text)

st.divider()
st.caption("※「元に戻す」はアプリを開いてからの操作履歴に対して有効です。")
