import streamlit as st
import dropbox

# --- 1. Dropbox設定 ---
TOKEN = st.secrets["DROPBOX_TOKEN"]
dbx = dropbox.Dropbox(TOKEN)
FILE_PATH = "/note.txt"

st.set_page_config(page_title="iPhone Editor", layout="centered")
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
    st.success("保存完了！")

# データの管理
if "text" not in st.session_state:
    st.session_state.text = load_file()

# --- 2. 編集エリア ---
# 入力欄
text_input = st.text_area("内容を編集", value=st.session_state.text, height=300)

# --- 3. 【新機能】iPhoneでも動くカーソル位置指定 ---
# ボタンがダメなら「スライダー」で文字の場所を指定します
st.write("▼ 文字を挿入したい場所を調整（iPhone用）")
pos = st.slider("現在の文字数（左から何文字目か）", 0, len(text_input), len(text_input))

# 挿入したい記号などを置く
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("「 」を挿入"):
        new_text = text_input[:pos] + "「」" + text_input[pos:]
        st.session_state.text = new_text
        st.rerun()

with col2:
    if st.button("。 を挿入"):
        new_text = text_input[:pos] + "。" + text_input[pos:]
        st.session_state.text = new_text
        st.rerun()

with col3:
    if st.button("改行を入れる"):
        new_text = text_input[:pos] + "\n" + text_input[pos:]
        st.session_state.text = new_text
        st.rerun()

st.divider()

# 保存ボタンを大きく
if st.button("💾 Dropboxに保存する", use_container_width=True):
    save_file(text_input)
