import streamlit as st
import dropbox
from streamlit.components.v1 import html

# --- 1. Dropboxの設定 ---
# StreamlitのSecretsに登録したトークンを読み込みます
TOKEN = st.secrets["DROPBOX_TOKEN"]
dbx = dropbox.Dropbox(TOKEN)

st.set_page_config(page_title="iPhone Dropbox Editor", layout="centered")
st.title("📝 Dropbox Editor")

# --- 2. ファイルの読み込み設定 ---
# Dropbox内の /note.txt というファイルを編集します
FILE_PATH = "/note.txt"

def load_file():
    try:
        _, res = dbx.files_download(FILE_PATH)
        return res.content.decode("utf-8")
    except:
        # ファイルがない場合は初期メッセージを表示
        return "ここに入力してください"

def save_file(content):
    # Dropboxへ上書き保存
    dbx.files_upload(content.encode("utf-8"), FILE_PATH, mode=dropbox.files.WriteMode.overwrite)
    st.success("Dropboxに保存しました！")

# 画面を開いたときにデータを一度だけ読み込む
if "content" not in st.session_state:
    st.session_state.content = load_file()

# --- 3. JavaScriptでカーソル移動ボタンを作る ---
# iPhoneでテキストの途中を編集しやすくするための「裏技」です
js_code = """
<script>
function moveCursor(offset) {
    const textArea = window.parent.document.querySelector('textarea');
    if (!textArea) return;
    const start = textArea.selectionStart;
    const newPos = start + offset;
    textArea.setSelectionRange(newPos, newPos);
    textArea.focus();
}

window.addEventListener('message', function(event) {
    if (event.data.type === 'move') moveCursor(event.data.val);
});
</script>
"""
html(js_code, height=0)

# --- 4. 編集エリアの表示 ---
# 入力された内容は text_input という変数に入ります
text_input = st.text_area("内容を編集", value=st.session_state.content, height=400)

# --- 5. 操作ボタンの配置 ---
st.write("▼ カーソル移動（iPhone用）")
col1, col2 = st.columns(2)
with col1:
    if st.button("⬅️ 左へ移動", use_container_width=True):
        html("<script>window.parent.postMessage({type: 'move', val: -1}, '*')</script>", height=0)
with col2:
    if st.button("➡️ 右へ移動", use_container_width=True):
        html("<script>window.parent.postMessage({type: 'move', val: 1}, '*')</script>", height=0)

st.divider()

# 保存ボタン
if st.button("💾 Dropboxに保存する", use_container_width=True):
    save_file(text_input)
