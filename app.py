import streamlit as st
import dropbox

# --- 1. Dropbox設定 ---
TOKEN = st.secrets["DROPBOX_TOKEN"]
dbx = dropbox.Dropbox(TOKEN)
FILE_PATH = "/note.txt"

st.set_page_config(page_title="iPhone Editor Pro", layout="centered")
st.title("📝 Dropbox Editor")

def load_file():
    try:
        _, res = dbx.files_download(FILE_PATH)
        return res.content.decode("utf-8")
    except:
        return ""

def save_file(content):
    dbx.files_upload(content.encode("utf-8"), FILE_PATH, mode=dropbox.files.WriteMode.overwrite)
    st.success("保存完了！")

# --- 2. 履歴と状態の管理 ---
if "history" not in st.session_state:
    initial_text = load_file()
    st.session_state.history = [initial_text]
    st.session_state.redo_stack = []
    st.session_state.current_text = initial_text

# --- 3. 編集エリア ---
# 入力されたテキストを受け取る
input_text = st.text_area("内容を編集", value=st.session_state.current_text, height=350)

# 手入力で内容が変わった場合のみ履歴を更新
if input_text != st.session_state.current_text:
    st.session_state.history.append(input_text)
    st.session_state.current_text = input_text
    st.session_state.redo_stack = []

# --- 4. 操作ボタンレイアウト ---
st.write("▼ 編集ツール")

# 1段目：取り消し・やり直し
col_undo, col_redo = st.columns(2)
with col_undo:
    if st.button("⬅️ 元に戻す (Undo)", use_container_width=True):
        if len(st.session_state.history) > 1:
            st.session_state.redo_stack.append(st.session_state.history.pop())
            st.session_state.current_text = st.session_state.history[-1]
            st.rerun()

with col_redo:
    if st.button("➡️ やり直す (Redo)", use_container_width=True):
        if st.session_state.redo_stack:
            next_state = st.session_state.redo_stack.pop()
            st.session_state.history.append(next_state)
            st.session_state.current_text = next_state
            st.rerun()

# 2段目：改行・保存
col_nl, col_save = st.columns(2)
with col_nl:
    if st.button("⏎ 改行を入れる", use_container_width=True):
        # 現在のテキストの末尾に改行を追加
        new_text = input_text + "\n"
        st.session_state.history.append(new_text)
        st.session_state.current_text = new_text
        st.rerun()

with col_save:
    if st.button("💾 Dropboxに保存", color="primary", use_container_width=True):
        save_file(input_text)

st.divider()
st.caption("Tip: 改行ボタンは文章の最後にパッと改行を入れたい時に便利です。")
